---
record: 2026-08-01-ro-inv-05stage-power-26
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
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-08-01-ro-inv-05stage-power-26/
  files:
    - ss_125c_3.30v.spice  sha256:213874a9dd2109623ca00849ea37ec3bfd3ab9fb60522b9a2a7d516b51df10f4
    - ss_125c_3.30v.log  sha256:2bf1701bbaa9ab3c4a946f503add3f9f6b6109ec3332293d734259a22886ad3c
wall_time: 14.6s
---

## Result

- `period`: 8.822501e-10
- `f_osc`: 1.133465e+09
- `i_supply_a`: 2.402108e-04
- `p_active_w`: 7.926958e-04
- `e_per_cycle_j`: 6.993559e-13
- `c_eff_node_f`: 1.284400e-14
- `i_supply_first16_a`: 2.402108e-04
- `i_supply_last16_a`: 2.402109e-04

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-power --corners ss --temps 125 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.30 V / 125 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
