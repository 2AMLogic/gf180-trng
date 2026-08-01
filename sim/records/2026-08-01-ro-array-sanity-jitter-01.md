---
record: 2026-08-01-ro-array-sanity-jitter-01
date: 2026-08-01T11:06:23Z
status: valid

testbench:
  path: sim/tb/ro-array-sanity-jitter/tb_ro_array_sanity_jitter.sp
  sha: a121117b6b213a61ae4eabf7b97b7e496c6e8be1
netlist:
  path: design/ro_array_sanity.spice
  sha: b21e21d9b0388d4357ea0f82ba5e5d1f42b9597c
repo_commit: c953bc4d235908b512d8c15b5a2e8b4a5bb6b5ec-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /home/ubuntu/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-42 : Circuit level simulation program"
  platform: Linux-7.0.0-1009-aws-x86_64-with-glibc2.39

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran-noise
  tstop: 70n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources per ring, 20 in total
  runs: 3
seeds: [1, 2, 3]

raw:
  path: sim/records/raw/2026-08-01-ro-array-sanity-jitter-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:5287da8c701183d19303b42dfa40c586c85e7688d1ec70c46e09338010912177
    - tt_27c_3.30v-run0.log  sha256:c615ffaabcd4ff321e11d92b41db1ba0d842caa2aa41cbccb260e4f1f183a859
    - tt_27c_3.30v-run1.spice  sha256:2cf29983d611bd6b6ea8cf7062d0fd113a147fdf68721062738756faf58f437c
    - tt_27c_3.30v-run1.log  sha256:afd6ced5d1194425236927152de5fd9922999e87b394d804a1db1d6e2f15b360
    - tt_27c_3.30v-run2.spice  sha256:b0564d14f6c504ea51ab6d8ab9ff9248012b08f4a1e1ac0cc06f9237e171d7c8
    - tt_27c_3.30v-run2.log  sha256:d4e539eeace21444233adb8fecef0cfa88d9785dc6b52b3762bad4a594ce3350
wall_time: 127.3m
---

## Result

- `period_r1`: mean 3.305380e-09 over 3 seeds (sd 2.559400e-13, 0.0% of mean; min 3.305092e-09, max 3.305582e-09)
- `period_r2`: mean 3.105242e-09 over 3 seeds (sd 7.601011e-14, 0.0% of mean; min 3.105156e-09, max 3.105301e-09)
- `period_r3`: mean 2.875955e-09 over 3 seeds (sd 5.968986e-14, 0.0% of mean; min 2.875893e-09, max 2.876012e-09)
- `period_r4`: mean 2.678266e-09 over 3 seeds (sd 1.415228e-13, 0.0% of mean; min 2.678102e-09, max 2.678351e-09)
- `f_r1`: mean 3.025370e+08 over 3 seeds (sd 23426.7, 0.0% of mean; min 3.025186e+08, max 3.025634e+08)
- `f_r2`: mean 3.220361e+08 over 3 seeds (sd 7882.89, 0.0% of mean; min 3.220300e+08, max 3.220450e+08)
- `f_r3`: mean 3.477106e+08 over 3 seeds (sd 7216.68, 0.0% of mean; min 3.477037e+08, max 3.477181e+08)
- `f_r4`: mean 3.733760e+08 over 3 seeds (sd 19730.2, 0.0% of mean; min 3.733640e+08, max 3.733987e+08)
- `sigma_r1_1`: mean 2.321311e-11 over 3 seeds (sd 5.927746e-14, 0.3% of mean; min 2.314627e-11, max 2.325930e-11)
- `sigma_r1_2`: mean 4.466015e-11 over 3 seeds (sd 1.570253e-13, 0.4% of mean; min 4.448039e-11, max 4.477054e-11)
- `sigma_r1_4`: mean 7.987967e-11 over 3 seeds (sd 4.742584e-13, 0.6% of mean; min 7.933543e-11, max 8.020444e-11)
- `sigma_r1_8`: mean 1.242592e-10 over 3 seeds (sd 1.222196e-12, 1.0% of mean; min 1.228496e-10, max 1.250235e-10)
- `i_r1_a`: mean -1.821560e-05 over 3 seeds (sd 7.941577e-10, 0.0% of mean; min -1.821648e-05, max -1.821492e-05)
- `i_r4_a`: mean -2.204056e-05 over 3 seeds (sd 5.946459e-10, 0.0% of mean; min -2.204120e-05, max -2.204003e-05)
- `i_tree_a`: mean -1.057772e-04 over 3 seeds (sd 1.677690e-08, 0.0% of mean; min -1.057966e-04, max -1.057671e-04)
- `e_cycle_r1_j`: mean -1.986913e-13 over 3 seeds (sd 6.786872e-18, 0.0% of mean; min -1.986960e-13, max -1.986835e-13)
- `c_eff_node_r1_f`: mean -3.649060e-15 over 3 seeds (sd 1.246443e-19, 0.0% of mean; min -3.649147e-15, max -3.648917e-15)
- `ring1_swing_v`: mean 2.64301 over 3 seeds (sd 4.280556e-04, 0.0% of mean; min 2.64259, max 2.64344)
- `xo_swing_v`: mean 3.52143 over 3 seeds (sd 3.167745e-05, 0.0% of mean; min 3.5214, max 3.52145)
- `xo_trans_per_s`: mean 2.691319e+09 over 3 seeds (sd 53598.2, 0.0% of mean; min 2.691261e+09, max 2.691367e+09)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-sanity-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-sanity-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-sanity-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
