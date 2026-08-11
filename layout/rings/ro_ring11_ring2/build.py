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

The row-placement math (`row_offsets()`), the wiring generator
(`_wiring_shapes()`), and the `gen-compose` request shape are byte-for-byte
the same code as `ro_ring11/build.py`'s -- copied here (not imported and
parameterised) the same way `ro_stage_ring2/build.py` is its own
`build_shapes()` rather than a parameter swap on `ro_stage/build.py`'s, so
that each ring's own assembly is independently reviewable end to end.

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

import argparse
import json
import os
import struct
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CELL_DIR = Path(__file__).resolve().parent
TOP_CELL = "ro_ring11_ring2"

#: Scratch space, git-ignored, shared with the rest of layout/ (see
#: layout/verify.py / layout/floorplan/floorplan.py's own WORK_DIR).
WORK_DIR = REPO_ROOT / "layout" / ".work"

sys.path.insert(0, str(REPO_ROOT))

from layout._klt import _run_klt, resolve_pdk  # noqa: E402

# --------------------------------------------------------------------------- #
# Layers -- gf180mcu drawn layers (layout/testcells/build.py's own set, plus
# Metal2/Via1 for the rails -- see the module docstring).
# --------------------------------------------------------------------------- #
METAL1 = [34, 0]
METAL2 = [36, 0]
VIA1 = [35, 0]

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
VIA_SZ = 0.22
M2_PAD = 0.30

DECK = "gf180mcu"
EXIT_OK = 0
EXIT_FAIL = 1


def klt_version() -> str | None:
    import shutil

    if shutil.which("klt") is None:
        return None
    try:
        done = subprocess.run(["klt", "--version"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return (done.stdout or done.stderr).strip() or None


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
        just past them (see ro_ring11/build.py's own docstring for the
        real metal1.space.1 failure that shipped once before this
        docstring existed).
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
# GDSII timestamp normalisation -- same reason and same technique
# layout/floorplan/floorplan.py's own normalise_gds documents
# (klayout-tools#320): `klt gen-compose`/`klt draw` stamp wall-clock time
# into BGNLIB/BGNSTR, so a byte-comparable committed artefact needs it
# zeroed on the way in.
# --------------------------------------------------------------------------- #
_BGNLIB = 0x0102
_BGNSTR = 0x0502


def normalise_gds(raw: bytes) -> bytes:
    out = bytearray(raw)
    offset = 0
    while offset + 4 <= len(out):
        length, record = struct.unpack_from(">HH", out, offset)
        if length < 4:
            break
        if record in (_BGNLIB, _BGNSTR):
            for index in range(offset + 4, offset + length):
                out[index] = 0
        offset += length
    return bytes(out)


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
    `ro_ring11_ring2.gds` or a throwaway compare target, the same
    convention `layout/cells/*/build.py`'s own `build()` follows).
    """
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    bboxes, locals_ = _bboxes_and_locals()
    offsets = row_offsets(ROW_ORDER, bboxes)

    shapes = _wiring_shapes(offsets, locals_)
    draw_params_path = WORK_DIR / "ro_ring11_ring2_wiring_params.json"
    draw_params_path.write_text(json.dumps({"shapes": shapes}, indent=2) + "\n")
    wiring_gds = WORK_DIR / "ro_ring11_ring2_wiring.gds"
    draw_resp = _run_klt([
        "draw", "--params", str(draw_params_path.relative_to(REPO_ROOT)),
        "--cell-name", "ro_ring11_ring2_wiring",
        "-o", str(wiring_gds.relative_to(REPO_ROOT)),
    ])

    def _report(generator: str, cell_name: str, gds: Path, bbox: dict) -> dict:
        return {
            "generator": generator, "cell_name": cell_name,
            "gds_path": str(gds.relative_to(REPO_ROOT) if gds.is_absolute() else gds),
            "bbox_um": bbox, "ports": [],
        }

    gr_stage = _report("layout.cells.ro_stage_ring2", "ro_stage_ring2",
                        REPO_ROOT / "layout/cells/ro_stage_ring2/ro_stage_ring2.gds", STAGE_BBOX)
    gr_nand = _report("layout.cells.ro_nand2_ring2", "ro_nand2_ring2",
                       REPO_ROOT / "layout/cells/ro_nand2_ring2/ro_nand2_ring2.gds", NAND_BBOX)
    gr_wire = _report("layout.rings.ro_ring11_ring2.wiring", "ro_ring11_ring2_wiring",
                       wiring_gds, draw_resp["bbox_um"])

    reports = {"stage": WORK_DIR / "ro_ring11_ring2_gr_stage.json",
               "nand": WORK_DIR / "ro_ring11_ring2_gr_nand.json",
               "wire": WORK_DIR / "ro_ring11_ring2_gr_wire.json"}
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
            "Generated by layout/rings/ro_ring11_ring2/build.py. Re-run by "
            "hand with: klt gen-compose "
            "layout/.work/ro_ring11_ring2-compose-request.json (from "
            "the repo root, so options.output lands at "
            "layout/.work/ro_ring11_ring2.gds)"
        ),
        "blocks": blocks,
        "placement": {"strategy": "explicit", "order": ROW_ORDER + ["wire"], "origins_um": origins},
        "pdk": {"variant": pdk_variant},
        "options": {"cell_name": TOP_CELL, "output": "layout/.work/ro_ring11_ring2.gds"},
    }
    request_path = WORK_DIR / "ro_ring11_ring2-compose-request.json"
    request_path.write_text(json.dumps(compose_request, indent=2) + "\n")
    _run_klt(["gen-compose", str(request_path.relative_to(REPO_ROOT))])

    gds_bytes = normalise_gds((WORK_DIR / "ro_ring11_ring2.gds").read_bytes())
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
        print(f"MISSING: {shown} -- run `python3 layout/rings/ro_ring11_ring2/build.py`")
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
            f"run `python3 layout/rings/ro_ring11_ring2/build.py`"
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
        print("SKIP: ro_ring11_ring2 build -- the tools above are not available.")
        return EXIT_OK

    if args.check:
        return check()
    build(pdk.variant)
    print(f"wrote {gds_path()}")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
