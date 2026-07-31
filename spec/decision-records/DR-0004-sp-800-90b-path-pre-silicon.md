---
dr: DR-0004-sp-800-90b-path-pre-silicon
title: Claim designed-for-SP-800-90B plus a bounded sim-stage min-entropy estimate; defer 90B validation to measured silicon
status: Proposed
date: 2026-07-30
deciders: pending — engineering (Robb) ratifies via #1
supersedes: n/a
superseded_by: n/a
related: "#6 (origin), #1 (ratification), #8, #10, #12, #13; README §Target specification — Quality row; DR-0001 (raw access), DR-0002 (health tests)"
---

# DR-0004: Claim designed-for-SP-800-90B plus a bounded sim-stage min-entropy estimate; defer 90B validation to measured silicon

## Status

- 2026-07-30: Proposed

## Context

The draft quality row reads `NIST SP 800-90B entropy validation pass`, with
`AIS-31 PTG.2` as stretch. As written it is a claim this project cannot make
and cannot currently size the work for:

- **90B validation is a process performed on a physical entropy source.** An
  entropy assessment is made from datasets collected from the *device*, and
  validation runs through a laboratory / CAVP-ESV submission. There is no path
  by which ngspice transient-noise output becomes a validated entropy claim.
  Nothing this repo produces before silicon can honestly be called a "pass".
- **The row nonetheless has to say something binding now**, because it scopes
  #10 and #12 (how much of the estimator suite the verification suite must
  attempt) and it constrains #8 (whether the conditioner must be a 90B *vetted*
  conditioning function — a decision with a large area consequence against the
  < 0.05 mm² budget).
- **#10 already establishes the honest ceiling.** Its methodology contract must
  state which statistical claims are supportable at feasible simulated bit
  counts and which are not. A quality row that demands more than #10 can
  support would force either an unsupported claim or a stalled issue.

The undiscussed cost driver is conditioning. 90B distinguishes *vetted*
conditioning functions (the cryptographic ones — CMAC/CBC-MAC, HMAC, hash and
block-cipher derivation functions) from *non-vetted* ones (everything else,
whose output entropy is credited only with a penalty factor). A vetted function
means an AES or SHA-2 core: on the order of a few thousand gate-equivalents for
the most compact serialized AES implementations, and tens of thousands for
round-based AES or SHA-2. The whole block's area budget is < 0.05 mm² in a
180 nm process — order 10⁴ µm² of routable digital area at most after the
analog core, bias, sampler, health tests, and register file take their share.
Mandating a vetted conditioner could therefore consume the majority of the area
budget for the conditioner alone. That number is an order-of-magnitude estimate
and is **not** evidence; #8 owes an actual area estimate.

(Clause numbering and the exact non-vetted output-entropy penalty should be
checked against the published SP 800-90B before ratification. This DR relies on
the vetted/non-vetted *distinction*, not on a specific constant.)

`sim/records/` is empty; no evidence is cited by this DR.

## Decision

We will split the quality row into **three tiers with different statuses**, and
claim only the first two before silicon.

### Tier 1 — Designed-for-90B (binding now, verifiable in this repo)

The architecture shall satisfy 90B's *structural* preconditions for a future
assessment. This is a design obligation, not an aspiration:

1. **Raw noise-source access** — satisfied by DR-0001 (raw tap at the sampler
   output; unconditional availability; raw streaming mode for long consecutive
   datasets).
2. **Continuous health tests on the raw stream** — RCT + APT with declared α,
   window, and cutoffs, plus a start-up test: satisfied by DR-0002.
3. **A documented entropy-source model** — a written description of the
   physical noise mechanism (RO phase jitter), the argument for why it is
   non-deterministic, the entropy-relevant nodes, and the known deterministic
   coupling risks (shared supply, injection locking between adjacent ROs).
   Owner: #7's design note plus #10's methodology document. **This is the one
   Tier-1 item with no issue currently accountable for producing it as a
   single artifact** — see Follow-up.
4. **A declared conditioning class** — see the constraint on #8 below.

Tier 1 is claimable pre-silicon because every element is a property of the
design, checkable by inspection.

