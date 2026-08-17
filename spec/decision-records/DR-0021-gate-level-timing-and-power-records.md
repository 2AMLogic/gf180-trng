---
dr: DR-0021-gate-level-timing-and-power-records
title: Record static timing and power analysis as a third verification level, `level: gate`, which keeps real corner fields
status: Accepted
date: 2026-08-17
deciders: Builder (issue #145), under the same delegated-methodology rule DR-0009 was accepted under. Not an operator ratification — see Status. It changes no ratified row and no ratified claim; it names a record kind that DR-0009's own follow-up asked for and could not classify.
supersedes: n/a
superseded_by: n/a
related: "#145 (origin), DR-0009 (the two-level split this record extends, and whose rule 6 and Follow-up section explicitly left digital timing closure unowned), #143/#111 (the synthesis and place-and-route runs that made a gate-level record possible at all), #124 (T1 checklist items 5 and 8), DR-0003 (the ratified raw rate whose clock this sweep's power leg reports at), DR-0005 (one record per corner), sim/README.md (the record format this record adds a `level:` value to); README §Target specification — no row is edited by this record"
---

# DR-0021: Record static timing and power analysis as a third verification level, `level: gate`, which keeps real corner fields

## Status

- 2026-08-17: **Accepted** by the Builder of #145. Delegated methodology, like
  DR-0009: it fixes what a record *is*, not what the block must do, and it is
  correctable by a superseding DR rather than by editing this one. No ratified
  row moves, and no existing record is edited.

## Context

[DR-0009] split recorded evidence in two and made every record say which side
it came from:

- `level: transistor` — ngspice, device models, a single P/V/T point per
  record, full `pdk`/`pdk.models`/`tool.ngspice`/`corner.*` frontmatter.
- `level: behavioral` — a bit-exact executable model, **no** device models,
  and therefore `corner.process`/`corner.voltage`/`corner.temperature`
  written as `n/a` with a reason, plus the standing rule that such a record
  "may not be cited for any claim that depends on process, voltage or
  temperature".

That taxonomy was written when this repository had no synthesis and no
place-and-route flow, and DR-0009 said so in as many words. Its rule 6:

> **Digital timing closure is not covered by either side and remains owed.**
> Nothing in this split shows that the digital blocks meet timing at `ss` /
> −10 % / +125 °C. That is a post-synthesis static-timing question against
> the gf180mcu liberty files, and no issue owns it yet.

and its Follow-up: *"New issue wanted: stand up a synthesis + static-timing
flow … so rule 6's gap can be closed. Nobody owns this today."*

That flow now exists — #143 (synthesis), #111 (place-and-route), #145 (this
corner sweep) — and its output fits neither existing level:

- It is **not** `transistor`. No device model is instantiated and ngspice is
  never invoked. Cell delays, internal energies and leakages come from the
  PDK's characterised liberty tables.
- It is **not** `behavioral` either, and labelling it so would be actively
  wrong. A liberty deck *is* a process/voltage/temperature point
  (`ss_125C_3v00` is slow-process, 125 °C, 3.00 V, and the deck states those
  as `nom_process`/`nom_temperature`/`nom_voltage` in its own header). A run
  against it moves with the corner in exactly the way DR-0009 rule 3 forbids
  a behavioral record from claiming — and the *reason* to run it at all is
  that it moves with the corner. Writing `corner.process: n/a` on a record
  whose whole content is a corner comparison would make the frontmatter lie.

Leaving it unlabelled is not available either: DR-0009 rule 1 requires every
new record to state its level, and "absence means `transistor`" would be the
worst of the three readings.

## Decision

Add a **third** value to `sim/README.md`'s `level:` field: **`gate`**.

### 1. What a `level: gate` record is

A record produced by static analysis of a **synthesized or placed-and-routed
gate-level netlist** against the PDK's own characterised standard-cell
libraries — static timing analysis, liberty-table power, and geometry read
from a placed/routed database. Today that means OpenSTA/OpenRCX inside
OpenROAD, driven by `sim/tb/digital-sta-power/run_sta.py`; the level is
defined by what the evidence *is*, not by which binary produced it.

### 2. A `gate` record carries real corner fields

`corner.process`, `corner.voltage` and `corner.temperature` are filled in
from the liberty deck's own operating conditions, never `n/a`. In addition:

- `corner.liberty` names the deck (`<library>__<corner>`), because
  "`ss`/125 °C/3.00 V" alone does not identify which library or which
  characterisation produced the numbers;
- `corner.interconnect` names the parasitic corner, because for a routed
  block a timing corner is a *(device, interconnect)* pair and the two axes
  move independently;
- `pdk.models` lists the liberty deck, both LEFs and the extraction rule
  deck, each with a content hash — the gate-level equivalent of a
  transistor-level record naming its model sections;
- `tool.ngspice` is written `n/a` **with the reason** (the same rule every
  inapplicable field already follows), and the tool that did produce the
  numbers is named alongside with its version.

### 3. What a `gate` record may be cited for, and what it may not

**May**: timing closure and slack, Fmax, standard-cell area, and liberty-model
power and leakage — each at the corner the record names, and each as a
property of the *implementation* (this netlist, this placement, this routing)
rather than of the RTL.

**May not**:

- **Anything the library itself is the source of truth for.** A gate record
  re-derives no device physics; it is downstream of the characterisation, so
  it can never be evidence *about* it.
- **A supply-current measurement.** Liberty power under a declared switching
  activity is a model evaluated at a corner, not a measured current. Where a
  transistor-level record exists for the same quantity (the entropy source's
  own `p_total_w`), the transistor record wins and the gate record does not
  average with it.
