#!/usr/bin/env python3
"""Hold `layout/floorplan/interregion.py`'s drawn inter-region wiring to
phase 1's declared net list -- stdlib only, no `klt` and no PDK, so this
runs on every push (`npm run test:layout`) rather than only where the
layout flow itself can run.

Issue #222 (phase 2 of #219) draws the geometry; `layout/floorplan/
floorplan.py`'s own `check_interregion()` verifies it the expensive way,
with `klt extract` + `klt lvs` over the composed stream. That check needs
`klt` and the PDK, so on an ordinary CI runner it does not run at all --
which is exactly the gap this file exists to cover. Everything here is
derived from committed artefacts:

* `design/floorplan_netlist.py` -- the declared net list itself.
* `layout/floorplan/reports/compose.json` -- the committed composition
  request, which is where each region's own placed origin comes from. Using
  it (rather than recomputing offsets from guard-ring geometry, which needs
  `klt`) also means a regression that drops the wiring block out of the
  composition fails *here*, in CI, instead of only in the full flow.

The check this file exists for is the one a reviewer cannot do by eye: that
no two of the drawn nets' shapes come within the deck's own metal spacing of
each other on the same layer. That is a short -- the failure mode
phase 1 names explicitly for `vddr1`/`vddr2` ("no shared strap segment
anywhere") -- and it is caught here by arithmetic over the drawn rectangles,
with no tool in the loop.
"""

from __future__ import annotations

import json
import sys
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "design"))

import floorplan_netlist  # noqa: E402
from layout.floorplan import floorplan  # noqa: E402
from layout.floorplan import interregion  # noqa: E402

COMPOSE_REPORT = REPO_ROOT / "layout" / "floorplan" / "reports" / "compose.json"


def _composition() -> dict:
    return json.loads(COMPOSE_REPORT.read_text())["request"]


def _content_origins() -> dict[str, dict]:
    """Each region's own *content* origin, out of the committed composition
    request -- the same `origins_um` entries `floorplan.py`'s own `compose()`
    computed and handed to `interregion.wiring_plan()`."""
    origins_um = _composition()["placement"]["origins_um"]
    return {
        rid: origins_um[f"{rid}_ring"]
        for rid in floorplan_netlist.REGION_ORDER
        if f"{rid}_ring" in origins_um
    }


def _combiner_sampler_east_edge(origins: dict[str, dict]) -> float:
    """`combiner_sampler`'s own content bbox `x1`, in its local frame.

    The composition report's own placed guard-ring bbox gives it without a
    GDS read: the content sits `GUARD_RING_WIDTH_UM` inside the guarded
    region's east edge. (The next region is no longer the neighbour to the
    east -- `digital` is stacked above the strip -- so the region's own
    placed bbox is the only source.)
    """
    blocks = json.loads(COMPOSE_REPORT.read_text())["response"]["blocks"]
    guard = next(b for b in blocks if b["id"] == "combiner_sampler")["bbox_um"]
    east_edge_composed = guard["x1"] - 1.0   # placed bbox is composed-frame; GUARD_RING_WIDTH_UM
    return round(east_edge_composed - origins["combiner_sampler"]["x"], 4)


def _plan() -> dict:
    origins = _content_origins()
    east = _combiner_sampler_east_edge(origins)
    bboxes = {"combiner_sampler": {"x0": -0.5, "y0": -0.3, "x1": east, "y1": 0.0}}
    return interregion.wiring_plan(origins, bboxes)


def _rects_by_net(plan: dict) -> dict[str, list[tuple[tuple[int, int], list[float]]]]:
    grouped: dict[str, list] = {}
    for shape in plan["shapes"]:
        key = (shape["layer"][0], shape["layer"][1])
        grouped.setdefault(shape["_net"], []).append((key, shape["rect_um"]))
    return grouped


def _gap(a: list[float], b: list[float]) -> float:
    """Euclidean-ish separation between two axis-aligned rectangles: the
    larger of the X and Y gaps, negative when they overlap."""
    dx = max(b[0] - a[2], a[0] - b[2])
    dy = max(b[1] - a[3], a[1] - b[3])
    if dx >= 0 and dy >= 0:
        return max(dx, dy)
    return max(dx, dy)


class DrawnNetsMatchTheDeclaration(unittest.TestCase):
    def test_every_declared_net_is_drawn(self):
        """No declared net is silently dropped. `drawn_nets()` filters
        nothing, so the two name sets match by construction; what this
        guards is that they keep matching -- the equality fails if a filter
        is ever reintroduced there, and a net phase 1 declares but this
        module cannot wire (no `endpoints`, or an endpoint with no anchor)
        makes `wiring_plan()` raise here instead of quietly shipping a
        floorplan missing that net."""
        declared = {net["name"] for net in floorplan_netlist.INTER_REGION_NETS}
        drawn = {route["net"] for route in _plan()["routes"]}
        self.assertEqual(declared, drawn)

    def test_every_declared_endpoint_gets_a_riser(self):
        for route in _plan()["routes"]:
            declared = next(
                net for net in floorplan_netlist.INTER_REGION_NETS
                if net["name"] == route["net"]
            )
            self.assertEqual(
                [tuple(e) for e in declared["endpoints"]],
                [(e["region"], e["pin"]) for e in route["endpoints"]],
                f"net {route['net']}",
            )


