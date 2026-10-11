# Work Plan

Snapshot of the GitHub label state. Operator priority does not override a
dependency block or an operator-only decision.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs stuck under a `loom:operator` merge-risk hold — implementation work is done, only a human merge decision is missing.

- **#433**: Give the strict record-checksum CI step an npm check entry and parity coverage
- **#586**: feat(spec): move the Raw rate row to 2 kbps and size the array at a = 7.32

## Operator Priority

Issues the operator starred (`loom:operator-priority`); land these first.

_None._

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist
- **#468**: Disambiguate the colliding DR-0011/DR-0012 citations (README links the wrong DR-0012) and guard them
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard

## In Progress

Issues currently being built (`loom:building`).

- **#486**: Obtain controlled GF180MCU DRM revision for LU.3/LU.4 and confirm the digital device-class column
- **#553**: Replace 24 hand-copied path-based module loaders with one helper

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

_None._

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#433**: Give the strict record-checksum CI step an npm check entry and parity coverage
- **#586**: feat(spec): move the Raw rate row to 2 kbps and size the array at a = 7.32

## Proposed

Issues carrying `loom:curated`.

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist *(curated)*
- **#418**: Verify assembled combiner/sampler reset and capture with native post-layout comparison *(curated)*
- **#432**: Give the strict record-checksum CI step an npm check entry and parity coverage *(curated)*
- **#449**: Digital tap spacing exceeds DRM 14.3.1 MV latch-up limit (49.7 um vs 15 um): confirm and decide *(curated)*
- **#468**: Disambiguate the colliding DR-0011/DR-0012 citations (README links the wrong DR-0012) and guard them *(curated)*
- **#472**: Characterize asymmetric fs/sf corners on the integrated ring-array sampler path *(curated)*
- **#486**: Obtain controlled GF180MCU DRM revision for LU.3/LU.4 and confirm the digital device-class column *(curated)*
- **#491**: Apply the mechanical edit set directed by ratified DR-0010 and DR-0011 (Raw rate row, sizing constant, derived figures) *(curated)*
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard *(curated)*
- **#553**: Replace 24 hand-copied path-based module loaders with one helper *(curated)*

## Proposed (Architect / Hermit)

- **#590**: Share one klt-request emit/run scaffold across the sim tools and enforce the no-full-grid-local rule once *(architect)*
- **#591**: Run shellcheck over tracked shell scripts in lint and CI (bash -n is the only check today) *(architect)*
- **#593**: Reject tracked raw simulation artifacts with no evidence record *(architect)*
- **#346**: Collapse duplicated ring1/ring2 layout generators (ro_nand2, ro_ring11) onto shared code *(hermit)*
- **#589**: Dedup the gds_path/check/main boilerplate repeated in every layout generator *(hermit)*

## Epics

_None._

## Backlog Balance

| Tier | Count |
|------|-------|
| Operator merge-risk holds | 2 |
| Operator priority | 0 |
| Ready (`loom:issue`) | 3 |
| In Progress (`loom:building`) | 2 |
| PRs awaiting review | 0 |
| Approved PRs awaiting merge | 2 |
| Curated | 10 |
| Architect / Hermit proposals | 5 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
