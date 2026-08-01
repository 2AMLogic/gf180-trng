---
dr: DR-0012-sampler-fixed-external-clock
title: Clock the sampler from a fixed external clock, not a divider on either entropy-source ring
status: Accepted
date: 2026-08-01
deciders: Robb Walters (engineering) — issue #9's binding architectural judgment call, per DR-0007 §6's obligation that #9 pins the sampler clock source
supersedes: n/a
superseded_by: n/a
related: "#9 (origin), #7/PR #45 (ro_array_core), #8 (conditioner, already fixes the clk/rst_n/raw_bit/raw_valid interface this record's cell drives), #13 (worst-corner analysis, blocked on this record's corner-metric selection); DR-0001 (raw tap), DR-0003 (raw rate, ratified), DR-0007 §4/§6 (corner metric, binding obligation), DR-0010 (proposed raw-rate row, not ratified); design/README.md §The sampler (#9)"
---

# DR-0012: Clock the sampler from a fixed external clock, not a divider on either entropy-source ring

## Status

- 2026-08-01: Accepted, as part of issue #9's implementation. DR-0007 §6
  scopes this choice to #9 and names it binding on #13; this record is the
  short decision record DR-0007 §6 recommends (not strictly mandatory, but
  called out because the choice gates a downstream worst-corner analysis).
