"""Item 1/2/9/10 inventories: the drift gate must name what moved (#653).

signoff/inventories.py rebuilds each inventory from the live tree, and
signoff/check.py fails when the committed one no longer matches. The cases
here copy only the files an inventory reads into a temporary root, so a file
can be changed, added or removed without touching the real tree. Stdlib only;
no klt, no PDK.
"""

import json
import re
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
        copy_files(
            self.root,
            [*WORKFLOWS, "README.md", "LICENSE", inv.SPEC, "sim/README.md", inv.CHECK_SCRIPT, "package.json"],
        )

    def stage_item9_digital(self):
        files = [
            *WORKFLOWS, "README.md", "sim/README.md", "sim/pdk.json", "package.json",
            inv.CHECK_SCRIPT,
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

    def test_gate_whose_command_is_a_prefix_of_a_longer_step_fails_the_audit(self):
        """The anchored needle: `npm run test` must be satisfied by its own
        step line alone, never by the longer `npm run test:layout` step a
        bare substring containment also hits (issue #1004)."""
        self.stage_item9_digital()
        script = self.root / inv.CHECK_SCRIPT
        script.write_text(
            script.read_text().replace('step "npm run test" npm run test\n', "", 1)
        )
        with self.assertRaises(inv.AuditError) as ctx:
            inv.build_inventory(self.root, 9, "digital")
        self.assertIn('step "npm run test" npm run test', str(ctx.exception))

    def test_hygiene_gate_whose_command_is_a_prefix_of_a_longer_step_fails_the_audit(self):
        """The hygiene row's `npm run test` claim (item 10, analog) is audited
        against the same whole step lines, so the longer `npm run test:layout`
        step cannot satisfy it either (issue #1004's second false pass)."""
        self.stage_item10()
        script = self.root / inv.CHECK_SCRIPT
        script.write_text(
            script.read_text().replace('step "npm run test" npm run test\n', "", 1)
        )
        with self.assertRaises(inv.AuditError) as ctx:
            inv.build_inventory(self.root, 10, "analog")
        self.assertIn("ci group does not run 'npm run test'", str(ctx.exception))

    def test_gate_the_workflow_does_not_run_fails_the_audit(self):
        self.stage_item10()
        ci = self.root / inv.CI_WORKFLOW
        ci.write_text(ci.read_text().replace("python3 signoff/check.py --require-tools", "true"))
        with self.assertRaises(inv.AuditError):
            inv.build_inventory(self.root, 10, "analog")

    def test_gate_the_check_list_does_not_run_fails_the_audit(self):
        """The single-source guard: a step removed from sim/check.sh's `ci`
        group fails the audit even though the script still contains the same
        command elsewhere (issue #1000 -- the `all` group is not what CI
        runs)."""
        self.stage_item10()
        script = self.root / inv.CHECK_SCRIPT
        script.write_text(
            script.read_text().replace(
                'step "npm run check:digital-input" npm run check:digital-input\n', "", 1
            )
        )
        with self.assertRaises(inv.AuditError):
            inv.build_inventory(self.root, 10, "digital")

    def delete_check_list_run_line(self) -> None:
        """Delete only the `sim/check.sh ci` run body from the staged ci.yml,
        leaving the `#` comment (issue #1000) and the step `name:` string --
        which both quote the call -- in place (issue #1007)."""
        ci = self.root / inv.CI_WORKFLOW
        text = ci.read_text()
        self.assertEqual(len(re.findall(r"(?m)^[ \t]*sim/check\.sh ci[ \t]*$", text)), 1)
        ci.write_text(re.sub(r"(?m)^[ \t]*sim/check\.sh ci[ \t]*\n", "", text, count=1))

    def test_item10_audit_fails_when_only_the_check_list_run_line_is_deleted(self):
        """Item 10's claim that CI runs the check list is satisfied by the run
        body line alone: deleting it fails the audit even though the comment
        and the step `name:` still quote the call (issue #1007)."""
        self.stage_item10()
        self.delete_check_list_run_line()
        with self.assertRaises(inv.AuditError) as ctx:
            inv.build_inventory(self.root, 10, "analog")
        self.assertIn("does not run 'sim/check.sh ci'", str(ctx.exception))

    def test_item9_audit_fails_when_only_the_check_list_run_line_is_deleted(self):
        """Item 9's gates pin the same ci.yml call through `unit-tests`'s
        `also` entry, so the run line vanishing fails there too (issue
        #1007)."""
        self.stage_item9_digital()
        self.delete_check_list_run_line()
        with self.assertRaises(inv.AuditError) as ctx:
            inv.build_inventory(self.root, 9, "digital")
        self.assertIn("does not contain 'sim/check.sh ci'", str(ctx.exception))

    def test_every_gate_pinning_the_check_list_call_fails_when_the_run_line_is_deleted(self):
        """All five `_GATES` `also` entries that pin ci.yml's call of the
        check list fail the same way when only the run body line is deleted
        (issue #1007)."""
        self.stage_item10()
        self.delete_check_list_run_line()
        sites = [
            (1, "analog", "netlist-lint"),
            (1, "digital", "regmap-check"),
            (2, "analog", "floorplan-netlist-check"),
            (2, "digital", "digital-input-check"),
            (9, "analog", "unit-tests"),
        ]
        for item, partition, gate in sites:
            with self.subTest(gate=gate):
                with self.assertRaises(inv.AuditError) as ctx:
                    inv._gate_records(self.root, item, partition)
                message = str(ctx.exception)
                self.assertIn("does not contain 'sim/check.sh ci'", message)
                self.assertIn(inv._GATES[gate][0], message)

    def test_comment_only_check_list_occurrence_fails_the_audit(self):
        """A `#` comment line quoting the call must not satisfy the audit;
        only the run body line counts (issue #1007)."""
        self.stage_item10()
        ci = self.root / inv.CI_WORKFLOW
        ci.write_text(
            re.sub(
                r"(?m)^[ \t]*sim/check\.sh ci[ \t]*$",
                " " * 10 + "# sim/check.sh ci",
                ci.read_text(),
                count=1,
            )
        )
        with self.assertRaises(inv.AuditError) as ctx:
            inv.build_inventory(self.root, 10, "analog")
        self.assertIn("does not run 'sim/check.sh ci'", str(ctx.exception))

    def test_comment_only_signoff_check_occurrence_fails_the_audit(self):
        """The second literal the old substring pair checked --
        `python3 signoff/check.py --require-tools` -- is pinned by the
        `signoff-check` gate's anchored `run:` needle, so a comment quoting
        that step cannot satisfy item 10 either (issue #1007)."""
        self.stage_item10()
        ci = self.root / inv.CI_WORKFLOW
        ci.write_text(
            ci.read_text().replace(
                "run: python3 signoff/check.py --require-tools",
                "# run: python3 signoff/check.py --require-tools",
            )
        )
        with self.assertRaises(inv.AuditError) as ctx:
            inv.build_inventory(self.root, 10, "analog")
        self.assertIn("run: python3 signoff/check.py --require-tools", str(ctx.exception))


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
