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

- **#574**: ngspice-46 transient-noise (trnoise) draws are not reproduced by the recorded seed
- **#584**: test_hostile_init_fixtures_affect_plain_batch_but_not_the_policy fails on hosts with ngspice-46
- **#590**: Share one klt-request emit/run scaffold across the sim tools and enforce the no-full-grid-local rule once

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

- **#606**: Record that trnoise waveforms are not seed-reproducible on ngspice-46 (#574)

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
- **#574**: ngspice-46 transient-noise (trnoise) draws are not reproduced by the recorded seed *(curated)*
- **#584**: test_hostile_init_fixtures_affect_plain_batch_but_not_the_policy fails on hosts with ngspice-46 *(curated)*
- **#590**: Share one klt-request emit/run scaffold across the sim tools and enforce the no-full-grid-local rule once *(curated)*

## Proposed (Architect / Hermit)

- **#601**: Add direct unit tests for layout/cells/_build_cli.py message contract *(architect)*
- **#346**: Collapse duplicated ring1/ring2 layout generators (ro_nand2, ro_ring11) onto shared code *(hermit)*
- **#603**: Remove dead functions clk_at, contract_rows, convergence_text (and dead local ctrl) *(hermit)*

## Epics

_None._

## Backlog Balance

| Tier | Count |
|------|-------|
| Operator merge-risk holds | 2 |
| Operator priority | 0 |
| Ready (`loom:issue`) | 3 |
| In Progress (`loom:building`) | 3 |
| PRs awaiting review | 1 |
| Approved PRs awaiting merge | 2 |
| Curated | 12 |
| Architect / Hermit proposals | 3 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
