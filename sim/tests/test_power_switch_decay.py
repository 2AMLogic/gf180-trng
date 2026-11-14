#!/usr/bin/env python3
"""Offline tests for the gated-rail decay evidence tool (issue #782).

No ngspice, no PDK, no ``klt``, no network: the committed request against the declared grid,
the deck against the tool's constants, the censoring arithmetic on synthetic readings, and
the committed records (every grid point once, and ``reached`` flags consistent with the rail).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR / "tools"))

import power_switch_decay as pd  # noqa: E402
import _record_golden as rg  # noqa: E402

DECK = pd.TB_DIR / pd.DECK
VDD = 3.3


def readings(t90=1e-3, t50=2e-3, t05=pd.TSTOP_S, vmin=1.0, vfin=1.0) -> dict:
    v: dict = {}
    for k in pd.CASES:
        v.update({f"t90_d{k}": pd.T_EDGE_S + t90, f"t50_d{k}": pd.T_EDGE_S + t50, f"t05_d{k}": t05,
                  f"vmin_d{k}": vmin, f"vfin_d{k}": vfin})
    return v


class RequestAndDeck(unittest.TestCase):
    def test_committed_request_matches_the_declared_grid(self) -> None:
        self.assertEqual(pd.cmd_emit(check=True), 0)

    def test_grid_is_the_power_switch_pvt_grid(self) -> None:
        req = pd.build_request()
        self.assertEqual(pd.n_units(), 45)
        self.assertEqual(req["corners"]["temperature_c"], [-40, 27, 125])
        self.assertIn("set num_threads=1", req["options"]["ngspice_init"])

    def test_deck_has_every_detector_and_node_the_request_reads(self) -> None:
        deck = DECK.read_text()
        for k in pd.CASES:
            self.assertIn(f"vd{k}", deck)
            for lab in pd.LEVELS:
                self.assertIn(f"c{lab}_{k} ", deck)
        self.assertIn("99.9e3", deck)  # censor step at 0.999 * TSTOP
        self.assertLess(pd.CENSOR_S, 0.999 * pd.TSTOP_S - pd.TSTEP_S)


class Arithmetic(unittest.TestCase):
    def test_reached_levels_subtract_the_edge_time(self) -> None:
        row = pd.derive(readings(t05=pd.T_EDGE_S + 5e-3, vmin=0.01), VDD)
        t = pd.tag(1)
        self.assertEqual(row[f"reached_t05_{t}"], 1.0)
        self.assertAlmostEqual(row[f"t_decay_s_t05_{t}"], 5e-3)
        self.assertEqual(pd.checks(row), [])

    def test_a_censored_crossing_is_reported_as_not_reached(self) -> None:
        row = pd.derive(readings(t05=0.999 * pd.TSTOP_S + 0.5), VDD)
        t = pd.tag(1)
        self.assertEqual(row[f"reached_t05_{t}"], 0.0)
        self.assertEqual(pd.checks(row), [])

    def test_a_crossing_flag_that_disagrees_with_the_rail_minimum_is_suspect(self) -> None:
        row = pd.derive(readings(t05=pd.T_EDGE_S + 5e-3, vmin=1.0), VDD)  # claims reached, rail never low
        self.assertTrue(any("disagree" in p for p in pd.checks(row)))

    def test_missing_readings_are_unmeasured(self) -> None:
        v = readings()
        del v["vmin_d2"]
        with self.assertRaises(pd.DerivationError):
            pd.derive(v, VDD)


class Records(unittest.TestCase):
    def test_every_grid_point_has_one_current_record(self) -> None:
        recs = pd.load_records(SIM_DIR / "records")
        self.assertEqual(len(recs), 45)
        self.assertEqual(len({(r["corner"][0], float(r["corner"][1]), round(float(r["corner"][2]), 2)) for r in recs}), 45)

    def test_recorded_flags_agree_with_recorded_rail_minimum(self) -> None:
        for r in pd.load_records(SIM_DIR / "records"):
            vdd = float(r["corner"][2])
            for k in pd.CASES:
                t = pd.tag(k)
                low = r["values"][f"vmin_v_{t}"] <= pd.OFF_FRACTION * vdd
                self.assertEqual(low, r["values"][f"reached_t05_{t}"] > 0.5, f"{r['stem']} {t}")


class RecordFrontMatter(unittest.TestCase):
    """The record front matter this tool renders, pinned line for line (issue #834).

    The four power tools render their front matter through one skeleton,
    ``_power_cli.render_header``, so a header edit meant for one of them that reaches the
    others -- or a consolidation that quietly reorders a field -- fails here. Only the git
    blob SHAs, the ``repo_commit`` and ``platform.platform()`` are masked
    (``_record_golden.front_matter``); they are facts about the host and the checkout, not
    about the renderer. Records already committed under ``sim/records/`` are written in this
    format and are append-only, so it may not drift silently.
    """

    MEASURED = """\
---
record: 2026-01-02-power_switch_decay-1
date: 2026-01-02T03:04:05Z
status: valid

testbench:
  path: sim/tb/power-switch/tb_power_switch_decay.sp
  sha: <BLOB>
netlist:
  path: design/power_switch.spice
  sha: <BLOB>
repo_commit: <COMMIT>

pdk: gf180mcuD @ 1.0.test
pdk.models:
  - libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 9.9.9 (client; batch backend)
  ngspice: "ngspice-99 test build (batch fleet)"
  platform: <PLATFORM>

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran (deterministic)
  tstop: 100000
  tstep: 100 (print step; the solver steps adaptively)
  tmax: default
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-01-02-power_switch_decay-1/
  files:
    - probe.sp  sha256:<SHA256>
    - probe.log  sha256:<SHA256>
wall_time: 12.5s
---
"""

    ATTEMPT = """\
---
record: 2026-01-02-power_switch_decay-attempt-1
date: 2026-01-02T03:04:05Z
status: valid

testbench:
  path: sim/tb/power-switch/tb_power_switch_decay.sp
  sha: <BLOB>
netlist:
  path: design/power_switch.spice
  sha: <BLOB>
repo_commit: <COMMIT>

tool:
  klt: 9.9.9

raw:
  path: sim/records/raw/2026-01-02-power_switch_decay-attempt-1/
  files:
    - probe.sp  sha256:<SHA256>
    - probe.log  sha256:<SHA256>
---
"""

    def _rendered(self) -> tuple[str, str]:
        unit = rg.unit(readings())
        rep = rg.report(unit)
        row = pd.analyse_report(rep)[0]
        self.assertEqual(row["verdict"], "OK", row.get("problems"))
        return (pd.render_measured("2026-01-02-power_switch_decay-1", row, unit, rep, rg.RAW_FILES,
                                 rg.NOW, rg.GIT),
                pd.render_unmeasured("2026-01-02-power_switch_decay-attempt-1", [unit], rep, rg.RAW_FILES,
                                   rg.NOW, rg.GIT, rg.NOTE))

    def test_measured_front_matter_is_unchanged(self) -> None:
        self.assertEqual(rg.front_matter(self._rendered()[0]), self.MEASURED)

    def test_attempt_front_matter_is_unchanged(self) -> None:
        self.assertEqual(rg.front_matter(self._rendered()[1]), self.ATTEMPT)

    def test_the_per_tool_prose_outlives_the_shared_header(self) -> None:
        measured, attempt = self._rendered()
        for section in ("## Result", "## How to reproduce", "## Caveats"):
            self.assertIn(section, measured)
        for section in ('## Result',):
            self.assertIn(section, attempt)
        for text in (measured, attempt):
            self.assertIn("Written by `sim/tools/power_switch_decay.py record`", text)
            self.assertTrue(text.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
