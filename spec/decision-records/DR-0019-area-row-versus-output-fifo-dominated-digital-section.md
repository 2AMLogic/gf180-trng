---
dr: DR-0019-area-row-versus-output-fifo-dominated-digital-section
title: Record the 2.7x miss on the < 0.05 mm2 area row, whose dominant term is the interface's two 8x32-bit output FIFOs, and hold the row until the FIFO-depth question is settled jointly with DR-0017
status: Proposed
date: 2026-08-04
deciders: Proposed by #96 (the area row has no decision record, unlike every other missed or unmeasured row). NOT ratified — acceptance is an operator decision, as DR-0001…DR-0004 and DR-0007 were.
supersedes: n/a (this record edits no row; on acceptance of option B or D it would be superseded by the record that states the new row)
superseded_by: n/a
related: "#16/PR (the floorplan and its area inventory — origin of this record's evidence), #94 (the hygiene pass that surfaced the missing record), #26/DR-0013 (the interface and its two 8x32-bit FIFOs), DR-0017 (the same FIFOs, the idle-current row), DR-0008 (the conditioner's area figure and the AES-128 rejection that is conditioned on this budget), DR-0004 (claim tiers), DR-0010 (the 500 bps raw rate that sets what a buffered word is worth), DR-0016 (the ring-liveness monitor, excluded from the totals here), DR-0020 (the FIFO-depth follow-up this record named in its Consequences, now filed: it sets FIFO_DEPTH = 2, so this record's Decision item-4 supersession trigger does not fire and its Revisit-if 'below 8' branch applies instead), #15/#17 (layout, which will add to this number and cannot reduce it); README §Target specification — Area, layout/floorplan/README.md §Area against the `< 0.05 mm²` row"
---

# DR-0019: Record the 2.7× miss on the `< 0.05 mm²` area row, whose dominant term is the interface's two 8 × 32-bit output FIFOs, and hold the row until the FIFO-depth question is settled jointly with [DR-0017]

## Status

- 2026-08-04: Proposed, by #96. Not ratified.

Until ratified the `< 0.05 mm²` row stands as written and this record is a
proposal, not spec. Nothing in `README.md`'s ratified table is edited by the
pull request that proposes this record; the only README changes it makes are
pointers to this record.

## Context

### The row, and why it has no record

`README.md`'s `Area` row states `< 0.05 mm²` — 50 000 µm² for the whole block —
ratified 2026-07-31 with no supporting estimate of any kind. Every other row
that is missed or unmeasured now has a decision record routing it: the raw rate
to [DR-0010] / [DR-0011], the entropy-binding corner to [DR-0015], the idle
current to [DR-0017]. The area row had none, which is the gap #96 filed and
this record closes. `CLAUDE.md` is explicit that a row that cannot be met
becomes a superseding decision record rather than a silent edit, so the absence
of a record — not the number — was the defect.

### What #16's floorplan inventory prices

From `python3 layout/floorplan/floorplan.py`, recorded in
[`layout/floorplan/reports/area.json`](../../layout/floorplan/reports/area.json)
and broken down under *Area against the `< 0.05 mm²` row* in
[`layout/floorplan/README.md`](../../layout/floorplan/README.md):

| | area | share of the `< 0.05 mm²` row |
|---|---:|---:|
| Entropy source + samplers + guard rings + isolation channels | 2 070.8 µm² | **4.1 %** |
| Digital section (conditioner + health tests + interface) | 125 556.8 µm² | **251.1 %** |
| **Floorplan total** | **134 714.4 µm² = 0.1347 mm²** | **269.4 %** |

Three facts do the work, and they pull apart as cleanly as [DR-0017]'s did.

**The analog block is not the problem.** The entire isolated entropy source —
both rings, the XOR combiner, all four samplers, four guard rings and every
isolation channel between them — is **4.1 %** of the row, of which the whole
isolation structure (guard rings plus channels) is 2.1 %. Whatever happens to
this row, the isolation argument does not trade against it.

**The miss is not a placement artefact.** The digital section's *standard-cell
area alone*, before any placement, spacing, guard ring or channel, is
**74 485.3 µm² — 149.0 % of the whole row.** The floorplan reports 269.4 % at
its 60 % utilisation and 205.1 % at the 80 % variant it also prints; at a
physically unreachable 100 % utilisation the same geometry still gives 166.3 %.
There is no placement density that reaches the row at the shipped inventory.

