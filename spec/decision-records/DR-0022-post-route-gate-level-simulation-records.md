---
dr: DR-0022-post-route-gate-level-simulation-records
title: Record dynamic gate-level simulation as `level: gate-simulation`, a sibling of DR-0021's `level: gate` that may never be cited for timing closure
status: Accepted
date: 2026-08-17
deciders: Builder (issue #147), under the same delegated-methodology rule DR-0009 and DR-0021 were accepted under. Not an operator ratification — see Status. It changes no ratified row and no ratified claim; it names a record kind DR-0021 deliberately scoped itself away from.
supersedes: n/a
superseded_by: n/a
related: "#147 (origin), DR-0021 (the `level: gate` record kind this one is a sibling of, and whose frontmatter conventions it adopts wholesale), DR-0009 (the two-level split both extend; its rule 6 named digital timing closure as owed and DR-0021 closed that half), #111/#143 (the place-and-route and synthesis runs that produced the netlist simulated here), #124 (T1 checklist item 7, digital column — this record's origin), #176 (the model/RTL handoff skew #147's re-run found and which was fixed before this record was written), sim/README.md (the record format this record adds a `level:` value to); README §Target specification — no row is edited by this record"
---

# DR-0022: Record dynamic gate-level simulation as `level: gate-simulation`, a sibling of DR-0021's `level: gate` that may never be cited for timing closure

## Status

- 2026-08-17: **Accepted** by the Builder of #147. Delegated methodology, in
  the same sense and with the same correctability as [DR-0009] and [DR-0021]:
  it fixes what a record *is*, not what the block must do, and a later DR
  supersedes it rather than editing it. No ratified row moves, and no existing
  record is edited or re-labelled.

## Context

[DR-0021], accepted the same day for #145, added `level: gate` for a kind of
evidence neither DR-0009 level described, and defined it precisely:

> **static analysis of a synthesized or placed-and-routed gate-level netlist
> against the PDK's own characterised standard-cell libraries** — static
> timing analysis, liberty-table power, and geometry read from a
> placed/routed database.

#147's deliverable — T1 checklist item 7's digital column, the post-layout
re-run of the digital functional suite — reads the same netlist against the
same characterised libraries, and is **not static**. It elaborates
`layout/digital/trng_top.pnr.v` together with the library's timing Verilog
models, back-annotates cell delays from an SDF through Icarus's
`$sdf_annotate`, drives per-cycle stimulus at the top-level ports, and
compares every output cycle by cycle against the RTL the netlist was
synthesized from and against the behavioural model. That is a simulation, and
it produces a different kind of claim: *the implementation still behaves as its
source does, under annotated delay*.

Three ways to classify it were available.

1. **Label it `level: gate`.** Rejected: it would contradict the accepted
   definition quoted above, which says "static analysis" in as many words. A
   `level:` value whose own DR excludes half the records carrying it is worse
   than no value.
2. **Label it `level: behavioral`.** Rejected for the same reason DR-0021
   rejected it: a liberty deck *is* a P/V/T point, the run's delays come from
   one, and writing `corner.process: n/a` on a record whose content depends on
   that deck would make the frontmatter lie.
3. **A sibling value.** Adopted, for the reason in the next section — the
   citation rule genuinely differs, and that difference is exactly what a
   `level:` value exists to signal.

## Decision

**A record produced by dynamic simulation of a gate-level netlist carries
`level: gate-simulation`.** It inherits every frontmatter convention
[DR-0021] fixes for `level: gate`:

- `corner.process` / `corner.voltage` / `corner.temperature` are filled in
  from the liberty deck's own operating conditions — never `n/a` — alongside
  `corner.liberty` naming the deck, since P/V/T alone does not say which
  library or which characterisation.
- `pdk.models` lists every deck and cell-model file actually read, content-
  hashed.
- `tool.ngspice` is `n/a` **with the reason**, and every tool that did produce
  the numbers is named with its version. For a simulation that is more tools
  than for an analysis — the simulator, the cocotb/VPI layer, the driver, and
  the tool that wrote the annotation file — and all of them are recorded,
  because reproducibility depends on the whole chain.
- No `tb.json`: `sim/run_corners.py` must not sweep it across the analog P/V/T
  grid, because the corner is a characterised bundle rather than a free choice
  of three axes.

And it adds two requirements of its own.

**1. A `timing_annotation` block is mandatory, and it must state what the
annotation omits.** At minimum: which delay classes are modelled (cell,
interconnect), which annotation classes the simulator actually *applied* as
opposed to accepted, the annotation file with a content hash, and the corner
selected. An omission stated is a coverage limit; an omission unstated is a
defect — the same standing rule `Caveats` carries, made explicit here because
this is the field a reader has no other way to reconstruct.

**2. A `level: gate-simulation` record may never be cited for timing
closure, Fmax, or any margin claim — not even at the corner it names.** This is
the operative difference from `level: gate`, and it is not conservatism. Which
classes of an SDF a simulator applies is simulator-dependent and silent: the
first run under this level established, from the simulator's own transcript,
that Icarus Verilog 13.0 applies no SDF `TIMINGCHECK` section *and* implements
no `$setup`/`$hold`/`$width` at all — so 708 characterised setup/hold limits
and 1926 library timing checks were both dropped, and the run performed no
timing checking of any kind while reporting a clean pass. A gate-level
simulation that reports no timing violation therefore says nothing about
timing, and a taxonomy that let it share a `level:` value with STA would
invite exactly that misreading.

What such a record **may** be cited for: functional equivalence of the
as-built netlist to its RTL and/or its behavioural model, on the stimulus
actually run, at the annotated corner; and any behaviour the simulation
directly observed (a detection latency in cycles, an output word, an
unresolved-value count). Timing closure remains [DR-0021]'s `level: gate`
records' business.

## Consequences

- `sim/README.md` gains a fourth `level:` value and a section stating the
  table above. Nothing existing is re-labelled: `transistor`, `behavioral` and
  `gate` records keep their values and their citation limits.
- T1 checklist item 7's digital column can be closed by a `gate-simulation`
  record, and item 8's digital column can cite one — but neither may use it
  for a timing row, which stays with #145's `level: gate` sweep.
- The next dynamic gate-level run (a different corner, a longer stimulus, a
  post-PDN netlist) is a new record at this level, one per corner, under
  [DR-0005]'s unchanged granularity rule.
- If a future simulator *does* apply timing checks, requirement 2 does not
  automatically relax: the record would state that in its
  `timing_annotation` block, and relaxing the citation rule would need a DR
  superseding this one. That is the right friction — the failure mode being
  guarded against is a silently unchecked run reading as a checked one.

## Follow-up

- **Not owed by this record**: interconnect-delay annotation. The first run at
  this level models cell delay only, because the available route to routed
  parasitics extracts them from a DEF→GDS merge that is geometrically wrong by
  a factor of two (klayout-tools#1090) and an SDF wrong by a data-dependent
  factor is worse than one that models none. When that upstream defect closes,
  a new record at this level with interconnect delay annotated is a strict
  improvement, and its `timing_annotation` block will say so.
- **Wanted**: a simulator (or `klt` capability) that reports per-class
  annotation coverage rather than a boolean, so requirement 2's evidence does
  not have to be reconstructed by counting transcript lines. Filed generically
  upstream as klayout-tools#1102.

[DR-0005]: DR-0005-sim-harness-record-granularity.md
[DR-0009]: DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0021]: DR-0021-gate-level-timing-and-power-records.md
