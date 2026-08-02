#!/usr/bin/env python3
"""Unit tests for sim/harness/cli.py: the "shadowed PDK variant" note added
in #39, and the raw-output integrity check a completed run must pass (#60).
"""

from __future__ import annotations

import io
import json
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


if __name__ == "__main__":
    unittest.main()
