#!/usr/bin/env python3
"""Malformed-number handling (#529) and ratified-rate defaults (#491) in
``sim/tools/time_to_first_valid.py``.

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


class RatifiedRateTests(unittest.TestCase):
    """The default rate is the ratified Raw rate row (issue #491) and the
    latency model keeps the health-test and conditioner windows
    non-overlapping. Reads the committed start-up records; no simulation."""

    def run_main(self, *args: str) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = ttfv.main(list(args))
        return code, out.getvalue()

    def test_default_rate_is_two_kbps(self) -> None:
        # DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy §1.
        self.assertEqual(ttfv.RATIFIED_RAW_RATE_BPS, 2000.0)
        self.assertAlmostEqual(ttfv.README_FLOOR_S, 0.640)

    def test_digital_terms_do_not_overlap(self) -> None:
        b = ttfv.budget(2000.0)
        self.assertAlmostEqual(
            b["digital_total_s"], b["sampler_s"] + b["health_test_s"] + b["conditioner_s"])
        self.assertAlmostEqual(b["digital_total_s"], 1281 / 2000.0)

    def test_default_matches_explicit_2000_and_check_passes(self) -> None:
        code_d, out_d = self.run_main("--check")
        code_e, out_e = self.run_main("--check", "--rate", "2000")
        self.assertEqual((code_d, code_e), (0, 0))
        self.assertEqual(out_d, out_e)
        self.assertRegex(out_d, r"TIME-TO-FIRST-VALID\s*: 640\.5 ms")
        self.assertIn("the ratified Raw rate row", out_d)
        self.assertNotIn("OVERRIDDEN", out_d)

    def test_total_is_oscillator_startup_plus_digital_terms(self) -> None:
        records = ttfv.dedupe_by_corner(ttfv.load_startup_records())
        results = [ttfv.CornerResult(r, 0.01) for r in records]
        worst = max(r.t_startup for r in results if r.converged)
        total = worst + ttfv.budget(2000.0)["digital_total_s"]
        self.assertGreater(total, ttfv.README_FLOOR_S)
        self.assertLess(worst, 1e-6)  # oscillator start-up is nanoseconds

    def test_historical_rate_is_explicit_and_labelled(self) -> None:
        code, out = self.run_main("--rate", "1e6")
        self.assertEqual(code, 0)
        self.assertIn("OVERRIDDEN via --rate", out)
        self.assertRegex(out, r"TIME-TO-FIRST-VALID\s*: 1\.281 ms")
        self.assertIn("Historical", out)

    def test_impossible_rate_is_rejected(self) -> None:
        for rate in ("0", "-1", "nan", "inf", "x"):
            with self.subTest(rate=rate), self.assertRaises(SystemExit) as ctx:
                with contextlib.redirect_stderr(io.StringIO()):
                    ttfv.main(["--rate", rate])
            self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
