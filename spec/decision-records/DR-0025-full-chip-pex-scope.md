---
dr: DR-0025-full-chip-pex-scope
title: Scope a full-chip PEX path to the inter-region nets whose driver and receiver are both already transistor-level, and not to the whole composed stream
status: Accepted
date: 2026-09-12
deciders: Builder (issue #225), under the same delegated-methodology rule DR-0009, DR-0021, DR-0022 and DR-0024 were accepted under. Not an operator ratification — see Status. It changes no ratified row, relaxes no ratified claim, and adds no `level:` value; it fixes what the next post-layout increment is allowed to be about.
supersedes: n/a
superseded_by: n/a
related: "#225 (origin, the scope decision this record IS), #219/#221/#222 (the composed, routed floorplan that made the question answerable at all), #217 (the intra-region routing-level extraction this would extend), #17 (the device-level extraction both sit on top of), DR-0024 (the `level: extracted` record kind these records would carry — unchanged by this decision, see Consequences), DR-0021/DR-0022/DR-0023 (the gate-level path that already owns the digital section's own timing and power), DR-0010 (the Proposed raw rate whose sizing margin is the measurement this scoping is chosen to move), #224 (digital's vddd/vss PDN tie, explicitly not in scope here); README §Target specification — no row is edited by this record"
---

# DR-0025: Scope a full-chip PEX path to the inter-region nets whose driver and receiver are both already transistor-level, and not to the whole composed stream

## Status

- 2026-09-12: **Accepted** by the Builder of #225. Delegated methodology, in
  the same sense and with the same correctability as [DR-0009], [DR-0021],
  [DR-0022] and [DR-0024]: it fixes what the *next* post-layout increment is
  allowed to be about, not what the block must do. A later DR supersedes it
  rather than editing it. No ratified row moves and no existing record is
  edited or re-labelled.

**No full-chip extraction output informed the scope below**, which is issue
#225's own first acceptance criterion (the decision is recorded before any
extraction is run). Every number below is either read out of an artefact
already committed on `main` (`layout/floorplan/reports/interregion.json`,
`layout/pex/*.spice`, `sim/records/`) or computed analytically from
committed geometry and the `klt` gf180mcu deck's own published parasitics
coefficient table. Nothing below is a simulation result, and nothing below
is cited as one; the estimates are labelled as estimates everywhere they
appear, per this repository's own "no claim without a testbench" rule.

Disclosed rather than omitted: a full-chip `klt extract --parasitics` run
*was* started while this record was being written, as a **runtime
feasibility probe only** — see "Runtime, measured as far as it went" under
Consequences. Its netlist and its `parasitics` block were not read, and no
figure in this record comes from it. Had it been read, the honest thing
would have been to say so and let a reviewer discount the scope
accordingly; it was not, and the scope stands on the committed-artefact
arithmetic above.

## Context

### What changed, and what question it opened

Until issue #222 there was no full chip to extract. `layout/floorplan/`
placed four guarded regions (`ring1`, `ring2`, `combiner_sampler`,
`digital`) with a 20 um isolation channel and **no wiring at all** between
them — `layout/pex/build.py`'s own "Out of scope" section recorded the
empirical signature (`klt extract --top trng_floorplan` reporting 2588
top-level pins for what should be a ~12-pin block, i.e. the regions were not
electrically joined).

#222 (merged via PR #226, on `main` as of `143b029`) draws real Metal4
trunks and Metal3 risers across those channels for every net
`design/floorplan_netlist.py` declares. Verified against the committed
evidence, not the PR description: `layout/floorplan/reports/floorplan.drc.json`
records `status: "clean"`, and `layout/floorplan/reports/interregion.json`'s
`check.lvs` records `status: "match"` (`mismatch_count: 2`, both categorized
`topology.flattened`).

So a full-chip parasitic extraction is now *possible*. Issue #225 exists
because "possible" is not "worth doing", and because the shape of a
full-chip PEX path is not obvious: both existing paths in
`layout/pex/build.py` are **intra**-region (they re-run a single block's own
netlist with device-level or routing-level parasitics annotated), and
neither reads the composed floorplan stream at all.

