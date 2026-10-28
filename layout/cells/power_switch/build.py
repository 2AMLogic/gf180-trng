#!/usr/bin/env python3
"""Draw and check `power_switch`, the PMOS header for the gated digital supply (issue #707).

    python3 layout/cells/power_switch/build.py            # write power_switch.gds
    python3 layout/cells/power_switch/build.py --check     # rebuild, compare bytes

`power_switch` is `design/power_switch.spice`'s `.subckt power_switch`
(`design/xschem/power_switch.sch`) at its default parameters: one PFET of
`nfing = 40` parallel fingers, each `wf = 10um` wide at `lsw = 0.28um`, so 400um
in total, between the always-on `vdd` and the gated `vvdd`, with `sleep` on the gate.

Topology, drawn as one shared-diffusion strip:

    pad0 | g0 | pad1 | g1 | ... | g39 | pad40        (41 pads, 40 gates)
     vdd    sleep  vvdd                  vdd        (even pads source, odd pads drain)

Every pad carries one column of contacts and a Metal1 stripe. Even (source) stripes
run up to a Metal1 bar over the strip that is `vdd`; odd (drain) stripes run down to a
Metal1 bar under the strip that is `vvdd`. The 40 gate fingers extend below the strip
and join one poly bus, which lands on a contact and a Metal1 pad on the left (`sleep`).
Only Metal1 is used: the cell has no routing of its own beyond its three buses, and the
pins are the bars and the pad.

Why hand-drawn: like every cell under `layout/cells/`, it is drawn from explicit
rectangles, so that the LVS reference (`power_switch.spice` next door) is transcribed
independently of the geometry and `klt lvs` compares two separate statements.

What is NOT drawn, stated so nobody reads the cell as more than it is:
  - no n-well tap and no implant layers (the curated extraction deck used by every
    cell under `layout/cells/` takes a PFET's well as a floating net, so the well bias
    to `vdd` is not checked here, and a tapeout cell would need a well tap ring);
  - no guard ring and no substrate tap;
  - no sizing for electromigration: the Metal1 buses are 1.0um wide and carry the
    cell's DC current (a few mA at most), which is well inside the PDK's limit, but
    this is a statement about the numbers and not a check.

Design-rule values (`comp.width.1` 0.22, `comp.enclosing.contact.1` 0.07,
`contact.width.1`/`contact.space.1` 0.22/0.25, `poly2.width.1`/`poly2.space.1`/
`poly2.enclosing.contact.1` 0.18/0.24/0.07, `metal1.width.1`/`metal1.space.1`
0.23/0.23, `nwell.enclosing.comp.1` 0.12) are transcribed from `klt`'s own gf180mcu
deck, as the other cells here do. Every margin is deliberately over its minimum.
"""

from __future__ import annotations

import os
import sys

_TESTCELL_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "testcells"
)
sys.path.insert(0, os.path.abspath(_TESTCELL_DIR))
_CELLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.abspath(_CELLS_DIR))

from _build_cli import gds_file, make_check, make_main  # noqa: E402
from gdsii import Label, Rect, write_gds  # noqa: E402

NWELL = (21, 0)
COMP = (22, 0)
POLY2 = (30, 0)
CONTACT = (33, 0)
METAL1 = (34, 0)
METAL1_LABEL = (34, 10)

CELL_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_CELL = "power_switch"

# Device sizing -- from design/power_switch.spice at its default parameters.
# Echoed into power_switch.spice; a change here must be mirrored there.
NFING = 40
W_FINGER = 10.0
L_GATE = 0.28

# Geometry constants (um).
PAD_W = 0.70  # comp x-extent of a contacted pad
PITCH = PAD_W + L_GATE
CONTACT_SIZE = 0.22
CONTACT_PITCH = 0.47  # 0.22 contact + 0.25 contact.space.1
CONTACT_EDGE = 0.24  # first contact edge from the pad edge, both axes
M1_STRIPE_W = 0.42
M1_STRIPE_INSET = 0.14
POLY_OVERHANG = 0.30
BUS_H = 1.0  # Metal1 bar height
BAR_GAP = 0.60  # Metal1 gap between a bar and the stripe ends that must not touch it
GATE_BUS_Y = (-2.60, -2.10)  # poly bus, below the vvdd bar
NWELL_MARGIN = 0.50

N_PADS = NFING + 1
X_RIGHT = N_PADS * PAD_W + NFING * L_GATE
Y0, Y1 = 0.0, W_FINGER

assert abs(PITCH * NFING + PAD_W - X_RIGHT) < 1e-9
assert CONTACT_EDGE >= 0.07 and CONTACT_PITCH - CONTACT_SIZE >= 0.25 - 1e-9, "contact rules"
assert CONTACT_EDGE + CONTACT_SIZE <= PAD_W - 0.07, "comp.enclosing.contact.1 across the pad"


