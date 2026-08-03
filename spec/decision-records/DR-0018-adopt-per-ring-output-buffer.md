---
dr: DR-0018-adopt-per-ring-output-buffer
title: Adopt the per-ring output buffer into the shipped entropy-source schematic
status: Proposed
date: 2026-08-02
deciders: Proposed by #78 (Builder). NOT ratified -- acceptance is an operator decision, as DR-0001…DR-0004, DR-0007, DR-0010…DR-0012, DR-0015…DR-0017 were.
supersedes: n/a
superseded_by: n/a
related: "#78 (this record), #75/#80 (the measurement this record adopts -- sim/characterization-ring-buffer-mitigation.md), #51/PR #67 (measured the 27.10x/28.6x coupling this record's mitigation addresses), #16/#77 (layout/floorplan/README.md's mitigation proposal), #65/#71/DR-0016 (the ro1/ro2 observation pins this record re-drives), #13/#12 (PVT sizing and worst-corner entropy, both due for a re-run against the adopted array), #14 (time-to-first-valid, likewise); DR-0007 §1/§2 (topology and the sizing law this record does not change), DR-0007 §2's per-ring sigma_acc measurement rule (unchanged, explicitly not relaxed by this record)"
---

# DR-0018: Adopt the per-ring output buffer into the shipped entropy-source schematic

## Status

- 2026-08-02: Proposed, by #78. Not ratified.

## Context

### The mechanism this record adopts a fix for

