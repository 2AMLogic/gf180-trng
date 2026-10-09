"""Ring2 native pex comparison (#423): fixture, source audits and publication gate, offline.

No klt, ngspice or PDK. The committed state is an explicitly unrun fixture; the
publication tests build a synthetic publication in a scratch copy of the paths.
"""

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bd = _load("ring_build_dut", "sim/tb/ro-ring11-pex/build_dut.py")
check = _load("signoff_check", "signoff/check.py")

DESIGN = bd.DESIGN.read_text()
HEADER2 = ["ro"] + [f"n{i}" for i in range(1, 11)] + ["en", "vddr", "vss", "vsubs"]


class Ring2Sizing(unittest.TestCase):
    def test_ring2_params_are_xr2_not_xr1(self):
        self.assertEqual(bd.ring_instance_params(DESIGN, bd.RING2).split(), bd.RING2_PARAMS.split())
        self.assertNotEqual(bd.RING2_PARAMS.split(), bd.RING1_PARAMS.split())
        self.assertIn("wstv=0.240u", bd.RING2_PARAMS)

    def test_ring2_dut_carries_ring2_sizing_and_top(self):
        text = bd.RING2.dut.read_text()
        self.assertIn(f".subckt ro_ring11_ring2 {' '.join(bd.dut_header(text, bd.RING2))} {bd.RING2_PARAMS}", text)
        self.assertNotIn("wstv=0.220u", text)

    def test_committed_ring2_dut_matches_source(self):
        self.assertIsNone(bd.dut_source_problem(ring=bd.RING2))

    def test_ring1_substitution_is_rejected(self):
        ring1_dut = bd.RING1.dut.read_text()
        problem = bd.dut_source_problem(ring1_dut, ring=bd.RING2)
        self.assertIn("no .subckt ro_ring11_ring2", problem)
        # a ring1 body relabelled as ring2 still differs from the ring2 render
        relabelled = ring1_dut.replace(".subckt ro_ring11 ", ".subckt ro_ring11_ring2 ")
        self.assertIn("does not match", bd.dut_source_problem(relabelled, ring=bd.RING2))

    def test_xr2_with_ring1_sizing_refuses(self):
        same = DESIGN.replace("wstv=0.240u", "wstv=0.220u")
        with self.assertRaises(bd.BuildError) as cm:
            bd.render_dut(HEADER2, same, bd.RING2)
        self.assertIn("disagrees with xr2", str(cm.exception))
        # even a restated ring2 constant that was edited to match is refused
        edited = bd.RING2._replace(params=bd.RING1_PARAMS)
        with self.assertRaises(bd.BuildError) as cm:
            bd.render_dut(HEADER2, same, edited)
        self.assertIn("really ring1", str(cm.exception))

    def test_drifted_xr2_sizing_makes_dut_stale(self):
        problem = bd.dut_source_problem(design=DESIGN.replace("wstv=0.240u", "wstv=0.250u"), ring=bd.RING2)
        self.assertIn("disagrees with xr2", problem)

    def test_missing_xr2_refuses(self):
        problem = bd.dut_source_problem(design=DESIGN.replace("xr2 ", "xq2 "), ring=bd.RING2)
        self.assertIn("no xr2 ro_ring11 instance", problem)

    def test_identities_are_independent(self):
        self.assertNotEqual(bd.source_identity(ring=bd.RING1), bd.source_identity(ring=bd.RING2))
        # editing ring1's sizing moves ring1's identity only
        edited = DESIGN.replace("xr1 en1 rn1 vddr1 vss ro_ring11 wstv=0.220u", "xr1 en1 rn1 vddr1 vss ro_ring11 wstv=0.230u")
        self.assertNotEqual(bd.source_identity(edited, bd.RING1), bd.source_identity(DESIGN, bd.RING1))
        self.assertEqual(bd.source_identity(edited, bd.RING2), bd.source_identity(DESIGN, bd.RING2))

    def test_ring1_fixture_is_unchanged_by_the_ring_parameter(self):
        self.assertEqual(bd.RING1.top, "ro_ring11")
        self.assertIsNone(bd.dut_source_problem())


