# Floorplan: stacked arrangement with a redesigned digital PDN tie (2026-11-09)

Record for issue #803 (follow-up to #797, record
[`area-floorplan-arrangement-2026-11-09.md`](area-floorplan-arrangement-2026-11-09.md)).
That record measured that stacking the `digital` region above the analog strip
composes cleanly and shrinks the composed bbox by 39 %, and listed three things
that stopped it landing. This record lands the stack and the redesign that
removes each blocker. The ratified Area row (< 0.05 mm^2) is untouched: its
miss stays disclosed as FAIL, and the 33 mV IR-drop yardstick, the 20 um
isolation channel and every block's internals are unchanged.

Area is geometry; no PVT corner applies. The IR-drop figures are the existing
corner-swept bounds from `sim/tools/digital_supply_ir_drop.py` and keep their
own corners.

## What changed

- `layout/floorplan/floorplan.py`: `_stack_origins` places the analog regions
  as one strip at `y = 0` and `digital` one `ISOLATION_CHANNEL_UM` above the
  tallest of them. `compose()` uses its 2-D origins.
- `layout/floorplan/interregion.py`: the `vddd`/`vss` tie is a 2 um wide
  Metal3 riser per net on the stack's east flank, east of every top-pin wrap
  column, with a four-cut Via3 row on the trunk and a 16-cut Via3 + 16-cut Via4
  array under a Metal5 dock onto the east end of the lowest PDN strap.
  `stack_digital_east_um` derives `digital`'s east edge from the riser tables.
- `sim/tools/digital_supply_ir_drop.py`: prices the cuts of one landing, which
  the plan tags with a shared `_array` id, as n parallel cuts. The 33 mV
  yardstick, the resistance variants and the current records are not edited.
- `layout/tests/test_interregion.py`: one helper no longer assumes `digital` is
  `combiner_sampler`'s east neighbour, and new tests pin the properties below.

Tool build. As in #797, the committed floorplan artefacts are normative under
`klayout-tools==0.6.0` with `klayout==0.30.10` (DR-0026 as amended), so the
floorplan flow ran from a throwaway virtual environment at that pin, not the
host `klt`; `signoff/check.py` ran under `klayout-tools==0.8.0`, the grader <!-- klt-pin: grader -->
pin in `.github/workflows/ci.yml`. No host tool was installed or changed.

## 1. Before and after (`klt economy`, klt 0.6.0, same build both rows)

| | committed row (before) | stacked, this change |
|---|---:|---:|
| bbox (um) | 931.145 x 413.515 | 516.915 x 451.765 |
| bbox area (um^2) | 385 042.425 | 233 524.105 |
| utilization | 0.4221 | 0.6949 |
| whitespace (um^2) | 222 523.375 (0.5779) | 71 237.552 (0.3051) |

The stack removes 151 518 um^2 of bbox (39.4 %). It does not reach the
`area.json` roll-up (173 158 um^2) and does not close the Area row. The
`digital` east edge is an output of the riser tables (5.0 um past the strip's
guarded east edge), not a constant.

## 2. Blockers from #797 and how each is met

1. **IR drop.** `python3 sim/tools/digital_supply_ir_drop.py --check` passes at
   the unchanged 33.000 mV yardstick: active cross-corner bound **6.379 mV**,
   idle **0.138 mV**. The committed row measured 23.180 mV and the single-cut
   stacked trial 69.001 mV. The high-resistance external feed is 14.8 ohm for
   `vddd` and 12.4 ohm for `vss`, against about 85 and 70 ohm for the single
   0.30 um riser with single cuts. The model's per-element breakdown is in
   `sim/characterization-digital-supply-ir-drop.md`. #797 noted the riser
   length was a candidate cause, not an established one; this change widens the
   riser and multiplies the cuts without shortening the path, and the bound
   falls well below the committed row's, so the single-cut, 0.30 um riser was
   the dominant term.
2. **Isolation channel.** The risers are on the east flank: nothing the tie
   draws is west of the strip's east edge, so it crosses no `ring1 | ring2` or
   `ring2 | combiner_sampler` channel (asserted by
   `StackedDigitalSupplyTie.test_no_pdn_conductor_enters_a_ring_isolation_channel`).
   The isolation argument is recorded in `layout/floorplan/README.md`, section
   "The stacked arrangement and the `digital` supply tie". No substrate
   coupling attenuation is claimed; DRC and LVS do not see isolation.
