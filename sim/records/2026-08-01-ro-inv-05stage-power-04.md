---
record: 2026-08-01-ro-inv-05stage-power-04
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
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
  path: sim/records/raw/2026-08-01-ro-inv-05stage-power-04/
  files:
    - tt_27c_2.97v.spice  sha256:7912c66d5526dcaf37610f5981ac396e1783575457a3e2f49f786090010998ad
    - tt_27c_2.97v.log  sha256:c2c73f733ddeb6835108e00d7d0701f574aad76b834b36eb00d42255bd0e94d9
wall_time: 9.1s
---

## Result

- `period`: 6.775475e-10
- `f_osc`: 1.475911e+09
- `i_supply_a`: 2.728341e-04
- `p_active_w`: 8.103173e-04
- `e_per_cycle_j`: 5.490285e-13
- `c_eff_node_f`: 1.244835e-14
- `i_supply_first16_a`: 2.728341e-04
- `i_supply_last16_a`: 2.728341e-04

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-power --corners tt --temps 27 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / 27 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
