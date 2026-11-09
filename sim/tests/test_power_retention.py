#!/usr/bin/env python3
"""Offline tests for the retention / measured-idle evidence tool (issue #790).

No ngspice, no PDK, no ``klt``, no network. They cover:

1. the committed request matching the declared grid, and the deck naming every node the
   measurements read;
2. the arithmetic on synthetic readings where the answer is known by construction;
3. the checks rejecting a unit whose retained bits were lost, whose control kept state (so the
   testbench would not discriminate), or whose clamp failed;
4. the committed records: every grid point once, all passing, and the binding-corner idle.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR / "tools"))

import power_retention as pr  # noqa: E402

DECK = pr.TB_DIR / pr.DECK
VDD = 3.3


def synthetic_readings() -> dict:
    v: dict = {}
    n = len(pr.RETAINED)
    for k in range(1, n + 1):
        high = VDD if pr.PATTERN[k - 1] else 0.0
        v[f"qg_pre_{k}"] = high
        v[f"qg_post_{k}"] = high
        v[f"qi_{k}"] = high
        v[f"qb_post_{k}"] = 0.0
    v.update(z_off=0.01, z_on=VDD, i_ao_static=15e-9, i_ao_clk=250e-9, i_sw=40e-9, v_rail=0.0145)
    return v


class RequestAndDeck(unittest.TestCase):
    def test_committed_request_matches_the_declared_grid(self) -> None:
        self.assertEqual(pr.cmd_emit(check=True), 0)

    def test_grid_is_45_points_and_requests_capacity_wait(self) -> None:
        req = pr.build_request()
        self.assertEqual(pr.n_units(), 45)
        self.assertEqual(req["batch"]["capacity_wait_s"], 600)
        self.assertIn("set num_threads=1", req["options"]["ngspice_init"])

    def test_probe_is_a_single_point(self) -> None:
        req = pr.build_request("ff/125/3.63")
        self.assertEqual(len(req["corners"]["process"]), 1)
        self.assertEqual(req["corners"]["temperature_c"], [125])

    def test_every_measured_node_exists_in_the_deck(self) -> None:
        deck = DECK.read_text()
        for m in pr.measurements():
            for node in re.findall(r"[vi]\(([a-z0-9_]+)\)", m["spice"]):
                self.assertRegex(deck, rf"(?m)^\S*\s*.*\b{node}\b", f"{node} not in deck ({m['name']})")

    def test_deck_has_the_declared_always_on_set(self) -> None:
        deck = DECK.read_text()
        self.assertEqual(len(re.findall(r"(?m)^xiso\d+ ", deck)), 66)
        self.assertEqual(len(re.findall(r"(?m)^xfi\d ", deck)), len(pr.RETAINED))
        self.assertEqual(len(re.findall(r"(?m)^xicg[fi] ", deck)), 2)

    def test_pattern_has_ones_and_zeros(self) -> None:
        self.assertEqual(len(pr.PATTERN), len(pr.RETAINED))
        self.assertTrue(0 < sum(pr.PATTERN) < len(pr.PATTERN))


class Arithmetic(unittest.TestCase):
    def test_good_readings_pass(self) -> None:
        row = pr.derive(synthetic_readings(), VDD)
        self.assertEqual(row["bits_qg_post"], "10101")
        self.assertEqual(pr.checks(row), [])
        self.assertAlmostEqual(row["i_digital_idle_a"], 55e-9)

    def test_lost_retained_bit_fails(self) -> None:
        v = synthetic_readings()
        v["qg_post_1"] = 0.0
        self.assertIn("retained_ok = 0", pr.checks(pr.derive(v, VDD)))

    def test_control_that_keeps_state_means_the_bench_does_not_discriminate(self) -> None:
        v = synthetic_readings()
        for k, bit in enumerate(pr.PATTERN, 1):
            v[f"qb_post_{k}"] = VDD if bit else 0.0
        self.assertIn("control_lost = 0", pr.checks(pr.derive(v, VDD)))

    def test_unclamped_output_fails(self) -> None:
        v = synthetic_readings()
        v["z_off"] = VDD
        self.assertIn("clamp_ok = 0", pr.checks(pr.derive(v, VDD)))

    def test_missing_reading_is_unmeasured(self) -> None:
        v = synthetic_readings()
        del v["i_sw"]
        rows = pr.analyse_report({"corners": [{"process": "tt", "temperature_c": 27, "supply_v": {"vsup": VDD},
                                               "measurements": [{"name": k, "value": x} for k, x in v.items()]}]})
        self.assertEqual(rows[0]["verdict"], "UNMEASURED")


class CommittedRecords(unittest.TestCase):
    def setUp(self) -> None:
        self.recs = pr.load_records(REPO_ROOT / "sim" / "records")

    def test_every_grid_point_once_and_all_pass(self) -> None:
        keys = [(p, float(t), round(float(v), 2)) for p, t, v in (r["corner"] for r in self.recs)]
        self.assertEqual(len(keys), pr.n_units())
        self.assertEqual(len(set(keys)), pr.n_units())
        for r in self.recs:
            for k in ("retained_ok", "idle_hold_ok", "control_lost", "clamp_ok"):
                self.assertEqual(r["values"][k], 1.0, f"{r['stem']} {k}")

    def test_measured_idle_stays_inside_the_row_at_every_corner(self) -> None:
        analog, _ = pr._ps.analog_idle_a(REPO_ROOT / "sim" / "records")
        for r in self.recs:
            self.assertLess(r["values"]["i_digital_idle_a"] + analog, pr.IDLE_BUDGET_A, r["stem"])

    def test_summary_names_the_binding_corner(self) -> None:
        analog, stem = pr._ps.analog_idle_a(REPO_ROOT / "sim" / "records")
        self.assertIn("Binding idle corner", pr.summary_text(self.recs, analog, stem))


if __name__ == "__main__":
    unittest.main()
