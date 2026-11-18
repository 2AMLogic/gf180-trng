#!/usr/bin/env python3
"""Hold sim/tools/workflow_yaml_guard.py to its contract (issue #1003).

The guard is a line scanner, not a YAML parser: it flags the one defect
class measured in issue #1003 -- a plain ``name:`` mapping value containing
``": "`` (or ending in ``:``), which every YAML parser reads as a nested
mapping and which therefore turns the workflow into a zero-job startup
failure -- while leaving quoted values, block scalars, flow collections,
comments and URL colons alone. Every case feeds a literal document to
findings(); nothing depends on the state of the real tree except the final
guard-on-this-tree case. Stdlib only.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))

import workflow_yaml_guard as guard  # noqa: E402

OFFENDING = ("jobs:\n"
             "  t:\n"
             "    steps:\n"
             "      - name: Self-checks (the one check list: sim/check.sh ci)\n")


class Findings(unittest.TestCase):
    def finding(self, doc: str, path: str = "wf.yml") -> str:
        found = guard.findings(doc, path)
        self.assertEqual(len(found), 1, found)
        return found[0]

    def clean(self, doc: str, path: str = "wf.yml") -> None:
        self.assertEqual(guard.findings(doc, path), [])

    # -- the defect class -------------------------------------------------

    def test_list_item_name_with_interior_colon_space_is_flagged(self):
        f = self.finding(OFFENDING)
        self.assertTrue(f.startswith("wf.yml:4:"), f)
        self.assertIn("- name", f)

    def test_top_level_name_is_flagged(self):
        self.assertEqual(len(guard.findings("name: TRNG (the: thing)\n")), 1)

    def test_trailing_colon_is_flagged(self):
        self.assertEqual(len(guard.findings("- name: Steps:\n")), 1)

    def test_name_under_with_is_flagged(self):
        doc = ("steps:\n"
               "  - uses: x\n"
               "    with:\n"
               "      name: bad: value\n")
        f = self.finding(doc)
        self.assertTrue(f.startswith("wf.yml:4:"), f)

    def test_finding_names_line_and_value(self):
        f = self.finding("name: a: b\n", "ci.yml")
        self.assertTrue(f.startswith("ci.yml:1:"), f)
        self.assertIn("a: b", f)

    # -- non-defects that must not false-positive -------------------------

    def test_double_quoted_value_is_clean(self):
        self.clean('- name: "Self-checks (check list: sim/check.sh ci)"\n')

    def test_single_quoted_value_is_clean(self):
        self.clean("- name: 'Self-checks (check list: sim/check.sh ci)'\n")

    def test_trailing_comment_is_clean(self):
        self.clean("- name: Build # note: this does: stuff\n")

    def test_comment_only_line_is_clean(self):
        self.clean("#   - name: not: a real step\n")

    def test_url_colon_is_clean(self):
        self.clean("name: see http://example.com/x\n")

    def test_colon_without_space_is_clean(self):
        self.clean("name: a:b\n")

    def test_flow_value_is_clean(self):
        self.clean("name: {a: b}\n")

    def test_empty_value_is_clean(self):
        self.clean("name:\n")

    def test_longer_key_is_ignored(self):
        # `display-name:` and `run-name:` are different keys; so is `name:foo`.
        self.clean("display-name: a: b\n")
        self.clean("run-name: a: b\n")
        self.clean("name:foo: bar\n")

    def test_block_scalar_name_value_is_clean(self):
        self.clean("name: |\n  a: b\n")

    def test_line_inside_block_scalar_is_clean(self):
        doc = ("      - name: Build\n"
               "        run: |\n"
               "          name: looks: like the trap\n"
               "          make all\n")
        self.clean(doc)

    def test_dedent_exits_block_scalar(self):
        doc = ("steps:\n"
               "  - name: Build\n"
               "    run: |\n"
               "      name: inside: block\n"
               "  - name: a: b\n")
        self.assertEqual(len(guard.findings(doc)), 1)

    def test_sequence_item_block_value_is_clean(self):
        doc = ("env:\n"
               "  - |\n"
               "    A: B: C\n")
        self.clean(doc)


class Main(unittest.TestCase):
    def test_this_tree_is_clean(self):
        self.assertEqual(guard.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
