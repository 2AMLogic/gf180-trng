---
dr: DR-0027-digital-facing-trunk-estimates-follow-the-regenerated-geometry
title: Treat DR-0025's digital-facing trunk table as a dated depth-8 snapshot, and pin the six trunks' C/R estimates to the geometry regenerated in #256
status: Accepted
date: 2026-10-10
deciders: Doctor for PR #454 (issue #256), under the same delegated-methodology rule DR-0025 was accepted under, and ratified through ordinary review of the pull request that carries it. Not an operator ratification. No ratified row moves, no claim is relaxed, and DR-0025's decision stands.
supersedes: n/a
superseded_by: n/a
related: "#256 / PR #454 (the regeneration that moved the trunks), #255 and #315 (the depth-2 place-and-route and the top-edge pin routing that the regeneration picks up), DR-0025 (whose Context table this record dates. Its decision is unchanged and it is not edited), DR-0026 (the klt build the regenerated reports are produced under), #233 / #242 (the STA interface-load treatment that reads these trunks, and the trunk-only floor it discloses); sim/tests/test_run_sta_interface_load.py (the test that pins the six estimates), #456 (follow-up: price the top-edge legs, re-run the STA interface-load sweep)"
---

# DR-0027: Treat DR-0025's digital-facing trunk table as a dated depth-8 snapshot, and pin the six trunks' C/R estimates to the geometry regenerated in #256

## Status

- 2026-10-10: **Accepted** by the Doctor of PR #454 (issue #256), under
  delegated methodology. This record makes the same kind of change as
  [DR-0025]: it says which committed artefact a set of derived estimates is
  read from. It does not change what the block must do. If review of the PR
  rejects it, the PR does not merge.

## Context

[DR-0025]'s Context section tabulates first-order Metal4 C and R for every
inter-region trunk. It computes them from `layout/floorplan/reports/
interregion.json` as committed on 2026-09-12, which is the depth-8 `digital`
place-and-route. The record is immutable once accepted, and its table is
correct for that geometry.

`sim/tests/test_run_sta_interface_load.py::InterfaceTrunkArithmeticTests`
cross-checks `run_sta.InterfaceTrunk`'s arithmetic against those six
`digital`-facing rows. It does this through `run_sta.digital_facing_trunks()`,
which reads the live `interregion.json`, so it is tied to the committed
geometry rather than to a spec limit. No spec row or ratified claim depends
on these six numbers.

