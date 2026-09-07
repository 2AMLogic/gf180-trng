#!/usr/bin/env python3
"""Compose parasitic-annotated (`klt extract --parasitics`) leaf-cell
netlists into post-layout drop-in replacements for `design/ro_array_core.spice`
and `design/sampler_core.spice`, for issue #17 (post-layout extracted re-run
of the verification suite).

    python3 layout/pex/build.py            # extract + compose, write files
    python3 layout/pex/build.py --check    # rebuild to scratch, compare bytes

## Why leaf cells, not the assembled `ro_ring11`/`combiner_sampler` GDS

The physically assembled, DRC-clean, LVS-matching rings and combiner/sampler
block (`layout/rings/`, `layout/blocks/`, issue #106/#110/#135) are the more
complete post-layout artefact in principle -- they carry real inter-cell
(stage-to-stage) wiring parasitics that this composition does not. They are
not used here because `klt extract`'s flat extraction gives every net a name
derived from the touching cell pins it merges (issue klayout-tools#N, filed
alongside this change): `ro_ring11`'s ten *genuinely internal* inter-stage
nodes and its *one* true external `ro` boundary pin are extraction-flattened
into eleven **identically-named** `a|y`/`a|y$1`/.../`a|y$10` header entries,
and neither the extracted netlist's own header nor `klt lvs`'s
`net_correspondence[]` (which reports the pin-name correspondence sorted by
*reference* net name, not by extracted header position) discloses which
position is the true `ro` port. Composing a new top-level netlist that wires
one specific position out to the rest of the design requires knowing that
correspondence positionally, which is not recoverable from any documented,
stable `klt` output today. Filed as a generic tool gap; see this module's own
`FRICTION_ISSUE` constant below and `sim/characterization-post-layout-extracted.md`
for the full account.

Every **leaf** cell this repo has drawn (`ro_stage`, `ro_stage_ring2`,
`ro_nand2`, `ro_nand2_ring2`, `ro_buf`, `xor2`, `sampler_dff`) has no such
ambiguity: each is a small, single-purpose cell whose declared ports (`a`,
`en`, `vddr`/`vdd`, `vss`, `y`, ...) are the *only* named nets `klt extract`
finds, so every extracted `.SUBCKT` header names its ports uniquely and
unambiguously, one-for-one with `design/netlist.py`'s own schematic ports for
that same cell. This module extracts each of those seven leaf GDS streams
with `--parasitics --pdk gf180mcuD` (binding the generic `nfet`/`pfet` device
class onto the real `nfet_03v3`/`pfet_03v3` PDK subcircuits `design/
netlist.py`'s own schematics already instantiate), then hand-composes them
into `ro_array_core_extracted`/`sampler_core_extracted` using *exactly* the
same instance-level topology `design/ro_array_core.spice`/`design/
sampler_core.spice` declare (transcribed from those generated files, not
re-derived) -- so what changes between the schematic and this extracted
netlist is *only* each leaf cell's own drawn-layout parasitics (device
junction geometry as actually drawn, plus that cell's own internal routing),
not the ring/combiner-level topology, which is identical to the schematic on
both sides.

## What this does and does not capture

**Captured**: every drawn leaf cell's own device geometry (as extracted from
its real layout, not the schematic's idealised `W`/`L`/`AS`/`AD`/`PS`/`PD`)
plus that cell's own internal metal parasitics (its `--parasitics` R/C).

**Not captured** (disclosed here, and again in every evidence record this
composition backs): the *inter-cell* wiring inside each already-assembled
ring/block (`layout/rings/README.md`'s hand-routed metal1 stage-to-stage
chain and metal2/via1 `vddr`/`vss` straps, `layout/blocks/README.md`'s
combiner/sampler row wiring) and any inter-region routing at all (the
`layout/floorplan/` guarded regions are placed with a 20 µm isolation
channel and no signal routing between them -- confirmed empirically: `klt
extract --top trng_floorplan` on the composed floorplan GDS reports 2588
top-level pins for what should be a ~12-pin block, i.e. the regions are not
electrically joined in the committed layout at all). This composition is
therefore a **device-level, not a routing-level, post-layout re-run**: a
real but partial capture of "extraction changes RO frequencies, adds
coupling paths, and loads the sampler" (issue #17's own framing), not the
full-chip parasitic re-run that framing evokes. See
`sim/characterization-post-layout-extracted.md` for the honest accounting of
what this changes and what it cannot yet show.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from layout._klt import FlowError, _run_klt, resolve_pdk  # noqa: E402

PEX_DIR = REPO_ROOT / "layout" / "pex"
WORK_DIR = REPO_ROOT / "layout" / ".work" / "pex-check"
DECK = "gf180mcu"

# Filed against 2AMLogic/klayout-tools per this repo's CLAUDE.md friction
# protocol (issue #17's own re-run could not use the assembled ro_ring11/
# combiner_sampler GDS because of this gap -- see module docstring).
FRICTION_ISSUE = "https://github.com/2AMLogic/klayout-tools/issues/1540"

#: (output stem, gds path, top cell name) for every leaf cell this
#: composition needs. `wstv`/`lstv` differences between ring1 and ring2 are
#: already baked into the *drawn* geometry of the `_ring2` cells -- nothing
#: here is parameterised the way the schematic's `.subckt ... wstv=... ` is.
LEAF_CELLS = [
    ("ro_stage", "layout/cells/ro_stage/ro_stage.gds", "ro_stage"),
    ("ro_stage_ring2", "layout/cells/ro_stage_ring2/ro_stage_ring2.gds", "ro_stage_ring2"),
    ("ro_nand2", "layout/cells/ro_nand2/ro_nand2.gds", "ro_nand2"),
    ("ro_nand2_ring2", "layout/cells/ro_nand2_ring2/ro_nand2_ring2.gds", "ro_nand2_ring2"),
    ("ro_buf", "layout/cells/ro_buf/ro_buf.gds", "ro_buf"),
    ("xor2", "layout/cells/xor2/xor2.gds", "xor2"),
    ("sampler_dff", "layout/cells/sampler_dff/sampler_dff.gds", "sampler_dff"),
]

PDK_VARIANT = "gf180mcuD"


def extract_leaf(name: str, gds: str, top: str, outdir: Path) -> dict:
    out_path = outdir / f"{name}.extracted.spice"
    args = [
        "extract",
        gds,
        "--deck",
        DECK,
        "--top",
        top,
        "--parasitics",
        "--pdk",
        PDK_VARIANT,
        "-o",
        str(out_path.relative_to(REPO_ROOT)),
    ]
    return _run_klt(args)


def _ring_subckt(name: str, nand_cell: str, stage_cell: str) -> str:
    """`ro_ring11`/`ro_ring11_ring2`'s own topology (design/ro_array_core.spice),
    transcribed with each leaf's own extracted pin order:

        ro_nand2:  a en vddr vss vsubs y
        ro_stage:  a    vddr vss vsubs y
    """
    lines = [f".subckt {name} en ro vddr vss vsubs"]
    lines.append(f"xg ro en vddr vss vsubs n1 {nand_cell}")
    for i in range(1, 10):
        lines.append(f"x{i} n{i} vddr vss vsubs n{i + 1} {stage_cell}")
    lines.append(f"x10 n10 vddr vss vsubs ro {stage_cell}")
    lines.append(".ends")
    return "\n".join(lines) + "\n"


def _ro_array_core_subckt() -> str:
    """`design/ro_array_core.spice`'s own topology, with each leaf's own
    extracted pin order (`ro_buf`: a vdd vss vsubs y; `xor2`: a b vdd vss
    vsubs y; rings declared above: en ro vddr vss vsubs).
    """
    lines = [".subckt ro_array_core_extracted en1 en2 vddr1 vddr2 vdd vss xo ro1 ro2 vsubs"]
    lines.append("xr1 en1 rn1 vddr1 vss vsubs ro_ring11_extracted")
    lines.append("xr2 en2 rn2 vddr2 vss vsubs ro_ring11_ring2_extracted")
    lines.append("xb1 rn1 vdd vss vsubs ro1 ro_buf")
    lines.append("xb2 rn2 vdd vss vsubs ro2 ro_buf")
    lines.append("xa1 ro1 ro2 vdd vss vsubs xo xor2")
    lines.append(".ends")
    return "\n".join(lines) + "\n"


def _sampler_core_subckt() -> str:
    """`design/sampler_core.spice`'s own topology, with `sampler_dff`'s own
    extracted pin order (clk d q rst_n vdd vss vsubs) and
    `ro_array_core_extracted`'s pin order declared above.
    """
    lines = [
        ".subckt sampler_core_extracted en1 en2 vddr1 vddr2 vdd vss "
        "clk rst_n raw_bit raw_valid ring_bit1 ring_bit2 vsubs"
    ]
    lines.append("xdut en1 en2 vddr1 vddr2 vdd vss xo ro1 ro2 vsubs ro_array_core_extracted")
    lines.append("xsb clk xo raw_bit rst_n vdd vss vsubs sampler_dff")
    lines.append("xsv clk vdd raw_valid rst_n vdd vss vsubs sampler_dff")
    lines.append("xsr1 clk ro1 ring_bit1 rst_n vdd vss vsubs sampler_dff")
    lines.append("xsr2 clk ro2 ring_bit2 rst_n vdd vss vsubs sampler_dff")
    lines.append(".ends")
    return "\n".join(lines) + "\n"


HEADER = """* GENERATED by layout/pex/build.py -- do not edit by hand.
* Post-layout, device-level-parasitic-annotated drop-in replacement for
* {source}, composed from `klt extract --parasitics --pdk {pdk}` runs
* over this design's individually drawn, DRC-clean, LVS-matching leaf
* cells (layout/cells/), using EXACTLY the instance-level topology
* {source} itself declares -- see this file's own module docstring
* (layout/pex/build.py) for what this captures and what it does not.
* Regenerate with: python3 layout/pex/build.py
"""


def build(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    for name, gds, top in LEAF_CELLS:
        extract_leaf(name, gds, top, outdir)

    ro_array_core = (
        HEADER.format(source="design/ro_array_core.spice", pdk=PDK_VARIANT)
        + '.include "ro_stage.extracted.spice"\n'
        + '.include "ro_nand2.extracted.spice"\n'
        + '.include "ro_stage_ring2.extracted.spice"\n'
        + '.include "ro_nand2_ring2.extracted.spice"\n'
        + '.include "ro_buf.extracted.spice"\n'
        + '.include "xor2.extracted.spice"\n'
        + "\n"
        + _ring_subckt("ro_ring11_extracted", "ro_nand2", "ro_stage")
        + "\n"
        + _ring_subckt("ro_ring11_ring2_extracted", "ro_nand2_ring2", "ro_stage_ring2")
        + "\n"
        + _ro_array_core_subckt()
    )
    (outdir / "ro_array_core.extracted.spice").write_text(ro_array_core)

    sampler_core = (
        HEADER.format(source="design/sampler_core.spice", pdk=PDK_VARIANT)
        + '.include "ro_array_core.extracted.spice"\n'
        + '.include "sampler_dff.extracted.spice"\n'
        + "\n"
        + _sampler_core_subckt()
    )
    (outdir / "sampler_core.extracted.spice").write_text(sampler_core)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="rebuild to scratch, compare to committed output")
    parser.add_argument("--require-tools", action="store_true", help="fail instead of skipping when klt/PDK are absent")
    args = parser.parse_args(argv)

    if shutil.which("klt") is None or resolve_pdk() is None:
        msg = "klt and/or the gf180mcu PDK are not available -- skipping layout/pex/build.py"
        if args.require_tools:
            print(f"error: {msg}", file=sys.stderr)
            return 1
        print(msg)
        return 0

    target = WORK_DIR if args.check else PEX_DIR
    try:
        build(target)
    except FlowError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.check:
        failures = []
        for path in sorted(target.glob("*.spice")):
            committed = PEX_DIR / path.name
            if not committed.is_file():
                failures.append(f"missing committed file: {committed}")
                continue
            if committed.read_bytes() != path.read_bytes():
                failures.append(f"stale: {committed} does not match a fresh rebuild")
        shutil.rmtree(WORK_DIR, ignore_errors=True)
        if failures:
            for f in failures:
                print(f"FAIL {f}", file=sys.stderr)
            return 1
        print("OK: layout/pex/*.spice matches a fresh rebuild")
        return 0

    print(f"wrote {len(list(PEX_DIR.glob('*.spice')))} files under {PEX_DIR.relative_to(REPO_ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