**Half of the inventory is enumerated, not modelled.** The 658 flip-flops are
counted from the three modules' `reg` declarations at their shipped default
parameters (41 conditioner, 45 health tests, 572 interface) — the same count
[DR-0017] uses. At the PDK's own LEF area for `dffrnq_1` (74.637 µm²) **the
flip-flops alone are 49 111 µm², 98.2 % of the area row**, with zero
combinational cells, zero placement overhead and zero isolation structure. That
figure has no modelling freedom in it: it is a cell count times a library
constant.

### Where the area actually is

The two 8 × 32-bit output FIFOs ([DR-0013]) are **69.8 % of the digital
section's cell area and 82.4 % of the interface's**:

| FIFO term | count | unit (LEF) | area |
|---|---:|---:|---:|
| Storage flops | 512 `dffrnq_1` | 74.637 µm² | 38 214.0 µm² |
| 8:1 read muxes (2 × 32 bits × 7) | 448 `mux2_1` | 28.538 µm² | 12 784.8 µm² |
| Per-word clock gates | 16 `icgtp_1` | 61.466 µm² | 983.4 µm² |
| **total** | | | **51 982.3 µm²** |

This is the same structure, in the same block, that [DR-0017] identifies as the
reason the `< 1 µA` idle row misses by 4.5×. One design decision — the depth of
the interface's output buffering — lands on two ratified rows.

### The same lever has very different reach on the two rows

[DR-0017] §"Alternatives considered → B" rejected shrinking `FIFO_DEPTH` as a
response to the *power* row, and rejected it on reach: depth 2 gives 2.04 µA,
depth 1 gives 1.64 µA, and deleting both FIFOs entirely still leaves 1.44 µA
against a `< 1 µA` row. The lever never arrives.

On the *area* row it very nearly does. Scaling only the depth-dependent terms
(storage `64 × D` flops, read mux `64 × (D − 1)` `mux2_1`, `2 × D` clock gates)
and holding every other cell in the block fixed, through the floorplan script's
own geometry — cell area / utilisation, squared up, plus a 1 µm guard ring per
side, plus the three isolation channels:

| `FIFO_DEPTH` | FIFO cell area | digital cell area | floorplan total @ 60 % | share of row | share @ 80 % |
|---:|---:|---:|---:|---:|---:|
| **8 (shipped)** | 51 982 µm² | 74 485 µm² | 134 713 µm² | **269.4 %** | 205.1 % |
| 4 | 25 078 µm² | 47 581 µm² | 88 175 µm² | 176.3 % | 134.9 % |
| 2 | 11 626 µm² | 34 129 µm² | 64 720 µm² | 129.4 % | 99.5 % |
| 1 | 4 900 µm² | 27 403 µm² | 52 915 µm² | 105.8 % | 81.6 % |
| 0 (no FIFOs) | 0 µm² | 22 503 µm² | 44 268 µm² | 88.5 % | 68.5 % |

(The `FIFO_DEPTH = 8` row reproduces the shipped total to 1.3 µm², 0.001 %,
from `area.json`'s own rounded per-region figures — so the other rows are
comparable to it. Depth is the only thing varied; pointer and occupancy-counter
widths, which also shrink with depth, are held at their depth-8 values, which
makes every reduced row very slightly pessimistic.)

The reason for the asymmetry is arithmetic, not judgement. Leakage has a floor
set by the 146 non-FIFO flops plus the whole combinational inventory, and that
floor is already 1.4× the power row. The area row's non-FIFO remainder is
22 503 µm² of cell area — **45 % of the area row**, i.e. *under* it. So the same
change that is futile on one row is most of an answer on the other. Whoever
decides `FIFO_DEPTH` cannot decide it from [DR-0017] alone.

The corresponding break-even: for the floorplan total to reach 50 000 µm² at the
script's 60 % utilisation, **the digital section's cell area must come down from
74 485 µm² to 25 748 µm² — a 65.4 % reduction.** Deleting both FIFOs entirely
gets to 22 503 µm², under that break-even by 13 %. Nothing short of the FIFOs
gets close: the conditioner and health tests together are 11 387 µm², so even
deleting *both of them* moves the total only from 269.4 % to 230.1 %.

