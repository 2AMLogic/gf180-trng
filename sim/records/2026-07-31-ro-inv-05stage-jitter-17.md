---
record: 2026-07-31-ro-inv-05stage-jitter-17
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
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-17/
  files:
    - ff_125c_3.30v-run0.spice  sha256:a34aad9675bdc34f1a3a9f6d2fb80a271fccbfe8888efed4d9235f8eae343398
    - ff_125c_3.30v-run0.log  sha256:6f93d23e8ab27f272f39144da9cdc2b715ef138517133b17e556d5360aa33699
    - ff_125c_3.30v-run1.spice  sha256:bf0113a3d37ba8a01ef0703fe36333554db1c358893a622def989e8b391ecd00
    - ff_125c_3.30v-run1.log  sha256:39109202fb956c85c109ee531a2e09d2e0d66e1bd8a60b65455c281568ef43d1
    - ff_125c_3.30v-run2.spice  sha256:c7e3d291c4676c06e057c1c2c549cca43478eea2b040a96c95901c22ad3440d0
    - ff_125c_3.30v-run2.log  sha256:dde125966944d05e1effe8d1d27448c4b18534c3d9b342bb768ad0e8ae75e050
    - ff_125c_3.30v-run3.spice  sha256:d1860947a635e56e4c061646fb24ab28dcfe21e335d4cda272a3d782accba62d
    - ff_125c_3.30v-run3.log  sha256:e49bb2d13582dcd83ef785a546837db25f6290521123b376a1df38a820cbec15
wall_time: 2.7m
---

## Result

- `period`: mean 6.087035e-10 over 4 seeds (sd 4.394029e-15, 0.0% of mean; min 6.086995e-10, max 6.087089e-10)
- `f_osc`: mean 1.642836e+09 over 4 seeds (sd 11859, 0.0% of mean; min 1.642821e+09, max 1.642847e+09)
- `slew_v_per_s`: mean 3.397421e+10 over 4 seeds (sd 1.265066e+07, 0.0% of mean; min 3.395935e+10, max 3.398558e+10)
- `sigma_1`: mean 8.708974e-14 over 4 seeds (sd 6.577447e-15, 7.6% of mean; min 7.727729e-14, max 9.122078e-14)
- `sigma_2`: mean 1.132191e-13 over 4 seeds (sd 7.449779e-15, 6.6% of mean; min 1.034594e-13, max 1.207075e-13)
- `sigma_4`: mean 1.488655e-13 over 4 seeds (sd 5.107820e-15, 3.4% of mean; min 1.415685e-13, max 1.534411e-13)
- `sigma_8`: mean 2.143546e-13 over 4 seeds (sd 1.795601e-14, 8.4% of mean; min 1.976253e-13, max 2.389746e-13)
- `sigma_16`: mean 2.852199e-13 over 4 seeds (sd 4.011796e-14, 14.1% of mean; min 2.271926e-13, max 3.180303e-13)
- `sigma_32`: mean 3.752110e-13 over 4 seeds (sd 1.090786e-13, 29.1% of mean; min 3.168277e-13, max 5.387612e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.30 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
