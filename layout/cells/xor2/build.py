#!/usr/bin/env python3
"""Draw and check `xor2`, the entropy source's combiner gate.

    python3 layout/cells/xor2/build.py            # write xor2.gds
    python3 layout/cells/xor2/build.py --check     # rebuild, compare bytes

`xor2` is `design/ro_array_core.spice`'s `.subckt xor2` (from
`design/xschem/xor2.sch`): the two-input XOR that combines ring1's and
ring2's buffered outputs into `xo`, the `combiner_sampler` guarded region's
one non-sampler cell (#16, `layout/floorplan/`; see `layout/cells/README.md`
for how this cell and `sampler_dff` fit that region).

Twelve devices, three times `ro_stage`'s four -- two inverting-input pairs
feeding an eight-transistor XOR core (`design/ro_array_core.spice`'s own
device names, at that file's own sizing):

    XMpiA/XMniA:  an = NOT(a)   (W=0.44/0.22, L=0.28 -- a plain inverter)
    XMpiB/XMniB:  bn = NOT(b)   (W=0.44/0.22, L=0.28 -- a plain inverter)
    XMp1/XMp2:    mid pulled to vdd through a or b (W=0.88 each, parallel)
    XMp3/XMp4:    y pulled to mid through an or bn (W=0.88 each, parallel)
    XMn1/XMn2:    y pulled to vss through a THEN b (W=0.44 each, series)
    XMn3/XMn4:    y pulled to vss through an THEN bn (W=0.44 each, series)

This is the standard 12T static XOR: `y` is high when exactly one of
`a`/`b` is high, driven by two independent PMOS pull-up paths (through the
inverted inputs `an`/`bn`) and two independent NMOS pull-down stacks
(through the true inputs). Every device's own L is 0.28um; W ranges from
0.22um (the input inverters' NMOS -- the "smallest inverter the gf180mcu
3.3V core devices allow", `ro_stage.build.py`'s own phrase) up to 0.88um
(the XOR core's PMOS legs) -- so, like `ro_stage`, most of this cell cannot
be drawn with `klt gen mos_array` (0.42um floor, klayout-tools#322) and is
hand-drawn instead, via the shared engine `layout/cells/_mos_row.py`
documents (see that module's own docstring for why a shared engine and not
another from-scratch `ro_stage.build.py`-style hand-placement: at 12
devices -- three times `ro_stage`'s -- re-deriving the same per-device
diffusion/contact/routing arithmetic from scratch was judged more
error-prone than factoring it out once, before `sampler_dff` needed the
same thing again at 22 devices).

Decomposing into a reused "inverter" sub-drawing (as the issue that
requested this cell considered) was not taken: `_mos_row.py`'s per-device
placement already treats every device identically regardless of role, so a
special-cased "inverter" building block would duplicate machinery this
module already provides generically, for a marginal area saving that does
not matter to a verification-only cell (see `_mos_row.py`'s own docstring,
"Topology").
"""

from __future__ import annotations

import argparse
import os
import sys

_CELLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.abspath(_CELLS_DIR))

from _mos_row import Device, build_cell  # noqa: E402

CELL_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_CELL = "xor2"
PINS = ["a", "b", "y", "vdd", "vss"]

# --------------------------------------------------------------------------- #
# Device list -- transcribed directly from design/ro_array_core.spice's
# `.subckt xor2` (at that file's own sizing). `drain`/`source` are the
# netlist's two diffusion-terminal net names; see _mos_row.Device's own
# docstring for why which one is called which does not matter here.
# --------------------------------------------------------------------------- #
L = 0.28

NMOS = [
    Device("MNIA", "n", 0.22, L, gate="a", drain="an", source="vss"),
    Device("MNIB", "n", 0.22, L, gate="b", drain="bn", source="vss"),
    Device("MN1", "n", 0.44, L, gate="a", drain="y", source="s1"),
    Device("MN2", "n", 0.44, L, gate="b", drain="s1", source="vss"),
    Device("MN3", "n", 0.44, L, gate="an", drain="y", source="s2"),
    Device("MN4", "n", 0.44, L, gate="bn", drain="s2", source="vss"),
]

PMOS = [
    Device("MPIA", "p", 0.44, L, gate="a", drain="an", source="vdd"),
    Device("MPIB", "p", 0.44, L, gate="b", drain="bn", source="vdd"),
    Device("MP1", "p", 0.88, L, gate="a", drain="mid", source="vdd"),
    Device("MP2", "p", 0.88, L, gate="b", drain="mid", source="vdd"),
    Device("MP3", "p", 0.88, L, gate="an", drain="y", source="mid"),
    Device("MP4", "p", 0.88, L, gate="bn", drain="y", source="mid"),
]


def gds_path() -> str:
    return os.path.join(CELL_DIR, f"{TOP_CELL}.gds")


def build(path: str | None = None) -> bytes:
    return build_cell(TOP_CELL, PINS, NMOS, PMOS, path or gds_path())


def check() -> int:
    path = gds_path()
    shown = os.path.relpath(path, os.getcwd())
    if not os.path.exists(path):
        print(f"MISSING: {shown} -- run `python3 layout/cells/xor2/build.py`")
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
            f"run `python3 layout/cells/xor2/build.py`"
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