### What the estimate is, and what it is not

A **bottom-up inventory estimate with a stated method** — [DR-0004] Tier 2 —
not a measurement:

- No synthesiser, placer or router has been run on this block, and no analog
  cell has been drawn. `layout/floorplan/README.md` §"What the area model is"
  states the method in full.
- Gate-shaped analog cells are priced at their nearest
  `gf180mcu_fd_sc_mcu7t5v0` equivalent, a 7-track library with wider devices
  than the hand-drawn minimum-width cells they stand in for, and the starve
  devices are priced at a generated footprint 1.8–1.9× their drawn width
  (0.42 µm generated against 0.240 / 0.220 µm drawn) because the generator will
  not go narrower. Both **over**-estimate the analog side —
  the 4.1 % figure is conservative, which only strengthens the finding that the
  miss is entirely digital.
- The digital side reuses the cell inventories `design/digital_power_estimate.py`
  already maintains, guarded by `sim/tests/test_power_rollups.py` — the same
  inventory [DR-0017] draws its flop count from.
- One term is **excluded**: [DR-0016]'s ring-liveness monitor (85 cells,
  2 849.4 µm²), which is shipped RTL as of #71 but still flagged
  `shipped=False` in that inventory. Including it takes the total to 279.2 %.
- The estimate contains **no** routing beyond the utilisation factor, no fill or
  tap cells, no power grid, no pads or seal ring. As with [DR-0017]'s leakage
  figure, layout adds to this number and cannot subtract from it.

The soft half is the combinational inventory (a structural guess at what a
synthesiser must produce). It is not load-bearing: delete every combinational
cell in all three blocks and the 658 flops alone are still 98.2 % of the row,
and the block still has to be placed.

## Decision

**We will** report the miss, keep the ratified `< 0.05 mm²` row unedited, and
**defer the choice of response until `FIFO_DEPTH` is decided**, because that one
design decision determines which responses are even available. Of the four
options below, **option C (record the miss, hold the row, sequence the response
behind the FIFO-depth decision)** is proposed as the recommendation.

Specifically, on acceptance of option C:

1. `README.md`'s `Area` row is **not** edited. Its note under the ratification
   block cites this record, exactly as the `Power` row's note cites [DR-0017],
   and `layout/floorplan/README.md`'s area section does the same.
2. This record states the ordering constraint as spec-process fact: **the area
   row is not moved before the FIFO-depth decision is made**, because at depth 1
   the estimate is 105.8 % of the row (81.6 % at 80 % utilisation) and at depth 0
   it is 88.5 %. Moving a ratified row to accommodate a design parameter nobody
   has yet examined is the thing `CLAUDE.md` forbids — relaxing the spec to make
   a result pass.
3. The FIFO-depth decision is **jointly owned with [DR-0017] and [DR-0013]** and
   needs its own record: the same change is worth nothing on the power row, most
   of the area row, and a real functional cost on the streaming port. That
   record is named in Follow-up below and is not filed by this one.
4. If that decision keeps `FIFO_DEPTH = 8`, then option B or option D becomes
   live and **this record is superseded by the one that states the new row** —
   not amended.

**No option is chosen by the pull request that proposes this record**, no
ratified row is edited by it, and no design parameter is changed by it.

## Alternatives considered

### A. Shrink the digital section until it fits — `FIFO_DEPTH` first

- **What**: reduce the output FIFO depth from 8, the dominant term at 69.8 % of
  digital cell area, and take the rest from the read path if needed.
- **Why plausible**: it is the only lever with the reach shown in the table
  above — depth 2 lands at 99.5 % of the row at 80 % utilisation, depth 1 at
  81.6 %, and it needs no new cell type, no synthesis flow and no spec change.
  It also has a second beneficiary, though a small one: each halving is worth
  ~0.8 µA at [DR-0017]'s corner.
