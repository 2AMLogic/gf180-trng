#!/usr/bin/env python3
"""Malformed-number handling in ``sim/tools/time_to_first_valid.py`` (#529).

A start-up record whose numeric result bullet is malformed (``1e+``) or
overflows (``1e999``) must make the CLI exit unsuccessfully with an error
naming the record and the bullet key -- never print a result computed from a
truncated value. The module's ``RECORDS`` attribute is patched to a temporary
directory; no committed record is read.

Stdlib only.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import time_to_first_valid as ttfv  # noqa: E402

FRONTMATTER = (
    "---\nrecord: fixture\nstatus: valid\nprocess: tt\n"
    "temperature: 27\nvoltage: 3.3\n---\n\n## Result\n\n"
)


class MalformedNumberCliTests(unittest.TestCase):
    def _run(self, bullet: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "2026-01-01-ro-array-core-startup-01.md").write_text(
                FRONTMATTER + bullet
            )
            err = io.StringIO()
            with (
                mock.patch.object(ttfv, "RECORDS", Path(tmp)),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(err),
            ):
                code = ttfv.main([])
        return code, err.getvalue()

    def test_incomplete_exponent_fails_with_context(self) -> None:
        code, err = self._run("- `period_1`: 1e+\n")
        self.assertNotEqual(code, 0)
        self.assertIn("2026-01-01-ro-array-core-startup-01", err)
        self.assertIn("period_1", err)

    def test_exponent_continuation_fails_with_context(self) -> None:
        for token in ("1e2.3", "1e2e3"):
            with self.subTest(token=token):
                code, err = self._run(f"- `period_1`: {token}\n")
                self.assertNotEqual(code, 0)
                self.assertIn("2026-01-01-ro-array-core-startup-01", err)
                self.assertIn("period_1", err)

    def test_overflow_fails_with_context(self) -> None:
        code, err = self._run("- `period_1`: 1e999\n")
        self.assertNotEqual(code, 0)
        self.assertIn("period_1", err)


if __name__ == "__main__":
    unittest.main()
