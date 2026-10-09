"""combiner-sampler-pex (#418): port resolution, fixture freshness and verdict, offline.

No klt, ngspice or PDK. The extracted netlist used here is the committed
layout/reports/combiner_sampler.extracted.spice (a `klt extract` of the same
GDS without parasitics) plus synthetic mutations of it, so the connectivity
match is exercised on the real block's topology.
"""

import copy
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TB = ROOT / "sim" / "tb" / "combiner-sampler-pex"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bd = _load("cs_build_dut", TB / "build_dut.py")
st = _load("cs_stimulus", TB / "stimulus.py")
sys.path.insert(0, str(ROOT / "signoff"))
check = _load("cs_check", ROOT / "signoff" / "check.py")

REPORT = (ROOT / "layout" / "reports" / "combiner_sampler.extracted.spice").read_text()
WANT = ["rn1", "rn2", "ro1", "ro2", "clk", "vdd", "xo", "raw_bit", "raw_valid",
        "ring_bit1", "ring_bit2", "rst_n", "vss", "vsubs"]


def _sources():
    return {bd.ARRAY_SRC: bd.ARRAY_SRC.read_text(), bd.SAMPLER_SRC: bd.SAMPLER_SRC.read_text()}


class PortMap(unittest.TestCase):
    def test_real_extraction_resolves_uniquely(self):
        self.assertEqual(bd.extraction_port_map(REPORT), WANT)

    def test_committed_dut_header_is_the_resolved_map(self):
        self.assertEqual(bd.dut_header(bd.DUT.read_text()), WANT)

    def test_header_order_follows_the_extraction(self):
        # Moving ports in the extracted header moves them in the result.
        text = REPORT.replace(
            ".SUBCKT combiner_sampler a a$1 a|d|y b|d|y clk d|vdd d|y q q$1 q$2 q$3 rst_n\n+ vss vsubs",
            ".SUBCKT combiner_sampler q$3 a$1 a|d|y b|d|y clk d|vdd d|y q q$1 q$2 a rst_n\n+ vss vsubs",
        )
        got = bd.extraction_port_map(text)
        self.assertEqual(got[0], "ring_bit2")
        self.assertEqual(got[10], "rn1")

    def assertRefuses(self, text, fragment, dut_text=None):
        with self.assertRaises(bd.BuildError) as cm:
            bd.extraction_port_map(text, dut_text)
        self.assertIn(fragment, str(cm.exception))

    def test_ambiguous_map_is_refused(self):
        # The only thing that tells ring 1 from ring 2 in this block is the
        # XOR's NMOS stacks (a/an on top, b/bn at the bottom). Make both
        # stacks symmetric -- on BOTH sides, so the circuits still match --
        # and rn1/rn2, ro1/ro2 and ring_bit1/ring_bit2 become
        # indistinguishable by connectivity. The map must refuse, not guess.
        dut = bd.render_dut(WANT, _sources())
        dut = dut.replace("XMn2 s1 b vss vss", "XMn2 y b s1 vss").replace(
            "XMn4 s2 bn vss vss", "XMn4 y bn s2 vss")
        ext = REPORT.replace("X$4 \\$6 b|d|y vss vsubs", "X$4 d|y b|d|y \\$6 vsubs").replace(
            "X$6 \\$8 \\$5 vss vsubs", "X$6 d|y \\$5 \\$8 vsubs")
        self.assertNotEqual(ext, REPORT)
        self.assertRefuses(ext, "ambiguous", dut)

    def test_symmetric_toy_circuit_is_ambiguous(self):
        dut = (
            ".subckt combiner_sampler rn1 rn2 ro1 ro2 vdd vss vsubs\n"
            "xb1 rn1 ro1 vdd vss ro_buf\nxb2 rn2 ro2 vdd vss ro_buf\n.ends\n"
            ".subckt ro_buf a y vdd vss\n"
            "XMp y a vdd vdd pfet_03v3 L=0.28u W=0.44u\nXMn y a vss vss nfet_03v3 L=0.28u W=0.22u\n.ends\n"
        )
        ext = (
            ".SUBCKT combiner_sampler a a$1 y y$1 vdd vss vsubs\n"
            "X$1 y a vdd \\$9 pfet_03v3 L=0.28U W=0.44U\nX$2 y a vss vsubs nfet_03v3 L=0.28U W=0.22U\n"
            "X$3 y$1 a$1 vdd \\$8 pfet_03v3 L=0.28U W=0.44U\nX$4 y$1 a$1 vss vsubs nfet_03v3 L=0.28U W=0.22U\n"
            ".ENDS\n"
        )
        self.assertRefuses(ext, "ambiguous", dut)

    def test_topology_mismatch_is_refused(self):
        # Delete one sampler device from the extraction.
        ext = re.sub(r"\* device instance \$8 .*\nX\$8 .*\n\+.*\n", "", REPORT)
        self.assertNotEqual(ext, REPORT)
        self.assertRefuses(ext, "not the same circuit")

    def test_wrong_device_size_is_refused(self):
        ext = REPORT.replace("X$1 vss a a|d|y vsubs nfet_03v3 L=0.28U W=0.22U",
                             "X$1 vss a a|d|y vsubs nfet_03v3 L=0.28U W=0.44U")
        self.assertRefuses(ext, "not the same circuit")

    def test_label_vetoes_a_contradicting_map(self):
        # Swap the names `clk` and `rst_n` in the extraction: connectivity
        # still resolves, but the labels contradict it.
        ext = REPORT.replace("clk", "TMP").replace("rst_n", "clk").replace("TMP", "rst_n")
        self.assertRefuses(ext, "carries label")

    def test_repeated_header_port_is_refused(self):
        ext = REPORT.replace("q$3 rst_n\n+ vss vsubs", "q$3 rst_n\n+ vss vsubs q")
        self.assertRefuses(ext, "repeats a port")

    def test_missing_vsubs_is_refused(self):
        ext = REPORT.replace("+ vss vsubs\n", "+ vss\n", 1)
        self.assertRefuses(ext, "'vsubs' 0 times")

    def test_ground_tie_resistor_is_not_a_wire(self):
        ext = REPORT.replace(".ENDS", "Rtie vss 0 1e12\nRtie2 vdd|x 0 1e12\n.ENDS")
        self.assertEqual(bd.extraction_port_map(ext), WANT)

    def test_parasitic_star_is_merged(self):
        # Re-point a device terminal at a star node tied to its net by an R.
        ext = REPORT.replace("X$1 vss a a|d|y vsubs", "X$1 vss__t0 a__t0 a|d|y vsubs")
        ext = ext.replace(".ENDS", "R1 vss__t0 vss 10\nR2 a a__t0 12\n.ENDS")
        self.assertEqual(bd.extraction_port_map(ext), WANT)


