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

import re
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(SIM_DIR / "tools"))
sys.path.insert(0, str(SIM_DIR / "tb" / "digital-sta-power"))
sys.path.insert(0, str(SIM_DIR / "tb" / "digital-power-by-block"))

import activity  # noqa: E402
import active_power_breakdown as apb  # noqa: E402
import power_rollup as pr  # noqa: E402
import run_by_block as rbb  # noqa: E402
import run_sta  # noqa: E402

REPO_ROOT = SIM_DIR.parent
SPLIT_DECK = SIM_DIR / "tb" / "ro-array-core-power-split" / "tb_ro_array_core_power_split.sp"
SHIPPED = REPO_ROOT / "design" / "ro_array_core.spice"

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


def _segment(annot: str, rows: str, total: str) -> str:
    return (
        "ACT_BEGIN conditioned-streaming steady\n" + annot
        + "BLOCK_BEGIN\n   hdr\n" + rows + "BLOCK_END\n" + total + "ACT_END\n"
    )


_TOTAL = """\
Group                  Internal  Switching    Leakage      Total
                          Power      Power      Power      Power (Watts)
----------------------------------------------------------------
Sequential           0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00   0.0%
Combinational        0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00   0.0%
Clock                0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00   0.0%
Macro                0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00   0.0%
Pad                  0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00   0.0%
----------------------------------------------------------------
Total                {i:.6e} {s:.6e} {l:.6e} {t:.6e} 100.0%
"""
_ROWS = (
    " 1.0e-06 2.0e-06 3.0e-07 3.3e-06 u_conditioner/_1_\n"
    " 4.0e-06 1.0e-06 1.0e-07 5.1e-06 u_interface/_3_\n"
    " 2.0e-06 1.0e-06 1.0e-07 3.1e-06 clkbuf_leaf_0_clk\n"
)
_GOOD_ANN = "Annotated 990 pin activities.\nvcd          990\nunannotated     5\n"


class ActivityModeTests(unittest.TestCase):
    def _total(self, t):
        return _TOTAL.format(i=6e-6, s=4e-6, l=5e-7, t=t)

    def test_activity_session_groups_and_reconciles(self):
        out = rbb.parse_activity_session(
            _segment(_GOOD_ANN, _ROWS, self._total(1.15e-5)),
            "conditioned-streaming", "steady")
        self.assertAlmostEqual(out["instance_sum_w"], 1.15e-5, places=15)
        self.assertEqual(out["groups"]["u_interface"]["n"], 1)
        self.assertEqual(out["groups"][rbb.CLOCK_TREE]["n"], 1)
        self.assertEqual(out["annotation"]["vcd"], 990)

    def test_sum_gap_beyond_tolerance_is_rejected(self):
        with self.assertRaises(run_sta.StaError):
            rbb.parse_activity_session(
                _segment(_GOOD_ANN, _ROWS, self._total(1.3e-5)),
                "conditioned-streaming", "steady")

    def test_unbound_trace_is_rejected(self):
        # Negative control: a wrong scope / empty trace binds no pin to the VCD.
        for ann in ("Annotated 0 pin activities.\nunannotated   995\n",
                    "Annotated 500 pin activities.\nvcd          500\nunannotated   495\n"):
            with self.assertRaises(activity.ActivityError):
                rbb.parse_activity_session(
                    _segment(ann, _ROWS, self._total(1.15e-5)),
                    "conditioned-streaming", "steady")

    def test_missing_segment_is_rejected(self):
        with self.assertRaises(activity.ActivityError):
            rbb.parse_activity_session(
                _segment(_GOOD_ANN, _ROWS, self._total(1.15e-5)),
                "other-workload", "steady")

    def test_compare_rows_ratio(self):
        mk = lambda w: {g: {"total_w": w} for g in rbb.GROUPS}
        rows = rbb.compare_rows({"uniform": {"groups": mk(2.0)}, "observed": {"groups": mk(1.0)}})
        self.assertEqual([r[0] for r in rows], list(rbb.GROUPS))
        self.assertTrue(all(abs(r[3] - 0.5) < 1e-12 for r in rows))

    def test_activity_slug_does_not_match_uniform_glob(self):
        import fnmatch
        self.assertFalse(fnmatch.fnmatch(
            f"2026-11-10-{rbb.ACTIVITY_SLUG}-01.md", apb.BY_BLOCK_GLOB))

    def test_only_declared_capture_periods(self):
        self.assertIn(500_000.0, activity.ALLOWED_PERIODS_NS)
        with self.assertRaises(activity.ActivityError):
            activity._check_period(123.0)


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


