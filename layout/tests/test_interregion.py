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
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "design"))

import floorplan_netlist  # noqa: E402
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

    The composed row's own arithmetic gives it without a GDS read: the next
    region's guard ring starts one isolation channel past this region's
    guarded east edge, and the content sits `GUARD_RING_WIDTH_UM` inside
    that edge.
    """
    origins_um = _composition()["placement"]["origins_um"]
    guard_x = origins_um["combiner_sampler"]["x"]
    next_guard_x = origins_um["digital"]["x"]
    guarded_w = next_guard_x - guard_x - 20.0   # ISOLATION_CHANNEL_UM
    east_edge_composed = guard_x + guarded_w - 1.0   # GUARD_RING_WIDTH_UM
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
    def test_every_declared_net_with_endpoints_is_drawn(self):
        declared = {
            net["name"] for net in floorplan_netlist.INTER_REGION_NETS
            if net.get("endpoints") and net["layer_role"] != "guard_ring_tap"
        }
        drawn = {route["net"] for route in _plan()["routes"]}
        self.assertEqual(declared, drawn)

    def test_vsubs_is_not_drawn(self):
        """`vsubs` is declared by phase 1 but deliberately carries no drawn
        wire: it is the guard rings' own substrate tap, not a metal route at
        all. `vddd` used to be excluded here too (its only connection was
        into `digital`'s SPECIALNETS-only PDN, which the phase-1 reference
        this layout was LVS'd against could not express) -- gf180-trng#224
        promoted `vddd`/`vss` to real `.SUBCKT trng_top` pins on `digital`'s
        own reference, so both are ordinary drawn endpoints now (see
        `test_every_declared_net_with_endpoints_is_drawn` above)."""
        drawn = {route["net"] for route in _plan()["routes"]}
        self.assertNotIn("vsubs", drawn)

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


if __name__ == "__main__":
    unittest.main()
