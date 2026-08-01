# Raw min-entropy estimation and statistical test battery (issue #12)

Status: analysis complete for issue #12, applying the #10/[DR-0012] methodology
contract to the real design. **No non-trivial raw min-entropy figure is
reported as a design estimate.** Sections 1–3 below explain, quantitatively
and from evidence already committed under `sim/records/`, why that is the
correct outcome under this repository's evidence rules rather than a gap in
the analysis.

**This document is an ordinary summary, not evidence.** Every measured
number below cites the `sim/records/` stem or `sim/tools/` derivation that
produced it — treat this document as a reading guide over that evidence, not
a substitute for it. This is the same convention
[`sim/characterization-supply-current-and-leakage.md`](characterization-supply-current-and-leakage.md)
uses.

**Label (mandatory, [DR-0004]):** every number in this document that comes
from simulation is a *simulation-derived design estimate; not an SP 800-90B
entropy assessment.*

## What is and is not covered

Covered: the two things issue #12 was scoped to do —

1. a min-entropy point estimate on the one transistor-derived raw bitstream
   this repository has (`sim/tb/sampler-array-digitize`, issue #9), with the
   confidence-degradation discussion [DR-0012] §2 requires, plus a physical
   cross-check against the design's own jitter-energy sizing law
   ([DR-0007] §2, [DR-0010]);
2. a statistical test battery on the CRC-32-conditioned output, at the one
   scale this repository can actually run one at.

Not covered: a measurement of the design's real min-entropy at any rate the
design might ship at. Section 1 is the quantitative reason no simulation
this repository can afford reaches that regime — not a missing testbench,
a cost ceiling.

## 1. Transistor-level: the MCV estimator on the real bitstream

### Method

`sim/tools/raw_min_entropy_estimate.py` (new) reads the two committed
`sampler-array-digitize` records —
[`2026-08-01-sampler-array-digitize-01`](records/2026-08-01-sampler-array-digitize-01.md)
(`tt`/27 °C/3.30 V, 3 seeds) and
[`…-02`](records/2026-08-01-sampler-array-digitize-02.md)
(`ss`/−40 °C/3.63 V, DR-0010's entropy-binding corner, 3 seeds) — and applies
the most-common-value point estimator
`H_hat = -log2(max(p1_hat, 1 - p1_hat))`, the same estimator
`sim/tools/jitter_estimator_calibration_check.py` validated against a
closed-form target (issue #10, closed via #50) to within 0.02 bit. Nothing
here re-derives or re-validates the estimator; it is applied, unmodified, to
real bits instead of the calibration testbench's idealized Gaussian source.

**Why 3 seeds, not [DR-0012] §1's 4-seed default.** This analysis does not
mine a fourth seed. §1 permits a stated reduction from the default, and the
reason here is direct rather than a cost excuse: the three already-run seeds
produce **bit-identical output** at both corners (see the "Effective
independence" discussion below) — every per-bit seed-to-seed spread is at
or below the sampler's own settled-rail precision (worst case 5.1 µV on a
3.63 V rail). A fourth independent noise draw, run at the same operating
point, has no mechanism to produce a qualitatively different outcome from
what three already show, and this record's own §3 explains *why* physically.
Re-running a fourth seed would spend real simulation cost (each run took
13.6–19.3 minutes of ngspice time, see the cited records' `wall_time`
fields) to confirm a conclusion this analysis already reaches by a different,
stronger route.

### Result

| Corner | N (bits) | seeds | ones | `p1_hat` | `H_hat` (bit) | SE(`p1_hat`), naive N=10 | SE(`H_hat`), naive |
|---|---|---|---|---|---|---|---|
| `tt`/27 °C/3.30 V | 10 | 3 | 6 | 0.600 | 0.7370 | 0.1549 | 0.3725 |
| `ss`/−40 °C/3.63 V (entropy-binding) | 10 | 3 | 7 | 0.700 | 0.5146 | 0.1449 | 0.2987 |

The "naive" standard errors are [DR-0012] §2's own stated formula
(binomial SE on `p1_hat`, propagated through the estimator's local
sensitivity `1/(p_max ln 2)`), applied honestly at the achieved N = 10. They
are already large — order 0.3–0.4 bit on an `H_hat` of order 0.5–0.7 bit —
which alone would be reason for caution. The next paragraph is why even
these numbers overstate the confidence that exists.

### Effective independence: why N = 10 (or N = 30 across 3 seeds) is not real

Each record's ten bits are **successive** samples of one evolving ring-phase
process (`ring_periods_per_sample` ≈ 1.4–1.6 in both records — each sample
is barely more than one ring period after the last), not ten independent
draws, so treating them as i.i.d. Bernoulli trials — which is what the SE
formula above assumes — is already generous. What makes it worse is
directly measured, not inferred: **the bit pattern is identical across all
three independent noise seeds run at each corner.** `design/README.md`
already reports this (`0101111100` at `tt`, `1111010011` at `ss`, at every
seed), and `raw_min_entropy_estimate.py` confirms it from the records'
seed-to-seed spread fields directly — worst-case spread 3.4e-8 V (`tt`) and
5.1e-6 V (`ss`), both far below the sampler's rail-settled precision. An
additional independent realization of the injected noise process changed
**none** of the ten output bits, at either corner.

That is strong direct evidence that the true number of independent random
realizations behind each row above is much closer to **1** — one noise
process, observed not to move the outcome — than to the 10 (or 30) samples
the naive SE formula assumes. No confidence interval beyond "we observed one
realization, and it looks like this" is defensible at this N. Section 3
explains, quantitatively rather than by appeal to the seed count alone, why
this is exactly the expected outcome and not a simulation anomaly.

### Physical cross-check: is this the rate that entropy lives at, or not?

[`DR-0007`](spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)
§2 sizes the shipped array against `Q_array(T_s) = kappa^2 * T_s / T0^2`,
summed over rings, and states the array needs `Q_array >= M * Q_H0 =
1.5 * 4.0e-3 = 6.0e-3` for `H = 0.5` to be a supportable design point.
`sim/tools/array_sizing.py` already evaluates this from committed
`ro-array-core-power` records; `raw_min_entropy_estimate.py` calls it
directly, at `sampler-array-digitize`'s own sample interval
(`T_s = tclk = 10 ns`, read from `sim/tb/sampler-array-digitize/tb.json`
rather than assumed), using **both** DR-0010's stated plain-cell constant
(`a = 1.79`) **and** issue #46's measured constant for the shipped
**starved** cell (`a = 11.77`, the asymptotic-slope figure
`sim/tools/starved_cell_jitter_energy.py` derives — ~6.6× more favorable to
entropy than the plain-cell value DR-0010 states, so this is the more
generous of the two available constants, not a worst case):

| Corner | `Q_array` (`a` = 1.79, plain) | `Q_array` (`a` = 11.77, #46 starved) | required `M·Q_H0` | shortfall (starved) |
|---|---|---|---|---|
| `tt`/27 °C/3.30 V | 4.86e-08 | 3.19e-07 | 6.0e-3 | **18,783×** |
| `ss`/−40 °C/3.63 V | 3.91e-08 | 2.57e-07 | 6.0e-3 | **23,352×** |

Even using the more favorable, physically-measured constant, `Q_array` at
this testbench's necessarily-fast 10 ns sample interval is four to five
orders of magnitude below what DR-0007's own sizing law considers
sufficient for `H = 0.5`. **This is the physical reason the bits are
identical across every seed run so far**: at `T_s = 10` ns the array has
accumulated only ~1.4–1.6 ring periods of phase noise, nowhere near enough
for that noise to plausibly flip which side of the sampler's threshold a
sample lands on. The seed-invariance in Section 1 is not a simulation
artifact to work around; it is exactly what `(★)` (DR-0010 §"The measurement
that makes the choice one-dimensional") predicts at this `T_s`.

This generalizes, and the news does not improve at the rates the design
might actually ship at:

| Target rate | `T_s` | `Q_array` (`ss`, `a` = 11.77 starved) | vs. required 6.0e-3 |
|---|---|---|---|
| `sampler-array-digitize`'s testbench rate | 10 ns (100 MHz) | 2.57e-07 | 23,352× short |
| DR-0003's **ratified** raw rate, > 1 Mbps | 1 µs | 2.57e-05 | 233× short |
| DR-0010's **proposed** raw rate, > 500 bps | 2 ms | 5.14e-02 | **8.6× margin** (meets it) |

Only at DR-0010's proposed 500 bps — a rate not yet ratified — does the
array's own sizing law predict enough accumulated phase noise for `H = 0.5`
to be plausible. DR-0003's still-ratified 1 Mbps figure does not reach it
even with the more favorable starved-cell constant, independently
corroborating DR-0010's own argument for why that row had to move. This
document does not resolve that ratification question; it reports what the
array-sizing law says at each rate, from evidence already committed.

### Why the entropy-supporting rate cannot be simulated directly either

Simulating `sampler-array-digitize`'s own ten raw bits at `T_s = 2` ms
(500 bps) instead of 10 ns means 200,000× more simulated time at the same
10 ps noise-breakpoint resolution the testbench already needs for numerical
accuracy. The two committed records' own `wall_time` fields put one run at
13.6–19.3 minutes of ngspice time for 132 ns simulated (already described in
those records as inflated by concurrent-job contention, so read as an
order of magnitude, not a benchmark) — extrapolating linearly puts a single
run of the *same ten bits* at `T_s = 2` ms at **roughly 4–8 years** of
ngspice time. That is the same order of magnitude as
[`DR-0009`](spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md)'s
independently-derived cost table (~1.9 days for one 256-bit conditioner
block at the *ratified* 1 Mbps rate; DR-0004 Tier 2's 10⁶-sample dataset at
~20 years), arrived at here from a different starting record family. There
is no simulated rate at which this repository can both (a) afford the run
and (b) accumulate enough phase noise per bit for a non-trivial min-entropy
estimate. That is not a gap in this issue's testbench coverage; it is a
structural consequence of `(★)` plus this repository's measured per-run
simulation cost, and [DR-0004] Tier 2 anticipated exactly this outcome
("report the largest achievable N together with what that N does and does
not support").

### What Section 1 does and does not establish

- **Does**: apply the calibrated MCV estimator, honestly, to the only
  transistor-derived raw bits this repository has, at both corners they
  exist for, with the confidence-degradation figure [DR-0012] §2 requires.
  Explains, quantitatively rather than by assertion, why those bits are
  seed-invariant and why that is expected rather than anomalous.
- **Does not**: support the `H_hat` figures in the Result table as a
  design-stage min-entropy estimate for the shipped array at any rate under
  consideration. They are the estimator's output on ten seed-invariant
  samples at a rate ~4–5 orders of magnitude below the array's own
  entropy-sufficiency threshold; reporting either number as *the* raw
  min-entropy would be exactly the "review-blocking defect" [DR-0004]/
  [DR-0012] name — quoting an estimator at an unsupported N (or, here, an
  unsupported physical regime) as if it were the real answer.
- **Does not** attempt the SP 800-90B non-IID suite or the restart dataset,
  per [DR-0012] §2's explicit exclusion.

## 2. Statistical battery on the conditioned stream

### Method

`sim/tools/statistical_battery.py` (new) implements four SP 800-22-style
tests — monobit (frequency), block frequency, runs, and longest run of ones
— each gated on its own NIST-tabulated minimum sample count, with the
regularized incomplete gamma function implemented from scratch (no SciPy
dependency, matching this repository's stdlib-only convention) and
cross-validated against the closed-form identity `Q(1/2, x) = erfc(sqrt(x))`
(`--check`; also `sim/tests/test_statistical_battery.py`).

**This is explicitly not the SP 800-90B non-IID entropy-source suite
[DR-0012] §2 forbids running at an unsupported N.** SP 800-22 is a different
standard aimed at a different, much cheaper question — does a stream that is
*supposed* to already look uniform (post-conditioning) show a classical
statistical defect — with a sample-size floor (hundreds to low thousands of
bits) this repository can actually reach, unlike the non-IID suite's
10⁶-sample-per-estimator regime.

Because [`sim/tb/sampler-array-digitize`]'s ten raw bits per seed are
1/3277 of what one battery run needs (and 1/25.6 of a single 256-bit
conditioner block), the input is the declared-synthetic source
[`sim/tb/conditioner-crc32/source_model.py`](tb/conditioner-crc32/source_model.py)
already uses, at the design's own `H0 = 0.5` target, per [DR-0009] rule 4
("a behavioural run driven by a synthetic source is evidence about the
block, never about the source"). See
[`sim/tb/conditioned-stream-battery/`](tb/conditioned-stream-battery/) (new)
for the testbench and
[`2026-08-01-conditioned-stream-battery-01`](records/2026-08-01-conditioned-stream-battery-01.md)
for the evidence record.

### Result

32768 declared-synthetic raw bits (`H0 = 0.5`) → 128 CRC-32-conditioned
words → 4096 conditioned bits, tested at `alpha = 0.01`:

| Test | n | statistic | p-value | Result |
|---|---|---|---|---|
| monobit (frequency) | 4096 | 0.2500 | 0.802587 | PASS |
| block frequency (M=128) | 4096 | 20.6250 | 0.939546 | PASS |
| runs | 4096 | 2068.0000 | 0.531324 | PASS |
| longest run of ones (M=8) | 4096 | 0.6882 | 0.875973 | PASS |

All four tests pass, at the one scale (behavioral, synthetic-source) a
battery run is achievable in this repository today.

### What Section 2 does and does not establish

- **Does**: show the conditioner's own whitening does not trip four classical
  statistical detectors at the design's own `H0 = 0.5` operating point, at a
  sample count each test's NIST table supports.
- **Does not**: say anything about the physical entropy source. As
  `sim/tb/conditioner-crc32/README.md`'s own `h003` scenario already
  demonstrates, a raw stream with ~0.03 bit/sample of *measured* min-entropy
  still yields a conditioned stream that looks statistically clean — a
  linear conditioner spreads even a very weak input across its whole output
  space. A PASS here is a pipeline sanity check, not entropy evidence.
- **Sim-length limits which passes are meaningful.** All four tests ran at
  N comfortably inside their NIST-tabulated minimum ranges (see
  `sim/tools/statistical_battery.py`'s module docstring for the exact
  bounds); the `longest run of ones` test specifically is implemented for
  only the smallest tabulated regime (128 ≤ n < 6272) and is *omitted*,
  not misapplied, outside it.

## 3. Comparison against the draft targets

| Row | Draft target | What #12 found |
|---|---|---|
| Raw min-entropy per bit ([DR-0007], [DR-0002]) | `H0 = 0.5` bit/sample, entropy-binding corner | **Not measurable by transistor-level simulation at any rate under consideration** — Section 1. The array's own sizing law predicts `H0 = 0.5` is plausible only at DR-0010's proposed (not yet ratified) 500 bps; DR-0003's still-ratified 1 Mbps falls ~233× short even with the more favorable measured jitter-energy constant, and simulating *any* bitstream at 500 bps costs years of ngspice per run. |
| Quality ([DR-0004]) | designed-for-90B (Tier 1) + a simulation-derived design-stage min-entropy estimate (Tier 2) | Tier 1 (structural) is unaffected by this issue. Tier 2's target — a supportable non-trivial point estimate — **is not delivered by this issue**, for the reason above, and is not recorded as one; see [DR-0004] Tier 2's own "report the largest achievable N together with what that N does and does not support," which is exactly Section 1's shape. |
| Statistical test battery on conditioned output | (issue #12's own acceptance criterion) | Delivered, at behavioral/synthetic-source scale — Section 2. Four SP 800-22-style tests pass on the design's own `H0 = 0.5` operating point; explicitly not evidence about the physical source. |

## No spec row is edited by this issue

Per `CLAUDE.md` and this repository's evidence rules, a row the evidence
cannot yet support is **reported, not filled in with a placeholder-shaped
number**. The README's "Raw min-entropy per bit" and "Quality" rows remain
the placeholders they already were, now pointing at this document rather
than only at "owed by #12/#13" — #13's worst-corner analysis inherits the
same ceiling this document derives (Section 1 already evaluates DR-0010's
own entropy-binding corner, `ss`/−40 °C/3.63 V, alongside nominal) and does
not change the conclusion that no affordable transistor-level simulation
reaches the entropy-supporting rate. A non-placeholder number for this row
becomes available only from measured silicon (DR-0004 Tier 3) or from a
superseding decision that changes the rate/power/cell trade-off DR-0010
already argues through.

## Follow-up

- **#13** (worst-corner min-entropy) inherits this document's ceiling; its
  job is confirming the entropy-binding corner over the full grid, not
  producing a number this issue could not.
- **If DR-0010's proposed 500 bps rate is ratified**, the array-sizing
  cross-check in Section 1 (`Q_array` ≈ 8.6× the required margin at `ss`,
  using the more favorable starved-cell constant) is the number to revisit —
  but a transistor-level bitstream at that rate remains unaffordable to
  simulate directly by the same argument that makes it unaffordable today;
  only measured silicon (Tier 3) or a materially cheaper simulation method
  changes that.
- **A cheaper accumulation-window design**, if one is ever found, is named
  by [DR-0010]'s own "Revisit if" as the kind of change that would move this
  conclusion; nothing in this repository's toolchain provides one today.

[DR-0002]: spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md
[DR-0003]: spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0004]: spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0007]: spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md
[DR-0009]: spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0010]: spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0012]: spec/decision-records/DR-0012-transient-noise-simulation-methodology.md
