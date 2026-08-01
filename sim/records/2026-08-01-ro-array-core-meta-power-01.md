---
record: 2026-08-01-ro-array-core-meta-power-01
date: 2026-08-01T16:21:44Z
status: valid

testbench:
  path: sim/tb/ro-array-core-meta-power/tb_ro_array_core_meta_power.sp
  sha: 8d41a052792221e426d32ab94c836cded23cd4d2
netlist:
  path: design/ro_array_core_meta.spice
  sha: e4062fcfd33a6dd1b026c20c01efa5fea70e5544
repo_commit: 762a90e86ec15db2231dd3dec8748ee7adec8fd2-dirty

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
  path: sim/records/raw/2026-08-01-ro-array-core-meta-power-01/
  files:
    - ff_-40c_3.63v.spice  sha256:aee87692c488a13b0005c723f1f939b7a14637eef2a5452aebf189e965862a22
    - ff_-40c_3.63v.log  sha256:20668535be590c5d287ee665d00e4a1af825b453dac46e30daf23f98e8606d82
wall_time: 12.3m
---

## Result

- `period_r1`: 4.285763e-09
- `period_r2`: 4.055149e-09
- `f_r1`: 2.333307e+08
- `f_r2`: 2.466000e+08
- `i_r1_a`: -3.600421e-05
- `i_r2_a`: -3.825028e-05
- `i_tree_a`: -4.142017e-05
- `i_tap_a`: -5.151733e-05
- `e_cycle_r1_j`: -5.601290e-13
- `c_eff_node_r1_f`: -3.864400e-15
- `ring_swing_v`: 3.65294
- `xo_swing_v`: 3.69797
- `mo_swing_v`: 0.925879
- `i_total_a`: -1.671920e-04
- `p_rings_w`: -2.695438e-04
- `p_tap_w`: -1.870079e-04
- `p_total_w`: -6.069069e-04
- `xo_trans_per_s`: 9.598614e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-meta-power --corners ff --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core_meta.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
