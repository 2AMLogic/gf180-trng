#!/usr/bin/env python3
"""Unit tests for sim/harness/report.py -- the append-only evidence-record
writer conforming to sim/README.md."""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import sys
import tempfile
import unittest
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

    def test_different_slugs_do_not_collide(self):
        with tempfile.TemporaryDirectory() as tmp:
            records_dir = Path(tmp)
            (records_dir / "2026-08-14-alpha-01.md").write_text("x")
            stem = report.allocate_record_stem(records_dir, "2026-08-14", "beta")
            self.assertEqual(stem, "2026-08-14-beta-01")


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

    def test_write_record_refuses_to_overwrite(self):
        records_dir = Path(self.tmp.name) / "records"
        path = report.write_record(self.record, self.tb, records_dir, ["a caveat"])
        self.assertTrue(path.is_file())
        with self.assertRaises(report.RecordExists):
            report.write_record(self.record, self.tb, records_dir, ["a caveat"])


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


if __name__ == "__main__":
    unittest.main()
