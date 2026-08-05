---
dr: DR-0020-fifo-depth-set-to-two-against-power-area-and-streaming
title: Set the interface's output FIFO_DEPTH to 2, decided once with the idle-power, area and 500 bps streaming consequences in view
status: Proposed
date: 2026-08-04
deciders: Proposed by #99 (the joint FIFO-depth follow-up DR-0019 named and did not file). NOT ratified — acceptance is an operator decision, as DR-0001…DR-0004, DR-0007, DR-0017 and DR-0019 were.
supersedes: n/a (DR-0013 fixed the interface but never fixed a depth; `FIFO_DEPTH = 8` is a shipped RTL default, not a decided value)
superseded_by: n/a
related: "#99 (origin), #96/PR #98 (DR-0019, which named this record as its unfiled follow-up), #26/DR-0013 (the interface, its two output FIFOs and the `OUT_MODE` drain cost this record prices), DR-0017 (the `< 1 µA` idle row and its §B depth figures), DR-0019 (the `< 0.05 mm²` area row and its depth table), DR-0010 (the proposed 500 bps raw rate that sets what a buffered word is worth), DR-0003 (the superseded 1 Mbps rate the depth was originally sized against), DR-0008 (K = 8, so what a conditioned word is worth, and §4's AES-128 rejection conditioned on the area budget), DR-0001 (the two output paths and the `OUT_MODE` flush rule), DR-0002 (the 1024-sample start-up window), DR-0004 (claim tiers and the sequential dataset), DR-0016 (the ring-liveness monitor, excluded from DR-0019's totals); README §Target specification — Power, Area and Raw rate rows, none of which are edited by this record"
---

# DR-0020: Set the interface's output `FIFO_DEPTH` to 2, decided once with the idle-power, area and 500 bps streaming consequences in view

## Status

- 2026-08-04: Proposed, by #99. Not ratified.

Until ratified, `FIFO_DEPTH = 8` stands as the shipped default and this record
is a proposal, not spec. **No RTL, no generated register map, no estimate script
and no ratified row is edited by the pull request that proposes this record** —
it changes only this file and the `related` fields of the three records that
jointly own the decision.

## Context

### The question, and why three records could not answer it separately

[DR-0013] fixed the interface — four registers, a 32-bit mode-selected streaming
port, two output FIFOs, and the flush scopes — but it never fixed how deep those
FIFOs are. `FIFO_DEPTH = 8` is a parameter default in
`design/interface/trng_interface.v` and `design/interface/regmap.py`, carried
into `design/digital_power_estimate.py` and the floorplan inventory. It has
never been the subject of a decision.

Two later records then discovered that this undecided default is the single
largest term in two ratified rows:

- [DR-0017] found the two 8 × 32-bit FIFOs are **78 % of the block's flop
  count**, and the `< 1 µA` idle row missed by 4.5×.
- [DR-0019] found the same FIFOs are **69.8 % of digital cell area and 82.4 % of
  the interface's**, and the `< 0.05 mm²` area row missed by 2.7×.

Neither could take the decision alone. [DR-0017] §B rejected the depth lever on
the *power* row and was right to; [DR-0019] showed that same rejection does not
transfer to the *area* row, where the lever has far more reach, and explicitly
declined to take a design decision inside a spec-process record. [DR-0013] owns
the third consequence — what a shallower queue costs a reader — and was written
against a rate row that [DR-0010] has since proposed moving by a factor of 2000.

[DR-0019] §Consequences named this record as follow-up and noted, honestly, that
"a follow-up that is named and not filed is a follow-up that can be lost". This
is it.

### What the depth is worth on the idle-power row — [DR-0017] §"Alternatives considered → B"

Cited, not re-derived. At the row's own binding corner `ff` / +10 % / +125 °C,
against `< 1 µA`:

