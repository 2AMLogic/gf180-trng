---
record: 2026-07-31-ro-inv-05stage-jitter-03
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-03/
  files:
    - tt_-40c_3.63v-run0.spice  sha256:32033204169507c2ea5c1a5c9b042f4413edc25cb380800c2680af6702692efa
    - tt_-40c_3.63v-run0.log  sha256:223d2d209684a6f35e87e2cdf8b40e41808504180a876ce68493867f52588a7f
    - tt_-40c_3.63v-run1.spice  sha256:0aea0b41a6a56acfd77222e235e83d4198afb2a5ebe26a34ed285ce47906e1f1
    - tt_-40c_3.63v-run1.log  sha256:d812db49fb37b7f3e0cbf0f88285f1921b1fb1ac90e88f633bad31cbf04de05c
    - tt_-40c_3.63v-run2.spice  sha256:11de4003fa00a9346b98456e38fd2e62d2063f8e2ece90705afab2b1835cc7c3
    - tt_-40c_3.63v-run2.log  sha256:df477563e0c3c381bc3277b4d5a991f488ae62472e24af5379e57c8bfe5774b1
    - tt_-40c_3.63v-run3.spice  sha256:f0b0532fc9e40442c6650c88a5213e5743e6911c798ccc747e81e50abb0306c0
    - tt_-40c_3.63v-run3.log  sha256:99cbd76b853a0e4799f3d88f19c13038e0ac9b28fccd45503c78060f402e6a76
wall_time: 8.5m
---

## Result

- `period`: mean 5.100695e-10 over 4 seeds (sd 6.383733e-15, 0.0% of mean; min 5.100626e-10, max 5.100777e-10)
- `f_osc`: mean 1.960517e+09 over 4 seeds (sd 24536.6, 0.0% of mean; min 1.960486e+09, max 1.960544e+09)
- `slew_v_per_s`: mean 4.674751e+10 over 4 seeds (sd 4.367505e+07, 0.1% of mean; min 4.668210e+10, max 4.677232e+10)
- `sigma_1`: mean 7.079080e-14 over 4 seeds (sd 2.080761e-15, 2.9% of mean; min 6.828107e-14, max 7.331594e-14)
- `sigma_2`: mean 9.570435e-14 over 4 seeds (sd 5.420430e-15, 5.7% of mean; min 8.890458e-14, max 1.018480e-13)
- `sigma_4`: mean 1.367340e-13 over 4 seeds (sd 1.068017e-14, 7.8% of mean; min 1.266953e-13, max 1.508419e-13)
- `sigma_8`: mean 1.893728e-13 over 4 seeds (sd 1.162394e-14, 6.1% of mean; min 1.760814e-13, max 2.042884e-13)
- `sigma_16`: mean 2.949659e-13 over 4 seeds (sd 1.903182e-14, 6.5% of mean; min 2.803923e-13, max 3.225485e-13)
- `sigma_32`: mean 3.738319e-13 over 4 seeds (sd 4.227456e-14, 11.3% of mean; min 3.121117e-13, max 4.081129e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
