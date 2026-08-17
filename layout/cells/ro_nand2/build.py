#!/usr/bin/env python3
"""Draw and check `ro_nand2`, the ring's one stoppable stage.

    python3 layout/cells/ro_nand2/build.py            # write ro_nand2.gds
    python3 layout/cells/ro_nand2/build.py --check     # rebuild, compare bytes

`ro_nand2` is `design/ro_array_core.spice`'s `.subckt ro_nand2` (from
`design/xschem/ro_nand2.sch`): a 2-input NAND with the same series-starved
topology `layout/cells/ro_stage/build.py`'s `ro_stage` establishes (see that
module's docstring for the full "why hand-drawn, why dog-boned" account,
which applies unchanged here), used once per ring in place of one `ro_stage`
to gate the ring's oscillation on `en`. Drawn at the schematic's own default
sizing (`wstv=0.22u`, ring1's value -- the same convention `ro_stage/`
itself uses for its own first drawn variant).

Six devices (`design/ro_array_core.spice`'s `.subckt ro_nand2`):

    XMph py vss vddr vddr  pfet L=lstv W=wstv   -- starve, gate=vss (opposite rail)
    XMpa y  a  py  vddr    pfet L=0.28 W=0.44   -- pull-up, gate=a
    XMpb y  en py  vddr    pfet L=0.28 W=0.44   -- pull-up, gate=en
    XMna y  a  nm  vss     nfet L=0.28 W=0.44   -- pull-down, gate=a
    XMnb nm en ny  vss     nfet L=0.28 W=0.44   -- pull-down, gate=en
    XMnt ny vddr vss vss   nfet L=lstv W=wstv   -- starve, gate=vddr (opposite rail)

`XMpa`/`XMpb` are wired in *parallel* (both source=`py`, drain=`y`): either
input low pulls `y` high through the shared starve device `XMph`. `XMna`/
`XMnb` are wired in *series* (`y`-`nm`-`ny`): both `a` and `en` must be high
to pull `y` low through the shared starve device `XMnt`. Together this is a
plain NAND2 (`y = NOT(a AND en)`), with `en` low forcing `y` high regardless
of `a` -- the mechanism the ring uses to stop oscillating.

Layout technique
-----------------
The series pull-down (`XMna`/`XMnb`) is drawn the same way `ro_stage`'s own
NMOS row is: one continuous full-height comp strip crossed by two gates in
sequence (`a` then `en`), narrowing only across `XMnt`'s own starve channel.
Both `XMna` and `XMnb` are `W=0.44`, which already equals `PAD_H`, so
(unlike `ro_stage`'s minimum-width NMOS) neither needs dog-boning.

The parallel pull-up pair (`XMpa`/`XMpb`) is the one new technique this cell
needs: two transistors sharing the *same* source (`py`) and *same* drain
(`y`) cannot be drawn as a simple series chain (that would wire `XMpb`
between `y` and a second, different node). Instead they are drawn
"back-to-back" -- one continuous comp strip crossed by `a`'s gate, then `y`'s
pad, then `en`'s gate again -- so the two gate crossings are electrically
*siblings* off a shared middle region (`y`) rather than a series chain, with
the two ends (`py`, on the near side of `XMph`, and `py2`, the far end past
`XMpb`) tied together by an explicit metal1 riser. This is the ordinary
"folded" technique for drawing parallel-source/parallel-drain transistors
(the same idea as a multi-finger MOSFET's shared internal diffusion), not a
DRC workaround -- `py`/`py2` are two separate diffusion islands (each gate
crossing electrically isolates the comp on either side of it), so they need
an explicit tie the way `ro_stage`'s single-branch `py`/`ny` never did.

`a` and `en` are each an external pin (unlike `ro_stage`'s internal `py`/
`ny`), so each gets its own off-to-the-side poly landing pad + contact +
metal1 label, the same technique `ro_stage`'s own `a` pin uses -- extended
here to two pins by keeping each landing pad's own X range >= poly2.space.1
clear of the other's and of every tie gate's.

Every long inter-row tie (`XMnt`-to-`vddr`, `XMph`-to-`vss`, `py`-to-`py2`,
the NMOS/PMOS `y` tie) is routed through open space -- above the PMOS row,
below the NMOS row, or through an empty stretch of the row gap -- rather
than through the pin landing pads' own Y band, specifically to avoid the
`metal1.space.1` violations a shorter, more direct route would risk against
a pin's own local metal.

Design-rule values (`comp.width.1` 0.22, `comp.enclosing.contact.1` 0.07,
`contact.width.1`/`contact.space.1` 0.22/0.25, `poly2.width.1`/
`poly2.space.1`/`poly2.enclosing.contact.1` 0.18/0.24/0.07, `metal1.width.1`/
`metal1.space.1` 0.23/0.23, `nwell.enclosing.comp.1` 0.12) are the same set
`ro_stage/build.py`'s own docstring transcribes from `klt`'s gf180mcu deck;
every margin below is checked against those thresholds, generously over
each one's minimum for the same reason `ro_stage/build.py` documents.
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
# Layers -- gf180mcu drawn layers, matching klt's curated decks.
# --------------------------------------------------------------------------- #
NWELL = (21, 0)
COMP = (22, 0)
POLY2 = (30, 0)
CONTACT = (33, 0)
METAL1 = (34, 0)
METAL1_LABEL = (34, 10)

CELL_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_CELL = "ro_nand2"

# --------------------------------------------------------------------------- #
# Device sizing -- design/xschem/ro_nand2.sch's own default parameters
# (`wstv=0.22u lstv=2u`, ring1's value; see the module docstring). Echoed
# into ro_nand2.spice; a change here must be mirrored there.
# --------------------------------------------------------------------------- #
W_STARVE = 0.22  # XMph, XMnt (wstv)
L_STARVE = 2.00  # XMph, XMnt (lstv)
W_PARALLEL = 0.44  # XMpa, XMpb, XMna, XMnb
L_SWITCH = 0.28  # XMpa, XMpb, XMna, XMnb

# --------------------------------------------------------------------------- #
# Geometry constants (um).
# --------------------------------------------------------------------------- #
PAD_H = 0.44  # comp height at every contacted (source/drain) region
PAD_W = 0.70  # comp x-extent of a contacted end pad (pad_y, pad_vddr, pad_vss)
GATE_GAP = 0.80  # x-span reserved between adjacent gates for an internal-node
# contact (py, py2) or a pin's own landing pad -- wider than ro_stage's 0.40
# GATE_GAP because several of these gaps host a contact ro_stage's own
# internal nm/ny gaps never needed to.
ROW_GAP = 1.20  # comp-comp vertical gap between the NMOS and PMOS rows
NWELL_MARGIN = 0.25  # Nwell enclosure of PMOS comp
#: How far a metal1 riser runs past the contact it lands on, on the side the
#: riser leaves from. `metal1.enclosing.contact.1` (gf180mcu DRM 7.12 rule
#: "CO.6") requires 0.005um of metal1 beyond the cut on every side; each
#: riser below used to *start* on its contact's own edge, i.e. at exactly
#: 0.0um, which the deck this repo installed before #142 did not check and
#: the one it pins now does (issue #162). 0.02um is 4x the requirement and
#: still leaves every neighbouring metal1 shape >= metal1.space.1 (0.23)
#: away -- asserted where each riser is drawn.
M1_CONTACT_MARGIN = 0.02

assert PAD_H == W_PARALLEL, "PAD_H sized to need no narrowing for Mpa/Mpb/Mna/Mnb"

Y_NMOS = PAD_H / 2  # 0.22 -- NMOS row spans [0, 0.44]
Y_PMOS = PAD_H + ROW_GAP + PAD_H / 2  # 1.86 -- PMOS row spans [1.64, 2.08]


def _pad(y_center: float) -> tuple[float, float]:
    return (y_center - PAD_H / 2, y_center + PAD_H / 2)


def _narrow(y_center: float, w: float) -> tuple[float, float]:
    return (y_center - w / 2, y_center + w / 2)


# --------------------------------------------------------------------------- #
# X layout. `a`'s gate and `en`'s gate land at the same X range on both rows
# (NMOS: XMna/XMnb; PMOS: XMpa/XMpb), so each is drawn as one poly rectangle
# spanning both rows, the same technique ro_stage/build.py uses for its own
# `a` gate.
#
#   NMOS row: pad(y) -- XMna[a] -- (nm) -- XMnb[en] -- (ny) -- XMnt[tie=vddr] -- pad(vss)
#   PMOS row: pad(vddr) -- XMph[tie=vss] -- (py) -- XMpa[a] -- pad(y) -- XMpb[en] -- (py2)
# --------------------------------------------------------------------------- #
X0 = 0.0
X_A0 = X0 + PAD_W  # 0.70
X_A1 = X_A0 + L_SWITCH  # 0.98
X_EN0 = X_A1 + GATE_GAP  # 1.78
X_EN1 = X_EN0 + L_SWITCH  # 2.06
X_MNT0 = X_EN1 + GATE_GAP  # 2.86
X_MNT1 = X_MNT0 + L_STARVE  # 4.86
X_END = X_MNT1 + PAD_W  # 5.56 -- NMOS row's own right edge

# PMOS row: XMph + its pad_vddr sit to the *left* of X_A0 (negative X), so
# that `a`'s gate still lands at [X_A0, X_A1] to match the NMOS row above.
X_PY0 = X_A0 - GATE_GAP  # -0.10 -- left edge of (py), right after XMph's channel
X_MPH0 = X_PY0 - L_STARVE  # -2.10
X_VDDR0 = X_MPH0 - PAD_W  # -2.80
X_PY2_1 = X_EN1 + GATE_GAP  # 2.86 -- right edge of (py2), matches X_MNT0


def build_shapes() -> tuple[list[Rect], list[Label]]:
    rects: list[Rect] = []
    labels: list[Label] = []

    def rect(layer, x0, y0, x1, y1):
        rects.append(Rect(layer[0], layer[1], x0, y0, x1, y1))

    def label(layer, x, y, text):
        labels.append(Label(layer[0], layer[1], x, y, text))

    ny0, ny1 = _pad(Y_NMOS)  # (0.00, 0.44)
    py0, py1 = _pad(Y_PMOS)  # (1.64, 2.08)
    nt0, nt1 = _narrow(Y_NMOS, W_STARVE)  # XMnt channel band
    pt0, pt1 = _narrow(Y_PMOS, W_STARVE)  # XMph channel band

    # ----------------------------------------------------------------- #
    # NMOS row comp: pad(y) -- XMna[a] -- (nm) -- XMnb[en] -- (ny) --
    # narrows only across XMnt's own channel -- pad(vss). XMna/XMnb are
    # both W=PAD_H, so the whole span up to XMnt's channel is one
    # full-height rectangle (mirrors layout/cells/ro_stage_ring2/build.py's
    # fix: narrowing only exactly at a gate's own crossing, never abutting
    # two different widths at a shared gate edge, is what makes `klt
    # extract` measure each device's W/L cleanly).
    # ----------------------------------------------------------------- #
    rect(COMP, X0, ny0, X_MNT0, ny1)  # pad(y) + XMna + (nm) + XMnb + (ny)
    rect(COMP, X_MNT0, nt0, X_MNT1, nt1)  # XMnt channel, narrowed to W_STARVE
    rect(COMP, X_MNT1, ny0, X_END, ny1)  # pad(vss)

    # ----------------------------------------------------------------- #
    # PMOS row comp: pad(vddr) -- narrows only across XMph's own channel --
    # (py) -- XMpa[a] -- pad(y) -- XMpb[en] -- (py2). XMpa/XMpb are both
    # W=PAD_H, so (py) through (py2) is one full-height rectangle; (py)
    # and (py2) are two electrically distinct islands (the two gate
    # crossings in between isolate them) despite being drawn as one
    # continuous strip -- they are tied by the metal1 riser below.
    # ----------------------------------------------------------------- #
    rect(COMP, X_VDDR0, py0, X_MPH0, py1)  # pad(vddr)
    rect(COMP, X_MPH0, pt0, X_PY0, pt1)  # XMph channel, narrowed to W_STARVE
    rect(COMP, X_PY0, py0, X_PY2_1, py1)  # (py) + XMpa + pad(y) + XMpb + (py2)

    # ----------------------------------------------------------------- #
    # Nwell around the PMOS row only.
    # ----------------------------------------------------------------- #
    rect(
        NWELL,
        X_VDDR0 - NWELL_MARGIN,
        py0 - NWELL_MARGIN,
        X_PY2_1 + NWELL_MARGIN,
        py1 + NWELL_MARGIN,
    )

    # ----------------------------------------------------------------- #
    # `a` gate poly -- one rectangle crossing both rows (XMna, XMpa), plus
    # an off-to-the-side landing pad + contact + metal1 pin, the same
    # technique ro_stage/build.py uses for its own `a` pin.
    # ----------------------------------------------------------------- #
    rect(POLY2, X_A0, ny0 - 0.30, X_A1, py1 + 0.30)
    a_pad_y0, a_pad_y1 = 1.00, 1.50
    # Landing pad's left edge stays >= poly2.space.1 clear of XMph's own
    # channel crossing ([X_MPH0, X_PY0]), which it would otherwise overlap
    # in x at this y band (checked below by assertion).
    a_pad_x0 = 0.20
    rect(POLY2, a_pad_x0, a_pad_y0, X_A1, a_pad_y1)
    a_contact = (0.48, 1.14, 0.70, 1.36)
    rect(CONTACT, *a_contact)
    a_metal = (0.44, 1.10, 0.74, 1.40)
    rect(METAL1, *a_metal)
    label(METAL1_LABEL, 0.59, 1.25, "a")
    assert a_pad_x0 - X_PY0 >= 0.24, "poly2.space.1: a's landing pad to XMph's channel"

    # ----------------------------------------------------------------- #
    # `en` gate poly -- one rectangle crossing both rows (XMnb, XMpb), plus
    # its own landing pad extended to the *right* of its own gate (so its
    # X range stays >= poly2.space.1 clear of `a`'s landing pad and of
    # XMnt's gate) + contact + metal1 pin.
    # ----------------------------------------------------------------- #
    rect(POLY2, X_EN0, ny0 - 0.30, X_EN1, py1 + 0.30)
    en_pad_y0, en_pad_y1 = a_pad_y0, a_pad_y1  # same Y band as `a`'s pad
    rect(POLY2, X_EN0, en_pad_y0, 2.50, en_pad_y1)
    en_contact = (2.15, 1.14, 2.37, 1.36)
    rect(CONTACT, *en_contact)
    en_metal = (2.11, 1.10, 2.41, 1.40)
    rect(METAL1, *en_metal)
    label(METAL1_LABEL, 2.26, 1.25, "en")
    assert X_EN0 - X_A1 >= 0.24, "poly2.space.1: a's landing pad to en's gate"
    assert X_MNT0 - 2.50 >= 0.24, "poly2.space.1: en's landing pad to XMnt's gate"

    # ----------------------------------------------------------------- #
    # XMnt gate poly (tied to vddr) -- NMOS row, tall enough (nothing else
    # occupies this X range in the row gap) to host its own contact
    # directly, mirroring ro_stage/build.py's Mnt gate.
    # ----------------------------------------------------------------- #
    mnt_gate_y0, mnt_gate_y1 = nt0 - 0.30, 1.05
    rect(POLY2, X_MNT0, mnt_gate_y0, X_MNT1, mnt_gate_y1)
    mnt_contact = (3.75, 0.70, 3.97, 0.92)
    rect(CONTACT, *mnt_contact)

    # ----------------------------------------------------------------- #
    # XMph gate poly (tied to vss) -- PMOS row. Unlike XMnt, XMph's own
    # channel X range ([X_MPH0, X_PY0]) overlaps `a`'s landing pad's X
    # range, so its own landing/contact is drawn as a second, localized
    # rectangle (well clear of `a`'s pad in X) rather than by tallening the
    # whole channel crossing the way XMnt's is.
    # ----------------------------------------------------------------- #
    rect(POLY2, X_MPH0, py0 - 0.05, X_PY0, py1 + 0.05)  # channel crossing only
    mph_landing = (-1.35, 1.25, -0.85, 1.70)
    rect(POLY2, *mph_landing)
    mph_contact = (-1.24, 1.40, -1.02, 1.62)
    rect(CONTACT, *mph_contact)
    assert a_pad_x0 - mph_landing[2] >= 0.24, "poly2.space.1: a's pad to XMph's landing"

    # ----------------------------------------------------------------- #
    # (py) <-> (py2) tie -- both XMpa/XMpb pull-up branches' shared source,
    # drawn as two separate diffusion islands (see module docstring) and
    # tied by a metal1 riser routed *above* the PMOS row, clear of every
    # other net's metal down in the row itself.
    # ----------------------------------------------------------------- #
    py_contact = (0.18, 1.75, 0.40, 1.97)
    py2_contact = (2.34, 1.75, 2.56, 1.97)
    rect(CONTACT, *py_contact)
    rect(CONTACT, *py2_contact)
    PY_JOG_Y = (2.25, 2.55)
    # Both risers start M1_CONTACT_MARGIN *below* their contact's own bottom
    # edge, not flush with it, so metal1 encloses the cut on that side too.
    py_riser_y0 = py_contact[1] - M1_CONTACT_MARGIN
    rect(METAL1, 0.16, py_riser_y0, 0.42, PY_JOG_Y[1])
    rect(METAL1, 2.32, py_riser_y0, 2.58, PY_JOG_Y[1])
    rect(METAL1, 0.16, PY_JOG_Y[0], 2.58, PY_JOG_Y[1])
    # The `en` pin's own metal sits directly under (py2)'s riser in X; `a`'s
    # is 0.02 clear of (py)'s riser in X but shares no Y band with it. Both
    # gaps are checked once, here, against the riser's new lower edge.
    assert py_riser_y0 - en_metal[3] >= 0.23, "metal1.space.1: py/py2 riser to en pin metal"

    # ----------------------------------------------------------------- #
    # pad(y): one contact per row (NMOS drain-of-XMna/XMnb-pair pad, PMOS
    # shared XMpa/XMpb drain pad), tied by a metal1 riser through the row
    # gap -- clear of `a`/`en`'s own pin metal (different Y band) and of
    # the below-/above-row tie lanes (different Y band again).
    # ----------------------------------------------------------------- #
    y_contact_n = (0.24, 0.11, 0.46, 0.33)
    y_contact_p = (1.27, 1.75, 1.49, 1.97)
    rect(CONTACT, *y_contact_n)
    rect(CONTACT, *y_contact_p)
    Y_JOG_Y = (0.55, 0.85)
    y_vert_p_top = 1.99  # just above y_contact_p's own top (1.97)
    rect(METAL1, 0.20, 0.09, 0.50, Y_JOG_Y[1])
    rect(METAL1, 1.23, Y_JOG_Y[0], 1.53, y_vert_p_top)
    rect(METAL1, 0.20, Y_JOG_Y[0], 1.53, Y_JOG_Y[1])
    label(METAL1_LABEL, 0.35, Y_NMOS, "y")
    assert a_metal[1] - Y_JOG_Y[1] >= 0.23, "metal1.space.1: y-tie jog to a/en pin metal"
    assert PY_JOG_Y[0] - y_vert_p_top >= 0.23, "metal1.space.1: y-tie riser to py-py2 jog"

    # ----------------------------------------------------------------- #
    # pad(vddr) (PMOS, far left) and pad(vss) (NMOS, far right) contacts +
    # local metal + labels.
    # ----------------------------------------------------------------- #
    vddr_contact = (-2.60, 1.75, -2.38, 1.97)
    vss_contact = (5.10, 0.11, 5.32, 0.33)
    rect(CONTACT, *vddr_contact)
    rect(CONTACT, *vss_contact)
    label(METAL1_LABEL, (X_VDDR0 + X_MPH0) / 2, Y_PMOS, "vddr")
    label(METAL1_LABEL, (X_MNT1 + X_END) / 2, Y_NMOS, "vss")

    # ----------------------------------------------------------------- #
    # XMnt-tie riser: contact -> vertical run (clear of the PMOS row's own
    # comp, which ends at X_PY2_1) -> horizontal jog *above* the PMOS row
    # -> vertical run down into pad(vddr).
    # ----------------------------------------------------------------- #
    VDDR_JOG_Y = (2.80, 3.10)
    assert VDDR_JOG_Y[0] - PY_JOG_Y[1] >= 0.23, "metal1.space.1: vddr jog to py-py2 jog"
    # Both risers again start M1_CONTACT_MARGIN below their own contact's
    # bottom edge rather than flush with it (see M1_CONTACT_MARGIN).
    rect(METAL1, 3.73, mnt_contact[1] - M1_CONTACT_MARGIN, 3.99, VDDR_JOG_Y[1])
    rect(METAL1, -2.62, vddr_contact[1] - M1_CONTACT_MARGIN, -2.36, VDDR_JOG_Y[1])
    rect(METAL1, -2.62, VDDR_JOG_Y[0], 3.99, VDDR_JOG_Y[1])  # the jog itself

    # ----------------------------------------------------------------- #
    # XMph-tie riser: contact -> vertical run (down through the row gap,
    # clear of the NMOS row's own comp, which starts at X0=0) -> horizontal
    # jog *below* the NMOS row -> vertical run up into pad(vss).
    # ----------------------------------------------------------------- #
    VSS_JOG_Y = (-0.55, -0.25)
    # This riser leaves its contact downward, so the M1_CONTACT_MARGIN goes
    # on the *top* edge (the one that was flush with mph_contact's own top).
    rect(METAL1, -1.26, VSS_JOG_Y[0], -1.00, mph_contact[3] + M1_CONTACT_MARGIN)
    rect(METAL1, 5.08, VSS_JOG_Y[0], 5.34, 0.35)  # vss_contact -> jog
    rect(METAL1, -1.26, VSS_JOG_Y[0], 5.34, VSS_JOG_Y[1])  # the jog itself

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
        print(f"MISSING: {shown} -- run `python3 layout/cells/ro_nand2/build.py`")
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
            f"run `python3 layout/cells/ro_nand2/build.py`"
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