def netlist(header, top="ro_ring11_ring2", order=None):
    ring = [p for p in header if p not in bd.NAMED_PORTS]
    order = order or list(range(len(ring)))
    lines = [f".SUBCKT {top} " + " ".join(header)]
    for port, pos in zip(ring, order):
        lines += [f"* device instance $1 r0 nfet {100.0 * pos},0.0 nfet", f"X1 d {port} s b nfet_03v3"]
    return "\n".join(lines + [".ENDS"]) + "\n"


class Ring2Ports(unittest.TestCase):
    RING = [f"a|y{'' if i == 0 else '$' + str(i)}" for i in range(11)]
    NAMED = ["en", "vddr", "vss", "vsubs"]

    def test_ring2_ports_resolve_by_geometry_not_ring1_order(self):
        order = [3, 0, 10, 5, 1, 9, 2, 8, 4, 7, 6]
        got = bd.extraction_port_map(netlist(self.RING + self.NAMED, order=order), bd.RING2)
        self.assertEqual(got, [bd.RING_NODES[p] for p in order] + self.NAMED)

    def test_ring1_extraction_is_not_accepted_as_ring2(self):
        with self.assertRaises(bd.BuildError) as cm:
            bd.extraction_port_map(netlist(self.RING + self.NAMED, top="ro_ring11"), bd.RING2)
        self.assertIn("no .SUBCKT ro_ring11_ring2", str(cm.exception))

    def test_ambiguous_ports_refused(self):
        text = netlist(self.RING + self.NAMED, order=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9])
        with self.assertRaises(bd.BuildError) as cm:
            bd.extraction_port_map(text, bd.RING2)
        self.assertIn("tie on leftmost gate x", str(cm.exception))

    def test_testbench_xdut_follows_the_dut_header(self):
        header = bd.dut_header(bd.RING2.dut.read_text(), bd.RING2)
        bd.check_testbench(header, bd.RING2)
        with self.assertRaises(bd.BuildError):
            bd.check_testbench(header[1:] + header[:1], bd.RING2)


class Ring2Fixture(unittest.TestCase):
    def test_request_pairs_ring1_grid_and_measurements(self):
        self.assertEqual(check.ring2_request_problems(), [])
        r2 = json.loads((ROOT / check.RING2_INPUTS[0]).read_text())
        self.assertEqual(len(check.request_corner_ids(r2)), check.ITEM7A_CORNERS)
        self.assertEqual([m["name"] for m in r2["measurements"]],
                         ["period_s", "supply_current_avg_a", "ro_swing_v"])

    def test_committed_state_is_an_unrun_fixture_that_passes_the_gate(self):
        self.assertFalse((ROOT / check.RING2_ENVELOPE).exists())
        self.assertEqual(check.verify_ring2_pex_publication({"evidence": {}}), [])

    def test_manifest_must_not_cite_ring2(self):
        manifest = {"evidence": {"7.analog": {"file": check.RING2_ENVELOPE, "content_hash": "x"}}}
        self.assertTrue(any("not part of any citation" in p for p in check.verify_ring2_pex_publication(manifest)))
        real = json.loads(check.MANIFEST.read_text())
        self.assertEqual(real["evidence"]["7.analog"]["file"], check.ITEM7A_ENVELOPE)


class Ring2Verdict(unittest.TestCase):
    """Missing measurements are `incomplete`, never a pass."""

    def setUp(self):
        self.req = json.loads((ROOT / check.RING2_INPUTS[0]).read_text())
        self.env = {"delta": [
            {"corner_id": c, "spec_row": m["name"], "status": "pass",
             "schematic_value": 1.0, "extracted_value": 1.1}
            for c in check.request_corner_ids(self.req) for m in self.req["measurements"]]}

    def test_complete_run_is_measured_on_all_81_rows(self):
        v = check.combiner_sampler_verdict(self.env, self.req)
        self.assertEqual((v["verdict"], v["counts"]["measured"]), ("pass", 81))

    def test_missing_row_and_one_sided_row_are_incomplete(self):
        env = copy.deepcopy(self.env)
        env["delta"].pop()
        env["delta"][0]["extracted_value"] = None
        v = check.combiner_sampler_verdict(env, self.req)
        self.assertEqual(v["verdict"], "incomplete")
        self.assertEqual(v["counts"]["unmeasured"], 2)


if __name__ == "__main__":
    unittest.main()
