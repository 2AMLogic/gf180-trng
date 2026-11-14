---
dr: DR-0035-digital-facing-trunk-estimates-follow-the-bottom-edge-pins
title: Pin the six digital-facing trunks' C/R estimates to the bottom-edge pin geometry landed in #866
status: Accepted
date: 2026-11-13
deciders: Builder of issue #866, under the same delegated-methodology rule DR-0027 and DR-0034 were accepted under, and ratified through ordinary review of the pull request that carries it. Not an operator ratification. No spec row, ratified claim or limit changes.
supersedes: n/a
superseded_by: n/a
related: "#866 (the rebuild under the toolchain pdk-nightly.yml installs), DR-0034 (the same kind of re-pin for #803's stacked floorplan), DR-0028 (the with-legs table), DR-0027 (the #256 regeneration), DR-0025 (the original table), #315 (interregion.py routes both pin edges)"
---

# DR-0035: Pin the six digital-facing trunks' C/R estimates to the bottom-edge pin geometry

## Status

- 2026-11-13: **Accepted** by the Builder of #866, under delegated
  methodology. Like [DR-0027] and [DR-0034], it says which committed artefact
  a set of derived estimates is read from; it does not change what the block
  must do. If review of the pull request rejects it, the pull request does
  not merge.

## Context

#866 re-ran the digital chain under the toolchain
`.github/workflows/pdk-nightly.yml` actually installs (Yosys 0.69 via
`yowasp-yosys==0.69.0.0.post1233`, and the latest tagged klayout-tools
release with `klayout==0.30.10`), because the committed synthesis outputs had
been produced by a local Yosys 0.67+post build and the nightly's synthesis
staleness guard had been red since 2026-11-04.