3. **Row-ordering test.** `test_clk_and_rst_n_never_run_west_of_the_combiner_sampler_region`
   was not edited or loosened. Its failure in #797 (88.115 against a 203.32
   floor) came from its helper deriving `combiner_sampler`'s east edge from the
   next region in the row, which stopped being the neighbour; the helper now
   reads the region's placed bbox. The rationale it cites (DR-0012-clock: `clk` and
   `rst_n` reach the samplers from the `digital` side, never across a ring's
   isolation channel) is still satisfied, and a new test asserts it against the
   strip's east edge.

The east-edge riser columns of `combiner_sampler` and the digital top-pin wrap
are separated by construction: `stack_digital_east_um` solves for the least
`digital` east edge at which the first wrap column clears the eastmost
`combiner_sampler` column by `metal3.space.1` plus a margin, and
`test_derived_east_edge_clears_the_combiner_sampler_columns` re-checks it.
Moving either riser table re-derives the edge; no overhang constant is left.

## 3. Composed geometry (klt 0.6.0, `python3 layout/floorplan/floorplan.py`)

| Check | Result |
|---|---|
| Composed stream DRC | clean, 0 violations, 0 new |
| Extracted top-level pins | 112 of 112 expected |
| Composed LVS vs the declared inter-region reference | match, 2 mismatches, no unexpected category (the same 2 as the committed tree) |
| Per-region ring fit (DRC + LVS, x4) | clean, match (unchanged) |
| Isolation channel | 20 um between the strip and `digital`; 20 um between analog regions |

The first run of this redesign extracted 114 pins: the Metal5 dock stopped at
the riser's west edge and did not cover the Via4 array, so `vddd` and `vss` each
split in two. The dock now spans the whole array and the count is 112.

## 4. Commands run and exit statuses

Run on the final tree. Unavailable or unrun checks are listed in section 5.

| Command | Exit |
|---|---:|
| `python3 layout/floorplan/floorplan.py --write` (klt 0.6.0 venv) | 0 |
| `python3 layout/floorplan/floorplan.py` (klt 0.6.0 venv; committed artefacts match) | 0 |
| `python3 signoff/check.py --write` then `python3 signoff/check.py` (klt 0.8.0 venv) | 0, 0 (18/22 items met, unchanged) |
| `npm run lint` | 0 |
| `npm run test` (the `sim/tests` suite) | 0 |
| `npm run test:layout` | 0 |
| `npm run check:spec` | 0 |
| `npm run check:record-checksums`, `check:artifact-manifests`, `check:regmap`, `check:floorplan-netlist` | 0 each |
| `npm run check:fixtures`, `check:digital-input`, `check:digital-tap-distance`, `check:evidence-history`, `check:no-host-paths` | 0 each |
| `npm run check:layout` (klt 0.6.0 venv) | 0 |

Not run: `sim/selftest.sh` (the last step of `check:ci`; it simulates when
ngspice and the PDK exist, and simulation is opt-in here), `check:lint-shell`,
and the `--require-tools` variants in `check:all`. The `sim/tests` suite
includes tests that exercise `klt sim` against the batch backend; those
refused submissions are the suite's own and were not hand-launched.

The `sim/tests` suite initially failed on seven tests pinned to the previous
geometry (the `vss` lumped total, three single-cut assumptions in
`test_digital_supply_ir_drop.py`, the two interface-trunk tables, and the
bbox quoted in the Chipalooza proposal's Area row). They are re-pinned in this
change; the interface-trunk tables through
[DR-0034](../spec/decision-records/DR-0034-digital-facing-trunk-estimates-follow-the-stacked-floorplan.md),
which also records the STA interface-load re-run as an unperformed follow-up.

## 5. Stale consumers (not re-simulated)

`layout/pex/` and the `sim/tb/*-extracted-fullchip` testbenches that reference
`trng_floorplan` (`ro-array-core-power`, `ro-array-core-startup`,
`ro-array-core-pvt-q`, `sampler-core-idle-leakage`, with records dated
2026-09-12 and 2026-10-30) use extracted full-chip inputs built from the
previous composed stream, so they are **stale** against this one. Simulation is
opt-in and was not run; re-simulation is tracked separately and is out of scope
for #803. Their committed records remain evidence about the previous
arrangement.

## Reproduce

```sh
uv venv .venv-klt && uv pip install --python .venv-klt/bin/python \
  "klayout-tools==0.6.0" "klayout==0.30.10"
PATH=$PWD/.venv-klt/bin:$PATH python3 layout/floorplan/floorplan.py
PATH=$PWD/.venv-klt/bin:$PATH klt economy layout/floorplan/trng_floorplan.gds
python3 sim/tools/digital_supply_ir_drop.py --check
```
