#!/usr/bin/env python3
"""Assemble `combiner_sampler` (2x `ro_buf` + `xor2` + 4x `sampler_dff`)
from the drawn cells, and check it.

    python3 layout/blocks/combiner_sampler/build.py            # write .gds
    python3 layout/blocks/combiner_sampler/build.py --check    # rebuild, compare bytes
    python3 layout/blocks/combiner_sampler/build.py --require-tools  # fail, don't skip

`combiner_sampler` is `design/ro_array_core.spice`'s `xb1`/`xb2` (`ro_buf`,
DR-0018's per-ring output buffer, lines 17-18) plus `design/
sampler_core.spice`'s `xa1` (`xor2`) and its `xsb`/`xsv`/`xsr1`/`xsr2`
(`sampler_dff`) instances -- both buffers, the entropy source's combining
gate, and its four samplers (raw bit, raw-valid, and the two DR-0016
per-ring liveness taps), per `layout/floorplan/`'s own `combiner_sampler`
guarded region (issue #16). This module places the seven already-drawn,
individually DRC-clean/LVS-matching cells (`layout/cells/ro_buf/` twice,
`layout/cells/xor2/` once, `layout/cells/sampler_dff/` four times) into a
single row and draws the metal connecting them, producing one composed,
DRC-clean, LVS-matching `combiner_sampler` layout -- the same rung
`layout/rings/ro_ring11/build.py` established for `ring1` (issue #110).

Originally (issue #134) this block assembled only the combiner and the four
samplers, with `ro1`/`ro2` (ring1's/ring2's own buffered outputs) as its own
top-level input pins; the two `ro_buf` instances that produce `ro1`/`ro2`
were budgeted into this region (`layout/floorplan/floorplan.py`'s
`REGIONS["combiner_sampler"]`) but not drawn into any assembly, since
adding them to the old reference netlist without also declaring them there
would have reported four extra devices as `device.unmatched`. Issue #151
closes that gap: both buffers are now placed and wired inside this same
block, `ro1`/`ro2` are internal nets, and `rn1`/`rn2` (each ring's own
un-buffered output, `design/ro_array_core.spice`'s own node names) are this
block's new top-level input pins in their place. Placing the assembled
result inside `layout/floorplan/`'s own guarded `combiner_sampler` region
(sized from this block's own real bbox, `check_ring_fit`) is issue #135's
own resolution, applied unchanged here since `layout/floorplan/floorplan.py`
reads this block's bbox at run time rather than a value cached at #135's own
time.

Connectivity (`design/ro_array_core.spice`'s own `xb1`/`xb2` instances,
lines 17-18, plus `design/sampler_core.spice`'s own declared instances):

    xb1  rn1                       ro1            vdd vss   ro_buf
    xb2  rn2                       ro2            vdd vss   ro_buf
    xa1  ro1 ro2 xo   vdd vss                  xor2
    xsb  xo  clk rst_n raw_bit    vdd vss       sampler_dff
    xsv  vdd clk rst_n raw_valid  vdd vss       sampler_dff  (d tied to vdd)
    xsr1 ro1 clk rst_n ring_bit1  vdd vss       sampler_dff
    xsr2 ro2 clk rst_n ring_bit2  vdd vss       sampler_dff

`ro1`/`ro2` are each driven by their own `ro_buf` instance (`xb1`/`xb2`) and
each reach *two* further cells inside this block (`xa1`'s own `a`/`b` input
and `xsr1`/`xsr2`'s own `d` input), so both are three-terminal nets needing
an internal tie. `clk`/`rst_n` tie all four samplers together; `vdd`/`vss`
tie all seven cells (plus `xsv`'s own `d`, wired straight to `vdd` by the
schematic, not a separate external net). `xb1`/`xb2`'s own `rn1`/`rn2`,
`xsb`'s own `raw_bit`, `xsv`'s own `raw_valid`, and `xsr1`/`xsr2`'s own
`ring_bit1`/`ring_bit2` are this block's own boundary pins (two inputs, four
outputs) -- left as each cell's own pin pad with no further routing, the
same way `ro_ring11`'s own `en`/`ro` pins are left unrouted past the ring's
own row (assembly places and wires what is *inside* the block; routing a
pin out to the guarded region's own boundary is a placement-level concern,
out of this module's own scope, same division `layout/rings/README.md`
already draws).

Row placement, left to right: `xb1, xb2, xa1, xsb, xsv, xsr1, xsr2` (each
`ro_buf` ahead of the cell it feeds, then `design/sampler_core.spice`'s own
instance order), `ROW_GAP_UM` apart -- computed the same way
`layout/rings/ro_ring11/build.py`'s own `row_offsets()` is (and,
transitively, the same arithmetic `klt gen-compose`'s own
`placement.strategy: "row"` would use).

Why the wiring is hand-routed, and why it looks different from
`ro_ring11`'s
------------------------------------------------------------------------
`xor2`/`sampler_dff` are drawn by the shared `layout/cells/_mos_row.py`
engine (issue #109), not hand-placed like `ro_stage`/`ro_nand2`: every
declared pin already lands on its own **Metal2 trunk** (`_mos_row.py`'s
`_route_nets`), a horizontal strip at a pin-specific Y, spanning every
terminal that net touches within the cell. That is a *different* interface
than `ro_stage`/`ro_nand2`'s own single-point Metal1 pads
(`STAGE_LOCAL`/`NAND_LOCAL` in `ro_ring11/build.py`), so this module's own
wiring plan differs from that file's, even though the underlying technique
(`klt draw` for the wiring stream, `klt gen-compose` with
`placement.strategy: "explicit"` for translation-only placement, per
klayout-tools#330) is identical:

- Every pin this module needs to tie together is reached by picking one
  point on its own local Metal2 trunk (`*_LOCAL` dictionaries below, each
  value the trunk's own centre X, transcribed from a small offline script
  that re-runs `_mos_row.py`'s own `_place_row`/`_route_nets` arithmetic on
  `xor2`/`sampler_dff`'s own committed `NMOS`/`PMOS` device lists -- see
  "Deriving the *_LOCAL tables" below -- and cross-checked against `klt
  stats`'s own bbox for both committed cells).
- From each such point, a **Metal3** riser (`VIA2` at the bottom, landing on
  the cell's own existing Metal2 trunk) climbs straight up to a
  **block-level Metal2 track** dedicated to that net (`TRACK_Y`, one row per
  net, stacked `TRACK_PITCH` apart, all starting above `TRACK_FLOOR_UM` --
  higher than the tallest net any placed cell draws on its own, so no new
  track's own Y band ever overlaps an existing cell-internal Metal2 trunk,
  by construction rather than by a router's own overlap check), then another
  `VIA2` drops back down at the far end. The block-level track itself is
  Metal2, spanning every terminal X the net touches.
- This is the *same two-layer idea* `ro_ring11/build.py`'s own maze routing
  uses (Metal1 for the ring's own signal chain, Metal2 + Via1 for the
  rails, so the two families never cross on the same layer) one level up:
  Metal3 crossing freely over any cell's own internal Metal2 trunk (no
  `Via2` there, so no short) is what makes an "elevated track, connect from
  above" plan work without a maze search at all here -- unlike `ro_nand2`'s
  dense internal metal1, nothing in `xor2`'s or `sampler_dff`'s own drawn
  geometry sits *above* that cell's own tallest trunk, so the space this
  module routes through is provably empty before it ever draws anything in
  it.

`ro_buf`, added by issue #151, is a *third* interface again: it is
hand-drawn (`layout/cells/ro_buf/build.py`, not `_mos_row.py`), so its four
pins (`a`/`y`/`vdd`/`vss`) each land on a bare **Metal1** pad, not a Metal2
trunk -- there is no Metal2 anywhere in the committed `ro_buf.gds` for a
riser to extend from. `RO_BUF_LOCAL`'s three routed pins (`y`/`vdd`/`vss` --
`a` is this block's own `rn1`/`rn2` input pin, a single-terminal net left
unrouted, same treatment as `raw_bit` etc.) therefore each get one extra
step before the usual sideways-hop-then-riser: a `Via1` plus a small Metal2
stub landing directly on that pin's own drawn Metal1 pad, the same
Contact-already-drawn half of `_mos_row.py`'s own `_terminal()` pattern
(`Via1` -> Metal2 stub -> `Via2` riser), just applied to a hand-drawn pad
instead of a generated one. `RO_BUF_STUB_NEEDED` below is what tells
`_wiring_shapes` which terminals need that extra step.

Choosing `y`'s own tap point took one extra bit of care `xor2`'s/
`sampler_dff`'s pins never need: `ro_buf`'s `y` net is strapped across two
disjoint Metal1 pads (one on the NMOS row, Y=0.22; one on the PMOS row,
Y=1.86 -- see `ro_buf/build.py`'s own `Y_NMOS`/`Y_PMOS`), and those two Y
values are exactly where `vss` and `vdd`'s own pads sit. Tapping `y` at
either pad would put its own Metal2 stub at the *same* Y as `vss`'s or
`vdd`'s -- and since a stub's own sideways hop extends in X from its pin
toward its own gap slot, two different nets' stubs sharing a Y band would
overlap in X too (their hops are not confined to disjoint X ranges the way
`xor2`'s/`sampler_dff`'s per-net trunk Y already keeps them apart), merging
two nets into one polygon. `y`'s own drawn Metal1 is not only the two pads:
a vertical strap (`ro_buf/build.py`'s own metal1 rect joining them,
X 0.23-0.47, Y 0.40-1.68) ties them together, and Y=1.00 on that strap sits
comfortably clear of both `vss` (Y=0.22) and `vdd` (Y=1.86) by more than
`metal2.space.1` even after each stub's own half-height -- so `RO_BUF_LOCAL`
taps `y` there instead of at either pad.

Deriving the `*_LOCAL` tables
------------------------------
`_mos_row.py`'s `_place_row`/`_route_nets` are ordinary Python functions,
not private in the language sense (leading underscore is a naming
convention here, not an import guard) -- so the `XOR2_LOCAL`/
`SAMPLER_LOCAL` numbers below were produced by importing that module
directly and re-running its own placement/trunk arithmetic against
`layout/cells/xor2/build.py`'s and `layout/cells/sampler_dff/build.py`'s
own committed `NMOS`/`PMOS` lists, capturing each net's own trunk
`(x0, x1, y)` instead of writing GDS. That is a re-derivation of the exact
same deterministic computation `build_cell` already ran to draw the
committed `.gds` files (same inputs, same pure functions), not a guess at
their geometry -- and every `XOR2_LOCAL`/`SAMPLER_LOCAL` X/Y pair is a
**trunk interior point**, verified to land strictly inside that net's own
drawn Metal2 span, not merely close to it. `RO_BUF_LOCAL`'s numbers were
produced the same way in spirit, but against `layout/cells/ro_buf/
build.py`'s own hand-drawn rectangle list directly (there is no
`_route_nets`-style trunk to re-derive since `ro_buf` draws no Metal2 at
all) -- each entry is the centre of that pin's own drawn Metal1 pad (`a`,
`vdd`, `vss`) or a verified-interior point of its own drawn Metal1 strap
(`y`, see above). `klt drc`/`klt lvs` on this module's own output is what
actually proves the result: same convention `ro_ring11/build.py`'s own
maze-routing waypoints follow (module docstring, "Maze routing").

Standard library only, `klayout.db` never imported directly -- same as
every other build script in this repository.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CELL_DIR = Path(__file__).resolve().parent
TOP_CELL = "combiner_sampler"

#: Scratch space, git-ignored, shared with the rest of layout/ (see
#: layout/verify.py / layout/floorplan/floorplan.py's own WORK_DIR).
WORK_DIR = REPO_ROOT / "layout" / ".work"

sys.path.insert(0, str(REPO_ROOT))

from layout._klt import _run_klt, klt_version, normalise_gds, resolve_pdk  # noqa: E402

# --------------------------------------------------------------------------- #
# Layers -- gf180mcu drawn layers. Metal3/Via2 for the block-level routing
# (see module docstring for why this level uses Metal3/Via2 rather than
# ro_ring11's Metal1/Metal2/Via1); Via1 additionally for the Metal1->Metal2
# stub `ro_buf`'s own hand-drawn pins need before they can join that
# block-level routing (module docstring, the `ro_buf` paragraph).
# --------------------------------------------------------------------------- #
VIA1 = [35, 0]
VIA2 = [38, 0]
METAL2 = [36, 0]
METAL3 = [42, 0]

# --------------------------------------------------------------------------- #
# Drawn-cell geometry -- bbox_um from `klt stats` on the committed .gds
# files (authoritative for placement); pin trunk `(x0, x1, y)` from
# re-running _mos_row.py's own placement/trunk arithmetic against xor2's/
# sampler_dff's own committed device lists, or (for ro_buf) directly from
# ro_buf/build.py's own hand-drawn rectangle list (see module docstring,
# "Deriving the *_LOCAL tables"). A geometry change in any sibling cell must
# be mirrored here, the same rule ro_ring11/build.py's own header states for
# STAGE_BBOX/NAND_BBOX; klt drc/klt lvs on this module's own output is the
# check that catches a missed mirror.
# --------------------------------------------------------------------------- #
RO_BUF_BBOX = {"x0": -0.50, "y0": -0.30, "x1": 1.93, "y1": 2.38}
XOR2_BBOX = {"x0": -0.22, "y0": 0.31, "x1": 30.67, "y1": 8.59}
SAMPLER_BBOX = {"x0": -0.22, "y0": 0.53, "x1": 54.67, "y1": 10.97}

#: {cell kind -> bbox}, for the placement/wiring helpers below.
CELL_BBOX = {"ro_buf": RO_BUF_BBOX, "xor2": XOR2_BBOX, "sampler_dff": SAMPLER_BBOX}

#: {pin: (trunk centre X, trunk Y)} in the cell's own local frame -- for
#: `xor2`/`sampler_dff`, every value is the centre of that pin's own Metal2
#: trunk (`_mos_row.py`'s `_route_nets`), which is always strictly inside
#: the trunk's own drawn X-span (the trunk exists specifically to span
#: every terminal the net touches, and its centre is never a terminal's own
#: exact X except by coincidence -- not the case for any pin used here,
#: checked against the derivation script's own printed spans).
XOR2_LOCAL = {
    "a": (11.5, 2.59),
    "b": (13.9, 3.24),
    "y": (18.3, 3.89),
    "vdd": (20.2, 4.54),
    "vss": (6.0, 5.19),
}
SAMPLER_LOCAL = {
    "d": (18.3, 2.37),
    "clk": (27.1, 3.02),
    "rst_n": (35.5, 3.67),
    "q": (31.1, 4.32),
    "vdd": (39.4, 4.97),
    "vss": (12.0, 5.62),
}
#: `ro_buf` draws no Metal2 trunk at all (module docstring, "ro_buf" and
#: "Choosing y's own tap point") -- each value here is instead a verified-
#: interior point of that pin's own drawn Metal1 (a pad centre for `a`/
#: `vdd`/`vss`; a point on the `y` net's own connecting strap, chosen clear
#: of `vdd`'s/`vss`'s own Y). `a` is never used for routing (it is this
#: block's own `rn1`/`rn2` input pin, a single-terminal net -- see
#: ROUTED_NETS below) but is listed for completeness, the same convention
#: SAMPLER_LOCAL's own unrouted `q` entry follows.
RO_BUF_LOCAL = {
    "a": (-0.29, 1.00),
    "y": (0.35, 1.00),
    "vdd": (1.33, 1.86),
    "vss": (1.33, 0.22),
}

#: {cell kind -> pin table}, for the placement/wiring helpers below.
CELL_LOCAL = {"ro_buf": RO_BUF_LOCAL, "xor2": XOR2_LOCAL, "sampler_dff": SAMPLER_LOCAL}

#: Row order -- each `ro_buf` ahead of the cell its own buffered output
#: feeds, then design/sampler_core.spice's own instance order (`xa1`,
#: `xsb`, `xsv`, `xsr1`, `xsr2`). The block-level "elevated track" routing
#: plan (module docstring) does not depend on adjacency for wiring cost the
#: way ro_ring11's chain wiring does, so this order is chosen for
#: readability (matches the schematic), not for a routing-distance
#: reason.
ROW_ORDER = ["xb1", "xb2", "xa1", "xsb", "xsv", "xsr1", "xsr2"]
#: Wide enough for every routed net's own gap riser (see `GAP_MARGIN_UM`/
#: `GAP_SLOT_PITCH_UM` below) to fit between two adjacent cells with margin
#: to spare before the next cell's own drawn geometry starts -- checked by
#: `klt drc`, not merely asserted.
ROW_GAP_UM = 6.0

#: Each instance's own cell kind, for bbox/pin-table lookup.
INSTANCE_CELL = {
    "xb1": "ro_buf",
    "xb2": "ro_buf",
    "xa1": "xor2",
    "xsb": "sampler_dff",
    "xsv": "sampler_dff",
    "xsr1": "sampler_dff",
    "xsr2": "sampler_dff",
}

#: Each instance's own (pin -> net) map, transcribed directly from
#: design/ro_array_core.spice's `xb1`/`xb2` instances (lines 17-18) and
#: design/sampler_core.spice's declared instances (module docstring).
INSTANCE_NETS = {
    "xb1": {"a": "rn1", "y": "ro1", "vdd": "vdd", "vss": "vss"},
    "xb2": {"a": "rn2", "y": "ro2", "vdd": "vdd", "vss": "vss"},
    "xa1": {"a": "ro1", "b": "ro2", "y": "xo", "vdd": "vdd", "vss": "vss"},
    "xsb": {"d": "xo", "clk": "clk", "rst_n": "rst_n", "q": "raw_bit",
            "vdd": "vdd", "vss": "vss"},
    "xsv": {"d": "vdd", "clk": "clk", "rst_n": "rst_n", "q": "raw_valid",
            "vdd": "vdd", "vss": "vss"},
    "xsr1": {"d": "ro1", "clk": "clk", "rst_n": "rst_n", "q": "ring_bit1",
             "vdd": "vdd", "vss": "vss"},
    "xsr2": {"d": "ro2", "clk": "clk", "rst_n": "rst_n", "q": "ring_bit2",
             "vdd": "vdd", "vss": "vss"},
}

#: Nets that need a block-level tie -- everything with more than one
#: terminal inside this block. `rn1`/`rn2` (each touched only by its own
#: `ro_buf`'s `a` pin) and `raw_bit`/`raw_valid`/`ring_bit1`/`ring_bit2`
#: (each touched by exactly one pin) are left unrouted -- module docstring:
#: left as that cell's own pin pad, no further routing -- the same
#: treatment ro_ring11's own `en`/`ro` pins get. `ro1`/`ro2` stay routed:
#: each now has three terminals (its own `ro_buf`'s `y`, plus the same two
#: consumers as before), not two, but the routing scheme below already
#: handles any terminal count >= 2 uniformly.
ROUTED_NETS = ["xo", "ro1", "ro2", "clk", "rst_n", "vdd", "vss"]

#: Block-level routing geometry (module docstring, "Why the wiring is
#: hand-routed"). `TRACK_FLOOR_UM` clears SAMPLER_BBOX's own top (10.97,
#: the tallest of the placed cells) by more than metal2.space.1 (0.28 um);
#: `TRACK_PITCH_UM` clears metal2.width.1 + metal2.space.1 (0.28 + 0.28)
#: with margin, the same pitch _mos_row.py's own TRUNK_PITCH uses inside
#: each cell.
TRACK_FLOOR_UM = 11.6
TRACK_PITCH_UM = 0.7
RISER_W = 0.30  # Metal3 riser width, same as _mos_row.py's METAL3_W
TRACK_H = 0.30  # Metal2 track height, same as _mos_row.py's METAL2_TRUNK_H
VIA_SZ = 0.22  # Via2 size, same as _mos_row.py's CONTACT_SIZE

#: `ro_buf`'s own routed pins (module docstring, "ro_buf") need a Via1 +
#: small Metal2 stub landing on their own drawn Metal1 pad before the usual
#: sideways-hop-then-riser applies -- `RO_BUF_VIA1_SZ` matches this file's
#: own `VIA_SZ` (no width/enclosure rule constrains either Via1 or Via2 in
#: this deck -- see layout/cells/_mos_row.py's own module docstring, which
#: confirms this by grepping the deck's own DrcRule table); `RO_BUF_STUB_UM`
#: matches `TRACK_H` (both >= metal2.width.1's 0.28 um floor).
RO_BUF_VIA1_SZ = 0.22
RO_BUF_STUB_UM = 0.30

#: Each pin's own local Metal2 trunk already runs almost the full width of
#: its own cell (`_mos_row.py`'s `_route_nets` spans every terminal the net
#: touches), so a riser dropped straight up from a point *inside* the cell
#: risks running close-and-parallel to some *other* net's own per-terminal
#: Metal3 riser somewhere along the way (found by `klt drc`, not by
#: inspection -- see this module's own commit history for the
#: `metal3.space.1` violations that first exposed it). The fix is not a
#: closer read of the geometry, it is to never put a riser inside a cell's
#: own drawn footprint in the first place: every routed net's own Metal2
#: trunk is instead extended sideways (same Y, same layer -- so this never
#: changes that net's own already-DRC-clean internal spacing, only its own
#: X extent) out into the empty gap after its own cell, and the riser climbs
#: there instead, where nothing else is ever drawn. `GAP_MARGIN_UM` is how
#: far into the gap the first slot starts; `GAP_SLOT_PITCH_UM` (comfortably
#: above metal3.width.1 + metal3.space.1 = 0.28 + 0.28) is the spacing
#: between the (up to `len(ROUTED_NETS))` slots one gap can hold --
#: `ROW_GAP_UM` is sized to fit every slot with room to spare before the
#: next cell's own geometry begins.
GAP_MARGIN_UM = 0.4
GAP_SLOT_PITCH_UM = 0.65

DECK = "gf180mcu"
EXIT_OK = 0
EXIT_FAIL = 1


# --------------------------------------------------------------------------- #
# Row placement
# --------------------------------------------------------------------------- #


def row_offsets() -> dict[str, float]:
    """Left-to-right row offsets, `ROW_GAP_UM` apart -- the same arithmetic
    `layout/rings/ro_ring11/build.py`'s own `row_offsets()` uses."""
    offsets: dict[str, float] = {}
    cursor_x1: float | None = None
    for inst in ROW_ORDER:
        bbox = CELL_BBOX[INSTANCE_CELL[inst]]
        offset_x = 0.0 if cursor_x1 is None else (cursor_x1 + ROW_GAP_UM) - bbox["x0"]
        offsets[inst] = offset_x
        cursor_x1 = bbox["x1"] + offset_x
    return offsets


