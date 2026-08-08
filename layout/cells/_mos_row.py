#!/usr/bin/env python3
"""Shared hand-drawn layout engine for `layout/cells/xor2/` and
`layout/cells/sampler_dff/`.

Why this exists (not a per-cell copy)
--------------------------------------
`layout/cells/ro_stage/build.py` hand-places every rectangle of its one
four-device cell explicitly (see that file's own docstring for why hand
drawing is required at all: most of this design's devices sit at or below
the gf180mcu 3.3V core devices' 0.42um `klt gen mos_array` floor --
klayout-tools#322). `xor2` (12 devices) and `sampler_dff` (22 devices) are
3x and 5.5x that cell's device count, and issue #109 introduces both of them
together -- hand-placing each transistor's coordinates individually, `
ro_stage`-style, would mean re-deriving the same dog-boned-diffusion /
contact / routing arithmetic twice at a scale where a transcription slip is
easy to make and hard to spot in review. So this module factors out the
part that generalises (an arbitrary list of independent, minimum-or-near-
minimum-width MOS devices, each getting its own primitive geometry) and
each cell's `build.py` supplies only the two device lists transcribed from
its own `.subckt` (`design/ro_array_core.spice`'s `xor2`,
`design/sampler_core.spice`'s `sampler_dff`) -- the same transcription
`ro_stage.spice`'s header describes, just expressed as data instead of
hand-drawn coordinates.

Topology: an independent-device "gate array", not stacked stdcell rows
------------------------------------------------------------------------
Every device gets its **own** source and drain diffusion pad -- unlike
`ro_stage`, which shares one continuous diffusion strip between its two
series-connected, equal-width devices, nothing here is series-merged.
That costs area (this is a verification cell, not a tapeout-density one)
and buys a layout algorithm simple enough to state precisely:

1. All NMOS devices are placed in one row (`_place_row`), left to right,
   each on its own dog-boned diffusion island (the same "PAD_H-tall pads,
   narrowed only under the gate" technique `ro_stage.spice`'s header
   documents -- narrowing is skipped for a device whose own W already
   exceeds the pad-safe minimum, e.g. `xor2`'s W=0.88um XOR-core pull-up).
2. All PMOS devices are placed in a second row, offset in X by a fixed gap
   so **no two devices in the whole cell ever share an X coordinate** --
   the property the routing stage below depends on.
3. One Nwell rectangle encloses the whole PMOS row (plus margin), so every
   PMOS device's body lands on the *same* deck-synthesized floating net --
   `ro_stage.spice`'s header explains why that is what the curated
   extraction deck does with an un-tapped well, and why two devices in one
   drawn Nwell therefore share one floating net rather than each getting
   its own.
4. Every device terminal (source, drain, and the gate -- routed off a poly
   landing pad above the row, mirroring `ro_stage.build.py`'s own gate
   landing pad, just without needing to dodge a neighbour asymmetrically
   since this layout's pitch already clears every spacing rule) gets a
   Contact -> Metal1 -> Via1 -> Metal2 stub -> Via2 stack.
5. Routing is a two-layer Manhattan grid: each *net* gets one horizontal
   Metal2 "trunk" at its own dedicated Y (`_route_nets`), and each
   *terminal* gets its own vertical Metal3 "riser" at its own X (already
   unique per (3) above) connecting up to its net's trunk via a Via2 at
   each end. Metal2 trunks (horizontal, stacked by Y) never collide with
   each other because different nets get different Y; Metal3 risers
   (vertical, one per terminal) never collide with each other because
   every terminal already has a unique X; and a riser never collides with
   an *unrelated* net's trunk it happens to pass under/over because they
   are on different drawn layers (Metal2 vs Metal3) connected only by an
   explicit Via2, not by direct overlap on the same layer. This is the
   ordinary reason real routers keep horizontal and vertical wrong-way
   jogs on separate layers; it is applied here by construction instead of
   by a router because the device count is still small enough to place
   deterministically.

Design-rule values reused below (`comp.width.1` 0.22, `comp.space.1` 0.28,
`comp.enclosing.contact.1`/`poly2.enclosing.contact.1` 0.07,
`poly2.space.1` 0.24, `contact.width.1`/`contact.space.1` 0.22/0.25,
`metal1.width.1`/`metal1.space.1` 0.23/0.23, `metal2.width.1`/
`metal2.space.1` 0.28/0.28, `nwell.enclosing.comp.1` 0.12) are transcribed
from `klt`'s own gf180mcu deck (`klayout_tools/decks/gf180mcu.py`), the
same source `ro_stage.build.py` cites. `Via1`/`Via2` (Metal1<->Metal2,
Metal2<->Metal3) carry no width/space/enclosure rule in that curated deck
at all -- confirmed by grepping the deck's own `DrcRule` table -- so this
module still draws them at a contact-sized 0.22 x 0.22um and centres them
generously inside their neighbouring pad, but nothing here is tuned
against a threshold that does not exist; only the Comp/Poly2/Contact/
Metal1/Metal2 margins below are.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from dataclasses import dataclass

_TESTCELL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "testcells"
)
sys.path.insert(0, os.path.abspath(_TESTCELL_DIR))

from gdsii import Label, Rect, write_gds  # noqa: E402

# --------------------------------------------------------------------------- #
# Layers -- gf180mcu drawn layers, matching klt's curated decks (same set
# layout/testcells/build.py and layout/cells/ro_stage/build.py use), plus
# Via1/Metal2/Via2/Metal3 for the routing grid described above.
# --------------------------------------------------------------------------- #
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

# --------------------------------------------------------------------------- #
# Geometry constants (um). See the module docstring for the rule each
# margin below is checked against.
# --------------------------------------------------------------------------- #
PAD_H_MIN = 0.44  # contact-safe diffusion/poly-landing pad height
PAD_W = 0.44  # comp x-extent of a device's own pad zone
SLOT_PITCH = 0.80  # source -> gate -> drain spacing within one device
LANDING_W = 0.50  # gate poly landing pad width (x)
LANDING_GAP = 0.30  # clearance from row top (comp) to landing pad bottom
LANDING_H = 0.40  # gate poly landing pad height (y)
CONTACT_SIZE = 0.22
METAL1_PAD = 0.40
METAL2_STUB = 0.32
METAL2_TRUNK_H = 0.30
METAL3_W = 0.30
TRUNK_PITCH = 0.65  # Y spacing between adjacent net trunks
BLOCK_GAP = 3.0  # X gap between the NMOS row and the PMOS row
ROW_Y = 1.00  # both rows' shared centreline
NWELL_MARGIN = 0.25
CHANNEL_MARGIN = 0.45  # clearance from the taller row's landing top to the
# first net trunk -- must clear metal2.space.1 (0.28) between a gate
# terminal's own Metal2 stub (centred at the landing pad's Y, so its own
# top edge sits ~0.04 below landing_top) and the first trunk's bottom edge

assert PAD_W + 0.28 <= SLOT_PITCH, "SLOT_PITCH must clear comp.space.1 (0.28)"


@dataclass(frozen=True)
class Device:
    """One MOS device, transcribed directly from a `.subckt`'s `X...` line.

    `drain`/`source` are just the netlist's two diffusion-terminal net
    names -- which one is nominally "drain" vs "source" does not affect
    the drawn geometry or the LVS result (a MOSFET's two diffusion
    terminals are interchangeable for device-level topology matching).
    """

    name: str
    kind: str  # "n" or "p"
    w: float
    l: float
    gate: str
    drain: str
    source: str


class _Canvas:
    def __init__(self) -> None:
        self.rects: list[Rect] = []
        self.labels: list[Label] = []

    def rect(self, layer: tuple[int, int], x0: float, y0: float, x1: float, y1: float) -> None:
        self.rects.append(Rect(layer[0], layer[1], x0, y0, x1, y1))

    def label(self, layer: tuple[int, int], x: float, y: float, text: str) -> None:
        self.labels.append(Label(layer[0], layer[1], x, y, text))


def _pad_half(w: float) -> float:
    """Half-height of a device's own dog-boned pad zone.

    A device whose own W already meets the contact-safe minimum (>=
    PAD_H_MIN) is not narrowed at all -- its comp is one uniform-height
    rectangle from source pad to drain pad, and `w` itself is what the
    extractor measures at the (also full-height) gate crossing.
    """
    return max(PAD_H_MIN, w) / 2.0


def _place_row(
    canvas: _Canvas,
    devices: list[Device],
    y_center: float,
    x0: float,
    terminals: dict[str, list[tuple[float, float]]],
) -> tuple[float, float, float, float]:
    """Place `devices` left to right, each fully independent, starting at
    `x0`, all centred on `y_center`.

    Returns `(x_end, row_bottom, row_top, landing_top)`: `x_end` is the
    last device's drain-pad centre X (the next caller's own X origin, if
    chaining another row); `row_bottom`/`row_top` bound the row's comp
    (for Nwell sizing); `landing_top` is the Y every gate's landing pad
    tops out at (for channel placement).
    """
    if not devices:
        return x0, y_center, y_center, y_center

    max_pad_half = max(_pad_half(d.w) for d in devices)
    row_top = y_center + max_pad_half
    landing_y0 = row_top + LANDING_GAP
    landing_y1 = landing_y0 + LANDING_H

    x = x0
    for d in devices:
        source_x = x
        gate_x = x + SLOT_PITCH
        drain_x = x + 2 * SLOT_PITCH
        pad_half = _pad_half(d.w)
        narrow_half = min(pad_half, d.w / 2.0)
        gl = d.l / 2.0

        if d.w < PAD_H_MIN:
            # Dog-boned: full pad height either side of the gate, narrowed
            # to the device's real W only at the gate crossing -- the
            # technique layout/cells/ro_stage/build.py's docstring
            # documents, applied per-device instead of per-series-pair.
            canvas.rect(
                COMP, source_x - PAD_W / 2, y_center - pad_half, gate_x - gl, y_center + pad_half
            )
            canvas.rect(
                COMP, gate_x - gl, y_center - narrow_half, gate_x + gl, y_center + narrow_half
            )
            canvas.rect(
                COMP, gate_x + gl, y_center - pad_half, drain_x + PAD_W / 2, y_center + pad_half
            )
        else:
            # W already at/above the pad-safe minimum: one uniform-height
            # rectangle, no narrowing needed anywhere.
            canvas.rect(
                COMP,
                source_x - PAD_W / 2,
                y_center - pad_half,
                drain_x + PAD_W / 2,
                y_center + pad_half,
            )

        _terminal(canvas, terminals, d.source, source_x, y_center)
        _terminal(canvas, terminals, d.drain, drain_x, y_center)

        # Gate poly: a narrow strip crossing the channel (measured width =
        # d.w at the comp overlap -- the extractor measures W there, not
        # at the widest point of the diffusion, same as ro_stage), plus a
        # widened landing pad above the row for the gate's own contact.
        # The two pieces overlap by 0.05um so they merge into one net.
        canvas.rect(
            POLY2, gate_x - gl, y_center - narrow_half - 0.20, gate_x + gl, landing_y0 + 0.05
        )
        canvas.rect(
            POLY2, gate_x - LANDING_W / 2, landing_y0, gate_x + LANDING_W / 2, landing_y1
        )
        _terminal(canvas, terminals, d.gate, gate_x, (landing_y0 + landing_y1) / 2)

        x += 3 * SLOT_PITCH

    x_end = x - SLOT_PITCH  # last device's drain-pad centre X
    return x_end, y_center - max_pad_half, row_top, landing_y1


def _terminal(
    canvas: _Canvas,
    terminals: dict[str, list[tuple[float, float]]],
    net: str,
    x: float,
    y: float,
) -> None:
    """Contact -> Metal1 -> Via1 -> Metal2 stub -> Via2, all centred at
    `(x, y)`; records `(x, y)` under `net` for `_route_nets` to riser up
    to that net's trunk.
    """
    h = CONTACT_SIZE / 2
    canvas.rect(CONTACT, x - h, y - h, x + h, y + h)
    m1 = METAL1_PAD / 2
    canvas.rect(METAL1, x - m1, y - m1, x + m1, y + m1)
    canvas.rect(VIA1, x - h, y - h, x + h, y + h)
    m2 = METAL2_STUB / 2
    canvas.rect(METAL2, x - m2, y - m2, x + m2, y + m2)
    canvas.rect(VIA2, x - h, y - h, x + h, y + h)
    terminals[net].append((x, y))


def _route_nets(
    canvas: _Canvas,
    terminals: dict[str, list[tuple[float, float]]],
    pins: list[str],
    channel_y0: float,
) -> None:
    """One Metal2 trunk per net (stacked by Y, `TRUNK_PITCH` apart,
    starting at `channel_y0`), one Metal3 riser per terminal (at that
    terminal's own X, already unique across the whole cell -- see the
    module docstring). Only declared `pins` get a Metal2-purpose label;
    internal nets are left unlabelled and matched by topology alone, the
    same as `ro_stage`'s own internal `py`/`ny` nodes.
    """
    internal = sorted(net for net in terminals if net not in pins)
    ordered_nets = list(pins) + internal
    for index, net in enumerate(ordered_nets):
        points = terminals.get(net)
        if not points:
            continue
        trunk_y = channel_y0 + index * TRUNK_PITCH
        xs: list[float] = []
        for x, y in points:
            m3 = METAL3_W / 2
            y0, y1 = sorted((y, trunk_y))
            canvas.rect(METAL3, x - m3, y0, x + m3, y1)
            h = CONTACT_SIZE / 2
            canvas.rect(VIA2, x - h, trunk_y - h, x + h, trunk_y + h)
            xs.append(x)
        x0, x1 = min(xs), max(xs)
        if x1 - x0 < METAL2_TRUNK_H:
            pad = (METAL2_TRUNK_H - (x1 - x0)) / 2 + 0.02
            x0 -= pad
            x1 += pad
        th = METAL2_TRUNK_H / 2
        canvas.rect(METAL2, x0, trunk_y - th, x1, trunk_y + th)
        if net in pins:
            canvas.label(METAL2_LABEL, (x0 + x1) / 2, trunk_y, net)


def build_cell(
    top_cell: str,
    pins: list[str],
    nmos: list[Device],
    pmos: list[Device],
    path: str,
) -> bytes:
    """Draw `top_cell` (an NMOS row, a PMOS row, and the routing grid
    connecting every device terminal by net) and write it to `path`.
    """
    canvas = _Canvas()
    terminals: dict[str, list[tuple[float, float]]] = defaultdict(list)

    nmos_end, nmos_bottom, nmos_top, nmos_landing_top = _place_row(
        canvas, nmos, ROW_Y, 0.0, terminals
    )
    pmos_x0 = nmos_end + BLOCK_GAP if nmos else 0.0
    pmos_end, pmos_bottom, pmos_top, pmos_landing_top = _place_row(
        canvas, pmos, ROW_Y, pmos_x0, terminals
    )

    if pmos:
        # One Nwell rectangle enclosing every PMOS device's comp (plus
        # margin) -- see the module docstring on why this is what makes
        # every PMOS body land on the *same* floating net.
        canvas.rect(
            NWELL,
            pmos_x0 - PAD_W / 2 - NWELL_MARGIN,
            pmos_bottom - NWELL_MARGIN,
            pmos_end + PAD_W / 2 + NWELL_MARGIN,
            pmos_top + NWELL_MARGIN,
        )

    channel_y0 = max(nmos_landing_top, pmos_landing_top) + CHANNEL_MARGIN
    _route_nets(canvas, terminals, pins, channel_y0)

    return write_gds(path, library_name=top_cell, structures=[(top_cell, canvas.rects, canvas.labels)])
