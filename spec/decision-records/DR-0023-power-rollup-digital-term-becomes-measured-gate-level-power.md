---
dr: DR-0023-power-rollup-digital-term-becomes-measured-gate-level-power
title: Move power_rollup.py's digital term from the DR-0004 Tier 2 pre-synthesis estimate to #145's measured gate-level figure at the shared 0.25 transitions/net/cycle activity -- the active row moves from met (86.6 %) to a 2.2x miss, and DR-0017's idle miss narrows from 4.5x to ~4.0x
status: Proposed
date: 2026-08-21
deciders: Proposed by #174 (Builder). NOT ratified -- acceptance is an operator decision, per #145 §4.4 and the same convention [DR-0017] and [DR-0019] were filed under (both cited by #174 as the direct precedent for this record's shape).
supersedes: n/a (edits no ratified figure; on acceptance it supersedes the evidential standing of the 2026-07-31 ratification note's "Active: met" paragraph, and narrows -- without superseding -- [DR-0017]'s idle-miss figure)
superseded_by: n/a
related: "#145 (the measurement this record acts on), #174 (this decision), sim/characterization-digital-sta-area-power.md §4 (the corner sweep, §4.4 the prior deferral this record resolves), DR-0004 (claim tiers -- Tier 2 estimate, defined and unchanged), DR-0017 (idle row, Proposed -- this record narrows its headline miss figure without touching its diagnosis or its four options), DR-0019 (area row, Proposed -- the precedent for this record's shape: report the miss, do not edit the ratified row, route the verdict change through a record), DR-0021 (defines `level: gate` and, in §3, forbids citing one as a measured supply current -- the reason this record's term is labelled MEASURED-at-gate-level and never bare MEASURED), DR-0018 (the per-ring output buffer whose adoption produced the 433.2 uW active figure this record's Decision supersedes the standing of), DR-0022/#147 (the post-route gate-level *simulation* that does not yet supply a per-net switching-activity annotation -- named in Follow-up), #171 (the PDN population that moved measured leakage from 0.63x to 0.89x the estimate at the row's binding corner, since the pre-#171 records this issue's own filed numbers cite); README §Target specification -- Power"
---

# DR-0023: Move `power_rollup.py`'s digital term from the [DR-0004] Tier 2 estimate to the measured gate-level figure

## Status

- 2026-08-21: Proposed, by the Builder of #174. Not ratified.

Until ratified the `Power` row stands exactly as the 2026-07-31 ratification
left it, and this record is a proposal, not spec. The pull request that files
this record edits `sim/tools/power_rollup.py`'s *evidence*, not any ratified
figure: the tool's own totals change (that is the whole point -- an evidence
tool that keeps citing a superseded source is worse than no tool), but
`README.md`'s `< 500 uW` / `< 1 uA` target text is untouched, exactly as
[DR-0017] and [DR-0019] left their own rows untouched. The README's
*evidenced-figure* commentary -- the "Now evidenced (#14 ...)" sentence and
the "Active: met" / "Idle: missed" paragraphs beneath it, which are provenance
commentary on the row rather than the ratified target -- is updated by this
same pull request, on the same basis [DR-0017]'s idle-miss paragraph already
established: reporting a miss is not editing the row.

## Context

### What `power_rollup.py` computed before this record, and why

`sim/tools/power_rollup.py` assembles the whole-block active and idle power
figures the README's `Power` row is evidenced against:
`P_active = P_array + P_sampler + P_digital` and
`I_idle = I_analog + I_digital_leakage`. The array and sampler terms are
transistor-level MEASUREMENTS; the digital term (conditioner + health tests +
interface) has, since #14, been `design/digital_power_estimate.py`'s
[DR-0004] Tier 2 estimate -- a gate-level inventory of the RTL priced against
the PDK's own Liberty library, because at the time the digital blocks had no
netlist to simulate or synthesize.