- **Why not chosen here**: three reasons, none of which is "it doesn't work".
  (i) At the floorplan's own conservative 60 % utilisation, *no* depth ≥ 1 meets
  the row — depth 1 is still 105.8 % — so the option's success depends on a
  placement density this repository has no placer to demonstrate. (ii) It costs
  real function: [DR-0013] already records that an `OUT_MODE` write costs a
  reader up to `FIFO_DEPTH` buffered words, and at [DR-0010]'s proposed 500 bps
  raw rate one buffered raw word is 64 ms of accumulation and one conditioned
  word is 512 ms — a shallow FIFO is a far more serious thing at 500 bps than
  it was at 1 Mbps. (iii) It is a **design** decision about the interface, and
  this record is a spec-process one; taken here it would be a documentation
  change silently rewriting a ratified interface parameter. It should be taken
  deliberately, with the power row's numbers and the streaming semantics in
  front of the decider, in its own record.

### B. Raise the area row, with the reasoning recorded

- **What**: supersede `< 0.05 mm²` with a figure the evidence supports —
  0.1347 mm² measured by this method, so a row somewhere around `< 0.20 mm²`
  once [DR-0016]'s monitor (0.1396 mm²), routing, fill, taps and the undrawn
  analog cells are allowed for.
- **Why plausible**: it is exactly what [DR-0010] did to the rate row and what
  [DR-0017] proposes for the idle row — state what the block actually is rather
  than what it was hoped to be. The original 50 000 µm² was ratified with no
  estimate behind it at all, which is the weakest possible standing for a
  constraint.
- **Why rejected (for now)**: **the area row is load-bearing on another
  decision.** [DR-0008] rejected a 90B-*vetted* AES-128 conditioner on area —
  0.044–0.062 mm², "88–124 % of the entire block budget" — and `README.md`'s
  Conditioning row says in as many words that it is "live again only if the area
  budget grows". Under a 0.20 mm² row that same core is 22–31 % of the budget,
  so raising the row does not merely restate a number: it reopens [DR-0008] §4
  and, with it, the non-vetted conditioning decision and its 0.85 bit/bit
  creditable-entropy cap. That is a much larger consequence than the row itself
  and must not be triggered as a side effect. And unlike the power row, the
  design lever here has not been shown to be exhausted — option A demonstrably
  has reach.

### C. Record the miss, hold the row, and sequence the response behind the FIFO-depth decision — *recommended*

- **What**: the decision above. The miss is stated with its method and limits in
  `README.md`, `layout/floorplan/README.md` and this record; the ratified row is
  untouched; the response waits on a decision that has to be made anyway.
- **Why plausible**: it is the only option that does not spend something it
  cannot get back. Option A spends streaming function; option B spends the
  conditioner decision. This one spends time, and the thing it waits for — a
  `FIFO_DEPTH` decision jointly owned with [DR-0017] — is a decision the
  repository owes regardless of this row. It also keeps the genuinely strong
  result visible: the isolated entropy source, samplers, guard rings and
  channels are 4.1 % of the row, which is the number an integrator worried about
  an analog block's footprint would want, and which a single 0.1347 mm² headline
  buries.
- **Why not automatic**: it leaves a ratified row standing that the best
  available evidence says is missed by 2.7×, which is uncomfortable in exactly
  the way [DR-0017] §D calls out. The defence is that this record's evidence
  says the miss is **contingent on a parameter**, not structural — depth 0 gives
  88.5 % — where [DR-0017]'s says its miss survives every setting of the same
  parameter. Waiting is only honest while that stays true; if the depth decision
  lands on 8, holding the row stops being defensible and B or D must supersede.

### D. Split the row, as [DR-0017] proposes splitting the power row

- **What**: two figures instead of one — an *entropy source + isolation* area
  (2 070.8 µm², so a row around `< 0.005 mm²` with margin) and a *whole-block*
  area, each carrying its own evidential standing.
- **Why plausible**: it is the shape [DR-0017] arrived at for the same reason —
  the two halves of the number have completely different design meaning and
  completely different futures. The analog half is the one that is hard to
  change after layout and is comfortably good; the digital half is the one a
  synthesis run and a FIFO-depth decision will both move.
- **Why rejected (for now)**: it is option B with extra structure — the
  whole-block figure still has to be a number, and stating one still reopens
  [DR-0008] §4. It is also less informative here than it is on the power row:
  there, the analog figure was a *measurement* (32.8 nA across 45 corners) and
  the split separated measured from estimated. Here both halves come from the
  same inventory script with the same standing, so the split separates two
  estimates. Worth revisiting as the form of the eventual superseding record if
  option B is taken.

