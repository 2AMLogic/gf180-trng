#!/usr/bin/env python3
"""Unit tests for issue #464's digital supply-path DC drop derivation
(``sim/tools/digital_supply_ir_drop.py``). The solver itself is tested on
synthetic networks in ``test_resistor_network.py``; these tests cover what
the tool builds from the committed geometry and evidence, and what it
refuses:

- the external feed is the drawn series path, element by element;
- removing a drawn supply join (a via cut, the Metal5 dock, a rail's vias)
  is rejected, never priced as zero drop;
- raising a resistance on the path raises the drop by exactly that much;
- a change to the current evidence or the geometry stales the committed
  document, and missing evidence makes ``--check`` exit 2, not 0.
"""

from __future__ import annotations

import copy
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR / "tools"))

import digital_supply_ir_drop as ir  # noqa: E402
from layout.floorplan import interregion  # noqa: E402


class _Shared(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan, cls.origin = ir.committed_wiring_plan()
        cls.def_text = ir.DIGITAL_DEF.read_text(errors="replace")
        cls.pdn = {net: ir.parse_pdn(cls.def_text, net) for net in ir.NETS}

    def built(self, net, variant="nominal", **kw):
        return ir.build_network(net, self.plan, self.origin, self.pdn[net], variant, **kw)


class ExternalFeed(_Shared):
    def test_feed_is_the_drawn_series_path(self):
        for net in ir.NETS:
            b = self.built(net)
            kinds = [d.split(",")[0] for d, _ in b.external_path]
            self.assertEqual(kinds, [
                "metal4 wiring-plan rect", "via3 single cut", "metal3 wiring-plan rect",
                "via3 single cut", "via4 single cut", "metal5 wiring-plan rect"], net)
            resp = ir.grid_response(b, self.pdn[net], self.origin)
            # Every amp of the grid's load crosses the feed: its potential at
            # the join is exactly the series sum.
            self.assertAlmostEqual(resp["external_ohm"], resp["path_sum_ohm"], places=6)

    def test_riser_length_matches_the_route(self):
        # vss: trunk at y = -11.0, lowest vss band centred 54.88 um local,
        # digital content origin y = 1.0 -> 66.88 um of 0.30 um Metal3.
        b = self.built("vss")
        riser = [r for d, r in b.external_path if d.startswith("metal3")][0]
        self.assertAlmostEqual(riser, 0.09 * 66.88 / 0.30, places=6)

    def test_vss_shares_the_trunk_with_the_analog_taps(self):
        b = self.built("vss")
        self.assertEqual(set(b.analog_taps), {"ring1", "ring2", "combiner_sampler"})
        self.assertEqual(self.built("vddd").analog_taps, {})


class RemovedJoinIsRejected(_Shared):
    def _drop(self, net, layer):
        return lambda s: s.get("_net") == net and list(s["layer"]) == list(layer)

    def test_missing_via4_floats_the_grid(self):
        for net in ir.NETS:
            with self.assertRaises(ir.ConnectivityError) as ctx:
                self.built(net, drop_shapes=self._drop(net, interregion.VIA4))
            self.assertIn("join missing", str(ctx.exception))

    def test_missing_metal5_dock_floats_the_grid(self):
        with self.assertRaises(ir.ConnectivityError):
            self.built("vddd", drop_shapes=self._drop("vddd", interregion.METAL5))

    def test_rail_without_vias_is_rejected(self):
        # Strip every Via1 array off one vss rail (y = 40320 DEF units).
        text = re.sub(r"\n\s*NEW Metal1 0 \+ SHAPE STRIPE \( \d+ 40320 \) via1_2\S*", "",
                      self.def_text)
        pdn = ir.parse_pdn(text, "vss")
        with self.assertRaises(ir.ConnectivityError) as ctx:
            ir.build_network("vss", self.plan, self.origin, pdn, "nominal")
        self.assertIn("has no via", str(ctx.exception))

    def test_broken_via_stack_islands_a_rail(self):
        # Keep the rail's Via1 cuts, remove its Via2 arrays: the rail and
        # its Metal2 landings become an island.
        text = re.sub(r"\n\s*NEW Metal2 0 \+ SHAPE STRIPE \( \d+ 40320 \) via2_3\S*", "",
                      self.def_text)
        pdn = ir.parse_pdn(text, "vss")
        with self.assertRaises(ir.ConnectivityError):
            ir.build_network("vss", self.plan, self.origin, pdn, "nominal")


class ResistanceRaisesDrop(_Shared):
    def test_doubling_via3_adds_exactly_two_cuts_worth(self):
        base = ir.grid_response(self.built("vddd"), self.pdn["vddd"], self.origin)
        patched = copy.deepcopy(ir.RESISTANCE_VARIANTS)
        patched["nominal"]["via_ohm_per_cut"]["Via3"] *= 2
        with mock.patch.object(ir, "RESISTANCE_VARIANTS", patched):
            more = ir.grid_response(self.built("vddd"), self.pdn["vddd"], self.origin)
        # Two single Via3 cuts on the feed, 4.5 ohm more each. Inside the
        # grid the Via3 arrays (x16) get more resistive too.
        self.assertAlmostEqual(more["external_ohm"] - base["external_ohm"], 9.0, places=6)
        self.assertGreater(more["internal_bound_ohm"], base["internal_bound_ohm"])

    def test_high_variant_exceeds_nominal_everywhere(self):
        for net in ir.NETS:
            nom = ir.grid_response(self.built(net), self.pdn[net], self.origin)
            hi = ir.grid_response(self.built(net, "high"), self.pdn[net], self.origin)
            for k in ("external_ohm", "internal_uniform_ohm", "internal_bound_ohm"):
                self.assertGreater(hi[k], nom[k], f"{net} {k}")

    def test_bound_is_not_below_the_uniform_estimate(self):
        for net in ir.NETS:
            r = ir.grid_response(self.built(net), self.pdn[net], self.origin)
            self.assertGreaterEqual(r["internal_bound_ohm"], r["internal_uniform_ohm"])


class StalenessAndMissingEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.derived = ir.derive()

    def test_committed_document_is_current(self):
        self.assertEqual(ir.check(self.derived), [])

    def test_every_scenario_bound_dominates_its_estimates(self):
        for name, sc in self.derived["scenarios"].items():
            self.assertGreaterEqual(sc["bound"]["collapse_v"],
                                    sc["estimate_worst"]["collapse_v"], name)
            self.assertTrue(sc["bound"]["collapse_v"] > 0, name)

    def _family_copy(self, tmp: Path) -> Path:
        out = tmp / "records"
        out.mkdir()
        for p in sorted((REPO_ROOT / "sim" / "records").glob(ir.dcc.RECORD_GLOB)):
            shutil.copy(p, out / p.name)
        return out

    def _current_record(self, records: Path) -> Path:
        stem = self.derived["provenance"]["current"]["records"][0]["record"]
        return records / f"{stem}.md"

    def test_changed_current_evidence_stales_the_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            records = self._family_copy(Path(tmp))
            rec = self._current_record(records)
            rec.write_text(re.sub(r"(- `p_total_1mhz_w`: )(\S+)",
                                  lambda m: m.group(1) + repr(float(m.group(2)) * 1.01),
                                  rec.read_text()))
            fails = ir.check(ir.derive(records_dir=records))
        self.assertTrue(any("stale" in f for f in fails), fails)

    def test_geometry_change_refuses_the_old_evidence(self):
        # A DEF that is not the one the records describe: the evidence is
        # stale, which is an error, not a silently reused current.
        with tempfile.TemporaryDirectory() as tmp:
            moved = Path(tmp) / "trng_top.def"
            moved.write_text(ir.DIGITAL_DEF.read_text() + "\n# moved\n")
            with self.assertRaises(ir.EvidenceError):
                ir.load_currents(def_path=moved)

    def test_plan_digest_follows_a_moved_shape(self):
        plan, _ = ir.committed_wiring_plan()
        before = ir.plan_digest(plan)
        shape = next(s for s in plan["shapes"] if s.get("_net") == "vddd")
        shape["rect_um"] = [v + 0.01 for v in shape["rect_um"]]
        self.assertNotEqual(ir.plan_digest(plan), before)

    def test_missing_records_are_unknown_not_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ir.EvidenceError):
                ir.load_currents(records_dir=Path(tmp))

    def test_zero_current_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            records = self._family_copy(Path(tmp))
            rec = self._current_record(records)
            rec.write_text(re.sub(r"(- `i_leakage_a`: )\S+", r"\g<1>0.0", rec.read_text()))
            with self.assertRaises(ir.EvidenceError):
                ir.load_currents(records_dir=records)

    def test_check_exits_2_when_evidence_is_missing(self):
        def boom():
            raise ir.EvidenceError("no records")
        with mock.patch.object(ir, "derive", boom), \
                mock.patch("sys.stderr"):
            self.assertEqual(ir.main(["--check"]), 2)

    def test_erc_report_for_another_stream_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rep = json.loads(ir.ERC_SUPPLY_REPORT.read_text())
            rep["provenance"]["input"]["content_hash"] = "sha256:" + "0" * 64
            path = Path(tmp) / "erc.json"
            path.write_text(json.dumps(rep))
            with self.assertRaises(ir.ConnectivityError):
                ir.erc_precondition(path)

    def test_erc_finding_on_a_supply_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            rep = json.loads(ir.ERC_SUPPLY_REPORT.read_text())
            rep["erc_findings"] = [{"rule": "erc.unconnected_net", "net": "vddd"}]
            path = Path(tmp) / "erc.json"
            path.write_text(json.dumps(rep))
            with self.assertRaises(ir.ConnectivityError):
                ir.erc_precondition(path)


if __name__ == "__main__":
    unittest.main()
