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

`ro_ring11` is assembled from `layout/cells/ro_stage/` (ten instances) and
`layout/cells/ro_nand2/` (one instance, the ring's stoppable stage), placed
left to right in ring order (`xg, x1, x2, ..., x10`) by `klt gen-compose`
(`placement.strategy: "explicit"`, a caller-declared `{x, y}` per block —
every cell's own drawn geometry is kept exactly as committed, only
translated) plus one more `klt draw` stream carrying the inter-cell
metal1/metal2 wiring this assembly step adds. See
[`ro_ring11/build.py`](ro_ring11/build.py)'s own module docstring for the
full account: why the wiring is hand-routed rather than `gen-compose`'s own
`connectivity[]` router (same-side-I/O cells the router cannot chain
without rotation/mirroring support it does not have — filed as
klayout-tools friction from that module), the two-metal-layer plan (metal1
for the ring's own `a`/`y` chain, metal2 + via1 for the `vddr`/`vss`
rails), and the small maze-routed escape `ro_nand2`'s own dense internal
metal1 needs.

## What is explicitly *not* here yet

- **Ring2's own `ro_ring11`** (`wstv=0.240u`). `layout/cells/ro_stage_ring2/`
  exists, but no ring2-sized `ro_nand2` does — `layout/cells/ro_nand2/` is
  drawn only at ring1's sizing, and #108's own acceptance criteria required
  exactly one `ro_nand2` cell, not one per ring sizing the way `ro_stage`'s
  criteria explicitly did. That gap was not identified until this
  directory's own assembly work surfaced it, and is filed separately:
  [#118][gf118].
- **Placing this ring (or ring2's, once it exists) inside
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