class NoTwoNetsTouch(unittest.TestCase):
    """The short check. Two different nets' shapes on the same drawn layer
    must stay at least `interregion.MIN_SPACE` apart."""

    def test_no_two_drawn_nets_come_within_min_space(self):
        grouped = _rects_by_net(_plan())
        names = sorted(grouped)
        offenders: list[str] = []
        for i, left in enumerate(names):
            for right in names[i + 1:]:
                for layer_a, rect_a in grouped[left]:
                    for layer_b, rect_b in grouped[right]:
                        if layer_a != layer_b:
                            continue
                        gap = _gap(rect_a, rect_b)
                        if gap < interregion.MIN_SPACE:
                            offenders.append(
                                f"{left} {rect_a} vs {right} {rect_b} on "
                                f"{layer_a}: {gap:.3f} um"
                            )
        self.assertEqual(offenders, [], "\n".join(offenders[:20]))

    def test_the_four_supply_branches_share_no_conductor(self):
        """Phase 1's own DO-NOT-MERGE invariant, restated over drawn
        geometry: `vddr1`/`vddr2`/`vdd`/`vddd` must not share a single
        rectangle, and their trunks must be on distinct lanes. `vddd` joined
        the drawn set in gf180-trng#224 (previously it had no drawn wire at
        all)."""
        plan = _plan()
        grouped = _rects_by_net(plan)
        supplies = [name for name in ("vddr1", "vddr2", "vdd", "vddd") if name in grouped]
        self.assertEqual(len(supplies), 4)
        trunks = {
            route["net"]: route["trunk_y_um"] for route in plan["routes"]
            if route["net"] in supplies
        }
        self.assertEqual(len(set(trunks.values())), 4, trunks)


class TrunkLanes(unittest.TestCase):
    def test_every_trunk_is_below_the_row_and_on_its_own_lane(self):
        routes = _plan()["routes"]
        ys = [route["trunk_y_um"] for route in routes]
        self.assertEqual(len(set(ys)), len(ys), "two nets share a trunk lane")
        for route in routes:
            self.assertLess(
                route["trunk_y_um"] + interregion.WIRE_W / 2, 0.0,
                f"net {route['net']}'s trunk is not clear of the row's own floor",
            )

    def test_clk_and_rst_n_never_run_west_of_the_combiner_sampler_region(self):
        """DR-0012's routing constraint, carried over from phase 1: the
        sample clock (and the reset that shares its placement constraint)
        must reach the samplers from the `digital` side, never across a
        ring's own isolation channel."""
        west_limit = _content_origins()["combiner_sampler"]["x"]
        for route in _plan()["routes"]:
            if route["net"] not in ("clk", "rst_n"):
                continue
            self.assertGreaterEqual(
                route["trunk_x_um"][0], west_limit,
                f"net {route['net']} runs west of the combiner_sampler region",
            )


