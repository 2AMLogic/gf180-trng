---
dr: DR-0024-extracted-netlist-record-level
title: Record transistor-level simulation of a parasitic-extracted netlist as `level: extracted`, a sibling of DR-0009's `level: transistor`
status: Accepted
date: 2026-09-06
deciders: Builder (issue #17), under the same delegated-methodology rule DR-0009, DR-0021 and DR-0022 were accepted under. Not an operator ratification — see Status. It changes no ratified row and no ratified claim; it names a record kind DR-0009 deliberately scoped itself away from.
supersedes: n/a
superseded_by: n/a
related: "#17 (origin), DR-0009 (the transistor/behavioral split this value is a sibling within, on the transistor side), DR-0021/DR-0022 (the same pattern applied to gate-level records — precedent for adding a `level:` value by delegated DR rather than editing DR-0009), #106 (the DRC/LVS-clean layout this record kind reads from), #142 (the `klt pex` tooling this record kind depends on), sim/README.md (the record format this DR adds a value to); README §Target specification — no row is edited by this record"
---

# DR-0024: Record transistor-level simulation of a parasitic-extracted netlist as `level: extracted`, a sibling of DR-0009's `level: transistor`

## Status

- 2026-09-06: **Accepted** by the Builder of #17. Delegated methodology, in the
  same sense and with the same correctability as [DR-0009], [DR-0021] and
  [DR-0022]: it fixes what a record *is*, not what the block must do, and a
  later DR supersedes it rather than editing it. No ratified row moves, and no
  existing record is edited or re-labelled.

## Context

[DR-0009] defined `level: transistor` for a record whose DUT is a
schematic-derived netlist (`design/*.spice`, from `design/netlist.py`) run
through ngspice at a real P/V/T point. Issue #17's job — re-running the #12,
#13 and #14 methodologies against the post-layout, parasitic-extracted
netlist `klt pex`/`klt extract --parasitics` produces once #106 and #142
landed — produces records that are almost, but not quite, that:

- Same simulator (ngspice), same corner-file mechanics, same `tb.json`-driven
  `sim/run_corners.py` sweep, same measurement expressions where the DUT
  topology is unchanged.
- **Different DUT provenance.** The netlist under simulation is not
  `design/netlist.py`'s schematic-derived output; it is `layout/pex/*.extracted.spice`
  (`layout/pex/build.py`) — device geometry and internal metal parasitics read
  from real drawn layout (`layout/cells/`), extracted per leaf cell and
  hand-composed using the schematic's own instance-level topology (see that
  module's docstring for exactly what is and is not captured: leaf-cell
  device/routing parasitics, not inter-cell or inter-region wiring).

Three ways to classify these records were available, the same three shapes
[DR-0022] weighed for the gate-level/gate-simulation split:

1. **Label it `level: transistor`, unchanged.** Rejected: a reader filtering
   `level: transistor` today gets exclusively schematic-derived-netlist
   results (DR-0009's own definition), and folding an extraction-based DUT in
   silently would make a comparison like "does extraction move this number"
   — issue #17's entire point — impossible to run mechanically. It would also
   contradict `layout/pex/build.py`'s own module docstring, which is explicit
   that this is a distinct, partial kind of post-layout evidence.
2. **A new top-level frontmatter field instead of a new `level:` value**
   (e.g. `netlist_source: extracted`), leaving `level: transistor` in place.
   Rejected: `level:` is already the field `sim/README.md` uses to answer
   "what produced this run and what may it be cited for" (DR-0009/DR-0021/
   DR-0022 all extend it for exactly that reason); adding a second,
   overlapping axis would let a record be ambiguous about which axis a reader
   should filter on.
3. **A sibling `level:` value.** Adopted — same reasoning as [DR-0022]: the
   citation rule and provenance genuinely differ from a schematic-derived run,
   and that difference is exactly what a `level:` value exists to signal.

## Decision

**A record produced by ngspice transient/noise/DC simulation of a
parasitic-extracted netlist (`klt extract --parasitics` output, or a
composition of such output using the schematic's own topology) carries
`level: extracted`.** It inherits every DR-0009 `level: transistor`
frontmatter convention unchanged:

- `pdk`, `pdk.models`, `tool.ngspice`, `corner.process`, `corner.voltage`,
  `corner.temperature` are filled in exactly as a transistor record's are —
  never `n/a` — because this is still a real P/V/T-point ngspice run.
- One P/V/T point per record ([DR-0005]), seeds recorded for every stochastic
  run ([sim/README.md]'s "no seed, no evidence" rule).
- May be cited for anything a `level: transistor` record may be cited for —
  rate, power, jitter, metastability, min-entropy-adjacent measurements — at
  the corner and against the DUT it names.

And it adds one requirement of its own, mirroring [DR-0022]'s
`timing_annotation` block:

**A `level: extracted` record's `netlist.path` must point at the extracted
netlist actually simulated (`layout/pex/*.extracted.spice`, not
`design/*.spice`), and its Caveats must state what that extraction does and
does not capture** — at minimum, whether inter-cell/inter-region routing
parasitics are included, citing `layout/pex/build.py`'s own accounting (or
whatever tool produced the netlist, if a future record uses a different
composition). An extraction whose coverage is unstated is exactly the defect
[sim/README.md]'s general Caveats rule already forbids; this is that rule
applied to the one thing a reader of an extracted-netlist record has no other
way to reconstruct — which parasitics are actually in the numbers.

**A `level: extracted` record may not be cited as evidence about the fully
assembled, routed layout** unless its Caveats affirmatively state that
inter-cell and inter-region routing parasitics are included. Issue #17's own
first generation of these records is device-level only (leaf-cell parasitics,
schematic-topology composition) — a real but partial capture, not the
full-chip parasitic re-run "extraction changes RO frequencies, adds coupling
paths, and loads the sampler" evokes — and each such record's Caveats say so
explicitly, per the rule above.

## Consequences

- `sim/README.md` gains a fifth `level:` value (`transistor`, `behavioral`,
  `gate`, `gate-simulation`, now `extracted`) and a short section stating the
  rule above. Nothing existing is re-labelled: every prior value keeps its
  meaning and its citation limits.
- Issue #17's records are the first to carry `level: extracted`. Future
  extraction runs — a full assembled-ring/routed-region extraction once the
  `klt extract`/`klt lvs` net-naming gap this issue's own friction filing
  describes is resolved, or a re-run against a revised layout — are new
  records at this same level, one per corner, under [DR-0005]'s unchanged
  granularity rule; a record with fuller routing coverage says so in its own
  Caveats rather than needing a new `level:` value.
- A reader wanting "the current best transistor-level evidence, regardless of
  provenance" now has to consider both `transistor` and `extracted` records
  and read each one's Caveats — the same reading burden [DR-0009] already
  accepted for `transistor` vs. `behavioral`, extended to a third value.

## Follow-up

- **Not owed by this record**: a full assembled-ring/inter-region-routed
  extraction. `layout/pex/build.py`'s own docstring names the concrete
  upstream blocker (a `klt extract`/`klt lvs` net-naming ambiguity on the
  physically assembled `ro_ring11`/`combiner_sampler` geometry) and the
  generic tool-gap issue filed against it. When that lands, the resulting
  records are new `level: extracted` records whose Caveats state the fuller
  coverage — this DR does not need to change for that to happen.
- **Wanted, same friction-protocol scope as DR-0022's**: `klt` output that
  discloses net-to-pin correspondence positionally and unambiguously for a
  flattened extraction of an assembled block with internally-repeated
  sub-cells, so a downstream composition does not have to guess which
  extracted header position is the true external port.

[DR-0005]: DR-0005-sim-harness-record-granularity.md
[DR-0009]: DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0021]: DR-0021-gate-level-timing-and-power-records.md
[DR-0022]: DR-0022-post-route-gate-level-simulation-records.md
[sim/README.md]: ../../sim/README.md
