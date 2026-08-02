---
dr: DR-0014-entropy-binding-corner-moves-to-the-hot-slow-corner
title: Move the entropy-binding corner from ss/-40 C/3.63 V to ss/+125 C/3.63 V, measured over the full covered 27-point PVT grid
status: Proposed
date: 2026-08-02
deciders: Proposed by #13 (the measurement this record rests on). NOT ratified — acceptance is an operator decision, as DR-0001…DR-0004, DR-0007 and DR-0012 were.
supersedes: "DR-0012-sampler-fixed-external-clock — its stated minimum-`Q` CORNER only, and only on acceptance. Everything else in that record stands unchanged: the fixed external sample clock, the resulting `Q ∝ σ₁²/T₀³` corner metric, and every consequence drawn from the clock architecture itself."
superseded_by: n/a
related: "#13 (the measurement — this record's whole basis), #12 (measuring H, which must now be measured at this corner), #17 (post-layout re-run), #11 (health-test RTL); DR-0002 (RCT/APT cutoffs stated in H), DR-0004 (quality tiers), DR-0006 (the covered PVT grid), DR-0007 §2/§4 (the sizing inequality and the corner-metric fork), DR-0010/DR-0011 (raw rate), DR-0012-sampler-fixed-external-clock (the record this supersedes, its corner only); sim/characterization-worst-corner-and-mc-mismatch.md; sim/records/2026-08-02-ro-array-core-pvt-q-{01..27}.md"
---

# DR-0014: Move the entropy-binding corner from `ss`/−40 °C/3.63 V to `ss`/+125 °C/3.63 V

## Status

- 2026-08-02: Proposed, by #13. Not ratified.

## Context

[`DR-0012-sampler-fixed-external-clock`](DR-0012-sampler-fixed-external-clock.md)
(note: this repository has two files prefixed `DR-0012-`, a recorded
renumbering collision explained in that file's own Status section — this
record means the *sampler clock* one) settled
[DR-0007](DR-0007-multi-ro-xor-combined-entropy-source.md) §4's corner-metric
fork. Because the sampler clock is external and fixed, jitter accumulates
over a fixed wall-clock sample interval rather than over a fixed number of
ring periods, so the entropy-binding figure of merit is

```
Q_array(T_s)  =  Σ_i κ_i² · T_s / T0_i²        (DR-0007 §2)
```

i.e. `Q ∝ σ₁²/T₀³` per ring. DR-0012's §Consequences then states a corner:

> DR-0007 §4's corner-metric fork is resolved: `Q ∝ σ₁²/T₀³`, minimum at
> `ss`/−40 °C/3.63 V. #13 is unblocked on this specific question.

**That corner was inferred from three measured PVT points**, which were all
this repository had when DR-0012 was written: `tt`/27 °C/3.30 V,
`ff`/−40 °C/3.63 V and `ss`/−40 °C/3.63 V
(`sim/records/2026-08-01-ro-array-core-power-{01..06}.md`). No hot point at
high supply had ever been measured on the shipped array. DR-0012 knew this
and wrote its own trigger:

> **Revisit if**: … #13's measurement finds the `ss`/−40 °C/3.63 V corner is
> not in fact the metric's minimum over the full covered grid.

#13 has now made that measurement. `sim/tb/ro-array-core-pvt-q/` measures the
shipped two-ring array's per-ring period and supply current at every point of
the covered grid — `{tt, ff, ss}` × `{−40, 27, 125} °C` × `{2.97, 3.30,
3.63} V`, 27 records,
`sim/records/2026-08-02-ro-array-core-pvt-q-{01..27}.md` (`fs`/`sf` remain out
of scope per [DR-0006](DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md)).
It is the same DUT, the same rails and the same measurement expressions as
`sim/tb/ro-array-core-power/`, with a longer transient window because the
slow half of the grid does not fit in that testbench's 50 ns one; the two
families agree to **3.4 × 10⁻⁵** on every `Q`-relevant quantity at the three
PVT points they share (`python3 sim/tools/worst_corner_entropy.py`).

Over that grid the minimum of `Q` is **not** at `ss`/−40 °C/3.63 V. It is at
`ss`/+125 °C/3.63 V, by 8.1 %:

