#!/usr/bin/env python3
"""Standard-cell area estimate for the conditioner, from the PDK's own LEF.

The number quoted in
``spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md`` is
produced by this script, so it can be re-derived rather than trusted::

    python3 design/conditioner/area_estimate.py

What this is
------------
A **gate-level inventory** of ``crc32_conditioner.v`` mapped onto real
``gf180mcu_fd_sc_mcu7t5v0`` cells, with each cell's area read out of the
library LEF that ships with the installed PDK. It is an estimate with a
stated method, not a synthesis result: no synthesiser, floorplan or router
has been run on this block (yosys is not part of this repo's toolchain
today). The inventory is what a synthesiser would have to produce *at
minimum* for this RTL; a real run will differ in buffering, drive strengths
and the exact counter/decode implementation.

Why the 7-track 5 V library: gf180mcu ships ``mcu7t5v0`` (denser) and
``mcu9t5v0``. The 7-track library is characterised at, among others,
``ss_125C_3v00`` and ``ff_n40C_3v60`` -- which are exactly DR-0003's
rate-binding corner and the README Power row's corner inside the ratified
3.3 V +/- 10 % envelope.

Placement utilisation is a *range*, not a number: a small standalone digital
block placed alongside analog typically lands between 60 % and 80 %. Both
ends are printed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "sim"))

from harness import pdk as pdk_mod  # noqa: E402

STDCELL_LIB = "gf180mcu_fd_sc_mcu7t5v0"

#: The README `Area` row, in um^2. This block is one contributor to it.
AREA_BUDGET_UM2 = 0.05 * 1e6

#: Gate-level inventory of design/conditioner/crc32_conditioner.v.
#: (section, {cell suffix: count}, note)
INVENTORY = [
    (
        "LFSR state register",
        {"dffrnq_1": 32},
        "32-bit state, async power-on reset; flush is synchronous",
    ),
    (
        "LFSR feedback network",
        {"xor2_1": 14},
        "13 polynomial taps (bit 31 needs none -- the shifted-in bit is 0) "
        "+ 1 for fb = state[0] ^ raw_bit",
    ),
    ("block counter", {"dffrnq_1": 8}, "counts 0..255 raw samples per block (K = 8)"),
    (
        "block counter increment",
        {"xor2_1": 7, "and2_1": 7},
        "ripple-carry increment across bits 1..7",
    ),
    (
        "terminal-count decode",
        {"nand2_1": 5, "nor2_1": 2, "inv_1": 1},
        "8-input AND as a NAND/NOR tree",
    ),
    (
        "clock-enable gate",
        {"icgtp_1": 1},
        "integrated clock gate on (raw_valid & en) | flush",
    ),
    (
        "flush / enable control",
        {"and2_1": 2, "nor2_1": 2, "inv_1": 1},
        "flush-wins-over-absorb priority and the gated-hold term",
    ),
    ("cond_valid output strobe", {"dffrnq_1": 1}, "one-cycle valid pulse to the #26 FIFO"),
]

#: Same block with the enable realised as per-flop feedback muxes instead of a
#: clock gate -- the pessimistic bound if clock gating is disallowed.
MUX_FEEDBACK_DELTA = {"icgtp_1": -1, "mux2_1": 41}

#: Literature range for a compact serialised AES-128 core, in gate equivalents.
#: LITERATURE VALUE, UNCONFIRMED -- no synthesis of any AES core has been run in
#: this repository. Quoted only to size the vetted-conditioner alternative that
#: DR-0004 left open, at order-of-magnitude accuracy.
AES128_GE_RANGE = (2400, 3400)


def load_cell_areas(lef_path: Path) -> dict[str, float]:
    text = lef_path.read_text()
    areas: dict[str, float] = {}
    for match in re.finditer(r"^MACRO (\S+)(.*?)^END \1", text, re.M | re.S):
        name, body = match.group(1), match.group(2)
        size = re.search(r"SIZE\s+([\d.]+)\s+BY\s+([\d.]+)", body)
        if size:
            areas[name] = float(size.group(1)) * float(size.group(2))
    return areas


def _area(areas: dict[str, float], suffix: str) -> float:
    key = f"{STDCELL_LIB}__{suffix}"
    if key not in areas:
        raise KeyError(f"{key} not found in the LEF")
    return areas[key]


def report(areas: dict[str, float], provenance: dict) -> int:
    ge = _area(areas, "nand2_1")
    print(f"PDK      : {provenance['path']}")
    print(f"           {provenance['variant']} @ open_pdks {provenance['open_pdks_version']}")
    print(f"           discovered via {provenance['discovered_via']}")
    print(f"library  : {STDCELL_LIB}")
    print(f"1 GE     : {ge:.4f} um^2 (nand2_1, {STDCELL_LIB})")
    print()
    print(f"| {'Section':<30} | {'Cells':<40} | {'Area (um^2)':>11} |")
    print(f"|{'-' * 32}|{'-' * 42}|{'-' * 13}|")

    total = 0.0
    for section, cells, _note in INVENTORY:
        area = sum(_area(areas, c) * n for c, n in cells.items())
        total += area
        listing = " + ".join(f"{n} x {c}" for c, n in sorted(cells.items()))
        print(f"| {section:<30} | {listing:<40} | {area:>11.1f} |")
    print(f"|{'-' * 32}|{'-' * 42}|{'-' * 13}|")
    print(f"| {'TOTAL cell area':<30} | {f'{total / ge:.0f} GE':<40} | {total:>11.1f} |")
    print()

    for util in (0.60, 0.80):
        placed = total / util
        print(
            f"at {util:.0%} placement utilisation: {placed:>8.0f} um^2 "
            f"= {placed / 1e6:.5f} mm^2 = {placed / AREA_BUDGET_UM2:.1%} of the "
            f"< 0.05 mm^2 budget"
        )

    mux_total = total + sum(_area(areas, c) * n for c, n in MUX_FEEDBACK_DELTA.items())
    print()
    print(
        f"mux-feedback enable variant (no clock gating): {mux_total:.1f} um^2 cell "
        f"= {mux_total / ge:.0f} GE; {mux_total / 0.60 / 1e6:.5f} mm^2 at 60 % util "
        f"({mux_total / 0.60 / AREA_BUDGET_UM2:.1%} of budget)"
    )

    lo, hi = AES128_GE_RANGE
    print()
    print("For comparison -- a *vetted* conditioning function (AES-CMAC) needs an")
    print("AES core. LITERATURE VALUE, UNCONFIRMED (no AES synthesis run here):")
    for gates in (lo, hi):
        cell = gates * ge
        print(
            f"  compact serialised AES-128, {gates} GE: {cell:.0f} um^2 cell area "
            f"-> {cell / 0.60 / 1e6:.4f} mm^2 at 60 % util "
            f"({cell / 0.60 / AREA_BUDGET_UM2:.0%} of the whole block budget)"
        )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lef", type=Path, help="override the LEF path (skips PDK discovery)")
    args = parser.parse_args(argv)

    if args.lef:
        lef = args.lef
        provenance = {
            "path": str(lef),
            "variant": "n/a (--lef override)",
            "open_pdks_version": "n/a (--lef override)",
            "discovered_via": "--lef",
        }
    else:
        try:
            found = pdk_mod.find_pdk()
        except pdk_mod.PdkNotFound as exc:
            print(f"gf180mcu PDK not found: {exc}", file=sys.stderr)
            print("Install it (see README) or pass --lef <path>.", file=sys.stderr)
            return 2
        lef = found.path / "libs.ref" / STDCELL_LIB / "lef" / f"{STDCELL_LIB}.lef"
        provenance = found.provenance()

    if not lef.is_file():
        print(f"standard-cell LEF not found at {lef}", file=sys.stderr)
        return 2
    return report(load_cell_areas(lef), provenance)


if __name__ == "__main__":
    raise SystemExit(main())
