---
record: 2026-07-31-ro-inv-05stage-jitter-14
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
  temperature: 27

analysis:
  type: tran-noise
  tstop: 170n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-14/
  files:
    - ff_27c_3.30v-run0.spice  sha256:7a9b40f3164ed98ee53b304e44d5f8f475b015e1cfd6f5e73ebbea0f4e926087
    - ff_27c_3.30v-run0.log  sha256:6081740589eb161f0dda0a4722171265f0b4fc9424b100b82cc30d4138f66e95
    - ff_27c_3.30v-run1.spice  sha256:6934ad1121c005a53e8f379ab02d4a10be58b2264ebd6f422f769a113cb82dda
    - ff_27c_3.30v-run1.log  sha256:d1fa20141a3e4e08f26b0c1825aa0c56a997c581325cf92c7b4a97b00c22aeff
    - ff_27c_3.30v-run2.spice  sha256:5df8acb94d0cdf346b919cc8b05bded7429c94d9e07580bba14dec97bc288e39
    - ff_27c_3.30v-run2.log  sha256:e6216c44c573e121e52cde445aa421288599c2093d455d27b71321444f8206d4
    - ff_27c_3.30v-run3.spice  sha256:bfd25197ad3c707683a2d95a07e50f3133cd2d1720c12339d20cea459a8d3847
    - ff_27c_3.30v-run3.log  sha256:dfd0c637a6d1d6ab0646b48099f5ca18799475b688c7ae7000615da437a43857
wall_time: 1.8m
---

## Result

- `period`: mean 5.218050e-10 over 4 seeds (sd 4.421851e-15, 0.0% of mean; min 5.218011e-10, max 5.218092e-10)
- `f_osc`: mean 1.916425e+09 over 4 seeds (sd 16240.1, 0.0% of mean; min 1.916409e+09, max 1.916439e+09)
- `slew_v_per_s`: mean 3.974057e+10 over 4 seeds (sd 6.784468e+07, 0.2% of mean; min 3.965869e+10, max 3.981420e+10)
- `sigma_1`: mean 7.540040e-14 over 4 seeds (sd 3.138591e-15, 4.2% of mean; min 7.300564e-14, max 8.001605e-14)
- `sigma_2`: mean 1.015883e-13 over 4 seeds (sd 3.276954e-15, 3.2% of mean; min 9.819195e-14, max 1.059255e-13)
- `sigma_4`: mean 1.360636e-13 over 4 seeds (sd 9.561363e-15, 7.0% of mean; min 1.262346e-13, max 1.477092e-13)
- `sigma_8`: mean 1.838480e-13 over 4 seeds (sd 1.846511e-14, 10.0% of mean; min 1.653466e-13, max 2.052971e-13)
- `sigma_16`: mean 2.701740e-13 over 4 seeds (sd 3.940421e-14, 14.6% of mean; min 2.209985e-13, max 3.039871e-13)
- `sigma_32`: mean 4.034952e-13 over 4 seeds (sd 9.013296e-14, 22.3% of mean; min 3.131294e-13, max 4.965513e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
