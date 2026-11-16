"""Signoff verdict-of-record comparison: compare_record, _print_item_diff,
resolve_artifact, and the canonical-bytes gate on the two files check.py
writes (canonical_bytes_problems).

compare_record is what stops a silently drifting T1 verdict from passing, so
its fail-closed contract is pinned: a missing record fails, a differing record
fails with a diagnosable message, an equal record passes. canonical_bytes_problems
is what stops a hand-mangled file from passing as grader output. RECORD and
REPO_ROOT are pointed at a temp dir so the committed record is never touched.
"""

import contextlib
import io
import json
import tempfile
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
from sim.tools.pathload import load_module_from_path  # noqa: E402  (#553)
check = load_module_from_path("signoff_check", ROOT / "signoff" / "check.py")


def item(id_, status="met", reason="ok", tier="T1", partition="all"):
    return {"tier": tier, "id": id_, "partition": partition, "status": status, "reason": reason}


def make_report(items=None, version="0.6.0"):
    items = items if items is not None else [item(1)]
    return {
        "build": {"version": version},
        "tier": "T1",
        "t1_met_count": sum(1 for i in items if i["status"] == "met"),
        "t1_item_count": len(items),
        "items": items,
    }


def make_manifest():
    return {
        "block": {"name": "combiner_sampler"},
        "kind": "klayout-design-evidence",
        "partition_boundary": "combiner_sampler",
        "evidence": {
            "t1-1/all": {"file": "signoff/evidence/x.json", "content_hash": "abc123"},
        },
    }


