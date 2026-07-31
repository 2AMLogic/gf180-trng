---
dr: DR-0002-health-test-parameters-and-failure-behavior
title: Fix RCT/APT cutoffs as formulas in H at alpha = 2^-40, and latch-and-gate on failure
status: Accepted
date: 2026-07-31
deciders: Robb Walters (engineering) — ratified via #1 (operator decision, 2026-07-31), amended at ratification per #29 (A2, A6)
supersedes: n/a
superseded_by: n/a
related: "#6 (origin), #1 (ratification), #29 (ratification amendment package — A2 degeneracy floor, A6 verification), #8, #9, #11, #12, #13; README §Target specification — Health tests row; DR-0001 (raw tap), DR-0004 (90B path), DR-0007 (entropy-source sizing that targets H₀)"
---

# DR-0002: Fix RCT/APT cutoffs as formulas in H at α = 2⁻⁴⁰, and latch-and-gate on failure

## Status

- 2026-07-30: Proposed
- 2026-07-31: **Accepted, with two amendments made at ratification** by Robb
  Walters (engineering); ratification decision recorded on #1, executed by the
  #29 amendment package. **No parameter, formula, or cutoff changed.** The
  amendments are additive:
  - **A2** — the APT degeneracy floor and its revisit trigger are stated
    explicitly (new "APT degeneracy floor" subsection under Decision, plus a
    clause in "Revisit if"). The bound was always implied by α and W; it was
    never written down, and DR-0007's context makes very low measured H a live
    possibility.
  - **A6** — the independent verification of the RCT/APT formulas and all ten
    cutoff-table rows is recorded (new "Independent verification" subsection).
    A record of a check, not a change.

## Context

The draft spec row reads `Health tests | continuous (RCT + APT) on-die`. That
names the tests and nothing else. A health test without a cutoff, a window,
and a defined failure action is not a specification — it is an intention.
#11 cannot build or fault-inject against it.

Three facts shape the choice:

1. **SP 800-90B derives both cutoffs from two inputs**: the target false-positive
   probability α, and the assumed min-entropy per sample H. The Repetition
   Count Test cutoff is `C_RCT = 1 + ceil(-log2(α) / H)`. The Adaptive
   Proportion Test cutoff is the smallest integer `C_APT` such that
   `Pr(X ≥ C_APT) ≤ α` for `X ~ Binomial(W, 2^-H)`, with window size `W`.
   (Clause numbering and the exact recommended α range should be checked
   against the published document at ratification; the formulas above are the
   basis of the numbers in this DR.)
2. **H is not known yet in this repo.** `sim/records/` is empty. Any numeric
   cutoff written today rests on an assumed H, and #12 is the issue that will
   replace the assumption with an estimate. Writing bare numbers now would
   silently bake an unsupported assumption into RTL.
3. **α must be chosen against the *sample rate*, not by habit.** The RCT is
   evaluated once per sample. At the DR-0003 raw rate target of ≥ 1 Mbps,
   α = 2⁻²⁰ gives a false alarm roughly **once per second**; α = 2⁻³⁰ gives
   one every **~18 minutes**. Neither is tolerable for a test that gates
   output. α = 2⁻⁴⁰ gives ~1.1 × 10⁶ s ≈ **12.7 days** between spurious RCT
   alarms at 1 Mbps, and ~1.1 × 10⁹ s ≈ **36 years** between spurious APT
   alarms (the APT decides once per 1024-sample window, i.e. ~977 times per
   second at 1 Mbps).

No evidence record is cited by this DR because none exists; the H₀ below is
labelled as an assumption, not a measurement.

## Decision

We will specify the health tests as **formulas parameterized by H**, with a
declared draft H₀ supplying the initial numeric values, plus an explicit
recomputation trigger.

### Test inputs and placement

- Both tests observe the **raw tap defined in DR-0001** (sampler output,
  pre-conditioning), at the **full raw sample rate, undecimated**. They do not
  observe the conditioned stream.
- Samples are **binary** (1 bit/sample), so the APT window is **W = 1024**
  (the binary-source window; W = 512 is the non-binary case and does not apply
  here).

### Parameters

| Parameter | Value | Source |
|---|---|---|
| α (both tests) | **2⁻⁴⁰** | chosen against the ≥ 1 Mbps sample rate (see Context) |
| APT window `W` | **1024** | binary source |
| `C_RCT` | `1 + ceil(40 / H)` | `-log2(α) = 40` |
| `C_APT` | smallest `C` with `Pr(X ≥ C) ≤ 2⁻⁴⁰`, `X ~ Bin(1024, 2^-H)` | — |
| Draft assumption **H₀** | **0.5 bit/sample** | **assumption — no evidence record; placeholder pending #12** |

