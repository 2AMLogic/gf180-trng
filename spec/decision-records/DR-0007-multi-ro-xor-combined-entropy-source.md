---
dr: DR-0007-multi-ro-xor-combined-entropy-source
title: Build the entropy source as an N-way array of independent ring oscillators XOR-combined ahead of one sampler, with N fixed by a stated jitter-budget sizing law
status: Accepted
date: 2026-07-31
deciders: Robb Walters (engineering) — ratified via #1 (operator decision, 2026-07-31), amendment A1 of the #29 package
supersedes: n/a
superseded_by: n/a
related: "#29 (origin — amendment A1), #1 (ratification), #7 (consumer: RO core schematic), #9 (sampler clock source), #12, #13, #16, #32 (power/leakage characterization); spec/entropy-architecture-survey.md §Recommendation 1; sim/characterization-ro-delay-cell-jitter.md; DR-0002 (health-test H), DR-0003 (raw rate), DR-0004 (quality tiers), DR-0006 (PVT/seed coverage); README §Target specification — Entropy source row"
---

# DR-0007: Build the entropy source as an N-way array of independent ring oscillators XOR-combined ahead of one sampler, with N fixed by a stated jitter-budget sizing law

## Status

- 2026-07-31: Accepted (ratified with DR-0001…DR-0004 via #1; this record is
  amendment A1 of the #29 review package, which is the item that required a
  live architectural decision rather than transcription).

## Context

