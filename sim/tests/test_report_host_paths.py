#!/usr/bin/env python3
"""Tests for sim/tools/verify_report_host_paths.py, in temporary git repos."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
import verify_report_host_paths as guard  # noqa: E402

HIST = "signoff/evidence/post-route/gate_klt_response.json"


class GuardTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        self._git("init", "-q")

    def _git(self, *args):
        subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def _write(self, rel, content, track=True):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content if isinstance(content, str) else json.dumps(content))
        if track:
            self._git("add", "-f", rel)
        return p

    def test_safe_relative_paths_pass(self):
        self._write("layout/a.json", {"p": "layout/digital/x.def", "n": None})
        self.assertEqual(guard.check(self.repo), [])

    def test_both_forms_nested_with_field_path(self):
        self._write("design/a.json", {"x": [{"y": "/home/alice/w/f"}], "z": {"k": ["/Users/bob/q"]}})
        out = guard.check(self.repo)
        self.assertEqual(len(out), 2)
        self.assertTrue(any(l.startswith("design/a.json: $.x[0].y") for l in out))
        self.assertTrue(any("$.z.k[0]" in l for l in out))

    def test_malformed_json_fails(self):
        self._write("signoff/bad.json", "{not json")
        out = guard.check(self.repo)
        self.assertEqual(len(out), 1)
        self.assertIn("malformed", out[0])

    def test_working_tree_edit_is_checked(self):
        p = self._write("layout/a.json", {"p": "ok"})
        p.write_text(json.dumps({"p": "/home/alice/x/"}))
        self.assertEqual(len(guard.check(self.repo)), 1)

    def test_untracked_and_out_of_scope_ignored(self):
        bad = {"p": "/home/alice/x/"}
        self._write("layout/untracked.json", bad, track=False)
        self._write("sim/other.json", bad)
        self._write("layout/notes.txt", json.dumps(bad))
        self.assertEqual(guard.check(self.repo), [])

    def test_historical_exemption_requires_exact_path_and_hash(self):
        body = json.dumps({"p": "/home/alice/x/"})
        digest = hashlib.sha256(body.encode()).hexdigest()
        orig = dict(guard.HISTORICAL_EXEMPTIONS)
        self.addCleanup(lambda: (guard.HISTORICAL_EXEMPTIONS.clear(), guard.HISTORICAL_EXEMPTIONS.update(orig)))
        guard.HISTORICAL_EXEMPTIONS[HIST] = digest
        # same bytes, exact path: passes
        self._write(HIST, body)
        self.assertEqual(guard.check(self.repo), [])
        # identical bytes at another selected path: fails
        self._write("signoff/evidence/other.json", body)
        out = guard.check(self.repo)
        self.assertEqual(len(out), 1)
        self.assertTrue(out[0].startswith("signoff/evidence/other.json"))
        # changed bytes at the exempt path: fails
        (self.repo / HIST).write_text(body + " ")
        self.assertEqual(len(guard.check(self.repo)), 2)

    def test_production_exemption_is_fixed(self):
        self.assertEqual(
            guard.HISTORICAL_EXEMPTIONS,
            {HIST: "af63e5193ea6af94003478089aceb4eaeff81faf635ffe538944a12d1c3f17c7"},
        )

    def test_committed_tree_is_clean(self):
        self.assertEqual(guard.check(Path(__file__).resolve().parents[2]), [])


if __name__ == "__main__":
    unittest.main()
