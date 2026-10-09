# Work Plan

Snapshot of the GitHub label state. Operator priority does not override a
dependency block or an operator-only decision.

<!-- guide:plan-body:start -->
## Operator Attention: Merge-Risk-Hold Pileup

Judge-approved PRs stuck under a `loom:operator` merge-risk hold — implementation work is done, only a human merge decision is missing.

_None._

## Operator Priority

Issues the operator starred (`loom:operator-priority`); land these first.

_None._

## Ready

Human-approved issues ready for implementation (`loom:issue`).

- **#387**: lvs.py: fix two latent gaps (SPICE continuation after comment; _bit_names net<id> fallback)
- **#406**: Resolve the README's untracked 'still owed' min-entropy re-run at ss/+125C/3.63V

## In Progress

Issues currently being built (`loom:building`).

- **#315**: Inter-region stubs miss digital's top-edge pins after the re-place-and-route (clk, rst_n, raw_bit, raw_valid, ring_bit unjoined)
- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist
- **#403**: Unit-test build_dut.py's extraction_port_map refusal branches offline

## PRs Awaiting Review

PRs waiting on Judge (`loom:review-requested`).

_None._

## Approved (Awaiting Merge)

PRs that passed review and are queued for Champion auto-merge (`loom:pr`).

- **#409**: test(sim): unit-test build_dut port map refusal branches offline

## Proposed

Issues carrying `loom:curated`.

- **#315**: Inter-region stubs miss digital's top-edge pins after the re-place-and-route (clk, rst_n, raw_bit, raw_valid, ring_bit unjoined) *(curated)*
- **#339**: Post-layout re-sims run on floating PMOS wells; quantify against a well-tied extracted netlist *(curated)*
- **#387**: lvs.py: fix two latent gaps (SPICE continuation after comment; _bit_names net<id> fallback) *(curated)*

## Proposed (Architect / Hermit)

- **#404**: Committed generated reports embed absolute host paths (home dir, worktree); add a guard *(architect)*
- **#408**: check:all omits the append-only evidence-history guard that check:ci runs *(architect)*
- **#346**: Collapse duplicated ring1/ring2 layout generators (ro_nand2, ro_ring11) onto shared code *(hermit)*

## Epics

_None._

## Backlog Balance

| Tier | Count |
|------|-------|
| Operator merge-risk holds | 0 |
| Operator priority | 0 |
| Ready (`loom:issue`) | 2 |
| In Progress (`loom:building`) | 3 |
| PRs awaiting review | 0 |
| Approved PRs awaiting merge | 1 |
| Curated | 3 |
| Architect / Hermit proposals | 3 |
| Active epics | 0 |
<!-- guide:plan-body:end -->
