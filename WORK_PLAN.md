# Work Plan

Snapshot of the GitHub label state. Operator priority does not override a
dependency block or an operator-only decision.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs under a hold (`loom:blocked` or `loom:operator`) — only a human merge decision is missing.

- **#729**: feat(interface): drop raw_shift reset and size raw_bit_count from RAW_PACK_BITS, with measured digital chain

## Very Important

`loom:very-important` (one counts per workspace); every stage takes these first.

- **#709**: Area and power: FIFO and cell-inventory reductions toward the ratified bounds

## Important

`loom:important`; taken before unlabelled work.

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist
- **#414**: Characterize deterministic supply-ripple sensitivity of the buffered RO array
- **#654**: T1 item 5.analog: klayout-tools#2533 is fixed; emit the ratified analog rows as klt sim envelopes
- **#656**: T1 item 6: produce a klt yield report over the existing mismatch Monte Carlo campaign

## In Progress

Issues currently being built (`loom:building`).

- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard
- **#709**: Area and power: FIFO and cell-inventory reductions toward the ratified bounds
- **#717**: Digital tapcell pitch: configure in build.py, re-place, and re-measure tap distance (LU.3/LU.4 placement unit of #487)
- **#718**: Refresh sim/signoff evidence after digital tapcell re-placement (DR-0029 inventory, evidence unit of #487)
- **#734**: Refresh extracted/routed ro-array startup records on the 30 um tapcell geometry

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

_None._

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#729**: feat(interface): drop raw_shift reset and size raw_bit_count from RAW_PACK_BITS, with measured digital chain
- **#732**: evidence: refresh digital STA, activity and post-route records on the 30 um tapcell geometry
- **#737**: docs: record measured DR-0029 follow-up for the extracted ro-array startup family

## Proposed

Issues carrying `loom:curated`.

- **#200**: Champion: Merge-Risk Hold Digest *(curated)*
- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist *(curated)*
- **#366**: Guard telemetry: process substitution misclassified as worktree write *(curated)*
- **#414**: Characterize deterministic supply-ripple sensitivity of the buffered RO array *(curated)*
- **#418**: Verify assembled combiner/sampler reset and capture with native post-layout comparison *(curated)*
- **#449**: Digital tap spacing exceeds DRM 14.3.1 MV latch-up limit (49.7 um vs 15 um): confirm and decide *(curated)*
- **#472**: Characterize asymmetric fs/sf corners on the integrated ring-array sampler path *(curated)*
- **#486**: Obtain controlled GF180MCU DRM revision for LU.3/LU.4 and confirm the digital device-class column *(curated)*
- **#520**: Replace ad-hoc sys.path.insert bootstraps with one import convention and a lint guard *(curated)*
- **#654**: T1 item 5.analog: klayout-tools#2533 is fixed; emit the ratified analog rows as klt sim envelopes *(curated)*
- **#656**: T1 item 6: produce a klt yield report over the existing mismatch Monte Carlo campaign *(curated)*
- **#705**: Bump klayout-tools pin 0.6.0 → 0.8.0 *(curated)*
- **#708**: Power gating: define and verify the power-intent flow for a gated digital domain *(curated)*
- **#709**: Area and power: FIFO and cell-inventory reductions toward the ratified bounds *(curated)*
- **#717**: Digital tapcell pitch: configure in build.py, re-place, and re-measure tap distance (LU.3/LU.4 placement unit of #487) *(curated)*
- **#734**: Refresh extracted/routed ro-array startup records on the 30 um tapcell geometry *(curated)*

## Proposed (Architect / Hermit)

_None._

## Epics

_None._

## Backlog Balance

| Bucket | Count |
|------|-------|
| Operator merge-risk holds | 1 |
| Very important | 1 |
| Important | 1 |
| Ready (`loom:issue`) | 4 |
| In Progress (`loom:building`) | 5 |
| PRs awaiting review | 0 |
| Approved PRs awaiting merge | 3 |
| Curated | 16 |
| Architect / Hermit proposals | 0 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
