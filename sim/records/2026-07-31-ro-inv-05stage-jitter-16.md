---
record: 2026-07-31-ro-inv-05stage-jitter-16
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
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: tran-noise
  tstop: 170n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-16/
  files:
    - ff_125c_2.97v-run0.spice  sha256:58b6c0cf014f693be4eef21468504e5ffd20b87e833c3f71a787ad5dcf458b73
    - ff_125c_2.97v-run0.log  sha256:a7993356f09001fac59ef2bc7a947498e38fc6566795346731550c7552e1a531
    - ff_125c_2.97v-run1.spice  sha256:28d8856503f18387d4944333bef8c7b9a0a613bac588115eb052f7f3e99428b0
    - ff_125c_2.97v-run1.log  sha256:85f0ecd18e23b5f9529504b50dd48381217d71e0d36dc0610f844e6e298ca3d1
    - ff_125c_2.97v-run2.spice  sha256:f36d778919f1236f1ab3934771c39bc9218013908266be65eb2b7446cc3cc535
    - ff_125c_2.97v-run2.log  sha256:5279e0332048f103335713df7fc7e619db2d32b041a52a4948eefbc6ec8ef63c
    - ff_125c_2.97v-run3.spice  sha256:b434534fc252ef10a33798a7bebbeddd2a66ad9a82dbb2c710f0b235ee24c97e
    - ff_125c_2.97v-run3.log  sha256:883ff52e3325067ce858388a67a27af9b2d9aa22c07e7107a94f10553cf920b1
wall_time: 1.7m
---

## Result

- `period`: mean 6.547895e-10 over 4 seeds (sd 8.300107e-15, 0.0% of mean; min 6.547807e-10, max 6.548007e-10)
- `f_osc`: mean 1.527208e+09 over 4 seeds (sd 19358.8, 0.0% of mean; min 1.527182e+09, max 1.527229e+09)
- `slew_v_per_s`: mean 2.849332e+10 over 4 seeds (sd 2.256489e+07, 0.1% of mean; min 2.846600e+10, max 2.851382e+10)
- `sigma_1`: mean 9.929474e-14 over 4 seeds (sd 4.523827e-15, 4.6% of mean; min 9.358978e-14, max 1.037666e-13)
- `sigma_2`: mean 1.350832e-13 over 4 seeds (sd 1.248439e-14, 9.2% of mean; min 1.219416e-13, max 1.480018e-13)
- `sigma_4`: mean 1.982415e-13 over 4 seeds (sd 2.874140e-14, 14.5% of mean; min 1.726419e-13, max 2.276737e-13)
- `sigma_8`: mean 2.845764e-13 over 4 seeds (sd 5.663988e-14, 19.9% of mean; min 2.343565e-13, max 3.499767e-13)
- `sigma_16`: mean 3.793851e-13 over 4 seeds (sd 1.535988e-13, 40.5% of mean; min 2.356736e-13, max 5.491139e-13)
- `sigma_32`: mean 5.356459e-13 over 4 seeds (sd 2.458359e-13, 45.9% of mean; min 3.359086e-13, max 8.781471e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
