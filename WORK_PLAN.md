# Work Plan

Snapshot of the GitHub label state. Operator priority does not override a
dependency block or an operator-only decision.

<!-- guide:plan-body:start -->
_Generated: 2026-11-21T05:23:42Z (snapshot; compare against live labels)_
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

_None._

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

- **#717**: Digital tapcell pitch: configure in build.py, re-place, and re-measure tap distance (LU.3/LU.4 placement unit of #487)

## Important

`loom:important`; taken before unlabelled work.

- **#1025**: T1 item 6 (analog): size the mismatch Monte Carlo campaign to the klt yield target and declare a seeded negative control

## Ready

Human-approved issues (`loom:issue`) ready for implementation — excluding held (`loom:blocked`/`loom:operator`/`loom:frozen`), `loom:building`, and issues closed by an open `loom:pr` PR (listed under Approved).

- **#717**: Digital tapcell pitch: configure in build.py, re-place, and re-measure tap distance (LU.3/LU.4 placement unit of #487)

## In Progress

Issues currently being built (`loom:building`).

- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard
- **#942**: Item-7 source inventory: extra_files are not import-expanded, so run_demo.py's own imports are unpinned
- **#991**: xschem pin migration: migrate gf180-trng to the fleet 3.4.7
- **#1025**: T1 item 6 (analog): size the mismatch Monte Carlo campaign to the klt yield target and declare a seeded negative control
- **#1026**: T1 item 6 (digital): commit the hash-bound not_applicable statement against the pinned 0.8.0 grader, or record the mixed-signal refusal upstream
- **#1030**: Remove the obsolete no-waypoints claim from the ring layout README
- **#1032**: Track the klt grader pin: re-grade against a released 0.9.x, and retire the item-6 digital spec projection when the pin moves
- **#1035**: Remove obsolete empty-region and DRC-clean claims from the floorplan builder docstring
- **#1036**: Reuse the SPICE continuation helper so floorplan inventory counts split instances

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

- **#992**: ci: build the fleet-pinned xschem 3.4.7 from source in pdk-nightly *(held)*
- **#1029**: feat(signoff): bind the item 6 digital not_applicable statement and record its refusal *(held)*
- **#1033**: docs: drop the obsolete no-waypoint-router claim from the rings README
- **#1037**: fix: count comment-split instances in floorplan inventory via shared joiner
- **#1038**: docs: replace stale empty-region and DRC-clean claims in floorplan docstring
- **#1040**: spec: record DR-0036 keeping the grader pin at klt 0.8.0 over released 0.9.2

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

_None._

## Proposed

Issues carrying `loom:curated`.

- **#200**: Champion: Merge-Risk Hold Digest *(curated)* *(held)*
- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist *(curated)* *(held)*
- **#449**: Digital tap spacing exceeds DRM 14.3.1 MV latch-up limit (49.7 um vs 15 um): confirm and decide *(curated)* *(held)*
- **#476**: Complete the unrun 27-corner ring2 paired PEX diagnostic campaign *(curated)* *(held)*
- **#486**: Obtain controlled GF180MCU DRM revision for LU.3/LU.4 and confirm the digital device-class column *(curated)* *(held)*
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard *(curated)*
- **#700**: T1 item 5 (corner verification): resolve the missed Power (758 uW vs < 500 uW) and Area (0.176 mm^2 vs < 0.05 mm^2) rows *(curated)*
- **#717**: Digital tapcell pitch: configure in build.py, re-place, and re-measure tap distance (LU.3/LU.4 placement unit of #487) *(curated)*
- **#810**: Power: record ring-liveness sampler (xsr1/xsr2) active current at the binding corner *(curated)* *(held)*
- **#866**: pdk-nightly is red at the synthesis staleness guard, so the layout and floorplan freshness steps are skipped *(curated)* *(held)*
- **#942**: Item-7 source inventory: extra_files are not import-expanded, so run_demo.py's own imports are unpinned *(curated)*
- **#991**: xschem pin migration: migrate gf180-trng to the fleet 3.4.7 *(curated)*
- **#1025**: T1 item 6 (analog): size the mismatch Monte Carlo campaign to the klt yield target and declare a seeded negative control *(curated)*
- **#1026**: T1 item 6 (digital): commit the hash-bound not_applicable statement against the pinned 0.8.0 grader, or record the mixed-signal refusal upstream *(curated)*
- **#1032**: Track the klt grader pin: re-grade against a released 0.9.x, and retire the item-6 digital spec projection when the pin moves *(curated)*

## Proposed (Architect / Hermit)

- **#880**: Collapse the four copy-pasted recorded-verdict gates in sim/tools into one helper (they have drifted) *(hermit)* *(held)*
- **#889**: Collapse the six duplicated write_record callbacks in sim/tb behind one sim/harness/report.py helper (reverses #888's scope boundary) *(hermit)* *(held)*
- **#897**: Consolidate four divergent copies of the committed-PDK-provenance rule into layout/_klt.py *(hermit)* *(held)*
- **#1039**: Retire the empty floorplan assembly inventory gap table *(hermit)*

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 0 |
| Very important | 1 |
| Important | 1 |
| Ready (`loom:issue`, net of holds/building/merge-pending) | 1 |
| In Progress (`loom:building`) | 9 |
| PRs awaiting review | 6 |
| Approved PRs awaiting merge | 0 |
| Curated | 15 |
| Architect / Hermit proposals | 4 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
