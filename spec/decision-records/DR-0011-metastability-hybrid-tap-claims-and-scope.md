---
dr: DR-0011-metastability-hybrid-tap-claims-and-scope
title: Ship the metastability-hybrid tap's schematic with a regeneration-time bound and a measured PVT-drift figure as its ngspice evidence, and no entropy, histogram, or calibration-viability claim
status: Accepted
date: 2026-08-01
deciders: Builder (issue #43), a methodology/claims-scope decision -- not a change to a ratified spec row, see Status.
supersedes: n/a
superseded_by: n/a
related: "#43 (origin), #7 / PR #45 (the RO core the tap layers onto, unmodified), DR-0007 §1 (tap scoped as a secondary, non-gating hook), DR-0010 §Consequences/Follow-up (raises the tap's value once the raw-rate lever is spent), spec/entropy-architecture-survey.md §Recommendation 2, §B.2, §B.3, §B.4; design/xschem/meta_inv.sch, meta_nand2.sch, meta_arb.sch, ro_meta_tap.sch, ro_array_core_meta.sch; sim/tb/meta-arb-regeneration/, sim/tb/ro-meta-tap-skew/, sim/tb/ro-array-core-meta-power/; sim/records/2026-08-01-{meta-arb-regeneration,ro-meta-tap-skew,ro-array-core-meta-power}-{01,02,03}.md"
---

# DR-0011: Ship the metastability-hybrid tap's schematic with a regeneration-time bound and a measured PVT-drift figure as its ngspice evidence, and no entropy, histogram, or calibration-viability claim

## Status

- 2026-08-01: Accepted (Builder, #43).

## Context

### What #43 owes, and where the goalposts already are

The architecture survey (`spec/entropy-architecture-survey.md` §Recommendation 2)
and [`DR-0007`](DR-0007-multi-ro-xor-combined-entropy-source.md) §1 both carry the
metastability hybrid as a *stretch* item, scoped identically: a self-timed
matched-delay strobe off an RO transition into a metastable latch, layered onto
the RO core, never a free-standing source, and never gating the core's own
critical path. [`DR-0010`](DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md)
§Consequences raises the item's value without touching its scope: with the
raw-rate row now pinned to the jitter-energy limit `(★)`, a metastability tap is
the one architectural option that could raise that row without spending power,
because it is not rate-limited by accumulated phase noise the way the RO core is.

Neither document asks this issue to *close* that opportunity — measuring whether
the tap delivers entropy at all is explicitly out of reach of a transistor-level
ngspice run (see below) — only to build the schematic, keep it from perturbing
the core, and say honestly what is and is not established about it. That
"honestly" is this record's whole job: the survey raised a specific
substantiability objection to this candidate and this record has to answer it
head-on rather than assume it away.

### The survey's objection, verbatim

§B.2 (ngspice substantiability) draws a sharp line:

> directly simulating the full resolution-time statistics of a metastable
> element by running many noise-seeded transient trials and building a
> histogram is substantially harder to substantiate in ngspice than RO jitter
> accumulation

and separately states what *is* available:

> What ngspice can substantiate directly and cheaply: the regeneration time
> constant of a given latch/FF topology via a DC transfer-curve sweep near the
> balance point (the classical Kinniment/Chester characterization method) ...
> This is a meaningfully weaker claim than what RO jitter accumulation can
> support, and should be presented as such.

§B.4 adds a second, independent objection that is not about simulation at all://
a metastable arbiter's balance point drifts with **static mismatch** and with
**PVT**, degrading entropy silently rather than failing loudly, and the
literature's answer is a calibration loop — itself a new potential coupling
path that has to be re-argued alongside RO injection locking, not assumed safe
because the RO core's isolation work (#16) already covers it.

This record's job is to take the "meaningfully weaker claim" §B.2 offers, run it
for real, report what it actually gives (which turns out to be weaker still, in
a specific and quantifiable way — see §2), and turn §B.4's drift concern into a
measured number rather than a caveat.

### What was built to test this

- `design/xschem/meta_inv.sch` / `meta_nand2.sch` — unstarved minimum-width
  delay and logic cells, deliberately not `ro_stage`/`ro_nand2`: the tap wants
  the sharpest edge the process gives, the ring wants the opposite.
- `design/xschem/meta_arb.sch` — the metastable element: a cross-coupled NAND2
  SR latch, symmetric by construction, built from two identical `meta_nand2`
  instances (§B.3's "reuse an existing standard-cell FF" first pass is not
  taken — the open PDK ships no xschem symbols for the `gf180mcu_fd_sc_mcu9t5v0`
  library, only for `gf180mcu_fd_pr` primitives, so a library FF would need a
  hand-authored symbol around its CDL netlist, and a library FF's setup/hold
  window is characterized for being *met*, which is §B.3's own objection to
  that route).
- `design/xschem/ro_meta_tap.sch` — input buffer, two three-deep matched strobe
  paths differing only in one trim load (`cta`/`ctb`), the arbiter, and an
  output buffer, on its own supply pin `vddm`.
- `design/xschem/ro_array_core_meta.sch` — `ro_array_core` (unmodified,
  instantiated as a subcircuit) plus `ro_meta_tap` hanging off `xo`.
- Three testbenches, each run at the three PVT corners this repository's other
  entropy-source records use — `ff`/−40 °C/3.63 V, `ss`/−40 °C/3.63 V,
  `tt`/27 °C/3.30 V — matching `sim/records/2026-08-01-ro-array-core-power-{04,05,06}.md`:
  - `sim/tb/ro-array-core-meta-power/` — the core-unperturbed claim.
  - `sim/tb/meta-arb-regeneration/` — the survey's "allowed" measurement.
  - `sim/tb/ro-meta-tap-skew/` — trim sensitivity and its PVT drift.

## Decision

We will ship the tap's schematic with exactly the following four claims, each
backed by a testbench and a record at three PVT corners, and no others.

### 1. Claimed: the tap does not gate the RO core's own critical path

This is structural, not just measured: `design/xschem/ro_array_core.sch` and
`design/ro_array_core.spice` are byte-identical to what they were on `main`
before this issue (`git diff main..HEAD -- design/xschem/ro_array_core.sch` is
empty). `design/ro_array_core.spice`'s *bytes* differ from `main` only because
this issue's netlist-export fix (module docstring, `design/netlist.py`)
re-wraps every SPICE continuation line at a column the exporter now owns
instead of inheriting xschem's — the token stream is unchanged, which
`sim/tests/test_netlist_export.py` asserts as a property. `ro_array_core_meta`
instantiates the untouched core plus the tap as two subcircuits; nothing about
the core's own schematic, symbol, or generated netlist changed.

The residual question — whether the one gate load the tap presents on `xo`
couples back into the rings through the combining `xor2`'s own `Cgd` — is
measured, not asserted, by running `sim/tb/ro-array-core-meta-power/` against
its baseline counterpart `sim/tb/ro-array-core-power/`, testbench-for-testbench
identical except for the tap's presence:

| Corner | `period_r1/r2` | `i_r1_a/i_r2_a` | `p_rings_w` | `ring_swing_v` | `xo_swing_v` |
|---|---|---|---|---|---|
| `ff`/−40 °C/3.63 V | −0.004 % / −0.030 % | −0.005 % / +0.021 % | +0.009 % | −0.015 % | **−0.124 %** |
| `ss`/−40 °C/3.63 V | −0.018 % / −0.018 % | +0.008 % / +0.016 % | +0.012 % | +0.010 % | **−0.129 %** |
| `tt`/27 °C/3.30 V | −0.012 % / −0.019 % | +0.006 % / +0.015 % | +0.010 % | +0.020 % | **−0.073 %** |

(deltas of the tap-present record vs. the matching baseline record, e.g.
`sim/records/2026-08-01-ro-array-core-meta-power-01.md` vs.
`…-ro-array-core-power-04.md`; full figures in the six meta-power records.)

Every ring-side quantity — period, per-ring current, ring power, ring swing —
moves by under 0.03 % at every corner tested, which is noise-floor territory
for a deterministic transient run, not a measured effect. `xo_swing_v` is the
one quantity that moves consistently (−0.07 % to −0.13 %, same sign at all
three corners): the XOR node now drives one extra gate, exactly the load
`design/xschem/ro_meta_tap.sch`'s own commentary names as "the entire load this
cell presents." That is the residual coupling path, it is real, it is small,
and it is now a number instead of an assumption.

**Not claimed**: that the tap is free. `i_tree_a` rises 3.2–5.1 % at the three
corners (the XOR tree driving a new load), and the tap's own supply current on
`vddm` is new. See §4.

### 2. Claimed, with a stated and quantified limit: a regeneration-time bound, not a regeneration-time constant

`sim/tb/meta-arb-regeneration/` runs exactly the method §B.2 calls "directly
substantiable" — seven `meta_arb` instances released with a shared reference
edge and a skew `dt` spanning five decades (100 ps down to 1 fs, plus an
exactly-balanced control), reading `tau` off the slope of resolution time
against `ln(1/dt)` between adjacent decades. It is deterministic (no noise
sources, no seeds), so it is exactly reproducible — the property the histogram
approach the survey declines cannot offer.

What it actually returns, at all three corners tested
(`sim/records/2026-08-01-meta-arb-regeneration-{01,02,03}.md`):

| Decade pair | `ff`/−40 °C | `ss`/−40 °C | `tt`/27 °C | spread |
|---|---|---|---|---|
| 100 ps ↔ 10 ps | **−0.221 ps** | **−0.240 ps** | **−0.221 ps** | sign-indeterminate |
| 10 ps ↔ 1 ps | 0.621 ps | 0.775 ps | 1.082 ps | 1.74× |
| 1 ps ↔ 100 fs | 0.244 ps | 0.231 ps | 0.289 ps | 1.25× |
| 100 fs ↔ 10 fs | 0.0287 ps | 0.0269 ps | 0.0321 ps | 1.19× |
| 10 fs ↔ 1 fs | 0.0030 ps | 0.0026 ps | 0.0035 ps | 1.33× |

The physics behind the method predicts one constant `tau` per corner,
independent of which decade pair produced it — the decade-pair repetition in
the testbench is that self-check, stated in the testbench's own header before
the run. It fails, at all three corners, in the same shape: the coarsest pair
(100 ps ↔ 10 ps) returns a **negative** value, un-physical for a regeneration
constant, and every other pair's estimate falls by roughly an order of
magnitude as the decade pair gets finer, rather than holding constant. This is
not corner noise — the same shape, including the near-identical negative value
at the coarsest pair, reproduces at all three corners.

The reading that is consistent with the circuit rather than with a solver
artifact: at the 100 ps / 10 ps skews, the latch resolves in tens of
picoseconds dominated by ordinary logic propagation delay through
`meta_nand2`, not by exponential regeneration from a near-balanced start — the
exponential-growth model the method assumes has not been entered yet at those
skews, so fitting a slope to it there measures the wrong regime, and a
negative or unstable result is the expected diagnostic. The finer pairs, where
the resolved times cluster near a common asymptote (`t_res` moves by under a
femtosecond from the 10 fs to the 1 fs instance), are closer to the metastable
regime the method is meant for, but their own pairwise spread over PVT — 19 %
to 33 % between the three sub-picosecond pairs — does not converge to a single
`tau` either; it only narrows the plausible range to roughly **3 fs to 300 fs**
across the pairs and corners that are not obviously out of regime.

**Claimed**: the method the survey names as substantiable is runnable in this
schematic, deterministically and reproducibly, and it bounds the arbiter's
regeneration behavior to the low tens-to-hundreds-of-femtosecond range — a
number consistent with a minimum-width CMOS latch in this process, and a
result the survey did not have.

**Not claimed**: a single point-value `tau` per corner. The self-check the
survey's own method carries is the finding here: it does not converge on this
solver, at these decade steps, to one number. Reporting one anyway — picking
the "best-looking" decade pair and calling it *the* regeneration constant —
is exactly the overclaim this record exists to refuse. Closing that gap would
need either a finer/adaptive solver configuration than a print-step sweep
(tighter internal `tmax`, or an event-driven step near the balance point) or a
different technique entirely (an AC/DC loop-gain extraction at the balance
point, which the survey's method is a transient stand-in for) — neither is
attempted here.

**Not claimed at all, regardless of which number the method converges to**: a
resolution-time histogram, or anything about the *distribution* of resolution
times, which is what an entropy claim would need and which §B.2 declines as a
transient-noise substantiation problem this repository has not taken on.

### 3. Claimed: a measured trim sensitivity, and a measured PVT drift of it

`sim/tb/ro-meta-tap-skew/` gives the tap four deliberately detuned instances
(`ctb - cta` = 0.05, 0.5, 1, 2 fF) and reads the release-skew `dt` each produces.
At every corner the four points are linear to within 2 % of the ideal 2× ratio
(`dt(2 fF)/dt(1 fF)` = 1.967 / 1.961 / 1.958 at `ff`/`ss`/`tt` — the testbench's
own self-check that the skew is coming from the trim load and not from
somewhere else), so `dt` per fF of imbalance is a well-defined number:

| Corner | `dt_per_ff_s` | vs. `ff` |
|---|---|---|
| `ff`/−40 °C/3.63 V | 13.23 ps/fF | 1.00× |
| `ss`/−40 °C/3.63 V | 19.12 ps/fF | 1.45× |
| `tt`/27 °C/3.30 V | 18.21 ps/fF | 1.38× |

(`sim/records/2026-08-01-ro-meta-tap-skew-{01,02,03}.md`, `dt_per_ff_s`.)

**Claimed**: a trim capacitor sized to place `dt` at a target value — in
particular, near `tau` from §2 above, which is the balance regime — moves by
up to **1.45× across the three corners tested**, before any device mismatch is
added on top. §2's own bound puts `tau` at 3–300 fs; a trim step anywhere in
that range produces a `dt` that a 45 % PVT swing in the fF-to-`dt` conversion
alone can carry outside the regeneration window a fixed setting was aimed at.
This is a direct, measured answer to §B.4's concern that a one-time trim
cannot be assumed to hold: at this drift rate, on these three corners alone,
it cannot.

**Not claimed**: that a calibration loop is or is not viable, or how it should
be built. §B.4's second objection — that a re-centering loop is itself a new
coupling path requiring its own isolation argument — is untouched by this
record; nothing here is a loop, and nothing here argues one would be safe.

### 4. Claimed: a measured power cost, kept off the ratified `Power` row on purpose

The tap has its own supply pin `vddm` for the same reason each ring has its
own: so its cost is separately accountable rather than folded into a number
that would misrepresent the RO core. Measured directly on the array
(`sim/tb/ro-array-core-meta-power/`, the corner-accurate figure — the tap is
driven by the array's own `xo` node, whose transition rate falls at slower
corners):

| Corner | `p_rings_w` | `p_tree_w` | `p_tap_w` | combined total |
|---|---|---|---|---|
| `ff`/−40 °C/3.63 V (power-binding) | 269.5 µW | 150.4 µW | **187.0 µW** | 606.9 µW |
| `ss`/−40 °C/3.63 V | 165.5 µW | 74.9 µW | **120.2 µW** | 360.6 µW |
| `tt`/27 °C/3.30 V | 127.5 µW | 66.9 µW | **87.3 µW** | 281.7 µW |

`sim/tb/ro-meta-tap-skew/`'s own metered instance, driven by a fixed 480 MHz
stimulus rather than the array's actual (corner-dependent) `xo` rate, agrees
with the array figure to 0.14 % at `ff`/−40 °C — where the fixed stimulus rate
was deliberately chosen to match the array's measured rate at that corner —
and diverges at the other two (31 % at `ss`, 40 % at `tt`) because the array's
own `xo` rate falls with the ring periods at those corners while the fixed
stimulus does not. That divergence is not a discrepancy to explain away; it is
the expected consequence of one testbench holding drive rate fixed and the
other not, and it means `sim/tb/ro-meta-tap-skew/`'s power figures should be
read as "the tap's cost at a stated fixed drive rate," not as a second,
corner-independent prediction of the array-driven cost. `sim/tb/ro-array-core-meta-power/`
is the authoritative figure for what the tap actually costs attached to the
shipped array, at each corner.

**Claimed**: the tap costs a real, measured, non-trivial amount of power — of
the same order as the rings themselves at every corner tested.

**Not counted against the ratified `< 500 µW` row.** That row is measured, in
every record that cites it (`DR-0010` §3), against `design/ro_array_core.spice`
— the schematic this record leaves untouched. The tap lives in a separate
schematic (`ro_array_core_meta`) that nothing on `main` instantiates by
default; it is a stretch item, not a shipped one, and the `Power` row governs
what ships. Stated plainly for whoever next considers promoting the tap out of
stretch status: at the power-binding corner, the combined array-plus-tap total
is 606.9 µW, **1.21× over** the current row. Adopting the tap as shipped is not
free under the existing budget and this record does not paper over that.

## Alternatives considered

### Attempt the resolution-time histogram anyway, with noise-seeded transient trials

- **What**: add TRNOISE sources to `meta_arb` and run many seeded transient
  trials near the balance point, building an empirical resolution-time
  distribution directly.
- **Why plausible**: it is the only route to an actual entropy figure, which
  is what this candidate would need to be evaluated as more than a stretch
  hook.
- **Why rejected**: this is precisely what §B.2 declines, for two compounding
  reasons neither of which this record can defeat by trying harder — resolving
  whether a given trial resolves early or takes exponentially long needs
  timestep resolution finer than this transient run can afford at a run count
  large enough to be a distribution rather than a handful of points, and the
  flicker-noise contribution to the resolution-time tail is a non-stationary
  process SPICE's transient-noise synthesis is not built to represent
  faithfully at these timescales. §2's own finding — that even the
  *deterministic* decade-pair method does not converge to a stable number on
  this solver — is independent evidence that a noise-seeded version of the
  same circuit would be harder to trust, not easier.

### Report a single point-value `tau`, chosen from whichever decade pair looks cleanest

- **What**: pick the 100 fs ↔ 10 fs pair (the tightest cross-corner spread,
  19 %) and report it as *the* regeneration time constant.
- **Why plausible**: it would give downstream work (a calibration-loop design,
  a future entropy estimate) a single number to design against, which is more
  usable than a range.
- **Why rejected**: the method's own self-check — every decade pair should
  agree — fails, and picking the pair that happens to look best is exactly the
  selective reporting `CLAUDE.md`'s "no claim without a testbench" rule exists
  to prevent. A range with a stated failure mode at its edges is a smaller but
  honest claim; a point value chosen post hoc is a larger claim this record
  cannot actually support.

### Skip the ngspice substantiation attempt and cite only the schematic and the survey's judgment

- **What**: build the schematic, state that §B.2 already covers what is and is
  not substantiable, and not run `sim/tb/meta-arb-regeneration/` or
  `sim/tb/ro-meta-tap-skew/` at all.
- **Why plausible**: less simulation cost, and the survey's own text already
  says what the *method* can and cannot do — an implementer might reasonably
  think there is nothing left to run.
- **Why rejected**: the survey characterizes the *method*, not this specific
  cell on this specific PDK's transistor models on this solver. Whether the
  method actually converges here — and by how much it does not, per §2 — is
  new information the survey could not have had, and `CLAUDE.md` requires a
  testbench behind every claim in this repository, including the claim that a
  survey's prior judgment still holds for the concrete circuit built here.

## Consequences

- **Positive**:
  - The tap's schematic exists, in scope, and its one load-bearing structural
    claim — it does not gate the RO core — is verified the same way DR-0010's
    own baseline is verified (measured deltas at three PVT corners), not
    asserted from the topology alone.
  - The survey's "allowed" measurement (§B.2) was actually attempted rather
    than assumed to work, and the result — a bound, not a constant, with a
    documented and physically-motivated failure mode at large skew — is new,
    citable information this repository did not have before, obtained without
    claiming more than the data supports.
  - §B.4's drift concern is now a number (1.45× dt-per-fF spread across three
    corners) instead of a citation, which is exactly the input a future
    calibration-loop design would need and did not have.
  - The tap's power cost is measured and separately accountable (its own
    supply pin), so a future decision about adopting it is made against a
    real number rather than the survey's "very likely to fit" plausibility
    argument (§B.3).

- **Negative / accepted cost**:
  - **No entropy claim exists for this tap, and none is scheduled by this
    record.** The tap remains exactly what DR-0007 §1 and the survey scoped
    it as: a stretch hook, not a rate-row contributor. DR-0010's hope that it
    "could raise the rate row back up without spending power" is not resolved
    here in either direction — it is not evaluated, because evaluating it
    needs the histogram this record explicitly declines to attempt.
  - **The regeneration-time result is a range spanning roughly two orders of
    magnitude (3–300 fs), not a design parameter.** Any future calibration
    work has to either narrow this itself or proceed without a precise `tau`
    to target.
  - **Adopting the tap as shipped costs real power against a row that is
    already 83 % spent** (DR-0010 §Consequences): +187 µW at the power-binding
    corner puts the combined total 1.21× over the current `< 500 µW` row. This
    record does not resolve that; it states it so the next decision is made
    with the number in hand.
  - **The calibration-loop question §B.4 raises is entirely open.** Nothing
    here designs one, and nothing here re-argues the isolation risk a loop
    would introduce (§B.4's second point) — both remain exactly as open as
    before this record, now with a drift figure to design against.

- **Follow-up required**:
  - Any future work that treats this tap as more than a stretch hook must
    re-derive an entropy claim from a technique this record does not use
    (histogram, or an analytic/semi-analytic alternative to it) — the bound in
    §2 does not support one.
  - A calibration-loop design, if ever undertaken, inherits the 1.45×
    dt-per-fF PVT spread from §3 as its design target and still owes §B.4's
    second objection (the loop's own coupling-path risk) its own analysis
    alongside #16's floorplan isolation work.
  - Promoting the tap out of stretch status requires reconciling +187 µW
    against the `< 500 µW` `Power` row — either a `Power`-row revision (which
    DR-0010 already names as the row that gives next if N = 2 proves
    insufficient) or a lower-power tap redesign. Neither is scheduled.
  - `design/README.md`'s "Metastability-hybrid tap" section is updated by this
    same change to point at this record instead of stating the tap is "not in
    these schematics."

- **Revisit if**: a finer or adaptive-step ngspice configuration (or a
  DC/AC loop-gain technique standing in for the transient decade sweep)
  converges the §2 bound to a single stable `tau` per corner; or a future
  issue judges a seeded-noise histogram run affordable despite §B.2, and
  either confirms or overturns the bound here; or the `Power` row moves for
  an unrelated reason (DR-0010 §Consequences) and the tap's +187 µW no longer
  has to be reconciled against it.