### Tier 2 — Sim-stage min-entropy estimate (the pre-silicon numeric claim)

Before silicon we produce a **simulation-derived design-stage min-entropy
estimate**, not an entropy assessment. Concretely:

- **Bounded by #10.** Every estimate is produced within #10's methodology
  contract and inherits its stated claim limits. Claims outside the contract
  are not recorded as evidence.
- **Estimators.** 90B-style estimators (IID track and the non-IID suite) are
  applied **only to the extent the achievable simulated bit count supports**,
  with the confidence degradation at the achieved N stated explicitly per
  #10. Running an estimator at an unsupported N and quoting the result is a
  review-blocking defect, not a partial result.
- **Sequential dataset.** Target ≥ 10⁶ consecutive raw samples from the raw tap
  where transient-noise cost permits; otherwise report the largest achievable N
  together with what that N does and does not support. #12 owns this.
- **Restart dataset / restart test: deferred to silicon.** Its purpose —
  detecting dependence on start-up conditions across ~1000 genuinely
  independent power-on restarts — is answered far more meaningfully by measured
  silicon than by 1000 re-initialized transient-noise invocations. Its absence
  pre-silicon is **not** a spec failure. If #10's cost analysis finds it
  affordable, it may be attempted as a bonus; it is not a gate.
- **Mandatory labelling.** Every such number carries the label
  *"simulation-derived design estimate; not an SP 800-90B entropy
  assessment"* wherever it appears — evidence record, summary, spec, or
  datasheet.
- **Corner.** The headline min-entropy figure is the **worst-corner** value per
  #13 (fast / +10 % / −40 °C is the expected worst corner), not the nominal
  value — consistent with DR-0003's two-binding-corner structure and with
  DR-0002's use of worst-corner H for cutoff derivation.

### Tier 3 — 90B validation proper: deferred to measured silicon

**No SP 800-90B validation or "pass" claim is made pre-silicon, in any
document produced by this repo.** The claim attaches to the last rung of the
README maturity ladder (measured silicon over temperature), not to
simulation-complete.

### Constraint on #8 (conditioner class)

- A **vetted** 90B conditioning function is **not mandated**. Tier 3 is
  deferred, so nothing pre-silicon depends on having one, and the area cost is
  plausibly prohibitive.
- The **default assumption is a lightweight non-vetted conditioner** (von
  Neumann, XOR/parity compression, LFSR/CRC-based compression, or similar).
- **#8 must record, in its own DR**: which conditioning function it chose,
  whether it is vetted or non-vetted, the compression ratio K (feeding
  DR-0003), an **area estimate**, and — for a non-vetted function — the
  output-entropy accounting including 90B's non-vetted penalty.
- If #8's area estimate shows a vetted function *does* fit, that is a live
  option and a superseding DR to this one; it is not foreclosed, merely not
  required.

### AIS-31 PTG.2 (stretch row)

Same three-tier treatment: design so the structural requirements (raw access,
on-line tests, a documented stochastic model) are not foreclosed; make no
conformance claim pre-silicon. The stochastic model that PTG.2 requires is the
same artifact as Tier 1 item 3.

## Alternatives considered

### Keep "SP 800-90B entropy validation pass" as the target as written

- **What**: Leave the row unchanged and let downstream issues interpret it.
- **Why plausible**: It is the recognizable industry claim, it is what a
  integrator looks for, and it sets an unambiguously high bar.
- **Why rejected**: It is unachievable pre-silicon by construction, so the row
  would be permanently unmet and would give #10/#12 no scoping signal at all —
  the exact ambiguity #6 exists to remove. Worse, an unqualified row invites a
  downstream summary to quietly report a simulated estimator run as a "90B
  pass", which is precisely the failure mode CLAUDE.md's evidence rules exist
  to prevent.

### Claim only "designed-for-90B" and attempt no pre-silicon entropy numbers

- **What**: Tier 1 only; defer all min-entropy estimation to silicon.
- **Why plausible**: Maximally honest, cheapest, and removes any risk of a
  simulation number being mistaken for an assessment. Simulation cannot capture
  every real entropy contributor or detractor anyway.