def row_bbox_um(offsets: dict[str, float]) -> dict:
    x0 = min(CELL_BBOX[INSTANCE_CELL[i]]["x0"] + offsets[i] for i in ROW_ORDER)
    x1 = max(CELL_BBOX[INSTANCE_CELL[i]]["x1"] + offsets[i] for i in ROW_ORDER)
    y0 = min(CELL_BBOX[INSTANCE_CELL[i]]["y0"] for i in ROW_ORDER)
    y1 = max(CELL_BBOX[INSTANCE_CELL[i]]["y1"] for i in ROW_ORDER)
    return {"x0": x0, "y0": y0, "x1": x1, "y1": y1}


# --------------------------------------------------------------------------- #
# Wiring geometry (klt draw's own JSON shape list)
# --------------------------------------------------------------------------- #


def _rect(layer: list[int], x0: float, y0: float, x1: float, y1: float) -> dict:
    return {"layer": layer, "rect_um": [x0, y0, x1, y1]}


def _net_terminals(
    net: str, offsets: dict[str, float]
) -> list[tuple[float, float, float, bool]]:
    """Every (pin's own global X, gap-slot global X, local Y, needs a Via1 +
    Metal2 stub first) tuple this net touches inside the block -- the
    gap-slot X is where this specific terminal's own riser actually climbs
    (module docstring, "Block-level routing geometry"), always in the empty
    gap just after that terminal's own instance, never inside a cell's own
    drawn footprint. The last element is True only for a `ro_buf` terminal
    (module docstring, "ro_buf") -- `xor2`/`sampler_dff` pins already sit on
    their own Metal2 trunk and need no such stub.
    """
    net_index = ROUTED_NETS.index(net)
    points: list[tuple[float, float, float, bool]] = []
    for inst in ROW_ORDER:
        for pin, n in INSTANCE_NETS[inst].items():
            if n != net:
                continue
            cell = INSTANCE_CELL[inst]
            bbox = CELL_BBOX[cell]
            local = CELL_LOCAL[cell][pin]
            pin_x = local[0] + offsets[inst]
            gap_x = bbox["x1"] + offsets[inst] + GAP_MARGIN_UM + net_index * GAP_SLOT_PITCH_UM
            points.append((pin_x, gap_x, local[1], cell == "ro_buf"))
    return points


