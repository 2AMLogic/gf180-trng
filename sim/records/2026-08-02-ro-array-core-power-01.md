---
record: 2026-08-02-ro-array-core-power-01
date: 2026-08-02T23:55:06Z
status: valid

testbench:
  path: sim/tb/ro-array-core-power/tb_ro_array_core_power.sp
  sha: 07f62df20bff89c6c21be7d68f078fe23c717c6b
netlist:
  path: design/ro_array_core.spice
  sha: fd0aa75500320b36f980126377e3d07c71c0e6b1
repo_commit: fdbc373e5ede42fcecd66f63ba5e9b7bb911ba59-dirty

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
  path: sim/records/raw/2026-08-02-ro-array-core-power-01/
  files:
    - ff_-40c_3.63v.spice  sha256:ef97eeeef2045d664c20a5d6890110e0e2460a5ebd5a2a1edeb0d66c7898c6a4
    - ff_-40c_3.63v.log  sha256:01cf6211d542b7aaad9b6b9482f9c809e15c25ad1bdc8f458757dd55792697fe
wall_time: 55.7s
---

## Result

- `period_r1`: 4.015560e-09
- `period_r2`: 3.773054e-09
- `f_r1`: 2.490312e+08
- `f_r2`: 2.650373e+08
- `i_r1_a`: -3.649807e-05
- `i_r2_a`: -3.874487e-05
- `i_tree_a`: -3.305595e-05
- `e_cycle_r1_j`: -5.320136e-13
- `c_eff_node_r1_f`: -3.670429e-15
- `ring_swing_v`: 3.79165
- `xo_swing_v`: 3.76889
- `i_total_a`: -1.082989e-04
- `p_rings_w`: -2.731319e-04
- `p_total_w`: -3.931250e-04
- `xo_trans_per_s`: 1.028137e+09

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power --corners ff --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