class StackedDigitalSupplyTie(unittest.TestCase):
    """gf180-trng#803: `digital` is stacked above the analog strip and its
    `vddd`/`vss` ties run on the stack's east flank."""

    def setUp(self):
        self.plan = _plan()
        self.origins = _content_origins()
        self.cs_east = (_combiner_sampler_east_edge(self.origins)
                        + self.origins["combiner_sampler"]["x"])
        self.routes = {r["net"]: r for r in self.plan["routes"]}

    def _pdn_endpoint(self, net):
        return next(e for e in self.routes[net]["endpoints"] if e["region"] == "digital")

    def test_digital_sits_above_the_analog_strip(self):
        origins = _composition()["placement"]["origins_um"]
        blocks = {b["id"]: b["bbox_um"]
                  for b in json.loads(COMPOSE_REPORT.read_text())["response"]["blocks"]}
        strip_top = max(blocks[r]["y1"] + origins[r]["y"]
                        for r in ("ring1", "ring2", "combiner_sampler"))
        self.assertGreaterEqual(
            origins["digital"]["y"] - strip_top, floorplan.ISOLATION_CHANNEL_UM - 1e-6)

    def test_pdn_risers_are_east_of_the_whole_strip(self):
        """Unconditional: the `vddd`/`vss` ties dock on the stack's east
        flank whatever the signal pins do (gf180-trng#803)."""
        for net in ("vddd", "vss"):
            x = self._pdn_endpoint(net)["riser_x_um"]
            self.assertGreater(x, self.cs_east, f"{net} PDN riser is not east of the strip")

    def test_pdn_risers_clear_every_wrap_column(self):
        """Conditional on there being wrap columns at all: only a *top*-edge
        signal pin wraps around the east flank, and which edge the committed
        DEF places those six on is the P&R run's business
        (`_committed_pin_edges`). With bottom-edge pins no wrap column
        exists, so there is nothing for the PDN riser to clear -- asserted
        as the two possibilities, never skipped silently."""
        wrap_x = [
            e["riser_x_um"] for r in self.routes.values() for e in r["endpoints"]
            if e["region"] == "digital" and e["anchor"] == "digital_pin_top"
        ]
        self.assertEqual(bool(wrap_x), bool(_committed_top_edge_nets()))
        if not wrap_x:
            return
        last_wrap = max(wrap_x)
        for net in ("vddd", "vss"):
            x = self._pdn_endpoint(net)["riser_x_um"]
            self.assertGreaterEqual(
                x - interregion.PDN_RISER_W_UM / 2 - (last_wrap + interregion.WIRE_W / 2),
                interregion.MIN_SPACE, f"{net} PDN riser is too close to a wrap column")

    def test_pdn_risers_are_wide_and_multi_cut(self):
        for net in ("vddd", "vss"):
            shapes = [sh for sh in self.plan["shapes"] if sh["_net"] == net]
            risers = [sh for sh in shapes
                      if tuple(sh["layer"]) == tuple(interregion.METAL3)
                      and sh["rect_um"][2] - sh["rect_um"][0] > 1.0]
            self.assertEqual(len(risers), 1, net)
            tagged = {}
            for sh in shapes:
                if "_array" in sh:
                    tagged.setdefault(sh["_array"], []).append(sh)
            counts = {k: len(v) for k, v in tagged.items()}
            self.assertEqual(counts, {
                "pdn-via3-trunk": interregion.PDN_VIA_COLS,
                "pdn-via3-top": interregion.PDN_VIA_COLS ** 2,
                "pdn-via4-top": interregion.PDN_VIA_COLS ** 2,
            }, net)

    def test_no_pdn_conductor_enters_a_ring_isolation_channel(self):
        """The argument recorded in layout/floorplan/README.md: nothing the
        PDN ties draw lies west of the strip's east edge, so none of it is in
        the `ring1 | ring2` or `ring2 | combiner_sampler` channels."""
        for net in ("vddd", "vss"):
            for sh in self.plan["shapes"]:
                if sh["_net"] != net:
                    continue
                x0, y0, x1, y1 = sh["rect_um"]
                wide = max(x1 - x0, y1 - y0) >= interregion.PDN_RISER_W_UM - 1e-6
                if "_array" not in sh and not (wide and min(x1 - x0, y1 - y0) >= 1.0):
                    continue                       # the net's own analog legs / trunk
                if tuple(sh["layer"]) == tuple(interregion.METAL5):
                    continue                       # the dock reaches into digital's own strap
                self.assertGreater(sh["rect_um"][0], self.cs_east, (net, sh))

    def test_clk_and_rst_n_stay_clear_of_both_ring_channels(self):
        """DR-0012-clock's rationale for the row-ordering guard, restated for
        the stack: the sample clock and reset reach the samplers from the
        `digital` side, never over a ring's guarded area or isolation
        channel.

        The bound is `combiner_sampler`'s own **west** edge, which is what
        `layout/floorplan/README.md` states ("both trunks are pinned east of
        `combiner_sampler`'s own west edge and never enter a ring's isolation
        channel") and what `TrunkLanes` asserts for the trunks. This test
        extends it to the `digital`-side riser, which the trunk reaches.

        Until #866 this asserted the strictly stronger "east of
        combiner_sampler's own *east* edge". That held only because the
        committed DEF then placed these pins on the top edge, so they wrapped
        around the east flank -- a property of that P&R run, not of the
        floorplan (`_committed_pin_edges`). A bottom-edge pin drops straight
        into the `combiner_sampler | digital` channel instead, which is east
        of both ring channels and is the case `interregion.py` has routed
        since gf180-trng#315. Asserting the east edge would have made the
        documented constraint unsatisfiable for an equally valid placement."""
        west_limit = self.origins["combiner_sampler"]["x"]
        for net in ("clk", "rst_n"):
            self.assertGreaterEqual(
                min(e["riser_x_um"] for e in self.routes[net]["endpoints"]
                    if e["region"] == "digital"), west_limit, net)

    def test_derived_east_edge_clears_the_combiner_sampler_columns(self):
        east = interregion.stack_digital_east_um(self.cs_east)
        first_wrap = east + interregion.EAST_RISER_CLEAR_UM
        last_cs = self.cs_east + max(interregion.CS_CHANNEL_RISER_X.values())
        self.assertGreaterEqual(first_wrap - last_cs - interregion.WIRE_W,
                                interregion.MIN_SPACE)


# Metal stack the connectivity check below walks: a via layer joins the two
# metals it sits between.
_VIA_JOINS = {(40, 0): ((42, 0), (46, 0)), (41, 0): ((46, 0), (81, 0))}
#: The six inter-region signal endpoints on the `digital` region, by their
#: DEF pin name and by the net each carries. Which block edge they sit on is
#: NOT part of this list -- see `_committed_pin_edges()`.
_SIGNAL_ENDPOINTS = ("clk", "rst_n", "raw_bit", "raw_valid", "ring_bit[0]", "ring_bit[1]")
_SIGNAL_NETS = ("clk", "rst_n", "raw_bit", "raw_valid", "ring_bit1", "ring_bit2")