The rebuild moved one thing the composed floorplan reads: OpenROAD's
`place_pins` put `trng_top`'s six inter-region signal pins on the block's
**bottom** edge, where the previous DEF had them on the top edge.
`layout/digital/build.py` sends no `io.pin_constraints`, so the edge is a
property of the place-and-route run, not a design input — which is why
`layout/floorplan/interregion.py` has routed both edges since [#315].

A bottom-edge pin drops straight into the `combiner_sampler | digital`
isolation channel and joins its trunk there. A top-edge pin instead leaves
the block on a Metal4 stub, runs east on a Metal5 track above the guard ring,
and comes down a Metal3 riser on the east flank — the three `legs` [DR-0028]
exists to price. So this geometry has **no legs at all**, and the Metal4
trunks lengthen to reach west under the strip to each pin's own x.

`sim/tests/test_run_sta_interface_load.py::InterfaceTrunkArithmeticTests`
reads the live `interregion.json` through `run_sta.digital_facing_trunks()`
and pins [DR-0034]'s two tables. Both fail against this geometry, as that
test's own docstring says they should: such a change is "re-dated by a new
record". No spec row or ratified claim depends on these numbers.

## Decision

**We will pin the six trunks' estimated C/R to the bottom-edge
`interregion.json`, using the table below, with the same tolerances
(±0.1 fF, ±1 ohm, ±0.1 ps).** [DR-0025], [DR-0027], [DR-0028] and [DR-0034]
are not edited; their tables stay correct for the geometry they were measured
on.

Coefficients are unchanged (`LAYER_RC`, the `klt` gf180mcu deck's rows).

Because no endpoint carries legs, the trunk-only basis ([DR-0027]'s) and the
with-legs basis ([DR-0028]'s) are the **same numbers** here, and
`InterfaceTrunk.legs` is empty for all six. Transitions are at the 30/70 %,
derate-0.5 convention [DR-0028] uses.

| Net | Trunk (µm) | Est. C (fF) | Est. R (ohm) | Transition (ps) | [DR-0034] C / R / ps |
|---|---:|---:|---:|---:|---|
| `clk` | 272.05 | 15.9 | 82 | 2.2 | 37.4 / 165 / 10.5 |
| `rst_n` | 248.41 | 14.6 | 75 | 1.8 | 40.7 / 176 / 12.1 |
| `ring_bit2` | 228.84 | 13.4 | 69 | 1.6 | 39.7 / 173 / 11.6 |
| `ring_bit1` | 116.43 | 6.8 | 35 | 0.4 | 43.1 / 191 / 13.9 |
| `raw_valid` | 44.34 | 2.6 | 13 | 0.1 | 50.3 / 220 / 18.8 |
| `raw_bit` | 8.74 | 0.5 | 3 | 0.0 | 52.1 / 232 / 20.5 |

## Alternatives considered

### Keep pinning [DR-0034]'s numbers

- **Why rejected**: the test reads the live geometry. Keeping the old values
  means either not reading `interregion.json` (which defeats [#233]'s
  "derivation, not transcription") or not landing the rebuild — and the
  rebuild is what makes the nightly's synthesis guard green again.

### Loosen the tolerance

- **Why rejected**: the figures fall by 21 to 52 fF; no tolerance that admits
  both geometries leaves the cross-check meaningful ([DR-0027] and [DR-0034]
  ruled the same).

### Constrain `place_pins` to the north edge so the old table still holds

- **Why rejected**: it would make a property of one stochastic
  place-and-route run into a design input, on no evidence that the top edge
  is better. It is not: the bottom-edge route is shorter on every one of the
  six nets, the composed stream is still DRC-clean and still LVS-matches, and
  [DR-0012]-clock's constraint still holds (no `clk`/`rst_n` conductor west of
  `combiner_sampler`'s own west edge, so none over either ring's isolation
  channel). If a future issue does want the edge pinned, `klt
  place-and-route` takes `io.pin_constraints` and that is the place to do it
  — with its own rationale, not as a side effect of this re-pin.

### Edit [DR-0034] in place

- **Why rejected**: accepted DRs are immutable (`TEMPLATE.md`).

## Consequences

- **Positive**: the test again checks the arithmetic against the committed
  geometry. The estimates fall again — the interface-load transition worst
  case goes from 20.5 ps to 2.2 ps, against a library `max_transition` of
  4.4 to 13.2 ns depending on corner, so the margin widens from about 200× to
  about 2000×.
- **Unlike [DR-0034], the STA sweep *was* re-run against this geometry.**
  `sim/records/2026-11-13-digital-sta-power-01..15` and
  `2026-11-13-digital-sta-activity-01..15` read this `interregion.json` at run
  time and price the interface at these loads, so the committed timing and
  power are measurements of the committed geometry, not of a superseded one.
  The hold-side question [DR-0034] had to leave open is therefore closed by
  measurement here: hold slack is +0.6953 ns at `ff_n40C_3v60/rc-min`, within
  1 ps of [DR-0034]'s +0.6958 ns.
- **Negative / accepted cost**: [DR-0028]'s leg-pricing path is exercised by
  no committed geometry while these pins stay on the bottom edge. It is still
  covered by `sim/tests/test_run_sta_interface_load.py`'s synthetic-report
  tests and by `layout/tests/test_interregion.py`'s bottom/top-edge pair, so
  it is tested, not merely retained.
- **Revisit if**: `interregion.json` is regenerated again with a change to any
  digital-facing trunk — including another flip of the pin edge.

[DR-0012]: DR-0012-sampler-fixed-external-clock.md
[DR-0025]: DR-0025-full-chip-pex-scope.md
[DR-0027]: DR-0027-digital-facing-trunk-estimates-follow-the-regenerated-geometry.md
[DR-0028]: DR-0028-top-edge-legs-are-priced-in-the-sta-interface-load.md
[DR-0034]: DR-0034-digital-facing-trunk-estimates-follow-the-stacked-floorplan.md
[#233]: https://github.com/2AMLogic/gf180-trng/issues/233
[#315]: https://github.com/2AMLogic/gf180-trng/issues/315
