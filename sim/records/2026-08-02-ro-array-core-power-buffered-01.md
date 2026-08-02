---
record: 2026-08-02-ro-array-core-power-buffered-01
date: 2026-08-02T22:08:43Z
status: valid

testbench:
  path: sim/tb/ro-array-core-power-buffered/tb_ro_array_core_power_buffered.sp
  sha: d4c56568ffb202ef8ba0492eff4368e46cc196f6
netlist:
  path: design/ro_array_core.spice
  sha: 72fc8a57fa9b48e5338681d0fad1ddaeb2e560fc
repo_commit: 12110608f16a0f90f2b69d67350cb4d0f684d13b-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran
  tstop: 50n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-02-ro-array-core-power-buffered-01/
  files:
    - ff_-40c_3.63v.spice  sha256:4495b8961478724322c70d8e8fa732f49195de3c2099e703ff0cb186b682895e
    - ff_-40c_3.63v.log  sha256:a552c4097c39e012148d0215673e756d4815185deed48cfe34065f4488e399bb
wall_time: 48.7s
---

## Result

- `period_r1`: 4.015411e-09
- `period_r2`: 3.773032e-09
- `f_r1`: 2.490405e+08
- `f_r2`: 2.650389e+08
- `i_r1_a`: -3.649884e-05
- `i_r2_a`: -3.874489e-05
- `i_buf1_a`: -8.196446e-06
- `i_buf2_a`: -8.835320e-06
- `i_tree_a`: -1.655776e-05
- `e_cycle_r1_j`: -5.320049e-13
- `e_cycle_buf1_j`: -1.194709e-13
- `c_eff_node_r1_f`: -3.670369e-15
- `ring_swing_v`: 3.70489
- `xo_swing_v`: 3.76889
- `i_total_a`: -1.088333e-04
- `p_rings_w`: -2.731347e-04
- `p_bufs_w`: -6.182531e-05
- `p_buf1_w`: -2.975310e-05
- `p_buf2_w`: -3.207221e-05
- `p_total_w`: -3.950647e-04
- `xo_trans_per_s`: 1.028159e+09

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power-buffered --corners ff --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Issue #75's buffered variant of sim/tb/ro-array-core-power/. The ONLY circuit difference is one minimum-width inverter buffer per ring between that ring's output node and xa1's input (xa1 now sees rb1/rb2, not ro1/ro2). This deck hand-expands ro_array_core's two rings rather than instantiating the composed subckt, because the composed subckt has no splice point for the buffer and the buffer is not adopted into the schematic; the expansion is device-for-device identical to design/ro_array_core.spice's own (verified against it at netlist review time).
- Each buffer has its own metered supply pin (vddb1/vddb2), separate from its ring's own pin (vddr1/vddr2) and from the tree's (vdd) -- the same per-branch bookkeeping sim/tb/ro-array-core-power/ already uses to separate ring current from tree current. All branches are zero-impedance taps off the same ideal vsup, so the metering split adds no electrical path.
- The buffer device sizing (pfet_03v3 w=0.44u, nfet_03v3 w=0.22u, both l=0.28u) matches xor2's own input stage and ro_stage's core inverter -- the minimum-width 3.3 V inverter this design already uses elsewhere.
- Run at ff/-40 C/3.63 V for direct comparison against layout/floorplan/README.md's ~24.4 uW estimate (11.9 uW + 12.6 uW at that corner, from P = C_eff * V^2 * f using sim/records/2026-08-01-ro-array-core-power-04.md's measured c_eff_node_r1 and per-ring frequencies). tt and ss are also swept for the same reason sim/tb/ro-array-core-power/ sweeps them: cross-corner context, not a claim about any corner but ff/-40C/3.63V.
- Single corner per record, per sim/README.md. No jitter or entropy claim is made by this deck -- it is deterministic (no trnoise() sources), matching sim/tb/ro-array-core-power/'s own scope.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
