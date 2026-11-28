#!/usr/bin/env python3
"""Hold sim/tools/testimport_guard.py to its contract (#1085).

`python3 -m unittest sim/tests/<file>.py` imports a test module as
sim.tests.<name> from the repository root, where sim/tests is not on
sys.path; `npm test` adds that directory for every module, so one that
forgot its own insert passes every suite there (#1082). The guard has to
see what the root-level form sees, module by module. Every case builds a
throwaway sim/tests package under a temporary directory and calls check()
on an explicit file listing; the CLI is exercised against a throwaway git
repository. Nothing depends on the real tree except the final
guard-on-this-tree and package.json cases. Stdlib only.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR / "tools"))

import testimport_guard as guard  # noqa: E402

# Puts sim/tests on sys.path the way a well-formed module does, then imports
# the sibling helper. The second body omits the insert: #1082's defect.
REACHABLE = """\
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # sim/tests: _helper
import _helper
"""
UNREACHABLE = "import _helper\n"


class Tree:
    """A throwaway repository root holding a sim/tests package."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.tests = root / "sim" / "tests"
        self.tests.mkdir(parents=True)
        (self.tests / "__init__.py").write_text("")
        (self.tests / "_helper.py").write_text("VALUE = 1\n")
        self.files = ["sim/tests/__init__.py", "sim/tests/_helper.py"]

    def test(self, name: str, body: str) -> str:
        """Write sim/tests/<name>.py, list it, and return its repository path."""
        rel = f"sim/tests/{name}.py"
        (self.root / rel).write_text(textwrap.dedent(body))
        self.files.append(rel)
        return rel


class TestModules(unittest.TestCase):
    def test_only_direct_test_modules_map_to_sim_tests_name(self):
        files = ["sim/tests/test_b.py", "sim/tests/sub/test_c.py",
                 "sim/tests/_helper.py", "sim/tests/test_a.py",
                 "sim/tests/test_d.txt", "sim/tools/test_e.py"]
        self.assertEqual(guard.test_modules(files), [
            ("sim/tests/test_a.py", "sim.tests.test_a"),
            ("sim/tests/test_b.py", "sim.tests.test_b"),
        ])


