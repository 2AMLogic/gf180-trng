---
record: 2026-07-31-ro-inv-05stage-jitter-25
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-25/
  files:
    - ss_125c_2.97v-run0.spice  sha256:f5dd3bc7070d09ca92e6edfeddc65ef86da6e71ec54dbdaaa074e79835ae8889
    - ss_125c_2.97v-run0.log  sha256:3b62c6444a85e851f890293e5b8217744cc40a1bd9f21107298a030396b5c633
    - ss_125c_2.97v-run1.spice  sha256:ec6533bb57fa30eb947e91944e9f031a040f04414e018f8ca11a66ca1f77a731
    - ss_125c_2.97v-run1.log  sha256:083f546c4e6acb2acea9f17ba625b8c40e595585b90baa94b490144361b8e8a1
    - ss_125c_2.97v-run2.spice  sha256:6113a167822144c0db92169db0c5177b6558ea0d7475daf53d3f516bba6d743c
    - ss_125c_2.97v-run2.log  sha256:8f54630fb6ab6255393fbb40e2f7a0cf533f6b272d4d79e9747bf3a059275121
    - ss_125c_2.97v-run3.spice  sha256:219a19acf71022e4868c81d6a3ac9c39905717380efba46a360f4080557260e3
    - ss_125c_2.97v-run3.log  sha256:2a4646daeb7ebfb4e64d59c2e2fc7dfc6c89ea4ce97cf15df898e9c6d1988c47
wall_time: 1.6m
---

## Result

- `period`: mean 9.723890e-10 over 4 seeds (sd 1.430649e-14, 0.0% of mean; min 9.723772e-10, max 9.724067e-10)
- `f_osc`: mean 1.028395e+09 over 4 seeds (sd 15130.4, 0.0% of mean; min 1.028376e+09, max 1.028408e+09)
- `slew_v_per_s`: mean 2.066361e+10 over 4 seeds (sd 3.622876e+07, 0.2% of mean; min 2.062428e+10, max 2.069686e+10)
- `sigma_1`: mean 1.332980e-13 over 4 seeds (sd 1.108842e-14, 8.3% of mean; min 1.243068e-13, max 1.493544e-13)
- `sigma_2`: mean 1.787741e-13 over 4 seeds (sd 1.946875e-14, 10.9% of mean; min 1.617392e-13, max 2.027495e-13)
- `sigma_4`: mean 2.446157e-13 over 4 seeds (sd 2.780873e-14, 11.4% of mean; min 2.204848e-13, max 2.829785e-13)
- `sigma_8`: mean 3.282013e-13 over 4 seeds (sd 6.245879e-14, 19.0% of mean; min 2.570572e-13, max 4.059901e-13)
- `sigma_16`: mean 4.243274e-13 over 4 seeds (sd 1.106297e-13, 26.1% of mean; min 3.276498e-13, max 5.836498e-13)
- `sigma_32`: mean 6.082646e-13 over 4 seeds (sd 2.520429e-13, 41.4% of mean; min 3.339793e-13, max 9.310599e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
