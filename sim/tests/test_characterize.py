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

sys.path.insert(0, str(SIM_DIR / "tools"))

import characterize  # noqa: E402
import power_rollup  # noqa: E402


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


class RowCCornerTests(unittest.TestCase):
    """Row C must cover every corner a real bitstream exists for (#436)."""

    @staticmethod
    def _corner(c):
        args = c.extra_args
        return (
            args[args.index("--corners") + 1],
            args[args.index("--temps") + 1],
            args[args.index("--supply") + 1],
        )

    def test_row_c_is_exactly_the_three_bitstream_corners(self):
        got = {
            self._corner(c)
            for c in characterize.CAMPAIGNS
            if c.testbench == "sampler-array-digitize"
        }
        self.assertEqual(
            got,
            {("tt", "27", "3.30"), ("ss", "-40", "3.63"), ("ss", "125", "3.63")},
        )

    def test_row_c_dry_run_includes_entropy_binding_corner(self):
        result = subprocess.run(
            [sys.executable, str(SIM_DIR / "characterize.py"), "--dry-run", "--rows", "C"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"--temps\s+125\b[^\n]*--supply\s+3\.63")


class RowDReproductionTests(unittest.TestCase):
    """Every required power-ledger term must declare how Row D reproduces it (#528)."""

    @staticmethod
    def _by_term():
        return {e.term: e for e in characterize.ROW_D_EVIDENCE}

    def test_every_required_ledger_term_has_a_reproduction(self):
        declared = self._by_term()
        for term in power_rollup.LEDGER_TERMS:
            if not term["required"]:
                continue
            self.assertIn(
                term["name"], declared,
                f"required power_rollup ledger term {term['name']!r} has no Row D "
                "reproduction in characterize.ROW_D_EVIDENCE",
            )

    def test_digital_term_is_declared(self):
        self.assertIn("digital", self._by_term())

    def test_declared_terms_are_not_stale(self):
        ledger = {t["name"] for t in power_rollup.LEDGER_TERMS}
        for term in self._by_term():
            self.assertTrue(term == "digital" or term in ledger, f"{term!r} not in the ledger")

    def test_testbenches_exist_and_flow_matches_campaigns(self):
        in_campaigns = {c.testbench for c in characterize.CAMPAIGNS if "D" in c.rows}
        for e in characterize.ROW_D_EVIDENCE:
            for tb in e.testbenches:
                self.assertTrue((SIM_DIR / "tb" / tb).is_dir(), f"{e.term}: no sim/tb/{tb}")
                if e.flow == "campaign":
                    self.assertIn(tb, in_campaigns, f"{e.term}: {tb} not a Row D campaign")
                else:
                    self.assertNotIn(tb, in_campaigns, f"{e.term}: {tb} is run locally")

    def test_liveness_stays_opt_in(self):
        tb = SIM_DIR / "tb" / characterize.LIVENESS_TB
        self.assertFalse((tb / "tb.json").exists(), "liveness must have no tb.json")
        self.assertNotIn(characterize.LIVENESS_TB, {c.testbench for c in characterize.CAMPAIGNS})
        self.assertEqual(self._by_term()["liveness"].flow, "separate")

    def test_liveness_commands_are_real_subcommands(self):
        text = (SIM_DIR / "tools" / "liveness_sampler_power.py").read_text()
        for cmd, _ in characterize.LIVENESS_COMMANDS:
            sub = cmd.split("liveness_sampler_power.py ")[1].split()[0]
            self.assertIn(f'add_parser("{sub}"', text)

    def test_dry_run_enumerates_all_row_d_evidence(self):
        for rows in ([], ["--rows", "D"]):
            r = subprocess.run(
                [sys.executable, str(SIM_DIR / "characterize.py"), "--dry-run", *rows],
                cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            for e in characterize.ROW_D_EVIDENCE:
                for tb in e.testbenches:
                    self.assertIn(tb, r.stdout)
            self.assertIn("--backend batch", r.stdout)


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


    def test_mixed_valid_and_unknown_raises_naming_unknown(self):
        with self.assertRaises(SystemExit) as cm:
            characterize._select(["A", "TYPO", "QQ"])
        msg = str(cm.exception)
        self.assertIn("TYPO", msg)
        self.assertIn("QQ", msg)

    def test_mixed_valid_and_out_of_scope_reports_guidance(self):
        with self.assertRaises(SystemExit) as cm:
            characterize._select(["A", "G"])
        msg = str(cm.exception)
        self.assertIn("row G", msg)
        self.assertIn(characterize.ROWS_NOT_COVERED["G"], msg)

    def test_multi_row_and_lowercase_still_select(self):
        selected = characterize._select(["a", "f"])
        self.assertEqual(
            selected,
            [c for c in characterize.CAMPAIGNS if {"A", "F"} & set(c.rows)],
        )


class RefusalSubprocessTests(unittest.TestCase):
    """Bad selections fail before env probing or any subprocess launch."""

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(SIM_DIR / "characterize.py"), *args],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=30,
        )

    def test_normal_and_dry_run_reject_mixed_unknown(self):
        for extra in ([], ["--dry-run"]):
            r = self._run("--rows", "A", "TYPO", *extra)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("TYPO", r.stderr)
            self.assertNotIn("====", r.stdout)
            self.assertNotIn("run_corners.py", r.stdout)
            self.assertNotIn("environment check", r.stderr)

    def test_mixed_out_of_scope_rejected(self):
        for extra in ([], ["--dry-run"]):
            r = self._run("--rows", "A", "G", *extra)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("row G", r.stderr)
            self.assertIn("run_sta.py", r.stderr)
            self.assertEqual(r.stdout, "")


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
