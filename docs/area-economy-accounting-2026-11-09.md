# Area economy accounting: where the layout area goes (2026-11-09)

Append-only measurement record for issue #789 (part of #700). It explains
*why* each part of the committed layout is as large as it is. It changes no
floorplan, RTL, generator, decision record or spec row: the ratified Area row
(< 0.05 mm^2) stays as written and its miss stays disclosed as FAIL.

Everything below was measured on the committed tree at commit
`cdaf2fee558545d50e36177b9b5528b8ca31a7d4` (`main`, 2026-11-09) with
`klt 0.9.2.dev385+gfafa69b5f3b6` (klayout 0.30.13). Area is geometry; it does
not vary with PVT corner. The only corner-dependent input quoted here is the
place-and-route run in `layout/digital/reports/place_and_route.json`, which
was run at `ss_125C_3v00` (its area figures do not depend on that corner).

Nothing was simulated, re-placed or re-routed to produce this record.

## Method and sources

| Figure | Source |
|---|---|
| Bounding-box / drawn area, whitespace, attribution | `klt economy <gds> --attribute --format json`, run on each committed stream (commands below) |
| Placed-cell area, die, core, achieved utilization | `layout/digital/reports/place_and_route.json` (OpenROAD, seed 1, request: 40 % utilization target, 10 um core margin) |
| Per-sub-block cell area of the digital block | Instance-name prefixes in `layout/digital/trng_top.pnr.v` (1423 logical cells, hierarchical names such as `u_conditioner/_362_`), priced as site footprint = (`klt economy` cell bbox width - 0.86 um well/implant overhang) x 5.04 um row height. This is a derived estimate, see "Limits" |
| Analog inventory (7-track pricing), guard-ring and channel areas | `layout/floorplan/reports/area.json` (an estimate with a stated method, not a layout result) |
| Sweep at other utilization targets | `layout/floorplan/README.md`, "Re-run on the #709 inventory (issue #710)". Quoted, not re-run |

**Lower bounds used** (each is a bound given the *current* netlist/devices; none
is a claim about what a different RTL or device choice could reach):

- Digital: logical-cell site footprint at 100 % utilization, i.e. no
  whitespace, no margin, no guard ring, no physical-only cells.
- Rings and sampler: `drawn_area_um2` of the committed block stream (area
  actually covered by geometry), with the inventory cell area from `area.json`
  shown alongside.
- Routing/whitespace/isolation: bbox minus the sum of block bboxes.

## 1. Which figure is which

The three headline areas are different layouts and must not be mixed:

| Figure | Value | What it is |
|---|---:|---|
| Committed composed floorplan GDS bbox (`layout/floorplan/trng_floorplan.gds`) | **385 042 um^2** (0.385 mm^2; 770 % of the row) | The assembled layout stream as committed: 931.145 x 413.515 um, utilization 0.422, whitespace 0.578 |
| `area.json` roll-up (`rollup.floorplan_area_um2`) | 173 157.92 um^2 (346.3 %) | Sum of guarded regions (164 703.62) + isolation channels (8 454.30). A packing estimate, not the GDS bbox |
| #710 best floorplan point | 91 232 um^2 (182.5 %) | A *swept* point at 85 % requested utilization (90.4 % achieved). Not committed: the committed digital block is the 40 % point |

The `0.176 mm^2` figure in the issue's problem statement does not appear in
`area.json`, the READMEs or any floorplan report. The nearest committed figure
is the `area.json` roll-up (0.173 mm^2; a fresh `floorplan.py` composition gives
173 589 um^2, per the floorplan README) and I could not reconcile 0.176 to a
specific source. It is not used below.

**Reconciliation of the two committed figures:** 385 042 - 173 158 =
**211 884 um^2**. This is the unused area of the composed GDS that the
`area.json` roll-up does not count (see section 2).

## 2. Composed floorplan (`trng_floorplan`, bbox 385 042 um^2)

| Part | Area, um^2 | Share of bbox |
|---|---:|---:|
| Digital guarded region (`digital__fp_guard_digital`) | 158 177.2 | 41.1 % |
| Combiner/sampler guarded region | 5 434.1 | 1.4 % |
| Ring 1 + ring 2 guarded regions (2 x 546.14) | 1 092.3 | 0.3 % |
| **Sum of blocks (= `area.json` guarded_region_area)** | **164 703.6** | **42.8 %** |
| Not covered by any block (whitespace) | 220 338.8 | 57.2 % |

