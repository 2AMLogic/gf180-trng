#!/usr/bin/env python3
"""Hold sim/tools/unused_names.py to its documented contract (#494).

Each case feeds a small source fixture to the semantic core
(`check_source`), so nothing here depends on the state of the real tree;
file discovery is exercised over an injectable listing and a throwaway git
repository. Stdlib only.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))

import unused_names as un  # noqa: E402


def found(src: str, path: str = "m.py") -> list[tuple[int, str, str]]:
    findings = un.check_source(textwrap.dedent(src), path)
    return [(f.line, f.code, f.name) for f in findings]


class Reported(unittest.TestCase):
    def test_unused_import_is_f401(self):
        self.assertEqual(found("import os\nimport sys\nsys.exit\n"),
                         [(1, "F401", "os")])

    def test_unused_from_import_and_alias(self):
        self.assertEqual(
            found("from os import path as p, sep\nsep\n"),
            [(1, "F401", "path as p")])

    def test_unused_dotted_import_binds_first_component(self):
        self.assertEqual(found("import os.path\n"), [(1, "F401", "os.path")])
        self.assertEqual(found("import os.path\nos.getcwd()\n"), [])

    def test_unused_function_local_is_f841(self):
        self.assertEqual(found("""\
            def f():
                x = 1
                return 2
            """), [(2, "F841", "x")])

    def test_annassign_and_async_and_chained(self):
        self.assertEqual(found("""\
            async def f():
                a: int = 1
                b = c = 2
            """), [(2, "F841", "a"), (3, "F841", "b"), (3, "F841", "c")])

    def test_unused_import_inside_function(self):
        self.assertEqual(found("def f():\n    import os\n"), [(2, "F401", "os")])

    def test_diagnostic_text_and_deterministic_order(self):
        src = "import b\nimport a\ndef f():\n    z = 1\n"
        out = [f.format() for f in un.check_source(src, "pkg/m.py")]
        self.assertEqual(out, [
            "pkg/m.py:1:7: F401 'b' imported but unused",
            "pkg/m.py:2:7: F401 'a' imported but unused",
            "pkg/m.py:4:4: F841 'z' local variable is assigned to but never used",
        ])
        self.assertEqual(out, [f.format() for f in un.check_source(src, "pkg/m.py")])


class Used(unittest.TestCase):
    def test_ordinary_uses(self):
        self.assertEqual(found("""\
            import os
            def f():
                x = 1
                return x, os
            """), [])

    def test_annotation_use(self):
        self.assertEqual(found("""\
            from typing import Optional, Sequence
            import decimal
            def f(a: Optional[int]) -> "Sequence[int]":
                v: decimal.Decimal = a
                return v
            """), [])

    def test_annotation_use_under_future_annotations(self):
        self.assertEqual(found("""\
            from __future__ import annotations
            from typing import Callable
            class C:
                build: Callable[[], int]
                def m(self, cb: Callable) -> None: ...
            """), [])

    def test_decorator_and_default_use(self):
        self.assertEqual(found("""\
            import functools
            DEFAULT = 3
            @functools.cache
            def f(a=DEFAULT):
                return a
            """), [])

    def test_nested_closure_use(self):
        self.assertEqual(found("""\
            def outer():
                x = 1
                def inner():
                    return x
                return inner
            """), [])

    def test_closure_two_levels_down(self):
        self.assertEqual(found("""\
            def outer():
                x = 1
                def mid():
                    def inner():
                        return x
                    return inner
                return mid
            """), [])

    def test_module_import_used_only_in_function(self):
        self.assertEqual(found("import os\ndef f():\n    return os\n"), [])

    def test_comprehension_use(self):
        self.assertEqual(found("""\
            import math
            def f(items):
                scale = 2
                return [math.sqrt(i) * scale for i in items]
            """), [])

    def test_comprehension_use_in_nested_function(self):
        self.assertEqual(found("""\
            def f():
                s = 1
                def g():
                    return [s for _ in range(3)]
                return g
            """), [])

    def test_comprehension_variable_does_not_count_for_outer_name(self):
        self.assertEqual(found("""\
            def f(items):
                i = 1
                return [i for i in items]
            """), [(2, "F841", "i")])

    def test_inner_scope_shadowing_is_not_a_use(self):
        self.assertEqual(found("""\
            def f():
                x = 1
                def g(x):
                    return x
                return g
            """), [(2, "F841", "x")])

    def test_inner_assignment_shadowing_is_not_a_use(self):
        self.assertEqual(found("""\
            import os
            def f():
                os = 1
                return os
            """), [(1, "F401", "os")])

    def test_shadowing_does_not_hide_a_real_use_below(self):
        self.assertEqual(found("""\
            def f():
                x = 1
                def g():
                    x = 2
                    return x
                def h():
                    return x
                return g, h
            """), [])

    def test_augmented_assign_and_del_count_as_use(self):
        self.assertEqual(found("""\
            def f():
                n = 0
                n += 1
                t = 1
                del t
            """), [])

    def test_class_scope_is_separate_from_function_scope(self):
        self.assertEqual(found("""\
            def f():
                x = 1
                class C:
                    x = 2
                    y = x
                return C
            """), [(2, "F841", "x")])


class Exclusions(unittest.TestCase):
    def test_literal_all_reexport(self):
        self.assertEqual(found("""\
            from a import b, c
            __all__ = ["b"]
            """), [(1, "F401", "c")])
        self.assertEqual(found("from a import b\n__all__ = ('b',)\n"), [])
        self.assertEqual(found("from a import b\n__all__: list = ['b']\n"), [])
        self.assertEqual(found("from a import b\n__all__ = []\n__all__ += ['b']\n"), [])

    def test_non_literal_all_is_not_trusted(self):
        self.assertEqual(found("from a import b\n__all__ = make()\n"),
                         [(1, "F401", "b")])

    def test_future_import(self):
        self.assertEqual(found("from __future__ import annotations\n"), [])

    def test_star_import(self):
        self.assertEqual(found("from os import *\n"), [])

    def test_init_py(self):
        self.assertEqual(found("import os\n", "pkg/__init__.py"), [])
        self.assertEqual(found("import os\n", "pkg/mod.py"), [(1, "F401", "os")])

    def test_init_py_still_checks_locals(self):
        self.assertEqual(found("def f():\n    x = 1\n", "pkg/__init__.py"),
                         [(2, "F841", "x")])

    def test_underscore_names(self):
        self.assertEqual(found("""\
            import _os
            from a import b as _b
            def f():
                _x = 1
                __y = 2
            """), [])

    def test_noqa_forms(self):
        self.assertEqual(found("""\
            import a  # noqa
            import b  # noqa: F401
            import c  # NOQA:F401,E402
            import d  # noqa: E402, F401
            import e  # noqa: E402
            import f  # noqa : F841
            def g():
                x = 1  # noqa
                y = 2  # noqa: F841
                z = 3  # noqa: F401
            """), [(5, "F401", "e"), (6, "F401", "f"), (10, "F841", "z")])

    def test_noqa_in_string_is_not_a_comment(self):
        self.assertEqual(found("import os; s = '# noqa'\n"), [(1, "F401", "os")])

    def test_noqa_scope_is_the_statement(self):
        self.assertEqual(found("""\
            from a import (  # noqa: F401
                b,
                c,
            )
            from d import (
                e,  # noqa: F401
                f,
            )
            def g():
                x = (
                    1  # noqa: F841
                )
                y = 2
            """), [(7, "F401", "f"), (13, "F841", "y")])


class Unsupported(unittest.TestCase):
    def test_unsupported_assignment_forms_are_not_reported(self):
        self.assertEqual(found("""\
            def f(items, mgr):
                a, b = items
                [c, d] = items
                (e, *g) = items
                for i in items:
                    pass
                with mgr as w:
                    pass
                try:
                    pass
                except ValueError as exc:
                    pass
                match items:
                    case [p, q]:
                        pass
                    case {"k": r}:
                        pass
                    case str() as s:
                        pass
                if (h := len(items)):
                    pass
                obj.attr = 1
                items[0] = 2
                x: int
            """), [])

    def test_module_and_class_assignments_are_not_f841(self):
        self.assertEqual(found("x = 1\nclass C:\n    y = 2\n"), [])

    def test_parameter_and_global_and_nonlocal_are_skipped(self):
        self.assertEqual(found("""\
            G = 0
            def f(p):
                global G
                G = 1
                p = 2
            def outer():
                n = 0
                def inner():
                    nonlocal n
                    n = 1
                return inner
            """), [])


class DynamicNamespace(unittest.TestCase):
    def test_each_dynamic_call_skips_its_block(self):
        for call in ("exec", "eval", "globals", "locals", "vars"):
            with self.subTest(call=call):
                self.assertEqual(found(f"""\
                    def f():
                        x = 1
                        {call}("pass")
                    """), [])

    def test_module_dynamic_call_skips_module_imports_only(self):
        self.assertEqual(found("""\
            import os
            eval("1")
            def f():
                x = 1
            """), [(4, "F841", "x")])

    def test_function_dynamic_call_does_not_hide_other_blocks(self):
        self.assertEqual(found("""\
            import os
            def f():
                x = 1
                return locals()
            def g():
                y = 1
            class C:
                def m(self):
                    z = 1
            """), [(1, "F401", "os"), (6, "F841", "y"), (9, "F841", "z")])

    def test_dynamic_call_in_nested_block_does_not_skip_the_parent(self):
        self.assertEqual(found("""\
            def f():
                x = 1
                def g():
                    return eval("2")
                return g
            """), [(2, "F841", "x")])

    def test_dynamic_call_in_lambda_or_comprehension_is_its_own_block(self):
        self.assertEqual(found("""\
            def f():
                x = 1
                return lambda: eval("2")
            """), [(2, "F841", "x")])

    def test_attribute_call_is_not_direct(self):
        self.assertEqual(found("""\
            def f(m):
                x = 1
                m.eval("1")
            """), [(2, "F841", "x")])


class Failures(unittest.TestCase):
    def test_syntax_error_is_a_checker_error_with_context(self):
        with self.assertRaises(un.CheckerError) as cm:
            un.check_source("x = 1\ndef f(:\n", "bad.py")
        self.assertEqual(cm.exception.path, "bad.py")
        self.assertEqual(cm.exception.line, 2)
        self.assertIn("bad.py:2", str(cm.exception))

    def test_ambiguous_block_match_fails_closed(self):
        with self.assertRaises(un.CheckerError) as cm:
            un.check_source("class A: pass; class A: pass\n", "dup.py")
        self.assertIn("dup.py:1", str(cm.exception))

    def test_decorated_and_multiline_defs_match(self):
        self.assertEqual(found("""\
            import functools
            class C:
                @functools.cache
                def m(
                    self,
                ):
                    x = 1
            """), [(7, "F841", "x")])


class Discovery(unittest.TestCase):
    def test_select_files_scope_and_order(self):
        listing = [
            "sim/z.py", "sim/a.py", "sim/notes.md", "design/d.py",
            "layout/l.py", "signoff/s.py", "docs/x.py", "setup.py",
            ".loom/scripts/t.py", ".claude/x.py", ".agents/y.py",
            "sim/.venv/lib/site-packages/p.py", "sim/records/raw.txt",
            "sim/a.py",
        ]
        self.assertEqual(un.select_files(listing), [
            "design/d.py", "layout/l.py", "signoff/s.py", "sim/a.py", "sim/z.py"])

    def _git_repo(self, root: Path) -> None:
        def git(*a):
            subprocess.run(["git", "-C", str(root), *a], check=True,
                           capture_output=True)
        git("init", "-q")
        (root / "sim").mkdir()
        (root / ".loom").mkdir()
        (root / "sim" / "tracked.py").write_text("import os\n")
        (root / "sim" / "untracked.py").write_text("import sys\n")
        (root / ".loom" / "tooling.py").write_text("import json\n")
        git("add", "sim/tracked.py")
        git("-c", "user.name=t", "-c", "user.email=t@example.invalid",
            "add", "-f", ".loom/tooling.py")

    def test_only_tracked_first_party_files_are_scanned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._git_repo(root)
            files = un.select_files(un.tracked_files(root))
            self.assertEqual(files, ["sim/tracked.py"])
            findings = un.check_files(root, files)
            self.assertEqual([(f.path, f.code, f.name) for f in findings],
                             [("sim/tracked.py", "F401", "os")])

    def test_cli_exit_codes_and_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._git_repo(root)
            cmd = [sys.executable, "-m", "sim.tools.unused_names", "--check",
                   "--root", str(root)]
            repo = SIM_DIR.parent
            bad = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
            self.assertEqual(bad.returncode, 1, bad.stderr)
            self.assertIn("sim/tracked.py:1:", bad.stdout)
            self.assertIn("F401 'os'", bad.stdout)
            (root / "sim" / "tracked.py").write_text("import os\nos.getcwd()\n")
            ok = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
            (root / "sim" / "tracked.py").write_text("def f(:\n")
            err = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
            self.assertEqual(err.returncode, 2)
            self.assertIn("sim/tracked.py:1: checker error", err.stderr)


if __name__ == "__main__":
    unittest.main()
