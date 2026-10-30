#!/usr/bin/env python3
"""Tests for sim/tools/power_intent_check.py (#708).

The point of the tool is that it can FAIL, so every failure class is exercised
against a deliberately broken input: the ordering rules on hand-built traces,
the isolation table on edited intents, and (with Icarus Verilog and the
gf180mcu cell models) each broken gate-level fixture.
"""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))
sys.path.append(str(Path(__file__).resolve().parent))  # sim/tests: _tool_gate

import power_intent_check as pic  # noqa: E402
from _tool_gate import requires_tools  # noqa: E402

SETTLE, DECAY = 200, 80

GOOD = [
    (40, "pwr_on"), (240, "rail_good"), (260, "iso_release"), (280, "rst_release"), (300, "ret_clk_on"),
    (1000, "ret_clk_off"), (1020, "iso_assert"), (1040, "rst_assert"), (1050, "pwr_off"), (1130, "rail_off"),
    (1400, "pwr_on"), (1600, "rail_good"), (1620, "iso_release"), (1640, "rst_release"), (1660, "ret_clk_on"),
]


def without(*events):
    return [e for e in GOOD if e[1] not in events]


def moved(old, new):
    return [new if e == old else e for e in GOOD]


class SequenceRules(unittest.TestCase):
    def classes(self, events):
        return set(pic.check_sequence(sorted(events), SETTLE, DECAY))

    def test_good_trace_is_clean(self):
        self.assertEqual(self.classes(GOOD), set())

    def test_iso_release_before_rail_good(self):
        e = moved((260, "iso_release"), (100, "iso_release"))
        self.assertIn("iso_release_before_rail_good", self.classes(e))

    def test_reset_before_iso_release(self):
        e = moved((260, "iso_release"), (270, "iso_release"))
        e = [(255, "rst_release") if x == (280, "rst_release") else x for x in e]
        self.assertIn("reset_release_before_iso_release", self.classes(e))

    def test_rail_up_without_reset(self):
        e = [x for x in GOOD if x != (1040, "rst_assert")]
        self.assertIn("rail_up_without_reset", self.classes(e))

    def test_retention_clock_before_reset_release(self):
        e = moved((300, "ret_clk_on"), (270, "ret_clk_on"))
        self.assertIn("ret_clock_before_reset_release", self.classes(e))

    def test_power_off_before_isolation(self):
        e = moved((1020, "iso_assert"), (1060, "iso_assert"))
        self.assertIn("power_off_before_isolation", self.classes(e))

    def test_power_off_with_retained_clock_running(self):
        e = moved((1000, "ret_clk_off"), (1060, "ret_clk_off"))
        self.assertIn("power_off_with_retained_clock_running", self.classes(e))

    def test_wake_inside_decay(self):
        e = moved((1400, "pwr_on"), (1100, "pwr_on"))
        self.assertIn("wake_inside_decay", self.classes(e))

    def test_rail_settle_short(self):
        e = moved((240, "rail_good"), (100, "rail_good"))
        self.assertIn("rail_settle_short", self.classes(e))

    def test_missing_step(self):
        self.assertIn("missing_step", self.classes(without("ret_clk_on")))
        self.assertIn("missing_step", self.classes(without("ret_clk_off")))


class StaticChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intent = pic.load_intent()
        cls.netlist = (pic.REPO_ROOT / cls.intent["netlist"]).read_text()
        cls.rtl = pic.TOP_V.read_text()

    def test_shipped_intent_is_clean(self):
        self.assertEqual(pic.static_checks(self.intent, self.netlist), [])

    def test_unlisted_output_is_reported(self):
        i = copy.deepcopy(self.intent)
        i["isolation"] = [x for x in i["isolation"] if x["port"] != "str_data"]
        errs = pic.check_isolation(i, self.rtl, self.netlist)
        self.assertTrue(any("str_data" in e and "no isolation entry" in e for e in errs), errs)

    def test_wrong_width_is_reported(self):
        i = copy.deepcopy(self.intent)
        for x in i["isolation"]:
            if x["port"] == "reg_rdata":
                x["width"] = 31
        self.assertTrue(pic.check_isolation(i, self.rtl, self.netlist))

    def test_missing_clamp_is_reported(self):
        i = copy.deepcopy(self.intent)
        i["isolation"][0]["clamp"] = None
        self.assertTrue(pic.check_isolation(i, self.rtl, self.netlist))

    def test_unknown_retained_net_is_reported(self):
        i = copy.deepcopy(self.intent)
        i["retained"]["q_nets"].append("no_such_flop")
        self.assertIn("no_such_flop", pic.classify_flops(self.netlist, i)["missing"])
        self.assertTrue(pic.static_checks(i, self.netlist))

    def test_declared_sequence_violation_is_reported(self):
        i = copy.deepcopy(self.intent)
        wake = i["sequence"]["wake"]
        a, b = (k for k, s in enumerate(wake) if s["event"] in ("iso_release", "rst_release"))
        wake[a]["event"], wake[b]["event"] = wake[b]["event"], wake[a]["event"]
        errs = pic.static_checks(i, self.netlist)
        self.assertTrue(any("reset_release_before_iso_release" in e for e in errs), errs)

    def test_retained_flops_found_and_all_classified(self):
        c = pic.classify_flops(self.netlist, self.intent)
        self.assertEqual(c["retained"], 5)
        self.assertGreater(c["gated"], 300)

    def test_transform_repoints_only_retained_flops(self):
        out = pic.transform_netlist(self.netlist, self.intent)
        self.assertEqual(out.count(".CLK(clk_ret)"), 5)
        self.assertNotIn("gf180mcu_fd_sc_mcu9t5v0__dff", out)

    def test_budget_is_provisional_while_placeholders_remain(self):
        b = pic.wake_budget(self.intent)
        self.assertTrue(b["provisional"])
        self.assertGreater(b["wake_time_to_first_valid_s"], b["digital_floor_s"])


_LIB = None
try:
    _LIB = pic.find_cell_lib((pic.REPO_ROOT / "design/trng_top/trng_top.synth.v").read_text())
except Exception:  # no PDK
    pass


@requires_tools("iverilog", "vvp", reason="gate-level power-intent run needs Icarus Verilog")
@unittest.skipIf(_LIB is None, "gf180mcu cell models not found (PDK not installed)")
class GateLevel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.intent = pic.load_intent()
        cls.netlist = (pic.REPO_ROOT / cls.intent["netlist"]).read_text()

    def test_correct_design_passes(self):
        r = pic.run_gate_level(self.intent, self.netlist, _LIB)
        self.assertTrue(r["completed"])
        self.assertEqual(r["classes"], set(), r["log"][-1500:])
        self.assertGreaterEqual(len(r["passed_checks"]), 10)

    def test_each_broken_fixture_is_reported(self):
        for name, (defines, kw, required) in pic.VARIANTS.items():
            with self.subTest(name):
                r = pic.run_gate_level(self.intent, self.netlist, _LIB, defines, **kw)
                self.assertTrue(required <= r["classes"], (name, required, r["classes"]))


if __name__ == "__main__":
    unittest.main()
