---
dr: DR-0005-sim-harness-record-granularity
title: Bootstrap the PVT harness from gf180-bandgap#23 but keep this repo's per-point evidence-record granularity
status: Accepted
date: 2026-07-31
deciders: Builder (issue #2), following the ratified sim/README.md format from #18
supersedes: n/a
superseded_by: n/a
related: "#2, #5, #18, 2AMLogic/gf180-bandgap#23"
---

# DR-0005: Bootstrap the PVT harness from gf180-bandgap#23 but keep this repo's per-point evidence-record granularity

## Status

- 2026-07-31: Accepted (adopted directly during harness bring-up; no
  conflicting evidence yet recorded to migrate).

## Context

CLAUDE.md: "Harness bootstrap: copy the sim-harness pattern from
`2AMLogic/gf180-bandgap` once it lands there rather than reinventing."
`2AMLogic/gf180-bandgap#23` (merged) delivers exactly that pattern: a
`sim/run_corners.py` CLI, a no-hardcoded-path PDK resolver
(`GF180_PDK_PATH` → `PDK_ROOT`/`PDK` → `sim/pdk.local.json` →
`sim/pdk.json` → built-in search roots), named process-corner bundles
(`tt`/`ff`/`ss`/`fs`/`sf` plus passive-family skews), and a testbench
contract that rejects netlist fragments overriding `.temp`/`.lib`/
`.include`/`.control`/`.endc`/`.end`.

Independently, this repo's own issue #5 (closed before #2 landed) ratified
`sim/README.md`'s evidence-record format. That format states explicitly:

> One record covers **one testbench at one corner** (one process/voltage/
> temperature point). A PVT sweep produces one record per corner, not one
> record with a table of corners.

The gf180-bandgap harness does the opposite: one invocation of its
`run_corners.py` produces **one aggregate record** covering the entire PVT
grid (`grid.points`, `grid.points_ok`, a per-corner result table, and a
grid-wide summary/spread check inside a single `records/<record-id>.md`
file), with raw per-corner logs nested under that same record.

These two conventions cannot both be followed literally by the same
harness output. This DR is the reconciliation the Consumer-requirements
section of issue #2 called for: "If the upstream pattern's convention
conflicts, reconcile via a `spec/` decision record."

Note also (verified empirically during bring-up, not asserted from
inspection alone): the gf180-bandgap corner-section names
(`typical`/`ff`/`ss`/`fs`/`sf`, `bjt_typical`/`bjt_ff`/`bjt_ss`, etc.) *do*
correspond to real top-level `.LIB` sections in the installed gf180mcuD
`sm141064.ngspice` (confirmed via `grep -n "^\.LIB"`, case-sensitive
`.lib`/`.LIB` mixed use in the PDK file) and do measurably shift device
behavior (see `sim/tools/corner_sanity_check.py` and
`sim/records/2026-07-31-corner-sanity-nfet-id-0{1,2,3}.md`). The
corner-*architecture* (PDK resolver, corner bundles, testbench-fragment
contract) is therefore adopted with no material change; only the
record-granularity and file-layout differ from upstream.

## Decision

We will bootstrap `sim/harness/{pdk,corners,testbench,runner}.py` directly
from the gf180-bandgap#23 pattern (PDK resolution order, corner-section
bundles, the `.temp`/`.lib`/`.include`/`.control`/`.endc`/`.end`
testbench-fragment contract, and the `.option seed=<N>` mechanism for
stochastic runs), but replace its aggregate-grid `report.py` with one that
conforms to this repo's already-ratified `sim/README.md`:

- **One evidence record per (testbench, PVT point).** A single
  `sim/run_corners.py <testbench>` invocation that sweeps N corners × M
  temperatures × K supplies writes N×M×K records under `sim/records/`, not
  one aggregate record.
