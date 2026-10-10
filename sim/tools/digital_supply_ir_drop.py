#!/usr/bin/env python3
"""Issue #464: DC voltage loss on the digital section's supply and return,
from the chip pin through the composed floorplan's docking path and into
the placed power grid.

    python3 sim/tools/digital_supply_ir_drop.py             # the report
    python3 sim/tools/digital_supply_ir_drop.py --markdown  # the generated doc block
    python3 sim/tools/digital_supply_ir_drop.py --json      # the full result
    python3 sim/tools/digital_supply_ir_drop.py --check     # gate (no PDK, no klt)

Why a separate model
--------------------
`sim/tools/vss_trunk_ir_drop.py` (#234) is a series chain: one trunk
segment and one riser per analog tap. It deliberately leaves `digital` out
(its `SCOPED_OUT_REGIONS`), because that region's power grid is a mesh --
Metal1 follow-pin rails, Metal4 and Metal5 straps, and a via array at every
crossing -- and a chain would misstate it. This tool solves that mesh as a
resistor network (`sim/tools/_resistor_network.py`) joined to the external
docking path, and leaves the analog chain, its numbers and its coverage
exactly as they are.

What is modelled
----------------
For each of `vddd` and `vss`, one network, built from committed geometry and
nothing transcribed by hand:

- **External feed.** Every Metal3/Metal4/Metal5 rectangle and Via3/Via4 cut
  `layout.floorplan.interregion.wiring_plan()` draws for the net -- the same
  call `floorplan.py`'s `compose()` makes, fed the committed
  `reports/compose.json` origins and `reports/area.json` bounding boxes the
  way `vss_trunk_ir_drop.py` already feeds it. That is the Metal4 trunk
  from the chip pin to the `digital` riser, the Via3 onto the Metal3 riser
  in the isolation channel, the riser, the Via3/Via4 stack at its top, and
  the Metal5 dock onto the lowest strap of the net (#224).
- **Internal grid.** Every `SPECIALNETS` wire and via of the net in
  `layout/digital/trng_top.def`: the Metal5 and Metal4 straps, the Metal1
  follow-pin rails, the Via4 arrays at strap crossings and the Via1-Via3
  stacks from rail to strap, each via array priced per cut from the DEF's
  own `VIAS` `ROWCOL`.
- **Joins** are geometric: a via cut joins the conductors of its two layers
  that contain its centre, and two same-layer conductors join where they
  overlap. A join that is not drawn is not invented, and the network must
  be one piece (see "Refusals").

Resistance sources
------------------
Sheet and per-cut via resistances are the gf180mcu magic technology file's
own extraction tables for the PDK revision every digital record here pins
(`TECH_SOURCE`). Two of its variants are used: nominal (`variants ()`,
whose metal values equal the `klt` gf180mcu deck's curated `PARASITICS`)
and the high-resistance corner (`variants (hrhc),(hrlc)`). The file's third,
low-resistance variant prices every via at zero and is not used: a zero-ohm
via cannot be priced and is not a conservative choice anyway. The file has
no temperature coefficient, so the derating above 25 C is an assumption
(`ASSUMED_TCR_PER_K`), stated as one and applied only in the conservative
direction.

Current sources
---------------
The digital load is the current-DEF `digital-sta-power` family (15 corners,
gate level, DR-0021) through `digital_corner_characterization.load()`,
which refuses records of any other DEF revision. Three scenarios:

- **active**: total power at DR-0003's ratified 1 MHz rate, uniform 0.25
  activity, divided by that corner's deck voltage;
- **idle**: the record's own leakage current;
- **stress (informational)**: the same records' 20 MHz total -- the place-
  and-route clock constraint, not an operating rate this design ratifies.

Where in the grid the current is drawn is not known at cell resolution, so
two allocations are reported. *Uniform*: every standard-cell row draws the
same current, spread evenly along the row, from the rail on each of its
edges. *Allocation-free bound*: the whole current drawn at the single point
of the rails with the highest effective resistance to the pin. In a
resistor network every node's offset is at most the total current times the
largest effective resistance, so this bound holds for any allocation of the
same total.

The analog return on the shared `vss` trunk uses `vss_trunk_ir_drop.py`'s
own current profile (its `_active_currents_a`/`_idle_currents_a`), injected
at the analog taps; the analog tool's own conservative bound is quoted
beside the digital load's added shift at those taps.

Refusals
--------
Missing evidence never reads as a zero-offset pass:

- no complete current-DEF record family, or a non-positive or non-finite
  current -> `EvidenceError`;
- a network that is not one piece (an omitted via or dock leaves the grid
  floating) or a rail with no via -> `ConnectivityError`;
- the composed-floorplan `klt erc` supply report not describing the
  committed composed stream, or not reporting `vddd`/`vss` connected ->
  `ConnectivityError`.

`--check` exits 2 on any of these, and 1 when the committed document is
stale (any pinned geometry hash, record hash or derived number moved) or a
ratified-rate bound reaches the materiality threshold.

What this does not do
---------------------
DC only: no transient ground bounce, no supply ripple (`sim/tools/
supply_ripple.py`, #414), no electromigration verdict and no package or
bond-wire resistance -- the chip pin is the reference. It does not change
any README row or signoff tier, and it does not replace structural ERC.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SIM_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SIM_DIR.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "design"))
sys.path.insert(0, str(SIM_DIR / "tools"))

from layout.floorplan import interregion  # noqa: E402

import digital_corner_characterization as dcc  # noqa: E402
import vss_trunk_ir_drop as analog  # noqa: E402
from _resistor_network import (  # noqa: E402
    DisconnectedError,
    ResistorNetwork,
    uniform_segment_peak,
    uniform_tip_peak,
)

COMPOSE_REPORT = REPO_ROOT / "layout" / "floorplan" / "reports" / "compose.json"
AREA_REPORT = REPO_ROOT / "layout" / "floorplan" / "reports" / "area.json"
INTERREGION_REPORT = REPO_ROOT / "layout" / "floorplan" / "reports" / "interregion.json"
ERC_SUPPLY_REPORT = REPO_ROOT / "layout" / "floorplan" / "reports" / "erc-supply.json"
COMPOSED_GDS = REPO_ROOT / "layout" / "floorplan" / "trng_floorplan.gds"
DIGITAL_DEF = interregion.DIGITAL_DEF
DOC = SIM_DIR / "characterization-digital-supply-ir-drop.md"

BEGIN = ("<!-- digital-supply-ir-drop:begin (generated by "
         "sim/tools/digital_supply_ir_drop.py; do not edit) -->")
END = "<!-- digital-supply-ir-drop:end -->"

NETS = ("vddd", "vss")
DIGITAL = "digital"

# --------------------------------------------------------------------------- #
# Resistance assumptions
# --------------------------------------------------------------------------- #

#: Where every resistance below is transcribed from. The tech file's
#: `resist` entries are milliohm per square and its `contact` entries
#: milliohm per cut; its contact types map to this flow's via layers as
#: m2c = Via1, m3c = Via2, via3 = Via3, via4 = Via4.
TECH_SOURCE = {
    "file": "libs.tech/magic/gf180mcuD.tech",
    "pdk": "gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b",
    "sha256": "9340f8c2f97407281edc089363eda2ad369cdf5d2db8df6afcbf862162e4eafa",
}

RESISTANCE_VARIANTS: dict[str, dict] = {
    "nominal": {
        "tech_block": "variants ()",
        "sheet_ohm_sq": {"Metal1": 0.090, "Metal2": 0.090, "Metal3": 0.090,
                         "Metal4": 0.090, "Metal5": 0.060},
        "via_ohm_per_cut": {"Via1": 4.5, "Via2": 4.5, "Via3": 4.5, "Via4": 4.5},
    },
    "high": {
        "tech_block": "variants (hrhc),(hrlc)",
        "sheet_ohm_sq": {"Metal1": 0.104, "Metal2": 0.104, "Metal3": 0.104,
                         "Metal4": 0.104, "Metal5": 0.070},
        "via_ohm_per_cut": {"Via1": 15.0, "Via2": 15.0, "Via3": 15.0, "Via4": 15.0},
    },
}

#: Temperature coefficient applied to every resistance above
#: `TCR_REFERENCE_C`. An assumption (a typical aluminium-interconnect
#: figure), not a PDK value: the tech file carries none. No credit is taken
#: below the reference temperature.
ASSUMED_TCR_PER_K = 0.004
TCR_REFERENCE_C = 25.0


def derate(temperature_c: float) -> float:
    return 1.0 + ASSUMED_TCR_PER_K * max(0.0, temperature_c - TCR_REFERENCE_C)


#: Ratified operating envelope (README "Operating envelope": 3.3 V +-10 %).
ENVELOPE_V = (2.97, 3.63)

#: The same yardstick `vss_trunk_ir_drop.py` judges the analog return
#: against: 10 % of the 330 mV supply-corner spread the PVT sweep already
#: covers. Here it is applied to the local supply collapse -- the `vddd`
#: drop plus the `vss` rise the digital cells see together.
MATERIALITY_V = analog.SUPPLY_CORNER_SPREAD_V * analog.MATERIALITY_FRACTION

#: Scenarios: which record value carries the current, how it becomes amps,
#: which analog profile shares the `vss` trunk with it, and whether the
#: materiality verdict gates `--check`.
SCENARIOS = {
    "active": {"label": "active, 1 MHz (DR-0003 ratified rate), uniform 0.25 activity",
               "analog": "active", "gated": True},
    "idle": {"label": "idle, leakage only",
             "analog": "idle", "gated": True},
    "stress": {"label": "stress, 20 MHz (place-and-route clock constraint; informational)",
               "analog": "active", "gated": False},
}


class EvidenceError(RuntimeError):
    """Current evidence is missing, stale or not physical."""


class ConnectivityError(RuntimeError):
    """A supply join is missing, or connectivity is not established."""


# --------------------------------------------------------------------------- #
# Geometry
# --------------------------------------------------------------------------- #

_PLAN_LAYERS = {
    tuple(interregion.METAL3): "Metal3",
    tuple(interregion.METAL4): "Metal4",
    tuple(interregion.METAL5): "Metal5",
}
_PLAN_VIAS = {
    tuple(interregion.VIA3): ("Via3", "Metal3", "Metal4"),
    tuple(interregion.VIA4): ("Via4", "Metal4", "Metal5"),
}


def _nm(um: float) -> int:
    return int(round(um * 1000))


def committed_wiring_plan(compose_path: Path = COMPOSE_REPORT,
                          area_path: Path = AREA_REPORT) -> tuple[dict, dict]:
    """`interregion.wiring_plan()` over the committed reports -- the same
    inputs `vss_trunk_ir_drop.resistance_model()` uses -- and `digital`'s
    content origin in the composed frame."""
    compose = json.loads(compose_path.read_text())
    origins_um = compose["request"]["placement"]["origins_um"]
    area = json.loads(area_path.read_text())
    origins: dict[str, dict] = {}
    bboxes: dict[str, dict] = {}
    for region in area["regions"]:
        rid = region["id"]
        if f"{rid}_ring" in origins_um:
            origins[rid] = origins_um[f"{rid}_ring"]
            bboxes[rid] = region["ring_content_bbox_um"]
    if DIGITAL not in origins:
        raise ConnectivityError("compose.json places no `digital` content")
    bboxes[DIGITAL] = interregion.digital_die_bbox()
    return interregion.wiring_plan(origins, bboxes), origins[DIGITAL]


@dataclass
class Pdn:
    """One `SPECIALNETS` net of a DEF, plus the rows that load it."""
    net: str
    units: int
    stripes: list[tuple[str, int, tuple[int, int], tuple[int, int], str]]
    vias: list[tuple[int, int, str]]
    via_defs: dict[str, tuple[str, str, str, int]]
    rows: list[tuple[int, int, int]]
    row_height: int


_SPECIAL_WIRE_RE = re.compile(
    r"(?:\+\s*ROUTED|NEW)\s+(Metal\d)\s+(\d+)\s+\+\s+SHAPE\s+(\w+)\s+"
    r"\(\s*(-?\d+)\s+(-?\d+)\s*\)\s*(?:\(\s*(-?\d+|\*)\s+(-?\d+|\*)\s*\)|([A-Za-z_]\S*))"
)
_VIA_DEF_RE = re.compile(r"^\s*-\s+(\S+)(.*?);", re.M | re.S)
_ROW_RE = re.compile(
    r"^ROW\s+\S+\s+\S+\s+(-?\d+)\s+(-?\d+)\s+\S+\s+DO\s+(\d+)\s+BY\s+(\d+)\s+STEP\s+(\d+)\s+(\d+)",
    re.M,
)


def _section(text: str, start: str, end: str) -> str:
    i = text.find(f"\n{start}")
    j = text.find(f"\n{end}", i + 1)
    if i < 0 or j < 0:
        raise ConnectivityError(f"DEF has no {start} ... {end} section")
    return text[i:j]


def parse_pdn(def_text: str, net: str) -> Pdn:
    m = re.search(r"^UNITS\s+DISTANCE\s+MICRONS\s+(\d+)", def_text, re.M)
    if not m:
        raise ConnectivityError("DEF declares no UNITS DISTANCE MICRONS")
    units = int(m.group(1))

    via_defs: dict[str, tuple[str, str, str, int]] = {}
    for name, body in _VIA_DEF_RE.findall(_section(def_text, "VIAS", "END VIAS")):
        layers = re.search(r"\+\s*LAYERS\s+(\S+)\s+(\S+)\s+(\S+)", body)
        if not layers:
            raise ConnectivityError(f"DEF via {name!r} has no `+ LAYERS` this reader understands")
        rowcol = re.search(r"\+\s*ROWCOL\s+(\d+)\s+(\d+)", body)
        cuts = int(rowcol.group(1)) * int(rowcol.group(2)) if rowcol else 1
        bottom, cut, top = layers.groups()
        via_defs[name] = (bottom, cut, top, cuts)

    special = _section(def_text, "SPECIALNETS", "END SPECIALNETS")
    entries = re.split(r"\n[ \t]*-\s+", special)
    entry = next((e for e in entries if e.split(None, 1)[:1] == [net]), None)
    if entry is None:
        raise ConnectivityError(f"DEF SPECIALNETS has no `{net}` entry")
    stripes, vias = [], []
    for g in _SPECIAL_WIRE_RE.finditer(entry):
        layer, width, shape, x0, y0, x1, y1, via = g.groups()
        p0 = (int(x0), int(y0))
        if via is not None:
            if via not in via_defs:
                raise ConnectivityError(f"`{net}` places undefined via {via!r}")
            vias.append((p0[0], p0[1], via))
            continue
        p1 = (p0[0] if x1 == "*" else int(x1), p0[1] if y1 == "*" else int(y1))
        if p0[0] != p1[0] and p0[1] != p1[1]:
            raise ConnectivityError(f"`{net}` has a non-orthogonal {layer} wire {p0}-{p1}")
        stripes.append((layer, int(width), p0, p1, shape))
    if not stripes:
        raise ConnectivityError(f"DEF SPECIALNETS `{net}` has no wires")

    rows = []
    for x, y, nx, ny, sx, _sy in _ROW_RE.findall(def_text):
        if int(ny) != 1:
            raise ConnectivityError("DEF ROW with BY != 1 is not supported")
        rows.append((int(x), int(x) + int(nx) * int(sx), int(y)))
    if not rows:
        raise ConnectivityError("DEF declares no ROWs to load the grid with")
    ys = sorted({r[2] for r in rows})
    steps = {b - a for a, b in zip(ys, ys[1:])}
    if len(steps) != 1:
        raise ConnectivityError(f"DEF rows are not on one pitch: {sorted(steps)}")
    return Pdn(net, units, stripes, vias, via_defs, rows, steps.pop())


@dataclass
class _Conductor:
    layer: str
    rect: tuple[int, int, int, int]   # composed frame, nm
    axis: int                          # 0: runs along x, 1: along y
    width_nm: int
    desc: str
    rail: bool = False


@dataclass
class Built:
    net: str
    variant: str
    network: ResistorNetwork
    ref: tuple
    join: tuple
    dig_trunk: tuple
    rails: list[dict]
    analog_taps: dict[str, tuple]
    external_path: list[tuple[str, float]]
    counts: dict = field(default_factory=dict)


def _contains(rect, pt) -> bool:
    return rect[0] <= pt[0] <= rect[2] and rect[1] <= pt[1] <= rect[3]


def build_network(net: str, plan: dict, origin: dict, pdn: Pdn, variant: str,
                  *, drop_shapes=None) -> Built:
    """The resistor network of `net`, from the chip pin to every rail.

    `drop_shapes` (a predicate on a plan shape) exists for the removed-join
    test: it deletes drawn geometry before the network is built."""
    res = RESISTANCE_VARIANTS[variant]
    sheet, via_r = res["sheet_ohm_sq"], res["via_ohm_per_cut"]
    route = next((r for r in plan["routes"] if r["net"] == net), None)
    if route is None:
        raise ConnectivityError(f"the wiring plan draws no `{net}` route")
    if route["chip_pin_x_um"] is None:
        raise ConnectivityError(f"`{net}` has no chip pin to reference offsets against")
    dig = [e for e in route["endpoints"] if e["region"] == DIGITAL]
    if len(dig) != 1 or dig[0]["anchor"] != "digital_pdn_strap":
        raise ConnectivityError(f"`{net}` has no single `digital_pdn_strap` endpoint")
    trunk_y = _nm(route["trunk_y_um"])
    ref = ("pt", "Metal4", _nm(route["chip_pin_x_um"]), trunk_y)
    dig_trunk = ("pt", "Metal4", _nm(dig[0]["riser_x_um"]), trunk_y)

    conductors: list[_Conductor] = []
    cuts: list[tuple[str, str, str, int, tuple[int, int], str]] = []

    for s in plan["shapes"]:
        if s.get("_net") != net or (drop_shapes and drop_shapes(s)):
            continue
        layer = tuple(s["layer"])
        x0, y0, x1, y1 = (_nm(v) for v in s["rect_um"])
        if layer in _PLAN_LAYERS:
            w, h = x1 - x0, y1 - y0
            axis = 0 if w >= h else 1
            conductors.append(_Conductor(_PLAN_LAYERS[layer], (x0, y0, x1, y1), axis,
                                         min(w, h), f"{_PLAN_LAYERS[layer].lower()} wiring-plan rect"))
        elif layer in _PLAN_VIAS:
            cut, bottom, top = _PLAN_VIAS[layer]
            size = interregion.VIA_SZ
            if abs((x1 - x0) - _nm(size)) > 1 or abs((y1 - y0) - _nm(size)) > 1:
                raise ConnectivityError(f"`{net}` {cut} shape is not one {size} um cut")
            cuts.append((cut, bottom, top, 1, ((x0 + x1) // 2, (y0 + y1) // 2),
                         f"{cut.lower()} single cut"))

    # The DEF grid, moved into the composed frame (nm). Exact: 2000 DEF
    # units/um and an origin on the 10 nm grid.
    scale = 1000 / pdn.units
    ox, oy = _nm(origin["x"]), _nm(origin["y"])

    def to_nm(p):
        return (int(round(p[0] * scale)) + ox, int(round(p[1] * scale)) + oy)

    for layer, width, p0, p1, shape in pdn.stripes:
        a, b = to_nm(p0), to_nm(p1)
        hw = int(round(width * scale)) // 2
        if a[1] == b[1]:
            rect = (min(a[0], b[0]), a[1] - hw, max(a[0], b[0]), a[1] + hw)
            axis = 0
        else:
            rect = (a[0] - hw, min(a[1], b[1]), a[0] + hw, max(a[1], b[1]))
            axis = 1
        conductors.append(_Conductor(layer, rect, axis, 2 * hw,
                                     f"{layer.lower()} {shape.lower()}", rail=(shape == "FOLLOWPIN")))
    for x, y, name in pdn.vias:
        bottom, cut, top, n = pdn.via_defs[name]
        cuts.append((cut, bottom, top, n, to_nm((x, y)), f"{cut.lower()} array x{n}"))

    # Contact points, per layer.
    points: dict[str, set] = {}
    for cut, bottom, top, n, c, _ in cuts:
        points.setdefault(bottom, set()).add(c)
        points.setdefault(top, set()).add(c)
    points.setdefault("Metal4", set()).add(ref[2:])
    by_layer: dict[str, list[_Conductor]] = {}
    for c in conductors:
        by_layer.setdefault(c.layer, []).append(c)
    for layer, group in by_layer.items():
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                ox0, oy0 = max(a.rect[0], b.rect[0]), max(a.rect[1], b.rect[1])
                ox1, oy1 = min(a.rect[2], b.rect[2]), min(a.rect[3], b.rect[3])
                if ox0 < ox1 and oy0 < oy1:
                    points[layer].add(((ox0 + ox1) // 2, (oy0 + oy1) // 2))

    network = ResistorNetwork()
    network.add_node(ref)
    edge_desc: dict[frozenset, tuple[str, float]] = {}

    def connect(a, b, ohms, desc):
        network.add_resistor(a, b, ohms)
        edge_desc[frozenset((a, b))] = (desc, ohms)

    rails: list[dict] = []
    for c in conductors:
        on = sorted((p for p in points.get(c.layer, ()) if _contains(c.rect, p)),
                    key=lambda p: (p[c.axis], p[1 - c.axis]))
        for p, q in zip(on, on[1:]):
            d = q[c.axis] - p[c.axis]
            if d == 0:
                raise ConnectivityError(
                    f"`{net}`: two contacts side by side across one {c.layer} conductor at "
                    f"{p} and {q}; this model has no lateral resistance for that")
            ohms = sheet[c.layer] * d / c.width_nm
            connect(("pt", c.layer) + p, ("pt", c.layer) + q, ohms,
                    f"{c.desc}, {d / 1000:.2f} um x {c.width_nm / 1000:.2f} um")
        for p in on:
            network.add_node(("pt", c.layer) + p)
        if c.rail:
            if not on:
                raise ConnectivityError(
                    f"`{net}` {c.layer} rail at y = {c.rect[1]} nm has no via: its cells "
                    "would be unpowered, not offset-free")
            rails.append({"conductor": c, "xs": [p[0] for p in on], "y": on[0][1],
                          "x0": c.rect[0], "x1": c.rect[2]})

    for cut, bottom, top, n, c, desc in cuts:
        connect(("pt", bottom) + c, ("pt", top) + c, via_r[cut] / n, desc)

    if ref not in network or not network._g[ref]:
        raise ConnectivityError(f"`{net}` chip pin at {ref[2:]} nm lands on no Metal4 trunk")
    try:
        network.require_connected(ref)
    except DisconnectedError as exc:
        raise ConnectivityError(
            f"`{net}`: supply join missing -- {exc}. A floating grid is rejected, "
            "never priced as zero drop") from exc

    # The join: the one node where the docking path meets a DEF strap.
    def_m5 = [c for c in conductors if c.layer == "Metal5" and "stripe" in c.desc]
    plan_m5 = [c for c in conductors if c.layer == "Metal5" and "wiring-plan" in c.desc]
    joins = set()
    for a in plan_m5:
        for b in def_m5:
            ox0, oy0 = max(a.rect[0], b.rect[0]), max(a.rect[1], b.rect[1])
            ox1, oy1 = min(a.rect[2], b.rect[2]), min(a.rect[3], b.rect[3])
            if ox0 < ox1 and oy0 < oy1:
                joins.add(("pt", "Metal5", (ox0 + ox1) // 2, (oy0 + oy1) // 2))
    if len(joins) != 1:
        raise ConnectivityError(f"`{net}`: expected one dock-to-strap join, found {len(joins)}")
    join = joins.pop()

    # The series path from the pin to the join, for the report.
    prev = {ref: None}
    queue = [ref]
    while queue and join not in prev:
        nxt = []
        for n in queue:
            for m in network._g[n]:
                if m not in prev:
                    prev[m] = n
                    nxt.append(m)
        queue = nxt
    path, n = [], join
    while prev.get(n) is not None:
        path.append(edge_desc[frozenset((n, prev[n]))])
        n = prev[n]
    path.reverse()

    analog_taps = {}
    for e in route["endpoints"]:
        if e["region"] == DIGITAL:
            continue
        tap = ("pt", "Metal4", _nm(e["riser_x_um"]), trunk_y)
        if tap not in network:
            raise ConnectivityError(f"`{net}` analog tap {e['region']!r} is not on the trunk")
        analog_taps[e["region"]] = tap

    counts = {
        "rails": len(rails),
        "straps": {layer: sum(1 for c in conductors if c.layer == layer and "stripe" in c.desc)
                   for layer in ("Metal4", "Metal5")},
        "via_arrays": len(pdn.vias),
        "nodes": len(network.nodes),
    }
    return Built(net, variant, network, ref, join, dig_trunk, rails, analog_taps, path, counts)


def rail_loads(built: Built, pdn: Pdn, origin: dict) -> list[dict]:
    """Uniform allocation: each row draws 1/n of the total, evenly along its
    length, from the rail of this net on its edge. Returns each rail's own
    linear current density (A/nm for a 1 A total)."""
    scale = 1000 / pdn.units
    oy = _nm(origin["y"])
    h = pdn.row_height
    n_rows = len(pdn.rows)
    out = []
    covered = 0
    for rail in built.rails:
        y_local = int(round((rail["y"] - oy) / scale))
        serving = [r for r in pdn.rows if r[2] == y_local or r[2] + h == y_local]
        for x0, x1, _ in serving:
            if int(round(x0 * scale)) + _nm(origin["x"]) != rail["x0"] or \
                    int(round(x1 * scale)) + _nm(origin["x"]) != rail["x1"]:
                raise ConnectivityError(f"`{built.net}`: a row and its rail span different x ranges")
        covered += len(serving)
        out.append(dict(rail, density=len(serving) / n_rows / (rail["x1"] - rail["x0"])))
    if covered != n_rows:
        raise ConnectivityError(
            f"`{built.net}`: {covered} of {n_rows} rows sit on a rail of this net; "
            "the rest would draw current from nowhere this model can see")
    return out


def grid_response(built: Built, pdn: Pdn, origin: dict) -> dict:
    """Unit-current (1 A) figures for one built network."""
    variant = RESISTANCE_VARIANTS[built.variant]
    sheet = variant["sheet_ohm_sq"]["Metal1"]
    fac = built.network.factor(built.ref)
    loads = rail_loads(built, pdn, origin)

    inj: dict[tuple, float] = {}
    for rail in loads:
        xs, lam, y = rail["xs"], rail["density"], rail["y"]
        key = lambda x: ("pt", "Metal1", x, y)  # noqa: E731
        inj[key(xs[0])] = inj.get(key(xs[0]), 0.0) + lam * (xs[0] - rail["x0"])
        inj[key(xs[-1])] = inj.get(key(xs[-1]), 0.0) + lam * (rail["x1"] - xs[-1])
        for a, b in zip(xs, xs[1:]):
            half = lam * (b - a) / 2
            inj[key(a)] = inj.get(key(a), 0.0) + half
            inj[key(b)] = inj.get(key(b), 0.0) + half
    total = sum(inj.values())
    if abs(total - 1.0) > 1e-9:
        raise ConnectivityError(f"`{built.net}`: uniform allocation sums to {total} A, not 1 A")
    phi = fac.solve(inj)

    rail_nodes = [("pt", "Metal1", x, r["y"]) for r in loads for x in r["xs"]]
    reff = fac.effective_resistance(rail_nodes)

    def r_of(nm, width_nm):
        return sheet * nm / width_nm

    peak_u, at_u = -math.inf, None
    bound, at_b = -math.inf, None
    for rail in loads:
        y, xs, lam = rail["y"], rail["xs"], rail["density"]
        w = rail["conductor"].width_nm
        key = lambda x: ("pt", "Metal1", x, y)  # noqa: E731
        tips = ((rail["x0"], xs[0]), (rail["x1"], xs[-1]))
        for end, x in tips:
            r = r_of(abs(x - end), w)
            v = uniform_tip_peak(phi[key(x)], r, lam * abs(x - end))
            if v > peak_u:
                peak_u, at_u = v, (end, y)
            if reff[key(x)] + r > bound:
                bound, at_b = reff[key(x)] + r, (end, y)
        for a, b in zip(xs, xs[1:]):
            r = r_of(b - a, w)
            v = uniform_segment_peak(phi[key(a)], phi[key(b)], r, lam * (b - a))
            if v > peak_u:
                peak_u, at_u = v, ((a + b) // 2, y)
            # Effective resistance is a metric, so a point between a and b
            # is within (R_a + R_b + r) / 2 of the pin.
            rb = (reff[key(a)] + reff[key(b)] + r) / 2
            if rb > bound:
                bound, at_b = rb, ((a + b) // 2, y)

    out = {
        "external_ohm": phi[built.join],
        "internal_uniform_ohm": peak_u - phi[built.join],
        "internal_bound_ohm": bound - phi[built.join],
        "uniform_peak_at_um": [round(v / 1000, 3) for v in at_u],
        "bound_peak_at_um": [round(v / 1000, 3) for v in at_b],
        "path_sum_ohm": sum(r for _, r in built.external_path),
    }
    if built.analog_taps:
        out["digital_shift_at_analog_taps_ohm"] = max(phi[t] for t in built.analog_taps.values())
        out["_factor"] = fac
    return out


def analog_offsets_at_dock(built: Built, fac, scenario: str) -> float:
    """The analog return's own offset at the `digital` riser's trunk node
    (shared by every node of the digital grid behind it), using
    `vss_trunk_ir_drop.py`'s current profile."""
    currents = (analog._active_currents_a(analog.ACTIVE_CORNER["voltage_v"])
                if scenario == "active" else analog._idle_currents_a())
    missing = set(currents) - set(built.analog_taps)
    if missing:
        raise ConnectivityError(f"analog regions {sorted(missing)} have no tap on the `vss` trunk")
    phi = fac.solve({built.analog_taps[r]: i for r, i in currents.items()})
    return phi[built.dig_trunk]


