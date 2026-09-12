# The shared `vss` return trunk: IR drop against the chip pin, per region

Status: measurement complete for issue [#234] — the one deliberately shared
return in the composed floorplan (`design/floorplan_netlist.py`'s own net
table; every other supply branch is a star, `layout/floorplan/README.md`'s
"supply/ground star point" section) had never had its cost checked. [DR-0025]
explicitly scoped this out of the extracted-netlist increment ([#232]): IR
drop is a static supply analysis with its own methodology and needs a current
profile a PEX re-run does not produce. This is that analysis.

**Verdict: not material.** The largest computed local-`vss` offset is
**16.07 mV** (`ring1`, the active-power binding corner `ff`/−40 °C/3.63 V),
and a deliberately unphysical conservative bound — all of that corner's
active current forced through `ring1` alone — still only reaches
**21.94 mV**. Both are well under the **33 mV** (10 % of the ±10 %/330 mV
supply-corner spread this design's own PVT sweep already runs) yardstick this
document checks against. At the idle corner the offsets are three orders of
magnitude smaller (tens of µV). No ratified or Proposed row is affected — see
§4. (Updated post-[#224]: figures were 15.64 mV / 21.48 mV before that issue
moved the `vss` chip pin east to clear `digital`'s own new PDN riser — see
§1's own note.)

This document is an ordinary summary, not evidence. Every number below cites
the `sim/` record or committed report it comes from; the arithmetic itself is
`sim/tools/vss_trunk_ir_drop.py`, re-run with `python3 sim/tools/
vss_trunk_ir_drop.py`.

## 1. Why a segmented model, not the lumped ~129 ohm DR-0025 already quotes

[DR-0025]'s own preview-of-`klt`-extraction table gives `vss`'s full
430.23 µm Metal4 trunk a lumped **~129 ohm** at the deck's curated Metal4
sheet resistance (0.09 ohm/sq). That number answers "how resistive is the
whole trunk", not this issue's question — "what does each region's *own* tap
point see" — because `ring1`, `ring2` and `combiner_sampler` tap in at three
different points along it, and `combiner_sampler`'s tap sits a few µm from
the chip pin while `ring1`'s is the far end (`layout/floorplan/reports/
interregion.json`'s own `vss` route).

`sim/tools/vss_trunk_ir_drop.py`'s `resistance_model()` walks the *real*
drawn geometry instead: it calls `layout.floorplan.interregion.wiring_plan()`
— the same function `layout/floorplan/floorplan.py`'s own `compose()` calls —
with the origins and content bounding boxes already committed in
`layout/floorplan/reports/compose.json` and `area.json`, and reads the
resulting Metal3 riser rectangles and Metal4 trunk segments back out of the
shapes it draws. Nothing here is transcribed by hand; if issue [#222]'s
routing changes, these reports change with it and this derivation's numbers
change too (`sim/tests/test_vss_trunk_ir_drop.py` holds the endpoint set to
the committed `interregion.json` so a silent mismatch fails loudly instead of
just changing a number no one is watching).

The resulting network (chip pin at `x = 514.58 µm`, nearest tap first):

| Region | Segment to previous node (ohm) | Riser (ohm) | Riser length (µm) |
|---|---:|---:|---:|
| `combiner_sampler` | 3.480 | 8.520 | 28.40 |
| `ring2` | 97.806 | 3.906 | 13.02 |
| `ring1` | 30.273 | 3.906 | 13.02 |

Segment resistances alone sum to 131.56 ohm — 2.58 ohm above DR-0025's own
lumped ~129 ohm. Before [#224], that sum matched DR-0025 exactly (same
geometry, same sheet resistance table); #224 moved the `vss` chip pin
(`CHIP_PIN_PLACEMENT["vss"]` in `layout/floorplan/interregion.py`) east by
that same 2.58 ohm's worth of Metal4 length, to clear a new riser for
`digital`'s own PDN tie (`layout/digital`'s ground return, drawn into this
same `vss` net for the first time). `sim/tools/vss_trunk_ir_drop.py`
deliberately excludes `digital` itself from this table (`SCOPED_OUT_
REGIONS`) — its own PDN is a dense multi-strap grid, not a single riser tap,
so this series-chain model does not apply to it — but the chip pin's own
new position is real, drawn geometry this table correctly reflects. The
riser resistances (3.9–8.5 ohm each) are the piece the lumped number never
separated out. Both Metal3 (riser) and Metal4 (trunk) share the same curated
0.09 ohm/sq in the `klt` gf180mcu deck (klayout-tools#547), the same table
DR-0025 already cites — restated as a constant in the script rather than
imported, since `klayout_tools` is a build-time tool this repository does not
depend on at run time.

## 2. Current profile, and the corner each term is stated at

Two corners, matching this repository's own already-established power
binding corners (`sim/characterization-startup-and-power-budget.md`) — never
mixed silently:

**Active, `ff`/−40 °C/3.63 V** (the highest-current corner this repository's
PVT sweep has ever measured for the analog block — see §3 for why that makes
it the right corner to bound IR drop with):

| Term | Value | Source | Physically inside |
|---|---:|---|---|
| Entropy array (`xr1`+`xr2`+`xb1`+`xb2`+`xa1`) | 489.9 µW | [`2026-09-11-ro-array-core-power-extracted-routed-01`](records/2026-09-11-ro-array-core-power-extracted-routed-01.md), `sim/characterization-post-layout-extracted.md` §7.4 | `ring1`+`ring2` (oscillators) and `combiner_sampler` (`ro_buf`×2 + XOR) |
| Sampler flops (`xsb`+`xsv`) | 16.88 µW | `sim/tools/power_rollup.py`'s own formula, cited unchanged in §3.2/§7.4 of the same document | `combiner_sampler` |
| Per-ring liveness taps (`xsr1`+`xsr2`, [DR-0016]) | ~81 µW | `sim/characterization-startup-and-power-budget.md`, "Two taps that are not in the total" — `sim/tb/ring-liveness-tap-power/` | `combiner_sampler` |

The 489.9 µW term is not separable, in any committed record, into "the two
rings' own 22 oscillator stages" versus "the two `ro_buf` instances and the
XOR gate that physically sit in `combiner_sampler`". This document allocates
the whole term to `ring1`/`ring2`, split 50/50 by symmetry (both rings are
the same `ro_ring11` schematic topology — `sim/characterization-worst-corner-and-mc-mismatch.md`'s
own MC-mismatch section shows a real but small per-ring spread, not a power
asymmetry). That **overstates** each ring's own current a little and
**understates** `combiner_sampler`'s — the conservative direction for the two
nodes that sit farther from the chip pin, which is where a shared-trunk
offset matters most.

The "Two taps that are not in the total" framing predates [DR-0016]'s
adoption into the shipped design: `design/sampler_core.spice` now declares
`xsr1`/`xsr2` unconditionally and `layout/blocks/combiner_sampler/build.py`
places and wires both, so the floorplan this issue analyses does carry that
current, and it is included here even though the cited characterization
document's own power-budget rollup (`sim/tools/power_rollup.py`) still
excludes it from the ratified-row total for a different, narrower reason
(matching the row's own "shipped core" scope at the time that rollup's
formula was written).

**Idle, `ff`/+125 °C/3.63 V**:

| Term | Value | Source |
|---|---:|---|
| Whole analog block (`sampler_core`: both rings + all four `sampler_dff`) | 136.8 nA | [`2026-09-11-sampler-core-idle-leakage-extracted-routed-01`](records/2026-09-11-sampler-core-idle-leakage-extracted-routed-01.md), same document §7.4 |

Unlike the active corner, this DUT is the *whole* `sampler_core` in one
testbench, so no liveness-tap addition is needed — but no idle-level
per-block breakdown exists either. This document apportions the 136.8 nA
total across `ring1`/`ring2`/`combiner_sampler` using the **active** corner's
own power ratio between "the two rings' terms" (489.9 µW) and
"`combiner_sampler`'s terms" (97.88 µW) — an approximation, stated as one,
not a second idle measurement.

## 3. Why the active corner bounds every other corner in this repository's grid

Resistance is corner-independent in this model: it is fixed drawn Metal3/
Metal4 geometry, and the curated sheet-resistance table this repository
already uses (DR-0025) carries no per-corner variation. Current is the only
corner-dependent term, so the corner that maximizes total analog current also
maximizes every region's IR-drop offset.

`ff`/−40 °C/3.63 V is, by construction, that corner: it is this repository's
own **active-power binding corner**, chosen because a current-starved ring
oscillator's active current scales with switching frequency, and `ff`/cold is
where that frequency (and therefore current) is highest across the covered
PVT grid. In particular it is *not* the same corner as the **entropy-binding**
corner (`ss`/+125 °C/3.63 V, [DR-0015]) that [DR-0007]'s jitter-energy margin
is evaluated at — that corner is the *slowest* in the grid, hence draws less
active current than the one analysed here. So the 16.07 mV / 21.94 mV
figures in this document upper-bound the offset at the entropy-binding corner
too, without needing a separate run at it.

## 4. Does this move any ratified or Proposed row?

No measured row in this repository is affected, and the reasoning is
structural, not just "the number is small":

- **The active/idle power rows** (`sim/characterization-startup-and-power-budget.md`,
  `< 500 µW` / `< 1 µA`) are measured on isolated testbenches
  (`ro-array-core-power-*`, `sampler-core-idle-leakage-*`) whose DUT uses an
  ideal, zero-ohm `vss` net — they do not include this trunk's resistance at
  all, in either direction. This analysis does not change what those
  testbenches measured; it adds a separate, previously-unchecked fact about
  the physical die that no existing record captured.
- **The entropy-binding corner's jitter-energy margin** ([DR-0007] §2, the
  0.442× figure `sim/characterization-post-layout-extracted.md` §7.1 reports
  at routing level, cited by [DR-0025]) is a period/jitter claim, not a power
  claim — a `vss` offset perturbs it only by shifting the starving device's
  own `vddr`–`vss` bias, since `vddr` is delivered by its own low-resistance
  star branch (~1 ohm, DR-0025's own table) essentially unaffected by this
  trunk. §3 shows this trunk's own worst-case offset (21.94 mV) is bounded
  above the entropy-binding corner's *actual* offset (which draws less
  current still), and both are under 6.5 % of the ±10 % supply-corner spread
  this design's period is already characterised across. A period-vs-`vss`
  sensitivity has not been separately measured (no PSRR-style record exists
  in this repository as of this writing), so this is a bound by comparison,
  not a re-derivation of the margin itself — flagged here rather than
  silently assumed away; see Caveats.
- **No Proposed row** in `spec/` currently depends on a `vss` reference
  finer than what this bound already covers.

If a future increment tightens the entropy-binding-corner margin enough that
6.5 % of the supply-corner spread stops being clearly swamped, re-run this
document's script and, if warranted, the specific ring-period measurement
with the offset applied as a shifted `vss` source in the testbench — the
mechanism issue #234's own "What a first increment probably looks like" item
4 describes.

## 5. Reproducing this

```sh
# the full two-corner report, from committed geometry + cited sim/ records
python3 sim/tools/vss_trunk_ir_drop.py

# the CI gate: asserts the conservative bound stays under the materiality
# threshold and that the resistance model's endpoints still match the
# committed layout/floorplan/reports/interregion.json
python3 sim/tools/vss_trunk_ir_drop.py --check

# the arithmetic's own unit tests (synthetic geometry + committed-geometry guards)
python3 -m unittest sim.tests.test_vss_trunk_ir_drop -v
```

No PDK, no `klt` and no ngspice are needed for any of the above — every input
is either already-committed geometry or an already-recorded `sim/` figure.

## Caveats

- **Current-profile allocation, not a fourth measurement.** No committed
  record separates "the two rings' own oscillator current" from
  "`combiner_sampler`'s `ro_buf`+XOR share" within the 489.9 µW entropy-array
  term, and no idle-level per-block breakdown exists at all. §2 states the
  allocation rule used and why it is conservative for the two nodes farthest
  from the chip pin; it is not itself evidence of a per-region split.
- **No measured period-vs-`vss` sensitivity.** §4's jitter-margin argument
  bounds the offset by comparison against the already-characterised
  supply-corner spread, not by measuring how much a given `vss` shift moves
  `T0`. That measurement (a PSRR-style sweep, or a re-run of the
  entropy-binding-corner testbench with a shifted `vss` source) is a
  reasonable follow-up if a future margin gets tight enough for 6.5 % of the
  corner spread to matter.
- **Static DC analysis only.** This is a resistor-network DC offset, not a
  transient/di-dt drop — the starved oscillator's own current is not a fixed
  DC draw but this document uses each corner's own time-averaged active
  current, consistent with how `sim/characterization-post-layout-extracted.md`
  §7.4 itself reports `p_total_w`/idle current (time-averaged quantities, not
  instantaneous peaks).
- **The four supply branches (`vddr1`/`vddr2`/`vdd`/`vddd`) and `digital`
  itself are out of scope**, per issue #234's own "Out of scope" section —
  the four branches are each a deliberate off-die star with negligible
  (~1 ohm) on-die resistance. `digital`'s own connection into this trunk
  turned out to be more than a reference-interface question once [#224]
  actually drew it: it is a real chip-pin relocation this document's own
  §1 now reflects (chip pin moved from `x = 505.98` to `514.58 µm`,
  +2.58 ohm on `ring1`'s own path). What stays out of scope is `digital`'s
  own *internal* PDN drop — its dense multi-strap grid needs a different
  model than this trunk's single-riser-per-region chain, and no such model
  exists in this repository as of this writing.

[#222]: https://github.com/2AMLogic/gf180-trng/issues/222
[#224]: https://github.com/2AMLogic/gf180-trng/issues/224
[#225]: https://github.com/2AMLogic/gf180-trng/issues/225
[#232]: https://github.com/2AMLogic/gf180-trng/issues/232
[#234]: https://github.com/2AMLogic/gf180-trng/issues/234
[DR-0007]: ../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md
[DR-0015]: ../spec/decision-records/DR-0015-entropy-binding-corner-moves-to-the-hot-slow-corner.md
[DR-0016]: ../spec/decision-records/DR-0016-per-ring-liveness-monitor.md
[DR-0025]: ../spec/decision-records/DR-0025-full-chip-pex-scope.md
