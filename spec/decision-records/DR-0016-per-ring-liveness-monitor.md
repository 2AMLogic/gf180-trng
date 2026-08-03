---
dr: DR-0016-per-ring-liveness-monitor
title: Detect a stuck or dead ring by reusing DR-0002's RCT test per ring, and flag (not hard-stop) into the same latch-and-gate path
status: Proposed
date: 2026-08-02
deciders: Proposed by #44 (Builder). NOT ratified -- acceptance is an operator decision, as DR-0001...DR-0004, DR-0007, DR-0010...DR-0012 and DR-0015 were.
supersedes: n/a
superseded_by: n/a
related: "#44 (origin), #65 (integration follow-up -- delivered, see Status/A1), #7 / PR #45 (RO core schematic -- the two observation points this record chooses between), #11 / PR #57 (health-test RTL this monitor lives beside), #26 (design/interface/, the latch-and-gate mechanism this record extends); DR-0001 (raw tap / no exposed per-ring pin), DR-0002 (RCT/APT parameters and failure behavior -- the mechanism and the failure-behavior precedent this record reuses), DR-0007 §Consequences (first flags the per-ring-liveness gap), DR-0009 (behavioral/transistor verification split), DR-0010 §Consequences (N=2 makes one dead ring half the array; the Power row's ~85 uW headroom this record bounds against), DR-0012-sampler-fixed-external-clock (the digitizer's clock source), DR-0014 (sampler_dff's gated-reset cell, reused unmodified as the per-ring digitizer); design/README.md 'Per-ring liveness'; design/health_test/README.md; sim/tb/ring-liveness-fault-injection/, sim/tb/ring-liveness-tap-power/; #76 (phase cost of the same tap -- delivered, see Status/A2 and 'Phase cost'), #51/PR #67 (the coupling topology #76 measures this tap against), #75/#80/#78 and DR-0018 (the per-ring output buffer the digitizers now tap, and which removes 96.5 % of the phase cost), sim/characterization-liveness-tap-phase-cost.md, sim/tb/ring-liveness-tap-phase-{clk-high,clk-low,clocked,buffered,buffered-static}/; #86 (does that phase cost reach the SAMPLED BIT -- delivered, see Status/A3 and 'The bit-level follow-up'), sim/characterization-sampler-bit-bias.md, sim/tb/sampler-bit-bias-{clocked,static}-{integer,generic,clk-floor}/"
---

# DR-0016: Detect a stuck or dead ring by reusing DR-0002's RCT test per ring, and flag (not hard-stop) into the same latch-and-gate path

## Status

