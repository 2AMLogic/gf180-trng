#!/usr/bin/env python3
"""Hold sim/tools/pathload.py and its lint guard to their contract (#553).

Every case writes throwaway modules under a temporary directory; nothing
depends on the state of the real tree except the final guard-on-this-tree
case. Stdlib only.
"""

from __future__ import annotations

import pickle
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))

import pathload  # noqa: E402
import pathload_guard as guard  # noqa: E402


class LoadModuleFromPath(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        self.name = "pathload_test_module"
        sys.modules.pop(self.name, None)
        self.addCleanup(sys.modules.pop, self.name, None)

    def write(self, body: str, fname: str = "build.py") -> Path:
        p = self.dir / fname
        p.write_text(textwrap.dedent(body))
        return p

    def test_returns_executed_module_registered_under_name(self):
        mod = pathload.load_module_from_path(self.name, self.write("X = 3\n"))
        self.assertEqual(mod.X, 3)
        self.assertIs(sys.modules[self.name], mod)

    def test_registered_before_exec(self):
        mod = pathload.load_module_from_path(self.name, self.write(
            "import sys\nSEEN = sys.modules.get(__name__)\n"))
        self.assertIs(mod.SEEN, mod)

    def test_dataclass_and_pickle_work(self):
        mod = pathload.load_module_from_path(self.name, self.write("""
            from dataclasses import dataclass

            @dataclass
            class P:
                x: int = 1
            """))
        self.assertEqual(pickle.loads(pickle.dumps(mod.P(5))), mod.P(5))

    def test_same_basename_distinct_modules(self):
        (self.dir / "a").mkdir()
        (self.dir / "b").mkdir()
        a = pathload.load_module_from_path("pl_a", self.write("V = 'a'\n", "a/build.py"))
        b = pathload.load_module_from_path("pl_b", self.write("V = 'b'\n", "b/build.py"))
        self.addCleanup(sys.modules.pop, "pl_a", None)
        self.addCleanup(sys.modules.pop, "pl_b", None)
        self.assertEqual((a.V, b.V), ("a", "b"))

    def test_failed_exec_removes_registration(self):
        p = self.write("raise RuntimeError('boom')\n")
        with self.assertRaisesRegex(RuntimeError, "boom"):
            pathload.load_module_from_path(self.name, p)
        self.assertNotIn(self.name, sys.modules)

    def test_failed_exec_restores_preexisting_entry(self):
        sentinel = object()
        sys.modules[self.name] = sentinel
        p = self.write("raise RuntimeError('boom')\n")
        with self.assertRaises(RuntimeError):
            pathload.load_module_from_path(self.name, p)
        self.assertIs(sys.modules[self.name], sentinel)

    def test_missing_file_is_a_clear_error(self):
        with self.assertRaisesRegex(FileNotFoundError, "pathload_test_module"):
            pathload.load_module_from_path(self.name, self.dir / "nope.py")
        self.assertNotIn(self.name, sys.modules)

    def test_no_spec_is_a_clear_error(self):
        # An unrecognised suffix gives importlib no loader to build a spec from.
        p = self.write("X = 1\n", "data.txt")
        with self.assertRaisesRegex(ImportError, "no import spec or loader"):
            pathload.load_module_from_path(self.name, p)
        self.assertNotIn(self.name, sys.modules)


class Guard(unittest.TestCase):
    def test_detects_call_import_and_reference_but_not_text(self):
        self.assertTrue(guard.uses_loader(
            "import importlib.util\nimportlib.util.spec_from_file_location('a', 'b')\n"))
        self.assertTrue(guard.uses_loader(
            "from importlib.util import spec_from_file_location\n"))
        self.assertFalse(guard.uses_loader(
            '"""mentions spec_from_file_location"""\n# spec_from_file_location\n'))

    def test_new_copy_outside_allowlist_fails(self):
        out = guard.problems({"layout/new.py"}, frozenset())
        self.assertEqual(len(out), 1)
        self.assertIn("layout/new.py", out[0])

    def test_helper_itself_is_exempt(self):
        self.assertEqual(guard.problems({guard.HELPER}, frozenset()), [])

    def test_stale_allowlist_entry_fails(self):
        out = guard.problems(set(), frozenset({"layout/old.py"}))
        self.assertEqual(len(out), 1)
        self.assertIn("stale", out[0])

    def test_listed_user_passes(self):
        self.assertEqual(guard.problems({"a.py"}, frozenset({"a.py"})), [])

    def test_this_tree_is_clean(self):
        self.assertEqual(guard.main(["--check"]), 0)


if __name__ == "__main__":
    unittest.main()
