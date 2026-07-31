---
dr: DR-0006-ro-jitter-characterization-pvt-sampling-strategy
title: Reduce the PVT/seed grid for RO delay-cell jitter characterization to a documented cost/coverage trade-off instead of a full 5-corner x 3T x 3V x N-seed factorial
status: Accepted
date: 2026-07-31
deciders: Builder (issue #4)
supersedes: n/a
superseded_by: n/a
related: "#4, #2, #5, #7 (consumer); sim/characterization-ro-delay-cell-jitter.md"
---

# DR-0006: Reduce the PVT/seed grid for RO delay-cell jitter characterization to a documented cost/coverage trade-off instead of a full 5-corner x 3T x 3V x N-seed factorial

## Status

- 2026-07-31: Accepted (adopted directly during issue #4's characterization
  work; the trade-off is stated here rather than silently truncated, per
  #4's curator guidance).

## Context

Issue #4 requires "Full PVT grid on every recorded figure: -40/27/125 C x
+/-10% supply x process corners, with the fast/cold/high-supply corner
called out explicitly" and "Multiple independent seeds per configuration"
for both candidate RO delay-cell topologies at multiple stage counts (a
stage-count sweep to show jitter accumulation trends), plus flicker- and
linearity-sensitivity supplementary checks.

The harness's default corner set (`mos`) is 5 process corners (`tt`, `ff`,
`ss`, `fs`, `sf`). A literal full factorial -- 5 corners x 3 temperatures x
3 supplies x >=4 seeds -- applied to every one of the 8 transient-noise
(`tran-noise`) testbenches this issue adds (`ro-inv-{03,05,09}stage-jitter`,
`ro-cinv-{05,09}stage-jitter`, `ro-inv-05stage-{flicker,lownoise}`,
`trnoise-calibration`) would be several hundred ngspice invocations at
~1-5 minutes of wall-clock each (measured empirically during this issue's
bring-up: a single seeded run of a 5-stage ring at one PVT point took
~130-150s on the development machine; 9-stage and current-starved rings
measured up to ~300s under contention with other concurrent jobs on the
same shared host). A literal full-factorial sweep at this scale is many
hours of ngspice wall-clock, which the curator's implementation guidance
explicitly anticipated ("Jitter-accumulation runs are simulation-expensive
-- choose run lengths that bound the sqrt(t)-scaling check without
exploding cost, and record that cost/coverage trade-off explicitly rather
than silently truncating").

## Decision

We will run a **reduced, explicitly two-tier PVT/seed grid** rather than
the full factorial, split by role:

1. **Flagship reference config** -- `ro-inv-05stage-jitter` (candidate A,
   5-stage plain-inverter ring; 5 stages is the reference stage count this
   characterization treats as representative for candidate A) gets the
   full **process-corner-reduced** grid: `{tt, ff, ss}` x `{-40, 27, 125}
   deg C` x `{2.97, 3.30, 3.63} V` = 27 PVT points, each with the
   testbench's default 4 seeds (108 seeded runs total). This is the config
   issue #7 (RO core schematic) should size against.
2. **Every other transient-noise testbench** (the candidate-A stage-count
   comparison points `ro-inv-{03,09}stage-jitter`, candidate B at both
   stage counts `ro-cinv-{05,09}stage-jitter`, and the two supplementary
   sensitivity checks `ro-inv-05stage-{flicker,lownoise}`) gets exactly
   **three "headline" PVT points**, each with the default 4 seeds:
   - nominal: `tt` / 27 C / 3.30 V
   - fast/cold/high-supply: `ff` / -40 C / 3.63 V -- the corner issue #4's
     acceptance criteria calls out explicitly as "the figure that will
     matter most later" (tightest timing margin, most jitter-starved)
   - slow/hot/low-supply: `ss` / 125 C / 2.97 V -- the contrasting
     worst-case-margin corner (slowest oscillation, most RC/thermal noise)
3. **`trnoise-calibration`** (an analytic anchor with no active devices --
   two RC branches driven by an explicit `trnoise()` source) gets the
   nominal point only, 4 seeds. Its own testbench header states the
   physics being checked (the `trnoise()` sample-and-hold PSD mapping) has
   no PDK/corner dependence by construction; a PVT sweep of an ideal-RC
   circuit would not test anything the single point does not already
   cover.
4. The two **deterministic** `.noise`/`.ac` cross-check testbenches
   (`inv-stage-noise`, `cinv-stage-noise`) and the **deterministic**
   analytic anchor (`noise-floor-resistor`) are cheap (~1-3s per point,
   no active-device noise in the resistor case) and get the **full**
   `{tt, ff, ss}` x 3T x 3V grid (or, for `noise-floor-resistor`, `tt` x 3T
   at nominal supply only -- its own header states process corner must NOT
   move ideal-resistor noise, so sweeping corner would only be re-proving
   a null result already covered by any one corner).

The process-corner axis itself is reduced from the harness's full 5-corner
`mos` set to `{tt, ff, ss}` for every grid above: `fs`/`sf` (fast-NMOS/
slow-PMOS and the reverse) are dropped. This is a coverage gap, stated
explicitly rather than silently: every stage in these ring testbenches
receives an *identical* injected noise source, so what `fs`/`sf` would
primarily expose -- an N/P drive-strength asymmetry -- shows up as a
duty-cycle/slew-rate systematic, not as the period-jitter figure this
characterization measures. `tt`/`ff`/`ss` bound the speed range that
matters for jitter magnitude; `fs`/`sf` coverage is left for a follow-up
if duty-cycle-sensitive circuitry (e.g. an edge-triggered sampler) is
added downstream.

## Alternatives considered

### Full 5-corner x 3T x 3V x >=4-seed factorial for every testbench

- **What**: Apply issue #4's stated PVT/seed requirements literally and
  uniformly to all 8 transient-noise testbenches.
- **Why plausible**: Simplest to state, no judgment calls about which
  points matter more.
- **Why rejected**: ~180 seeded runs per testbench x 8 testbenches, at
  measured per-run costs of 1-5 minutes, is many hours to tens of hours of
  ngspice wall-clock on a single development machine -- explicitly the
  "exploding cost" the curator's guidance warned against. It would also
  spend the same diligence on a supplementary linearity check
  (`ro-inv-05stage-lownoise`) as on the flagship sizing reference, which
  does not match how the resulting numbers will actually be used (per
  the summary's "safe to size against" statement, only the flagship needs
  to bear that weight).

### Single point (nominal only) for everything

- **What**: Run every testbench at `tt`/27 C/3.30 V only.
- **Why plausible**: Cheapest possible option; still produces *a* jitter
  number for each topology/stage-count.
- **Why rejected**: Directly violates issue #4's explicit PVT-grid
  acceptance criterion and would say nothing about the fast/cold/
  high-supply corner the issue calls out as the one that matters most --
  the entire point of characterizing before #7 sizes against it.

## Consequences

- **Positive**: The flagship config (`ro-inv-05stage-jitter`) gets full
  PVT-grid diligence and is the one issue #7 should size against. Every
  other config still gets the three PVT points that matter most (nominal,
  and the two corners bracketing worst-case margin) with a full,
  seed-averaged spread, at a small fraction of the full-factorial cost.
- **Negative / accepted cost**: The stage-count trend (jitter accumulation
  vs. stage count) and the candidate-A-vs-B comparison are only checked at
  3 PVT points, not the full grid -- a corner-dependent crossover between
  candidates or stage counts outside those 3 points would not be caught by
  this characterization. `fs`/`sf` process-corner coverage is dropped
  entirely for every RO jitter/noise testbench in this issue.
- **Follow-up required**: If #7's schematic work surfaces a design that is
  sensitive to N/P drive-strength asymmetry (e.g. a duty-cycle-dependent
  sampler), file a follow-up issue to add `fs`/`sf` runs for the specific
  configs that matter to that design, rather than assuming this
  characterization already covers it.
- **Revisit if**: A future design decision needs jitter figures at a PVT
  point this trade-off did not cover, or the stage-count/candidate
  comparison needs to be re-checked at additional corners because the
  3-point comparison showed corner-dependent behavior worth resolving.
