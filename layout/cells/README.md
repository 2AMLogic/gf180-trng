# `layout/cells/` — drawn design cells

Everything under `layout/testcells/` is a flow-bringup fixture (#15): a
trivial inverter, drawn to prove `klt drc`/`klt extract`/`klt lvs` catch what
they are supposed to catch. **This directory is different: every cell here
is a real piece of `design/`**, hand-drawn from the schematic's own netlist
and driven through the same `klt` flow (`layout/verify.py`) to a DRC-clean,
LVS-matching result — the first rung issue #106 asks for, on the smallest
honestly-scoped unit rather than claimed across the whole block at once.

## What is drawn here

| cell | source | status |
|---|---|---|
| [`ro_stage/`](ro_stage/) | `design/ro_array_core.spice`'s `.subckt ro_stage` (`design/xschem/ro_stage.sch`), at ring1's sizing (`wstv=0.220u`) | DRC-clean, LVS-match, 0 errors — see `layout/reports/ro_stage.*` |
| [`ro_stage_ring2/`](ro_stage_ring2/) | `design/ro_array_core.spice`'s `.subckt ro_stage`, at ring2's own sizing (`wstv=0.240u`) — independently drawn geometry, not a relabelled copy of `ro_stage/`'s | DRC-clean, LVS-match, 0 errors — see `layout/reports/ro_stage_ring2.*` |
| [`ro_nand2/`](ro_nand2/) | `design/ro_array_core.spice`'s `.subckt ro_nand2` (`design/xschem/ro_nand2.sch`) — the ring's one stoppable stage, at ring1's sizing (`wstv=0.220u`) | DRC-clean, LVS-match, 0 errors — see `layout/reports/ro_nand2.*` |
| [`ro_nand2_ring2/`](ro_nand2_ring2/) | `design/ro_array_core.spice`'s `.subckt ro_nand2`, at ring2's own sizing (`wstv=0.240u`) — independently drawn geometry, not a relabelled copy of `ro_nand2/`'s | DRC-clean, LVS-match, 0 errors — see `layout/reports/ro_nand2_ring2.*` |
| [`xor2/`](xor2/) | `design/ro_array_core.spice`'s `.subckt xor2` (`design/xschem/xor2.sch`) — the combiner gate | DRC-clean, LVS-match, 0 errors — see `layout/reports/xor2.*` |
| [`sampler_dff/`](sampler_dff/) | `design/sampler_core.spice`'s `.subckt sampler_dff` (`design/xschem/sampler_dff.sch`) — the sampler's transmission-gate master-slave DFF, instantiated four times unmodified in `sampler_core` | DRC-clean, LVS-match, 0 errors — see `layout/reports/sampler_dff.*` |

`ro_stage` is the entropy source's repeated ring-stage: ten instances plus
one `ro_nand2` make one `ro_ring11`, and two `ro_ring11`s (plus a combiner
and four samplers) make the array `layout/floorplan/` reserves the
`ring1`/`ring2` guarded regions for. It was chosen as the first cell because
it is the block the isolation rationale (`layout/floorplan/README.md`) is
about — the place a drawn-geometry mistake (an isolation gap, a
mis-sized starve device) is most likely to degrade entropy quality without
DRC/LVS ever being able to see it, per issue #106's own framing.

`ro_stage_ring2` and `ro_nand2` ([#108][gf108]) complete ring1's cell set. The
array uses two different starve widths specifically so ring1 and ring2 are
*not* frequency-matched (`layout/floorplan/README.md`, "Mechanism 1" — a
deliberate mismatch load-bearing for the two rings' independence argument),
so `ro_stage_ring2` is its own drawn geometry at `wstv=0.240u`, not a
parameter override on `ro_stage/`'s. `ro_nand2` is the ring's one stoppable
stage: the same series-starved topology as `ro_stage`, plus a parallel
pull-up pair (`XMpa`/`XMpb`, gated by `a`/`en`) and a series pull-down pair
(`XMna`/`XMnb`) that make it a 2-input NAND — `en` low forces the ring's
output high regardless of `a`, stopping oscillation. See
`layout/cells/ro_nand2/build.py`'s own docstring for the parallel-pull-up
drawing technique (two diffusion islands tied by a metal1 riser, since
`XMpa`/`XMpb` share both terminals and cannot be drawn as a simple series
chain). `ro_nand2_ring2` ([#118][gf118]) closes the gap #108 left open: it
is `ro_nand2`'s same six-device topology, independently redrawn at ring2's
own `wstv=0.240u`, the same convention `ro_stage_ring2` already established
relative to `ro_stage`. With `ro_stage_ring2` and `ro_nand2_ring2` both
drawn, ring2's cell set is complete too — `layout/rings/ro_ring11_ring2/`
assembles them the same way `layout/rings/ro_ring11/` assembles ring1's.

`xor2` and `sampler_dff` ([#109][gf109]) are the two cells that make up the
`combiner_sampler` guarded region's contents: `xor2` combines ring1's and
ring2's buffered outputs into `xo`, and `sampler_dff` (drawn once, reused
four times unplaced — see "What is explicitly not here yet" below) is the
sampler's raw-bit/raw-valid/per-ring-liveness flip-flop, DR-0014's async
reset included. At twelve and twenty-two devices respectively they are
larger than `ro_stage`'s four, so both share a hand-drawn "gate array"
layout engine (`layout/cells/_mos_row.py`) instead of each hand-placing its
own coordinates from scratch — see that module's own docstring for the
layout technique (an independent-device gate array plus a two-layer
Manhattan routing grid) and why it generalises `ro_stage`'s dog-boned-pad
technique rather than replacing it.

## Why hand-drawn, and why one cell at a time

`layout/cells/ro_stage/build.py`'s own docstring has the full account; in
short: three of `ro_stage`'s four devices are drawn at the gf180mcu 3.3V
core devices' own minimum width (0.22µm), and `klt gen mos_array` refuses
`w_um` below 0.42µm ([klayout-tools#322][kt322], filed against the tool by
`layout/floorplan/`'s own bring-up; closed as a message-only fix -- the
0.42µm floor itself is unchanged). That floor is not
specific to this cell — 0.22µm-wide NMOS devices appear throughout
`design/` (every `ro_stage`, `ro_nand2`, `ro_buf`, `xor2` and `sampler_dff`
instance has at least one), so **no cell in this design can be generated at
its true width by `klt gen`** until that gap closes. Hand-drawing from
primitive geometry — the same technique, and the same
`layout/testcells/gdsii.py` writer, `layout/testcells/` already established
for the flow-bringup fixtures — is therefore not a shortcut taken for this
one cell; it is the only way to draw a faithful-width cell in this design
today.

That constraint, plus this issue's own complexity flag (a wrong isolation or
sizing decision can pass DRC/LVS cleanly and only show up as degraded
entropy quality once #17's post-layout re-run runs against it), is why this
directory grows one verified cell at a time rather than claiming the whole
block unverified: each cell here is drawn, DRC'd, and LVS'd against a
hand-written reference netlist (never a copy of `klt extract`'s own output —
see each cell's own `.spice` header) before the next one is started.

## What is explicitly *not* here yet

Deferred to follow-up issues, filed against this repository (not against
klayout-tools — none of the gaps below are tool gaps):

- **Placing either ring's assembled `ro_ring11`, or the assembled
  `combiner_sampler` block, inside the #16 floorplan's guarded regions**
  ([#110][gf110], [#134][gf134]). Both rings' own `ro_ring11` (ring1 at
  `wstv=0.220u`, ring2 at `wstv=0.240u`) are assembled and DRC/LVS-clean
  under [`layout/rings/`](../rings/) — see
  [`rings/README.md`](../rings/README.md) for what that covers. `xor2` plus
  the four `sampler_dff` instances are likewise now assembled and
  DRC/LVS-clean under [`layout/blocks/combiner_sampler/`](../blocks/)
  ([#134][gf134]) — see [`blocks/README.md`](../blocks/README.md). Placing
  `ring1`/`ring2` inside their own guarded regions is done ([#110][gf110],
  after resolving the size mismatch [#119][gf119] found); placing
  `combiner_sampler` is blocked on the same kind of size mismatch, filed as
  [#135][gf135]. Nothing in the digital section is placed inside a guarded
  region yet.
- **The digital section** (conditioner, health tests, interface — 1655
  standard cells per `layout/floorplan/README.md`'s own inventory) —
  [#111][gf111]. This is a placement-and-routing problem, not a
  hand-drawn-cell problem at this scale, and `klt synthesize`/
  `klt place-and-route` both resolve a sky130-only standard-cell deck with
  no path for any other installed PDK (`klt place-and-route --help`, as of
  this writing; filed as [klayout-tools#629][kt629]) — gf180mcu digital P&R
  is a distinct, larger, tool-level gap than anything `layout/cells/`
  addresses, and #111 is filed undecided on direction rather than
  prescribing one.

[kt322]: https://github.com/2AMLogic/klayout-tools/issues/322
[kt629]: https://github.com/2AMLogic/klayout-tools/issues/629
[gf108]: https://github.com/2AMLogic/gf180-trng/issues/108
[gf109]: https://github.com/2AMLogic/gf180-trng/issues/109
[gf110]: https://github.com/2AMLogic/gf180-trng/issues/110
[gf134]: https://github.com/2AMLogic/gf180-trng/issues/134
[gf135]: https://github.com/2AMLogic/gf180-trng/issues/135
[gf111]: https://github.com/2AMLogic/gf180-trng/issues/111
[gf118]: https://github.com/2AMLogic/gf180-trng/issues/118
[gf119]: https://github.com/2AMLogic/gf180-trng/issues/119
