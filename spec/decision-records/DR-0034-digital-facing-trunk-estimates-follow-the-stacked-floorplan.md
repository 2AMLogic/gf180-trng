---
dr: DR-0034-digital-facing-trunk-estimates-follow-the-stacked-floorplan
title: Pin the six digital-facing trunks' C/R estimates to the stacked floorplan geometry landed in #803
status: Accepted
date: 2026-11-09
deciders: Builder of issue #803, under the same delegated-methodology rule DR-0027 was accepted under, and ratified through ordinary review of the pull request that carries it. Not an operator ratification. No spec row, ratified claim or limit changes.
supersedes: n/a
superseded_by: n/a
related: "#803 (the stacked arrangement and the redesigned digital supply tie), #797 (the measurement that led to it), DR-0027 (the same kind of re-pin for the #256 regeneration), DR-0028 (the with-legs table), DR-0025 (the original table), docs/area-floorplan-stacked-pdn-2026-11-09.md"
---

# DR-0034: Pin the six digital-facing trunks' C/R estimates to the stacked floorplan

## Status

- 2026-11-09: **Accepted** by the Builder of #803, under delegated
  methodology. Like [DR-0027], it says which committed artefact a set of
  derived estimates is read from; it does not change what the block must do.
  If review of the pull request rejects it, the pull request does not merge.

## Context

#803 stacks the `digital` region above the analog strip
([record](../../docs/area-floorplan-stacked-pdn-2026-11-09.md)). The six
digital-facing signal trunks (`clk`, `rst_n`, `raw_bit`, `raw_valid`,
`ring_bit1`, `ring_bit2`) used to end at `digital`'s east flank about 420 um
east of `combiner_sampler`; the flank now sits about 5 um east of it. Their
Metal4 trunks shorten by about 414 um each. The Metal3 east-flank risers
lengthen by about 35 um each, because the stack is taller than the row.

`sim/tests/test_run_sta_interface_load.py::InterfaceTrunkArithmeticTests`
reads the live `interregion.json` through `run_sta.digital_facing_trunks()` and
pins the estimates from [DR-0027] (trunk only) and [DR-0028] (with the legs
priced). Both tables fail against the stacked geometry, as that test's own
docstring says they should: such a change is "re-dated by a new record". No
spec row or ratified claim depends on these numbers.

## Decision

**We will pin the six trunks' estimated C/R to the stacked
`interregion.json`, using the tables below, with the same tolerances (+/-0.1 fF,
+/-1 ohm, +/-0.1 ps).** [DR-0027] and [DR-0028] are not edited; their tables
stay correct for the geometry they were measured on.

Coefficients are unchanged (`LAYER_RC`, the `klt` gf180mcu deck's rows).

Trunk only (the [DR-0027] basis):

| Net | Trunk before (um) | Trunk stacked (um) | Est. C (fF) | Est. R (ohm) | [DR-0027] C / R |
|---|---:|---:|---:|---:|---|
| `raw_bit` | 607.49 | 193.26 | 11.3 | 58 | 35.6 / 182 |
| `raw_valid` | 547.95 | 133.72 | 7.8 | 40 | 32.1 / 164 |
| `ring_bit1` | 487.76 | 73.53 | 4.3 | 22 | 28.6 / 146 |
| `clk` | 430.62 | 16.39 | 1.0 | 5 | 25.2 / 129 |
| `rst_n` | 430.32 | 16.09 | 0.9 | 5 | 25.2 / 129 |
| `ring_bit2` | 427.57 | 13.34 | 0.8 | 4 | 25.1 / 128 |

With the legs priced (the [DR-0028] basis, 30/70 % derate-0.5 convention):

| Net | C (fF) | R (ohm) | Transition (ps) | [DR-0028] C / R / ps |
|---|---:|---:|---:|---|
| `raw_bit` | 52.1 | 232 | 20.5 | 73.9 / 345 / 43.3 |
| `raw_valid` | 50.3 | 220 | 18.8 | 72.2 / 333 / 40.7 |
| `ring_bit1` | 43.1 | 191 | 13.9 | 65.0 / 303 / 33.4 |
| `clk` | 37.4 | 165 | 10.5 | 59.2 / 278 / 27.9 |
| `rst_n` | 40.7 | 176 | 12.1 | 62.5 / 289 / 30.6 |
| `ring_bit2` | 39.7 | 173 | 11.6 | 61.5 / 286 / 29.8 |

## Alternatives considered

### Keep pinning the old numbers

- **Why rejected**: the test reads the live geometry. Keeping the old values
  means either not reading `interregion.json` (which defeats #233's
  "derivation, not transcription") or not landing the stack.

### Loosen the tolerance

- **Why rejected**: the figures moved by 20 to 35 fF; no tolerance that admits
  both geometries leaves the cross-check meaningful ([DR-0027] ruled the same).

### Edit DR-0027 and DR-0028 in place

- **Why rejected**: accepted DRs are immutable (`TEMPLATE.md`).

## Consequences

- **Positive**: the test again checks the arithmetic against the committed
  geometry. The estimates fall, so the interface-load transition worst case
  falls from 43.3 ps to 20.5 ps; it was already about 100 times below the
  library `max_transition`.
- **Negative / accepted cost: the digital STA interface-load assumption is
  now conservative on the setup side and unevaluated on the hold side.** The
  committed `sim/records/*digital-sta-power*` records price the interface at
  the earlier, larger loads and stay valid as evidence about that geometry
  (they are hash-pinned to the `interregion.json` they read and append-only).
  A lighter load shortens delays, which can only reduce hold slack. The
  committed hold slack is +0.70 ns at `ff_n40C_3v60/rc-min` against loads that
  are 20 to 35 fF higher; the change is far inside that margin by a sizing
  argument, but **the STA sweep was not re-run here**, so this is not a
  measurement.
- **Follow-up required**: re-run the post-route STA interface-load sweep
  against the stacked `interregion.json` and update
  `sim/characterization-digital-sta-area-power.md`. It is simulation, which is
  opt-in, so it is tracked separately from #803.
- **Revisit if**: `interregion.json` is regenerated again with a change to any
  digital-facing trunk.

[DR-0027]: DR-0027-digital-facing-trunk-estimates-follow-the-regenerated-geometry.md
[DR-0028]: DR-0028-top-edge-legs-are-priced-in-the-sta-interface-load.md
