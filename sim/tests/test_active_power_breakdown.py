#!/usr/bin/env python3
"""Unit tests for the per-sub-block active power breakdown (#790).

Pure Python, no OpenROAD, no ngspice: the by-block parser and grouping run on
synthetic ``report_power -instances`` output, and the breakdown tool runs over
the committed records. Properties held:

1. Instances are grouped by hierarchy prefix, CTS clock cells and the rest, and
   every instance lands in exactly one group.
2. Malformed power output is rejected rather than read as zero.
3. The committed breakdown reconciles with ``power_rollup.py``'s own terms at
   both the historical and the ratified rate.
4. The digital rate scaling is exact at the measurement rate and holds leakage
   constant.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(SIM_DIR / "tools"))
sys.path.insert(0, str(SIM_DIR / "tb" / "digital-sta-power"))
sys.path.insert(0, str(SIM_DIR / "tb" / "digital-power-by-block"))

import active_power_breakdown as apb  # noqa: E402
import power_rollup as pr  # noqa: E402
import run_by_block as rbb  # noqa: E402
import run_sta  # noqa: E402

SYNTHETIC = """
junk before
BLOCK_BEGIN
     Internal    Switching      Leakage        Total
        Power        Power        Power        Power (Watts)
----------------------------------------------------
 1.0e-06 2.0e-06 3.0e-07 3.3e-06 u_conditioner/_1_
 1.0e-06 0.0e+00 1.0e-07 1.1e-06 u_health_test/_2_
 4.0e-06 1.0e-06 1.0e-07 5.1e-06 u_interface/_3_
 2.0e-06 1.0e-06 1.0e-07 3.1e-06 clkbuf_leaf_0_clk
 1.0e-07 1.0e-07 1.0e-07 3.0e-07 max_cap62
 1.0e-07 0.0e+00 1.0e-07 2.0e-07 u_unknown/_4_
BLOCK_END
"""


class GroupingTests(unittest.TestCase):
    def test_group_of(self):
        self.assertEqual(rbb.group_of("u_conditioner/_1_"), "u_conditioner")
        self.assertEqual(rbb.group_of("u_ring_liveness/place55"), "u_ring_liveness")
        self.assertEqual(rbb.group_of("clkbuf_leaf_8_clk"), rbb.CLOCK_TREE)
        self.assertEqual(rbb.group_of("clkload3"), rbb.CLOCK_TREE)
        self.assertEqual(rbb.group_of("max_cap62"), rbb.OTHER)
        # An unknown hierarchy prefix is not silently attributed to a sub-block.
        self.assertEqual(rbb.group_of("u_unknown/_4_"), rbb.OTHER)

    def test_every_instance_lands_in_one_group(self):
        rows = rbb.parse_instance_rows(SYNTHETIC)
        self.assertEqual(len(rows), 6)
        groups = rbb.aggregate(rows)
        self.assertEqual(sum(g["n"] for g in groups.values()), 6)
        self.assertAlmostEqual(
            sum(g["total_w"] for g in groups.values()), sum(r[4] for r in rows), places=15
        )
        self.assertEqual(groups["u_conditioner"]["n"], 1)
        self.assertEqual(groups[rbb.OTHER]["n"], 2)

    def test_missing_block_is_an_error(self):
        with self.assertRaises(run_sta.StaError):
            rbb.parse_instance_rows("no markers here")


class BreakdownTests(unittest.TestCase):
    def test_reconciles_with_rollup_at_both_rates(self):
        for rate in apb.DEFAULT_RATES:
            self.assertEqual(apb.reconcile(rate), [], f"rate {rate:g} Hz")

    def test_historical_total_is_the_row_figure(self):
        bd = apb.breakdown(1e6)
        self.assertAlmostEqual(bd["total"] * 1e6, 749.4, delta=0.1)

    def test_digital_scaling_exact_at_measurement_rate(self):
        rec = pr.load(apb.BY_BLOCK_GLOB)[-1]
        at_1mhz = apb.digital_at_rate(rec, pr.DIGITAL_MEASUREMENT_RATE_HZ)
        for _, key in apb.DIGITAL_ROWS:
            self.assertAlmostEqual(at_1mhz[key], rec.values[f"p_{key}_total_w"], places=15)

    def test_digital_leakage_is_the_floor_at_zero_rate(self):
        rec = pr.load(apb.BY_BLOCK_GLOB)[-1]
        floor = apb.digital_at_rate(rec, 0.0)
        for _, key in apb.DIGITAL_ROWS:
            self.assertAlmostEqual(floor[key], rec.values[f"p_{key}_leakage_w"], places=15)

    def test_by_block_record_sums_to_its_own_total(self):
        rec = pr.load(apb.BY_BLOCK_GLOB)[-1]
        parts = sum(rec.values[f"p_{k}_total_w"] for _, k in apb.DIGITAL_ROWS)
        self.assertAlmostEqual(parts, rec.values["p_total_1mhz_w"], delta=rbb.SUM_TOLERANCE * parts)


if __name__ == "__main__":
    unittest.main()
