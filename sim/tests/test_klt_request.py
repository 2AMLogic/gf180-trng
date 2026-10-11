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
import threading
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


class ReservationTests(unittest.TestCase):
    """The output namespace is reserved before klt runs (issue #610)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.req = self.root / "request-grid.json"
        self.req.write_text("{}\n")
        self.outdir = self.root / "out"
        self.outdir.mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _run(self, call=no_klt, **kw):
        err = io.StringIO()
        with mock.patch("subprocess.call", call), contextlib.redirect_stderr(err), \
                contextlib.redirect_stdout(io.StringIO()):
            rc = kreq.run_klt_request(self.outdir, "grid", self.req, "batch", **kw)
        return rc, err.getvalue()

    def test_occupied_destination_is_refused_and_prior_files_are_untouched(self):
        report = self.outdir / "grid.report.json"
        stderr = self.outdir / "grid.stderr.txt"
        report.write_bytes(b'{"prior": 1}\n')
        stderr.write_bytes(b"prior diagnostics\n")
        unrelated = self.outdir / "other.report.json"
        unrelated.write_bytes(b"other\n")
        events = []
        rc, msg = self._run(cleanup=lambda: events.append("cleanup"))
        self.assertNotEqual(rc, 0)
        self.assertIn("fresh output directory", msg)
        self.assertEqual(report.read_bytes(), b'{"prior": 1}\n')
        self.assertEqual(stderr.read_bytes(), b"prior diagnostics\n")
        self.assertEqual(unrelated.read_bytes(), b"other\n")
        self.assertEqual(events, ["cleanup"])

    def test_a_lone_prior_stderr_file_is_also_occupied(self):
        stderr = self.outdir / "grid.stderr.txt"
        stderr.write_bytes(b"prior\n")
        rc, _ = self._run()
        self.assertNotEqual(rc, 0)
        self.assertEqual(stderr.read_bytes(), b"prior\n")
        self.assertFalse((self.outdir / "grid.report.json").exists(),
                         "a refused run must not leave a half reservation behind")

    def test_backend_output_without_a_response_is_occupied(self):
        product = self.outdir / "grid.corners.csv"
        product.write_bytes(b"backend\n")
        rc, msg = self._run()
        self.assertNotEqual(rc, 0)
        self.assertIn("grid.corners.csv", msg)
        self.assertEqual(product.read_bytes(), b"backend\n")
        self.assertEqual(sorted(p.name for p in self.outdir.iterdir()), ["grid.corners.csv"])

    def test_backend_output_directory_is_occupied(self):
        (self.outdir / "grid").mkdir()
        rc, _ = self._run()
        self.assertNotEqual(rc, 0)
        self.assertEqual(sorted(p.name for p in self.outdir.iterdir()), ["grid"])

    def test_a_sibling_request_name_does_not_collide(self):
        (self.outdir / "grid2.report.json").write_bytes(b"x")
        (self.outdir / "other.report.json").write_bytes(b"y")
        rc, _ = self._run(call=lambda cmd, stdout=None, stderr=None: 0)
        self.assertEqual(rc, 0)

    def test_fresh_submission_keeps_the_current_filenames(self):
        def fake_call(cmd, stdout=None, stderr=None):
            stdout.write('{"ok": true}\n')
            stderr.write("note\n")
            return 0

        rc, _ = self._run(call=fake_call)
        self.assertEqual(rc, 0)
        self.assertEqual((self.outdir / "grid.report.json").read_text(), '{"ok": true}\n')
        self.assertEqual((self.outdir / "grid.stderr.txt").read_text(), "note\n")

    def test_failure_before_subprocess_startup_keeps_diagnostics_and_a_later_run_is_refused(self):
        calls = []

        def missing(cmd, stdout=None, stderr=None):
            calls.append(cmd)
            raise FileNotFoundError(2, "No such file or directory: 'klt'")

        events = []
        rc, _ = self._run(call=missing, cleanup=lambda: events.append("cleanup"))
        self.assertEqual(rc, 127)
        self.assertEqual(events, ["cleanup"])
        self.assertIn("klt", (self.outdir / "grid.stderr.txt").read_text())
        before = (self.outdir / "grid.stderr.txt").read_bytes()
        rc2, _ = self._run()
        self.assertNotEqual(rc2, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual((self.outdir / "grid.stderr.txt").read_bytes(), before)

    def test_backend_failure_keeps_its_own_diagnostics_and_blocks_replacement(self):
        def failing(cmd, stdout=None, stderr=None):
            stderr.write("backend said no\n")
            return 4

        rc, _ = self._run(call=failing)
        self.assertEqual(rc, 4)
        rc2, _ = self._run()
        self.assertNotEqual(rc2, 0)
        self.assertEqual((self.outdir / "grid.stderr.txt").read_text(), "backend said no\n")

    def test_concurrent_attempts_allow_at_most_one_submission(self):
        n = 8
        barrier = threading.Barrier(n)
        gate = threading.Event()
        calls, rcs = [], []
        lock = threading.Lock()

        def slow_call(cmd, stdout=None, stderr=None):
            with lock:
                calls.append(cmd)
            gate.wait(5)
            return 0

        def worker():
            barrier.wait()
            with contextlib.redirect_stderr(io.StringIO()):
                rc = kreq.run_klt_request(self.outdir, "grid", self.req, "batch")
            with lock:
                rcs.append(rc)
                if len(rcs) == n - 1:
                    gate.set()

        with mock.patch("subprocess.call", slow_call), contextlib.redirect_stdout(io.StringIO()):
            threads = [threading.Thread(target=worker) for _ in range(n)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(10)
        self.assertEqual(len(calls), 1)
        self.assertEqual(sorted(rcs).count(0), 1)
        self.assertEqual(len([r for r in rcs if r != 0]), n - 1)

    def test_cleanup_runs_on_the_local_grid_refusal_too(self):
        events = []
        with mock.patch("subprocess.call", no_klt), contextlib.redirect_stderr(io.StringIO()):
            rc = kreq.run_klt_request(self.outdir, "grid", self.req, "local",
                                      cleanup=lambda: events.append("cleanup"))
        self.assertEqual(rc, 2)
        self.assertEqual(events, ["cleanup"])


if __name__ == "__main__":
    unittest.main()
