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
| Worst slack at `ss_125C_3v00`, 50 ns period | **+23.8 ns** |
| Total negative slack | 0 ns |
| `fmax_mhz` (OpenROAD's own report) | 38.2 MHz |
| Setup / hold violations at that corner | 0 / 0 |
| Clock skew after CTS | 0.16 ns |
| Swept worst **hold** slack, all 15 shipped `.lib` corners | **+0.52 ns** |
| Swept worst **setup** slack, all 15 shipped `.lib` corners | **−37.4 ns** |

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
driver pays — so the −37.4 ns is very probably theirs. "Very probably" is as
far as the recorded evidence goes: `klt` returns one number for the whole
sweep and never names the corner that produced it, filed generically upstream
as [klayout-tools#1092][klt1092]. What the recorded evidence does say
outright is that it is *not* the corner this block is implemented and
specified at, which closes with +23.8 ns.

What the sweep *does* establish outright is the hold result: **+0.52 ns worst
hold slack across all 15 decks**, including the fastest ones — and the fast
corner is exactly where hold binds, so that number is a real, unqualified
multi-corner result.

**What may be cited from this, and what may not.** The 50 ns constraint is
this run's own input, not a spec row: no issue in this repository has set a
digital-section Fmax requirement. The ratified requirement the clock rate
has to satisfy is the raw-rate row (`README.md`, [DR-0003][dr3]): > 1 Mbps
sustained at the sampler output, one raw bit per `clk` edge, so > 1 MHz, with
the stretch row at > 4 MHz. This run closes at 20 MHz with 23.8 ns of slack
at a slow-process/hot/−10 %-supply corner, which is 5–20× the rate the spec
asks for — that is a *margin statement about this implementation*, not an
Fmax claim, and not signoff. Corner-swept Fmax, area and power are #145's
deliverable, and it is #145 that gets to state them.

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

**One inconsistency this does not paper over**: the netlist itself was
*mapped* against `tt_025C_1v80` — `design/synth.py` (#143) took `klt`'s
nominal pick, so ABC's delay-driven cell/drive-strength choices came from the
1.8 V timing model even though this P&R re-times all of them at 3.00 V. Cell
*availability* is identical across decks, so the netlist is valid either way,
but the mapping is not the one a 3.3 V target would have produced. Filed as
[#169][gf169] rather than fixed here: it changes a committed artefact of a
closed issue and belongs with the characterization work, not with this
bring-up.

## Area

| | |
|---|---|
| Die (from the request's own 40 % utilization target) | 546.5 × 546.5 µm = **298 690 µm²** |
| Core | 275 918 µm² |
| Achieved utilization | 40.7 % |
| Standard-cell area inside the core | ≈ 112 000 µm² |
| Routed wirelength | 162 072 µm |

**The die figure is an input, not a result.** It follows arithmetically from
the 40 % utilization this run asked for, chosen to leave routing headroom on
a first attempt whose question was whether this design routes at all. Do not
compare it against the `< 0.05 mm²` README row; the number to compare is the
cell area, and even that comparison has caveats:
[`layout/floorplan/README.md`](../floorplan/README.md)'s bottom-up inventory
estimate prices the digital region at 74 485 µm² of cell area from **1655
cells in the 7-track library**, while this run places **2490 instances of
9-track cells** — taller rows, and a different (post-synthesis, real) cell
count. The two numbers are not like-for-like, and reconciling them against
the ratified area row is #145's job (with [#150][gf150] owning the row
itself). What can be said here: real synthesis and placement land the digital
section's cell area ~1.5× above the inventory estimate, and the estimate was
already 2.5× the whole-block budget.

## Power

`estimated_power_mw: 6.4` — OpenROAD's own `report_power` at
`ss_125C_3v00` with estimated (not extracted) parasitics and no activity
annotation beyond its defaults. It is recorded because the tool reports it;
it is **not** a power result, it does not supersede
`design/digital_power_estimate.py`, and it is not a corner sweep. #145 owns
that comparison.

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
[gf150]: https://github.com/2AMLogic/gf180-trng/issues/150
[gf169]: https://github.com/2AMLogic/gf180-trng/issues/169
[gf170]: https://github.com/2AMLogic/gf180-trng/issues/170
[gf171]: https://github.com/2AMLogic/gf180-trng/issues/171
[klt1090]: https://github.com/2AMLogic/klayout-tools/issues/1090
[klt1091]: https://github.com/2AMLogic/klayout-tools/issues/1091
[klt1092]: https://github.com/2AMLogic/klayout-tools/issues/1092
[dr3]: ../../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
