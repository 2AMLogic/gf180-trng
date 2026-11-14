#!/usr/bin/env python3
"""Unit tests for `layout/_klt.py`.

Two helpers are covered. `_run_klt()`'s subprocess plumbing -- specifically
the `FlowError` raised when a `klt ... --format json` invocation's
stdout/stderr is non-empty but does not parse as JSON (issue #196) -- and
`_ensure_openroad_reachable()`'s three provisioning branches (issue #892,
which moved that helper here out of byte-identical copies in
`layout/digital/build.py` and `layout/digital/gen_sdf.py`).

Both sets run against mocked `subprocess.run` / `shutil.which`, so they need
neither `klt`, `openroad`, `docker` nor an installed PDK -- the point is the
*error message construction* and the branch logic, not a live tool run.
`layout/tests/test_verify.py` follows the identical no-tool-needed pattern
for `layout/verify.py`.

Motivation (#196): before this change, a `json.JSONDecodeError` discarded
the raw pre-strip stdout/stderr once it decided the output was unparseable,
so a real occurrence in CI (an unhandled `KeyError('area')` traceback from a
klayout-tools bug, printed to stderr in place of the documented `{"error":
...}` envelope) surfaced only as "emitted unparseable JSON: Expecting value:
line 1 column 1 (char 0)" -- true, but not diagnosable without reproducing
the failure from scratch. The fix echoes a bounded prefix of the offending
raw output into the `FlowError` message instead.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from layout._klt import (  # noqa: E402
    FlowError,
    _ensure_openroad_reachable,
    _run_klt,
)


def _completed(*, stdout: str = "", stderr: str = "", returncode: int = 0):
    return subprocess.CompletedProcess(
        args=["klt"], returncode=returncode, stdout=stdout, stderr=stderr
    )


class UnparseableJsonMessageTests(unittest.TestCase):
    """`_run_klt()` must surface *what* failed to parse, not just that
    parsing failed -- the #196 traceback-vs-stray-log-line distinction."""

    def test_traceback_on_stderr_is_echoed_in_the_error(self):
        traceback_text = (
            "Traceback (most recent call last):\n"
            '  File "run_synthesize.py", line 572, in run_synthesize\n'
            "    \"area_um2\": module_stats[\"area\"],\n"
            "KeyError: 'area'\n"
        )
        with mock.patch(
            "subprocess.run",
            return_value=_completed(stderr=traceback_text, returncode=1),
        ):
            with self.assertRaises(FlowError) as ctx:
                _run_klt(["synthesize", "request.json"])
        message = str(ctx.exception)
        self.assertIn("emitted unparseable JSON", message)
        self.assertIn("Traceback (most recent call last):", message)
        self.assertIn("KeyError: 'area'", message)

    def test_long_raw_output_is_truncated_not_dropped(self):
        long_stdout = "x" * 5000
        with mock.patch(
            "subprocess.run", return_value=_completed(stdout=long_stdout)
        ):
            with self.assertRaises(FlowError) as ctx:
                _run_klt(["synthesize", "request.json"])
        message = str(ctx.exception)
        self.assertIn("x" * 2000, message)
        self.assertNotIn("x" * 2001, message)
        self.assertIn("truncated", message)

    def test_empty_output_still_reports_no_output_not_a_parse_error(self):
        """Unaffected sibling path: still distinct from the unparseable-JSON
        message this change touches."""
        with mock.patch(
            "subprocess.run", return_value=_completed(returncode=3)
        ):
            with self.assertRaises(FlowError) as ctx:
                _run_klt(["synthesize", "request.json"])
        message = str(ctx.exception)
        self.assertIn("produced no output", message)
        self.assertNotIn("unparseable JSON", message)


def _which(**installed: str):
    """Return a `shutil.which` stand-in that only knows `installed`.

    `_ensure_openroad_reachable()` asks for exactly two names (`openroad`,
    then `docker`); anything not named here answers "not installed".
    """

    def which(name, *args, **kwargs):
        return installed.get(name)

    return which


class EnsureOpenroadReachableTests(unittest.TestCase):
    """`_ensure_openroad_reachable()`'s three branches (#892).

    This is the one copy `layout/digital/build.py` and
    `layout/digital/gen_sdf.py` both call, and its documented contract is
    that it mutates `os.environ["PATH"]` process-wide. So every test here
    restores the entry `PATH` and removes any shim directory the helper
    created -- no `openroad`, `docker`, or PDK install needed, matching the
    no-tool pattern the `_run_klt()` tests above use.
    """

    def setUp(self):
        self._entry_path = os.environ["PATH"]
        self._shim_dirs = []

    def tearDown(self):
        os.environ["PATH"] = self._entry_path
        for shim_dir in self._shim_dirs:
            shutil.rmtree(shim_dir, ignore_errors=True)

    def test_native_openroad_wins_and_leaves_path_untouched(self):
        """A real local install always wins -- no shim, no `$PATH` edit."""
        with mock.patch(
            "shutil.which", _which(openroad="/usr/local/bin/openroad",
                                   docker="/usr/bin/docker")
        ):
            self.assertEqual(_ensure_openroad_reachable(), [])
        self.assertEqual(os.environ["PATH"], self._entry_path)

    def test_neither_openroad_nor_docker_reports_one_reason(self):
        with mock.patch("shutil.which", _which()):
            reasons = _ensure_openroad_reachable()
        self.assertEqual(len(reasons), 1)
        self.assertIn("openroad is not on PATH", reasons[0])
        self.assertIn("docker is not on PATH either", reasons[0])
        self.assertIn("layout/digital/README.md", reasons[0])
        self.assertEqual(os.environ["PATH"], self._entry_path)

    def test_docker_only_prepends_a_shim_pointed_at_openroad_docker_sh(self):
        with mock.patch("shutil.which", _which(docker="/usr/bin/docker")):
            self.assertEqual(_ensure_openroad_reachable(), [])

        entries = os.environ["PATH"].split(os.pathsep)
        shim_dir = Path(entries[0])
        self._shim_dirs.append(shim_dir)

        # Prepended, and nothing else about `$PATH` disturbed.
        self.assertEqual(entries[1:], self._entry_path.split(os.pathsep))
        self.assertTrue(shim_dir.name.startswith("klt-openroad-shim-"))

        shim = shim_dir / "openroad"
        self.assertTrue(shim.is_symlink())
        self.assertEqual(
            shim.readlink(), REPO_ROOT / "layout" / "openroad_docker.sh"
        )


if __name__ == "__main__":
    unittest.main()
