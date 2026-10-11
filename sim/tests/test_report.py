#!/usr/bin/env python3
"""Unit tests for sim/harness/report.py -- the append-only evidence-record
writer conforming to sim/README.md."""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR))

from harness import corners, report, runner, testbench  # noqa: E402
from harness.pdk import Pdk  # noqa: E402


class ChecksumTests(unittest.TestCase):
    def test_sha256_file_matches_hashlib(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.txt"
            path.write_text("hello evidence\n")
            expected = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(report.sha256_file(path), expected)

    def test_blob_sha_is_stable_for_identical_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = root / "a.spice"
            b = root / "b.spice"
            a.write_text("same content\n")
            b.write_text("same content\n")
            self.assertEqual(report.blob_sha(root, a), report.blob_sha(root, b))

    def test_blob_sha_differs_for_different_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a = root / "a.spice"
            b = root / "b.spice"
            a.write_text("content one\n")
            b.write_text("content two\n")
            self.assertNotEqual(report.blob_sha(root, a), report.blob_sha(root, b))


class RawPathValidationTests(unittest.TestCase):
    def test_library_rejects_escapes_before_hashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp).resolve()
            records = repo / "sim" / "records"
            (records / "raw" / "s").mkdir(parents=True)
            outside = repo.parent / "outside-raw-dir"
            outside.mkdir(exist_ok=True)
            self.addCleanup(outside.rmdir)
            digest = "0" * 64
            for raw_path, name in (
                (str(outside), "a.log"), ("../outside-raw-dir", "a.log"),
                ("sim/records/raw/s", "../a.log"), ("sim/records/raw/s", "/etc/hostname"),
            ):
                rec = records / "r.md"
                rec.write_text(
                    f"---\nraw:\n  path: {raw_path}\n  files:\n    - {name}  sha256:{digest}\n---\n"
                )
                with mock.patch.object(report, "sha256_file") as spy:
                    problems = report.verify_record_file(rec, repo)
                self.assertTrue(problems and "invalid raw provenance" in problems[0], problems)
                spy.assert_not_called()


class RecordStemTests(unittest.TestCase):
    def test_first_allocation_is_01(self):
        with tempfile.TemporaryDirectory() as tmp:
            records_dir = Path(tmp)
            stem = report.allocate_record_stem(records_dir, "2026-08-14", "ro-jitter")
            self.assertEqual(stem, "2026-08-14-ro-jitter-01")

    def test_allocation_never_reuses_an_existing_stem(self):
        with tempfile.TemporaryDirectory() as tmp:
            records_dir = Path(tmp)
            first = report.allocate_record_stem(records_dir, "2026-08-14", "ro-jitter")
            (records_dir / f"{first}.md").write_text("# first\n")
            second = report.allocate_record_stem(records_dir, "2026-08-14", "ro-jitter")
            self.assertEqual(second, "2026-08-14-ro-jitter-02")
            # the existing record was not touched
            self.assertEqual((records_dir / f"{first}.md").read_text(), "# first\n")

    def test_allocation_respects_a_raw_dir_with_no_record_yet(self):
        """A run still in flight has a raw/<stem>/ but no <stem>.md.

        A second concurrent run_corners.py invocation must not be handed that
        same number -- it would only find out at write_record() time, after
        paying for the whole run.
        """
        with tempfile.TemporaryDirectory() as tmp:
            records_dir = Path(tmp)
            in_flight = report.allocate_record_stem(records_dir, "2026-08-14", "ro-jitter")
            (records_dir / report.RAW_DIRNAME / in_flight).mkdir(parents=True)
            second = report.allocate_record_stem(records_dir, "2026-08-14", "ro-jitter")
            self.assertEqual(in_flight, "2026-08-14-ro-jitter-01")
            self.assertEqual(second, "2026-08-14-ro-jitter-02")

    def test_different_slugs_do_not_collide(self):
        with tempfile.TemporaryDirectory() as tmp:
            records_dir = Path(tmp)
            (records_dir / "2026-08-14-alpha-01.md").write_text("x")
            stem = report.allocate_record_stem(records_dir, "2026-08-14", "beta")
            self.assertEqual(stem, "2026-08-14-beta-01")