[`sim/characterization-array-ring-coupling.md`](../../sim/characterization-array-ring-coupling.md)
(issue #51 / PR #67) measured that a ring driving the array's XOR combiner
alongside a switching neighbour shows `sigma_1` **27.10x-28.6x** higher than
the same ring with a quiet neighbour, at `tt`/27 C/3.30 V -- charge injected
*backwards* into the ring node through the gate capacitance of the
combiner's own input stage, a shared electrical node by construction, not a
layout adjacency. `sim/tools/array_sizing.py`'s sizing law is derived from
each ring's *own*, independent statistics; a coupling term of that size
measured with the neighbour switching is not admissible evidence for it
(DR-0007 §2's measurement rule, ratified by `layout/floorplan/README.md`'s
"The measurement rule" section, unchanged by this record -- see
"Consequences").

`layout/floorplan/README.md` (issue #16) proposed a mitigation -- one
minimum-width inverter buffer per ring, between the ring node and *every*
consumer -- and explicitly declined to adopt it, because nothing had
measured whether it worked. Issue #75 (recorded in
[`sim/characterization-ring-buffer-mitigation.md`](../../sim/characterization-ring-buffer-mitigation.md))
built the buffer in two isolated testbenches (never in the committed
schematic) and measured it directly:

- **Coupling.** Against a matched quiet-neighbour control at the same
  buffered operating point, the coupling factor falls from **27.10x to
  2.87x** -- 92.8 % of the excess removed, not all of it. Squared (what
  DR-0007 §2 substitutes for a per-ring contribution), 2.87x is still an
  8.24x over-statement, still in the unsafe (undersized-array) direction.
- **Power.** At `ff`/-40 C/3.63 V (the power-binding corner), the buffered
  array's own measured total is **395.06 uW** against the unbuffered
  array's **415.27 uW** -- a **19.1 uW saving** (-4.9 %), not the ~24.4 uW
  *cost* `layout/floorplan/README.md`'s pre-measurement estimate projected.
  The saving is not where the estimate looked: each ring's own power is
  flat to slightly up (it spends the lighter load's per-cycle saving on
  running 6.7 % faster instead), the two buffers cost 2.5x the estimate
  (61.8 uW combined), and the combiner's own current drops 58.8 % once it is
  driven by the buffer's fast, un-starved edges instead of the ring's slow,
  starved ones -- an effect the estimate did not consider at all, and the
  effect that ends up dominating.

Issue #75's own scope stopped there: "adopting it edits the shipped
schematic and every downstream artefact that is derived from it, and this
repository puts a design change through a decision record rather than
through a summary document." This record is that decision.

## Decision

We will re-wire `design/xschem/ro_array_core.sch` so that each ring drives
its own dedicated output buffer -- a new reusable cell,
`design/xschem/ro_buf.sch`/`.sym` -- ahead of the XOR combiner, and re-export
`design/ro_array_core.spice` (and every netlist that instantiates it:
`ro_array_core_meta.spice`, `sampler_core.spice`, `trng_top.spice`) from that
schematic.

### Mechanism

`ro_buf` is a single minimum-width, UNSTARVED CMOS inverter --
`pfet_03v3 W=0.44u` / `nfet_03v3 W=0.22u`, both `L=0.28u` -- device-for-device
identical to `xor2`'s own input-stage inverter, carrying the same
`ad`/`as`/`pd`/`ps`/`nrd`/`nrs` diffusion-geometry expressions every device in
the committed netlists carries. It is the same device #75's testbenches
already measured; this record wires that exact cell into the shipped
schematic rather than a testbench-only expansion.

Each ring's own last stage drives one `ro_buf` instance, and `ro_array_core`'s
exported `ro1`/`ro2` pins -- the DR-0016 liveness-digitizer taps, added by
#65 -- are re-driven from the **buffer's output**, not from the ring
directly:

```
xr1 en1 rn1 vddr1 vss ro_ring11 ...      ring's own last stage -> internal node rn1
xr2 en2 rn2 vddr2 vss ro_ring11 ...      ring's own last stage -> internal node rn2
xb1 rn1 ro1 vdd vss ro_buf                buffer 1: rn1 -> ro1 (exported)
xb2 rn2 ro2 vdd vss ro_buf                buffer 2: rn2 -> ro2 (exported)
xa1 ro1 ro2 xo vdd vss xor2                combiner now driven by ro1/ro2 (buffered)
```

`ro1`/`ro2` are consumed in exactly two places, and both now see the buffered
node with **no change to either consumer**: `xa1` (wired inside this same
cell, automatically) and, one level up in `sampler_core.sch`, the two
DR-0016 `sampler_dff` liveness digitizers (`xsr1`/`xsr2`, unmodified --
`sampler_core.sch`'s own port-to-port wiring is untouched by this record).

**Two separate buffer instances, never one shared.** A single buffer feeding
both combiner inputs would recreate exactly the shared node the mitigation
exists to remove -- the same requirement `layout/floorplan/README.md` and
#75's own testbenches state.

**Buffer supply.** Both buffers run off `vdd`/`vss` -- the block/combiner
supply `xa1` already uses -- not off either ring's `vddr1`/`vddr2`. This is
a deliberate choice, not an incidental one: DR-0007's independence
requirement and DR-0016's per-ring liveness monitor both rely on each
ring's own supply pin carrying *only* that ring's own current (a stopped
ring's supply current collapses more than four orders of magnitude). Tying
the buffer to the ring's own `vddr` would add the buffer's switching current
to that signature; tying it to the block supply instead means adopting the
buffer changes **neither** ring's own `vddr1`/`vddr2` branch, and
`sim/tb/ro-array-core-power/`'s existing per-branch metering
(`i_r1_a`/`i_r2_a` on `vddr1`/`vddr2`, `i_tree_a` on `vdd`) continues to
read "each ring's own current" and "everything downstream of the ring"
respectively, unchanged in meaning, with the buffer's own cost now folded
into the `i_tree_a`/`p_tree` term alongside the combiner's. No new port is
added to `ro_array_core`'s pin list, and every existing testbench that
instantiates it (`sim/tb/ro-array-core-power/`, `ro-array-core-pvt-q/`,
`ro-array-core-mc-freq/`, `ro-array-core-xo-slew/`,
`ring-liveness-tap-power/`) needs no netlist edit of its own, because the
port list (`en1 en2 vddr1 vddr2 vdd vss xo ro1 ro2`, 9 signals) is unchanged
-- only the internal wiring behind `ro1`/`ro2` moved.

**Polarity inverts.** `ro1`/`ro2` are now the COMPLEMENT of their ring's own
internal node. `a XOR b == (NOT a) XOR (NOT b)`, so `xa1`'s output is
bit-identical to the unbuffered case; the DR-0016 liveness digitizer counts
transitions and is polarity-blind; the samplers' entropy does not depend on
polarity. Nothing downstream needs a matching change. `ro_buf.sch`'s and
`ro_array_core.sch`'s own text blocks say so, so a future reader of `ro1`'s
level does not assume it is the ring's own sense.

### What this record does NOT change

- **DR-0007 §1's topology and §2's sizing law.** Still two independent,
  separately-supplied rings, XOR-combined into one node a single sampler
  observes. `Q_array = sum_i kappa_i^2 T_s / T0_i^2` is unchanged; only the
  measured `T0_i` and `P_i` that feed it move (see Consequences).
- **DR-0007 §2's per-ring measurement rule.** The residual 2.87x coupling
  factor is 8.24x squared, still an over-statement in the unsafe direction.
  Per-ring `sigma_acc,i` measured with that ring's combiner neighbour
  switching remains inadmissible as DR-0007 §2 evidence, buffered or not.
  This record does not touch `layout/floorplan/README.md`'s "The measurement
  rule (adopted)" section's substance -- only its "Proposed mitigation"
  section, which now records adoption instead of a proposal.
- **The DR-0016 liveness monitor's mechanism, cutoff, or failure behavior.**
  `ring_liveness.v`, `C_LIVE`, and the latch-and-gate path are untouched;
  only the electrical node the digitizer taps moved from the ring's own
  output to the buffer's output, one level below where DR-0016 operates.
- **The clk-driven liveness-tap coupling path** `layout/floorplan/README.md`
  raises as a still-open, unmeasured concern -- that is #76's scope.
- **The PVT sweep of the residual 2.87x coupling factor** -- that is
  #13/#12's scope. This record's own coupling evidence, like #75's, is one
  corner (`tt`/27 C/3.30 V).

## Alternatives considered

### Leave the schematic unbuffered, keep the mitigation as a documented but unadopted proposal

- **What**: The state `layout/floorplan/README.md` and #75 left the design
  in -- the mitigation measured and recommended, the schematic unchanged.
- **Why plausible**: Avoids moving the shipped array's operating point
  (frequency, power) and avoids re-running every PVT/sizing record family
  that describes it.
- **Why rejected**: #75 already did the expensive, uncertain part (does the
  buffer actually work, and what does it actually cost) and found a
  significant, unambiguous win on both axes measured (92.8 % of the
  coupling excess removed; power *returned*, not spent). Leaving a measured
  improvement unadopted indefinitely, with no further work required to
  realize it, is not a neutral choice -- it ships an array with 27.10x
  avoidable coupling and a needless ~19 uW of headroom left on the table
  against the `< 500 uW` row's binding corner.

### A shared buffer feeding both combiner inputs

- **What**: One buffer, output fanned out to both of `xa1`'s inputs.
- **Why plausible**: Half the device count, half the area (already only
  0.06 % of the area row, so this saving is immaterial).
- **Why rejected**: Recreates exactly the shared electrical node the
  mitigation exists to remove -- a coupling path landing on the shared
  buffer output would inject back into *both* rings simultaneously through
  one low-impedance node, the opposite of the isolation this record adopts.
  `layout/floorplan/README.md` and #75's own testbenches already state this
  requirement; this record does not reopen it.

### Buffer supply from each ring's own `vddr`

- **What**: `xb1`/`xb2` powered from `vddr1`/`vddr2` instead of the block
  `vdd`/`vss`.
- **Why plausible**: Keeps "per-ring" wiring visually co-located with the
  ring it buffers, and needs no new supply-domain reasoning.
- **Why rejected**: Adds the buffer's own switching current to the exact
  signal DR-0007's independence requirement and DR-0016's liveness monitor
  both rely on being a *pure* per-ring signature (a stopped ring's current
  collapsing more than four orders of magnitude). Powering the buffer from
  the buffer's actual consumer domain (the block/combiner supply, which
  `xa1` already uses) keeps that signature untouched and needs no new pin on
  `ro_array_core`.

## Consequences

- **Positive**:
  - 92.8 % of the measured 27.10x ring-to-ring coupling excess is removed in
    the shipped array, not just in a testbench.
  - The block's active-power rollup at the binding corner (`ff`/-40 C/
    3.63 V) improves: the entropy source measures **393.1 uW** in the
    `ro-array-core-power` re-run and **393.2 uW** in the `ro-array-core-pvt-q`
    re-run (the two families agree to 3.3e-04 across everything they both
    measure), against the pre-adoption **415.3 uW**. `power_rollup.py` reads
    the `pvt-q` figure and totals the block at **433.2 uW, 86.6 %** of the
    `< 500 uW` row, down from 454.2 uW / 90.8 % -- headroom *gained*, not
    spent.
  - Adds 0.06 % to the area row (two minimum-width inverters), per
    `layout/floorplan/README.md`'s area rollup -- immaterial.
  - No change to any downstream consumer's port list, wiring, or logic:
    `sampler_core.sch`, `trng_top.v`/`.py`, and every already-shipped
    testbench that instantiates `ro_array_core` by its existing 9-signal
    port list need no edit.
