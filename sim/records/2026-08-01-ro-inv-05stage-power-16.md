---
record: 2026-08-01-ro-inv-05stage-power-16
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: tran
  tstop: 45n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-inv-05stage-power-16/
  files:
    - ff_125c_2.97v.spice  sha256:aeade2731c65fa2fbd052256d7a04ba35e8084f2091bb7c7332ff1a7219245f7
    - ff_125c_2.97v.log  sha256:aaaab8751391d071d041b6dd9607f4446a7f60e8e1b9b518868ffc092fb6e836
wall_time: 7.2s
---

## Result

- `period`: 6.548016e-10
- `f_osc`: 1.527180e+09
- `i_supply_a`: 2.939709e-04
- `p_active_w`: 8.730935e-04
- `e_per_cycle_j`: 5.717031e-13
- `c_eff_node_f`: 1.296247e-14
- `i_supply_first16_a`: 2.939707e-04
- `i_supply_last16_a`: 2.939711e-04

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-power --corners ff --temps 125 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 2.97 V / 125 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
