---
dr: DR-0033-mismatch-monte-carlo-limits-on-ring-period-and-sampler-threshold
title: Ratify numeric limits on the sampled ring period and sampler threshold, so the mismatch Monte Carlo campaign can be graded
status: Accepted
date: 2026-11-09
deciders: Operator ruling, round 20261107-r9 q26 (2026-11-09), option (a), recorded on issue #656. Written by the Builder of #656 from that ruling.
supersedes: n/a
superseded_by: n/a
related: "#656 (origin; operator ruling); #771 (install route); sim/characterization-worst-corner-and-mc-mismatch.md §3, §4; DR-0002 (health-test cutoffs); DR-0007 §2 (sizing law); DR-0008 (conditioner break-even); DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy (rate and constant); sim/tools/array_sizing.py"
---

# DR-0033: Numeric limits on the sampled ring period and sampler threshold

## Status

- 2026-11-09: **Accepted.** The operator ruled on #656 (option (a)): ratify
  limits for `period_r1` and `dtrip_v` derived from the campaign's own
  consequence check, add them through a decision record, then run `klt yield`
  over the existing campaign. These are **new** limits on two quantities the
  spec table did not bound. No existing row, target or stretch is changed.

## Context

Item 6 of the T1 checklist ("statistical claims carry Monte Carlo evidence")
accepts only a `klt yield` report, and `klt yield` grades samples against a
limit; it refuses a measurement that has none. The mismatch campaign in
`sim/characterization-worst-corner-and-mc-mismatch.md` §3 samples two
quantities, each at `tt` / 27 °C / 3.30 V and `ss` / +125 °C / 3.63 V:

- `period_r1`, ring 1's oscillation period (`ro-array-core-mc-freq`, 8 seeds
  per corner);
- `dtrip_v`, the sampler master latch's switching threshold
  (`sampler-dff-mc-offset`, 30 seeds per corner).