- **Negative / accepted cost**:
  - **The array's operating point moves.** Ring frequency +6.7 %
    (`f_r1`: 233.3 MHz -> 249.0 MHz at `ff`/-40 C/3.63 V), total power
    -4.9 % at the same corner. Every record family that describes the
    shipped array's PVT behavior (`ro-array-core-power`,
    `ro-array-core-pvt-q`, `ro-array-core-startup`) needed a re-run to
    describe the array as it now ships; that re-run is the bulk of this
    record's own PR (see "Re-run evidence" below). Pre-adoption records
    under those same slugs are **not** edited or deleted (`sim/records/` is
    append-only) and remain true of what they measured -- they describe the
    unbuffered array and no longer describe the shipped one.
  - **Four record families that touch the array are NOT re-run by this
    record**, each with a stated reason rather than an omission. The full
    list, and why each one's existing evidence survives adoption, is in
    `design/README.md` § "Erratum: which array-cell records predate the
    per-ring output buffer (#78)": `ro-array-core-xo-slew` (used only as a
    divisor, and the buffer moves it in the safe direction),
    `ro-array-core-mc-freq` (a *ratio* spread, and the buffer is identical on
    both rings), `ro-array-core-meta-power` / `ring-liveness-tap-power` (both
    measure a delta against a baseline that moved -4.9 %),
    `sampler-core-idle-leakage` (two more static minimum-width devices inside
    a row whose 4.5x miss is 99 % a digital-leakage estimate) and
    `sampler-array-digitize` (hand-restates the array rather than
    instantiating it; the unbuffered restatement is the harder case for the
    question it asks). What this record does NOT claim is that any of those
    is unaffected -- only that its conclusion survives the shift, and the
    direction of the shift is stated in each case.
  - **DR-0015's entropy-binding corner is re-derived and unchanged.**
    `sim/tools/worst_corner_entropy.py --check` ranks `Q` over the re-run
    27-point `pvt-q` grid and still finds `ss`/+125 C/3.63 V minimizes it at
    every sizing constant checked -- the buffer moves every corner's `P` and
    `T0` together rather than re-ordering them. What is still pre-adoption
    inside that tool is its Monte Carlo device-mismatch section, which reads
    `ro-array-core-mc-freq` (above).
  - **Polarity of `ro1`/`ro2` inverts**, documented in the schematic text and
    above, with no functional consequence traced.
