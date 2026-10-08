"""Item 7 (analog) publication gate: stale, partial or failing evidence is rejected."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("signoff_check", ROOT / "signoff" / "check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class Item7AnalogPublication(unittest.TestCase):
    def setUp(self):
        self.pub = json.loads((ROOT / check.ITEM7A_PUBLICATION).read_text())
        self.env = json.loads((ROOT / check.ITEM7A_ENVELOPE).read_text())

    def test_committed_publication_is_current(self):
        self.assertEqual(check.item7_analog_problems(self.pub, self.env), [])

    def test_manifest_cites_and_pins_it(self):
        manifest = json.loads(check.MANIFEST.read_text())
        self.assertEqual(check.verify_item7_analog_publication(manifest), [])
        entry = manifest["evidence"]["7.analog"]
        self.assertEqual(entry["content_hash"], check.pinned_input_hash(self.env))

    def test_stale_testbench_input_rejected(self):
        pub = copy.deepcopy(self.pub)
        pub["inputs_sha256"][check.ITEM7A_INPUTS[2]] = "sha256:" + "0" * 64
        self.assertTrue(any("STALE" in p for p in check.item7_analog_problems(pub, self.env)))

    def test_body_bias_must_be_stated_as_the_envelope_says(self):
        pub = copy.deepcopy(self.pub)
        pub["body_bias_status"] = "biased"
        self.assertTrue(any("body_bias" in p for p in check.item7_analog_problems(pub, self.env)))

    def test_failed_partial_or_one_sided_run_rejected(self):
        env = copy.deepcopy(self.env)
        env["status"] = "fail"
        self.assertTrue(check.item7_analog_problems(self.pub, env))
        env = copy.deepcopy(self.env)
        env["delta"] = env["delta"][:-1]
        self.assertTrue(check.item7_analog_problems(self.pub, env))
        env = copy.deepcopy(self.env)
        env["delta"][0]["extracted_value"] = None
        self.assertTrue(check.item7_analog_problems(self.pub, env))
        env = copy.deepcopy(self.env)
        env["pin_count_mismatch"] = {"detail": "x"}
        self.assertTrue(check.item7_analog_problems(self.pub, env))

    def test_netlist_must_be_the_one_the_run_extracted(self):
        env = copy.deepcopy(self.env)
        env["extraction"]["netlist_sha256"] = "0" * 64
        self.assertTrue(any("not the netlist" in p for p in check.item7_analog_problems(self.pub, env)))

    def test_freshness_gate_reads_the_pex_layout_object(self):
        failures: list[str] = []
        ok = check.check_envelope_against_its_input(ROOT / check.ITEM7A_ENVELOPE, self.env, failures)
        self.assertTrue(ok, failures)
        env = copy.deepcopy(self.env)
        env["provenance"]["input"]["content_hash"] = "sha256:" + "0" * 64
        failures = []
        self.assertFalse(check.check_envelope_against_its_input(ROOT / check.ITEM7A_ENVELOPE, env, failures))


class Item7AnalogDutSource(unittest.TestCase):
    """The generated DUT is held to design/ro_array_core.spice, offline."""

    @classmethod
    def setUpClass(cls):
        cls.bd = check._load_build_dut()
        cls.design = cls.bd.DESIGN.read_text()
        cls.dut = cls.bd.DUT.read_text()

    def test_current_source_and_dut_agree_without_klt(self):
        self.assertEqual(check.item7_analog_dut_source_problems(), [])
        self.assertIsNone(self.bd.dut_source_problem())

    def test_changed_leaf_device_with_old_dut_is_reported(self):
        stage = self.bd._subckt_block(self.design, "ro_stage")
        line = next(l for l in stage if l.lower().startswith("xmp") or " pmos" in l.lower() or "pfet" in l.lower())
        changed = self.design.replace(line, line + " m=2", 1)
        problem = self.bd.dut_source_problem(self.dut, changed)
        self.assertIsNotNone(problem)
        self.assertIn("does not match", problem)
        self.assertIn("m=2", problem)
        self.assertNotEqual(self.bd.source_identity(changed), self.bd.source_identity(self.design))

    def test_regenerated_dut_still_fails_the_publication_hash(self):
        stage = self.bd._subckt_block(self.design, "ro_stage")
        line = next(l for l in stage if l.lower().startswith("xmp") or " pmos" in l.lower() or "pfet" in l.lower())
        regenerated = self.bd.render_dut(self.bd.dut_header(self.dut), self.design.replace(line, line + " m=2", 1))
        self.assertIsNone(self.bd.dut_source_problem(regenerated, self.design.replace(line, line + " m=2", 1)))
        self.assertNotEqual(
            "sha256:" + __import__("hashlib").sha256(regenerated.encode()).hexdigest(),
            json.loads((ROOT / check.ITEM7A_PUBLICATION).read_text())["inputs_sha256"][check.ITEM7A_INPUTS[2]],
        )

    def test_unrelated_source_edits_do_not_move_identity(self):
        edited = self.design + "\n* a trailing comment\n.subckt unrelated a b\nr1 a b 1k\n.ends\n"
        self.assertEqual(self.bd.source_identity(edited), self.bd.source_identity(self.design))
        self.assertIsNone(self.bd.dut_source_problem(self.dut, edited))

    def test_ring_sizing_is_audited_against_xr1(self):
        self.assertEqual(self.bd.ring1_instance_params(self.design).split(), self.bd.RING1_PARAMS.split())
        drifted = self.design.replace("xr1 en1 rn1 vddr1 vss ro_ring11 wstv=0.220u", "xr1 en1 rn1 vddr1 vss ro_ring11 wstv=0.230u", 1)
        self.assertNotEqual(drifted, self.design)
        with self.assertRaises(self.bd.BuildError):
            self.bd.render_dut(self.bd.dut_header(self.dut), drifted)

    def test_recorded_source_identity_must_match_current(self):
        pub = json.loads((ROOT / check.ITEM7A_PUBLICATION).read_text())
        pub["source_sha256"] = self.bd.source_identity()
        self.assertEqual(check.item7_analog_dut_source_problems(pub), [])
        pub["source_sha256"] = "sha256:" + "0" * 64
        self.assertTrue(any("STALE" in p for p in check.item7_analog_dut_source_problems(pub)))


if __name__ == "__main__":
    unittest.main()