def _wiring_shapes(offsets: dict[str, float]) -> list[dict]:
    shapes: list[dict] = []

    for index, net in enumerate(ROUTED_NETS):
        track_y = TRACK_FLOOR_UM + index * TRACK_PITCH_UM
        points = _net_terminals(net, offsets)
        assert len(points) >= 2, f"net {net!r} has fewer than 2 terminals: {points}"

        for pin_x, gap_x, y_local, needs_stub in points:
            if needs_stub:
                # ro_buf's own pins are bare Metal1 pads with no Metal2
                # trunk yet (module docstring, "ro_buf") -- land a Via1 +
                # small Metal2 stub directly on that pad first, so the
                # sideways hop below has a Metal2 shape to extend from and
                # Via1 makes the Metal1<->Metal2 tie. Centred at the same
                # (pin_x, y_local) the hop and riser below use, so it
                # overlaps both the cell's own drawn Metal1 (by
                # construction, see the *_LOCAL tables' own docstring) and
                # the hop rectangle immediately below (which starts exactly
                # at pin_x).
                shapes.append(_rect(
                    VIA1,
                    pin_x - RO_BUF_VIA1_SZ / 2, y_local - RO_BUF_VIA1_SZ / 2,
                    pin_x + RO_BUF_VIA1_SZ / 2, y_local + RO_BUF_VIA1_SZ / 2,
                ))
                shapes.append(_rect(
                    METAL2,
                    pin_x - RO_BUF_STUB_UM / 2, y_local - RO_BUF_STUB_UM / 2,
                    pin_x + RO_BUF_STUB_UM / 2, y_local + RO_BUF_STUB_UM / 2,
                ))

            # Sideways hop: extend this pin's own local Metal2 trunk (same
            # Y, so this never touches any other net's own Y-band) out to
            # its own gap slot -- still well inside empty silicon, no via
            # needed since it is one contiguous Metal2 polygon with the
            # cell's own already-drawn trunk (pin_x sits inside that
            # trunk's own drawn span by construction, see the *_LOCAL
            # tables' own docstring) or, for a `ro_buf` pin, with the stub
            # just drawn above.
            hx0, hx1 = sorted((pin_x, gap_x))
            shapes.append(_rect(METAL2, hx0, y_local - TRACK_H / 2, hx1, y_local + TRACK_H / 2))

            # Riser: from the gap slot (guaranteed clear of any cell's own
            # geometry at every Y) straight up to this net's own
            # block-level track. Via2 at both ends.
            y0, y1 = sorted((y_local, track_y))
            shapes.append(_rect(METAL3, gap_x - RISER_W / 2, y0, gap_x + RISER_W / 2, y1))
            shapes.append(_rect(VIA2, gap_x - VIA_SZ / 2, y_local - VIA_SZ / 2,
                                 gap_x + VIA_SZ / 2, y_local + VIA_SZ / 2))
            shapes.append(_rect(VIA2, gap_x - VIA_SZ / 2, track_y - VIA_SZ / 2,
                                 gap_x + VIA_SZ / 2, track_y + VIA_SZ / 2))

        xs = [gap_x for _, gap_x, _, _ in points]
        x0, x1 = min(xs), max(xs)
        shapes.append(_rect(METAL2, x0, track_y - TRACK_H / 2, x1, track_y + TRACK_H / 2))

    return shapes


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #


