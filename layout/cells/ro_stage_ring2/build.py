#!/usr/bin/env python3
"""Draw and check `ro_stage` at ring2's sizing (`wstv=0.240u`).

    python3 layout/cells/ro_stage_ring2/build.py            # write ro_stage_ring2.gds
    python3 layout/cells/ro_stage_ring2/build.py --check     # rebuild, compare bytes

Same cell, same topology, as `layout/cells/ro_stage/build.py` (`ro_stage`,
`design/ro_array_core.spice`'s `.subckt ro_stage` -- see that module's own
docstring for the full device-list/why-hand-drawn account, which applies
here unchanged). The only difference is the starve width: ring1's `ro_stage`
(`layout/cells/ro_stage/`) draws `wstv=0.220u`; this cell draws ring2's own
instantiation (`design/ro_array_core.spice`'s `xr2 ... wstv=0.240u`).

That 0.020u difference is not cosmetic. `design/ro_array_core.spice`
deliberately gives the array's two rings different starve widths -- and
therefore different oscillation frequencies -- so that ring1 and ring2 are
not frequency-matched (`layout/floorplan/README.md`, "Mechanism 1": a
non-integer frequency ratio is load-bearing for the two rings' independence
argument the entropy source's isolation floorplan depends on). A layout that
reused ring1's drawn geometry under a new label would silently defeat that
mechanism -- DRC/LVS cannot see it, since both variants are legal, connected,
four-device inverters; only redrawing the starve device at its own width
represents the design ring2 actually specifies. So this file is its own
`build_shapes()`, not an import of `ro_stage`'s with a parameter swapped in
after the fact -- the two `.gds` files this directory and `ro_stage/` produce
are independently drawn and, per `layout/cells/README.md`, independently
DRC'd and LVS'd.

    vddr --[Mph: gate=vss, W=wstv, L=lstv]-- py --[Mp: gate=a, W=0.44, L=0.28]-- y
    y    --[Mn:  gate=a,   W=0.22, L=0.28]-- ny --[Mnt: gate=vddr, W=wstv, L=lstv]-- vss

Design-rule values are the same set `ro_stage/build.py`'s own docstring
transcribes from `klt`'s gf180mcu deck; see that file for the full account.
"""

from __future__ import annotations

import argparse
import os
import sys

_TESTCELL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "testcells"
)
sys.path.insert(0, os.path.abspath(_TESTCELL_DIR))

from gdsii import Label, Rect, write_gds  # noqa: E402

# --------------------------------------------------------------------------- #
# Layers -- gf180mcu drawn layers, matching klt's curated decks (same set
# layout/testcells/build.py and layout/cells/ro_stage/build.py use).
# --------------------------------------------------------------------------- #
NWELL = (21, 0)
COMP = (22, 0)
POLY2 = (30, 0)
CONTACT = (33, 0)
METAL1 = (34, 0)
METAL1_LABEL = (34, 10)

CELL_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_CELL = "ro_stage_ring2"

# --------------------------------------------------------------------------- #
# Device sizing -- design/ro_array_core.spice's ring2 instantiation
# (`xr2 en2 rn2 vddr2 vss ro_ring11 wstv=0.240u lstv=2u cld=0.5f`). Echoed
# into ro_stage_ring2.spice; a change here must be mirrored there.
# --------------------------------------------------------------------------- #
W_STARVE = 0.24  # Mph, Mnt (wstv, ring2) -- ring1's own ro_stage draws 0.22
L_STARVE = 2.00  # Mph, Mnt (lstv)
W_SWITCH_P = 0.44  # Mp
W_SWITCH_N = 0.22  # Mn
L_SWITCH = 0.28  # Mp, Mn

