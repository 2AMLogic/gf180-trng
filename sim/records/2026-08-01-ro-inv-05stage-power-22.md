---
record: 2026-08-01-ro-inv-05stage-power-22
date: 2026-08-01T00:23:28Z
status: valid

testbench:
  path: sim/tb/ro-inv-05stage-power/tb_ro_inv_05stage_power.sp
  sha: 299df2aad1f5ba3f60a87090cc50fb450929f518
netlist:
  path: sim/tb/ro-inv-05stage-power/tb_ro_inv_05stage_power.sp
  sha: 299df2aad1f5ba3f60a87090cc50fb450929f518
repo_commit: f03dd6c3036d67bd4f2245b92bb7765e23396d55-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 27

analysis:
  type: tran
  tstop: 45n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-inv-05stage-power-22/
  files:
    - ss_27c_2.97v.spice  sha256:4f677b4061af12527bb0f0012f71c5ae78a3d792d570199d095a8979c0fd9d56
    - ss_27c_2.97v.log  sha256:d5462da5c9f7bf01a545f46a642bfa7b038e95dd3a753fbc7b2d6100c3e56d76
wall_time: 7.3s
---

## Result

- `period`: 8.338252e-10
- `f_osc`: 1.199292e+09
- `i_supply_a`: 2.208831e-04
- `p_active_w`: 6.560227e-04
- `e_per_cycle_j`: 5.470083e-13
- `c_eff_node_f`: 1.240255e-14
- `i_supply_first16_a`: 2.208830e-04
- `i_supply_last16_a`: 2.208831e-04

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-power --corners ss --temps 27 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 27 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
