#!/usr/bin/env python3
"""Hold the Chipalooza proposal's current-evidence table (rows C, D, E, G, I)
and the README's characterize-campaign totals to the committed evidence (#436).

Offline and stdlib-only: the figures are re-derived from
``sim/tools/power_rollup.py`` output, the ``digital-sta-power`` record family
and ``sim/characterize.py``'s campaign table. A stale quoted figure, or a
Row C corner missing from the reproduction campaign, fails here.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(SIM_DIR))

import characterize  # noqa: E402

PROPOSAL = (REPO_ROOT / "docs" / "chipalooza" / "challenge-3-proposal.md").read_text()
README = (REPO_ROOT / "README.md").read_text()
RECORDS = SIM_DIR / "records"


def _row(letter: str) -> str:
    m = re.search(rf"^\| {letter} \| .*$", PROPOSAL, re.M)
    assert m, f"row {letter} missing from the proposal table"
    return m.group(0)


def _rollup() -> str:
    proc = subprocess.run(
        [sys.executable, "-I", str(SIM_DIR / "tools" / "power_rollup.py")],
        capture_output=True, text=True, cwd=REPO_ROOT, check=True,
    )
    return proc.stdout


def _fmax_by_corner() -> dict[tuple[str, str], float]:
    out = {}
    for f in sorted(RECORDS.glob("2026-10-07-digital-sta-power-*.md")):
        t = f.read_text()
        lib = re.search(r"^  liberty: \S+__(\S+)$", t, re.M).group(1)
        rc = re.search(r"^  interconnect: (\S+)", t, re.M).group(1)
        out[(lib, rc)] = float(re.search(r"`fmax_bisect_mhz`: (\S+)", t).group(1))
    return out


class ProposalTableAgreesWithEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rollup = _rollup()

    def _rollup_total(self, corner: str) -> str:
        m = re.search(rf"^\| {re.escape(corner)}\s*\|(?:[^|]*\|){{4}}\s*([\d.]+ uW)", self.rollup, re.M)
        self.assertIsNotNone(m, corner)
        return m.group(1).replace(" uW", " µW")

    def test_row_d_min_typ_max_are_the_rollup_totals(self):
        row = _row("D")
        for corner in ("ss/125/2.97", "tt/27/3.30", "ff/-40/3.63"):
            with self.subTest(corner=corner):
                self.assertIn(self._rollup_total(corner), row)
        self.assertRegex(self.rollup, r"digital \(MEASURED-at-gate-level\): 348\.2 uW")
        self.assertIn("348.2 µW", row)
        self.assertIn("151.6 %", row)

    def test_row_d_historical_figures_carry_revision_context(self):
        row = _row("D")
        self.assertRegex(row, r"Historical, not current: 712\.4 µW[^|]*depth-8 build")

    def test_row_e_worst_corner_is_the_rollup(self):
        row = _row("E")
        self.assertRegex(self.rollup, r"Worst idle corner: ff/125/3\.63\s*-> 2\.211 uA")
        self.assertIn("2.211 µA", row)
        self.assertRegex(row, r"Historical, not current: 3\.979 µA[^|]*depth-8 build")

    def test_row_g_fmax_matches_current_record_family(self):
        fm = _fmax_by_corner()
        self.assertEqual(len(fm), 15)
        row = _row("G")
        lo = min(fm.values())
        hi = max(fm.values())
        tt = [v for (lib, _), v in fm.items() if lib == "tt_025C_3v30"]
        self.assertEqual(lo, fm[("ss_125C_3v00", "max")])
        self.assertEqual(hi, fm[("ff_n40C_3v60", "min")])
        for want in (f"{lo:.2f} MHz", f"{min(tt):.2f}–{max(tt):.2f} MHz", f"{hi:.2f} MHz"):
            self.assertIn(want, row)
        self.assertRegex(row, r"35\.63 MHz[^|]*historical")

    def test_row_i_separates_current_estimate_from_stale_composed_figure(self):
        row = _row("I")
        self.assertIn("0.06885 mm²", row)
        self.assertIn("#256", row)
        self.assertIn("stale", row)
        self.assertRegex(row, r"Historical, not current: the earlier 0\.1350 mm²")
        self.assertNotIn("no full whole-block layout exists", row)

    def test_row_c_caveats_and_all_three_corners_cited(self):
        row = _row("C")
        for corner in ("`ss`/+125 °C/3.63 V", "`tt`/27 °C/3.30 V", "`ss`/−40 °C/3.63 V"):
            self.assertIn(corner, row)
        self.assertIn("2026-10-09-sampler-array-digitize-01", row)
        self.assertIn("Unmet/TBD — not measurable pre-silicon", row)
        self.assertTrue((RECORDS / "2026-10-09-sampler-array-digitize-01.md").is_file())


class ReadmeCampaignMatchesDriver(unittest.TestCase):
    def test_row_c_campaign_covers_binding_corner(self):
        corners = set()
        for c in characterize.CAMPAIGNS:
            if c.testbench == "sampler-array-digitize":
                a = c.extra_args
                corners.add((a[a.index("--corners") + 1], a[a.index("--temps") + 1]))
        self.assertIn(("ss", "125"), corners)
        self.assertEqual(len(corners), 3)

    def test_readme_point_count_matches_plan(self):
        # 27 + 27 + 45 + 45 + 3 per Row C corner (3 seeds, 1001..1003).
        n_c = sum(1 for c in characterize.CAMPAIGNS if c.testbench == "sampler-array-digitize")
        terms = [27, 27, 45, 45] + [3] * n_c
        m = re.search(r"((?:\d+ \+ )+\d+) = (\d+) ngspice points", README)
        self.assertIsNotNone(m)
        self.assertEqual([int(x) for x in m.group(1).split(" + ")], terms)
        self.assertEqual(int(m.group(2)), sum(terms))
        words = {6: "six", 7: "seven"}
        self.assertIn(f"across {words[len(characterize.CAMPAIGNS)]} campaign steps", README)


if __name__ == "__main__":
    unittest.main()
