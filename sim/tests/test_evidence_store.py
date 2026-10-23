"""harness/evidence_store.py and the recorded-run path through it (#686).

The artifact store is replaced by the ``klt`` shim in ``_fake_store``: no
network, no broker. The real broker is exercised out of band (see the PR).
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))
sys.path.append(str(Path(__file__).resolve().parent))  # sim/tests: _fake_store

import _fake_store  # noqa: E402
from harness import cli, evidence_store as es, report  # noqa: E402
import test_cli  # noqa: E402


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        _fake_store.install(self, self.root, cli)
        self.stage = self.root / ".work" / ".stage" / "s-01"
        self.stage.mkdir(parents=True)
        self.dest = self.root / "manifests" / "artifacts" / "s-01.manifest.json"

    def stage_files(self, files: dict[str, bytes]) -> list[str]:
        for name, data in files.items():
            (self.stage / name).write_bytes(data)
        return list(files)

    def test_preflight_passes_with_broker_and_put_verb(self):
        es.preflight()

    def test_preflight_refuses_without_broker(self):
        with mock.patch.dict(os.environ):
            os.environ.pop("KLT_ARTIFACT_BROKER")
            with self.assertRaisesRegex(es.EvidenceStoreError, "KLT_ARTIFACT_BROKER is unset"):
                es.preflight()

    def test_preflight_refuses_without_klt(self):
        with mock.patch.object(es.shutil, "which", return_value=None):
            with self.assertRaisesRegex(es.EvidenceStoreError, "not on PATH"):
                es.preflight()

    def test_preflight_refuses_a_klt_without_artifact_put(self):
        with mock.patch.dict(os.environ, {"FAKE_KLT_MODE": "noput"}):
            with self.assertRaisesRegex(es.EvidenceStoreError, "no `artifact put` verb"):
                es.preflight()

    def test_store_publishes_manifest_and_returns_the_table(self):
        names = self.stage_files({"deck.cir": b"* deck\n", "out.log": b"result\n", "m.json": b"{}\n"})
        table = es.store_files(self.stage, names, self.dest, repo_root=self.root)
        self.assertEqual(
            table,
            sorted((n, (self.stage / n).stat().st_size,
                    hashlib.sha256((self.stage / n).read_bytes()).hexdigest()) for n in names),
        )
        data = json.loads(self.dest.read_text())
        self.assertEqual(es.validate_manifest(data), [])
        self.assertTrue(all(e["uri"].startswith("artifact:") for e in data["entries"]))
        self.assertTrue((self.stage / "deck.cir").is_file())  # staged bytes kept

    def test_empty_staged_file_is_refused_before_any_put(self):
        names = self.stage_files({"deck.cir": b"* deck\n", "out.log": b""})
        with mock.patch.object(es.subprocess, "run") as run:
            with self.assertRaisesRegex(es.EvidenceStoreError, "out.log is empty"):
                es.store_files(self.stage, names, self.dest, repo_root=self.root)
        run.assert_not_called()
        self.assertFalse(self.dest.exists())

    def test_put_failure_publishes_nothing_keeps_bytes_and_hides_the_broker(self):
        names = self.stage_files({"deck.cir": b"* deck\n"})
        with mock.patch.dict(os.environ, {"FAKE_KLT_MODE": "fail"}):
            with self.assertRaises(es.EvidenceStoreError) as ctx:
                es.store_files(self.stage, names, self.dest, repo_root=self.root)
        self.assertFalse(self.dest.exists())
        self.assertFalse(self.dest.parent.exists())
        self.assertTrue((self.stage / "deck.cir").is_file())
        self.assertNotIn("broker.invalid", str(ctx.exception))
        self.assertIn("<broker>", str(ctx.exception))

    def test_existing_manifest_is_never_replaced(self):
        names = self.stage_files({"deck.cir": b"* deck\n"})
        self.dest.parent.mkdir(parents=True)
        self.dest.write_text("old\n")
        with self.assertRaisesRegex(es.EvidenceStoreError, "already exists"):
            es.store_files(self.stage, names, self.dest, repo_root=self.root)
        self.assertEqual(self.dest.read_text(), "old\n")

    def test_missing_staged_file_is_refused(self):
        with self.assertRaisesRegex(es.EvidenceStoreError, "missing"):
            es.store_files(self.stage, ["nope.log"], self.dest, repo_root=self.root)

    def test_stage_inside_the_tree_must_be_ignored(self):
        es.ensure_stage_ignored(self.root / ".work" / ".stage", self.root)
        with self.assertRaisesRegex(es.EvidenceStoreError, "not git-ignored"):
            es.ensure_stage_ignored(self.root / "tracked" / ".stage", self.root)

    def test_stage_outside_the_tree_is_fine(self):
        with tempfile.TemporaryDirectory() as other:
            es.ensure_stage_ignored(Path(other) / ".stage", self.root)

    def test_validate_manifest_rejects_bad_shapes(self):
        sha = "a" * 64
        good = {"name": "a", "sha256": sha, "size": 1, "kind": "evidence",
                "uri": f"artifact:evidence/r/{sha}"}
        self.assertEqual(es.validate_manifest({"schema_version": 1, "entries": [good]}), [])
        for label, entry in (
            ("scheme", {**good, "uri": f"s3://bucket/{sha}"}),
            ("uri without digest", {**good, "uri": "artifact:evidence/r/other"}),
            ("bucket in entry", {**good, "extra": "arn:aws:s3:::b"}),
        ):
            with self.subTest(label):
                self.assertTrue(es.validate_manifest({"schema_version": 1, "entries": [entry]}))
        self.assertTrue(es.validate_manifest({"schema_version": 1, "entries": [good, good]}))


class RecordedRunTests(unittest.TestCase):
    """A ``run_corners.py`` run stores its raw output and commits only a manifest."""

    _install_runner = test_cli.RunIntegrityTests._install_runner
    _run = test_cli.RunIntegrityTests._run

    def setUp(self):
        # Shared fixture: fake PDK/testbench, patched cli globals and the store shim.
        test_cli.RunIntegrityTests.setUp(self)

    def _manifests(self) -> list[Path]:
        return sorted((self.root / "manifests" / "artifacts").glob("*.manifest.json"))

    def _nothing_published(self):
        self.assertEqual(self._manifests(), [])
        self.assertEqual(list(self.records_dir.glob("*.md")), [])
        raw = self.records_dir / report.RAW_DIRNAME
        self.assertFalse(raw.exists() and any(raw.iterdir()))

    def test_run_writes_manifests_with_artifact_uris_and_no_raw_directory(self):
        self._install_runner()
        status, out, err = self._run()
        self.assertEqual(status, cli.EXIT_OK, err)
        records = sorted(self.records_dir.glob("*.md"))
        manifests = self._manifests()
        self.assertEqual([m.name[:-len(".manifest.json")] for m in manifests], [r.stem for r in records])
        self.assertEqual(len(records), 2)
        for record, manifest in zip(records, manifests):
            data = json.loads(manifest.read_text())
            self.assertTrue(all(e["uri"].startswith("artifact:") for e in data["entries"]))
            text = record.read_text()
            self.assertIn("stored_evidence:", text)
            self.assertNotIn("\nraw:\n", text)
            self.assertEqual(report.verify_record_file(record, self.root), [])
        raw = self.records_dir / report.RAW_DIRNAME
        self.assertFalse(raw.exists() and any(raw.iterdir()))
        # The bytes stay in the git-ignored staging area.
        self.assertTrue(any((self.root / ".work" / ".stage").rglob("*.spice")))

    def test_unset_broker_exits_nonzero_before_simulating_and_writes_nothing(self):
        self._install_runner()
        with mock.patch.dict(os.environ):
            os.environ.pop("KLT_ARTIFACT_BROKER")
            with mock.patch.object(cli.runner, "run_one") as run_one:
                status, out, err = self._run()
        self.assertEqual(status, cli.EXIT_ENVIRONMENT)
        self.assertIn("KLT_ARTIFACT_BROKER is unset", err)
        run_one.assert_not_called()
        self._nothing_published()

    def test_klt_without_artifact_put_exits_nonzero_and_writes_nothing(self):
        self._install_runner()
        with mock.patch.dict(os.environ, {"FAKE_KLT_MODE": "noput"}):
            with mock.patch.object(cli.runner, "run_one") as run_one:
                status, _out, err = self._run()
        self.assertEqual(status, cli.EXIT_ENVIRONMENT)
        run_one.assert_not_called()
        self._nothing_published()

    def test_unreachable_broker_fails_the_run_after_the_grid_and_publishes_nothing(self):
        self._install_runner()
        with mock.patch.dict(os.environ, {"FAKE_KLT_MODE": "fail"}):
            status, out, err = self._run()
        self.assertEqual(status, cli.EXIT_STORE_FAILED)
        self.assertIn("status    : FAIL", out)
        self.assertIn("record withheld", err)
        self.assertNotIn("broker.invalid", out + err)
        self._nothing_published()
        self.assertTrue(any((self.root / ".work" / ".stage").rglob("*.spice")))  # bytes kept

    def test_no_write_run_needs_no_store(self):
        self._install_runner()
        with mock.patch.dict(os.environ):
            os.environ.pop("KLT_ARTIFACT_BROKER")
            status, out, _err = self._run("--no-write")
        self.assertEqual(status, cli.EXIT_OK)
        self._nothing_published()

    def test_rerun_mints_new_stems_and_keeps_old_manifests(self):
        self._install_runner()
        self.assertEqual(self._run()[0], cli.EXIT_OK)
        first = [m.name for m in self._manifests()]
        self.assertEqual(self._run()[0], cli.EXIT_OK)
        self.assertEqual(len(self._manifests()), 4)
        self.assertTrue(set(first) < {m.name for m in self._manifests()})


if __name__ == "__main__":
    unittest.main()