### What is actually out there to extract

`layout/floorplan/reports/interregion.json` records the as-built geometry of
all fourteen drawn inter-region nets. Every trunk is Metal4 at
`WIRE_W = 0.30 um` (`layout/floorplan/interregion.py`). The `klt` gf180mcu
deck's own curated parasitics table gives Metal4 `sheet_res = 0.09 ohm/sq`,
`cap_area = 0.007602 fF/um^2`, `cap_perim = 0.028153 fF/um` — which is the
same table `klt extract --parasitics` itself uses, so the arithmetic below
is a *preview* of that extractor's own lumped model, not an independent
physical model:

| Net | Role | Trunk (um) | Est. C (fF) | Est. R (ohm) | Endpoints |
|---|---|---:|---:|---:|---|
| `raw_bit` | raw_tap | 524.77 | 30.8 | 157 | `combiner_sampler.raw_bit` → `digital.raw_bit` |
| `raw_valid` | raw_tap | 446.61 | 26.2 | 134 | `combiner_sampler.raw_valid` → `digital.raw_valid` |
| `vss` | ground | 430.23 | 25.2 | 129 | `ring1` / `ring2` / `combiner_sampler` |
| `clk` | clock | 353.78 | 20.7 | 106 | `digital.clk` → `combiner_sampler.clk` |
| `ring_bit1` | liveness_tap | 343.16 | 20.1 | 103 | `combiner_sampler.ring_bit1` → `digital.ring_bit[0]` |
| `rst_n` | reset | 339.34 | 19.9 | 102 | `digital.rst_n` → `combiner_sampler.rst_n` |
| `ring_bit2` | liveness_tap | 265.47 | 15.6 | 80 | `combiner_sampler.ring_bit2` → `digital.ring_bit[1]` |
| **`ro1`** | **entropy_tap** | **128.40** | **7.5** | **39** | **`ring1.ro` → `combiner_sampler.rn1`** |
| **`ro2`** | **entropy_tap** | **35.92** | **2.1** | **11** | **`ring2.ro` → `combiner_sampler.rn2`** |
| `en1`, `en2` | control | 3.30 | 0.2 | 1 | chip pin → `ring1.en` / `ring2.en` |
| `vddr1`, `vddr2`, `vdd` | supply | 3.30 | 0.2 | 1 | chip pin → its own region |

Trunks only; the Metal3 risers are a few um each and contribute well under
1 fF apiece. These are first-order estimates, not extraction output.

### The three questions #225 asked, answered

**1. Are the inter-region routing parasitics a new order of magnitude?**
For two nets, yes, and for a specific reason: they land on the *lightest*
nodes in the design. `layout/pex/ro_ring11.routed.extracted.spice`, already
committed, gives each ring's eleven inter-stage nets a combined **24.87 fF**
of extracted capacitance, of which the `ro` net alone carries 8.16 fF
(`ring1`) / 7.89 fF (`ring2`) — it is the ring's longest internal wire, the
wrap link. The `ro1` trunk's estimated 7.5 fF would land on top of exactly
that node, roughly **doubling** it.

Sizing what that would do, by linearizing this repository's own already-measured
routed-vs-leaf delta (§7.1 of `sim/characterization-post-layout-extracted.md`:
ring 1's period went 12.349 ns → 17.426 ns when 24.87 fF of ring-internal
signal-net capacitance was added, i.e. ≈ 0.20 ns/fF at the entropy-binding
corner):

- `ring1`: +7.5 fF ⇒ **≈ +1.5 ns, ≈ +9 %** on `period_r1`.
- `ring2`: +2.1 fF ⇒ **≈ +0.4 ns, ≈ +3 %** on `period_r2`.

A linearization of one measured pair of points is a sizing argument, not a
result — but +9 % is far outside anything that could be dismissed as
rounding, and it is the same direction and roughly the same magnitude as
increments this repository has previously judged worth recording.

