#!/usr/bin/env python3
"""Unit tests for the row-placement and wiring geometry helpers in
`layout/blocks/combiner_sampler/build.py` and `layout/rings/ro_ring11/build.py`.

Both generators compute the placement and routing geometry that the committed
GDS and the post-layout extraction are built from. Their only other
protection is the `--check` regeneration comparison, which needs the PDK and
`klt`. These helpers are pure functions of module constants, so the tests here
need neither: a change to the row arithmetic or to a wiring shape fails a unit
test instead of surfacing as an opaque GDS-hash mismatch.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

LAYOUT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = LAYOUT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


comb = _load("layout_block_geometry_comb", LAYOUT_DIR / "blocks" / "combiner_sampler" / "build.py")
ring = _load("layout_block_geometry_ring", LAYOUT_DIR / "rings" / "ro_ring11" / "build.py")

EPS = 1e-9


def _comb_bbox(inst: str) -> dict:
    return comb.CELL_BBOX[comb.INSTANCE_CELL[inst]]


def _assert_row_gaps(case: unittest.TestCase, order, bboxes, offsets, gap) -> None:
    case.assertEqual(list(offsets), list(order))
    case.assertEqual(offsets[order[0]], 0.0)
    for prev, nxt in zip(order, order[1:]):
        prev_right = bboxes[prev]["x1"] + offsets[prev]
        next_left = bboxes[nxt]["x0"] + offsets[nxt]
        case.assertAlmostEqual(next_left - prev_right, gap, delta=EPS)


class CombinerRowOffsets(unittest.TestCase):
    def test_gap_between_neighbours(self):
        bboxes = {i: _comb_bbox(i) for i in comb.ROW_ORDER}
        _assert_row_gaps(self, comb.ROW_ORDER, bboxes, comb.row_offsets(), comb.ROW_GAP_UM)

    def test_gap_follows_row_gap_constant(self):
        bboxes = {i: _comb_bbox(i) for i in comb.ROW_ORDER}
        with mock.patch.object(comb, "ROW_GAP_UM", 3.5):
            offsets = comb.row_offsets()
        _assert_row_gaps(self, comb.ROW_ORDER, bboxes, offsets, 3.5)

    def test_single_cell_order(self):
        with mock.patch.object(comb, "ROW_ORDER", ["xa1"]):
            self.assertEqual(comb.row_offsets(), {"xa1": 0.0})


class CombinerRowBbox(unittest.TestCase):
    def test_x_is_shifted_extent_and_y_is_unshifted_union(self):
        offsets = comb.row_offsets()
        box = comb.row_bbox_um(offsets)
        boxes = [(_comb_bbox(i), offsets[i]) for i in comb.ROW_ORDER]
        self.assertAlmostEqual(box["x0"], min(b["x0"] + o for b, o in boxes), delta=EPS)
        self.assertAlmostEqual(box["x1"], max(b["x1"] + o for b, o in boxes), delta=EPS)
        self.assertEqual(box["y0"], min(b["y0"] for b, _ in boxes))
        self.assertEqual(box["y1"], max(b["y1"] for b, _ in boxes))

    def test_x_extent_uses_offsets_given(self):
        offsets = {i: 0.0 for i in comb.ROW_ORDER}
        offsets[comb.ROW_ORDER[-1]] = 100.0
        box = comb.row_bbox_um(offsets)
        self.assertAlmostEqual(
            box["x1"], _comb_bbox(comb.ROW_ORDER[-1])["x1"] + 100.0, delta=EPS
        )


class CombinerWiring(unittest.TestCase):
    def setUp(self):
        self.offsets = comb.row_offsets()
        self.box = comb.row_bbox_um(self.offsets)

    def test_terminals_reference_known_instances(self):
        self.assertEqual(set(comb.ROW_ORDER), set(comb.INSTANCE_CELL))
        self.assertEqual(set(comb.ROW_ORDER), set(comb.INSTANCE_NETS))
        for net in comb.ROUTED_NETS:
            expected = sum(
                1 for i in comb.ROW_ORDER for n in comb.INSTANCE_NETS[i].values() if n == net
            )
            self.assertEqual(len(comb._net_terminals(net, self.offsets)), expected, net)

    def test_terminal_gap_slot_is_right_of_own_instance(self):
        for net in comb.ROUTED_NETS:
            for pin_x, gap_x, _y, _stub in comb._net_terminals(net, self.offsets):
                self.assertGreater(gap_x, pin_x, net)

    def test_every_routed_net_has_terminals_and_shapes(self):
        for net in comb.ROUTED_NETS:
            self.assertGreaterEqual(len(comb._net_terminals(net, self.offsets)), 2, net)
        # One trunk per net on its own track: a Metal2 rect at that track's Y.
        shapes = comb._wiring_shapes(self.offsets)
        for index, net in enumerate(comb.ROUTED_NETS):
            track_y = comb.TRACK_FLOOR_UM + index * comb.TRACK_PITCH_UM
            trunks = [
                s for s in shapes
                if s["layer"] == comb.METAL2
                and abs((s["rect_um"][1] + s["rect_um"][3]) / 2 - track_y) < EPS
            ]
            self.assertTrue(trunks, net)

    def test_shapes_well_formed_and_inside_bbox_plus_margin(self):
        margin = comb.GAP_MARGIN_UM + len(comb.ROUTED_NETS) * comb.GAP_SLOT_PITCH_UM
        y_top = comb.TRACK_FLOOR_UM + len(comb.ROUTED_NETS) * comb.TRACK_PITCH_UM
        shapes = comb._wiring_shapes(self.offsets)
        self.assertTrue(shapes)
        for s in shapes:
            x0, y0, x1, y1 = s["rect_um"]
            self.assertGreaterEqual(x1 - x0, 0.0, s)
            self.assertGreaterEqual(y1 - y0, 0.0, s)
            self.assertGreaterEqual(x0, self.box["x0"] - EPS, s)
            self.assertLessEqual(x1, self.box["x1"] + margin + EPS, s)
            self.assertGreaterEqual(y0, self.box["y0"] - EPS, s)
            self.assertLessEqual(y1, y_top + EPS, s)


class RingRowOffsets(unittest.TestCase):
    def setUp(self):
        self.bboxes, self.locals_ = ring._bboxes_and_locals()

    def test_gap_between_neighbours(self):
        offsets = ring.row_offsets(ring.ROW_ORDER, self.bboxes)
        _assert_row_gaps(self, ring.ROW_ORDER, self.bboxes, offsets, ring.ROW_GAP_UM)

    def test_gap_follows_row_gap_constant(self):
        with mock.patch.object(ring, "ROW_GAP_UM", 3.5):
            offsets = ring.row_offsets(ring.ROW_ORDER, self.bboxes)
        _assert_row_gaps(self, ring.ROW_ORDER, self.bboxes, offsets, 3.5)

    def test_single_cell_order(self):
        self.assertEqual(ring.row_offsets(["xg"], self.bboxes), {"xg": 0.0})


class RingWiring(unittest.TestCase):
    def setUp(self):
        self.bboxes, self.locals_ = ring._bboxes_and_locals()
        self.offsets = ring.row_offsets(ring.ROW_ORDER, self.bboxes)

    def test_tables_cover_row_order(self):
        self.assertEqual(set(ring.ROW_ORDER), set(self.bboxes))
        self.assertEqual(set(ring.ROW_ORDER), set(self.locals_))

    def test_shapes_well_formed_and_inside_bbox_plus_margin(self):
        x0 = min(self.bboxes[i]["x0"] + self.offsets[i] for i in ring.ROW_ORDER)
        x1 = max(self.bboxes[i]["x1"] + self.offsets[i] for i in ring.ROW_ORDER)
        y_lo = min(b["y0"] for b in self.bboxes.values())
        y_hi = max(ring.WRAP_TRACK[1], max(b["y1"] for b in self.bboxes.values()), ring.NAND_Y_WAYPOINTS[-1][1])
        shapes = ring._wiring_shapes(self.offsets, self.locals_)
        self.assertTrue(shapes)
        rail_margin = 1.0  # the vddr/vss Metal2 rails overhang the row by 1um
        for s in shapes:
            sx0, sy0, sx1, sy1 = s["rect_um"]
            self.assertGreaterEqual(sx1 - sx0, 0.0, s)
            self.assertGreaterEqual(sy1 - sy0, 0.0, s)
            self.assertGreaterEqual(sx0, x0 - rail_margin - EPS, s)
            self.assertLessEqual(sx1, x1 + rail_margin + EPS, s)
            self.assertGreaterEqual(sy0, y_lo - EPS, s)
            self.assertLessEqual(sy1, y_hi + ring.STUB_W + EPS, s)

    def test_every_ring_link_has_a_horizontal_jog_on_its_track(self):
        shapes = ring._wiring_shapes(self.offsets, self.locals_)
        tracks = [(s["rect_um"][1], s["rect_um"][3]) for s in shapes if s["layer"] == ring.METAL1]
        n = len(ring.ROW_ORDER)
        for track, want in ((ring.SHORT_TRACK, n - 1), (ring.WRAP_TRACK, 1)):
            got = sum(
                1 for y0, y1 in tracks
                if abs(y0 - track[0]) < EPS and abs(y1 - track[1]) < EPS
            )
            self.assertGreaterEqual(got, want, track)


class RowOffsetsAgree(unittest.TestCase):
    def test_same_bboxes_give_same_offsets(self):
        bboxes = {i: _comb_bbox(i) for i in comb.ROW_ORDER}
        with mock.patch.object(ring, "ROW_GAP_UM", comb.ROW_GAP_UM):
            ring_offsets = ring.row_offsets(comb.ROW_ORDER, bboxes)
        self.assertEqual(ring_offsets, comb.row_offsets())


if __name__ == "__main__":
    unittest.main()