| corner | `T₀` (ring 1) | `P_rings` | `T` | `Q_array` @ 500 bps | margin over `M·Q_H0` | `R_max` |
|---|---|---|---|---|---|---|
| **`ss`/+125 °C/3.63 V** (measured minimum) | 10.214 ns | 111.9 µW | 398.15 K | **7.185×10⁻³** | **1.20×** | **598.8 bps** |
| `ss`/−40 °C/3.63 V (DR-0012's prediction) | 6.154 ns | 165.5 µW | 233.15 K | 7.816×10⁻³ | 1.30× | 651.3 bps |
| `ss`/+125 °C/2.97 V (slowest ring on the grid) | 13.151 ns | 54.7 µW | 398.15 K | 8.902×10⁻³ | 1.48× | 741.9 bps |
| `ff`/−40 °C/3.63 V (fastest ring; maximum power) | 4.286 ns | 269.5 µW | 233.15 K | 9.845×10⁻³ | 1.64× | 820.4 bps |

(at DR-0010's `a = 1.79`; the full 27-row table at all three measured
jitter-energy constants is in
[`sim/characterization-worst-corner-and-mc-mismatch.md`](../../sim/characterization-worst-corner-and-mc-mismatch.md).)

**The metric did not change and nothing was re-fitted.** What changed is that
the grid now contains the hot end. The mechanism is visible in the table:
`Q ∝ T/(P·T₀²)`, and warming `ss`/3.63 V from −40 °C to +125 °C lengthens
`T₀` by 66 % (6.154 → 10.214 ns). The resulting `1/T₀²` factor of 0.36
outweighs the two effects that push the other way — 1.71× more `kT` and 0.68×
the ring power — for a net 8 % *reduction* in `Q`. The intuition in #13's own
title (fast/cold/high-supply is the dangerous corner) is the right intuition
for a *self-divided* sample clock, where a faster ring means fewer accumulated
periods per bit. Under DR-0012's fixed external clock it is the wrong one:
`σ_acc(T_s)` does not care how fast the ring runs, but the phase-per-period it
buys you does, and a slow ring converts the same absolute jitter into less
per-sample uncertainty.

Because `a` multiplies every corner's `Q` by the same factor, the ranking is
identical at DR-0010's plain-cell `a = 1.79` and at both starved-cell
constants #52 measured (`a = 11.77` asymptotic, `a = 24.84` lag-1). Only the
margin moves: 1.20× at `a = 1.79`, 7.87× at `a = 11.77`, 16.62× at
`a = 24.84`.

## Decision

We will state the entropy source's **entropy-binding corner as `ss` / +125 °C
/ 3.63 V**, and read every claim that is qualified "at the entropy-binding
corner" at that point rather than at `ss`/−40 °C/3.63 V.

Concretely:

1. `README.md`'s **Raw min-entropy per bit** row names `ss` / +125 °C /
   3.63 V as the corner its (still unmeasured) `H` is to be stated at.
2. **#12 measures `H` at this corner.** That is the substantive obligation
   this record creates: the Tier 2 headline figure DR-0004 allows must be
   reported at `ss`/+125 °C/3.63 V, not at the corner DR-0012 named.
3. [DR-0002](DR-0002-health-test-parameters-and-failure-behavior.md)'s RCT/APT
   cutoffs are formulas in `H`, so **no cutoff number changes today** — the
   cutoff table is evaluated at whatever `H` #12 eventually measures, and the
   only thing this record moves is *where* that `H` is measured.
4. `sim/tools/worst_corner_entropy.py` states this corner as a constant and
   `--check` (wired into `npm run check:spec`) fails if the committed grid
   stops supporting it. `sim/tools/array_sizing.py` now reads the full grid
   rather than the three-point family, so its own "minimum-Q corner" line and
   its `--check` gate cannot drift from this record.
5. Nothing about DR-0012's actual decision — the fixed external clock — or
   about the `Q ∝ σ₁²/T₀³` metric it fixed, changes. This record supersedes
   one sentence of that record's §Consequences.

**DR-0007 §2's sizing inequality still holds at the new corner**, at every
constant: `Q_array(500 bps) = 7.185×10⁻³ ≥ M·Q_H0 = 6.0×10⁻³`, a 1.20×
margin. `R_max` at the new corner is 598.8 bps at `a = 1.79` (so DR-0010's
proposed 500 bps row survives) and 3937 bps at the starved cell's asymptotic
`a = 11.77` (so [DR-0011](DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md)'s
proposed 2 kbps row survives too). **This record therefore reports a moved
corner, not a failed spec** — but the margin at `a = 1.79` is 1.20× rather
than the 1.30× the previously-named corner implied, and that is the honest
number to plan against.

## Alternatives considered

### Keep `ss`/−40 °C/3.63 V as the stated corner

- **What**: Treat DR-0012's corner as ratified and the new grid as
  supplementary detail.
- **Why plausible**: The two corners differ by only 8 % in `Q`; the
  inequality holds at both; nothing downstream has consumed a number from
  either yet, because `H` is still unmeasured. Leaving the statement alone
  would cost nothing today.
- **Why rejected**: It would leave the repository asserting a minimum that
  its own committed records contradict, and the assertion is load-bearing:
  #12's whole job is to report `H` *at the binding corner*, and #17 re-runs
  the analysis post-layout at the same corner. A corner that is wrong by 8 %
  in `Q` today becomes a headline min-entropy figure quoted at the wrong
  operating point later. DR-0012 anticipated exactly this and asked for a
  superseding record rather than silence.

### Re-cut the grid so the prediction holds

- **What**: Restrict the "covered grid" to the three points DR-0012 was
  written against, or exclude +125 °C on the grounds that DR-0003's
  raw-rate row already binds at a hot corner.
- **Why plausible**: It would keep every document consistent with no edits at
  all, and the hot corner is arguably already "covered" by the rate row.
- **Why rejected**: `CLAUDE.md` is explicit — *agents do not relax the
  ratified spec to make results pass*, and narrowing the grid until the
  measurement agrees with the prediction is that, in its purest form. It is
  also wrong on the merits: the rate row binds at the *slowest ring*
  (`ss`/125 °C/2.97 V), which this grid shows is **not** the minimum-`Q`
  corner (8.902×10⁻³ vs 7.185×10⁻³). Rate-binding and entropy-binding are
  different corners on the same grid, and conflating them is exactly the
  error this measurement exists to prevent.

### State a "binding corner family" rather than a point

- **What**: Say the entropy-binding corner is `ss`/3.63 V, at either
  temperature extreme, since the two differ by 8 %.
- **Why plausible**: It is honest about the flatness of the minimum along the
  temperature axis and would not need revising if a future measurement
  reordered two nearly-tied points.
- **Why rejected**: A minimum-`Q` corner is the point where a claim has to
  hold; a family is not a point, and downstream records (DR-0002's cutoffs,
  DR-0004's Tier 2 figure) need somewhere specific to state a number. The
  flatness is worth recording — it is, in the Consequences below — but as a
  caveat on the margin, not as a refusal to name the corner.

## Consequences

- **Positive**:
  - The corner every future entropy claim is stated at is now measured over
    the whole covered grid rather than inferred from three points, and the
    grid that measured it is committed evidence a reader can re-run
    (`python3 sim/tools/worst_corner_entropy.py --full`).
  - The rate-binding corner (`ss`/125 °C/2.97 V, slowest ring, per DR-0003)
    and the entropy-binding corner (`ss`/125 °C/3.63 V) are now known to be
    *different points*, with numbers behind the difference.
  - The maximum-power corner is unchanged and independently confirmed by the
    same grid: `ff`/−40 °C/3.63 V, 415.3 µW.
  - `npm run check:spec` now holds this corner statement to the records, so
    it cannot silently drift.

- **Negative / accepted cost**:
  - The margin against DR-0007 §2 at DR-0010's stated `a = 1.79` is 1.20×,
    down from the 1.30× the previously-named corner implied. Under the
    starved-cell constants the array actually ships (#52) it is 7.87×–16.62×,
    so this is not a live risk to the design — but the plain-cell number is
    the one DR-0010's published arithmetic is quoted against, and it moved.
  - **The minimum is flat along temperature**: 7.185×10⁻³ at +125 °C against
    7.816×10⁻³ at −40 °C, an 8 % separation on a metric whose own constant
    `a` is only known to ±8 % (DR-0010) and whose starved-cell value scatters
    ~1.3× across corners (#52). The *ordering* of these two points is
    therefore not robust to a better-measured `a` that turns out to be
    corner-dependent; the claim "the minimum is on the `ss`/3.63 V edge" is
    much more robust than the claim "it is at the hot end of that edge".
  - **`κ²` at this corner is law-derived, not directly measured.**
    `sim/tb/ro-ring5-starved-jitter-long/` — the only transient-noise
    measurement of the shipped cell's jitter — was run at three corners, none
    of which is `ss`/125 °C/3.63 V. Every `Q` in the table above comes from
    the DR-0010 `(★)` jitter-energy law applied to a measured period and
    supply current, which is exactly how DR-0007 §2 intends `Q` to be
    evaluated, but it means the new binding corner has no direct `σ_acc`
    behind it.

- **Follow-up required**:
  - **#12** measures `H` at `ss`/+125 °C/3.63 V.
  - A transient-noise `sim/tb/ro-ring5-starved-jitter-long/` run at
    `ss`/+125 °C/3.63 V, so the binding corner has a directly measured `κ²`
    rather than a law-derived one. Worth filing as its own issue; it is the
    single measurement that would most strengthen this record.
  - **#17**'s post-layout re-run uses this corner.
  - DR-0006's "Follow-up required" clause (add `fs`/`sf` if a
    duty-cycle-sensitive downstream circuit appears) is now more pointed: an
    edge-triggered sampler *has* been added (#9), so a later issue should
    price `fs`/`sf` on this same grid and say whether they move the minimum
    again.

- **Revisit if**: `fs`/`sf` are added to the covered grid and either lands
  below `ss`/+125 °C/3.63 V; a directly measured `κ²` at the hot corner
  disagrees with the law-derived one used here; or a corner-dependent `a`
  is established, which would break the "`a` cannot change the ranking"
  argument this record leans on.
