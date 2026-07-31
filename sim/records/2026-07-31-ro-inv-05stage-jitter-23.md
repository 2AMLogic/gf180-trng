---
record: 2026-07-31-ro-inv-05stage-jitter-23
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-23/
  files:
    - ss_27c_3.30v-run0.spice  sha256:ace6bbdc0000e9a80b6c7fde6ea1ef6c858ad261b9ee492dde1040acc1144a40
    - ss_27c_3.30v-run0.log  sha256:df6f5b941c6e92fb23e5330711314bc0f795b159a636d724cd0df5d10658ff8a
    - ss_27c_3.30v-run1.spice  sha256:f934a01007e168fc45147bea7f64b2362d9305492bf1d33b7a67de520f34723c
    - ss_27c_3.30v-run1.log  sha256:4ad5d6fbd10feb89dc74f17b042a3cb5a2fcaf9168b886a6cec27ad4374e41ca
    - ss_27c_3.30v-run2.spice  sha256:652c485151b5c22f7c9a4389eb403e966fd4b46d7ed6076d34540644b5db1a84
    - ss_27c_3.30v-run2.log  sha256:710739f31cdab54a249e2832d75942c135e1e12204bcb349b7dddf89705bb090
    - ss_27c_3.30v-run3.spice  sha256:7e181370e30b2825e5d6968914a08218daf53db5dcb8c4ecf95118055a63005c
    - ss_27c_3.30v-run3.log  sha256:d2fdd2ab11b010eae77efc7c7de12ea49f09709de8c64304040e00de1bb3bacb
wall_time: 1.9m
---

## Result

- `period`: mean 7.545892e-10 over 4 seeds (sd 7.487972e-15, 0.0% of mean; min 7.545806e-10, max 7.545988e-10)
- `f_osc`: mean 1.325224e+09 over 4 seeds (sd 13150.5, 0.0% of mean; min 1.325208e+09, max 1.325239e+09)
- `slew_v_per_s`: mean 2.948275e+10 over 4 seeds (sd 3.975346e+07, 0.1% of mean; min 2.942750e+10, max 2.951303e+10)
- `sigma_1`: mean 9.809396e-14 over 4 seeds (sd 2.877883e-15, 2.9% of mean; min 9.515415e-14, max 1.020473e-13)
- `sigma_2`: mean 1.330870e-13 over 4 seeds (sd 5.495285e-15, 4.1% of mean; min 1.253769e-13, max 1.372911e-13)
- `sigma_4`: mean 1.777066e-13 over 4 seeds (sd 1.536412e-14, 8.6% of mean; min 1.586830e-13, max 1.961546e-13)
- `sigma_8`: mean 2.258289e-13 over 4 seeds (sd 2.376712e-14, 10.5% of mean; min 2.035992e-13, max 2.470556e-13)
- `sigma_16`: mean 2.909523e-13 over 4 seeds (sd 4.009386e-14, 13.8% of mean; min 2.598056e-13, max 3.494243e-13)
- `sigma_32`: mean 4.143912e-13 over 4 seeds (sd 1.198772e-13, 28.9% of mean; min 2.977917e-13, max 5.740612e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
