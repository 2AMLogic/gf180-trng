---
record: 2026-07-31-ro-cinv-09stage-jitter-06
date: 2026-07-31T20:24:58Z
status: valid
supersedes: 2026-07-31-ro-cinv-09stage-jitter-03

testbench:
  path: sim/tb/ro-cinv-09stage-jitter/tb_ro_cinv_09stage_jitter.sp
  sha: 14f2ebcbd6b97b99223bc5dbdb17b2ee56493df2
netlist:
  path: sim/tb/ro-cinv-09stage-jitter/tb_ro_cinv_09stage_jitter.sp
  sha: 14f2ebcbd6b97b99223bc5dbdb17b2ee56493df2
repo_commit: 5988414021b3c1b1ea109dadc6097ae4e62000b3-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: tran-noise
  tstop: 580n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-cinv-09stage-jitter-06/
  files:
    - ss_125c_2.97v-run0.spice  sha256:491d7ef0a83347f421a69d54a9775774097c1a45f64cc1050e7ff6d29b96622f
    - ss_125c_2.97v-run0.log  sha256:1fb8bb15d6812785473ed747f39a6c32c7350a107dbf422adc9a9a4147e2f7f2
    - ss_125c_2.97v-run1.spice  sha256:6c3992b4af8c1397a43f04b190d12cfbf96f83ed85d6f5e77c59dd323f61c9f0
    - ss_125c_2.97v-run1.log  sha256:db5179f7e368c6324ea75d197aa7dc33bd6a14fea92c3a06c730d324c76045c0
    - ss_125c_2.97v-run2.spice  sha256:f25fa6ccabf15f4fff8cebd0cb8adcead943e07daa630451327539410b4b2b3b
    - ss_125c_2.97v-run2.log  sha256:c2eda09542bfc303dff1112457c52a5593ecae199cb0a53164dd5da4c5f03792
    - ss_125c_2.97v-run3.spice  sha256:87b25630185f2f72f00744e1e8a144b5355359575ac13abc2155ee6742b6a2bf
    - ss_125c_2.97v-run3.log  sha256:b076d2f50ad6964e6a15295a4cc01940b65c9e3d07d2ae8ee97ea4b2095d7898
wall_time: 14.9m
---

## Result

- `period`: mean 3.446906e-09 over 4 seeds (sd 9.655388e-15, 0.0% of mean; min 3.446898e-09, max 3.446919e-09)
- `f_osc`: mean 2.901152e+08 over 4 seeds (sd 812.661, 0.0% of mean; min 2.901142e+08, max 2.901159e+08)
- `slew_v_per_s`: mean 9.063535e+09 over 4 seeds (sd 1.612467e+07, 0.2% of mean; min 9.049360e+09, max 9.086737e+09)
- `sigma_1`: mean 2.321999e-13 over 4 seeds (sd 1.936424e-14, 8.3% of mean; min 2.175407e-13, max 2.604307e-13)
- `sigma_2`: mean 3.032819e-13 over 4 seeds (sd 1.614391e-14, 5.3% of mean; min 2.841825e-13, max 3.197002e-13)
- `sigma_4`: mean 4.118451e-13 over 4 seeds (sd 2.171829e-14, 5.3% of mean; min 3.922006e-13, max 4.427959e-13)
- `sigma_8`: mean 5.466222e-13 over 4 seeds (sd 3.164593e-14, 5.8% of mean; min 5.136411e-13, max 5.884559e-13)
- `sigma_16`: mean 6.960765e-13 over 4 seeds (sd 3.441280e-14, 4.9% of mean; min 6.605221e-13, max 7.430056e-13)
- `sigma_32`: mean 9.533337e-13 over 4 seeds (sd 1.075318e-13, 11.3% of mean; min 8.210418e-13, max 1.050979e-12)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
