#!/usr/bin/env python3
"""Unit tests for ``run_sta``'s `klt sta` envelope comparison (#699).

Stdlib only: a synthetic response, no PDK, no openroad, no klt. The committed
comparison against the real records is re-run by ``run_sta.py --klt-sta``.

``record_slacks`` no longer parses records itself (#867) -- it maps
``sim/tools/digital_corner_characterization.load()``, the one reader of the
``digital-sta-power`` family, onto the pairs ``compare_envelope`` wants. The
selection rules it inherits (record lifecycle, DUT identity, a complete
fifteen-corner family) are tested against that reader in
``test_digital_corner_characterization.py``; what is tested here is the
mapping, and that the reader's refusal reaches ``run_sta``'s own error path
instead of being swallowed.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(SIM_DIR / "tools"))
sys.path.insert(0, str(SIM_DIR / "tb" / "digital-sta-power"))

import digital_corner_characterization as dcc  # noqa: E402
import run_sta  # noqa: E402


class RecordSlacksTest(unittest.TestCase):
    def test_the_pairs_are_the_one_readers_current_layout_family(self):
        self.assertEqual(
            run_sta.record_slacks(SIM_DIR / "records"),
            {(r.liberty, r.rc): (r.v("worst_setup_slack_ns"), r.v("worst_hold_slack_ns"))
             for r in dcc.load()},
        )

    def test_every_envelope_corner_has_a_pair(self):
        slacks = run_sta.record_slacks(SIM_DIR / "records")
        self.assertEqual(
            sorted(f"{lib}/rc-{rc}" for lib, rc in slacks),
            sorted(dcc.EXPECTED_CORNERS),
        )

    def test_no_records_at_all_is_an_error(self):
        # The pre-#867 reader globbed the directory itself, so it returned an
        # empty map here and the comparison failed later, on a KeyError.
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(run_sta.StaError) as caught:
                run_sta.record_slacks(Path(tmp))
        self.assertIn("digital-sta-power", str(caught.exception))

    def test_an_incomplete_family_is_refused_rather_than_compared(self):
        # The behaviour #867 is after: fourteen of the fifteen points is not a
        # fifteen-point envelope, and saying so names the missing corner. The
        # pre-#867 reader handed back the fourteen without complaint.
        family = sorted(dcc.load(), key=lambda r: r.path.name)
        dropped = family[-1]
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            for rec in family[:-1]:
                (d / rec.path.name).write_bytes(rec.path.read_bytes())
            with self.assertRaises(run_sta.StaError) as caught:
                run_sta.record_slacks(d)
        message = str(caught.exception)
        self.assertIn("14 of 15 corners recorded", message)
        self.assertIn(dropped.corner, message)


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