def pad_x(i: int) -> tuple[float, float]:
    x0 = i * PITCH
    return x0, x0 + PAD_W


def gate_x(i: int) -> tuple[float, float]:
    x0 = i * PITCH + PAD_W
    return x0, x0 + L_GATE


def contact_ys() -> list[float]:
    ys = []
    y = Y0 + CONTACT_EDGE
    while y + CONTACT_SIZE <= Y1 - 0.07 + 1e-9:
        ys.append(round(y, 3))
        y += CONTACT_PITCH
    return ys


def build_shapes() -> tuple[list[Rect], list[Label]]:
    rects: list[Rect] = []
    labels: list[Label] = []

    def rect(layer, x0, y0, x1, y1):
        rects.append(Rect(layer[0], layer[1], round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)))

    def label(layer, x, y, text):
        labels.append(Label(layer[0], layer[1], round(x, 3), round(y, 3), text))

    # The shared diffusion strip and the n-well around it.
    rect(COMP, 0.0, Y0, X_RIGHT, Y1)
    rect(NWELL, -NWELL_MARGIN, Y0 - NWELL_MARGIN, X_RIGHT + NWELL_MARGIN, Y1 + NWELL_MARGIN)

    # Gate fingers, each running down from over the strip to the poly bus.
    for i in range(NFING):
        gx0, gx1 = gate_x(i)
        rect(POLY2, gx0, GATE_BUS_Y[0], gx1, Y1 + POLY_OVERHANG)
    bus_x0 = -1.10
    rect(POLY2, bus_x0, GATE_BUS_Y[0], gate_x(NFING - 1)[1], GATE_BUS_Y[1])

    # Metal1 bars: vdd over the strip, vvdd under it.
    vdd_bar = (Y1 + BAR_GAP, Y1 + BAR_GAP + BUS_H)
    vvdd_bar = (Y0 - BAR_GAP - BUS_H, Y0 - BAR_GAP)
    rect(METAL1, 0.0, vdd_bar[0], X_RIGHT, vdd_bar[1])
    rect(METAL1, 0.0, vvdd_bar[0], X_RIGHT, vvdd_bar[1])
    label(METAL1_LABEL, X_RIGHT / 2, (vdd_bar[0] + vdd_bar[1]) / 2, "vdd")
    label(METAL1_LABEL, X_RIGHT / 2, (vvdd_bar[0] + vvdd_bar[1]) / 2, "vvdd")

    # Pads: contacts and a Metal1 stripe each. Even pads are sources (up to vdd),
    # odd pads are drains (down to vvdd).
    ys = contact_ys()
    for i in range(N_PADS):
        px0, _ = pad_x(i)
        for y in ys:
            rect(CONTACT, px0 + CONTACT_EDGE, y, px0 + CONTACT_EDGE + CONTACT_SIZE, y + CONTACT_SIZE)
        sx0 = px0 + M1_STRIPE_INSET
        sx1 = sx0 + M1_STRIPE_W
        if i % 2 == 0:
            rect(METAL1, sx0, Y0 + 0.10, sx1, vdd_bar[0])
        else:
            rect(METAL1, sx0, vvdd_bar[1], sx1, Y1 - 0.10)

    # Gate contact and Metal1 pad (sleep) at the left end of the poly bus.
    cy0 = (GATE_BUS_Y[0] + GATE_BUS_Y[1]) / 2 - CONTACT_SIZE / 2
    rect(CONTACT, bus_x0 + 0.20, cy0, bus_x0 + 0.20 + CONTACT_SIZE, cy0 + CONTACT_SIZE)
    rect(METAL1, bus_x0 + 0.10, cy0 - 0.09, bus_x0 + 0.62, cy0 + CONTACT_SIZE + 0.09)
    label(METAL1_LABEL, bus_x0 + 0.36, cy0 + CONTACT_SIZE / 2, "sleep")

    return rects, labels


def gds_path() -> str:
    return gds_file(CELL_DIR, TOP_CELL)


def build(path: str | None = None) -> bytes:
    rects, labels = build_shapes()
    return write_gds(
        path or gds_path(),
        library_name=TOP_CELL,
        structures=[(TOP_CELL, rects, labels)],
    )


check = make_check(
    gds_path=gds_path, build=build, script="layout/cells/power_switch/build.py"
)
main = make_main(
    check=check,
    gds_path=gds_path,
    build=build,
    description=__doc__.splitlines()[0],
)


if __name__ == "__main__":
    raise SystemExit(main())
