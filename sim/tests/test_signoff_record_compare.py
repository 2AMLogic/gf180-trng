"""Signoff verdict-of-record comparison: compare_record, _print_item_diff,
resolve_artifact.

compare_record is what stops a silently drifting T1 verdict from passing, so
its fail-closed contract is pinned: a missing record fails, a differing record
fails with a diagnosable message, an equal record passes. RECORD and
REPO_ROOT are pointed at a temp dir so the committed record is never touched.
"""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("signoff_check", ROOT / "signoff" / "check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


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
        self.assertIn(f"klt {check.KLT_PIN}", err)

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
