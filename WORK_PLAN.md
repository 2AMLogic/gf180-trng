# Work Plan

Snapshot of the GitHub label state. Operator priority does not override a
dependency block or an operator-only decision.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

- **#433**: Give the strict record-checksum CI step an npm check entry and parity coverage
- **#646**: ci(nightly): pin yowasp-yosys to 0.69.0.0.post1233

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

_None._

## Important

`loom:important`; taken before unlabelled work.

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist
- **#468**: Disambiguate the colliding DR-0011/DR-0012 citations (README links the wrong DR-0012) and guard them
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard

## In Progress

Issues currently being built (`loom:building`).

- **#630**: PDK nightly red: Yosys 0.70 (yowasp-yosys, unpinned) makes trng_top.synth.{v,json} STALE

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

_None._

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#433**: Give the strict record-checksum CI step an npm check entry and parity coverage
- **#646**: ci(nightly): pin yowasp-yosys to 0.69.0.0.post1233

## Proposed

Issues carrying `loom:curated`.

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist *(curated)*
- **#414**: Characterize deterministic supply-ripple sensitivity of the buffered RO array *(curated)*
- **#418**: Verify assembled combiner/sampler reset and capture with native post-layout comparison *(curated)*
- **#432**: Give the strict record-checksum CI step an npm check entry and parity coverage *(curated)*
- **#449**: Digital tap spacing exceeds DRM 14.3.1 MV latch-up limit (49.7 um vs 15 um): confirm and decide *(curated)*
- **#468**: Disambiguate the colliding DR-0011/DR-0012 citations (README links the wrong DR-0012) and guard them *(curated)*
- **#472**: Characterize asymmetric fs/sf corners on the integrated ring-array sampler path *(curated)*
- **#486**: Obtain controlled GF180MCU DRM revision for LU.3/LU.4 and confirm the digital device-class column *(curated)*
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard *(curated)*
- **#630**: PDK nightly red: Yosys 0.70 (yowasp-yosys, unpinned) makes trng_top.synth.{v,json} STALE *(curated)*

## Proposed (Architect / Hermit)

_None._

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 2 |
| Very important | 0 |
| Important | 1 |
| Ready (`loom:issue`) | 3 |
| In Progress (`loom:building`) | 1 |
| PRs awaiting review | 0 |
| Approved PRs awaiting merge | 2 |
| Curated | 10 |
| Architect / Hermit proposals | 0 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