The whitespace splits as follows (the isolation channels are `area.json`'s
20 um channels per DR-0019; the rest is derived from child bboxes):

| Part of the whitespace | um^2 |
|---|---:|
| Isolation channels (ring1-ring2 135, ring2-sampler 365, sampler-digital 7 954.3) | 8 454.3 |
| Empty area beside/above the analog row (see below) | 211 884.5 |

**Named reason (measured):** the committed composition is a single row. The
digital block is 397.7 um tall and sits at x = 519.6-917.3 um; the analog
blocks (rings, sampler) form a strip only 18.25 um tall at x = 0-499.6 um. The
rectangle above the analog strip and left of the digital block
(about 519.6 x 384.1 um = 199 576 um^2) is empty, as are a 11.15 um routing
strip below the row and a 13.85 um strip at the right edge. `klt economy`
reports a left dead margin of 465.57 um and a largest empty region of
202 912 um^2 (757.3 x 406.2 um, fill 0.66) on this stream. The row's aspect
ratio (2.25) and the analog strip's height, not any cell or device area, drive
this term. The `area.json` roll-up assumes the blocks are packed without that
rectangle.

## 3. Digital block (`trng_top`)

Committed stream `layout/digital/trng_top.gds`: bbox 395.715 x 395.715 um =
**156 590.4 um^2**; guarded region 158 177.2 um^2.

| Part | um^2 | x lower bound |
|---|---:|---:|
| **Lower bound:** 1423 logical cells, site footprint, 100 % utilization | 59 264.8 | 1.00 |
| Placed area reported by OpenROAD (43.4086 % x core 139 935) | 60 744 | 1.02 |
| Core (unfilled part of the core = 139 935 - 60 744) | 79 191 | |
| Die-to-core margin (156 590 - 139 935) | 16 655 | |
| Guard ring (158 177.2 - 156 590.4) | 1 586.8 | |
| **Guarded digital region** | **158 177.2** | **2.67** |

Reconciling the pieces: 60 744 + 79 191 + 16 655 + 1 587 = 158 177. The
logical-cell lower bound (59 265) is **above** the 50 000 um^2 whole-block
budget on its own (118.5 %), so no layout lever can close the row without
removing cell area; the floorplan README reached the same conclusion from
the placed area.

**Per sub-block** (flat netlist split by instance-name prefix; the bound is
cell area at 100 % utilization, the same bound applies to each share):

| Sub-block (prefix) | Cells | Flops | Lower bound, um^2 | Share | `area.json` inventory (7-track), um^2 | Lower bound / inventory |
|---|---:|---:|---:|---:|---:|---:|
| Interface (`u_interface`) | 772 | 183 | 32 023.0 | 54.0 % | 21 842.2 | 1.47 |
| Conditioner (`u_conditioner`) | 249 | 73 | 11 478.7 | 19.4 % | 3 957.9 | 2.90 |
| Health tests (`u_health_test`) | 250 | 45 | 9 635.7 | 16.3 % | 7 428.6 | 1.30 |
| Ring-liveness monitor (`u_ring_liveness`) | 100 | 18 | 4 202.6 | 7.1 % | 2 849.4 | 1.48 |
| Clock tree + repair buffers (no RTL owner) | 52 | 0 | 1 924.9 | 3.2 % | not inventoried | |
| **Total** | **1 423** | **319** | **59 264.8** | 100 % | 36 078.1 (incl. liveness) | 1.64 |

Flop cells (`dffrnq` 14 270 + `dffq` 12 565 um^2) are 45 % of the cell area,
`mux2` another 15.7 %. Every sub-block's *allocated* share of the guarded
region is its share x 158 177 (e.g. interface about 85 400 um^2), because
whitespace, margin and guard are not attributable to RTL.

**Named reasons for the overrun (bound 59 265 -> guarded 158 177 um^2, x2.67):**

1. **Placement density (measured, dominant, 79 191 um^2 = 50 %).** The
   place-and-route request asked for a 40 % utilization target (43.4 %
   achieved). The digital README states this was chosen for routing headroom
   on a first attempt. The floorplan README's sweep measured the same netlist
   at 85 % requested / 90.4 % achieved: die 77 140 um^2, 0 route-DRC, 0
   antenna, setup/hold met, but 7 composed-LVS mismatches (undiagnosed) and
   unchanged LU.3/LU.4 tap-spacing failures. Quoted, not re-run.
2. **Die-to-core margin (measured, 16 655 um^2 = 10.5 %).** The request's
   10 um core margin plus site rounding. Not varied by any run.
