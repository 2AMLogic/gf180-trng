---
dr: DR-0028-top-edge-legs-are-priced-in-the-sta-interface-load
title: Price the Metal4 stub, Metal5 track and Metal3 flank riser of the six top-edge digital endpoints in the STA interface load, and pin the with-legs C/R/transition table
status: Accepted
date: 2026-10-10
deciders: Builder of issue #456, under the same delegated-methodology rule DR-0025 and DR-0027 were accepted under, ratified through ordinary review of the pull request that carries it. Not an operator ratification. No ratified row moves, no claim is relaxed, and DR-0025 and DR-0027 are not edited.
supersedes: n/a
superseded_by: n/a
related: "DR-0027 (whose trunk-only table and 'follow-up required' this record answers), DR-0025, DR-0026, #315 (the top-edge routing that creates the legs), #256 (the regeneration), #233 / #242 (the interface-load treatment and the trunk-only floor), #456 (this change); sim/tests/test_run_sta_interface_load.py (pins the table below)"
---

# DR-0028: Top-edge legs are priced in the STA interface load

## Status

- 2026-10-10: **Accepted** by the Builder of #456 under delegated
  methodology, as DR-0027 was. It changes which conductor a derived
  estimate counts. It does not change what the block must do.

## Context

[DR-0027] pinned the six `digital`-facing trunks' trunk-only Metal4 C/R and
recorded that this covers only about half the drawn conductor: each of
`clk`, `rst_n`, `raw_bit`, `raw_valid`, `ring_bit1`, `ring_bit2` also has a
Metal4 stub, a Metal5 track and a Metal3 east-flank riser (#315). DR-0027
sized them crudely, with every leg at the Metal4 coefficients (about 45 ps
worst case), and named #456 as the follow-up.

The committed `interregion.json` did not carry the leg lengths.

## Decision

1. **One owner of the leg geometry.** `layout/floorplan/interregion.py`
   computes the track Y and flank-riser X in one function
   (`_top_edge_coords`), draws from it, and reports from it
   (`top_edge_legs`). Each `digital_pin_top` endpoint in
   `layout/floorplan/reports/interregion.json` now carries `legs`:
   `{layer, role, length_um, width_um}` for the stub, track and riser. The
   lengths are the drawn rectangles' end-to-end lengths (the same
   convention `trunk_length_um` uses). The report was updated by recomputing
   the wiring plan from the committed composition and adding only the `legs`
   keys; every other field is identical to the file it replaces, and the
   geometry (GDS) is untouched. `layout/tests/test_interregion.py` measures
   each reported leg off the emitted shapes and checks the committed report
   against the rules.
2. **Per-layer coefficients.** `run_sta.LAYER_RC` holds Metal3, Metal4 and
   Metal5 rows from `PARASITICS` in `klayout_tools/decks/gf180mcu.py` (klt
   0.7.0 on the sweep host), which that file transcribes from the public
   gf180mcu magic technology file (nominal corner, 5-metal stack):

   | Layer | Sheet (ohm/sq) | Area (fF/um^2) | Fringe (fF/um, per edge) |
   |---|---:|---:|---:|
   | Metal3 | 0.09 | 0.010094 | 0.030021 |
   | Metal4 | 0.09 | 0.007602 | 0.028153 |
   | Metal5 | 0.06 | 0.005798 | 0.030386 |

   The Metal4 row is the pair DR-0025 already cites. The Metal3 and Metal5
   rows were not previously used in this repository. They are
   order-of-magnitude values, not calibrated to silicon.
3. **Convention.** `InterfaceTrunk.cap_fF` and `res_ohm` are the sum of C
   and the series sum of R over the trunk and the legs, then multiplied as
   a single lumped RC with an ideal step, as before. **Vias, the Metal4
   landing pad, plate coupling between layers and neighbour coupling are not
   priced**, and neither is the Metal3 riser at the other endpoint. The
   result is still a floor on the real load (#232 / #242). The trunk-only
   figures stay available as `trunk_cap_fF`, `trunk_res_ohm` and
   `trunk_transition_ns`, and DR-0027's table is still asserted on those.
4. **The pinned with-legs table.** `InterfaceTrunkArithmeticTests` asserts
   the following with tolerances of 0.1 fF, 1 ohm and 0.1 ps, via
   `run_sta.digital_facing_trunks()` on the committed report. The
   transition is the stated `set_input_transition` at the library's
   30 %/70 % thresholds and 0.5 derate.

   | Net | Trunk-only C / R (DR-0027) | Legs (um) | C (fF) | R (ohm) | Transition, trunk-only (ps) | Transition, with legs (ps) |
   |---|---|---:|---:|---:|---:|---:|
   | `raw_bit` | 35.8 / 183 | 614.4 | 74.4 | 347 | 11.1 | 43.8 |
   | `raw_valid` | 32.3 / 165 | 619.5 | 71.2 | 331 | 9.0 | 39.9 |
   | `ring_bit1` | 28.8 / 147 | 583.1 | 65.4 | 306 | 7.2 | 33.9 |
   | `clk` | 25.4 / 130 | 543.9 | 59.6 | 280 | 5.6 | 28.3 |
   | `rst_n` | 25.4 / 130 | 573.6 | 61.5 | 286 | 5.6 | 29.8 |
   | `ring_bit2` | 25.2 / 129 | 637.4 | 65.3 | 299 | 5.5 | 33.0 |

   The worst case, `raw_bit`, is 43.8 ps, not DR-0027's crude 45 ps: that
   figure priced every leg at Metal4 and was a bound, not an estimate. The
   library `max_transition` is 4.4 to 13.2 ns, so the worst stated
   transition is about 100 times below the tightest deck (4.4 ns) and about
   300 times below the loosest (13.2 ns).

## Evidence

The sweep was re-run on the regenerated geometry, minting
`sim/records/2026-10-10-digital-sta-power-01` through `-15` (15 corners,
OpenSTA over the committed depth-2 routed DEF). Each record's
`interface_loads:` block lists the legs, the with-legs and trunk-only
figures and the ratio to that corner's `max_transition`. All six ports are
within the limit at all 15 corners (`interface_load_max_slew_violations`
is 0). Against the 2026-10-07 family (same DEF, previous report), pricing
the legs moved worst setup slack by at most 10 fs, worst hold slack by at
most 1 fs, the bisected Fmax not at all, and total 1 MHz power by at most
0.004 %. The 2026-10-07 records are not edited. Where both families cover a
corner, the newer record is the one `sim/tools/digital_corner_characterization.py`
reads.

## Alternatives considered

### Derive the legs from `interregion.py` at STA time

- **Why rejected**: it couples `sim/` to the layout module and to the
  composition request and block bboxes it needs. Reading the report keeps
  one committed artefact as the interface and lets `run_sta` stay a
  consumer.

### Price every leg at the Metal4 coefficients

- **Why rejected**: DR-0027 already did this as an explicit bound. Metal5
  has a lower sheet resistance and a different fringe, and Metal3 a larger
  area term. The deck has all three rows.

### Edit DR-0027's table

- **Why rejected**: accepted records are immutable.

## Consequences

- **Positive**: the interface load follows the drawn conductor of all six
  nets and each number has a named source.
- **Accepted cost**: still not a measurement. A full-chip extraction of
  these nets would add vias, pads and coupling. No ratified spec row depends
  on these numbers.
- **Revisit if**: `interregion.json` is regenerated with a change to any
  `digital`-facing net, or the klt deck's `PARASITICS` rows change.

[DR-0027]: DR-0027-digital-facing-trunk-estimates-follow-the-regenerated-geometry.md
