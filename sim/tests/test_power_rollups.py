#!/usr/bin/env python3
"""Unit tests for #14's two rollups and the digital power estimate.

Four groups:

1. ``sim/tools/time_to_first_valid.py``'s convergence extraction and
   sample-count arithmetic, on synthetic edge lists where the right answer is
   known by construction.
2. ``sim/tools/power_rollup.py``'s sampler arithmetic and record reading.
3. ``design/digital_power_estimate.py``'s Liberty parser, against a small
   synthetic library written in this file -- so the parser is tested without
   needing the PDK installed.
4. **Inventory staleness guards.** The digital estimate's flip-flop counts are
   enumerated from the three RTL modules' ``reg`` declarations at their
   shipped default parameters. If a parameter those counts depend on moves and
   the inventory does not, the estimate silently becomes wrong -- and it is the
   evidence behind DR-0017. These tests read the parameters back out of the
   RTL and fail if any of them has changed, which is the same guard
   ``design/interface/regmap.py --check`` applies to the register map.

The PDK-dependent parts of both tools are exercised in CI's PDK nightly, not
here: everything in this file runs with no ngspice and no PDK.
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR / "tools"))
sys.path.insert(0, str(REPO_ROOT / "design"))
sys.path.insert(0, str(REPO_ROOT / "design" / "conditioner"))

import digital_power_estimate as dpe  # noqa: E402
import power_rollup as pr  # noqa: E402
import time_to_first_valid as ttfv  # noqa: E402


# ---------------------------------------------------------------------------
# 1. time_to_first_valid
# ---------------------------------------------------------------------------


def edges_from_periods(periods, t0=0.0):
    out = [t0]
    for p in periods:
        out.append(out[-1] + p)
    return out


class ConvergenceTests(unittest.TestCase):
    def test_already_converged_returns_the_first_edge(self):
        edges = edges_from_periods([10.0] * 9, t0=1.0)
        t, steady, idx = ttfv.converged_time(edges, t_en=0.0, tol=0.01)
        self.assertEqual(idx, 0)
        self.assertAlmostEqual(steady, 10.0)
        self.assertAlmostEqual(t, 1.0)

    def test_settling_run_reports_the_first_in_band_edge(self):
        # Three periods outside a 1 % band, then six inside it.
        edges = edges_from_periods([13.0, 11.0, 10.5] + [10.0] * 6, t0=0.0)
        t, _steady, idx = ttfv.converged_time(edges, t_en=0.0, tol=0.01)
        self.assertEqual(idx, 3)
        self.assertAlmostEqual(t, 13.0 + 11.0 + 10.5)

    def test_a_single_lucky_crossing_does_not_count_as_converged(self):
        """First-AND-thereafter: a period that grazes the band on its way past
        must not be reported as the start of convergence."""
        edges = edges_from_periods([10.0, 13.0, 12.0, 11.0] + [10.0] * 5, t0=0.0)
        _t, _steady, idx = ttfv.converged_time(edges, t_en=0.0, tol=0.01)
        self.assertEqual(idx, 4, "the grazing first period must not win")

    def test_never_converging_is_reported_not_extrapolated(self):
        edges = edges_from_periods([10.0, 12.0, 14.0, 16.0, 18.0], t0=0.0)
        t, steady, idx = ttfv.converged_time(edges, t_en=0.0, tol=0.01)
        self.assertIsNone(t)
        self.assertIsNone(idx)
        self.assertIsNotNone(steady)

    def test_too_few_edges_is_not_an_answer(self):
        self.assertEqual(ttfv.converged_time([1.0, 2.0], 0.0, 0.01), (None, None, None))

    def test_the_plateau_requirement_is_not_vacuous(self):
        """The last estimate is always inside its own band, so without a
        minimum plateau length every run would 'converge' at its last edge."""
        edges = edges_from_periods([10.0, 12.0, 14.0, 16.0, 18.0], t0=0.0)
        self.assertIsNone(ttfv.converged_time(edges, 0.0, 0.01, min_stable=3)[0])
        self.assertIsNotNone(ttfv.converged_time(edges, 0.0, 0.01, min_stable=1)[0])

    def test_tolerance_is_actually_applied(self):
        edges = edges_from_periods([10.3, 10.1] + [10.0] * 5, t0=0.0)
        self.assertEqual(ttfv.converged_time(edges, 0.0, 0.05)[2], 0)
        self.assertEqual(ttfv.converged_time(edges, 0.0, 0.005)[2], 2)


class BudgetTests(unittest.TestCase):
    def test_sample_counts_match_the_shipped_rtl_parameters(self):
        self.assertEqual(ttfv.STARTUP_SAMPLES, 1024)
        self.assertEqual(ttfv.CONDITIONER_SAMPLES, 256)
        self.assertEqual(ttfv.SAMPLER_SAMPLES, 1)

    def test_budget_at_the_ratified_rate_matches_the_readme_floor(self):
        b = ttfv.budget(ttfv.RATIFIED_RAW_RATE_BPS)
        self.assertAlmostEqual(b["health_test_s"], 1.024e-3)
        self.assertAlmostEqual(b["conditioner_s"], 256e-6)
        # 1281 samples, i.e. the README's 1280 plus the one sampler clock the
        # floor does not count.
        self.assertAlmostEqual(b["digital_total_s"], 1.281e-3)
        self.assertGreater(b["digital_total_s"], ttfv.README_FLOOR_S)

    def test_the_row_scales_exactly_with_the_rate(self):
        fast = ttfv.budget(1e6)["digital_total_s"]
        slow = ttfv.budget(500.0)["digital_total_s"]
        self.assertAlmostEqual(slow / fast, 2000.0)


class StartupRecordTests(unittest.TestCase):
    """The committed records themselves, read the way the tool reads them."""

    @classmethod
    def setUpClass(cls):
        cls.records = ttfv.load_startup_records()

    def test_the_full_covered_grid_is_present(self):
        self.assertEqual(len(self.records), 27)
        corners = {r.corner for r in self.records}
        self.assertEqual(len(corners), 27)
        self.assertEqual({r.process for r in self.records}, {"tt", "ff", "ss"})

    def test_every_corner_converges_and_starts_from_the_clamped_state(self):
        for rec in self.records:
            res = ttfv.CornerResult(rec, tol=0.01)
            with self.subTest(corner=rec.corner):
                self.assertTrue(res.converged, f"{rec.stem} did not converge")
                # The ring is clamped HIGH and xo (their XOR) is LOW before en.
                self.assertGreater(rec.values["v_ro1_off_v"], 0.9 * rec.vdd)
                self.assertLess(abs(rec.values["v_xo_off_v"]), 0.05 * rec.vdd)
                # Start-up is a small multiple of the steady period, not a
                # long envelope build-up.
                self.assertLess(res.t_startup, 5 * res.periods[1])
                # Amplitude settled too, so the period-based figure is not
                # hiding a swing still on its way up.
                self.assertAlmostEqual(res.swing_ratio, 1.0, delta=0.15)


# ---------------------------------------------------------------------------
# 2. power_rollup
# ---------------------------------------------------------------------------


class _FakeRecord:
    def __init__(self, values, vdd=3.63):
        self.values = values
        self.vdd = vdd
        self.stem = "fake"


class SamplerArithmeticTests(unittest.TestCase):
    def test_data_term_uses_the_clock_duty_and_both_phases(self):
        rec = _FakeRecord({
            "q_d_open_c": -1e-14, "q_d_shut_c": -2e-15,
            "q_clkcyc_xsv_c": -0.0, "vdd_mean_v": 3.0,
        })
        out = pr.sampler_active(rec, r_xo=1e9, f_clk=1e6)
        # 1e9 * (0.5*1e-14 + 0.5*2e-15) = 6e-6 A
        self.assertAlmostEqual(out["i_data_a"], 6e-6)
        self.assertAlmostEqual(out["p_total_w"], 6e-6 * 3.0)

    def test_clock_term_counts_both_instances(self):
        rec = _FakeRecord({
            "q_d_open_c": 0.0, "q_d_shut_c": 0.0,
            "q_clkcyc_xsv_c": -8e-15, "vdd_mean_v": 3.3,
        })
        out = pr.sampler_active(rec, r_xo=0.0, f_clk=1e6)
        self.assertAlmostEqual(out["i_clk_a"], 2 * 1e6 * 8e-15)

    def test_recorded_sign_convention_is_normalised_to_magnitudes(self):
        neg = _FakeRecord({"q_d_open_c": -1e-14, "q_d_shut_c": -1e-15,
                           "q_clkcyc_xsv_c": -1e-15, "vdd_mean_v": 3.3})
        pos = _FakeRecord({"q_d_open_c": 1e-14, "q_d_shut_c": 1e-15,
                           "q_clkcyc_xsv_c": 1e-15, "vdd_mean_v": 3.3})
        self.assertAlmostEqual(pr.sampler_active(neg, 1e9, 1e6)["i_total_a"],
                               pr.sampler_active(pos, 1e9, 1e6)["i_total_a"])

    def test_duty_is_the_real_clocks_and_not_the_decks(self):
        """The active-current deck runs a 10/21 duty for an aliasing reason of
        its own; the rollup must use the real 50 %."""
        self.assertEqual(pr.DUTY_OPEN, 0.5)


class PowerRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samplers = pr.by_corner(pr.load(pr.SAMPLER_ACTIVE_GLOB))
        cls.idles = pr.by_corner(pr.load(pr.IDLE_GLOB))
        cls.arrays = pr.by_corner(pr.load(pr.ARRAY_GLOBS), prefer="pvt-q")

    def test_full_grids_are_present(self):
        self.assertEqual(len(self.samplers), 45)
        self.assertEqual(len(self.idles), 45)
        self.assertGreaterEqual(len(self.arrays), 27)

    def test_every_sampler_record_witnesses_both_flops_capturing(self):
        for corner, rec in self.samplers.items():
            with self.subTest(corner=corner):
                self.assertLess(abs(rec.values["qv_pre_v"]), 0.1 * rec.vdd)
                self.assertGreater(rec.values["qv_post_v"], 0.9 * rec.vdd)
                self.assertLess(abs(rec.values["qb_pre_v"]), 0.1 * rec.vdd)
                self.assertGreater(rec.values["qb_post_v"], 0.9 * rec.vdd)

    def test_the_master_gate_dominates_the_open_phase(self):
        """The whole reason this deck measures two phases separately: the shut
        phase must be negligible against the open one, or the rollup's 50/50
        weighting would be hiding something."""
        for corner, rec in self.samplers.items():
            with self.subTest(corner=corner):
                self.assertLess(abs(rec.values["q_d_shut_c"]),
                                0.01 * abs(rec.values["q_d_open_c"]))

    def test_every_idle_record_passes_its_own_two_window_self_check(self):
        for corner, rec in self.idles.items():
            for key in ("clklo", "clkhi"):
                a = abs(rec.values[f"i_idle_{key}_a"])
                b = abs(rec.values[f"i_idle_{key}_prev_a"])
                with self.subTest(corner=corner, park=key):
                    self.assertGreater(a, 0.0)
                    self.assertLess(abs(a - b) / a, 0.05)

    def test_idle_records_landed_in_the_clamped_state(self):
        for corner, rec in self.idles.items():
            with self.subTest(corner=corner):
                self.assertGreater(rec.values["v_ro1_v"], 0.9 * rec.vdd)
                self.assertGreater(rec.values["v_ro2_v"], 0.9 * rec.vdd)
                self.assertLess(abs(rec.values["v_xo_v"]), 0.05 * rec.vdd)
                # raw_valid latched 1 (xsv's D is tied to vdd); raw_bit
                # latched xo, which is 0 with the rings clamped.
                self.assertGreater(rec.values["v_rawvalid_clklo_v"], 0.9 * rec.vdd)
                self.assertLess(abs(rec.values["v_rawbit_clklo_v"]), 0.05 * rec.vdd)

    def test_analog_idle_is_far_below_the_row_at_every_corner(self):
        """Not a spec assertion -- a regression guard. If the analog block ever
        stops being a rounding error in the idle budget, DR-0017's whole
        diagnosis changes and this must fail loudly."""
        for corner, rec in self.idles.items():
            worst = max(abs(rec.values["i_idle_clklo_a"]),
                        abs(rec.values["i_idle_clkhi_a"]))
            with self.subTest(corner=corner):
                self.assertLess(worst, 0.2 * pr.IDLE_BUDGET_A)


# ---------------------------------------------------------------------------
# 3. Liberty parser (no PDK needed)
# ---------------------------------------------------------------------------

_SYNTHETIC_LIB = """
library(tiny) {
  time_unit : 1ns ;
  voltage_unit : 1V ;
  current_unit : 1mA ;
  capacitive_load_unit(1, pf);
  leakage_power_unit : 1uW ;

  cell(gf180mcu_fd_sc_mcu7t5v0__nand2_1) {
    area : 10.976000 ;
    leakage_power() {
      when : "!A1&!A2" ;
      value : "0.001000" ;
    }
    leakage_power() {
      when : "A1&A2" ;
      value : "0.003000" ;
    }
    leakage_power() {
      value : "0.002000" ;
    }
    pin(A1) {
      capacitance : 0.00472 ;
      direction : input ;
      internal_power() {
        rise_power(pwr_tin_10) {
          index_1("0.02, 0.07, 0.25");
          values("0.010, 0.020, 0.030");
        }
      }
    }
    pin(ZN) {
      direction : output ;
    }
  }

  cell(gf180mcu_fd_sc_mcu7t5v0__dffrnq_1) {
    area : 40.0 ;
    leakage_power() {
      value : "0.012000" ;
    }
    pin(CLK) {
      capacitance : 0.010 ;
      direction : input ;
    }
    pin(D) {
      capacitance : 0.005 ;
      direction : input ;
    }
  }
}
"""


class LibertyParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        path = Path(cls.tmp.name) / "tiny.lib"
        path.write_text(_SYNTHETIC_LIB)
        cls.cells = dpe.parse_liberty(path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_both_cells_are_found(self):
        self.assertIn("gf180mcu_fd_sc_mcu7t5v0__nand2_1", self.cells)
        self.assertIn("gf180mcu_fd_sc_mcu7t5v0__dffrnq_1", self.cells)

    def test_state_independent_leakage_is_separated_from_the_when_states(self):
        c = self.cells["gf180mcu_fd_sc_mcu7t5v0__nand2_1"]
        self.assertAlmostEqual(c.leak_default, 0.002)
        self.assertAlmostEqual(c.leak_min, 0.001)
        self.assertAlmostEqual(c.leak_max, 0.003)

    def test_only_input_pin_capacitances_are_collected(self):
        c = self.cells["gf180mcu_fd_sc_mcu7t5v0__nand2_1"]
        self.assertEqual(set(c.pin_caps), {"A1"})

    def test_the_clock_pin_is_identified_by_name(self):
        c = self.cells["gf180mcu_fd_sc_mcu7t5v0__dffrnq_1"]
        self.assertAlmostEqual(dpe._clock_pin_cap(c), 0.010)
        self.assertAlmostEqual(dpe._clock_pin_cap(
            self.cells["gf180mcu_fd_sc_mcu7t5v0__nand2_1"]), 0.0)

    def test_leakage_scales_with_the_declared_unit(self):
        inv = [("one flop", {"dffrnq_1": 100}, "")]
        est = dpe.estimate_block(self.cells, inv, vdd=3.6, freq=1e6,
                                 activity=0.0, fanout=0.0, wire_cap_f=0.0)
        # 100 cells x 0.012 uW
        self.assertAlmostEqual(est["leak_default_w"], 100 * 0.012e-6)
        self.assertEqual(est["flops"], 100)
        self.assertAlmostEqual(est["leak_flop_w"], est["leak_default_w"])
        self.assertAlmostEqual(est["leak_comb_w"], 0.0)

    def test_clock_gating_scales_the_clock_term_and_nothing_else(self):
        gated = [("gated", {"dffrnq_1": 100}, "", {"clock_duty": 0.01})]
        ungated = [("ungated", {"dffrnq_1": 100}, "")]
        g = dpe.estimate_block(self.cells, gated, 3.6, 1e6, 0.0, 0.0, 0.0)
        u = dpe.estimate_block(self.cells, ungated, 3.6, 1e6, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(g["p_clock_w"], 0.01 * u["p_clock_w"])
        self.assertAlmostEqual(g["leak_default_w"], u["leak_default_w"])

    def test_dynamic_scales_as_c_v_squared_f(self):
        inv = [("x", {"dffrnq_1": 1}, "")]
        a = dpe.estimate_block(self.cells, inv, 3.6, 1e6, 0.0, 0.0, 0.0)
        b = dpe.estimate_block(self.cells, inv, 7.2, 1e6, 0.0, 0.0, 0.0)
        c = dpe.estimate_block(self.cells, inv, 3.6, 2e6, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(b["p_clock_w"] / a["p_clock_w"], 4.0)
        self.assertAlmostEqual(c["p_clock_w"] / a["p_clock_w"], 2.0)


# ---------------------------------------------------------------------------
# 4. Inventory staleness guards
# ---------------------------------------------------------------------------

RTL = {
    "health": REPO_ROOT / "design" / "health_test" / "rct_apt.v",
    "liveness": REPO_ROOT / "design" / "health_test" / "ring_liveness.v",
    "interface": REPO_ROOT / "design" / "interface" / "trng_interface.v",
    "regmap": REPO_ROOT / "design" / "interface" / "trng_regmap.vh",
    "conditioner": REPO_ROOT / "design" / "conditioner" / "crc32_conditioner.v",
}


def _param(path: Path, name: str) -> int:
    text = path.read_text()
    m = re.search(rf"parameter\s+integer\s+{name}\s*=\s*(\d+)", text)
    if m is None:
        m = re.search(rf"localparam\s+integer\s+{name}\s*=\s*(\d+)", text)
    if m is None:
        raise AssertionError(f"{path.name}: parameter {name} not found")
    return int(m.group(1))


def _flops(inventory) -> int:
    return sum(n for counts, _ov in dpe._sections(inventory)
               for s, n in counts.items() if s.startswith("dff"))


class InventoryStalenessTests(unittest.TestCase):
    """Fail if the RTL moves out from under the gate inventories.

    These counts are DR-0017's evidence. A parameter change that silently
    invalidated them would leave a decision record citing a number the design
    no longer produces, which is exactly the failure the append-only evidence
    convention exists to prevent -- except that this estimate is not a record
    and has no checksum, so it needs this instead.
    """

    def test_health_test_parameters_are_the_ones_the_inventory_assumes(self):
        self.assertEqual(_param(RTL["health"], "C_RCT"), 81)     # -> 7-bit counter
        self.assertEqual(_param(RTL["health"], "C_APT"), 824)    # -> 11-bit
        self.assertEqual(_param(RTL["health"], "W"), 1024)       # -> 11-bit
        self.assertEqual(_flops(dpe.HEALTH_TEST_INVENTORY), 45)

    def test_liveness_parameters_are_the_ones_the_inventory_assumes(self):
        self.assertEqual(_param(RTL["liveness"], "N_RINGS"), 2)
        self.assertEqual(_param(RTL["liveness"], "C_LIVE"), 81)  # -> 7-bit counter
        self.assertEqual(_flops(dpe.LIVENESS_INVENTORY), 18)     # 2 x (1 + 7 + 1)

    def test_interface_parameters_are_the_ones_the_inventory_assumes(self):
        self.assertEqual(_param(RTL["interface"], "FIFO_DEPTH"), 8)
        self.assertEqual(_param(RTL["regmap"], "TRNG_LEVEL_BITS"), 4)
        self.assertEqual(_param(RTL["regmap"], "TRNG_RAW_PACK_BITS"), 32)
        # 2 x 8 x 32 FIFO + 6 head + 8 count + 32 shift + 6 bitcount + 8 ctrl
        self.assertEqual(_flops(dpe.INTERFACE_INVENTORY), 572)

    def test_conditioner_inventory_is_the_one_area_estimate_ships(self):
        import area_estimate
        self.assertIs(dpe.BLOCKS[0][1], area_estimate.INVENTORY)
        self.assertEqual(_flops(area_estimate.INVENTORY), 41)

    def test_the_word_periods_the_activity_model_assumes(self):
        """The FIFO clock-duty overrides are derived from these; if K or the
        raw packing width changes, the dynamic estimate silently drifts."""
        self.assertEqual(dpe.COND_WORD_PERIOD, 256)   # K = 8 blocks of 32
        self.assertEqual(dpe.RAW_WORD_PERIOD, 32)
        self.assertEqual(dpe.FIFO_DEPTH, _param(RTL["interface"], "FIFO_DEPTH"))
        self.assertEqual(dpe.COND_WORD_PERIOD, ttfv.CONDITIONER_SAMPLES)

    def test_shipped_blocks_exclude_the_liveness_monitor(self):
        """DR-0016's monitor is built but not wired in (#65). If it is ever
        promoted, this fails and the totals must be revisited deliberately."""
        shipped = {name for name, _inv, ship in dpe.BLOCKS if ship}
        self.assertNotIn("ring-liveness monitor [DR-0016]", shipped)
        self.assertEqual(len(shipped), 3)


if __name__ == "__main__":
    unittest.main()
