#!/usr/bin/env python3
"""Keep package.json's `check:all` a superset of `check:ci`.

`check:all` is the documented local pre-commit gate; every `check:*` step that
CI runs must also run there, either as `npm run check:X` or as the script's own
command with `--require-tools` appended. Stdlib only.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from sim.tools import _git_files

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "package.json"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


class CheckScriptParity(unittest.TestCase):
    def test_check_all_covers_check_ci(self) -> None:
        scripts = json.loads(PACKAGE.read_text())["scripts"]
        ci, full = scripts["check:ci"], scripts["check:all"]
        steps = re.findall(r"npm run (check:[\w-]+)", ci)
        self.assertTrue(steps)
        for step in steps:
            direct = f"npm run {step}"
            strict = f"{scripts[step]} --require-tools"
            self.assertTrue(
                re.search(re.escape(direct) + r"(?![\w-])", full) or strict in full,
                f"{step} runs in check:ci but not in check:all",
            )

    def test_ci_python_steps_are_named_entry_points(self) -> None:
        """A bare `python3 ...` CI `run:` step is invisible to the test above.

        Every such step must be the body of an `npm run check:*` script (or
        that body plus `--require-tools`) that both check:ci and check:all reach.
        """
        scripts = json.loads(PACKAGE.read_text())["scripts"]
        commands = re.findall(
            r"^\s*(?:-\s+)?run:\s*(python3\s.*?)\s*$", CI_WORKFLOW.read_text(), re.M
        )
        for command in commands:
            names = [
                n
                for n, body in scripts.items()
                if n.startswith("check:") and command in (body, f"{body} --require-tools")
            ]
            self.assertTrue(names, f"CI runs `{command}` with no npm check:* entry")
            for chain in ("check:ci", "check:all"):
                self.assertTrue(
                    command in scripts[chain]
                    or any(re.search(rf"npm run {re.escape(n)}(?![\w-])", scripts[chain]) for n in names),
                    f"CI runs `{command}` but {chain} does not reach it",
                )
    def test_every_named_entry_point_has_a_caller(self) -> None:
        """A `scripts` entry nothing invokes is invisible to the tests above.

        Guards the reverse direction: every named entry point except the two
        chain roots must be reached by an `npm run <name>` (yarn/pnpm count
        too) in some tracked file. Scanning `git ls-files` rather than just
        package.json keeps docs-only callers like `check:signoff` in
        `signoff/README.md` valid, and makes an unreachable second name for
        a command fail here instead of sitting unnoticed.
        """
        scripts = json.loads(PACKAGE.read_text())["scripts"]
        chain_roots = {"check:ci", "check:all"}
        unreached = {
            name: re.compile(
                rf"(?:npm|yarn|pnpm) run {re.escape(name)}(?![\w:-])".encode()
            )
            for name in scripts
            if name not in chain_roots
        }
        for rel in _git_files.tracked_files(ROOT):
            text = (ROOT / rel).read_bytes()
            for name in [n for n, pat in unreached.items() if pat.search(text)]:
                del unreached[name]
            if not unreached:
                return
        self.assertEqual(
            sorted(unreached),
            [],
            "package.json scripts that no tracked file invokes",
        )


if __name__ == "__main__":
    unittest.main()
