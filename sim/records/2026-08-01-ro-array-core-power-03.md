---
record: 2026-08-01-ro-array-core-power-03
date: 2026-08-01T11:46:17Z
status: valid

testbench:
  path: sim/tb/ro-array-core-power/tb_ro_array_core_power.sp
  sha: 35384af333100d98b21704d8e05745f3c656dbdd
netlist:
  path: design/ro_array_core.spice
  sha: 72499835497bd4760147f49e60f5acd830f1f865
repo_commit: c953bc4d235908b512d8c15b5a2e8b4a5bb6b5ec-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /home/ubuntu/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-42 : Circuit level simulation program"
  platform: Linux-7.0.0-1009-aws-x86_64-with-glibc2.39

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran
  tstop: 80n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-array-core-power-03/
  files:
    - ss_-40c_3.63v.spice  sha256:4fccf408e424c58b14a36f136219c93c2d8513fe8e968498f446445acf0b8fc4
    - ss_-40c_3.63v.log  sha256:a36bdd8409bf8c8bbc2e89c2cd4af1972805e37ef197b824a7c11a3e79b528c7
wall_time: 39.7m
---

## Result

- `period_r1`: 1.138556e-08
- `period_r2`: 1.006406e-08
- `period_r3`: 8.523570e-09
- `period_r4`: 7.117315e-09
- `f_r1`: 8.783055e+07
- `f_r2`: 9.936348e+07
- `f_r3`: 1.173217e+08
- `f_r4`: 1.405024e+08
- `i_r1_a`: -1.320930e-05
- `i_r2_a`: -1.483156e-05
- `i_r3_a`: -1.673546e-05
- `i_r4_a`: -1.928240e-05
- `i_tree_a`: -6.706930e-05
- `i_total_a`: -1.311280e-04
- `p_rings_w`: -2.325332e-04
- `p_total_w`: -4.759947e-04
- `e_cycle_r1_j`: -5.459349e-13
- `e_cycle_r4_j`: -4.981772e-13
- `c_eff_node_r1_f`: -3.766474e-15
- `xo_trans_per_s`: 8.900364e+08
- `ring_swing_v`: 3.35028
- `xo_swing_v`: 3.88758

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power --corners ss --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