- 2026-08-02: Proposed, by #44 (Builder). Not ratified.
- 2026-08-02: **Amendment A1 (#65) -- the two integrations this record left as
  follow-up are built. No decision, parameter, cutoff or mechanism in this
  record changed; the record still stands as Proposed, and A1 only replaces
  "designed to be wired" with "wired". What #65 delivered:**
  - `ring_stuck_any` is the interface's `ht_fail_ring` input, OR'd into
    exactly the latch/alarm/gate this record's "Failure behavior" specified,
    and reported by a new `STATUS.HT_FAIL_RING` bit **at bit 9** -- reserved
    space, so no previously published DR-0013 bit position moved. One bit for
    "a ring stopped", not one per ring, so the published register map does not
    acquire an `N_RINGS` dependency; `ring_stuck[i]` stays a named net in
    `trng_top.v` for a future per-ring report to take from.
  - The `ro1`/`ro2` tap is shipped rather than testbench-only:
    `ro_array_core.sym`/`.sch` carry two **observation-only output pins** (no
    device added, no ring changed -- an unconnected parent netlists to the
    identical circuit, which is why this record's own power measurements below
    still describe the shipped cell), `sampler_core.sch` digitizes them with
    two more unmodified `sampler_dff` instances on the same DR-0012 clock, and
    `trng_top.v`/`.py` instantiate `trng_ring_liveness` beside `rct_apt`.
    The digitizers live in `sampler_core` rather than `ro_array_core` because
    a digitizer needs a clock and the entropy source has none.
  - `sim/tb/ring-liveness-tap-power/` now reaches those nets through the pins
    (`v(ro1)`) instead of ngspice's hierarchical internal-node naming
    (`v(xdut.ro1)`): the same nets, the same circuit, the same numbers -- a
    subcircuit port is simply not addressable as an internal node. The
    measured costs tabulated under "Power/area cost" are unaffected and are
    now the cost of something the design contains.
- 2026-08-03: **Amendment A2 (#76) -- the tap's PHASE cost is measured. No
  decision, parameter, cutoff or mechanism in this record changed; the record
  still stands as Proposed. What changed is that "Power/area cost" was the
  only cost this record priced, and it is not the only cost the tap has.**
  Measured at `tt`/27 C/3.30 V in
  `sim/characterization-liveness-tap-phase-cost.md`: with the digitizer's `d`
  input directly on the ring node (the arrangement this record specified and
  the block shipped up to PR #82), the ring runs at **two different
  frequencies 25.6 % apart** depending on which rail `clk` sits on, and
  alternates between them in lockstep with `clk`. Since PR #82 / DR-0018 the
  digitizer taps a buffer output instead, which removes 96.5 % of that; the
  residual is 19.9x and is still `clk`-locked. See "Phase cost" below.
- 2026-08-03: **Amendment A3 (#86) -- the phase cost A2 records does NOT reach
  the sampled bit. No decision, parameter, cutoff or mechanism in this record
  changed, and DR-0007 is unamended; the record still stands as Proposed.** A2
  measured phase and declined a bit-level claim; #86 earns it. At the same
  corner, on `sampler_core`'s own wiring and across three `clk` rates including
  DR-0003's ratified floor, running the digitizers' clock rather than parking
  it moves the sampled bit's bias by at most 0.82 sigma and its short-lag
  serial correlation by at most 1.68 sigma of the measurement's own resolution,
  pulls neither ring towards lock at either of the two near-integer sampling
  ratios in the sweep, and shifts the ring's mean frequency by the same
  +0.225 % at every rate -- a static-load signature, not injection pulling.
  See "The bit-level follow-up" below and
  `sim/characterization-sampler-bit-bias.md`.

## Context

### The gap, and why DR-0002's existing tests do not close it

[`DR-0007`](DR-0007-multi-ro-xor-combined-entropy-source.md) §Consequences
flags a specific blind spot: a stuck or dead ring is **invisible at the
XOR-combined node**. It contributes a constant, the XOR still toggles (driven
by the surviving ring), and the raw bit stream still looks plausible while the
array has quietly lost part of its jitter budget.
[`DR-0010`](DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md)
raises the stakes: it sizes the shipped array at **N = 2**, so one dead ring
is now **half** the array, not a quarter or an eighth.

[`DR-0002`](DR-0002-health-test-parameters-and-failure-behavior.md)'s RCT and
APT do not catch this **by construction**: "Test inputs and placement" fixes
both tests on the **raw tap** (the sampler's output, i.e. the digitized,
XOR-combined `xo`), not on either ring individually. A half-dead N=2 array's
combined raw stream is still driven by one live, freely-running ring, so it
can sail through both cutoffs indefinitely while true min-entropy has halved.

### The two observation points the schematic already provides

`design/README.md` "Per-ring liveness" (built by #7, PR #45) names two, both
already present in `ro_array_core.sch` without any new pin:

1. **The per-ring supply pin** (`vddr1`, `vddr2`). A stopped ring's supply
   current collapses more than four orders of magnitude -- tens of
   microamps active vs. tens of nanoamps stopped
   (`sim/records/2026-08-01-ro-array-core-power-*.md` against
   `sim/records/2026-08-01-ro-inv-05stage-stopped-leakage-*.md`). This needs a
   bespoke analog current sensor per ring.
2. **The per-ring output as an internal net** (`ro1`, `ro2` inside
   `ro_array_core`). A digital divider/toggle check, no new analog circuit,
   and no new exposed pin -- DR-0001 constrains what the block *publishes*,
   not what it monitors internally.

`design/README.md` names option 2 as "the obvious starting point"; this
record follows it, for the same reason: it needs no new analog sensor design
and it reuses an already-verified digital cell (see Decision).

### What #11's health-test block already establishes, and this record reuses

`design/health_test/rct_apt.py`/`.v` (DR-0002, #11) already implement the
Repetition Count Test: a saturating run-length counter over a raw bit stream,
with cutoff `C_RCT = 1 + ceil(-log2(alpha) / H)` at the ratified `alpha =
2**-40` and the draft `H0 = 0.5` (giving `C_RCT = 81`). That test exists
*specifically* to catch "a sampled bit repeating far more than an
effectively-random source would" -- which is exactly the signature of a
stopped ring, on the ring's own output rather than the combined tap.

## Decision

We will add a **per-ring liveness monitor** to `design/health_test/`
(`ring_liveness.py` / `ring_liveness.v`, `trng_ring_liveness`): **N
independent instances of DR-0002's own RCT test, one per entropy-source
ring**, each observing that ring's own already-digitized sample instead of
the combined raw tap.

### Mechanism

Each ring's digitized bit (`ring_bit[i]`) is fed through a saturating
run-length counter identical in structure to `rct_apt.v`'s RCT counter:
`ring_stuck[i]` pulses for one cycle exactly when that ring's bit has
repeated `C_LIVE` times in a row, then the counter saturates rather than
wrapping (one pulse per stall onset, not a periodic one). `ring_stuck_any` is
the bitwise OR of `ring_stuck`.

**`C_LIVE` defaults to `rct_apt.c_rct(H0)` = 81 -- DR-0002's own draft C_RCT,
reused unchanged, not a new number.** No new min-entropy assumption is
introduced for an individual ring: the justification for treating a ring's
own sampled bit as approximately IID at `H0 = 0.5` is the *same* physical
argument DR-0002 already rests on for the combined tap (an asynchronous
sample of a free-running oscillator with no rational frequency relationship
to the sampling clock -- DR-0007 §1's independence argument -- looks
approximately random to the sampler regardless of which node is sampled). No
per-ring duty-cycle or jitter measurement exists in this repository to
justify a *tighter* number, so this record does not invent one; see "Revisit
if".

Because `C_LIVE` is imported programmatically from `rct_apt.c_rct(rct_apt.H0)`
rather than hard-coded, a future ratified worst-corner `H` (#13) updates both
`C_RCT` and `C_LIVE` from the same one-line edit -- the same "parameter, not
a constant" discipline DR-0002 already requires of `C_RCT` itself.

**Digitization**: `ring_bit[i]` is produced by tapping `ro1`/`ro2` with a
per-ring digitizer that is **structurally identical to the raw tap's own
`sampler_dff`** (DR-0014's gated-reset TG master-slave cell) -- the same cell
that already resolves a rail-to-rail, asynchronous, continuously-toggling
node (`xo`) to a clean logic level within nanoseconds
(`sim/tb/sampler-dff-setup-hold/`). No new analog cell is designed; the
existing, already-characterized cell is reused, clocked by the same DR-0012
fixed external sample clock. This module (`ring_liveness.v`) does not perform
its own synchronization; it assumes `ring_bit` arrives already synchronized,
the same contract `rct_apt.v` already has for `raw_bit`.

**Why RCT only, no per-ring APT**: RCT alone already gives a deterministic,
bounded detection of "ring frozen at a single value" -- the issue's stated
failure mode (a *stuck or dead* ring). A per-ring APT would mostly re-detect
the same failure at worse latency (`2*W` vs. `C_LIVE`) without covering a
materially different, demonstrated fault mode (e.g. "live but heavily
duty-cycle-skewed", for which no measurement or failure evidence exists in
this repository). See "Revisit if".

### Detection latency

**Exactly `C_LIVE` sampler-clock cycles (default 81) after the onset of a
ring holding a constant digitized value.** This is the same class of bound
DR-0002 already states for `C_RCT` ("detected within `C_RCT` samples of
onset") and is verified the same way:
`sim/tb/ring-liveness-fault-injection/run_demo.py` freezes one ring's
digitized bit mid-stream and confirms `ring_stuck[i]` fires within `C_LIVE -
1` samples of onset every time, while the surviving ring's `ring_stuck` bit
never fires
(`sim/records/2026-08-02-ring-liveness-fault-injection-{02,03,04}.md`, the
`ring1-stuck`/`ring2-stuck`/`both-stuck` scenarios).

In absolute time this is **81 us at DR-0003's ratified >= 1 Mbps raw rate**,
or **162 ms at DR-0010's proposed 500 bps** -- both fast relative to the
health-test block's own recovery path (an explicit software clear plus a
1024-sample start-up retest), and far faster than DR-0002's own RCT/APT
latency bounds already accepted for the combined tap (`C_RCT`, `2*W`).

### Failure behavior: flag, not hard stop

**`ring_stuck_any` is designed to be OR'd into the exact same latch-and-gate
mechanism DR-0002 already defines for `ht_fail_rct`/`ht_fail_apt`**: a
latched status bit, a block-level alarm, immediate gating of the
**conditioned** output path only (valid deasserts, `DATA` reads return no new
bits, the output FIFO is flushed), the **raw path stays ungated** (DR-0001) so
the failure can be diagnosed, and recovery is only via an explicit
software clear followed by the full start-up retest. This module itself never
latches or gates anything -- the same "we only ever report" boundary
`rct_apt.v` already draws.

**Why flag, and not a hard stop** (an irreversible disable, a fuse-blow, or
any state that cannot be cleared by software): DR-0002 already made and
justified this choice for the combined-tap failure modes, and a dead ring is
not a different *class* of failure from what DR-0002 already handles --
it is the same underlying fact (the entropy source is compromised) observed
at a different, more direct point. Reusing the identical mechanism means:

- **No new safety property is needed.** DR-0002's "Alternatives considered"
  already rejects "flag only, never gate" (moves the safety property into
  every integrator's firmware) and "gate but self-clear" (a marginal source
  would flap, delivering bits between undetected failures) for reasons that
  apply identically here. A hard stop is strictly *more* than DR-0002's own
  analysis found necessary for a confirmed source failure, and it would
  delete the "let me see it anyway" raw diagnostic escape hatch DR-0002
  deliberately preserved.
- **A genuinely dead ring self-consistently re-fails.** Because recovery is
  never automatic (DR-0002 §4), a software clear on a truly stopped ring
  simply restarts the noise source and the start-up retest; if the ring is
  actually dead, `ring_stuck_any` fires again within `C_LIVE` samples of the
  restart, and the block stays gated. There is no path by which a dead ring
  can "flap" bits out under this mechanism -- the same argument DR-0002 makes
  for its own latching choice.
- **One mechanism, not two.** Software already has to handle `HT_ALARM`;
  adding a structurally different failure state (hard stop) for a
  functionally identical outcome (the entropy source cannot be trusted) would
  double the recovery logic every integrator has to write for no additional
  safety.

### Power/area cost, bounded against DR-0010's Power row

DR-0010 measures the shipped N=2 array at **415 uW** total (`ff`/+10%/-40 C,
the power-binding corner) against the ratified `< 500 uW` row -- **~85 uW of
headroom** (`sim/records/2026-08-01-ro-array-core-power-04.md`).

This record's own cost has two parts:

1. **The RTL itself** (`ring_liveness.v`): a small saturating counter per
   ring (7 bits at the default `C_LIVE = 81`) plus one comparator and one
   register per ring. This repository has no synthesis or gate-level power
   flow for *any* digital RTL block (`design/conditioner/`,
   `design/interface/`, `design/health_test/` all ship with no schematic and
   no netlist, per DR-0009's split, so none has ever had its power/area
   measured here) -- this record does not create a new gap, and this cost is
   the same order of magnitude as the existing `rct_apt.v` RCT counter it
   duplicates, replicated N=2 times.
2. **The electrical tap on `ro1`/`ro2`** -- the part that actually loads the
   analog entropy source and is therefore the part that can spend the Power
   row's headroom. `sim/tb/ring-liveness-tap-power/` measures this directly:
   the shipped array (`design/ro_array_core.spice`, unmodified) with two
   `sampler_dff` instances (the existing raw-tap digitizer cell, unmodified)
   tied to `ro1`/`ro2` via ngspice's hierarchical internal-node addressing --
   the same addressing `sim/tb/ro-array-core-power/`'s own `.measure` lines
   already use to probe those nodes without a new pin -- so nothing in this
   measurement, or in the design it measures, creates an exposed per-ring tap
   (see "No exposed tap" below).

**Measured, at all three of the baseline sweep's points** (`sim/records/2026-08-02-ring-liveness-tap-power-{02,03,04}.md`, directly comparable point for point to the un-tapped baseline `sim/records/2026-08-01-ro-array-core-power-{04,05,06}.md`):

| Corner | Baseline `p_total_w` | Tapped `p_total_w` | Loading delta (`ring_swing`/`p_total_w` only) | Tap's own switching (`p_tap_avg_w`, at this deck's 100 MHz measurement clock) |
|---|---|---|---|---|
| `ff` / -40 C / 3.63 V (Power-row binding corner) | 415.27 uW (-04) | 443.79 uW (-02) | **+28.53 uW** | 81.33 uW |
| `ss` / -40 C / 3.63 V | 236.78 uW (-05) | 242.83 uW (-03) | +6.05 uW | 42.46 uW |
| `tt` / 27 C / 3.30 V (nominal) | 191.94 uW (-06) | 203.27 uW (-04) | +11.33 uW | 46.69 uW |

The two columns are two different, separately-accounted costs (see item 2
above: the tap's own switching lives on its own supply branch, `vddtap`, not
on either ring's `vddr`):

- **Loading delta** is the part that actually spends the Power row's
  headroom: two `sampler_dff` gate inputs tied to `ro1`/`ro2` add input
  capacitance to the ring nodes, which measurably slows both rings (e.g. at
  `ff`/-40 C, `period_r1` goes from 4.286 ns un-tapped to 4.617 ns tapped) and
  raises `p_total_w` by the amounts above. This delta is **independent of the
  tap's own clock rate** -- it is a DC/AC loading effect on the ring itself,
  present at any digitizer clock frequency, including the real DR-0012
  external sample clock this deck does not use (see next point). At the
  binding corner (`ff`/-40 C/3.63 V), **+28.53 uW is 34 % of the ~85 uW
  headroom, leaving ~56 uW** for everything this repository has never
  measured the power of: the raw tap's own `sampler_dff`, `rct_apt.v`,
  `ring_liveness.v` itself, the conditioner, and `design/interface/` (item 1
  above already names this as an existing, not a new, gap).
- **The tap's own switching power (`p_tap_avg_w`)** is measured at this
  deck's deliberately fast 100 MHz local measurement clock (`tb.json`'s
  caveats), not DR-0012's real fixed external sample clock, and CMOS dynamic
  power scales linearly with clock frequency. Scaled down to the ratified
  DR-0003 raw rate (>= 1 Mbps, i.e. >= 100x slower than this deck's clock),
  the bound becomes **<= 0.81 uW** at the binding corner (<= 3.25 uW at the
  stretch 4 Mbps rate) -- negligible next to the loading delta above. This
  scaling is a bound, not a fresh measurement: no PVT sweep was run at the
  real clock rate, but dynamic power's linear frequency dependence is a
  standard CMOS result, not a new assumption specific to this record.

**Conclusion**: the part of this record's own cost that can spend the Power
row's headroom (the electrical loading on `ro1`/`ro2`) fits inside it at
every corner measured, using at most 34 % of the ~85 uW headroom at the
binding corner. It does not, by itself, threaten the ratified `< 500 uW`
row. The RTL and conditioner/interface/health-test digital-logic power this
repository has never measured (item 1) remains an open, pre-existing gap
this record does not close and does not worsen.

### Phase cost, measured (#76, amendment A2)

The table above prices the tap in **power**. It does not price it in **phase**,
and the two are not the same cost: the loading delta it reports is a *time
average* over the two states the tap's own `clk` puts it in, and averaging over
those two states is exactly what hides the effect this section records.

Measured at `tt`/27 C/3.30 V in
[`sim/characterization-liveness-tap-phase-cost.md`](../../sim/characterization-liveness-tap-phase-cost.md),
on the same 5-stage starved ring, injected noise density and window geometry
issue #51's coupling ladder used, so the two are directly comparable:

| | `T_0` | `sigma_1` vs its own static reference | per-block period swing |
|---|---|---|---|
| tap on the ring node, `clk` HIGH (master transmission gate off) | 2.7472 ns | 1.00x (reference) | 0.00 % |
| tap on the ring node, `clk` LOW (master transmission gate on) | 3.4507 ns | — | 0.00 % |
| tap on the ring node, **`clk` running** (the arrangement this record specified) | 3.0444 ns | **541.3x** | **23.11 %** |
| tap on the **buffer output**, `clk` running (what ships since PR #82 / DR-0018) | 2.8596 ns | **19.9x** | **0.96 %** |

Three points, in order of how much they change what this record claims:

1. **The two static endpoints are 25.6 % apart on ring period.** Which rail
   `clk` sits on decides how fast the ring runs, because the `sampler_dff`
   master transmission gate conducts while `clk` is low and the ring node then
   drives the master latch's input inverter through a full transition every
   ring cycle. That gap is **rate-independent**: a 50 % duty-cycle clock puts
   the ring in each state half the time whatever its frequency.
2. **With `clk` running the ring visits exactly those two endpoints**, block
   for block, with a repeat period equal to the clk period. What that inflates
   is not jitter -- across four independent noise seeds the resulting
   `sigma_1` reproduces to 0.01 % where a genuine estimate scatters 2.69 %,
   and it accumulates as `L^0.95` rather than a random walk's `L^0.5`.
3. **The consequence is a measurement rule, not a design change.** A per-ring
   `sigma_acc,i` measured with a digitizer attached and `clk` toggling is not
   admissible evidence for DR-0007 §2's sizing law, for the same reason
   `sim/characterization-array-ring-coupling.md` ruled out one measured with
   the combiner neighbours switching. No committed record in this repository
   is affected -- every per-ring `sigma_acc` on file comes from a deck with no
   digitizer in it -- so this is forward-looking. **DR-0007 §2 is unamended and
   this amendment does not amend it.**

This does not change this record's Decision, its cutoffs, `C_LIVE`, or the
Power row conclusion above. It records a second measured cost of the same tap,
and the direction of the finding is that the mitigation the block already
adopted for a different reason (DR-0018) also happens to remove most of this
one. What to do about the 19.9x residual is not decided here and has no
evidence here.

#### The bit-level follow-up (#86, amendment A3)

A2 is a measurement about **phase**, and it deliberately stops there. Whether
the `clk`-locked modulation it records reaches the **sampled bit** -- and so
whether DR-0007 §1's "free-running ring oscillators, no phase-locking of any
kind" needs a term for the sample clock -- was left open, and is answered by
issue #86 in
[`sim/characterization-sampler-bit-bias.md`](../../sim/characterization-sampler-bit-bias.md).

Measured at the same corner, on `sampler_core`'s own wiring (both rings, both
buffers, the XOR, the DR-0001 raw tap and both digitizers), against the same
circuit with the digitizers' clock parked instead of running, at three `clk`
rates -- one placed at a near-4:1 ring-to-sample ratio, one deliberately off
resonance, and DR-0003's ratified floor, which turns out to sit within 0.006 of
a 352:1 ratio:

- the sampled bit's **bias** differs between the two arrangements by at most
  **0.82 sigma** of the measurement's own resolution, and its short-lag
  **serial correlation** by at most **1.68 sigma**, with no trend across the
  three rates;
- **neither near-resonant rate locks**: ring 1 stays 81x and 120x the
  measurement's own seed-to-seed scatter clear of an exact `T_clk/N`;
- the frequency shift running the digitizers' clock causes is **+0.225 %** and
  is the **same fraction at every rate** (+0.225 / +0.228 / +0.223 %), which is
  a static-load offset's signature and not injection pulling's.

**No decision, parameter, cutoff or mechanism in this record changes, and
DR-0007 is unamended** -- #86's own conclusion is that §1's requirement is met
and that what is approximate is its premise, whose size is now bounded rather
than assumed. The residual A2 records is still a real cost of this tap; #86
adds that, at this corner, it does not arrive at the bit.

### No exposed per-ring tap (DR-0001)

`ring_liveness.v`'s port list is `clk`, `rst_n`, `ring_bit[N_RINGS-1:0]`,
`ring_stuck[N_RINGS-1:0]`, `ring_stuck_any` -- all internal health-test-block
signals, the same status `raw_bit`/`ht_fail_rct` already have. **No per-ring
signal reaches a chip-level pin**, which is the property DR-0001 actually
constrains: it governs what the block publishes at the die boundary, not what
it monitors internally.

*(Amended by #65, A1.)* As written, this record added no pin to
`ro_array_core.sym` at all, and `sim/tb/ring-liveness-tap-power/`'s tap
connections were a testbench-only construct (ngspice hierarchical node
addressing, `ro-array-core-power/`'s existing technique extended from a
read-only probe to an electrical connection). #65 made the tap real:
`ro_array_core.sym` gained `ro1`/`ro2` as observation-only **cell** pins, and
`sampler_core.sch` consumes them. The DR-0001 property above is unchanged and
is the one that matters -- a cell pin inside the block is not an exposed tap,
and `trng_top`'s own pin list carries `ring_bit1`/`ring_bit2` no further than
`design/health_test/`.

## Alternatives considered

### Per-ring analog supply-current sensing (option 1 from design/README.md)

- **What**: A comparator (or similar analog sensor) on each `vddr1`/`vddr2`
  branch, tripping when current collapses toward the stopped-ring leakage
  floor.
- **Why plausible**: The signal is enormous (>4 orders of magnitude) and
  needs no digitizer at the ring's own node, so it cannot load `ro1`/`ro2` at
  all.
- **Why rejected**: Needs a bespoke analog sensor design and its own
  characterization (offset, corner drift, response time) -- exactly the
  class of new-analog-block work `design/README.md` flags this issue as
  needing to trade off, not assume. Option 2 reuses an already-verified
  digital cell (`sampler_dff`) and an already-verified algorithm (RCT),
  needing no new transistor-level design.

### A bespoke small-window "transition-silence" watchdog

- **What**: An earlier draft of this record counted consecutive
  *non-toggling* samples directly (a small window, e.g. 8 cycles), reasoning
  that a live ring's period is many times shorter than one sampler-clock
  period so it should "almost always" toggle between samples.
- **Why plausible**: A small, fixed window gives very fast detection (8
  cycles vs. 81) and needs no min-entropy assumption at all.
- **Why rejected**: The reasoning was wrong. Many ring periods elapsing
  between samples does not make the sampled *level* more likely to differ
  from the previous sample -- phase aliasing means the sampled bit is
  approximately an IID coin flip, not a value biased toward toggling (see
  `sim/tb/ring-liveness-fault-injection/fault_injection.py`'s
  `healthy_ring_bits` docstring). Under that corrected model an 8-sample
  window on a genuinely healthy ring has a non-negligible chance of eight
  consecutive matches (~1/128 per window), which at a real sample rate would
  fire spuriously far too often -- exactly the false-alarm-rate problem
  DR-0002's own Context section already solved once for the combined tap by
  choosing `alpha = 2**-40`. Reusing that solved problem (RCT at `C_RCT`) is
  strictly better than re-deriving a smaller, weaker one.

### Wire `ring_stuck_any` into `design/interface/`'s alarm/gate path in this same change

- **What**: Add a fourth failure source (alongside `ht_fail_rct`/
  `ht_fail_apt`) to `design/interface/trng_interface.v`/`.py` and the
  `STATUS` register map, so `ring_stuck_any` actually latches and gates
  today.
- **Why plausible**: Makes the "flag, not hard stop" decision immediately
  real and testable end to end, rather than a documented intention.
- **Why rejected (for this record, not the decision)**: `design/interface/`
  is a closed, ratified block (DR-0013, #26) with a generated register map
  (`regmap.py` / `trng_regmap.vh` / `REGMAP.md`) and its own test suite.
  Re-opening it is a well-defined, low-risk, but *separate* piece of work
  (one more OR term, one more `STATUS` bit, mirroring `HT_FAIL_RCT`/
  `HT_FAIL_APT` exactly) that does not need to ride on this issue's scope.
  Filed as a follow-up (see Consequences) so this record's own PR stays
  focused on the monitor itself, per this repository's scope-discipline
  convention.

### A hard stop (irreversible disable) on a confirmed dead ring

- Covered under "Failure behavior" above -- rejected because DR-0002 already
  established that latch-and-gate-with-explicit-recovery is sufficient for a
  confirmed source failure, and a hard stop would remove the raw diagnostic
  path DR-0002 deliberately preserved for no additional safety benefit.

## Consequences

- **Positive**:
  - Closes the specific blind spot DR-0007 §Consequences names and DR-0010
    sharpens: a dead ring in the shipped N=2 array is now detected
    deterministically, independent of whether the surviving ring keeps the
    combined raw stream inside RCT/APT's own cutoffs.
  - No new statistical assumption, no new analog cell, and no new exposed
    pin: the cutoff, the digitizer cell, and the failure-behavior mechanism
    are all reused from DR-0002/#11/DR-0014, not reinvented.
  - `C_LIVE` tracks `C_RCT` automatically if #13 changes the ratified `H`.
- **Negative / accepted cost**:
  - `C_LIVE = 81` is DR-0002's own conservative `H0 = 0.5` assumption, not a
    number derived for an individual ring's actual statistics -- no per-ring
    duty-cycle or bias measurement exists in this repository. A tighter,
    measured cutoff (faster detection) is possible but not built here.
  - The electrical tap this record measures the cost of was not, in this
    record's own change, shipped RTL/schematic: `sim/tb/ring-liveness-tap-power/`
    proved the mechanism and bounded its cost using ngspice's hierarchical
    internal-node addressing rather than a `design/` schematic change.
    **Closed by #65** (amendment A1): `ro1`/`ro2` are observation-only pins
    and two `sampler_dff` instances digitize them in `sampler_core.sch`.
  - `design/interface/`'s alarm/gate path did not consume `ring_stuck_any`
    when this record was written. **Closed by #65** (amendment A1):
    `ht_fail_ring` / `STATUS.HT_FAIL_RING`.
- **Follow-up required**:
  - ~~[#65](https://github.com/2AMLogic/gf180-trng/issues/65)~~ -- **done**,
    see amendment A1 under Status. It wired `ring_stuck_any` into
    `design/interface/`'s `HT_ALARM`/gate OR-condition with a `STATUS`
    register bit (`HT_FAIL_RING`, bit 9) exactly parallel to
    `HT_FAIL_RCT`/`HT_FAIL_APT`, and promoted the `ro1`/`ro2` tap from this
    record's testbench-only hierarchical connection into shipped `design/`
    RTL/schematic.
  - #13's ratified worst-corner `H`, once available, is a one-line change to
    both `C_RCT` and `C_LIVE` (`rct_apt.c_rct(H)`).
- **Revisit if**: a per-ring duty-cycle or bias measurement is ever taken
  (which would justify a tighter, measured `C_LIVE` rather than the reused
  conservative `C_RCT`), **or** a real fault demonstrates a ring that
  degrades (slows, or biases) without ever holding a constant value for
  `C_LIVE` samples, which would motivate a per-ring APT rather than RCT
  alone, **or** #13's ratified `H` changes `C_RCT` enough to matter for
  `C_LIVE` too.
