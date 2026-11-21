---
dr: DR-0036-keep-grader-pin-0.8.0-over-0.9.2
title: Keep the klt signoff grader pin at 0.8.0 after re-grading main against the released klt 0.9.2
status: Accepted
date: 2026-11-21
deciders: Builder of issue #1032, under the same delegated-methodology rule DR-0035 was accepted under, and ratified through ordinary review of the pull request that carries it. Not an operator ratification. No spec row, ratified claim or limit changes.
supersedes: n/a
superseded_by: n/a
related: "#1032 (the pin-tracking issue), DR-0026 (normative klt build), signoff/check.py (KLT_GRADER_PIN), PR #1029 (the item-6 JSON projection and its retirement note, still open at decision time), klayout-tools#4793 (the markdown-table spec source), klayout-tools#6938 (mixed-signal item-6 scoping, out of scope)"
---

# DR-0036: Keep the klt signoff grader pin at 0.8.0 after re-grading main
against the released klt 0.9.2

## Status

- 2026-11-21: **Accepted** by the Builder of #1032, under delegated
  methodology. Like [DR-0035], it records a measured keep decision about
  which release grades this block; it does not change what the block must
  do. If review of the pull request rejects it, the pull request does not
  merge.

## Context

`klt signoff` parses the T1 item list out of klayout-tools' own bundled
`docs/design-evidence-tiers.md`, so the grader release *is* the yardstick:
moving `KLT_GRADER_PIN` (signoff/check.py) re-renders the committed verdict
`signoff/records/t1-tier-report.json` and must align CI's install step and
the README's "Running it" line in the same commit. The pin is a published
PyPI release so a third party reproduces the record with one `pip install`
of `klayout-tools==0.8.0`. <!-- klt-pin: grader -->

