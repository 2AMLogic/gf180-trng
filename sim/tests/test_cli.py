#!/usr/bin/env python3
"""Unit tests for sim/harness/cli.py: the "shadowed PDK variant" note added
in #39, and the raw-output integrity check a completed run must pass (#60).
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest import mock

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import cli, report, runner  # noqa: E402
from harness.pdk import Pdk  # noqa: E402


def _make_variant(root: Path, name: str = "gf180mcuD") -> Path:
    variant = root / name
    (variant / "libs.tech" / "ngspice").mkdir(parents=True)
    (variant / "libs.tech" / "ngspice" / "sm141064.ngspice").write_text("* fake\n")
    return variant


class CheckEnvTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # Every test here cares only about the PDK section of --check-env
        # output, so stub ngspice_version to a fixed, always-OK value.
        patcher = mock.patch.object(cli.runner, "ngspice_version", return_value="ngspice-42")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_single_variant_dir_prints_no_shadow_note(self):
        variant = _make_variant(self.root, "gf180mcuD")
        pdk = Pdk(path=variant, variant="gf180mcuD", source=f"search_root:{self.root}")
        with mock.patch.object(cli, "find_pdk", return_value=pdk):
            with mock.patch.object(cli, "find_all_variant_dirs", return_value=[(variant, pdk.source)]):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    status = cli.cmd_check_env()
        output = buf.getvalue()
        self.assertEqual(status, cli.EXIT_OK)
        self.assertIn("PDK     : OK", output)
        self.assertNotIn("note:", output)

    def test_shadowed_variant_dir_prints_note(self):
        ciel_root = self.root / "ciel_store"
        volare_root = self.root / "volare_store"
        winner = _make_variant(ciel_root, "gf180mcuD")
        loser = _make_variant(volare_root, "gf180mcuD")
        pdk = Pdk(path=winner, variant="gf180mcuD", source=f"search_root:{ciel_root}")
        with mock.patch.object(cli, "find_pdk", return_value=pdk):
            with mock.patch.object(
                cli,
                "find_all_variant_dirs",
                return_value=[
                    (winner, f"search_root:{ciel_root}"),
                    (loser, f"search_root:{volare_root}"),
                ],
            ):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    status = cli.cmd_check_env()
        output = buf.getvalue()
        self.assertEqual(status, cli.EXIT_OK)
        self.assertIn("PDK     : OK", output)
        self.assertIn(
            f"note: gf180mcuD also found under {volare_root} (search_root:{volare_root}) -- shadowed, not used",
            output,
        )
        # The winning path must never be reported as shadowing itself.
        self.assertNotIn(f"under {ciel_root}", output)

    def test_pdk_not_found_reports_missing_without_note(self):
        with mock.patch.object(cli, "find_pdk", side_effect=cli.PdkNotFound("not found")):
            buf = io.StringIO()
            with redirect_stdout(buf):
                status = cli.cmd_check_env()
        output = buf.getvalue()
        self.assertEqual(status, cli.EXIT_ENVIRONMENT)
        self.assertIn("PDK     : MISSING", output)
        self.assertNotIn("note:", output)


class RunIntegrityTests(unittest.TestCase):
    """A completed run re-hashes its raw output before it reports success.

    Regression coverage for #60: two concurrent ``run_corners.py``
    invocations were handed overlapping record stems, the second overwrote
    raw files the first had already hashed into its records, and the run
    printed ``status : OK`` and exited 0 with 30 records whose ``raw.files``
    checksums matched nothing on disk.

    No ngspice is needed: ``runner.run_one`` is replaced by a stub that
    writes a deck and a log the way a real run does, and the collision is
    injected by having a later run write into an earlier point's raw
    directory -- exactly what the losing invocation did.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.records_dir = self.root / "records"

        self.tb_dir = self.root / "tb" / "an-experiment"
        self.tb_dir.mkdir(parents=True)
        (self.tb_dir / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (self.tb_dir / "tb.json").write_text(
            json.dumps({
                "name": "an-experiment", "netlist": "x.spice",
                "measure": {"vout": "v(out)"},
            })
        )

        variant = _make_variant(self.root, "gf180mcuD")
        (variant / "libs.tech" / "ngspice" / "design.ngspice").write_text("* fake\n")
        (variant / "SOURCES").write_text("open_pdks deadbeef\n")
        pdk = Pdk(path=variant, variant="gf180mcuD", source="test")

        for target, value in (
            ("RECORDS_DIR", self.records_dir),
            ("REPO_ROOT", self.root),
        ):
            patcher = mock.patch.object(cli, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        for target, value in (
            ("find_pdk", lambda: pdk),
            ("git_provenance", lambda _root: {"commit": "f" * 40, "dirty": False}),
        ):
            patcher = mock.patch.object(
                cli if target == "find_pdk" else cli.report, target, value
            )
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch.object(cli.runner, "ngspice_version", return_value="ngspice-46")
        patcher.start()
        self.addCleanup(patcher.stop)

    def _install_runner(self, on_run=None):
        """Stub run_one: write the deck + log a real run would leave behind."""
        def fake_run_one(tb, pdk, point, workdir, seed=None, run_index=0, timeout_s=0):
            workdir.mkdir(parents=True, exist_ok=True)
            stem = point.corner_id
            deck = workdir / f"{stem}.spice"
            log = workdir / f"{stem}.log"
            deck.write_text(f"* deck for {stem}\n")
            log.write_text("m_vout = 1.65\n")
            if on_run is not None:
                on_run(point, workdir)
            return runner.RunResult(
                point=point, seed=seed, status="ok", measurements={"vout": 1.65},
                seconds=0.1, deck_name=deck.name, log_name=log.name,
            )

        patcher = mock.patch.object(cli.runner, "run_one", side_effect=fake_run_one)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _run(self, *extra: str):
        """Drive the whole CLI entry point, so exit codes are the real ones."""
        argv = [str(self.tb_dir), "--corners", "tt", "ss", "--temps", "27",
                "--supply-tol", "0", *extra]
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = cli.main(argv)
        return status, out.getvalue(), err.getvalue()

    def test_clean_run_reserves_disjoint_stems_and_reports_ok(self):
        self._install_runner()
        status, out, _err = self._run()
        self.assertEqual(status, cli.EXIT_OK)
        self.assertIn("status    : OK", out)
        stems = sorted(p.stem for p in self.records_dir.glob("*.md"))
        self.assertEqual(len(stems), 2)
        self.assertEqual(len(set(stems)), 2)
        for stem in stems:
            problems = report.verify_record_file(self.records_dir / f"{stem}.md", self.root)
            self.assertEqual(problems, [], problems)

    def test_a_second_writer_clobbering_raw_output_fails_the_run(self):
        """The record for point 1 is written, then its raw output is
        overwritten while point 2 is still running -- as a colliding second
        invocation would do. The run must not report OK."""
        first_raw: list[Path] = []

        def clobber(point, workdir):
            if not first_raw:
                first_raw.append(workdir)
                return
            if workdir != first_raw[0]:
                victim = next(iter(sorted(first_raw[0].glob("*.spice"))))
                victim.write_text("* deck written by a SECOND invocation\n")

        self._install_runner(on_run=clobber)
        status, out, err = self._run()

        self.assertEqual(status, cli.EXIT_RECORD_CORRUPT)
        self.assertNotIn("status    : OK", out)
        self.assertIn("raw output does not match the recorded checksums", out)
        self.assertIn("sha256 on disk", err)
        self.assertIn("Do NOT commit these records", err)

    def test_raw_output_clobbered_before_the_record_is_written_is_refused(self):
        """Same collision, landing between build_record() and write_record():
        the corrupt record must never reach the disk at all."""
        self._install_runner()
        real_build = cli.report.build_record

        def build_then_clobber(*args, **kwargs):
            record = real_build(*args, **kwargs)
            raw_dir = Path(record["raw_dir"])
            for path in sorted(raw_dir.glob("*.log")):
                path.write_text("m_vout = 9.99\n")  # another run's result
            return record

        with mock.patch.object(cli.report, "build_record", side_effect=build_then_clobber):
            status, _out, err = self._run()

        self.assertEqual(status, cli.EXIT_RECORD_CORRUPT)
        self.assertEqual(list(self.records_dir.glob("*.md")), [])
        self.assertIn("raw output changed after it was hashed", err)


class NoWriteScratchIsolationTests(RunIntegrityTests):
    # Inherits only the fixture; the parent's own tests run in their class.
    test_clean_run_reserves_disjoint_stems_and_reports_ok = None
    test_a_second_writer_clobbering_raw_output_fails_the_run = None
    test_raw_output_clobbered_before_the_record_is_written_is_refused = None

    """``--no-write`` invocations never share scratch directories (#499).

    Reuses the RunIntegrityTests fixture (fake PDK, tiny testbench); the
    simulator is a stub, so no PDK or ngspice is needed. Overlap between two
    invocations is made deterministic by running the second one from inside
    the first one's stubbed simulator call.
    """

    def setUp(self):
        super().setUp()
        self.work_dir = self.root / "work"
        patcher = mock.patch.object(cli, "WORK_DIR", self.work_dir)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _run_one_point(self, *extra):
        argv = [str(self.tb_dir), "--corners", "tt", "--temps", "27",
                "--supply-tol", "0", "--no-write", *extra]
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = cli.main(argv)
        return status, out.getvalue(), err.getvalue()

    def test_overlapping_invocations_use_disjoint_scratch_and_keep_each_others_files(self):
        seen: dict[str, Path] = {}
        inner: dict[str, tuple] = {}

        def fake_run_one(tb, pdk, point, workdir, seed=None, run_index=0, timeout_s=0):
            workdir.mkdir(parents=True, exist_ok=True)
            deck = workdir / f"{point.corner_id}.spice"
            log = workdir / f"{point.corner_id}.log"
            if "outer" not in seen:
                seen["outer"] = workdir
                deck.write_text("* outer deck\n")
                log.write_text("m_vout = 1.0\n")
                (workdir / "sentinel").write_text("outer")
                # Second invocation starts while the first is mid-run, same
                # testbench, point and seed.
                inner["result"] = self._run_one_point()
                # The first run's files must be untouched by the second.
                self.assertEqual((workdir / "sentinel").read_text(), "outer")
                self.assertEqual(deck.read_text(), "* outer deck\n")
                self.assertEqual(log.read_text(), "m_vout = 1.0\n")
                value = 1.0
            else:
                seen["inner"] = workdir
                deck.write_text("* inner deck\n")
                log.write_text("m_vout = 2.0\n")
                value = 2.0
            return runner.RunResult(
                point=point, seed=seed, status="ok", measurements={"vout": value},
                seconds=0.1, deck_name=deck.name, log_name=log.name,
            )

        with mock.patch.object(cli.runner, "run_one", side_effect=fake_run_one):
            status, out, _err = self._run_one_point()

        self.assertEqual(status, cli.EXIT_OK)
        self.assertEqual(inner["result"][0], cli.EXIT_OK)
        outer_dir, inner_dir = seen["outer"], seen["inner"]
        self.assertNotEqual(outer_dir, inner_dir)
        self.assertNotEqual(outer_dir.parent, inner_dir.parent)
        # Each result is tied to its own output.
        self.assertIn("vout=1", out)
        self.assertIn("vout=2", inner["result"][1])
        # Scratch is retained and its location is reported.
        self.assertTrue(any(outer_dir.glob("*.log")))
        self.assertIn(str(outer_dir.parent), out)
        self.assertIn(str(inner_dir.parent), inner["result"][1])
        # No evidence record minted by either run.
        self.assertFalse(self.records_dir.exists() and any(self.records_dir.iterdir()))

    def test_a_failing_invocation_does_not_disturb_the_other(self):
        seen: dict[str, Path] = {}
        inner: dict[str, tuple] = {}

        def fake_run_one(tb, pdk, point, workdir, seed=None, run_index=0, timeout_s=0):
            workdir.mkdir(parents=True, exist_ok=True)
            log = workdir / f"{point.corner_id}.log"
            if "outer" not in seen:
                seen["outer"] = workdir
                log.write_text("m_vout = 1.0\n")
                inner["result"] = self._run_one_point()
                self.assertEqual(log.read_text(), "m_vout = 1.0\n")
                return runner.RunResult(
                    point=point, seed=seed, status="ok", measurements={"vout": 1.0},
                    seconds=0.1, deck_name="d", log_name=log.name,
                )
            log.write_text("fatal\n")
            return runner.RunResult(
                point=point, seed=seed, status="failed", measurements={},
                seconds=0.1, deck_name="d", log_name=log.name, message="boom",
            )

        with mock.patch.object(cli.runner, "run_one", side_effect=fake_run_one):
            status, _out, _err = self._run_one_point()

        self.assertEqual(status, cli.EXIT_OK)
        self.assertEqual(inner["result"][0], cli.EXIT_CHECK_FAILED)
        # The failing run's diagnostics are retained.
        self.assertTrue(any(self.work_dir.rglob("*.log")))


class InvalidPlanRejectionTests(RunIntegrityTests):
    # Inherits only the fixture; the parent's own tests run in their class.
    test_clean_run_reserves_disjoint_stems_and_reports_ok = None
    test_a_second_writer_clobbering_raw_output_fails_the_run = None
    test_raw_output_clobbered_before_the_record_is_written_is_refused = None

    """A plan that repeats a seed or a PVT point, or whose points alias to one
    output id, is refused before anything is allocated (#511).

    For every invalid plan, in write and ``--no-write`` mode and with
    ``-j 1`` and ``-j 2``: the simulator stub is never called, no
    ``raw/<stem>/`` directory is reserved, no ``run-*`` scratch directory is
    created, and the exit is nonzero with the repeated value on stderr.
    """

    INVALID_PLANS = (
        # (label, extra argv, text the diagnostic must contain)
        ("duplicate seed", ["--temps", "27", "--supply-tol", "0", "--seeds", "1001", "1002", "1001"],
         "duplicate seed(s) 1001 "),
        ("duplicate temperature", ["--temps", "27", "125", "27", "--supply-tol", "0", "--seeds", "1"],
         "repeated PVT point tt_27c_3.30v"),
        # 3.3 V +/-0.1% -> 3.2967 / 3.3 / 3.3033 V, all formatted as 3.30v.
        ("aliasing supplies", ["--temps", "27", "--supply-tol", "0.001", "--seeds", "1"],
         "share the output id tt_27c_3.30v"),
        ("NaN temperature", ["--temps", "nan", "--supply-tol", "0", "--seeds", "1"],
         "temperature must be finite, got nan"),
        ("infinite temperature", ["--temps", "inf", "--supply-tol", "0", "--seeds", "1"],
         "temperature must be finite, got inf"),
        ("zero nominal supply", ["--temps", "27", "--supply", "0", "--seeds", "1"],
         "nominal supply must be finite and > 0 V, got 0.0"),
        ("infinite nominal supply", ["--temps", "27", "--supply", "inf", "--seeds", "1"],
         "nominal supply must be finite and > 0 V, got inf"),
        ("negative tolerance", ["--temps", "27", "--supply-tol", "-0.1", "--seeds", "1"],
         "supply tolerance must be finite and >= 0, got -0.1"),
        ("NaN tolerance", ["--temps", "27", "--supply-tol", "nan", "--seeds", "1"],
         "supply tolerance must be finite and >= 0, got nan"),
    )

    def setUp(self):
        super().setUp()
        (self.tb_dir / "tb.json").write_text(
            json.dumps({
                "name": "an-experiment", "netlist": "x.spice",
                "measure": {"vout": "v(out)"},
                "analysis_type": "tran-noise", "default_runs": 2,
            })
        )
        self.work_dir = self.root / "work"
        patcher = mock.patch.object(cli, "WORK_DIR", self.work_dir)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _invoke(self, extra):
        argv = [str(self.tb_dir), "--corners", "tt", *extra]
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = cli.main(argv)
        return status, out.getvalue(), err.getvalue()

    def test_invalid_plans_launch_nothing_and_allocate_nothing(self):
        for label, extra, needle in self.INVALID_PLANS:
            for mode in ([], ["--no-write"]):
                for jobs in ("1", "2"):
                    with self.subTest(plan=label, mode=mode or "write", jobs=jobs):
                        with mock.patch.object(cli.runner, "run_one") as run_one, \
                                mock.patch.object(cli.report, "reserve_record_stems",
                                                  wraps=cli.report.reserve_record_stems) as reserve:
                            status, out, err = self._invoke([*extra, *mode, "-j", jobs])
                        self.assertEqual(status, cli.EXIT_ENVIRONMENT)
                        self.assertIn(needle, err)
                        self.assertNotIn("status    : OK", out)
                        run_one.assert_not_called()
                        reserve.assert_not_called()
                        raw = self.records_dir / report.RAW_DIRNAME
                        self.assertFalse(raw.exists() and any(raw.iterdir()))
                        self.assertFalse(self.records_dir.exists() and any(self.records_dir.glob("*.md")))
                        self.assertFalse(self.work_dir.exists() and any(self.work_dir.rglob("run-*")))

    def test_manifest_with_invalid_plan_is_rejected_before_allocation(self):
        for label, overrides, needle in (
            ("empty temperatures", {"temperatures_c": []}, "grid is empty"),
            ("negative tolerance", {"supply_tolerance": -0.05}, "supply tolerance must be"),
            ("zero nominal", {"nominal_supply_v": 0}, "nominal supply must be"),
        ):
            manifest = {
                "name": "an-experiment", "netlist": "x.spice",
                "measure": {"vout": "v(out)"},
                "analysis_type": "tran-noise", "default_runs": 2,
                "temperatures_c": [27], "supply_tolerance": 0, **overrides,
            }
            (self.tb_dir / "tb.json").write_text(json.dumps(manifest))
            for jobs in ("1", "2"):
                with self.subTest(case=label, jobs=jobs):
                    with mock.patch.object(cli.runner, "run_one") as run_one, \
                            mock.patch.object(cli.report, "reserve_record_stems") as reserve:
                        status, out, err = self._invoke(["-j", jobs])
                    self.assertEqual(status, cli.EXIT_ENVIRONMENT)
                    self.assertIn(needle, err)
                    self.assertNotIn("status    : OK", out)
                    run_one.assert_not_called()
                    reserve.assert_not_called()
                    self.assertFalse(self.work_dir.exists() and any(self.work_dir.rglob("run-*")))

    def test_zero_tolerance_and_out_of_envelope_requests_still_run(self):
        self._install_runner(on_run=lambda point, _w: None)
        status, out, err = self._invoke(
            ["--temps", "-60", "200", "--supply", "1.2", "--supply-tol", "0",
             "--seeds", "1", "--no-write"]
        )
        self.assertEqual(status, cli.EXIT_OK, err)
        self.assertIn("status    : OK", out)

    def test_distinct_seeds_and_points_still_run_and_write_records(self):
        for jobs in ("1", "2"):
            with self.subTest(jobs=jobs):
                calls: list[tuple] = []
                self._install_runner(on_run=lambda point, _w: calls.append(point.corner_id))
                status, out, err = self._invoke(
                    ["--temps", "27", "125", "--supply-tol", "0", "--seeds", "1002", "1001",
                     "-j", jobs]
                )
                self.assertEqual(status, cli.EXIT_OK, err)
                self.assertIn("status    : OK", out)
                self.assertEqual(len(calls), 4)  # 2 points x 2 seeds
                self.assertEqual(sorted(set(calls)), ["tt_125c_3.30v", "tt_27c_3.30v"])
        records = sorted(self.records_dir.glob("*.md"))
        self.assertEqual(len(records), 4)  # two invocations x two points
        for path in records:
            self.assertEqual(report.verify_record_file(path, self.root), [])
            self.assertIn("1002, 1001", path.read_text())

    def test_default_seeds_still_run_in_no_write_mode(self):
        self._install_runner()
        status, out, err = self._invoke(["--temps", "27", "--supply-tol", "0", "--no-write"])
        self.assertEqual(status, cli.EXIT_OK, err)
        self.assertEqual(len(list(self.work_dir.glob("*/run-*"))), 1)


class NonpositiveTimeoutRejectionTests(RunIntegrityTests):
    # Inherits only the fixture; the parent's own tests run in their class.
    test_clean_run_reserves_disjoint_stems_and_reports_ok = None
    test_a_second_writer_clobbering_raw_output_fails_the_run = None
    test_raw_output_clobbered_before_the_record_is_written_is_refused = None

    """``--timeout`` must be a strictly positive integer: coreutils
    ``timeout(1)`` treats 0 as "no timeout", which would disable the
    independent watchdog. An invalid bound is refused before PDK discovery,
    record-stem reservation, or any simulator launch (#563).
    """

    def _assert_nothing_started(self, run_one, reserve, find_pdk):
        run_one.assert_not_called()
        reserve.assert_not_called()
        find_pdk.assert_not_called()
        raw = self.records_dir / report.RAW_DIRNAME
        self.assertFalse(raw.exists() and any(raw.iterdir()))

    def test_parser_rejects_nonpositive_and_non_integer_timeouts(self):
        parser = cli.build_parser()
        for bad in ("0", "-1", "abc", "1.5"):
            with self.subTest(timeout=bad):
                err = io.StringIO()
                with redirect_stderr(err), self.assertRaises(SystemExit) as ctx:
                    parser.parse_args(["tb", "--timeout", bad])
                self.assertEqual(ctx.exception.code, 2)
                self.assertIn("--timeout", err.getvalue())

    def test_parser_keeps_default_and_accepts_positive_timeout(self):
        parser = cli.build_parser()
        self.assertEqual(parser.parse_args(["tb"]).timeout, runner.DEFAULT_TIMEOUT_S)
        self.assertEqual(parser.parse_args(["tb", "--timeout", "7"]).timeout, 7)

    def test_nonpositive_timeout_launches_nothing_and_allocates_nothing(self):
        for bad in ("0", "-1"):
            for mode in ([], ["--no-write"]):
                for jobs in ("1", "2"):
                    with self.subTest(timeout=bad, mode=mode or "write", jobs=jobs):
                        with mock.patch.object(cli.runner, "run_one") as run_one, \
                                mock.patch.object(cli, "find_pdk") as find_pdk, \
                                mock.patch.object(cli.report, "reserve_record_stems",
                                                  wraps=cli.report.reserve_record_stems) as reserve:
                            err = io.StringIO()
                            with redirect_stdout(io.StringIO()), redirect_stderr(err), \
                                    self.assertRaises(SystemExit) as ctx:
                                cli.main([str(self.tb_dir), "--corners", "tt", "--timeout", bad,
                                          "-j", jobs, *mode])
                        self.assertEqual(ctx.exception.code, 2)
                        self.assertIn("positive integer", err.getvalue())
                        self._assert_nothing_started(run_one, reserve, find_pdk)

    def test_run_refuses_a_hand_built_namespace_with_nonpositive_timeout(self):
        for bad in (0, -5):
            with self.subTest(timeout=bad):
                args = cli.build_parser().parse_args([str(self.tb_dir), "--corners", "tt"])
                args.timeout = bad
                with mock.patch.object(cli.runner, "run_one") as run_one, \
                        mock.patch.object(cli, "find_pdk") as find_pdk, \
                        mock.patch.object(cli.report, "reserve_record_stems") as reserve:
                    err = io.StringIO()
                    with redirect_stderr(err):
                        status = cli.run(args)
                self.assertEqual(status, cli.EXIT_ENVIRONMENT)
                self.assertIn("positive integer", err.getvalue())
                self._assert_nothing_started(run_one, reserve, find_pdk)

    def test_positive_timeout_is_forwarded_to_every_run_serial_and_parallel(self):
        for jobs in ("1", "2"):
            with self.subTest(jobs=jobs):
                self._install_runner()
                status, _out, _err = self._run("--no-write", "--timeout", "42", "-j", jobs)
                self.assertEqual(status, cli.EXIT_OK)
                calls = cli.runner.run_one.call_args_list
                self.assertTrue(calls)
                self.assertTrue(all(c.kwargs["timeout_s"] == 42 for c in calls))
                mock.patch.stopall()
                self.setUp()


class TimeoutSummaryTests(unittest.TestCase):
    """A corner ``runner.run_one`` reports as killed by the wall-clock bound
    (issue #83) must stand out in the summary and still leave a written
    breadcrumb record naming the deck and elapsed time -- not vanish the
    way the incident's silent 4.5h hang did."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.records_dir = self.root / "records"

        self.tb_dir = self.root / "tb" / "an-experiment"
        self.tb_dir.mkdir(parents=True)
        (self.tb_dir / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (self.tb_dir / "tb.json").write_text(
            json.dumps({
                "name": "an-experiment", "netlist": "x.spice",
                "measure": {"vout": "v(out)"},
            })
        )

        variant = _make_variant(self.root, "gf180mcuD")
        (variant / "libs.tech" / "ngspice" / "design.ngspice").write_text("* fake\n")
        (variant / "SOURCES").write_text("open_pdks deadbeef\n")
        pdk = Pdk(path=variant, variant="gf180mcuD", source="test")

        for target, value in (
            ("RECORDS_DIR", self.records_dir),
            ("REPO_ROOT", self.root),
        ):
            patcher = mock.patch.object(cli, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        for target, value in (
            ("find_pdk", lambda: pdk),
            ("git_provenance", lambda _root: {"commit": "f" * 40, "dirty": False}),
        ):
            patcher = mock.patch.object(
                cli if target == "find_pdk" else cli.report, target, value
            )
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = mock.patch.object(cli.runner, "ngspice_version", return_value="ngspice-46")
        patcher.start()
        self.addCleanup(patcher.stop)

    def _install_runner(self, timed_out_corner: str):
        def fake_run_one(tb, pdk, point, workdir, seed=None, run_index=0, timeout_s=0):
            workdir.mkdir(parents=True, exist_ok=True)
            stem = point.corner_id
            deck = workdir / f"{stem}.spice"
            deck.write_text(f"* deck for {stem}\n")
            if point.corner.name == timed_out_corner:
                log = workdir / f"{stem}.log"
                log.write_text(f"TIMEOUT after {timeout_s}.0s (bound {timeout_s}s)\n")
                return runner.RunResult(
                    point=point, seed=seed, status="timeout", seconds=float(timeout_s),
                    deck_name=deck.name, log_name=log.name,
                    message=(
                        f"ngspice timed out: no result after {timeout_s}.0s "
                        f"(bound {timeout_s}s + 30s kill-grace), killed by timeout(1)/gtimeout "
                        f"via process-group SIGKILL; deck {deck.name}"
                    ),
                )
            log = workdir / f"{stem}.log"
            log.write_text("m_vout = 1.65\n")
            return runner.RunResult(
                point=point, seed=seed, status="ok", measurements={"vout": 1.65},
                seconds=0.1, deck_name=deck.name, log_name=log.name,
            )

        patcher = mock.patch.object(cli.runner, "run_one", side_effect=fake_run_one)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _run(self, *extra: str):
        argv = [str(self.tb_dir), "--corners", "tt", "ss", "--temps", "27",
                "--supply-tol", "0", *extra]
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = cli.main(argv)
        return status, out.getvalue(), err.getvalue()

    def test_timed_out_corner_reports_failed_timeout_and_fails_the_run(self):
        self._install_runner(timed_out_corner="ss")
        status, out, _err = self._run()

        self.assertEqual(status, cli.EXIT_CHECK_FAILED)
        self.assertIn("FAILED-TIMEOUT", out)
        self.assertIn("status    : FAIL", out)
        # The corner that actually completed must still read as ok, not be
        # dragged down by its sibling's timeout.
        self.assertIn("ok  ", out)

    def test_timed_out_corner_still_leaves_a_written_breadcrumb_record(self):
        self._install_runner(timed_out_corner="ss")
        self._run()

        stems = sorted(p.stem for p in self.records_dir.glob("*.md"))
        self.assertEqual(len(stems), 2)
        texts = [(self.records_dir / f"{s}.md").read_text() for s in stems]
        candidates = [t for t in texts if "process: ss" in t]
        self.assertEqual(len(candidates), 1, "expected exactly one ss-corner record")
        text = candidates[0]
        # Names the deck and the elapsed/bound time (issue #83 AC #3), and
        # is a normal written record under sim/records/ -- not an absent
        # result -- so a reviewing Judge sees the hang.
        self.assertIn("timeout --", text)
        self.assertIn("kill-grace", text)
        self.assertIn(".spice", text)


class ExecutionFailureExitTests(unittest.TestCase):
    """A fake ngspice that prints every measurement but exits nonzero (issue
    #498) must fail the CLI run; the real ``runner.run_one`` is exercised."""

    setUp = TimeoutSummaryTests.setUp
    _run = TimeoutSummaryTests._run

    def _fake(self, body: str):
        bin_dir = self.root / "bin"
        bin_dir.mkdir(exist_ok=True)
        path = bin_dir / "ngspice"
        path.write_text("#!/usr/bin/env python3\n" + body)
        path.chmod(0o755)
        patcher = mock.patch.dict(
            os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_nonzero_exit_with_all_measurements_fails_the_run(self):
        self._fake("import sys\nprint('m_vout = 1.65')\nsys.exit(1)\n")
        status, out, _err = self._run()
        self.assertEqual(status, cli.EXIT_CHECK_FAILED)
        self.assertIn("FAIL", out)

    def test_clean_run_exits_ok(self):
        self._fake("print('Warning: benign')\nprint('m_vout = 1.65')\n")
        status, _out, _err = self._run()
        self.assertEqual(status, 0)

    def test_overflowed_sole_measurement_fails_the_run(self):
        # Issue #527: `1e999` overflows float() to +/-inf without raising.
        for raw in ("1e999", "-1e999"):
            with self.subTest(raw=raw):
                self._fake(f"print('m_vout = {raw}')\n")
                status, out, _err = self._run()
                self.assertEqual(status, cli.EXIT_CHECK_FAILED)
                self.assertIn("FAIL", out)
                self.assertIn("non-finite measurements: vout", out)

    def test_literal_non_finite_measurement_fails_the_run(self):
        for raw in ("inf", "nan"):
            with self.subTest(raw=raw):
                self._fake(f"print('m_vout = {raw}')\n")
                status, out, _err = self._run()
                self.assertEqual(status, cli.EXIT_CHECK_FAILED)
                self.assertIn("FAIL", out)


if __name__ == "__main__":
    unittest.main()