- 2026-08-01: Renumbered `DR-0011` → `DR-0012` before merge. This record was
  drafted as DR-0011 on a branch that forked before
  [#47](https://github.com/2AMLogic/gf180-trng/pull/47) merged; #47 took
  DR-0011 for the metastability-hybrid tap's claims and scope. Two numbers
  were allocated in parallel from two branches, and the one that merged first
  keeps its number. Nothing in the decision changed. Simulation records and
  testbench headers written before the renumber are cited under the correct
  number here; `design/README.md` §Erratum records the two testbench-source
  SHAs the renumber moved.

## Context

`design/ro_array_core.spice` (#7, PR #45) ships the entropy source: two
independent, separately-supplied ring oscillators, XOR-combined into one
internal node `xo`. `xo` is not a chip pin — DR-0001 puts the raw tap at the
**sampler** output, after digitization — so #9 owns both the sampling
flip-flop and the clock that drives it, and DR-0007 §6 states plainly that
this choice is binding: *"#9 pins the sampler clock source, which selects
the corner metric in §4."*

DR-0007 §4 spells out the fork precisely. For a ring oscillator sampled with
period `T_s`, min-entropy per bit depends on `Q = σ²_acc(T_s) / T₀²`. Under
white-noise (random-walk) jitter accumulation, `σ²_acc(T_s) = σ₁² · (T_s /
T₀)`, so:

- **Fixed sample clock** (`T_s` independent of `T₀`): `Q ∝ σ₁² / T₀³`. Per
  DR-0007 §4, the measured minimum over this repository's PVT grid is at
  `ss`/−40 °C/3.63 V, about 1.5× worse than `ff` at the same temperature and
  supply.
- **Sample clock divided down from one of the rings** (`T_s = k · T₀` for
  some fixed integer `k`, i.e. the accumulated-period count per sample is
  fixed rather than the wall-clock sample period): `Q ∝ σ₁ / T₀`. Under this
  metric, `ss` and `ff` at −40 °C/3.63 V sit within 4 % of each other —
  unresolvable at this repository's 4-seed PVT grid (DR-0006).

Either way the cold/+10 %-supply region binds; only the *process letter* is
unsettled, and #13 cannot name it until the clock source — and therefore the
metric — is fixed. This record is what fixes it.

A second, independent concern is the one the original issue text raises
directly: *"the sampling-clock relationship to the entropy ROs, and
avoidance of deterministic beat patterns between sampler and source."* A
clock derived from one of the two rings is, by construction, in a fixed
integer relationship with that ring's own period — the opposite of the
non-integer frequency skew DR-0007 §1 deliberately builds between the two
rings to avoid injection locking. Using one ring as the sampler's own timing
reference reintroduces a structured relationship between the entropy source
and the thing observing it, inside the very cell whose output is the raw
tap.

No rate evidence exists yet at this repository's target rate (DR-0003's
`> 1 Mbps`, ratified, vs. DR-0010's proposed `> 500 bps` — see the
"Rate target" note in the Decision section below); this is an architecture
decision, not a measured one, and does not depend on which rate figure is
current when it is read.

## Decision

**We will clock the sampler (`sampler_core.clk`, and therefore
`sampler_dff`'s `clk` input) from a fixed external clock, with no divider
circuitry derived from either entropy-source ring.**

Concretely:

1. `design/xschem/sampler_dff.sch` and `design/xschem/sampler_core.sch`
   contain no clock-generation or clock-division circuitry. `clk` is an
   ordinary input pin, sourced externally (in simulation, an ideal pulse
   source; on silicon, whatever system clock the integrator supplies).
2. This resolves DR-0007 §4's corner-metric fork: the entropy-binding
   metric is `Q ∝ σ₁² / T₀³`, measured minimum at `ss`/−40 °C/3.63 V. **#13
   should use this metric and this corner family when it identifies the
   process letter.**
3. **Rate target.** `sim/README.md`/`README.md`'s `Raw rate` row currently
   cites [DR-0003](DR-0003-throughput-defined-at-the-raw-tap.md) (`> 1 Mbps`,
   ratified) rather than the not-yet-ratified
   [DR-0010](DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md)
   (`> 500 bps`, proposed). #9 targets **DR-0003's ratified figure**. Because
   the clock is external and carries no frequency relationship to either
   ring, `R_raw = f(clk)` by construction at every corner — retargeting the
   rate later (whether DR-0010 is accepted, or any other figure is chosen)
   is a clock-frequency parameter change in whatever testbench or top-level
   integration drives `sampler_core.clk`, and requires no change to this
   record's decision or to the schematics it governs. The clock-source
   question and the rate-target question are independent, and this
   architecture keeps them independent in the implementation, not just in
   principle.
4. **Consequence for DR-0003's "report `R_raw`, sustained" obligation.**
   Because sample rate does not depend on ring speed under this
   architecture, meeting the rate row reduces to the sampler resolving
   correctly (no missed sample, no unbounded metastable failure) at the
   chosen clock frequency, at every corner — a setup/hold/metastability
   question, answered by `sim/tb/sampler-dff-setup-hold/`, not a multi-cycle
   transient-noise rate measurement.

## Alternatives considered

### Sample clock divided down from one ring

- **What**: Pick one of the two entropy-source rings, divide its own output
  by a fixed integer `k`, and use the result as `sampler_core.clk`. This is
  a classic RO-TRNG sampling scheme and needs no external clock pin.
- **Why plausible**: No external clock dependency — the whole block becomes
  self-clocking, which is attractive for a standalone IP block, and it is
  the scheme most literature RO-TRNG designs of this general shape use when
  no other on-chip clock is assumed available.
- **Why rejected**: Two independent reasons, either alone sufficient. First,
  it collapses DR-0007 §4's corner metric to `Q ∝ σ₁/T₀`, under which the
  fast and slow process corners are within 4 % — below this repository's
  measurement resolution at 4 seeds — leaving #13 with no corner to name.
  Second, it ties the sampler's timing reference to one of the two signals
  the sampler is meant to be observing independently of, reintroducing
  exactly the fixed source/observer relationship DR-0007 §1's non-integer
  ring-frequency skew exists to avoid at the array level. Using a ring as
  its own sampling clock does not literally violate DR-0007 (the *rings*
  stay non-integer-related to each other), but it revives the same class of
  concern — a deterministic beat between the thing being sampled and the
  thing doing the sampling — one level closer to the raw tap, which is the
  specific failure mode the original issue's text calls out.
- **What would change this**: if a later design needs the block to be fully
  self-clocking (no external clock pin at all — e.g. a hard macro with a
  minimal pin count budget), that is a real, different set of constraints
  and would warrant its own superseding decision, not a quiet reversal of
  this one.

### Sample clock divided down from a THIRD, dedicated free-running ring (not one of the two entropy rings)

- **What**: Add a third ring, outside the entropy array, whose sole purpose
  is generating the sample clock via a divider — self-clocking, but not
  coupled to either entropy ring.
- **Why plausible**: Keeps the block self-contained (no external clock pin)
  while avoiding the direct source/sampler coupling of the previous
  alternative, since the clock ring shares no XOR node with the sampled
  signal.
- **Why rejected**: Adds a third free-running ring purely for clock
  generation, on top of an entropy array whose N = 2 sizing was already
  driven to its floor by the `< 500 µW` power row (`design/README.md`
  §`ro_array_core`: N = 4 measured 1.9–2.0× over the power budget, N = 2 is
  what fits). A third ring plus a divider chain is exactly the area/power
  cost DR-0007's Consequences section already flags as scarce, spent on a
  clock rather than on entropy margin. It also still leaves the fixed
  clock's own frequency uncharacterized against process/voltage/temperature
  in a way an external clock — whose frequency is a testbench/integration
  parameter, not a simulated quantity — is not. Not rejected on principle;
  rejected on this repository's current power/area budget. Live again if a
  fully self-clocking requirement is added (see the note on the previous
  alternative).

## Consequences

- **Positive**:
  - DR-0007 §4's corner-metric fork is resolved: `Q ∝ σ₁²/T₀³`, minimum at
    `ss`/−40 °C/3.63 V. #13 is unblocked on this specific question.
  - No deterministic beat risk between the sampler's timing reference and
    the signal it samples — the concern the original issue's acceptance
    criteria name directly.
  - The clock frequency is a parameter external to the schematics
    (`design/xschem/sampler_dff.sch`, `design/xschem/sampler_core.sch`
    contain no clock generation of any kind), so retargeting the raw rate —
    whether DR-0010 is later ratified or any other figure is chosen — never
    requires touching this decision or the cells it governs.
  - `R_raw` at the DR-0003 binding corner follows architecturally
    (`R_raw = f(clk)` at every corner) rather than requiring a long,
    expensive transient-noise run to measure a sustained bit rate; the
    remaining verification obligation is a setup/hold/metastability
    characterization, which is far cheaper to run across a full PVT grid.

- **Negative / accepted cost**:
  - The block needs an external clock pin/pad, rather than being fully
    self-clocking. For an IP block with an expected digital host (which
    already supplies `clk`/`rst_n` to the conditioner per
    `design/conditioner/README.md`), this is a modest cost; it would be a
    real one for a pin-constrained, fully autonomous macro.
  - The external clock's own jitter/duty-cycle/frequency accuracy is now a
    system-level dependency this repository does not control or
    characterize — the sampler's own setup/hold margin
    (`sim/tb/sampler-dff-setup-hold/`) is characterized against an ideal
    clock edge, not against a realistic external clock's own jitter.

- **Evidence as of 2026-08-01** (added with this record's implementing PR, so
  the claim in item 4 above is not left as an assertion): the
  setup/hold/metastability obligation this decision creates has been measured
  over the full 45-point PVT grid,
  `sim/records/2026-08-01-sampler-dff-setup-hold-01…45.md`. `clk`→`Q` is
  82.3 ps (`ff`/−40 °C/3.63 V) to 203.0 ps (`ss`/+125 °C/2.97 V — DR-0003's
  rate-binding corner), the asynchronous reset takes at every point, and **no
  point shows a metastable hang**: an edge struck at zero setup *and* zero
  hold leaves `Q` within 0.33 mV of a rail 1 ns later and within 6.4 µV at
  100 ns. That last one is the property item 4 actually depends on, since a
  fixed external clock guarantees the data edge will sometimes land inside the
  aperture. Setup time is bracketed to under 500 ps everywhere, crossing 59 ps
  inside the grid (captured at 59 ps in 13 of 45 points, all fast and/or cold).
  See `design/README.md` § "Setup/hold and metastability, measured".

- **Follow-up required**:
  - **#13**: use the `Q ∝ σ₁²/T₀³` metric and the `ss`/−40 °C/3.63 V minimum
    named above when identifying the process letter for the entropy-binding
    corner.
  - **#26**: the exact `clk` pin assignment and any board/system-level clock
    source requirements (frequency accuracy, jitter budget) are that
    issue's job, not this record's.
  - If DR-0010 is later ratified (or any other raw-rate figure is chosen),
    re-derive the clock frequency used in `sim/tb/sampler-array-digitize/`
    and `sim/tb/sampler-dff-setup-hold/` from the new target; this record's
    decision does not change.

- **Revisit if**: a fully self-clocking (no external clock pin) requirement
  is added to the block's scope, or #13's measurement finds the
  `ss`/−40 °C/3.63 V corner is not in fact the metric's minimum over the
  full covered grid (the `fs`/`sf` corners remain uncovered per DR-0006, per
  DR-0007 §4).