That estimate gave **23.1 uW active** (at `ff_n40C_3v60`, the corner the
README's active row states it binds at) and **4.43 uA idle leakage** (at
`ff_125C_3v60`, the corner the idle half binds at), rolling up to the figures
the 2026-07-31 ratification note and `sim/characterization-startup-and-power-budget.md`
both cite: **433.2 uW active (86.6 % of the row, met)** and **4.46 uA idle
(446 % of the row, missed by 4.5x -- [DR-0017])**.

### What #145 measured, and why it did not already replace the estimate

`design/trng_top/trng_top.synth.v` (#143) and `layout/digital/trng_top.def`
(#111, re-run with a power-delivery network by #171) did not exist when the
estimate was written; they do now. #145 built a `level: gate` ([DR-0021])
static-timing-and-power sweep over the committed routed DEF --
`sim/tb/digital-sta-power/run_sta.py`, OpenSTA + OpenRCX inside OpenROAD, 5
liberty decks x 3 interconnect decks = 15 corners, one record each under
`sim/records/2026-08-18-digital-sta-power-{01..15}.md` (superseding the
pre-[#171] `2026-08-17-...` generation, still committed and still accurate
about the DEF it names -- #183) -- and reported the same quantity the
estimate computes, at the same [DR-0003] ratified 1 MHz raw rate and the
**same declared 0.25 transitions/net/cycle activity** the estimate assumes.
Full write-up: `sim/characterization-digital-sta-area-power.md` §4.

At the row's own binding corners, from the current (post-#171) record family
(`sim/tools/digital_corner_characterization.py`):

| | estimate (`design/digital_power_estimate.py`) | measured (`level: gate`, #145) | ratio |
|---|---:|---:|---:|
| Active, `ff_125C_3v60`/`max` (digital section's own worst corner) | 65.77 uW (ungated variant, like-for-like -- see below) | **712.4 uW** | **10.83x** |
| Active, across the swept 5-corner set, ungated-vs-measured | 29.57 .. 65.77 uW | 401.7 .. 712.4 uW | 10.6x .. 14.3x |
| Idle leakage, `ff_125C_3v60` | 4.43 uA | **3.946 uA** | **0.89x** |

Two things this table already forces:

1. **The digital section's own active-power worst corner is `ff_125C_3v60`,
   not `ff_n40C_3v60`.** The estimate's headline corners were chosen to match
   where the README row's *target text* says the whole block binds --
   `ff_n40C_3v60` for active, because that is where the entropy source (the
   then-dominant term) is fastest and leakiest. Now that the digital term is
   an order of magnitude larger than the entropy source, that corner choice
   no longer represents the digital section's own worst case: at
   `ff_n40C_3v60` the measured digital figure is 625.1-648.3 uW across the
   three interconnect corners, materially below its own 712.4 uW worst case
   at `ff_125C_3v60`/`max`.
2. **`design/digital_power_estimate.py`'s dynamic term is checked against its
   own `interface_mux_feedback` (ungated) variant, not its headline.** The
   headline credits the two output FIFOs with clock gating the synthesized
   netlist never built -- Yosys mapped every write-enable to a feedback
   `mux2`, and the as-built netlist contains zero integrated clock-gating
   cells (`sim/characterization-digital-sta-area-power.md` §4.2). Comparing
   against the headline instead would overstate the ratio by another ~1.7x
   and would be comparing measurement against a model of a circuit that was
   never built.

Why the gap is real and not an artefact, per §4.3 of the characterization
document: a single library fact settles the dominant term by hand.
`gf180mcu_fd_sc_mcu9t5v0__dffq_1`'s `CLK` pin declares 0.278 pJ per cycle,
**unconditional on `D`**, and the netlist has 708 flip-flops -- 196.8 uW
before anything toggles, at 1 MHz, on its own 5.3x the estimate's entire
ungated active figure. The estimate instead prices a flop's clock-edge energy
at the *data* activity (`p_internal += n * sec_activity * ...`), which is
wrong for every clocked flop regardless of what it stores. That assumption,
and the absent clock gating, are now documented in
`design/digital_power_estimate.py`'s own docstring (added ahead of this
record, per its final paragraph naming #174 as the deciding issue).

**#145 deliberately did not perform this substitution** (§4.4 of its
characterization document): "swapping a 10-14x larger number into the tool
that evaluates a ratified README row changes that row's verdict, which is an
operator decision, not a Builder one." That is exactly the boundary
[DR-0017] and [DR-0019] were filed to cross for the idle and area rows, and
this record is the same crossing for the digital power term specifically --
named explicitly in both #145 §4.4 and #174 as the issue that owns it.

### The four questions #174 poses, and this record's answer to each

1. **Does the digital term become the measured figure?** Yes -- see Decision.
2. **At what activity?** The SAME uniform 0.25 transitions/net/cycle both
   sides already share. This is deliberately not this design's real activity
   -- a TRNG's data-dependent switching is not representable by a uniform
   model -- but it is the assumption that makes the *comparison* fair, it is
   already the estimate's own assumption (so adopting the measurement changes
   no activity model, only which side of the same model is authoritative),
   and a real per-net annotation is a dependency this record does not have to
   wait on to be honest about what it is reporting (see Follow-up).
3. **Scope reconciliation.** The measured figure covers *all* trng_top digital
   `COMPONENTS` OpenROAD placed for #145's sweep: 2502 logical instances plus
   6136 tapcell/endcap/filler cells [#171] added for the power delivery
   network. The estimate's inventory is 1655 cells across three logical
   blocks (conditioner, health tests, interface) with no PDN term at all.
   This record's Decision states the wider scope is the *more* representative
   one for a whole-block rollup, not a defect to correct for: the PDN cells
   are real, placed, and part of what the digital section actually is once
   built, in the same way [DR-0019]'s area miss found routing/fill/taps only
   ever add to a pre-layout estimate and never subtract.
4. **Does `design/digital_power_estimate.py` stay?** Yes, unedited in method.
   It remains the pre-synthesis prediction the measurement is checked
   against, and its own docstring already says so. What changes is only that
   `sim/tools/power_rollup.py` stops treating its number as the one that
   decides the row's verdict.

## Decision

**We will** make the measured, gate-level, `level: gate` figure
`sim/tools/power_rollup.py`'s digital term for both the active-power and
idle-leakage rollups, replacing `design/digital_power_estimate.py`'s [DR-0004]
Tier 2 estimate as the number that feeds the printed totals -- while keeping
the estimate computed and printed alongside it, unmistakably labelled as
CONTEXT ONLY.

Specifically, on filing this record (all of the following ship in the same
pull request, because a tool change and its own row-note update travel
together or the row-note goes stale on merge):

1. **`sim/tools/power_rollup.py`'s digital term is read from
   `sim/tools/digital_corner_characterization.py`'s aggregation of the
   committed `sim/records/*-digital-sta-power-*.md` family** (15 corners,
   `level: gate`, [DR-0021]) -- specifically the corner where each quantity is
   individually worst across that swept set (`ff_125C_3v60`/`max` for active,
   `ff_125C_3v60` for leakage), the same convention this script already
   applies to the idle row's two clock-park states. This needs no PDK: the
   records are committed evidence, unlike the estimate's live Liberty-library
   lookup.
2. **Rate scaling is an exact re-derivation of the same liberty model, not a
   new approximation.** The record family carries two fixed clock rates (1
   MHz and 20 MHz, the P&R run's own constraint); every non-leakage watt in a
   liberty power report is `toggles/sec x energy/toggle` at a declared
   activity, linear in the clock rate, while leakage is not. Checked against
   the committed family's own 1 MHz/20 MHz pair at all 15 corners,
   `P(rate) = leakage + (P_1MHz - leakage) * (rate / 1MHz)` agrees with the
   as-recorded 20 MHz figure to better than 2e-6 relative everywhere in the
   set -- so this is arithmetic on committed numbers, not a new claim.
3. **Provenance labelling.** Every place the digital term appears in the
   tool's output says `MEASURED-at-gate-level`, never bare `MEASURED`. Per
   [DR-0021] §3, a `level: gate` liberty-power result "may not" be cited as a
   supply-current measurement; the array and sampler terms (real
   transistor-level current measurements) keep the bare `measured` label they
   already carry, and the digital term's label stays visibly different from
   both that and the `ESTIMATE` context line next to it.
4. **`design/digital_power_estimate.py` is unchanged in method.** It keeps
   computing and its docstring keeps documenting the two assumptions the
   netlist falsified. `power_rollup.py` still runs it and prints its result,
   at the same two corners it always used, explicitly marked "CONTEXT ONLY
   (does not feed the totals)".
5. **`README.md`'s ratified `< 500 uW` / `< 1 uA` target text is not edited.**
   Its evidenced-figure commentary is updated to state, in the same place and
   the same register [DR-0017]'s idle-miss sentence already occupies:
   - **Active is now evidenced as missed**, not met: from the current tool
     output, **1.122 mW at `ff`/-40 C/3.63 V, 224.5 % of the row** -- entropy
     source 393.2 uW (measured) + sampler 16.9 uW (measured) + digital 712.4
     uW (MEASURED-at-gate-level, `ff_125C_3v60`/`max`, rate-scaled to 1 MHz).
     Citing this record (Proposed), exactly as the idle sentence cites
     [DR-0017] (Proposed).
   - **Idle's already-reported 4.46 uA / 4.5x miss narrows to 3.979 uA /
     ~4.0x** -- analog 32.8 nA (measured, unchanged) + digital 3.946 uA
     (MEASURED-at-gate-level, was 4.43 uA ESTIMATE). [DR-0017] itself is
     **not** superseded: its diagnosis (ungated standard-cell leakage; no
     retention/power-switch cell in this library) and its four options are
     untouched, only its headline figure narrows.
   - `sim/characterization-startup-and-power-budget.md` and
     `sim/characterization-digital-sta-area-power.md` §4.4 each get a pointer
     note to this record, in the same "Update --" style the #78 buffer-
     adoption note already established in the former document, rather than a
     rewrite of their own historical text (both documents already say to
     prefer the tool's own output over their own numbers where the two
     disagree).

**No option below is chosen automatically by ratifying this record's
*mechanism*** independent of its *consequence*: accepting this record is
accepting that the active row is reported as missed. There is no reading of
the evidence in which the digital term is adopted and the row stays "met".

## Alternatives considered

### A. Leave `power_rollup.py` on the estimate, and only report the gap in prose

- **What**: keep the tool exactly as it was; state the #145 vs. estimate
  comparison only in `sim/characterization-digital-sta-area-power.md`, as
  #145 itself did.
- **Why plausible**: it changes no tool output and needs no README edit at
  all -- the smallest possible diff, and #145 explicitly chose it as the
  interim state precisely because #174 was filed to make this decision.
- **Why rejected**: #174 exists because this state is not meant to be
  permanent, and CLAUDE.md's "no claim without a testbench" cuts against a
  tool that keeps citing a 10-14x-superseded number as if nothing measured it
  yet. The estimate is not *wrong* to keep running (Decision item 4), but
  letting it keep deciding the row's verdict once a measurement of the same
  quantity exists is the asymmetric version of "relaxing the spec to make
  results pass" CLAUDE.md forbids -- refusing to *tighten* a claim once
  better evidence exists is the same failure in the other direction.

### B. Adopt the measurement, but wait for #147's switching-activity annotation first

- **What**: hold this decision until a VCD/SAIF-derived per-net toggle count
  from #147's post-route gate-level simulation ([DR-0022]) can replace the
  uniform 0.25 transitions/net/cycle assumption on both sides.
- **Why plausible**: it is the technically strongest available path -- a
  measured activity is strictly better evidence than a declared uniform one,
  and #174's own filing named it as such. A verdict change built on an
  admittedly-uniform activity model risks a second flip once real activity
  data lands.
- **Why rejected**: the annotation does not exist yet and is not close.
  `sim/characterization-digital-sta-area-power.md` §5a states plainly that
  #147's re-run "does NOT contribute a switching-activity annotation... wiring
  its activity into a liberty power run is still future work rather than
  something already available" -- there is no in-flight work this record
  would be jumping ahead of. More importantly, the *uniform* assumption is
  not the reason for the 10-14x gap: §4.3 shows the dominant term (unconditional
  per-cycle clock-edge energy, 196.8 uW on its own) is invariant to whatever
  the data activity turns out to be, because it is charged whether or not
  `D` moves at all. A real activity annotation would move the smaller,
  genuinely activity-dependent terms (data-net switching, 83.5 of 517.7 uW at
  `tt_025C_3v30`) and could not plausibly erase the miss. Waiting for it
  before reporting today's best-available evidence is the [DR-0017] §D
  failure mode again: "the spec is not being relaxed to make results pass,
  the results are being ignored to leave the spec comfortable."

### C. Adopt the measurement, but reconcile scope by excluding [#171]'s PDN cells

- **What**: subtract the tapcell/endcap/filler contribution from the measured
  figure before rolling it up, so the comparison stays apples-to-apples
  against the estimate's logic-only, three-block inventory.
- **Why plausible**: it would isolate exactly the delta a re-run of the
  estimate against the real netlist (holding the PDN fixed) could explain,
  and it is the more conservative of the two readings of "scope
  reconciliation" -- reporting only what the estimate could in principle have
  predicted.
- **Why rejected**: it answers the wrong question. The rollup's purpose is
  the whole *block's* power, and the PDN cells are real, placed, and part of
  what `trng_top`'s digital section actually is once synthesized -- excluding
  them would understate the row on the same logic [DR-0019] rejected for the
  area row (routing/fill/taps only ever add to a pre-layout number). It is
  also not the dominant effect: at the row's own binding corner
  (`ff_125C_3v60`) #171's PDN population adds roughly 4.2 uW of leakage
  (10.03 -> 14.21 uW, the pre- vs. post-#171 record generations) against a
  ~650 uW dynamic gap that predates #171 entirely -- the pre-#171 record
  generation already showed a 10-14x dynamic gap with no PDN cells in it at
  all. Scope purity here would buy a single-digit-percent correction to the
  active figure at the cost of reporting a number that is not what the
  block, as synthesized, actually draws.

### D. Split the row, as [DR-0017] split idle into analog and digital halves

- **What**: state two active-power figures instead of one -- an *entropy
  source + sampler* figure (measured, the part hardest to change post-layout)
  and a *whole-block* figure (including the now-dominant digital term).
- **Why plausible**: it is the shape [DR-0017] chose for idle, for the same
  underlying reason -- the two halves have different evidential standing and
  different design trajectories, and it keeps the genuinely strong result
  (410.1 uW from the entropy source + sampler alone, 82.0 % of the row on
  their own) visible rather than buried under a >1 mW headline.
- **Why not chosen here (for now)**: unlike idle, where the two halves were
  already ~450x apart in absolute terms and rarely traded against each other
  in the same design decision, the active side's two halves are within a
  small factor and both draw from the SAME 500 uW budget an integrator has to
  plan against -- splitting invites exactly the double-counting risk
  [DR-0019] Alternative D flagged for the analogous area split. It is also
  strictly less informative about the row's actual verdict: the row asks
  whether the *whole block* draws under 500 uW active, and it does not, by a
  factor of 2.2. This record reports the split components in its own table
  (Decision item 5) without adopting a split *row* -- a genuine split row, if
  wanted, is better decided alongside whatever design response (if any) is
  chosen for the miss this record reports, not as a side effect of choosing
  the evidence source.

## Consequences

- **Positive**:
  - The whole-block power rollup stops citing a number #145 measured to be
    10-14x too small on the dominant term. A reader of `power_rollup.py`'s
    output, or of the README row it evidences, now sees the best available
    evidence rather than a superseded pre-synthesis guess.
  - The idle row's already-`Proposed` miss ([DR-0017]) gets more accurate
    without needing its own re-derivation: `power_rollup.py`'s digital term
    and [DR-0017]'s digital term are the same script call, so this record's
    change updates both consistently, and narrows the miss from 4.5x to
    ~4.0x -- real headroom, even though it does not close the gap.
  - `design/digital_power_estimate.py` keeps a clean, well-defined role (the
    pre-synthesis prediction) instead of a load-bearing one it can no longer
    support, and its own docstring already says so.
  - The scope difference (2502+6136 cells measured vs. 1655 cells estimated)
    is stated explicitly in the tool's own docstring and output rather than
    left to be discovered by comparing two numbers that turn out not to be
    counting the same thing.

- **Negative / accepted cost**:
  - **The active row's verdict changes from "met" to "missed by 2.2x", and
    that is a materially different product claim** in exactly the sense
    [DR-0010]'s rate change and [DR-0017]'s idle change already were. An
    integrator who read "433 uW, met" is now reading "1.12 mW, 224 %". This
    record does not soften that; it reports it.
  - **The row's evidence now rests partly on a uniform, not-representative
    activity model**, shared with the estimate it replaces, so the substitution
    changes *which side* of that shared assumption is authoritative without
    removing the assumption itself. Section 2 above argues the dominant term
    is activity-*independent* (a flop's per-cycle clock energy), which limits
    how much this matters, but it is not zero -- the data-net switching term
    genuinely would move under a real annotation.
  - **The digital section's own worst corner (`ff_125C_3v60`) is now the
    figure quoted, not the corner the README's active-row text names
    (`ff_n40C_3v60`)**, because the digital term now dominates and using each
    term's own worst case is the conservative convention this script already
    applies elsewhere. A reader checking the row against its own stated
    binding corner and the tool's printed worst-case corner will see they
    differ, and the tool's own output states why.
  - **The measurement is still not signoff** ([DR-0021] §3, restated in
    `sim/characterization-digital-sta-area-power.md` §5): no IR drop, no
    on-chip variation, no foundry-signed extraction. Adopting it as the
    rollup's best-available term does not upgrade its standing beyond that.

- **Follow-up required**:
  - **A per-net switching-activity annotation** from #147's post-route
    gate-level simulation ([DR-0022]), replacing the shared uniform 0.25
    transitions/net/cycle assumption with a measured one on both the digital
    term and (if ever re-derived) the estimate. Named as follow-up by #145
    §4.4, restated here, and still not filed as its own issue as of this
    record's date -- filing it is the honest next step, per the same pattern
    [DR-0017] and [DR-0019] left their own synthesis-flow follow-ups in.
  - **`README.md`'s Power row's evidenced-figure text**, updated by this same
    pull request (Decision item 5) -- not deferred, because an accepted
    record with a stale README pointer is worse than no record.
  - **Whatever design response (if any) the operator chooses for the active
    miss** is out of scope for this record, exactly as [DR-0017] priced idle
    responses and [DR-0019] deferred area responses without choosing one.
    This record's job is the evidence source, not the design lever.

- **Revisit if**:
  - a per-net switching-activity annotation lands (#147/[DR-0022]'s named
    follow-up) and moves either figure enough to change the row's verdict
    direction, which the activity-independence argument above says is
    unlikely for the active miss but is not ruled out for the (already
    narrow) idle margin;
  - a re-synthesis, re-placement or re-routing run changes the digital
    section's cell count, library or PDN population, any of which the
    measured figure would move with and the estimate would not (unless it is
    itself re-derived against the new inventory);
  - the operator chooses a design response to the active miss (e.g. a
    narrower interface, a different conditioner, or a synthesis re-target)
    that changes the netlist this record's figures were measured against, at
    which point #145's sweep must be re-run before this record's numbers are
    still current.

[DR-0003]: DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0004]: DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0010]: DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0017]: DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
[DR-0018]: DR-0018-adopt-per-ring-output-buffer.md
[DR-0019]: DR-0019-area-row-versus-output-fifo-dominated-digital-section.md
[DR-0021]: DR-0021-gate-level-timing-and-power-records.md
[DR-0022]: DR-0022-post-route-gate-level-simulation-records.md
