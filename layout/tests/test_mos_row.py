#!/usr/bin/env python3
"""Unit tests for the shared hand-drawn layout engine, `layout/cells/_mos_row.py`.

The generated cells (`xor2`, `sampler_dff`) only exercise this engine
indirectly, through whole-cell verification. These tests pin its placement,
terminal-stack and routing geometry directly, against coordinates worked out
by hand from the documented constants (written here as literals, not read back
from the module), so they need no KLayout, no `klt` and no PDK.

They are geometry regression tests. They are not evidence of DRC/LVS
compliance or of PVT performance; physical verification remains separate.

Helpers covered: `_pad_half`, `_place_row`, `_terminal`, `_route_nets` and
`build_cell`.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path
from unittest import mock

_MOS_ROW_PATH = Path(__file__).resolve().parents[1] / "cells" / "_mos_row.py"
_SPEC = importlib.util.spec_from_file_location("_mos_row_under_test", _MOS_ROW_PATH)
mos_row = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = mos_row  # dataclasses resolves annotations via sys.modules
_SPEC.loader.exec_module(mos_row)  # type: ignore[union-attr]

Device = mos_row.Device

# Layer numbers, restated independently of the module under test.
NWELL = (21, 0)
COMP = (22, 0)
POLY2 = (30, 0)
CONTACT = (33, 0)
METAL1 = (34, 0)
VIA1 = (35, 0)
METAL2 = (36, 0)
METAL2_LABEL = (36, 10)
VIA2 = (38, 0)
METAL3 = (42, 0)

TOL = 1e-9


def on_layer(rects, layer):
    """Rectangles on `layer` as (x0, y0, x1, y1) tuples, in drawing order."""
    return [(r.x0, r.y0, r.x1, r.y1) for r in rects if (r.layer, r.datatype) == layer]


def centered(x, y, w, h=None):
    h = w if h is None else h
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)


def encloses(outer, inner, margin):
    """True when `outer` extends at least `margin` past `inner` on all sides."""
    return (
        outer[0] <= inner[0] - margin + TOL
        and outer[1] <= inner[1] - margin + TOL
        and outer[2] >= inner[2] + margin - TOL
        and outer[3] >= inner[3] + margin - TOL
    )


class GeometryCase(unittest.TestCase):
    def assertRect(self, actual, expected):
        self.assertEqual(len(actual), 4)
        for a, e in zip(actual, expected):
            self.assertAlmostEqual(a, e, delta=1e-9, msg=f"{actual} != {expected}")

    def assertRects(self, actual, expected):
        self.assertEqual(len(actual), len(expected), f"{actual} vs {expected}")
        for a, e in zip(actual, expected):
            self.assertRect(a, e)


class PadHalfTests(unittest.TestCase):
    def test_below_minimum_uses_minimum(self):
        self.assertAlmostEqual(mos_row._pad_half(0.30), 0.22, delta=TOL)
        self.assertAlmostEqual(mos_row._pad_half(0.0), 0.22, delta=TOL)

    def test_equal_to_minimum(self):
        self.assertAlmostEqual(mos_row._pad_half(0.44), 0.22, delta=TOL)

    def test_above_minimum_uses_width(self):
        self.assertAlmostEqual(mos_row._pad_half(0.88), 0.44, delta=TOL)
        self.assertAlmostEqual(mos_row._pad_half(0.45), 0.225, delta=TOL)


class PlaceRowTests(GeometryCase):
    def test_empty_row_returns_origin_and_draws_nothing(self):
        canvas = mos_row._Canvas()
        terminals = defaultdict(list)
        result = mos_row._place_row(canvas, [], 1.0, 7.5, terminals)
        self.assertEqual(result, (7.5, 1.0, 1.0, 1.0))
        self.assertEqual(canvas.rects, [])
        self.assertEqual(canvas.labels, [])
        self.assertEqual(dict(terminals), {})

    def test_narrow_device_is_dog_boned(self):
        canvas = mos_row._Canvas()
        terminals = defaultdict(list)
        dev = Device("m1", "n", 0.30, 0.28, "g", "d", "s")
        x_end, bottom, top, landing_top = mos_row._place_row(canvas, [dev], 1.0, 0.0, terminals)

        # Pad half 0.22 (W < 0.44), narrow half 0.15; gate x 0.8, half-L 0.14.
        self.assertRects(
            on_layer(canvas.rects, COMP),
            [
                (-0.22, 0.78, 0.66, 1.22),  # source pad up to the gate edge
                (0.66, 0.85, 0.94, 1.15),  # narrowed under the gate
                (0.94, 0.78, 1.82, 1.22),  # drain pad from the gate edge
            ],
        )
        self.assertRects(
            on_layer(canvas.rects, POLY2),
            [
                (0.66, 0.65, 0.94, 1.57),  # gate strip: 0.20 below narrow comp, 0.05 into pad
                (0.55, 1.52, 1.05, 1.92),  # landing pad: 0.30 above row top, 0.40 tall
            ],
        )
        self.assertAlmostEqual(x_end, 1.6, delta=TOL)
        self.assertAlmostEqual(bottom, 0.78, delta=TOL)
        self.assertAlmostEqual(top, 1.22, delta=TOL)
        self.assertAlmostEqual(landing_top, 1.92, delta=TOL)

    def test_terminal_coordinates_source_gate_drain(self):
        canvas = mos_row._Canvas()
        terminals = defaultdict(list)
        dev = Device("m1", "n", 0.30, 0.28, "g", "d", "s")
        mos_row._place_row(canvas, [dev], 1.0, 0.0, terminals)
        self.assertEqual(sorted(terminals), ["d", "g", "s"])
        self.assertEqual(len(terminals["s"]), 1)
        self.assertEqual(len(terminals["g"]), 1)
        self.assertEqual(len(terminals["d"]), 1)
        sx, sy = terminals["s"][0]
        gx, gy = terminals["g"][0]
        dx, dy = terminals["d"][0]
        self.assertAlmostEqual(sx, 0.0, delta=TOL)
        self.assertAlmostEqual(sy, 1.0, delta=TOL)
        self.assertAlmostEqual(gx, 0.8, delta=TOL)
        self.assertAlmostEqual(gy, 1.72, delta=TOL)  # middle of landing pad 1.52..1.92
        self.assertAlmostEqual(dx, 1.6, delta=TOL)
        self.assertAlmostEqual(dy, 1.0, delta=TOL)

    def test_wide_device_is_one_uniform_rectangle(self):
        canvas = mos_row._Canvas()
        terminals = defaultdict(list)
        dev = Device("m1", "p", 0.88, 0.28, "g", "d", "s")
        x_end, bottom, top, landing_top = mos_row._place_row(canvas, [dev], 1.0, 0.0, terminals)

        self.assertRects(on_layer(canvas.rects, COMP), [(-0.22, 0.56, 1.82, 1.44)])
        self.assertRects(
            on_layer(canvas.rects, POLY2),
            [
                (0.66, 0.36, 0.94, 1.79),  # strip reaches 0.20 below the full-width comp
                (0.55, 1.74, 1.05, 2.14),
            ],
        )
        self.assertAlmostEqual(x_end, 1.6, delta=TOL)
        self.assertAlmostEqual(bottom, 0.56, delta=TOL)
        self.assertAlmostEqual(top, 1.44, delta=TOL)
        self.assertAlmostEqual(landing_top, 2.14, delta=TOL)
        self.assertAlmostEqual(terminals["g"][0][1], 1.94, delta=TOL)

    def test_width_at_boundary_is_not_dog_boned(self):
        canvas = mos_row._Canvas()
        dev = Device("m1", "n", 0.44, 0.28, "g", "d", "s")
        mos_row._place_row(canvas, [dev], 1.0, 0.0, defaultdict(list))
        self.assertRects(on_layer(canvas.rects, COMP), [(-0.22, 0.78, 1.82, 1.22)])

    def test_devices_placed_left_to_right_on_disjoint_islands(self):
        canvas = mos_row._Canvas()
        terminals = defaultdict(list)
        devs = [
            Device("m1", "n", 0.30, 0.28, "g1", "d1", "s1"),
            Device("m2", "n", 0.88, 0.28, "g2", "d2", "s2"),
        ]
        x_end, bottom, top, landing_top = mos_row._place_row(canvas, devs, 1.0, 0.0, terminals)

        # The row is bounded by the tallest device and every gate landing
        # pad tops out at the same Y.
        self.assertAlmostEqual(x_end, 4.0, delta=TOL)
        self.assertAlmostEqual(bottom, 0.56, delta=TOL)
        self.assertAlmostEqual(top, 1.44, delta=TOL)
        self.assertAlmostEqual(landing_top, 2.14, delta=TOL)
        self.assertAlmostEqual(terminals["g1"][0][1], 1.94, delta=TOL)
        self.assertAlmostEqual(terminals["g2"][0][1], 1.94, delta=TOL)

        # Second device is one 3 * SLOT_PITCH (2.4) step to the right.
        self.assertAlmostEqual(terminals["s1"][0][0], 0.0, delta=TOL)
        self.assertAlmostEqual(terminals["d1"][0][0], 1.6, delta=TOL)
        self.assertAlmostEqual(terminals["s2"][0][0], 2.4, delta=TOL)
        self.assertAlmostEqual(terminals["g2"][0][0], 3.2, delta=TOL)
        self.assertAlmostEqual(terminals["d2"][0][0], 4.0, delta=TOL)

        comps = on_layer(canvas.rects, COMP)
        first = comps[:3]
        second = comps[3:]
        self.assertEqual(len(second), 1)
        self.assertAlmostEqual(max(r[2] for r in first), 1.82, delta=TOL)
        self.assertAlmostEqual(second[0][0], 2.18, delta=TOL)
        self.assertGreater(second[0][0] - max(r[2] for r in first), 0.28 - TOL)

    def test_both_rows_at_build_cell_offset_have_unique_terminal_x(self):
        canvas = mos_row._Canvas()
        terminals = defaultdict(list)
        nmos = [
            Device("mn1", "n", 0.30, 0.28, "a", "y", "vss"),
            Device("mn2", "n", 0.50, 0.28, "b", "y", "vss"),
        ]
        pmos = [
            Device("mp1", "p", 0.88, 0.28, "a", "y", "vdd"),
            Device("mp2", "p", 0.60, 0.28, "b", "y", "vdd"),
        ]
        nmos_end = mos_row._place_row(canvas, nmos, 1.0, 0.0, terminals)[0]
        self.assertAlmostEqual(nmos_end, 4.0, delta=TOL)
        pmos_x0 = nmos_end + 3.0  # the gap build_cell applies
        mos_row._place_row(canvas, pmos, 1.0, pmos_x0, terminals)

        xs = [x for points in terminals.values() for x, _ in points]
        self.assertEqual(len(xs), 12)  # 4 devices x (source, gate, drain)
        self.assertEqual(len({round(x, 6) for x in xs}), 12)
        self.assertAlmostEqual(min(x for x, _ in terminals["vdd"]), 7.0, delta=TOL)


class TerminalTests(GeometryCase):
    def test_stack_is_centered_and_sized(self):
        canvas = mos_row._Canvas()
        terminals = defaultdict(list)
        mos_row._terminal(canvas, terminals, "n1", 2.0, 3.0)

        self.assertEqual(
            [(r.layer, r.datatype) for r in canvas.rects],
            [CONTACT, METAL1, VIA1, METAL2, VIA2],
        )
        self.assertRects(on_layer(canvas.rects, CONTACT), [(1.89, 2.89, 2.11, 3.11)])
        self.assertRects(on_layer(canvas.rects, METAL1), [(1.80, 2.80, 2.20, 3.20)])
        self.assertRects(on_layer(canvas.rects, VIA1), [(1.87, 2.87, 2.13, 3.13)])
        self.assertRects(on_layer(canvas.rects, METAL2), [(1.84, 2.84, 2.16, 3.16)])
        self.assertRects(on_layer(canvas.rects, VIA2), [(1.87, 2.87, 2.13, 3.13)])
        self.assertEqual(canvas.labels, [])

    def test_conductors_enclose_cuts(self):
        canvas = mos_row._Canvas()
        mos_row._terminal(canvas, defaultdict(list), "n1", -1.5, 0.25)
        contact = on_layer(canvas.rects, CONTACT)[0]
        m1 = on_layer(canvas.rects, METAL1)[0]
        via1 = on_layer(canvas.rects, VIA1)[0]
        m2 = on_layer(canvas.rects, METAL2)[0]
        via2 = on_layer(canvas.rects, VIA2)[0]
        self.assertTrue(encloses(m1, contact, 0.07))
        self.assertTrue(encloses(m1, via1, 0.0))
        self.assertTrue(encloses(m2, via1, 0.01))
        self.assertTrue(encloses(m2, via2, 0.01))
        # Cuts are fixed squares of the documented sizes.
        self.assertAlmostEqual(contact[2] - contact[0], 0.22, delta=TOL)
        self.assertAlmostEqual(via1[2] - via1[0], 0.26, delta=TOL)
        self.assertAlmostEqual(via2[3] - via2[1], 0.26, delta=TOL)

    def test_records_positions_per_net(self):
        canvas = mos_row._Canvas()
        terminals = defaultdict(list)
        mos_row._terminal(canvas, terminals, "n1", 2.0, 3.0)
        mos_row._terminal(canvas, terminals, "n1", 4.0, 5.0)
        mos_row._terminal(canvas, terminals, "n2", 6.0, 7.0)
        self.assertEqual(dict(terminals), {"n1": [(2.0, 3.0), (4.0, 5.0)], "n2": [(6.0, 7.0)]})
        self.assertEqual(len(canvas.rects), 15)


class RouteNetsTests(GeometryCase):
    PINS = ["a", "missing", "b"]
    CHANNEL_Y0 = 5.0

    def routed(self):
        canvas = mos_row._Canvas()
        terminals = {
            "a": [(0.0, 1.0), (2.0, 1.0)],
            "b": [(4.0, 1.5)],  # singleton declared pin
            "zint": [(6.0, 1.0), (8.0, 1.0)],  # internal nets, sorted after pins
            "aint": [(10.0, 1.0)],
        }
        mos_row._route_nets(canvas, terminals, self.PINS, self.CHANNEL_Y0)
        return canvas, terminals

    def test_trunks_in_pin_then_sorted_internal_order_with_distinct_y(self):
        canvas, _ = self.routed()
        # Index 1 belongs to the missing pin and keeps its slot (5.65 unused).
        # Trunks: a=5.00, b=6.30, aint=6.95, zint=7.60.
        self.assertRects(
            on_layer(canvas.rects, METAL2),
            [
                (-0.15, 4.85, 2.15, 5.15),  # a: terminals 0..2, runout 0.15
                (3.68, 6.15, 4.32, 6.45),  # b: singleton padded to min width then runout
                (9.68, 6.80, 10.32, 7.10),  # aint: singleton, padded like b
                (5.85, 7.45, 8.15, 7.75),  # zint
            ],
        )
        ys = [round((r[1] + r[3]) / 2, 6) for r in on_layer(canvas.rects, METAL2)]
        self.assertEqual(len(set(ys)), len(ys))

    def test_one_riser_and_trunk_via_per_terminal(self):
        canvas, terminals = self.routed()
        trunk_y = {"a": 5.0, "b": 6.3, "aint": 6.95, "zint": 7.6}
        risers = on_layer(canvas.rects, METAL3)
        vias = on_layer(canvas.rects, VIA2)
        expected_risers = []
        expected_vias = []
        for net in ("a", "b", "aint", "zint"):
            for x, y in terminals[net]:
                lo, hi = sorted((y, trunk_y[net]))
                expected_risers.append((x - 0.15, lo - 0.15, x + 0.15, hi + 0.15))
                expected_vias.append(centered(x, trunk_y[net], 0.26))
        self.assertRects(risers, expected_risers)
        self.assertRects(vias, expected_vias)
        self.assertEqual(len(risers), 6)
        self.assertEqual(len(vias), 6)

    def test_trunks_and_risers_enclose_endpoint_vias(self):
        canvas, terminals = self.routed()
        trunk_y = {"a": 5.0, "b": 6.3, "aint": 6.95, "zint": 7.6}
        trunks = {
            round((r[1] + r[3]) / 2, 6): r for r in on_layer(canvas.rects, METAL2)
        }
        risers = on_layer(canvas.rects, METAL3)
        i = 0
        for net in ("a", "b", "aint", "zint"):
            trunk = trunks[round(trunk_y[net], 6)]
            for x, y in terminals[net]:
                riser = risers[i]
                i += 1
                trunk_via = centered(x, trunk_y[net], 0.26)
                terminal_via = centered(x, y, 0.26)
                self.assertTrue(encloses(trunk, trunk_via, 0.01), net)
                self.assertTrue(encloses(riser, trunk_via, 0.01), net)
                self.assertTrue(encloses(riser, terminal_via, 0.01), net)
        self.assertEqual(i, len(risers))

    def test_labels_only_for_populated_declared_pins(self):
        canvas, _ = self.routed()
        got = [(l.layer, l.texttype, l.x, l.y, l.text) for l in canvas.labels]
        self.assertEqual([g[4] for g in got], ["a", "b"])
        self.assertEqual([(g[0], g[1]) for g in got], [METAL2_LABEL, METAL2_LABEL])
        self.assertAlmostEqual(got[0][2], 1.0, delta=TOL)  # trunk a centre
        self.assertAlmostEqual(got[0][3], 5.0, delta=TOL)
        self.assertAlmostEqual(got[1][2], 4.0, delta=TOL)  # trunk b centre
        self.assertAlmostEqual(got[1][3], 6.3, delta=TOL)
        texts = {l.text for l in canvas.labels}
        self.assertNotIn("missing", texts)
        self.assertNotIn("zint", texts)
        self.assertNotIn("aint", texts)

    def test_missing_declared_pin_does_not_raise_and_adds_nothing(self):
        canvas = mos_row._Canvas()
        terminals = {"b": [(4.0, 1.5)]}
        mos_row._route_nets(canvas, terminals, ["missing", "b"], 5.0)
        # "b" keeps index 1, so its trunk sits one pitch above channel_y0.
        self.assertRects(on_layer(canvas.rects, METAL2), [(3.68, 5.50, 4.32, 5.80)])
        self.assertEqual([l.text for l in canvas.labels], ["b"])
        self.assertAlmostEqual(canvas.labels[0].y, 5.65, delta=TOL)

    def test_empty_terminal_list_for_declared_pin_is_skipped(self):
        canvas = mos_row._Canvas()
        mos_row._route_nets(canvas, {"a": []}, ["a"], 5.0)
        self.assertEqual(canvas.rects, [])
        self.assertEqual(canvas.labels, [])

    def test_empty_terminal_map(self):
        canvas = mos_row._Canvas()
        mos_row._route_nets(canvas, {}, ["a", "b"], 5.0)
        self.assertEqual(canvas.rects, [])
        self.assertEqual(canvas.labels, [])
        canvas = mos_row._Canvas()
        mos_row._route_nets(canvas, {}, [], 5.0)
        self.assertEqual(canvas.rects, [])
        self.assertEqual(canvas.labels, [])

    def test_internal_only_nets_are_routed_without_labels(self):
        canvas = mos_row._Canvas()
        terminals = {"n2": [(1.0, 1.0)], "n1": [(3.0, 1.0)]}
        mos_row._route_nets(canvas, terminals, [], 2.0)
        # Sorted: n1 at 2.00, n2 at 2.65.
        self.assertRects(
            on_layer(canvas.rects, METAL2),
            [(2.68, 1.85, 3.32, 2.15), (0.68, 2.50, 1.32, 2.80)],
        )
        self.assertEqual(canvas.labels, [])


class BuildCellTests(GeometryCase):
    PINS = ["a", "y", "vss", "vdd"]
    NMOS = [Device("mn1", "n", 0.30, 0.28, "a", "y", "vss")]
    PMOS = [Device("mp1", "p", 0.88, 0.28, "a", "y", "vdd")]

    def build(self, nmos, pmos, name="out.gds"):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / name)
            with mock.patch.object(
                mos_row, "write_gds", wraps=mos_row.write_gds
            ) as spy:
                data = mos_row.build_cell("CELL", self.PINS, nmos, pmos, path)
            written = Path(path).read_bytes()
        self.assertEqual(spy.call_count, 1)
        return data, written, spy.call_args

    @staticmethod
    def structure(call_args):
        structures = call_args.kwargs["structures"]
        assert len(structures) == 1
        return structures[0]

    def test_mixed_cell_bytes_and_determinism(self):
        data, written, call = self.build(self.NMOS, self.PMOS)
        self.assertEqual(data, written)
        self.assertGreater(len(data), 100)
        data2, written2, _ = self.build(self.NMOS, self.PMOS, name="again.gds")
        self.assertEqual(data, data2)
        self.assertEqual(written, written2)
        self.assertEqual(call.kwargs["library_name"], "CELL")
        self.assertEqual(self.structure(call)[0], "CELL")

    def test_mixed_cell_has_one_enclosing_nwell(self):
        _, _, call = self.build(self.NMOS, self.PMOS)
        rects = self.structure(call)[1]
        nwells = on_layer(rects, NWELL)
        # PMOS row starts at 1.6 + 3.0 = 4.6 and ends at 6.2; comp is 0.56..1.44.
        self.assertRects(nwells, [(4.13, 0.31, 6.67, 1.69)])
        pmos_comp = on_layer(rects, COMP)[3]  # NMOS draws three comp rects first
        self.assertTrue(encloses(nwells[0], pmos_comp, 0.12))
        for comp in on_layer(rects, COMP)[:3]:  # NMOS diffusion stays outside the well
            self.assertLess(comp[2], nwells[0][0])

    def test_mixed_cell_labels_and_trunks(self):
        _, _, call = self.build(self.NMOS, self.PMOS)
        _, rects, labels = self.structure(call)
        # Channel starts 0.45 above the tallest landing top (2.14): 2.59.
        # Trunks, in pin order: a 2.59, y 3.24, vss 3.89, vdd 4.54.
        got = {l.text: (l.layer, l.texttype, l.x, l.y) for l in labels}
        self.assertEqual([l.text for l in labels], self.PINS)
        expected = {
            "a": (3.10, 2.59),  # gates at x 0.8 and 5.4
            "y": (3.90, 3.24),  # drains at x 1.6 and 6.2
            "vss": (0.00, 3.89),  # NMOS source only
            "vdd": (4.60, 4.54),  # PMOS source only
        }
        for text, (x, y) in expected.items():
            layer, texttype, lx, ly = got[text]
            self.assertEqual((layer, texttype), METAL2_LABEL)
            self.assertAlmostEqual(lx, x, delta=1e-9)
            self.assertAlmostEqual(ly, y, delta=1e-9)
        trunks = on_layer(rects, METAL2)[-4:]
        self.assertRects(
            trunks,
            [
                (0.65, 2.44, 5.55, 2.74),
                (1.45, 3.09, 6.35, 3.39),
                (-0.32, 3.74, 0.32, 4.04),
                (4.28, 4.39, 4.92, 4.69),
            ],
        )

    def test_nmos_only_cell_has_no_nwell(self):
        data, written, call = self.build(self.NMOS, [])
        self.assertEqual(data, written)
        _, rects, labels = self.structure(call)
        self.assertEqual(on_layer(rects, NWELL), [])
        self.assertEqual(len(on_layer(rects, COMP)), 3)
        # Only NMOS landing pads count: tops out at 1.92, so channel at 2.37.
        first_trunk = on_layer(rects, METAL2)[-3]  # trunk of "a", the first pin
        self.assertAlmostEqual((first_trunk[1] + first_trunk[3]) / 2, 2.37, delta=TOL)
        self.assertEqual({l.text for l in labels}, {"a", "y", "vss"})

    def test_nmos_only_bytes_differ_from_mixed(self):
        mixed, _, _ = self.build(self.NMOS, self.PMOS)
        nmos_only, _, _ = self.build(self.NMOS, [])
        self.assertNotEqual(mixed, nmos_only)


if __name__ == "__main__":
    unittest.main()
