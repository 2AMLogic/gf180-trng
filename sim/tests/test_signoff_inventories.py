"""Item 1/2/9/10 inventories: the drift gate must name what moved (#653).

signoff/inventories.py rebuilds each inventory from the live tree, and
signoff/check.py fails when the committed one no longer matches. The cases
here copy only the files an inventory reads into a temporary root, so a file
can be changed, added or removed without touching the real tree. Stdlib only;
no klt, no PDK.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
from sim.tools.pathload import load_module_from_path  # noqa: E402  (#553)

inv = load_module_from_path("signoff_inventories_under_test", ROOT / "signoff" / "inventories.py")

WORKFLOWS = [inv.CI_WORKFLOW, inv.NIGHTLY_WORKFLOW]


def copy_files(dest: Path, rels) -> None:
    for rel in rels:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)


def globbed(*patterns: str) -> list[str]:
    return inv._glob(ROOT, *patterns)


class InventoryDrift(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def stage_item10(self):
        copy_files(self.root, [*WORKFLOWS, "README.md", "LICENSE", inv.SPEC, "sim/README.md", "package.json"])

    def stage_item9_digital(self):
        files = [
            *WORKFLOWS, "README.md", "sim/README.md", "sim/pdk.json", "package.json",
            *inv.DOCUMENTED_BY.values(),
        ]
        for slug in inv.DIGITAL_TESTBENCHES:
            files += globbed(f"sim/tb/{slug}/**/*")
        copy_files(self.root, files)

    def test_unchanged_tree_has_no_drift(self):
        self.stage_item10()
        built = inv.build_inventory(self.root, 10, "analog")
        self.assertEqual(inv.diff_inventory(built, inv.build_inventory(self.root, 10, "analog")), [])

    def test_changed_member_is_named(self):
        self.stage_item10()
        committed = inv.build_inventory(self.root, 10, "digital")
        with (self.root / "LICENSE").open("ab") as handle:
            handle.write(b"\n")
        problems = inv.diff_inventory(committed, inv.build_inventory(self.root, 10, "digital"))
        self.assertEqual(problems, ["LICENSE: changed since it was inventoried"])

    def test_added_testbench_file_is_named(self):
        self.stage_item9_digital()
        committed = inv.build_inventory(self.root, 9, "digital")
        (self.root / "sim/tb/interface-regfile/extra_tb.v").write_text("module extra; endmodule\n")
        problems = inv.diff_inventory(committed, inv.build_inventory(self.root, 9, "digital"))
        self.assertEqual(problems, ["sim/tb/interface-regfile/extra_tb.v: in the tree but absent from the inventory"])

    def test_removed_testbench_file_is_named(self):
        self.stage_item9_digital()
        committed = inv.build_inventory(self.root, 9, "digital")
        (self.root / "sim/tb/smoke-trng-top/run_demo.py").unlink()
        problems = inv.diff_inventory(committed, inv.build_inventory(self.root, 9, "digital"))
        self.assertEqual(problems, ["sim/tb/smoke-trng-top/run_demo.py: listed in the inventory but no longer in the tree"])

    def test_unclassified_testbench_directory_fails_the_audit(self):
        self.stage_item9_digital()
        (self.root / "sim/tb/new-bench").mkdir()
        (self.root / "sim/tb/new-bench/run.py").write_text("print(1)\n")
        with self.assertRaises(inv.AuditError) as ctx:
            inv.build_inventory(self.root, 9, "digital")
        self.assertIn("not classified in DIGITAL_TESTBENCHES", str(ctx.exception))

    def test_gate_the_workflow_does_not_run_fails_the_audit(self):
        self.stage_item10()
        ci = self.root / inv.CI_WORKFLOW
        ci.write_text(ci.read_text().replace("python3 signoff/check.py --require-tools", "true"))
        with self.assertRaises(inv.AuditError):
            inv.build_inventory(self.root, 10, "analog")


class CommittedCitations(unittest.TestCase):
    def test_every_citation_matches_the_live_tree(self):
        manifest = json.loads((ROOT / "signoff" / "block-manifest.json").read_text())
        for item, partition in inv.all_units():
            with self.subTest(item=item, partition=partition):
                self.assertEqual(inv.verify_item(ROOT, item, partition, manifest), [])

    def test_manifest_pin_drift_is_reported(self):
        manifest = json.loads((ROOT / "signoff" / "block-manifest.json").read_text())
        manifest["evidence"]["10.analog"]["content_hash"] = "sha256:" + "0" * 64
        problems = inv.verify_item(ROOT, 10, "analog", manifest)
        self.assertTrue(any("pins sha256:" + "0" * 64 in p for p in problems), problems)

    def test_item2_stream_is_the_one_item3_pins(self):
        manifest = json.loads((ROOT / "signoff" / "block-manifest.json").read_text())
        manifest["evidence"]["3.digital"]["content_hash"] = "sha256:" + "1" * 64
        problems = inv.verify_item(ROOT, 2, "digital", manifest)
        self.assertTrue(any("manifest 3.digital" in p for p in problems), problems)

    def test_envelope_declares_its_item(self):
        for item, partition in inv.all_units():
            env = json.loads((ROOT / inv.envelope_path(item, partition)).read_text())
            self.assertEqual((env["kind"], env["t1_item"]), ("generic", item))
            self.assertEqual(env["provenance"]["input"]["path"]["path"], inv.inventory_path(item, partition))


if __name__ == "__main__":
    unittest.main()