3. **Guard ring (measured, 1 587 um^2 = 1.0 %).** 792 guard taps in a 1.0 um
   band around the block.
4. **Library and mix versus the inventory (documented elsewhere).**
   `sim/characterization-digital-sta-area-power.md` section 3 attributes the
   digital cell area being 1.597 x the inventory to x1.243 cell count/mix,
   x1.257 for 9-track rather than 7-track rows and x1.023 power-delivery
   cells. That is not an overrun of the bound above; it explains why the
   inventory understated the bound.
5. **Physical-only cells.** 3 365 fill/tap/endcap instances (114 filltie, 148
   endcap) fill the rest of the core. Their footprint is inside item 1.

Unreconciled: my site-footprint estimate of the logical cells (59 265) and
OpenROAD's placed area (60 744) differ by 2.5 % (1 479 um^2). The derived
footprint of the 148 endcaps and 114 tap cells alone (about 3 340 um^2) is
larger than that difference, so the two figures do not count the same set of
cells. Not diagnosed here.

## 4. Ring array (`ro_ring11`, `ro_ring11_ring2`) and sampler (`combiner_sampler`)

| Block | Stream | bbox, um^2 | Lower bound (drawn), um^2 | bbox / bound | Inventory cell area, um^2 | Guarded, um^2 |
|---|---|---:|---:|---:|---:|---:|
| Ring 1 | `layout/rings/ro_ring11/ro_ring11.gds` | 374.82 (78.91 x 4.75) | 174.57 | 2.15 | 225.06 | 546.14 |
| Ring 2 | `layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds` | 374.82 | 175.31 | 2.14 | 225.06 | 546.14 |
| Combiner/sampler | `layout/blocks/combiner_sampler/combiner_sampler.gds` | 4 806.1 (295.76 x 16.25) | 1 728.28 | 2.78 | 342.45 | 5 434.12 |
| **Analog total** | | 5 555.7 | 2 078.2 | 2.67 | 792.57 | 6 526.4 |

Analog is 6 526 um^2 guarded, 1.7 % of the composed bbox and 4 % of the
guarded sum. Its lower bound is far below the digital one, so none of the
overrun in the row is analog-driven.

**Named reasons:**

- **Ring row geometry (measured).** A ring is one 78.91 x 4.75 um row
  (aspect 16.6, utilization 0.466). Eleven stages at a 6.83 um pitch, each
  4.83 um wide, leave a 2.0 um inter-stage gap for the wiring cell, which
  alone spans 78.91 x 4.18 um and carries 229 um^2 of its own whitespace.
- **Guard band (measured).** The ring guard adds 171.3 um^2 per ring (546.14 -
  374.82): a 0.6 um band, 0.4 um clearance, 16 taps. 342.6 um^2 for both.
- **Sampler geometry (measured geometry, cause not isolated).** The sampler is
  a single 18:1 row: four sampler flip-flops (54.89 x 10.44 um each, 573 um^2
  bbox, 2 292 um^2 total), one XOR (30.89 x 8.28 um) and two buffers, with
  about 6 um between neighbours, in a 16.25 um tall box. Child bboxes sum to
  2 561 um^2 of the 4 806 um^2 box (fill 0.53). Why each sampler flip-flop is
  573 um^2 of bbox for 4 sampler flip-flops sharing a 342 um^2 inventory
  price is **not determined here** (generator inefficiency is a candidate,
  untested); this is the item for the follow-up.
- **Guard (measured).** The sampler guard adds 628 um^2 (5 434.12 - 4 806.1).

## 5. Measurement gaps hit, filed generically in `2AMLogic/klayout-tools`