Issue #256 (PR #454) regenerated `interregion.json` against the depth-2
place-and-route ([#255], repaired by [#315]). The depth-2 `trng_top.def`
places `clk`, `rst_n`, `raw_bit`, `raw_valid`, `ring_bit[0]` and
`ring_bit[1]` on the block's **top** edge. Under [#315]'s routing, each of
those endpoints rises on Metal4, runs east on a Metal5 track above the guard
ring, and drops down the free east flank on a Metal3 riser to the Metal4
trunk. The trunk's `digital` end therefore moves from the pin's own x
(759.7 to 841.5 µm absolute at depth 8) to the east flank (921.5 to
925.2 µm). That makes all six trunks longer. The `ro1`, `ro2`, `vss`, `en*`
and supply trunks do not change.

## Decision

**We will pin the six `digital`-facing trunks' estimated C/R to the
regenerated `interregion.json`, using the table below, and keep DR-0025's
table as the depth-8 record it is.** `InterfaceTrunkArithmeticTests` asserts
the table below with the same tolerances as before (±0.1 fF, ±1 Ω). DR-0025
is not edited.

The coefficients are the same as DR-0025's: the `klt` gf180mcu deck's Metal4
values, 0.09 Ω/sq, 0.007602 fF/µm² and 0.028153 fF/µm, at
`WIRE_W = 0.30 µm`. Only the trunk itself is counted, as in DR-0025.

| Net | `digital` pin | Trunk at depth 8 (µm) | Trunk regenerated (µm) | Est. C (fF) | Est. R (Ω) | DR-0025 C / R (depth 8) |
|---|---|---:|---:|---:|---:|---|
| `raw_bit` | `raw_bit` | 524.77 | 610.70 | 35.8 | 183 | 30.8 / 157 |
| `raw_valid` | `raw_valid` | 446.61 | 551.16 | 32.3 | 165 | 26.2 / 134 |
| `ring_bit1` | `ring_bit[0]` | 343.16 | 490.97 | 28.8 | 147 | 20.1 / 103 |
| `clk` | `clk` | 353.78 | 433.83 | 25.4 | 130 | 20.7 / 106 |
| `rst_n` | `rst_n` | 339.34 | 433.53 | 25.4 | 130 | 19.9 / 102 |
| `ring_bit2` | `ring_bit[1]` | 265.47 | 430.78 | 25.2 | 129 | 15.6 / 80 |

DR-0025's **decision** is unchanged. Its filter is structural: only trunks
with a transistor-level device at both ends are simulated. That filter still
selects `ro1` and `ro2`, and their trunk lengths (128.40 and 35.92 µm) did not
change in the regeneration. None of the six trunks above is in that scope,
before or after.

## Alternatives considered

### Keep pinning DR-0025's depth-8 numbers

- **What**: leave the test's expected values as they were.
- **Why plausible**: the values match a ratified record word for word.
- **Why rejected**: the test reads the live geometry. To keep it at depth-8
  values, either the test would have to stop reading `interregion.json`,
  which defeats its purpose (#233's "derivation, not transcription"), or
  the regeneration would have to be reverted. The depth-8 numbers are
  history, not a limit.

### Loosen the tolerance

- **What**: widen `delta` until both geometries pass.
- **Why rejected**: a tolerance of about 17 fF would make the cross-check
  meaningless. Review on PR #454 ruled it out explicitly.

### Edit DR-0025's table in place

- **Why rejected**: accepted DRs are immutable (`TEMPLATE.md`).

## Consequences

- **Positive**: the test again checks the arithmetic against the geometry
  that is actually committed. The depth-8 numbers stay readable in
  DR-0025, and the `sim/records/*digital-sta-power*` records already carry
  the sha256 of the `interregion.json` they read.
- **Negative / accepted cost: the trunk-only floor is now much lower than
  the drawn wire.** DR-0025 assumed that Metal3 risers are "a few µm each
  and contribute well under 1 fF apiece". That still holds for bottom-edge
  pins. It does not hold for these six top-edge endpoints. `trunk_length_um`
  does not count the [#315] legs, which are estimated from `trng_top.def`'s
  pin positions and `interregion.py`'s track and riser rules:

  | Net | Metal4 stub | Metal5 track | Metal3 riser | Uncounted total |
  |---|---:|---:|---:|---:|
  | `clk` | 2.3 | 134.9 | 405.9 | ≈543 µm |
  | `rst_n` | 3.0 | 162.5 | 407.3 | ≈573 µm |
  | `raw_bit` | 3.7 | 201.3 | 408.7 | ≈614 µm |
  | `raw_valid` | 4.4 | 204.2 | 410.1 | ≈619 µm |
  | `ring_bit1` | 5.1 | 165.7 | 411.5 | ≈582 µm |
  | `ring_bit2` | 5.8 | 218.0 | 412.9 | ≈637 µm |

  For these nets, the trunk-only estimate therefore covers roughly half of
  the drawn conductor. This is *in addition to* the via and riser floor
  that #242 measured on the short `ro1` and `ro2` trunks. As a crude stand-in,
  pricing every leg at the Metal4 coefficients gives a worst-case lumped
  30/70 % derated transition of about 45 ps (`raw_bit`). The trunk-only
  figure is 11.1 ps. Both are about 100 times or more below the library
  `max_transition` of 4.4 to 13.2 ns that
  `sim/characterization-digital-sta-area-power.md` reports for these ports.
  This is a sizing argument, not a measurement. No ratified spec row
  depends on it.
- **Follow-up required** ([#456]): price the [#315] top-edge legs in
  `run_sta.InterfaceTrunk`, or read them from an extraction, and re-run the
  post-route STA interface-load sweep against the regenerated geometry.
  The existing `digital-sta-power` records stay valid as evidence about
  the depth-8 trunks, because they are hash-pinned to that
  `interregion.json`. They are append-only and are not edited.
- **Revisit if**: `interregion.json` is regenerated again with a change to
  any `digital`-facing trunk. The test fails, as it should, and the
  estimates are re-dated by a new record rather than by editing this one.

[DR-0025]: DR-0025-full-chip-pex-scope.md
[#255]: https://github.com/2AMLogic/gf180-trng/issues/255
[#315]: https://github.com/2AMLogic/gf180-trng/issues/315
[#456]: https://github.com/2AMLogic/gf180-trng/issues/456