Two things forced a measured keep-or-move decision now ([#1032]):

1. **A host dev-build anomaly.** Grading clean `main` with the host's
   development klt (`0.9.3.dev2575+g6bd18bbc8637`, measured 2026-11-20 on
   `0fb996a3` against the recorded 0.8.0 report) flips exactly one row:
   T1 item 11 analog `unmet / supply_spec_disclosed_unexpressible` →
   `unmet / invalid_evidence`. Whether that tightening was real had to be
   checked against a *release*, not a dev build.
2. **An in-tree retirement trigger.** PR #1029's item-6 JSON projection
   exists only because the 0.8.0 grader pin has no markdown-table spec
   source (klayout-tools#4793, first released in klt 0.9.2), and its
   retirement note — repeated in `signoff/README.md` on that branch — says
   to retire the projection when the pin moves to a release whose native
   source can read the ratified table. PR #1029 is still open; on `main`
   the projection is absent and item 6 digital stands at
   `unmet / no_evidence`.

### The measurement

Released `klayout-tools` **0.9.2** (the newest PyPI release on 2026-11-21:
0.9.0, 0.9.1, 0.9.2) in a throwaway `uvx` environment
(`uvx --from "klayout-tools==0.9.2" klt …` <!-- klt-pin: historical --> —
never the host tool, per DR-0026's environment discipline), run over clean
`main` at `cd6778b2`:

```
klt signoff --manifest signoff/block-manifest.json --format json   # exit 3 on both releases
```

Compared by `(id, partition)` against the committed 0.8.0 report:

- **All 22 T1 rows match** in status and reason; `t1_item_count` 22 and
  `t1_met_count` 17 on both. The three non-T1 `tier_not_supported` rows
  match too.
- **Item 11 analog**: `unmet / supply_spec_disclosed_unexpressible` on
  both, with byte-identical detail — including the combiner/sampler
  `ties_disclosure_reason`. The dev build's `invalid_evidence` **does not
  reproduce on the release**: the anomaly is a development-tree change,
  not something a pin move today would import. A measured refutation; no
  fix target exists.
- **Item 6 digital**: `unmet / no_evidence` on both (`main` carries no
  #1029 content; that branch's `not_applicable_statistical_row` refusal is
  its own record).
- What *does* change on 0.9.2 is yardstick text and report shape, none of
  it verdict-bearing for this block: `source_doc_content_hash` and
  `grading_ruleset_id` (the bundled tiers document was reworded for items
  3, 4, 5, 6, 8 and 11 — foundry-cell DRC exceptions on item 3, pinned
  LVS runsets replacing the 2026-10-17 interim on item 4, model-run
  envelopes on item 5, the analog-partitions operator ruling on item 6,
  `--attest 8` mechanical attestation on item 8, a
  `power_delivery_parts_missing` reason on item 11); item 8's citation
  objects gain `attestation: {"tool_produced": false}` with citation
  content hashes unchanged; item 6 analog's detail gains an empty
  `not_applicable_negative_controls` list; advisory `notes` appear on the
  item 6 rows.

### The retirement blocker

The 0.9.2 native markdown-table spec source cannot yet replace the item-6
JSON projection. Measured 2026-11-20 in a disposable copy of #1029
(pointing only `evidence["6.digital"].not_applicable.spec` at `README.md`
with its byte hash, `format: "markdown-table"`, `id_column: "Parameter"`):
the released parser takes the **document's first status line** as the spec
status — README's project-maturity line, `Status: early` — so the row
grades `unmet / not_applicable_spec_unratified` instead of the recorded
statistical-row finding, and it takes the parameter cell literally as the
row ID where the projection derives ids like `period_r1`. The retirement
note's conditions (reads the ratified table, binds the statement to the
same rows, reproduces the statistical-row finding) are not met.

## Decision

**We keep `KLT_GRADER_PIN` at `klayout-tools==0.8.0`.** Nothing changes: <!-- klt-pin: grader -->
not `signoff/check.py`, not CI's grader install step, not
`signoff/README.md`'s install lines, not the committed
`t1-tier-report.json`. The released 0.9.2 grader renders an identical
verdict on this block's committed evidence, so moving the pin buys a
record regeneration, a ruleset-id churn and CI/README alignment with zero
grading benefit — while the one in-tree obligation that a pin move would
trigger (retiring the item-6 projection, on a #1029-containing base)
cannot be discharged: 0.9.2's native spec source mis-reads the ratified
table. The item-11 dev-build anomaly is recorded here as not reproducing
on releases, so a future host-klt diff is not misread as record drift.

## Alternatives considered

### Move the pin to 0.9.2 now

- **What**: bump `KLT_GRADER_PIN`, regenerate `t1-tier-report.json` under
  0.9.2, align CI and the README install lines.
- **Why plausible**: 0.9.2 is the newest release; its yardstick text is
  what klayout-tools currently documents, and it carries the attestation
  and foundry-cell-exception machinery this block may want later.
- **Why rejected**: the measured verdict delta is zero. The move is pure
  churn against a changelog of item-text rewordings, and the projection
  retirement it would obligate is blocked by the mis-reading native
  source above. A pin move is a change to the verdict of record and needs
  its evidence treatment; with no verdict change there is nothing to
  treat.

### Pin the development build that flags item 11

- **What**: adopt the host dev build (or wait for whatever release
  carries its tightening) because it flags item 11 analog
  `invalid_evidence`.
- **Why plausible**: a stricter grader that surfaces a real evidence gap
  is exactly what a signoff yardstick is for.
- **Why rejected**: the tightening does not reproduce on any release
  (0.9.2 keeps `supply_spec_disclosed_unexpressible` with identical
  detail), the pin must stay a published PyPI release for one-command
  reproducibility, and no release exists that grades the way the dev
  build does. When one ships, that is the revisit condition below.

### Record nothing; let the retirement note do the tracking

- **What**: leave the keep decision implicit in the 0.8.0 pin's continued
  existence.
- **Why plausible**: doing nothing is free.
- **Why rejected**: the retirement triggers were written into the tree
  with no measured baseline, and the item-11 anomaly was an unverified
  hypothesis about a *released* grader's behavior. Without this record,
  the next reader re-derives the whole comparison — or worse, trusts the
  dev-build diff.

## Consequences

- **Positive**: the verdict of record stays reproducible with one
  `pip install`; the item-11 hypothesis is closed by measurement
  (refuted on the release); the retirement condition now has a dated,
  measured blocker; the cost of the next pin move (what regenerates, what
  must align) is written down next to the pin it concerns.
- **Negative / accepted cost**: the yardstick text drifts from what
  klayout-tools currently documents (0.9.2's reworded items 3/4/5/6/8/11
  are not what grades this block), and the committed 0.8.0 record lacks
  the newer report shape (`attestation` fields,
  `not_applicable_negative_controls`). Neither affects any verdict.
- **Follow-up required**: none open. PR #1029's retirement note remains
  the gate for the projection; this record supplies the measured
  0.9.2 baseline it will be judged against.
- **Revisit if**: a released klt grader changes any T1 row's status or
  reason on this block's committed evidence, or a release's native
  markdown-table source reads the ratified README table the way #1029's
  retirement note requires. Either supersedes this record with a new DR.

[DR-0035]: DR-0035-digital-facing-trunk-estimates-follow-the-bottom-edge-pins.md
[DR-0026]: DR-0026-normative-klt-build-for-floorplan-reports.md
[#1032]: https://github.com/2AMLogic/gf180-trng/issues/1032
