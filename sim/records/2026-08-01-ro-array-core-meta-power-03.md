---
record: 2026-08-01-ro-array-core-meta-power-03
date: 2026-08-01T16:44:27Z
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran
  tstop: 50n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-array-core-meta-power-03/
  files:
    - tt_27c_3.30v.spice  sha256:e7f85f7a6875dac355e00198ee475f8db8b01bf9a243362b83d9de1992e29bdd
    - tt_27c_3.30v.log  sha256:d32ab11d33f2339201d7c4431197473f9f3fadf2b5b7843ffe7900025da773c2
wall_time: 9.0m
---

## Result

- `period_r1`: 7.135710e-09
- `period_r2`: 6.716732e-09
- `f_r1`: 1.401402e+08
- `f_r2`: 1.488819e+08
- `i_r1_a`: -1.868191e-05
- `i_r2_a`: -1.995641e-05
- `i_tree_a`: -2.026681e-05
- `i_tap_a`: -2.645458e-05
- `e_cycle_r1_j`: -4.399188e-13
- `c_eff_node_r1_f`: -3.672417e-15
- `ring_swing_v`: 3.38388
- `xo_swing_v`: 3.34489
- `mo_swing_v`: 0.781617
- `i_total_a`: -8.535972e-05
- `p_rings_w`: -1.275065e-04
- `p_tap_w`: -8.730012e-05
- `p_total_w`: -2.816871e-04
- `xo_trans_per_s`: 5.780443e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-meta-power --corners tt --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core_meta.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