| `FIFO_DEPTH` | idle current | vs the `< 1 µA` row |
|---:|---:|---|
| 8 (shipped) | 4.46 µA total (32.8 nA analog + 4.43 µA digital) | 446 % |
| 2 | **2.04 µA** | miss |
| 1 | **1.64 µA** | miss |
| 0 (both FIFOs deleted) | **1.44 µA** | miss |

[DR-0017] §Revisit-if prices the slope at **~0.8 µA per halving** at this
corner. Its §"Why 'just tighten the estimate' is not available" states the
conclusion this record adopts unchanged: *"There is no inventory refinement, and
no FIFO depth, that reaches 1 µA at this corner."* The floor is set by the 146
non-FIFO flops and the whole combinational inventory, and that floor is already
1.4× the row.

**The power row therefore does not get a vote on the depth.** Every candidate
value misses it, so no candidate can be preferred over another on this axis.

### What the depth is worth on the area row — [DR-0019]'s depth table

Cited verbatim from [DR-0019] §"The same lever has very different reach on the
two rows", against the `< 0.05 mm²` row:

| `FIFO_DEPTH` | FIFO cell area | digital cell area | floorplan total @ 60 % | share of row | share @ 80 % |
|---:|---:|---:|---:|---:|---:|
| **8 (shipped)** | 51 982 µm² | 74 485 µm² | 134 713 µm² | **269.4 %** | 205.1 % |
| 4 | 25 078 µm² | 47 581 µm² | 88 175 µm² | 176.3 % | 134.9 % |
| 2 | 11 626 µm² | 34 129 µm² | 64 720 µm² | **129.4 %** | 99.5 % |
| 1 | 4 900 µm² | 27 403 µm² | 52 915 µm² | 105.8 % | 81.6 % |
| 0 (no FIFOs) | 0 µm² | 22 503 µm² | 44 268 µm² | 88.5 % | 68.5 % |

Two further figures from the same record bound what this lever can achieve:

- the **break-even**: for the floorplan total to reach 50 000 µm² at the
  script's own 60 % utilisation, digital cell area must come down to
  **25 748 µm²**. Depth 1 gives 27 403 µm²; only depth 0 (22 503 µm²) is under
  it;
- the **exclusions**: [DR-0016]'s ring-liveness monitor is left out of every row
  above and is worth **+9.8 points** on the shipped inventory, and the estimate
  contains no routing beyond the utilisation factor, no fill or tap cells, no
  power grid, no pads and no seal ring. As [DR-0019] puts it, layout "will add to
  this figure and cannot reduce it."

So on the area row the lever has real reach — 269.4 % → 129.4 % between depth 8
and depth 2 — but it does not *arrive*. At the floorplan's own 60 % utilisation
**no depth ≥ 1 meets the row**, and depth 0 is not an available design:
[DR-0001] and [DR-0013] both require an output FIFO on each path, and
`design/interface/trng_interface.py` refuses `FIFO_DEPTH < 1` outright. The
80 % column does show depth 1 (81.6 %) and depth 2 (99.5 %) under the row, but
[DR-0019] is explicit that this is "a placement density this repository has no
placer to demonstrate", and both figures still exclude the monitor and all of
layout. Choosing the more optimistic of two numbers in one's own model in order
to keep a ratified row would be the thing `CLAUDE.md` forbids.

**The area row therefore argues for the smallest depth function will tolerate,
but it cannot be closed by any of them.** What the depth decides is not whether
the row moves — it is *how far* it has to move, and therefore how much
collateral the move does.

### What the depth is worth on the streaming port — [DR-0013] at [DR-0010]'s 500 bps

[DR-0013] §Consequences states the cost side: **"An `OUT_MODE` write costs a
reader up to `FIFO_DEPTH` buffered raw words plus a partial word,"** with a
procedural mitigation (drain before switching), not an architectural one. The
FIFO's other job is the reader's deadline: the entropy source free-runs and the
port cannot back-pressure it, so a reader that does not service the queue within
`FIFO_DEPTH` word periods drops the incoming word and sets `OVF_DATA`/`OVF_RAW`.
Both quantities are `FIFO_DEPTH` × one word period, and **they pull in opposite
directions**: deeper is worse on the mode switch and better on the deadline.