### Initial numeric values (at H₀ = 0.5)

- **`C_RCT` = 81** — 81 identical consecutive raw samples trips the RCT.
- **`C_APT` = 824** — 824 or more occurrences of the window's reference value
  within a 1024-sample window trips the APT.

### Cutoff table (α = 2⁻⁴⁰, W = 1024) — use the row matching the ratified H

| H (bit/sample) | `C_RCT` | `C_APT` |
|---|---|---|
| 0.1 | 401 | 1005 |
| 0.2 | 201 | 961 |
| 0.3 | 135 | 915 |
| 0.4 | 101 | 869 |
| **0.5 (H₀, draft)** | **81** | **824** |
| 0.6 | 68 | 780 |
| 0.7 | 59 | 739 |
| 0.8 | 51 | 699 |
| 0.9 | 46 | 661 |
| 1.0 | 41 | 625 |

For an H not in the table, evaluate the formulas. The implementation should
make both cutoffs **parameters, not hard-coded constants**, so a change in the
ratified H is an edit to one parameter rather than a redesign.

### APT degeneracy floor: this parameterization has a hard lower bound in H

*(Added at ratification, 2026-07-31 — amendment A2 of #29. The bound follows
from the α and W already fixed above; nothing here changes a parameter.)*

The cutoff table above extends down to H = 0.1, which invites the reading that
the formulas simply keep producing looser cutoffs as H falls. **They do not.**
`C_APT` is bounded above by the window size W, so once the smallest C
satisfying `Pr(X ≥ C) ≤ α` for `X ~ Bin(W, 2^-H)` exceeds W, **no valid cutoff
exists and the APT is unsatisfiable** — it can never trip, and the block would
carry a health test that is structurally incapable of failing.

At the ratified parameters (**α = 2⁻⁴⁰, W = 1024**), by exact binomial
computation:

| H (bit/sample) | `C_APT` | Status |
|---|---|---|
| 0.10 | 1005 | valid |
| 0.08 | 1012 | valid |
| 0.06 | 1019 | valid |
| 0.05 | 1022 | valid |
| **0.04** | **1024** | **degenerate — cutoff has reached W; the test fires only on a perfectly constant window** |
| ≤ 0.03 | — | **no C ≤ W satisfies the criterion; the APT is unsatisfiable** |

So this parameterization is only meaningful for **H ≳ 0.05**, and is
*unusable* at **H ≤ 0.03**. The RCT does not degenerate the same way
(`C_RCT = 1 + ⌈40/H⌉` simply grows — 1334 at H = 0.03 — costing detection
latency and counter width, not validity), so a low-H failure shows up first
and only in the APT.

**Why this matters now, and not only in theory.** DR-0007 records that a single
ring oscillator at the DR-0003 target rate supports a `Q` some 220–370× below
the value `H = 0.5` requires; if the entropy source is under-sized against
DR-0007's sizing law, worst-corner H at 1 Mbps plausibly lands in the
10⁻³–10⁻² range — **inside the degenerate region**, where the block's entire
health-test safety story silently evaporates rather than failing loudly.

**The fix at low H is structural, not a parameter edit.** If #12/#13 report a
worst-corner H below ~0.05, the response is *not* to read a lower row off the
table. The available structural moves are:

1. **Decimate ahead of the tests** — feed the tests one bit per k raw samples
   (or one XOR/parity of k raw samples), raising the per-tested-sample H by
   roughly k× at the cost of k× detection latency. This changes what the tests
   observe, which touches DR-0001's "tests observe the raw tap, undecimated".
2. **Change W** — a larger APT window admits a valid cutoff at lower H, at
   proportionally worse detection latency (the 2×W bound below) and more
   counter state.
3. **Change α** — a larger α restores a valid cutoff but re-opens the
   false-alarm-rate argument in Context, which was the reason α = 2⁻⁴⁰ was
   chosen against the ≥ 1 Mbps sample rate in the first place.