The ratified spec table bounded neither. §4 of the same document asks the
question a limit should answer ("do the conditioner and health-test margins
cover the observed spread?") but answers it as a headroom table rather than as
a limit on the sampled value. This record turns each margin into a bound on
the quantity that was sampled, and nothing else.

## Decision

We will add two rows to the ratified spec table. Both are stated **per PVT
point at which the campaign sampled**, because the quantities are absolute
(volts, seconds) and move with the corner.

**`period_r1` (upper bound only).**

| Corner | `T0_r1` mismatch-free (s) | `Q_array` at 2 kbps | `period_r1` limit |
|---|---|---|---|
| `tt` / 27 °C / 3.30 V | 6.6776 ns | 1.127×10⁻² | **≤ 9.151 ns** |
| `ss` / +125 °C / 3.63 V | 9.5812 ns | 8.319×10⁻³ | **≤ 11.28 ns** |

Derivation. [DR-0007] §2 requires `Q_array ≥ M·Q_H0 = 1.5 × 4.0×10⁻³ = 6×10⁻³`
at the ratified 2 kbps raw rate with the stated `a = 7.32`
([DR-0011-rate]). At fixed ring power `Q ∝ 1/T0²` (the same relation
§3.1 uses). If every ring's period lengthens by a factor `s`, `Q` falls by
`s²`, so the sizing law holds while `s ≤ √(Q_array / 6×10⁻³)`:
`√(1.127×10⁻² / 6×10⁻³) = 1.370` at `tt` / 27 °C / 3.30 V and
`√(8.319×10⁻³ / 6×10⁻³) = 1.178` at `ss` / +125 °C / 3.63 V. Multiplying the
mismatch-free ring-1 period by that factor, and rounding **down** to four
significant figures, gives the limits above. `T0_r1` and `Q_array` are the
`array_sizing.py` values; the `T0_r1` figures equal the `sw_stat_mismatch=0`
control runs' period exactly. Scaling the whole array together is the stricter
reading (lengthening ring 1 alone costs less `Q`), so the bound is
conservative. There is **no lower bound**: a shorter period raises `Q`, so
the sizing law gives no need for one. The ring-frequency-ratio distance from
an integer (§3.1) is a separate concern, has no ratified numeric floor, and is
not turned into a limit here.

**`dtrip_v` (supply-rail window).**

| Corner | `dtrip_v` limit |
|---|---|
| `tt` / 27 °C / 3.30 V | **0 V < `dtrip_v` < 3.30 V** |
| `ss` / +125 °C / 3.63 V | **0 V < `dtrip_v` < 3.63 V** |

Derivation. §4's model gives the raw-bit majority probability
`p = Φ(dt/σ_acc)` for a threshold offset displacing the crossing by
`dt = offset/slew`. Take the entropy-binding corner's measured slew
(1.380×10¹⁰ V/s) and `σ_acc` (1.538 ns). The offset at which each downstream
requirement is first violated is:

| Requirement | `p_major` at the violation | Offset at the violation |
|---|---|---|
| [DR-0002] APT, `C_APT` = 824, `Pr(X ≥ 824) ≤ 9.095×10⁻¹³` | 0.7078 | 11.6 V |
| [DR-0002] RCT, `C_RCT` = 81, `Pr(81 identical) ≤ 9.095×10⁻¹³` | 0.7101 | 11.8 V |
| [DR-0008] conditioner break-even `H ≥ 0.106456` | 0.9289 | 31.1 V |

(Solved numerically from the formulas quoted in §4; `H` is the bias-only
ceiling, as in §4.) The binding requirement is the APT, at **±11.6 V** of
threshold offset from mid-supply. That is more than three times the supply, so
the derived window is wider than the rails, and the rails are the operative
bound: a threshold outside `(0, VDD)` is not a threshold. The limit is
therefore `0 < dtrip_v < VDD`, with the upper bound taken at the corner's own
supply.

**This limit is not tight, and that is the finding, not a defect of the
record.** The consequence check says the conditioner and health tests tolerate
far more threshold offset than the cell can physically produce, so the
sampler's measured −265 / −275 mV systematic offset and 15 mV mismatch spread
are nowhere near binding. We state the limit this way instead of narrowing it,
because a narrower figure would not trace to a design need and agents do not
invent spec limits. A tighter, design-motivated bound (a bias budget on the raw
stream, for example) would be a separate decision.

**No target yield is ratified.** The limits above are bounds on a sampled value.
This record does not ratify a `target_yield`, so the `klt yield` report states
the empirical yield, its confidence interval, Cpk and the sample-size verdict,
and does not itself pass or fail on a yield target.

Where the limits live: two rows in the README target-specification table
(`period_r1` mismatch bound; `dtrip_v` mismatch bound), and
`signoff/evidence/mc-yield/limits.json`, which is what `klt yield` reads.

## Alternatives considered

### Wider, placeholder-style limits

- **What**: Pick round numbers wide enough that the campaign grades `met`.
- **Why plausible**: Fastest way to a `6.analog` citation.
- **Why rejected**: Not traceable to a design need, and a loose limit grades
  `met` without meaning anything. The operator ruled for derived limits.

### Leave item 6 unmet and record why

- **What**: No spec change; keep the campaign uncited.
- **Why plausible**: No risk of a weak limit.
- **Why rejected**: The operator ruled for (a); the T1 gap would stay open
  although the campaign exists.

### Narrow the `dtrip_v` window to a design bias budget

- **What**: Bound `|offset|` by a bias target on the raw stream.
- **Why plausible**: Would give a limit that can actually bind.
- **Why rejected here**: No ratified bias target exists, and choosing one is a
  design decision this ruling did not make. Flagged as the follow-up below.

## Consequences

- **Positive**: Both sampled quantities have a stated limit with a written
  derivation, so a `klt yield` report over the existing campaign can be
  produced and cited as `6.analog`.
- **Negative / accepted cost**: The `dtrip_v` limit is the supply rails, so a
  `met` on it says the cell has a working threshold, not that its bias is small.
  The campaign (8 and 30 seeds) is far below `klt yield`'s default sample-size
  target, and no negative control in `klt yield`'s sense (a seeded known-bad
  variant that must degrade yield) exists; the campaign's own control only
  shows the spread collapsing with mismatch off. Item 6 can therefore grade
  `unmet` / `undersized_sample`, and that outcome is recorded as it comes.
- **Follow-up required**: A decision on a bias budget for the sampler
  threshold if a binding `dtrip_v` limit is wanted; more seeds if a sized
  sample is wanted (a `klt sim` request with `monte_carlo`, which goes to the
  batch fleet). Neither is part of this record.
- **Revisit if**: the sizing law's `Q_H0`, `M`, raw rate or `a` constant
  moves (the `period_r1` limits move with them), a bias target is ratified, or
  the campaign is re-run at more seeds or more corners.

[DR-0002]: DR-0002-health-test-parameters-and-failure-behavior.md
[DR-0007]: DR-0007-multi-ro-xor-combined-entropy-source.md
[DR-0008]: DR-0008-crc32-lfsr-non-vetted-conditioner.md
[DR-0011-rate]: DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md
