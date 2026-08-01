---
dr: DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy
title: Re-derive the raw-rate row from the jitter-energy constant measured on the shipped starved cell, raising it from 500 bps to 2 kbps
status: Proposed
date: 2026-08-01
deciders: Proposed by #46 (validating DR-0010's `(★)` on the shipped cell). NOT ratified — acceptance is an operator decision, as DR-0001…DR-0004, DR-0007 and DR-0010 were.
supersedes: "DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit — its §1 rate VALUE only, and only on acceptance. Everything else in DR-0010 stands unchanged: `(★)` as the sizing law, N = 2, eleven stages, the array of §3, the Power row, and DR-0003's definition of where the rate is measured and what corner it binds at."
superseded_by: n/a
related: "#46 (the measurement — this record's whole basis), #7 (array sizing), #12 (min-entropy on bitstreams, still owns H), #13 (minimum-Q corner over the full grid), #16 (two-ring isolation); DR-0003 (raw rate), DR-0004 (quality tiers), DR-0006 (PVT/seed coverage), DR-0007 §2 (sizing law), DR-0010 (the record this supersedes, §1 only); sim/characterization-starved-cell-jitter-energy.md; sim/records/2026-08-01-ro-ring5-starved-jitter-long-{01,02,03}.md"
---

# DR-0011: Re-derive the raw-rate row from the jitter-energy constant measured on the shipped starved cell

## Status

- 2026-08-01: Proposed, by #46. Not ratified.

## Context

[`DR-0010`](DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md)
proposes a raw-rate row of **> 500 bps**, derived from the empirical invariant
it calls `(★)`:

```
a  ≡  κ² · P_ring / (k_B · T)   =   1.79 ± 0.14
```

DR-0010 names its own largest open risk in §Consequences and in its "Revisit
if" clause: **every record `a` is fitted to is a plain, unstarved inverter
ring, and the cell the project ships is a minimum-width, series-starved one.**
It goes further and says what would move the row:

> If it shows the starved cell really does deliver far more jitter per unit
> power than the plain one, the rate row moves back up — by a superseding
> record.