# --------------------------------------------------------------------------- #
# Current evidence
# --------------------------------------------------------------------------- #


def load_currents(records_dir: Path = dcc.RECORDS, def_path: Path = DIGITAL_DEF) -> list[dict]:
    try:
        family = dcc.load(records_dir, def_path)
    except dcc.RecordError as exc:
        raise EvidenceError(f"no current-DEF digital power evidence: {exc}") from exc
    rows = []
    for r in family:
        try:
            v = float(r.fields["voltage"])
            t = float(r.fields["temperature"])
            row = {
                "corner": r.corner, "record": r.stem,
                "sha256": hashlib.sha256(r.path.read_bytes()).hexdigest(),
                "voltage_v": v, "temperature_c": t,
                "active": r.v("p_total_1mhz_w") / v,
                "stress": r.v("p_total_20mhz_w") / v,
                "idle": r.v("i_leakage_a"),
            }
        except (dcc.RecordError, TypeError, ValueError) as exc:
            raise EvidenceError(f"{r.stem}: {exc}") from exc
        for s in SCENARIOS:
            if not (math.isfinite(row[s]) and row[s] > 0):
                raise EvidenceError(f"{r.stem}: {s} current {row[s]!r} is not a positive number")
        rows.append(row)
    return rows


# --------------------------------------------------------------------------- #
# Connectivity precondition and provenance
# --------------------------------------------------------------------------- #


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def erc_precondition(report_path: Path = ERC_SUPPLY_REPORT, gds_path: Path = COMPOSED_GDS) -> dict:
    """The structural half: the composed-floorplan `klt erc` supply report
    must describe the committed composed stream and report both nets as one
    connected island each. This is the precondition, not the measurement."""
    if not report_path.is_file() or not gds_path.is_file():
        raise ConnectivityError("composed ERC supply report or composed stream is missing")
    rep = json.loads(report_path.read_text())
    want = "sha256:" + _sha256(gds_path)
    got = rep.get("provenance", {}).get("input", {}).get("content_hash")
    if got != want:
        raise ConnectivityError(
            f"{report_path.name} describes {got}, not the committed composed stream {want}")
    checked = rep.get("erc_coverage", {}).get("checked", [])
    for net in NETS:
        if f'erc.net_connectivity:["{net}"]' not in checked:
            raise ConnectivityError(f"{report_path.name} did not check `{net}` connectivity")
        bad = [f for f in rep.get("erc_findings", []) if net in json.dumps(f)]
        if bad:
            raise ConnectivityError(f"{report_path.name} has {len(bad)} finding(s) naming `{net}`")
    return {"report": str(report_path.relative_to(REPO_ROOT)), "erc_status": rep.get("erc_status"),
            "klt_version": rep.get("provenance", {}).get("klt_version"),
            "nets_checked": list(NETS)}


