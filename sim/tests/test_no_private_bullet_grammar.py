#!/usr/bin/env python3
"""No sim tool may carry its own copy of the result-bullet grammar (#537).

``sim/tools/_record_parsing.py`` is the one place that defines what a
``- `key`: value`` result bullet may look like, including the numeric token.
A private re-typed copy silently diverges when that grammar is hardened, so a
record could be accepted by one report tool and rejected by another. This
test fails if any other tool module compiles a pattern that starts with the
bullet prefix. Stdlib only.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
BULLET_PREFIX = "^- `("
SHARED = "_record_parsing.py"


def _offending_strings(path: Path) -> list[int]:
    tree = ast.parse(path.read_text(), filename=str(path))
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if BULLET_PREFIX in node.value:
                lines.append(node.lineno)
    return lines


class NoPrivateBulletGrammarTest(unittest.TestCase):
    def test_only_shared_module_defines_bullet_grammar(self) -> None:
        offenders = {}
        for path in sorted(TOOLS_DIR.glob("*.py")):
            if path.name == SHARED:
                continue
            lines = _offending_strings(path)
            if lines:
                offenders[path.name] = lines
        self.assertEqual(
            offenders,
            {},
            "result-bullet regex re-typed outside _record_parsing.py; use "
            "VALUE_RE / SEED_SUMMARY_RE / NUMBER_PATTERN from there instead",
        )

    def test_shared_module_still_defines_it(self) -> None:
        # Keeps the guard honest: if the prefix moved, the scan above is vacuous.
        self.assertTrue(_offending_strings(TOOLS_DIR / SHARED))


if __name__ == "__main__":
    unittest.main()
