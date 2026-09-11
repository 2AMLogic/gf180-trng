#!/usr/bin/env python3
"""Compose parasitic-annotated (`klt extract --parasitics`) netlists into
post-layout drop-in replacements for `design/ro_array_core.spice` and
`design/sampler_core.spice`, for issue #17 (device-level post-layout
re-run) and issue #217 (routing-level post-layout re-run, on top of #17).

    python3 layout/pex/build.py            # extract + compose, write files
    python3 layout/pex/build.py --check    # rebuild to scratch, compare bytes

This module now runs two independent composition paths, both written by the
same `build()` call and both covered by the same `--check`:

1. **Leaf-cell (device-level)**, issue #17 -- `ro_array_core.extracted.spice`
   / `sampler_core.extracted.spice`. See "Why leaf cells" below; unchanged
   by issue #217.
2. **Assembled-block (routing-level)**, issue #217 --
   `ro_array_core.routed.extracted.spice` / `sampler_core.routed.extracted.spice`.
   See "Routing-level composition" below.

## Why leaf cells, not the assembled `ro_ring11`/`combiner_sampler` GDS -- for path 1

The physically assembled, DRC-clean, LVS-matching rings and combiner/sampler
block (`layout/rings/`, `layout/blocks/`, issue #106/#110/#135) are the more
complete post-layout artefact in principle -- they carry real inter-cell
(stage-to-stage) wiring parasitics that this composition does not. Path 1
does not use them because, historically, `klt extract`'s flat extraction
gave every net a name derived from the touching cell pins it merges (issue
klayout-tools#1540): `ro_ring11`'s ten *genuinely internal* inter-stage
nodes and its *one* true external `ro` boundary pin were extraction-
flattened into eleven **identically-named** `a|y` header entries, with no
way to tell which position was the port. klayout-tools#1540 closed
2026-09-07T01:16Z via merged klayout-tools#1543 (commit
`3fbb4478e3017c8d8580fba4feb08bc386b4c925`): `nets[]` now carries `net_id`
(per-net cluster id), `pin_index` (the net's 0-based `.SUBCKT`/instance-line
port position) and `label_positions_um` (every drawn label naming the net,
in the top cell's own coordinates) -- exactly the positional correspondence
this module's docstring used to say was unrecoverable. That is what path 2,
below, uses. Path 1 is kept unchanged (not re-derived from path 2) because
it backs existing #17 evidence records and remains a useful, narrower
capture on its own -- see "What this does and does not capture" below.

Every **leaf** cell this repo has drawn (`ro_stage`, `ro_stage_ring2`,
`ro_nand2`, `ro_nand2_ring2`, `ro_buf`, `xor2`, `sampler_dff`) has no naming
ambiguity at all: each is a small, single-purpose cell whose declared ports
(`a`, `en`, `vddr`/`vdd`, `vss`, `y`, ...) are the *only* named nets `klt
extract` finds, so every extracted `.SUBCKT` header names its ports
uniquely and unambiguously, one-for-one with `design/netlist.py`'s own
schematic ports for that same cell. This module extracts each of those
seven leaf GDS streams with `--parasitics --pdk gf180mcuD` (binding the
generic `nfet`/`pfet` device class onto the real `nfet_03v3`/`pfet_03v3`
PDK subcircuits `design/netlist.py`'s own schematics already instantiate),
then hand-composes them into `ro_array_core_extracted`/`sampler_core_extracted`
using *exactly* the same instance-level topology `design/ro_array_core.spice`/
`design/sampler_core.spice` declare (transcribed from those generated
files, not re-derived) -- so what changes between the schematic and this
extracted netlist is *only* each leaf cell's own drawn-layout parasitics
(device junction geometry as actually drawn, plus that cell's own internal
routing), not the ring/combiner-level topology, which is identical to the
schematic on both sides.

## What path 1 does and does not capture

**Captured**: every drawn leaf cell's own device geometry (as extracted from
its real layout, not the schematic's idealised `W`/`L`/`AS`/`AD`/`PS`/`PD`)
plus that cell's own internal metal parasitics (its `--parasitics` R/C).

**Not captured**: the *inter-cell* wiring inside each already-assembled
ring/block (`layout/rings/README.md`'s hand-routed metal1 stage-to-stage
chain and metal2/via1 `vddr`/`vss` straps, `layout/blocks/README.md`'s
combiner/sampler row wiring) and any inter-region routing at all (see
"Out of scope" below, unchanged by issue #217).

## Routing-level composition (issue #217) -- how each true external port
   was positively identified

`klt extract --parasitics --pdk gf180mcuD` run directly on the assembled
`layout/rings/ro_ring11/ro_ring11.gds`, `layout/rings/ro_ring11_ring2/
ro_ring11_ring2.gds` and `layout/blocks/combiner_sampler/combiner_sampler.gds`
still reports the same flat, collided net names path 1's docstring always
described (`ro_ring11`'s eleven `a|y`-named ports; `combiner_sampler`'s two
`a`-named and four `q`-named ports -- see below) -- collision is inherent
to flat extraction over repeated leaf-cell instances, not a defect
klayout-tools#1543 removes. What #1543 adds is the *positional disclosure*
that makes the collision resolvable from outside the tool: each collided
`nets[]` entry now carries its own `pin_index` (that net's port position in
the `.SUBCKT` header) and `label_positions_um` (every drawn pin-label text
and its own absolute (x_um, y_um) in the top cell's coordinate frame,
copied through from whichever leaf-cell instance(s) that merged net
touches).

This module resolves each assembled block's true external ports by
*independently recomputing the expected absolute label position* of that
port from the block's own `build.py` (`layout/rings/ro_ring11/build.py`'s
`ROW_ORDER`/`row_offsets()`/`_bboxes_and_locals()`,
`layout/blocks/combiner_sampler/build.py`'s `ROW_ORDER`/`row_offsets()`),
combined with that leaf cell's own already-extracted, *unambiguous* local
pin-label position (from this same module's own leaf-cell extraction,
path 1 above) -- then matching that expected `(x_um, y_um)` against the
assembled extraction's own `label_positions_um`, within `_POS_TOL_UM`
(0.02 um, comfortably tighter than any drawn geometry step in this design).
A position that matches exactly one collided candidate is a positive
identification, cross-checked against this repository's own placement code
(not merely against the extractor's own self-consistency); zero or more
than one match raises `FlowError` rather than guessing -- see "If
disambiguation still fails" below.

- **`ro_ring11`/`ro_ring11_ring2`** (`_resolve_ring_ports`): eleven nets
  share the flat name `a|y` (ten genuinely internal inter-stage nodes plus
  the one true external `ro` boundary net, `ro_ring11/build.py`'s own
  module docstring). The `ro` net is the *wrap* link (`x10.y -> xg.a`,
  closing the ring) -- structurally distinct from the other ten
  (`xg.y -> x1.a`, `x1.y -> x2.a`, ...) in that its `a`-labelled endpoint
  belongs to the row's *first* placed block (`xg`, offset 0) while its
  `y`-labelled endpoint belongs to the row's *last* (`x10`, the row's
  largest offset) -- every other collided net's two labels sit at
  *adjacent* row positions instead. This module computes both expected
  absolute positions (`xg`'s own `a` pin, `x10`'s own `y` pin, each the
  corresponding leaf cell's already-extracted unambiguous local label
  position plus that block's own `row_offsets()` X offset) and matches
  them positionally -- it does not rely on the "wrap link" structural
  argument alone, though the two agree. `en`, `vddr`, `vss`, `vsubs` are
  each already uniquely named (only one physical net carries that name in
  this block) and need no positional resolution.
- **`combiner_sampler`** (`_resolve_combiner_sampler_ports`): two nets
  share the flat name `a` (`xb1`'s and `xb2`'s own `ro_buf` input pin --
  this block's `rn1`/`rn2`), and four share `q` (`xsb`/`xsv`/`xsr1`/`xsr2`'s
  own `sampler_dff` output pin -- this block's `raw_bit`/`raw_valid`/
  `ring_bit1`/`ring_bit2`). Each is resolved the same way: that instance's
  own row offset (`combiner_sampler/build.py`'s `ROW_ORDER`/`row_offsets()`)
  plus the leaf cell's (`ro_buf`'s `a`, `sampler_dff`'s `q`) already-
  extracted unambiguous local label position. `clk`, `rst_n`, `vss`,
  `vsubs` are each already uniquely named; `vdd` is uniquely named `d|vdd`
  (merged with `xsv`'s own `d` pin, tied straight to `vdd` by the schematic
  -- `combiner_sampler/build.py`'s own `INSTANCE_NETS["xsv"]`). `ro1`,
  `ro2`, `xo` (each a genuine 2-3-terminal internal net inside this block)
  are never resolved to an external name -- see "Two composed drop-ins,
  different scope" below for why `sampler_core.routed.extracted.spice`
  never needs them exposed.

Every other collided-but-unresolved port position (the ten non-`ro`
`ro_ring11` nodes; `combiner_sampler`'s `ro1`/`ro2`/`xo`) is wired to an
arbitrary, locally-unique node name (`n1`..`n10`, `c1`..`c3`) inside a thin
per-block wrapper `.subckt` (`_ring_routed_subckt`/
`_combiner_sampler_routed_subckt`) -- SPICE subcircuit instantiation scopes
those names to that one instance automatically, so two ring instances (or
two chip copies) never collide even though both wrappers reuse `n1..n10`.
The wrapper's own *exposed* ports are exactly the block's true I/O
(`en ro vddr vss vsubs` for a ring; `rn1 rn2 vdd vss clk rst_n raw_bit
raw_valid ring_bit1 ring_bit2 vsubs` for `combiner_sampler`) -- everything
downstream (`ro_array_core.routed.extracted.spice`, `sampler_core.
routed.extracted.spice`) instantiates the wrapper, never the raw `klt
extract` output directly, and is unaffected by whatever arbitrary names the
wrapper chose for its own private nodes.

### Two composed drop-ins, different scope

`ro_array_core`'s own schematic boundary (`design/ro_array_core.spice`)
exposes `xo`/`ro1`/`ro2` (the combiner's buffered outputs), which are
genuine internal nets of the *physical* `combiner_sampler` block -- the
schematic's own module split (ring array vs combiner+samplers) does not
line up with this repository's *floorplan* split (rings are their own
guarded regions; buffer+combiner+all four samplers are one physical region,
`layout/blocks/combiner_sampler/build.py`'s own docstring, "Originally...
this block assembled only the combiner and the four samplers... Issue #151
closes that gap: both buffers are now placed and wired inside this same
block"). There is therefore no assembled GDS boundary that exposes
`xo`/`ro1`/`ro2` *without* also physically carrying the four samplers'
wiring -- so:

- **`ro_array_core.routed.extracted.spice`** keeps the buffer/XOR stage at
  **leaf level** (`ro_buf.extracted.spice`/`xor2.extracted.spice`, path 1's
  own leaf extractions), on top of the two **routing-level** ring wrappers.
  A genuine, disclosed mix: ring-internal wiring (the dominant new physics
  for #13's RO-frequency-spread methodology) is routing-level; the
  buffer/XOR stage is not, because no assembled GDS gives it a clean
  boundary independent of the four samplers.
- **`sampler_core.routed.extracted.spice`** uses the **fully assembled**
  `combiner_sampler` extraction (buffer, XOR and all four samplers,
  together, exactly as physically wired) on top of the same two
  routing-level ring wrappers, going straight from each ring's own `ro`
  port to `combiner_sampler_routed_extracted`'s `rn1`/`rn2` input (the
  schematic's own name for that same node, `design/ro_array_core.spice`'s
  `xr1 en1 rn1 vddr1 vss ro_ring11 ...`) -- it does **not** reuse
  `ro_array_core.routed.extracted.spice`'s own buffer/XOR instances, to
  avoid instantiating the samplers' real gate-load fan-out on `ro1`/`ro2`/
  `xo` twice under two different (leaf vs routed) buffer models. This is
  the more complete of the two files: every device between `en1`/`en2` and
  `raw_bit`/`raw_valid`/`ring_bit1`/`ring_bit2` is routing-level.

One consequence worth stating plainly: because `combiner_sampler`'s own
`ro1`/`ro2`/`xo` nets, in the real assembled floorplan, already carry the
four samplers' own gate-load fan-out (they are the literal same physical
wire), `sampler_core.routed.extracted.spice` includes that loading on the
ring-facing side of the buffer stage for the first time in this
repository's post-layout evidence -- path 1's leaf-composed
`sampler_core_extracted` does not, since its leaf `ro_buf`/`xor2`/
`sampler_dff` extractions are each standalone and carry no fan-out beyond
their own declared ports.

### If disambiguation still fails

`_match_positional`/`_unique_pin_index` raise `FlowError` (not a silent
fallback to path 1) on zero or more than one match. That would mean either
this repository's own drawn geometry moved out from under the coordinates
this module computes (a bug here, not a tool gap -- `klt drc`/`klt lvs` on
the affected block's own `build.py` is the first thing to check), or a
genuinely new `klt extract` positional-disclosure gap. Per this repo's own
friction protocol (root `CLAUDE.md`), the latter is filed generically at
`2AMLogic/klayout-tools` (describing the tool gap, not this design) and the
residual is recorded rather than silently composing from path 1 instead --
see `sim/characterization-post-layout-extracted.md`'s 2026-09-11 delta
section for the one instance of this that this issue's own work found (the
per-stage noise-injection incompatibility affecting
`sampler-array-digitize-extracted`'s own routed re-run -- not a port-naming
ambiguity `klt extract` could resolve either way, since a flat extraction
never preserved a "this device belongs to stage N" tag `klt extract` could
disclose positionally; recorded as a residual, not attempted, with its own
generic gap filed).

## Out of scope (routing-level, same as path 1)

Any inter-*region* routing: the `layout/floorplan/` guarded regions are
placed with a 20 um isolation channel and no signal routing between them --
confirmed empirically, `klt extract --top trng_floorplan` on the composed
floorplan GDS reports 2588 top-level pins for what should be a ~12-pin
block, i.e. the regions are not electrically joined in the committed layout
at all. Both paths here are therefore *intra*-region (device-level or
routing-level) post-layout re-runs, never a full-chip one -- see
`sim/characterization-post-layout-extracted.md` for the honest accounting
of what each path changes and what it cannot yet show.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from layout._klt import FlowError, _run_klt, resolve_pdk  # noqa: E402
import layout.blocks.combiner_sampler.build as _cs_mod  # noqa: E402
import layout.rings.ro_ring11.build as _ring1_mod  # noqa: E402
import layout.rings.ro_ring11_ring2.build as _ring2_mod  # noqa: E402

PEX_DIR = REPO_ROOT / "layout" / "pex"
WORK_DIR = REPO_ROOT / "layout" / ".work" / "pex-check"
DECK = "gf180mcu"

# Filed against 2AMLogic/klayout-tools per this repo's CLAUDE.md friction
# protocol. #1540 (the original leaf-only-composition blocker) closed
# 2026-09-07 via merged klayout-tools#1543 (commit
# 3fbb4478e3017c8d8580fba4feb08bc386b4c925) -- see this module's own
# docstring, "Routing-level composition". Kept as a historical pointer, not
# a live blocker: if `_match_positional`/`_unique_pin_index` raise below, it
# means a *new* gap, to be filed fresh (see the docstring's "If
# disambiguation still fails").
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

#: (output stem, gds path, top cell name, ring build module) for each
#: assembled ring this composition's routing-level path extracts directly.
ASSEMBLED_RINGS = [
    ("ro_ring11", "layout/rings/ro_ring11/ro_ring11.gds", "ro_ring11",
     _ring1_mod, "ro_nand2", "ro_stage"),
    ("ro_ring11_ring2", "layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds", "ro_ring11_ring2",
     _ring2_mod, "ro_nand2_ring2", "ro_stage_ring2"),
]

COMBINER_SAMPLER_GDS = "layout/blocks/combiner_sampler/combiner_sampler.gds"
COMBINER_SAMPLER_TOP = "combiner_sampler"

PDK_VARIANT = "gf180mcuD"

#: Tolerance (um) for matching a recomputed expected label position against
#: `klt extract`'s own reported `label_positions_um` -- see the module
#: docstring, "Routing-level composition". Comfortably tighter than any
#: drawn geometry step in this design (the coarsest grid used anywhere here
#: is 0.01 um, `layout/README.md`'s own dbu).
_POS_TOL_UM = 0.02


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


def extract_assembled(name: str, gds: str, top: str, outdir: Path) -> dict:
    """Like `extract_leaf`, but for an *assembled* block (issue #217) --
    output filename carries `.routed.extracted.spice` so it never globs
    together with a leaf `.extracted.spice` (post-layout doc's own
    prefix-collision caveat). Returns `klt extract`'s full JSON payload
    (not just the netlist path) so callers can resolve ports from
    `nets[]`."""
    out_path = outdir / f"{name}.routed.extracted.spice"
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

ROUTED_HEADER = """* GENERATED by layout/pex/build.py -- do not edit by hand.
* Post-layout, ROUTING-level-parasitic-annotated drop-in replacement for
* {source}, composed from `klt extract --parasitics --pdk {pdk}` runs
* over this design's assembled, DRC-clean, LVS-matching rings/blocks
* (layout/rings/, layout/blocks/), with true external ports positively
* identified from `nets[].pin_index`/`net_id`/`label_positions_um`
* (klayout-tools#1543) -- see this file's own module docstring
* (layout/pex/build.py, "Routing-level composition") for exactly how each
* port was identified and what this does and does not capture.
* Regenerate with: python3 layout/pex/build.py
"""


# --------------------------------------------------------------------------- #
# Routing-level port resolution (issue #217)
# --------------------------------------------------------------------------- #


def _nets_by_name(payload: dict) -> dict[str, list[dict]]:
    """Group `payload["nets"]` (a `klt extract` response) by flat name,
    dropping any entry with no `pin_index` (not a promoted `.SUBCKT` port --
    see klayout-tools#1543's own schema addition)."""
    groups: dict[str, list[dict]] = {}
    for net in payload["nets"]:
        if net.get("pin_index") is None:
            continue
        groups.setdefault(net["name"], []).append(net)
    return groups


def _leaf_local_pos(payload: dict, pin_name: str) -> tuple[float, float]:
    """Return a leaf cell's own local (x_um, y_um) for a named, unambiguous
    pin, from that leaf's own (already-run) `klt extract` payload -- see
    the module docstring, "Routing-level composition"."""
    for net in payload["nets"]:
        if net["name"] == pin_name:
            labels = net.get("label_positions_um") or []
            if len(labels) != 1:
                raise FlowError(
                    f"leaf pin {pin_name!r} expected exactly one drawn label, "
                    f"found {len(labels)} -- cannot use it as a positional "
                    f"anchor for routing-level port resolution"
                )
            return (labels[0]["x_um"], labels[0]["y_um"])
    raise FlowError(f"leaf pin {pin_name!r} not found in this extraction's own nets[]")


def _unique_pin_index(groups: dict[str, list[dict]], name: str) -> int:
    """Return the sole `pin_index` for a flat net name that is not shared by
    any other net in this extraction (no positional resolution needed)."""
    candidates = groups.get(name, [])
    if len(candidates) != 1:
        raise FlowError(
            f"expected exactly one net named {name!r}, found {len(candidates)} "
            f"-- cannot positively identify this port without positional "
            f"resolution (see {FRICTION_ISSUE} and this module's own "
            f"docstring, 'If disambiguation still fails')"
        )
    return candidates[0]["pin_index"]


def _label_dict(net: dict) -> dict[str, tuple[float, float]]:
    return {lbl["text"]: (lbl["x_um"], lbl["y_um"]) for lbl in net.get("label_positions_um") or []}


def _close(a: tuple[float, float], b: tuple[float, float]) -> bool:
    return abs(a[0] - b[0]) <= _POS_TOL_UM and abs(a[1] - b[1]) <= _POS_TOL_UM


def _match_positional(
    groups: dict[str, list[dict]], name: str, expected: dict[str, tuple[float, float]]
) -> int:
    """Find the unique net named `name` whose own drawn label positions
    positively match `expected` (a `{label text: (x_um, y_um)}` map, each
    within `_POS_TOL_UM`), among possibly several same-named collided
    candidates -- see the module docstring, "Routing-level composition".
    Raises `FlowError` (a positive-identification failure, not a guess) on
    zero or more than one match."""
    candidates = groups.get(name, [])
    matches = []
    for net in candidates:
        labels = _label_dict(net)
        if all(text in labels and _close(labels[text], pos) for text, pos in expected.items()):
            matches.append(net)
    if len(matches) != 1:
        raise FlowError(
            f"could not positively identify the net named {name!r} matching "
            f"expected label positions {expected} among {len(candidates)} "
            f"same-named candidates ({len(matches)} positional matches) -- "
            f"see {FRICTION_ISSUE} and this module's own docstring, 'If "
            f"disambiguation still fails'"
        )
    return matches[0]["pin_index"]


def _resolve_ring_ports(payload: dict, nand_payload: dict, stage_payload: dict, mod) -> dict[int, str]:
    """Positively identify `ro_ring11`/`ro_ring11_ring2`'s five true
    external ports (`en`, `ro`, `vddr`, `vss`, `vsubs`) among the assembled
    ring's `nets[]`, returning `{pin_index: port_name}`. See the module
    docstring, "Routing-level composition"."""
    groups = _nets_by_name(payload)
    bboxes, _locals = mod._bboxes_and_locals()
    offsets = mod.row_offsets(mod.ROW_ORDER, bboxes)
    xg_a_local = _leaf_local_pos(nand_payload, "a")
    last_id = mod.ROW_ORDER[-1]
    last_y_local = _leaf_local_pos(stage_payload, "y")
    expected_ro = {
        "a": (offsets["xg"] + xg_a_local[0], xg_a_local[1]),
        "y": (offsets[last_id] + last_y_local[0], last_y_local[1]),
    }
    return {
        _match_positional(groups, "a|y", expected_ro): "ro",
        _unique_pin_index(groups, "en"): "en",
        _unique_pin_index(groups, "vddr"): "vddr",
        _unique_pin_index(groups, "vss"): "vss",
        _unique_pin_index(groups, "vsubs"): "vsubs",
    }


def _resolve_combiner_sampler_ports(
    payload: dict, ro_buf_payload: dict, dff_payload: dict, mod
) -> dict[int, str]:
    """Positively identify `combiner_sampler`'s eleven true external ports,
    plus its three internal-only `ro1`/`ro2`/`xo` nets (each already
    uniquely named, per the module docstring's own "Two composed drop-ins"
    section), among its `nets[]`, returning `{pin_index: name}`. The three
    internal names are never added to `_combiner_sampler_routed_subckt`'s
    own exposed `.subckt` port list -- they exist purely so a testbench
    addressing this block's internal state (e.g.
    `sim/tb/sampler-core-idle-leakage-extracted-routed/`) can use a
    self-documenting node name (`xcs.xo`) instead of an arbitrary `cN`
    placeholder."""
    groups = _nets_by_name(payload)
    offsets = mod.row_offsets()
    robuf_a_local = _leaf_local_pos(ro_buf_payload, "a")
    dff_q_local = _leaf_local_pos(dff_payload, "q")

    def _expect_a(block_id: str) -> dict[str, tuple[float, float]]:
        return {"a": (offsets[block_id] + robuf_a_local[0], robuf_a_local[1])}

    def _expect_q(block_id: str) -> dict[str, tuple[float, float]]:
        return {"q": (offsets[block_id] + dff_q_local[0], dff_q_local[1])}

    return {
        _match_positional(groups, "a", _expect_a("xb1")): "rn1",
        _match_positional(groups, "a", _expect_a("xb2")): "rn2",
        _match_positional(groups, "q", _expect_q("xsb")): "raw_bit",
        _match_positional(groups, "q", _expect_q("xsv")): "raw_valid",
        _match_positional(groups, "q", _expect_q("xsr1")): "ring_bit1",
        _match_positional(groups, "q", _expect_q("xsr2")): "ring_bit2",
        _unique_pin_index(groups, "clk"): "clk",
        _unique_pin_index(groups, "rst_n"): "rst_n",
        _unique_pin_index(groups, "vss"): "vss",
        _unique_pin_index(groups, "vsubs"): "vsubs",
        _unique_pin_index(groups, "d|vdd"): "vdd",
        # Internal-only, not exposed as wrapper ports -- see docstring above.
        _unique_pin_index(groups, "a|d|y"): "ro1",
        _unique_pin_index(groups, "b|d|y"): "ro2",
        _unique_pin_index(groups, "d|y"): "xo",
    }


def _positional_args(pin_count: int, port_map: dict[int, str], prefix: str) -> list[str]:
    """Return `pin_count` positional call-site node names for a raw `klt
    extract` `.SUBCKT`: `port_map`'s resolved name at each identified
    `pin_index`, an arbitrary locally-unique `{prefix}{n}` name (SPICE
    subcircuit-instance-scoped, so safe to reuse across instances) at every
    other position -- see the module docstring, "Routing-level
    composition"."""
    args = []
    counter = 0
    for idx in range(pin_count):
        if idx in port_map:
            args.append(port_map[idx])
        else:
            counter += 1
            args.append(f"{prefix}{counter}")
    return args


def _ring_routed_subckt(name: str, raw_subckt: str, pin_count: int, port_map: dict[int, str]) -> str:
    args = _positional_args(pin_count, port_map, "n")
    lines = [f".subckt {name} en ro vddr vss vsubs"]
    lines.append(f"xcore {' '.join(args)} {raw_subckt}")
    lines.append(".ends")
    return "\n".join(lines) + "\n"


def _combiner_sampler_routed_subckt(pin_count: int, port_map: dict[int, str]) -> str:
    args = _positional_args(pin_count, port_map, "c")
    lines = [
        ".subckt combiner_sampler_routed_extracted rn1 rn2 vdd vss clk rst_n "
        "raw_bit raw_valid ring_bit1 ring_bit2 vsubs"
    ]
    lines.append(f"xcore {' '.join(args)} combiner_sampler")
    lines.append(".ends")
    return "\n".join(lines) + "\n"


def _ro_array_core_routed_subckt() -> str:
    """`design/ro_array_core.spice`'s own topology: two routing-level ring
    wrappers, plus the buffer/XOR stage at leaf level -- see the module
    docstring, "Two composed drop-ins, different scope", for why."""
    lines = [".subckt ro_array_core_routed_extracted en1 en2 vddr1 vddr2 vdd vss xo ro1 ro2 vsubs"]
    lines.append("xr1 en1 rn1 vddr1 vss vsubs ro_ring11_routed_extracted")
    lines.append("xr2 en2 rn2 vddr2 vss vsubs ro_ring11_ring2_routed_extracted")
    lines.append("xb1 rn1 vdd vss vsubs ro1 ro_buf")
    lines.append("xb2 rn2 vdd vss vsubs ro2 ro_buf")
    lines.append("xa1 ro1 ro2 vdd vss vsubs xo xor2")
    lines.append(".ends")
    return "\n".join(lines) + "\n"


def _sampler_core_routed_subckt() -> str:
    """`design/sampler_core.spice`'s own external boundary, entirely
    routing-level: two ring wrappers feeding the fully assembled
    `combiner_sampler` wrapper directly (bypassing
    `ro_array_core_routed_extracted` -- see the module docstring, "Two
    composed drop-ins, different scope")."""
    lines = [
        ".subckt sampler_core_routed_extracted en1 en2 vddr1 vddr2 vdd vss "
        "clk rst_n raw_bit raw_valid ring_bit1 ring_bit2 vsubs"
    ]
    lines.append("xr1 en1 rn1 vddr1 vss vsubs ro_ring11_routed_extracted")
    lines.append("xr2 en2 rn2 vddr2 vss vsubs ro_ring11_ring2_routed_extracted")
    lines.append(
        "xcs rn1 rn2 vdd vss clk rst_n raw_bit raw_valid ring_bit1 ring_bit2 vsubs "
        "combiner_sampler_routed_extracted"
    )
    lines.append(".ends")
    return "\n".join(lines) + "\n"


def build(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    leaf_payloads: dict[str, dict] = {}
    for name, gds, top in LEAF_CELLS:
        leaf_payloads[name] = extract_leaf(name, gds, top, outdir)

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

    # -- Routing-level composition (issue #217) -- see module docstring. --
    ring_payloads = {}
    ring_ports = {}
    for name, gds, top, mod, nand_leaf, stage_leaf in ASSEMBLED_RINGS:
        payload = extract_assembled(name, gds, top, outdir)
        ring_payloads[name] = payload
        ring_ports[name] = _resolve_ring_ports(payload, leaf_payloads[nand_leaf], leaf_payloads[stage_leaf], mod)

    cs_payload = extract_assembled(
        "combiner_sampler", COMBINER_SAMPLER_GDS, COMBINER_SAMPLER_TOP, outdir
    )
    cs_ports = _resolve_combiner_sampler_ports(
        cs_payload, leaf_payloads["ro_buf"], leaf_payloads["sampler_dff"], _cs_mod
    )

    ring1_payload = ring_payloads["ro_ring11"]
    ring2_payload = ring_payloads["ro_ring11_ring2"]

    ro_array_core_routed = (
        ROUTED_HEADER.format(source="design/ro_array_core.spice", pdk=PDK_VARIANT)
        + '.include "ro_ring11.routed.extracted.spice"\n'
        + '.include "ro_ring11_ring2.routed.extracted.spice"\n'
        + '.include "ro_buf.extracted.spice"\n'
        + '.include "xor2.extracted.spice"\n'
        + "\n"
        + _ring_routed_subckt(
            "ro_ring11_routed_extracted", "ro_ring11", ring1_payload["pin_count"], ring_ports["ro_ring11"]
        )
        + "\n"
        + _ring_routed_subckt(
            "ro_ring11_ring2_routed_extracted",
            "ro_ring11_ring2",
            ring2_payload["pin_count"],
            ring_ports["ro_ring11_ring2"],
        )
        + "\n"
        + _ro_array_core_routed_subckt()
    )
    (outdir / "ro_array_core.routed.extracted.spice").write_text(ro_array_core_routed)

    sampler_core_routed = (
        ROUTED_HEADER.format(source="design/sampler_core.spice", pdk=PDK_VARIANT)
        + '.include "ro_ring11.routed.extracted.spice"\n'
        + '.include "ro_ring11_ring2.routed.extracted.spice"\n'
        + '.include "combiner_sampler.routed.extracted.spice"\n'
        + "\n"
        + _ring_routed_subckt(
            "ro_ring11_routed_extracted", "ro_ring11", ring1_payload["pin_count"], ring_ports["ro_ring11"]
        )
        + "\n"
        + _ring_routed_subckt(
            "ro_ring11_ring2_routed_extracted",
            "ro_ring11_ring2",
            ring2_payload["pin_count"],
            ring_ports["ro_ring11_ring2"],
        )
        + "\n"
        + _combiner_sampler_routed_subckt(cs_payload["pin_count"], cs_ports)
        + "\n"
        + _sampler_core_routed_subckt()
    )
    (outdir / "sampler_core.routed.extracted.spice").write_text(sampler_core_routed)


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