class Fixture(unittest.TestCase):
    def test_committed_dut_matches_source(self):
        self.assertIsNone(bd.dut_source_problem())

    def test_stale_dut_is_detected(self):
        stale = bd.DUT.read_text().replace("xsv vdd clk", "xsv vss clk")
        self.assertIn("does not match", bd.dut_source_problem(dut_text=stale))

    def test_source_change_is_detected(self):
        src = _sources()
        src[bd.SAMPLER_SRC] = src[bd.SAMPLER_SRC].replace(
            "XMpc clkb clk vdd vdd pfet_03v3 L=0.28u W=0.44u", "XMpc clkb clk vdd vdd pfet_03v3 L=0.28u W=0.88u")
        self.assertIn("does not match", bd.dut_source_problem(sources=src))
        self.assertNotEqual(bd.source_identity(src), bd.source_identity())

    def test_unrelated_source_edit_keeps_identity(self):
        src = _sources()
        src[bd.ARRAY_SRC] = src[bd.ARRAY_SRC].replace(
            "xr2 en2 rn2 vddr2 vss ro_ring11 wstv=0.240u", "xr2 en2 rn2 vddr2 vss ro_ring11 wstv=0.300u")
        src[bd.ARRAY_SRC] = "* a new comment\n" + src[bd.ARRAY_SRC]
        self.assertEqual(bd.source_identity(src), bd.source_identity())

    def test_diverging_embedded_copy_is_refused(self):
        src = _sources()
        src[bd.SAMPLER_SRC] = src[bd.SAMPLER_SRC].replace(
            "XMp1 mid a vdd vdd pfet_03v3 L=0.28u W=0.88u", "XMp1 mid a vdd vdd pfet_03v3 L=0.28u W=0.44u")
        with self.assertRaises(bd.BuildError):
            bd.audit_sources(src)

    def test_testbench_and_request_are_current(self):
        self.assertEqual(st.TESTBENCH.read_text(), st.render_testbench())
        self.assertEqual(st.REQUEST.read_text(), st.render_request_text())

    def test_testbench_xdut_matches_dut(self):
        bd.check_testbench(bd.dut_header(bd.DUT.read_text()))

    def test_contract_covers_every_input_combination_and_toggle(self):
        exp = st.expected()
        combos = {(e["pre_e%d_ro1" % k], e["pre_e%d_ro2" % k]) for e in [exp] for k in range(3, 9)}
        self.assertEqual(combos, {(0, 0), (0, 1), (1, 0), (1, 1)})
        for k in range(3, 9):
            self.assertEqual(exp[f"cap_e{k}_raw_bit"], exp[f"pre_e{k}_xo"])
            self.assertEqual(exp[f"pre_e{k}_xo"], exp[f"pre_e{k}_ro1"] ^ exp[f"pre_e{k}_ro2"])
            self.assertEqual(exp[f"cap_e{k}_ring_bit1"], exp[f"pre_e{k}_ro1"])
            self.assertEqual(exp[f"cap_e{k}_raw_valid"], 1)
        for f in st.FLOPS:
            seq = [exp[f"cap_e{k}_{f}"] for k in range(3, 9)]
            if f != "raw_valid":
                self.assertIn((0, 1), list(zip(seq, seq[1:])), f)
                self.assertIn((1, 0), list(zip(seq, seq[1:])), f)
            for name in ("rst_hold_e1", "rst_hold_e2", "startup_pre_e3", "rst_async", "rst_hold_e9"):
                self.assertEqual(exp[f"{name}_{f}"], 0)

    def test_reset_hold_is_not_trivial(self):
        # During reset each flop sees at least one capture edge with D = 1.
        d_at = {}
        for t in (st.RISES[0], st.RISES[1], st.RISES[8]):
            rn1, rn2 = st._level(st.INPUTS, t, 1), st._level(st.INPUTS, t, 2)
            ro1, ro2 = 1 - rn1, 1 - rn2
            d_at[t] = {"raw_bit": ro1 ^ ro2, "raw_valid": 1, "ring_bit1": ro1, "ring_bit2": ro2}
        for f in st.FLOPS:
            self.assertTrue(any(d[f] for d in d_at.values()), f)


