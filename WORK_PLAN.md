# Work Plan

Snapshot of the GitHub label state. Operator priority does not override a
dependency block or an operator-only decision.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

- **#688**: feat(sim): store raw output of new recorded runs in the artifact store

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

_None._

## Important

`loom:important`; taken before unlabelled work.

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist
- **#654**: T1 item 5.analog: klayout-tools#2533 is fixed; emit the ratified analog rows as klt sim envelopes

## In Progress

Issues currently being built (`loom:building`).

- **#468**: Disambiguate the colliding decision-record citations (numbers 0011 and 0012) (README links the wrong record for number 0012) and guard them
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard
- **#686**: Adopt the common artifact store for sim evidence (manifests in git, bytes via klt artifact)

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

_None._

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#688**: feat(sim): store raw output of new recorded runs in the artifact store

## Proposed

Issues carrying `loom:curated`.

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist *(curated)*
- **#414**: Characterize deterministic supply-ripple sensitivity of the buffered RO array *(curated)*
- **#418**: Verify assembled combiner/sampler reset and capture with native post-layout comparison *(curated)*
- **#449**: Digital tap spacing exceeds DRM 14.3.1 MV latch-up limit (49.7 um vs 15 um): confirm and decide *(curated)*
- **#468**: Disambiguate the colliding decision-record citations (numbers 0011 and 0012) (README links the wrong record for number 0012) and guard them *(curated)*
- **#472**: Characterize asymmetric fs/sf corners on the integrated ring-array sampler path *(curated)*
- **#486**: Obtain controlled GF180MCU DRM revision for LU.3/LU.4 and confirm the digital device-class column *(curated)*
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard *(curated)*
- **#654**: T1 item 5.analog: klayout-tools#2533 is fixed; emit the ratified analog rows as klt sim envelopes *(curated)*
- **#656**: T1 item 6: produce a klt yield report over the existing mismatch Monte Carlo campaign *(curated)*
- **#686**: Adopt the common artifact store for sim evidence (manifests in git, bytes via klt artifact) *(curated)*

## Proposed (Architect / Hermit)

_None._

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 1 |
| Very important | 0 |
| Important | 1 |
| Ready (`loom:issue`) | 2 |
| In Progress (`loom:building`) | 3 |
| PRs awaiting review | 0 |
| Approved PRs awaiting merge | 1 |
| Curated | 11 |
| Architect / Hermit proposals | 0 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
