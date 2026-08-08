#!/usr/bin/env python3
"""Draw and check `ro_stage`, the entropy source's repeated ring-stage cell.

    python3 layout/cells/ro_stage/build.py            # write ro_stage.gds
    python3 layout/cells/ro_stage/build.py --check     # rebuild, compare bytes

`ro_stage` is `design/ro_array_core.spice`'s `.subckt ro_stage` (from
`design/xschem/ro_stage.sch`): the series-starved minimum-width inverter that
is the ring's repeated delay element -- ten instances plus one `ro_nand2`
make one `ro_ring11`, and the array's isolation floorplan (#16,
`layout/floorplan/`) reserves the `ring1`/`ring2` guarded regions this cell
is meant to populate.

Four devices, two series-stacked pairs, at the schematic's own default sizing
(`wstv=0.22u lstv=2u`, `ro_stage.sch`'s `G {...}` line -- ring1's own value;
ring2 overrides `wstv` to 0.240u and is not drawn here, see
`layout/cells/README.md`):

    vddr --[Mph: gate=vss, W=wstv, L=lstv]-- py --[Mp: gate=a, W=0.44, L=0.28]-- y
    y    --[Mn:  gate=a,   W=0.22, L=0.28]-- ny --[Mnt: gate=vddr, W=wstv, L=lstv]-- vss

`Mph`/`Mnt` are the "starve" devices: always-on (gate tied to the *opposite*
rail) series pass transistors whose long channel (`L=lstv=2um`) sets the
stage's charge/discharge current -- and therefore the ring frequency --
without adding switched capacitance at `y`. `Mp`/`Mn` are the minimum-size
switching pair. `py`/`ny` are internal nodes with no external pin and no
contact: they are carried by diffusion continuity within each device's own
active (Comp) region, the same way a stdcell's internal stack nodes are.

`design/xschem/ro_stage.sch` also carries `Cld`, a behavioural load
capacitor -- but its own schematic text is explicit that this is "an
estimate, not an extracted parasitic: layout ... owes either an extraction
that lands at or below cld, or a superseding sizing pass," i.e. it is not a
device to draw. `ro_stage.spice` (the LVS reference next to this file)
omits it for that reason, and so does this layout.

Why hand-drawn, not `klt gen mos_array`
----------------------------------------
Three of this cell's four devices (`Mph`, `Mn`, `Mnt`) are drawn at
`W=0.22um` -- the gf180mcu 3.3V core devices' own minimum, and the width the
schematic's own comment calls "the smallest inverter the gf180mcu 3.3V core
devices allow." `klt gen mos_array` refuses `w_um` below 0.42um
([klayout-tools#322][kt322], filed by `layout/floorplan/`; closed as a
message-only fix -- the 0.42um floor itself is unchanged, only the error text
now correctly describes it as a generator-side contact-fit constraint rather
than implying it is a PDK DRC minimum) -- so it cannot generate a single
device at this cell's actual design width, and
generating instead at the 0.42um floor would draw a device roughly double
the intended width, silently misrepresenting the delay/current the starve
devices are sized to produce. That is exactly the class of "passes DRC/LVS
but is not what the schematic specifies" mistake issue #106 itself warns
about, so this cell is hand-drawn from primitive geometry instead, the same
approach (and the same `layout/testcells/gdsii.py` writer) `layout/testcells/`
already established for the flow-bringup fixtures.

Minimum-width devices need contacts, and a contact needs comp enclosure
margin a minimum-width (0.22um) active region cannot provide on its own
(0.22 == the fixed 0.22 x 0.22um contact size, leaving zero room for the
0.07um `comp.enclosing.contact.1` margin either side). So every device here
is drawn "dog-boned": full W only under the gate it actually needs to be W
at, widened to `PAD_H` (0.44um, itself >= every W this cell uses) wherever a
contact lands. `klt`'s extractor (KLayout's native
`DeviceExtractorMOS4Transistor`) measures W at the gate crossing, not at the
widest point of the diffusion, so this is the standard technique for a
contacted minimum-width device -- not a DRC workaround.

Design-rule values (`comp.width.1` 0.22, `comp.enclosing.contact.1` 0.07,
`contact.width.1`/`contact.space.1` 0.22/0.25, `poly2.width.1`/
`poly2.space.1`/`poly2.enclosing.contact.1` 0.18/0.24/0.07, `metal1.width.1`/
`metal1.space.1` 0.23/0.23, `nwell.enclosing.comp.1` 0.12) are transcribed
from `klt`'s own gf180mcu deck
(`klayout_tools/decks/gf180mcu.py`, DRM-cited) so every margin below can be
checked against a real threshold, not tuned blind. Every margin is
deliberately well over its rule's minimum, in the same spirit
`layout/testcells/build.py`'s own margins document: so that a future
threshold correction does not turn this cell red for a reason unrelated to
its own geometry.

[kt322]: https://github.com/2AMLogic/klayout-tools/issues/322
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
# layout/testcells/build.py uses).
# --------------------------------------------------------------------------- #
NWELL = (21, 0)
COMP = (22, 0)
POLY2 = (30, 0)
CONTACT = (33, 0)
METAL1 = (34, 0)
METAL1_LABEL = (34, 10)

CELL_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_CELL = "ro_stage"

# --------------------------------------------------------------------------- #
# Device sizing -- from design/xschem/ro_stage.sch's own default parameters
# (`G {wstv=0.22u lstv=2u cld=0.5f}`), which is also ring1's instantiation in
# design/ro_array_core.spice (`xr1 ... wstv=0.220u`). Echoed into
# ro_stage.spice; a change here must be mirrored there.
# --------------------------------------------------------------------------- #
W_STARVE = 0.22  # Mph, Mnt (wstv)
L_STARVE = 2.00  # Mph, Mnt (lstv)
W_SWITCH_P = 0.44  # Mp
W_SWITCH_N = 0.22  # Mn
L_SWITCH = 0.28  # Mp, Mn

# --------------------------------------------------------------------------- #
# Geometry constants (um). See the module docstring for why every device is
# dog-boned and why the margins below are generous relative to the deck's
# minimums.
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
# X layout -- identical total span on both rows, so the "a" gate (shared by
# Mn and Mp) lands at the same x range on each and can be drawn as one
# continuous poly rectangle, the same way layout/testcells/build.py merges
# its single inverter's gate into one shape.
#
#   row      | pad(y) | gate(a) L=0.28 | gap | gate(tie) L=2.00 | pad(vddr/vss)
#   NMOS     | drain of Mn  | Mn  | (ny) | Mnt (tie=vddr) | source of Mnt
#   PMOS     | drain of Mp  | Mp  | (py) | Mph (tie=vss)  | source of Mph
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
    # Uniform W=0.22 under both gates (Mn and Mnt share the same width
    # here), so the comp between the two pads is one narrow rectangle.
    # ----------------------------------------------------------------- #
    ny0, ny1 = _pad(Y_NMOS)
    rect(COMP, X0, ny0, X0 + PAD_W, ny1)  # pad: drain of Mn -> y
    nn0, nn1 = _narrow(Y_NMOS, W_SWITCH_N)
    assert W_SWITCH_N == W_STARVE  # one narrow band covers both NMOS gates
    rect(COMP, X0 + PAD_W, nn0, X_GATE_TIE1, nn1)  # Mn + (ny) + Mnt channel
    rect(COMP, X_GATE_TIE1, ny0, X_PAD2, ny1)  # pad: source of Mnt -> vss

    # ----------------------------------------------------------------- #
    # PMOS row: pad(y) -- Mp[a] -- (py) -- Mph[vss-tie] -- pad(vddr)
    # Mp's own W (0.44) already equals PAD_H, so only the Mph crossing
    # needs narrowing.
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
    # Extended past each comp crossing for margin (no rule requires this
    # in the curated deck, but it is ordinary practice and costs nothing).
    # ----------------------------------------------------------------- #
    rect(POLY2, X_GATE_A0, ny0 - 0.30, X_GATE_A1, py1 + 0.30)
    # Landing pad, off to the side (mirrors layout/testcells/build.py's
    # inverter gate landing pad), safely inside the NMOS/PMOS gap and far
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
    mnt_gate_y0, mnt_gate_y1 = nn0 - 0.30, 1.05
    rect(POLY2, X_GAP1, mnt_gate_y0, X_GATE_TIE1, mnt_gate_y1)
    mnt_contact = (2.20, 0.70, 2.42, 0.92)
    rect(CONTACT, *mnt_contact)

    # ----------------------------------------------------------------- #
    # Mph gate poly (tied to vss) -- PMOS row only, mirrored.
    # ----------------------------------------------------------------- #
    # Contact kept clear of the narrow_Mph comp band below (pn0 = 1.75) --
    # a contact that only partly overlaps Comp trips comp.enclosing.contact.1
    # (it is not *enclosed*, just clipped); this one lands on bare poly.
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
    rect(CONTACT, y_contact_x[0], nn0, y_contact_x[1], nn1)
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
    rect(CONTACT, rail_contact_x[0], nn0, rail_contact_x[1], nn1)
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
        print(f"MISSING: {shown} -- run `python3 layout/cells/ro_stage/build.py`")
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
            f"run `python3 layout/cells/ro_stage/build.py`"
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
