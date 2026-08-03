---
record: 2026-08-02-ro-array-core-power-02
date: 2026-08-02T23:56:08Z
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
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
  path: sim/records/raw/2026-08-02-ro-array-core-power-02/
  files:
    - ss_-40c_3.63v.spice  sha256:8c8e0ee83693dc06796d26b77504a31eb2b6c0c770e952ee473ec10bb9266176
    - ss_-40c_3.63v.log  sha256:1715ebed99fe779e02c88fb0efe5ee0f691974046c04ab6ef86abd4d1ab9dffa
wall_time: 42.9s
---

## Result

- `period_r1`: 5.743527e-09
- `period_r2`: 5.373587e-09
- `f_r1`: 1.741090e+08
- `f_r2`: 1.860954e+08
- `i_r1_a`: -2.238063e-05
- `i_r2_a`: -2.385670e-05
- `i_tree_a`: -1.834716e-05
- `e_cycle_r1_j`: -4.666139e-13
- `c_eff_node_r1_f`: -3.219228e-15
- `ring_swing_v`: 3.80029
- `xo_swing_v`: 3.81016
- `i_total_a`: -6.458450e-05
- `p_rings_w`: -1.678415e-04
- `p_total_w`: -2.344417e-04
- `xo_trans_per_s`: 7.204089e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power --corners ss --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
