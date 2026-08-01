---
record: 2026-08-01-ro-inv-05stage-power-14
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
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-08-01-ro-inv-05stage-power-14/
  files:
    - ff_27c_3.30v.spice  sha256:d8c7a7543fc17390a28e66a84126d4e9769dcf97cfe36937a5501198b50a9d24
    - ff_27c_3.30v.log  sha256:48f5bd0e5ac8eb2685efcdbeb49bed7447a9843bec2c6e94bd01cd7c8d73ddda
wall_time: 6.9s
---

## Result

- `period`: 5.218162e-10
- `f_osc`: 1.916384e+09
- `i_supply_a`: 4.038394e-04
- `p_active_w`: 0.00133267
- `e_per_cycle_j`: 6.954088e-13
- `c_eff_node_f`: 1.277151e-14
- `i_supply_first16_a`: 4.038395e-04
- `i_supply_last16_a`: 4.038394e-04

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-power --corners ff --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.30 V / 27 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
