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

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CELL_DIR = Path(__file__).resolve().parent
TOP_CELL = "ro_ring11"

#: Scratch space, git-ignored, shared with the rest of layout/ (see
#: layout/verify.py / layout/floorplan/floorplan.py's own WORK_DIR).
WORK_DIR = REPO_ROOT / "layout" / ".work"

sys.path.insert(0, str(REPO_ROOT))

from layout._klt import _run_klt, klt_version, normalise_gds, resolve_pdk  # noqa: E402

# --------------------------------------------------------------------------- #
# Layers -- gf180mcu drawn layers (layout/testcells/build.py's own set, plus
# Metal2/Via1 for the rails -- see the module docstring).
# --------------------------------------------------------------------------- #
METAL1 = [34, 0]
METAL2 = [36, 0]
VIA1 = [35, 0]

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
STAGE_BBOX = {"x0": -0.5, "y0": -0.3, "x1": 4.33, "y1": 2.38}
#: `a`/`y` are the switching pair's own drawn metal; `vddr`/`vss` are the
#: starve devices' own rail pads. Y chosen at 1.9/0.2 -- inside both
#: `ro_stage`'s and `ro_nand2`'s own rail-pad footprints, see NAND_LOCAL.
STAGE_LOCAL = {
    "a": (-0.29, 1.15),
    "y": (0.35, 2.07),
    "vddr": (3.73, 1.9),
    "vss": (3.73, 0.2),
}
NAND_BBOX = {"x0": -3.05, "y0": -0.55, "x1": 5.56, "y1": 3.10}
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

STUB_W = 0.30
VIA_SZ = 0.26  # gf180mcu DRM 7.14 "Vn.1": Via1..Via4 are a fixed 0.26um square
M2_PAD = 0.30

# Via sizing/enclosure, against the deck thresholds each exists to satisfy --
# see the module docstring's Metal2/Via1 bullet (issue #162).
assert VIA_SZ >= 0.26, "via1.width.1 floor is 0.26"
assert (M2_PAD - VIA_SZ) / 2 >= 0.01, "metal2.enclosing.via1.1 (0.01)"
assert M2_PAD >= 0.28, "metal2.width.1 (0.28)"

DECK = "gf180mcu"
EXIT_OK = 0
EXIT_FAIL = 1


# --------------------------------------------------------------------------- #
# Row placement
# --------------------------------------------------------------------------- #


def row_offsets(order: list[str], bboxes: dict[str, dict]) -> dict[str, float]:
    """Left-to-right row offsets, `ROW_GAP_UM` apart -- the same arithmetic
    `klt gen-compose`'s own `placement.strategy: "row"` uses
    (`compute_row_offsets` in klayout-tools' `gen_compose.py`), computed
    here in plain Python because the wiring geometry needs these same
    numbers before `gen-compose` is ever invoked (see module docstring)."""
    offsets: dict[str, float] = {}
    cursor_x1: float | None = None
    for block_id in order:
        bbox = bboxes[block_id]
        offset_x = 0.0 if cursor_x1 is None else (cursor_x1 + ROW_GAP_UM) - bbox["x0"]
        offsets[block_id] = offset_x
        cursor_x1 = bbox["x1"] + offset_x
    return offsets


def _bboxes_and_locals() -> tuple[dict[str, dict], dict[str, dict]]:
    bboxes = {"xg": NAND_BBOX}
    locals_ = {"xg": NAND_LOCAL}
    for i in range(1, 11):
        bboxes[f"x{i}"] = STAGE_BBOX
        locals_[f"x{i}"] = STAGE_LOCAL
    return bboxes, locals_


# --------------------------------------------------------------------------- #
# Wiring geometry (klt draw's own JSON shape list)
# --------------------------------------------------------------------------- #


def _rect(layer: list[int], x0: float, y0: float, x1: float, y1: float) -> dict:
    return {"layer": layer, "rect_um": [x0, y0, x1, y1]}