# --------------------------------------------------------------------------- #
# Geometry constants (um) -- identical to layout/cells/ro_stage/build.py's;
# see that module's docstring for why every device is dog-boned and why
# these margins are generous relative to the deck's minimums.
# --------------------------------------------------------------------------- #
PAD_H = 0.44  # comp height at every contacted (source/drain) region
PAD_W = 0.70  # comp x-extent of a contacted region
GATE_GAP = 0.40  # poly2-poly2 gap between adjacent gates on one row (deck min 0.24)
ROW_GAP = 1.20  # comp-comp vertical gap between the NMOS and PMOS rows (deck min 0.28)
NWELL_MARGIN = 0.25  # Nwell enclosure of PMOS comp (deck min 0.12)

assert PAD_H == W_SWITCH_P, "PAD_H sized to need no narrowing for Mp's own W"

# Row 1 (NMOS) centreline and row 2 (PMOS) centreline.
Y_NMOS = PAD_H / 2  # 0.22
Y_PMOS = PAD_H + ROW_GAP + PAD_H / 2  # 0.44 + 1.20 + 0.22 = 1.86


def _pad(y_center: float) -> tuple[float, float]:
    return (y_center - PAD_H / 2, y_center + PAD_H / 2)


def _narrow(y_center: float, w: float) -> tuple[float, float]:
    return (y_center - w / 2, y_center + w / 2)


# --------------------------------------------------------------------------- #
# X layout -- identical shape to ro_stage/build.py's (see that module's own
# comment for the row-by-row account); only W_STARVE differs, which widens
# the two narrow comp bands below but does not move any gate boundary.
# --------------------------------------------------------------------------- #
X0 = 0.0
X_GATE_A0 = X0 + PAD_W
X_GATE_A1 = X_GATE_A0 + L_SWITCH
X_GAP1 = X_GATE_A1 + GATE_GAP
X_GATE_TIE1 = X_GAP1 + L_STARVE
X_PAD2 = X_GATE_TIE1 + PAD_W  # right edge of the cell

assert X_PAD2 == PAD_W + L_SWITCH + GATE_GAP + L_STARVE + PAD_W


