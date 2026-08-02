---
dr: DR-0017-idle-current-row-versus-ungated-standard-cell-leakage
title: Resolve the measured 4.5x miss on the < 1 uA idle row, whose cause is ungated standard-cell leakage in the digital section and not the analog block
status: Proposed
date: 2026-08-02
deciders: Proposed by #14 (start-up, time-to-first-valid and power characterization). NOT ratified — acceptance is an operator decision, as DR-0001…DR-0004 and DR-0007 were.
supersedes: n/a (on acceptance of option C it would supersede the README `Power` row's idle half only; DR-0007's and DR-0010's active-power reasoning is untouched either way)
superseded_by: n/a
related: "#14 (origin — this record's evidence), #32/PR #38 (the first leakage characterization), #26/DR-0013 (the interface and its two 8x32-bit FIFOs), #11/DR-0002 (health-test window sizing), #8/DR-0008 (conditioner K), DR-0004 (claim tiers), DR-0009 (behavioural/transistor split), DR-0010 (the still-Proposed active-power/rate collision), DR-0012 (fixed external sample clock), #15/#17 (layout, which will add to this number and cannot reduce it); README §Target specification — Power"
---

# DR-0017: Resolve the measured 4.5× miss on the `< 1 µA` idle row, whose cause is ungated standard-cell leakage in the digital section and not the analog block

## Status

- 2026-08-02: Proposed, by #14. Not ratified.

Until ratified the `< 1 µA` row stands as written and this record is a
proposal, not spec. Nothing in `README.md` is edited by the pull request that
proposes this record.

## Context

### The row, and what it was ratified on

`README.md`'s `Power` row states `< 1 µA idle, binding at ff / +10 % / +125 °C
(max leakage)`, with "idle" defined in the ratification note as "all ring
oscillators stopped and no bits being produced, with the block powered and
register state retained — i.e. leakage plus static bias only."

That same note already recorded the doubt:

> Both halves of the row are unevidenced, and the `< 1 µA` idle figure is
> order-of-magnitude questionable for an ungated few-kGE digital section at
> `ff`/+125 °C without power gating.

This record turns that sentence into numbers. It is not a new discovery so much
as the arrival of the measurement the ratification note asked for.

### What #14 measured

Per [`sim/characterization-startup-and-power-budget.md`](../../sim/characterization-startup-and-power-budget.md),
at the row's own binding corner `ff` / +125 °C / 3.63 V:

| Contribution | Idle current | Share of the row | Standing |
|---|---|---|---|
| Whole `sampler_core` — both rings, XOR combiner, both `sampler_dff` instances — clamped, reset released, clock parked | **32.8 nA** | 3.3 % | **Measured**, `sim/records/2026-08-02-sampler-core-idle-leakage-{01..45}.md` |
| Conditioner + health tests + interface: 658 flip-flops, 1655 cells, no power gating | **4.43 µA** | 442 % | **Estimate** ([DR-0004] Tier 2), `design/digital_power_estimate.py` |
| **Total** | **4.46 µA** | **446 %** | |

Two facts do the work here, and they pull apart cleanly.

**The analog block is not the problem, and is now measured for the first time.**
32.8 nA is 3.3 % of the whole row. The clamped ring array is a genuinely quiet
idle state — with `en` low, `ro_nand2`'s output is forced high, every node in
both eleven-stage rings sits at a rail, and there is no crowbar path anywhere.
The two clock-park states differ by 12 % (32.8 nA parked low, 29.2 nA parked
high), so the parked level is not a lever worth pulling. This supersedes
nothing: it is the first idle measurement of the *shipped* block, where
`sim/tb/ro-inv-05stage-stopped-leakage/` measured the characterization-cell
five-stage ring and #32's projection extrapolated a per-micron coefficient onto
an assumed gate width.

**The digital section misses the row on leakage alone, and half of that figure
is not an estimate.** The 658 flip-flops are enumerated from the three modules'
`reg` declarations at their shipped default parameters, not modelled: 41
(conditioner), 45 (health tests), 572 (interface, of which 512 are the two
8 × 32-bit output FIFOs). At `ff`/+125 °C the PDK's own Liberty library gives
`dffrnq_1` a state-independent leakage of 12.2 nW, so **the flops alone are
2.24 µA — 2.2× the row — before a single combinational cell is counted.**

### The miss is a corner phenomenon, and the corner is the one the row names

`python3 design/digital_power_estimate.py --all-corners`:

| Liberty corner | Digital idle leakage | vs the `< 1 µA` row |
|---|---|---|
| `tt` / +25 °C / 3.30 V | 85 nA | 8.5 % |
| `ff` / −40 °C / 3.60 V | 85 nA | 8.5 % |
| `ss` / +125 °C / 3.00 V | 350 nA | 35 % |
| **`ff` / +125 °C / 3.60 V** | **4.43 µA** | **442 %** |

The row is met with a factor of ten to spare at every characterised corner
except the one it binds at, where it is missed by 4.4×. That is a 52× swing
across the library, and it is ordinary: sub-threshold leakage is exponential in
temperature and the `ff` skew stacks on top of it. A row written at nominal and
then annotated with a worst-case corner is exactly the shape of specification
that this outcome catches.

### Why "just tighten the estimate" is not available

The combinational half of the estimate (2.19 µA, dominated by 576 `mux2_1`
cells in the FIFO read path) is genuinely soft. It is also not load-bearing:

- delete **every** combinational cell in all three blocks and the flops alone
  still give 2.24 µA, 2.2× over;
- delete **both FIFOs entirely** — all 512 storage flops, all 448 read-mux
  cells, all 16 clock gates — and the remainder is **1.44 µA, still 1.4× over**;
- implement the 8:1 read muxes as `mux4_1` trees instead of `mux2_1` trees and
  the total moves from 4.43 µA to 4.29 µA.

There is no inventory refinement, and no FIFO depth, that reaches 1 µA at this
corner. That is what makes this a specification decision rather than a
modelling one.

### One hard constraint on the obvious fix

`gf180mcu_fd_sc_mcu7t5v0` **ships no state-retention flip-flop, no power-switch
(header/footer) cell, and no isolation cell.** The library's sequential set is
`dffq`/`dffrnq`/`dffsnq`/`dffrsnq`, their negative-edge and scan variants, and
plain latches — checked against the installed PDK's own Liberty file. So the
textbook answer to a leakage problem, *state-retention power gating*, is not a
library instantiation here; it would be custom analog design (a PMOS header,
its control, and isolation on every output crossing the domain) inside a block
whose whole digital section is currently RTL with no synthesis flow at all.

## Decision

**We will** report the miss, keep the ratified row unedited, and choose one of
the four options below — with **option C (move the row, and split it)**
proposed as the recommendation.

Specifically, on acceptance of option C:

1. `README.md`'s `Power` row's idle half changes from `< 1 µA idle` to two
   stated figures rather than one, because they have completely different
   evidential standing and completely different design meaning:
   - **`< 100 nA` analog idle** (`ro_array_core` + `sampler_core`), binding at
     `ff` / +10 % / +125 °C — measured, with a 3× margin over the 32.8 nA
     evidence, and citing `…-sampler-core-idle-leakage-*`.
   - **`< 6 µA` total block idle**, binding at the same corner — an estimate,
     labelled [DR-0004] Tier 2, citing `design/digital_power_estimate.py`, and
     set above the 4.46 µA figure by the ~35 % margin the combinational half of
     the estimate can plausibly move by.
2. The row records that the total-idle figure **is not met by a design
   constraint but by a measurement of what the design does**, and that
   reducing it needs power gating that this standard-cell library cannot
   supply.
3. `DR-0004`'s tiering language is not touched; this is an application of it.

**No option is chosen by the pull request that proposes this record**, and no
README row is edited by it.

## Alternatives considered

### A. Power-gate the digital section

- **What**: a supply switch on the conditioner / health tests / interface,
  with the section powered down in idle.
- **Why plausible**: it is the only mechanism that actually removes leakage
  rather than reducing the cell count it is proportional to, and it would get
  the total to roughly the analog block's 32.8 nA plus switch leakage.
- **Why rejected (as the response to *this* record)**: it does not preserve the
  ratified definition of idle. "Register state retained" is part of the row's
  own wording, and a gated section without retention flops loses `CTRL`,
  `STATUS`, the FIFO contents, the health-test window position and the
  conditioner's in-flight block — i.e. the block returns from idle needing a
  full start-up test, so **option A silently converts every idle exit into a
  1.28 ms time-to-first-valid event**. It is also not a library instantiation:
  `gf180mcu_fd_sc_mcu7t5v0` has no header, isolation or retention cell, so this
  is custom analog work plus a UPF-style power-intent flow this repository does
  not have. Worth doing eventually; not available as a spec answer today.
  Would need its own DR, and would supersede the idle definition, not just its
  number.

### B. Shrink the digital section until it fits

- **What**: `FIFO_DEPTH` from 8 to 2 or 1, a cheaper read path, narrower
  health-test counters.
- **Why plausible**: it needs no new cell type and no power-intent flow, and
  the two FIFOs really are 78 % of the flop count.
- **Why rejected**: it does not reach the row. `FIFO_DEPTH = 2` gives 2.04 µA
  and `FIFO_DEPTH = 1` gives 1.64 µA; removing both FIFOs entirely gives
  1.44 µA. Every one of those still misses `< 1 µA`, and each costs real
  function — a one-word FIFO makes the streaming port's back-pressure behaviour
  ([DR-0013]) materially worse, and at DR-0010's proposed 500 bps a shallow
  FIFO is a much bigger deal than at 1 Mbps because each lost word is 0.5 s of
  accumulation. Paying a functional cost for a change that still misses the
  target is the worst of both.

### C. Move the row, and split it into an analog figure and a total figure

- **What**: the recommendation above — `< 100 nA` analog (measured) and
  `< 6 µA` total (estimated), both at `ff` / +10 % / +125 °C.
- **Why plausible**: it is the option that states what the block actually does,
  at the standing each half of the number actually has. It also keeps the one
  genuinely strong result visible: the entropy source and sampler idle at
  3.3 % of the original row, which is the part an integrator worried about an
  always-on analog block would care about, and which would be buried inside a
  single 4.46 µA number.
- **Why not automatic**: `< 1 µA` is a real product-facing figure and 6 µA is a
  different claim. An integrator budgeting a always-on always-powered
  peripheral at 1 µA and getting 6 µA has a problem this record does not solve
  for them; it only stops the datasheet lying to them. This is exactly the
  trade [DR-0010] made on the rate row, and it should be weighed the same way.

### D. Do nothing — leave the row and record the contradiction

- **What**: `sim/characterization-startup-and-power-budget.md` states the miss;
  the row stays as ratified; the conflict is tracked.
- **Why plausible**: the number that misses is an *estimate*, and this
  repository has no synthesised netlist for any of the three blocks. Ratifying
  a worse row on the strength of a pre-synthesis inventory has its own cost,
  and a synthesis flow (with real clock gating and a real read-path
  implementation) might move the combinational half substantially.
- **Why rejected**: it would not move the *flop* half, which is enumerated
  rather than estimated and misses on its own by 2.2×; and the same argument
  would have blocked DR-0010, which moved a ratified row on evidence of exactly
  this kind. Leaving a row standing that the best available evidence says is
  missed by 4.5× is the thing `CLAUDE.md` calls not relaxing the spec, applied
  backwards — the spec is not being relaxed to make results pass, the results
  are being ignored to leave the spec comfortable.

## Consequences

- **Positive**:
  - The idle row acquires evidence for the first time, and the evidence
    separates cleanly into a measured analog figure and an estimated digital
    one, so a future synthesis run can improve half of it without disturbing
    the other half.
  - The analog block's idle behaviour — the part hardest to fix later, because
    it is transistor-level and inside a layout — is comfortably good: 32.8 nA
    at the leakiest corner, 3.3 % of even the original row.
  - It records, findably, that this standard-cell library has no retention or
    power-switch cells. Anyone who later assumes power gating is a synthesis
    option will hit that fact in this record instead of in a schedule.

- **Negative / accepted cost**:
  - **A 6 µA idle claim is a materially different product claim from 1 µA**, in
    the same way DR-0010's 500 bps is from 1 Mbps. An always-on integrator
    sizing a coin cell around this block has to be told.
  - **The number rests on an estimate.** Half of it (the flop count and the
    per-cell Liberty leakage) is hard; half (the combinational inventory) is a
    pre-synthesis structural guess that a real synthesiser will not reproduce
    exactly. The proposed 6 µA carries that uncertainty as margin rather than
    resolving it.
  - **It is a worst-corner number that the block will almost never sit at.**
    At `tt`/+25 °C the same estimate is 85 nA. Stating the row at its binding
    corner is correct and is what the ratified table does everywhere else, but
    it makes the headline figure 52× worse than typical, and a reader who wants
    a typical figure has to go and find one.
  - **Layout will add to this and cannot reduce it.** #15/#17 have not run;
    routing adds wire capacitance (dynamic, not leakage) and fill/tap cells
    add area, and nothing in post-layout closure reduces standard-cell
    sub-threshold leakage.

- **Follow-up required**:
  - **A synthesis flow for the three digital blocks** is the single thing that
    would replace this record's estimate with a measurement. It does not exist
    in this repository (yosys is not part of the toolchain today, per
    `design/conditioner/area_estimate.py`) and is not filed. Filing it is the
    honest follow-up; it is also the prerequisite for a serious power-gating
    proposal.
  - **A power-gating DR** if option A is ever pursued, which must settle what
    happens to the retained state and therefore to time-to-first-valid on every
    idle exit.
  - **`README.md`'s Power row** is edited only on acceptance, and only in the
    idle half. The active half is met (454.2 µW, 90.8 % of `< 500 µW`) and this
    record does not touch it.

- **Revisit if**:
  - a synthesis run replaces the combinational inventory with a real netlist —
    it can only move ~2.19 µA of the 4.43 µA, but it would settle the number;
  - the interface's FIFO depth changes for an unrelated reason (each halving is
    worth ~0.8 µA at this corner);
  - a retention-capable cell library or a power-switch cell becomes available
    for gf180mcu, which would put option A back on the table as an
    instantiation rather than a custom design;
  - the operating envelope's upper temperature is reduced — the whole miss is a
    +125 °C phenomenon, and the row is met by 10× at +25 °C.

[DR-0004]: DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0010]: DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0013]: DR-0013-interface-register-map-and-streaming-semantics.md