The README's `Entropy source` row has read `ring-oscillator jitter |
metastability hybrid` since the DRAFT was first filed. It is the only spec row
that names no architecture beyond a mechanism, and — unlike the four rows
clarified by DR-0001…DR-0004 — it was never tied to a decision record. The
architecture survey ([`spec/entropy-architecture-survey.md`](../entropy-architecture-survey.md)
§Recommendation 1) already recommends **multi-RO, XOR-combined** jitter as the
primary source, over a single free-running RO, on injection-locking grounds
[Sunar/Martin/Stinson 2007; Markettos & Moore 2009]. That recommendation had
no DR, so nothing bound #7 to it.

The #29 spec review turned that documentation gap into a **load-bearing**
one by checking the draft's rate × entropy operating point against this
repository's own measured jitter, and finding they do not meet.

### The measured gap

Baudet et al. (CHES 2011) bound the min-entropy per sampled bit of a
jitter-sampled ring oscillator as

```
H ≥ 1 − (4 / (π² ln 2)) · exp(−4π² Q),      Q = σ²_acc(T_s) / T₀²
```

where `T₀` is the RO period, `T_s` the sample period, and `σ_acc(T_s)` the
jitter accumulated over one sample interval. Under white-noise (random-walk)
accumulation, `σ²_acc(T_s) = σ₁² · (T_s / T₀)`, so for a single ring

```
Q = σ₁² · T_s / T₀³
```

Setting `H = 0.5` — the draft `H₀` that DR-0002's cutoffs are derived from —
requires **`Q ≈ 3.96 × 10⁻³`** (call it `Q_H₀ = 4.0 × 10⁻³`).

Evaluated at `T_s = 1 µs` (the DR-0003 raw-rate target of 1 Mbps) against the
physically-scaled flagship measurements in
[`sim/characterization-ro-delay-cell-jitter.md`](../../sim/characterization-ro-delay-cell-jitter.md)
(candidate A, 5-stage; each row's raw σ₁ from
`sim/records/2026-07-31-ro-inv-05stage-jitter-NN.md`, scaled by the per-corner
device-noise ratio from `sim/records/2026-07-31-inv-stage-noise-NN.md`):

| Corner | record `NN` | `T₀` (s) | scaled `σ₁` (s) | `Q` at 1 Mbps | rate supporting `H = 0.5` |
|---|---|---|---|---|---|
| `ss`/−40 °C/3.63 V (measured minimum `Q`) | 21 | 6.123e-10 | 4.973e-14 | **1.08e-05** | ~2.7 kbps |
| `ff`/−40 °C/3.63 V | 12 | 4.342e-10 | 3.677e-14 | 1.65e-05 | ~4.2 kbps |
| `ss`/125 °C/2.97 V | 25 | 9.724e-10 | 1.282e-13 | 1.79e-05 | ~4.5 kbps |
| `tt`/27 °C/3.30 V (nominal) | 05 | 6.213e-10 | 6.592e-14 | 1.81e-05 | ~4.6 kbps |

(The `Q` and rate columns are computed here from those records' figures; they
are derived quantities, not measured ones, and inherit the characterization's
stated ~1.5–2× accuracy on σ — ~2–4× on `Q`.)

A **single** candidate-A 5-stage ring therefore supports `H ≈ 0.5` at roughly
**3–5 kbps**, not 1 Mbps — a shortfall of ~220–370× in `Q` at the target rate.
That is far outside the characterization's own stated accuracy (a factor of
~1.5–2× on σ, i.e. ~2–4× on `Q`). Candidate B (current-starved) does not close
it either: its higher relative jitter is largely cancelled by its ~2× longer
period in the `1/T₀³` term, leaving `Q` within ~1.1× of candidate A at matched
corners.

No spec row ever *claimed* `H = 0.5` — `H₀` is labelled an assumption
everywhere it appears — but ratifying the draft unchanged would have carried
`H₀ = 0.5` into #11's RTL cutoffs while the repository's own measurements
contradicted it at the target rate.

### The decision that was open

The review left three ratifiable resolutions: (a) make the entropy source an
explicitly multi-RO XOR-combined array sized so the gap closes, (b) re-label
`H₀` as "expected ≪ 0.5 at 1 Mbps single-RO, re-derived by #12", or
(c) lower the raw-rate target. The operator chose **(a)** (#29, 2026-07-31):
the gap closes architecturally, the 1 Mbps × `H₀ = 0.5` operating point
stands.

## Decision

We will build the entropy source as an **N-way array of independently-supplied,
free-running ring oscillators of a common cell design but deliberately skewed
frequencies, combined by XOR into a single node that feeds one sampler**, and we
fix the sizing rule that sets N.

### 1. Topology (binding on #7)

- **N free-running ring oscillators**, no phase-locking of any kind between
  them, deliberately **non-integer nominal frequency ratios** (achieved by
  per-ring stage-count and/or drive-strength skew), each with its **own supply
  routing** back to the block's supply, per the survey's §A.4 injection-locking
  argument.
- **XOR-combined ahead of the sampler.** The combination is a balanced XOR
  tree over the N ring outputs; the tree's output is the single node the
  sampler observes. Sampling one XOR node, rather than N samplers plus a
  digital combine, is what keeps the raw tap of DR-0001 a single, well-defined
  one-bit-per-sample node.
- **DR-0001 is unchanged**: the raw tap stays at the **sampler output** — after
  the XOR, after digitization, before all post-processing. The XOR tree is part
  of the noise source, not post-processing, and no per-ring signal is exposed
  as a raw tap.
- The **metastability hybrid remains a stretch item**, and stays scoped as the
  survey scoped it (§Recommendation 2): a secondary tap layered onto this RO
  core, never a free-standing source. This DR neither adds nor removes it.

### 2. Sizing law (binding — this is the durable part of this DR)

For an array of N rings sampled with period `T_s`, the array's jitter budget is
the **sum of the per-ring normalized phase variances**:

```
Q_array(T_s) = Σ_{i=1..N} σ²_acc,i(T_s) / T₀,i²        (independent rings)
```

and the array **shall be sized so that, at the entropy-binding corner,**

```
Q_array(T_s) ≥ M · Q_H₀ ,   Q_H₀ = 4.0 × 10⁻³ (H = 0.5),   M = 1.5
```

For an array of one cell design (the frequency skew of §1 is small enough that
the rings share a `Q₁` to well inside the measurement accuracy) this reduces to
`N ≥ M · Q_H₀ / Q₁`, with `Q₁ = σ₁² · T_s / T₀³` the per-ring figure at that
corner. If #7 mixes materially different ring designs, the sum form above
governs and the per-design `Q_i` must be reported separately. `M = 1.5` is
declared design margin on the *model*, and is deliberately **not** sized to
cover the characterization's 2–4× uncertainty on `Q` itself — that uncertainty
is carried as a named risk, closed by #12/#13, not hidden inside a margin
factor.

Two properties of this law are load-bearing and must not be quietly dropped:

- **It credits no XOR "piling-up" bonus.** The classical piling-up-lemma
  argument (bias multiplies, so a handful of rings suffice) relies on a
  first-harmonic truncation of the phase distribution that is invalid in
  precisely this regime — at `Q ~ 10⁻⁵` a single sampled ring bit is nearly
  deterministic and its bias approaches ½, so the "bonus" is an artifact of
  the approximation, not physics. Summing variances is the conservative
  reading and is the one this DR adopts.
- **It credits no flicker/low-frequency accumulation.** `σ_acc(T_s)` above is
  extrapolated from a measured *32-period* white-noise window (≈20 ns) out to
  a 1 µs sample interval by √t. At 1 µs — some ~1600 RO periods — long-term
  jitter in a real ring is normally 1/f-dominated and accumulates faster than
  √t. The repo's own flicker testbench could not resolve the 1/f contribution
  at 4 seeds and a 32-period window (`sim/records/2026-07-31-ro-inv-05stage-flicker-{01,02,03}.md`),
  so it is excluded rather than assumed. **Consequently the measured `Q₁` is a
  lower bound on the physical `Q₁`, and every N below is an upper bound on the
  N actually required.**

### 3. First-cut N from today's evidence (indicative, not frozen)

Against the measured minimum-`Q` corner of the flagship config
(`Q₁ = 1.08 × 10⁻⁵`, `ss`/−40 °C/3.63 V, `T_s = 1 µs`):

```
N ≥ 1.5 × 4.0e-3 / 1.08e-5 = 552   →   first-cut  N₀ = 560
```

`N₀ = 560` is what today's white-noise-only evidence demands of a 5-stage
candidate-A ring, and it is recorded here so the number is on the record
rather than reinvented. It is **not** frozen as the built N.

This **supersedes the architecture survey's "a small number (single digits)"
of rings** (§Recommendation 1) *on the count only* — that figure was a
literature-informed plausibility estimate written before this repository had
any measured jitter, and #4's characterization has since replaced the estimate
with data. The survey's *topology* recommendation (independent, non-integer-
ratio, XOR-combined, separately supplied) is adopted unchanged and is what §1
above makes binding.

Two measured levers move N, and #7 owns exercising them:

- **Shorter rings.** `Q ∝ σ₁²/T₀³ ∝ 1/n_stages²` for a fixed delay cell, and
  the measured 3-stage candidate-A points confirm it: `Q` is **3.2–4.0×**
  higher than the 5-stage ring at the three matched headline corners
  (`sim/records/2026-07-31-ro-inv-03stage-jitter-*.md`). That alone puts N in
  the ~140–175 range — but the 3-stage config has only 3 PVT points, not a
  full grid (DR-0006), so its minimum-`Q` corner is unmeasured and it cannot
  be sized against until that grid exists.
- **Resolving the flicker contribution** (see §2) — the single largest source
  of conservatism in `N₀`.

### 4. Entropy-binding corner (corrects the polarity error of amendment A3)

The corner this array is sized at is the **measured minimum-`Q` corner**, which
is the corner where entropy per bit is *worst*. State it as:

> **measured minimum-`Q` corner — expected cold / +10 % supply; process letter
> TBD by #13.**

- Do **not** size entropy margin at the largest-relative-jitter corner
  (`ss`/125 °C/2.97 V). That corner has the *most* scaled `σ₁/T₀`, but also the
  longest period, so it accumulates the fewest RO periods per sample; its
  measured `Q` (1.79e-05) is among the **highest** in the grid, i.e. it is the
  entropy-**best** corner, not the worst. `sim/characterization-ro-delay-cell-jitter.md`
  said the opposite until #29 corrected it; DR-0003 §4 and DR-0004 had it
  right in direction.
- **The metric depends on the sampler clock source, which #9 has not yet
  pinned.** With a **fixed** sample clock, the per-sample figure is
  `Q ∝ σ₁²/T₀³` and the measured minimum is `ss`/−40 °C/3.63 V — about 1.5×
  worse than `ff`/−40 °C/3.63 V. With a sample clock **divided from the RO
  itself**, the accumulated-period count is fixed and the metric collapses to
  `σ₁/T₀`, under which `ss`/−40 °C/3.63 V and `ff`/−40 °C/3.63 V are within
  4 % — unresolvable at 4 seeds. Either way the **cold / +10 %-supply** region
  binds; only the process letter is unsettled.
- `fs`/`sf` are **uncovered** (DR-0006), so no minimum-`Q` claim is made over
  those corners.

### 5. What this DR does not change

- **DR-0003's raw-rate row is unchanged**: > 1 Mbps sustained at the raw tap,
  binding at `ss`/−10 %/+125 °C. Rate and entropy still bind at opposite
  corners.
- **DR-0002's `H₀ = 0.5`, α = 2⁻⁴⁰, W = 1024 and cutoff formulas are
  unchanged.** This DR is what makes `H₀ = 0.5` an *architectural target the
  design is sized to hit* rather than an unbacked assumption — but it stays an
  assumption until #12 measures it. DR-0002's APT degeneracy floor (no valid
  cutoff at `H ≤ 0.03`) is the failure mode of under-sizing this array.
- **DR-0004's tiering is unchanged**: nothing here is an entropy assessment,
  and the array's `H` remains a simulation-derived design estimate carrying
  DR-0004's mandatory label.

### 6. Obligations this creates (binding on downstream issues)

- **#7** sizes the array: picks the per-ring topology and stage count, fixes N
  against §2 using the best available `Q₁`, and reports the resulting
  `Q_array` at the entropy-binding corner. #7 may not close on an N without
  showing the §2 inequality holds at that corner.
- **#7 / #16** own the independence argument. The sizing law is a sum over
  **independent** rings; mutual injection locking between array members
  collapses it silently (the array degenerates toward one ring while the bit
  stream still looks plausible). Non-integer frequency ratios, per-ring supply
  routing, and floorplan separation are requirements, not preferences.
- **#9** pins the sampler clock source, which selects the corner metric in §4.
- **#12** reports `H` for the *array* (not a single ring), reports the measured
  `σ_acc(T_s)` at the actual sample interval rather than a √t extrapolation
  from a 32-period window, and reports an empirical independence check across
  array members.
- **#13** identifies the minimum-`Q` corner over the covered grid and names the
  process letter §4 leaves TBD.

## Alternatives considered

### Single free-running RO, with `H₀` re-labelled as "expected ≪ 0.5 at 1 Mbps"

- **What**: Keep one ring; keep 1 Mbps; state in the spec that raw min-entropy
  per bit is expected to be far below 0.5 and will be re-derived by #12.
- **Why plausible**: Zero design cost, immediately honest, and arguably the
  most evidence-faithful option — it changes only what the spec *claims*, not
  what the block is. The conditioner (#8) could then be sized to recover
  entropy density from a low-`H` raw stream.
- **Why rejected**: At the `Q` the measurements imply, worst-corner `H` at
  1 Mbps plausibly lands in the 10⁻³–10⁻² range — **below DR-0002's APT
  degeneracy floor** (`α = 2⁻⁴⁰`, `W = 1024` admits no valid cutoff at
  `H ≤ 0.03`). The health-test parameterization the block's safety story rests
  on would degenerate, and the fix at that point is structural (α/W change or
  decimation ahead of the tests), not a parameter edit. It also leaves the
  single-RO injection-locking exposure the survey specifically recommends
  against. Operator decision (#29, A1): close the gap architecturally.

### Lower the raw-rate target until a single RO supports `H = 0.5`

- **What**: Move the DR-0003 row from > 1 Mbps to ~3–5 kbps.
- **Why plausible**: It is the one option that needs no new hardware and no new
  evidence — the measurements already support it exactly as they stand, and it
  would make every existing row self-consistent today.
- **Why rejected**: Operator decision (#29, A1) — the rate target stays.
  A ~kbps TRNG is a materially different product claim, and the rate row is
  also the row with the most downstream consumers (#8's K, #11's α-vs-false-
  alarm arithmetic, the time-to-first-valid row). Kept explicitly live as the
  superseding path if the power collision below proves unresolvable.

### Time-interleave N independent RO+sampler channels instead of XOR-combining

- **What**: N channels each sampled at `R/N`, outputs concatenated to reach R.
- **Why plausible**: Each channel accumulates N× more jitter per sample, so
  per-channel `Q` rises linearly — the same arithmetic as the XOR array, with
  no XOR tree and with per-channel observability.
- **Why rejected**: Identical N for identical entropy (total jitter budget is
  conserved either way), but it multiplies the sampler and the raw tap by N —
  directly against DR-0001's single, unambiguous one-bit-per-sample tap — and
  it gives an attacker N separately-observable, individually-weak streams. The
  XOR array buys, for the same ring count, the injection-locking resilience the
  survey documents.

### Accept the piling-up-lemma reading and build a handful of rings

- **What**: Treat the XOR of N biased bits via the piling-up lemma
  (`ε_XOR = 2^{N−1} Πε_i`), under which `N = 2` already yields `H > 0.5` even
  at the measured `Q`.
- **Why plausible**: It is a standard, correct lemma, it is cited in the
  RO-TRNG literature, and it would make the whole gap evaporate for two
  rings' worth of area and power.
- **Why rejected**: Its inputs are not valid here. The per-ring bias it
  requires comes from a first-harmonic truncation of the wrapped phase
  distribution that only holds at large `Q`; at `Q ~ 10⁻⁵` the true bias
  approaches ½ (the bit is nearly deterministic given the sampling phase) and
  the product telescopes to ≈½, not to zero. Adopting it would let the block
  claim `H = 0.5` from two rings on the strength of an approximation used
  outside its domain — the exact failure mode this repo's evidence rules
  exist to prevent.

### Metastability-based source as the primary (not stretch) architecture

- **What**: Promote the metastability hybrid to primary, sidestepping the
  jitter-accumulation budget entirely.
- **Why plausible**: Metastable resolution is not rate-limited by accumulated
  phase noise the way jitter sampling is, so the rate × entropy tension does
  not arise in the same form.
- **Why rejected**: The survey rejected it as a free-standing source on
  simulation-substantiability grounds (full resolution-time histograms are not
  credibly reproducible in ngspice at the run lengths this project can afford)
  and on PVT balance-point-drift/calibration grounds — none of which #29's
  review changes. It stays where the survey put it: a secondary tap on the RO
  core.

## Consequences

- **Positive**:
  - The entropy-source row is finally tied to a citable DR, closing the gap
    #1's curator note flagged, and #7 has a binding topology instead of a
    mechanism name.
  - The rate × entropy operating point is now *checkable*: §2 is an inequality
    a reviewer can evaluate against evidence records, rather than an
    assumption. Under-sizing becomes a visible spec violation instead of a
    silent entropy shortfall.
  - The survey's injection-locking recommendation becomes a requirement with
    named owners (#7, #16) rather than advice.
  - The entropy-binding corner is stated once, correctly, with its dependence
    on the (still-open) sampler clock source explicit — and the
    characterization document's inverted guidance is corrected rather than
    propagated.

- **Negative / accepted cost**:
  - **The first-cut N collides hard with the Power row, and this DR does not
    resolve it.** Order-of-magnitude only (no evidence record exists — see
    Follow-up): a 5-stage ring at the measured ~1.6 GHz nominal draws
    `n · C_node · V² · f ≈ 5 × 5 fF × (3.3 V)² × 1.6 GHz ≈ 0.4 mW`, so
    `N₀ = 560` projects ~250 mW — roughly 500× the `< 500 µW` active row. Even
    the 3-stage variant at N ≈ 170 projects tens of mW. **As of ratification
    the §2 sizing law and the Power row are not simultaneously satisfiable on
    the white-noise-only evidence available.** That is recorded as a live,
    tracked conflict, not resolved by adjusting either number to fit.
  - Area follows the same pressure: hundreds of rings plus an XOR tree against
    a `< 0.05 mm²` budget that also has to hold the sampler, health tests,
    conditioner and register file.
  - N rings switching at GHz rates on a shared supply is itself a coupling
    risk — the mechanism the array exists to defend against, re-introduced
    internally at scale. #16's isolation work grows accordingly.
  - The XOR tree adds skew and a combinational depth in front of the sampler,
    and a stuck/dead ring is invisible at the XOR node (it contributes a
    constant); per-ring liveness observability is now a design question #7
    inherits.

- **Follow-up required**:
  - **#32 (filed alongside this DR): supply-current and leakage
    characterization** — no power or leakage measurement of any kind exists in
    `sim/`. It must produce per-ring active current at the `ff`/+10 % corner
    and block leakage at `ff`/+10 %/+125 °C, and project the N-ring array total
    against the Power row. Until it lands, every power figure in this DR is an
    order-of-magnitude estimate and is explicitly not evidence.
  - **#7**: fix N per §2; report `Q_array` at the entropy-binding corner;
    resolve the per-ring topology/stage-count trade (a full-grid
    characterization of any ring config it wants to size against is a
    prerequisite, per DR-0006); address per-ring liveness observability.
  - **#12/#13**: measure `σ_acc(T_s)` at the actual sample interval instead of
    √t-extrapolating a 32-period window — the single biggest lever on N — and
    identify the minimum-`Q` corner and its process letter.
  - **#9**: pin the sampler clock source (§4).
  - **#16**: array-scale isolation — inter-ring locking, shared-supply
    coupling, and the guard-ring/floorplan consequences of N rings.
  - README `Entropy source` row updated to cite this DR (done alongside it).

- **Revisit if**: #12/#13's measured `σ_acc(T_s)` (with flicker resolved)
  changes `Q₁` enough to move N by more than the `M = 1.5` margin; or #7's
  array power/area projection, informed by the new characterization issue,
  shows the §2-compliant N cannot fit the Power/Area rows — in which case the
  superseding DR trades raw rate or entropy-per-raw-bit (with the conditioner
  recovering entropy density per DR-0004), and says so explicitly rather than
  silently under-sizing the array; or #9's sampler-clock decision changes the
  corner metric enough to move the entropy-binding corner off the cold/+10 %
  region.
