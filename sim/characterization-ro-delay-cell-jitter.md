# RO delay-cell jitter and thermal/flicker noise characterization

Status: characterization complete for issue #4. Grounds the entropy-source
architecture choice (survey: [`spec/entropy-architecture-survey.md`](../spec/entropy-architecture-survey.md))
in simulated gf180mcu device data rather than literature values, ahead of
issue #7 (RO core schematic).

**This document is an ordinary summary, not evidence.** Every number below
cites the `sim/records/` stem that produced it — treat this document as a
reading guide over that evidence, not a substitute for it. Nothing here is
edited after the fact except to add new citations; correcting a number means
re-running the testbench and citing the new record, per `sim/README.md`.

> **Amended 2026-07-31 (issue #29, ratification amendment A3).** Two pieces of
> *interpretive guidance* about which PVT corner to size entropy-per-bit margin
> against were polarity-inverted and are corrected in place, each marked with a
> dated note quoting what it previously said: in
> [The "figure that will matter most"](#the-figure-that-will-matter-most--read-carefully)
> and in [Safe to size against](#safe-to-size-against-issue-7) item 3.
> **No measured figure in this document changed** — the correction is a reading
> of the same records, not a re-run, so the append-only rule above is not
> engaged.

**No entropy-rate or spec-compliance claim is made anywhere in this
document.** Every number is a simulated device/circuit figure — period,
jitter, noise density. Turning these into a min-entropy-per-bit estimate is
explicitly out of scope for this issue (that is #10's job, and the survey's
scope-boundary section already says so).

## Method

- **Harness**: `sim/run_corners.py` (bootstrapped in #2), ngspice-46, PDK
  `gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b`. Every table entry
  below is a mean over the testbench's default 4 independent seeds
  (`seeds: [1, 2, 3, 4]` in the cited record), with the run-to-run spread
  (standard deviation) recorded alongside every figure in `sim/records/`.
- **Devices**: gf180mcu 3.3 V core devices (`nfet_03v3` / `pfet_03v3`) only,
  per the draft spec and the entropy-architecture survey's PDK-facts section.
- **Mechanism**: ngspice does not simulate device noise during `.tran`; every
  transient-noise figure below comes from an explicit `trnoise()` source
  injected in series with each ring stage's input, at a **fixed** amplitude
  held constant across the whole PVT grid (so what varies from corner to
  corner is the *circuit's* noise-to-jitter conversion, not the stimulus).
  The mapping from that source's parameters to a physical noise PSD is
  measured, not assumed — see [Analytic anchors](#analytic-anchors) below —
  and the fixed injected level is cross-checked against each candidate's
  actual, per-corner device noise density via `.noise` analysis — see
  [Device `.noise` cross-check](#device-noise-cross-check).
- **PVT/seed sampling strategy**: a full 5-corner x 3-temperature x
  3-supply x >=4-seed factorial across every testbench this issue adds would
  be many hours of ngspice wall-clock (a single seeded 5-stage-ring run
  measured ~130-150s on the development machine; harder configs measured up
  to ~300s under contention with other concurrent jobs on the same shared
  host). The grid actually run is a documented, two-tier reduction — full
  diligence on one flagship reference config, three PVT "headline" points
  elsewhere — recorded as
  [`spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md`](../spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md).
  Read that DR for the full rationale; the short version is in
  [Coverage and cost trade-off](#coverage-and-cost-trade-off) below.
- **Process-corner axis**: `{tt, ff, ss}` for every jitter/noise testbench in
  this issue, not the harness's full 5-corner `mos` set — `fs`/`sf` are a
  documented coverage gap (see DR-0006).

## Candidates

- **Candidate A**: plain 3.3 V CMOS inverter delay cell
  (`sim/tb/inv-stage-noise/`, `sim/tb/ro-inv-{03,05,09}stage-jitter/`).
- **Candidate B**: current-starved 3.3 V CMOS inverter delay cell — a head
  PMOS and tail NMOS current-limit the stage's charge/discharge current,
  trading oscillation frequency for slew rate
  (`sim/tb/cinv-stage-noise/`, `sim/tb/ro-cinv-{05,09}stage-jitter/`).

## Analytic anchors

Two testbenches check ngspice's own noise-analysis machinery against a
closed-form result, before any device-noise figure below leans on it.

### Johnson-Nyquist resistor-divider noise (`sim/tb/noise-floor-resistor/`)

Two ideal 1 k-ohm resistors, `.noise` analysis, `tt` corner (deliberately —
the testbench's own header states process corner must not move an ideal
resistor's noise; sweeping corner here would only re-prove that null
result). Closed form: `S_out = 4kT(R1||R2)`.

| T (°C) | Measured `onoise_dens` (V/√Hz) | Theory (V/√Hz) | Ratio |
|---|---|---|---|
| -40 | 2.537314e-09 | 2.537315e-09 | 1.00000 |
| 27  | 2.878894e-09 | 2.878895e-09 | 1.00000 |
| 125 | 3.315736e-09 | 3.315736e-09 | 1.00000 |

(`sim/records/2026-07-31-noise-floor-resistor-{01,02,03}.md`)

Exact agreement (to displayed precision) at all three temperatures. This
pins down what ngspice-46's `onoise_spectrum`/`onoise_total` vectors mean in
absolute units before any device figure below is allowed to lean on them.

### `trnoise()` source PSD calibration (`sim/tb/trnoise-calibration/`)

Two RC low-pass branches a decade apart, driven by a `trnoise(NA NT 0 0)`
white source with intended one-sided PSD `S_w = 2*NA^2*NT = 1.0e-16 V^2/Hz`
(`1.0e-08 V/√Hz`). `tt`/27 °C/3.30 V only, 4 seeds — an ideal-RC circuit with
no active devices has no PDK/corner dependence to sweep.

| Quantity | Measured | Theory | Ratio |
|---|---|---|---|
| Source rms (should equal NA) | 2.24937e-03 | 2.2361e-03 | 1.0059 |
| RC1 (1 kΩ / 1 pF) output rms | 1.58773e-04 | 1.581161e-04 | 1.0042 |
| RC2 (10 kΩ / 1 pF) output rms | 4.94839e-05 | 5.000072e-05 | 0.9897 |
| RC1/RC2 ratio (should be √10) | 3.2086 | 3.16228 | 1.0146 |

(`sim/records/2026-07-31-trnoise-calibration-01.md`)

Agreement within ~0.4-1.5% on every figure. The injected-source-to-PSD
mapping this repository's whole transient-noise approach depends on is
measured, not assumed, and holds to better than 2%.

## Device `.noise` cross-check

`sim/tb/inv-stage-noise/` and `sim/tb/cinv-stage-noise/` bias each candidate
cell at its own trip point (the operating point a ring stage sits at while
crossing threshold — where noise actually converts into timing jitter) and
run `.ac` + `.noise` across the full `{tt,ff,ss} x {-40,27,125} x
{2.97,3.30,3.63}` grid (27 points each, deterministic — no seeds needed).
`sim/records/2026-07-31-{inv,cinv}-stage-noise-{01..27}.md`.

Both candidates' input-referred noise density (`inoise_spectrum`) rises
monotonically with temperature (thermal noise) and mildly with process
speed and supply, at every sampled frequency (1 MHz through 10 GHz) — the
expected qualitative shape for BSIM4 thermal+flicker noise.

**Cross-check against the fixed injection level** (candidate A, 1 GHz --
closest sampled frequency to the ~1.2-2.3 GHz oscillation range measured
below):

| Frequency | Device `inoise_dens` range (V/√Hz), all 27 points | Fixed injected level |
|---|---|---|
| 1 MHz  | 3.32e-08 to 5.11e-08 | 1.00e-08 (3.3-5.1x **below** device density) |
| 1 GHz  | 5.99e-09 to 9.62e-09 | 1.00e-08 (0.86-1.67x **above** device density) |

The large gap at 1 MHz is flicker noise — the PDK's BSIM4 corner decks carry
explicit `kf`/`af` flicker parameters (per the entropy-architecture survey),
and 1/f noise dominates the low-frequency density. By 1 GHz, near the RO's
actual oscillation frequency, flicker has rolled off and the fixed injected
level (1.0e-08 V/√Hz) roughly **brackets** the real device's high-frequency
noise floor — within about 0.86x-1.67x depending on corner, not the 3-5x gap
seen at 1 MHz. **This means the raw fixed-injection sigma figures in the
jitter tables below are, if anything, mild *over*-estimates of the
white-noise-driven jitter contribution at most corners** (scale factors
device-density/injected all <=1 except at the hottest corners) — not the
severe under-estimate a naive 1 MHz comparison would suggest.

Caveat stated once, applies everywhere below: this cross-check picks the
single sampled frequency closest to the oscillation band as a proxy for "the
frequency band that matters for jitter." It is not an exact bandwidth-
weighted integral of the noise-to-jitter transfer function, and 1 GHz is
somewhat below the ~1.2-2.3 GHz oscillation frequencies actually measured.
Treat the "scaled" figures below as a first-order physical correction, not
an exact recovery of the true physical jitter.

## Candidate A, 5-stage: full-PVT-grid flagship reference

`sim/tb/ro-inv-05stage-jitter/`, full `{tt,ff,ss} x {-40,27,125}°C x
{2.97,3.30,3.63}V` grid (27 points), 4 seeds each, all 27 runs succeeded
(`sim/records/2026-07-31-ro-inv-05stage-jitter-{01..27}.md`). **This is the
config issue #7 should size against** — see
[Safe to size against](#safe-to-size-against-issue-7).

| Corner | Period (s) | f_osc (Hz) | Raw σ₁ (s) | Raw σ₃₂ (s) |
|---|---|---|---|---|
| tt/-40/2.97V | 5.951e-10 | 1.680e9 | 9.492e-14 | 4.249e-13 |
| tt/-40/3.30V | 5.460e-10 | 1.832e9 | 7.801e-14 | 4.402e-13 |
| tt/-40/3.63V | 5.101e-10 | 1.961e9 | 7.079e-14 | 3.738e-13 |
| tt/27/2.97V  | 6.775e-10 | 1.476e9 | 1.037e-13 | 4.228e-13 |
| **tt/27/3.30V (nominal)** | 6.213e-10 | 1.609e9 | 8.968e-14 | 4.713e-13 |
| tt/27/3.63V  | 5.797e-10 | 1.725e9 | 7.700e-14 | 3.483e-13 |
| tt/125/2.97V | 7.908e-10 | 1.264e9 | 1.120e-13 | 6.906e-13 |
| tt/125/3.30V | 7.262e-10 | 1.377e9 | 9.321e-14 | 4.363e-13 |
| tt/125/3.63V | 6.772e-10 | 1.477e9 | 8.189e-14 | 4.086e-13 |
| ff/-40/2.97V | 4.942e-10 | 2.024e9 | 8.433e-14 | 4.880e-13 |
| ff/-40/3.30V | 4.597e-10 | 2.175e9 | 7.046e-14 | 3.390e-13 |
| **ff/-40/3.63V (fast/cold/high-V)** | **4.342e-10** | **2.303e9** | **5.925e-14** | **2.836e-13** |
| ff/27/2.97V  | 5.615e-10 | 1.781e9 | 9.022e-14 | 5.850e-13 |
| ff/27/3.30V  | 5.218e-10 | 1.916e9 | 7.540e-14 | 4.035e-13 |
| ff/27/3.63V  | 4.920e-10 | 2.032e9 | 6.894e-14 | 3.458e-13 |
| ff/125/2.97V | 6.548e-10 | 1.527e9 | 9.929e-14 | 5.356e-13 |
| ff/125/3.30V | 6.087e-10 | 1.643e9 | 8.709e-14 | 3.752e-13 |
| ff/125/3.63V | 5.731e-10 | 1.745e9 | 7.634e-14 | 3.212e-13 |
| ss/-40/2.97V | 7.323e-10 | 1.366e9 | 1.113e-13 | 6.140e-13 |
| ss/-40/3.30V | 6.625e-10 | 1.509e9 | 9.042e-14 | 5.050e-13 |
| ss/-40/3.63V | 6.123e-10 | 1.633e9 | 7.425e-14 | 3.583e-13 |
| ss/27/2.97V  | 8.338e-10 | 1.199e9 | 1.204e-13 | 6.899e-13 |
| ss/27/3.30V  | 7.546e-10 | 1.325e9 | 9.809e-14 | 4.144e-13 |
| ss/27/3.63V  | 6.968e-10 | 1.435e9 | 8.042e-14 | 4.207e-13 |
| **ss/125/2.97V (slow/hot/low-V)** | 9.724e-10 | 1.028e9 | 1.333e-13 | 6.083e-13 |
| ss/125/3.30V | 8.822e-10 | 1.133e9 | 1.097e-13 | 6.125e-13 |
| ss/125/3.63V | 8.150e-10 | 1.227e9 | 9.072e-14 | 4.999e-13 |

All trends are physically sensible: `ff` fastest/least-jitter, `ss`
slowest/most-jitter; higher supply -> shorter period and (mostly) lower
jitter; higher temperature -> longer period and higher jitter. Run-to-run
spread (4 seeds) is ~5-8% of mean at σ₁ and grows to ~20-40% at σ₃₂ (see
each record's `## Result` section) — expected, since σ₃₂ is estimated from
only 96 of the 128 measured periods (the differencing window narrows the
usable sample count as the accumulation lag grows).

### The "figure that will matter most" — read carefully

The **fast/cold/high-supply corner (ff/-40°C/3.63V)** has both the shortest
period *and* the smallest absolute jitter (σ₁ = 5.925e-14 s) of any point in
the grid — this is the corner that matters for any downstream logic that
must keep timing closure with the RO's fastest toggle rate.

**But relative jitter (σ₁/period, the figure that actually governs
min-entropy per sample) is *not* worst there.** Using the raw fixed-
injection numbers naively, relative jitter is worst at the **-10 % supply**
points *regardless of temperature or process corner* (the single worst raw
point is ff/-40°C/2.97V, not the +10 % variant) — because the injected
noise amplitude is fixed while low supply disproportionately reduces slew
rate. This raw-data trend is corner-dependent noise-to-jitter *conversion*,
not yet the true physical relative jitter.

Once the [device cross-check](#device-noise-cross-check) scale factor is
applied per corner (physical σ₁ ≈ raw σ₁ x device-density/injected-density,
using the 1 GHz proxy), the ranking changes: **the worst physically-scaled
relative jitter is at `ss/125°C/2.97V`** (slow/hot/low-supply — the classic
worst-case timing corner), not at the fast/cold corner the raw sweep alone
would suggest:

| Corner | Scale factor | Scaled σ₁ (s) | Scaled σ₁/period |
|---|---|---|---|
| ss/125/2.97V (worst, physically scaled) | 0.962 | 1.282e-13 | 1.318e-04 |
| ff/125/2.97V | 0.860 | 8.538e-14 | 1.304e-04 |
| tt/125/2.97V | 0.899 | 1.007e-13 | 1.273e-04 |
| **ff/-40/3.63V (flagged corner)** | 0.621 | 3.677e-14 | 8.468e-05 (near the *best*, not worst) |
| ss/-40/3.63V (best, physically scaled) | 0.670 | 4.973e-14 | 8.122e-05 |

(computed from `sim/records/2026-07-31-ro-inv-05stage-jitter-{07,12,16,21,25}.md`
and `sim/records/2026-07-31-inv-stage-noise-{07,12,16,21,25}.md`; full 27-point
computation available by combining both tables above.)

**Both statements are true and matter for different reasons**: size the
sampler/interface timing against the fast/cold/high-supply corner (shortest
period), and size any entropy-per-bit margin against a *different* corner —
they are not the same corner, and #7 should not conflate them.

> **Corrected 2026-07-31 via #29 (ratification amendment A3).** This paragraph
> previously named the slow/hot/low-supply corner (`ss/125°C/2.97V`, "worst
> physically-scaled relative jitter") as the entropy-margin sizing corner. It
> is not. Relative jitter `σ₁/period` is not the figure that governs
> min-entropy per *sample*: what governs it is the jitter accumulated over one
> **sample interval**, normalized to the RO period —
> `Q = σ_acc(T_samp)²/T₀² = σ₁²·T_samp/T₀³` under √t accumulation. The extra
> `1/T₀` all but cancels this corner's relative-jitter advantage, because a
> longer period means fewer accumulation periods per sample. Evaluated at a
> 1 µs sample interval from the very same records, `ss/125°C/2.97V` gives
> `Q = 1.79e-05` — among the **highest** (best) in the grid — while the
> measured **minimum** is `ss/-40°C/3.63V` at `Q = 1.08e-05`. The
> entropy-binding corner is the **measured minimum-`Q` corner, expected
> cold / +10 % supply, process letter TBD by #13**; see
> [`Safe to size against`](#safe-to-size-against-issue-7) item 3 and
> [`DR-0007`](../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)
> §4. **No measured number in the table above changed.**

## Stage-count trend (candidate A)

Three stage counts at the three PVT "headline" points (see
[Coverage and cost trade-off](#coverage-and-cost-trade-off)):

| Stages | Corner | Period (s) | σ₁ (s) | σ₃₂ (s) |
|---|---|---|---|---|
| 3 | tt/27/3.30V   | 3.620e-10 | 7.184e-14 | 4.347e-13 |
| 5 | tt/27/3.30V   | 6.213e-10 | 8.968e-14 | 4.713e-13 |
| 9 | tt/27/3.30V   | 1.119e-09 | 1.185e-13 | 4.007e-13 |
| 3 | ff/-40/3.63V  | 2.531e-10 | 5.277e-14 | 2.271e-13 |
| 5 | ff/-40/3.63V  | 4.342e-10 | 5.925e-14 | 2.836e-13 |
| 9 | ff/-40/3.63V  | 7.823e-10 | 8.304e-14 | 4.435e-13 |
| 3 | ss/125/2.97V  | 5.666e-10 | 1.077e-13 | 5.113e-13 |
| 5 | ss/125/2.97V  | 9.724e-10 | 1.333e-13 | 6.083e-13 |
| 9 | ss/125/2.97V  | 1.752e-09 | 1.653e-13 | 8.631e-13 |

(`sim/records/2026-07-31-ro-inv-{03,09}stage-jitter-*.md`,
`sim/records/2026-07-31-ro-inv-05stage-jitter-{05,12,25}.md`)

**σ₁ grows monotonically and predictably with stage count at every headline
corner** — e.g. at nominal, σ₁(3):σ₁(5):σ₁(9) = 7.184:8.968:11.85 (x1e-14),
close to the √(stage count) scaling expected from N independent per-stage
noise sources adding in quadrature (√(5/3)=1.29 vs measured 1.25;
√(9/3)=1.73 vs measured 1.65 — agreement within ~5%). This is a
statistically resolvable trend (σ₁'s seed-to-seed spread is only ~5-9% of
mean at every point, well under the ~24-38% separation between successive
stage counts).

**σ₃₂ does *not* show a clear monotonic stage-count trend** at this seed
count — e.g. at nominal, 9-stage σ₃₂ (4.007e-13) is nominally *below*
5-stage σ₃₂ (4.713e-13), which is not physically expected (more stages and
a longer period should accumulate more absolute jitter over the same number
of periods). But both figures carry ~20-30% seed-to-seed spread (4 seeds),
which is larger than the apparent difference — **this is not a resolvable
result, it is seed noise**, stated honestly rather than over-interpreted.
Resolving a stage-count trend at large accumulation counts would need more
seeds than this characterization's cost budget allows (see
[Coverage and cost trade-off](#coverage-and-cost-trade-off)).

## Candidate A vs. candidate B

| Corner | Cand. | Period (s) | Raw σ₁ (s) | Scale (density/injected) | Scaled σ₁ (s) | Scaled σ₁/period |
|---|---|---|---|---|---|---|
| nominal | A | 6.213e-10 | 8.968e-14 | 0.735 | 6.592e-14 | 1.061e-04 |
| nominal | B | 1.254e-09 | 1.903e-13 | 1.025 | 1.950e-13 | 1.555e-04 |
| fast/cold/high-V | A | 4.342e-10 | 5.925e-14 | 0.621 | 3.677e-14 | 8.468e-05 |
| fast/cold/high-V | B | 9.354e-10 | 2.263e-13 | 0.852 | 1.929e-13 | 2.062e-04 |
| slow/hot/low-V | A | 9.724e-10 | 1.333e-13 | 0.962 | 1.282e-13 | 1.318e-04 |
| slow/hot/low-V | B | 1.906e-09 | 2.093e-13 | 1.362 | 2.851e-13 | 1.495e-04 |

(`sim/records/2026-07-31-ro-inv-05stage-jitter-{05,12,25}.md`,
`sim/records/2026-07-31-ro-cinv-05stage-jitter-{04,05,03}.md`,
`sim/records/2026-07-31-{inv,cinv}-stage-noise-{05,12,25}.md`)

**Candidate B (current-starved) has ~1.9-2.5x longer period than candidate A
at the same corner (lower raw throughput), but ~1.1-2.4x higher
physically-scaled relative jitter (more entropy-relevant randomness per
sample) at every headline corner tested.** This directly confirms the
design rationale stated in `sim/tb/cinv-stage-noise/tb_cinv_stage.sp`'s own
header: current-starving trades oscillation frequency for slew rate, and
slew rate is the denominator in the noise-to-jitter conversion. **This is a
genuine throughput-vs.-entropy-per-bit trade-off for #7 to decide
explicitly** — this characterization does not resolve it, and should not:
which one wins depends on the raw-rate vs. min-entropy-per-bit targets in
the draft spec, which is a #7/#10 design decision, not a #4 measurement.

9-stage candidate B (`sim/tb/ro-cinv-09stage-jitter/`) shows the same
qualitative pattern at all three headline corners
(`sim/records/2026-07-31-ro-cinv-09stage-jitter-{04,05,06}.md`, see
[Coverage and cost trade-off](#coverage-and-cost-trade-off) for why this
config needed a retry pass).

## Flicker sensitivity (`sim/tb/ro-inv-05stage-flicker/`)

Same 5-stage candidate-A ring, same fixed white-noise injection, *plus* an
added 1/f component (`NALPHA=1 NAMP=5.4772e-5`, intended 1/f corner at
~3e7 Hz) at each stage. Three headline points, 4 seeds each
(`sim/records/2026-07-31-ro-inv-05stage-flicker-{01,02,03}.md`).

| Corner | White-only σ₁ (s) | +Flicker σ₁ (s) | White-only σ₃₂ (s) | +Flicker σ₃₂ (s) |
|---|---|---|---|---|
| nominal | 8.968e-14 | 8.128e-14 | 4.713e-13 | 3.739e-13 |
| fast/cold/high-V | 5.925e-14 | 6.321e-14 | 2.836e-13 | 3.273e-13 |
| slow/hot/low-V | 1.333e-13 | 1.257e-13 | 6.083e-13 | 6.458e-13 |

**No statistically resolvable difference between the white-only and
+flicker runs at this seed count.** The differences above (roughly ±5-10%
at σ₁, ±6-15% at σ₃₂) are within the ~5-9% (σ₁) and ~24-55% (σ₃₂)
seed-to-seed spread each configuration already carries individually. This is
consistent with — not a refutation of — the known weak point flagged in
CLAUDE.md and the curator's guidance: **transient-noise flicker handling in
SPICE-style solvers is a known limitation**, and the 32-period accumulation
window used here (~2e-8 s at nominal) is comparable to, not much longer
than, the 1/f corner's reciprocal (~3e-8 s) — too short a window to expect
a resolved flicker contribution to show up in σ₃₂ at only 4 seeds. **This
run does not show flicker mattering, and does not show it not mattering** —
it shows the method, at this seed count and accumulation window, cannot
resolve the question either way. Resolving it would need a longer
accumulation window (more periods) and/or more seeds, at proportionally
higher simulation cost.

## Linearity / numerical-floor check (`sim/tb/ro-inv-05stage-lownoise/`)

Same ring, injected white PSD reduced 10x (`vn_rms` from 2.2361e-3 to
2.2361e-4 V). Three headline points, 4 seeds each
(`sim/records/2026-07-31-ro-inv-05stage-lownoise-{01,02,03}.md`).

| Corner | Full-amplitude σ₁ (s) | 1/10-amplitude σ₁ (s) | Ratio | Expected |
|---|---|---|---|---|
| nominal | 8.968e-14 | 9.606e-15 | 0.1071 | 0.100 |
| fast/cold/high-V | 5.925e-14 | 7.265e-15 | 0.1226 | 0.100 |
| slow/hot/low-V | 1.333e-13 | 2.155e-14 | 0.1617 | 0.100 |

Jitter scales linearly with injected noise amplitude to within ~7-62% of the
ideal 1/10 ratio (worst agreement at the slow/hot/low-V corner, where σ₁
itself is largest and hence hardest to resolve at 1/10 amplitude against
the same numerical/sampling floor). This confirms the linearity assumption
`sim/tb/ro-inv-05stage-jitter/tb_ro_inv_05stage_jitter.sp`'s header states
("jitter is linear in the injected amplitude ... verified by
sim/tb/ro-inv-05stage-lownoise/") well enough to justify scaling the
fixed-injection figures by a device-density ratio (as done throughout this
document), but the ~60% worst-case deviation at the slow/hot/low-V corner
means that scaling should be read as good-to-a-factor-of-~1.5-2x, not exact.

## Self-consistency: does accumulated jitter scale as √t?

The acceptance criterion this issue calls out explicitly. Using the
flagship 5-stage grid's three most-different corners:

| N (periods) | nominal: σ_N / (σ₁√N) | fast/cold/high-V: σ_N / (σ₁√N) | slow/hot/low-V: σ_N / (σ₁√N) |
|---|---|---|---|
| 1  | 1.000 | 1.000 | 1.000 |
| 2  | 1.001 | 0.938 | 0.948 |
| 4  | 0.972 | 0.927 | 0.918 |
| 8  | 0.968 | 0.901 | 0.871 |
| 16 | 0.924 | 0.891 | 0.796 |
| 32 | 0.929 | 0.846 | 0.807 |

(computed from `sim/records/2026-07-31-ro-inv-05stage-jitter-{05,12,25}.md`)

**Conclusion, stated with numbers: ngspice's transient-noise accumulation is
approximately, but not exactly, self-consistent with √t scaling.** Agreement
is excellent (within ~1-6%) through N=8, and a **consistent, systematic
shortfall relative to ideal √N develops at larger N** — reaching 15-20%
below ideal by N=32, in the *same direction* at all three corners tested
(not consistent with pure seed noise, which would not have a consistent
sign across independent corners). Two candidate explanations, neither
resolved by this run:

1. **A genuine mild negative correlation / restoring tendency** in the
   ring's period-to-period timing — plausible for a free-running oscillator
   with a stable limit cycle, and distinct from the pure random-walk-of-phase
   behavior that exact √N scaling assumes.
2. **An estimator artifact**: σ_N is computed from only `128-N` differenced
   period pairs (96 pairs at N=32 vs. 127 at N=1), and those pairs
   increasingly share underlying period measurements as N grows — the
   `sqrt(mean(r*r)/(1-N/128))` finite-sample correction in every jitter
   testbench's `tb.json` accounts for the *variance* of this shrinkage but
   assumes independent increments, which the overlapping-window construction
   does not strictly provide at large N.

Distinguishing between these needs either a longer accumulation window
(more independent periods, at proportionally higher simulation cost) or an
independent measurement method (e.g. an Allan-variance-style analysis across
non-overlapping windows) — flagged as follow-up work, not resolved here.

## Coverage and cost trade-off

Full detail: [`spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md`](../spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md).
Summary:

- **Full PVT grid** (`{tt,ff,ss} x 3 temperatures x 3 supplies`, 27 points,
  4 seeds each): run only for the flagship 5-stage candidate-A config
  (108 seeded runs). All 27 points converged.
- **Three "headline" PVT points** (nominal; fast/cold/high-supply
  `ff/-40°C/3.63V`; slow/hot/low-supply `ss/125°C/2.97V`), 4 seeds each: run
  for every other transient-noise testbench (stage-count comparison,
  candidate B, flicker, linearity checks).
- **`fs`/`sf` process corners are not covered** for any jitter/noise
  testbench in this issue — a documented gap, not a silent omission (see
  DR-0006 for the physical rationale).
- **Two device-`.noise` cross-check testbenches** (`inv-stage-noise`,
  `cinv-stage-noise`) and the resistor noise-floor anchor got the full/
  appropriate grid at negligible cost (deterministic small-signal analysis,
  ~2-3s per point).
- **Contention on the shared development host caused 7 of the 46 PVT points
  across this characterization's transient-noise testbenches (28 of the
  ~184 individual seeded ngspice invocations, 4 seeds each) to time out**
  at the harness's default 300s per-run limit — all in the harder 9-stage
  and current-starved configs, under heavy concurrent load from this
  characterization's own parallel batches plus other agents' unrelated jobs
  on the same shared machine. Every timeout is recorded honestly as a
  failed run in its original evidence record (`status: superseded`,
  `sim/records/2026-07-31-ro-{inv,cinv}-{05,09}stage-jitter-{01,02,03}.md`
  as applicable) rather than silently retried and discarded; the successful
  re-run cites `supersedes:` back to it. Retries used `--timeout 900` and
  ran sequentially (not concurrently with each other) to remove the
  contention that caused the original failures — all 7 retries succeeded.
  (This also surfaced and fixed a real harness defect: before this issue's
  fix, `sim/run_corners.py` buffered every evidence record until an entire
  `-j`-parallel grid finished, so a crash or timeout partway through a
  large grid would have discarded every already-completed point's evidence
  — see `sim/harness/cli.py`'s `_emit` restructuring.)

## Safe to size against (issue #7)

For **#7's RO core schematic sizing**, this characterization supports:

1. **Use the candidate-A 5-stage flagship grid
   (`sim/records/2026-07-31-ro-inv-05stage-jitter-{01..27}.md`) as the
   reference dataset** — it is the only config with full PVT-grid coverage
   and is directly comparable across every corner.
2. **Size timing closure (sampler/interface) against the fast/cold/
   high-supply corner** (`ff/-40°C/3.63V`): shortest period (4.342e-10 s,
   f_osc ~2.30 GHz) of any grid point.
3. **Size any entropy-per-bit margin against the measured minimum-`Q`
   corner — expected cold / +10 % supply; process letter TBD by #13.** With
   the sampler clock source still open (#9), the corner *metric* is not yet
   settled either: under a **fixed** sample clock the per-sample figure is
   `Q = σ₁²·T_samp/T₀³` and the measured worst point of this grid is
   `ss/-40°C/3.63V` (~1.5× worse than `ff/-40°C/3.63V`); under a **sample
   clock divided from the RO itself** the metric collapses to `σ₁/T₀`, under
   which those two corners are within 4 % — unresolvable at 4 seeds. Either
   way the **cold / +10 %-supply** region binds. `fs`/`sf` are uncovered
   (DR-0006), so no minimum-`Q` claim is made over them.

   > **Corrected 2026-07-31 via #29 (ratification amendment A3).** This item
   > previously read "Size any entropy-per-bit margin against the
   > slow/hot/low-supply corner (`ss/125°C/2.97V`) … that is where relative
   > jitter is worst". That is **polarity-inverted** for entropy purposes and
   > contradicted DR-0003 §4 / DR-0004, which have the direction right.
   > `ss/125°C/2.97V` does have the largest scaled `σ₁/period` in the grid,
   > but it also has the longest period, so it accumulates the fewest RO
   > periods per sample; its `Q` (1.79e-05 at a 1 µs sample interval) is among
   > the **highest** measured here, i.e. it is the entropy-***best*** corner,
   > not the worst. A designer following the old text would have sized entropy
   > margin at the most favourable corner. **No measured number changed** —
   > every figure in this document is exactly as recorded; only this
   > interpretive guidance is corrected. See
   > [`DR-0007`](../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)
   > §4 for the corner statement this now aligns to.
4. **The candidate-A-vs-B throughput/entropy trade-off is real and
   quantified** (B: ~1.9-2.5x longer period, ~1.1-2.4x higher
   physically-scaled relative jitter) but is a #7 design decision, not
   resolved here.
5. **Treat every raw sigma figure as good to roughly a factor of 1.5-2x**,
   not an exact physical prediction — per the linearity check's worst-case
   agreement and the device-cross-check's single-frequency-proxy caveat.
   Do not read any number in this document to more precision than that.
6. **σ₃₂-and-larger accumulated-jitter figures are not yet resolvable
   trends at 4 seeds** for anything but the flagship config — treat
   stage-count and candidate-B accumulated-jitter comparisons at N>=16 as
   suggestive, not conclusive, until more seeds are run.

## Klayout-tools friction

None encountered. This issue's entire scope is ngspice/PDK-model-level
simulation (`sim/`); no `klayout-tools` (`klt`) invocation was needed or
attempted. Per CLAUDE.md's friction protocol, a friction issue is filed only
when the tool is actually exercised and found lacking — nothing to file
here.

## What does *not* belong in this document (see `sim/README.md`)

Entropy-rate claims, spec pass/fail verdicts, and architecture
recommendations are explicitly out of scope for this document — those
belong to #10 (methodology) and #1 (spec ratification), citing the records
above as their evidentiary basis.