class TempRepo(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        self.record = self.root / "signoff" / "records" / "t1-tier-report.json"
        for name, value in (("REPO_ROOT", self.root), ("RECORD", self.record)):
            patch = mock.patch.object(check, name, value)
            patch.start()
            self.addCleanup(patch.stop)

    def write_record(self, report):
        self.record.parent.mkdir(parents=True, exist_ok=True)
        self.record.write_text(json.dumps(report))

    def call(self, fn, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rv = fn(*args)
        return rv, out.getvalue(), err.getvalue()


class CompareRecord(TempRepo):
    def test_missing_record_fails_and_names_regenerate_command(self):
        rc, _, err = self.call(check.compare_record, make_report())
        self.assertEqual(rc, 1)
        self.assertIn("missing", err)
        self.assertIn("python3 signoff/check.py --write", err)

    def test_equal_report_passes_and_prints_counts(self):
        report = make_report([item(1), item(2, status="unmet", reason="x")])
        self.write_record(report)
        rc, out, err = self.call(check.compare_record, report)
        self.assertEqual(rc, 0)
        self.assertIn("T1 1/2", out)
        self.assertEqual(err, "")

    def test_differing_report_fails_with_versions_and_pin(self):
        self.write_record(make_report(version="0.5.0"))
        rc, _, err = self.call(check.compare_record, make_report(version="0.6.1"))
        self.assertEqual(rc, 1)
        self.assertIn("stale", err)
        self.assertIn("klt 0.5.0", err)
        self.assertIn("klt 0.6.1", err)
        self.assertIn(f"klt {check.KLT_GRADER_PIN}", err)

    def test_differing_report_prints_item_diff(self):
        self.write_record(make_report([item(1)]))
        rc, _, err = self.call(check.compare_record, make_report([item(1, status="unmet")]))
        self.assertEqual(rc, 1)
        self.assertIn("T1 item 1", err)

    def test_record_is_not_modified(self):
        self.write_record(make_report(version="0.5.0"))
        before = self.record.read_text()
        self.call(check.compare_record, make_report(version="0.6.1"))
        self.assertEqual(self.record.read_text(), before)


class CanonicalBytes(TempRepo):
    """The canonical-form gate (issue #951): the two files check.py writes --
    the manifest and the record -- must stay byte-equal to
    ``json.dumps(json.loads(raw), indent=2) + "\\n"``. A hand edit that only
    moves whitespace stays valid JSON, so the byte comparison is the only
    thing that can catch it; the failure must name the file and the fix."""

    def setUp(self):
        super().setUp()
        self.manifest = self.root / "signoff" / "block-manifest.json"
        patch = mock.patch.object(check, "MANIFEST", self.manifest)
        patch.start()
        self.addCleanup(patch.stop)
        self.record.parent.mkdir(parents=True, exist_ok=True)
        self.record.write_text(json.dumps(make_report([item(1)]), indent=2) + "\n")
        self.manifest.write_text(json.dumps(make_manifest(), indent=2) + "\n")

    def assert_mangle_fails(self, path, mangled, name):
        path.write_text(mangled)
        problems = check.canonical_bytes_problems()
        self.assertEqual(len(problems), 1, problems)
        self.assertIn(name, problems[0])
        self.assertIn("python3 signoff/check.py --write", problems[0])

    def test_canonical_copies_pass(self):
        self.assertEqual(check.canonical_bytes_problems(), [])

    def test_record_newline_eaten_before_final_brace_fails(self):
        self.assert_mangle_fails(
            self.record,
            self.record.read_text().replace("\n}", "}", 1),
            "signoff/records/t1-tier-report.json",
        )

    def test_record_newline_eaten_before_sibling_key_fails(self):
        self.assert_mangle_fails(
            self.record,
            self.record.read_text().replace('\n  "items"', '  "items"', 1),
            "signoff/records/t1-tier-report.json",
        )

    def test_manifest_newline_eaten_before_final_brace_fails(self):
        self.assert_mangle_fails(
            self.manifest,
            self.manifest.read_text().replace("\n}", "}", 1),
            "signoff/block-manifest.json",
        )

    def test_manifest_newline_eaten_before_sibling_key_fails(self):
        self.assert_mangle_fails(
            self.manifest,
            self.manifest.read_text().replace('\n  "evidence"', '  "evidence"', 1),
            "signoff/block-manifest.json",
        )

    def test_unparsable_file_fails_and_names_fix(self):
        self.record.write_text("{oops")
        problems = check.canonical_bytes_problems()
        self.assertEqual(len(problems), 1)
        self.assertIn("not readable JSON", problems[0])
        self.assertIn("python3 signoff/check.py --write", problems[0])

    def test_main_gate_fails_even_when_the_grader_self_skips(self):
        # Wire-up proof: with klt absent, main() would print SKIPPED and exit 0
        # -- the canonical gate must fire before that and fail instead. The
        # gate's expensive neighbours are patched so this stays offline.
        self.record.write_text(self.record.read_text().replace("\n}", "}", 1))
        with mock.patch.object(check, "freshness_gate", return_value=0), \
                mock.patch.object(check, "verify_current_status", return_value=[]), \
                mock.patch.object(
                    check, "run_grader",
                    side_effect=check.GraderUnavailable("no klt")), \
                mock.patch.object(check.sys, "argv", ["check.py"]):
            rc, out, err = self.call(check.main)
        self.assertEqual(rc, 1)
        self.assertIn("signoff/records/t1-tier-report.json", err)
        self.assertIn("python3 signoff/check.py --write", err)
        self.assertNotIn("SKIPPED", out)


class PrintItemDiff(TempRepo):
    def diff(self, committed, fresh):
        _, out, err = self.call(check._print_item_diff, committed, fresh)
        return out + err

    def test_changes_appear_and_unchanged_does_not(self):
        committed = make_report(
            [
                item(1),  # unchanged
                item(2, status="met"),  # status changes
                item(3, reason="old reason"),  # reason changes
                item(4),  # only in committed
            ]
        )
        fresh = make_report(
            [
                item(1),
                item(2, status="unmet"),
                item(3, reason="new reason"),
                item(5),  # only in fresh
            ]
        )
        text = self.diff(committed, fresh)
        self.assertNotIn("item 1 ", text)
        self.assertIn("item 2 ", text)
        self.assertIn("'met', 'ok') -> ('unmet', 'ok')", text)
        self.assertIn("item 3 ", text)
        self.assertIn("old reason", text)
        self.assertIn("new reason", text)
        self.assertIn("item 4 ", text)
        self.assertIn("None", text.split("item 4 ")[1].splitlines()[0])
        self.assertIn("item 5 ", text)
        self.assertIn("None ->", text.split("item 5 ")[1].splitlines()[0])

    def test_identical_reports_print_nothing(self):
        report = make_report([item(1), item(2)])
        self.assertEqual(self.diff(report, report), "")


class ResolveArtifact(TempRepo):
    def setUp(self):
        super().setUp()
        self.env_path = self.root / "ev" / "report.json"
        self.env_path.parent.mkdir()

    def test_found_under_repo_root(self):
        target = self.root / "art" / "a.gds"
        target.parent.mkdir()
        target.write_bytes(b"x")
        self.assertEqual(check.resolve_artifact(self.env_path, "art/a.gds"), target)

    def test_found_only_beside_envelope(self):
        target = self.env_path.parent / "a.gds"
        target.write_bytes(b"x")
        self.assertEqual(check.resolve_artifact(self.env_path, "a.gds"), target)

    def test_repo_root_wins_when_both_exist(self):
        (self.root / "a.gds").write_bytes(b"root")
        (self.env_path.parent / "a.gds").write_bytes(b"beside")
        self.assertEqual(check.resolve_artifact(self.env_path, "a.gds"), self.root / "a.gds")

    def test_neither_returns_none(self):
        self.assertIsNone(check.resolve_artifact(self.env_path, "missing.gds"))


if __name__ == "__main__":
    unittest.main()
