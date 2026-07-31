---
record: 2026-07-31-ro-inv-05stage-jitter-27
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-27/
  files:
    - ss_125c_3.63v-run0.spice  sha256:d33da628bf7b0e3444b4b2b5ef2ab88fd2ffe54902b63c4d602557c1b977d26c
    - ss_125c_3.63v-run0.log  sha256:5d70a07ca1cffa1f9e1671b890cf98a804c3555848b1e219fc79de668fe6f0fb
    - ss_125c_3.63v-run1.spice  sha256:42cd4b7dbe417aaaf978de1f0ae6a719e4c18ea16d14e8060cd25f20ba96c517
    - ss_125c_3.63v-run1.log  sha256:d587dab04d7fa51978195ec21555a459dacba0384279fb46f1b1d4b6e09015b0
    - ss_125c_3.63v-run2.spice  sha256:e38c2983260d642af122e7aa8ed5ff219c2f5312e0cc6d55ed69daf5c2770160
    - ss_125c_3.63v-run2.log  sha256:19af928f2741ada2af64b48fe2f084165b08a38f7e13e2b6db56f42504e2ad60
    - ss_125c_3.63v-run3.spice  sha256:5eee857e52f5ab129004cfcc228c899510a5834f2da57556a0c2be394889a9b1
    - ss_125c_3.63v-run3.log  sha256:f812573fdcc259d1eff736fccbe8cbb6776fd6a4a1e5ee6a1638852ef38d6e8c
wall_time: 1.5m
---

## Result

- `period`: mean 8.149977e-10 over 4 seeds (sd 6.150640e-15, 0.0% of mean; min 8.149923e-10, max 8.150037e-10)
- `f_osc`: mean 1.226997e+09 over 4 seeds (sd 9259.92, 0.0% of mean; min 1.226988e+09, max 1.227005e+09)
- `slew_v_per_s`: mean 2.980945e+10 over 4 seeds (sd 5.402889e+07, 0.2% of mean; min 2.973582e+10, max 2.986057e+10)
- `sigma_1`: mean 9.071805e-14 over 4 seeds (sd 5.592178e-15, 6.2% of mean; min 8.522666e-14, max 9.580661e-14)
- `sigma_2`: mean 1.183520e-13 over 4 seeds (sd 7.492246e-15, 6.3% of mean; min 1.110301e-13, max 1.288307e-13)
- `sigma_4`: mean 1.659052e-13 over 4 seeds (sd 7.735258e-15, 4.7% of mean; min 1.566450e-13, max 1.745624e-13)
- `sigma_8`: mean 2.428433e-13 over 4 seeds (sd 1.794949e-14, 7.4% of mean; min 2.163261e-13, max 2.553049e-13)
- `sigma_16`: mean 3.600726e-13 over 4 seeds (sd 5.863643e-14, 16.3% of mean; min 2.776019e-13, max 4.137622e-13)
- `sigma_32`: mean 4.999922e-13 over 4 seeds (sd 1.351074e-13, 27.0% of mean; min 3.749443e-13, max 6.859635e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