## Consequences

- **Positive**:
  - The last ratified row without a decision record has one. Every row that is
    missed or unmeasured — rate, entropy-binding corner, idle current, area — is
    now routed to a record that prices its responses, which is what `CLAUDE.md`
    asks for and what #94 found missing.
  - The shared root cause is stated once, findably, with numbers on both sides:
    the two 8 × 32-bit output FIFOs are 69.8 % of digital cell area *and* the
    reason the idle row misses. Anyone who proposes changing `FIFO_DEPTH` for
    either reason will find the other row's arithmetic in the neighbouring
    record instead of discovering it afterwards.
  - The asymmetry is recorded: a lever [DR-0017] correctly rejected as futile
    for power is most of an answer for area. Without this record the obvious
    (and wrong) inference from [DR-0017] §B is "FIFO depth has been considered
    and rejected".
  - The isolation result survives contact with the area budget: 4.1 % of the
    row, 2.1 % for the guard rings and channels themselves. #16's mitigations
    are not area-constrained and should not be traded against this row.

- **Negative / accepted cost**:
  - **A ratified row stays standing that the best available evidence misses by
    2.7×.** This record makes that visible rather than resolving it, and an
    integrator reading the row today is reading a target, not a claim. The note
    in `README.md` says so.
  - **The response is deferred, and deferral has a deadline this record does not
    set.** The FIFO-depth decision is named as follow-up but not filed here, and
    a follow-up that is named and not filed is a follow-up that can be lost.
  - **The number rests on an estimate.** Half of it (658 flops × a library
    constant) is hard; half (the combinational inventory, and the 60 %
    utilisation) is a pre-synthesis structural guess. A real synthesis and
    placement run will not reproduce it exactly — though it can only move the
    soft half, and the hard half alone is 98.2 % of the row.
  - **Every number here is pre-layout.** Routing, fill, taps, the power grid,
    pads and the seal ring are all absent, as are the analog cells, which have
    not been drawn. #15/#17 will add to this figure and cannot reduce it.

- **Follow-up required**:
  - **A `FIFO_DEPTH` decision record**, jointly owned with [DR-0017] (power),
    [DR-0013] (streaming semantics and the `OUT_MODE` drain cost) and this
    record (area), settling the depth once with all three consequences in view.
    It is **not filed** as of this record's date; filing it is the honest next
    step and it is the prerequisite for resolving this row either way.
  - **A synthesis flow for the three digital blocks** — the same follow-up
    [DR-0017] names, and the single thing that would replace both records'
    estimates with something measured. It does not exist in this repository.
  - **Reconcile [DR-0016]'s `shipped=False` flag** in
    `design/digital_power_estimate.BLOCKS` with #71 having shipped the RTL. The
    monitor is 2 849.4 µm² of cell area — 9.8 points of the area row once
    placed and guarded — and is currently reported outside the totals in both
    scripts.
  - **`README.md`'s `Area` row** is edited only on acceptance of option B or D,
    and only by the superseding record that states the new figure.

- **Revisit if**:
  - the `FIFO_DEPTH` decision lands — at 8 this record must be superseded by B
    or D; below 8 the estimate must be re-run and the row re-checked against the
    table above;
  - a synthesis and placement run replaces the inventory estimate, which can
    move the combinational half and the utilisation assumption but not the
    98.2 % of the row that the flop count alone accounts for;
  - the area budget is raised for any reason — [DR-0008] §4's AES-128 rejection
    is explicitly conditioned on it and would become live again;
  - [DR-0016]'s monitor is folded into the shipped totals (+9.8 points), or
    #15/#17 produce a real layout, at which point the estimate stops being the
    best available evidence.

[DR-0004]: DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0008]: DR-0008-crc32-lfsr-non-vetted-conditioner.md
[DR-0010]: DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0011]: DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md
[DR-0013]: DR-0013-interface-register-map-and-streaming-semantics.md
[DR-0015]: DR-0015-entropy-binding-corner-moves-to-the-hot-slow-corner.md
[DR-0016]: DR-0016-per-ring-liveness-monitor.md
[DR-0017]: DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
