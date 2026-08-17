#!/usr/bin/env python3
"""Unit tests for #145's gate-level aggregation
(``sim/tools/digital_corner_characterization.py``).

Two groups:

1. **Record reading and the derivations**, against synthetic records written
   into a temporary directory, so the arithmetic is tested where the right
   answer is known by construction -- including the two guards that exist to
   stop a wrong aggregate being presented as a right one (a record that is
   not ``level: gate``; records that disagree on a corner-independent
   quantity).
2. **The committed family**, as a coverage/consistency guard: the fifteen
   corners the characterization document is written against are all present,
   all ``valid``, and each carries the fields the document quotes.

Everything here runs with no PDK, no ``openroad`` and no ngspice -- the
tool's PDK-dependent legs (``--estimate``) are exercised by running the tool
itself, not by these tests.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent

sys.path.insert(0, str(SIM_DIR / "tools"))

import digital_corner_characterization as dcc  # noqa: E402


def synthetic_record(
    stem: str,
    liberty: str,
    rc: str,
    *,
    level: str = "gate",
    status: str = "valid",
    setup_ns: float = 20.0,
    hold_ns: float = 1.0,
    fmax_mhz: float = 50.0,
    cell_area_um2: float = 113_087.9,
    p_1mhz_w: float = 5e-4,
    leakage_w: float = 1e-6,
) -> str:
    """One record in the shape ``run_sta.py`` writes, with only the fields
    this tool reads. Deliberately hand-written rather than generated from the
    driver: a test that builds its input with the same code path as
    production cannot catch a format change in that path."""
    return f"""---
record: {stem}
date: 2026-08-17T00:00:00Z
status: {status}

