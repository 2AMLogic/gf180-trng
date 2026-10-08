# ro-ring11-pex — ring1 schematic vs. extracted, as a native `klt pex` report

Issue [#326](https://github.com/2AMLogic/gf180-trng/issues/326). The producer
behind T1 item 7's analog citation (`signoff/evidence/post-layout/`).

`klt pex` extracts `layout/rings/ro_ring11/ro_ring11.gds` (ring1, the
assembled, DRC-clean, LVS-matching eleven-stage ring) with parasitics, runs
`request.json` once against the schematic DUT and once against the extracted
netlist at every corner, and reports a per-corner, per-row delta. This is the
same physics as the routing-level re-run in
`sim/characterization-post-layout-extracted.md` §7 (issue #217): the ring's
own drawn devices plus its hand-routed inter-stage chain and rail straps.

| File | Role |
|---|---|
| `request.json` | the `klt sim` request: 27 corners (`{tt, ff, ss}` x `{2.97, 3.30, 3.63}` V x `{-40, 27, 125}` C, DR-0006's grid), `tran 10p 1300n`, three `.meas` rows |
| `tb_ro_ring11_pex.sp` | the circuit body: supply, enable tied to supply, one `.ic` kick, the DUT; its one `.include` is what `klt pex` re-points |
| `ro_ring11_schematic.spice` | generated schematic DUT: `design/ro_array_core.spice`'s ring at ring1 sizing, under the extraction's fifteen-port header |
| `build_dut.py` | generates the DUT, `--check`s it, and `--verify-netlist`s a netlist `klt pex` wrote |

## Cold start

```bash
pip install "klayout-tools==0.6.0" "klayout==0.30.10"   # DR-0026's producer build
python3 sim/tb/ro-ring11-pex/build_dut.py --check
python3 signoff/publish_item7_analog.py                 # runs klt pex, then publishes
python3 signoff/check.py --write
```

## Rows

| Row | `.meas` | Notes |
|---|---|---|
| `period_s` | 10th to 11th rising 50 % crossing of `ro` | one period, after startup; the ring is noiseless and deterministic here |
| `supply_current_avg_a` | `avg i(vsupply)` over 300–1300 ns | SPICE sign convention: negative is current out of the supply. The window is fixed in time, not in periods: at least ~40 periods at the slowest corner, so the truncation error is a few percent at most |
| `ro_swing_v` | `pp v(ro)` over 300–1300 ns | |

No row carries a `limits` block. A row's `pass` therefore means "measured on
both sides" (the ring oscillated and every crossing was found), not "met a
spec". None of these is a ratified spec row; the delta is the content.

## Why ring1 and not `combiner_sampler`

`klt pex` reuses the testbench's `xdut` line on both sides, so the schematic
DUT has to carry the extraction's port list. Ring1's extraction has fifteen
ports, eleven of them the ring nodes, and each can be positively identified
from the extracted netlist's own device geometry (`build_dut.py`). The rows
are ones the existing post-layout work already measures (ring period and
supply current), at the corners it uses. `combiner_sampler` needs a clocked
two-ring stimulus and a schematic DUT that exposes its internal buffer and
XOR nets as ports; that is not done here.

## What this does not cover

- **Ring2**, the buffers, the XOR combiner, the four samplers and every
  inter-region net. Ring1 only.
- **Bodies.** The layout has no n-well taps, so every PMOS body in the
  extraction is an anonymous floating net: the envelope's `body_bias.status`
  is `"unbiased"`, and `klt`'s own documentation calls a re-simulation of
  such a netlist physically wrong, not merely imprecise. The schematic side
  ties PMOS bulk to `vddr`. See signoff/README.md, "Item 7 analog".
- **The schematic's `cld`.** Each schematic stage output carries the
  schematic's 0.5 fF lumped wiring estimate; the extracted side has none and
  carries the drawn parasitics instead.
- **Noise, mismatch, load.** Deterministic transient, no device mismatch,
  `ro` unloaded (no `ro_buf`), so absolute periods differ from the
  array-level records in `sim/records/`.
- **The PDK switch file.** `design.ngspice`'s `.param` values are restated in
  the testbench body: `klt pex` allows one `.include`, and it is the one it
  swaps (klayout-tools#2871).
