#!/usr/bin/env python3
"""Unit tests for ``sim/tools/jitter_estimator_calibration_check.py`` record
selection (issue #427).

With no record named on the command line, the tool reads the newest
``jitter-estimator-calibration`` record. These tests build synthetic records
in a temporary directory, patch the module's ``RECORDS`` and ``REPO_ROOT``,
and check:

1. ``latest_record`` skips a record whose frontmatter says
   ``status: superseded`` before choosing the newest one, reports a
   superseded-only family as missing evidence, and rejects a missing,
   unknown or duplicated ``status:`` with an error naming the record;
2. ``include_superseded=True`` is the explicit historical read;
3. a record named on the command line is read as given, whatever its
   lifecycle, while automatic selection still skips superseded records.

Stdlib only: no ngspice, no PDK, no committed record is read.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SIM_DIR / "tools"))

import jitter_estimator_calibration_check as jc  # noqa: E402


def record_text(status: str | None, *, body: str = "") -> str:
    """A record whose measured P(bit=1) hits every level's target exactly."""
    head = "---\n" + ("" if status is None else f"status: {status}\n") + "---\n\n## Result\n\n"
    bullets = "".join(
        f"- `{name}`: {jc.p1_target(h)!r}\n" for name, h in jc.LEVELS
    )
    return head + body + bullets


class CalibrationSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.records = self.root / "sim" / "records"
        self.records.mkdir(parents=True)
        for name, value in (("REPO_ROOT", self.root), ("RECORDS", self.records)):
            p = mock.patch.object(jc, name, value)
            p.start()
            self.addCleanup(p.stop)

    def write(self, day: int, status: str | None, *, body: str = "") -> Path:
        path = self.records / f"2026-01-0{day}-{jc.SLUG}-01.md"
        path.write_text(record_text(status, body=body))
        return path

    def run_main(self, *args: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = jc.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_lexically_newer_superseded_record_is_not_selected(self) -> None:
        valid = self.write(1, "valid")
        self.write(2, "superseded")
        self.assertEqual(jc.latest_record(), valid)

    def test_historical_read_selects_the_superseded_record(self) -> None:
        self.write(1, "valid")
        newer = self.write(2, "superseded")
        self.assertEqual(jc.latest_record(include_superseded=True), newer)

    def test_superseded_only_family_is_missing_evidence(self) -> None:
        self.write(1, "superseded")
        with self.assertRaisesRegex(jc.RecordError, "no valid record"):
            jc.latest_record()
        code, _out, err = self.run_main("--check")
        self.assertEqual(code, 2)
        self.assertIn("no valid record", err)

    def test_empty_directory_is_missing_evidence(self) -> None:
        with self.assertRaisesRegex(jc.RecordError, "no committed record"):
            jc.latest_record()

    def test_body_status_line_does_not_override_frontmatter(self) -> None:
        path = self.write(1, "valid", body="Quoted:\n\nstatus: superseded\n\n")
        self.assertEqual(jc.latest_record(), path)

    def test_missing_unknown_and_duplicate_status_name_the_record(self) -> None:
        for status in (None, "draft", "valid\nstatus: valid"):
            with self.subTest(status=status):
                path = self.write(1, status)
                with self.assertRaisesRegex(jc.RecordError, path.stem):
                    jc.latest_record()

    def test_automatic_selection_reports_the_valid_record(self) -> None:
        valid = self.write(1, "valid")
        self.write(2, "superseded")
        code, out, err = self.run_main("--check")
        self.assertEqual(code, 0, err)
        self.assertIn(f"record: sim/records/{valid.name}", out)

    def test_explicitly_named_superseded_record_is_read_as_given(self) -> None:
        self.write(1, "valid")
        newer = self.write(2, "superseded")
        for arg in (newer.stem, str(newer)):
            with self.subTest(arg=arg):
                code, out, err = self.run_main(arg, "--check")
                self.assertEqual(code, 0, err)
                self.assertIn(f"record: sim/records/{newer.name}", out)


if __name__ == "__main__":
    unittest.main()
