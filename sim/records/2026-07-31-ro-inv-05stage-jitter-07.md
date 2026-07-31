---
record: 2026-07-31-ro-inv-05stage-jitter-07
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-07/
  files:
    - tt_125c_2.97v-run0.spice  sha256:51a967dd66bdaf0e47a30323bfaef89d2a61e4452ce4b71f866e9f001325a315
    - tt_125c_2.97v-run0.log  sha256:c5be70cca9be1373a80e0079c59e806a3435c5f5e0b6b3868169122f20bb2ea3
    - tt_125c_2.97v-run1.spice  sha256:ab5882561283733e563033c83ef7293c1e23816a4f8d82651cf32a3962e72395
    - tt_125c_2.97v-run1.log  sha256:f4f65c8b6dbcc06222075dbb3e900fcf725f10f020356ab4ed11b8b7c5465194
    - tt_125c_2.97v-run2.spice  sha256:4a0946ccb0a70ff77c400714ce52ca5233725ced376b5dd54971d7a97ca58380
    - tt_125c_2.97v-run2.log  sha256:0a67c2ae9c5fc12d963ec6dfe3ab0417dc9e243e736f6fabad45375aa15c613a
    - tt_125c_2.97v-run3.spice  sha256:d7a21cef61f46ec96b3455ac9f47fdfd77be253b462d6b75c7d43f2c23467f56
    - tt_125c_2.97v-run3.log  sha256:b6a7c660bed568eb84a23f909aae5b87fe63839d19fa2a5a8e2603c7a9cb1685
wall_time: 3.6m
---

## Result

- `period`: mean 7.908277e-10 over 4 seeds (sd 7.962490e-15, 0.0% of mean; min 7.908189e-10, max 7.908351e-10)
- `f_osc`: mean 1.264498e+09 over 4 seeds (sd 12731.6, 0.0% of mean; min 1.264486e+09, max 1.264512e+09)
- `slew_v_per_s`: mean 2.450826e+10 over 4 seeds (sd 3.035160e+07, 0.1% of mean; min 2.446357e+10, max 2.453025e+10)
- `sigma_1`: mean 1.119687e-13 over 4 seeds (sd 4.897246e-15, 4.4% of mean; min 1.053294e-13, max 1.163840e-13)
- `sigma_2`: mean 1.526258e-13 over 4 seeds (sd 8.273531e-15, 5.4% of mean; min 1.434390e-13, max 1.622579e-13)
- `sigma_4`: mean 2.073463e-13 over 4 seeds (sd 3.935372e-14, 19.0% of mean; min 1.616615e-13, max 2.558992e-13)
- `sigma_8`: mean 3.064946e-13 over 4 seeds (sd 9.953434e-14, 32.5% of mean; min 2.202858e-13, max 4.500398e-13)
- `sigma_16`: mean 4.580834e-13 over 4 seeds (sd 2.118558e-13, 46.2% of mean; min 3.209878e-13, max 7.733319e-13)
- `sigma_32`: mean 6.906059e-13 over 4 seeds (sd 3.422435e-13, 49.6% of mean; min 4.751775e-13, max 1.199812e-12)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
