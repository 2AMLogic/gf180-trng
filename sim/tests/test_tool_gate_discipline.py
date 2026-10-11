#!/usr/bin/env python3
"""Every simulator-gated unit test goes through ``_tool_gate.requires_tools``
(#618).

The strict switch (``REQUIRE_RTL_TOOLS=1``, set by the nightly workflow) only
works for gates that use the shared helper. A test that writes its own
``@unittest.skipUnless(shutil.which("iverilog"), ...)`` would still skip
silently in the one CI job meant to run it. This test scans the unit-test
trees (``sim/tests``, ``layout/tests``) by AST and fails on any ``which()``
call whose argument is one of ``_tool_gate.GATED_TOOLS`` outside the helper
itself -- whether it sits directly in a skip decorator or is hoisted into a
module constant first. Other skips (data artifacts, git, the PDK, klayout)
are out of scope and not flagged.
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _tool_gate as gate  # noqa: E402

REPO_ROOT = HERE.parents[1]
TREES = (REPO_ROOT / "sim" / "tests", REPO_ROOT / "layout" / "tests")
HELPER = HERE / "_tool_gate.py"


def raw_tool_probes(source: str, filename: str = "<source>") -> list[tuple[int, str]]:
    """``(line, tool)`` for every ``which("<gated tool>")`` call in ``source``."""
    found = []
    for node in ast.walk(ast.parse(source, filename=filename)):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        arg = node.args[0]
        if (name == "which" and isinstance(arg, ast.Constant)
                and arg.value in gate.GATED_TOOLS):
            found.append((node.lineno, arg.value))
    return found


class ScannerSelfTests(unittest.TestCase):
    """The scanner must catch the patterns it exists to forbid."""

    def test_flags_a_raw_skipunless_on_iverilog(self):
        src = ('import shutil, unittest\n'
               '@unittest.skipUnless(shutil.which("iverilog") and shutil.which("vvp"), "x")\n'
               'class T(unittest.TestCase):\n    pass\n')
        self.assertEqual(raw_tool_probes(src), [(2, "iverilog"), (2, "vvp")])

    def test_flags_a_hoisted_probe_and_a_bare_which(self):
        src = ('from shutil import which\nimport shutil\n'
               'NG = shutil.which("ngspice")\nIV = which("iverilog")\n')
        self.assertEqual(sorted(raw_tool_probes(src)), [(3, "ngspice"), (4, "iverilog")])

    def test_ignores_the_helper_call_and_ungated_tools(self):
        src = ('import shutil\nfrom _tool_gate import requires_tools\n'
               '@requires_tools("iverilog", "vvp", reason="x")\nclass T: pass\n'
               'GIT = shutil.which("git")\n# shutil.which("ngspice") in a comment\n')
        self.assertEqual(raw_tool_probes(src), [])


class ToolGateDisciplineTests(unittest.TestCase):
    maxDiff = None

    def test_no_test_file_probes_a_gated_tool_itself(self):
        offenders = []
        for tree in TREES:
            for path in sorted(tree.glob("*.py")):
                if path.resolve() == HELPER:
                    continue
                for line, tool in raw_tool_probes(path.read_text(encoding="utf-8"), str(path)):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{line}: which({tool!r})")
        self.assertEqual(
            offenders, [],
            "gate these through sim/tests/_tool_gate.py's requires_tools() so "
            "REQUIRE_RTL_TOOLS=1 can turn a missing tool into a failure",
        )

    def test_the_trees_scanned_exist(self):
        for tree in TREES:
            self.assertTrue(tree.is_dir(), tree)


if __name__ == "__main__":
    unittest.main()
