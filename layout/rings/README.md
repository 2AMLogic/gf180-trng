# `layout/rings/` — assembled entropy-source rings

`layout/cells/` (#106) draws individual design cells one at a time, each
DRC-clean and LVS-matching standalone. This directory is the next rung:
*assembling* already-verified cells into the multi-cell blocks
`layout/floorplan/`'s guarded regions (#16) are reserved for, and holding
the assembled result to the same DRC-clean/LVS-matching bar.

## What is assembled here

| block | source | status |
|---|---|---|
| [`ro_ring11/`](ro_ring11/) | `design/ro_array_core.spice`'s `.subckt ro_ring11` at **ring1's sizing** (`wstv=0.220u`): `xg` (`ro_nand2`) + `x1`..`x10` (`ro_stage`), chained `ro -> n1 -> n2 -> ... -> ro` per the subcircuit's own connectivity | DRC-clean, LVS-match, 0 errors — see `layout/reports/ro_ring11.*` |
| [`ro_ring11_ring2/`](ro_ring11_ring2/) | `design/ro_array_core.spice`'s `.subckt ro_ring11` at **ring2's own sizing** (`wstv=0.240u`): `xg` (`ro_nand2_ring2`) + `x1`..`x10` (`ro_stage_ring2`), same connectivity | DRC-clean, LVS-match, 0 errors — see `layout/reports/ro_ring11_ring2.*` |

`ro_ring11` is assembled from `layout/cells/ro_stage/` (ten instances) and
`layout/cells/ro_nand2/` (one instance, the ring's stoppable stage), placed
left to right in ring order (`xg, x1, x2, ..., x10`) by `klt gen-compose`
(`placement.strategy: "explicit"`, a caller-declared `{x, y}` per block —
every cell's own drawn geometry is kept exactly as committed, only
translated) plus one more `klt draw` stream carrying the inter-cell
metal1/metal2 wiring this assembly step adds. See
[`ro_ring11/build.py`](ro_ring11/build.py)'s own module docstring for the
full account: why the wiring is hand-routed rather than `gen-compose`'s own
`connectivity[]` router (`ro_stage` puts both `a` and `y` on its west side,
so every chain link is a *same-facing* port pair — the case the router
detects and rejects but cannot route around, with no orientation, waypoint,
or routing-channel control to work around it; filed generically as
[klayout-tools#634][klt634]), the two-metal-layer plan (metal1
for the ring's own `a`/`y` chain, metal2 + via1 for the `vddr`/`vss`
rails), and the small maze-routed escape `ro_nand2`'s own dense internal
metal1 needs.

`ro_ring11_ring2` ([#118][gf118]) closes the gap this directory's own ring1
assembly work surfaced: `layout/cells/ro_nand2/` was drawn only at ring1's
sizing, so ring2 had `layout/cells/ro_stage_ring2/` but no matching
`ro_nand2`. `layout/cells/ro_nand2_ring2/` (independently drawn geometry at
`wstv=0.240u`, not a relabelled copy of `ro_nand2/`'s) closes that, and this
directory's ring2 assembly is the identical row-placement and hand-routed-
wiring technique against that pair of ring2 cells instead — see
[`ro_ring11_ring2/build.py`](ro_ring11_ring2/build.py)'s own module
docstring for why the per-cell geometry constants (bounding boxes, pin
positions, the `ro_nand2` maze-routing waypoints) carry over unchanged from
`ro_ring11/build.py`'s: verified by diffing each ring2 cell's own Metal1
output against its ring1 counterpart, not assumed.

## What is explicitly *not* here yet

- **Placing `xor2` + the four `sampler_dff` instances inside
  `layout/floorplan/trng_floorplan.gds`'s own guarded `combiner_sampler`
  region.** Neither is assembled into a block the way `ro_ring11` is here,
  so there is no committed GDS to place. Out of scope for this directory
  either way — `layout/floorplan/` is where placement happens, not here.

## Placing `ro_ring11`/`ro_ring11_ring2` inside the floorplan (#110)

This was blocked for a while by a discovered size mismatch, not merely
unattempted: `ro_ring11`'s real, DRC-clean assembled geometry is a single row
measuring **~78.9 µm × ~4.75 µm**
(`layout/.work/ro_ring11_gr_wire.json`'s own `bbox_um` at build time), and
`layout/floorplan/trng_floorplan.gds`'s own `ring1`/`ring2` guard rings were
originally sized from `layout/floorplan/reports/area.json`'s bottom-up *area*
estimate at a 15.1×15.1 µm inner / 17.1×17.1 µm guarded **square**
footprint — roughly a quarter of this row's own width, which the assembled
ring did not fit inside.

**[#119][gf119] resolved the size mismatch** (Option A of the two it posed):
`layout/floorplan/floorplan.py` derives `ring1`/`ring2`'s guarded *outer*
footprint from each ring's own committed GDS bounding box instead of the area
estimate (**80.9 × 6.75 µm guarded**, per ring), and a check in that same
script composes each region's guard ring with the real ring geometry and runs
`klt drc` over the pair to confirm the fit is clean
(`layout/floorplan/reports/ring_fit.json`). `combiner_sampler` keeps the
area-estimate square, since it is still unassembled.

**[#110][gf110] placed both rings inside those regions.** The naive
placement — the ring's own bbox flush against the guard ring's inner wall,
since the guarded region's inner cavity is sized to exactly that bbox —
turned out to be DRC-clean but not connectivity-clean: `klt lvs` found it
shorts the ring's own signal wiring to `vss` (see
`layout/floorplan/README.md`'s own
["Placement — issue #110"](../floorplan/README.md#placement--issue-110)
section for the full account, and [klayout-tools#692][kt692] for the tool
gap it surfaced). `layout/floorplan/floorplan.py` now places both rings with
a small clearance instead, carved out of the guard ring's own band width so
the region's committed *outer* footprint is unchanged, and both placements
are DRC-clean-relative-to-baseline and `klt lvs`-match. `combiner_sampler`
and the digital section remain unplaced — out of #110's own scope.

[gf110]: https://github.com/2AMLogic/gf180-trng/issues/110
[gf118]: https://github.com/2AMLogic/gf180-trng/issues/118
[gf119]: https://github.com/2AMLogic/gf180-trng/issues/119
[klt634]: https://github.com/2AMLogic/klayout-tools/issues/634
[kt692]: https://github.com/2AMLogic/klayout-tools/issues/692
