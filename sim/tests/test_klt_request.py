#!/usr/bin/env python3
"""Unit tests for ``sim/harness/klt_request.py`` -- the shared emit/run
scaffold the evidence tools were each hand-copying (issue #590).

No ngspice, no PDK, no ``klt``, no network: ``subprocess.call`` is always
patched, so a test that reaches it fails rather than submitting anything.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import klt_request as kreq  # noqa: E402


def no_klt(*_a, **_k):
    raise AssertionError("subprocess must not be reached on a refused run")


class EmitTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_drift_is_detected_and_fails_the_check(self):
        req = self.root / "tb" / "request-grid.json"
        req.parent.mkdir(parents=True)
        req.write_text('{"drifted": true}\n')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = kreq.emit_requests([(req, '{"declared": true}\n')], True, repo_root=self.root)
        self.assertEqual(rc, 1)
        self.assertIn("DRIFT: tb/request-grid.json does not match the declared grid", buf.getvalue())

    def test_a_missing_file_is_drift(self):
        req = self.root / "tb" / "request-grid.json"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = kreq.emit_requests([(req, '{"declared": true}\n')], True, repo_root=self.root)
        self.assertEqual(rc, 1)
        self.assertIn("DRIFT:", buf.getvalue())

    def test_a_clean_check_calls_the_tools_own_ok_line(self):
        req = self.root / "tb" / "request-grid.json"
        req.parent.mkdir(parents=True)
        req.write_text('{"declared": true}\n')
        said = []
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = kreq.emit_requests([(req, '{"declared": true}\n')], True, repo_root=self.root,
                                    ok=lambda: said.append(1))
        self.assertEqual(rc, 0)
        self.assertEqual(said, [1])
        self.assertNotIn("DRIFT:", buf.getvalue())

    def test_write_mode_rewrites_the_file_and_creates_its_parent(self):
        req = self.root / "tb" / "request-grid.json"
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = kreq.emit_requests([(req, '{"declared": true}\n')], False, repo_root=self.root)
        self.assertEqual(rc, 0)
        self.assertEqual(req.read_text(), '{"declared": true}\n')
        self.assertIn("wrote tb/request-grid.json", buf.getvalue())

    def test_write_mode_never_calls_the_ok_line(self):
        req = self.root / "tb" / "request-grid.json"
        said = []
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = kreq.emit_requests([(req, '{"declared": true}\n')], False, repo_root=self.root,
                                    ok=lambda: said.append(1))
        self.assertEqual(rc, 0)
        self.assertEqual(said, [])

    def test_every_request_is_reported_not_just_the_first_drift(self):
        a = self.root / "tb" / "request-a.json"
        b = self.root / "tb" / "request-b.json"
        for p in (a, b):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("stale\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = kreq.emit_requests([(a, "new-a\n"), (b, "new-b\n")], True, repo_root=self.root)
        self.assertEqual(rc, 1)
        self.assertEqual(buf.getvalue().count("DRIFT:"), 2)


class RunTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.req = self.root / "tb" / "request-grid.json"
        self.req.parent.mkdir(parents=True)
        self.req.write_text("{}\n")
        self.outdir = self.root / "out"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_a_whole_grid_never_runs_locally(self):
        err = io.StringIO()
        with mock.patch("subprocess.call", no_klt), contextlib.redirect_stderr(err):
            rc = kreq.run_klt_request(self.outdir, "grid", self.req, "local")
        self.assertEqual(rc, 2)
        self.assertFalse(self.outdir.exists(), "a refused run must not create the outdir")
        self.assertEqual(err.getvalue().strip(),
                         "refusing to run the whole grid locally: use --backend batch (shared-host rule)")

    def test_the_refusal_names_the_tools_single_point_selector(self):
        err = io.StringIO()
        with mock.patch("subprocess.call", no_klt), contextlib.redirect_stderr(err):
            rc = kreq.run_klt_request(self.outdir, "grid", self.req, "local",
                                      probe_hint="--only PROCESS/TEMP/VDD")
        self.assertEqual(rc, 2)
        self.assertEqual(err.getvalue().strip(),
                         "refusing to run the whole grid locally: use --backend batch (shared-host rule), "
                         "or --only PROCESS/TEMP/VDD for one probe point")

    def test_a_single_point_probe_is_the_local_exception(self):
        seen = {}

        def fake_call(cmd, stdout=None, stderr=None):
            seen["cmd"] = cmd
            return 0

        with mock.patch("subprocess.call", fake_call):
            rc = kreq.run_klt_request(self.outdir, "probe", self.req, "local", single_point=True)
        self.assertEqual(rc, 0)
        self.assertEqual(seen["cmd"][3:5], ["--backend", "local"])

    def test_batch_builds_the_identical_command_line(self):
        seen = {}

        def fake_call(cmd, stdout=None, stderr=None):
            seen["cmd"] = cmd
            seen["stdout"], seen["stderr"] = stdout.name, stderr.name
            return 5

        klt = "uvx --from klayout-tools==0.6.0 klt"
        with mock.patch("subprocess.call", fake_call):
            rc = kreq.run_klt_request(self.outdir, "grid", self.req, "batch", klt)
        self.assertEqual(rc, 5)
        self.assertEqual(seen["cmd"], [
            "uvx", "--from", "klayout-tools==0.6.0", "klt", "sim", str(self.req),
            "--backend", "batch", "-o", str(self.outdir / "grid"), "--format", "json"])
        self.assertEqual(seen["stdout"], str(self.outdir / "grid.report.json"))
        self.assertEqual(seen["stderr"], str(self.outdir / "grid.stderr.txt"))

    def test_cleanup_runs_after_the_subprocess_and_even_when_it_raises(self):
        events = []

        def fake_call(cmd, stdout=None, stderr=None):
            events.append("call")
            raise RuntimeError("klt exploded")

        with mock.patch("subprocess.call", fake_call):
            with self.assertRaises(RuntimeError):
                kreq.run_klt_request(self.outdir, "grid", self.req, "batch", cleanup=lambda: events.append("cleanup"))
        self.assertEqual(events, ["call", "cleanup"])


if __name__ == "__main__":
    unittest.main()
