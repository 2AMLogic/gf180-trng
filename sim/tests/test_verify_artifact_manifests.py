"""sim/tools/verify_artifact_manifests.py: schema, no storage names, no committed bytes (#686).

Each case builds a throwaway git repository; nothing reads the repository's
own manifests/. Stdlib only; needs only `git`.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(SIM_DIR / "tools"))

import verify_artifact_manifests as vam  # noqa: E402

RAW = b"raw evidence bytes\n"
SHA = hashlib.sha256(RAW).hexdigest()


def manifest(**override) -> str:
    entry = {
        "sha256": SHA, "size": len(RAW), "kind": "evidence", "name": "out.log",
        "uri": f"artifact:evidence/example__repo/{SHA[:2]}/{SHA}",
    }
    entry.update(override)
    return json.dumps({"schema_version": 1, "entries": [entry]})


@unittest.skipIf(shutil.which("git") is None, "git is not installed")
class ManifestCheckTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name).resolve()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        self.path = self.repo / "manifests" / "artifacts" / "2026-01-01-demo-01.manifest.json"
        self.path.parent.mkdir(parents=True)

    def put(self, rel: str, data: str | bytes) -> None:
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data if isinstance(data, bytes) else data.encode())

    def check(self) -> list[str]:
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        return vam.check(self.repo, vam.tracked_files(self.repo))

    def test_sound_manifest_passes(self):
        self.path.write_text(manifest())
        self.assertEqual(self.check(), [])

    def test_no_manifests_passes(self):
        self.assertEqual(self.check(), [])

    def test_non_artifact_uri_fails(self):
        self.path.write_text(manifest(uri="https://example.invalid/x/" + SHA))
        self.assertTrue(any("uri must start with 'artifact:'" in p for p in self.check()))

    def test_storage_names_fail(self):
        for marker in ("s3://", "arn:aws:"):
            with self.subTest(marker=marker):
                self.path.write_text(manifest(note=f"{marker}some-place"))
                self.assertTrue(any(marker in p for p in self.check()))

    def test_storage_name_in_a_non_manifest_file_under_manifests_fails(self):
        self.path.write_text(manifest())
        self.put("manifests/artifacts/README.md", "see s3://somewhere\n")
        self.assertTrue(any("README.md" in p and "s3://" in p for p in self.check()))

    def test_schema_violations_fail(self):
        for label, bad in (
            ("short sha", manifest(sha256="abc")),
            ("negative size", manifest(size=-1)),
            ("absolute name", manifest(name="/etc/passwd")),
            ("dotdot name", manifest(name="../x")),
            ("wrong kind", manifest(kind="other")),
            ("not json", "{"),
            ("no entries", json.dumps({"schema_version": 1, "entries": []})),
        ):
            with self.subTest(label):
                self.path.write_text(bad)
                self.assertTrue(self.check(), label)

    def test_committed_bytes_of_a_stored_object_fail(self):
        self.path.write_text(manifest())
        self.put("sim/records/raw/x/out.log", RAW)
        problems = self.check()
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("sim/records/raw/x/out.log", problems[0])

    def test_input_snapshot_names_may_equal_tracked_bytes(self):
        for name in sorted(vam.INPUT_SNAPSHOT_NAMES):
            with self.subTest(name=name):
                self.path.write_text(manifest(name=name))
                self.put("sim/harness/input.copy", RAW)
                self.assertEqual(self.check(), [])

    def test_snapshot_name_set_is_the_harness_constants(self):
        self.assertEqual(
            vam.INPUT_SNAPSHOT_NAMES,
            {"spinit", "tb.fragment.spice", "dut.netlist.spice", "tb.manifest.json", "pdk-models.json"},
        )

    def test_exempt_entry_does_not_exempt_other_names_with_same_bytes(self):
        entries = [
            {"sha256": SHA, "size": len(RAW), "kind": "evidence", "name": n,
             "uri": f"artifact:evidence/example__repo/{SHA[:2]}/{SHA}"}
            for n in ("spinit", "out.log")
        ]
        self.path.write_text(json.dumps({"schema_version": 1, "entries": entries}))
        self.put("leak.log", RAW)
        problems = self.check()
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("out.log", problems[0])

    def record(self, stem: str, deps: str | None) -> None:
        lines = ["---", "manifest:", "inputs:"]
        if deps is not None:
            lines.append(f"  netlist_dependencies: {deps}")
        lines += ["stored_evidence:", f"  manifest: manifests/artifacts/{stem}.manifest.json", "---", ""]
        self.put(f"sim/records/{stem}.md", "\n".join(lines))

    def test_declared_dependency_may_equal_tracked_bytes(self):
        self.path.write_text(manifest(name="models.spice"))
        self.record("2026-01-01-demo-01", "other.spice, models.spice")
        self.put("layout/models.spice", RAW)
        self.assertEqual(self.check(), [])

    def test_declared_dependency_does_not_exempt_same_bytes_under_another_name(self):
        entries = [
            {"sha256": SHA, "size": len(RAW), "kind": "evidence", "name": n,
             "uri": f"artifact:evidence/example__repo/{SHA[:2]}/{SHA}"}
            for n in ("models.spice", "out.log")
        ]
        self.path.write_text(json.dumps({"schema_version": 1, "entries": entries}))
        self.record("2026-01-01-demo-01", "models.spice")
        self.put("leak.log", RAW)
        problems = self.check()
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("out.log", problems[0])

    def test_dependency_declared_by_another_record_does_not_exempt(self):
        self.path.write_text(manifest(name="models.spice"))
        self.record("2026-01-01-demo-01", None)
        self.record("2026-02-02-other-01", "models.spice")
        self.put("layout/models.spice", RAW)
        self.assertEqual(len(self.check()), 1)

    def test_record_without_inputs_or_with_missing_manifest_is_tolerated(self):
        self.path.write_text(manifest())
        self.put("sim/records/old.md", "---\nname: old\n---\n")
        self.record("2026-03-03-gone-01", "x.spice")
        self.assertEqual(self.check(), [])

    def test_same_size_different_bytes_passes(self):
        self.path.write_text(manifest())
        self.put("other.txt", b"x" * len(RAW))
        self.assertEqual(self.check(), [])

    def test_empty_files_are_not_leaks(self):
        empty = hashlib.sha256(b"").hexdigest()
        self.path.write_text(manifest(sha256=empty, size=0, uri=f"artifact:evidence/r/{empty}"))
        self.put("pkg/__init__.py", b"")
        self.assertEqual(self.check(), [])

    def test_tracked_file_under_staging_area_fails(self):
        self.path.write_text(manifest())
        self.put("sim/.work/.stage/s/deck.cir", "* deck\n")
        self.assertTrue(any("staging area" in p for p in self.check()))

    def test_cli_exit_codes(self):
        self.path.write_text(manifest())
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(vam.main(["check", "--repo", str(self.repo)]), 0)
        self.put("leak.log", RAW)
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(vam.main(["check", "--repo", str(self.repo)]), 1)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(vam.main(["check", "--repo", str(self.repo / "nope")]), 2)


if __name__ == "__main__":
    unittest.main()