def _request():
    return json.loads(st.REQUEST.read_text())


def _envelope(request, value=None):
    """A synthetic, fully measured envelope consistent with the request."""
    rows = []
    for corner in check.request_corner_ids(request):
        for m in request["measurements"]:
            lim = m.get("limits") or {}
            v = value if value is not None else (1.0 if "min" in lim else 0.0 if "max" in lim else 1e-10)
            rows.append({"spec_row": m["name"], "corner_id": corner, "schematic_value": v,
                         "extracted_value": v, "delta_pct": 0.0, "status": "pass"})
    return {"delta": rows}


class Verdict(unittest.TestCase):
    def setUp(self):
        self.req = _request()
        self.env = _envelope(self.req)

    def test_grid_is_dr0006(self):
        ids = check.request_corner_ids(self.req)
        self.assertEqual(len(ids), 27)
        self.assertIn("tt/2.970V/-40C", ids)
        self.assertIn("ss/3.630V/125C", ids)

    def test_full_pass(self):
        v = check.combiner_sampler_verdict(self.env, self.req)
        self.assertEqual(v["verdict"], "pass")
        self.assertEqual(v["counts"]["unmeasured"], 0)
        self.assertEqual(v["counts"]["measured"], 27 * 4)
        self.assertEqual(v["counts"]["pass"], 27 * 62)

    def test_missing_corner_is_incomplete(self):
        self.env["delta"] = [r for r in self.env["delta"] if r["corner_id"] != "ss/2.970V/125C"]
        v = check.combiner_sampler_verdict(self.env, self.req)
        self.assertEqual(v["verdict"], "incomplete")
        self.assertEqual(v["counts"]["unmeasured"], 66)

    def test_missing_measurement_is_incomplete(self):
        self.env["delta"] = [r for r in self.env["delta"]
                             if not (r["spec_row"] == "cap_e5_raw_bit" and r["corner_id"] == "tt/3.300V/27C")]
        v = check.combiner_sampler_verdict(self.env, self.req)
        self.assertEqual(v["verdict"], "incomplete")
        self.assertEqual(v["unmeasured"], ["tt/3.300V/27C/cap_e5_raw_bit"])

    def test_null_side_is_unmeasured_not_pass(self):
        for side in ("schematic_value", "extracted_value"):
            env = copy.deepcopy(self.env)
            env["delta"][0][side] = None
            v = check.combiner_sampler_verdict(env, self.req)
            self.assertEqual(v["verdict"], "incomplete", side)
        env = copy.deepcopy(self.env)
        env["delta"][-1]["extracted_value"] = None  # an informational row
        self.assertEqual(check.combiner_sampler_verdict(env, self.req)["verdict"], "incomplete")

    def test_schematic_side_limit_failure_is_a_failure(self):
        # klt pex grades only the extracted side; the verdict grades both.
        row = next(r for r in self.env["delta"] if r["spec_row"] == "cap_e5_raw_bit")
        row["schematic_value"] = 0.5
        v = check.combiner_sampler_verdict(self.env, self.req)
        self.assertEqual(v["verdict"], "fail")
        self.assertEqual(v["failures"][0]["sides"], ["schematic"])
        self.assertEqual(v["consistency_problems"], [])

    def test_extracted_failure_must_agree_with_klt_status(self):
        row = next(r for r in self.env["delta"] if r["spec_row"] == "cap_e5_raw_bit")
        row["extracted_value"] = 0.05
        v = check.combiner_sampler_verdict(self.env, self.req)
        self.assertEqual(v["verdict"], "fail")
        self.assertTrue(v["consistency_problems"])  # klt said pass for a violating value
        row["status"] = "fail"
        self.assertEqual(check.combiner_sampler_verdict(self.env, self.req)["consistency_problems"], [])

    def test_undeclared_corner_is_flagged(self):
        self.env["delta"].append({"spec_row": "cap_e5_raw_bit", "corner_id": "tt/1.800V/27C",
                                  "schematic_value": 1.0, "extracted_value": 1.0, "status": "pass"})
        v = check.combiner_sampler_verdict(self.env, self.req)
        self.assertTrue(any("undeclared" in p for p in v["consistency_problems"]))