- **Follow-up required**:
  - Re-run `sim/tb/ro-array-core-mc-freq/` so the Monte Carlo mismatch half
    of `sim/tools/worst_corner_entropy.py` describes the buffered array too.
    Not required for this record's own acceptance criteria
    (`array_sizing.py --check`, `power_rollup.py --check` and
    `worst_corner_entropy.py --check` all pass against this record's re-run
    data -- see below).
  - `sim/characterization-ring-buffer-mitigation.md`,
    `sim/characterization-startup-and-power-budget.md`,
    `layout/floorplan/README.md`'s mitigation section, `design/README.md` and
    the root `README.md`'s Power row are updated by this record's own PR to
    state adoption and to carry the re-run numbers. None needed a structural
    rewrite; the two characterization documents are annotated rather than
    rewritten, because what they measured stays true of the array they
    measured.
- **Revisit if**: a future mismatch re-run under the follow-up above finds
  the Monte Carlo independence margin materially changed by the buffer's
  adoption (not expected, per the uniform-shift argument above, but not yet
  confirmed either).

## Re-run evidence

Every number in "What it costs" and "What it buys" above, and the schematic
change itself, are reproducible with:

```sh
python3 design/netlist.py --check                       # schematic -> netlist, unchanged
python3 sim/run_corners.py ro-array-core-power --corners ff --temps -40 --supply 3.63 --supply-tol 0
python3 sim/run_corners.py ro-array-core-power --corners ss --temps -40 --supply 3.63 --supply-tol 0
python3 sim/run_corners.py ro-array-core-power --corners tt --temps 27 --supply 3.3 --supply-tol 0
python3 sim/run_corners.py ro-array-core-pvt-q --corners tt ff ss --temps -40 27 125
python3 sim/run_corners.py ro-array-core-startup --corners tt ff ss --temps -40 27 125
python3 sim/tools/array_sizing.py --check
python3 sim/tools/power_rollup.py --check
python3 sim/tools/worst_corner_entropy.py --check
python3 sim/tools/time_to_first_valid.py --check
```

