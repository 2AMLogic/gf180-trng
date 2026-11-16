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
- **#917**: sim/harness/scenario_cli.py has no dedicated test module, unlike 10 of the 13 other harness modules
- **#934**: sim/characterization-post-layout-extracted.md:1538 still reads the composed floorplan as DRC-clean — live prose, not struck-through history

## In Progress

Issues currently being built (`loom:building`).

- **#472**: Characterize asymmetric fs/sf corners on the integrated ring-array sampler path
- **#476**: Complete the unrun 27-corner ring2 paired PEX diagnostic campaign
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard
- **#879**: README claims the digital section and composed floorplan are DRC-clean; the committed reports read 2769/2750 tap-distance violations
- **#883**: sim/characterization-digital-activity-power.md marks a superseded record family "(current)"
- **#915**: layout/tests/test_klt.py: the shim-dir tearDown registers $PATH[0] for rmtree before validating it
- **#920**: Single-source the tool --version probes hand-rolled in four places (two have no timeout)
- **#921**: sim/tb/trng-top-post-route/README.md asks for a klayout-tools commit pdk-nightly.yml no longer pins
- **#928**: Point test_evidence_store.py's three borrowed fixture members at _CliFixture instead of RunIntegrityTests
- **#929**: Audit note's block-manifest "Key count" column (38/39) is not reproducible and states no counting rule
- **#930**: Lint guard: fail when a tracked *.py defines a class or function after a module-level __main__ guard
- **#941**: publish_item7_analog.py does not redact client_ngspice_binary, so a /home-resolved ngspice costs a whole fleet rerun
- **#942**: Item-7 source inventory: extra_files are not import-expanded, so run_demo.py's own imports are unpinned

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

- **#923**: signoff: run and publish ring2's native 27-corner paired comparison
- **#948**: Redact client host paths in the shared klt pex envelope loader

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#895**: sim: pin the activity-power prose to its generator, and re-derive it
- **#937**: chore(loom): resync installed Loom to v0.19.1302
- **#938**: fix(sim): replace the dead klayout-tools git pin in the post-route provisioning instructions
- **#939**: feat: teach unused_names to flag definitions after the __main__ guard (TRNG001)
- **#943**: docs: state the manifest key-count rule and correct the audit's figures

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
- **#915**: layout/tests/test_klt.py: the shim-dir tearDown registers $PATH[0] for rmtree before validating it *(curated)*
- **#917**: sim/harness/scenario_cli.py has no dedicated test module, unlike 10 of the 13 other harness modules *(curated)*
- **#921**: sim/tb/trng-top-post-route/README.md asks for a klayout-tools commit pdk-nightly.yml no longer pins *(curated)*
- **#928**: Point test_evidence_store.py's three borrowed fixture members at _CliFixture instead of RunIntegrityTests *(curated)*
- **#929**: Audit note's block-manifest "Key count" column (38/39) is not reproducible and states no counting rule *(curated)*
- **#930**: Lint guard: fail when a tracked *.py defines a class or function after a module-level __main__ guard *(curated)*
- **#934**: sim/characterization-post-layout-extracted.md:1538 still reads the composed floorplan as DRC-clean — live prose, not struck-through history *(curated)*
- **#941**: publish_item7_analog.py does not redact client_ngspice_binary, so a /home-resolved ngspice costs a whole fleet rerun *(curated)*
- **#942**: Item-7 source inventory: extra_files are not import-expanded, so run_demo.py's own imports are unpinned *(curated)*
- **#947**: unused_names docstring: the RUF100 carve-out sentence does not cover the dynamic-call block *(curated)*

## Proposed (Architect / Hermit)

- **#880**: Collapse the four copy-pasted recorded-verdict gates in sim/tools into one helper (they have drifted) *(hermit)*
- **#889**: Collapse the six duplicated write_record callbacks in sim/tb behind one sim/harness/report.py helper (reverses #888's scope boundary) *(hermit)*
- **#897**: Consolidate four divergent copies of the committed-PDK-provenance rule into layout/_klt.py *(hermit)*
- **#902**: Single-source the klt/PDK availability preflight hand-rolled in six layout entry points (#589 follow-up) *(hermit)*

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 2 |
| Very important | 1 |
| Important | 0 |
| Ready (`loom:issue`) | 3 |
| In Progress (`loom:building`) | 13 |
| PRs awaiting review | 2 |
| Approved PRs awaiting merge | 5 |
| Curated | 23 |
| Architect / Hermit proposals | 4 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