def build_shapes() -> tuple[list[Rect], list[Label]]:
    rects: list[Rect] = []
    labels: list[Label] = []

    def rect(layer, x0, y0, x1, y1):
        rects.append(Rect(layer[0], layer[1], x0, y0, x1, y1))

    def label(layer, x, y, text):
        labels.append(Label(layer[0], layer[1], x, y, text))

    # ----------------------------------------------------------------- #
    # NMOS row: pad(y) -- Mn[a] -- (ny) -- Mnt[vddr-tie] -- pad(vss)
    # Mn stays at its own minimum W=0.22; Mnt is ring2's wider W_STARVE
    # (0.24), so unlike ro_stage's own NMOS row the two channels are NOT
    # the same width. Each is narrowed only across its own gate crossing,
    # with (ny) drawn back at full PAD_H between them -- the same
    # full-height-except-at-the-gate technique the PMOS row below already
    # uses for Mph. (An earlier draft narrowed Mn's channel and (ny)
    # together as one uniform 0.22 band butted directly against Mnt's 0.24
    # band with no full-height step between them; `klt extract` measured
    # that abutment as a distorted W/L for Mnt -- W=0.23, L=2.09 instead of
    # 0.24/2.00 -- because the width discontinuity landed exactly on Mnt's
    # gate edge. This shape keeps every gate crossing's comp a uniform
    # width along its own full channel length, which measures correctly.)
    # ----------------------------------------------------------------- #
    ny0, ny1 = _pad(Y_NMOS)
    rect(COMP, X0, ny0, X0 + PAD_W, ny1)  # pad: drain of Mn -> y
    mn0, mn1 = _narrow(Y_NMOS, W_SWITCH_N)
    rect(COMP, X0 + PAD_W, mn0, X_GATE_A1, mn1)  # Mn channel only, narrowed to 0.22
    rect(COMP, X_GATE_A1, ny0, X_GAP1, ny1)  # (ny), full PAD_H, between Mn and Mnt
    nt0, nt1 = _narrow(Y_NMOS, W_STARVE)
    rect(COMP, X_GAP1, nt0, X_GATE_TIE1, nt1)  # Mnt channel, narrowed to W_STARVE
    rect(COMP, X_GATE_TIE1, ny0, X_PAD2, ny1)  # pad: source of Mnt -> vss

    # ----------------------------------------------------------------- #
    # PMOS row: pad(y) -- Mp[a] -- (py) -- Mph[vss-tie] -- pad(vddr)
    # Mp's own W (0.44) already equals PAD_H, so only the Mph crossing
    # needs narrowing (to ring2's W_STARVE=0.24).
    # ----------------------------------------------------------------- #
    py0, py1 = _pad(Y_PMOS)
    rect(COMP, X0, py0, X0 + PAD_W, py1)  # pad: drain of Mp -> y
    rect(COMP, X0 + PAD_W, py0, X_GAP1, py1)  # Mp channel + (py), stays PAD_H
    pn0, pn1 = _narrow(Y_PMOS, W_STARVE)
    rect(COMP, X_GAP1, pn0, X_GATE_TIE1, pn1)  # Mph channel, narrowed to W_STARVE
    rect(COMP, X_GATE_TIE1, py0, X_PAD2, py1)  # pad: source of Mph -> vddr

    # ----------------------------------------------------------------- #
    # Nwell around the PMOS row only.
    # ----------------------------------------------------------------- #
    rect(
        NWELL,
        X0 - NWELL_MARGIN,
        py0 - NWELL_MARGIN,
        X_PAD2 + NWELL_MARGIN,
        py1 + NWELL_MARGIN,
    )

    # ----------------------------------------------------------------- #
    # "a" gate poly -- one rectangle crossing both rows' Mn/Mp channels.
    # ----------------------------------------------------------------- #
    rect(POLY2, X_GATE_A0, ny0 - 0.30, X_GATE_A1, py1 + 0.30)
    # Landing pad, off to the side, safely inside the NMOS/PMOS gap and far
    # (>= poly2.space.1) from every other poly shape in x.
    a_pad_y0, a_pad_y1 = 0.75, 1.25
    rect(POLY2, -0.50, a_pad_y0, X_GATE_A1, a_pad_y1)
    a_contact = (-0.40, 0.89, -0.18, 1.11)
    rect(CONTACT, *a_contact)
    a_metal = (-0.44, 0.85, -0.14, 1.15)
    rect(METAL1, *a_metal)
    label(METAL1_LABEL, -0.29, 1.00, "a")

    # ----------------------------------------------------------------- #
    # Mnt gate poly (tied to vddr) -- NMOS row only. Extended upward for
    # its own contact, kept >= poly2.space.1 (0.24) from the Mph gate
    # poly on the row above (checked below by assertion).
    # ----------------------------------------------------------------- #
    mnt_gate_y0, mnt_gate_y1 = nt0 - 0.30, 1.05
    rect(POLY2, X_GAP1, mnt_gate_y0, X_GATE_TIE1, mnt_gate_y1)
    mnt_contact = (2.20, 0.70, 2.42, 0.92)
    rect(CONTACT, *mnt_contact)

    # ----------------------------------------------------------------- #
    # Mph gate poly (tied to vss) -- PMOS row only, mirrored.
    # ----------------------------------------------------------------- #
    mph_gate_y0, mph_gate_y1 = 1.35, pn1 + 0.30
    rect(POLY2, X_GAP1, mph_gate_y0, X_GATE_TIE1, mph_gate_y1)
    mph_contact = (1.60, 1.48, 1.82, 1.70)
    rect(CONTACT, *mph_contact)

    assert mph_gate_y0 - mnt_gate_y1 >= 0.24, "poly2.space.1 margin"

    # ----------------------------------------------------------------- #
    # pad(y) contacts (NMOS + PMOS), strapped together via metal1 -- the
    # cell's single output.
    # ----------------------------------------------------------------- #
    y_contact_x = (0.24, 0.46)
    rect(CONTACT, y_contact_x[0], mn0, y_contact_x[1], mn1)
    rect(CONTACT, y_contact_x[0], pn0, y_contact_x[1], pn1)
    y_metal_n = (0.14, ny0 + 0.01, 0.56, ny1 - 0.01)
    y_metal_p = (0.14, py0 + 0.01, 0.56, py1 - 0.01)
    rect(METAL1, *y_metal_n)
    rect(METAL1, *y_metal_p)
    rect(METAL1, 0.23, y_metal_n[3] - 0.03, 0.47, y_metal_p[1] + 0.03)  # strap
    label(METAL1_LABEL, 0.35, Y_NMOS, "y")

    # ----------------------------------------------------------------- #
    # pad(vss) (NMOS) and pad(vddr) (PMOS) contacts + metal pads.
    # ----------------------------------------------------------------- #
    rail_contact_x = (X_GATE_TIE1 + 0.24, X_GATE_TIE1 + 0.46)
    rect(CONTACT, rail_contact_x[0], nt0, rail_contact_x[1], nt1)
    rect(CONTACT, rail_contact_x[0], pn0, rail_contact_x[1], pn1)
    vss_metal = (X_GATE_TIE1 + 0.14, ny0 + 0.01, X_GATE_TIE1 + 0.56, ny1 - 0.01)
    vddr_metal = (X_GATE_TIE1 + 0.14, py0 + 0.01, X_GATE_TIE1 + 0.56, py1 - 0.01)
    rect(METAL1, *vss_metal)
    rect(METAL1, *vddr_metal)
    label(METAL1_LABEL, X_GATE_TIE1 + 0.25, Y_NMOS, "vss")
    label(METAL1_LABEL, X_GATE_TIE1 + 0.25, Y_PMOS, "vddr")

    # ----------------------------------------------------------------- #
    # Mnt-tie riser: contact -> vertical run -> horizontal jog into the
    # vddr rail (PMOS pad_vddr metal).
    # ----------------------------------------------------------------- #
    rect(METAL1, 2.16, 0.65, 2.46, 1.85)  # vertical, covers mnt_contact
    rect(  # horizontal jog into vddr rail, 0.30 tall (>= metal1.width.1)
        METAL1, 2.16, Y_PMOS - 0.15, X_GATE_TIE1 + 0.52, Y_PMOS + 0.15
    )

    # ----------------------------------------------------------------- #
    # Mph-tie riser: contact -> vertical run -> horizontal jog into the
    # vss rail (NMOS pad_vss metal).
    # ----------------------------------------------------------------- #
    rect(METAL1, 1.54, 0.20, 1.88, 1.82)  # vertical, covers mph_contact
    rect(  # horizontal jog into vss rail, 0.30 tall (>= metal1.width.1)
        METAL1, 1.54, Y_NMOS - 0.15, X_GATE_TIE1 + 0.52, Y_NMOS + 0.15
    )

    return rects, labels


def gds_path() -> str:
    return os.path.join(CELL_DIR, f"{TOP_CELL}.gds")


def build(path: str | None = None) -> bytes:
    rects, labels = build_shapes()
    return write_gds(
        path or gds_path(),
        library_name=TOP_CELL,
        structures=[(TOP_CELL, rects, labels)],
    )


def check() -> int:
    path = gds_path()
    shown = os.path.relpath(path, os.getcwd())
    if not os.path.exists(path):
        print(f"MISSING: {shown} -- run `python3 layout/cells/ro_stage_ring2/build.py`")
        return 1
    scratch = path + ".check"
    try:
        rebuilt = build(scratch)
    finally:
        if os.path.exists(scratch):
            os.remove(scratch)
    with open(path, "rb") as handle:
        committed = handle.read()
    if rebuilt != committed:
        print(
            f"STALE: {shown} does not match build.py "
            f"({len(committed)} bytes committed, {len(rebuilt)} rebuilt) -- "
            f"run `python3 layout/cells/ro_stage_ring2/build.py`"
        )
        return 1
    print(f"ok: {shown}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed .gds matches this script, and exit",
    )
    args = parser.parse_args(argv)
    if args.check:
        return check()
    build()
    print(f"wrote {gds_path()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
