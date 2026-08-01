---
dr: DR-0012-transient-noise-simulation-methodology
title: Fix the seed policy, run-length/claim-support limits, and noise-model limits that bound every transient-noise entropy claim this repo makes
status: Accepted
date: 2026-08-01
deciders: Builder (issue #10), a methodology/claim-boundary decision -- not a change to a ratified spec row, see Status.
supersedes: n/a
superseded_by: n/a
related: "#10 (origin), #2, #7 (dependencies, closed); #12, #13, #17, #46 (downstream consumers); DR-0004 (SP 800-90B tiering this record enforces), DR-0006 (seed/PVT precedent this record generalizes), DR-0007 (Baudet Q-to-H formula), DR-0002 (health-test H-dependence); sim/README.md (record format, base seed rule); sim/tb/trnoise-calibration (noise-model empirical basis); sim/tb/jitter-estimator-calibration (this record's calibration experiment)"
---

# DR-0012: Fix the seed policy, run-length/claim-support limits, and noise-model limits that bound every transient-noise entropy claim this repo makes

## Status

- 2026-08-01: **Accepted** by the Builder of #10. This is a
  methodology/claim-boundary record -- it fixes the seed policy, run-length/
  claim-support ceiling, and noise-model limits that bound a *future* numeric
  claim; it does not itself change any ratified spec row -- the same
  self-ratification basis DR-0006 (deciders: "Builder (issue #4)"), DR-0009
  (deciders: "Builder (issue #8) ... Not an operator ratification") and
  DR-0011 (deciders: "Builder (issue #43) ... not a change to a ratified spec
  row") already established as current practice in this repository.
  DR-0004/DR-0007/DR-0010, by contrast, needed operator ratification (#1, #29)
  because each *changed* a ratified spec row (the quality tiers, the
  entropy-source architecture, the raw-rate target); this record changes no
  spec row and enforces DR-0004's tiering rather than amending it.
  Note the numbering: this is DR-0012, not DR-0011 -- DR-0011
  (`DR-0011-metastability-hybrid-tap-claims-and-scope.md`) landed first via
  #47 on 2026-08-01, ahead of this record.

## Context

Issue #6 drafted a quality row this project cannot honestly claim pre-silicon
("NIST SP 800-90B entropy validation pass"). DR-0004 resolved that into a
three-tier structure -- designed-for-90B (Tier 1), a bounded sim-stage
min-entropy *estimate* (Tier 2), and 90B validation proper deferred to
measured silicon (Tier 3) -- and named this issue as the source of "the
honest ceiling" Tier 2 operates under: *"Every estimate is produced within
#10's methodology contract and inherits its stated claim limits. Claims
outside the contract are not recorded as evidence."* Nothing before this
record fixed what that ceiling actually is.

Three separate questions were open, and conflating them is the failure mode
this record exists to prevent:

1. **How many independent stochastic runs are enough**, and where is that
   already decided vs. still ad hoc? DR-0006 answered this for one issue's
   testbenches (#4's jitter characterization) with a documented cost/coverage
   trade-off (4 seeds per PVT point; a reduced 3-corner grid; a flagship-vs-
   headline-point split), but the reasoning was never generalized into a
   repo-wide default. `sim/README.md` already states the mechanical floor --
   *"No seed, no evidence... any stochastic analysis... must record every
   seed it used"* (`sim/README.md:24`) -- but that is a record-format rule,
   not a statistical-adequacy one; it says a seed must be written down, not
   how many seeds make a reported spread trustworthy.
2. **What can a feasible simulated bit count actually support?** DR-0004
   Tier 2 already restricts estimators to "the extent the achievable
   simulated bit count supports" and defers the restart dataset, but does
   not say which named estimator classes cross that line. Downstream issues
   (#12, #13, #17) all cite "the #10 methodology contract" as the boundary on
   what they are allowed to claim; until this record exists, that citation
   points at nothing.
3. **What does ngspice's injected `trnoise()` noise represent, and what does
   it silently omit?** Every transient-noise result in this repo (jitter
   characterization, the entropy source's sizing law, any future estimator
   run) rests on this. `sim/tb/trnoise-calibration/` already measured the
   `trnoise()` sample-and-hold PSD mapping (`sim/records/2026-07-31-trnoise-calibration-01.md`,
   confirming `S_w = 2*NA^2*NT` to within ~1-3% on the white branch and
   flagging the 1/f branch as order-of-magnitude only). That is the empirical
   basis for a noise-model-limits statement; it had never been written down
   as one.

A related, explicitly out-of-scope question: issue #46 validates the
DR-0010 jitter-energy law (`σ_acc(t)` on a bare ring node) using none of
this record's machinery, and by design -- its scope confirmation is adopted
here rather than re-litigated: this record stays at the **bit/estimator**
level (seed policy for stochastic runs in general, run-length vs.
claim-support limits, noise-model coverage) and does not also own raw
ring-node jitter-accumulation calibration, which is DR-0010's
`sim/tools/jitter_energy_law.py` territory.

No numeric entropy claim is cited or made by this record. It fixes the rules
a later record must follow to make one.

## Decision

We adopt three rules, binding on every stochastic transient-noise result
this repository records or cites as evidence from this point forward, and we
add one calibration experiment that checks the estimator half of the
pipeline behaves as this record says it does.

### 1. Seed policy (generalizes DR-0006)

DR-0006's per-testbench trade-off is adopted as the **repo-wide default**,
stated once instead of re-derived per issue:

- **Default: 4 independent seeds per reported PVT point.** This is not a new
  number -- it is DR-0006's flagship-and-headline-point default, already in
  use by every `tran-noise` testbench this repo has shipped
  (`sim/tb/trnoise-calibration`, the `ro-*-jitter` family, and this record's
  own `sim/tb/jitter-estimator-calibration`). Four seeds is enough to report
  a mean and a run-to-run spread (sim/README.md's required frontmatter
  fields `analysis.runs` and `seeds`, and the required "Result" prose
  spread) without each additional seed being separately justified.
- **A single-corner or single-point testbench may use fewer, if the circuit
  has no PVT dependence by construction.** DR-0006 already carved this out
  for `trnoise-calibration` (an ideal RC/noise-source circuit: "process
  corner must NOT move ideal-resistor noise, so sweeping corner would only
  be re-proving a null result already covered by any one corner") and for
  `noise-floor-resistor`. This record generalizes the carve-out's *reason*
  (no PVT dependence -> no PVT sweep needed) rather than the specific
  testbenches it was granted to; a future ideal-circuit calibration
  testbench may claim it without a fresh DR, provided its own header states
  the same no-PVT-dependence argument DR-0006 and `trnoise-calibration`'s
  header make.
- **A reduced PVT grid (fewer than the harness's full corner set) requires
  the same kind of stated trade-off DR-0006 made, not silent truncation.**
  DR-0006's own three-tier split (flagship: full reduced grid; other
  configs: three headline points; ideal circuits: one point) is the worked
  example a future testbench should follow and cite, not re-argue from
  scratch, unless its own cost/coverage balance genuinely differs -- in
  which case it states its own trade-off the way DR-0006 did, as a citable
  record rather than an unstated shortcut.
- **This is a statistical-adequacy floor layered on top of, not a
  replacement for, `sim/README.md`'s mechanical rule.** Every seed used
  must still be recorded verbatim in run order (`sim/README.md`'s `seeds`
  frontmatter field); this section governs how many, that section governs
  how they get written down. Deviating from the 4-seed default (either
  direction) is permitted but must be justified in the record's own text,
  the same way DR-0006 justified its trade-off rather than asserting it.

### 2. Run-length and claim-support limits (the DR-0004 Tier 2 ceiling)

This section is the artifact DR-0004 Tier 2 and downstream issues (#12,
#17) cite. It does not change DR-0004's tiering; it fills in the boundary
DR-0004 left to this record.

**Supportable in simulation, within this repo's demonstrated cost budget**
(per-run wall-clock times of order minutes to tens of minutes, per DR-0006's
measured figures, and the multi-seed defaults in §1 above):

- A **bounded sim-stage min-entropy point estimate** from a most-common-value
  (or comparably simple bounded) estimator, applied to a raw bitstream of up
  to roughly `10^5`-`10^6` samples per seed -- the range this repo's
  transient-noise testbenches already reach in a `tran-noise` run of a few
  microseconds at a `~10 ps` step (e.g. `sim/tb/trnoise-calibration` and
  `sim/tb/jitter-estimator-calibration` both reach `4*10^5` samples per seed
  at `tstop=4u`, `tstep=10p`). This is the estimator DR-0004 Tier 2 means by
  "90B-style estimators ... applied only to the extent the achievable
  simulated bit count supports."
- **Confidence degradation at the achieved N, stated explicitly.** A point
  estimate from `N` binary samples carries a binomial standard error of
  order `sqrt(p(1-p)/N)` on the underlying bias, which propagates to the
  reported `H` through the estimator's sensitivity near the achieved `p`
  (steepest, `~1/(p ln 2)`, near `p = 0.5`, i.e. near `H = 1`). At
  `N ~ 4*10^5` and `p` near 0.5 this is order `10^-3` bit; smaller `N` (a
  real RO-jitter testbench's accumulation window is typically far shorter
  than 4 µs, per DR-0006's per-run cost figures) worsens it proportionally
  to `1/sqrt(N)`. Every reported estimate states this figure or its
  equivalent, not just the point value.

**Not supportable in simulation, and not to be attempted as a substitute for
a genuine result:**

- **The full SP 800-90B non-IID estimator suite (all ten estimators) run at
  its recommended sample sizes.** 90B's non-IID track is designed and
  validated against datasets on the order of `10^6` *consecutive* samples
  per estimator, run across multiple estimators whose confidence intervals
  assume that scale; several of the ten estimators (e.g. the collision,
  Markov, and compression estimators) are also computationally expensive
  at that N even given the data. Reaching `10^6`+ consecutive transient-
  noise samples from a *real* RO-jitter testbench (not an idealized noise
  source like this record's calibration) multiplies the per-seed simulated
  time proportionally, which multiplies the per-run wall-clock cost DR-0006
  already measured in the minutes-to-tens-of-minutes range per run --
  pushing a single seed into hours, and four seeds (§1's default) into a
  day or more, for *one* PVT point. Running the suite at an unsupported,
  truncated N and quoting the result is explicitly a **review-blocking
  defect**, not a partial result (this restates, rather than relaxes,
  DR-0004 Tier 2's identical rule).
- **The restart test** (SP 800-90B's dependence-on-startup-conditions check,
  nominally ~1000 independent power-on restarts). DR-0004 already defers
  this to measured silicon as "answered far more meaningfully by measured
  silicon than by 1000 re-initialized transient-noise invocations," and
  states its absence pre-silicon is not a spec failure. This record's cost
  analysis does not change that verdict: 1000 independent transient-noise
  invocations, each needing its own settling transient before the sampled
  window even starts, is the same order-of-magnitude cost problem as the
  non-IID suite above, applied 1000 times over. **Affordability verdict:
  not affordable**, consistent with DR-0004's default and closing the one
  question DR-0004 left open to this record ("the affordability verdict on
  the restart dataset").
- **Anything requiring correlated statistics across independent seeds**
  beyond a simple mean/spread (e.g. a claimed confidence interval that
  assumes seeds are draws from a single long-run stationary process rather
  than what they actually are -- independent short transient-noise runs).
  §1's seed policy produces a spread across runs, not a single long
  sequence; conflating the two overstates confidence.

**Consistency with DR-0004's Tier 1-3 structure:** nothing above moves any
tier. Tier 1 (designed-for-90B) is a structural, by-inspection property and
unaffected. Tier 2's ceiling is exactly what this section states -- a bounded
point estimate with stated confidence degradation, sequential dataset
targeted at up to the achievable N, restart dataset out. Tier 3 (validation
proper) remains deferred to measured silicon; nothing in this record
authorizes calling any simulated number a 90B assessment, pass, or
validation, and DR-0004's mandatory label (*"simulation-derived design
estimate; not an SP 800-90B entropy assessment"*) applies to every number
produced under this ceiling.

### 3. Noise model limits (what `trnoise()` does and does not represent)

`sim/tb/trnoise-calibration/` is the empirical basis for this section; its
result is cited, not re-derived:

- **ngspice does not simulate device noise during `.tran`.** Every
  transient-noise result in this repo comes from an explicitly *injected*
  `trnoise()` source, never from a device's own intrinsic noise being
  excited by the simulator during a transient analysis. This is stated in
  `tb_trnoise_cal.sp`'s header and is the load-bearing assumption every
  `tran-noise` testbench in `sim/tb/` inherits.
- **The injected source is a sample-and-hold approximation, not continuous
  white noise.** `trnoise(NA, NT, NALPHA, NAMP)` holds a fresh Gaussian
  sample of rms amplitude `NA` for `NT` seconds, giving a flat one-sided PSD
  `S_w = 2*NA^2*NT` that rolls off as `sinc^2(f*NT)` with its first null at
  `1/NT` -- confirmed to within ~1-3% on the white branch by two independent
  RC-filtered measurements a decade apart
  (`sim/records/2026-07-31-trnoise-calibration-01.md`). Any claim relying on
  noise content above roughly `1/NT` is outside what the injected source
  represents, regardless of what a real device would do at that frequency.
- **The 1/f (flicker) branch is a materially weaker calibration.** The same
  record states the 1/f branch is confirmed only at order-of-magnitude,
  because a 1/f spectrum's low-frequency integral is run-length-dependent
  by construction; DR-0007 separately notes the repo's flicker testbench
  "could not resolve the 1/f contribution at 4 seeds and a 32-period
  window," so every jitter figure derived from these testbenches is a
  **lower bound** on real flicker-dominated long-term jitter, not a
  measurement of it.
- **Every real entropy contributor or detractor the injected sources do not
  model is invisible to every result in this repo**, specifically:
  - Any noise mechanism not represented by an injected `trnoise()` call at
    all (e.g. supply/substrate noise coupling not modeled as an explicit
    source in the testbench).
  - **Cross-coupling between array members.** DR-0007's array sizing law
    sums *independent* per-ring variances; an isolated single-ring
    testbench structurally cannot observe injection locking or shared-
    supply coupling between rings, which DR-0007 §6 and the array-level
    `sim/tb/ro-array-sanity-jitter` testbench address separately, not this
    record.
  - **Anything a physical fabricated device does that ngspice's device
    models do not reproduce** (a PDK-model-fidelity limit, not a
    `trnoise()`-specific one, but one every number in this repo inherits
    regardless of source).

### 4. Calibration experiment

`sim/tb/jitter-estimator-calibration/` (new) exercises the *estimator* half
of the pipeline this record's §2 bounds, using the *already-calibrated*
`trnoise()` source §3 describes -- deliberately **not** re-deriving the
`trnoise()`-to-PSD mapping `trnoise-calibration` already covers, and
deliberately **not** modeling RO phase accumulation/wraparound (DR-0010's
`sim/tools/jitter_energy_law.py` and the real jitter testbenches' territory,
per the #46 scope confirmation cited in Context).

**Design.** The testbench's `trnoise()` source delivers one fresh,
independent, zero-mean Gaussian sample `v(nw) ~ N(0, NA^2)` every `NT`
seconds (`NA = 2.2361e-3`, the same value `trnoise-calibration` validates;
`NT` set equal to the harness's `linearize` print step, so each grid point
is one held sample, not an interpolated one). A comparator decision --
`bit = 1` iff `v(nw) + bias > 0` -- is exactly the structural decision an
RO-jitter sampler makes when accumulated phase noise competes against a
fixed timing reference, and for a Gaussian sample of known sigma it has a
**closed-form, exact** (not bounded) probability:

```
P(bit = 1) = Phi(bias / NA)
```

Three `bias` values are chosen (via the standard normal quantile function,
`statistics.NormalDist.inv_cdf`, in
`sim/tools/jitter_estimator_calibration_check.py`) so this probability
equals `2^-H` for `H` in `{1.0, 0.5, 0.1}` bit/sample -- spanning
near-unbiased, the design's own `H_0 = 0.5` target (DR-0002/DR-0007), and a
strongly biased regime near the low end of DR-0002's APT degeneracy
discussion. All three run in a **single** ngspice invocation (one
`trnoise()` source, three independent `let` expressions over the same
sampled vector), so the experiment costs one testbench's worth of
transient-noise simulation, not three.

**Estimator under test.** The most-common-value point estimator
`H_hat = -log2(max(p1_hat, 1 - p1_hat))` -- the estimator §2 names as what a
bounded sim-stage estimate is allowed to be -- is applied to the simulated
`p1_hat` at each bias level.

**Prediction and tolerance.** `sim/tools/jitter_estimator_calibration_check.py --check`
computes the closed-form `H` target at each level and asserts
`|H_hat - H_target|` is within **0.02 bit** for all three, exiting non-zero
otherwise -- the same shape as DR-0010's
`sim/tools/jitter_energy_law.py --check`. The tolerance is chosen with
headroom over the binomial sampling error this repo's own §2 analysis
predicts at the achieved N (order `10^-3` bit per seed near `H = 1`,
smaller elsewhere), so the check fails on a real regression (the bias
values and the estimator silently drifting apart, or a testbench/harness
change altering the sampled distribution) rather than on ordinary run-to-run
noise.

**Result.** See `sim/records/2026-08-01-jitter-estimator-calibration-01.md`
for the committed run (4 seeds, `tt`/27 C/3.30 V -- no PVT sweep, per §1's
ideal-circuit carve-out, since the injected source has no PDK/corner
dependence by construction) and its measured deviation from the closed-form
prediction.

## Alternatives considered

### State the seed/run-length/noise-model rules inline in each future
### evidence record instead of one shared methodology document

- **What**: Let each testbench or issue re-derive its own seed count,
  run-length justification, and noise-model caveat as needed.
- **Why plausible**: No new document; every record already carries a
  Caveats section that could, in principle, carry this.
- **Why rejected**: DR-0004 Tier 2 and three downstream issues (#12, #13,
  #17) already cite "the #10 methodology contract" as a single load-bearing
  boundary. A boundary re-derived per record is not a boundary -- it invites
  exactly the drift (a later record quietly attempting the non-IID suite at
  an unsupported N, or omitting the noise-model caveat) this repo's
  evidence rules exist to prevent. A single decision record, cited rather
  than restated, is the same pattern `sim/README.md` already uses for the
  record-format rules.

### Attempt the full non-IID suite at whatever N is affordable, with a
### confidence caveat instead of a hard "not supportable" line

- **What**: Run all ten 90B non-IID estimators against the largest N this
  repo's cost budget affords, and label the output "reduced-confidence"
  rather than refusing it.
- **Why plausible**: It would exercise the whole estimator pipeline early,
  which has some rehearsal value, and "reduced confidence" is technically
  true.
- **Why rejected**: Several of the ten estimators are validated by 90B
  specifically against large-sample asymptotic behavior; run far below that
  N, their output is not a "less confident version of the real answer," it
  is arithmetic performed outside the regime the estimator's own derivation
  assumes -- indistinguishable, to a reader, from a real result. DR-0004
  already calls exactly this failure mode out ("Running an estimator at an
  unsupported N and quoting the result is a review-blocking defect, not a
  partial result"); this record enforces rather than relaxes that line.
  This record's calibration experiment gets the pipeline-rehearsal benefit
  a full-suite attempt would have provided, at a fraction of the cost,
  without the mislabeling risk.

### Extend `sim/tb/trnoise-calibration/` in place, rather than adding a new
### testbench for the calibration experiment

- **What**: Add the bit-extraction/estimator stage as new measurements on
  the existing `trnoise-calibration` testbench instead of a sibling
  directory.
- **Why plausible**: One fewer testbench directory; reuses the exact same
  `trnoise()` parameters already committed there.
- **Why rejected**: `trnoise-calibration` checks a **different** claim (the
  source-to-PSD mapping, via RC-filtered rms measurements) than this
  record's calibration checks (bit-extraction + estimator behavior, via a
  comparator and a min-entropy point estimate). Folding both into one
  manifest would mean one `tb.json`'s `measure` block mixes rms-based and
  probability-based quantities with different analytic derivations and
  different tolerance bases, which is harder to review and harder to cite
  precisely later ("`trnoise-calibration` measurement N" would stop meaning
  one thing). A sibling testbench that explicitly reuses and cites the
  validated NA/NT keeps each testbench's claim single-purpose, matching how
  `sim/tb/ro-*-jitter` and `sim/tb/inv-stage-noise`/`sim/tb/cinv-stage-noise`
  already split the per-stage-noise-density check from the ring-level
  jitter-accumulation check rather than merging them.

### Model RO phase accumulation and wraparound in the calibration experiment,
### rather than a simpler comparator/threshold decision

- **What**: Build the calibration testbench around an ideal phase
  accumulator (`sigma_acc(t)` growing with `t`, wrapped mod an assumed
  period `T0`) and check its bits against the Baudet-et-al. `H(Q)` bound
  DR-0007 cites, instead of a single-sample Gaussian threshold.
- **Why plausible**: It would be a closer analogue of a real RO-jitter
  sampler, and would exercise the same `Q` formula DR-0007's sizing law and
  DR-0002's cutoff table depend on.
- **Why rejected**: Two problems, not one. First, the Baudet formula is a
  **bound**, not an exact prediction -- checking a point estimate against a
  bound cannot demonstrate the estimator "recovers the right answer within
  tolerance" the way a check against an exact closed form can, because a
  passing result would not distinguish "the pipeline is correct" from "the
  bound has slack." Second, and more importantly, this is explicitly #46's
  and DR-0010's territory per the Context section's scope confirmation:
  `sim/tools/jitter_energy_law.py` already calibrates the accumulation-law
  side of this problem using real ring measurements, and duplicating it
  here with an idealized accumulator would blur exactly the boundary the
  curator's related-work reconciliation drew. The simpler
  threshold-on-a-known-Gaussian design isolates the estimator stage this
  record's §2 actually bounds, with an exact rather than bounded prediction
  to check against.

## Consequences

- **Positive**:
  - #12, #13, #17 have a citable, concrete boundary instead of an
    open-ended "use judgement" -- both what they may claim (§2's supportable
    list) and what they must not attempt (§2's unsupportable list, with the
    restart-dataset affordability question DR-0004 left open now closed:
    not affordable).
  - The seed-policy default (§1) is now stated once and generalized from
    DR-0006's worked example, so a future testbench cites it instead of
    re-deriving a seed count from scratch.
  - The noise-model-limits section (§3) makes explicit, in one place, every
    real-world entropy contributor/detractor this repo's simulation results
    are structurally blind to -- which is exactly the caveat CLAUDE.md's
    "no claim without a testbench" rule needs to be enforceable rather than
    aspirational.
  - The calibration experiment demonstrates the estimator half of the
    pipeline (comparator + most-common-value point estimate) recovers a
    known closed-form answer within a stated, pre-committed tolerance --
    the same kind of check DR-0010's jitter-energy-law calibration provides
    on the accumulation side, now covering the other half.
  - No numeric entropy claim is made by this record, consistent with
    DR-0004's caution that a sim-stage estimate is a design estimate, not a
    validated claim, and with this issue's own acceptance criteria.

- **Negative / accepted cost**:
  - The non-IID suite and the restart dataset are now formally out of
    scope for every pre-silicon issue, not just informally deferred --
    #12/#13 cannot partially attempt either and label it "reduced
    confidence" without that being a review-blocking defect under this
    record.
  - The seed-policy default (4 seeds) is not re-derived from first
    principles here; it inherits DR-0006's own accepted cost/coverage
    trade-off and its accepted gaps (no `fs`/`sf` corner coverage by
    default, a stage-count/candidate comparison checked at only 3 PVT
    points rather than a full grid).
  - The calibration experiment's comparator/threshold design deliberately
    does not exercise RO phase accumulation or wraparound -- a genuine gap
    in what it demonstrates, closed by construction (see Alternatives)
    rather than by omission, but real: passing this calibration says
    nothing about whether a *real* RO-jitter bitstream's min-entropy
    estimate will be well-behaved, only that the estimator arithmetic
    itself is correct given a bitstream of known statistics.

- **Follow-up required**:
  - **#12** applies this record's §2 ceiling to the real raw bitstream: a
    bounded point estimate (with the confidence-degradation figure §2
    requires) at the achievable sequential N, explicitly not the non-IID
    suite or the restart dataset.
  - **#13** identifies the worst-corner min-entropy within the same §2
    ceiling.
  - **#17** (post-layout extracted re-run) inherits the same ceiling for
    its own bitstream.
  - Any future transient-noise testbench that wants a seed count other than
    the §1 default, or a PVT grid narrower than the harness's full set,
    states its own cost/coverage trade-off in its own record or a citing
    DR, following the DR-0006 pattern rather than truncating silently.

- **Revisit if**: this repo's measured per-run simulation cost changes
  enough (e.g. a faster host, or a cheaper accumulation-window design) to
  make the non-IID suite or the restart dataset affordable at the scale
  they need -- in which case a superseding DR states the new affordability
  verdict rather than silently attempting either; or a future testbench's
  cost/coverage balance genuinely does not fit DR-0006's worked example,
  in which case that testbench's own citing record states why, per §1.
