#!/usr/bin/env python3
"""Offline tests for the digital power switch evidence tool (issue #707).

No ngspice, no PDK, no ``klt``, no network. They cover:

1. the committed request matching the declared grid and the deck/netlist agreeing with the
   tool's constants (widths, loads, wake cases, DUT subcircuit parameters);
2. the arithmetic on synthetic raw readings where the answer is known by construction;
3. the plausibility checks rejecting a unit that is not a measurement;
4. the committed records: every grid point present once, and the selected switch's off-state
   leakage at the binding corner (and at every other corner) within the recorded limit.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR / "tools"))

import power_switch as ps  # noqa: E402

DECK = ps.TB_DIR / ps.DECK
VDD = 3.3


def synthetic_readings(scale: float = 1.0) -> dict:
    """Raw readings with a 10 ohm / 100 nA / known-inrush switch at every width."""
    v: dict = {}
    for k, w in ps.WIDTH_UM.items():
        ron = 4000.0 / w  # ohm; so 400 um is 10 ohm
        for ld, i_a in ps.LOADS_A.items():
            v[f"droop_{k}{ld}"] = ron * i_a * scale
        v[f"ileak_{k}"] = w * 0.25e-9
    v.update(i_stack=40e-9, v_stack=0.01, i_ungated=2.0e-6)
    for k, (cap, trf) in ps.WAKE_CASES.items():
        v[f"ipk_w{k}"] = cap / trf * VDD
        v[f"t95_w{k}"] = ps.T_WAKE_S + 3.0 * 10.0 * cap
        v[f"vfin_w{k}"] = VDD
    return v


class RequestAndDeck(unittest.TestCase):
    def test_committed_request_matches_the_declared_grid(self) -> None:
        self.assertEqual(ps.cmd_emit(check=True), 0)

    def test_grid_is_the_harness_pvt_grid(self) -> None:
        req = ps.build_request()
        self.assertEqual(ps.n_units(), 45)
        self.assertEqual([p["name"] for p in req["corners"]["process"]], ["tt", "ff", "ss", "fs", "sf"])
        self.assertEqual(req["corners"]["temperature_c"], [-40, 27, 125])
        self.assertEqual(req["corners"]["supply_v"], {"vsup": [2.97, 3.3, 3.63]})

    def test_fleet_request_pins_one_ngspice_thread(self) -> None:
        # Without it the fleet's ngspice-46 did not finish this deck in 120 s and every unit timed out.
        self.assertIn("set num_threads=1", ps.build_request()["options"]["ngspice_init"])

    def test_single_point_probe_is_one_unit(self) -> None:
        req = ps.build_request("ff/125/3.63")
        self.assertEqual(req["corners"]["supply_v"], {"vsup": [3.63]})
        self.assertEqual(req["corners"]["temperature_c"], [125])
        self.assertEqual([p["name"] for p in req["corners"]["process"]], ["ff"])
        with self.assertRaises(ValueError):
            ps.parse_only("ff/125/3.5")

    def test_every_measurement_names_something_the_deck_defines(self) -> None:
        deck = DECK.read_text()
        for m in ps.measurements():
            for node in re.findall(r"[iv]\((\w+)\)", m["spice"]):
                if node == "vdd":
                    continue
                self.assertRegex(deck, rf"(?m)^[a-z]*\s*{re.escape(node)}\b|\b{re.escape(node)}\b")

    def test_deck_widths_loads_and_wake_cases_match_the_tool(self) -> None:
        deck = DECK.read_text()
        for k in ps.WIDTH_UM:
            self.assertRegex(deck, rf"(?m)^xr{k}a .* nfing={10 * k} ")
            self.assertRegex(deck, rf"(?m)^xl{k} .* nfing={10 * k} ")
        self.assertIn(f"iA={ps.LOADS_A['a'] * 1e6:g}u", deck)
        self.assertIn(f"iB={ps.LOADS_A['b'] * 1e3:g}m", deck)
        for k, (cap, _trf) in ps.WAKE_CASES.items():
            self.assertRegex(deck, rf"(?m)^cw{k} vw{k} 0 {cap * 1e12:g}p$")
        self.assertIn(f"nfing={ps.SELECTED_WIDTH_UM // 10} ", deck.split("Group W")[1])

    def test_netlist_defaults_are_the_selected_switch(self) -> None:
        netlist = (REPO_ROOT / "design" / "power_switch.spice").read_text()
        self.assertIn(".subckt power_switch sleep vdd vvdd wf=10u nfing=40 lsw=0.28u", netlist)
        self.assertEqual(40 * 10, ps.SELECTED_WIDTH_UM)

    def test_deck_has_no_time_in_a_behavioural_expression(self) -> None:
        # ngspice-46 on the fleet stalled on this construct; the sleep ramps are PWL sources.
        self.assertNotRegex(re.sub(r"(?m)^\*.*$", "", DECK.read_text()), r"\btime\b")


class Arithmetic(unittest.TestCase):
    def test_on_resistance_is_droop_over_load(self) -> None:
        row = ps.derive(synthetic_readings(), VDD)
        self.assertAlmostEqual(row["ron_ohm_400um_a"], 10.0)
        self.assertAlmostEqual(row["ron_ohm_400um_b"], 10.0)
        self.assertAlmostEqual(row["ron_ohm_100um_b"], 40.0)

    def test_loss_and_percent_follow_from_the_droop(self) -> None:
        row = ps.derive(synthetic_readings(), VDD)
        droop = 10.0 * ps.LOADS_A["b"]
        self.assertAlmostEqual(row["droop_v_400um_b"], droop)
        self.assertAlmostEqual(row["p_loss_w_400um_b"], droop * ps.LOADS_A["b"])
        self.assertAlmostEqual(row["droop_pct_400um_b"], droop / VDD * 100.0)

    def test_leakage_scales_with_width_and_stack_reduction_is_a_ratio(self) -> None:
        row = ps.derive(synthetic_readings(), VDD)
        self.assertAlmostEqual(row["ileak_a_800um"], 2 * row["ileak_a_400um"])
        self.assertAlmostEqual(row["stack_reduction_x"], 2.0e-6 / 40e-9)

    def test_settling_is_counted_from_the_start_of_the_sleep_fall(self) -> None:
        row = ps.derive(synthetic_readings(), VDD)
        self.assertAlmostEqual(row["t_settle_s_50pf_10ns"], 30.0 * 50e-12 * 10.0)
        self.assertAlmostEqual(row["ipk_a_200pf_10ns"], 200e-12 / 10e-9 * VDD)

    def test_a_missing_reading_is_unmeasured_not_zero(self) -> None:
        v = synthetic_readings()
        del v["droop_4b"]
        with self.assertRaises(ps.DerivationError):
            ps.derive(v, VDD)

    def test_report_rows_carry_a_verdict(self) -> None:
        good = {"process": "tt", "temperature_c": 27, "supply_v": {"vsup": VDD}, "status": "pass",
                "measurements": [{"name": k, "value": x} for k, x in synthetic_readings().items()]}
        bad = {"process": "tt", "temperature_c": 27, "supply_v": {"vsup": VDD}, "status": "error",
               "measurements": []}
        rows = ps.analyse_report({"corners": [good, bad]})
        self.assertEqual([r["verdict"] for r in rows], ["OK", "UNMEASURED"])


class Plausibility(unittest.TestCase):
    def test_clean_synthetic_unit_passes(self) -> None:
        self.assertEqual(ps.checks(ps.derive(synthetic_readings(), VDD)), [])

    def test_a_droop_larger_than_half_the_supply_is_suspect(self) -> None:
        self.assertTrue(ps.checks(ps.derive(synthetic_readings(scale=1e4), VDD)))

    def test_a_rail_that_did_not_wake_is_suspect(self) -> None:
        v = synthetic_readings()
        v["vfin_w1"] = 0.5 * VDD
        self.assertTrue(any("did not wake" in p for p in ps.checks(ps.derive(v, VDD))))

    def test_nonpositive_leakage_is_suspect(self) -> None:
        v = synthetic_readings()
        v["ileak_4"] = -1e-12
        self.assertTrue(any("not positive" in p for p in ps.checks(ps.derive(v, VDD))))


class CommittedRecords(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.recs = ps.load_records(ps.REPO_ROOT / "sim" / "records")

    def test_every_grid_point_is_recorded_once(self) -> None:
        got = sorted(ps._label(r) for r in self.recs)
        want = sorted(f"{p}/{t:g}C/{v:.2f}V" for p in ps.PROCESSES for t in ps.TEMPS_C for v in ps.SUPPLIES_V)
        self.assertEqual(got, want)

    def test_off_leakage_of_the_selected_switch_is_within_the_limit_at_every_corner(self) -> None:
        key = f"ileak_a_{ps.SELECTED_WIDTH_UM}um"
        worst = max(r["values"][key] for r in self.recs)
        self.assertLess(worst, ps.OFF_LEAKAGE_LIMIT_A)

    def test_binding_corner_gated_idle_is_a_small_part_of_the_row(self) -> None:
        (binding,) = [r for r in self.recs
                      if (r["corner"][0], float(r["corner"][1]), round(float(r["corner"][2]), 2)) == ps.BINDING]
        analog, _ = ps.analog_idle_a(ps.REPO_ROOT / "sim" / "records")
        self.assertLess(binding["values"]["i_stack_a"] + analog, ps.IDLE_BUDGET_A)

    def test_selected_width_meets_the_droop_yardstick_at_the_bound_load(self) -> None:
        worst = max(r["values"][f"droop_v_{ps.SELECTED_WIDTH_UM}um_b"] for r in self.recs)
        self.assertLess(worst, ps.DROOP_BUDGET_V)

    def test_summary_renders_from_the_records(self) -> None:
        analog, stem = ps.analog_idle_a(ps.REPO_ROOT / "sim" / "records")
        text = ps.summary_text(self.recs, analog, stem)
        self.assertIn("**idle, gated digital + analog**", text)
        self.assertIn("45 records", text)


if __name__ == "__main__":
    unittest.main()
