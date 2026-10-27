#!/usr/bin/env python3
"""Unit tests for ``run_sta``'s `klt sta` envelope comparison (#699).

Stdlib only: synthetic records and a synthetic response, no PDK, no openroad,
no klt. The committed comparison against the real records is re-run by
``run_sta.py --klt-sta``.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(SIM_DIR / "tb" / "digital-sta-power"))

import run_sta  # noqa: E402


def _record(lib: str, rc: str, setup: str, hold: str) -> str:
    return (
        f"  liberty: gf180mcu_fd_sc_mcu9t5v0__{lib}\n"
        f"  interconnect: {rc} (OpenRCX rule deck)\n"
        f"- `worst_setup_slack_ns`: {setup}\n"
        f"- `worst_hold_slack_ns`: {hold}\n"
    )


class RecordSlacksTest(unittest.TestCase):
    def test_newest_record_per_point_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "2026-09-01-digital-sta-power-01.md").write_text(
                _record("ss_125C_3v00", "min", "1.0e+00", "2.0e+00"))
            (d / "2026-10-01-digital-sta-power-01.md").write_text(
                _record("ss_125C_3v00", "min", "3.0e+01", "4.0e-01"))
            (d / "2026-10-01-other-01.md").write_text(
                _record("ss_125C_3v00", "min", "9", "9"))
            self.assertEqual(
                run_sta.record_slacks(d), {("ss_125C_3v00", "min"): (30.0, 0.4)})


class CompareEnvelopeTest(unittest.TestCase):
    def test_rows_pair_each_corner_with_its_record(self):
        response = {"corners": [{
            "corner": "ss_125C_3v00", "interconnect_corner": "max",
            "timing_status": "constrained",
            "worst_slack_ns": 31.2203, "worst_hold_slack_ns": 2.3831,
        }]}
        rows = run_sta.compare_envelope(
            response, {("ss_125C_3v00", "max"): (31.2203, 2.3831)})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["record_setup_ns"], 31.2203)
        self.assertEqual(rows[0]["timing_status"], "constrained")

    def test_missing_record_is_an_error_not_a_skip(self):
        response = {"corners": [{
            "corner": "tt_025C_3v30", "interconnect_corner": "nom",
            "timing_status": "constrained",
            "worst_slack_ns": 1.0, "worst_hold_slack_ns": 1.0,
        }]}
        with self.assertRaises(KeyError):
            run_sta.compare_envelope(response, {})


if __name__ == "__main__":
    unittest.main()