- **Naming and layout follow `sim/README.md` exactly**:
  `sim/records/<YYYY-MM-DD>-<testbench-slug>-<nn>.md`, with raw output at
  `sim/records/raw/<same-stem>/`. Testbenches live at `sim/tb/<slug>/`
  (flat, no nested `testbench/` subdirectory as gf180-bandgap uses).
- **Multiple seeded runs at one PVT point still aggregate into one
  record** — `sim/README.md`'s `analysis.runs` / `seeds` fields are exactly
  for this case (N repeated stochastic runs *at the same corner*), so a
  stochastic testbench's seed list is per-point, not per-grid.
- Frontmatter fields (`testbench.*`, `netlist.*`, `repo_commit`, `pdk`,
  `pdk.models`, `tool.*`, `corner.*`, `analysis.*`, `seeds`, `raw.*`,
  `wall_time`) match `sim/README.md`'s required-fields table verbatim; see
  `sim/harness/report.py`.

## Alternatives considered

### Copy gf180-bandgap's aggregate-record format as-is

- **What**: Reuse `report.py`'s `build_record`/`render_record` from
  gf180-bandgap#23 unchanged, aggregating the whole grid into one record
  per invocation.
- **Why plausible**: Least code to adapt; keeps this repo bit-for-bit
  aligned with the sibling repo's harness, easing future cross-repo
  harness updates.
- **Why rejected**: Directly contradicts `sim/README.md`'s ratified,
  closed-issue convention ("one record covers one testbench at one
  corner"). Re-litigating that convention was out of scope for a
  harness-bootstrap issue, and downstream consumers (#4's corner-by-corner
  claims, #10's per-run seed methodology) are written against the
  one-record-per-point convention already in the repo.

### Rewrite `sim/README.md` to match gf180-bandgap's aggregate convention

- **What**: Treat gf180-bandgap's convention as authoritative and amend
  this repo's ratified format to match (aggregate grid records).
- **Why plausible**: Would keep exactly one evidence-record convention
  across both repos' harnesses, and an aggregate record's grid-wide
  spread/check fields are convenient for at-a-glance PVT-matrix
  conformance.
- **Why rejected**: `sim/README.md` was independently ratified by this
  repo's own issue #5 before #2 landed, with reasoning specific to this
  repo (a corner citable by its own record ID; a re-run of one corner
  never invalidates the rest). Overriding it to match an upstream repo's
  independent choice, inside a harness-bootstrap issue, is scope creep on
  a ratified spec decision and was not requested by #2's acceptance
  criteria (which only asked to reconcile a *conflict*, not to pick a
  side by default).

## Consequences

- **Positive**: This repo's evidence records stay exactly as `sim/README.md`
  and issue #5 specify -- one record per PVT point, independently citable,
  independently supersedable. Downstream issues (#4, #10, #13, #14) can
  build on the ratified format without a second migration. The
  corner-architecture and PDK-resolution code path stays aligned with the
  sibling repo's pattern, so future harness fixes there (e.g. a corrected
  corner-section name) are easy to port.
- **Negative / accepted cost**: A full PVT sweep now produces many small
  record files (e.g. 45 for a `full` corner-set × default 3×3 P/V grid)
  instead of one aggregate file with a grid-wide summary table. There is
  currently no committed "PVT matrix conformance" check at the record
  level (gf180-bandgap's `matrix_conformance`/`--subset-reason`
  machinery was not ported); a run that only covers a subset of the
  mandated grid is not currently refused or flagged.
- **Follow-up required**: If a later issue (e.g. #4 or #10) needs an
  at-a-glance "is this the full mandated PVT matrix" check across a set of
  per-point records, it should be built as a read-only tool over
  `sim/records/*.md` frontmatter rather than reopening this DR.
- **Revisit if**: The gf180-bandgap harness's per-point section-name
  mapping is found to diverge from this repo's needs (e.g. a device family
  this block relies on that gf180-bandgap's corner set does not cover), or
  if a future decision genuinely needs to change `sim/README.md`'s
  record granularity -- that would be its own DR, not a silent harness
  change.
