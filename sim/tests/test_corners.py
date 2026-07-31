#!/usr/bin/env python3
"""Unit tests for sim/harness/corners.py. No PDK and no ngspice required.

    python3 -m unittest discover -s sim/tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SIM_DIR))

from harness import corners  # noqa: E402


class CornerAxesTests(unittest.TestCase):
    def test_pvt_axes_match_the_mandated_grid(self):
        """CLAUDE.md: 'PVT corners on every recorded result' -- these are
        the axes the whole harness is built around."""
        self.assertEqual(corners.DEFAULT_TEMPERATURES_C, (-40.0, 27.0, 125.0))
        self.assertAlmostEqual(corners.DEFAULT_SUPPLY_TOLERANCE, 0.10)

    def test_supply_points_are_nominal_plus_minus_ten_percent(self):
        self.assertEqual(corners.supply_points(3.3, 0.10), [2.97, 3.3, 3.63])

    def test_zero_tolerance_collapses_the_voltage_axis(self):
        self.assertEqual(corners.supply_points(3.3, 0.0), [3.3])


class CornerSetTests(unittest.TestCase):
    def test_every_corner_names_one_section_per_device_family(self):
        for name, corner in corners.CORNERS.items():
            with self.subTest(corner=name):
                self.assertEqual(len(corner.sections), 6, corner.sections)

    def test_corner_sets_expand_and_deduplicate(self):
        resolved = corners.resolve_corners(["mos", "tt"])
        self.assertEqual([c.name for c in resolved], ["tt", "ff", "ss", "fs", "sf"])

    def test_full_set_adds_passive_corners_on_top_of_mos(self):
        resolved = corners.resolve_corners(["full"])
        names = {c.name for c in resolved}
        self.assertEqual(
            names, {"tt", "ff", "ss", "fs", "sf", "res_ff", "res_ss", "bjt_ff", "bjt_ss"}
        )

    def test_unknown_corner_is_rejected(self):
        with self.assertRaises(KeyError):
            corners.resolve_corners(["nope"])

    def test_default_set_is_used_when_no_names_given(self):
        resolved = corners.resolve_corners(None)
        self.assertEqual([c.name for c in resolved], list(corners.CORNER_SETS["mos"]))


class GridTests(unittest.TestCase):
    def test_grid_is_full_factorial_and_ordered(self):
        grid = corners.build_grid(
            corners.resolve_corners(["mos"]), (-40, 27, 125), [2.97, 3.3, 3.63]
        )
        self.assertEqual(len(grid), 5 * 3 * 3)
        self.assertEqual(len({p.corner_id for p in grid}), 45)

    def test_corner_id_naming(self):
        grid = corners.build_grid(
            corners.resolve_corners(["tt", "ss", "ff"]), (-40, 27, 125), [2.97, 3.3, 3.63]
        )
        ids = {p.corner_id for p in grid}
        self.assertIn("tt_27c_3.30v", ids)
        self.assertIn("ss_-40c_2.97v", ids)
        self.assertIn("ff_125c_3.63v", ids)


if __name__ == "__main__":
    unittest.main()