4. **Fix the source** — raise H at the entropy source (DR-0007's N), which is
   the preferred route and the reason DR-0007 states a sizing law rather than
   a ring count.

Any of 1–3 is a **superseding DR**, not an edit to this one.

### Independent verification of the cutoffs (record of a check, no change)

*(Added at ratification, 2026-07-31 — amendment A6 of #29.)*

The formulas and every numeric cutoff in this record were independently
reproduced against SP 800-90B §4.4.1/§4.4.2 by exact binomial computation, at
two separate times: by the #29 spec review, and again while landing this
amendment. Both reproductions agree exactly with the table above.

- **RCT**: `C = 1 + ⌈−log₂α / H⌉` gives `1 + ⌈40/0.5⌉ = 81` at H₀, and all ten
  table rows reproduce (401, 201, 135, 101, 81, 68, 59, 51, 46, 41).
- **APT**: this record's criterion (smallest `C` with `Pr(X ≥ C) ≤ α` for
  `X ~ Bin(1024, 2^-H)`) is equivalent to 90B's
  `1 + CRITBINOM(W, 2^-H, 1-α)`. At H₀ = 0.5 it yields `C_APT = 824`, with
  `Pr(X ≥ 824) = 6.44×10⁻¹³ ≤ α = 2⁻⁴⁰ = 9.09×10⁻¹³` and
  `Pr(X ≥ 823) = 1.10×10⁻¹² > α` — i.e. 824 is the *smallest* satisfying
  cutoff, not merely *a* satisfying one. All ten table rows reproduce (1005,
  961, 915, 869, 824, 780, 739, 699, 661, 625).
- **W = 1024** is confirmed as the binary-source window (W = 512 is the
  non-binary case).
- The **false-alarm-interval arithmetic** in Context (≈12.7 days between
  spurious RCT alarms and ≈36 years between spurious APT alarms at 1 Mbps) and
  the **2 × W detection-latency bound** for non-overlapping APT windows both
  check out as stated.

This subsection exists so the check is on the record and does not have to be
re-derived by the next reader; it asserts nothing new.

### Which H to use

Cutoffs are derived from the **worst-corner H** identified by #13 — the lowest
min-entropy per sample across the PVT grid — **not** the nominal-corner H.
Deriving from nominal would make the cutoffs too tight at the fast/high-V/cold
corner, producing nuisance alarms exactly where the source is weakest. Using
the worst-corner (lowest) H loosens the cutoffs, which costs sensitivity but
guarantees the designed α holds at every corner.

### Failure behavior

Both **flag and gate**, latching:

1. **Flag.** An RCT or APT failure sets a sticky status bit
   (`HT_FAIL_RCT` / `HT_FAIL_APT`) and asserts a block-level `HT_ALARM` output.
   These are **latching**: they stay set until explicitly cleared by a
   write-1-to-clear from software.
2. **Gate — conditioned path only.** On failure the conditioned output path is
   gated immediately: the streaming port deasserts valid, `DATA` reads return
   no new bits, and **the output FIFO is flushed** so no bit produced under the
   failing window can be read afterward.
3. **Raw path is not gated** (DR-0001) — `RAW_DATA` and `OUT_MODE = raw`
   continue to work so a failure can be diagnosed rather than merely observed.
4. **Recovery is explicit, never automatic.** Clearing the latched flag
   restarts the noise source and runs the **start-up health test** — RCT and
   APT over **1024 consecutive raw samples** — and the conditioned path stays
   gated until that start-up test passes. The same start-up test runs at
   power-on before the conditioned path is ever ungated.

Self-clearing gating is explicitly rejected (see Alternatives): a marginal
source would flap in and out of gating and deliver bits from a source that
just failed, with no record that it did.

### Detection-latency targets (acceptance for #11's fault injection)

- **Stuck output** (constant raw bit): detected within `C_RCT` samples of onset
  — 81 samples at H₀.
- **Heavily biased stream / injection-locked source**: detected within at most
  **2 × W = 2048 samples** of onset, since the bias may begin mid-window and
  the first straddling window can fall below cutoff.
- **False-positive rate on a healthy simulated stream**: consistent with
  α = 2⁻⁴⁰, i.e. *no* alarm is expected over any feasible simulated bit count.
  #11 therefore verifies α indirectly — by driving a synthetic stream at a
  deliberately inflated α (or a deliberately reduced cutoff) and checking the
  observed alarm rate matches the binomial prediction — rather than by trying
  to observe a 2⁻⁴⁰ event.

## Alternatives considered

### Bare numeric cutoffs, no formula

- **What**: Publish `C_RCT = 81`, `C_APT = 824` and stop.
- **Why plausible**: Simplest thing to implement; #11 could start immediately;
  the numbers are what actually gets synthesized anyway.
- **Why rejected**: They rest entirely on an unmeasured H₀ = 0.5. When #12
  lands a real estimate, a bare number gives no way to tell whether the
  implemented cutoff is still correct, and no way to recompute it without
  re-deriving the whole thing. The formula plus the table costs nothing and
  makes the dependency on H explicit and auditable.

### Defer health-test parameters entirely until #12 measures H

- **What**: Leave the row as "RCT + APT" and revisit after min-entropy
  estimation.
- **Why plausible**: Avoids committing to a number that is likely to change,
  and #12's estimate is the honest input.
- **Why rejected**: #11 is blocked on this decision *now*, and #12 is
  downstream of #9 which is downstream of this interface work — deferring
  would stall the health-test path behind almost the entire verification
  chain. More importantly, the *structure* (which stream, which window, what
  happens on failure) does not depend on H at all and can be fixed today.

### α = 2⁻²⁰ (the commonly quoted default)

- **What**: Use the low end of the recommended α range.
- **Why plausible**: Most sensitive to real failures; the value most often
  seen in worked examples.
- **Why rejected**: At ≥ 1 Mbps the RCT is evaluated ≥ 10⁶ times per second, so
  α = 2⁻²⁰ produces a spurious alarm about every second. With latching gating,
  the block would be permanently gated within seconds of power-on. The
  sensitivity loss at 2⁻⁴⁰ is modest (`C_RCT` 41 → 81 at H = 0.5); the
  usability difference is total.

### Flag only, never gate

- **What**: Report failures; let the consumer decide whether to keep reading.
- **Why plausible**: Never denies service; a system integrator may have a
  better policy than we do; simpler hardware.
- **Why rejected**: It moves the one safety property the health tests exist to
  provide (do not hand out bits from a failed noise source) into every
  integrator's firmware, where it will sometimes be omitted. The raw path
  (ungated) already preserves the "let me see it anyway" escape hatch for the
  cases where the integrator genuinely wants the failing stream.

### Gate but self-clear when the source recovers

- **What**: Ungate automatically as soon as a subsequent window passes.
- **Why plausible**: No software involvement; transient glitches self-heal;
  higher availability.
- **Why rejected**: A marginal source (e.g. one drifting toward
  injection-locking at a temperature extreme) would oscillate between gated and
  ungated, delivering bits between failures with nothing durable to indicate
  it happened. Latching converts an intermittent failure into a recorded,
  unmissable event — which is also what makes #11's detection-latency
  measurement deterministic.

## Consequences

- **Positive**:
  - #11 can implement and fault-inject immediately: input stream, window,
    cutoffs, failure semantics, and latency targets are all fixed.
  - The cutoffs' dependence on H is explicit, so #12's estimate feeds a
    parameter change rather than a redesign.
  - Deriving from the worst-corner H means the designed α holds across the
    whole PVT grid, not just at nominal — this is what makes the health-test
    row honest against #13.
  - Latching + flush means "a bit that was readable was produced under a
    passing window" is a hardware property #11 can test directly.

- **Negative / accepted cost**:
  - α = 2⁻⁴⁰ trades sensitivity for usability; slow, mild degradation of the
    source will be detected later (or not at all) compared to α = 2⁻²⁰. The
    residual risk is carried by #12/#13's characterization, not by the on-die
    tests.
  - Worst-corner-derived cutoffs are looser than they need to be at nominal,
    so the on-die tests are least sensitive exactly at the typical corner.
  - Latching gating means a single spurious event requires software
    intervention to recover. Accepted: at α = 2⁻⁴⁰ the expected interval is
    ~12.7 days at 1 Mbps, and the alternative is silent flapping.
  - **H₀ = 0.5 is an assumption with no evidence behind it.** Every number in
    the "initial numeric values" section inherits that status until #12 lands.

- **Follow-up required**:
  - #11: implement with `C_RCT`/`C_APT`/`W`/α as parameters; verify the
    detection-latency targets above; verify gate-and-flush and the start-up
    test.
  - #12: report the worst-corner min-entropy estimate (with its confidence
    treatment per #10) in a form directly usable as the H in these formulas —
    i.e. report the **lower bound** intended for cutoff derivation, explicitly.
  - #13: the worst-corner identification is an input to this DR, not just to
    the quality row.
  - #8: the conditioner sits behind the gate; its FIFO is what gets flushed.
  - README Health tests row updated alongside this DR.

- **Revisit if**: #12's worst-corner H lower bound differs from H₀ = 0.5 enough
  to change `C_RCT` or `C_APT` (per the table above, any change of ±0.1
  bit/sample does), **or** the ratified raw rate in DR-0003 changes by enough
  to alter the α-versus-false-alarm-interval argument, **or** the sample width
  ceases to be binary (which would change W), **or — the degeneracy trigger
  added at ratification — any measured or projected worst-corner H falls below
  ~0.05**, at which point the APT is approaching (and by H ≤ 0.03 has passed)
  the point where no valid cutoff exists and the structural response in "APT
  degeneracy floor" above is required. Any of these produces a superseding DR;
  this one is not edited.