A word period is fixed by three cited facts — a raw word is 32 consecutive raw
samples ([DR-0013] §3), a conditioned word is one 256-sample conditioner block
([DR-0008], K = 8), and the raw rate is [DR-0010]'s proposed **500 bps**:

| | one raw word | one conditioned word |
|---|---:|---:|
| at 500 bps ([DR-0010], proposed) | **64 ms** | **512 ms** |
| at 1 Mbps ([DR-0003], superseded by [DR-0010] on acceptance) | 32 µs | 256 µs |

Multiplying through (arithmetic on the figures above, not a new measurement):

| `FIFO_DEPTH` | raw deadline / mode-switch cost @ 500 bps | conditioned deadline / mode-switch cost @ 500 bps |
|---:|---:|---:|
| 8 (shipped) | 512 ms | 4.096 s |
| 4 | 256 ms | 2.048 s |
| **2 (this record)** | **128 ms** | **1.024 s** |
| 1 | 64 ms | 512 ms |

For scale, [DR-0013]'s start-up scenario measures 1280 raw samples to the first
readable conditioned word, which at 500 bps is 2.56 s.

### The depth was sized against a rate that no longer exists

This is the fact that makes the decision tractable. At [DR-0003]'s `> 1 Mbps`,
`FIFO_DEPTH = 8` bought a reader **256 µs** of raw slack — a plausible interrupt
latency budget, and a sensible default. [DR-0010] proposes moving that row to
500 bps, which multiplies the wall-clock worth of every buffered word by ~2000
without anyone re-examining the parameter. At 500 bps, **depth 2 buys 128 ms of
raw slack — 500× what the whole depth-8 FIFO bought at the rate it was chosen
for**, and even depth 1 buys 250×. The shipped default is not a considered
answer to the 500 bps interface; it is an artefact of a superseded rate row.

### Reconciling the two existing statements of the streaming cost

[DR-0017] §B says a shallow FIFO is "a much bigger deal than at 1 Mbps because
each lost word is 0.5 s of accumulation"; [DR-0019] §A says "one buffered raw
word is 64 ms of accumulation and one conditioned word is 512 ms". These are not
in conflict: [DR-0017]'s 0.5 s is the **conditioned**-word figure (512 ms), and
the raw-word figure is 64 ms. This record uses [DR-0019]'s two-number form
throughout, because the raw path is the one with the tighter deadline and the
one [DR-0004]'s sequential dataset is captured from.

## Decision

**We will set `FIFO_DEPTH = 2`** for both output FIFOs, on the following rule:
*the power row cannot be reached at any depth and gets no vote; the area row
cannot be closed at any legal depth but is monotonically improved by a smaller
one; therefore the depth is set to the smallest value the 500 bps streaming
contract can defend, and the area row takes the rest.*

Depth 2 is that value. Depth 1 is a single-entry buffer, not a queue: under
[DR-0013] §3 the register read and the streaming port draw from the **same**
queue, so at depth 1 a reader has no elasticity whatsoever behind the word it is
taking, and a single missed 64 ms service window ends the contiguous run that
[DR-0004]'s sequential dataset needs. Depth 2 keeps one word of elasticity
behind the word in flight, and it does so with a raw deadline (128 ms) and a
conditioned deadline (1.024 s) that are two and three orders of magnitude
larger, in wall-clock terms, than anything the interface was originally sized to
provide.

Specifically, on acceptance:

1. **`FIFO_DEPTH` becomes 2** in `design/interface/regmap.py` (the normative
   table), which propagates to `design/interface/trng_interface.v`'s parameter
   default, the generated header, `design/interface/REGMAP.md`, and
   `design/interface/trng_interface.py`'s model default. `LEVEL_BITS` follows
   the table's own rule (enough for `0..FIFO_DEPTH` inclusive). None of this is
   done by the pull request that proposes this record — see Follow-up, and note
   the sizing hazard recorded there.
