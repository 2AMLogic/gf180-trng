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


if __name__ == "__main__":
    unittest.main()