#: Net carried by each signal endpoint, in the same order.
_NET_OF_ENDPOINT = dict(zip(_SIGNAL_ENDPOINTS, _SIGNAL_NETS))


def _committed_pin_edges() -> dict[str, str]:
    """Which block edge the committed DEF places each signal pin on.

    **This is read, never assumed.** `layout/digital/build.py` does not ask
    for a pin edge, and `layout/digital/README.md`'s own "The one command"
    section says placement and routing are "seeded but not byte-reproducible
    across `openroad` builds, thread counts or host architectures" -- so
    which edge `place_pins` lands these six on is a property of the
    *committed artefact*, not a design input. It has already flipped twice:
    bottom when gf180-trng#315 was filed, top after that issue's own
    re-place-and-route (commit `4fc111b0`), and bottom again when #866
    re-ran the chain under the nightly's pinned toolchain.

    `interregion.py` routes both edges by design (`digital_pin_edge`, and
    its "Bottom-edge pins keep the existing stub" path), so a flip is not a
    regression -- it is the supported case changing. What *is* asserted
    below is the invariant that survives a flip: every pin sits on an edge
    this module can route (`digital_pin_edge` raises otherwise), the drawn
    stub reaches it, DR-0012-clock's channel constraint still holds, and the
    committed report states exactly the legs the rules produce for that edge.
    """
    bbox = interregion.digital_die_bbox()
    positions = interregion.digital_pin_positions()
    return {pin: interregion.digital_pin_edge(positions[pin][1], bbox)
            for pin in _SIGNAL_ENDPOINTS}


def _committed_top_edge_nets() -> set[str]:
    """The signal nets whose committed `digital` pin is on the top edge --
    exactly the endpoints that get a stub/track/riser leg triple."""
    return {_NET_OF_ENDPOINT[pin] for pin, edge in _committed_pin_edges().items()
            if edge == "top"}


def _overlap_area(a: list[float], b: list[float]) -> float:
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w * h if w > 0 and h > 0 else 0.0


def _pin_rect(pin: str, origin: dict[str, float]) -> list[float]:
    """The pin's drawn Metal4 rectangle at the placed DEF coordinate."""
    lx, ly = interregion.digital_pin_positions()[pin]
    return [lx + origin["x"] - interregion.DIGITAL_PIN_W / 2,
            ly + origin["y"] - interregion.DIGITAL_PIN_H / 2,
            lx + origin["x"] + interregion.DIGITAL_PIN_W / 2,
            ly + origin["y"] + interregion.DIGITAL_PIN_H / 2]


