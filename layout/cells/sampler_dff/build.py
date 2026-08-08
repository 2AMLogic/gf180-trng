#!/usr/bin/env python3
"""Draw and check `sampler_dff`, the sampler's transmission-gate DFF.

    python3 layout/cells/sampler_dff/build.py            # write sampler_dff.gds
    python3 layout/cells/sampler_dff/build.py --check     # rebuild, compare bytes

`sampler_dff` is `design/sampler_core.spice`'s `.subckt sampler_dff` (from
`design/xschem/sampler_dff.sch`): the master-slave transmission-gate D
flip-flop `sampler_core` instantiates four times unmodified (`xsb`/`xsv`/
`xsr1`/`xsr2` -- raw bit, raw-valid, and the two DR-0016 per-ring liveness
taps), with an async reset (DR-0014). One drawn cell covers all four uses;
see `layout/cells/README.md` for how this cell and `xor2` fit the
`combiner_sampler` guarded region (#16, `layout/floorplan/`).

Twenty-two devices -- the largest cell drawn under `layout/cells/` so far
(5.5x `ro_stage`'s four, 1.8x `xor2`'s twelve) -- transcribed directly from
`design/sampler_core.spice`'s own device list and sizing (every L=0.28um;
W is 0.44um throughout except the seven clock/data-path NMOS legs at
0.22um -- the same "smallest inverter the gf180mcu 3.3V core devices
allow" width `ro_stage`/`xor2` also draw):

    MPC/MNC:              clkb = NOT(clk)
    MTDP/MTDN:             master transmission gate: d -> m, gated by clk/clkb
    MIMPA/MIMPB/MIMNA/MIMNB:  master cross-coupled latch (mb = NOT(m),
                              MIMPB/MIMNB gated by rst_n -- the async set
                              that pulls mb high, forcing m/q low, DR-0014)
    MIM2P/MIM2N:           mc = NOT(mb)
    MFMP/MFMN:             master feedback transmission gate: mc -> m,
                              gated by clkb/clk (opposite phase from the
                              input gate, closing the latch while MTDP/MTDN
                              are open)
    MTSP/MTSN:             slave transmission gate: mb -> s, gated by
                              clkb/clk
    MISP/MISN:             q = NOT(s)
    MIS2PA/MIS2PB/MIS2NA/MIS2NB:  slave cross-coupled latch (qb = NOT(q),
                              MIS2PB/MIS2NB gated by rst_n -- the async
                              reset's second stage, holding q low)
    MFSP/MFSN:             slave feedback transmission gate: qb -> s,
                              gated by clk/clkb

Hand-drawn for the same reason `ro_stage`/`xor2` are (most devices below
the `klt gen mos_array` 0.42um floor, klayout-tools#322), via the shared
engine `layout/cells/_mos_row.py` documents. At this device count -- more
than either `ro_stage` or `xor2` -- a shared engine stops being a
convenience and becomes the only tractable way to hand-place a
transistor-accurate cell without a transcription slip; see `_mos_row.py`'s
own docstring for the full account of why an independent-device "gate
array" (every device its own dog-boned pads, no series-shared diffusion)
and a two-layer Manhattan routing grid (Metal2 trunks per net, Metal3
risers per terminal) generalise cleanly to this scale.
"""

from __future__ import annotations

import argparse
import os
import sys

_CELLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.abspath(_CELLS_DIR))

from _mos_row import Device, build_cell  # noqa: E402

CELL_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_CELL = "sampler_dff"
PINS = ["d", "clk", "rst_n", "q", "vdd", "vss"]

# --------------------------------------------------------------------------- #
# Device list -- transcribed directly from design/sampler_core.spice's
# `.subckt sampler_dff` (at that file's own sizing). `drain`/`source` are
# the netlist's two diffusion-terminal net names; see _mos_row.Device's own
# docstring for why which one is called which does not matter here.
# --------------------------------------------------------------------------- #
L = 0.28

NMOS = [
    Device("MNC", "n", 0.22, L, gate="clk", drain="clkb", source="vss"),
    Device("MTDN", "n", 0.22, L, gate="clkb", drain="d", source="m"),
    Device("MIM2N", "n", 0.22, L, gate="mb", drain="mc", source="vss"),
    Device("MFMN", "n", 0.22, L, gate="clk", drain="mc", source="m"),
    Device("MTSN", "n", 0.22, L, gate="clk", drain="mb", source="s"),
    Device("MISN", "n", 0.22, L, gate="s", drain="q", source="vss"),
    Device("MFSN", "n", 0.22, L, gate="clkb", drain="qb", source="s"),
    Device("MIMNA", "n", 0.44, L, gate="m", drain="mb", source="mmid"),
    Device("MIMNB", "n", 0.44, L, gate="rst_n", drain="mmid", source="vss"),
    Device("MIS2NA", "n", 0.44, L, gate="q", drain="qb", source="s2mid"),
    Device("MIS2NB", "n", 0.44, L, gate="rst_n", drain="s2mid", source="vss"),
]

PMOS = [
    Device("MPC", "p", 0.44, L, gate="clk", drain="clkb", source="vdd"),
    Device("MTDP", "p", 0.44, L, gate="clk", drain="d", source="m"),
    Device("MIMPA", "p", 0.44, L, gate="m", drain="mb", source="vdd"),
    Device("MIMPB", "p", 0.44, L, gate="rst_n", drain="mb", source="vdd"),
    Device("MIM2P", "p", 0.44, L, gate="mb", drain="mc", source="vdd"),
    Device("MFMP", "p", 0.44, L, gate="clkb", drain="mc", source="m"),
    Device("MTSP", "p", 0.44, L, gate="clkb", drain="mb", source="s"),
    Device("MISP", "p", 0.44, L, gate="s", drain="q", source="vdd"),
    Device("MIS2PA", "p", 0.44, L, gate="q", drain="qb", source="vdd"),
    Device("MIS2PB", "p", 0.44, L, gate="rst_n", drain="qb", source="vdd"),
    Device("MFSP", "p", 0.44, L, gate="clk", drain="qb", source="s"),
]


def gds_path() -> str:
    return os.path.join(CELL_DIR, f"{TOP_CELL}.gds")


def build(path: str | None = None) -> bytes:
    return build_cell(TOP_CELL, PINS, NMOS, PMOS, path or gds_path())


def check() -> int:
    path = gds_path()
    shown = os.path.relpath(path, os.getcwd())
    if not os.path.exists(path):
        print(f"MISSING: {shown} -- run `python3 layout/cells/sampler_dff/build.py`")
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
            f"run `python3 layout/cells/sampler_dff/build.py`"
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