def plan_digest(plan: dict) -> str:
    """sha256 over the drawn shapes and routes of the two nets, so a
    geometry change -- not a comment edit -- stales the report."""
    keep = {
        "shapes": [s for s in plan["shapes"] if s.get("_net") in NETS],
        "routes": [r for r in plan["routes"] if r["net"] in NETS],
    }
    return hashlib.sha256(json.dumps(keep, sort_keys=True).encode()).hexdigest()


# --------------------------------------------------------------------------- #
# The derivation
# --------------------------------------------------------------------------- #


def derive(records_dir: Path = dcc.RECORDS, def_path: Path = DIGITAL_DEF) -> dict:
    erc = erc_precondition()
    currents = load_currents(records_dir, def_path)
    plan, origin = committed_wiring_plan()
    def_text = def_path.read_text(errors="replace")

    unit: dict[str, dict[str, dict]] = {}
    analog_at_dock: dict[str, dict[str, float]] = {}
    for net in NETS:
        pdn = parse_pdn(def_text, net)
        unit[net] = {}
        for variant in RESISTANCE_VARIANTS:
            built = build_network(net, plan, origin, pdn, variant)
            resp = grid_response(built, pdn, origin)
            fac = resp.pop("_factor", None)
            resp["external_path"] = [{"element": d, "ohm": r} for d, r in built.external_path]
            resp["counts"] = built.counts
            unit[net][variant] = resp
            if fac is not None:
                analog_at_dock[variant] = {s: analog_offsets_at_dock(built, fac, s)
                                           for s in ("active", "idle")}

    f_max = derate(max(c["temperature_c"] for c in currents))
    scen: dict[str, dict] = {}
    for s, spec in SCENARIOS.items():
        per_corner = []
        for c in currents:
            f, i = derate(c["temperature_c"]), c[s]
            u = {net: unit[net]["nominal"] for net in NETS}
            vddd_ext = f * i * u["vddd"]["external_ohm"]
            vddd_int = f * i * u["vddd"]["internal_uniform_ohm"]
            vss_ext = f * i * u["vss"]["external_ohm"]
            vss_int = f * i * u["vss"]["internal_uniform_ohm"]
            vss_shared = f * analog_at_dock["nominal"][spec["analog"]]
            per_corner.append({
                "corner": c["corner"], "current_a": i, "derate": f,
                "vddd_external_v": vddd_ext, "vddd_internal_v": vddd_int,
                "vss_external_v": vss_ext, "vss_internal_v": vss_int,
                "vss_analog_shared_v": vss_shared,
                "collapse_v": vddd_ext + vddd_int + vss_ext + vss_int + vss_shared,
                "analog_tap_shift_v": f * i * u["vss"]["digital_shift_at_analog_taps_ohm"],
            })
        worst = max(currents, key=lambda c: c[s])
        hi = {net: unit[net]["high"] for net in NETS}
        i_max = worst[s]
        bound = {
            "corner_of_max_current": worst["corner"], "current_a": i_max, "derate": f_max,
            "vddd_external_v": f_max * i_max * hi["vddd"]["external_ohm"],
            "vddd_internal_v": f_max * i_max * hi["vddd"]["internal_bound_ohm"],
            "vss_external_v": f_max * i_max * hi["vss"]["external_ohm"],
            "vss_internal_v": f_max * i_max * hi["vss"]["internal_bound_ohm"],
            "vss_analog_shared_v": f_max * analog_at_dock["high"][spec["analog"]],
            "analog_tap_shift_v": f_max * i_max * hi["vss"]["digital_shift_at_analog_taps_ohm"],
        }
        bound["collapse_v"] = sum(bound[k] for k in (
            "vddd_external_v", "vddd_internal_v", "vss_external_v", "vss_internal_v",
            "vss_analog_shared_v"))
        est = max(per_corner, key=lambda r: r["collapse_v"])
        least = min(r["collapse_v"] for r in per_corner)
        scen[s] = {
            "label": spec["label"], "gated": spec["gated"], "per_corner": per_corner,
            "estimate_worst": est, "bound": bound,
            "local_supply_range_v": [ENVELOPE_V[0] - bound["collapse_v"], ENVELOPE_V[1] - least],
            "material": bound["collapse_v"] >= MATERIALITY_V,
        }

    model = analog.resistance_model()
    act = analog._active_currents_a(analog.ACTIVE_CORNER["voltage_v"])
    far = model["chain"][-1]["region"]
    analog_bound = max(analog.node_offsets(model["chain"], analog.worst_case_bound_a(act, far)).values())

    provenance = {
        "geometry": {
            "layout/digital/trng_top.def": {"git_blob_sha": dcc.blob_sha(def_path)},
            "layout/floorplan/trng_floorplan.gds": {"sha256": _sha256(COMPOSED_GDS)},
            "layout/floorplan/reports/compose.json": {"sha256": _sha256(COMPOSE_REPORT)},
            "layout/floorplan/reports/area.json": {"sha256": _sha256(AREA_REPORT)},
            "layout/floorplan/reports/interregion.json": {"sha256": _sha256(INTERREGION_REPORT)},
            "wiring_plan(vddd, vss) shapes+routes": {"sha256": plan_digest(plan)},
        },
        "connectivity": erc,
        "resistance": {"source": TECH_SOURCE,
                       "variants": {k: {"tech_block": v["tech_block"],
                                        "sheet_ohm_sq": v["sheet_ohm_sq"],
                                        "via_ohm_per_cut": v["via_ohm_per_cut"]}
                                    for k, v in RESISTANCE_VARIANTS.items()},
                       "assumed_tcr_per_k": ASSUMED_TCR_PER_K,
                       "tcr_reference_c": TCR_REFERENCE_C},
        "current": {
            "family": "digital-sta-power (gate level, DR-0021), current DEF only",
            "activity": "uniform 0.25 transitions/net/cycle, duty 0.5",
            "rates": {"active": "1 MHz", "stress": "20 MHz", "idle": "leakage"},
            "records": [{"corner": c["corner"], "record": c["record"], "sha256": c["sha256"]}
                        for c in currents],
            "analog_profile": {
                "source": "sim/tools/vss_trunk_ir_drop.py",
                "active_uw": analog.CURRENT_PROFILE_UW["active"],
                "active_corner": analog.ACTIVE_CORNER,
                "idle_total_na": analog.IDLE_TOTAL_NA,
                "idle_corner": analog.IDLE_CORNER,
            },
        },
    }
    return {"provenance": provenance, "unit": unit, "analog_at_dock_v": analog_at_dock,
            "scenarios": scen, "materiality_v": MATERIALITY_V, "envelope_v": list(ENVELOPE_V),
            "analog_only_bound_v": analog_bound}


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #


