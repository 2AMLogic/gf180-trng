#!/usr/bin/env python3
"""Draw and check `ro_buf`, the per-ring output buffer DR-0018 adopted.

    python3 layout/cells/ro_buf/build.py            # write ro_buf.gds
    python3 layout/cells/ro_buf/build.py --check     # rebuild, compare bytes

`ro_buf` is the `.subckt ro_buf` that `design/netlist.py` flattens into every
netlist instantiating it -- `design/trng_top.spice`, `design/
ro_array_core.spice`, `design/ro_array_core_meta.spice` and
`design/sampler_core.spice` all carry an identical copy, exported from
`design/xschem/ro_buf.sch`/`.sym`. There is deliberately no standalone
`design/ro_buf.spice`; the transcription below is taken from those flattened
copies (they agree device for device) and is independent of the geometry in
this file, which is what makes the `klt lvs` run next door mean something.

Two devices, one unstarved minimum-width CMOS inverter:

    vdd --[XMp: gate=a, W=0.44, L=0.28]-- y --[XMn: gate=a, W=0.22, L=0.28]-- vss

DR-0018 ("Adopt the per-ring output buffer", Proposed) is why this cell
exists: a ring driving the XOR combiner directly showed `sigma_1` 27.10x
higher with a switching neighbour than with a quiet one -- charge injected
backwards into the ring node through the combiner input stage's own gate
capacitance -- and one buffer per ring between the ring node and every
consumer takes that to 2.87x. `design/ro_array_core.spice` therefore
instantiates this cell **twice**, once per ring (`xb1 rn1 ro1 vdd vss ro_buf`
and `xb2 rn2 ro2 vdd vss ro_buf`, lines 17-18).

**One cell, placed twice -- not a ring1/ring2 pair.** Unlike `ro_stage`/
`ro_stage_ring2` and `ro_nand2`/`ro_nand2_ring2`, whose ring1/ring2 variants
are independently drawn because `xr1`/`xr2` pass different `wstv=` starve
widths into `ro_ring11`, both `ro_buf` instances instantiate the bare
subcircuit with no per-instance parameter override. The cell is a fixed
two-device inverter, so there is exactly one geometry to draw. DR-0018 is
also explicit that both buffers run off the block supply `vdd`/`vss`, never
off either ring's `vddr1`/`vddr2`: tying a buffer to its ring's own starved
supply would fold the buffer's switching current into the per-ring supply
signature DR-0007's independence argument and DR-0016's liveness monitor
both read. The pin named here is `vdd` for that reason, not `vddr`.

Why hand-drawn, not `klt gen mos_array`
----------------------------------------
`XMn` is drawn at `W=0.22um`, the gf180mcu 3.3 V core devices' own minimum,
and `klt gen mos_array` refuses `w_um` below 0.42um
([klayout-tools#322][kt322]; closed as a message-only fix -- the 0.42um floor
itself is unchanged, it is a generator-side contact-fit constraint rather
than a PDK DRC minimum). Generating at the floor would draw an NMOS roughly
double the intended width, which for an inverter means a skewed trip point
and a faster falling edge than the schematic specifies -- exactly the
"passes DRC/LVS but is not what the schematic says" failure issue #106
warns about. So this cell is hand-drawn from primitive geometry, the same
technique (and the same `layout/testcells/gdsii.py` writer) every other cell
under `layout/cells/` uses. See `layout/cells/ro_stage/build.py`'s own
docstring for the full account, including why every contacted diffusion
region here is "dog-boned": a 0.22um-wide active region cannot hold a
0.22 x 0.22um contact *and* the 0.07um `comp.enclosing.contact.1` margin
either side, so each device is drawn at full W only under its own gate and
widened to `PAD_H` wherever a contact lands. KLayout's own
`DeviceExtractorMOS4Transistor` measures W at the gate crossing, so the
extracted device is 0.22um wide, which is the point.

Design-rule values (`comp.width.1` 0.22, `comp.enclosing.contact.1` 0.07,
`contact.width.1`/`contact.space.1` 0.22/0.25, `poly2.width.1`/
`poly2.space.1`/`poly2.enclosing.contact.1` 0.18/0.24/0.07, `metal1.width.1`/
`metal1.space.1` 0.23/0.23, `metal1.enclosing.contact.1` 0.005,
`nwell.enclosing.comp.1` 0.12) are transcribed from `klt`'s own gf180mcu deck
(`klayout_tools/decks/gf180mcu.py`, DRM-cited), so every margin below is
checked against a real threshold rather than tuned blind. Every margin is
deliberately well over its rule's minimum, in the same spirit as the other
cells here: a future threshold correction should not turn this cell red for
a reason unrelated to its own geometry.

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
# Layers -- gf180mcu drawn layers, matching klt's curated decks (the same set
# every other cell under layout/cells/ uses).
# --------------------------------------------------------------------------- #
NWELL = (21, 0)
COMP = (22, 0)
POLY2 = (30, 0)
CONTACT = (33, 0)
METAL1 = (34, 0)
METAL1_LABEL = (34, 10)

CELL_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_CELL = "ro_buf"

# --------------------------------------------------------------------------- #
# Device sizing -- from the `.subckt ro_buf` body flattened into
# design/trng_top.spice (lines 170-180) and design/ro_array_core.spice, itself
# exported from design/xschem/ro_buf.sch. Echoed into ro_buf.spice; a change
# here must be mirrored there.
# --------------------------------------------------------------------------- #
W_P = 0.44  # XMp
W_N = 0.22  # XMn
L_GATE = 0.28  # both

# --------------------------------------------------------------------------- #
# Geometry constants (um). See the module docstring for why every device is
# dog-boned and why these margins are generous relative to the deck minimums.
# --------------------------------------------------------------------------- #
PAD_H = 0.44  # comp height at every contacted (source/drain) region
PAD_W = 0.70  # comp x-extent of a contacted region
ROW_GAP = 1.20  # comp-comp vertical gap between the NMOS and PMOS rows (deck min 0.28)
NWELL_MARGIN = 0.25  # Nwell enclosure of PMOS comp (deck min 0.12)
POLY_OVERHANG = 0.30  # poly2 extension past each comp crossing

assert PAD_H == W_P, "PAD_H sized so the PMOS row needs no narrowing for XMp's own W"
assert PAD_H >= W_N

# Row 1 (NMOS) centreline and row 2 (PMOS) centreline -- the same two-row
# arrangement layout/cells/ro_stage/build.py uses, at the same pitch, so the
# two cells abut consistently if a future assembly ever rows them together.
Y_NMOS = PAD_H / 2  # 0.22
Y_PMOS = PAD_H + ROW_GAP + PAD_H / 2  # 0.44 + 1.20 + 0.22 = 1.86


def _pad(y_center: float) -> tuple[float, float]:
    return (y_center - PAD_H / 2, y_center + PAD_H / 2)


def _narrow(y_center: float, w: float) -> tuple[float, float]:
    return (y_center - w / 2, y_center + w / 2)


# --------------------------------------------------------------------------- #
# X layout -- identical span on both rows, so the single `a` gate (shared by
# XMn and XMp, as in any inverter) is one continuous poly rectangle crossing
# both channels.
#
#   row  | pad (drain -> y) | gate(a) L=0.28 | pad (source -> rail)
#   NMOS | y                | XMn            | vss
#   PMOS | y                | XMp            | vdd
# --------------------------------------------------------------------------- #
X0 = 0.0
X_GATE0 = X0 + PAD_W
X_GATE1 = X_GATE0 + L_GATE
X_RIGHT = X_GATE1 + PAD_W  # right edge of the drawn diffusion

assert X_RIGHT == PAD_W + L_GATE + PAD_W

#: Contact x-ranges, one per diffusion pad, at the deck's fixed 0.22um contact
#: size. Both sit 0.24um in from their pad's own outer edge -- comfortably over
#: `comp.enclosing.contact.1` (0.07) and far over `contact.space.1` (0.25)
#: from each other.
DRAIN_CONTACT_X = (X0 + 0.24, X0 + 0.46)
SOURCE_CONTACT_X = (X_GATE1 + 0.24, X_GATE1 + 0.46)

assert SOURCE_CONTACT_X[0] - DRAIN_CONTACT_X[1] >= 0.25, "contact.space.1 margin"


def build_shapes() -> tuple[list[Rect], list[Label]]:
    rects: list[Rect] = []
    labels: list[Label] = []

    def rect(layer, x0, y0, x1, y1):
        rects.append(Rect(layer[0], layer[1], x0, y0, x1, y1))

    def label(layer, x, y, text):
        labels.append(Label(layer[0], layer[1], x, y, text))

    # ----------------------------------------------------------------- #
    # NMOS row: pad(y) -- XMn[a] -- pad(vss).
    # Only the gate crossing is at W_N; both pads widen to PAD_H so their
    # contacts have comp enclosure to sit in.
    # ----------------------------------------------------------------- #
    ny0, ny1 = _pad(Y_NMOS)
    nn0, nn1 = _narrow(Y_NMOS, W_N)
    rect(COMP, X0, ny0, X_GATE0, ny1)  # pad: drain of XMn -> y
    rect(COMP, X_GATE0, nn0, X_GATE1, nn1)  # XMn channel, at W_N
    rect(COMP, X_GATE1, ny0, X_RIGHT, ny1)  # pad: source of XMn -> vss

    # ----------------------------------------------------------------- #
    # PMOS row: pad(y) -- XMp[a] -- pad(vdd).
    # XMp's own W (0.44) already equals PAD_H, so this row is one
    # uninterrupted rectangle -- nothing to narrow.
    # ----------------------------------------------------------------- #
    py0, py1 = _pad(Y_PMOS)
    assert abs((py1 - py0) - W_P) < 1e-9  # float arithmetic; the writer grids to 1 nm
    rect(COMP, X0, py0, X_RIGHT, py1)

    # ----------------------------------------------------------------- #
    # Nwell around the PMOS row only. The NMOS row sits in the substrate.
    # ----------------------------------------------------------------- #
    rect(
        NWELL,
        X0 - NWELL_MARGIN,
        py0 - NWELL_MARGIN,
        X_RIGHT + NWELL_MARGIN,
        py1 + NWELL_MARGIN,
    )

    # ----------------------------------------------------------------- #
    # `a` gate poly -- one rectangle crossing both rows' channels, plus a
    # landing pad off to the left (in the clear band between the two rows)
    # for its contact. The two shapes overlap, so this is one poly polygon
    # and no poly2.space.1 question arises inside the cell.
    # ----------------------------------------------------------------- #
    rect(POLY2, X_GATE0, ny0 - POLY_OVERHANG, X_GATE1, py1 + POLY_OVERHANG)
    a_pad_y0, a_pad_y1 = 0.75, 1.25
    assert ny1 < a_pad_y0 and a_pad_y1 < py0, "gate landing pad clears both comp rows"
    rect(POLY2, -0.50, a_pad_y0, X_GATE1, a_pad_y1)
    rect(CONTACT, -0.40, 0.89, -0.18, 1.11)
    rect(METAL1, -0.44, 0.85, -0.14, 1.15)
    label(METAL1_LABEL, -0.29, 1.00, "a")

    # ----------------------------------------------------------------- #
    # pad(y) contacts on both rows, strapped together in metal1 -- the
    # cell's single output, and its only internal-to-external node.
    # ----------------------------------------------------------------- #
    rect(CONTACT, DRAIN_CONTACT_X[0], nn0, DRAIN_CONTACT_X[1], nn1)
    rect(CONTACT, DRAIN_CONTACT_X[0], Y_PMOS - 0.11, DRAIN_CONTACT_X[1], Y_PMOS + 0.11)
    y_metal_n = (0.14, ny0 + 0.01, 0.56, ny1 - 0.01)
    y_metal_p = (0.14, py0 + 0.01, 0.56, py1 - 0.01)
    rect(METAL1, *y_metal_n)
    rect(METAL1, *y_metal_p)
    # The strap is 0.30um wide, not the 0.23um `metal1.width.1` minimum it
    # used to be drawn just over: `layout/blocks/combiner_sampler/build.py`
    # drops this cell's `y` Via1 right here, and a Via1 is a fixed 0.26um
    # square (gf180mcu DRM 7.14 "Vn.1"), so a narrower strap leaves part of
    # the cut outside metal1 -- `metal1.enclosing.via1.1`, issue #162. 0.30
    # clears the cut by 0.02um on each side and still leaves 0.34um to the
    # `a` pin's own metal, well over `metal1.space.1` (0.23).
    Y_STRAP_X = (0.20, 0.50)
    rect(METAL1, Y_STRAP_X[0], y_metal_n[3] - 0.03, Y_STRAP_X[1], y_metal_p[1] + 0.03)
    assert Y_STRAP_X[1] - Y_STRAP_X[0] >= 0.26 + 2 * 0.02, "metal1.enclosing.via1.1 headroom"
    assert Y_STRAP_X[0] - (-0.14) >= 0.23, "metal1.space.1: y strap to a pin metal"
    label(METAL1_LABEL, 0.35, Y_NMOS, "y")

    # ----------------------------------------------------------------- #
    # pad(vss) (NMOS) and pad(vdd) (PMOS) contacts + metal pads. The two
    # rails are deliberately NOT strapped to each other here -- they are
    # separate pins of the subcircuit.
    # ----------------------------------------------------------------- #
    rect(CONTACT, SOURCE_CONTACT_X[0], nn0, SOURCE_CONTACT_X[1], nn1)
    rect(
        CONTACT, SOURCE_CONTACT_X[0], Y_PMOS - 0.11, SOURCE_CONTACT_X[1], Y_PMOS + 0.11
    )
    rect(METAL1, X_GATE1 + 0.14, ny0 + 0.01, X_GATE1 + 0.56, ny1 - 0.01)
    rect(METAL1, X_GATE1 + 0.14, py0 + 0.01, X_GATE1 + 0.56, py1 - 0.01)
    label(METAL1_LABEL, X_GATE1 + 0.35, Y_NMOS, "vss")
    label(METAL1_LABEL, X_GATE1 + 0.35, Y_PMOS, "vdd")

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
        print(f"MISSING: {shown} -- run `python3 layout/cells/ro_buf/build.py`")
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
            f"run `python3 layout/cells/ro_buf/build.py`"
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