**2. What to do about `digital`'s ~2500 standard-cell instances?**
Leave them abstracted. `klt extract --abstract-cells
'gf180mcu_fd_sc_mcu9t5v0__*'` is what every existing extraction of the
composed stream already does (`layout/digital/lvs.py`,
`layout/floorplan/floorplan.py`'s `run_extract_composed`), and it is what
the composed LVS reference is written against. The alternative —
transistor-level extraction of the whole chip — is argued down below; the
short version is that the digital section's timing and power are already
owned by a *better* evidence path ([DR-0021]/[DR-0022]/[DR-0023],
post-route gate-level STA and power against the real routed DEF), and that
path is not improved by re-deriving it in ngspice.

**3. What claim would it support?** `sim/characterization-post-layout-extracted.md`
§7.1 and §7.6: the entropy-binding-corner ring period, and through it the
[DR-0007] §2 sizing margin at [DR-0010]'s own stated jitter-energy constant
— the number that went 0.865× → 0.442× when intra-region routing was
included, and the one number in this repository that a Proposed-but-unratified
spec row turns on. Secondarily §7.3 (startup) and §7.4 (power), which read
off the same netlist.

### The load-bearing filter

The reason this decision can be narrow rather than a judgement call is a
structural property of the deck, not a preference:

> **A trunk's parasitics change a number this repository can measure only if
> both ends of that trunk are already inside a transistor-level deck.**

- If the **receiver** is abstracted (`digital`), the added trunk C is a real
  load on a transistor-level driver — it changes that driver's own slew and
  its share of the analog power term — but the receiving gate's input
  capacitance is not modelled at all, so the *net* is only partly
  represented and no arrival-time claim can be made from it.
- If the **driver** is abstracted (`digital` driving `clk`/`rst_n`), the
  existing decks replace it with an ideal ngspice source. Putting the
  trunk's ≈106 ohm and ≈21 fF in front of a 0-ohm ideal source produces
  ≈2 ps of RC on an edge measured in tens to hundreds of ps. The
  interesting question there — *can `digital`'s own clock driver drive
  21 fF of trunk?* — is a drive-strength question about a standard cell,
  answerable by feeding the trunk's extracted load into the post-route STA
  ([DR-0022]'s path), and not by an ngspice run over an ideal source.
- `ro1` and `ro2` are the **only** two inter-region nets with a
  transistor-level device at each end (a ring's own last `ro_stage` driving
  a `ro_buf`'s gate, both extracted, both already in
  `sampler_core.routed.extracted.spice`).

## Decision

**A full-chip PEX increment is worth building, in exactly one form: extract
`layout/floorplan/trng_floorplan.gds` with `--parasitics` at the same
cell-instance granularity the composed LVS already uses, take from it only
the *inter-region* net parasitics, and simulate only the nets whose driver
and receiver are both already transistor-level — today `ro1` and `ro2`.
A blanket transistor-level extraction and simulation of the composed stream
is rejected.**

Concretely, the increment this record authorises is:

1. **Extraction.** `klt extract layout/floorplan/trng_floorplan.gds --deck
   gf180mcu --top trng_floorplan --parasitics --pdk gf180mcuD
   --abstract-cells 'gf180mcu_fd_sc_mcu9t5v0__*' --pins <the composed
   reference's own `.SUBCKT trng_floorplan` header> --def-net-names` — i.e.
   `floorplan.py`'s own `run_extract_composed` invocation plus
   `--parasitics`, so the extraction the composed LVS is already held to and
   the extraction the parasitics come from are the same run shape, not two
   divergent ones.
2. **What is taken from it.** The per-net R/C of the inter-region nets only,
   as a **delta** over what the intra-region extractions already carry. The
   full-chip extraction's `ro1` net is the ring's own internal wrap wire
   *plus* the trunk *plus* the riser *plus* `combiner_sampler`'s own `rn1`
   stub, all merged; `ro_ring11.routed.extracted.spice` and
   `combiner_sampler.routed.extracted.spice` already carry the first and
   last of those. Adding the merged value on top of them would double-count,
   and the increment must subtract rather than sum. Any composition that
   cannot show its arithmetic closes must fail loudly rather than compose.
3. **What is simulated.** `sampler_core.routed.extracted.spice`'s existing
   topology, with that delta inserted between each ring wrapper's `ro` port
   and `combiner_sampler`'s `rn1`/`rn2`, and (disclosed as driver-side-only,
   per the filter above) as added load on `raw_bit`/`raw_valid`/
   `ring_bit1`/`ring_bit2`.
4. **Which measurements are re-run.** The entropy-binding corner (§7.1),
   startup (§7.3) and power (§7.4) families, at the same binding corners
   #17 and #217 used, as new sibling testbenches. Each produces new
   `level: extracted` records, one P/V/T point per record ([DR-0005]), with
   `corner.process`/`voltage`/`temperature` filled in — never `n/a` — and
   seeds recorded for every stochastic run.
5. **What the records' Caveats must say**, in addition to [DR-0024]'s
   existing requirement: that the digital section is at **cell-instance
   granularity, not transistor level**, so no number in the record is
   evidence about a standard cell's own devices; and that `clk`/`rst_n`
   arrival is still driven from an ideal source, so the record says nothing
   about clock-tree arrival at the sampler.

Explicitly **not** in this increment, and not owed by it:

- Device-level extraction or ngspice simulation of any
  `gf180mcu_fd_sc_mcu9t5v0__*` instance.
- Any arrival-time, setup/hold or clock-tree claim across a region boundary.
  That is [DR-0021]/[DR-0022]'s path.
- IR drop on the shared `vss` trunk (≈129 ohm, the one trunk that spans the
  row). That is a static supply analysis with its own methodology, not a PEX
  re-run, and it needs a current profile this increment does not produce.
- `vddd`/`vss`'s tie into `digital`, which is #224.
- Any change to the drawn inter-region routing itself (#222) or to the
  regions' own internal layout.

## Alternatives considered

### A. Blanket full-chip, transistor-level PEX

- **What**: extract the composed stream *without* `--abstract-cells`, so the
  ~2500 standard-cell instances come back as real devices, and simulate the
  whole thing.
- **Why plausible**: it is what "full-chip PEX" means in ordinary usage, and
  it is the only construction that would make the four `digital`-facing
  trunks (`raw_bit`, `raw_valid`, `ring_bit1`, `ring_bit2`, `clk`, `rst_n`)
  fully represented rather than driver-side-only.
- **Why rejected**: three independent reasons, any one of which is
  sufficient.
  1. **It answers a question already better answered.** The digital
     section's timing and power are measured post-route, against the real
     routed DEF, by [DR-0021]/[DR-0022]/[DR-0023]. An ngspice re-derivation
     would be a *less* trustworthy second opinion (no SDF, no library
     characterisation, no multi-corner liberty), not a more trustworthy one.
  2. **Runtime.** ~2500 instances at roughly 10–20 devices each is tens of
     thousands of transistors with a full parasitic star on every net, in a
     simulator this repository already runs for minutes to hours on ~200
     devices — and the entropy-relevant testbenches are transient-*noise*
     runs, the most expensive kind, repeated per seed and per corner.
  3. **LVS pairing.** Nothing in this repository has ever built a
     transistor-level reference for the composed chip to pair a flat
     transistor-level extraction against, and this design has already met
     one instance of that class of problem (closed
     [klayout-tools#1533](https://github.com/2AMLogic/klayout-tools/issues/1533)
     — composing an unrelated extra block destabilised ambiguous-net-pairing
     resolution). Building the reference is a larger piece of work than the
     extraction it would validate, for a result reason (1) says is not
     wanted.

### B. Scope it to the `clk` trunk and re-run the DR-0012 sampling path

- **What**: #225's own suggested framing — "re-running the DR-0012 sampling
  path with the real `clk` trunk's RC in it".
- **Why plausible**: `clk` is the second-longest signal trunk (353.78 um)
  and the sampling path is where [DR-0012]'s fixed-external-clock decision
  bites; it looks like the natural place for a floorplan-level parasitic to
  matter.
- **Why rejected**: measured against the deck's own coefficients, the trunk
  is ≈106 ohm and ≈21 fF, and every deck in `sim/tb/` drives `clk` from an
  ideal ngspice source with zero output impedance. ≈2 ps of series RC in
  front of an ideal source is not a measurement — it is a no-op dressed as
  one, and recording it would be exactly the kind of "we ran the full-chip
  extraction" claim this repository's evidence rules exist to prevent. The
  real `clk` question is whether `digital`'s own clock driver can drive
  21 fF, which is a gate-level drive-strength question ([DR-0022]'s path,
  by loading the trunk's extracted C into the post-route STA), not an
  extracted-netlist ngspice question. Filed as the follow-up below rather
  than folded in here.

### C. Do nothing — record the decision as "not worth building yet"

- **What**: close #225 with a scope decision that defers the build
  indefinitely.
- **Why plausible**: §0.1 of `sim/characterization-post-layout-extracted.md`
  already establishes that every post-layout degradation this repository
  reports is a **floor, not a ceiling** — inter-region parasitics can only
  add capacitance and resistance, never remove it. Every ratified README row
  is already decided (§7.6: "no ratified README row's pass/fail verdict
  changes"), so no *ratified* verdict is waiting on this number, and a
  known-direction, unmeasured increment is a legitimate thing to leave on
  the shelf.
- **Why rejected**: the ≈+9 % first-order estimate on `period_r1` is too
  large to leave as "direction known, magnitude unknown" on the one number
  a live spec proposal turns on. [DR-0010]'s rate is `Proposed`, and
  [DR-0007] §2's margin at that rate has already moved 0.865× → 0.442× once
  for exactly this reason; whoever eventually rules on DR-0010 should not
  have to rule on a number with a known, unpriced 9 %-scale correction still
  outstanding. The cost of the narrow increment is small (one extraction of
  a stream that is already extracted on every floorplan check, plus a
  re-run of three testbench families that already exist), so "cheap and
  decision-relevant" beats "known direction".

### D. A new `level:` value for floorplan-level records

- **What**: what #225's own Affected Files section anticipated — amending
  [DR-0024], or adding a sixth `level:` sibling (`level: extracted-chip`)
  for records whose DUT carries inter-region parasitics.
- **Why plausible**: [DR-0022] and [DR-0024] both added a `level:` value
  precisely when the citation rule changed, and inter-region coverage is a
  genuinely different coverage claim from intra-region coverage.
- **Why rejected**: the citation rule does **not** change, and [DR-0024]
  already legislated this exact case. Its own Consequences section says a
  future extraction with fuller routing coverage produces "new records at
  this same level ... a record with fuller routing coverage says so in its
  own Caveats rather than needing a new `level:` value", and its Decision
  already *requires* every `level: extracted` record's Caveats to state
  "whether inter-cell/inter-region routing parasitics are included". A
  floorplan-level record satisfies that rule by answering "yes, for these
  two nets" instead of "no". Adding a sixth value would split a filter
  readers already have to read Caveats behind, for no gain. **DR-0024 needs
  no amendment, and this record makes none.**

## Consequences

- **Positive**:
  - The next post-layout increment has a written scope that fits in one
    issue: one extraction invocation (a flag added to one this repository
    already runs on every floorplan check), one delta computation, one
    composed netlist, three existing testbench families re-run at corners
    that are already chosen.
  - The two questions that *look* like full-chip PEX questions but are not
    — the digital section's own timing/power, and clock arrival at the
    sampler — are routed to the evidence path that actually owns them
    ([DR-0021]/[DR-0022]) instead of being answered badly here.
  - `layout/pex/build.py`'s "Out of scope" section stops being a statement
    about a *blocker* (which is now stale — the blocker is gone) and becomes
    a statement about a *choice*, with this record behind it.

- **Negative / accepted cost**:
  - Six of the fourteen inter-region nets (`clk`, `rst_n`, `raw_bit`,
    `raw_valid`, `ring_bit1`, `ring_bit2`) stay partly modelled — real
    trunk load on a real driver, no receiver gate capacitance — and every
    record produced under this scope must say so. That is a genuine, stated
    coverage hole, not a silent one.
  - `sim/characterization-post-layout-extracted.md`'s "floor, not ceiling"
    framing survives this increment: even with `ro1`/`ro2` priced, the
    numbers remain a floor, because the unpriced receiver-side capacitance
    can still only add load.
  - The scope is drawn by *what this repository can currently simulate*, not
    by what is physically largest. `raw_bit`'s 524.77 um trunk is the
    biggest parasitic on the chip and it is not fully priced by this
    increment. If the digital section ever gains a transistor-level model,
    that filter changes and so does this scope — see Revisit if.

- **Runtime, measured as far as it went** (the feasibility probe disclosed
  under Status — a cost input, not a scope input): `klt extract
  layout/floorplan/trng_floorplan.gds --parasitics --abstract-cells
  'gf180mcu_fd_sc_mcu9t5v0__*' --pins <composed header> --def-net-names`
  **had not completed after ~19.5 minutes** of wall clock on the host this
  record was written on (`klt 0.4.0+g3fbb4478e301`, macOS/arm64), and was
  terminated rather than waited out. Two caveats, both understating and
  overstating: for roughly the first third of that window a duplicate copy
  of the same command was accidentally running and competing for CPU, so the
  figure is pessimistic; and it is a single, uninstrumented observation on
  one host, not a benchmark. Treat it as "tens of minutes, order of
  magnitude" and nothing finer. Two consequences for whoever builds the
  increment: budget the runtime explicitly (this is not a step that can be
  bolted onto an interactive check the way the non-`--parasitics`
  floorplan extraction is), and expect to need `klt extract --rerun` or an
  equivalent caching strategy so the composition step can be iterated
  without re-paying it. Neither changes the scope decided above — the
  extraction is run once per layout revision either way.

- **Follow-up required**:
  - Build the increment authorised above (its own issue, filed from #225),
    with the runtime figure above budgeted into it.
    Until it exists, no record in this repository may be cited as full-chip
    post-layout evidence.
  - Feed the six `digital`-facing trunks' extracted capacitance into the
    post-route STA as an interface load, under [DR-0022]'s path — the
    correct home for the `clk` drive-strength question Alternative B
    declines. Its own issue.
  - IR drop on the shared `vss` trunk, if and when a current profile exists
    to run it against.

- **Revisit if**:
  - The extraction authorised above returns an `ro1`/`ro2` delta materially
    different from the ≈7.5 fF / ≈2.1 fF estimated here (the estimate is a
    trunk-only, lumped, deck-coefficient calculation; risers, vias and
    vertical-overlap coupling to the trunks above and below are not in it).
    A large discrepancy means the sizing argument that justified this scope
    was wrong, and the scope should be re-derived from the measured values.
  - A transistor-level model of the digital section ever exists, for any
    reason — the "both ends transistor-level" filter would then admit six
    more nets, including the two longest on the chip.
  - The inter-region routing is redrawn (#222's geometry changes), moving
    the trunk lengths this record's arithmetic is built on. Re-count against
    `layout/floorplan/reports/interregion.json` rather than trusting the
    table above.

[DR-0005]: DR-0005-sim-harness-record-granularity.md
[DR-0007]: DR-0007-multi-ro-xor-combined-entropy-source.md
[DR-0009]: DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0010]: DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0012]: DR-0012-sampler-fixed-external-clock.md
[DR-0021]: DR-0021-gate-level-timing-and-power-records.md
[DR-0022]: DR-0022-post-route-gate-level-simulation-records.md
[DR-0023]: DR-0023-power-rollup-digital-term-becomes-measured-gate-level-power.md
[DR-0024]: DR-0024-extracted-netlist-record-level.md