- **Why rejected**: It would leave the design with no quantitative feedback
  before tape-out — sizing (#7), sampler design (#9), and the worst-corner
  analysis (#13) all need a min-entropy *number* to design against, even a
  bounded one. Shipping to a shuttle with no entropy estimate at all is a
  bigger risk than a clearly-labelled estimate.

### Attempt the full 90B estimator suite (including the restart test) in simulation

- **What**: Treat the full 90B assessment procedure as the pre-silicon target.
- **Why plausible**: It would be the closest possible dress rehearsal, and it
  would de-risk the eventual silicon submission by exercising the whole
  pipeline early.
- **Why rejected**: #10's methodology contract is expected to show that feasible
  transient-noise bit counts cannot support the full non-IID suite at
  recommended sample sizes; the restart dataset additionally requires ~1000
  independent power-on restarts. Committing to it would either blow the
  simulation budget or produce estimator outputs at unsupported N — numbers
  that look like an assessment and are not one. The calibration experiment #10
  already requires gives most of the pipeline-rehearsal benefit at a fraction
  of the cost.

### Mandate a vetted (cryptographic) conditioning function now

- **What**: Require AES-CMAC / hash-based conditioning so the block is
  submission-ready on day one of silicon.
- **Why plausible**: Removes the non-vetted entropy penalty, makes the eventual
  validation path cleaner, and is what a production-grade TRNG typically does.
- **Why rejected**: The area cost is plausibly a majority of the < 0.05 mm²
  budget, and Tier 3 is deferred anyway, so the cost buys nothing that this
  project can cash in before silicon. Deliberately left as a live option
  pending #8's area estimate rather than ruled out permanently.

## Consequences

- **Positive**:
  - #10 and #12 have a scope: bounded estimators at the achievable N, the
    sequential dataset targeted, the restart dataset explicitly out.
  - #8 is unblocked on the conditioner class and knows exactly what its own DR
    must record (function, vetted status, K, area, entropy accounting).
  - The quality row becomes a claim the project can actually meet and defend,
    which is the point of a canary block whose product is verification.
  - The mandatory labelling rule makes it structurally hard for a simulation
    number to be laundered into a certification claim in a summary or
    datasheet.
  - Nothing is foreclosed: the vetted-conditioner and full-suite paths remain
    reachable via superseding DRs if area or cost analysis changes the picture.

- **Negative / accepted cost**:
  - The quality row is weaker-sounding than "90B validation pass". That
    is the honest state of the block until silicon, and the maturity ladder
    already communicates staged claims.
  - Choosing a non-vetted conditioner means the eventual output-entropy
    accounting carries 90B's penalty factor, so more raw entropy per output bit
    is needed. This tightens the pressure on `R_raw` × H (DR-0003 §5) and on
    the compression ratio K.
  - Deferring the restart test means a start-up-dependence failure mode goes
    undetected until measured silicon.
  - Tier 1's "documented entropy-source model" currently has no single
    accountable issue.

- **Follow-up required**:
  - **File a new issue** for the consolidated entropy-source model / stochastic
    model document (Tier 1 item 3, and the PTG.2 stretch's prerequisite),
    drawing on #7's design note and #10's methodology. Not currently owned.
  - #8: record conditioning function, vetted/non-vetted status, K, area
    estimate, and non-vetted output-entropy accounting in its own DR.
  - #10: state the claim limits this DR defers to, including the affordability
    verdict on the restart dataset.
  - #12: apply the labelling rule to every reported number; report the
    worst-corner min-entropy as the headline; treat the ≥ 10⁶-sample sequential
    dataset as the target and the achieved N as a reported quantity.
  - #13: the worst-corner min-entropy identified there is the figure Tier 2
    reports.
  - README Quality row updated alongside this DR.

- **Revisit if**: #8's area estimate shows a vetted conditioning function fits
  within the area budget; #10's cost analysis shows the full estimator suite
  and/or restart dataset *is* affordable in simulation; or the block reaches
  measured silicon, at which point Tier 3 becomes live and this DR is
  superseded by one that states the actual validation path.
