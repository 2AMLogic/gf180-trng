---
record: 2026-07-31-ro-inv-05stage-jitter-05
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
  tstop: 170n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-05/
  files:
    - tt_27c_3.30v-run0.spice  sha256:971765d91f6a2eb22c77aa2f9be97d0584a530aeb99a05d99384995c2abe9075
    - tt_27c_3.30v-run0.log  sha256:36e28eef08731c1c3b9abce377094efeab8740ea98bcd45da928cff1f4216c93
    - tt_27c_3.30v-run1.spice  sha256:2cd392692c22e248c1aad6c3627c0aff427a640caf56d80d3bb24188bc6711b9
    - tt_27c_3.30v-run1.log  sha256:ad86a0fe394f94c05b1ff5854e62f17d05f5966e1545e190912078ea6bcee88d
    - tt_27c_3.30v-run2.spice  sha256:9d56b01eb9ee4c7a258d6d9321759a09e9fc76333f5d4eb1d682bfe5918804dc
    - tt_27c_3.30v-run2.log  sha256:0e3bee0aaa59b5a20050fe0ec2624327e22ff4cd1b424152f9ec0ef3e5552ba8
    - tt_27c_3.30v-run3.spice  sha256:f2e056ee6e88144b5e51558875bf517d42a193099f9c93c325497539e1a513e9
    - tt_27c_3.30v-run3.log  sha256:f5af430003ab5e54a86a37038f48921de4cff9b26216a1e283cd07f140ba83a7
wall_time: 4.1m
---

## Result

- `period`: mean 6.213368e-10 over 4 seeds (sd 8.127262e-15, 0.0% of mean; min 6.213253e-10, max 6.213445e-10)
- `f_osc`: mean 1.609433e+09 over 4 seeds (sd 21052, 0.0% of mean; min 1.609413e+09, max 1.609463e+09)
- `slew_v_per_s`: mean 3.454779e+10 over 4 seeds (sd 4.755081e+07, 0.1% of mean; min 3.448096e+10, max 3.458757e+10)
- `sigma_1`: mean 8.967516e-14 over 4 seeds (sd 4.316717e-15, 4.8% of mean; min 8.324395e-14, max 9.237313e-14)
- `sigma_2`: mean 1.269471e-13 over 4 seeds (sd 7.458003e-15, 5.9% of mean; min 1.186873e-13, max 1.367243e-13)
- `sigma_4`: mean 1.743888e-13 over 4 seeds (sd 1.462201e-14, 8.4% of mean; min 1.592047e-13, max 1.927589e-13)
- `sigma_8`: mean 2.455078e-13 over 4 seeds (sd 2.674546e-14, 10.9% of mean; min 2.149810e-13, max 2.706422e-13)
- `sigma_16`: mean 3.313197e-13 over 4 seeds (sd 6.463509e-14, 19.5% of mean; min 2.434280e-13, max 3.873504e-13)
- `sigma_32`: mean 4.713382e-13 over 4 seeds (sd 1.430696e-13, 30.4% of mean; min 3.048579e-13, max 6.543575e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
