#!/usr/bin/env python3
"""Offline tests for ``sim/tools/starved_hot_corner.py`` (issue #628).

No ngspice, no PDK, no ``klt``, no network. They cover the declared request
(committed file equals the grid), the estimator definitions against the
family's ``tb.json``, the refusal paths of record ingestion, and that a
synthetic report round-trips through the record reader that
``sim/tools/starved_cell_jitter_energy.py`` uses.
"""

from __future__ import annotations

import json
import math
import random
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))

import starved_hot_corner as hc  # noqa: E402

TB = json.loads((SIM_DIR / "tb" / "ro-ring5-starved-jitter-long" / "tb.json").read_text())


def synth_unit(seed: int, period: float = 3.78e-9, jit: float = 4e-13) -> dict:
    rng = random.Random(seed)
    t, tc = 6e-9, []
    for _ in range(hc.N_EDGES):
        tc.append(t)
        t += period + rng.gauss(0, jit)
    m = {"tc": tc}
    m["qw0"], m["qw1"], m["vsup_avg"] = 1e-9 * 0.1, 1e-9 * 0.6, 3.63
    return m


def corner(m: dict, status: str = "pass") -> dict:
    ms = [{"name": k, "value": v} for k, v in m.items() if k != "tc"]
    ms += [{"name": hc.edge_name(k), "value": t} for k, t in enumerate(m.get("tc", []))]
    return {"status": status, "runtime_s": 1.0, "measurements": ms}


class RequestTests(unittest.TestCase):
    def test_committed_request_matches_grid(self):
        self.assertEqual(hc.request_path().read_text(), hc.render(hc.build_request()))

    def test_grid_is_one_hot_corner_eight_units(self):
        req = hc.build_request()
        self.assertEqual(req["corners"]["temperature_c"], [125])
        self.assertEqual([p["name"] for p in req["corners"]["process"]], ["ss"])
        sv = req["corners"]["supply_v"]
        self.assertEqual(sv["vsup"], [3.63] * 8)
        self.assertEqual(sv["vseed"], [float(i) for i in range(1, 9)])

    def test_measurement_cards(self):
        ms = {m["name"]: m for m in hc.build_request()["measurements"]}
        self.assertEqual(len(ms), 769 + 3)
        self.assertTrue(ms["tc_0"]["spice"].endswith("rise=2"))
        self.assertIn("rise=770", ms["tc_768"]["spice"])
        for m in ms.values():
            self.assertEqual(sum(k in m for k in ("spice", "expr", "crossings")), 1)
            self.assertNotIn("crossings", m)
        self.assertIn("rise=258", ms["qw0"]["spice"])
        self.assertIn("rise=770", ms["qw1"]["spice"])

    def test_run_is_long_enough_for_the_window(self):
        # 770 crossings at the slowest corner period this request targets (3.78 ns)
        self.assertGreater(float(hc.TSTOP.rstrip("u")) * 1e-6, 770 * 3.78e-9)

    def test_geometry_matches_tb_json(self):
        self.assertIn(f"let tc = vector({hc.N_EDGES})", TB["analyses"])
        self.assertEqual(sorted(hc.MEASURE_ORDER), sorted(TB["measure"]))


class EstimatorTests(unittest.TestCase):
    def test_exact_on_a_pure_period(self):
        m = {"tc": [1e-9 + k * 2e-9 for k in range(hc.N_EDGES)]}
        m.update(qw0=0.0, qw1=-1e-9, vsup_avg=3.63)
        d = hc.derive(m)
        self.assertAlmostEqual(d["period"], 2e-9, delta=1e-21)
        for lag in hc.LAGS:
            self.assertLess(d[f"sigma_{lag}"], 1e-20)
        self.assertAlmostEqual(d["i_ring_a"], 1e-9 * 1e-9 / (512 * 2e-9), delta=1e-18)

    def test_lag_sigma_definition(self):
        u = synth_unit(1)
        d = hc.derive(u)
        tc = u["tc"]
        tbar = (tc[768] - tc[256]) / 512
        r = [(tc[i + 4] - tc[i]) - 4 * tbar for i in range(256, 765)]
        self.assertEqual(len(r), 509)
        want = math.sqrt(sum(x * x for x in r) / 509 / (1 - 4 / 512))
        self.assertAlmostEqual(d["sigma_4"], want, delta=want * 1e-12)

    def test_startup_window_uses_16_periods(self):
        u = synth_unit(2)
        d = hc.derive(u)
        tc = u["tc"]
        tbars = (tc[16] - tc[0]) / 16
        r = [(tc[i + 8] - tc[i]) - 8 * tbars for i in range(0, 9)]
        want = math.sqrt(sum(x * x for x in r) / 9 / (1 - 8 / 16))
        self.assertAlmostEqual(d["sigma_startup16_8"], want, delta=want * 1e-12)

    def test_white_jitter_accumulates_as_sqrt_lag(self):
        ds = [hc.derive(synth_unit(s)) for s in range(1, 9)]
        s1 = sum(d["sigma_1"] for d in ds) / 8
        s64 = sum(d["sigma_64"] for d in ds) / 8
        self.assertAlmostEqual(math.log(s64 / s1) / math.log(64), 0.5, delta=0.1)

    def test_all_family_measures_present(self):
        self.assertEqual(set(hc.derive(synth_unit(3))), set(TB["measure"]))


class IngestTests(unittest.TestCase):
    def report(self, units):
        return {"corners": [corner(u) for u in units], "environment": {"engine_version": "46"},
                "provenance": {"klt_version": "test", "pdk": {"version": "x"}}}

    def ingest(self, report):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "r.json").write_text(json.dumps(report))
            recs = td / "records"
            recs.mkdir()
            rc = hc.cmd_ingest(td / "r.json", None, None, recs)
            files = sorted(p.name for p in recs.glob("*.md"))
            text = (recs / files[0]).read_text() if files else ""
            return rc, text

    def test_wrong_unit_count_refused(self):
        rc, text = self.ingest(self.report([synth_unit(1)] * 3))
        self.assertEqual((rc, text), (2, ""))

    def test_failed_unit_refused(self):
        rep = self.report([synth_unit(s) for s in range(1, 9)])
        rep["corners"][3]["status"] = "error"
        self.assertEqual(self.ingest(rep)[0], 2)

    def test_missing_primitive_refused(self):
        units = [synth_unit(s) for s in range(1, 9)]
        del units[2]["qw1"]
        self.assertEqual(self.ingest(self.report(units))[0], 2)

    def test_run_too_short_for_the_window_refused(self):
        units = [synth_unit(s) for s in range(1, 9)]
        units[4]["tc"] = units[4]["tc"][:640]
        self.assertEqual(self.ingest(self.report(units))[0], 2)

    def test_duplicated_realization_refused(self):
        units = [synth_unit(s) for s in range(1, 8)] + [synth_unit(1)]
        self.assertEqual(self.ingest(self.report(units))[0], 2)

    def test_good_report_writes_parseable_record(self):
        rc, text = self.ingest(self.report([synth_unit(s) for s in range(1, 9)]))
        self.assertEqual(rc, 0)
        self.assertIn("process: ss", text)
        self.assertIn("temperature: 125", text)
        self.assertIn("voltage: 3.630 V", text)
        self.assertIn("seeds: [1, 2, 3, 4, 5, 6, 7, 8]", text)
        for name in TB["measure"]:
            self.assertRegex(text, rf"(?m)^- `{name}`: mean \S+ over 8 seeds \(sd \S+")


if __name__ == "__main__":
    unittest.main()
