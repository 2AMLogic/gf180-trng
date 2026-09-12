#!/usr/bin/env python3
"""Unit tests for issue #234's shared-`vss`-trunk IR-drop derivation
(``sim/tools/vss_trunk_ir_drop.py``).

Two groups:

1. **The resistor-network arithmetic** (``node_offsets``), against a small
   synthetic chain with a hand-computed expected answer -- independent of
   this repository's real floorplan geometry, per the curator's own test
   plan for issue #234 ("cross-check the script's output against a
   by-hand computation for one region").
2. **The real geometry**, as a coverage/consistency guard: the resistance
   model this repository's own committed
   ``layout/floorplan/reports/{compose,area,interregion}.json`` implies
   matches a hand-derived expectation, and the full report/--check paths
   run cleanly with no PDK, no ``klt`` and no ngspice.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR / "tools"))

import vss_trunk_ir_drop as ir  # noqa: E402


class NodeOffsetsSyntheticGeometry(unittest.TestCase):
    """A synthetic two-node chain, hand-computed.

    Layout: pin --10 ohm-- A --20 ohm-- B, with A carrying a 5 ohm riser and
    B a 2 ohm riser. A draws 1 mA, B draws 2 mA.

    Segment feeding A carries both currents (3 mA): trunk-side voltage at A
    = 10 ohm * 3 mA = 30 mV. Local vss at A = 30 mV + 5 ohm * 1 mA = 35 mV.
    Segment feeding B carries only B's own current (2 mA): trunk-side
    voltage at B = 30 mV + 20 ohm * 2 mA = 70 mV. Local vss at B =
    70 mV + 2 ohm * 2 mA = 74 mV.
    """

    def test_two_node_chain_matches_hand_computation(self):
        chain = [
            {"region": "A", "seg_r_ohm": 10.0, "riser_r_ohm": 5.0},
            {"region": "B", "seg_r_ohm": 20.0, "riser_r_ohm": 2.0},
        ]
        currents = {"A": 1e-3, "B": 2e-3}
        offsets = ir.node_offsets(chain, currents)
        self.assertAlmostEqual(offsets["A"], 0.035, places=9)
        self.assertAlmostEqual(offsets["B"], 0.074, places=9)

    def test_single_node_at_the_end_of_the_trunk_is_just_iR(self):
        chain = [{"region": "only", "seg_r_ohm": 12.5, "riser_r_ohm": 3.5}]
        offsets = ir.node_offsets(chain, {"only": 4e-3})
        # 12.5 ohm + 3.5 ohm total, all carrying the same 4 mA.
        self.assertAlmostEqual(offsets["only"], 16.0 * 4e-3, places=9)

    def test_upstream_node_offset_only_reflects_current_that_crosses_it(self):
        """A node nearest the pin sees every downstream node's current on
        its own segment even if it draws none itself -- the shared-trunk
        effect issue #234 exists to quantify."""
        chain = [
            {"region": "near", "seg_r_ohm": 1.0, "riser_r_ohm": 1.0},
            {"region": "far", "seg_r_ohm": 100.0, "riser_r_ohm": 1.0},
        ]
        offsets = ir.node_offsets(chain, {"near": 0.0, "far": 5e-3})
        # near's own segment (1 ohm) carries far's 5 mA even though near
        # itself draws nothing; near's own riser then carries 0.
        self.assertAlmostEqual(offsets["near"], 1.0 * 5e-3, places=9)
        self.assertAlmostEqual(offsets["far"], 1.0 * 5e-3 + 100.0 * 5e-3 + 1.0 * 5e-3, places=9)


class ResistanceModelFromCommittedGeometry(unittest.TestCase):
    """Guards the derivation against silent drift in #222's own committed
    routing (`reports/{compose,area,interregion}.json`) -- if a future
    change moves a riser or re-taps the trunk, this either updates
    automatically (the common case, since every number below is read from
    those reports) or fails loudly (the endpoint-set check)."""

    @classmethod
    def setUpClass(cls):
        cls.model = ir.resistance_model()

    def test_three_endpoints_in_trunk_order_nearest_pin_first(self):
        regions = [node["region"] for node in self.model["chain"]]
        self.assertEqual(regions, ["combiner_sampler", "ring2", "ring1"])

    def test_matches_committed_interregion_json_endpoints(self):
        import json
        committed = json.loads(
            (REPO_ROOT / "layout" / "floorplan" / "reports" / "interregion.json").read_text()
        )
        route = next(r for r in committed["routes"] if r["net"] == "vss")
        committed_regions = {e["region"] for e in route["endpoints"]}
        model_regions = {node["region"] for node in self.model["chain"]}
        self.assertEqual(committed_regions, model_regions)

    def test_riser_lengths_are_positive_and_plausible(self):
        # "A few um each", per DR-0025's own capacitance note -- risers
        # cross the row height plus the trunk's under-row offset, so tens of
        # um is the right order of magnitude, not hundreds.
        for node in self.model["chain"]:
            self.assertGreater(node["riser_len_um"], 1.0)
            self.assertLess(node["riser_len_um"], 100.0)

    def test_segment_resistances_sum_close_to_dr0025s_lumped_129_ohm(self):
        total = sum(node["seg_r_ohm"] for node in self.model["chain"])
        # DR-0025's own lumped estimate over the full 430.23 um trunk.
        self.assertAlmostEqual(total, 128.979, delta=0.5)


class ReportAndCheckRunCleanly(unittest.TestCase):
    def test_report_prints_without_raising(self):
        model = ir.resistance_model()
        ir._report(model)  # noqa: SLF001 -- exercised for its side effects only

    def test_check_exits_zero_today(self):
        model = ir.resistance_model()
        self.assertEqual(ir._check(model), 0)  # noqa: SLF001

    def test_worst_case_bound_forces_all_current_through_one_region(self):
        currents = {"ring1": 1e-6, "ring2": 2e-6, "combiner_sampler": 3e-6}
        bound = ir.worst_case_bound_a(currents, "ring1")
        self.assertAlmostEqual(bound["ring1"], 6e-6, places=12)
        self.assertEqual(bound["ring2"], 0.0)
        self.assertEqual(bound["combiner_sampler"], 0.0)


if __name__ == "__main__":
    unittest.main()
