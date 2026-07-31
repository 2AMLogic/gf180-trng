---
record: 2026-07-31-ro-inv-05stage-jitter-21
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-21/
  files:
    - ss_-40c_3.63v-run0.spice  sha256:64926d187aa6a83a1c6af91b4d0a3e503c94481192b20d992c409179ffc473b3
    - ss_-40c_3.63v-run0.log  sha256:1cd0e275894c01c3cf00a8f37ecec10da68c4a7d4f995eb12cccfd908a6a23a7
    - ss_-40c_3.63v-run1.spice  sha256:02fe7fb108c084327962748475ef10f4b4e54995c282fa30489d13151ad2c950
    - ss_-40c_3.63v-run1.log  sha256:6568e00573e0a0e798b6841c1b8cf07b49eb3b216cd98337e0a22b93fef7a805
    - ss_-40c_3.63v-run2.spice  sha256:c5daa4783690b8588a6a2649a3cebc396898f8264a413a903a9f05626cc4f301
    - ss_-40c_3.63v-run2.log  sha256:808e44e4c2d5936253caf69eb83c94fa3ff3b8e29a778efc23442a2bbaab5455
    - ss_-40c_3.63v-run3.spice  sha256:20879686cfd68b065136c866e54bca46e1875ac622ec9e72d3bd4925459077d2
    - ss_-40c_3.63v-run3.log  sha256:08abc65b17e0ad0b0dc3fc7e2a56984aa67a5920f7327245d2dda0d9dd360827
wall_time: 1.5m
---

## Result

- `period`: mean 6.123139e-10 over 4 seeds (sd 7.607916e-15, 0.0% of mean; min 6.123051e-10, max 6.123223e-10)
- `f_osc`: mean 1.633149e+09 over 4 seeds (sd 20291.6, 0.0% of mean; min 1.633127e+09, max 1.633173e+09)
- `slew_v_per_s`: mean 4.016545e+10 over 4 seeds (sd 3.980574e+07, 0.1% of mean; min 4.012380e+10, max 4.020379e+10)
- `sigma_1`: mean 7.424807e-14 over 4 seeds (sd 1.434756e-15, 1.9% of mean; min 7.269791e-14, max 7.554834e-14)
- `sigma_2`: mean 1.021556e-13 over 4 seeds (sd 5.125260e-15, 5.0% of mean; min 9.711885e-14, max 1.085208e-13)
- `sigma_4`: mean 1.378794e-13 over 4 seeds (sd 1.338797e-14, 9.7% of mean; min 1.231193e-13, max 1.533499e-13)
- `sigma_8`: mean 1.845259e-13 over 4 seeds (sd 3.139117e-14, 17.0% of mean; min 1.459841e-13, max 2.218012e-13)
- `sigma_16`: mean 2.442948e-13 over 4 seeds (sd 5.286756e-14, 21.6% of mean; min 1.818099e-13, max 3.106933e-13)
- `sigma_32`: mean 3.582706e-13 over 4 seeds (sd 1.233373e-13, 34.4% of mean; min 2.576776e-13, max 5.316199e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
