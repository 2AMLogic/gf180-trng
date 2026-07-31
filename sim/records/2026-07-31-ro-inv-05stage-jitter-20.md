---
record: 2026-07-31-ro-inv-05stage-jitter-20
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-20/
  files:
    - ss_-40c_3.30v-run0.spice  sha256:3eea66bad98bbdc6b859fa66688182ac13c410ea5b2d20ee1ec535fbb8134933
    - ss_-40c_3.30v-run0.log  sha256:631960dd69df805eb017fe48f305ac4ea0920b109771d496d652d4f3084476c6
    - ss_-40c_3.30v-run1.spice  sha256:09c8ddb36594b5667994e6ba8a55f60acf6abd837989e291be9104527b2cd529
    - ss_-40c_3.30v-run1.log  sha256:1f094630a995b6f633ed1989710829e64b0bc8ad2f04d1d7b117def1e24f1eb4
    - ss_-40c_3.30v-run2.spice  sha256:8cab7a1436982baa07496f70c1362539bed6bab9fcca8f61e1fb835c0dfa97b0
    - ss_-40c_3.30v-run2.log  sha256:084678d6dc29765dd4157e27c862926ba160848512ffe0e99b024a60885a9826
    - ss_-40c_3.30v-run3.spice  sha256:538db27e6e7585de1e9d71804893f9c21a633ea803b4d5e9fb373610384529e2
    - ss_-40c_3.30v-run3.log  sha256:f2edf1f4bac37213bf45254e4023856bae6217df6bb87b738412ac15b7ed85ea
wall_time: 1.8m
---

## Result

- `period`: mean 6.625308e-10 over 4 seeds (sd 7.289337e-15, 0.0% of mean; min 6.625241e-10, max 6.625375e-10)
- `f_osc`: mean 1.509364e+09 over 4 seeds (sd 16606.4, 0.0% of mean; min 1.509349e+09, max 1.509379e+09)
- `slew_v_per_s`: mean 3.402204e+10 over 4 seeds (sd 6.855424e+07, 0.2% of mean; min 3.393665e+10, max 3.409972e+10)
- `sigma_1`: mean 9.042458e-14 over 4 seeds (sd 8.188592e-15, 9.1% of mean; min 8.184861e-14, max 1.009245e-13)
- `sigma_2`: mean 1.230827e-13 over 4 seeds (sd 9.984910e-15, 8.1% of mean; min 1.125861e-13, max 1.366462e-13)
- `sigma_4`: mean 1.676482e-13 over 4 seeds (sd 1.748621e-14, 10.4% of mean; min 1.498787e-13, max 1.875051e-13)
- `sigma_8`: mean 2.409504e-13 over 4 seeds (sd 5.213035e-14, 21.6% of mean; min 1.902973e-13, max 2.921061e-13)
- `sigma_16`: mean 3.530756e-13 over 4 seeds (sd 1.046843e-13, 29.6% of mean; min 2.351777e-13, max 4.570869e-13)
- `sigma_32`: mean 5.049533e-13 over 4 seeds (sd 1.952851e-13, 38.7% of mean; min 3.004375e-13, max 7.536987e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 3.30 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
