# Work Plan

Snapshot of the GitHub label state. Operator priority does not override a
dependency block or an operator-only decision.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

- **#895**: sim: pin the activity-power prose to its generator, and re-derive it
- **#937**: chore(loom): resync installed Loom to v0.19.1302

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

- **#717**: Digital tapcell pitch: configure in build.py, re-place, and re-measure tap distance (LU.3/LU.4 placement unit of #487)

## Important

`loom:important`; taken before unlabelled work.

_None._

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#717**: Digital tapcell pitch: configure in build.py, re-place, and re-measure tap distance (LU.3/LU.4 placement unit of #487)
- **#902**: Single-source the klt/PDK availability preflight hand-rolled in six layout entry points (#589 follow-up)
- **#917**: sim/harness/scenario_cli.py has no dedicated test module, unlike 10 of the 13 other harness modules
- **#942**: Item-7 source inventory: extra_files are not import-expanded, so run_demo.py's own imports are unpinned
- **#947**: unused_names docstring: the RUF100 carve-out sentence does not cover the dynamic-call block
- **#951**: No gate catches hand-mangled formatting in generated signoff/ JSON

## In Progress

Issues currently being built (`loom:building`).

- **#472**: Characterize asymmetric fs/sf corners on the integrated ring-array sampler path
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard
- **#879**: README claims the digital section and composed floorplan are DRC-clean; the committed reports read 2769/2750 tap-distance violations
- **#883**: sim/characterization-digital-activity-power.md marks a superseded record family "(current)"
- **#920**: Single-source the tool --version probes hand-rolled in four places (two have no timeout)

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

_None._

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#895**: sim: pin the activity-power prose to its generator, and re-derive it
- **#937**: chore(loom): resync installed Loom to v0.19.1302

## Proposed

Issues carrying `loom:curated`.

- **#200**: Champion: Merge-Risk Hold Digest *(curated)*
- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist *(curated)*
- **#449**: Digital tap spacing exceeds DRM 14.3.1 MV latch-up limit (49.7 um vs 15 um): confirm and decide *(curated)*
- **#472**: Characterize asymmetric fs/sf corners on the integrated ring-array sampler path *(curated)*
- **#476**: Complete the unrun 27-corner ring2 paired PEX diagnostic campaign *(curated)*
- **#486**: Obtain controlled GF180MCU DRM revision for LU.3/LU.4 and confirm the digital device-class column *(curated)*
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard *(curated)*
- **#700**: T1 item 5 (corner verification): resolve the missed Power (758 uW vs < 500 uW) and Area (0.176 mm^2 vs < 0.05 mm^2) rows *(curated)*
- **#717**: Digital tapcell pitch: configure in build.py, re-place, and re-measure tap distance (LU.3/LU.4 placement unit of #487) *(curated)*
- **#810**: Power: record ring-liveness sampler (xsr1/xsr2) active current at the binding corner *(curated)*
- **#866**: pdk-nightly is red at the synthesis staleness guard, so the layout and floorplan freshness steps are skipped *(curated)*
- **#879**: README claims the digital section and composed floorplan are DRC-clean; the committed reports read 2769/2750 tap-distance violations *(curated)*
- **#883**: sim/characterization-digital-activity-power.md marks a superseded record family "(current)" *(curated)*
- **#917**: sim/harness/scenario_cli.py has no dedicated test module, unlike 10 of the 13 other harness modules *(curated)*
- **#942**: Item-7 source inventory: extra_files are not import-expanded, so run_demo.py's own imports are unpinned *(curated)*
- **#947**: unused_names docstring: the RUF100 carve-out sentence does not cover the dynamic-call block *(curated)*
- **#951**: No gate catches hand-mangled formatting in generated signoff/ JSON *(curated)*

## Proposed (Architect / Hermit)

- **#880**: Collapse the four copy-pasted recorded-verdict gates in sim/tools into one helper (they have drifted) *(hermit)*
- **#889**: Collapse the six duplicated write_record callbacks in sim/tb behind one sim/harness/report.py helper (reverses #888's scope boundary) *(hermit)*
- **#897**: Consolidate four divergent copies of the committed-PDK-provenance rule into layout/_klt.py *(hermit)*

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 2 |
| Very important | 1 |
| Important | 0 |
| Ready (`loom:issue`) | 6 |
| In Progress (`loom:building`) | 5 |
| PRs awaiting review | 0 |
| Approved PRs awaiting merge | 2 |
| Curated | 17 |
| Architect / Hermit proposals | 3 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
