#!/usr/bin/env python3
"""Unit tests for sim/characterize.py -- the `make characterize` driver
(issue #203). No PDK/ngspice needed: these exercise the campaign table and
--dry-run/--rows selection, not the ngspice runs themselves."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR))

import characterize  # noqa: E402


class CampaignTableTests(unittest.TestCase):
    def test_every_campaign_has_at_least_one_row(self):
        for c in characterize.CAMPAIGNS:
            self.assertTrue(c.rows, f"{c.testbench} declares no rows")

    def test_every_campaign_testbench_exists(self):
        tb_dir = SIM_DIR / "tb"
        for c in characterize.CAMPAIGNS:
            manifest = tb_dir / c.testbench / "tb.json"
            self.assertTrue(
                manifest.is_file(), f"{c.testbench}: no {manifest} (stale campaign entry?)"
            )

    def test_command_includes_jobs_and_testbench(self):
        c = characterize.CAMPAIGNS[0]
        cmd = c.command(jobs=4)
        self.assertIn(c.testbench, cmd)
        self.assertIn("--jobs", cmd)
        self.assertIn("4", cmd)

    def test_fully_uncovered_rows_absent_from_campaign_rows(self):
        # ROWS_NOT_COVERED documents rows (or row *terms*, e.g. "D (digital
        # term)") this script does not produce evidence for. A row with no
        # "(...)" qualifier is claimed fully uncovered and must not also
        # appear on a Campaign; a qualified entry (D/E's digital term) is
        # deliberately partial -- the analog term of the same row letter IS
        # covered -- so it is exempt from this check.
        covered = {r for c in characterize.CAMPAIGNS for r in c.rows}
        for row in characterize.ROWS_NOT_COVERED:
            if "(" in row:
                continue
            self.assertNotIn(
                row, covered,
                f"row {row!r} is claimed both covered (by a Campaign) and not covered",
            )


class SelectTests(unittest.TestCase):
    def test_no_filter_returns_everything(self):
        self.assertEqual(characterize._select(None), list(characterize.CAMPAIGNS))
        self.assertEqual(characterize._select([]), list(characterize.CAMPAIGNS))

    def test_filter_by_row_letter(self):
        selected = characterize._select(["F"])
        self.assertTrue(selected)
        for c in selected:
            self.assertIn("F", c.rows)

    def test_filter_is_case_insensitive(self):
        self.assertEqual(characterize._select(["f"]), characterize._select(["F"]))

    def test_unknown_row_raises(self):
        with self.assertRaises(SystemExit):
            characterize._select(["ZZ"])


class DryRunSubprocessTests(unittest.TestCase):
    """No PDK/ngspice required -- --dry-run never touches either."""

    def test_dry_run_lists_every_campaign_testbench(self):
        result = subprocess.run(
            [sys.executable, str(SIM_DIR / "characterize.py"), "--dry-run", "--jobs", "2"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for c in characterize.CAMPAIGNS:
            self.assertIn(c.testbench, result.stdout)
        self.assertIn("run_corners.py", result.stdout)
        # rows this script does not cover should be surfaced too
        for row in characterize.ROWS_NOT_COVERED:
            self.assertIn(row, result.stdout)

    def test_dry_run_with_rows_filter_excludes_other_campaigns(self):
        result = subprocess.run(
            [sys.executable, str(SIM_DIR / "characterize.py"), "--dry-run", "--rows", "F"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ro-array-core-startup", result.stdout)
        self.assertNotIn("sampler-array-digitize", result.stdout)


if __name__ == "__main__":
    unittest.main()