def _mv(v: float) -> str:
    return f"{v * 1e3:.3f}"


def markdown(d: dict) -> str:
    out = [BEGIN, "", "### Provenance (pinned inputs; any change stales this block)", "",
           "```json", json.dumps(d["provenance"], indent=1, sort_keys=True), "```", ""]

    out += ["### Network and unit response (per ampere of digital current, 25 C)", "",
            "| net | resistance variant | external feed (ohm) | internal, uniform (ohm) "
            "| internal, allocation-free bound (ohm) | rails | Metal4 / Metal5 straps "
            "| DEF via arrays | nodes |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for net in NETS:
        for var, u in d["unit"][net].items():
            c = u["counts"]
            out.append(f"| `{net}` | {var} | {u['external_ohm']:.3f} | {u['internal_uniform_ohm']:.3f} "
                       f"| {u['internal_bound_ohm']:.3f} | {c['rails']} | "
                       f"{c['straps']['Metal4']} / {c['straps']['Metal5']} | {c['via_arrays']} "
                       f"| {c['nodes']} |")
    out += ["", "External feed, element by element, chip pin first (nominal / high, ohm):", "",
            "| net | element | nominal | high |", "|---|---|---:|---:|"]
    for net in NETS:
        nom, hi = d["unit"][net]["nominal"]["external_path"], d["unit"][net]["high"]["external_path"]
        for a, b in zip(nom, hi):
            out.append(f"| `{net}` | {a['element']} | {a['ohm']:.3f} | {b['ohm']:.3f} |")
    out += ["", "Worst points (composed frame, um): "
            + "; ".join(f"`{net}` uniform at {d['unit'][net]['nominal']['uniform_peak_at_um']}, "
                        f"bound at {d['unit'][net]['high']['bound_peak_at_um']}" for net in NETS)
            + ".", ""]
    out += ["Analog return's own offset at the `digital` dock on the shared `vss` trunk: "
            + ", ".join(f"{var} {s} {_mv(v)} mV" for var, by in d["analog_at_dock_v"].items()
                        for s, v in by.items()) + ".", ""]

    for s, sc in d["scenarios"].items():
        out += [f"### Scenario: {sc['label']}", "",
                "Estimate per corner -- nominal resistance, uniform allocation, derated to the "
                "corner's own temperature (mV):", "",
                "| corner | I digital (uA) | vddd ext | vddd int | vss ext | vss int "
                "| vss analog share | local collapse | shift at analog taps |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for r in sc["per_corner"]:
            out.append(f"| {r['corner']} | {r['current_a'] * 1e6:.3f} | {_mv(r['vddd_external_v'])} "
                       f"| {_mv(r['vddd_internal_v'])} | {_mv(r['vss_external_v'])} "
                       f"| {_mv(r['vss_internal_v'])} | {_mv(r['vss_analog_shared_v'])} "
                       f"| {_mv(r['collapse_v'])} | {_mv(r['analog_tap_shift_v'])} |")
        b = sc["bound"]
        lo, hi = sc["local_supply_range_v"]
        verdict = "MATERIAL" if sc["material"] else "not material"
        if not sc["gated"]:
            verdict += " (informational: not a ratified operating rate)"
        out += ["",
                f"**Cross-corner upper bound** (a bound, not a corner: high-resistance variant x "
                f"{b['derate']:.2f} temperature derating x the family's largest current, "
                f"{b['current_a'] * 1e6:.3f} uA at {b['corner_of_max_current']}, allocation-free): "
                f"vddd external {_mv(b['vddd_external_v'])} + internal {_mv(b['vddd_internal_v'])}, "
                f"vss external {_mv(b['vss_external_v'])} + internal {_mv(b['vss_internal_v'])} "
                f"+ analog share {_mv(b['vss_analog_shared_v'])} = **{_mv(b['collapse_v'])} mV** "
                f"local supply collapse; shift the digital load adds at the analog `vss` taps "
                f"<= {_mv(b['analog_tap_shift_v'])} mV.",
                "",
                f"Worst per-corner estimate: {_mv(sc['estimate_worst']['collapse_v'])} mV at "
                f"{sc['estimate_worst']['corner']}. Effective local supply over the "
                f"{d['envelope_v'][0]:.2f}-{d['envelope_v'][1]:.2f} V pin envelope: "
                f"{lo:.4f}-{hi:.4f} V. Against the {_mv(d['materiality_v'])} mV yardstick: "
                f"**{verdict}**.", ""]

    act = d["scenarios"]["active"]["bound"]["analog_tap_shift_v"]
    out += ["### The shared `vss` return, analog side", "",
            f"`vss_trunk_ir_drop.py`'s own conservative bound (analog load only, nominal sheet): "
            f"{_mv(d['analog_only_bound_v'])} mV. Adding the digital load's active-rate shift bound "
            f"at the analog taps ({_mv(act)} mV): {_mv(d['analog_only_bound_v'] + act)} mV against "
            f"{_mv(d['materiality_v'])} mV.", "", END]
    return "\n".join(out)


def _doc_block(text: str) -> str | None:
    i, j = text.find(BEGIN), text.find(END)
    if i < 0 or j < 0:
        return None
    return text[i:j + len(END)]


def check(d: dict, doc: Path = DOC) -> list[str]:
    fails = []
    for s, sc in d["scenarios"].items():
        if sc["gated"] and sc["material"]:
            fails.append(f"{s}: cross-corner bound {_mv(sc['bound']['collapse_v'])} mV reaches the "
                         f"{_mv(d['materiality_v'])} mV materiality yardstick")
    if not doc.is_file():
        fails.append(f"{doc.relative_to(REPO_ROOT)} is missing")
        return fails
    have = _doc_block(doc.read_text())
    if have is None:
        fails.append(f"{doc.name} has no generated block between its markers")
    elif have != markdown(d):
        fails.append(f"{doc.name} is stale: its generated block no longer matches the pinned "
                     "geometry, records or derivation -- regenerate with --markdown and re-read "
                     "the prose against it")
    return fails


def _strip(d):
    if isinstance(d, dict):
        return {k: _strip(v) for k, v in d.items() if not k.startswith("_")}
    if isinstance(d, list):
        return [_strip(v) for v in d]
    return d


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="gate the committed document")
    g.add_argument("--markdown", action="store_true", help="print the generated doc block")
    g.add_argument("--json", action="store_true", help="print the full result as JSON")
    args = ap.parse_args(argv)
    try:
        d = derive()
    except (EvidenceError, ConnectivityError) as exc:
        print(f"UNKNOWN (not a pass): {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(_strip(d), indent=1, sort_keys=True))
        return 0
    if args.check:
        fails = check(d)
        for f in fails:
            print(f"FAIL: {f}", file=sys.stderr)
        if fails:
            return 1
        a = d["scenarios"]["active"]["bound"]["collapse_v"]
        i = d["scenarios"]["idle"]["bound"]["collapse_v"]
        print(f"digital supply IR drop (issue #464): active bound {_mv(a)} mV, idle bound "
              f"{_mv(i)} mV < {_mv(d['materiality_v'])} mV; document current -- OK")
        return 0
    print(markdown(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
