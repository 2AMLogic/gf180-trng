#!/usr/bin/env python3
"""Compose parasitic-annotated (`klt extract --parasitics`) netlists into
post-layout drop-in replacements for `design/ro_array_core.spice` and
`design/sampler_core.spice`, for issue #17 (device-level post-layout
re-run), issue #217 (routing-level post-layout re-run, on top of #17) and
issue #232 (the full-chip inter-region delta DR-0025 authorises, on top of
#217).

    python3 layout/pex/build.py            # extract + compose, write files
    python3 layout/pex/build.py --check    # rebuild to scratch, compare bytes
    python3 layout/pex/build.py --fullchip-extract   # refresh the DR-0025
                                           # delta report (EXPENSIVE -- tens
                                           # of minutes; see below)

This module now runs three composition paths. The first two are written by
the same `build()` call and covered by the same `--check`; the third is
written by `build()` too, but from a committed, separately-refreshed report,
because the extraction behind it is far too expensive to run on every check:

1. **Leaf-cell (device-level)**, issue #17 -- `ro_array_core.extracted.spice`
   / `sampler_core.extracted.spice`. See "Why leaf cells" below; unchanged
   by issues #217 and #232.
2. **Assembled-block (routing-level)**, issue #217 --
   `ro_array_core.routed.extracted.spice` / `sampler_core.routed.extracted.spice`.
   See "Routing-level composition" below.
3. **Full chip (inter-region delta)**, issue #232 / DR-0025 --
   `sampler_core.fullchip.extracted.spice`, from
   `layout/pex/reports/fullchip_parasitics.json`. See "Full-chip
   (inter-region) delta composition" below.

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
"Full-chip (inter-region) delta composition" below, where path 3 prices two
of those inter-region nets -- unchanged by issues #217 and #232 for path 1
itself, which still composes leaf cells only).

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
residual is recorded rather than silently composing from path 1 instead.

## Per-stage noise injection (issue #217 §7.5), and why no tool gap blocks it

`sim/tb/sampler-array-digitize-*/` puts a series `trnoise` source on every
one of a ring's eleven inter-stage nets, and its own manifest records the
constraint that forces its shape: *"ngspice cannot insert a series noise
source inside a subcircuit."* At leaf level (path 1) that costs nothing --
the inter-stage wire runs BETWEEN eleven separately-instantiated leaf
subcircuits, so the source goes on the wire. At routing level the assembled
ring is one subcircuit and the wire is inside it.

This document's own 2026-09-11 delta section first recorded that as a
residual blocked on per-instance device addressability (filed as
klayout-tools#1666: a flat extraction keeps no "this device belongs to
stage N" tag). **That framing overstated what the testbench actually
needs, and this module no longer depends on it.** A series source does not
need to know which stage a device came from. It needs one net broken
between its driver side and its receiver side -- and `klt extract
--parasitics` already discloses exactly that, in the netlist it writes:

* every net's lumped resistance arrives as a star of `R<name> <terminal>
  <hub> <ohms>` cards, one per device terminal on that net (the extractor's
  own documented model, restated in every generated file's banner), so each
  terminal is individually addressable whether or not its stage is;
* every device card names its own gate node, so a terminal is classifiable
  as receiver-side (a gate) or driver-side (anything else) without any
  instance tag.

`_noise_tapped()` therefore re-points each tapped net's *gate-side* star
resistors from the shared hub to a new `rx<j>` hub and promotes both to
ports, emitting `<ring>_routed_ntap` alongside the untapped netlist. Tie a
pair together and the two are the same circuit: a 0 V source is a short, so
every star resistance, the net's grounded capacitance, and therefore every
terminal-to-terminal path are bit-for-bit what the untapped ring has. The
only difference the testbench introduces is the injected series EMF --
which is the leaf-level deck's own construction, one hierarchy level down.

`layout/tests/test_pex_noise_tap.py` holds that equivalence to **byte**
equality (un-tap the committed netlist, compare against the committed
untapped one), and `_noise_tapped()`/`_tap_positions()`/`_gate_nodes()`
raise rather than guess if a tapped net ends up with nothing on either
side, if a device card's arity or model is not what the gate rule assumes,
or if the ring stops having exactly eleven tappable nets.

One asymmetry is disclosed rather than hidden: the net's lumped grounded
capacitance stays on the DRIVER side of the tap -- as it does in the
leaf-level deck, where the wire capacitance lives inside the driving cell's
own extraction, ahead of the source.

## Full-chip (inter-region) delta composition (issue #232, DR-0025)

Both paths above are *intra*-region: each re-runs a single block's own
netlist with device-level or routing-level parasitics annotated, and
neither reads `layout/floorplan/trng_floorplan.gds` at all. Until issue
#222 that was a blocker, not a choice: `layout/floorplan/`'s four guarded
regions were placed with a 20 um isolation channel and **no wiring at all**
between them (`klt extract --top trng_floorplan` on the composed floorplan
GDS reported 2588 top-level pins for what should be a ~12-pin block).

#222 (phase 2 of #219) draws real Metal4 trunks and Metal3 risers across
the isolation channels for every net `design/floorplan_netlist.py`
declares, and the composed, routed floorplan is DRC-clean and LVS-matches
that declaration's own composed reference. That made a third,
**inter-region** path possible, and
`spec/decision-records/DR-0025-full-chip-pex-scope.md` decided what it is
allowed to be about: extract `trng_floorplan.gds` with `--parasitics` at
the same cell-instance granularity the composed LVS already uses, take from
it only the inter-region net parasitics as a **delta** over what the two
intra-region paths above already carry, and simulate only the nets with a
transistor-level device at both ends -- today `ro1`/`ro2`
(`design/floorplan_netlist.INTER_REGION_NETS`'s own `role: "entropy_tap"`
nets), plus a disclosed, driver-side-only output-load capacitor on the four
`role: "raw_tap"/"liveness_tap"` nets (`raw_bit`, `raw_valid`, `ring_bit1`,
`ring_bit2`). Read DR-0025 in full before extending this section further --
in particular its "Alternatives considered" for why a blanket
transistor-level full-chip extraction, and a `clk`-trunk-focused increment,
were both rejected, and its own worked-example arithmetic for why `ro1`/
`ro2` are the only two nets the "both ends transistor-level" filter admits
today.

### Why a DELTA, and why it must be able to raise rather than compose

The full-chip extraction's `ro1` net merges four physically distinct
pieces into one electrical net: `ring1`'s own internal wrap wire (already
inside `ro_ring11.routed.extracted.spice`'s own `ro` net), the Metal4 trunk
and Metal3 risers `interregion.py` draws, and `combiner_sampler`'s own
`rn1` stub (already inside `combiner_sampler.routed.extracted.spice`'s own
`rn1` net). Composing the full-chip extraction's merged R/C **on top of**
those two intra-region extractions would double-count the wire they already
carry; the trunk's own contribution is only recoverable by subtraction:

    delta = fullchip_net.{resistance_ohm, capacitance_ff}
            - ring_net.{resistance_ohm, capacitance_ff}
            - combiner_sampler_net.{resistance_ohm, capacitance_ff}

`_reconcile_delta` is the one function that arithmetic runs through, for
every net this module prices this way. Parasitics are only ever *added* by
more wire, never removed, so a merged net's own R/C can only be >= the sum
of its already-extracted intra-region parts; a result below that (beyond
`_CLOSE_TOLERANCE_OHM`/`_CLOSE_TOLERANCE_FF`'s own float-rounding
allowance) can only mean a labelling/positional-identification bug
upstream, not physical reality, and `_reconcile_delta` raises `FlowError`
rather than composing from it -- the same "raise rather than guess"
discipline `_match_positional`/`_unique_pin_index` already follow for the
routing-level path.

Net identity for `ro1`/`ro2`/the four output-load nets in the full-chip
extraction needs no *positional* resolution (unlike the routing-level path's
collided `a|y`/`a`/`q` names), but it does need more than an exact name
match, because flat extraction of the composed stream joins every drawn
label on a net into one name. Measured, not assumed: `ro1` comes back as
`a|ro1|y` (the ring's own `y` pin label, `interregion.py`'s own trunk label
and `ro_buf`'s own `a` pin label, merged), `ring_bit1` as
`q|ring_bit1|ring_bit[0]`. What IS unique is the *label*:
`interregion.py` draws exactly one `ro1` text, on the trunk itself, and no
other net carries it. `_parasitics_entry_by_label` matches on that label
and raises `FlowError` if it ever stops resolving to exactly one net,
rather than guessing. The ring-side and
`combiner_sampler`-side intra-region parts, by contrast, DO need the
existing routing-level path's own positional port resolution (`ro`/`rn1`/
`rn2` are collided flat names in *those* extractions) -- `_net_id_at_pin_index`
joins a resolved `pin_index` back to its own `parasitics.nets[]` entry via
`net_id` (`net.cluster_id`), the stable cross-reference `klt extract`'s own
JSON schema provides for exactly this.

### The composed segment: a symmetric pi-model, not a re-derived star

`klt extract --parasitics`'s own model gives each net a single lumped
series resistance distributed as a star across that net's device terminals,
plus one hub-level ground capacitance -- there is no per-position R/C
breakdown to subtract piecewise, only the net's own two scalar totals. A
delta computed from two scalars cannot reconstruct the trunk's own
internal star, so `_pi_delta_lines` instead inserts the standard lumped
approximation of a distributed line for a segment with only its own total R
and total C known: `C_delta/2` at each end, `R_delta` in series between
them -- between each ring wrapper's own `ro` port and
`combiner_sampler_routed_extracted`'s `rn1`/`rn2` port respectively. This is
a disclosed modelling choice (a symmetric split is not derived from the
extraction, it is the simplest lumped equivalent available from two
scalars), stated here and in every record's own Caveats.

The four output-load nets get no series R at all: `raw_bit`/`raw_valid`/
`ring_bit1`/`ring_bit2` are driven by a real extracted `sampler_dff`
instance into an *abstracted* `digital` receiver (DR-0025's own filter
excludes them from being simulated as two-ended nets), so a series resistor
ending in an open node would pass no current and change nothing
electrically -- only the added grounded capacitance at the driver's own pin
is carried forward (`_sampler_core_fullchip_subckt`'s `cload_<net>` cards),
disclosed as driver-side-only, exactly as DR-0025 requires.

### The expensive step is never on `build()`'s unconditional path

The full-chip `--parasitics` extraction is not cheap the way every other
`_run_klt` call in this module is. DR-0025's own runtime probe had not
completed after ~19.5 minutes (partly CPU-contended, single uninstrumented
observation) before being terminated; issue #232 re-measured it properly and
recorded **~17.5 minutes of CPU time** (the contention-independent figure to
budget against), which was ~38 minutes of wall clock on a 28-core host
running at a ~25-29 load average. Every run writes its own `runtime_s` AND
the host load average it was measured under into the committed report, so
the next person does not have to discount an uninstrumented number the way
DR-0025 had to.

`run_fullchip_extraction_and_report` (invoked only by `main()`'s
`--fullchip-extract`, never by `build()`) is the one place this module ever
runs it, at `FULLCHIP_TIMEOUT_S` (3600s, chosen to leave headroom above that
without being unbounded), and writes its result to the COMMITTED
`layout/pex/reports/fullchip_parasitics.json`.

There are therefore TWO caches here, doing two different jobs, and it is
worth keeping them straight:

* the **committed report** is what every ordinary `build()`/`--check` run
  composes from, so the expensive extraction is paid once per layout
  revision rather than once per check; and
* `FULLCHIP_CACHE` (gitignored, under `layout/.work/`) holds the last run's
  raw `klt` response, so `--fullchip-extract --reuse-cache` can recompute
  the delta arithmetic in seconds while that arithmetic is being developed
  or debugged. It is keyed on the exact argument list, and a report produced
  from it is stamped `from_cache: true` -- a cache hit never re-dates
  someone else's measurement as a fresh one. `klt extract --rerun` is not a
  substitute: it re-runs the extraction and diffs it against a committed
  report, which is a staleness check, not a cache.

`build()`'s own unconditional path (every plain invocation and every
`--check`) never re-runs that extraction. It reads the committed report
back (cheap, no new `klt` call) and reconciles it (`_reconcile_cached_report`)
against a FRESH ring1/ring2/combiner_sampler extraction -- which `build()`
already runs for the routing-level path above, so this costs nothing
additional -- raising `FlowError` if the cached report's own recorded
intra-region R/C has drifted from what a fresh extraction now reports (the
drawn geometry moved since `--fullchip-extract` was last run, and the
committed report needs refreshing, not silently trusting). This is the
"held, not asserted" reconciliation covered by
`layout/tests/test_pex_fullchip.py`.

### What this does and does not capture

**Captured**: `ro1`/`ro2`'s own inter-region trunk-plus-riser delta,
inserted where it physically sits (between each ring's own output and
`combiner_sampler`'s own buffer input), on top of every parasitic the two
intra-region extractions already carry for that same net; plus a disclosed
driver-side-only output-load capacitor on `raw_bit`/`raw_valid`/
`ring_bit1`/`ring_bit2`.

**Not captured**, per DR-0025's own stated coverage hole -- restated here,
not relaxed:

- **Nothing about `digital`'s own devices.** The ~2500
  `gf180mcu_fd_sc_mcu9t5v0__*` instances stay abstracted (black boxes); the
  digital section's timing and power are owned by the post-route
  gate-level path (DR-0021/DR-0022/DR-0023), better evidence for that
  question than an ngspice re-derivation would be.
- **No arrival-time / clock-tree claim across a region boundary.** `clk`
  and `rst_n` are driven from `digital` in the real chip, but every deck in
  `sim/tb/` (including the new `-extracted-fullchip` siblings) replaces
  that driver with an ideal, zero-impedance ngspice source -- the trunks'
  own resistance in front of a 0 ohm source is a no-op dressed as a
  measurement, so this module prices no delta on `clk`/`rst_n` at all.
- **Only driver-side loading on the four `digital`-facing outputs**, with
  **no receiver gate capacitance** behind it -- `raw_bit`'s 524.77 um trunk
  is the largest single parasitic on the chip and is only partly priced
  here, stated rather than hidden.
- **No IR-drop verdict** on the shared 430.23 um `vss` trunk, and nothing
  about `digital`'s `vddd`/`vss` PDN tie (gf180-trng#224) -- both their own
  follow-ups (gf180-trng#234, gf180-trng#224).
- **Net-to-net (vertical-overlap) coupling capacitance is reported, not
  composed.** `klt extract --parasitics` keeps each net's ground
  capacitance (`parasitics.nets[].capacitance_ff`) separate from the
  capacitors it shares with the nets it crosses
  (`parasitics.nets[].coupled[]`), and a coupling capacitor belongs to a
  *pair* of nets, so it has no intra-region counterpart for
  `_reconcile_delta` to subtract. Each net's coupling total is written into
  the committed report as `fullchip_coupling_capacitance_ff` beside its
  delta (`_coupling_total_ff`) rather than folded into it -- under-reporting
  rather than over-reporting, which is the direction the "floor, not
  ceiling" framing below requires. Measured, for scale: 0.077 fF on `ro1`
  and 0.067 fF on `ro2`, against deltas of 8.5 fF and 3.2 fF.

Because inter-region parasitics can only *add* R and C,
`sim/characterization-post-layout-extracted.md` §0.1's "floor, not
ceiling" framing survives this increment unchanged -- every degradation
reported anywhere in this module's evidence, including this section's own,
is still a lower bound on what a full transistor-level chip extraction
would show.

See `sim/characterization-post-layout-extracted.md` for the honest
accounting of what each path changes and what it cannot show, and
`layout/pex/reports/fullchip_parasitics.json` (once `--fullchip-extract`
has been run) for the measured delta figures themselves.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from layout._klt import FlowError, _run_klt, klt_version, resolve_pdk  # noqa: E402
import layout.blocks.combiner_sampler.build as _cs_mod  # noqa: E402
import layout.rings.ro_ring11.build as _ring1_mod  # noqa: E402
import layout.rings.ro_ring11_ring2.build as _ring2_mod  # noqa: E402
from design.floorplan_netlist import INTER_REGION_NETS  # noqa: E402
from layout.floorplan.floorplan import _reference_top_pins  # noqa: E402

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

# --------------------------------------------------------------------------- #
# Full-chip delta composition (issue #232, DR-0025). See this module's own
# docstring, "Full-chip (inter-region) delta composition", for the design.
# --------------------------------------------------------------------------- #

FULLCHIP_GDS = "layout/floorplan/trng_floorplan.gds"
FULLCHIP_TOP = "trng_floorplan"
FULLCHIP_LVS_REFERENCE = REPO_ROOT / "layout" / "floorplan" / "trng_floorplan.lvs_reference.spice"
#: Same glob `layout/floorplan/floorplan.py`'s own `run_extract_composed`
#: uses (`COMPOSED_ABSTRACT_CELLS`) -- kept as a literal here rather than
#: imported, the same "don't import a caller's constant, restate the deck
#: fact" discipline `layout/tests/test_pex_noise_tap.py`'s own `TAP_PREFIX`
#: follows, so a rename of one does not silently desync the other.
FULLCHIP_ABSTRACT_CELLS = "gf180mcu_fd_sc_mcu9t5v0__*"
#: DR-0025's own measured cost input: the full-chip `--parasitics` extraction
#: had not completed after ~19.5 minutes (partly CPU-contended, single
#: uninstrumented observation) on the host that record was written on.
#: 3600s leaves headroom above that without being unbounded. Every other
#: `_run_klt` call in this module keeps `_run_klt`'s own 600s default --
#: this is the one deliberate exception, and it is never on `build()`'s own
#: unconditional path (see `main()`'s `--fullchip-extract`).
FULLCHIP_TIMEOUT_S = 3600
FULLCHIP_REPORT = PEX_DIR / "reports" / "fullchip_parasitics.json"
#: Raw `klt extract` response of the last `--fullchip-extract` run, under the
#: gitignored scratch tree -- never committed, and never read unless
#: `--reuse-cache` asks for it. This is the iteration cache DR-0025's own
#: runtime note anticipated: composing, re-composing and debugging the delta
#: arithmetic against a fixed extraction costs seconds instead of the
#: tens-of-minutes the extraction itself does. See `extract_fullchip`.
FULLCHIP_CACHE = REPO_ROOT / "layout" / ".work" / "pex-fullchip" / "fullchip_extraction_cache.json"
#: Scratch directory `--fullchip-extract` extracts into. Deliberately NOT
#: `WORK_DIR`: `--check` globs `*.spice` out of `WORK_DIR` and requires a
#: committed counterpart for each, so a multi-megabyte
#: `trng_floorplan.fullchip.extracted.spice` left there by an earlier
#: `--fullchip-extract` run would make the next `--check` fail demanding a
#: file this module never composes (`layout/pex/` holds composed drop-ins,
#: not raw full-chip extractions). Found the hard way while building #232.
FULLCHIP_WORK_DIR = FULLCHIP_CACHE.parent

#: DR-0025's own load-bearing filter: a full-chip inter-region trunk is
#: SIMULATED only when both its endpoints are already transistor-level in
#: this module's existing intra-region extractions -- today exactly the two
#: nets `design/floorplan_netlist.INTER_REGION_NETS` tags `role:
#: "entropy_tap"` (`ro1`: ring1.ro -> combiner_sampler.rn1; `ro2`: ring2.ro
#: -> combiner_sampler.rn2). Derived from that declared data, not
#: hardcoded, so a future net gaining a transistor-level receiver (DR-0025's
#: own "Revisit if") is picked up here without an edit.
_SIMULATED_ROLES = ("entropy_tap",)
#: Roles whose driver is transistor-level (a real `sampler_dff` inside
#: `combiner_sampler`) but whose receiver is `digital`, abstracted --
#: DR-0025 prices these as a disclosed, driver-side-only OUTPUT LOAD (a
#: capacitor at the driver's own pin), never as a simulated two-ended net
#: (no receiver gate capacitance is modelled -- see the module docstring).
_DRIVER_SIDE_LOAD_ROLES = ("raw_tap", "liveness_tap")

#: Absolute tolerance the delta arithmetic must close within (float rounding
#: only -- `klt extract`'s own JSON already rounds `resistance_ohm` to 4
#: decimals and `capacitance_ff` to 6, so this is generous against that
#: alone). A full-chip merged net's own R/C can only be >= the sum of its
#: already-extracted intra-region parts (more wire only adds parasitics);
#: anything below `-`(tolerance) means a labelling/positional-identification
#: bug, not physical reality, and `_reconcile_delta` raises rather than
#: composing from it.
_CLOSE_TOLERANCE_OHM = 1e-3
_CLOSE_TOLERANCE_FF = 1e-4


def _entropy_tap_nets() -> list[dict]:
    """The full-chip inter-region nets DR-0025's filter actually simulates
    (today: `ro1`, `ro2`) -- see `_SIMULATED_ROLES`."""
    return [net for net in INTER_REGION_NETS if net["role"] in _SIMULATED_ROLES]


def _driver_side_load_nets() -> list[dict]:
    """The full-chip inter-region nets DR-0025 prices as an added,
    driver-side-only output load (today: `raw_bit`, `raw_valid`,
    `ring_bit1`, `ring_bit2`) -- see `_DRIVER_SIDE_LOAD_ROLES`."""
    return [net for net in INTER_REGION_NETS if net["role"] in _DRIVER_SIDE_LOAD_ROLES]


def _net_id_at_pin_index(payload: dict, pin_index: int) -> int:
    """The `net_id` (`net.cluster_id`) of the `nets[]` entry promoted to
    `.SUBCKT` position `pin_index` in this extraction -- the stable key that
    joins a resolved port position back to its own `parasitics.nets[]`
    entry (which is indexed by `net_id`, not `pin_index`)."""
    for net in payload["nets"]:
        if net.get("pin_index") == pin_index:
            return net["net_id"]
    raise FlowError(f"no net at pin_index {pin_index} in this extraction's own nets[]")


def _parasitics_entry_by_net_id(payload: dict, net_id: int) -> dict:
    parasitics = payload.get("parasitics")
    if not parasitics:
        raise FlowError(
            "this extraction has no `parasitics` block -- was `--parasitics` given?"
        )
    matches = [net for net in parasitics["nets"] if net["net_id"] == net_id]
    if len(matches) != 1:
        raise FlowError(
            f"expected exactly one parasitics.nets[] entry for net_id {net_id}, "
            f"found {len(matches)}"
        )
    return matches[0]


#: KLayout joins every drawn label on one net into a single net name -- `'|'`
#: between labels of a flat extraction (`layout/floorplan/interregion.
#: extracted_net_name`'s own documented convention) and `','` in the
#: LEF/DEF-merged case. A full-chip inter-region net therefore never arrives
#: under its own bare name: `ro1` comes back as `a|ro1|y` (the ring's own `ro
#: _stage` `y` pin label, `interregion.py`'s own trunk label, and `ro_buf`'s
#: own `a` pin label, all merged onto one electrical net), and `ring_bit1` as
#: `q|ring_bit1|ring_bit[0]`. Measured, not assumed -- see
#: `_parasitics_entry_by_label`.
_NET_LABEL_SEPARATORS = re.compile(r"[|,]")


def _net_labels(name: str) -> set[str]:
    """Every drawn label KLayout joined into one extracted net name."""
    return {part for part in _NET_LABEL_SEPARATORS.split(name) if part}


def _parasitics_entry_by_label(payload: dict, label: str) -> dict:
    """Like `_parasitics_entry_by_net_id`, but for a full-chip net identified
    by one of its own drawn labels.

    Positional resolution is not needed here, and exact-name matching does
    not work: flat extraction of the composed stream merges every label on a
    net into one joined name (`_NET_LABEL_SEPARATORS`), so the net
    `design/floorplan_netlist.py` calls `ro1` arrives as `a|ro1|y`. What IS
    unique is the label itself -- `interregion.py` draws exactly one `ro1`
    text, on the trunk, and no other net carries that label. That uniqueness
    is CHECKED here rather than assumed: zero or more than one match raises
    `FlowError` instead of composing, the same discipline
    `_match_positional`/`_unique_pin_index` follow for the routing-level
    path.
    """
    parasitics = payload.get("parasitics")
    if not parasitics:
        raise FlowError(
            "this extraction has no `parasitics` block -- was `--parasitics` given?"
        )
    matches = [net for net in parasitics["nets"] if label in _net_labels(net["net"])]
    if len(matches) != 1:
        raise FlowError(
            f"expected exactly one parasitics.nets[] entry carrying the drawn label "
            f"{label!r} in the full-chip extraction, found {len(matches)} "
            f"({[net['net'] for net in matches]}) -- see {FRICTION_ISSUE} and this "
            "module's own docstring, 'Full-chip (inter-region) delta composition'"
        )
    return matches[0]


def _coupling_total_ff(entry: dict) -> float:
    """This net's total net-to-net (vertical-overlap) coupling capacitance,
    which is reported ALONGSIDE the delta and deliberately NOT folded into
    it.

    `klt extract --parasitics` keeps a net's own ground capacitance
    (`capacitance_ff`) separate from the net-to-net capacitors it shares with
    the nets it crosses (`coupled[]`), and only the first is a quantity the
    subtraction in `_reconcile_delta` can close over -- a coupling capacitor
    belongs to a *pair* of nets, so it has no intra-region counterpart to
    subtract. Recording it is how this module keeps
    `sim/characterization-post-layout-extracted.md` section 0.1's "floor, not
    ceiling" framing honest: the coupled term is real added load that this
    composition does not carry, so the composed netlist under-reports rather
    than over-reports.
    """
    return round(sum(c["capacitance_ff"] for c in (entry.get("coupled") or [])), 6)


def _reconcile_delta(name: str, fullchip: dict, parts: list[dict]) -> dict:
    """DR-0025's own arithmetic: `fullchip`'s merged R/C, less every already-
    extracted intra-region `parts` entry's own R/C for that same physical
    net. Raises `FlowError` (composes nothing) rather than returning a
    negative delta beyond float-rounding tolerance -- see
    `_CLOSE_TOLERANCE_OHM`/`_CLOSE_TOLERANCE_FF`.
    """
    delta_r = fullchip["resistance_ohm"] - sum(p["resistance_ohm"] for p in parts)
    delta_c = fullchip["capacitance_ff"] - sum(p["capacitance_ff"] for p in parts)
    if delta_r < -_CLOSE_TOLERANCE_OHM or delta_c < -_CLOSE_TOLERANCE_FF:
        raise FlowError(
            f"{name}: the full-chip extraction's merged net (R={fullchip['resistance_ohm']} "
            f"ohm, C={fullchip['capacitance_ff']} fF) is SMALLER than the sum of its own "
            f"already-extracted intra-region parts (R={sum(p['resistance_ohm'] for p in parts)} "
            f"ohm, C={sum(p['capacitance_ff'] for p in parts)} fF) -- the arithmetic does not "
            "close. Parasitics are only ever added by more wire, never removed, so this can "
            "only mean a labelling/positional-identification bug upstream of this function, "
            "not physical reality. Composing from this would double-count or undercount; see "
            "this module's own docstring, 'Full-chip (inter-region) delta composition'."
        )
    # A tiny negative residual inside tolerance is float rounding, not signal
    # -- clamp rather than writing a (physically meaningless) negative R/C
    # card into the composed netlist.
    return {
        "resistance_ohm": round(max(delta_r, 0.0), 6),
        "capacitance_ff": round(max(delta_c, 0.0), 6),
    }


def _fullchip_extract_args(outdir: Path) -> list[str]:
    """`layout/floorplan/floorplan.py`'s own `run_extract_composed` argument
    list, plus `--parasitics` -- DR-0025 step 1, verbatim. Built in one place
    so the run, the cache key and the provenance line in the committed report
    can never describe three different invocations."""
    pins = _reference_top_pins(FULLCHIP_LVS_REFERENCE, FULLCHIP_TOP)
    out_path = outdir / "trng_floorplan.fullchip.extracted.spice"
    return [
        "extract",
        FULLCHIP_GDS,
        "--deck",
        DECK,
        "--top",
        FULLCHIP_TOP,
        "--parasitics",
        "--pdk",
        PDK_VARIANT,
        "--abstract-cells",
        FULLCHIP_ABSTRACT_CELLS,
        "--pins",
        ",".join(pins),
        "--def-net-names",
        "-o",
        str(out_path.relative_to(REPO_ROOT)),
    ]


def _fullchip_cache_key(args: list[str]) -> list[str]:
    """`args` with the `-o <path>` pair dropped.

    Everything else in the invocation changes what the extractor computes;
    where the netlist is written does not. Keying the cache on the full list
    would miss on a pure scratch-directory move, which is a false negative
    that costs tens of minutes."""
    out: list[str] = []
    skip = False
    for arg in args:
        if skip:
            skip = False
            continue
        if arg in ("-o", "--output"):
            skip = True
            continue
        out.append(arg)
    return out


def extract_fullchip(
    outdir: Path, timeout_s: int = FULLCHIP_TIMEOUT_S, *, reuse_cache: bool = False
) -> tuple[dict, dict]:
    """`klt extract --parasitics` over the composed, routed floorplan
    (DR-0025) -- the SAME run shape `layout/floorplan/floorplan.py`'s own
    `run_extract_composed` is held to (the extraction the composed LVS is
    already checked against), plus `--parasitics`. Returns
    `(payload, meta)`.

    Expensive (see `FULLCHIP_TIMEOUT_S`'s own docstring) and NOT part of
    `build()`'s unconditional path -- only ever invoked by `main()`'s
    `--fullchip-extract`.

    Every run writes its raw response to `FULLCHIP_CACHE` (under the
    gitignored `layout/.work/`), and `reuse_cache=True` reads that back
    instead of re-running -- the "equivalent cache" DR-0025's own runtime
    note says whoever built this would need, so the composition step can be
    iterated without re-paying a tens-of-minutes extraction. The cache is
    keyed on the full argument list, so a changed flag, pin set or input path
    misses it rather than silently composing from the wrong run. A cached
    run's own measured `runtime_s` travels with it, and the report it
    produces says `from_cache: true` -- a cache hit never re-dates or
    re-attributes someone else's measurement as a fresh one.
    """
    args = _fullchip_extract_args(outdir)
    if reuse_cache and FULLCHIP_CACHE.is_file():
        cached = json.loads(FULLCHIP_CACHE.read_text())
        if _fullchip_cache_key(cached.get("args") or []) != _fullchip_cache_key(args):
            raise FlowError(
                f"{FULLCHIP_CACHE.relative_to(REPO_ROOT)} was written by a DIFFERENT "
                "extraction invocation than the one this module now builds -- refusing "
                "to compose from it. Re-run without --reuse-cache to refresh it."
            )
        meta = dict(cached["meta"])
        meta["from_cache"] = True
        return cached["payload"], meta

    start = time.monotonic()
    payload = _run_klt(args, timeout_s=timeout_s)
    runtime_s = time.monotonic() - start
    meta = {
        "command": "klt " + " ".join(args),
        "runtime_s": round(runtime_s, 1),
        "klt_version": klt_version(),
        "pdk_variant": PDK_VARIANT,
        "host_load_average_1min": _load_average_1min(),
        "cpu_count": os.cpu_count(),
        "from_cache": False,
    }
    FULLCHIP_CACHE.parent.mkdir(parents=True, exist_ok=True)
    FULLCHIP_CACHE.write_text(json.dumps({"args": args, "meta": meta, "payload": payload}))
    return payload, meta


def _load_average_1min() -> float | None:
    """The host's 1-minute load average at the moment an extraction finished,
    recorded next to its wall-clock runtime.

    DR-0025's own runtime probe had to be discounted precisely because it was
    partly CPU-contended and nobody wrote down by how much. A wall-clock
    figure with no load figure beside it is not reproducible evidence about
    the tool -- it is evidence about the host that day."""
    try:
        return round(os.getloadavg()[0], 2)
    except (OSError, AttributeError):  # pragma: no cover - platform-dependent
        return None


def compute_fullchip_report(
    fullchip_payload: dict,
    ring_payloads: dict[str, dict],
    ring_ports: dict[str, dict[int, str]],
    cs_payload: dict,
    cs_ports: dict[int, str],
) -> dict:
    """DR-0025's own delta arithmetic for every inter-region net this module
    prices, keyed by net name. See the module docstring, "Full-chip
    (inter-region) delta composition"."""
    region_payload = {"ring1": ring_payloads["ro_ring11"], "ring2": ring_payloads["ro_ring11_ring2"]}
    region_ports = {"ring1": ring_ports["ro_ring11"], "ring2": ring_ports["ro_ring11_ring2"]}

    def _pin_index(port_map: dict[int, str], pin: str) -> int:
        for idx, name in port_map.items():
            if name == pin:
                return idx
        raise FlowError(f"no resolved port named {pin!r} in {port_map!r}")

    def _entry_for(payload: dict, port_map: dict[int, str], pin: str) -> dict:
        net_id = _net_id_at_pin_index(payload, _pin_index(port_map, pin))
        return _parasitics_entry_by_net_id(payload, net_id)

    entropy: dict[str, dict] = {}
    for net in _entropy_tap_nets():
        name = net["name"]
        ring_region = next(r for r, _p in net["endpoints"] if r in region_payload)
        ring_pin = next(p for r, p in net["endpoints"] if r == ring_region)
        cs_pin = next(p for r, p in net["endpoints"] if r == "combiner_sampler")

        ring_entry = _entry_for(region_payload[ring_region], region_ports[ring_region], ring_pin)
        cs_entry = _entry_for(cs_payload, cs_ports, cs_pin)
        fc_entry = _parasitics_entry_by_label(fullchip_payload, name)

        delta = _reconcile_delta(name, fc_entry, [ring_entry, cs_entry])
        entropy[name] = {
            "ring_region": ring_region,
            "ring_pin": ring_pin,
            "cs_pin": cs_pin,
            "fullchip_net_name": fc_entry["net"],
            "fullchip_coupling_capacitance_ff": _coupling_total_ff(fc_entry),
            "fullchip": {
                "resistance_ohm": fc_entry["resistance_ohm"],
                "capacitance_ff": fc_entry["capacitance_ff"],
            },
            "ring_intra_region": {
                "resistance_ohm": ring_entry["resistance_ohm"],
                "capacitance_ff": ring_entry["capacitance_ff"],
            },
            "combiner_sampler_intra_region": {
                "resistance_ohm": cs_entry["resistance_ohm"],
                "capacitance_ff": cs_entry["capacitance_ff"],
            },
            "delta": delta,
        }

    loads: dict[str, dict] = {}
    for net in _driver_side_load_nets():
        name = net["name"]
        cs_pin = next(p for r, p in net["endpoints"] if r == "combiner_sampler")
        cs_entry = _entry_for(cs_payload, cs_ports, cs_pin)
        fc_entry = _parasitics_entry_by_label(fullchip_payload, name)
        delta = _reconcile_delta(name, fc_entry, [cs_entry])
        loads[name] = {
            "cs_pin": cs_pin,
            "fullchip_net_name": fc_entry["net"],
            "fullchip_coupling_capacitance_ff": _coupling_total_ff(fc_entry),
            "fullchip": {
                "resistance_ohm": fc_entry["resistance_ohm"],
                "capacitance_ff": fc_entry["capacitance_ff"],
            },
            "combiner_sampler_intra_region": {
                "resistance_ohm": cs_entry["resistance_ohm"],
                "capacitance_ff": cs_entry["capacitance_ff"],
            },
            # Driver-side-only (DR-0025): no receiver device exists to size
            # a series R against (an R ending in an open node passes no
            # current and changes nothing electrically), so only the added
            # capacitance is carried forward into the composed netlist.
            "delta": delta,
        }

    return {"entropy_tap": entropy, "driver_side_load": loads}


def write_fullchip_report(report: dict, extraction_meta: dict, path: Path = FULLCHIP_REPORT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_comment": (
            "GENERATED by layout/pex/build.py --fullchip-extract -- do not edit by "
            "hand. DR-0025's own inter-region delta arithmetic -- see "
            "layout/pex/build.py's module docstring, 'Full-chip (inter-region) "
            "delta composition'."
        ),
        "extraction": extraction_meta,
        **report,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def run_fullchip_extraction_and_report(outdir: Path, *, reuse_cache: bool = False) -> dict:
    """The expensive step (DR-0025's own measured tens-of-minutes cost) --
    ONLY invoked by `main()`'s `--fullchip-extract`, never by `build()`'s own
    unconditional path. Re-runs the cheap intra-region assembled extractions
    too (ring1/ring2/combiner_sampler), since the delta needs both sides
    fresh to reconcile against, then writes the committed derived report
    `layout/pex/reports/fullchip_parasitics.json` that `build()`'s own
    default path reads back cheaply (no new `klt` call) on every
    run/`--check`, reconciling it against a FRESH intra-region extraction
    each time -- see the module docstring.

    `reuse_cache=True` composes from the last run's cached raw response
    (`FULLCHIP_CACHE`) instead of re-extracting -- for iterating on the
    composition, not for producing the committed report.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    leaf_payloads: dict[str, dict] = {}
    for name, gds, top in LEAF_CELLS:
        leaf_payloads[name] = extract_leaf(name, gds, top, outdir)

    ring_payloads: dict[str, dict] = {}
    ring_ports: dict[str, dict[int, str]] = {}
    for name, gds, top, mod, nand_leaf, stage_leaf in ASSEMBLED_RINGS:
        payload = extract_assembled(name, gds, top, outdir)
        ring_payloads[name] = payload
        ring_ports[name] = _resolve_ring_ports(payload, leaf_payloads[nand_leaf], leaf_payloads[stage_leaf], mod)

    cs_payload = extract_assembled("combiner_sampler", COMBINER_SAMPLER_GDS, COMBINER_SAMPLER_TOP, outdir)
    cs_ports = _resolve_combiner_sampler_ports(
        cs_payload, leaf_payloads["ro_buf"], leaf_payloads["sampler_dff"], _cs_mod
    )

    fullchip_payload, meta = extract_fullchip(outdir, reuse_cache=reuse_cache)
    report = compute_fullchip_report(fullchip_payload, ring_payloads, ring_ports, cs_payload, cs_ports)
    write_fullchip_report(report, meta)
    return report


def _reconcile_cached_report(
    cached: dict,
    ring_payloads: dict[str, dict],
    ring_ports: dict[str, dict[int, str]],
    cs_payload: dict,
    cs_ports: dict[int, str],
) -> None:
    """Hold the COMMITTED `fullchip_parasitics.json` report to a FRESH
    intra-region extraction, every `build()`/`--check` run -- the cheap half
    of the reconciliation this module's docstring describes (the expensive
    half, re-running the full-chip extraction itself, is
    `run_fullchip_extraction_and_report`'s job, invoked separately). Raises
    `FlowError` if the cached report's own recorded intra-region R/C no
    longer matches a fresh extraction -- meaning the committed report is
    stale relative to the current drawn geometry and `--fullchip-extract`
    needs re-running, not that this module should silently keep composing
    from a number that no longer describes what is on disk.
    """
    region_payload = {"ring1": ring_payloads["ro_ring11"], "ring2": ring_payloads["ro_ring11_ring2"]}
    region_ports = {"ring1": ring_ports["ro_ring11"], "ring2": ring_ports["ro_ring11_ring2"]}

    def _pin_index(port_map: dict[int, str], pin: str) -> int:
        for idx, name in port_map.items():
            if name == pin:
                return idx
        raise FlowError(f"no resolved port named {pin!r} in {port_map!r}")

    def _fresh_entry(payload: dict, port_map: dict[int, str], pin: str) -> dict:
        net_id = _net_id_at_pin_index(payload, _pin_index(port_map, pin))
        return _parasitics_entry_by_net_id(payload, net_id)

    def _check(name: str, cached_entry: dict, fresh: dict) -> None:
        if (
            abs(fresh["resistance_ohm"] - cached_entry["resistance_ohm"]) > _CLOSE_TOLERANCE_OHM
            or abs(fresh["capacitance_ff"] - cached_entry["capacitance_ff"]) > _CLOSE_TOLERANCE_FF
        ):
            raise FlowError(
                f"{name}: {FULLCHIP_REPORT.relative_to(REPO_ROOT)}'s cached intra-region "
                f"R/C (R={cached_entry['resistance_ohm']} ohm, C={cached_entry['capacitance_ff']} "
                f"fF) no longer matches a fresh extraction (R={fresh['resistance_ohm']} ohm, "
                f"C={fresh['capacitance_ff']} fF) -- the committed report is stale relative to "
                "the current drawn geometry. Re-run `python3 layout/pex/build.py "
                "--fullchip-extract` to refresh it."
            )

    for name, entry in cached["entropy_tap"].items():
        ring_region = entry["ring_region"]
        fresh_ring = _fresh_entry(region_payload[ring_region], region_ports[ring_region], entry["ring_pin"])
        _check(f"{name} (ring)", entry["ring_intra_region"], fresh_ring)
        fresh_cs = _fresh_entry(cs_payload, cs_ports, entry["cs_pin"])
        _check(f"{name} (combiner_sampler)", entry["combiner_sampler_intra_region"], fresh_cs)

    for name, entry in cached["driver_side_load"].items():
        fresh_cs = _fresh_entry(cs_payload, cs_ports, entry["cs_pin"])
        _check(f"{name} (combiner_sampler)", entry["combiner_sampler_intra_region"], fresh_cs)


FULLCHIP_HEADER = """* GENERATED by layout/pex/build.py -- do not edit by hand.
* Post-layout, FULL-CHIP-DELTA-annotated drop-in replacement for {source},
* extending sampler_core.routed.extracted.spice with the two-net inter-
* region delta DR-0025 authorises: klt extract --parasitics --pdk {pdk}
* over the composed, routed layout/floorplan/trng_floorplan.gds, less what
* ro_ring11(_ring2).routed.extracted.spice and
* combiner_sampler.routed.extracted.spice already carry for that same
* physical net (see layout/pex/reports/fullchip_parasitics.json and this
* file's own module docstring, "Full-chip (inter-region) delta
* composition", for what this captures and what it does not -- DR-0025's
* own stated coverage hole).
* Regenerate with: python3 layout/pex/build.py --fullchip-extract && python3 layout/pex/build.py
"""


def _pi_delta_lines(prefix: str, from_node: str, to_node: str, delta: dict) -> list[str]:
    """A symmetric pi-model two-terminal lumped RC segment (`C/2` at each
    end, `R` in series between them) for one net's own delta -- the
    standard lumped approximation of a distributed line when only the net's
    own total R and total C (not a per-position breakdown) are available.
    See the module docstring, "Full-chip (inter-region) delta composition".
    """
    c_half_f = delta["capacitance_ff"] * 1e-15 / 2
    return [
        f"c{prefix}a {from_node} vsubs {c_half_f:.6e}",
        f"r{prefix} {from_node} {to_node} {delta['resistance_ohm']:.6f}",
        f"c{prefix}b {to_node} vsubs {c_half_f:.6e}",
    ]


def _sampler_core_fullchip_subckt(report: dict) -> str:
    """`sampler_core.routed.extracted.spice`'s own topology
    (`_sampler_core_routed_subckt`), with DR-0025's `ro1`/`ro2` delta
    inserted between each ring wrapper's `ro` port and
    `combiner_sampler_routed_extracted`'s `rn1`/`rn2` port, plus the
    disclosed driver-side-only output load on `raw_bit`/`raw_valid`/
    `ring_bit1`/`ring_bit2` (a grounded capacitor at each pin -- no series R,
    since no receiver device exists on the other end of that trunk to
    justify one -- see the module docstring)."""
    entropy = report["entropy_tap"]
    loads = report["driver_side_load"]
    ro1 = next(n for n in _entropy_tap_nets() if n["name"] == "ro1")
    ro2 = next(n for n in _entropy_tap_nets() if n["name"] == "ro2")

    lines = [
        ".subckt sampler_core_fullchip_extracted en1 en2 vddr1 vddr2 vdd vss "
        "clk rst_n raw_bit raw_valid ring_bit1 ring_bit2 vsubs"
    ]
    lines.append("xr1 en1 dro1 vddr1 vss vsubs ro_ring11_routed_extracted")
    lines.append("xr2 en2 dro2 vddr2 vss vsubs ro_ring11_ring2_routed_extracted")
    lines += _pi_delta_lines("delta1", "dro1", "rn1", entropy[ro1["name"]]["delta"])
    lines += _pi_delta_lines("delta2", "dro2", "rn2", entropy[ro2["name"]]["delta"])
    lines.append(
        "xcs rn1 rn2 vdd vss clk rst_n raw_bit raw_valid ring_bit1 ring_bit2 vsubs "
        "combiner_sampler_routed_extracted"
    )
    for name, port in (
        ("raw_bit", "raw_bit"),
        ("raw_valid", "raw_valid"),
        ("ring_bit1", "ring_bit1"),
        ("ring_bit2", "ring_bit2"),
    ):
        c_f = loads[name]["delta"]["capacitance_ff"] * 1e-15
        lines.append(f"cload_{name} {port} vsubs {c_f:.6e}")
    lines.append(".ends")
    return "\n".join(lines) + "\n"


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


# --------------------------------------------------------------------------- #
# Noise-tapped ring variant (issue #217, closing this document's own §7.5
# residual). See the module docstring, "Per-stage noise injection".
# --------------------------------------------------------------------------- #

#: The two device models `--pdk gf180mcuD` binds this design's extracted
#: devices onto. `_gate_nodes()` refuses to classify a card naming anything
#: else, because the "node field 2 is the gate" rule below is a property of
#: these two PDK subcircuits' own pin order, not a general SPICE truth.
_TAP_DEVICE_MODELS = ("nfet_03v3", "pfet_03v3")

#: Field index of the gate on an `nfet_03v3`/`pfet_03v3` instance card as
#: `klt extract` writes it -- `X<name> <n1> <g> <n3> <b> <model> ...`, i.e.
#: field 0 is the card name, fields 1..4 are nodes and field 5 is the model.
#: Cross-checked against this design's own extractions rather than assumed:
#: the always-on starving devices (`L=2U`) come back with their gate on
#: `vddr` (nfet) and `vss` (pfet), which is exactly how those cells are
#: drawn, and every inverter device comes back with its gate on the stage
#: input it is drawn on.
_GATE_FIELD = 2
_DEVICE_NODE_FIELDS = 4

#: Prefix for the receiver-side hub a tapped net is split onto. Indexed by
#: the tap's own position in `_tap_positions()`'s output, NOT by a net name:
#: the whole point of this construction is that it needs no semantic name
#: for the ten internal ring nets, only the extraction's own header order.
_TAP_PREFIX = "rx"

#: The four `.SUBCKT` ports of an assembled ring that are NOT ring nets.
#: Everything else in the header is one of the eleven inter-stage nets a
#: per-stage noise source has to sit on.
_RING_NON_SIGNAL_PORTS = ("en", "vddr", "vss", "vsubs")

#: An 11-stage ring has exactly eleven tappable nets (the NAND output, nine
#: stage outputs, and the ring output `ro` that closes the loop back into
#: the NAND). Asserted rather than assumed -- a ring whose extraction stops
#: matching this shape must fail loudly, not silently tap a different set.
_RING_TAP_COUNT = 11


def _subckt_header(text: str, name: str) -> tuple[list[str], list[int]]:
    """`(port tokens, source line indexes)` for one raw `.SUBCKT` header,
    continuation lines folded."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        match = re.match(rf"^\.SUBCKT\s+{re.escape(name)}\s*(.*)$", line, re.IGNORECASE)
        if not match:
            continue
        tokens = match.group(1).split()
        idx = [i]
        j = i + 1
        while j < len(lines) and lines[j].startswith("+"):
            tokens += lines[j][1:].split()
            idx.append(j)
            j += 1
        return tokens, idx
    raise FlowError(f"no `.SUBCKT {name}` header in the extracted netlist")


def _gate_nodes(text: str, name: str) -> set[str]:
    """Every node an `nfet_03v3`/`pfet_03v3` card in `text` uses as its gate.

    Raises rather than guessing on any card whose arity or model is not the
    one `_GATE_FIELD` assumes: a misclassified gate would split a net at the
    wrong place and quietly simulate a different circuit.
    """
    gates: set[str] = set()
    for line in text.splitlines():
        if line[:1].upper() != "X":
            continue
        fields = line.split()
        if len(fields) < _DEVICE_NODE_FIELDS + 2:
            raise FlowError(
                f"{name}: device card {fields[0]!r} has fewer than "
                f"{_DEVICE_NODE_FIELDS} nodes plus a model name"
            )
        model = fields[_DEVICE_NODE_FIELDS + 1]
        if model not in _TAP_DEVICE_MODELS:
            raise FlowError(
                f"{name}: device card {fields[0]!r} instantiates {model!r}, not "
                f"one of {_TAP_DEVICE_MODELS} -- this module cannot say which "
                f"of its nodes is the gate"
            )
        gates.add(fields[_GATE_FIELD])
    if not gates:
        raise FlowError(f"{name}: no device cards found to classify")
    return gates


def _tap_positions(pin_count: int, port_map: dict[int, str]) -> list[int]:
    """Header positions of the eleven ring nets: every `.SUBCKT` port that
    flat extraction promoted which is not one of the ring's four non-signal
    ports. Includes `ro`, which is both a true external port and the net
    that closes the loop into the NAND's own `a` input."""
    skip = {idx for idx, nm in port_map.items() if nm in _RING_NON_SIGNAL_PORTS}
    positions = [idx for idx in range(pin_count) if idx not in skip]
    if len(positions) != _RING_TAP_COUNT:
        raise FlowError(
            f"expected {_RING_TAP_COUNT} tappable ring nets in a {pin_count}-pin "
            f"assembled ring extraction, found {len(positions)} -- this ring's "
            f"extraction no longer has the shape the per-stage noise tap assumes"
        )
    return positions


def _noise_tapped(text: str, raw_subckt: str, positions: list[int]) -> str:
    """Split each tapped net's parasitic star hub into a driver-side hub (the
    existing header token) and a receiver-side hub (`rx<j>`, a new port)
    carrying only that net's gate-connected terminals.

    See the module docstring, "Per-stage noise injection". Tie `rx<j>` to its
    own header token and the result is this same subcircuit: a 0 V source is a
    short, so every terminal's star resistance, the net's grounded
    capacitance, and therefore every terminal-to-terminal path are untouched.
    `layout/tests/test_pex_noise_tap.py` holds that to BYTE equality against
    the committed untapped netlist.
    """
    tokens, header_lines = _subckt_header(text, raw_subckt)
    gates = _gate_nodes(text, raw_subckt)
    hubs = {tokens[p]: f"{_TAP_PREFIX}{j}" for j, p in enumerate(positions)}
    if len(hubs) != len(positions):
        raise FlowError(
            f"{raw_subckt}: two tapped header positions carry the same token -- "
            f"they cannot be split onto two distinct receiver hubs"
        )

    moved = dict.fromkeys(hubs, 0)
    kept = dict.fromkeys(hubs, 0)
    out: list[str] = []
    for i, line in enumerate(text.splitlines()):
        if i in header_lines:
            if i == header_lines[0]:
                out.append(
                    ".SUBCKT " + " ".join(
                        [f"{raw_subckt}_ntap"] + tokens
                        + [hubs[tokens[p]] for p in positions]
                    )
                )
            continue
        fields = line.split()
        if line[:1].upper() == "R" and len(fields) == 4 and fields[2] in hubs:
            hub = fields[2]
            if fields[1] in gates:
                moved[hub] += 1
                out.append(" ".join([fields[0], fields[1], hubs[hub], fields[3]]))
                continue
            kept[hub] += 1
        elif line.upper().startswith(".ENDS"):
            out.append(f".ENDS {raw_subckt}_ntap")
            continue
        elif line.strip() == f"* cell {raw_subckt}":
            out.append(f"* cell {raw_subckt}_ntap")
            continue
        out.append(line)

    for hub in hubs:
        if moved[hub] == 0:
            raise FlowError(
                f"{raw_subckt}: tapped net at header token {hub!r} has no "
                f"gate-side terminal -- a noise source on its tap would drive "
                f"nothing"
            )
        if kept[hub] == 0:
            raise FlowError(
                f"{raw_subckt}: tapped net at header token {hub!r} has no "
                f"driver-side terminal -- tapping it would float the net"
            )
    return "\n".join(out) + "\n"


def _ring_routed_ntap_subckt(
    name: str, raw_subckt: str, pin_count: int, port_map: dict[int, str],
    positions: list[int],
) -> str:
    """The `_ring_routed_subckt` wrapper again, with each tapped net's pair of
    hubs exposed so a testbench can place a series source between them.

    Port order after the base interface is `<net> <net>__rx` for each tapped
    position in header order, with `<net>` omitted where it is already a base
    port (`ro`). That order is the contract with
    `sim/tb/sampler-array-digitize-extracted-routed/`'s instantiation line and
    is restated in the generated file's own banner.
    """
    args = _positional_args(pin_count, port_map, "n")
    tail: list[str] = []
    tap_args: list[str] = []
    for p in positions:
        label = args[p]
        if label != "ro":
            tail.append(label)
        tail.append(f"{label}__rx")
        tap_args.append(f"{label}__rx")
    lines = [f".subckt {name} en ro vddr vss vsubs " + " ".join(tail)]
    lines.append(f"xcore {' '.join(args + tap_args)} {raw_subckt}_ntap")
    lines.append(".ends")
    return "\n".join(lines) + "\n"


def _ntap_port_order(pin_count: int, port_map: dict[int, str], positions: list[int]) -> str:
    args = _positional_args(pin_count, port_map, "n")
    tail: list[str] = []
    for p in positions:
        label = args[p]
        if label != "ro":
            tail.append(label)
        tail.append(f"{label}__rx")
    return " ".join(tail)


NTAP_HEADER = """* GENERATED by layout/pex/build.py -- do not edit by hand.
* NOISE-TAPPED variant of {raw} ({stem}.routed.extracted.spice): the same
* cards and the same parasitics, with each of this ring's {count} inter-stage
* nets split into a driver-side hub (its existing `.SUBCKT` header token)
* and a receiver-side hub `{prefix}<j>` carrying only that net's
* gate-connected terminals. Both are ports, so a testbench can place a
* series `trnoise` source between them; tie each pair together and this
* subcircuit is ELECTRICALLY IDENTICAL to {raw} -- a 0 V source is a short,
* so every star resistance and the net's grounded capacitance are untouched.
* That equivalence is held to BYTE equality by
* layout/tests/test_pex_noise_tap.py, which un-taps this file and compares
* it against the committed untapped one.
* Exists because ngspice cannot insert a series source inside a subcircuit
* and, at routing level, the inter-stage wire IS inside one. See
* layout/pex/build.py's module docstring, "Per-stage noise injection".
* Regenerate with: python3 layout/pex/build.py
"""

NTAP_BUNDLE_HEADER = """* GENERATED by layout/pex/build.py -- do not edit by hand.
* The DUT bundle sim/tb/sampler-array-digitize-extracted-routed/ needs, and
* nothing else: the two NOISE-TAPPED routing-level rings behind clean
* wrappers, plus the leaf-level `xor2` and `sampler_dff` extractions.
* That deck restates ro_array_core's top-level wiring in its own fragment
* (its pre-layout ancestor already did, and its manifest says why), so what
* it needs from layout/pex/ is the cell library, not a composed core.
* PARTIAL BY CONSTRUCTION, and deliberately so: the two rings are
* routing-level, `xor2`/`sampler_dff` are leaf-level. That is exactly the
* leaf-level deck's own topology with the rings swapped, which is what makes
* the leaf-vs-routed delta attributable to the ring routing -- the only
* place that testbench's entropy comes from. Substituting
* `combiner_sampler_routed_extracted` would also have changed the TOPOLOGY
* (it carries two `ro_buf` instances and the two ring-liveness samplers that
* this deck's pre-layout ancestor does not instantiate).
* Each ring wrapper's tapped ports follow its base `en ro vddr vss vsubs`
* interface in this order -- the contract with that testbench's own
* positional instantiation line:
*   ro_ring11_routed_ntap:       {order1}
*   ro_ring11_ring2_routed_ntap: {order2}
* Regenerate with: python3 layout/pex/build.py
"""


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

    # -- Noise-tapped ring variant (issue #217 §7.5) -- see module docstring. --
    tap_positions = {}
    for name, _gds, _top, _mod, _nand, _stage in ASSEMBLED_RINGS:
        payload = ring_payloads[name]
        positions = _tap_positions(payload["pin_count"], ring_ports[name])
        tap_positions[name] = positions
        raw_path = outdir / f"{name}.routed.extracted.spice"
        (outdir / f"{name}.routed.ntap.extracted.spice").write_text(
            NTAP_HEADER.format(
                raw=name, stem=name, count=_RING_TAP_COUNT, prefix=_TAP_PREFIX
            )
            + _noise_tapped(raw_path.read_text(), name, positions)
        )

    ntap_bundle = (
        NTAP_BUNDLE_HEADER.format(
            order1=_ntap_port_order(
                ring1_payload["pin_count"], ring_ports["ro_ring11"],
                tap_positions["ro_ring11"],
            ),
            order2=_ntap_port_order(
                ring2_payload["pin_count"], ring_ports["ro_ring11_ring2"],
                tap_positions["ro_ring11_ring2"],
            ),
        )
        + '.include "ro_ring11.routed.ntap.extracted.spice"\n'
        + '.include "ro_ring11_ring2.routed.ntap.extracted.spice"\n'
        + '.include "xor2.extracted.spice"\n'
        + '.include "sampler_dff.extracted.spice"\n'
        + "\n"
        + _ring_routed_ntap_subckt(
            "ro_ring11_routed_ntap", "ro_ring11", ring1_payload["pin_count"],
            ring_ports["ro_ring11"], tap_positions["ro_ring11"],
        )
        + "\n"
        + _ring_routed_ntap_subckt(
            "ro_ring11_ring2_routed_ntap", "ro_ring11_ring2",
            ring2_payload["pin_count"], ring_ports["ro_ring11_ring2"],
            tap_positions["ro_ring11_ring2"],
        )
    )
    (outdir / "ro_ring_pair.routed.ntap.extracted.spice").write_text(ntap_bundle)

    # -- Full-chip (inter-region) delta composition (issue #232, DR-0025). --
    # Reads the COMMITTED fullchip_parasitics.json report (written by
    # `--fullchip-extract`, never by this unconditional path -- see the
    # module docstring) and reconciles it against the ring1/ring2/
    # combiner_sampler extractions this same build() call already ran
    # above, cheaply, on every run/--check. Raises FlowError (via
    # `_reconcile_cached_report`) if the committed report is stale relative
    # to a fresh intra-region extraction.
    #
    # UNCONDITIONAL, deliberately: composing this file only `if
    # FULLCHIP_REPORT.is_file()` would make `--check` silently PASS on a
    # stale committed `sampler_core.fullchip.extracted.spice` whenever the
    # report went missing, because `--check` only compares files a rebuild
    # actually produced. A missing report is a hard error with an
    # instruction, not a skipped step.
    if not FULLCHIP_REPORT.is_file():
        raise FlowError(
            f"{FULLCHIP_REPORT.relative_to(REPO_ROOT)} is missing -- the full-chip "
            "delta composition (DR-0025) cannot be rebuilt without it. Run "
            "`python3 layout/pex/build.py --fullchip-extract` to regenerate it "
            "(expensive: see FULLCHIP_TIMEOUT_S's own docstring and this module's "
            "docstring, 'The expensive step is never on build()'s unconditional path')."
        )
    fullchip_report = json.loads(FULLCHIP_REPORT.read_text())
    _reconcile_cached_report(fullchip_report, ring_payloads, ring_ports, cs_payload, cs_ports)

    sampler_core_fullchip = (
        FULLCHIP_HEADER.format(source="design/sampler_core.spice", pdk=PDK_VARIANT)
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
        + _sampler_core_fullchip_subckt(fullchip_report)
    )
    (outdir / "sampler_core.fullchip.extracted.spice").write_text(sampler_core_fullchip)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="rebuild to scratch, compare to committed output")
    parser.add_argument("--require-tools", action="store_true", help="fail instead of skipping when klt/PDK are absent")
    parser.add_argument(
        "--fullchip-extract",
        action="store_true",
        help=(
            "re-run the expensive klt extract --parasitics over the composed "
            "layout/floorplan/trng_floorplan.gds (DR-0025) and refresh the committed "
            "layout/pex/reports/fullchip_parasitics.json delta report. NOT part of the "
            "default build/--check path -- see FULLCHIP_TIMEOUT_S's own docstring for why."
        ),
    )
    parser.add_argument(
        "--reuse-cache",
        action="store_true",
        help=(
            "with --fullchip-extract: recompute the delta report from the LAST run's "
            "cached raw extraction (layout/.work/pex-fullchip/, gitignored) instead of "
            "re-extracting. For iterating on the composition -- the report it writes "
            "records from_cache: true, and is not a fresh measurement."
        ),
    )
    args = parser.parse_args(argv)
    if args.reuse_cache and not args.fullchip_extract:
        parser.error("--reuse-cache is only meaningful with --fullchip-extract")

    if shutil.which("klt") is None or resolve_pdk() is None:
        msg = "klt and/or the gf180mcu PDK are not available -- skipping layout/pex/build.py"
        if args.require_tools:
            print(f"error: {msg}", file=sys.stderr)
            return 1
        print(msg)
        return 0

    if args.fullchip_extract:
        try:
            report = run_fullchip_extraction_and_report(
                FULLCHIP_WORK_DIR, reuse_cache=args.reuse_cache
            )
        except FlowError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"wrote {FULLCHIP_REPORT.relative_to(REPO_ROOT)}")
        for name, entry in report["entropy_tap"].items():
            d = entry["delta"]
            print(f"  {name}: delta R={d['resistance_ohm']} ohm, C={d['capacitance_ff']} fF")
        for name, entry in report["driver_side_load"].items():
            d = entry["delta"]
            print(f"  {name}: delta C={d['capacitance_ff']} fF (output load only)")
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
