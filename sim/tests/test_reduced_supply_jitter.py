#!/usr/bin/env python3
"""Tests for the reduced-supply starved-ring jitter family (issue #831).

Offline: no ngspice, no PDK, no ``klt``. They hold three things:

1. the reduced-supply records are kept OUT of the corner mean, so the published
   four-corner constants (asymptotic 10.932, lag-1 23.255) and the array-sizing
   constant (7.32 at ``ss/-40/3.63``) are exactly what they were;
2. the reduced-supply records are all readable, each is scaled by a same-corner
   noise record, and each passes the same seed-spread ``--check``;
3. the multi-supply request/ingest path of ``starved_hot_corner.py`` splits a
   report by measured supply and refuses a unit whose run was too short.
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import starved_cell_jitter_energy as sc  # noqa: E402
import starved_hot_corner as hc  # noqa: E402
import test_starved_hot_corner as th  # noqa: E402

REDSUP = [hc.GRIDS[n] for n in sorted(hc.GRIDS) if hc.GRIDS[n] is not hc.HOT_GRID]


class CornerMeanUnchanged(unittest.TestCase):
    def test_published_constants_do_not_move(self):
        points, _ = sc.load_points()
        self.assertEqual(len(points), 4)
        asym = sum(p.a(p.kappa2_asym) for p in points) / len(points)
        lag1 = sum(p.a(p.kappa2_lag1) for p in points) / len(points)
        self.assertAlmostEqual(asym, 10.932, places=3)
        self.assertAlmostEqual(lag1, 23.255, places=3)

    def test_sizing_constant_unchanged(self):
        self.assertAlmostEqual(sc.sizing_constant().value, 7.322, places=3)

    def test_reduced_supply_records_are_not_in_the_mean(self):
        mean_corners = {p.rec.corner for p in sc.load_points()[0]}
        reduced = sc.load_reduced_supply_points()
        self.assertFalse(mean_corners & {p.rec.corner for p in reduced})
        self.assertFalse(sc.JITTER_GLOB == sc.REDSUP_GLOB)
        for p in sc.load_points()[0]:
            self.assertNotIn("redsup", p.rec.stem)


class ReducedSupplyRecords(unittest.TestCase):
    def test_five_points_at_the_declared_corners(self):
        got = {p.rec.corner for p in sc.load_reduced_supply_points()}
        self.assertEqual(got, set(sc.REDSUP_COMPARATOR))

    def test_each_has_eight_seeds_and_a_comparator(self):
        by = {p.rec.corner for p in sc.load_points()[0]}
        for p in sc.load_reduced_supply_points():
            self.assertEqual(p.rec.seeds, 8)
            self.assertIn(sc.REDSUP_COMPARATOR[p.rec.corner], by)

    def test_check_passes_with_reduced_supply_gated(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sc.main(["--check", "--reduced-supply"]), 0)


class MultiSupplyRequests(unittest.TestCase):
    def test_committed_requests_match_grids(self):
        for g in hc.GRIDS.values():
            self.assertEqual(g.request_path.read_text(), hc.render(hc.build_request(g)), g.name)

    def test_baseline_request_has_no_batch_block(self):
        self.assertNotIn("batch", hc.build_request(hc.HOT_GRID))

    def test_reduced_requests_wait_for_capacity(self):
        for g in REDSUP:
            self.assertEqual(hc.build_request(g)["batch"], {"capacity_wait_s": 600})

    def test_units_and_supplies(self):
        for g in REDSUP:
            sv = hc.build_request(g)["corners"]["supply_v"]
            self.assertEqual(len(sv["vsup"]), 8 * len(g.supplies))
            self.assertEqual(sorted(set(sv["vsup"])), sorted(g.supplies))

    def test_run_covers_the_window(self):
        # probed ring periods (s) at each point; 770 edges plus ~8 ns start-up
        period = {("ss", 3.30): 4.23e-9, ("ss", 2.97): 4.85e-9,
                  ("ff", 3.30): 1.63e-9, ("ff", 2.97): 1.80e-9, ("tt", 2.97): 2.90e-9}
        for g in REDSUP:
            for v in g.supplies:
                need = 770 * period[(g.process, v)] + 8e-9
                self.assertGreater(float(g.tstop.rstrip("u")) * 1e-6, need * 1.1, (g.name, v))


class MultiSupplyIngest(unittest.TestCase):
    GRID = hc.GRIDS["ring5-redsup-ss125"]

    def report(self, units):
        return {"corners": [th.corner(m) for m in units],
                "provenance": {"klt_version": "test", "pdk": {"version": "x"}}}

    def units(self):
        out = []
        for i, v in enumerate(self.GRID.supplies):
            for s in range(1, 9):
                m = th.synth_unit(100 * i + s, period=4.5e-9)
                m["vsup_avg"] = v
                out.append(m)
        return out

    def ingest(self, units, order=None):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "r.json").write_text(json.dumps(self.report(units)))
            recs = td / "records"
            recs.mkdir()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc = hc.cmd_ingest(td / "r.json", None, None, recs, grid=self.GRID)
            return rc, {f.name: f.read_text() for f in sorted(recs.glob("*.md"))}

    def test_split_into_one_record_per_supply(self):
        rc, files = self.ingest(self.units())
        self.assertEqual(rc, 0)
        self.assertEqual(len(files), 2)
        for (name, text), v in zip(files.items(), self.GRID.supplies):
            self.assertIn(f"voltage: {v:.3f} V", text)
            self.assertIn("process: ss", text)
            self.assertIn("-redsup-", name)
            self.assertRegex(text, r"(?m)^- `period`: mean \S+ over 8 seeds")

    def test_unit_order_is_not_trusted(self):
        u = self.units()
        rc, files = self.ingest(u[::2] + u[1::2])
        self.assertEqual((rc, len(files)), (0, 2))

    def test_unbalanced_supplies_refused(self):
        u = self.units()
        u[0]["vsup_avg"] = self.GRID.supplies[1]
        self.assertEqual(self.ingest(u), (2, {}))

    def test_too_short_run_at_low_supply_refused_not_averaged(self):
        u = self.units()
        u[-1]["tc"] = u[-1]["tc"][:700]
        self.assertEqual(self.ingest(u), (2, {}))


if __name__ == "__main__":
    unittest.main()