2. **`design/digital_power_estimate.py`'s `FIFO_DEPTH` constant and the
   floorplan inventory follow**, and both estimates are re-run so that
   [DR-0017]'s and [DR-0019]'s numbers stop describing a configuration the
   design no longer ships.
3. **No ratified row is edited by this record.** Per [DR-0019] §Decision item 4,
   the `Area` row moves only via the record that supersedes [DR-0019]; per
   [DR-0017] §Consequences, the `Power` row's idle half moves only on
   [DR-0017]'s own acceptance. This record moves a design parameter, not a spec
   row, which is exactly the division of labour [DR-0019] asked for.
4. **[DR-0017] is left standing, unchanged and unsuperseded.** This record does
   not resolve the idle row and does not claim to. It *confirms* [DR-0017] §B
   rather than overturning it: §B priced depth 2 at 2.04 µA against a `< 1 µA`
   row, and that is still a miss, so the depth is changed here for reasons §B
   correctly said were not power reasons. [DR-0017]'s options A and C remain the
   only paths to that row and remain an operator decision on [DR-0017]'s own
   terms. Its only edit is a `related` pointer to this record.
5. **[DR-0019] is left standing and is *not* superseded by this record**, and
   its §Decision item-4 supersession trigger does **not** fire: that trigger is
   conditioned on the decision keeping `FIFO_DEPTH = 8`, and it does not.
   Instead [DR-0019] §Revisit-if's other branch fires — *"below 8 the estimate
   must be re-run and the row re-checked against the table above"* — which is
   item 2 above plus the follow-up below. Its only edit is a `related` pointer.
6. **[DR-0013] is not superseded either.** Its §Decision clauses never fixed a
   depth; this record fills in a parameter [DR-0013] left as a default, and
   every clause of [DR-0013] — the four registers, the shared queue, the two
   flush scopes, the `OVF_*` semantics — is unchanged in meaning. It gains a
   `related` pointer so that a reader of the `OUT_MODE` drain cost finds the
   number it now costs.
7. **[DR-0008] §4's AES-128 rejection is not reopened by this record**, and
   this record deliberately does not state a replacement area row, which is the
   act that would reopen it. The honest qualification is in Consequences: any
   eventual row that accommodates this block at all weakens §4's area argument
   somewhat, and the point of setting the depth to 2 rather than leaving it at 8
   is that it makes that eventual move — and therefore that weakening — much
   smaller.

## Alternatives considered

### A. Keep `FIFO_DEPTH = 8` (do nothing)

- **What**: take the decision and decline to move the parameter, on the grounds
  that no legal depth meets the area row at the floorplan's own utilisation, so
  paying a functional cost buys a target that is still missed — [DR-0017] §B's
  own argument, transplanted to the area row.
- **Why plausible**: it is a genuinely strong argument and it nearly carries.
  [DR-0017] §B rejected this lever with the words "Paying a functional cost for
  a change that still misses the target is the worst of both", and depth 2 does
  still miss (129.4 % at 60 % utilisation). Keeping 8 also preserves the largest
  reader deadline (512 ms raw, 4.096 s conditioned), which is the friendliest
  configuration for a register-polled capture host.
- **Why rejected**: the transplant does not survive contact with the two rows'
  arithmetic. On power the lever's *whole* range is futile (4.46 → 1.44 µA
  against 1 µA), so "still misses" is the end of the argument. On area the range
  spans 269.4 % → 88.5 %, so "still misses" is a statement about *how far the
  row must move*, not about whether the change is worth making — and the size of
  that move is precisely what determines the collateral on [DR-0008] §4. Keeping
  8 also fires [DR-0019] §Decision item 4, which commits [DR-0019] to being
  superseded by a record that raises or splits the row, and [DR-0019] §B sketches
  that row at roughly `< 0.20 mm²` — under which a compact serialised AES-128
  (0.044–0.062 mm², [DR-0008] §4) stops being 88–124 % of the budget and becomes
  a minority of it, reopening the conditioner decision and its 0.85 bit/bit
  creditable-entropy cap as a *side effect of not deciding a FIFO depth*. That
  is an expensive way to keep a reader deadline that is already 2000× more
  generous than the one the parameter was chosen for.

