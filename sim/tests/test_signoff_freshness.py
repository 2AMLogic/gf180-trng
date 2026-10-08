"""Signoff freshness gate: an envelope must still describe its input on disk.

check_envelope_against_its_input() is what stops stale evidence from being
cited, so both halves are pinned: a matching digest passes, and every way an
envelope can fail to prove freshness is rejected with a message. Synthetic
envelopes live under a temp dir that stands in for the repo root.
"""

import contextlib
import hashlib
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

PAYLOAD = b"synthetic layout bytes\n"
DIGEST = "sha256:" + hashlib.sha256(PAYLOAD).hexdigest()
WRONG = "sha256:" + "0" * 64


class EnvelopeFreshness(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        patch = mock.patch.object(check, "REPO_ROOT", self.root)
        patch.start()
        self.addCleanup(patch.stop)
        (self.root / "art").mkdir()
        (self.root / "art" / "in.gds").write_bytes(PAYLOAD)
        self.env_path = self.root / "ev" / "report.json"
        self.env_path.parent.mkdir()
        self.failures: list[str] = []

    def run_check(self, envelope):
        return check.check_envelope_against_its_input(self.env_path, envelope, self.failures)

    def prov(self, digest=DIGEST):
        return {"input": {"content_hash": digest}} if digest else {}

    def test_matching_digest_passes(self):
        env = {"file": "art/in.gds", "provenance": self.prov()}
        self.assertTrue(self.run_check(env))
        self.assertEqual(self.failures, [])

    def test_source_field_matching_digest_passes(self):
        env = {"source": "art/in.gds", "provenance": self.prov()}
        self.assertTrue(self.run_check(env))
        self.assertEqual(self.failures, [])

    def test_input_relative_to_envelope_dir_passes(self):
        (self.env_path.parent / "local.gds").write_bytes(PAYLOAD)
        env = {"layout": "local.gds", "environment": {"layout_sha256": DIGEST[7:]}}
        self.assertTrue(self.run_check(env))
        self.assertEqual(self.failures, [])

    def test_digest_mismatch_rejected(self):
        env = {"file": "art/in.gds", "provenance": self.prov(WRONG)}
        self.assertFalse(self.run_check(env))
        self.assertEqual(len(self.failures), 1)
        self.assertIn("hashes to", self.failures[0])

    def test_missing_input_rejected(self):
        env = {"file": "art/gone.gds", "provenance": self.prov()}
        self.assertFalse(self.run_check(env))
        self.assertEqual(len(self.failures), 1)
        self.assertIn("does not exist", self.failures[0])

    def test_input_named_without_digest_rejected(self):
        env = {"file": "art/in.gds", "provenance": {}}
        self.assertFalse(self.run_check(env))
        self.assertEqual(len(self.failures), 1)
        self.assertIn("records no", self.failures[0])

    def test_no_input_field_rejected(self):
        self.assertFalse(self.run_check({"provenance": self.prov()}))
        self.assertEqual(len(self.failures), 1)
        self.assertIn("names no input artifact", self.failures[0])

    def test_layout_environment_digest_form(self):
        good = {"layout": "art/in.gds", "environment": {"layout_sha256": DIGEST[7:]}}
        self.assertTrue(self.run_check(good))
        self.assertEqual(self.failures, [])
        bad = {"layout": "art/in.gds", "environment": {"layout_sha256": "0" * 64}}
        self.assertFalse(self.run_check(bad))
        self.assertIn("environment.layout_sha256", self.failures[0])
        self.failures.clear()
        self.assertFalse(self.run_check({"layout": "art/in.gds", "environment": {}}))
        self.assertIn("records no", self.failures[0])

    def test_layout_object_form_uses_provenance_digest(self):
        env = {"layout": {"path": "art/in.gds", "scope": "repo"}, "provenance": self.prov()}
        self.assertTrue(self.run_check(env))
        self.assertEqual(self.failures, [])
        env = {"layout": {"path": "art/in.gds", "scope": "repo"}, "provenance": self.prov(WRONG)}
        self.assertFalse(self.run_check(env))
        # a non-repo-scoped object names no checkable input
        self.failures.clear()
        env = {"layout": {"path": "art/in.gds", "scope": "other"}, "provenance": self.prov()}
        self.assertFalse(self.run_check(env))
        self.assertIn("names no input artifact", self.failures[0])


class Helpers(unittest.TestCase):
    def test_pinned_input_hash(self):
        self.assertEqual(check.pinned_input_hash({"provenance": {"input": {"content_hash": "x"}}}), "x")
        self.assertIsNone(check.pinned_input_hash({}))
        self.assertIsNone(check.pinned_input_hash({"provenance": None}))

    def test_manifest_entries_flattens_lists_and_skips_non_objects(self):
        manifest = {"evidence": {"b": {"file": "b"}, "a": [{"file": "a1"}, "text", {"file": "a2"}], "c": "x"}}
        got = [(k, p["file"]) for k, p in check.manifest_entries(manifest)]
        self.assertEqual(got, [("a", "a1"), ("a", "a2"), ("b", "b")])
        self.assertEqual(list(check.manifest_entries({})), [])


class CommittedManifest(unittest.TestCase):
    def test_freshness_gate_passes_on_committed_manifest(self):
        manifest = json.loads((ROOT / "signoff" / "block-manifest.json").read_text())
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(check.freshness_gate(manifest), 0)


if __name__ == "__main__":
    unittest.main()