def _connected(shapes: list[dict], pin_rect: list[float], trunk: dict) -> bool:
    """Is `pin_rect` (Metal4) joined to `trunk` through positive-area
    same-layer overlaps and via cuts that sit inside both adjacent metals?"""
    nodes = [((46, 0), pin_rect)] + [(tuple(sh["layer"]), sh["rect_um"]) for sh in shapes]
    parent = list(range(len(nodes)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, (la, ra) in enumerate(nodes):
        for j in range(i + 1, len(nodes)):
            lb, rb = nodes[j]
            area = _overlap_area(ra, rb)
            if not area:
                continue
            is_via_a, is_via_b = la in _VIA_JOINS, lb in _VIA_JOINS
            if is_via_a and is_via_b:
                continue
            if is_via_a:
                joined = lb in _VIA_JOINS[la]
            elif is_via_b:
                joined = la in _VIA_JOINS[lb]
            else:
                joined = la == lb
            if joined:
                parent[find(i)] = find(j)
    trunk_idx = next(k for k, (lay, r) in enumerate(nodes)
                     if k and lay == (46, 0) and r == trunk["rect_um"])
    return find(0) == find(trunk_idx)


class DigitalEndpointsFollowThePlacedPin(unittest.TestCase):
    """gf180-trng#315: the drawn stub must reach whichever block edge the
    committed DEF places each of the six `digital` signal pins on, wherever
    the block itself is placed."""

    def _plan_at(self, dx: float, dy: float) -> tuple[dict, dict]:
        origins = {rid: dict(o) for rid, o in _content_origins().items()}
        origins["digital"] = {"x": origins["digital"]["x"] + dx,
                              "y": origins["digital"]["y"] + dy}
        east = _combiner_sampler_east_edge(_content_origins())
        bboxes = {"combiner_sampler": {"x0": -0.5, "y0": -0.3, "x1": east, "y1": 0.0}}
        return interregion.wiring_plan(origins, bboxes), origins["digital"]

    def _check_all_joined(self, dx: float, dy: float) -> None:
        plan, origin = self._plan_at(dx, dy)
        for net in floorplan_netlist.INTER_REGION_NETS:
            for rid, pin in net.get("endpoints", ()):
                if rid != "digital" or pin not in _SIGNAL_ENDPOINTS:
                    continue
                shapes = [sh for sh in plan["shapes"] if sh["_net"] == net["name"]]
                trunk = next(sh for sh in shapes
                             if tuple(sh["layer"]) == (46, 0)
                             and sh["rect_um"][3] - sh["rect_um"][1] <= interregion.WIRE_W + 1e-9
                             and sh["rect_um"][2] - sh["rect_um"][0] > 5.0)
                self.assertTrue(_connected(shapes, _pin_rect(pin, origin), trunk),
                                f"{net['name']}/{pin} is not joined to its trunk")

    def test_the_committed_def_places_the_signal_pins_on_a_routable_edge(self):
        """`digital_pin_edge` raises on anything but the two edges this
        module routes, so resolving all six is the assertion -- which edge
        they landed on is the P&R run's business (`_committed_pin_edges`),
        not this file's."""
        edges = _committed_pin_edges()
        self.assertEqual(set(edges), set(_SIGNAL_ENDPOINTS))
        for pin, edge in edges.items():
            self.assertIn(edge, ("top", "bottom"), pin)

    def test_the_six_signal_pins_share_one_edge(self):
        """They are placed as one group by `place_pins`, and the stacked
        arrangement's wiring argument (`layout/floorplan/README.md`) reasons
        about them together. A split would mean half the nets take the
        east-flank wrap and half drop into the channel -- routable, but a
        topology nobody has reviewed."""
        self.assertEqual(len(set(_committed_pin_edges().values())), 1,
                         _committed_pin_edges())

    def test_every_top_edge_pin_is_joined_to_its_trunk(self):
        self._check_all_joined(0.0, 0.0)

    def test_translated_block_origin_stays_joined(self):
        self._check_all_joined(37.5, 11.25)

    def test_the_stub_overlaps_the_pin_with_positive_area(self):
        plan, origin = self._plan_at(0.0, 0.0)
        for pin in _SIGNAL_ENDPOINTS:
            rect = _pin_rect(pin, origin)
            hits = [sh for sh in plan["shapes"] if tuple(sh["layer"]) == (46, 0)
                    and _overlap_area(sh["rect_um"], rect) > 0]
            self.assertTrue(hits, f"no drawn Metal4 overlaps pin {pin}")

    def test_no_drawn_wire_enters_the_digital_block(self):
        """Every top-edge leg stays outside the block footprint except the
        pin overlap itself (Metal4 stub starting at the pin's centre)."""
        plan, origin = self._plan_at(0.0, 0.0)
        bbox = interregion.digital_die_bbox()
        x1 = origin["x"] + bbox["x1"]
        y1 = origin["y"] + bbox["y1"]
        for sh in plan["shapes"]:
            if tuple(sh["layer"]) not in ((81, 0), (40, 0)):
                continue
            r = sh["rect_um"]
            if r[0] >= origin["x"] and r[2] <= x1 and r[1] >= origin["y"] and r[3] <= y1 \
                    and sh["_net"] in ("clk", "rst_n", "raw_bit", "raw_valid",
                                    "ring_bit1", "ring_bit2"):
                self.fail(f"{sh['_net']} {r} inside digital's footprint")

    def test_bottom_edge_pins_are_still_supported(self):
        bbox = {"x0": 0.0, "y0": 0.0, "x1": 100.0, "y1": 100.0}
        self.assertEqual(interregion.digital_pin_edge(0.26, bbox), "bottom")
        with mock.patch.object(interregion, "digital_pin_positions",
                               return_value={p: (10.0 + i * 3, 0.26)
                                             for i, p in enumerate(_SIGNAL_ENDPOINTS)}):
            plan = interregion.wiring_plan(
                _content_origins(),
                {"combiner_sampler": {"x0": -0.5, "y0": -0.3, "x1": 50.0, "y1": 0.0},
                 "digital": bbox})
        anchors = {e["anchor"] for r in plan["routes"] for e in r["endpoints"]
                   if e["region"] == "digital" and e["pin"] in _SIGNAL_ENDPOINTS}
        self.assertEqual(anchors, {"digital_pin"})

    def test_a_mid_block_pin_is_rejected_before_any_geometry(self):
        with self.assertRaises(interregion.WiringError):
            interregion.digital_pin_edge(50.0, {"x0": 0.0, "y0": 0.0, "x1": 100.0, "y1": 100.0})


class TopEdgeLegsAreReported(unittest.TestCase):
    """gf180-trng#456: the Metal4 stub, Metal5 track and Metal3 flank riser
    of each top-edge endpoint are most of that net's drawn conductor, so the
    report states them, and a consumer prices them from the report."""

    _LAYER_KEY = {"metal4": (46, 0), "metal5": (81, 0), "metal3": (42, 0)}

    def _legs(self, plan: dict) -> dict[str, list[dict]]:
        return {r["net"]: e["legs"] for r in plan["routes"]
                for e in r["endpoints"] if "legs" in e}

    def test_only_top_edge_digital_endpoints_carry_legs(self):
        plan = _plan()
        legged = {(r["net"], e["pin"]) for r in plan["routes"]
                  for e in r["endpoints"] if "legs" in e}
        self.assertEqual({net for net, _ in legged}, _committed_top_edge_nets())
        for r in plan["routes"]:
            for e in r["endpoints"]:
                self.assertEqual("legs" in e, e["anchor"] == "digital_pin_top")

    def test_each_leg_is_the_length_of_the_rectangle_actually_drawn(self):
        """Measured off the emitted shapes, not off the formula that sizes them:
        the stub is the one Metal4 rectangle taller than wide, the track the
        one Metal5 rectangle wider than tall, the riser the Metal3 rectangle
        taller than wide, on that net."""
        plan = _plan()
        legs_by_net = self._legs(plan)
        if not legs_by_net:
            self.skipTest("the committed DEF places no signal pin on the top "
                          "edge, so no endpoint draws a stub/track/riser "
                          "triple to measure")
        riser_x = {r["net"]: e["riser_x_um"] for r in plan["routes"]
                   for e in r["endpoints"] if "legs" in e}
        for net, legs in legs_by_net.items():
            by_layer = {leg["layer"]: leg for leg in legs}
            self.assertEqual(set(by_layer), {"metal4", "metal5", "metal3"})
            shapes = [sh for sh in plan["shapes"] if sh["_net"] == net]

            def long_side(layer, vertical):
                found = []
                for sh in shapes:
                    if tuple(sh["layer"]) != self._LAYER_KEY[layer]:
                        continue
                    x0, y0, x1, y1 = sh["rect_um"]
                    w, h = x1 - x0, y1 - y0
                    # A net's other endpoint has its own Metal3 riser; this
                    # one is the riser standing on the east flank.
                    if layer == "metal3" and abs((x0 + x1) / 2 - riser_x[net]) > 1e-3:
                        continue
                    if vertical and h > 2 * w:
                        found.append(h)
                    if not vertical and w > 2 * h:
                        found.append(w)
                self.assertEqual(len(found), 1, f"{net} {layer}")
                return found[0]

            self.assertAlmostEqual(by_layer["metal4"]["length_um"],
                                   long_side("metal4", True), places=3)
            self.assertAlmostEqual(by_layer["metal5"]["length_um"],
                                   long_side("metal5", False), places=3)
            self.assertAlmostEqual(by_layer["metal3"]["length_um"],
                                   long_side("metal3", True), places=3)
            for leg in legs:
                self.assertEqual(leg["width_um"], interregion.WIRE_W)

    def test_the_committed_report_carries_the_legs_the_rules_produce(self):
        committed = json.loads((REPO_ROOT / "layout" / "floorplan" / "reports"
                                / "interregion.json").read_text())
        got = {r["net"]: e["legs"] for r in committed["routes"]
               for e in r["endpoints"] if "legs" in e}
        self.assertEqual(got, self._legs(_plan()))
        self.assertEqual(set(got), _committed_top_edge_nets())

    def test_bottom_edge_endpoints_report_no_legs(self):
        bbox = {"x0": 0.0, "y0": 0.0, "x1": 100.0, "y1": 100.0}
        with mock.patch.object(interregion, "digital_pin_positions",
                               return_value={p: (10.0 + i * 3, 0.26)
                                             for i, p in enumerate(_SIGNAL_ENDPOINTS)}):
            plan = interregion.wiring_plan(
                _content_origins(),
                {"combiner_sampler": {"x0": -0.5, "y0": -0.3, "x1": 50.0, "y1": 0.0},
                 "digital": bbox})
        self.assertEqual(self._legs(plan), {})


class CompositionCarriesTheWiring(unittest.TestCase):
    def test_the_committed_composition_places_the_wiring_block(self):
        request = _composition()
        ids = {block["id"] for block in request["blocks"]}
        self.assertIn(
            "trng_interregion", ids,
            "layout/floorplan/reports/compose.json no longer places the "
            "inter-region wiring block -- the four regions would be "
            "composed unconnected again (issue #222)",
        )
        self.assertIn("trng_interregion", request["placement"]["order"])


# --------------------------------------------------------------------------- #
# The composed top-level interface (gf180-trng#309)
# --------------------------------------------------------------------------- #

#: The five declared chip pins whose nets also carry a region cell's own
#: label, with the name klt 0.6.0 (klayout-tools#1687) reports each under.
#: Written out, not derived from `interregion`, so the table itself is checked.
JOINED_PINS = {
    "en1": "en|en1",
    "en2": "en|en2",
    "vdd": "d|vdd",
    "vddr1": "vddr|vddr1",
    "vddr2": "vddr|vddr2",
}

_MATCH = {"status": "match", "mismatch_count": 2, "category_counts": {"topology.flattened": 2}}


def _declared() -> list[str]:
    return floorplan._reference_top_pins(
        floorplan_netlist.LVS_REFERENCE_PATH, floorplan_netlist.TOP_CELL
    )


def _fake_extraction(declared: list[str], plan: dict, *, drop=(), extra=()) -> dict:
    """A hand-built `klt extract` report: one promoted net per declared pin
    under its joined name (what the 0.6.0 producer does), the drawn
    non-chip-pin nets joined to their cell labels but not promoted. `drop`
    removes promoted net names, `extra` adds more (name, pin?) nets. The
    pin count is the number of promoted nets -- never a literal."""
    nets = [
        {"name": interregion.extracted_net_name(pin), "pin": True}
        for pin in declared
    ]
    for route in plan["routes"]:
        if not route["chip_pin"]:
            nets.append({"name": f"q|{route['net']}", "pin": False})
    nets = [net for net in nets if net["name"] not in drop]
    nets.extend({"name": name, "pin": is_pin} for name, is_pin in extra)
    return {
        "status": "ok", "device_count": 196, "net_count": len(nets),
        "pin_count": sum(1 for net in nets if net["pin"]),
        "nets": nets, "abstracted_cells": [],
    }


class ComposedInterfaceExpectation(unittest.TestCase):
    """`floorplan.expected_interface`/`check_interregion` hold the composed
    extraction to the interface derived from the declaration -- exactly."""

    def setUp(self):
        self.declared = _declared()
        self.plan = _plan()

    def _check(self, extraction, lvs=_MATCH):
        with mock.patch.object(floorplan, "run_extract_composed", return_value=extraction), \
                mock.patch.object(floorplan, "run_lvs", return_value=lvs):
            return floorplan.check_interregion(self.plan)

    def test_the_five_joined_chip_pins_are_named_by_their_joined_labels(self):
        names, joined, problems = floorplan.expected_interface(self.declared)
        self.assertEqual(joined, JOINED_PINS)
        self.assertEqual(problems, [])
        for joined_name in JOINED_PINS.values():
            self.assertEqual(names[joined_name], 1)
        # every joined name is '|'-separated, never comma-separated
        self.assertTrue(all("," not in name for name in names))

    def test_the_expectation_counts_the_joined_pins_instead_of_subtracting_them(self):
        names, _, _ = floorplan.expected_interface(self.declared)
        # one promoted net per declared pin: 112 declared -> 112 expected,
        # not 107 (the superseded producers subtracted the five joined pins)
        self.assertEqual(sum(names.values()), len(self.declared))
        self.assertEqual(floorplan.DUPLICATE_PIN_NAME_PROMOTIONS, ())

    def test_a_promotion_adds_exactly_one_expected_net_of_that_name(self):
        names, _, _ = floorplan.expected_interface(self.declared, promotions=("vss",))
        self.assertEqual(names["vss"], 2)
        self.assertEqual(sum(names.values()), len(self.declared) + 1)

    def test_two_declared_pins_on_one_predicted_net_are_a_declaration_problem(self):
        with mock.patch.dict(interregion.REGION_CELL_LABELS, {"en1": ("en", "en2")}):
            _, _, problems = floorplan.expected_interface(self.declared)
        self.assertTrue(any("same net" in p for p in problems), problems)

    def test_the_normative_extraction_shape_passes_with_no_problems(self):
        check = self._check(_fake_extraction(self.declared, self.plan))
        self.assertEqual(check["problems"], [])
        self.assertEqual(check["expected_pin_count"], len(self.declared))
        self.assertEqual(check["extract"]["pin_count"], check["expected_pin_count"])
        self.assertEqual(check["joined_name_pins"], JOINED_PINS)

    def test_an_unexpected_extra_pin_fails_by_name(self):
        # a second net carrying `clk` -- an unjoined endpoint, not a promotion
        check = self._check(_fake_extraction(
            self.declared, self.plan, extra=[("clk", True), ("rst_n", True)]))
        text = "\n".join(check["problems"])
        self.assertIn("{'clk': 1, 'rst_n': 1}", text)
        self.assertIn(f"reports {len(self.declared) + 2} top-level pin(s)", text)
        # and the connectivity check sees the second carrier too
        self.assertIn("drawn net 'clk' is carried by 2", text)
        self.assertIn("drawn net 'rst_n' is carried by 2", text)

    def test_an_unknown_extra_pin_fails(self):
        check = self._check(_fake_extraction(
            self.declared, self.plan, extra=[("stray_label", True)]))
        self.assertTrue(any("stray_label" in p for p in check["problems"]))

    def test_an_omitted_joined_pin_fails_by_name(self):
        for joined_name in JOINED_PINS.values():
            with self.subTest(pin=joined_name):
                check = self._check(_fake_extraction(
                    self.declared, self.plan, drop={joined_name}))
                text = "\n".join(check["problems"])
                self.assertIn(f"{joined_name!r}", text)
                self.assertIn("did not promote", text)
                self.assertIn(f"reports {len(self.declared) - 1} top-level", text)

    def test_the_count_is_exact_even_when_the_names_agree(self):
        extraction = _fake_extraction(self.declared, self.plan)
        extraction["pin_count"] += 1
        check = self._check(extraction)
        self.assertTrue(any("top-level pin(s)" in p for p in check["problems"]))

    def test_a_legitimate_duplicate_promotion_is_accounted_exactly(self):
        extraction = _fake_extraction(self.declared, self.plan, extra=[("vss", True)])
        with mock.patch.object(floorplan, "DUPLICATE_PIN_NAME_PROMOTIONS", ("vss",)):
            check = self._check(extraction)
            self.assertEqual(check["problems"], [])
            self.assertEqual(check["expected_pin_count"], len(self.declared) + 1)
            # a third `vss` net is still caught
            three = _fake_extraction(
                self.declared, self.plan, extra=[("vss", True), ("vss", True)])
            self.assertTrue(self._check(three)["problems"])

    def test_several_labels_on_one_net_are_one_carrier(self):
        # `en|en1` carries two labels but is a single net for the route `en1`
        extraction = _fake_extraction(self.declared, self.plan)
        carriers = [n for n in extraction["nets"] if "en1" in n["name"].split("|")]
        self.assertEqual(len(carriers), 1)
        self.assertEqual(self._check(extraction)["problems"], [])

    def test_a_disconnected_route_still_fails(self):
        extraction = _fake_extraction(
            self.declared, self.plan, extra=[("raw_bit", False)])
        text = "\n".join(self._check(extraction)["problems"])
        self.assertIn("drawn net 'raw_bit' is carried by 2", text)

    # gf180-trng#315: `--def-net-names` names a net that contains `digital`'s
    # DEF-annotated routing by its DEF net name and drops the text labels.
    # Measured under klt 0.6.0 on the composed, routed floorplan: the joined
    # `ring_bit1`/`ring_bit2` nets came back as `ring_bit[0]`/`ring_bit[1]`
    # (no `ring_bit1`/`ring_bit2`/`q` component), and with `ring_bit[1]`'s
    # Metal4 stub deleted the same extraction split it into `ring_bit[1]`
    # and `q|ring_bit2`.

    @staticmethod
    def _def_named(extraction: dict) -> dict:
        renames = {"q|ring_bit1": "ring_bit[0]", "q|ring_bit2": "ring_bit[1]",
                   "q|raw_bit": "raw_bit", "q|raw_valid": "raw_valid"}
        for net in extraction["nets"]:
            net["name"] = renames.get(net["name"], net["name"])
        return extraction

    def test_route_labels_include_the_digital_def_net_name(self):
        nets = {net["name"]: net for net in interregion.drawn_nets()}
        self.assertEqual(interregion.route_net_labels(nets["ring_bit1"]),
                         {"ring_bit1", "ring_bit[0]"})
        self.assertEqual(interregion.route_net_labels(nets["ring_bit2"]),
                         {"ring_bit2", "ring_bit[1]"})
        self.assertEqual(interregion.route_net_labels(nets["clk"]), {"clk"})
        self.assertEqual(interregion.route_net_labels(nets["ro1"]), {"ro1"})
        # the wiring plan's own route records give the same answer
        route = next(r for r in self.plan["routes"] if r["net"] == "ring_bit2")
        self.assertEqual(
            interregion.route_net_labels({"name": "ring_bit2", "endpoints": route["endpoints"]}),
            {"ring_bit2", "ring_bit[1]"})

    def test_a_joined_net_named_by_its_def_net_is_one_carrier(self):
        check = self._check(self._def_named(_fake_extraction(self.declared, self.plan)))
        self.assertEqual(check["problems"], [])

    def test_an_unjoined_digital_endpoint_under_its_def_name_fails(self):
        extraction = self._def_named(_fake_extraction(self.declared, self.plan))
        for net in extraction["nets"]:
            if net["name"] == "ring_bit[1]":
                net["name"] = "q|ring_bit2"      # cs side + trunk
        extraction["nets"].append({"name": "ring_bit[1]", "pin": False})  # digital side
        text = "\n".join(self._check(extraction)["problems"])
        self.assertIn("drawn net 'ring_bit2' is carried by 2", text)

    def test_a_wrong_chip_pin_label_set_still_fails(self):
        extraction = _fake_extraction(self.declared, self.plan)
        for net in extraction["nets"]:
            if net["name"] == "en|en1":
                net["name"] = "en|en1|zz"
        text = "\n".join(self._check(extraction)["problems"])
        self.assertIn("came back labelled", text)

    def test_merged_supply_branches_still_fail(self):
        extraction = _fake_extraction(self.declared, self.plan)
        for net in extraction["nets"]:
            if net["name"] == "vddd":
                net["name"] = "vdd|vddd"
        text = "\n".join(self._check(extraction)["problems"])
        self.assertIn("two supply-branch labels", text)

    def test_an_unexpected_lvs_category_still_fails(self):
        lvs = {"status": "match", "mismatch_count": 1,
               "category_counts": {"net.split": 1}}
        text = "\n".join(self._check(
            _fake_extraction(self.declared, self.plan), lvs)["problems"])
        self.assertIn("composed LVS", text)

    def test_compare_interface_reports_extras_and_omissions_together(self):
        expected = Counter({"a": 1, "b": 1})
        report = {"nets": [{"name": "a", "pin": True}, {"name": "c", "pin": True}]}
        text = "\n".join(floorplan.compare_interface(report, expected, 2))
        self.assertIn("{'c': 1}", text)
        self.assertIn("{'b': 1}", text)


if __name__ == "__main__":
    unittest.main()