### B. `FIFO_DEPTH = 4`

- **What**: one binary step down, keeping 256 ms of raw and 2.048 s of
  conditioned reader deadline.
- **Why plausible**: it is the least disruptive real reduction, and it halves the
  mode-switch drain cost with a deadline no reader could reasonably call tight.
- **Why rejected**: it buys the least and costs the most of the reductions.
  [DR-0019]'s table puts depth 4 at 47 581 µm² of digital cell area and 176.3 %
  of the row (134.9 % at 80 %), against depth 2's 34 129 µm² and 129.4 %
  (99.5 %) — so it leaves the row missed by 1.8× rather than 1.3×, and it is
  still nowhere near the 25 748 µm² break-even. The extra binary step of deadline
  it buys is not a step any consumer has asked for: at 500 bps the difference
  between 128 ms and 256 ms of service slack is not a difference that changes
  what software can be written.

### C. `FIFO_DEPTH = 1`

- **What**: the shallowest legal setting — 105.8 % of the area row at 60 %
  utilisation, 81.6 % at 80 %, and 1.64 µA on the power row.
- **Why plausible**: it is the only depth ≥ 1 that comes within a few points of
  the area row at the floorplan's own utilisation, and it is the *best* setting
  for the [DR-0013] §2 mode-switch cost — an `OUT_MODE` write would discard at
  most one buffered word plus a partial one, 64 ms of raw accumulation.
- **Why rejected**: it stops being a queue. [DR-0013] §3 puts the register read
  and the streaming port on the same queue, so at depth 1 there is no elasticity
  at all behind the word being read, and the raw path's service deadline becomes
  64 ms with no slack for jitter. [DR-0004]'s sequential dataset is a long
  contiguous raw capture, and [DR-0001]'s named hazard — a reader falling behind
  and invalidating the dataset — becomes a live risk for any non-realtime capture
  host. It also does not actually reach the row: 105.8 % at 60 % utilisation,
  27 403 µm² against a 25 748 µm² break-even, before [DR-0016]'s +9.8 points and
  before any of layout. Spending the last of the reader's elasticity for a
  configuration that still misses is the trade [DR-0017] §B correctly warned
  against.

### D. `FIFO_DEPTH = 0` — delete both FIFOs

- **What**: the only setting in [DR-0019]'s table that is under the row at 60 %
  utilisation (88.5 %), and the lowest idle current the lever can produce
  (1.44 µA).
- **Why plausible**: it is the only depth that reaches the area break-even
  (22 503 µm² against 25 748 µm²), and on a 500 bps interface a strict
  valid/ready port with no buffering is a coherent design.
- **Why rejected**: it is not a legal configuration of this block. [DR-0001] §3
  defines `DATA` and `RAW_DATA` as reads that *pop a FIFO*, [DR-0002] and
  [DR-0013] §4 define flush behaviour in terms of FIFO contents, [DR-0013] §2's
  `OVF_*` and `*_LEVEL` semantics presuppose a queue, and
  `design/interface/trng_interface.py` refuses `FIFO_DEPTH < 1`. Removing the
  queues is a superseding DR against [DR-0001] and [DR-0013], not a parameter
  choice. And even it does not survive its own margin: 88.5 % excludes
  [DR-0016]'s +9.8 points and all of routing, fill, taps, power grid, pads and
  seal ring, every one of which can only add.

### E. Asymmetric depths — a deeper raw FIFO than conditioned

- **What**: split the single parameter in two, e.g. `RAW_FIFO_DEPTH = 4` with
  `COND_FIFO_DEPTH = 1`, matching the fact that a raw word is 64 ms and a
  conditioned word is 512 ms, so the two paths do not need the same number of
  words to get the same wall-clock deadline.
