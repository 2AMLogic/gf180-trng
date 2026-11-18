#!/usr/bin/env python3
"""Wire the merge_group event into ci.yml's required checks (#1009).

The repo's required contexts all report from ``.github/workflows/ci.yml``
(``harness`` and the T1 ``signoff`` job), so a merge-queue rollout needs two
things to hold in that one file, and nothing else in the tree re-checks
them. This test does, by text: PyYAML is not available here (#1003), and
both properties are textual anyway.

1. ``on:`` declares ``merge_group`` with no filter. A queued merge is
   checked as a ``merge_group`` event; a ``paths:``/``branches:`` filter
   would make the required checks never run, and the queue would hang.
2. The ``Self-checks`` base-selection ``case`` has an explicit
   ``merge_group)`` arm fed from ``github.event.merge_group.base_sha``.
   Without it, a queued merge silently falls into the ``*) origin/main``
   fallback and the append-only gate compares against a moving ref instead
   of the queue's base -- a gate that skips on ``merge_group`` is a silent
   drop, not a pass (#1009). The arm must sit before the ``*)`` fallback,
   and an empty value must fail through the existing ``[ -z "$base" ]``
   guard rather than proceed.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

CI_YML = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"


def on_block(text: str) -> str:
    """The indented body of the top-level ``on:`` mapping."""
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if re.match(r"^on:\s*$", line))
    body = []
    for line in lines[start + 1 :]:
        if line and not line[0].isspace():
            break
        body.append(line)
    return "\n".join(body)


def event_body(block: str, event: str) -> str | None:
    """The sub-mapping under ``  <event>:`` up to the next event key.

    ``None`` when the event is not declared; the empty string when it is
    declared with no filter (the form the merge queue needs).
    """
    m = re.search(rf"^  {re.escape(event)}:[ \t]*$", block, re.M)
    if m is None:
        return None
    rest = block[m.end() :]
    nxt = re.search(r"^  \S", rest, re.M)
    return (rest[: nxt.start()] if nxt else rest).strip()


class MergeGroupTriggerTests(unittest.TestCase):
    def test_merge_group_declared_with_no_filter(self):
        block = on_block(CI_YML.read_text())
        self.assertEqual(event_body(block, "merge_group"), "")

    def test_existing_triggers_still_declared(self):
        block = on_block(CI_YML.read_text())
        # The three pre-merge-queue triggers keep their form (#1009: the
        # existing triggers stay byte-unchanged; push keeps its branch
        # filter, the other two stay bare).
        self.assertIn("  push:\n    branches: [main]\n", block)
        self.assertEqual(event_body(block, "pull_request"), "")
        self.assertEqual(event_body(block, "workflow_dispatch"), "")


class MergeGroupBaseSelectionTests(unittest.TestCase):
    def test_env_taps_merge_group_base_sha(self):
        text = CI_YML.read_text()
        m = re.search(
            r"^\s+MERGE_GROUP_BASE_SHA: \$\{\{ github\.event\.merge_group\.base_sha \}\}\s*$",
            text,
            re.M,
        )
        self.assertIsNotNone(m, "Self-checks env must set MERGE_GROUP_BASE_SHA from github.event.merge_group.base_sha")

    def test_case_has_merge_group_arm(self):
        text = CI_YML.read_text()
        m = re.search(r'^\s+merge_group\)\s+base="\$MERGE_GROUP_BASE_SHA"\s*;;\s*$', text, re.M)
        self.assertIsNotNone(m, "the base-selection case needs a merge_group) arm fed by MERGE_GROUP_BASE_SHA")

    def test_merge_group_arm_precedes_the_fallback(self):
        text = CI_YML.read_text()
        arm = re.search(r'^\s+merge_group\)\s+base="\$MERGE_GROUP_BASE_SHA"\s*;;\s*$', text, re.M)
        fallback = re.search(r'^\s+\*\)\s+base="origin/main"\s*;;\s*$', text, re.M)
        self.assertIsNotNone(arm)
        self.assertIsNotNone(fallback)
        self.assertLess(arm.start(), fallback.start())

    def test_empty_base_fails_closed(self):
        # The shared guard the merge_group arm falls into when the env value
        # is empty (first event of its kind, or a stripped context): a
        # failure, never a quiet comparison against nothing.
        text = CI_YML.read_text()
        guard = re.search(r'^\s+if \[ -z "\$base" \]; then\s*$', text, re.M)
        self.assertIsNotNone(guard)
        tail = text[guard.end() :]
        self.assertIn("exit 2", tail[: len("ERROR: no base revision") + 200])


if __name__ == "__main__":
    unittest.main()
