#!/usr/bin/env python3
"""Assemble `ro_ring11` (ring1 sizing) from the drawn `ro_stage`/`ro_nand2`
cells, and check it.

    python3 layout/rings/ro_ring11/build.py            # write ro_ring11.gds
    python3 layout/rings/ro_ring11/build.py --check    # rebuild, compare bytes
    python3 layout/rings/ro_ring11/build.py --require-tools  # fail, don't skip

`ro_ring11` is `design/ro_array_core.spice`'s `.subckt ro_ring11`: ten
`ro_stage` instances (`x1`..`x10`) plus one `ro_nand2` (`xg`, the ring's
stoppable stage), chained `xg.y -> x1.a -> x1.y -> x2.a -> ... -> x10.y ->
xg.a` -- a closed loop, not a straight chain. This module places all eleven
already-drawn, individually DRC-clean/LVS-matching cells
(`layout/cells/ro_stage/`, `layout/cells/ro_nand2/`) into a single row and
draws the metal connecting them, producing one composed, DRC-clean,
LVS-matching `ro_ring11` layout -- the "assemble" half of issue #110. It is
**ring1's own sizing only** (`wstv=0.220u`, `ro_nand2`'s only drawn
variant); ring2 needs its own `ro_nand2` at `wstv=0.240u` (`ro_stage_ring2`
already exists, `layout/cells/ro_stage_ring2/`, but no ring2-sized
`ro_nand2` does) -- see `layout/rings/README.md` for that gap and why this
module does not paper over it with the wrong-sized cell.

Two tools, both `klt`, no direct KLayout import (`layout/README.md`'s
"everything through klt" rule, same as every other build script here):

- `klt draw` writes the connecting metal as one more primitive GDSII
  stream, the same tool `layout/testcells/` uses for its own known-bad
  fixtures (a JSON shape list in, a stream out -- no PDK awareness, no rule
  checking, by design).
- `klt gen-compose` places the eleven cells' own `.gds` files, plus the
  wiring stream, into one composed cell -- `placement.strategy: "explicit"`
  (klayout-tools#330), a caller-declared `{x, y}` origin per block, used
  here purely for *translation*: every block keeps its own drawn geometry
  exactly as committed, gen-compose only offsets it. This module never
  calls gen-compose's own `connectivity[]` router (see "Why the wiring is
  hand-routed" below); it hands gen-compose a synthetic `generator_report`
  per block (`{generator, cell_name, gds_path, bbox_um, ports: []}`) since
  none of these blocks came from `klt gen` -- a hand-crafted report is an
  anticipated input (`gen_compose.route_two_pin`'s own docstring: "A block
  with no reported ports[] (a hand-crafted generator_report) can't supply a
  routable position"), not a workaround.

Row placement, ten `ro_stage` plus one `ro_nand2`, left to right in ring
order (`xg, x1, x2, ..., x10`), `ROW_GAP_UM` apart -- computed the same way
`klt gen-compose`'s own `placement.strategy: "row"` would (`ROW_ORDER`,
`row_offsets()`), but done here in plain Python because the *wiring*
geometry below (`klt draw`'s input) has to be computed from the very same
per-block offsets before gen-compose ever runs, and there is no reason to
call the tool twice for numbers this module can derive once.

Why the wiring is hand-routed, not `gen-compose`'s own `connectivity[]`
------------------------------------------------------------------------
`gen-compose`'s router (`route_two_pin` in klayout-tools' own
`gen_compose.py`) rejects a route whose backbone would "plow through" a
block's own interior past a small port-edge margin (`docs/cli/gen-
compose.md`, "Obstacle-overlap check", klayout-tools#199). `ro_stage`'s
own drawn geometry (`layout/cells/ro_stage/build.py`) puts *both* `a`
(input) and `y` (output) on the cell's west side, with `vddr`/`vss` on the
east. Every `y -> a` link in the chain is therefore a *same-facing* port
pair, which is exactly the case that check rejects: both stubs leave
westward, so `manhattan_backbone`'s midpoint jog -- the only backbone
shape the router draws -- lands inside the source cell's own bbox. No
spacing, port ordering, or placement strategy changes that, and the
documented workaround for the case ("wire `connectivity[]` between
*opposite*-facing port pairs only") does not apply to a ring whose
connectivity is fixed by `design/ro_array_core.spice`. `ro_nand2`
compounds this with genuinely dense internal metal1 (five separate
full-width-ish ties: the `py`/`py2` bridge, the `vddr`/`vss` risers) that
leaves no straight vertical column clear from its `a`/`y` pads out past
`Y=3.10` (`ro_nand2`'s own cell top) -- see
`_NAND_A_WAYPOINTS`/`_NAND_Y_WAYPOINTS` below.

The tool has no next move here: `gen-compose` places by translation only
(`gen_compose.py`'s own "Orientation (rotation) is out of scope"), so the
caller cannot re-face a block's ports either, and there is no way to hand
the router a waypoint or a routing channel above the row even when a clear
path is known. That gap is filed generically as klayout-tools#634 (the
routability half klayout-tools#199's detection fix explicitly deferred --
`docs/cli/gen-compose.md`'s own "full obstacle avoidance ... remains its
own follow-up"), rather than worked around silently: it applies to *any*
same-side-I/O cell, an ordinary minimum-width-cell layout choice, not one
specific to this repository. The workaround below (hand-computed wiring,
drawn with `klt draw`, merged in by `gen-compose` placement alone) is the
same technique `layout/cells/_mos_row.py` already established for
`xor2`/`sampler_dff`'s own internal routing -- extended here to
*inter*-cell routing instead of intra-cell.

Two metal layers, so the chain-signal wiring and the two supply rails never
have to cross on the same layer:

- **Metal1** (`(34, 0)`): the ring's own `a`/`y` chain, nine of the ten
  `ro_stage`-to-`ro_stage` links drawn as a straight vertical stub from
  each pin up into a shared horizontal track (their own X intervals are
  pairwise disjoint -- proven once, geometrically, not per-instance: `y`
  sits west of `a` within one cell, so consecutive links' intervals are
  separated by a full cell width), plus the two links touching `ro_nand2`
  (`xg.y -> x1.a`, `x10.y -> xg.a`) drawn as a maze-routed polyline
  (`_NAND_Y_WAYPOINTS`/`_NAND_A_WAYPOINTS`, found once against `ro_nand2`'s
  own committed metal1 geometry -- see "Maze routing" below) that escapes
  clear of `ro_nand2`'s internal ties before joining the same tracks.
- **Metal2** (`(36, 0)`) plus **Via1** (`(35, 0)`): `vddr`/`vss`, one
  continuous strip per rail spanning the whole row, with a `Via1` drop at
  every cell's own `vddr`/`vss` pad. Metal2 is gf180mcu's own second
  routing-metal role (`klayout_tools.gen._PDK_ROLE_LAYERS["gf180mcu"]
  ["metal2"]`/`["via1"]`, added for `gen-compose`'s own via-drop routing,
  issue #454) -- using it here the same way lets the rails cross freely
  over every metal1 chain-track without a same-layer short, which is the
  entire reason two layers were needed at all (an M1-only design was tried
  first and failed DRC exactly this way -- see the module's own git
  history). `klt extract` needs the `Via1` for connectivity
  (`ExtractionDeck.vias[0]`, Metal1<->Metal2), and the curated DRC deck now
  also has an opinion about its geometry: this module used to size it at a
  contact-sized 0.22um on the (then correct) grounds that the deck carried
  "no `via1.*` rule id at all", but klayout-tools#546/#564 transcribed DRM
  7.14 ("Vian") and the `klt` build #142 pins enforces `via1.width.1` at
  0.26um plus `metal2.enclosing.via1.1` at 0.01um (issue #162). `VIA_SZ` is
  therefore the DRM's own fixed 0.26um via, and `M2_PAD` clears it by
  0.02um -- both asserted below.

Maze routing (`ro_nand2`'s `a`/`y` escapes only)
-------------------------------------------------
`_NAND_A_WAYPOINTS`/`_NAND_Y_WAYPOINTS` were found with a small breadth-
first grid search (not committed -- a one-off tool, not part of the build)
against `ro_nand2`'s own fourteen metal1 rectangles
(`layout/cells/ro_nand2/build.py`'s `build_shapes()`), inflated by
`metal1.space.1` (0.23 um) plus half this module's own stub width, over a
0.05 um grid: a Dijkstra/Lee-style maze router, the standard technique for
"route around these obstacles with this clearance" when the obstacle set
is small and fixed. The nine plain `ro_stage`-to-`ro_stage` links need no
such search -- `ro_stage`'s own metal1 is simple enough (four devices, one
gate crossing per row) that a straight vertical stub from each pin already
clears everything else in the cell, checked once by inspection
(`layout/cells/ro_stage/build.py`'s own geometry) rather than by search.
Re-deriving `_NAND_A_WAYPOINTS`/`_NAND_Y_WAYPOINTS` (e.g. after a
`ro_nand2` geometry change) needs the same search re-run by hand; `klt drc`
on this module's own output is what actually proves whatever waypoints are
committed here are still clear.

Standard library only, `klayout.db` never imported directly, same as every
other build script in this repository.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CELL_DIR = Path(__file__).resolve().parent
TOP_CELL = "ro_ring11"

#: Scratch space, git-ignored, shared with the rest of layout/ (see
#: layout/verify.py / layout/floorplan/floorplan.py's own WORK_DIR).
WORK_DIR = REPO_ROOT / "layout" / ".work"

sys.path.insert(0, str(REPO_ROOT))

from layout._klt import klt_version, resolve_pdk  # noqa: E402
from layout.cells._build_cli import make_pdk_check, make_pdk_main  # noqa: E402
from layout.rings import _ring_common  # noqa: E402

# --------------------------------------------------------------------------- #
# Drawn-cell geometry -- bbox_um and every named pin's own (x_um, y_um),
# transcribed from layout/cells/ro_stage/build.py and
# layout/cells/ro_nand2/build.py's own committed geometry (echoed here, not
# re-derived at build time, the same way layout/cells/*/build.py's own
# device-sizing constants echo design/xschem/*.sch rather than parsing it).
# A geometry change in either sibling cell must be mirrored here, the same
# rule those files' own headers state for their schematic sources; klt drc
# on this module's own output is the check that catches a missed mirror.
# --------------------------------------------------------------------------- #
STAGE_BBOX = {"x0": -0.5, "y0": -0.3, "x1": 5.57, "y1": 2.38}
#: `a`/`y` are the switching pair's own drawn metal; `vddr`/`vss` are the
#: starve devices' own rail pads. Y chosen at 1.9/0.2 -- inside both
#: `ro_stage`'s and `ro_nand2`'s own rail-pad footprints, see NAND_LOCAL.
STAGE_LOCAL = {
    "a": (-0.29, 1.15),
    "y": (0.35, 2.07),
    "vddr": (3.73, 1.9),
    "vss": (3.73, 0.2),
}
NAND_BBOX = {"x0": -3.05, "y0": -0.55, "x1": 6.80, "y1": 3.10}
NAND_LOCAL = {
    "a": (0.59, 1.40),
    "y": (1.38, 1.99),
    "en": (2.26, 1.40),  # ring enable -- external pin, no internal wiring
    "vddr": (-2.49, 1.9),
    "vss": (5.21, 0.2),
}

#: See "Maze routing" in the module docstring. Local (cell-frame)
#: coordinates; global position adds the block's own row offset (0.0 for
#: `xg`, the row's first block).
NAND_A_WAYPOINTS = [
    (0.59, 1.25), (-0.6, 1.25), (-0.6, 2.05),
    (-1.95, 2.05), (-1.95, 1.35), (-3.05, 1.35), (-3.05, 4.20),
]
NAND_Y_WAYPOINTS = [(1.38, 1.0), (1.38, 0.3), (4.4, 0.3), (4.4, 3.60)]

#: Ring order, `xg` (`ro_nand2`) first -- also the placement/composition
#: order (`ROW_GAP_UM` apart, left to right).
ROW_ORDER = ["xg"] + [f"x{i}" for i in range(1, 11)]
ROW_GAP_UM = 2.0

#: The two metal1 tracks the chain wiring runs on, and the two metal2 bands
#: the rails run on -- see the module docstring for why the ordering
#: (chain tracks low, rails higher but on a different layer entirely) does
#: not actually matter for DRC, only each band's own internal consistency.
SHORT_TRACK = (3.30, 3.60)
WRAP_TRACK = (3.90, 4.20)
VDDR_M2_BAND = (1.75, 2.05)
VSS_M2_BAND = (0.02, 0.32)

METAL1 = _ring_common.METAL1
STUB_W = 0.30
VIA_SZ = 0.26  # gf180mcu DRM 7.14 "Vn.1": Via1..Via4 are a fixed 0.26um square
M2_PAD = 0.30

# Via sizing/enclosure, against the deck thresholds each exists to satisfy --
# see the module docstring's Metal2/Via1 bullet (issue #162).
assert VIA_SZ >= 0.26, "via1.width.1 floor is 0.26"
assert (M2_PAD - VIA_SZ) / 2 >= 0.01, "metal2.enclosing.via1.1 (0.01)"
assert M2_PAD >= 0.28, "metal2.width.1 (0.28)"

DECK = "gf180mcu"

# --------------------------------------------------------------------------- #
# Shared assembly (layout/rings/_ring_common.py) driven by this ring's own
# constants above. `row_offsets`/`_bboxes_and_locals` keep their signatures:
# layout/pex/build.py calls them on this module.
# --------------------------------------------------------------------------- #

SPEC = _ring_common.RingSpec(
    repo_root=REPO_ROOT,
    top_cell=TOP_CELL,
    stage_cell="ro_stage",
    nand_cell="ro_nand2",
    stage_bbox=STAGE_BBOX,
    stage_local=STAGE_LOCAL,
    nand_bbox=NAND_BBOX,
    nand_local=NAND_LOCAL,
    nand_a_waypoints=NAND_A_WAYPOINTS,
    nand_y_waypoints=NAND_Y_WAYPOINTS,
    row_order=ROW_ORDER,
    row_gap_um=ROW_GAP_UM,
    short_track=SHORT_TRACK,
    wrap_track=WRAP_TRACK,
    vddr_m2_band=VDDR_M2_BAND,
    vss_m2_band=VSS_M2_BAND,
    stub_w=STUB_W,
    via_sz=VIA_SZ,
    m2_pad=M2_PAD,
)


def row_offsets(order: list[str], bboxes: dict[str, dict]) -> dict[str, float]:
    return _ring_common.row_offsets(order, bboxes, ROW_GAP_UM)


def _bboxes_and_locals() -> tuple[dict[str, dict], dict[str, dict]]:
    return _ring_common.bboxes_and_locals(SPEC)


def _wiring_shapes(offsets: dict[str, float], locals_: dict[str, dict]) -> list[dict]:
    return _ring_common.wiring_shapes(SPEC, offsets, locals_)


def gds_path() -> Path:
    return SPEC.gds_path()


def build(pdk_variant: str, path: Path | None = None) -> bytes:
    return _ring_common.build(SPEC, pdk_variant, path)


# The check/CLI tail is the shared one (`layout/cells/_build_cli.py`, #589);
# `layout/verify.py`'s `_STALENESS_CHECKS` calls this module's `check()`
# with no arguments.
check = make_pdk_check(
    gds_path=gds_path,
    build=build,
    resolve_pdk=resolve_pdk,
    work_dir=WORK_DIR,
    top_cell=TOP_CELL,
    script="layout/rings/ro_ring11/build.py",
)
main = make_pdk_main(
    check=check,
    gds_path=gds_path,
    build=build,
    resolve_pdk=resolve_pdk,
    klt_version=klt_version,
    top_cell=TOP_CELL,
    description=__doc__.splitlines()[0],
)


if __name__ == "__main__":
    raise SystemExit(main())
