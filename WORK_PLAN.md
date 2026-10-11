# Work Plan

Snapshot of the GitHub label state. Operator priority does not override a
dependency block or an operator-only decision.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs stuck under a `loom:operator` merge-risk hold — implementation work is done, only a human merge decision is missing.

- **#433**: Give the strict record-checksum CI step an npm check entry and parity coverage

## Operator Priority

Issues the operator starred (`loom:operator-priority`); land these first.

_None._

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist
- **#468**: Disambiguate the colliding DR-0011/DR-0012 citations (README links the wrong DR-0012) and guard them

## In Progress

Issues currently being built (`loom:building`).

- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard
- **#553**: Replace 24 hand-copied path-based module loaders with one helper
- **#563**: Reject nonpositive simulation timeout bounds before launching ngspice

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

_None._

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#433**: Give the strict record-checksum CI step an npm check entry and parity coverage
- **#567**: Deduplicate git blob SHA-1 helper onto sim/harness/report.py (#557)

## Proposed

Issues carrying `loom:curated`.

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist *(curated)*
- **#418**: Verify assembled combiner/sampler reset and capture with native post-layout comparison *(curated)*
- **#432**: Give the strict record-checksum CI step an npm check entry and parity coverage *(curated)*
- **#449**: Digital tap spacing exceeds DRM 14.3.1 MV latch-up limit (49.7 um vs 15 um): confirm and decide *(curated)*
- **#468**: Disambiguate the colliding DR-0011/DR-0012 citations (README links the wrong DR-0012) and guard them *(curated)*
- **#472**: Characterize asymmetric fs/sf corners on the integrated ring-array sampler path *(curated)*
- **#486**: Obtain controlled GF180MCU DRM revision for LU.3/LU.4 and confirm the digital device-class column *(curated)*
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard *(curated)*
- **#553**: Replace 24 hand-copied path-based module loaders with one helper *(curated)*
- **#557**: Deduplicate git blob SHA-1 helper: 4 copies across sim/harness and sim/tools *(curated)*
- **#563**: Reject nonpositive simulation timeout bounds before launching ngspice *(curated)*

## Proposed (Architect / Hermit)

- **#565**: Reject DUT include filenames that collide with generated simulation artifacts *(architect)*
- **#566**: Enforce harness ownership of stochastic simulation seed controls *(architect)*
- **#570**: Add a relative markdown link guard to npm run lint (and fix existing broken links) *(architect)*
- **#346**: Collapse duplicated ring1/ring2 layout generators (ro_nand2, ro_ring11) onto shared code *(hermit)*

## Epics

_None._

## Backlog Balance

| Tier | Count |
|------|-------|
| Operator merge-risk holds | 1 |
| Operator priority | 0 |
| Ready (`loom:issue`) | 2 |
| In Progress (`loom:building`) | 3 |
| PRs awaiting review | 0 |
| Approved PRs awaiting merge | 2 |
| Curated | 11 |
| Architect / Hermit proposals | 4 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