def _array_instances(text: str, *, top_only: bool) -> dict[str, tuple]:
    """``{name: (model, params, nodes)}`` for the ring/buffer/XOR instances.

    ``top_only`` reads just the ``ro_array_core`` subcircuit body of the shipped
    netlist; otherwise every x-line of the deck. Supply-pin nodes are folded:
    ``en*`` -> ``en``, ground -> ``0``, and the three split buffer/XOR rails ->
    ``vdd`` (the one pin they were split from), which is the only electrical
    difference the deck is allowed.
    """
    if top_only:
        text = text.split(".subckt ro_array_core", 1)[1].split(".ends", 1)[0]
    fold = {"en1": "en", "en2": "en", "vss": "0", "vddb1": "vdd", "vddb2": "vdd", "vddx": "vdd"}
    out = {}
    for line in text.splitlines():
        if not re.match(r"x(r|b|a)\d", line):
            continue
        tok = line.split()
        model = next(i for i, t in enumerate(tok) if t.startswith("ro_") or t == "xor2")
        out[tok[0]] = (tok[model], tuple(tok[model + 1:]),
                       tuple(fold.get(n, n) for n in tok[1:model]))
    return out


class SplitTests(unittest.TestCase):
    def test_deck_instances_equal_the_shipped_array(self):
        deck = _array_instances(SPLIT_DECK.read_text(), top_only=False)
        shipped = _array_instances(SHIPPED.read_text(), top_only=True)
        self.assertEqual(sorted(shipped), ["xa1", "xb1", "xb2", "xr1", "xr2"])
        self.assertEqual(deck, shipped)

    def test_deck_splits_the_vdd_rail_three_ways(self):
        deck = SPLIT_DECK.read_text()
        for src in ("vb1 vsup vddb1", "vb2 vsup vddb2", "vx vsup vddx"):
            self.assertIn(src, deck)
        self.assertNotIn("vsup vdd dc", deck)

    def test_split_rows_sum_to_the_remainder_and_keep_the_totals(self):
        split = pr.load(apb.SPLIT_GLOB)
        self.assertTrue(split, "no ro-array-core-power-split record")
        for rate in apb.DEFAULT_RATES:
            with_split = apb.breakdown(rate)
            self.assertEqual(with_split["split_record"], split[-1].stem)
            merged = apb.breakdown(rate, split=False)
            rows = {label: w for label, w, _ in with_split["rows"]}
            self.assertAlmostEqual(rows["ring buffers"] + rows["XOR combiner"],
                                   dict((l, w) for l, w, _ in merged["rows"])[apb.MERGED_ROW],
                                   delta=1e-12)
            self.assertAlmostEqual(with_split["total"], merged["total"], delta=1e-12)

    def test_split_record_is_within_tolerance_of_the_array_record(self):
        bd = apb.breakdown(1e6)
        self.assertLessEqual(abs(bd["split_gap"]), apb.SPLIT_RECONCILE_TOL)

    def test_reconcile_flags_a_split_that_disagrees(self):
        arrays = pr.by_corner(pr.load(pr.ARRAY_GLOBS), prefer="pvt-q")
        split = pr.load(apb.SPLIT_GLOB)[-1]
        split.values = dict(split.values, p_xor_w=split.values["p_xor_w"] * 2)
        self.assertGreater(abs(apb.split_gap(arrays[apb.ARRAY_CORNER], split)),
                           apb.SPLIT_RECONCILE_TOL)


if __name__ == "__main__":
    unittest.main()