def gds_path() -> Path:
    return CELL_DIR / f"{TOP_CELL}.gds"


def build(pdk_variant: str, path: Path | None = None) -> bytes:
    """Draw the wiring, compose the row, and return the normalised GDS bytes.

    Writes scratch artefacts under `layout/.work/`; the composed, normalised
    stream is returned (and, unless `path` overrides it, also written to
    `path`), the same convention `layout/rings/ro_ring11/build.py`'s own
    `build()` follows.
    """
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    offsets = row_offsets()

    shapes = _wiring_shapes(offsets)
    draw_params_path = WORK_DIR / "combiner_sampler_wiring_params.json"
    draw_params_path.write_text(json.dumps({"shapes": shapes}, indent=2) + "\n")
    wiring_gds = WORK_DIR / "combiner_sampler_wiring.gds"
    draw_resp = _run_klt([
        "draw", "--params", str(draw_params_path.relative_to(REPO_ROOT)),
        "--cell-name", "combiner_sampler_wiring",
        "-o", str(wiring_gds.relative_to(REPO_ROOT)),
    ])

    def _report(generator: str, cell_name: str, gds: Path, bbox: dict) -> dict:
        return {
            "generator": generator, "cell_name": cell_name,
            "gds_path": str(gds.relative_to(REPO_ROOT) if gds.is_absolute() else gds),
            "bbox_um": bbox, "ports": [],
        }

    gr_ro_buf = _report("layout.cells.ro_buf", "ro_buf",
                         REPO_ROOT / "layout/cells/ro_buf/ro_buf.gds", RO_BUF_BBOX)
    gr_xor2 = _report("layout.cells.xor2", "xor2",
                       REPO_ROOT / "layout/cells/xor2/xor2.gds", XOR2_BBOX)
    gr_sampler = _report("layout.cells.sampler_dff", "sampler_dff",
                          REPO_ROOT / "layout/cells/sampler_dff/sampler_dff.gds", SAMPLER_BBOX)
    gr_wire = _report("layout.blocks.combiner_sampler.wiring", "combiner_sampler_wiring",
                       wiring_gds, draw_resp["bbox_um"])

    reports = {"ro_buf": WORK_DIR / "combiner_sampler_gr_ro_buf.json",
               "xor2": WORK_DIR / "combiner_sampler_gr_xor2.json",
               "sampler_dff": WORK_DIR / "combiner_sampler_gr_sampler.json",
               "wire": WORK_DIR / "combiner_sampler_gr_wire.json"}
    reports["ro_buf"].write_text(json.dumps(gr_ro_buf, indent=2) + "\n")
    reports["xor2"].write_text(json.dumps(gr_xor2, indent=2) + "\n")
    reports["sampler_dff"].write_text(json.dumps(gr_sampler, indent=2) + "\n")
    reports["wire"].write_text(json.dumps(gr_wire, indent=2) + "\n")

    blocks = []
    origins = {}
    for inst in ROW_ORDER:
        report_path = reports[INSTANCE_CELL[inst]]
        blocks.append({"id": inst, "generator_report": report_path.name})
        origins[inst] = {"x": offsets[inst], "y": 0.0}
    blocks.append({"id": "wire", "generator_report": reports["wire"].name})
    origins["wire"] = {"x": 0.0, "y": 0.0}

    compose_request = {
        "_comment": (
            "Generated by layout/blocks/combiner_sampler/build.py. Re-run by "
            "hand with: klt gen-compose "
            "layout/.work/combiner_sampler-compose-request.json (from the "
            "repo root, so options.output lands at "
            "layout/.work/combiner_sampler.gds)"
        ),
        "blocks": blocks,
        "placement": {"strategy": "explicit", "order": ROW_ORDER + ["wire"], "origins_um": origins},
        "pdk": {"variant": pdk_variant},
        "options": {"cell_name": TOP_CELL, "output": "layout/.work/combiner_sampler.gds"},
    }
    request_path = WORK_DIR / "combiner_sampler-compose-request.json"
    request_path.write_text(json.dumps(compose_request, indent=2) + "\n")
    _run_klt(["gen-compose", str(request_path.relative_to(REPO_ROOT))])

    gds_bytes = normalise_gds((WORK_DIR / "combiner_sampler.gds").read_bytes())
    target = path or gds_path()
    target.write_bytes(gds_bytes)
    return gds_bytes