**Two generations of the same corner now exist**, for the first time in this
repository's history: an appended re-run does not remove what it re-measures.
Every tool above therefore had to be told which generation describes the
shipped array, and all four now resolve it the same way -- **one record per
PVT corner, the newest measurement of that corner wins**
(`power_rollup.by_corner`, `array_sizing.dedupe_by_corner`,
`worst_corner_entropy.shipped_points`, `time_to_first_valid.dedupe_by_corner`).
This is deliberately NOT `sim/README.md`'s superseding mechanism, which marks
a run *mistaken*; the pre-adoption records are not mistaken, they simply
measure a circuit that is no longer built, and they keep `status: valid`.

- **`ro-array-core-power`** (3 points, the power-binding-corner set):
  [`2026-08-02-ro-array-core-power-01`](../../sim/records/2026-08-02-ro-array-core-power-01.md)
  (`ff`/-40 C/3.63 V), [`-02`](../../sim/records/2026-08-02-ro-array-core-power-02.md)
  (`ss`/-40 C/3.63 V), [`-03`](../../sim/records/2026-08-02-ro-array-core-power-03.md)
  (`tt`/27 C/3.30 V).
- **`ro-array-core-pvt-q`** (the full 27-point covered grid):
  `sim/records/2026-08-02-ro-array-core-pvt-q-{28..54}.md`.
- **`ro-array-core-startup`** (the same 27-point grid):
  `sim/records/2026-08-03-ro-array-core-startup-{01..27}.md`.

  This family could not be re-run as it stood, because of a **latent,
  pre-existing breakage unrelated to this record's own change**: its `xdut`
  line supplied 7 nodes, matching `ro_array_core`'s port list *before* #65
  added the `ro1`/`ro2` observation pins, and was never updated when that
  port list grew to 9 -- the deck's own last change (#72) predates #65 and it
  was never re-run in between, so nothing caught it. The same 7-node call
  fails identically ("Too few parameters for subcircuit type ro_array_core")
  against the unbuffered, pre-#78 netlist on `origin/main` today. Fixing it
  needed one more decision than adding two node names, because the same #65
  change also broke the deck's *measurements*: it addresses each ring's own
  output node, and #65 turned that node into a port, which ngspice reports
  under its flat top-level name only, so `v(xdut.ro1)` stops resolving. Since
  this record makes the ring's own node internal again (as `rn1`/`rn2`, with
  `ro1`/`ro2` now driven by the buffers), the deck's measure lines address
  `v(xdut.rn1)`/`v(xdut.rn2)` -- **the same physical node the pre-#65 records
  of this family measured**, which is what keeps two generations of start-up
  times comparable across both changes rather than silently changing what the
  family means. The buffered `ro1`/`ro2` ports are connected and unmeasured;
  what the sampler sees is `xo`, which this deck measures and which *is*
  driven through the buffers.
