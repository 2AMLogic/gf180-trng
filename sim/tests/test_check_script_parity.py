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

PACKAGE = Path(__file__).resolve().parents[2] / "package.json"


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


if __name__ == "__main__":
    unittest.main()