class Check(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tree = Tree(Path(tmp.name))

    def findings(self, timeout: float = guard.TIMEOUT_S) -> list[str]:
        return guard.check(self.tree.root, self.tree.files, timeout)

    def test_reachable_sibling_passes(self):
        self.tree.test("test_okay", REACHABLE)
        self.assertEqual(self.findings(), [])

    def test_unreachable_sibling_is_named(self):
        self.tree.test("test_broken", UNREACHABLE)
        found = self.findings()
        self.assertEqual(found, [
            "sim/tests/test_broken.py:1: ModuleNotFoundError: No module named '_helper'",
        ])

    def test_fails_after_a_module_that_inserts_sim_tests(self):
        # Regression for the single-process form of this check. test_aaa puts
        # sim/tests on sys.path and imports the sibling; imported in one
        # process, it would make test_broken's import succeed too. Measured
        # on main before #1084: 96 of 96 importable in one process, 92 of 96
        # one interpreter per module.
        self.tree.test("test_aaa", REACHABLE + "assert _helper.VALUE == 1\n")
        self.tree.test("test_broken", UNREACHABLE)
        found = self.findings()
        self.assertEqual(len(found), 1, found)
        self.assertIn("sim/tests/test_broken.py", found[0])

    def test_each_module_is_imported_by_its_own_interpreter(self):
        body = ("import os\n"
                "from pathlib import Path\n"
                "Path(__file__).with_suffix('.pid').write_text(str(os.getpid()))\n")
        self.tree.test("test_one", body)
        self.tree.test("test_two", body)
        self.assertEqual(self.findings(), [])
        pids = {(self.tree.tests / f"test_{n}.pid").read_text()
                for n in ("one", "two")}
        self.assertEqual(len(pids), 2)
        self.assertNotIn(str(os.getpid()), pids)

    def test_ambient_pythonpath_does_not_stand_in_for_a_missing_insert(self):
        self.tree.test("test_broken", UNREACHABLE)
        with mock.patch.dict(os.environ, {"PYTHONPATH": str(self.tree.tests)}):
            found = self.findings()
        self.assertEqual(len(found), 1, found)

    def test_every_failing_module_is_listed(self):
        self.tree.test("test_one", UNREACHABLE)
        self.tree.test("test_two", UNREACHABLE)
        found = self.findings()
        self.assertEqual([line.split(":")[0] for line in found],
                         ["sim/tests/test_one.py", "sim/tests/test_two.py"])

    def test_exception_beyond_import_error_is_reported_with_its_line(self):
        self.tree.test("test_boom", "X = 1\nraise RuntimeError('boom')\n")
        self.assertEqual(self.findings(),
                         ["sim/tests/test_boom.py:2: RuntimeError: boom"])

    def test_system_exit_at_import_is_reported(self):
        self.tree.test("test_exit", "import sys\nsys.exit(3)\n")
        self.assertEqual(self.findings(),
                         ["sim/tests/test_exit.py:2: SystemExit: 3"])

    def test_syntax_error_is_reported(self):
        self.tree.test("test_bad", "def f(:\n")
        found = self.findings()
        self.assertEqual(len(found), 1, found)
        self.assertTrue(found[0].startswith("sim/tests/test_bad.py:1: SyntaxError"),
                        found)

    def test_output_at_import_cannot_forge_a_verdict(self):
        # The module prints exactly what the child's own verdict line looks
        # like, and then text with no trailing newline that would glue itself
        # onto it; then it fails on its sibling import.
        forged = repr(f"{guard.TAG}\tok\t\t\t")
        body = f"print({forged})\nprint('partial', end='')\nimport _helper\n"
        self.tree.test("test_noisy", body)
        found = self.findings()
        self.assertEqual(len(found), 1, found)
        self.assertIn("ModuleNotFoundError", found[0])

    def test_a_module_that_prints_at_import_passes(self):
        self.tree.test("test_chatty", "print('loading fixtures')\n" + REACHABLE)
        self.tree.test("test_terse", "print('partial', end='')\n" + REACHABLE)
        self.assertEqual(self.findings(), [])

    def test_output_from_a_subprocess_or_atexit_does_not_hide_a_pass(self):
        # A child process writes a partial line to the inherited stdout during
        # import, and a callback prints after the import ends.
        self.tree.test("test_progress",
                       "import subprocess, sys\n"
                       "subprocess.run([sys.executable, '-c', \"print('loading', end='')\"], check=True)\n"
                       + REACHABLE)
        self.tree.test("test_cleanup",
                       "import atexit\natexit.register(print, 'cleanup complete')\n"
                       + REACHABLE)
        self.assertEqual(self.findings(), [])

    def test_genuine_failure_is_reported_despite_subprocess_and_atexit_output(self):
        body = ("import atexit, subprocess, sys\n"
                "subprocess.run([sys.executable, '-c', \"print('loading', end='')\"], check=True)\n"
                "atexit.register(print, 'cleanup complete')\n"
                "import _helper\n")
        self.tree.test("test_noisy_broken", body)
        self.assertEqual(self.findings(), [
            "sim/tests/test_noisy_broken.py:4: ModuleNotFoundError: "
            "No module named '_helper'"])

    def test_import_that_does_not_return_is_a_failure(self):
        self.tree.test("test_hang", "import time\ntime.sleep(30)\n")
        found = self.findings(timeout=1.0)
        self.assertEqual(found,
                         ["sim/tests/test_hang.py: import did not finish within 1 s"])

    def test_child_exit_without_a_verdict_is_a_failure(self):
        # Status 0 without a verdict line is not a pass.
        self.tree.test("test_vanish", "import os\nos._exit(0)\n")
        found = self.findings()
        self.assertEqual(len(found), 1, found)
        self.assertIn("sim/tests/test_vanish.py: import process exited with status 0 "
                      "without reporting a verdict", found[0])


class Cli(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.tree = Tree(self.root)
        self.git = ["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(self.git[:3] + ["init", "-q"], check=True)

    def run_guard(self, root: Path | None = None) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = guard.main(["--check", "--root", str(root or self.root)])
        return code, out.getvalue(), err.getvalue()

    def test_exit_codes_and_output(self):
        tracked = self.tree.test("test_tracked", "print('loading fixtures')\n" + REACHABLE)
        # Broken, but not tracked: not this guard's to judge, like the nested
        # module below, which no root-level invocation imports as sim.tests.*.
        self.tree.test("test_untracked", UNREACHABLE)
        nested = self.tree.tests / "sub"
        nested.mkdir()
        (nested / "test_nested.py").write_text(UNREACHABLE)
        subprocess.run(self.git + ["add", "sim/tests/test_tracked.py", "sim/tests/sub"],
                       check=True)

        code, out, err = self.run_guard()
        self.assertEqual((code, err), (0, ""))
        self.assertIn("OK (1 module(s) imported", out)
        self.assertNotIn("loading fixtures", out)

        (self.root / tracked).write_text(UNREACHABLE)
        code, out, err = self.run_guard()
        self.assertEqual(code, 1, err)
        self.assertEqual(out,
                         "sim/tests/test_tracked.py:1: ModuleNotFoundError: "
                         "No module named '_helper'\n")
        self.assertIn("testimport_guard: 1 of 1 module(s)", err)

    def test_root_outside_a_git_repository_exits_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err = self.run_guard(Path(tmp))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("testimport_guard: git ls-files", err)

    def test_repository_without_test_modules_exits_2(self):
        subprocess.run(self.git + ["add", "-A"], check=True)
        code, out, err = self.run_guard()
        self.assertEqual((code, out), (2, ""))
        self.assertIn("no tracked sim/tests/test_*.py", err)


class Main(unittest.TestCase):
    def test_this_tree_is_clean(self):
        self.assertEqual(guard.main(["--check"]), 0)

    def test_wired_into_lint_script(self):
        scripts = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertIn("python3 -m sim.tools.testimport_guard --check", scripts["lint"])


if __name__ == "__main__":
    unittest.main()
