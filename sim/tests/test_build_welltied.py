"""The ring1 well-tie rewiring generator (issue #339): count, stability, failure."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "build_welltied", ROOT / "sim/tb/ro-ring11-pex-welltied/build_welltied.py"
)
bw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bw)

BODY_BIAS = {
    "status": "unbiased",
    "unbiased_device_count": 2,
    "unbiased_nets": ["\\$9"],
    "unbiased_pmos_body_nets": [
        {"device": "$1", "net": "\\$9"},
        {"device": "$2", "net": "\\$9"},
    ],
}
NETLIST = (
    "* device instance $1 r0 *1 0,0 pfet\n"
    "X$1 d1 g1 vddr__t1 \\$9 pfet_03v3 L=2U W=0.22U\n"
    "+ PS=2.28U PD=1.24U\n"
    "* device instance $2 r0 *1 1,0 pfet\n"
    "X$2 d2 g2 s2 \\$9 pfet_03v3 L=0.28U W=0.44U\n"
    "X$3 d3 g3 s3 vsubs nfet_03v3 L=0.28U W=0.44U\n"
    "Cx a b 1e-15\n"
)


class Rewire(unittest.TestCase):
    def test_rewires_only_the_listed_bodies(self):
        out, n = bw.rewire(NETLIST, BODY_BIAS)
        self.assertEqual(n, 2)
        self.assertIn("X$1 d1 g1 vddr__t1 vddr pfet_03v3 L=2U W=0.22U\n+ PS=2.28U PD=1.24U", out)
        self.assertIn("X$2 d2 g2 s2 vddr pfet_03v3", out)
        self.assertIn("X$3 d3 g3 s3 vsubs nfet_03v3", out)
        self.assertNotIn("\\$9", out)

    def test_deterministic(self):
        self.assertEqual(bw.rewire(NETLIST, BODY_BIAS), bw.rewire(NETLIST, BODY_BIAS))

    def test_missing_device_raises(self):
        with self.assertRaisesRegex(bw.BuildError, "no card"):
            bw.rewire(NETLIST.replace("X$2 ", "Y$2 "), BODY_BIAS)

    def test_count_mismatch_raises(self):
        bb = copy.deepcopy(BODY_BIAS)
        bb["unbiased_device_count"] = 3
        with self.assertRaisesRegex(bw.BuildError, "unbiased_device_count"):
            bw.rewire(NETLIST, bb)

    def test_body_not_matching_envelope_raises(self):
        with self.assertRaisesRegex(bw.BuildError, "body is"):
            bw.rewire(NETLIST.replace("g2 s2 \\$9", "g2 s2 \\$7"), BODY_BIAS)

    def test_unlisted_pfet_raises(self):
        with self.assertRaisesRegex(bw.BuildError, "not in the envelope"):
            bw.rewire(NETLIST + "X$4 d g s \\$11 pfet_03v3 L=1U W=1U\n", BODY_BIAS)

    def test_listed_nfet_raises(self):
        with self.assertRaisesRegex(bw.BuildError, "model is"):
            bw.rewire(NETLIST.replace("s2 \\$9 pfet_03v3", "s2 \\$9 nfet_03v3"), BODY_BIAS)

    def test_well_still_referenced_raises(self):
        with self.assertRaisesRegex(bw.BuildError, "still referenced"):
            bw.rewire(NETLIST + "Cw \\$9 0 1e-15\n", BODY_BIAS)

    def test_not_unbiased_raises(self):
        bb = copy.deepcopy(BODY_BIAS)
        bb["status"] = "biased"
        with self.assertRaisesRegex(bw.BuildError, "status"):
            bw.rewire(NETLIST, bb)


class CommittedFiles(unittest.TestCase):
    def test_ring1_ties_23_of_23(self):
        bb = json.loads(bw.ENVELOPE.read_text())["body_bias"]
        out, n = bw.rewire(bw.SOURCE_NETLIST.read_text(), bb)
        self.assertEqual((n, bb["unbiased_device_count"]), (23, 23))
        self.assertEqual(len(bb["unbiased_nets"]), 11)

    def test_committed_outputs_are_current(self):
        netlist, tb = bw.render()
        self.assertEqual(bw.OUT_NETLIST.read_text(), netlist)
        self.assertEqual(bw.OUT_TB.read_text(), tb)

    def test_request_matches_sibling_except_testbench_and_artifacts(self):
        a = json.loads((ROOT / "sim/tb/ro-ring11-pex/request.json").read_text())
        b = json.loads((bw.HERE / "request.json").read_text())
        for r in (a, b):
            r.pop("netlist")
            r["options"].pop("keep_artifacts")
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
