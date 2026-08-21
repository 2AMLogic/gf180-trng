#!/usr/bin/env python3
"""Unit tests for `layout/_klt.py`'s `_run_klt()` subprocess plumbing --
specifically the `FlowError` raised when a `klt ... --format json`
invocation's stdout/stderr is non-empty but does not parse as JSON (issue
#196).

These exercise `_run_klt()` directly against a mocked `subprocess.run`, so
they need neither `klt` nor an installed PDK -- the point is the *error
message construction*, not a live tool run. `layout/tests/test_verify.py`
follows the identical no-tool-needed pattern for `layout/verify.py`.

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

import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from layout._klt import FlowError, _run_klt  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
