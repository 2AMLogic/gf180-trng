#!/usr/bin/env python3
"""Offline tests for ``sim/tools/fs_sf_capture.py`` (issue #472).

No ngspice, no PDK, no ``klt``, no network. They cover:

1. the declared campaign: the committed requests match the grid, the grid is
   exactly the 18 asymmetric PVT points x the declared phases, the tt control is
   present, and the zipped ``supply_v`` axes are consistent;
2. the pulse-width / duty extraction on synthetic edge trains;
3. the capture checker on hand-built measurement sets: a clean capture, a wrong
   captured bit, an output stuck mid-rail, a reset that does not dominate, a
   raw_valid that never rises, and a missing clock edge -- the checker must flag
   each (this is the negative-control logic, exercised without a simulator);
4. the pooling of phase units into a per-PVT-point outcome, including the rule
   that a missing unit prevents a coverage-complete verdict.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))

import fs_sf_capture as fc  # noqa: E402

VDD = 3.3


def clean_measurements(vdd: float = VDD, phase: float = 0.0, bits=(1, 0, 1)) -> dict[str, float]:
    """A set of readouts that a correct, resolved capture would produce."""
    v: dict[str, float] = {}
    for k in range(fc.N_EDGES):
        v[f"te_{k}"] = fc.edge_nominal_s(k, phase)
        post = k >= 1
        for d in fc.READ_DELAYS_S:
            tag = str(round(d * 1e9))
            v[f"rv_{k}_{tag}"] = vdd if post else 0.0
            v[f"rb_{k}_{tag}"] = (vdd if bits[k - 1] else 0.0) if post else 0.0
        if post:
            level = vdd if bits[k - 1] else 0.0
            v[f"xl_{k}"] = v[f"xm_{k}"] = v[f"xh_{k}"] = level
    return v


def unit(meas: dict[str, float], vdd: float = VDD, phase: float = 0.0, **sv) -> dict:
    supply = {"vsupply": vdd, "vph": phase, "vrel": fc.REL_S, "vthw": fc.THW_S}
    supply.update(sv)
    core = {
        "xo_max": vdd, "xo_min": 0.0, "r1_max": vdd, "r1_min": 0.0, "r2_max": vdd, "r2_min": 0.0,
    }
    for r in (1, 2):
        for i, k in enumerate(fc.RING_EDGE_RANGE):
            core[f"r{r}_rise_{k}"] = 10e-9 + i * 6e-9
            core[f"r{r}_fall_{k}"] = 10e-9 + i * 6e-9 + 3e-9
    for i, k in enumerate(fc.XO_EDGE_RANGE):
        core[f"xo_rise_{k}"] = 10e-9 + i * 3e-9
        core[f"xo_fall_{k}"] = 10e-9 + i * 3e-9 + 1.5e-9
    allm = {**core, **meas}
    return {
        "corner_id": "x", "process": "sf", "temperature_c": 27, "supply_v": supply, "status": "pass",
        "measurements": [{"name": n, "value": x} for n, x in allm.items()],
    }


class TestDeclaredCampaign(unittest.TestCase):
    def test_committed_requests_match_grid(self):
        for name, req in fc.all_requests().items():
            path = fc.request_path(name)
            self.assertTrue(path.exists(), path)
            self.assertEqual(path.read_text(), fc.render(req), f"{name} drifted: run `emit`")

    def test_grid_is_the_eighteen_asymmetric_points(self):
        req = fc.build_request("grid")
        procs = [p["name"] for p in req["corners"]["process"]]
        self.assertEqual(sorted(procs), ["fs", "sf"])
        self.assertEqual(req["corners"]["temperature_c"], [-40, 27, 125])
        self.assertEqual(sorted(set(req["corners"]["supply_v"]["vsupply"])), [2.97, 3.30, 3.63])
        self.assertEqual(fc.n_units("grid"), 18 * len(fc.PHASES_S))
        # every (process, T, V) point carries every declared phase
        rows = list(zip(req["corners"]["supply_v"]["vsupply"], req["corners"]["supply_v"]["vph"]))
        self.assertEqual(len(rows), len(set(rows)))
        for v in fc.SUPPLIES_V:
            self.assertEqual(sorted(p for vv, p in rows if vv == v), sorted(fc.PHASES_S))

    def test_fs_sf_sections_skew_only_the_mos_family(self):
        for p in ("fs", "sf"):
            secs = fc.PROCESS_SECTIONS[p]
            self.assertEqual(secs[0], p)
            self.assertEqual(secs[1:], fc.PROCESS_SECTIONS["tt"][1:])

    def test_control_has_tt_and_negative_controls(self):
        req = fc.build_request("control-tt")
        self.assertEqual([p["name"] for p in req["corners"]["process"]], ["tt"])
        sv = req["corners"]["supply_v"]
        n = len(sv["vsupply"])
        self.assertEqual(n, len(fc.PHASES_S) + len(fc.NEGATIVE_CONTROLS))
        self.assertTrue(all(len(x) == n for x in sv.values()))
        self.assertEqual(sum(1 for r in sv["vrel"] if r > 0.9), 1)
        self.assertEqual(sum(1 for w in sv["vthw"] if w < 1e-9), 1)

    def test_phases_fit_before_the_first_read(self):
        # the +8 ns read must come after the latest phase-shifted edge has completed
        self.assertGreater(fc.READ_DELAYS_S[0], max(fc.PHASES_S) + fc.TR_S)

    def test_reset_release_is_between_edge0_and_edge1(self):
        self.assertGreater(fc.REL_S, fc.TCLK0_S + max(fc.PHASES_S) + fc.TR_S)
        self.assertLess(fc.REL_S, fc.TCLK0_S + fc.TCLK_S)

    def test_ring_windows_end_before_edge0(self):
        self.assertLess(290e-9, fc.TCLK0_S)

    def test_measurement_names_unique(self):
        names = [m["name"] for m in fc.measurements()]
        self.assertEqual(len(names), len(set(names)))


class TestPulseWidths(unittest.TestCase):
    def test_duty_from_interleaved_edges(self):
        rises = [0.0, 10.0, 20.0, 30.0]
        falls = [3.0, 13.0, 23.0, 33.0]
        hi, lo = fc.pulse_widths(rises, falls)
        self.assertEqual(hi, [3.0] * 4)
        self.assertEqual(lo, [7.0] * 3)

    def test_unordered_and_starting_with_a_fall(self):
        hi, lo = fc.pulse_widths([5.0, 15.0], [0.5, 8.0, 18.0])
        self.assertEqual(lo, [4.5, 7.0])
        self.assertEqual(hi, [3.0, 3.0])


class TestCaptureChecker(unittest.TestCase):
    def test_clean_capture_is_ok(self):
        u = fc.analyse_unit(unit(clean_measurements()))
        self.assertEqual(u["fails"], [])
        self.assertEqual(u["verdict"], "OK")
        self.assertEqual(u["n_decisive"], 3)
        self.assertEqual(u["ones"], 2)

    def test_wrong_captured_bit_is_a_miss(self):
        m = clean_measurements()
        for d in fc.READ_DELAYS_S:  # xo was high (1), sampler holds 0
            m[f"rb_1_{round(d * 1e9)}"] = 0.0
        u = fc.analyse_unit(unit(m))
        self.assertEqual(u["verdict"], "FUNCTIONAL_MISS")
        self.assertTrue(any("captured 0 but xo" in f for f in u["fails"]))

    def test_unresolved_output_is_a_miss(self):
        m = clean_measurements()
        m["rb_2_50"] = m["rb_2_300"] = 1.6  # parked near mid-rail
        u = fc.analyse_unit(unit(m))
        self.assertEqual(u["verdict"], "FUNCTIONAL_MISS")
        self.assertTrue(any("not at a rail" in f for f in u["fails"]))

    def test_slow_drift_is_a_miss(self):
        m = clean_measurements()
        m["rb_3_50"] = 3.0  # moving toward the rail, 0.3 V short at +50 ns
        u = fc.analyse_unit(unit(m))
        self.assertTrue(any("drifts" in f or "not at a rail" in f for f in u["fails"]))

    def test_reset_must_dominate_a_clock_edge(self):
        m = clean_measurements()
        for d in fc.READ_DELAYS_S:
            m[f"rv_0_{round(d * 1e9)}"] = VDD  # raw_valid rose under reset
        u = fc.analyse_unit(unit(m))
        self.assertEqual(u["verdict"], "FUNCTIONAL_MISS")
        self.assertTrue(any("not low under reset" in f for f in u["fails"]))

    def test_reset_never_released_is_caught(self):
        m = clean_measurements()
        for k in range(1, fc.N_EDGES):
            for d in fc.READ_DELAYS_S:
                m[f"rv_{k}_{round(d * 1e9)}"] = 0.0
                m[f"rb_{k}_{round(d * 1e9)}"] = 0.0
        u = fc.analyse_unit(unit(m, vrel=1.0))
        self.assertEqual(u["verdict"], "FUNCTIONAL_MISS")
        self.assertTrue(any("raw_valid" in f and "not high" in f for f in u["fails"]))

    def test_missing_clock_edge_is_caught(self):
        m = clean_measurements()
        for k in range(fc.N_EDGES):
            del m[f"te_{k}"]
            if k:
                for n in ("xl", "xm", "xh"):
                    del m[f"{n}_{k}"]
        u = fc.analyse_unit(unit(m, vthw=20e-12))
        self.assertEqual(u["verdict"], "FUNCTIONAL_MISS")
        self.assertTrue(any("no clock crossing" in f for f in u["fails"]))

    def test_aperture_sample_is_checked_for_resolution_not_value(self):
        m = clean_measurements()
        m["xl_1"], m["xm_1"], m["xh_1"] = 0.0, 1.6, VDD  # xo transiting the edge
        m["rb_1_50"] = m["rb_1_300"] = m["rb_1_8"] = 0.0  # either bit is acceptable
        u = fc.analyse_unit(unit(m))
        self.assertEqual(u["verdict"], "OK")
        self.assertEqual(u["n_in_aperture"], 1)
        self.assertEqual(u["n_decisive"], 2)

    def test_edge_time_off_nominal_is_flagged(self):
        m = clean_measurements()
        m["te_2"] += 1e-9
        u = fc.analyse_unit(unit(m))
        self.assertTrue(any("nominal" in f for f in u["fails"]))

    def test_low_swing_is_a_miss(self):
        u = unit(clean_measurements())
        for x in u["measurements"]:
            if x["name"] == "xo_max":
                x["value"] = 0.5 * VDD
        self.assertEqual(fc.analyse_unit(u)["verdict"], "FUNCTIONAL_MISS")

    def test_missing_core_measurements_are_unmeasured(self):
        u = {"corner_id": "x", "supply_v": {"vsupply": VDD}, "status": "error", "measurements": []}
        self.assertEqual(fc.analyse_unit(u)["verdict"], "UNMEASURED")

    def test_duty_outside_band_is_flagged_not_failed(self):
        u = unit(clean_measurements())
        for x in u["measurements"]:
            if x["name"].startswith("r1_fall_"):
                x["value"] -= 2.5e-9  # duty 0.5 -> ~0.083
        r = fc.analyse_unit(u)
        self.assertEqual(r["verdict"], "FLAGGED")
        self.assertTrue(any("duty" in f for f in r["flags"]))

    def test_negative_controls_are_classified_caught(self):
        self.assertTrue(fc.classify_negative({"verdict": "FUNCTIONAL_MISS"}))
        self.assertFalse(fc.classify_negative({"verdict": "OK"}))


class TestPooling(unittest.TestCase):
    def _pt(self, n_units=4, drop=0, miss=False):
        out = []
        for i in range(n_units):
            m = clean_measurements(phase=fc.PHASES_S[i % len(fc.PHASES_S)])
            u = fc.analyse_unit(unit(m, phase=fc.PHASES_S[i % len(fc.PHASES_S)]))
            u["process"], u["temperature_c"], u["vdd"] = "sf", 27, VDD
            out.append(u)
        for u in out[:drop]:
            u["verdict"] = "UNMEASURED"
        if miss:
            out[-1]["verdict"] = "FUNCTIONAL_MISS"
        return out

    def test_complete_point_is_ok(self):
        (p,) = fc.pool_points(self._pt())
        self.assertEqual(p["verdict"], "OK")
        self.assertEqual(p["decisive"], 12)

    def test_missing_unit_prevents_a_complete_verdict(self):
        (p,) = fc.pool_points(self._pt(drop=1))
        self.assertEqual(p["verdict"], "UNMEASURED")

    def test_functional_miss_dominates(self):
        (p,) = fc.pool_points(self._pt(miss=True))
        self.assertEqual(p["verdict"], "FUNCTIONAL_MISS")

    def test_too_few_decisive_samples_is_insufficient_coverage(self):
        us = self._pt(n_units=1)
        (p,) = fc.pool_points(us)
        self.assertEqual(p["verdict"], "INSUFFICIENT_COVERAGE")

    def test_rows_render(self):
        rows = fc.point_rows(fc.pool_points(self._pt()))
        self.assertEqual(len(rows), 1)
        self.assertIn("| sf | 27 | 3.30 | OK |", rows[0])


if __name__ == "__main__":
    unittest.main()
