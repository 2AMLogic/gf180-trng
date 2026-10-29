#!/usr/bin/env python3
"""Geometry tests for `layout/cells/power_switch/build.py` (issue #707).

No KLayout, no `klt`, no PDK. Expectations are written as literals worked out from the cell's
documented structure (41 pads, 40 gates, 10 um fingers at 0.28 um), not read back from the module.
They are geometry regression tests, not DRC/LVS evidence: physical verification is
`layout/verify.py`.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "layout" / "testcells"))
sys.path.insert(0, str(REPO_ROOT / "layout" / "cells"))
from sim.tools.pathload import load_module_from_path  # noqa: E402

cell = load_module_from_path("power_switch_build_under_test", REPO_ROOT / "layout" / "cells" / "power_switch" / "build.py")

NWELL, COMP, POLY2, CONTACT, METAL1 = 21, 22, 30, 33, 34


class PowerSwitchGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rects, cls.labels = cell.build_shapes()

    def on(self, layer: int):
        return [r for r in self.rects if r.layer == layer and r.datatype == 0]

    def test_one_shared_diffusion_strip_of_ten_microns(self) -> None:
        (strip,) = self.on(COMP)
        self.assertAlmostEqual(strip.y1 - strip.y0, 10.0)
        # 41 pads of 0.70 um and 40 gates of 0.28 um.
        self.assertAlmostEqual(strip.x1 - strip.x0, 41 * 0.70 + 40 * 0.28)

    def test_forty_gate_fingers_each_0p28_long_and_over_the_strip(self) -> None:
        fingers = [r for r in self.on(POLY2) if abs((r.x1 - r.x0) - 0.28) < 1e-9]
        self.assertEqual(len(fingers), 40)
        for f in fingers:
            self.assertLess(f.y0, 0.0)
            self.assertGreater(f.y1, 10.0)

    def test_gate_fingers_do_not_touch_each_other_except_through_the_bus(self) -> None:
        fingers = sorted((r for r in self.on(POLY2) if abs((r.x1 - r.x0) - 0.28) < 1e-9), key=lambda r: r.x0)
        for a, b in zip(fingers, fingers[1:]):
            self.assertGreaterEqual(b.x0 - a.x1, 0.24 - 1e-9)  # poly2.space.1

    def test_one_contact_column_per_pad_and_enough_rows(self) -> None:
        contacts = self.on(CONTACT)
        rows = len({round(c.y0, 3) for c in contacts if c.y0 >= 0.0})
        self.assertEqual(rows, 21)
        columns = len({round(c.x0, 3) for c in contacts if c.y0 >= 0.0})
        self.assertEqual(columns, 41)
        self.assertEqual(len(contacts), 41 * 21 + 1)  # plus the one gate contact

    def test_every_contact_has_comp_or_poly_enclosure(self) -> None:
        strip = self.on(COMP)[0]
        for c in self.on(CONTACT):
            if c.y0 >= 0.0:
                self.assertGreaterEqual(c.x0 - strip.x0, 0.07 - 1e-9)
                self.assertGreaterEqual(strip.x1 - c.x1, 0.07 - 1e-9)
                self.assertGreaterEqual(c.y0 - strip.y0, 0.07 - 1e-9)
                self.assertGreaterEqual(strip.y1 - c.y1, 0.07 - 1e-9)

    def test_contacts_keep_the_deck_spacing(self) -> None:
        cs = sorted((c for c in self.on(CONTACT) if c.y0 >= 0.0), key=lambda c: (c.x0, c.y0))
        same_col = [(a, b) for a, b in zip(cs, cs[1:]) if abs(a.x0 - b.x0) < 1e-9]
        for a, b in same_col:
            self.assertGreaterEqual(b.y0 - a.y1, 0.25 - 1e-9)  # contact.space.1

    def test_pads_alternate_between_vdd_and_vvdd_stripes(self) -> None:
        stripes = sorted((r for r in self.on(METAL1) if abs((r.x1 - r.x0) - 0.42) < 1e-9), key=lambda r: r.x0)
        self.assertEqual(len(stripes), 41)
        for i, s in enumerate(stripes):
            if i % 2 == 0:  # source: runs up to the vdd bar
                self.assertGreater(s.y1, 10.0)
                self.assertLess(s.y0, 1.0)
            else:  # drain: runs down to the vvdd bar
                self.assertLess(s.y0, 0.0)
                self.assertLess(s.y1, 10.5)

    def test_vdd_and_vvdd_buses_never_overlap_and_keep_metal1_spacing(self) -> None:
        bars = sorted((r for r in self.on(METAL1) if (r.x1 - r.x0) > 30.0), key=lambda r: r.y0)
        self.assertEqual(len(bars), 2)
        vvdd, vdd = bars
        self.assertLess(vvdd.y1, 0.0)
        self.assertGreater(vdd.y0, 10.0)
        # a stripe of one net ends short of the other net's bar by at least metal1.space.1
        stripes = [r for r in self.on(METAL1) if abs((r.x1 - r.x0) - 0.42) < 1e-9]
        for s in stripes:
            if s.y1 > 10.0:  # source stripe: must stay clear of the vvdd bar
                self.assertGreaterEqual(s.y0 - vvdd.y1, 0.23)
            else:
                self.assertGreaterEqual(vdd.y0 - s.y1, 0.23)

    def test_pins_are_labelled(self) -> None:
        self.assertEqual(sorted(l.text for l in self.labels), ["sleep", "vdd", "vvdd"])

    def test_nwell_encloses_the_strip(self) -> None:
        (nwell,) = self.on(NWELL)
        strip = self.on(COMP)[0]
        for lo, hi in ((nwell.x0, strip.x0), (strip.x1, nwell.x1), (nwell.y0, strip.y0), (strip.y1, nwell.y1)):
            self.assertGreaterEqual(abs(hi - lo), 0.12 - 1e-9)  # nwell.enclosing.comp.1
        self.assertLess(nwell.x0, strip.x0)
        self.assertGreater(nwell.x1, strip.x1)

    def test_total_width_matches_the_schematic_default(self) -> None:
        self.assertEqual(cell.NFING * cell.W_FINGER, 400.0)
        self.assertAlmostEqual(cell.L_GATE, 0.28)


if __name__ == "__main__":
    unittest.main()
