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

- **Placing either ring's `ro_ring11` inside
  `layout/floorplan/trng_floorplan.gds`'s own guarded `ring1`/`ring2`
  regions**, and placing `xor2` + the four `sampler_dff` instances inside
  `combiner_sampler` — the other half of #110's own scope. This is
  **blocked by a discovered size mismatch, not merely unattempted**:
  `ro_ring11`'s real, DRC-clean assembled geometry is a single row
  measuring **~78.9 µm × ~4.75 µm** (`layout/.work/ro_ring11_gr_wire.json`'s
  own `bbox_um` at build time, `klt gen-compose`'s only placement
  strategies being a 1-D row or an explicit per-block translation of
  already-drawn geometry — klayout-tools#321, no 2-D packing exists to
  arrange this more compactly). `layout/floorplan/trng_floorplan.gds`'s
  own `ring1`/`ring2` guard rings are **already drawn, real geometry**,
  sized from `layout/floorplan/reports/area.json`'s bottom-up *area*
  estimate at a 15.1×15.1 µm inner / 17.1×17.1 µm guarded **square**
  footprint — roughly a quarter of this row's own width. The assembled
  ring does not fit inside the region its own floorplan reserved for it,
  and forcing it in would mean violating the guard ring's own DRC geometry
  or spilling into the neighbouring isolation channel — exactly what
  `layout/floorplan/README.md`'s "Mechanism 1" (individually guarded,
  unmatched blocks, no shared dummy row or well) exists to prevent between
  the two rings. Resolving this needs an explicit decision (resize the
  floorplan's guarded regions to the real assembled footprint, or lay the
  ring out compactly instead of as a row) that is out of scope for a
  single assembly step — filed separately: [#119][gf119].

[gf118]: https://github.com/2AMLogic/gf180-trng/issues/118
[gf119]: https://github.com/2AMLogic/gf180-trng/issues/119
[klt634]: https://github.com/2AMLogic/klayout-tools/issues/634