class StemReservationTests(unittest.TestCase):
    """reserve_record_stems() claims stems by creating raw/<stem>/ (#60)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.records_dir = Path(self.tmp.name)

    def test_reservation_creates_the_raw_directory(self):
        stems = report.reserve_record_stems(self.records_dir, "2026-08-14", "ro-jitter", 2)
        self.assertEqual(stems, ["2026-08-14-ro-jitter-01", "2026-08-14-ro-jitter-02"])
        for stem in stems:
            self.assertTrue((self.records_dir / report.RAW_DIRNAME / stem).is_dir())

    def test_two_reservations_never_overlap(self):
        first = report.reserve_record_stems(self.records_dir, "2026-08-14", "ro-jitter", 3)
        second = report.reserve_record_stems(self.records_dir, "2026-08-14", "ro-jitter", 3)
        self.assertEqual(set(first) & set(second), set())
        self.assertEqual(second, [f"2026-08-14-ro-jitter-{n:02d}" for n in (4, 5, 6)])

    def test_reservation_skips_a_stem_another_invocation_already_holds(self):
        """The exact race #60 reports: a second invocation whose scan of the
        directory saw the same free numbers the first one is about to take.

        Simulated by pre-creating the raw directories the scan would hand out,
        which is what the other process's own reservation would have done.
        """
        raw_root = self.records_dir / report.RAW_DIRNAME
        raw_root.mkdir(parents=True)
        for n in (1, 2):
            (raw_root / f"2026-08-14-ro-jitter-{n:02d}").mkdir()
        stems = report.reserve_record_stems(self.records_dir, "2026-08-14", "ro-jitter", 2)
        self.assertEqual(stems, ["2026-08-14-ro-jitter-03", "2026-08-14-ro-jitter-04"])

    def test_reservation_skips_a_stem_whose_record_exists_without_a_raw_dir(self):
        (self.records_dir / "2026-08-14-ro-jitter-01.md").write_text("# a record\n")
        stems = report.reserve_record_stems(self.records_dir, "2026-08-14", "ro-jitter", 1)
        self.assertEqual(stems, ["2026-08-14-ro-jitter-02"])

    def test_concurrent_reservations_are_disjoint(self):
        """Threads standing in for concurrent run_corners.py processes.

        mkdir(2) is the arbiter, so no two callers can come away with the
        same stem no matter how their scans interleave.
        """
        results: list[list[str]] = []
        barrier = threading.Barrier(4)

        def reserve():
            barrier.wait()
            results.append(
                report.reserve_record_stems(self.records_dir, "2026-08-14", "ro-jitter", 5)
            )

        threads = [threading.Thread(target=reserve) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        allocated = [stem for batch in results for stem in batch]
        self.assertEqual(len(allocated), 20)
        self.assertEqual(len(set(allocated)), 20, "two callers were handed the same stem")


class FinalizeRecordTests(unittest.TestCase):
    """finalize_record() reserves its stem before render runs (#514).

    PDK-free: the render callbacks here stand in for the behavioral
    ``sim/tb/*/run_*.py`` writers that share this finalizer.
    """

    DATE = "2026-08-14"
    SLUG = "a-behavioral-demo"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo_root = Path(self.tmp.name)
        self.records_dir = self.repo_root / "sim" / "records"

    def _raw(self, stem: str) -> Path:
        return self.records_dir / report.RAW_DIRNAME / stem

    def _render_with_checksums(self, payload: bytes):
        """A render callback shaped like the shipped behavioral writers."""
        def render(stem: str, raw_dir: Path) -> str:
            (raw_dir / "out.bin").write_bytes(payload)
            digest = report.sha256_file(raw_dir / "out.bin")
            rel = raw_dir.relative_to(self.repo_root).as_posix()
            return (
                "---\n"
                f"record: {stem}\n"
                "raw:\n"
                f"  path: {rel}\n"
                "  files:\n"
                f"    - out.bin  sha256:{digest}\n"
                "---\n\n"
                f"# {stem}\n"
            )
        return render

    def test_concurrent_allocations_get_distinct_stems_and_disjoint_raw_dirs(self):
        """Both writers' scans are forced to finish before either claims a
        stem -- the interleaving in which the advisory allocator hands both
        the same number -- and both renders then run at the same time."""
        scan_barrier = threading.Barrier(2, timeout=10)
        render_barrier = threading.Barrier(2, timeout=10)
        real_scan = report.allocate_record_stems

        def synchronized_scan(*args, **kwargs):
            stems = real_scan(*args, **kwargs)
            scan_barrier.wait()
            return stems

        results: dict[str, tuple[str, Path, list[str]]] = {}
        errors: list[BaseException] = []

        def writer(name: str):
            def render(stem: str, raw_dir: Path) -> str:
                render_barrier.wait()
                (raw_dir / f"{name}.txt").write_text(name)
                render_barrier.wait()  # both have written before either lists
                listing = sorted(p.name for p in raw_dir.iterdir())
                results[name] = (stem, raw_dir, listing)
                return f"# {stem} by {name}\n"
            try:
                report.finalize_record(self.records_dir, self.DATE, self.SLUG, render)
            except BaseException as exc:  # surfaced in the main thread
                errors.append(exc)

        with mock.patch.object(report, "allocate_record_stems", side_effect=synchronized_scan):
            threads = [threading.Thread(target=writer, args=(n,)) for n in ("alpha", "beta")]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        self.assertEqual(errors, [])
        (stem_a, raw_a, list_a), (stem_b, raw_b, list_b) = results["alpha"], results["beta"]
        self.assertNotEqual(stem_a, stem_b, "two writers were handed the same stem")
        self.assertNotEqual(raw_a, raw_b)
        self.assertEqual(list_a, ["alpha.txt"], "beta wrote into alpha's raw directory")
        self.assertEqual(list_b, ["beta.txt"], "alpha wrote into beta's raw directory")
        self.assertEqual(
            sorted([stem_a, stem_b]),
            [f"{self.DATE}-{self.SLUG}-01", f"{self.DATE}-{self.SLUG}-02"],
        )
        self.assertEqual((self.records_dir / f"{stem_a}.md").read_text(), f"# {stem_a} by alpha\n")
        self.assertEqual((self.records_dir / f"{stem_b}.md").read_text(), f"# {stem_b} by beta\n")

    def test_raw_dir_is_reserved_before_render_runs(self):
        seen = {}

        def render(stem: str, raw_dir: Path) -> str:
            seen["is_dir"] = raw_dir.is_dir()
            seen["empty"] = not any(raw_dir.iterdir())
            # A second allocation while this render is in flight skips it.
            seen["next"] = report.reserve_record_stems(self.records_dir, self.DATE, self.SLUG, 1)[0]
            return "# x\n"

        report.finalize_record(self.records_dir, self.DATE, self.SLUG, render)
        self.assertEqual(seen["is_dir"], True)
        self.assertEqual(seen["empty"], True)
        self.assertEqual(seen["next"], f"{self.DATE}-{self.SLUG}-02")

    def test_renderer_failure_keeps_its_partial_directory_occupied(self):
        def failing(stem: str, raw_dir: Path) -> str:
            (raw_dir / "partial.bin").write_bytes(b"half")
            raise RuntimeError("renderer blew up")

        with self.assertRaises(RuntimeError):
            report.finalize_record(self.records_dir, self.DATE, self.SLUG, failing)
        failed = f"{self.DATE}-{self.SLUG}-01"
        self.assertEqual((self._raw(failed) / "partial.bin").read_bytes(), b"half")
        self.assertFalse((self.records_dir / f"{failed}.md").exists())

        handed = {}

        def render(stem: str, raw_dir: Path) -> str:
            handed["stem"] = stem
            handed["listing"] = sorted(p.name for p in raw_dir.iterdir())
            return "# retry\n"

        path = report.finalize_record(self.records_dir, self.DATE, self.SLUG, render)
        self.assertEqual(handed["stem"], f"{self.DATE}-{self.SLUG}-02")
        self.assertEqual(handed["listing"], [], "retry was handed a non-empty raw directory")
        self.assertEqual(path.name, f"{self.DATE}-{self.SLUG}-02.md")
        # The failed attempt's partial output is untouched.
        self.assertEqual((self._raw(failed) / "partial.bin").read_bytes(), b"half")

    def test_existing_record_without_raw_dir_is_skipped_not_overwritten(self):
        first = self.records_dir / f"{self.DATE}-{self.SLUG}-01.md"
        self.records_dir.mkdir(parents=True)
        first.write_text("# historical record\n")
        path = report.finalize_record(self.records_dir, self.DATE, self.SLUG, lambda s, d: "# new\n")
        self.assertEqual(path.name, f"{self.DATE}-{self.SLUG}-02.md")
        self.assertEqual(first.read_text(), "# historical record\n")

    def test_record_appearing_between_render_and_publish_is_not_overwritten(self):
        def render(stem: str, raw_dir: Path) -> str:
            (raw_dir / "out.bin").write_bytes(b"mine")
            # Another writer publishes this stem's markdown while we render.
            (self.records_dir / f"{stem}.md").write_text("# someone else's record\n")
            return "# would clobber\n"

        with self.assertRaises(report.RecordExists):
            report.finalize_record(self.records_dir, self.DATE, self.SLUG, render)
        stem = f"{self.DATE}-{self.SLUG}-01"
        self.assertEqual(
            (self.records_dir / f"{stem}.md").read_text(), "# someone else's record\n"
        )
        # The reservation stays occupied; the next writer moves on.
        self.assertTrue(self._raw(stem).is_dir())
        nxt = report.finalize_record(self.records_dir, self.DATE, self.SLUG, lambda s, d: "# n\n")
        self.assertEqual(nxt.name, f"{self.DATE}-{self.SLUG}-02.md")

    def test_publish_record_text_refuses_existing_file(self):
        path = Path(self.tmp.name) / "r.md"
        path.write_text("original\n")
        with self.assertRaises(report.RecordExists):
            report.publish_record_text(path, "replacement\n")
        self.assertEqual(path.read_text(), "original\n")

    def test_sequential_records_keep_format_and_verify(self):
        paths = [
            report.finalize_record(
                self.records_dir, self.DATE, self.SLUG, self._render_with_checksums(payload)
            )
            for payload in (b"one", b"two")
        ]
        self.assertEqual(
            [p.name for p in paths],
            [f"{self.DATE}-{self.SLUG}-01.md", f"{self.DATE}-{self.SLUG}-02.md"],
        )
        for path in paths:
            text = path.read_text()
            self.assertTrue(text.startswith(f"---\nrecord: {path.stem}\n"))
            self.assertEqual(report.verify_record_file(path, self.repo_root), [])


def fake_pdk(root: Path) -> Pdk:
    (root / "libs.tech" / "ngspice").mkdir(parents=True, exist_ok=True)
    (root / "libs.tech" / "ngspice" / "sm141064.ngspice").write_text("* fake\n")
    (root / "libs.tech" / "ngspice" / "design.ngspice").write_text("* fake\n")
    (root / "SOURCES").write_text("open_pdks deadbeef\n")
    return Pdk(path=root, variant=root.name, source="test")


class BuildRecordTests(unittest.TestCase):
    """The rendered record carries exactly the fields sim/README.md requires."""

    REQUIRED_FRONTMATTER_LABELS = (
        "record:", "date:", "status:", "testbench:", "netlist:", "repo_commit:",
        "pdk:", "pdk.models:", "tool:", "corner:", "analysis:", "seeds:",
        "raw:", "wall_time:",
    )

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        tb_dir = root / "tb" / "an-experiment"
        tb_dir.mkdir(parents=True)
        (tb_dir / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (tb_dir / "tb.json").write_text(
            json.dumps({"name": "an-experiment", "netlist": "x.spice", "measure": {"vout": "v(out)"}})
        )
        self.tb = testbench.load(tb_dir)
        self.pdk = fake_pdk(root / "gf180mcuD")
        self.point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]
        raw_dir = root / "raw"
        raw_dir.mkdir()
        self.results = [
            runner.RunResult(
                point=self.point, seed=None, status="ok", measurements={"vout": 1.65},
                deck_name="tt_27c_3.30v.spice", log_name="tt_27c_3.30v.log",
            )
        ]
        (raw_dir / "tt_27c_3.30v.spice").write_text("* deck\n")
        (raw_dir / "tt_27c_3.30v.log").write_text("m_vout = 1.65\n")
        self.record = report.build_record(
            tb=self.tb, pdk=self.pdk, point=self.point, results=self.results,
            ngspice="ngspice-46", repo_root=root, stem="2026-07-31-an-experiment-01",
            completed_utc=_dt.datetime(2026, 7, 31, 12, 0, 0, tzinfo=_dt.timezone.utc),
            wall_seconds=1.3, raw_dir=raw_dir,
            git={"commit": "f" * 40, "dirty": False},
        )

    def test_every_ratified_field_label_is_present(self):
        text = report.render_frontmatter(self.record)
        for label in self.REQUIRED_FRONTMATTER_LABELS:
            self.assertIn(label, text, f"missing ratified field {label!r}")

    def test_seeds_are_na_for_deterministic_analysis(self):
        text = report.render_frontmatter(self.record)
        self.assertIn("seeds: n/a (deterministic analysis)", text)

    def test_repo_commit_carries_dirty_suffix_when_dirty(self):
        dirty_record = dict(self.record)
        dirty_record["repo_commit"] = report.repo_commit_field({"commit": "a" * 40, "dirty": True})
        self.assertTrue(dirty_record["repo_commit"].endswith("-dirty"))

    def test_raw_files_are_listed_with_checksums(self):
        text = report.render_frontmatter(self.record)
        self.assertIn("tt_27c_3.30v.spice  sha256:", text)
        self.assertIn("tt_27c_3.30v.log  sha256:", text)

    def test_result_section_reports_the_measurement(self):
        text = report.render_result_section(self.record)
        self.assertIn("`vout`: 1.65", text)

    def test_reproduce_section_pins_the_exact_recorded_supply(self):
        # The point built in setUp is 3.3 V -- pass a non-nominal point here
        # to check the regression this guards: omitting --supply/--supply-tol
        # would silently re-sweep tb.nominal_supply_v +/- tb.supply_tolerance
        # (3 points) instead of reproducing the single recorded corner.
        offset_point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.63])[0]
        record = report.build_record(
            tb=self.tb, pdk=self.pdk, point=offset_point, results=self.results,
            ngspice="ngspice-46", repo_root=Path(self.tmp.name), stem="2026-07-31-an-experiment-02",
            completed_utc=_dt.datetime(2026, 7, 31, 12, 0, 0, tzinfo=_dt.timezone.utc),
            wall_seconds=1.3, raw_dir=Path(self.tmp.name) / "raw",
            git={"commit": "f" * 40, "dirty": False},
        )
        text = report.render_reproduce_section(record, self.tb)
        self.assertIn("--supply 3.63 --supply-tol 0", text)

    def _reproduce_with_timeout(self, timeout_s):
        record = report.build_record(
            tb=self.tb, pdk=self.pdk, point=self.point, results=self.results,
            ngspice="ngspice-46", repo_root=Path(self.tmp.name), stem="2026-07-31-an-experiment-03",
            completed_utc=_dt.datetime(2026, 7, 31, 12, 0, 0, tzinfo=_dt.timezone.utc),
            wall_seconds=1.3, raw_dir=Path(self.tmp.name) / "raw",
            git={"commit": "f" * 40, "dirty": False}, timeout_s=timeout_s,
        )
        return report.render_reproduce_section(record, self.tb)

    def test_reproduce_section_carries_a_non_default_timeout(self):
        # A multi-hour transient-noise run is not reproducible by a command
        # that omits the --timeout it ran with: the re-run dies on the 300 s
        # default and records "no data (all runs failed to converge)".
        self.assertIn("--timeout 40000", self._reproduce_with_timeout(40000))

    def test_reproduce_section_omits_the_default_timeout(self):
        self.assertNotIn("--timeout", self._reproduce_with_timeout(runner.DEFAULT_TIMEOUT_S))
        self.assertNotIn("--timeout", self._reproduce_with_timeout(None))

    def test_write_record_refuses_to_overwrite(self):
        records_dir = Path(self.tmp.name) / "records"
        path = report.write_record(self.record, self.tb, records_dir, ["a caveat"])
        self.assertTrue(path.is_file())
        with self.assertRaises(report.RecordExists):
            report.write_record(self.record, self.tb, records_dir, ["a caveat"])

    def test_write_record_publishes_exactly_the_rendered_record(self):
        records_dir = Path(self.tmp.name) / "records"
        expected = report.render_record(self.record, self.tb, ["a caveat"])
        path = report.write_record(self.record, self.tb, records_dir, ["a caveat"])
        self.assertEqual(path, records_dir / "2026-07-31-an-experiment-01.md")
        self.assertEqual(path.read_text(), expected)
        self.assertEqual(report.verify_record(self.record), [])


class FailedRunSeparationTests(unittest.TestCase):
    """Failed runs keep their parsed measurements (runner.run_one) but must
    not feed the primary numeric summaries (#506)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        tb_dir = self.root / "tb" / "an-experiment"
        tb_dir.mkdir(parents=True)
        (tb_dir / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (tb_dir / "tb.json").write_text(json.dumps(
            {"name": "an-experiment", "netlist": "x.spice",
             "measure": {"vout": "v(out)", "iout": "i(v1)"}}))
        self.tb = testbench.load(tb_dir)
        self.pdk = fake_pdk(self.root / "gf180mcuD")
        self.point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]
        self.raw_dir = self.root / "raw"
        self.raw_dir.mkdir()

    def _result(self, seed, status, meas, message="", missing=()):
        return runner.RunResult(
            point=self.point, seed=seed, status=status, measurements=dict(meas),
            missing=list(missing), message=message,
            deck_name=f"s{seed}.spice", log_name=f"s{seed}.log")

    def _text(self, results):
        record = report.build_record(
            tb=self.tb, pdk=self.pdk, point=self.point, results=results,
            ngspice="ngspice-46", repo_root=self.root, stem="2026-07-31-an-experiment-01",
            completed_utc=_dt.datetime(2026, 7, 31, tzinfo=_dt.timezone.utc),
            wall_seconds=1.0, raw_dir=self.raw_dir,
            git={"commit": "f" * 40, "dirty": False})
        return record, report.render_result_section(record)

    def test_mixed_fixture_summarizes_only_successful_run(self):
        both = {"vout": 1.0, "iout": 2.0}
        results = [
            self._result(1, "ok", both),
            self._result(2, "failed", {"vout": 9.0, "iout": 8.0},
                         "ngspice exit 1; Error: singular matrix"),
        ]
        record, text = self._text(results)
        self.assertEqual(record["samples"]["vout"], [1.0])
        self.assertIn("- `vout`: 1\n", text)
        self.assertNotIn("mean", text)
        self.assertIn("Runs: 1 of 2 successful", text)
        self.assertIn("Failed-run diagnostics", text)
        self.assertIn("  - `vout`: 9", text)
        self.assertIn("singular matrix", text)
        # 9.0 appears only in the diagnostics block, after its heading.
        head, _, diag = text.partition("Failed-run diagnostics")
        self.assertNotIn("9", head)

    def test_all_failed_has_no_numeric_summary_but_keeps_diagnostics(self):
        results = [
            self._result(1, "failed", {"vout": 9.0, "iout": 8.0},
                         "fatal diagnostic: analysis aborted"),
            self._result(2, "failed", {"vout": 7.0}, "missing measurements: iout",
                         missing=["iout"]),
        ]
        record, text = self._text(results)
        self.assertEqual(record["samples"], {"vout": [], "iout": []})
        self.assertIn("- `vout`: no successful-run data (0 of 2 runs succeeded)", text)
        self.assertNotIn("all runs failed to converge", text)
        self.assertNotIn("mean", text)
        self.assertIn("analysis error", text)
        self.assertIn("missing measurements", text)
        self.assertIn("fatal diagnostic: analysis aborted", text)
        self.assertIn("  - `vout`: 7", text)

    def test_all_success_keeps_existing_numeric_format(self):
        results = [self._result(i, "ok", {"vout": v, "iout": 1.0})
                   for i, v in ((1, 1.0), (2, 3.0))]
        record, text = self._text(results)
        self.assertIn("- `vout`: mean 2 over 2 seeds (sd 1.41421, 70.7% of mean; min 1, max 3)", text)
        self.assertIn("Runs: 2 of 2 successful", text)
        self.assertNotIn("Failed-run diagnostics", text)
        self.assertNotIn("Run failures", text)

    def test_timeout_without_measurements_has_no_diagnostics_block(self):
        results = [self._result(1, "ok", {"vout": 1.0, "iout": 1.0}),
                   self._result(2, "timeout", {}, "ngspice timed out")]
        _, text = self._text(results)
        self.assertIn("Runs: 1 of 2 successful", text)
        self.assertIn("seed 2: timeout", text)
        self.assertNotIn("Failed-run diagnostics", text)

    def test_missing_measurement_on_failed_seed_keeps_counts_consistent(self):
        results = [self._result(1, "ok", {"vout": 1.0, "iout": 2.0}),
                   self._result(2, "ok", {"vout": 3.0, "iout": 2.0}),
                   self._result(3, "failed", {"vout": 50.0}, "missing measurements: iout",
                                missing=["iout"])]
        record, text = self._text(results)
        self.assertEqual(len(record["samples"]["vout"]), len(record["samples"]["iout"]))
        self.assertIn("mean 2 over 2 seeds", text)
        self.assertIn("Runs: 2 of 3 successful", text)

    def test_run_one_retained_fatal_diagnostic_with_all_measurements(self):
        # run_one marks a run failed on a fatal diagnostic even when every
        # requested measurement was parsed; those values must stay diagnostic.
        results = [self._result(1, "failed", {"vout": 9.0, "iout": 8.0},
                                "Error: timestep too small")]
        record, text = self._text(results)
        self.assertEqual(record["runs_ok"], 0)
        self.assertEqual(record["runs_attempted"], 1)
        self.assertIn("no successful-run data", text)
        self.assertIn("  - `iout`: 8", text)

    def test_mixed_campaign_with_overflowed_seed_keeps_only_finite_seed(self):
        # Issue #527: real runner.run_one against a fake ngspice that prints
        # finite values for seed 1 and an overflowing `1e999` for seed 2.
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        fake = bin_dir / "ngspice"
        fake.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "deck = open(sys.argv[-1]).read()\n"
            "if '.option seed=2' in deck:\n"
            "    print('m_vout = 1e999')\n"
            "    print('m_iout = 4.0e-6')\n"
            "else:\n"
            "    print('m_vout = 1.5')\n"
            "    print('m_iout = 2.0e-6')\n"
        )
        fake.chmod(0o755)
        env = mock.patch.dict(
            os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"}
        )
        env.start()
        self.addCleanup(env.stop)

        results = [
            runner.run_one(self.tb, self.pdk, self.point, self.raw_dir,
                           seed=seed, run_index=i, timeout_s=5)
            for i, seed in enumerate((1, 2))
        ]
        self.assertEqual([r.status for r in results], ["ok", "failed"])
        bad = results[1]

        record, text = self._text(results)
        self.assertEqual(record["samples"], {"vout": [1.5], "iout": [2.0e-6]})
        self.assertEqual(record["runs_ok"], 1)
        self.assertEqual(record["runs_attempted"], 2)
        self.assertIn("Runs: 1 of 2 successful", text)
        self.assertNotIn("`vout`: inf", text)
        self.assertIn("seed 2: failed -- non-finite measurements: vout", text)
        # The finite value from the failed seed stays diagnostic-only.
        head, _, diag = text.partition("Failed-run diagnostics")
        self.assertIn("  - `iout`: 4.000000e-06", diag)
        self.assertNotIn("4.000000e-06", head)
        # The invalid seed's raw log is preserved and checksummed.
        log = self.raw_dir / bad.log_name
        self.assertIn("m_vout = 1e999", log.read_text())
        self.assertIn(bad.log_name, [name for name, _ in record["raw_files"]])

    def test_consumer_regex_still_matches_mean_lines(self):
        import re
        results = [self._result(i, "ok", {"vout": float(i), "iout": 1.0}) for i in (1, 2)]
        _, text = self._text(results)
        self.assertTrue(any(re.match(r"^- `(\w+)`: mean (\S+) over", l) for l in text.splitlines()))


class ChangedRecordDiscoveryTests(unittest.TestCase):
    """`verify_record_checksums.py --changed` must find the records it lists.

    `git diff --name-only` prints paths from the REPO ROOT no matter which
    directory it is invoked in, so joining its output onto `sim/` produced
    `sim/sim/records/...` and every changed record failed as "no such
    record" -- turning the pre-commit command sim/README.md mandates into a
    check that could only ever fail once a branch actually added a record.
    """

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
        import verify_record_checksums as vrc  # noqa: PLC0415

        self.vrc = vrc

    def test_git_output_is_joined_onto_the_repo_root_not_sim(self):
        """`git diff --name-only` output is repo-root-relative, always."""
        printed = "sim/records/2026-01-01-an-experiment-01.md\n"
        real_run = subprocess.run

        def fake_run(argv, **kwargs):
            if argv[:2] == ["git", "diff"]:
                return subprocess.CompletedProcess(argv, 0, stdout=printed, stderr="")
            return real_run(argv, **kwargs)

        self.vrc.subprocess.run = fake_run
        self.addCleanup(setattr, self.vrc.subprocess, "run", real_run)

        paths = self.vrc._changed_records("origin/main")
        self.assertEqual(
            paths, [self.vrc.REPO_ROOT / "sim/records/2026-01-01-an-experiment-01.md"]
        )
        self.assertNotIn("sim/sim/", str(paths[0]))

    def test_changed_records_that_exist_are_reported_as_existing(self):
        """End-to-end against the real repo: whatever this branch added must
        resolve to files on disk, never to a doubled `sim/sim/...` path."""
        for path in self.vrc._changed_records("origin/main"):
            with self.subTest(path=str(path)):
                self.assertTrue(path.is_file(), f"discovered a path that does not exist: {path}")

    def test_nonzero_git_result_raises_naming_the_base(self):
        real_run = subprocess.run

        def fake_run(argv, **kwargs):
            if argv[:2] == ["git", "diff"]:
                return subprocess.CompletedProcess(
                    argv, 128, stdout="", stderr="fatal: bad revision 'nope...HEAD'\n")
            return real_run(argv, **kwargs)

        self.vrc.subprocess.run = fake_run
        self.addCleanup(setattr, self.vrc.subprocess, "run", real_run)
        with self.assertRaises(self.vrc.ChangedDiscoveryError) as ctx:
            self.vrc._changed_records("nope")
        self.assertIn("nope", str(ctx.exception))
        self.assertIn("128", str(ctx.exception))
        self.assertIn("bad revision", str(ctx.exception))

    def _git(self, repo, *args):
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.com",
             "-c", "commit.gpgsign=false", *args],
            cwd=repo, check=True, capture_output=True, text=True)

    def _temp_repo(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        repo = Path(tmp.name)
        self._git(repo, "init", "-q", "-b", "main")
        (repo / "sim" / "records").mkdir(parents=True)
        (repo / "sim" / "records" / ".keep").write_text("")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", "base")
        for name, value in (("SIM_DIR", repo / "sim"), ("REPO_ROOT", repo)):
            old = getattr(self.vrc, name)
            setattr(self.vrc, name, value)
            self.addCleanup(setattr, self.vrc, name, old)
        return repo

    def _run_cli(self, argv):
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = self.vrc.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_cli_fails_closed_on_unknown_base(self):
        self._temp_repo()
        rc, out, err = self._run_cli(["--changed", "nonexistent-base"])
        self.assertNotEqual(rc, 0)
        self.assertIn("nonexistent-base", err)
        self.assertNotIn("no records to check", out)

    def test_cli_fails_closed_on_missing_base_history(self):
        self._temp_repo()
        # A base that names an object this clone does not have.
        rc, out, err = self._run_cli(["--changed", "0123456789abcdef0123456789abcdef01234567"])
        self.assertNotEqual(rc, 0)
        self.assertIn("0123456789abcdef", err)
        self.assertNotIn("no records to check", out)

    def test_cli_fails_closed_on_unrelated_histories(self):
        repo = self._temp_repo()
        self._git(repo, "checkout", "-q", "--orphan", "other")
        (repo / "other.txt").write_text("x\n")  # sim/records stays on disk
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", "unrelated")
        rc, out, err = self._run_cli(["--changed", "main"])
        self.assertNotEqual(rc, 0)
        self.assertIn("'main'", err)
        self.assertNotIn("no records to check", out)

    def test_valid_base_with_empty_diff_succeeds(self):
        repo = self._temp_repo()
        (repo / "README").write_text("not a record\n")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", "no record")
        rc, out, err = self._run_cli(["--changed", "HEAD~1"])
        self.assertEqual(rc, 0, err)
        self.assertIn("no records to check", out)

    def test_valid_base_with_added_record_is_discovered(self):
        repo = self._temp_repo()
        rec = repo / "sim" / "records" / "2026-01-01-x-01.md"
        rec.write_text("# record\n")
        self._git(repo, "add", "-A")
        self._git(repo, "commit", "-q", "-m", "add record")
        paths = self.vrc._changed_records("HEAD~1")
        self.assertEqual([p.resolve() for p in paths], [rec.resolve()])


class RawFileVerificationTests(unittest.TestCase):
    """A record whose raw output changed after it was hashed is not evidence.

    Regression coverage for #60: a second concurrent run_corners.py
    invocation, handed an overlapping stem, overwrote raw files that the
    first run had already hashed into its record -- and the harness wrote a
    `status: valid` record with checksums matching nothing and exited OK.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        tb_dir = root / "tb" / "an-experiment"
        tb_dir.mkdir(parents=True)
        (tb_dir / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (tb_dir / "tb.json").write_text(
            json.dumps({"name": "an-experiment", "netlist": "x.spice", "measure": {"vout": "v(out)"}})
        )
        self.tb = testbench.load(tb_dir)
        self.pdk = fake_pdk(root / "gf180mcuD")
        self.point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]
        self.raw_dir = root / "records" / "raw" / "2026-07-31-an-experiment-01"
        self.raw_dir.mkdir(parents=True)
        self.deck = self.raw_dir / "tt_27c_3.30v.spice"
        self.log = self.raw_dir / "tt_27c_3.30v.log"
        self.deck.write_text("* deck from the first invocation\n")
        self.log.write_text("m_vout = 1.65\n")
        self.results = [
            runner.RunResult(
                point=self.point, seed=None, status="ok", measurements={"vout": 1.65},
                deck_name=self.deck.name, log_name=self.log.name,
            )
        ]
        self.records_dir = root / "records"
        self.record = self._build("2026-07-31-an-experiment-01")

    def _build(self, stem: str) -> dict:
        return report.build_record(
            tb=self.tb, pdk=self.pdk, point=self.point, results=self.results,
            ngspice="ngspice-46", repo_root=Path(self.tmp.name), stem=stem,
            completed_utc=_dt.datetime(2026, 7, 31, 12, 0, 0, tzinfo=_dt.timezone.utc),
            wall_seconds=1.3, raw_dir=self.raw_dir,
            git={"commit": "f" * 40, "dirty": False},
        )

    def test_untouched_record_verifies(self):
        self.assertEqual(report.verify_record(self.record), [])

    def test_overwritten_raw_file_is_detected(self):
        self.deck.write_text("* deck from a SECOND invocation\n")
        problems = report.verify_record(self.record)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("tt_27c_3.30v.spice", problems[0])
        self.assertIn("sha256 on disk", problems[0])

    def test_missing_raw_file_is_detected(self):
        self.log.unlink()
        problems = report.verify_record(self.record)
        self.assertTrue(any("not present" in p for p in problems), problems)

    def test_unlisted_raw_file_is_detected(self):
        # Another run's deck landing in this record's raw directory: the
        # record's numbers and that file have nothing to do with each other.
        (self.raw_dir / "ss_125c_2.97v.spice").write_text("* another run's deck\n")
        problems = report.verify_record(self.record)
        self.assertTrue(any("absent from raw.files" in p for p in problems), problems)

    def test_write_record_refuses_a_record_that_is_already_wrong(self):
        """Collision between build_record() and write_record()."""
        self.deck.write_text("* clobbered between hashing and writing\n")
        with self.assertRaises(report.RawFilesMismatch) as caught:
            report.write_record(self.record, self.tb, self.records_dir, ["a caveat"])
        self.assertIn("tt_27c_3.30v.spice", str(caught.exception))
        # Nothing was written: a record that is wrong at birth never lands.
        self.assertFalse((self.records_dir / "2026-07-31-an-experiment-01.md").exists())

    def _dest(self) -> Path:
        return self.records_dir / "2026-07-31-an-experiment-01.md"

    def test_existing_destination_takes_precedence_over_raw_mismatch(self):
        # Exception precedence: the early existence check still fires before
        # raw verification, so a collision is reported as RecordExists.
        self.deck.write_text("* clobbered between hashing and writing\n")
        sentinel = b"independent record\n"
        self._dest().write_bytes(sentinel)
        with self.assertRaises(report.RecordExists):
            report.write_record(self.record, self.tb, self.records_dir, ["a caveat"])
        self.assertEqual(self._dest().read_bytes(), sentinel)

    def test_destination_created_after_the_early_check_is_not_overwritten(self):
        # Deterministic stand-in for a concurrent writer: the sentinel lands
        # after write_record's existence check and raw verification (inside
        # rendering), before publication. Exclusive creation must refuse it.
        sentinel = b"record published by another writer\n"
        real_render = report.render_record

        def render_then_collide(*args, **kwargs):
            text = real_render(*args, **kwargs)
            self._dest().write_bytes(sentinel)
            return text

        with mock.patch.object(report, "render_record", side_effect=render_then_collide):
            with self.assertRaises(report.RecordExists):
                report.write_record(self.record, self.tb, self.records_dir, ["a caveat"])
        self.assertEqual(self._dest().read_bytes(), sentinel)

    def test_failed_publication_write_leaves_no_partial_record(self):
        real_open = open

        class FailingHandle:
            def __init__(self, handle):
                self._handle = handle

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                self._handle.close()
                return False

            def write(self, text):
                # Leave a genuinely partial file before failing.
                self._handle.write(text[: len(text) // 2])
                self._handle.flush()
                raise OSError("simulated disk full")

        opened = []

        def failing_open(path, mode="r", *args, **kwargs):
            handle = real_open(path, mode, *args, **kwargs)
            if mode == "x":
                opened.append(Path(path))
                return FailingHandle(handle)
            return handle

        with mock.patch.object(report, "open", side_effect=failing_open, create=True):
            with self.assertRaisesRegex(OSError, "simulated disk full"):
                report.write_record(self.record, self.tb, self.records_dir, ["a caveat"])
        self.assertEqual(opened, [self._dest()])
        self.assertFalse(self._dest().exists())
        # The stem is free again: a retry publishes the full record.
        path = report.write_record(self.record, self.tb, self.records_dir, ["a caveat"])
        self.assertEqual(path.read_text(), report.render_record(self.record, self.tb, ["a caveat"]))

    def test_refused_publication_never_removes_an_existing_destination(self):
        # publish_record_text cleans up only a file it created itself; a
        # refused exclusive open must not unlink the destination.
        sentinel = b"independent record\n"
        self._dest().parent.mkdir(parents=True, exist_ok=True)
        self._dest().write_bytes(sentinel)
        with self.assertRaises(report.RecordExists):
            report.publish_record_text(self._dest(), "replacement\n")
        self.assertEqual(self._dest().read_bytes(), sentinel)

    def test_written_record_can_be_re_verified_from_disk(self):
        path = report.write_record(self.record, self.tb, self.records_dir, ["a caveat"])
        self.assertEqual(report.verify_record_file(path, Path(self.tmp.name)), [])
        # Now simulate the late clobber -- the record is on disk and looks
        # valid, but the raw output underneath it has been replaced.
        self.log.write_text("m_vout = 9.99\n")
        problems = report.verify_record_file(path, Path(self.tmp.name))
        self.assertTrue(any("tt_27c_3.30v.log" in p for p in problems), problems)

    def test_parse_raw_section_round_trips_the_renderer(self):
        text = report.render_record(self.record, self.tb, ["a caveat"])
        raw_path, files = report.parse_raw_section(text)
        self.assertEqual(raw_path, self.record["raw_path"])
        self.assertEqual(files, list(self.record["raw_files"]))

    # --- malformed raw provenance (#369) -----------------------------------

    def _write_text_record(self, text):
        path = Path(self.tmp.name) / "bad-record.md"
        path.write_text(text)
        return path

    def _good_text(self):
        return report.render_record(self.record, self.tb, ["a caveat"])

    def _entry_line(self):
        return next(l for l in self._good_text().splitlines() if l.startswith("    - ") and "sha256:" in l)

    def test_body_only_raw_section_is_not_accepted(self):
        text = "---\nrecord: x\nwall_time: 1\n---\n\n```\n" + "\n".join(
            report.render_frontmatter(self.record).splitlines()[1:-1]
        ) + "\n```\n"
        self.assertEqual(report.parse_raw_section(text), ("", []))
        problems = report.verify_record_file(self._write_text_record(text), Path(self.tmp.name))
        self.assertTrue(any("no raw.path" in p for p in problems), problems)

    def test_no_frontmatter_ignores_raw_in_body(self):
        text = "\n".join(self._good_text().splitlines()[1:])
        self.assertEqual(report.parse_raw_section(text), ("", []))

    def test_unterminated_frontmatter_raises(self):
        lines = self._good_text().splitlines()
        text = "\n".join(lines[: lines.index("---", 1)])
        with self.assertRaises(report.RawSectionError):
            report.parse_raw_section(text)
        problems = report.verify_record_file(self._write_text_record(text), Path(self.tmp.name))
        self.assertTrue(any("malformed raw provenance" in p for p in problems), problems)

    def test_duplicate_raw_declarations_raise(self):
        text = self._good_text()
        dup_raw = text.replace("wall_time:", "raw:\n  path: elsewhere\n  files:\nwall_time:", 1)
        with self.assertRaises(report.RawSectionError):
            report.parse_raw_section(dup_raw)
        dup_path = text.replace("  files:", "  path: elsewhere\n  files:", 1)
        with self.assertRaises(report.RawSectionError):
            report.parse_raw_section(dup_path)
        dup_files = text.replace("wall_time:", "  files:\nwall_time:", 1)
        with self.assertRaises(report.RawSectionError):
            report.parse_raw_section(dup_files)

    def test_valid_checksum_then_malformed_checksum_fails(self):
        text = self._good_text()
        entry = self._entry_line()
        for bad in ("    - ghost-not-on-disk.spice  sha256:abc123",
                    "    - ghost-not-on-disk.spice",
                    "    garbage"):
            with self.subTest(bad=bad):
                broken = text.replace(entry, entry + "\n" + bad, 1)
                with self.assertRaises(report.RawSectionError):
                    report.parse_raw_section(broken)
                problems = report.verify_record_file(
                    self._write_text_record(broken), Path(self.tmp.name))
                self.assertTrue(problems)

    def test_invalid_first_checksum_not_replaced_by_body_example(self):
        text = self._good_text()
        entry = self._entry_line()
        broken = text.replace(entry, "    - first.spice  sha256:zzz", 1)
        broken += "\n" + "\n".join(text.splitlines()[1:text.splitlines().index("---", 1)]) + "\n"
        with self.assertRaises(report.RawSectionError):
            report.parse_raw_section(broken)


class VerifyRecordChecksumsCliTests(unittest.TestCase):
    """The verify_record_checksums.py entry point on malformed evidence."""

    def test_cli_exits_nonzero_naming_record_without_traceback(self):
        script = Path(__file__).resolve().parents[1] / "tools" / "verify_record_checksums.py"
        with tempfile.TemporaryDirectory() as tmp:
            rec = Path(tmp) / "2026-01-01-malformed-01.md"
            rec.write_text("---\nrecord: x\nraw:\n  path: a/b\n  files:\n"
                           "    - f.log  sha256:nothex\n---\n")
            proc = subprocess.run(
                [sys.executable, str(script), "--no-git", str(rec)],
                capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("2026-01-01-malformed-01.md", proc.stderr)
        self.assertIn("malformed raw provenance", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


class StochasticRecordTests(unittest.TestCase):
    """Multiple seeded runs at one PVT point aggregate into ONE record."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        tb_dir = root / "tb" / "mc-demo"
        tb_dir.mkdir(parents=True)
        (tb_dir / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (tb_dir / "tb.json").write_text(
            json.dumps(
                {
                    "name": "mc-demo", "netlist": "x.spice", "measure": {"id": "-i(vdd)"},
                    "analysis_type": "mc", "default_runs": 2,
                }
            )
        )
        self.tb = testbench.load(tb_dir)
        self.pdk = fake_pdk(root / "gf180mcuD")
        self.point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]
        raw_dir = root / "raw"
        raw_dir.mkdir()
        self.results = []
        for i, (seed, value) in enumerate([(1, 2.7e-4), (2, 2.8e-4)]):
            deck = f"tt_27c_3.30v-run{i}.spice"
            log = f"tt_27c_3.30v-run{i}.log"
            (raw_dir / deck).write_text("* deck\n")
            (raw_dir / log).write_text(f"m_id = {value}\n")
            self.results.append(
                runner.RunResult(
                    point=self.point, seed=seed, status="ok", measurements={"id": value},
                    deck_name=deck, log_name=log,
                )
            )
        self.record = report.build_record(
            tb=self.tb, pdk=self.pdk, point=self.point, results=self.results,
            ngspice="ngspice-46", repo_root=root, stem="2026-07-31-mc-demo-01",
            completed_utc=_dt.datetime(2026, 7, 31, 12, 0, 0, tzinfo=_dt.timezone.utc),
            wall_seconds=2.6, raw_dir=raw_dir,
            git={"commit": "f" * 40, "dirty": False},
        )

    def test_seeds_are_listed_in_run_order(self):
        text = report.render_frontmatter(self.record)
        self.assertIn("seeds: [1, 2]", text)

    def test_analysis_runs_matches_seed_count(self):
        text = report.render_frontmatter(self.record)
        self.assertIn("runs: 2", text)

    def test_result_reports_mean_and_spread(self):
        text = report.render_result_section(self.record)
        self.assertIn("`id`: mean", text)
        self.assertIn("over 2 seeds", text)


class ManifestSnapshotTests(unittest.TestCase):
    """The loaded tb.json is snapshotted and checksummed with the raw output
    (#510). No PDK or ngspice involved."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tb_dir = self.root / "tb" / "an-experiment"
        self.tb_dir.mkdir(parents=True)
        (self.tb_dir / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        self.pdk = fake_pdk(self.root / "gf180mcuD")
        self.point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]

    def _record(self, measure_expr: str, stem: str) -> dict:
        (self.tb_dir / "tb.json").write_text(json.dumps(
            {"name": "an-experiment", "netlist": "x.spice", "measure": {"vout": measure_expr}}
        ))
        tb = testbench.load(self.tb_dir)
        raw_dir = self.root / "records" / "raw" / stem
        raw_dir.mkdir(parents=True)
        (raw_dir / "d.spice").write_text("* deck\n")
        (raw_dir / "d.log").write_text("m_vout = 1\n")
        results = [runner.RunResult(
            point=self.point, seed=None, status="ok", measurements={"vout": 1.0},
            deck_name="d.spice", log_name="d.log",
        )]
        record = report.build_record(
            tb=tb, pdk=self.pdk, point=self.point, results=results,
            ngspice="ngspice-46", repo_root=self.root, stem=stem,
            completed_utc=_dt.datetime(2026, 7, 31, 12, 0, 0, tzinfo=_dt.timezone.utc),
            wall_seconds=1.0, raw_dir=raw_dir, git={"commit": "f" * 40, "dirty": True},
        )
        self.tb = tb
        return record

    def test_manifest_only_change_is_distinguishable(self):
        a = self._record("v(out)", "2026-07-31-an-experiment-01")
        b = self._record("v(out)*2", "2026-07-31-an-experiment-02")
        self.assertEqual(a["testbench_sha"], b["testbench_sha"])  # same fragment
        self.assertNotEqual(a["manifest_sha256"], b["manifest_sha256"])
        self.assertIn(f"sha256: {a['manifest_sha256']}", report.render_frontmatter(a))
        self.assertIn(f"sha256: {b['manifest_sha256']}", report.render_frontmatter(b))

    def test_snapshot_holds_loaded_bytes_and_is_checksummed(self):
        rec = self._record("v(out)", "2026-07-31-an-experiment-01")
        snap = Path(rec["raw_dir"]) / report.MANIFEST_SNAPSHOT_NAME
        self.assertEqual(snap.read_bytes(), (self.tb_dir / "tb.json").read_bytes())
        self.assertIn((report.MANIFEST_SNAPSHOT_NAME, rec["manifest_sha256"]), rec["raw_files"])
        self.assertEqual(report.verify_record(rec), [])

    def test_snapshot_is_the_loaded_config_not_a_later_edit(self):
        rec = self._record("v(out)", "2026-07-31-an-experiment-01")
        original = self.tb.manifest_bytes
        (self.tb_dir / "tb.json").write_text("{}")
        again = report.snapshot_manifest(self.tb, Path(rec["raw_dir"]))
        self.assertEqual((Path(rec["raw_dir"]) / again[0]).read_bytes(), original)

    def test_changed_snapshot_is_detected_on_disk(self):
        rec = self._record("v(out)", "2026-07-31-an-experiment-01")
        records_dir = self.root / "records"
        path = report.write_record(rec, self.tb, records_dir, ["c"])
        self.assertEqual(report.verify_record_file(path, self.root), [])
        (Path(rec["raw_dir"]) / report.MANIFEST_SNAPSHOT_NAME).write_text("{}")
        problems = report.verify_record_file(path, self.root)
        self.assertTrue(any(report.MANIFEST_SNAPSHOT_NAME in p for p in problems), problems)

    def test_manifest_digest_must_match_raw_files_entry(self):
        rec = self._record("v(out)", "2026-07-31-an-experiment-01")
        text = report.render_frontmatter(rec).replace(rec["manifest_sha256"], "0" * 64, 1)
        problems = report.verify_manifest_reference(text, rec["raw_files"])
        self.assertEqual(len(problems), 1, problems)

    def test_manifest_edited_during_load_is_rejected(self):
        self._record("v(out)", "2026-07-31-an-experiment-01")
        real = testbench.validate_netlist

        def edit_then_validate(tb):
            (self.tb_dir / "tb.json").write_text(json.dumps({"changed": 1}))
            real(tb)

        with mock.patch.object(testbench, "validate_netlist", edit_then_validate):
            with self.assertRaises(ValueError):
                testbench.load(self.tb_dir)

    def test_legacy_record_without_manifest_block_is_readable(self):
        rec = self._record("v(out)", "2026-07-31-an-experiment-01")
        legacy = dict(rec, manifest_snapshot="", manifest_sha256="", manifest_sha="")
        legacy["raw_files"] = [f for f in rec["raw_files"] if f[0] != report.MANIFEST_SNAPSHOT_NAME]
        (Path(rec["raw_dir"]) / report.MANIFEST_SNAPSHOT_NAME).unlink()
        text = report.render_frontmatter(legacy)
        self.assertNotIn("manifest:", text)
        self.assertEqual(report.parse_manifest_section(text), {})
        self.assertEqual(report.verify_manifest_reference(text, legacy["raw_files"]), [])
        self.assertEqual(report.verify_record(legacy), [])
        path = report.write_record(legacy, self.tb, self.root / "records", ["c"])
        self.assertEqual(report.verify_record_file(path, self.root), [])


class InputSnapshotTests(unittest.TestCase):
    """The SPICE fragment and DUT netlist are captured once at load, frozen
    into each corner's directory, and hashed from those same bytes (#515).
    No PDK and no ngspice involved."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tb_dir = self.root / "tb" / "an-experiment"
        self.tb_dir.mkdir(parents=True)
        self.frag = self.tb_dir / "x.spice"
        self.dut = self.root / "dut.spice"
        self.frag.write_text("v1 out 0 dc {vdd_val}\n")
        self.dut.write_text(".subckt cell a b\nr1 a b 1k\n.ends\n")
        (self.tb_dir / "tb.json").write_text(json.dumps({
            "name": "an-experiment", "netlist": "x.spice",
            "design_netlist": str(self.dut), "measure": {"vout": "v(out)"},
        }))
        self.pdk = fake_pdk(self.root / "gf180mcuD")
        self.tb = testbench.load(self.tb_dir)
        self.point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]
        self.orig_frag = self.frag.read_bytes()
        self.orig_dut = self.dut.read_bytes()

    def _run_corner(self, stem: str) -> dict:
        raw_dir = self.root / "records" / "raw" / stem
        raw_dir.mkdir(parents=True)
        (raw_dir / "d.spice").write_text("* deck\n")
        (raw_dir / "d.log").write_text("m_vout = 1\n")
        testbench.write_input_snapshots(self.tb, raw_dir)
        results = [runner.RunResult(
            point=self.point, seed=None, status="ok", measurements={"vout": 1.0},
            deck_name="d.spice", log_name="d.log",
        )]
        return report.build_record(
            tb=self.tb, pdk=self.pdk, point=self.point, results=results,
            ngspice="ngspice-46", repo_root=self.root, stem=stem,
            completed_utc=_dt.datetime(2026, 7, 31, 12, 0, 0, tzinfo=_dt.timezone.utc),
            wall_seconds=1.0, raw_dir=raw_dir, git={"commit": "f" * 40, "dirty": True},
        )

    def test_hashes_are_of_captured_bytes_even_after_edit(self):
        self.frag.write_text("v1 out 0 dc 99\n")
        self.dut.write_text("* changed\n")
        rec = self._run_corner("2026-07-31-an-experiment-01")
        self.assertEqual(rec["testbench_sha"], report._git_blob_sha1(self.orig_frag))
        self.assertEqual(rec["netlist_sha"], report._git_blob_sha1(self.orig_dut))
        raw = Path(rec["raw_dir"])
        self.assertEqual((raw / testbench.FRAGMENT_SNAPSHOT_NAME).read_bytes(), self.orig_frag)
        self.assertEqual((raw / testbench.DUT_SNAPSHOT_NAME).read_bytes(), self.orig_dut)
        names = {n for n, _ in rec["raw_files"]}
        self.assertLessEqual(
            {testbench.FRAGMENT_SNAPSHOT_NAME, testbench.DUT_SNAPSHOT_NAME}, names
        )
        self.assertEqual(report.verify_record(rec), [])

    def test_frontmatter_block_and_verification(self):
        rec = self._run_corner("2026-07-31-an-experiment-01")
        text = report.render_frontmatter(rec)
        self.assertIn("inputs:", text)
        path = report.write_record(rec, self.tb, self.root / "records", ["c"])
        self.assertEqual(report.verify_record_file(path, self.root), [])
        bad = path.read_text().replace(rec["testbench_sha256"], "0" * 64, 1)
        problems = report.verify_inputs_reference(bad, rec["raw_files"])
        self.assertEqual(len(problems), 1, problems)

    def test_mutated_snapshot_is_detected(self):
        rec = self._run_corner("2026-07-31-an-experiment-01")
        path = report.write_record(rec, self.tb, self.root / "records", ["c"])
        (Path(rec["raw_dir"]) / testbench.DUT_SNAPSHOT_NAME).write_text("* tampered\n")
        problems = report.verify_record_file(path, self.root)
        self.assertTrue(any(testbench.DUT_SNAPSHOT_NAME in p for p in problems), problems)

    def test_snapshot_mutated_before_record_is_refused(self):
        raw_dir = self.root / "records" / "raw" / "s"
        testbench.write_input_snapshots(self.tb, raw_dir)
        (raw_dir / testbench.FRAGMENT_SNAPSHOT_NAME).write_text("* tampered\n")
        with self.assertRaisesRegex(RuntimeError, "modified during the run"):
            testbench.write_input_snapshots(self.tb, raw_dir)

    def test_legacy_record_without_inputs_block_is_unchanged(self):
        rec = self._run_corner("2026-07-31-an-experiment-01")
        for key in ("testbench_sha256", "testbench_snapshot", "netlist_sha256", "netlist_snapshot"):
            rec[key] = ""
        self.assertNotIn("inputs:", report.render_frontmatter(rec))
        self.assertEqual(report.verify_inputs_reference("---\nrecord: x\n---\n", []), [])

    def test_dut_dependencies_are_snapshotted_hashed_and_verified(self):
        (self.root / "extra.spice").write_text("* extra original\n")
        self.dut.write_text('.include "extra.spice"\n.subckt cell a b\n.ends\n')
        self.tb = testbench.load(self.tb_dir)
        (self.root / "extra.spice").write_text("* extra MUTATED\n")
        rec = self._run_corner("2026-07-31-an-experiment-01")
        raw = Path(rec["raw_dir"])
        self.assertEqual((raw / "extra.spice").read_text(), "* extra original\n")
        self.assertIn("extra.spice", dict(rec["raw_files"]))
        self.assertEqual(report.verify_record(rec), [])
        text = report.render_frontmatter(rec)
        self.assertIn("netlist_dependencies: extra.spice", text)
        self.assertEqual(report.verify_inputs_reference(text, rec["raw_files"]), [])
        self.assertEqual(
            len(report.verify_inputs_reference(text, [r for r in rec["raw_files"] if r[0] != "extra.spice"])), 1
        )
        (raw / "extra.spice").write_text("* tampered\n")
        self.assertTrue(any("extra.spice" in p for p in report.verify_record(rec)))

    def test_hand_built_testbench_falls_back_to_live_files(self):
        tb = testbench.Testbench(directory=self.tb_dir, slug="h", netlist=self.frag)
        self.assertEqual(testbench.write_input_snapshots(tb, self.root / "o"), [])
        self.assertEqual(tb.input_snapshots(), [])


if __name__ == "__main__":
    unittest.main()