def _wiring_shapes(offsets: dict[str, float], locals_: dict[str, dict]) -> list[dict]:
    shapes: list[dict] = []

    def stub_up(x: float, y_bottom: float, y_top: float) -> None:
        shapes.append(_rect(METAL1, x - STUB_W / 2, y_bottom, x + STUB_W / 2, y_top))

    def hjog(y0: float, y1: float, x_lo: float, x_hi: float) -> None:
        shapes.append(_rect(METAL1, x_lo - STUB_W / 2, y0, x_hi + STUB_W / 2, y1))

    def polyline(points: list[tuple[float, float]]) -> None:
        """Draw a Manhattan polyline as a sequence of STUB_W-wide rects.

        Each segment's own endpoint is extended along the segment's axis by
        STUB_W/2 only when that endpoint is an *interior* joint (shared with
        the previous/next segment), squaring off the corner so consecutive
        segments overlap cleanly. The polyline's true first and last
        endpoints (a pin pad, or a track's own edge) are left exact --
        over-extending those risks landing too close to unrelated geometry
        just past them (this shipped once, as a real metal1.space.1
        failure against the wrap track, before this docstring existed).
        """
        n = len(points) - 1
        for i, ((x0, y0), (x1, y1)) in enumerate(zip(points, points[1:])):
            horizontal = y0 == y1
            ext_lo = STUB_W / 2 if i > 0 else 0.0
            ext_hi = STUB_W / 2 if i < n - 1 else 0.0
            if horizontal:
                lx0, lx1 = sorted((x0, x1))
                if x0 > x1:
                    ext_lo, ext_hi = ext_hi, ext_lo
                lx0 -= ext_lo
                lx1 += ext_hi
                ly0, ly1 = y0 - STUB_W / 2, y0 + STUB_W / 2
            else:
                ly0, ly1 = sorted((y0, y1))
                if y0 > y1:
                    ext_lo, ext_hi = ext_hi, ext_lo
                ly0 -= ext_lo
                ly1 += ext_hi
                lx0, lx1 = x0 - STUB_W / 2, x0 + STUB_W / 2
            shapes.append(_rect(METAL1, lx0, ly0, lx1, ly1))

    # --- the ring's own a/y chain, xg.y -> x1.a -> x1.y -> x2.a -> ... ---
    for k in range(len(ROW_ORDER)):
        src, dst = ROW_ORDER[k], ROW_ORDER[(k + 1) % len(ROW_ORDER)]
        is_wrap = dst == "xg"  # the one link that closes the loop
        track = WRAP_TRACK if is_wrap else SHORT_TRACK

        if src == "xg":
            polyline(NAND_Y_WAYPOINTS)
            src_exit_x = NAND_Y_WAYPOINTS[-1][0]
        else:
            sx = locals_[src]["y"][0] + offsets[src]
            stub_up(sx, locals_[src]["y"][1], track[1])
            src_exit_x = sx

        if dst == "xg":
            polyline(NAND_A_WAYPOINTS)
            dst_exit_x = NAND_A_WAYPOINTS[-1][0]
        else:
            dx = locals_[dst]["a"][0] + offsets[dst]
            stub_up(dx, locals_[dst]["a"][1], track[1])
            dst_exit_x = dx

        hjog(track[0], track[1], min(src_exit_x, dst_exit_x), max(src_exit_x, dst_exit_x))

    # --- vddr/vss rails: one Metal2 strip per rail, one Via1 drop per cell ---
    row_x0 = min(STAGE_BBOX["x0"] + offsets[b] if b != "xg" else NAND_BBOX["x0"] + offsets[b]
                 for b in ROW_ORDER)
    row_x1 = max(STAGE_BBOX["x1"] + offsets[b] if b != "xg" else NAND_BBOX["x1"] + offsets[b]
                 for b in ROW_ORDER)
    shapes.append(_rect(METAL2, row_x0 - 1.0, VDDR_M2_BAND[0], row_x1 + 1.0, VDDR_M2_BAND[1]))
    shapes.append(_rect(METAL2, row_x0 - 1.0, VSS_M2_BAND[0], row_x1 + 1.0, VSS_M2_BAND[1]))
    for b in ROW_ORDER:
        for net, band in (("vddr", VDDR_M2_BAND), ("vss", VSS_M2_BAND)):
            lx, ly = locals_[b][net]
            gx = lx + offsets[b]
            shapes.append(_rect(VIA1, gx - VIA_SZ / 2, ly - VIA_SZ / 2, gx + VIA_SZ / 2, ly + VIA_SZ / 2))
            shapes.append(_rect(METAL2, gx - M2_PAD / 2, ly - M2_PAD / 2, gx + M2_PAD / 2, ly + M2_PAD / 2))

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
    `path` -- the caller decides whether that lands on the committed
    `ro_ring11.gds` or a throwaway compare target, the same convention
    `layout/cells/*/build.py`'s own `build()` follows).
    """
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    bboxes, locals_ = _bboxes_and_locals()
    offsets = row_offsets(ROW_ORDER, bboxes)

    shapes = _wiring_shapes(offsets, locals_)
    draw_params_path = WORK_DIR / "ro_ring11_wiring_params.json"
    draw_params_path.write_text(json.dumps({"shapes": shapes}, indent=2) + "\n")
    wiring_gds = WORK_DIR / "ro_ring11_wiring.gds"
    draw_resp = _run_klt([
        "draw", "--params", str(draw_params_path.relative_to(REPO_ROOT)),
        "--cell-name", "ro_ring11_wiring",
        "-o", str(wiring_gds.relative_to(REPO_ROOT)),
    ])

    def _report(generator: str, cell_name: str, gds: Path, bbox: dict) -> dict:
        return {
            "generator": generator, "cell_name": cell_name,
            "gds_path": str(gds.relative_to(REPO_ROOT) if gds.is_absolute() else gds),
            "bbox_um": bbox, "ports": [],
        }

    gr_stage = _report("layout.cells.ro_stage", "ro_stage",
                        REPO_ROOT / "layout/cells/ro_stage/ro_stage.gds", STAGE_BBOX)
    gr_nand = _report("layout.cells.ro_nand2", "ro_nand2",
                       REPO_ROOT / "layout/cells/ro_nand2/ro_nand2.gds", NAND_BBOX)
    gr_wire = _report("layout.rings.ro_ring11.wiring", "ro_ring11_wiring",
                       wiring_gds, draw_resp["bbox_um"])

    reports = {"stage": WORK_DIR / "ro_ring11_gr_stage.json",
               "nand": WORK_DIR / "ro_ring11_gr_nand.json",
               "wire": WORK_DIR / "ro_ring11_gr_wire.json"}
    reports["stage"].write_text(json.dumps(gr_stage, indent=2) + "\n")
    reports["nand"].write_text(json.dumps(gr_nand, indent=2) + "\n")
    reports["wire"].write_text(json.dumps(gr_wire, indent=2) + "\n")

    blocks = []
    origins = {}
    for b in ROW_ORDER:
        report_path = reports["nand"] if b == "xg" else reports["stage"]
        # Relative to the request document's own directory (WORK_DIR, same
        # as request_path below), not the repo root -- klayout-tools#328,
        # the same convention layout/floorplan/floorplan.py's own compose()
        # already follows.
        blocks.append({"id": b, "generator_report": report_path.name})
        origins[b] = {"x": offsets[b], "y": 0.0}
    blocks.append({"id": "wire", "generator_report": reports["wire"].name})
    origins["wire"] = {"x": 0.0, "y": 0.0}

    compose_request = {
        "_comment": (
            "Generated by layout/rings/ro_ring11/build.py. Re-run by hand with: "
            "klt gen-compose layout/.work/ro_ring11-compose-request.json (from "
            "the repo root, so options.output lands at "
            "layout/.work/ro_ring11.gds)"
        ),
        "blocks": blocks,
        "placement": {"strategy": "explicit", "order": ROW_ORDER + ["wire"], "origins_um": origins},
        "pdk": {"variant": pdk_variant},
        "options": {"cell_name": TOP_CELL, "output": "layout/.work/ro_ring11.gds"},
    }
    request_path = WORK_DIR / "ro_ring11-compose-request.json"
    request_path.write_text(json.dumps(compose_request, indent=2) + "\n")
    _run_klt(["gen-compose", str(request_path.relative_to(REPO_ROOT))])

    gds_bytes = normalise_gds((WORK_DIR / "ro_ring11.gds").read_bytes())
    target = path or gds_path()
    target.write_bytes(gds_bytes)
    return gds_bytes


def check() -> int:
    """Rebuild into scratch and byte-compare against the committed .gds.

    Matches `layout/cells/*/build.py`'s own `check()` contract
    (`layout/verify.py`'s `_STALENESS_CHECKS` calls it with no arguments and
    treats a nonzero return as a hard failure) -- `klt`/the PDK are already
    confirmed present by the time `layout/verify.py` reaches this call, so
    resolving the PDK variant here does not need its own skip path.
    """
    path = gds_path()
    shown = os.path.relpath(path, os.getcwd())
    if not path.exists():
        print(f"MISSING: {shown} -- run `python3 layout/rings/ro_ring11/build.py`")
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
            f"run `python3 layout/rings/ro_ring11/build.py`"
        )
        return 1
    print(f"ok: {shown}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                         help="verify the committed .gds matches this script, and exit")
    parser.add_argument("--require-tools", action="store_true",
                         help="fail instead of skipping when klt or the PDK is absent")
    args = parser.parse_args(argv)

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
        print("SKIP: ro_ring11 build -- the tools above are not available.")
        return EXIT_OK

    if args.check:
        return check()
    build(pdk.variant)
    print(f"wrote {gds_path()}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
