#!/usr/bin/env python3
"""Unit tests for sim/harness/runner.py deck composition and output parsing.

No PDK and no ngspice required -- deck composition is tested against a fake
PDK layout; actual ngspice execution is exercised by sim/selftest.sh instead.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import corners, runner, testbench  # noqa: E402
from harness.pdk import Pdk  # noqa: E402


def fake_pdk(root: Path) -> Pdk:
    (root / "libs.tech" / "ngspice").mkdir(parents=True, exist_ok=True)
    (root / "libs.tech" / "ngspice" / "sm141064.ngspice").write_text("* fake\n")
    (root / "libs.tech" / "ngspice" / "design.ngspice").write_text("* fake\n")
    (root / "SOURCES").write_text("open_pdks deadbeef\n")
    return Pdk(path=root, variant=root.name, source="test")


class DeckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "tb").mkdir()
        (root / "tb" / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (root / "tb" / "tb.json").write_text(
            json.dumps(
                {
                    "name": "x",
                    "netlist": "x.spice",
                    "measure": {"vout": "v(out)", "iq": "-i(v1)"},
                    "params": {"cload": "1p"},
                    "options": ["reltol=1e-5"],
                }
            )
        )
        self.tb = testbench.load(root / "tb")
        self.pdk = fake_pdk(root / "gf180mcuD")
        self.point = corners.build_grid(corners.resolve_corners(["ss"]), (125,), [3.63])[0]

    def test_deck_sets_the_pvt_point(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point)
        self.assertIn(".param vdd_val=3.63", deck)
        self.assertIn(".param vdd_nom=3.3", deck)
        self.assertIn(".temp 125", deck)

    def test_deck_includes_design_switches_before_model_sections(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point)
        design_at = deck.index("design.ngspice")
        lib_at = deck.index("sm141064.ngspice")
        self.assertLess(design_at, lib_at)

    def test_deck_selects_every_section_of_the_corner(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point)
        for section in self.point.corner.sections:
            self.assertIn(f'sm141064.ngspice" {section}', deck)

    def test_deck_carries_manifest_params_and_options(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point)
        self.assertIn(".param cload=1p", deck)
        self.assertIn(".options reltol=1e-5", deck)

    def test_deck_emits_one_measurement_vector_per_measure_entry(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point)
        self.assertIn("let m_vout = v(out)", deck)
        self.assertIn("let m_iq = -i(v1)", deck)
        self.assertIn("print m_vout", deck)
        self.assertTrue(deck.rstrip().endswith(".end"))

    def test_seed_only_emitted_when_given(self):
        deck_no_seed = runner.compose_deck(self.tb, self.pdk, self.point, seed=None)
        self.assertNotIn(".option seed=", deck_no_seed)
        deck_seeded = runner.compose_deck(self.tb, self.pdk, self.point, seed=7)
        self.assertIn(".option seed=7", deck_seeded)


class ExtraLibSectionsTests(unittest.TestCase):
    """extra_lib_sections replaces the plain corner sections entirely (a
    section like "statistical" redefines the same subckts)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "tb").mkdir()
        (root / "tb" / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (root / "tb" / "tb.json").write_text(
            json.dumps(
                {
                    "name": "x",
                    "netlist": "x.spice",
                    "measure": {"vout": "v(out)"},
                    "analysis_type": "mc",
                    "default_runs": 2,
                    "design_params": {"sw_stat_mismatch": 1},
                    "extra_lib_sections": ["statistical"],
                }
            )
        )
        self.tb = testbench.load(root / "tb")
        self.pdk = fake_pdk(root / "gf180mcuD")
        self.point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]

    def test_extra_sections_replace_corner_sections(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point, seed=1)
        self.assertIn('sm141064.ngspice" statistical', deck)
        self.assertNotIn('sm141064.ngspice" typical', deck)

    def test_design_params_override_after_design_include(self):
        deck = runner.compose_deck(self.tb, self.pdk, self.point, seed=1)
        design_at = deck.index("design.ngspice")
        override_at = deck.index(".param sw_stat_mismatch=1")
        self.assertLess(design_at, override_at)


class ParseTests(unittest.TestCase):
    def test_parses_print_output(self):
        text = "\n".join(
            [
                "Circuit: * x",
                "m_vout = 1.2003456789e+00",
                "m_iq = -4.5e-05",
                "v(other) = 9.9",
                "m_bad = not_a_number",
            ]
        )
        self.assertEqual(
            runner.parse_measurements(text), {"vout": 1.2003456789, "iq": -4.5e-05}
        )


class RunPointContractTests(unittest.TestCase):
    """run_point enforces the 'no seed, no evidence' rule at the API level
    (before ever invoking ngspice)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "tb").mkdir()
        (root / "tb" / "x.spice").write_text("v1 out 0 dc {vdd_val}\n")
        (root / "tb" / "tb.json").write_text(
            json.dumps(
                {
                    "name": "x",
                    "netlist": "x.spice",
                    "measure": {"vout": "v(out)"},
                    "analysis_type": "mc",
                    "default_runs": 1,
                }
            )
        )
        self.tb = testbench.load(root / "tb")
        self.point = corners.build_grid(corners.resolve_corners(["tt"]), (27,), [3.3])[0]

    def test_stochastic_testbench_without_seeds_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            runner.run_point(self.tb, None, self.point, Path("/nonexistent"), seeds=None)
        self.assertIn("no seed, no evidence", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
