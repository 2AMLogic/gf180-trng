---
record: 2026-07-31-trnoise-calibration-01
date: 2026-07-31T19:21:43Z
status: valid

testbench:
  path: sim/tb/trnoise-calibration/tb_trnoise_cal.sp
  sha: 0133a71dfae7eca4015c55df521e06771c76ea1f
netlist:
  path: sim/tb/trnoise-calibration/tb_trnoise_cal.sp
  sha: 0133a71dfae7eca4015c55df521e06771c76ea1f
repo_commit: 5988414021b3c1b1ea109dadc6097ae4e62000b3-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran-noise
  tstop: 4u
  tstep: 10p
  tmax: n/a
  noise_params: trnoise(NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0) white branch; trnoise(NA=0 NT=1e-11 NALPHA=1 NAMP=5.4772e-5) 1/f branch; intended S_w = 2*NA^2*NT = 1.0e-16 V^2/Hz (1.0e-8 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-trnoise-calibration-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:dbb05d0a64228a23d17f2a6a2dc6ca8f280a92382e0882ead5c9792c6462498c
    - tt_27c_3.30v-run0.log  sha256:154606bac1fbb2393bffa63e128fc5560d10c213d4a2d41c1da5ac877d85f03e
    - tt_27c_3.30v-run1.spice  sha256:4939359de537a10d4b16d5d62a28f1d1c3c48e39eb69dc5c9c03a35ca65085b6
    - tt_27c_3.30v-run1.log  sha256:660cdd1d942e0169c444cc581632f616b6e6dd76263de9638c5c62446baf75a3
    - tt_27c_3.30v-run2.spice  sha256:e66d34b0d4a543f1e5b32dd344afda75a18f0dd43764f27381ebd64c0d01d475
    - tt_27c_3.30v-run2.log  sha256:fe0547645c7a08cad4f80cf7b335a10084c5014a05edeb7f87e87730aed5b431
    - tt_27c_3.30v-run3.spice  sha256:6f3ba033d391de6960f42efbeb67ecddd73feb68bea597832599971cd4acc5f1
    - tt_27c_3.30v-run3.log  sha256:5035075fe4ee5fe76ca74e752508271f5c509c459dce41d6270cc585591125f9
wall_time: 10.7m
---

## Result

- `rms_white_src`: mean 0.00224937 over 4 seeds (sd 1.408819e-05, 0.6% of mean; min 0.00223278, max 0.00226331)
- `rms_rc_159meg`: mean 1.587734e-04 over 4 seeds (sd 1.967364e-06, 1.2% of mean; min 1.570736e-04, max 1.607786e-04)
- `rms_rc_15meg`: mean 4.948393e-05 over 4 seeds (sd 1.697722e-06, 3.4% of mean; min 4.739912e-05, max 5.088671e-05)
- `rms_flicker_rc_159meg`: mean 1.079188e-04 over 4 seeds (sd 1.132541e-05, 10.5% of mean; min 9.167712e-05, max 1.166417e-04)
- `n_samples`: mean 4.000010e+05 over 4 seeds (sd 0, 0.0% of mean; min 4.000010e+05, max 4.000010e+05)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py trnoise-calibration --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py trnoise-calibration --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py trnoise-calibration --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py trnoise-calibration --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
