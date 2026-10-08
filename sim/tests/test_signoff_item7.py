"""Item 7 (digital) publication gate: stale or failing evidence is rejected."""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("signoff_check", ROOT / "signoff" / "check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class Item7Publication(unittest.TestCase):
    def setUp(self):
        self.pub = json.loads((ROOT / check.ITEM7_PUBLICATION).read_text())
        self.env = json.loads((ROOT / check.ITEM7_ENVELOPE).read_text())

    def test_committed_publication_is_current(self):
        self.assertEqual(check.item7_problems(self.pub, self.env), [])

    def test_stale_netlist_rejected(self):
        pub = copy.deepcopy(self.pub)
        pub["netlist"]["sha256"] = "sha256:" + "0" * 64
        self.assertTrue(any("netlist: STALE" in p for p in check.item7_problems(pub, self.env)))

    def test_stale_sdf_rejected(self):
        pub = copy.deepcopy(self.pub)
        pub["sdf"]["sha256"] = "sha256:" + "0" * 64
        self.assertTrue(any("sdf: STALE" in p for p in check.item7_problems(pub, self.env)))

    def test_unannotated_or_failed_response_rejected(self):
        env = copy.deepcopy(self.env)
        env["environment"]["sdf"]["annotated"] = False
        self.assertTrue(check.item7_problems(self.pub, env))
        env = copy.deepcopy(self.env)
        env["status"] = "fail"
        self.assertTrue(check.item7_problems(self.pub, env))

    def test_changed_raw_evidence_rejected(self):
        pub = copy.deepcopy(self.pub)
        pub["raw_sha256"]["verdict.json"] = "sha256:" + "0" * 64
        self.assertTrue(any("verdict.json" in p for p in check.item7_problems(pub, self.env)))


if __name__ == "__main__":
    unittest.main()
