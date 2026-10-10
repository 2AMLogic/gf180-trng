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


class GridValidationTests(unittest.TestCase):
    """validate_grid: a plan must not schedule two writes to one output id
    (issue #511). Rejected, never silently deduplicated."""

    def _grid(self, names, temps, supplies):
        return corners.build_grid(corners.resolve_corners(names), temps, supplies)

    def test_valid_grid_passes_and_keeps_order_and_indices(self):
        grid = self._grid(["tt", "ss"], (27, -40), [3.3, 2.97])
        corners.validate_grid(grid)
        self.assertEqual(
            [p.corner_id for p in grid],
            ["tt_27c_3.30v", "tt_27c_2.97v", "tt_-40c_3.30v", "tt_-40c_2.97v",
             "ss_27c_3.30v", "ss_27c_2.97v", "ss_-40c_3.30v", "ss_-40c_2.97v"],
        )
        self.assertEqual([p.index for p in grid], list(range(8)))

    def test_repeated_temperature_is_rejected(self):
        grid = self._grid(["tt"], (27, 125, 27), [3.3])
        with self.assertRaises(ValueError) as ctx:
            corners.validate_grid(grid)
        self.assertIn("repeated PVT point tt_27c_3.30v", str(ctx.exception))
        self.assertNotIn("125", str(ctx.exception))

    def test_repeated_corner_is_rejected(self):
        tt = corners.CORNERS["tt"]
        grid = corners.build_grid([tt, tt], (27,), [3.3])
        with self.assertRaises(ValueError) as ctx:
            corners.validate_grid(grid)
        self.assertIn("repeated PVT point tt_27c_3.30v", str(ctx.exception))

    def test_repeated_supply_is_rejected(self):
        grid = self._grid(["tt"], (27,), [3.3, 3.3])
        with self.assertRaises(ValueError) as ctx:
            corners.validate_grid(grid)
        self.assertIn("repeated PVT point tt_27c_3.30v", str(ctx.exception))

    def test_supplies_that_alias_at_two_decimals_are_rejected(self):
        grid = self._grid(["tt"], (27,), [3.301, 3.304])
        self.assertEqual(grid[0].corner_id, grid[1].corner_id)
        with self.assertRaises(ValueError) as ctx:
            corners.validate_grid(grid)
        message = str(ctx.exception)
        self.assertIn("share the output id tt_27c_3.30v", message)
        self.assertIn("3.301", message)
        self.assertIn("3.304", message)

    def test_temperatures_that_alias_in_the_id_are_rejected(self):
        grid = self._grid(["tt"], (27.0, 27.0000001), [3.3])
        self.assertEqual(grid[0].corner_id, grid[1].corner_id)
        with self.assertRaises(ValueError) as ctx:
            corners.validate_grid(grid)
        self.assertIn("share the output id tt_27c_3.30v", str(ctx.exception))

    def test_empty_and_single_point_grids_are_valid(self):
        corners.validate_grid([])
        corners.validate_grid(self._grid(["tt"], (27,), [3.3]))


if __name__ == "__main__":
    unittest.main()
