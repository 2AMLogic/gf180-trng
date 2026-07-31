---
record: 2026-07-31-ro-inv-05stage-jitter-12
date: 2026-07-31T19:37:01Z
status: valid

testbench:
  path: sim/tb/ro-inv-05stage-jitter/tb_ro_inv_05stage_jitter.sp
  sha: 3af228d176eeadc4a2f5ca5b471be9233df646f7
netlist:
  path: sim/tb/ro-inv-05stage-jitter/tb_ro_inv_05stage_jitter.sp
  sha: 3af228d176eeadc4a2f5ca5b471be9233df646f7
repo_commit: 5988414021b3c1b1ea109dadc6097ae4e62000b3-dirty

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
  type: tran-noise
  tstop: 170n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-12/
  files:
    - ff_-40c_3.63v-run0.spice  sha256:91237fffab94ed920b19f3de9f4c35254d2ad66b28714dfee8d891b105c562d4
    - ff_-40c_3.63v-run0.log  sha256:acfa2b48a985399a312fb056673241301bbb14400d7523f2977ec4c0b458fcc6
    - ff_-40c_3.63v-run1.spice  sha256:3e7e9ad8c62616ce42e9e42d07c253e4a5f698092cd588c9f7f0a764ef3fdabe
    - ff_-40c_3.63v-run1.log  sha256:62bd3c1452b77ab5315d9e73702bcece147baebe85329f58afedf5ac11efd9a9
    - ff_-40c_3.63v-run2.spice  sha256:e1a8cabd3479823beba09eecd9da72d2346cfdb42ade8f55ea7975392879a030
    - ff_-40c_3.63v-run2.log  sha256:c03a6138feb5998952e9a15ea90ebc79acce502e2e5dfdc1ecddb72587e50c79
    - ff_-40c_3.63v-run3.spice  sha256:8871055f7249495b5f79d9131940fb43cb859fd52cf40a9db3399c6242248d51
    - ff_-40c_3.63v-run3.log  sha256:8f06168e9c51eb1757e130d57c4431be74cf1bdd6134b25be127cdf0c25e3007
wall_time: 3.7m
---

## Result

- `period`: mean 4.342455e-10 over 4 seeds (sd 3.885147e-15, 0.0% of mean; min 4.342398e-10, max 4.342485e-10)
- `f_osc`: mean 2.302845e+09 over 4 seeds (sd 20603.4, 0.0% of mean; min 2.302829e+09, max 2.302875e+09)
- `slew_v_per_s`: mean 5.322987e+10 over 4 seeds (sd 1.060539e+08, 0.2% of mean; min 5.307794e+10, max 5.331179e+10)
- `sigma_1`: mean 5.924859e-14 over 4 seeds (sd 2.929516e-15, 4.9% of mean; min 5.527683e-14, max 6.151815e-14)
- `sigma_2`: mean 7.857101e-14 over 4 seeds (sd 5.291539e-15, 6.7% of mean; min 7.097405e-14, max 8.320161e-14)
- `sigma_4`: mean 1.098743e-13 over 4 seeds (sd 7.885761e-15, 7.2% of mean; min 9.960995e-14, max 1.171606e-13)
- `sigma_8`: mean 1.510048e-13 over 4 seeds (sd 8.792347e-15, 5.8% of mean; min 1.428634e-13, max 1.634002e-13)
- `sigma_16`: mean 2.112515e-13 over 4 seeds (sd 2.615589e-14, 12.4% of mean; min 1.802168e-13, max 2.367005e-13)
- `sigma_32`: mean 2.835979e-13 over 4 seeds (sd 7.670283e-14, 27.0% of mean; min 1.991013e-13, max 3.852929e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
