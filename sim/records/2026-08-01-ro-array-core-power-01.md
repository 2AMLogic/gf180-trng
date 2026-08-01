---
record: 2026-08-01-ro-array-core-power-01
date: 2026-08-01T11:06:06Z
status: valid

testbench:
  path: sim/tb/ro-array-core-power/tb_ro_array_core_power.sp
  sha: 35384af333100d98b21704d8e05745f3c656dbdd
netlist:
  path: design/ro_array_core.spice
  sha: faa556c8ef00db6f2bc7d15b29431ebe0bf24d78
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
  tstop: 60n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-array-core-power-01/
  files:
    - ff_-40c_3.63v.spice  sha256:2dd4306d057cce8fea973984bb42436fdf5c731d21dcefae7a712e6674503d30
    - ff_-40c_3.63v.log  sha256:b6c4fab66589f1fcbdca1de325a4cb0b9dd8e2ecb1d8faec847ece1c1627a8a6
wall_time: 36.0m
---

## Result

- `period_r1`: 4.285562e-09
- `period_r2`: 4.053318e-09
- `period_r3`: 3.802551e-09
- `period_r4`: 3.568925e-09
- `f_r1`: 2.333416e+08
- `f_r2`: 2.467115e+08
- `f_r3`: 2.629814e+08
- `f_r4`: 2.801964e+08
- `i_r1_a`: -3.600265e-05
- `i_r2_a`: -3.826268e-05
- `i_r3_a`: -4.033525e-05
- `i_r4_a`: -4.314389e-05
- `i_tree_a`: -1.223328e-04
- `i_total_a`: -2.800773e-04
- `p_rings_w`: -5.726125e-04
- `p_total_w`: -0.00101668
- `e_cycle_r1_j`: -5.600785e-13
- `e_cycle_r4_j`: -5.589377e-13
- `c_eff_node_r1_f`: -3.864052e-15
- `xo_trans_per_s`: 2.046462e+09
- `ring_swing_v`: 3.69378
- `xo_swing_v`: 3.86463

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power --corners ff --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
