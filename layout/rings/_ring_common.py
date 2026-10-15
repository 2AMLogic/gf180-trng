#!/usr/bin/env python3
"""Shared assembly code for the two `ro_ring11` generators.

`layout/rings/ro_ring11/build.py` (ring1) and
`layout/rings/ro_ring11_ring2/build.py` (ring2) place the same eleven drawn
cells in a row, hand-wire the a/y chain on Metal1, drop the rails on Metal2
through Via1, and compose the result with `klt gen-compose`. Their code was
identical apart from cell-name strings and work-file names, so the row
placement, the wiring generator and the compose/normalise `build()` live here
once, parameterised by a `RingSpec`.

What stays per ring, in each `build.py`
---------------------------------------
Each ring's driver keeps its own `STAGE_BBOX`/`STAGE_LOCAL`/`NAND_BBOX`/
`NAND_LOCAL`, the maze-route waypoints, the track/band constants, and the
account of why those numbers are what they are. Ring2's are numerically equal
to ring1's today because the two ring2 cells only widen the starve-channel
Comp bands, but they are transcribed from ring2's own committed cells and are
deliberately not shared: a future ring2 cell change must be able to move them
without touching ring1. Sharing the code does not share the geometry; each
ring's committed `.gds` is still produced from its own constants and still
byte-checked by its own `--check`.

Standard library plus `layout/_klt.py` only, like the drivers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from layout._klt import _rect, _run_klt, normalise_gds

# --------------------------------------------------------------------------- #
# Layers -- gf180mcu drawn layers (layout/testcells/build.py's own set, plus
# Metal2/Via1 for the rails).
# --------------------------------------------------------------------------- #
METAL1 = [34, 0]
METAL2 = [36, 0]
VIA1 = [35, 0]


@dataclass(frozen=True)
class RingSpec:
    """Everything that distinguishes one ring's assembly from the other's."""

    repo_root: Path
    top_cell: str  # also the stem of the committed .gds
    stage_cell: str  # drawn stage cell this ring places ten of
    nand_cell: str  # drawn NAND cell this ring places once
    stage_bbox: dict
    stage_local: dict
    nand_bbox: dict
    nand_local: dict
    nand_a_waypoints: list
    nand_y_waypoints: list
    row_order: list
    row_gap_um: float
    short_track: tuple
    wrap_track: tuple
    vddr_m2_band: tuple
    vss_m2_band: tuple
    stub_w: float
    via_sz: float
    m2_pad: float

    @property
    def work_dir(self) -> Path:
        return self.repo_root / "layout" / ".work"

    def gds_path(self) -> Path:
        return self.repo_root / "layout" / "rings" / self.top_cell / f"{self.top_cell}.gds"


# --------------------------------------------------------------------------- #
# Row placement
# --------------------------------------------------------------------------- #


def row_offsets(order: list[str], bboxes: dict[str, dict], row_gap_um: float) -> dict[str, float]:
    """Left-to-right row offsets, `row_gap_um` apart -- the same arithmetic
    `klt gen-compose`'s own `placement.strategy: "row"` uses
    (`compute_row_offsets` in klayout-tools' `gen_compose.py`), computed
    here in plain Python because the wiring geometry needs these same
    numbers before `gen-compose` is ever invoked."""
    offsets: dict[str, float] = {}
    cursor_x1: float | None = None
    for block_id in order:
        bbox = bboxes[block_id]
        offset_x = 0.0 if cursor_x1 is None else (cursor_x1 + row_gap_um) - bbox["x0"]
        offsets[block_id] = offset_x
        cursor_x1 = bbox["x1"] + offset_x
    return offsets


def bboxes_and_locals(spec: RingSpec) -> tuple[dict[str, dict], dict[str, dict]]:
    bboxes = {"xg": spec.nand_bbox}
    locals_ = {"xg": spec.nand_local}
    for i in range(1, 11):
        bboxes[f"x{i}"] = spec.stage_bbox
        locals_[f"x{i}"] = spec.stage_local
    return bboxes, locals_


# --------------------------------------------------------------------------- #
# Wiring geometry (klt draw's own JSON shape list)
# --------------------------------------------------------------------------- #


def wiring_shapes(spec: RingSpec, offsets: dict[str, float], locals_: dict[str, dict]) -> list[dict]:
    shapes: list[dict] = []
    stub_w = spec.stub_w
    via_sz = spec.via_sz
    m2_pad = spec.m2_pad
    nand_bbox = spec.nand_bbox
    stage_bbox = spec.stage_bbox
    row_order = spec.row_order

    def stub_up(x: float, y_bottom: float, y_top: float) -> None:
        shapes.append(_rect(METAL1, x - stub_w / 2, y_bottom, x + stub_w / 2, y_top))

    def hjog(y0: float, y1: float, x_lo: float, x_hi: float) -> None:
        shapes.append(_rect(METAL1, x_lo - stub_w / 2, y0, x_hi + stub_w / 2, y1))

    def polyline(points: list[tuple[float, float]]) -> None:
        """Draw a Manhattan polyline as a sequence of stub_w-wide rects.

        Each segment's own endpoint is extended along the segment's axis by
        stub_w/2 only when that endpoint is an *interior* joint (shared with
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
            ext_lo = stub_w / 2 if i > 0 else 0.0
            ext_hi = stub_w / 2 if i < n - 1 else 0.0
            if horizontal:
                lx0, lx1 = sorted((x0, x1))
                if x0 > x1:
                    ext_lo, ext_hi = ext_hi, ext_lo
                lx0 -= ext_lo
                lx1 += ext_hi
                ly0, ly1 = y0 - stub_w / 2, y0 + stub_w / 2
            else:
                ly0, ly1 = sorted((y0, y1))
                if y0 > y1:
                    ext_lo, ext_hi = ext_hi, ext_lo
                ly0 -= ext_lo
                ly1 += ext_hi
                lx0, lx1 = x0 - stub_w / 2, x0 + stub_w / 2
            shapes.append(_rect(METAL1, lx0, ly0, lx1, ly1))

    # --- the ring's own a/y chain, xg.y -> x1.a -> x1.y -> x2.a -> ... ---
    for k in range(len(row_order)):
        src, dst = row_order[k], row_order[(k + 1) % len(row_order)]
        is_wrap = dst == "xg"  # the one link that closes the loop
        track = spec.wrap_track if is_wrap else spec.short_track

        if src == "xg":
            polyline(spec.nand_y_waypoints)
            src_exit_x = spec.nand_y_waypoints[-1][0]
        else:
            sx = locals_[src]["y"][0] + offsets[src]
            stub_up(sx, locals_[src]["y"][1], track[1])
            src_exit_x = sx

        if dst == "xg":
            polyline(spec.nand_a_waypoints)
            dst_exit_x = spec.nand_a_waypoints[-1][0]
        else:
            dx = locals_[dst]["a"][0] + offsets[dst]
            stub_up(dx, locals_[dst]["a"][1], track[1])
            dst_exit_x = dx

        hjog(track[0], track[1], min(src_exit_x, dst_exit_x), max(src_exit_x, dst_exit_x))

    # --- vddr/vss rails: one Metal2 strip per rail, one Via1 drop per cell ---
    row_x0 = min(stage_bbox["x0"] + offsets[b] if b != "xg" else nand_bbox["x0"] + offsets[b]
                 for b in row_order)
    row_x1 = max(stage_bbox["x1"] + offsets[b] if b != "xg" else nand_bbox["x1"] + offsets[b]
                 for b in row_order)
    shapes.append(_rect(METAL2, row_x0 - 1.0, spec.vddr_m2_band[0], row_x1 + 1.0, spec.vddr_m2_band[1]))
    shapes.append(_rect(METAL2, row_x0 - 1.0, spec.vss_m2_band[0], row_x1 + 1.0, spec.vss_m2_band[1]))
    for b in row_order:
        for net in ("vddr", "vss"):
            lx, ly = locals_[b][net]
            gx = lx + offsets[b]
            shapes.append(_rect(VIA1, gx - via_sz / 2, ly - via_sz / 2, gx + via_sz / 2, ly + via_sz / 2))
            shapes.append(_rect(METAL2, gx - m2_pad / 2, ly - m2_pad / 2, gx + m2_pad / 2, ly + m2_pad / 2))

    return shapes


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #


def build(spec: RingSpec, pdk_variant: str, path: Path | None = None) -> bytes:
    """Draw the wiring, compose the row, and return the normalised GDS bytes.

    Writes scratch artefacts under `layout/.work/`; the composed, normalised
    stream is returned (and, unless `path` overrides it, also written to
    `path` -- the caller decides whether that lands on the committed
    `<top_cell>.gds` or a throwaway compare target, the same convention
    `layout/cells/*/build.py`'s own `build()` follows).
    """
    repo_root = spec.repo_root
    work_dir = spec.work_dir
    top = spec.top_cell
    work_dir.mkdir(parents=True, exist_ok=True)
    bboxes, locals_ = bboxes_and_locals(spec)
    offsets = row_offsets(spec.row_order, bboxes, spec.row_gap_um)

    shapes = wiring_shapes(spec, offsets, locals_)
    draw_params_path = work_dir / f"{top}_wiring_params.json"
    draw_params_path.write_text(json.dumps({"shapes": shapes}, indent=2) + "\n")
    wiring_gds = work_dir / f"{top}_wiring.gds"
    draw_resp = _run_klt([
        "draw", "--params", str(draw_params_path.relative_to(repo_root)),
        "--cell-name", f"{top}_wiring",
        "-o", str(wiring_gds.relative_to(repo_root)),
    ])

    def _report(generator: str, cell_name: str, gds: Path, bbox: dict) -> dict:
        return {
            "generator": generator, "cell_name": cell_name,
            "gds_path": str(gds.relative_to(repo_root) if gds.is_absolute() else gds),
            "bbox_um": bbox, "ports": [],
        }

    stage, nand = spec.stage_cell, spec.nand_cell
    gr_stage = _report(f"layout.cells.{stage}", stage,
                       repo_root / f"layout/cells/{stage}/{stage}.gds", spec.stage_bbox)
    gr_nand = _report(f"layout.cells.{nand}", nand,
                      repo_root / f"layout/cells/{nand}/{nand}.gds", spec.nand_bbox)
    gr_wire = _report(f"layout.rings.{top}.wiring", f"{top}_wiring",
                      wiring_gds, draw_resp["bbox_um"])

    reports = {"stage": work_dir / f"{top}_gr_stage.json",
               "nand": work_dir / f"{top}_gr_nand.json",
               "wire": work_dir / f"{top}_gr_wire.json"}
    reports["stage"].write_text(json.dumps(gr_stage, indent=2) + "\n")
    reports["nand"].write_text(json.dumps(gr_nand, indent=2) + "\n")
    reports["wire"].write_text(json.dumps(gr_wire, indent=2) + "\n")

    blocks = []
    origins = {}
    for b in spec.row_order:
        report_path = reports["nand"] if b == "xg" else reports["stage"]
        # Relative to the request document's own directory (work_dir, same
        # as request_path below), not the repo root -- klayout-tools#328,
        # the same convention layout/floorplan/floorplan.py's own compose()
        # already follows.
        blocks.append({"id": b, "generator_report": report_path.name})
        origins[b] = {"x": offsets[b], "y": 0.0}
    blocks.append({"id": "wire", "generator_report": reports["wire"].name})
    origins["wire"] = {"x": 0.0, "y": 0.0}

    compose_request = {
        "_comment": (
            f"Generated by layout/rings/{top}/build.py. Re-run by hand with: "
            f"klt gen-compose layout/.work/{top}-compose-request.json (from "
            f"the repo root, so options.output lands at "
            f"layout/.work/{top}.gds)"
        ),
        "blocks": blocks,
        "placement": {"strategy": "explicit", "order": spec.row_order + ["wire"], "origins_um": origins},
        "pdk": {"variant": pdk_variant},
        "options": {"cell_name": top, "output": f"layout/.work/{top}.gds"},
    }
    request_path = work_dir / f"{top}-compose-request.json"
    request_path.write_text(json.dumps(compose_request, indent=2) + "\n")
    _run_klt(["gen-compose", str(request_path.relative_to(repo_root))])

    gds_bytes = normalise_gds((work_dir / f"{top}.gds").read_bytes())
    target = path or spec.gds_path()
    target.write_bytes(gds_bytes)
    return gds_bytes