level: {level} (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/run_sta.py
  sha: 0000000000000000000000000000000000000000
netlist:
  path: layout/digital/trng_top.def
  sha: 1111111111111111111111111111111111111111
repo_commit: 2222222222222222222222222222222222222222

tool:
  openroad: "26Q3-0000-gtest"

corner:
  process: {liberty.split('_')[0]}
  voltage: 3.30 V (nominal 3.3 V)
  temperature: 25
  liberty: gf180mcu_fd_sc_mcu9t5v0__{liberty}
  interconnect: {rc} (OpenRCX rule deck)

analysis:
  type: sta+power
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/{stem}/
  files:
    - constraint.log  sha256:dead
wall_time: 1.0s
---

## Result

- `constraint_period_ns`: 5.000000e+01
- `constraint_freq_mhz`: 2.000000e+01
- `worst_setup_slack_ns`: {setup_ns:.6e}
- `worst_hold_slack_ns`: {hold_ns:.6e}
- `tns_setup_ns`: 0.000000e+00
- `tns_hold_ns`: 0.000000e+00
- `clock_skew_setup_ns`: 1.000000e-01
- `min_period_ns`: {1e3 / fmax_mhz:.6e}
- `fmax_bisect_mhz`: {fmax_mhz:.6e}
- `fmax_linear_mhz`: {fmax_mhz:.6e}
- `cell_area_um2`: {cell_area_um2:.6e}
- `utilization_pct`: 4.081242e+01
- `wire_cap_per_net_f`: 3.939893e-15
- `p_total_20mhz_w`: {p_1mhz_w * 20:.6e}
- `p_total_1mhz_w`: {p_1mhz_w:.6e}
- `p_clock_1mhz_w`: 1.000000e-04
- `p_sequential_1mhz_w`: 2.000000e-04
- `p_combinational_1mhz_w`: 1.000000e-04
- `p_leakage_w`: {leakage_w:.6e}
- `i_leakage_a`: {leakage_w / 3.3:.6e}
- `unconstrained_endpoints`: 6.800000e+01
- `inputs_missing_delay`: 4.200000e+01
- `outputs_missing_delay`: 6.600000e+01
"""


class SyntheticRecordTests(unittest.TestCase):
    """The derivations, where the answer is known by construction."""

    def _dir(self, records: list[str]) -> Path:
        tmp = Path(tempfile.mkdtemp())
        for i, text in enumerate(records, start=1):
            (tmp / f"2026-08-17-digital-sta-power-{i:02d}.md").write_text(text)
        return tmp

    def test_binding_corners_are_the_minima_on_their_own_side(self):
        tmp = self._dir([
            synthetic_record("2026-08-17-digital-sta-power-01", "ss_125C_3v00",
                             "max", setup_ns=5.0, hold_ns=2.0, fmax_mhz=22.0),
            synthetic_record("2026-08-17-digital-sta-power-02", "ff_n40C_3v60",
                             "min", setup_ns=40.0, hold_ns=0.3, fmax_mhz=120.0),
        ])
        t = dcc.timing(dcc.load(tmp))
        # Setup binds slow, hold binds fast -- two different corners, which is
        # the whole reason both are reported.
        self.assertEqual(t["setup_binding"], "ss_125C_3v00/rc-max")
        self.assertEqual(t["hold_binding"], "ff_n40C_3v60/rc-min")
        self.assertEqual(t["fmax_floor_corner"], "ss_125C_3v00/rc-max")
        self.assertAlmostEqual(t["fmax_floor_mhz"], 22.0)
        self.assertTrue(t["closes_everywhere"])

    def test_a_negative_slack_anywhere_fails_closes_everywhere(self):
        tmp = self._dir([
            synthetic_record("2026-08-17-digital-sta-power-01", "ss_125C_3v00",
                             "max", setup_ns=5.0),
            synthetic_record("2026-08-17-digital-sta-power-02", "ff_n40C_3v60",
                             "min", hold_ns=-0.05),
        ])
        records = dcc.load(tmp)
        self.assertFalse(dcc.timing(records)["closes_everywhere"])
        self.assertTrue(any("positive setup AND hold" in f
                            for f in dcc.check(records)))

    def test_a_non_gate_record_is_refused_rather_than_aggregated(self):
        tmp = self._dir([
            synthetic_record("2026-08-17-digital-sta-power-01", "tt_025C_3v30",
                             "nom", level="behavioral"),
        ])
        with self.assertRaises(dcc.RecordError):
            dcc.load(tmp)

    def test_records_disagreeing_on_cell_area_are_refused(self):
        # Cell area is corner-independent. Two different values mean two
        # different designs were measured, and averaging or picking one would
        # silently produce a figure describing neither.
        tmp = self._dir([
            synthetic_record("2026-08-17-digital-sta-power-01", "tt_025C_3v30",
                             "nom", cell_area_um2=113_087.9),
            synthetic_record("2026-08-17-digital-sta-power-02", "ss_125C_3v00",
                             "max", cell_area_um2=98_000.0),
        ])
        with self.assertRaises(dcc.RecordError):
            dcc.area(dcc.load(tmp))

    def test_superseded_records_are_not_aggregated(self):
        tmp = self._dir([
            synthetic_record("2026-08-17-digital-sta-power-01", "tt_025C_3v30",
                             "nom", status="superseded", setup_ns=1.0),
            synthetic_record("2026-08-17-digital-sta-power-02", "tt_025C_3v30",
                             "nom", setup_ns=30.0),
        ])
        records = dcc.load(tmp)
        self.assertEqual(len(records), 1)
        self.assertAlmostEqual(
            dcc.timing(records)["setup_binding_slack_ns"], 30.0
        )

    def test_power_and_leakage_maxima_are_reported_separately(self):
        # The hot/fast corner can bind leakage while another binds total
        # power; reporting one as if it were the other is the mistake this
        # guards.
        tmp = self._dir([
            synthetic_record("2026-08-17-digital-sta-power-01", "ff_125C_3v60",
                             "max", p_1mhz_w=6.0e-4, leakage_w=1.0e-5),
            synthetic_record("2026-08-17-digital-sta-power-02", "ff_n40C_3v60",
                             "min", p_1mhz_w=7.0e-4, leakage_w=3.0e-7),
        ])
        p = dcc.power(dcc.load(tmp))
        self.assertEqual(p["max_1mhz_corner"], "ff_n40C_3v60/rc-min")
        self.assertEqual(p["max_leakage_corner"], "ff_125C_3v60/rc-max")


class CommittedFamilyTests(unittest.TestCase):
    """The fifteen committed corners the characterization document quotes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.records = dcc.load()

    def test_the_full_grid_is_present_exactly_once_each(self):
        corners = sorted(r.corner for r in self.records)
        expected = sorted(
            f"{lib}/rc-{rc}"
            for lib in ("ss_125C_3v00", "ss_n40C_3v00", "tt_025C_3v30",
                        "ff_125C_3v60", "ff_n40C_3v60")
            for rc in ("min", "nom", "max")
        )
        self.assertEqual(corners, expected)

    def test_every_record_carries_every_quoted_field(self):
        quoted = (
            "worst_setup_slack_ns", "worst_hold_slack_ns", "tns_setup_ns",
            "tns_hold_ns", "clock_skew_setup_ns", "fmax_bisect_mhz",
            "fmax_linear_mhz", "min_period_ns", "cell_area_um2",
            "utilization_pct", "wire_cap_per_net_f", "p_total_1mhz_w",
            "p_total_20mhz_w", "p_clock_1mhz_w", "p_sequential_1mhz_w",
            "p_combinational_1mhz_w", "p_leakage_w", "i_leakage_a",
            "worst_setup_slack_ideal_clock_ns", "clock_tree_cost_ns",
        )
        for record in self.records:
            for key in quoted:
                self.assertIn(key, record.values, f"{record.stem}: {key}")

    def test_leakage_is_independent_of_the_interconnect_corner(self):
        # Leakage is a device property; a wire model that moved it would mean
        # the two axes are not the independent axes this sweep treats them as.
        by_liberty: dict[str, set[float]] = {}
        for record in self.records:
            by_liberty.setdefault(record.liberty, set()).add(
                round(record.v("p_leakage_w"), 15)
            )
        for liberty, values in by_liberty.items():
            self.assertEqual(len(values), 1, f"{liberty}: {values}")

    def test_the_recorded_findings_still_hold(self):
        # The same gate `npm run check:spec` runs, as a unit test so a local
        # `npm test` catches a stale document too.
        self.assertEqual(dcc.check(self.records), [])


if __name__ == "__main__":
    unittest.main()