- **Why plausible**: it is the configuration that actually fits the physics. The
  raw path carries the tight deadline and [DR-0004]'s capture requirement; the
  conditioned path gets 512 ms of slack from a single word, because [DR-0008]'s
  K = 8 makes each of its words worth eight raw ones.
- **Why rejected (for now)**: it is a second parameter in a *generated*
  normative register map — two `*_LEVEL` field widths, two occupancy counters,
  two pointer widths, and a `REGMAP.md` that has to explain why the two paths
  differ — for an advantage over symmetric depth 2 of one binary step on the raw
  deadline (256 ms vs 128 ms) while costing more total storage than depth 2 does.
  [DR-0013] deliberately made the two paths symmetric at the register map, and
  asymmetry should be bought with evidence rather than with symmetry-breaking on
  principle. If a real capture campaign later shows 128 ms is not enough on the
  raw path, this is the shape of the superseding record, and this record's
  arithmetic is the input it will need.

## Consequences

- **Positive**:
  - **The parameter is decided, once, in the open.** `FIFO_DEPTH` stops being an
    undecided RTL default that two spec records independently discovered was the
    largest term in their row. Anyone who proposes changing it again will find
    all three consequences priced in one place.
  - **The area miss falls from 2.7× to 1.3×** ([DR-0019]: 269.4 % → 129.4 % at
    60 % utilisation, 205.1 % → 99.5 % at 80 %), which is the difference between
    a row that has to move a long way and a row that has to move a little. That
    difference is the whole of this record's effect on [DR-0008] §4.
  - **[DR-0019]'s deferral is discharged rather than extended.** [DR-0019] held
    the area row on the explicit ground that the miss was contingent on an
    unexamined parameter. The parameter has now been examined, and the branch of
    [DR-0019] §Revisit-if that fires is the benign one ("below 8 … re-run and
    re-check"), not the one that forces [DR-0019]'s supersession.
  - **The streaming contract is stated in the units a reader cares about.** The
    `OUT_MODE` drain cost and the overflow deadline are the same quantity pulling
    in opposite directions, and both are now written down in milliseconds at the
    proposed rate rather than in words at an unstated one.
  - **The 500 bps re-examination is recorded.** [DR-0010] proposes moving the
    rate row by ~2000×; this is the first record to check what that does to a
    parameter sized against the old row. Others may need the same treatment.

- **Negative / accepted cost**:
  - **The reader's service deadline shrinks 4×**, from 512 ms to 128 ms on the
    raw path and from 4.096 s to 1.024 s on the conditioned path. A
    register-polled capture host on a non-realtime OS that stalls for more than
    128 ms will drop a raw word and end a contiguous run. `OVF_RAW` makes that
    visible rather than silent ([DR-0013] §2), but the run is still ended, and
    [DR-0004]'s sequential dataset is exactly the workload that cares.
  - **This record does not meet the area row and does not claim to.** 129.4 % at
    the floorplan's own utilisation is still a miss, and the 99.5 % figure at
    80 % utilisation must not be cited as a pass: it rests on a placement density
    with no placer behind it, and it excludes [DR-0016]'s +9.8 points and all of
    layout. A superseding record still has to state a row.
  - **[DR-0008] §4's area argument is weakened by whatever row eventually
    lands.** Any row that accommodates this block at all puts a compact
    serialised AES-128 (0.044–0.062 mm²) below 100 % of the budget rather than
    at 88–124 % of it, so the rejection's *area* leg is disturbed in every
    outcome, including this one. What changes with depth is how much: the
    ~`< 0.20 mm²` row [DR-0019] §B sketches at depth 8 would make that core a
    fifth to a third of the budget, which is a different conversation from the
    one a much smaller move produces. §4's second leg is untouched either way —
    [DR-0004] Tier 3 defers validation to measured silicon, so the pre-silicon
    value of removing the non-vetted penalty remains zero. This record states the
    exposure rather than routing around it; it does not settle it, because
    settling it means stating a row, which is [DR-0019]'s successor's job.
  - **The power row is untouched.** 2.04 µA against `< 1 µA` ([DR-0017] §B). A
    reader who expects a FIFO-depth decision to have helped the idle row will be
    disappointed, and should be: [DR-0017] §B said so first.
  - **Every number here is an estimate on the digital side.** Both source
    records' figures come from pre-synthesis inventories with no synthesiser,
    placer or router behind them. This record inherits that standing exactly and
    adds nothing to it.

- **Follow-up required**:
  - **An RTL/regmap issue to set `FIFO_DEPTH = 2`** in
    `design/interface/regmap.py` and regenerate `REGMAP.md` and the RTL header
    (`python3 design/interface/regmap.py --check` guards the drift), with
    `sim/tests/test_interface.py` re-run against the model. **Sizing hazard,
    found while writing this record and deliberately not fixed here:**
    `trng_interface.v` derives `raw_bit_count` as `[TRNG_LEVEL_BITS+1:0]`, which
    holds 0..31 only because `LEVEL_BITS` is currently 4. That counter counts
    raw samples into a 32-bit word (`RAW_PACK_BITS`) and has nothing to do with
    FIFO occupancy, so lowering `LEVEL_BITS` with the depth would silently
    truncate it. It must be re-sized from `RAW_PACK_BITS` in the same change.
  - **Re-run both estimates at depth 2** — `design/digital_power_estimate.py`
    (guarded by `sim/tests/test_power_rollups.py`) and
    `layout/floorplan/floorplan.py` → `layout/floorplan/reports/area.json` — so
    that the recorded inventories describe the shipped configuration. This is
    [DR-0019] §Revisit-if's "below 8" obligation.
  - **The record that states the area row**, superseding [DR-0019], once the
    re-run numbers exist. It must state explicitly what it does to [DR-0008] §4,
    per that record's own "deliberately left live" clause.
  - **[DR-0017] still owes its own resolution** (its options A or C). Nothing in
    this record advances it, and the follow-ups [DR-0017] names — a synthesis
    flow, and a power-gating DR if option A is ever taken — are unchanged.
  - **[DR-0010] must be ratified or rejected.** This record's streaming
    arithmetic is stated at its *proposed* 500 bps. If that row lands somewhere
    else, the millisecond figures above move with it and the depth choice should
    be re-checked against them — though not the direction of the choice, which
    holds for any rate far below 1 Mbps.

- **Revisit if**:
  - **[DR-0010]'s rate row does not land at 500 bps.** Everything in the
    streaming section scales inversely with the raw rate; a rate materially above
    500 bps tightens the deadlines proportionally and argues for a deeper queue.
  - **a capture campaign shows 128 ms is not enough** on the raw path for a
    [DR-0004] sequential dataset — that is alternative E's evidence, and E is the
    shape of the record that would answer it.
  - **a synthesis and placement run replaces the inventory estimate**, which can
    move [DR-0019]'s combinational half and its utilisation assumption, and could
    change which side of the row depth 2 lands on.
  - **the area row is superseded at a figure that depth 2 meets**, at which point
    the pressure this record answers is gone and a deeper queue becomes
    affordable again on its own merits.
  - **a retention-capable or power-switch cell library becomes available for
    gf180mcu** ([DR-0017] §A), which would change the power row's arithmetic
    enough that the depth might get a vote on it after all.

[DR-0001]: DR-0001-raw-and-conditioned-output-paths.md
[DR-0002]: DR-0002-health-test-parameters-and-failure-behavior.md
[DR-0003]: DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0004]: DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0008]: DR-0008-crc32-lfsr-non-vetted-conditioner.md
[DR-0010]: DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0013]: DR-0013-interface-register-map-and-streaming-semantics.md
[DR-0016]: DR-0016-per-ring-liveness-monitor.md
[DR-0017]: DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
[DR-0019]: DR-0019-area-row-versus-output-fifo-dominated-digital-section.md