class Publication(unittest.TestCase):
    """Freshness of the committed publication, when one is committed."""

    def setUp(self):
        self.pub_path = ROOT / check.CS_PUBLICATION
        self.env_path = ROOT / check.CS_ENVELOPE
        if not self.pub_path.is_file():
            self.skipTest("no combiner_sampler publication committed")
        self.pub = json.loads(self.pub_path.read_text())
        self.env = json.loads(self.env_path.read_text())

    def test_committed_publication_is_current(self):
        self.assertEqual(check.combiner_sampler_problems(self.pub, self.env), [])

    def test_hand_edited_verdict_is_rejected(self):
        pub = copy.deepcopy(self.pub)
        pub["verdict"]["verdict"] = "pass" if pub["verdict"]["verdict"] != "pass" else "fail"
        self.assertIn("recorded verdict is not what the envelope and request yield today",
                      check.combiner_sampler_problems(pub, self.env))

    def test_stale_input_pin_is_rejected(self):
        pub = copy.deepcopy(self.pub)
        pub["inputs_sha256"][check.CS_REQUEST] = "sha256:" + "0" * 64
        self.assertTrue(any("STALE" in p for p in check.combiner_sampler_problems(pub, self.env)))

    def test_stale_source_identity_is_rejected(self):
        pub = copy.deepcopy(self.pub)
        pub["source_sha256"] = "sha256:" + "0" * 64
        self.assertTrue(any("source identity" in p for p in check.combiner_sampler_problems(pub, self.env)))

    def test_body_bias_must_be_stated_verbatim(self):
        pub = copy.deepcopy(self.pub)
        pub["body_bias_status"] = "biased"
        self.assertTrue(any("body_bias_status" in p for p in check.combiner_sampler_problems(pub, self.env)))


if __name__ == "__main__":
    unittest.main()
