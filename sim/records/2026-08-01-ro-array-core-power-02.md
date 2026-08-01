---
record: 2026-08-01-ro-array-core-power-02
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
  - /home/ubuntu/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-42 : Circuit level simulation program"
  platform: Linux-7.0.0-1009-aws-x86_64-with-glibc2.39

corner:
  process: ff
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
  path: sim/records/raw/2026-08-01-ro-array-core-power-02/
  files:
    - ff_-40c_3.63v.spice  sha256:62e6fa227718dbcc5aabf53b52dc1246f6cd75522d7368806283d9c6508b59e8
    - ff_-40c_3.63v.log  sha256:6dd61f1690a59baa886a49f6b1aec75a0acef220557caf47a42d33f51afc8588
wall_time: 40.8m
---

## Result

- `period_r1`: 7.504380e-09
- `period_r2`: 6.541445e-09
- `period_r3`: 5.386543e-09
- `period_r4`: 4.103333e-09
- `f_r1`: 1.332555e+08
- `f_r2`: 1.528714e+08
- `f_r3`: 1.856478e+08
- `f_r4`: 2.437043e+08
- `i_r1_a`: -2.305315e-05
- `i_r2_a`: -2.600472e-05
- `i_r3_a`: -2.971051e-05
- `i_r4_a`: -3.518432e-05
- `i_tree_a`: -1.446024e-04
- `i_total_a`: -2.585551e-04
- `p_rings_w`: -4.136483e-04
- `p_total_w`: -9.385548e-04
- `e_cycle_r1_j`: -6.279885e-13
- `e_cycle_r4_j`: -5.240740e-13
- `c_eff_node_r1_f`: -4.332572e-15
- `xo_trans_per_s`: 1.430958e+09
- `ring_swing_v`: 3.19288
- `xo_swing_v`: 3.87307

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power --corners ff --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