| Gap | Issue |
|---|---|
| `klt economy --attribute` charges whitespace to a nested placement wrapper and reports 326 821 um^2 of instance overlap; no per-leaf-gap partition (section 2) | [klayout-tools#5179](https://github.com/2AMLogic/klayout-tools/issues/5179) |
| No standard-cell site footprint, category split (logic/sequential/fill/tap/endcap) or grouping by instance-name prefix; section 3 needed a hand-written script and a hard-coded 0.86 um overhang | [klayout-tools#5180](https://github.com/2AMLogic/klayout-tools/issues/5180) |
| No additive decomposition of a P&R block bbox into placed cells, physical-only cells, unfilled core, die margin and guard; section 3 reconciled these by hand | [klayout-tools#5181](https://github.com/2AMLogic/klayout-tools/issues/5181) |

## 6. Ranked follow-up (by area recovered)

Filed as the separate proposal issue: [#793](https://github.com/2AMLogic/gf180-trng/issues/793). Ranking, with the
basis for each figure (derived or quoted; **none of these was run**):

| Rank | Lever | Area recovered, um^2 (of 385 042 bbox) | Basis |
|---:|---|---:|---|
| 1 | Composed floorplan arrangement (empty rectangle beside the analog row) | up to 211 884 | Section 2 arithmetic: committed GDS bbox minus `area.json` roll-up |
| 2 | Digital placement density (40 % -> 85 % requested) | about 79 450 (die 156 590 -> 77 140) | Quoted from the floorplan README sweep; open LVS (7 mismatches) and tap-spacing issues |
| 3 | Digital die-to-core margin (10 um) | on the order of 12 000 | Derived: ring of 8 um extra width around a 374 um core; not run |
| 4 | Isolation channels (20 um, DR-0019) | 8 454 | Decision-record-bound; recovery needs an isolation analysis, not a layout change |
| 5 | Digital cell area (the only lever that can close the row) | about 2.3 um^2 of die per um^2 of cell removed at the 40 % point, 1.1 at the 85 % point | Needs to remove > 9 265 um^2 (15.6 %) of the 59 265 bound to reach 50 000 um^2 of cell area alone |
| 6 | Guard rings (digital 1 587, sampler 628, rings 343) | 2 558 | Section 3/4 arithmetic |
| 7 | Sampler geometry (bbox 2.78 x drawn) | up to about 3 000 | Section 4; cause untested |

Levers 1-4 move the layout toward the cell-area floor but, with the
logical-cell bound at 118.5 % of the 50 000 um^2 budget, none of them alone
reaches the row.

## Limits

- The digital sub-block split is an estimate from a hierarchical-name grep of
  the P&R netlist and a site-footprint rule derived from two library cells
  (`and2_1`, `and2_4`); it is not a `klt` output (gap above).
- The 2.5 % difference to OpenROAD's placed area is unreconciled.
- The `area.json` inventory is a 7-track estimate and the committed digital
  block is 9-track; the per-sub-block "lower bound / inventory" column is
  context, not a bound.
- Lower bounds hold for the current netlist and devices only.
- No claim is made about routability or signoff for any lever in section 6.

## Reproduce

From a checkout at `cdaf2fee558545d50e36177b9b5528b8ca31a7d4`:

```sh
klt economy layout/floorplan/trng_floorplan.gds --attribute --format json
klt economy layout/digital/trng_top.gds --attribute --format json
klt economy layout/blocks/combiner_sampler/combiner_sampler.gds --attribute --format json
klt economy layout/rings/ro_ring11/ro_ring11.gds --attribute --format json
klt economy layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds --attribute --format json
```

The digital sub-block split: take each logical instance in
`layout/digital/trng_top.pnr.v`, group by the text before the first `/` in
its instance name (`clkbuf*`, `clkload*`, `max*` and similar are the clock-tree
and repair group), and sum (cell bbox width from the `trng_top` `klt economy`
`cells` list - 0.86 um) x 5.04 um per instance. The total is 59 264.8 um^2
over 1 423 instances.

## Addendum: dense placement and die-to-core margin (issue #798)

Measured at `044f0219` on `main`, 2026-11-09. Two scratch `klt
place-and-route` runs at `ss_125C_3v00` with the seed and constraints of
`layout/digital/build.py`. Only `FLOORPLAN["utilization_pct"]` and
`FLOORPLAN["core_margin_um"]` were overridden in memory; nothing committed
under `layout/digital/` was changed (each check that reads the committed
paths was run with the point's files copied over them, then restored with
`git checkout`). Wall-clock per P&R point was about 10 to 15 minutes.

| | Committed | 85 % / 10 um | 85 % / 2 um |
|---|---:|---:|---:|
| Requested utilization, core margin | 40 %, 10 um | 85 %, 10 um | 85 %, 2 um |
| Achieved utilization | 43.4 % (`place_and_route.json`) | 90.41 % | 92.49 % |
| Die, um^2 | 156 590 | 77 139.5 | 68 507.8 |
| Route-DRC / antenna violations | 0 / 0 | 0 / 0 | 0 / 0 |
| Setup / hold violations at `ss_125C_3v00` | 0 / 0 | 0 / 0 | 0 / 0 |
| Worst slack at `ss_125C_3v00`, ns | 32.864 | 33.146 | 32.110 |
| Worst setup / hold over all shipped `.lib` corners, ns | -5.546 / +0.503 | -4.834 / +0.509 | -8.372 / +0.507 |
| `layout/digital/lvs.py` (vs the point's own `.pnr.v`) | match | match, 2 notes | match, 2 notes |
| Composed digital LVS (`floorplan.py`) | match, 0 | match, 0 | match, 0 |
| Composed floorplan, um^2 (% of the 50 000 um^2 row) | 173 589 (347.2 %) | 91 232 (182.5 %) | 82 512 (165.0 %) |
| LU.3 / LU.4 max distance, um (limit 15) | 49.691 / 49.727 | 49.691 / 49.727 | 49.691 / 49.727 |

The 85 %/10 um point reproduces the die area (77 139.5 vs 77 140) and the
composed floorplan area (91 232) that the earlier sweep quoted. The margin
term is the difference between the die and the core: with the margin cut from
10 um to 2 um the die falls by 8 631.7 um^2 (11.2 %).

### The 7 composed-LVS mismatches are a harness artefact

The earlier sweep copied only `trng_top.def` and `trng_top.gds` over the
committed files. `floorplan.py` compares the composed digital region against
`layout/digital/trng_top.lvs_reference.spice`, which is derived from
`trng_top.pnr.v`, and that file was still the committed 40 % build's. The
dense placement has a different set of CTS and repair buffers and different
instance names, so layout and reference described different netlists.

Reproduced both ways at the 85 %/10 um point: with only the DEF and GDS
swapped, `floorplan.py` prints `lvs mismatch (7 mismatches, unexpected
categories: none)` for the digital region. With the point's `trng_top.pnr.v`
and the `trng_top.lvs_reference.spice` that `layout/digital/lvs.py` generates
from it also swapped in, the same composed request gives `lvs match (0
mismatches, unexpected categories: none)`, and `klt lvs` on that request
reports `status: match, mismatch_count: 0`. The 2 um point also gives 0.
The 6 mismatches at 70 % were not re-run; the same cause is expected but not
shown. A dense placement is therefore not shown to have a connectivity defect.

### LU.3 / LU.4

`layout/digital/tap_distance.py` on both dense layouts fails LU.3 (max
49.691 um) and LU.4 (max 49.727 um) against the 15 um limit, identical to the
committed layout, because the tapcell pitch does not change with density or
margin. #717 (tapcell pitch) and #487 are still open, so this is their
outcome to cite once they land, not something this addendum resolves.

### Outcome: negative finding for refreshing the artefacts

Both points route cleanly and meet setup/hold at `ss_125C_3v00`, and the LVS
question is closed. The committed `layout/digital/` artefacts are **not**
refreshed, because the criterion requires every check to pass and LU.3/LU.4
fail. Neither point is a signed-off implementation. Not done here:

- The fifteen-corner STA/area/power characterisation
  (`sim/characterization-digital-sta-area-power.md`) was not re-run on the dense
  DEFs; the swept worst setup figure above is the P&R tool's own, and it moves
  with the point without a trend (-4.8 ns at 85 %/10 um, -8.4 ns at 85 %/2 um,
  -5.5 ns committed). `max_transition_violation_count` was 658 and 692
  against 660 for the committed run.
- A tighter tapcell pitch was not run, so the area cost of meeting LU.3/LU.4
  is still unmeasured.
- Placed cell area stays near 60 k um^2, above the 50 000 um^2 row on its own;
  no point here changes the ratified Area row.
- The committed-column 40 % figures are from the committed
  `reports/place_and_route.json`; the committed LVS and floorplan columns
  come from the earlier sweep's fresh composition, not a re-run.

Reproduce a point: set `FLOORPLAN["utilization_pct"]` and
`FLOORPLAN["core_margin_um"]` in memory, call `build.place_and_route()` on a
scratch directory under `layout/.work/`, then run `lvs.py`, `floorplan.py` and
`tap_distance.py` with that point's DEF, GDS, `.pnr.v` and generated
reference in place of the committed files.

## 7. Addendum (2026-11-09, issue #800): why one sampler flip-flop is 573 um^2

Appended; sections 1-6 are unchanged. Measured on `main` at `044f0219` with
klt `0.9.2.dev385` (klayout 0.30.13). No layout, spec or inventory change was
made, and the ratified Area row is untouched.

### Re-measurement

```sh
klt economy layout/cells/sampler_dff/sampler_dff.gds --attribute --format json
klt economy layout/blocks/combiner_sampler/combiner_sampler.gds --attribute --format json
```

- `sampler_dff`: bbox 54.89 x 10.44 um = 573.05 um^2, drawn area 245.72 um^2
  (utilization 0.429), 22 `comp` islands (11 NMOS + 11 PMOS), tightness 1.0
  (no dead margin). Section 4's 573 um^2 reproduces.
- `klt economy --attribute` on this cell returns no children and one
  `margin` gap equal to the whole bbox, so it cannot split the area itself
  (filed generically as klayout-tools#5189). The split below uses per-layer
  extents read with the klayout module in the klt environment.

### Where the 573 um^2 goes

Per-layer extents (merged): `comp` x -0.22..54.42, y 0.78..1.22; `nwell`
x 28.13..54.67, y 0.53..1.47; `poly2` y 0.58..1.92; `metal1` y 0.80..1.92;
`metal2` and `metal3` y up to 10.97. Fourteen horizontal Metal2 trunks (one per
net), the first at y 2.22..2.52 and the last at 10.67..10.97.

| Band (Y) | Height, um | Area at 54.89 um wide, um^2 | Share |
|---|---:|---:|---:|
| Nwell margin, diffusion row, gate landing pads (0.53..1.92) | 1.39 | 76.30 | 13.3 % |
| Clearance to the first trunk (1.92..2.22) | 0.30 | 16.47 | 2.9 % |
| Net-trunk channel, 14 trunks at 0.65 um pitch (2.22..10.97) | 8.75 | 480.29 | 83.8 % |
| **Total** | **10.44** | **573.05** | **100 %** |

The trunk channel is 8.75 um = 13 x 0.65 + 0.30. Removing it entirely would
leave 92.76 um^2 (the first two rows), which is 1.24x the 74.64 um^2 priced
for `dffrnq_1`.

Width: 54.89 = 26.04 (NMOS row, `comp` x -0.22..25.82: 11 devices x 2.4 um
pitch - 0.8 um trailing slot + 0.44 um pad) + 2.56 (NMOS-to-PMOS `comp` gap:
`BLOCK_GAP` 3.0 um - 0.44 um pad) + 26.04 (PMOS row, 28.38..54.42) + 0.25
(Nwell margin past the last PMOS pad). The curator's 55.8 um estimate counted
a trailing slot (0.8 um) per row that the engine does not draw.

### Cause

- **Cell engine topology, not block spacing.** `layout/cells/_mos_row.py`
  gives every device its own diffusion island (no shared source/drain), puts
  NMOS and PMOS side by side, and routes each net on its own Metal2 trunk at
  `TRUNK_PITCH` 0.65 um. The cell's own whitespace is 327.33 um^2 per
  instance (57 %).
- **Dominant term is Y, not X:** the trunk channel (83.8 % of the box), not
  the 2.4 um device pitch. The candidate "generator spacing in X" is
  refuted as the main cause; the diffusion rows occupy 26.04 um of 54.89 um
  in X but only 1.39 um of 10.44 um in Y.
- **Block term is separate and smaller.** In `combiner_sampler`, six
  `ROW_GAP_UM` gaps of 6.0 um across the 16.25 um box are at most
  6 x 6.0 x 16.25 = 585 um^2 (upper bound, the buffers and XOR are
  shorter) against 4 x 327.33 = 1 309.3 um^2 of whitespace inside the four
  `sampler_dff` instances. Cell-internal whitespace is about 2.2x the
  inter-cell gap term.
- **Why the 7.7x ratio to the inventory price is not a defect to recover by
  itself:** the inventory prices `dffrnq_1`, a library cell, while this is a
  22-device transistor-level verification cell drawn by the independent-device
  engine (its docstring says so). The two are different objects.

### Decision

Negative finding, no change justified here. The measurement does not support a
cheap fix: the dominant term would need a router or channel-sharing change in
`_mos_row.py`, which is outside this issue (it affects `xor2` too) and would
need DRC, LVS and the sampler `sim/` evidence re-run with PVT corners.
Estimates only, not drawn or verified: tightening `TRUNK_PITCH` from 0.65 to
the 0.56 um rule floor (0.28 width + 0.28 space) would save about 1.2 um of
height, roughly 65 um^2 per instance (11 %); sharing trunks between
non-overlapping nets would save more.

Limits: figures are derived from one stream at one commit; the estimates in
the Decision paragraph were not drawn, extracted or DRC-checked.
