#!/usr/bin/env python3
"""Assemble `ro_ring11` (ring2 sizing) from the drawn `ro_stage_ring2`/
`ro_nand2_ring2` cells, and check it.

    python3 layout/rings/ro_ring11_ring2/build.py            # write ro_ring11_ring2.gds
    python3 layout/rings/ro_ring11_ring2/build.py --check    # rebuild, compare bytes
    python3 layout/rings/ro_ring11_ring2/build.py --require-tools  # fail, don't skip

Same block, same technique, as `layout/rings/ro_ring11/build.py`
(`ro_ring11` at ring1's sizing, `wstv=0.220u` -- see that module's own
docstring for the full row-placement/hand-routed-wiring/two-metal-layer
account, which applies here unchanged). The only difference is which pair
of already-drawn, individually DRC-clean/LVS-matching cells this module
places: ring1's assembly uses `layout/cells/ro_stage/` and
`layout/cells/ro_nand2/` (both `wstv=0.220u`); this module uses
`layout/cells/ro_stage_ring2/` and `layout/cells/ro_nand2_ring2/` (both
`wstv=0.240u`, ring2's own instantiation --
`design/ro_array_core.spice`'s `xr2 ... ro_ring11 wstv=0.240u ...`), the
gap `layout/rings/README.md` recorded and issue #118 closes.

The row-placement math (`row_offsets()`), the wiring generator, and the
`gen-compose` request shape are the same code as `ro_ring11/build.py`'s and
live once in `layout/rings/_ring_common.py`; this file supplies ring2's own
constants (below) and owns the committed `ro_ring11_ring2.gds`, which its
`--check` still byte-compares on its own.

Why the per-cell geometry constants below (`STAGE_BBOX`/`STAGE_LOCAL`/
`NAND_BBOX`/`NAND_LOCAL`/`NAND_A_WAYPOINTS`/`NAND_Y_WAYPOINTS`) are
numerically identical to `ro_ring11/build.py`'s own
--------------------------------------------------------------------------
This is not a copy-paste that forgot to update -- it is a checked fact
about the two sibling cells' own drawn geometry. `ro_stage_ring2/build.py`
and `ro_nand2_ring2/build.py`'s only difference from their ring1
counterparts is `W_STARVE` (`0.220u -> 0.240u`), which only widens the
`Mnt`/`Mph` (`XMnt`/`XMph`) starve-channel Comp bands -- every pin's own
Metal1 pad (`a`, `y`, `en`, `vddr`, `vss`) and every cell's own overall
bounding box are drawn from constants that do not depend on `W_STARVE` (see
each cell's own `build.py` for exactly which rects), so they land at the
same coordinates in both variants. This was verified, not assumed, by
diffing `build_shapes()`'s own Metal1 output between each ring1/ring2 cell
pair before this module was written: all fourteen of `ro_nand2`'s Metal1
rectangles are byte-identical to `ro_nand2_ring2`'s (only the two narrowed
Comp bands differ), and the same holds for `ro_stage`/`ro_stage_ring2`'s
Metal1. That is exactly why `NAND_A_WAYPOINTS`/`NAND_Y_WAYPOINTS` -- a maze
route around `ro_nand2`'s own Metal1 obstacles (see
`ro_ring11/build.py`'s "Maze routing" section) -- can be reused unchanged
against `ro_nand2_ring2` rather than re-derived: the obstacle set the
search ran against did not move. A future geometry change to either ring2
cell's own Metal1 would need these re-checked the same way (and `klt drc`
on this module's own output is what actually proves whatever is committed
here is still clear, the same backstop `ro_ring11/build.py`'s own docstring
notes).

Standard library only, `klayout.db` never imported directly, same as every
other build script in this repository.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CELL_DIR = Path(__file__).resolve().parent
TOP_CELL = "ro_ring11_ring2"

#: Scratch space, git-ignored, shared with the rest of layout/ (see
#: layout/verify.py / layout/floorplan/floorplan.py's own WORK_DIR).
WORK_DIR = REPO_ROOT / "layout" / ".work"

sys.path.insert(0, str(REPO_ROOT))

from layout._klt import klt_version, resolve_pdk  # noqa: E402
from layout.cells._build_cli import make_pdk_check, make_pdk_main  # noqa: E402
from layout.rings import _ring_common  # noqa: E402

# --------------------------------------------------------------------------- #
# Drawn-cell geometry -- bbox_um and every named pin's own (x_um, y_um),
# transcribed from layout/cells/ro_stage_ring2/build.py and
# layout/cells/ro_nand2_ring2/build.py's own committed geometry (echoed
# here, not re-derived at build time, the same way layout/cells/*/build.py's
# own device-sizing constants echo design/xschem/*.sch rather than parsing
# it). Numerically identical to layout/rings/ro_ring11/build.py's own
# STAGE_BBOX/STAGE_LOCAL/NAND_BBOX/NAND_LOCAL -- see the module docstring
# for why that is a checked fact about the two ring2 cells' own geometry,
# not an unedited copy. A geometry change in either sibling cell must be
# mirrored here, the same rule those files' own headers state for their
# schematic sources; klt drc on this module's own output is the check that
# catches a missed mirror.
# --------------------------------------------------------------------------- #
STAGE_BBOX = {"x0": -0.5, "y0": -0.3, "x1": 4.33, "y1": 2.38}
#: `a`/`y` are the switching pair's own drawn metal; `vddr`/`vss` are the
#: starve devices' own rail pads. Y chosen at 1.9/0.2 -- inside both
#: `ro_stage_ring2`'s and `ro_nand2_ring2`'s own rail-pad footprints, see
#: NAND_LOCAL.
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

#: See "Maze routing" in layout/rings/ro_ring11/build.py's own docstring,
#: and this module's own docstring for why these are reused unchanged
#: against ro_nand2_ring2 rather than re-derived. Local (cell-frame)
#: coordinates; global position adds the block's own row offset (0.0 for
#: `xg`, the row's first block).
NAND_A_WAYPOINTS = [
    (0.59, 1.25), (-0.6, 1.25), (-0.6, 2.05),
    (-1.95, 2.05), (-1.95, 1.35), (-3.05, 1.35), (-3.05, 4.20),
]
NAND_Y_WAYPOINTS = [(1.38, 1.0), (1.38, 0.3), (4.4, 0.3), (4.4, 3.60)]

#: Ring order, `xg` (`ro_nand2_ring2`) first -- also the placement/
#: composition order (`ROW_GAP_UM` apart, left to right).
ROW_ORDER = ["xg"] + [f"x{i}" for i in range(1, 11)]
ROW_GAP_UM = 2.0

#: The two metal1 tracks the chain wiring runs on, and the two metal2 bands
#: the rails run on -- see ro_ring11/build.py's module docstring for why the
#: ordering (chain tracks low, rails higher but on a different layer
#: entirely) does not actually matter for DRC, only each band's own
#: internal consistency.
SHORT_TRACK = (3.30, 3.60)
WRAP_TRACK = (3.90, 4.20)
VDDR_M2_BAND = (1.75, 2.05)
VSS_M2_BAND = (0.02, 0.32)

STUB_W = 0.30
VIA_SZ = 0.26  # gf180mcu DRM 7.14 "Vn.1": Via1..Via4 are a fixed 0.26um square
M2_PAD = 0.30

# Via sizing/enclosure, against the deck thresholds each exists to satisfy --
# the same `via1.width.1` (0.26) / `metal2.enclosing.via1.1` (0.01) pair
# `layout/rings/ro_ring11/build.py` documents at its own copy of these
# constants (issue #162).
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
    stage_cell="ro_stage_ring2",
    nand_cell="ro_nand2_ring2",
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
    script="layout/rings/ro_ring11_ring2/build.py",
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
