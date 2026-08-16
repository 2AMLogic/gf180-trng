# `layout/blocks/` — assembled non-ring blocks

`layout/cells/` (#106) draws individual design cells one at a time, each
DRC-clean and LVS-matching standalone. `layout/rings/` (#110) is the next
rung for the entropy source's two rings: *assembling* already-verified
cells into the multi-cell row `layout/floorplan/`'s `ring1`/`ring2` guarded
regions (#16) are reserved for. This directory is the same rung for
`layout/floorplan/`'s remaining analog region, `combiner_sampler`, which is
not a ring — hence a sibling directory rather than a third entry under
`rings/`.

## What is assembled here

| block | source | status |
|---|---|---|
| [`combiner_sampler/`](combiner_sampler/) | `design/ro_array_core.spice`'s `xb1`/`xb2` (`ro_buf`, DR-0018's per-ring output buffer) plus `design/sampler_core.spice`'s `xa1` (`xor2`) and `xsb`/`xsv`/`xsr1`/`xsr2` (`sampler_dff`, instantiated four times unmodified) | DRC-clean, LVS-match, 0 errors — see `layout/reports/combiner_sampler.*` |

`combiner_sampler` is assembled from `layout/cells/ro_buf/` (two
instances), `layout/cells/xor2/` (one instance) and `layout/cells/
sampler_dff/` (four instances), placed left to right — each `ro_buf` ahead
of the cell its own buffered output feeds, then `design/sampler_core.spice`'s
own instance order (`xb1, xb2, xa1, xsb, xsv, xsr1, xsr2`) — by
`klt gen-compose` (`placement.strategy: "explicit"`, the same
translation-only technique `layout/rings/ro_ring11/build.py` uses) plus one
more `klt draw` stream carrying the inter-cell Metal1/Via1/Metal2/Metal3/
Via2 wiring this assembly step adds. See
[`combiner_sampler/build.py`](combiner_sampler/build.py)'s own module
docstring for the full account: why the wiring plan differs from
`ro_ring11`'s own (`xor2`/`sampler_dff` expose every pin on its own Metal2
trunk, not a single Metal1 pad, since they are drawn by the shared
`layout/cells/_mos_row.py` engine — issue #109 — rather than hand-placed
like `ro_stage`/`ro_nand2`; `ro_buf` is hand-drawn too, but exposes its own
pins as bare Metal1 pads with no Metal2 trunk at all, a third interface
again — issue #151), and why every inter-cell riser climbs through the
empty gap after its own cell rather than straight up through the cell's own
footprint (found the hard way: a straight riser through a cell's own drawn
geometry runs parallel-and-too-close to that cell's own unrelated internal
risers somewhere along the way, a `metal3.space.1` violation `klt drc`
catches immediately but a routing plan should avoid by construction instead
of by search).

`combiner_sampler` is placed inside `layout/floorplan/trng_floorplan.gds`'s
own guarded `combiner_sampler` region: issue #135 sizes that region's own
guarded footprint from this block's real bounding box (295.76 × 16.25 µm as
of issue #151's own two added `ro_buf` instances — 278.90 × 15.64 µm
beforehand, issue #134) rather than the region's own bottom-up area
estimate (25.27 × 25.27 µm, the same kind of mismatch issue #119 found and
resolved for `ring1`/`ring2`), and `check_ring_fit`
(`layout/floorplan/floorplan.py`) confirms the placement DRC-clean and
LVS-matching. `layout/floorplan/` is where placement happens, not here —
same division `layout/rings/README.md` draws for `ring1`/`ring2`.

## What is explicitly *not* here yet

- **The digital section** — see `layout/cells/README.md`'s own account
  ([#111][gf111]); unrelated to this directory either way.

`combiner_sampler`'s own placement inside
`layout/floorplan/trng_floorplan.gds`'s guarded `combiner_sampler` region is
**done** — [#135][gf135] (resolved by PR #139) replaced that region's prior
area/utilisation-estimate square with the assembled block's own real
bounding box, re-measured from the assembly on every run, as described
above. See `layout/floorplan/README.md`'s own account, § "Placement —
issue #135 (`combiner_sampler`)", for the full writeup.

[gf109]: https://github.com/2AMLogic/gf180-trng/issues/109
[gf111]: https://github.com/2AMLogic/gf180-trng/issues/111
[gf119]: https://github.com/2AMLogic/gf180-trng/issues/119
[gf134]: https://github.com/2AMLogic/gf180-trng/issues/134
[gf135]: https://github.com/2AMLogic/gf180-trng/issues/135
[gf151]: https://github.com/2AMLogic/gf180-trng/issues/151