- **Entropy, jitter, metastability or any raw-tap claim.** Those live
  strictly upstream of this level, per DR-0009 §4, which is unchanged.
- **Signoff.** Absent a foundry-signed extraction and a power delivery
  network, a gate record is characterisation evidence, not sign-off.

Every such record states these limits in its own Caveats section; the rule is
not carried by this DR alone.

### 4. Corner granularity, unchanged

[DR-0005]'s rule holds: **one record per corner**, never one record with a
table of corners. A gate-level sweep over 5 liberty decks × 3 interconnect
decks is 15 records, not one.

The corner *set* is not free the way the analog side's is. `sim/harness/
corners.py` sweeps {tt, ss, ff} × {−40, 27, 125} °C × {2.97, 3.30, 3.63} V =
27 points because a device model takes P, V and T as independent inputs. A
liberty deck is a characterised bundle: `gf180mcu_fd_sc_mcu9t5v0` ships five
in this block's ratified 3.3 V family and no others, so a gate-level sweep
covers those five and says so, rather than interpolating a grid the library
does not characterise. The interconnect axis is swept in full (`min`/`nom`/
`max`), since the PDK ships all three.

### 5. What does not change

DR-0009 is not superseded and nothing in it is relaxed. The
behavioral/transistor boundary still sits exactly at the DR-0001 raw tap; the
five behavioral testbenches keep `level: behavioral` and keep their `n/a`
corner fields; CLAUDE.md's "PVT corners on every recorded result" keeps its
single bounded exception (behavioral records) and gains no second one — a
`gate` record *has* a corner and states it.

## Alternatives considered

### Call it `level: transistor`

- **Why plausible**: the numbers ultimately descend from transistor-level
  characterisation of the standard cells, and the record does carry a real
  P/V/T point, so every frontmatter field would be fillable.
- **Why rejected**: it would put liberty-table arithmetic and a
  transient-noise ngspice run in the same bucket, and the difference between
  them is exactly what a reader checking a power or timing claim needs to
  see. It would also make "no entropy, rate, or power claim may be made from
  anything other than a transistor-level record" (DR-0009 §1) silently admit
  a source DR-0009 never contemplated.

### Call it `level: behavioral`

- **Why plausible**: no device models are instantiated, which is the literal
  test DR-0009 §2 applies, and it needs no new taxonomy.
- **Why rejected**: it forces `corner.*: n/a` on a record whose entire
  content is a corner comparison, and DR-0009 rule 3 would then forbid citing
  the record for the timing and power claims it exists to make. The
  classification would have to be violated for the record to be usable, which
  is the strongest possible sign it is the wrong classification.

### Keep two levels and put STA results outside `sim/records/` entirely

- **What**: leave the sweep's output in `layout/digital/reports/` as JSON, and
  cite that from the characterization document.
- **Why plausible**: it is where the place-and-route report already lives, and
  it needs no DR at all.
- **Why rejected**: `sim/README.md`'s opening rule is that "a simulation
  result that is not recorded here in this format is not evidence, and must
  not be cited in `spec/`, in an issue, or in a summary document". A
  per-corner timing and power sweep is precisely the kind of result that rule
  exists for — append-only, one corner per record, checksummed raw output,
  reproduce command included. Exempting it would create a second, weaker
  evidence area whose first inhabitant is a set of numbers destined for the
  README's own rows.

### Add the level, but also add a `level: layout` for DRC/LVS results

- **Why plausible**: `layout/reports/*.drc.json` is another kind of evidence
  with another kind of provenance, and one taxonomy pass could cover both.
- **Why rejected**: one decision per record (the DR convention), and the two
  are not the same problem. DRC/LVS verdicts are not corner-swept, are not
  cited for any P/V/T-dependent claim, and already have a home with its own
  freshness gate (`layout/verify.py`). Nothing in this record's argument
  applies to them, and nothing here blocks such a record if one is ever
  wanted.

## Consequences

- **Positive**:
  - DR-0009 rule 6's gap ("digital timing closure is not covered by either
    side") stops being a gap: the evidence has a level, a format, a corner
    set and a citation rule.
  - The distinction a reader most needs — *was this measured on devices, or
    evaluated from library tables?* — is visible in one frontmatter field
    instead of inferred from the testbench's name.
  - A gate record's mandatory `corner.liberty` / `corner.interconnect` fields
    make the two independent corner axes of a routed block explicit, which
    the place-and-route report's single-corner shape could not express.

- **Negative / accepted cost**:
  - **Three levels now coexist in one append-only directory.** DR-0009
    already priced two as a real burden on the reader; this adds a third. The
    mitigation is that a `gate` record is conspicuous in the other direction
    from a behavioral one (it carries a corner *and* a liberty deck name),
    and that every `gate` record's Caveats section restates its own limits.
  - **A `gate` record's corner set is narrower than the analog grid's**, so a
    "worst corner" from a gate record and one from a transistor record are
    minima over different sets and must not be compared as if they were not.
  - The tooling that consumes records (`sim/tools/*.py`) must not assume two
    levels. `sim/tools/digital_corner_characterization.py` is the first
    consumer written against three.

- **Revisit if**: a gate-level record is ever found cited for a raw-tap,
  entropy or jitter claim (rule 3's boundary would then need mechanical
  enforcement rather than a written rule); or a liberty family covering the
  block's supply at more than five P/V/T points ships, which would make the
  gate-level corner set comparable to the analog grid rather than a subset of
  its box; or post-layout SPICE of the digital section ever becomes
  affordable, which would give the same block a `transistor` record for a
  quantity a `gate` record already covers.

[DR-0005]: DR-0005-sim-harness-record-granularity.md
[DR-0009]: DR-0009-behavioral-vs-transistor-verification-split.md
