# Work Plan

Snapshot of the GitHub label state. Operator priority does not override a
dependency block or an operator-only decision.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

_None._

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

- **#717**: Digital tapcell pitch: configure in build.py, re-place, and re-measure tap distance (LU.3/LU.4 placement unit of #487)

## Important

`loom:important`; taken before unlabelled work.

- **#885**: Restore the 6.analog citation that merge d870871b dropped from signoff/block-manifest.json
- **#886**: Layout and signoff READMEs still describe floating analog bodies; the committed LVS and PEX reports read verified and biased
- **#887**: Audit merges a395d6e1, 742bb2af and d870871b for content lost in conflict resolution

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#472**: Characterize asymmetric fs/sf corners on the integrated ring-array sampler path
- **#476**: Complete the unrun 27-corner ring2 paired PEX diagnostic campaign
- **#717**: Digital tapcell pitch: configure in build.py, re-place, and re-measure tap distance (LU.3/LU.4 placement unit of #487)
- **#886**: Layout and signoff READMEs still describe floating analog bodies; the committed LVS and PEX reports read verified and biased
- **#894**: Collapse the three ways sim/tests/test_cli.py shares one fixture into one mixin (its cancellation list already leaks a 5x-run test)

## In Progress

Issues currently being built (`loom:building`).

- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard
- **#866**: pdk-nightly is red at the synthesis staleness guard, so the layout and floorplan freshness steps are skipped
- **#877**: Remove four test-only helpers: allocate_record_stem, parse_measurements, parse_non_finite_measurements, tone_detected
- **#879**: README claims the digital section and composed floorplan are DRC-clean; the committed reports read 2769/2750 tap-distance violations
- **#881**: Verification plumbing describes the pre-0.9.0 world: the T1 marker hides row swaps, and tap-distance.json claims no deck codes a tie-distance rule
- **#882**: Collapse the duplicated ring CLI tail into _ring_common and delete the unused _wiring_shapes forwarder
- **#883**: sim/characterization-digital-activity-power.md marks a superseded record family "(current)"
- **#888**: The --scenario/--no-write runner CLI is hand-rolled once per behavioral testbench in sim/tb; move it behind a sim/harness entry point
- **#892**: Consolidate the duplicated OpenROAD shim provisioning in layout/digital into layout/_klt.py

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

- **#896**: refactor: hoist the shared scenario-runner CLI into sim/harness/scenario_cli
- **#899**: refactor: move the OpenROAD shim provisioning into layout/_klt.py
- **#901**: refactor: bind both ring CLI tails with one _ring_common.ring_cli call

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#878**: digital: re-run the chain under the nightly's Yosys 0.69 / klt 0.9.1 toolchain
- **#884**: docs: roadmap as of 2026-11-13
- **#891**: signoff: carry the unmet-row composition in the T1 status fence, and correct the tap-distance deck-coverage disclosure
- **#893**: refactor: drop four test-only helpers for the functions they wrapped
- **#895**: sim: pin the activity-power prose to its generator, and re-derive it

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
- **#881**: Verification plumbing describes the pre-0.9.0 world: the T1 marker hides row swaps, and tap-distance.json claims no deck codes a tie-distance rule *(curated)*
- **#883**: sim/characterization-digital-activity-power.md marks a superseded record family "(current)" *(curated)*
- **#885**: Restore the 6.analog citation that merge d870871b dropped from signoff/block-manifest.json *(curated)*
- **#886**: Layout and signoff READMEs still describe floating analog bodies; the committed LVS and PEX reports read verified and biased *(curated)*
- **#887**: Audit merges a395d6e1, 742bb2af and d870871b for content lost in conflict resolution *(curated)*

## Proposed (Architect / Hermit)

- **#880**: Collapse the four copy-pasted recorded-verdict gates in sim/tools into one helper (they have drifted) *(hermit)*
- **#889**: Collapse the six duplicated write_record callbacks in sim/tb behind one sim/harness/report.py helper (reverses #888's scope boundary) *(hermit)*
- **#897**: Consolidate four divergent copies of the committed-PDK-provenance rule into layout/_klt.py *(hermit)*
- **#900**: Remove three unused sim/harness wrappers: no production caller, and one offers the documented-unsafe allocator *(hermit)*
- **#902**: Single-source the klt/PDK availability preflight hand-rolled in six layout entry points (#589 follow-up) *(hermit)*
- **#904**: Remove eight stray mid-file __main__ guards in sim/tests that hide 47 tests from direct execution *(hermit)*

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 0 |
| Very important | 1 |
| Important | 3 |
| Ready (`loom:issue`) | 5 |
| In Progress (`loom:building`) | 9 |
| PRs awaiting review | 3 |
| Approved PRs awaiting merge | 5 |
| Curated | 17 |
| Architect / Hermit proposals | 6 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
