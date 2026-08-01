---
record: 2026-08-01-ro-array-core-meta-power-02
date: 2026-08-01T16:34:09Z
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
  path: sim/records/raw/2026-08-01-ro-array-core-meta-power-02/
  files:
    - ss_-40c_3.63v.spice  sha256:1153080f6adf035ea636707b704c908e73156b939427f5f4f8b10a5ea9ab28a3
    - ss_-40c_3.63v.log  sha256:b19b0f8337bac3052bdebe977fdeb71684cc6137503f4ac7fd7834f67a1f1cb2
wall_time: 10.2m
---

## Result

- `period_r1`: 6.152586e-09
- `period_r2`: 5.795285e-09
- `f_r1`: 1.625333e+08
- `f_r2`: 1.725541e+08
- `i_r1_a`: -2.204324e-05
- `i_r2_a`: -2.355294e-05
- `i_tree_a`: -2.062344e-05
- `i_tap_a`: -3.312109e-05
- `e_cycle_r1_j`: -4.923113e-13
- `c_eff_node_r1_f`: -3.396518e-15
- `ring_swing_v`: 3.7271
- `xo_swing_v`: 3.70957
- `mo_swing_v`: 1.06451
- `i_total_a`: -9.934071e-05
- `p_rings_w`: -1.655141e-04
- `p_tap_w`: -1.202296e-04
- `p_total_w`: -3.606068e-04
- `xo_trans_per_s`: 6.701747e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-meta-power --corners ss --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core_meta.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
