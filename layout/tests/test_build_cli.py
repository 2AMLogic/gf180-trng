#!/usr/bin/env python3
"""Unit tests for `layout/cells/_build_cli.py`'s message contract (issue #601).

The module's docstring declares the `MISSING:` / `STALE:` / `ok:` /
`SKIP-AS-STALE:` / `SKIP:` / `FAIL:` lines a contract that committed evidence
and docs quote. These tests drive the public factories with injected fake
`build` / `klt_version` / `resolve_pdk` hooks and assert the return code and
the exact printed line for each branch. No PDK or `klt` is needed.
"""

from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from sim.tools.pathload import load_module_from_path  # noqa: E402

cli = load_module_from_path(
    "layout_tests_build_cli", LAYOUT_DIR / "cells" / "_build_cli.py"
)

SCRIPT = "layout/cells/x/build.py"


def run(fn, *args):
    """Call `fn`, returning (return code, stdout lines)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = fn(*args)
    return rc, out.getvalue().splitlines()


class TempDirCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def shown(self, path):
        return os.path.relpath(str(path), os.getcwd())


class GdsFileTest(unittest.TestCase):
    def test_path(self):
        self.assertEqual(
            cli.gds_file("some/dir", "top"), os.path.join("some/dir", "top.gds")
        )


class MakeCheckTest(TempDirCase):
    def setUp(self):
        super().setUp()
        self.gds = self.dir / "cell.gds"
        self.scratch = Path(str(self.gds) + ".check")

    def make(self, build):
        return cli.make_check(
            gds_path=lambda: str(self.gds), build=build, script=SCRIPT
        )

    def test_missing(self):
        rc, lines = run(self.make(lambda p: b""))
        self.assertEqual(rc, 1)
        self.assertEqual(
            lines, [f"MISSING: {self.shown(self.gds)} -- run `python3 {SCRIPT}`"]
        )

    def test_ok_and_scratch_removed(self):
        self.gds.write_bytes(b"abc")

        def build(path):
            Path(path).write_bytes(b"abc")
            return b"abc"

        rc, lines = run(self.make(build))
        self.assertEqual(rc, 0)
        self.assertEqual(lines, [f"ok: {self.shown(self.gds)}"])
        self.assertFalse(self.scratch.exists())

    def test_stale_reports_counts_and_hint(self):
        self.gds.write_bytes(b"abc")

        def build(path):
            Path(path).write_bytes(b"abcdef")
            return b"abcdef"

        rc, lines = run(self.make(build))
        self.assertEqual(rc, 1)
        self.assertEqual(
            lines,
            [
                f"STALE: {self.shown(self.gds)} does not match build.py "
                f"(3 bytes committed, 6 rebuilt) -- run `python3 {SCRIPT}`"
            ],
        )
        self.assertFalse(self.scratch.exists())

    def test_scratch_removed_when_build_raises(self):
        self.gds.write_bytes(b"abc")

        def build(path):
            Path(path).write_bytes(b"partial")
            raise RuntimeError("boom")

        with self.assertRaises(RuntimeError):
            run(self.make(build))
        self.assertFalse(self.scratch.exists())


class MakeMainTest(TempDirCase):
    def make(self, check, build):
        return cli.make_main(
            check=check,
            gds_path=lambda: "out.gds",
            build=build,
            description="desc",
        )

    def test_check_delegates(self):
        built = []
        main = self.make(lambda: 7, lambda: built.append(1))
        rc, lines = run(main, ["--check"])
        self.assertEqual((rc, lines, built), (7, [], []))

    def test_default_builds_and_reports(self):
        built = []
        main = self.make(lambda: 7, lambda: built.append(1))
        rc, lines = run(main, [])
        self.assertEqual(rc, 0)
        self.assertEqual(lines, ["wrote out.gds"])
        self.assertEqual(built, [1])


class MakePdkCheckTest(TempDirCase):
    def setUp(self):
        super().setUp()
        self.gds = self.dir / "top.gds"
        self.calls = []

    def make(self, pdk, rebuilt=b"abc"):
        def build(variant, scratch):
            self.calls.append((variant, scratch))
            return rebuilt

        return cli.make_pdk_check(
            gds_path=lambda: self.gds,
            build=build,
            resolve_pdk=lambda: pdk,
            work_dir=self.dir,
            top_cell="top",
            script=SCRIPT,
        )

    def test_missing(self):
        rc, lines = run(self.make(SimpleNamespace(variant="v")))
        self.assertEqual(rc, 1)
        self.assertEqual(
            lines, [f"MISSING: {self.shown(self.gds)} -- run `python3 {SCRIPT}`"]
        )
        self.assertEqual(self.calls, [])

    def test_no_pdk_skip_as_stale(self):
        self.gds.write_bytes(b"abc")
        rc, lines = run(self.make(None))
        self.assertEqual(rc, 1)
        self.assertEqual(
            lines,
            [f"SKIP-AS-STALE: {self.shown(self.gds)} -- no gf180mcu PDK install found"],
        )
        self.assertEqual(self.calls, [])

    def test_ok(self):
        self.gds.write_bytes(b"abc")
        rc, lines = run(self.make(SimpleNamespace(variant="v")))
        self.assertEqual(rc, 0)
        self.assertEqual(lines, [f"ok: {self.shown(self.gds)}"])
        self.assertEqual(self.calls, [("v", self.dir / "top.check.gds")])

    def test_stale(self):
        self.gds.write_bytes(b"abc")
        rc, lines = run(self.make(SimpleNamespace(variant="v"), rebuilt=b"abcdefg"))
        self.assertEqual(rc, 1)
        self.assertEqual(
            lines,
            [
                f"STALE: {self.shown(self.gds)} does not match build.py "
                f"(3 bytes committed, 7 rebuilt) -- run `python3 {SCRIPT}`"
            ],
        )


class MakePdkMainTest(TempDirCase):
    def make(self, *, version, pdk, check=lambda: 5):
        self.built = []
        return cli.make_pdk_main(
            check=check,
            gds_path=lambda: Path("out/top.gds"),
            build=lambda variant: self.built.append(variant),
            resolve_pdk=lambda: pdk,
            klt_version=lambda: version,
            top_cell="top",
            description="desc",
        )

    PDK = SimpleNamespace(variant="v")

    def test_klt_absent_skips(self):
        rc, lines = run(self.make(version=None, pdk=self.PDK), [])
        self.assertEqual(rc, 0)
        self.assertEqual(
            lines,
            [
                "  - klayout-tools (`klt`) is not on PATH",
                "SKIP: top build -- the tools above are not available.",
            ],
        )
        self.assertEqual(self.built, [])

    def test_pdk_absent_skips(self):
        rc, lines = run(self.make(version="1.0", pdk=None), [])
        self.assertEqual(rc, 0)
        self.assertEqual(
            lines,
            [
                "  - no gf180mcu PDK install found (see sim/harness/pdk.py)",
                "SKIP: top build -- the tools above are not available.",
            ],
        )

    def test_both_absent_lists_both(self):
        rc, lines = run(self.make(version=None, pdk=None), [])
        self.assertEqual(rc, 0)
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].startswith("  - klayout-tools"))
        self.assertTrue(lines[1].startswith("  - no gf180mcu PDK"))

    def test_require_tools_fails_when_absent(self):
        for version, pdk, n in (("1.0", None, 1), (None, self.PDK, 1)):
            rc, lines = run(self.make(version=version, pdk=pdk), ["--require-tools"])
            self.assertEqual(rc, 1)
            self.assertEqual(len(lines), n + 1)
            self.assertEqual(
                lines[-1], "FAIL: --require-tools was given and the flow cannot run"
            )
            self.assertEqual(self.built, [])

    def test_require_tools_with_tools_present_builds(self):
        rc, lines = run(self.make(version="1.0", pdk=self.PDK), ["--require-tools"])
        self.assertEqual(rc, 0)
        self.assertEqual(lines, [f"wrote {Path('out/top.gds')}"])

    def test_check_delegates_when_tools_present(self):
        rc, lines = run(self.make(version="1.0", pdk=self.PDK), ["--check"])
        self.assertEqual((rc, lines, self.built), (5, [], []))

    def test_default_builds_with_variant(self):
        rc, lines = run(self.make(version="1.0", pdk=self.PDK), [])
        self.assertEqual(rc, 0)
        self.assertEqual(lines, [f"wrote {Path('out/top.gds')}"])
        self.assertEqual(self.built, ["v"])


if __name__ == "__main__":
    unittest.main()