def check() -> int:
    """Rebuild into scratch and byte-compare against the committed .gds.

    Matches `layout/rings/ro_ring11/build.py`'s own `check()` contract --
    `layout/verify.py`'s `_STALENESS_CHECKS` calls it with no arguments and
    treats a nonzero return as a hard failure.
    """
    path = gds_path()
    shown = os.path.relpath(path, os.getcwd())
    if not path.exists():
        print(f"MISSING: {shown} -- run `python3 layout/blocks/combiner_sampler/build.py`")
        return 1
    pdk = resolve_pdk()
    if pdk is None:
        print(f"SKIP-AS-STALE: {shown} -- no gf180mcu PDK install found")
        return 1
    scratch = WORK_DIR / f"{TOP_CELL}.check.gds"
    rebuilt = build(pdk.variant, scratch)
    committed = path.read_bytes()
    if rebuilt != committed:
        print(
            f"STALE: {shown} does not match build.py "
            f"({len(committed)} bytes committed, {len(rebuilt)} rebuilt) -- "
            f"run `python3 layout/blocks/combiner_sampler/build.py`"
        )
        return 1
    print(f"ok: {shown}")
    return 0


def print_table() -> None:
    offsets = row_offsets()
    bbox = row_bbox_um(offsets)
    print(f"{'instance':<8} {'cell':<14} offset_x_um")
    print("-" * 40)
    for inst in ROW_ORDER:
        print(f"{inst:<8} {INSTANCE_CELL[inst]:<14} {offsets[inst]:>10.3f}")
    print()
    print(f"row bbox: {bbox['x1'] - bbox['x0']:.2f} x {bbox['y1'] - bbox['y0']:.2f} um")
    print(f"routed nets: {', '.join(ROUTED_NETS)}")
    unrouted = sorted({n for inst in ROW_ORDER for n in INSTANCE_NETS[inst].values()}
                       - set(ROUTED_NETS))
    print(f"unrouted (single-terminal, own pin pad only): {', '.join(unrouted)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                         help="verify the committed .gds matches this script, and exit")
    parser.add_argument("--require-tools", action="store_true",
                         help="fail instead of skipping when klt or the PDK is absent")
    parser.add_argument("--list", action="store_true",
                         help="print the row placement table and exit")
    args = parser.parse_args(argv)

    if args.list:
        print_table()
        return EXIT_OK

    version = klt_version()
    pdk = resolve_pdk()
    missing = []
    if version is None:
        missing.append("klayout-tools (`klt`) is not on PATH")
    if pdk is None:
        missing.append("no gf180mcu PDK install found (see sim/harness/pdk.py)")
    if missing:
        for line in missing:
            print(f"  - {line}")
        if args.require_tools:
            print("FAIL: --require-tools was given and the flow cannot run")
            return EXIT_FAIL
        print("SKIP: combiner_sampler build -- the tools above are not available.")
        return EXIT_OK

    if args.check:
        return check()
    build(pdk.variant)
    print(f"wrote {gds_path()}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