That measurement has now been made. [#46] adds
[`sim/tb/ro-ring5-starved-jitter-long/`](../../sim/tb/ro-ring5-starved-jitter-long/)
— a 5-stage ring of the shipped `ro_stage`/`ro_nand2` cells, transient noise,
measurement window opened 256 periods after start-up and spanning 512 periods,
eight seeds per corner, three corners — and reports it in
[`sim/characterization-starved-cell-jitter-energy.md`](../../sim/characterization-starved-cell-jitter-energy.md),
citing `sim/records/2026-08-01-ro-ring5-starved-jitter-long-{01,02,03}.md`.

Three findings from it bear on this decision.

**1. The measurement is sound where the previous one was not.** The run
DR-0010 had to discount
(`sim/records/2026-08-01-ro-array-sanity-jitter-01.md`) was seed-independent to
0.3 % and accumulated as `lag^0.81`. The new records vary **3.9–5.9 %** at
lag 1 against a **2.7 %** reference calibrated on the committed plain-cell
family, and that spread tracks `√L` out to lag 128 (measured 28–35 %,
reference 31 %). The block-mean period is flat to **11–34 ppm** over the whole
run. `python3 sim/tools/starved_cell_jitter_energy.py --check` gates the seed
spread and passes.

**2. `σ_acc` really is a random walk for this cell.** The accumulation exponent
over the top decade of lag is **0.500 / 0.472 / 0.479** at `ss`/−40 °C/3.63 V,
`tt`/27 °C/3.30 V and `ff`/−40 °C/3.63 V. The `√t` extrapolation DR-0007 §2 and
DR-0010 both depend on is therefore justified on the shipped cell, not just
assumed.

**3. `a` is far larger for the starved cell, and just as constant.**

| | `a` (lag 1, like-for-like with `(★)`) | `a` (accumulating component only) |
|---|---|---|
| plain cell, 27-point grid (DR-0010) | 1.79, spread 1.29× | — |
| **shipped starved cell, 3 corners** | **24.84, spread 1.32×** | **11.77, spread 2.34×** |
| ratio | **13.9×** | **6.6×** |

The *form* of `(★)` survives — `a` varies 1.32× across a grid on which
`P_ring` spans 2.14× and `κ²` spans 2.43×, the same constancy the plain-cell
fit shows. Only the value moved. That is what a series starve device is for:
it fixes the ring's current, so the cell trades `T₀` against `P_ring` at
constant `E_cycle`, and it evidently converts a great deal more of that current
into phase noise than a plain inverter does.

Under `(★)`, `Q_array ∝ a`, so the rate row is linear in exactly this number.

## Decision

We will **move the raw-rate row again, and only the raw-rate row**, to the rate
the shipped array delivers under the jitter-energy constant measured on the
cell it is built from.

### 1. The row that moves

> `Raw rate` — **> 2 kbps sustained at the raw tap**, superseding DR-0010 §1's
> proposed `> 500 bps` (which in turn superseded DR-0003's `> 1 Mbps`).
> Everything else in DR-0003 is unchanged: the rate is still defined at the raw
> tap (DR-0001), still means *sustained* rather than burst, and still binds at
> `ss` / −10 % / +125 °C.

### 2. Which `a`, and why the conservative one

Three candidate values are defensible and all three are priced, from committed
records, by `python3 sim/tools/array_sizing.py --a <value>`:

| `a` | What it is | `Q_array` at `ss`/−40/3.63, 500 bps | Highest rate meeting DR-0007 §2 there |
|---|---|---|---|
| 1.79 | DR-0010, plain cell | 7.82 × 10⁻³ | 651 bps |
| **7.32** | **starved cell, accumulating component, at the entropy-binding corner itself** | 3.20 × 10⁻² | **2664 bps** |
| 11.77 | starved cell, accumulating component, mean of three corners | 5.14 × 10⁻² | 4282 bps |
| 24.84 | starved cell, lag 1, mean of three corners | 1.09 × 10⁻¹ | 9040 bps |

**This record uses 7.32** — the smallest of the three starved-cell figures —
for two independent reasons:

- **The accumulating component is the physically correct one.** DR-0007 §2
  evaluates `Q` at a sample period of order 10⁶ ring periods. `σ_acc` at lag 1
  contains a component that does not accumulate (both cells show it: the
  all-lag exponent is 0.39–0.46 for the starved cell and 0.40–0.55 across the
  plain-cell grid). Only the asymptotic slope survives extrapolation, so
  `κ²_asym` is what `Q(T_s)` is built from, even though `κ²_lag1` is what is
  like-for-like with DR-0010's number.
- **The corner that binds should supply its own constant.** `a` varies 2.34×
  across the three corners on the asymptotic measure, and the entropy-binding
  corner sits at the bottom of that range. Using the mean would quote the
  binding corner a constant it does not have.

`2664 bps` at the inequality's edge, quoted with the same **1.30×** margin
DR-0010 uses, gives **2049 bps → the > 2 kbps of §1**.

### 3. The rows and records that do not move

- **The `Power` row is unchanged** (`< 500 µW` active, `< 1 µA` idle). Nothing
  here changes any power measurement; `Q_array ∝ a` at fixed power is precisely
  the point.
- **DR-0010 §§2–5 stand as written** — `(★)` as the sizing law, N = 2, eleven
  stages, the array of §3, the five-stage costing, the minimum-Q corner. This
  record changes one input to that arithmetic, not the arithmetic.
- **DR-0002, DR-0007 §§1–2, DR-0001's raw tap and DR-0004's tiering are
  unchanged.** Nothing here is an entropy assessment; `H` remains a
  simulation-derived design estimate until [#12] measures it.
- **`sim/records/2026-08-01-ro-array-sanity-jitter-01.md` is not superseded.**
  Its numbers were never re-run; #46 measured a different testbench. Its `σ` is
  still unusable, for a reason that is now *narrower* than DR-0010 assumed —
  see Consequences.

### 4. What acceptance mechanically requires

Stated as a checklist so acceptance is not a research project:

1. `sim/tools/array_sizing.py`: `A_JITTER_ENERGY` 1.79 → **7.32**, and its
   `--check` derivation source moves from `sim/tools/jitter_energy_law.py`
   (plain cell) to `sim/tools/starved_cell_jitter_energy.py` (starved cell,
   asymptotic, entropy-binding corner). `A_TOLERANCE` may need widening to the
   spread of a three-corner fit.
2. `sim/tools/jitter_energy_law.py` is **not** edited. It derives the plain
   cell's constant and remains correct about it; it simply stops being the
   sizing input.
3. `DR-0010`'s `status` → `Superseded` and `superseded_by` → this record,
   changing nothing else in it (the immutability rule in
   `spec/decision-records/TEMPLATE.md`).
4. `README.md`'s `Raw rate` row and `design/README.md`'s quoted figures move to
   2 kbps, citing this record.
5. [#8] (conditioner `K`) and the README's time-to-first-valid row are
   re-derived at 2 kbps. DR-0010 already owed them a re-derivation at 500 bps;
   this changes the number they are re-derived at, not the obligation.

Until then the stated constant stays at 1.79 and `--a` prices the alternative
without moving anything published — which is how the table in §2 above was
produced.

## Alternatives considered

### Leave the rate row at 500 bps and record the measurement only

- **What**: accept #46's records as evidence, cite them, and change no row —
  500 bps simply carries more margin than DR-0010 thought.
- **Why plausible**: it is the zero-risk option, it never over-promises, and
  the measurement's absolute accuracy is limited (see below). A row that is
  conservative by 5× costs nothing technically.
- **Why rejected**: DR-0010 moved the ratified rate row down by ~2000× on the
  strength of `a = 1.79`, and explicitly filed #46 to check that number on the
  shipped cell, with a written commitment to move the row back up if it came
  back higher. Declining to move it now would make that commitment
  unfalsifiable and would leave a headline row derived from a cell the project
  does not build. The row is derived from `a`; `a` changed; the row moves.

### Use `a` = 24.84 (lag 1), the like-for-like figure

- **What**: quote the row at 9040 bps × (1/1.30) ≈ 7 kbps.
- **Why plausible**: it is the *same* estimator DR-0010's 1.79 uses, so the
  13.9× ratio is the cleanest apples-to-apples statement, and §2's argument
  about non-accumulating noise applies equally to the plain cell — meaning
  DR-0010's own 1.79 is inflated by the same effect, and using lag 1 on both
  sides is self-consistent.
- **Why rejected**: self-consistency is not the criterion; the criterion is
  what `Q_array(T_s)` actually equals at `T_s` ≈ 10⁶ periods, and there only the
  accumulating component contributes. That DR-0010's 1.79 has the same
  inflation is a reason to revisit *its* estimator, not a licence to carry the
  inflation into a headline row.

### Use `a` = 11.77 (asymptotic, three-corner mean)

- **What**: quote the row at 4282 bps × (1/1.30) ≈ 3.3 kbps.
- **Why plausible**: it is the natural summary statistic, and it is what
  `starved_cell_jitter_energy.py` prints as the headline.
- **Why rejected**: the 2.34× corner-to-corner spread on the asymptotic measure
  is not small, and the entropy-binding corner sits at its bottom. DR-0007 §2
  binds at a corner, not at a mean.

### Re-measure the shipped eleven-stage array directly instead

- **What**: skip the cell-level constant and run `sim/tb/ro-array-core-power/`'s
  DUT under transient noise with a long window.
- **Why plausible**: it would need no law at all — `Q_array` would be measured
  rather than derived, and it would settle the ring-to-ring independence
  question at the same time.
- **Why rejected**: not affordable, and DR-0010 §Method already says so. An
  eleven-stage ring at 7.1 ns needs ~7× more simulated time per period than the
  5-stage decks here, which already cost ~111 minutes of ngspice per seeded
  run; two rings plus a tree multiplies it again. It remains the right thing to
  do eventually and is named under Follow-up.

## Consequences

- **Positive**:
  - **DR-0010's largest stated open risk is closed.** `(★)` is confirmed *in
    form* on the shipped cell — `a` is as constant across corners for the
    starved cell (1.32×) as for the plain one (1.29×) — and quantified in
    value. A sizing law that had been fitted to a cell the project does not
    build is now measured on the one it does.
  - **The `√t` extrapolation is justified rather than assumed.** An
    accumulation exponent of 0.47–0.50 over the top decade of lag is the
    premise of DR-0007 §2, and it had never been checked on this cell.
  - **The rate row is 4× further from the inequality's edge**, so the margin
    that absorbs #12's and #13's eventual corrections is larger, not smaller.
  - **`--a` makes the next such move cheap.** Any future measurement of `a` can
    be priced against the shipped array from committed records without editing
    anything published.

- **Negative / accepted cost**:
  - **The absolute value carries the fixed-injection scaling error, and this is
    where it does *not* cancel.** Every `σ` in this repository is a
    fixed-injection figure scaled by a 1 GHz proxy for the device noise
    density, good to ~1.5–2× on `σ` and therefore ~2–4× on `a`. Across corners
    that error is largely common-mode; **between two different cells it is
    not**. A 13.9× (or 6.6×) ratio is outside that band but not by a large
    factor, and the row proposed here inherits the uncertainty. What does *not*
    depend on the scaling is that the two `.noise` testbenches
    (`sim/tb/inv-stage-noise/`, `sim/tb/rostage-noise/`) define
    `inoise_dens_1g` identically, and that `a`'s constancy is preserved.
  - **The constant is measured on a five-stage, unloaded ring, not the shipped
    eleven-stage loaded one.** `a` is stage-count-free by construction and
    DR-0010 §3 measures `E_cycle ∝ n` on this cell to within 1 %, but no
    five-to-eleven check of `a` itself exists, and this record does not pretend
    one does.
  - **Three corners, not twenty-seven.** DR-0010's 1.79 rests on a 27-point
    grid; this rests on three points chosen for what they bind (entropy, power,
    nominal). The 2.34× asymptotic spread across those three is handled by
    taking the binding corner's own value, not by averaging it away.
  - **Two ratified-row moves in one day, in opposite directions.** DR-0010
    moved the rate row down by ~2000× and this moves it back up by 4×. Both are
    derived from measurement rather than preference, and both are Proposed
    rather than ratified — but a reader is entitled to note the churn, and the
    honest summary is that the rate row has been an estimate the whole time and
    is now an estimate with a better-measured input.

- **Follow-up required**:
  - **The superseded array run's failure mode is now narrower than DR-0010
    diagnosed, and is not yet explained.** DR-0010 attributed
    `2026-08-01-ro-array-sanity-jitter-01`'s bad `σ` to its 16-period,
    opened-at-start-up window. #46 reproduces *that same window geometry inside
    its own runs* and gets a genuine (merely noisy) estimate — 16–24 % seed
    spread against a 15 % reference. So the window alone does not explain it,
    and the remaining difference is the device environment: four rings and an
    XOR tree in one deck, with `ro1` driving `xa1`. The leading hypothesis is
    deterministic ring-to-ring perturbation through the shared XOR input stage,
    which would be seed-independent and would accumulate faster than `√t`. That
    is a hypothesis, not a finding; it is **filed as its own issue** and it
    matters beyond bookkeeping, because ring-to-ring independence is [#16]'s
    subject and DR-0010 §Consequences already flags that at N = 2 the cost of
    getting it wrong is doubled.
  - **`a` on the shipped eleven-stage ring** — the stage-count check this
    record does not have.
  - **[#12] and [#13]** are unchanged in scope; both now evaluate against
    2 kbps rather than 500 bps.
  - **The acceptance checklist in §4** is the complete edit set.

- **Revisit if**: the eleven-stage check finds `a` materially different from the
  five-stage value; or the array's own long-window `σ` (once measured) is
  inconsistent with `(★)` at the constant proposed here; or #12/#13's flicker
  resolution changes `Q₁` by more than DR-0007's `M = 1.5` margin; or a direct,
  non-fixed-injection jitter measurement narrows the ~2–4× scaling uncertainty
  enough to move the value again.

[#8]: https://github.com/2AMLogic/gf180-trng/issues/8
[#12]: https://github.com/2AMLogic/gf180-trng/issues/12
[#16]: https://github.com/2AMLogic/gf180-trng/issues/16
[#46]: https://github.com/2AMLogic/gf180-trng/issues/46
