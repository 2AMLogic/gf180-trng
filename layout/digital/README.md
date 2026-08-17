# `layout/digital/` — the digital section, placed and routed

`layout/cells/`, `layout/rings/` and `layout/blocks/` draw the entropy
source's analog and mixed-signal cells one at a time, by hand, each one
DRC-clean and LVS-matching on its own. That approach is the right (and
currently only) tool at the scale of a ring stage or a combiner gate, and it
does not extend to the digital section: conditioner + health tests +
interface synthesize to **2500-odd standard-cell instances, 708 of them
flip-flops** ([`design/trng_top/trng_top.synth.json`](../../design/trng_top/trng_top.synth.json),
issue #143). That is a place-and-route problem, and this directory is where
it is solved — [#111][gf111].

## The one command

```sh
python3 layout/digital/build.py       # run P&R, check the artefacts, write the report
```

It drives the already-committed gate-level netlist
[`design/trng_top/trng_top.synth.v`](../../design/trng_top/trng_top.synth.v)
through `klt place-and-route` (OpenROAD under the hood: floorplan → global
and detailed placement → clock-tree synthesis → global and detailed
routing), then runs its own checks over what came back and commits the
artefacts that pass them. Every number quoted below is produced by that
script and lands in [`reports/place_and_route.json`](reports/place_and_route.json);
nothing here is a figure somebody typed in.

Unlike [`design/synth.py`](../../design/synth.py) there is no `--check`
mode. Yosys's mapped netlist is byte-reproducible for the same RTL and
liberty, so a staleness guard is meaningful there. Placement and routing are
seeded but not byte-reproducible across `openroad` builds, thread counts or
host architectures, so there is no "is the committed result stale" question
to ask here. What is committed is one recorded run, carrying enough
provenance (`openroad` version and pinned image digest, `klt` version,
resolved PDK, liberty corner, seed) that another run can be *compared*
against it rather than assumed identical to it.

## What ran, and what it produced

| | |
|---|---|
| Input | `design/trng_top/trng_top.synth.v` — 2505 instances mapped against `gf180mcu_fd_sc_mcu9t5v0` (#143) |
| Tool | `klt place-and-route` → OpenROAD `26Q3-1260-g06a5a02279`, `target_stage: route` |
| Liberty corner | `gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00` (see [Corners](#corners)) |
| Constraint | `clk`, 50 ns period (20 MHz) — see [Timing](#timing) |
| Floorplan | 40 % target utilization, aspect ratio 1.0, 10 µm core margin, site `GF018hv5v_green_sc9` |
| Routing | signal layers Metal2–Metal5 (Metal1 left to pin access and intra-cell geometry) |

Committed artefacts:

| file | what it is |
|---|---|
| [`trng_top.def`](trng_top.def) | the routed DEF — OpenROAD's own output, and the re-entry point for any later STA/extraction run |
| [`trng_top.pnr.v`](trng_top.pnr.v) | the **as-built** gate-level netlist (`write_verilog` after CTS and resizing): the netlist a post-route gate-level simulation (#147) or a golden-reference LVS run must use, *not* `klt synthesize`'s pre-CTS one |
| [`trng_top.gds`](trng_top.gds) | the DEF merged with the standard cells' own GDS views — committed as of #170, once the merge's database-unit defect ([klayout-tools#1090][klt1090]) was fixed upstream; see [GDS, DRC and LVS](#gds-drc-and-lvs) |
| [`reports/place_and_route.json`](reports/place_and_route.json) | the full response, the request that produced it, provenance, and this script's own checks (`checks.gds_geometry.status: "ok"`) |
| [`reports/drc.json`](reports/drc.json) | `klt drc` over `trng_top.gds` — verdict and per-rule counts |

`layout/digital/lvs.py` (below) writes three more committed artefacts — the
mechanically-generated LVS reference SPICE, the extracted layout-side SPICE,
and [`reports/lvs.json`](reports/lvs.json) — see
[GDS, DRC and LVS](#gds-drc-and-lvs).

## Timing

Reported by OpenROAD's own pre-signoff STA at the requested corner, over an
ideal (SDC-only) clock with global-routing-estimated parasitics — no
extraction, no SPEF, no back-annotation:

| | |
|---|---|
| Worst slack at `ss_125C_3v00`, 50 ns period | **+27.7 ns** |
| Total negative slack | 0 ns |
| `fmax_mhz` (OpenROAD's own report) | 44.9 MHz |
| Setup / hold violations at that corner | 0 / 0 |
| Clock skew after CTS | 0.40 ns |
| Swept worst **hold** slack, all 15 shipped `.lib` corners | **+0.52 ns** |
| Swept worst **setup** slack, all 15 shipped `.lib` corners | **−28.8 ns** |

The last two rows are the ones that need reading carefully, because a
positive worst slack sitting next to a strongly negative *swept* setup slack
looks like a contradiction and is not one. They are different measurements:

- `worst_slack_ns`, `setup_violation_count` and `hold_violation_count` are
  **single-corner** numbers, at the corner the request names.
- `worst_setup_slack_ns` / `worst_hold_slack_ns` come from a second STA
  session that loads **every `.lib` file the library ships** and reports the
  worst value across all of them. This library ships 15, spanning **three
  different supplies** — roughly 1.8 V, 3.3 V and 5.0 V families, three
  process/temperature points each.

The block's ratified supply is **3.3 V** (`design/README.md`), so only 3 of
those 15 decks (`ss`/`tt`/`ff` at 3.00 / 3.30 / 3.60 V) describe an operating
point this block is specified for. The 1.62 / 1.80 / 1.98 V decks are also
the slowest the library ships — `ss_125C_1v62`'s own `inv_1` `cell_fall`
table starts at 0.154 ns against `ss_125C_3v00`'s 0.073 ns at the same
slew/load index point, 2.1× before the extra interconnect delay a weaker
driver pays — so the −28.8 ns is very probably theirs. "Very probably" is as
far as the recorded evidence goes: `klt` returns one number for the whole
sweep and never names the corner that produced it, filed generically upstream
as [klayout-tools#1092][klt1092]. What the recorded evidence does say
outright is that it is *not* the corner this block is implemented and
specified at, which closes with +27.7 ns.

What the sweep *does* establish outright is the hold result: **+0.52 ns worst
hold slack across all 15 decks**, including the fastest ones — and the fast
corner is exactly where hold binds, so that number is a real, unqualified
multi-corner result.

**What may be cited from this, and what may not.** The 50 ns constraint is
this run's own input, not a spec row: no issue in this repository has set a
digital-section Fmax requirement. The ratified requirement the clock rate
has to satisfy is the raw-rate row (`README.md`, [DR-0003][dr3]): > 1 Mbps
sustained at the sampler output, one raw bit per `clk` edge, so > 1 MHz, with
the stretch row at > 4 MHz. This run closes at 20 MHz with 27.7 ns of slack
at a slow-process/hot/−10 %-supply corner, which is 5–20× the rate the spec
asks for — that is a *margin statement about this implementation*, not an
Fmax claim, and not signoff. Corner-swept Fmax, area and power are #145's
deliverable, and it is #145 that gets to state them.

**It has**: [`sim/characterization-digital-sta-area-power.md`](../../sim/characterization-digital-sta-area-power.md)
re-times this directory's committed DEF at fifteen corners (five 3.3 V liberty
decks × three interconnect decks) with OpenRCX-extracted parasitics and a
*propagated* clock, and reports an Fmax floor of **37.04 MHz** at
`ss_125C_3v00` with `max` interconnect, positive setup and hold slack and zero
TNS at every corner. It also reconciles the +27.7 ns above with its own
+23.8 ns at the same liberty corner: 3.83 ns of that is extraction versus the
global-routing estimate, 0.145 ns is the real clock tree.

## Corners

The request names its liberty corner explicitly:
**`ss_125C_3v00`** — slow process, 125 °C, 3.00 V.

That is not `klt`'s default. This library is characterised at three supplies,
and `klt`'s nominal-corner resolution is documented to return the **lowest**
of them (`tt_025C_1v80`). Two reasons to override it here:

1. **The block runs at 3.3 V**, not 1.8 V (`design/README.md`: "the block's
   ratified 3.3 V supply"). Timing a 3.3 V block against a 1.8 V deck is not
   conservatism, it is the wrong operating point.
2. **3.00 V / 125 °C / slow process is the ratified binding corner.**
   [DR-0003][dr3]'s raw-rate row binds at `ss` / −10 % supply / +125 °C;
   3.3 V − 10 % = 2.97 V, and `ss_125C_3v00` is the closest deck this library
   ships. Implementing *at* the binding corner is what makes the slack figure
   above mean something.

**The synthesis/P&R corner mismatch is resolved ([#169][gf169]).**
`design/synth.py` used to take `klt`'s nominal-corner pick (`tt_025C_1v80`)
for the netlist this run consumes, so ABC's delay-driven cell/drive-strength
choices came from a 1.8 V timing model even though this P&R re-times
everything at 3.00 V. `design/synth.py` now pins its own liberty corner
explicitly too — **`tt_025C_3v30`**, not `ss_125C_3v00` — and the two scripts
deliberately land on *different* decks for different reasons:

- This P&R run implements *at* the ratified binding corner
  (`ss_125C_3v00`), because that is what makes its own slack figures mean
  something.
- `design/synth.py`'s ABC mapping is a pre-place step with no timing closure
  of its own (`klt synthesize` "does not perform signoff timing analysis");
  mapping it against the same worst-case corner would only bias cell
  selection toward larger-than-typical drive strengths before this script's
  own placement/CTS resizing gets a chance to size anything. `tt_025C_3v30`
  — typical process, the block's real 3.3 V supply — is the conventional
  synthesis target for exactly that reason, and it replaces the old 1.8 V
  pick with the right voltage family either way.

Re-running both scripts against the re-mapped netlist moved the input this
run consumes: `design/trng_top/trng_top.synth.json`'s reported area grew
~0.9 % (110 892 → 111 857 µm², same 2505-instance count, different
cell/drive-strength mix) and its ABC-estimated critical path fell from
16 967 ps to 6 443 ps (an artefact of timing at 3.3 V instead of 1.8 V, not a
signoff number either way — see that report's own `timing` field caveats).
This run's own figures above and in [Area](#area) are from that re-mapped
netlist.

## Area

| | |
|---|---|
| Die (from the request's own 40 % utilization target) | 548.8 × 548.8 µm = **301 198 µm²** |
| Core | 277 092 µm² |
| Achieved utilization | 40.8 % |
| Standard-cell area inside the core | ≈ 112 000 µm² |
| Routed wirelength | 163 650 µm |

**The die figure is an input, not a result.** It follows arithmetically from
the 40 % utilization this run asked for, chosen to leave routing headroom on
a first attempt whose question was whether this design routes at all. Do not
compare it against the `< 0.05 mm²` README row; the number to compare is the
cell area, and even that comparison has caveats:
[`layout/floorplan/README.md`](../floorplan/README.md)'s bottom-up inventory
estimate prices the digital region at 74 485 µm² of cell area from **1655
cells in the 7-track library**, while this run places **2499 instances of
9-track cells** (`checks.components`, 2505 synthesized minus 6 optimized
away during placement/CTS) — taller rows, and a different (post-synthesis,
real) cell count. The two numbers are not like-for-like, and reconciling them against
the ratified area row is #145's job (with [#150][gf150] owning the row
itself). What can be said here: real synthesis and placement land the digital
section's cell area ~1.5× above the inventory estimate, and the estimate was
already 2.5× the whole-block budget.

**#145 has since done that reconciliation**
([`sim/characterization-digital-sta-area-power.md`](../../sim/characterization-digital-sta-area-power.md)
§3): the placed cell area is **113 087.9 µm²**, ×1.518 the inventory estimate,
splitting into ×1.209 from cell count/mix and ×1.256 from 9-track rather than
7-track rows. The area row itself is still [#150][gf150]'s.

## Power

`estimated_power_mw: 6.4` — OpenROAD's own `report_power` at
`ss_125C_3v00` with estimated (not extracted) parasitics and no activity
annotation beyond its defaults. It is recorded because the tool reports it;
it is **not** a power result, it does not supersede
`design/digital_power_estimate.py`, and it is not a corner sweep.

**#145 has since done that comparison** —
[`sim/characterization-digital-sta-area-power.md`](../../sim/characterization-digital-sta-area-power.md),
from this directory's own committed DEF re-timed at fifteen corners with
extracted parasitics: 8.45 mW at this corner at 20 MHz and 424 µW at
DR-0003's ratified 1 MHz raw rate, under a declared 0.25 transitions/net/cycle
activity, against the library-based estimate's 16.7 µW. The delta and its
causes are that document's §4; nothing in this directory is edited by it.

## Two defects this bring-up found

The point of this repository is to run a real design through an open flow and
report what breaks. Two things did. Both are filed generically against the
tool, per this repository's friction protocol, and both are visible in the
committed report rather than smoothed over.

### 1. The merged GDS was geometrically wrong — [klayout-tools#1090][klt1090], fixed

`klt place-and-route` also merges the routed DEF with the standard cells' own
GDS views and returns a `gds_path`. That stream **was** 2× too big in every
DEF-derived dimension: placement coordinates, routed wires and via cells all
doubled, while the standard-cell geometry stayed at its true size, so the
cells sat on a stretched grid where abutting rows did not abut, rails did not
join, and the routing did not land on the pins it was routed to.

Root cause, reduced to eight lines: the merge set the LEF/DEF reader's target
database unit from the tech LEF (this PDK declares `DATABASE MICRONS 2000`,
i.e. 0.5 nm), read the DEF correctly at that unit, and then read the
standard-cell GDS — written at 1000 units/µm — into the *same* layout.
KLayout adopted the incoming stream's unit and did not rescale the geometry
already there, so everything from the DEF silently doubled. The DEF was
fine; only the merged GDS was wrong.

**Fixed upstream**, [klayout-tools#1114][klt1114], merged at commit
`a65e2bb4fe199725af49c6bf1ba37bd3d6be4cc7` and closing #1090. This repository
re-pinned `klt` past that fix — to `e501e261c1ac9b96a08e2c3569bf6207123a5b6a`,
which also carries [klayout-tools#1115][klt1115] (a gf180mcu DRC deck
correctness fix that landed on `main` immediately after #1114, with no other
tool gap in between) — in [#170][gf170]:

- `build.py`'s `_gds_geometry_check` compares the merged stream's own extent
  against the DEF's own `DIEAREA` and records the ratio in the committed
  report. `checks.gds_geometry.status` is now `"ok"`
  (`gds_over_def_ratio: [1.0, 1.0]`, previously `[2.0, 2.0]`).
- `trng_top.gds` is now committed, and `klt drc`/`klt lvs` ran over it for
  the first time — see [GDS, DRC and LVS](#gds-drc-and-lvs) below.
- The symptom that led to the original diagnosis is worth keeping on record,
  because it is the kind of evidence that reads like a design problem and is
  not: DRC over the pre-fix merged stream reported ~1000 `metal1`
  spacing/width violations, **100 % of them between a router-inserted via
  cell's landing pad and standard-cell metal1** — two coordinate systems,
  not a routing failure. None of those ~1000 recur post-fix; the 149
  violations DRC reports now are a single different rule
  (`nwell.space.1`), attributable to a different, already-tracked cause —
  see [GDS, DRC and LVS](#gds-drc-and-lvs).

### 2. There is no power delivery at all — [klayout-tools#1091][klt1091]

The flow's stages are floorplan → place → CTS → route, and nothing in that
sequence connects a supply. The generated Tcl never calls `global_connect`
or `pdngen`, and inserts no tapcells, endcaps or filler cells. It shows up in
the committed report as `checks.def.special_nets: false` — the routed DEF has
no `SPECIALNETS` section, so:

- every standard cell's `VDD`/`VSS` pin belongs to no net,
- there are no rails, straps or rings,
- there are no well/substrate ties, and the rows are discontinuous wherever
  placement left a gap.

`status: "ok"` from this verb therefore means "the signals routed", not "this
block is implemented". [#171][gf171] tracks the repository-side work
(a real PDN, tapcells, fillers) once the tool can express it.

This gap is now directly measurable rather than only inferred: every one of
the 149 `nwell.space.1` violations DRC reports over `trng_top.gds` traces to
it, and the `klt lvs` mismatch against `trng_top.pnr.v` is dominated by the
same missing `VDD`/`VSS` connectivity — see
[GDS, DRC and LVS](#gds-drc-and-lvs) below.

## GDS, DRC and LVS

```sh
python3 layout/digital/build.py       # (the same command as above) also writes trng_top.gds + reports/drc.json now that the geometry check passes
python3 layout/digital/lvs.py         # generate the LVS reference, extract the layout side, run klt lvs, write reports/lvs.json
```

Both were blocked from the start of this bring-up by the DEF→GDS merge
defect above until it was fixed upstream and this repository re-pinned past
it ([#170][gf170]). `checks.gds_geometry.status` in
[`reports/place_and_route.json`](reports/place_and_route.json) is now
`"ok"`, so `trng_top.gds` is committed and `klt drc`/`klt lvs` ran over a
geometrically valid stream for the first time.

### DRC

`klt drc trng_top.gds --deck gf180mcu`: **149 violations, all one rule**
([`reports/drc.json`](reports/drc.json)):

| rule | count | DRM section |
|---|---|---|
| `nwell.space.1` | 149 | 7.4 Nwell, `NW.2a` — min. equipotential Nwell-to-Nwell spacing, 0.6 µm |

Every one of the 149 traces to the cause [Two defects this bring-up
found](#two-defects-this-bring-up-found) above already names: no filler
cells or tapcells are inserted anywhere in this flow ([#171][gf171]).
Cross-checking a representative violation directly against `trng_top.def`'s
own placement confirms the mechanism: running `klt drc trng_top.gds --deck
gf180mcu --format json` (the full per-violation dump — this repository's
committed `reports/drc.json` keeps only the verdict and rule counts, the
same choice `_drc_summary`'s own docstring makes for every DRC report in
this directory, since the full dump runs to megabytes over a design this
size), the first reported violation sits at coordinates (57980, 367410)–
(58500, 372100) — inside the two-site gap OpenROAD's detailed placement left
on row 34 between `u_interface/_1808_` (`mux2_1`, right edge at x=57120) and
`u_interface/_1546_` (`aoi22_1`, left edge at x=59360). A filler cell
dropped into that gap would carry Nwell across it and close the spacing;
none exists yet, so each cell's own Nwell — which does not reach the cell's
own outer edge — falls short of its neighbour's by exactly 0.26 µm, the
constant width of all 149 reported violation regions. This is not a routing
or synthesis defect: it is the direct, expected geometric consequence of a
40.8 %-utilization placement with no filler-cell insertion step, tracked
separately as [#171][gf171].

`status: "violations"`, not `"clean"`, is the correct and expected verdict
for this run — a zero count here would be the surprising result, not this
one.

### LVS

[`layout/digital/lvs.py`](lvs.py) bridges `trng_top.pnr.v` (the as-built,
post-CTS netlist — not `design/trng_top/trng_top.synth.v`'s pre-place
mapping) into the black-box SPICE shape `klt extract --abstract-cells`
already resolves for the layout side, then runs `klt lvs` between the two —
see the script's own module docstring for the full pipeline and the
reasoning for a cell-instance-granularity comparison rather than a
transistor-level one. Result ([`reports/lvs.json`](reports/lvs.json)):

| | |
|---|---|
| Verdict | `mismatch` |
| Mismatch count | 7694 |
| `net.merged` | 3786 |
| `net.split` | 411 |
| `topology` | 3497 |
| Nets (layout / reference) | 4165 / 7519 |
| Pins (layout / reference) | 109 / 109 |
| Devices (layout / reference) | 0 / 0 — comparison is cell-instance-granularity (`--abstract-cells`), not transistor-level; see the script's docstring |

**Expected, and attributable to the same missing PDN — not a
signal-routing defect.** `trng_top.pnr.v` carries no `VDD`/`VSS`
connectivity at all (this flow never runs `global_connect`/`pdngen` — [defect
#2 above](#2-there-is-no-power-delivery-at-all--klayout-tools1091)), so
`lvs.py`'s reference side ties every instance's `VDD` to one net and every
`VSS` to another — the correct *design intent* — while the layout side's own
drawn `VDD`/`VSS` pin labels resolve to whatever each cell happens to
physically abut, row by row, with no guarantee of a single continuous net
(the same physical gaps the DRC section above measures). That fragments into
exactly the `net.split`/`net.merged`/`topology` cascade `klt lvs` reports, on
every one of 2499 abstracted cell instances' two power pins. This run's
request does **not** filter `VDD`/`VSS` out of the comparison — no `klt lvs`
option exists to declare "compare pin X on every instance, but ignore what
net it landed on" (`lvs.py`'s own module docstring states this) — so the
mismatch count is reported un-redacted rather than narrowed to make it look
smaller than it is. Signal connectivity is what this run actually tests; a
real PDN, tapcells and fillers ([#171][gf171]) are the prerequisite for a
`klt lvs` run that could separate a power-connectivity finding from a
signal-connectivity one.

## SDF export

```sh
python3 layout/digital/gen_sdf.py            # (re-)generate, write the SDF + report
python3 layout/digital/gen_sdf.py --check    # regenerate to scratch and diff; never writes
```

`trng_top.pnr.v` on its own says nothing about *time*. What consumes it — the
post-route gate-level re-run of the digital functional suite,
[`sim/tb/trng-top-post-route/`](../../sim/tb/trng-top-post-route/) ([#147][gf147])
— needs delays attached, so this script writes them:

| file | what it is |
|---|---|
| [`trng_top.sdf`](trng_top.sdf) | per-instance **cell** delays for `trng_top.pnr.v`, from OpenSTA over the `ss_125C_3v00` liberty deck |
| [`reports/sdf_export.json`](reports/sdf_export.json) | provenance plus the coverage statement, machine-readable |

**What it models, and what it deliberately does not.** OpenSTA links the
as-built netlist against the resolved liberty and writes the delays it
computes from the library timing arcs at each net's own fan-out: real
per-instance cell delay from the CTS-buffered, resized netlist, with **zero
interconnect (wire) delay** — the same lumped, zero-length-net assumption a
pre-layout SDF makes.

The obvious better answer, real routed parasitics, is *worse* here and that is
why it was not taken. `klt place-and-route`'s own `request.post_route_sdf`
would write an SDF from a session with extracted parasitics — but it extracts
them from the merged DEF→GDS stream, and that merge is geometrically wrong for
this design by a factor of two in every DEF-derived dimension
([klayout-tools#1090][klt1090], defect #1 under
[Two defects this bring-up found](#two-defects-this-bring-up-found)). An SDF
whose interconnect delays are wrong by a data-dependent factor is worse than
one that models none, and — unlike "no wire delay", which is a stated,
one-line limitation — it is not distinguishable from a correct run without
re-deriving the geometry bug's effect on every net's RC.

Two further gaps belong to Icarus Verilog 13.0, the simulator that consumes
this SDF, and are generic to Icarus + `write_sdf` + this cell library rather
than to this design:

1. **`TIMINGCHECK` sections are not applied at all — and neither are the cell
   models' own timing checks.** Icarus implements no SDF `TIMINGCHECK`
   annotation, so all 708 of them (one per flop) are dropped; and it
   implements no `$setup`/`$hold`/`$width` either, so the placeholder checks
   in the library's own `specify` blocks do not run as a fallback (it warns
   `Timing checks are not supported` once per check while elaborating). The
   consequence to state plainly: a gate-level run through this path performs
   **no setup/hold checking whatsoever** and a run that reports no violation
   is not evidence that a constraint was met. Setup/hold **signoff** stays
   with OpenROAD's own STA, above, and with [#145][gf145]. That `klt`'s
   response reports `annotated: true` without distinguishing this case from a
   fully-annotated one is filed generically upstream as
   [klayout-tools#1102][klt1102].
2. **A minority of `IOPATH` arcs cannot be annotated.** Icarus rejects an
   `ifnone`-qualified edge-sensitive `specify` path at compile time — the shape
   `xor`/`xnor`/`mux`/`addf`/`addh` use for their select/toggle inputs — so
   those arcs never exist at simulation time and the SDF entry for them cannot
   apply. `gen_sdf.py` derives the exact `(cell, from, to)` list mechanically
   from the library's own Verilog and drops those entries, rather than letting
   them raise a diagnostic that would (correctly) fail the whole run; the
   count is in `reports/sdf_export.json`'s `coverage` block and in the
   evidence record.

Unlike P&R itself, this artefact **is** byte-reproducible for the same netlist
and liberty (no placement seed is involved), so `--check` is meaningful and
regenerates to scratch to diff against what is committed.

## What this establishes, and what it does not

**Establishes.** A gf180mcu digital place-and-route path exists, runs
cold-start from one committed script, and takes this design's real 2500-cell
gate-level netlist to a fully routed DEF: 0 setup violations, 0 hold
violations and 0 antenna violations at the ratified binding corner, 0 routing
DRC violations by the router's own check, +0.52 ns worst hold slack across
all 15 shipped liberty corners, and an as-built netlist that matches the DEF
instance-for-instance (`checks.components`). The question #111 was filed to
answer — *is there any path at all for the digital section's physical
implementation?* — is answered yes, with numbers. As of #170, the path also
produces a geometrically valid, committed GDS
(`checks.gds_geometry.status: "ok"`), a `klt drc` verdict over it (149
`nwell.space.1` violations, every one of them traced to the still-missing
filler cells/tapcells rather than to a routing or synthesis defect — see
[GDS, DRC and LVS](#gds-drc-and-lvs)), and a first `klt lvs` result against
the as-built netlist (`mismatch`, attributable to the same missing power
delivery network — same section).

**Does not establish.** Not signoff timing (no extraction, no SPEF, ideal
clock). Not a DRC-clean layout: 149 residual `nwell.space.1` violations
remain, all attributable to the still-missing PDN/tapcells/fillers (#171),
not to a routing or synthesis defect. Not an LVS-matching layout either, for
the identical reason — `klt lvs`'s reference declares the power-connectivity
design intent this layout does not yet have. Neither becomes a real signoff
DRC/LVS result until #171 lands. Not an area or power result. Not a corner
characterization: one implementation corner, and the multi-corner sweep the
tool does offer cannot yet be scoped to this block's supply. Not a
manufacturable block: no power delivery, no tapcells, no fillers, no pad/IO
integration, and no placement inside `layout/floorplan/`'s own guarded
`digital` region — that region is still empty, and
`layout/floorplan/README.md` remains correct in saying so.

## OpenROAD

`klt place-and-route` shells out to an `openroad` binary. There is no
Homebrew formula and no common Linux-distro package for it, so
[`../openroad_docker.sh`](../openroad_docker.sh) presents the pinned ORFS
Docker image as if it were a native `openroad`, and `build.py` puts it on
`$PATH` only when no native binary is already there (a real local install
always wins). The pin:

| | |
|---|---|
| Image | `openroad/orfs:26Q3-296-gda37dce1c` |
| Digest | `sha256:ebc8142da6d65d1a1e9a528aa2cedcde356243465dd859af8d3ade51075f8cb2` |
| `openroad -version` inside it | `26Q3-1260-g06a5a02279` |

The wrapper bind-mounts the working directory **and** the resolved PDK root
at their own absolute host paths, because the generated Tcl carries absolute
paths for the netlist, the LEF/liberty deck and every output — source ==
target is what makes those resolve identically on both sides of the container
boundary.

[gf111]: https://github.com/2AMLogic/gf180-trng/issues/111
[gf145]: https://github.com/2AMLogic/gf180-trng/issues/145
[gf147]: https://github.com/2AMLogic/gf180-trng/issues/147
[gf150]: https://github.com/2AMLogic/gf180-trng/issues/150
[gf169]: https://github.com/2AMLogic/gf180-trng/issues/169
[gf170]: https://github.com/2AMLogic/gf180-trng/issues/170
[gf171]: https://github.com/2AMLogic/gf180-trng/issues/171
[klt1090]: https://github.com/2AMLogic/klayout-tools/issues/1090
[klt1091]: https://github.com/2AMLogic/klayout-tools/issues/1091
[klt1092]: https://github.com/2AMLogic/klayout-tools/issues/1092
[klt1102]: https://github.com/2AMLogic/klayout-tools/issues/1102
[klt1114]: https://github.com/2AMLogic/klayout-tools/pull/1114
[klt1115]: https://github.com/2AMLogic/klayout-tools/pull/1115
[dr3]: ../../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
