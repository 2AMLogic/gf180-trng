# Decision record template

Copy this file to `spec/decision-records/DR-<nnnn>-<slug>.md` and fill it in.
Delete the guidance comments; keep the section headings.

## Convention

- **Filename**: `DR-<nnnn>-<slug>.md` — `<nnnn>` is a zero-padded, strictly
  increasing number (`DR-0001-…`, `DR-0002-…`); `<slug>` is lowercase-hyphenated
  (`DR-0003-ro-stage-count.md`). Numbers are never reused, including for
  rejected or superseded records.
- **Immutable once accepted.** An accepted DR is not rewritten when the
  decision changes. Write a new DR that supersedes it, and update only the
  old DR's `status` / `superseded_by` fields.
- **One decision per record.** If you are writing "and also", it is two DRs.

## When to write a DR

Write one when a choice **constrains future work** and someone would
otherwise have to re-derive it:

- Any change to the ratified spec in `spec/` (required — spec changes go
  through a decision record).
- Architecture choices (entropy-source topology, health-test scheme,
  interface shape).
- Methodology choices that bind downstream results (corner set, seed policy,
  what counts as a passing claim).
- Reconciling a conflict between conventions (e.g. this repo's `sim/`
  evidence format vs. an upstream harness convention).

Do **not** force these into DR format:

- Survey/literature notes and architecture comparisons — ordinary documents.
- Simulation results and characterization summaries — those are evidence
  records, see [`sim/README.md`](../../sim/README.md).
- Implementation details with no cross-cutting consequence — a commit
  message or PR description is enough.

A DR **cites** evidence (record stems from `sim/records/`); it does not
restate it.

---

<!-- ─────────── copy from here down ─────────── -->

```
---
dr: DR-<nnnn>-<slug>
title: <short imperative statement of the decision>
status: Proposed        # Proposed | Accepted | Rejected | Superseded
date: <YYYY-MM-DD>      # date of the current status
deciders: <who ratified it>
supersedes: <DR-nnnn-slug or n/a>
superseded_by: <DR-nnnn-slug or n/a>
related: <#issue / #PR / spec section references>
---
```

# DR-<nnnn>: <title>

## Status

<!-- Proposed | Accepted | Rejected | Superseded by DR-nnnn, with the date.
     Append status changes as dated lines rather than rewriting history:
       - 2026-08-01: Proposed
       - 2026-08-05: Accepted
-->

## Context

<!-- The forces at play, in enough detail that a reader in a year does not
     have to reconstruct them. What problem forced a choice? What
     constraints apply (spec targets, PDK, schedule, confidentiality)?
     Cite evidence by record stem — e.g. "per
     sim/records/2026-08-14-ro-delay-cell-jitter-03.md" — rather than
     restating numbers without provenance. If a claim here has no evidence
     record behind it, say so explicitly ("literature value, unconfirmed"). -->

## Decision

<!-- The choice, stated in active voice and in one or two sentences:
     "We will …". Then the specifics: what exactly changes, and where
     (files, spec sections, interfaces). Be concrete enough that a builder
     can act on it without asking a follow-up question. -->

## Alternatives considered

<!-- One subsection per genuine alternative — including "do nothing" when
     that was live. For each: what it was, why it was plausible, and the
     specific reason it lost. "Rejected" with no reason is not an
     alternative considered; it is a footnote. -->

### <Alternative A>

- **What**:
- **Why plausible**:
- **Why rejected**:

### <Alternative B>

- **What**:
- **Why plausible**:
- **Why rejected**:

## Consequences

<!-- What becomes true once this is accepted — the good, the bad, and the
     newly-constrained. Include what this decision forecloses and what it
     obligates (new verification work, spec edits, follow-up issues). -->

- **Positive**:
- **Negative / accepted cost**:
- **Follow-up required**: <issues to file, spec sections to update, evidence still owed>
- **Revisit if**: <the condition that would justify a superseding DR>
