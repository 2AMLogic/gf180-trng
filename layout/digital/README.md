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
| [`reports/place_and_route.json`](reports/place_and_route.json) | the full response, the request that produced it, provenance, and this script's own checks |

`trng_top.gds` is **not** committed. It is emitted by the tool and rejected
by this script's own geometry check — see
[Two defects this bring-up found](#two-defects-this-bring-up-found).

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

### 1. The merged GDS is geometrically wrong — [klayout-tools#1090][klt1090]

`klt place-and-route` also merges the routed DEF with the standard cells' own
GDS views and returns a `gds_path`. That stream is **2× too big in every
DEF-derived dimension**: placement coordinates, routed wires and via cells
all double, while the standard-cell geometry stays at its true size, so the
cells sit on a stretched grid where abutting rows no longer abut, rails no
longer join, and the routing does not land on the pins it was routed to.

Root cause, reduced to eight lines: the merge sets the LEF/DEF reader's
target database unit from the tech LEF (this PDK declares `DATABASE MICRONS
2000`, i.e. 0.5 nm), reads the DEF correctly at that unit, and then reads the
standard-cell GDS — written at 1000 units/µm — into the *same* layout.
KLayout adopts the incoming stream's unit and does not rescale the geometry
already there, so everything from the DEF silently doubles. The DEF is fine;
only the merged GDS is wrong.

How this repository responds:

- `build.py`'s `_gds_geometry_check` compares the merged stream's own extent
  against the DEF's own `DIEAREA` and records the ratio in the committed
  report (`checks.gds_geometry`, currently `mismatch`, ratio 2.0 × 2.0).
- **The GDS is not committed while that check fails**, and `klt drc` over it
  is gated behind the same check. When the tool is fixed, the artefact and
  its DRC report appear on the next run with no further edit here.
- The symptom that led to the diagnosis is worth recording, because it is the
  kind of evidence that reads like a design problem and is not: DRC over the
  merged stream reports ~1000 `metal1` spacing/width violations, **100 % of
  them between a router-inserted via cell's landing pad and standard-cell
  metal1** — two coordinate systems, not a routing failure.

So this directory has **no DRC or LVS result yet**, and that absence is the
honest state: a DRC verdict over a geometrically invalid stream would be
meaningless in either direction. [#170][gf170] tracks committing the verified
GDS once #1090 lands.

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
implementation?* — is answered yes, with numbers.

**Does not establish.** Not signoff timing (no extraction, no SPEF, ideal
clock). Not a DRC- or LVS-clean layout — there is no committed layout yet, for
the reason above. Not an area or power result. Not a corner characterization:
one implementation corner, and the multi-corner sweep the tool does offer
cannot yet be scoped to this block's supply. Not a manufacturable block: no
power delivery, no tapcells, no fillers, no pad/IO integration, and no
placement inside `layout/floorplan/`'s own guarded `digital` region — that
region is still empty, and `layout/floorplan/README.md` remains correct in
saying so.

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
[dr3]: ../../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
