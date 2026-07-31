---
record: 2026-07-31-ro-inv-05stage-jitter-06
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
  voltage: 3.630 V (nominal 3.3 V, +10%)
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-06/
  files:
    - tt_27c_3.63v-run0.spice  sha256:bbd6033a32f3d03b2c00dd1c0d5f18f9280141814984f12927345d918901bf75
    - tt_27c_3.63v-run0.log  sha256:efc66c3f4c8c1859068fddb76f795bd55f9fe99d9c7de4955bb0093680612361
    - tt_27c_3.63v-run1.spice  sha256:52bfcf82d130fa242ad6bb02599409da786eee80f8399984db7160bd6725f3cf
    - tt_27c_3.63v-run1.log  sha256:aa539536b537e179780e05933645f8e4a3c0a0ab96049e4fe8617cd733b9ae28
    - tt_27c_3.63v-run2.spice  sha256:c1950ae055df292b273a00978602b7fefda56e1ad477b0f050db656c81f00f4e
    - tt_27c_3.63v-run2.log  sha256:366ec216be7f6bd51a435749f4ba2d66ff0a9ff0debadcb07323150111937e3c
    - tt_27c_3.63v-run3.spice  sha256:d6f6614f2f210085cb96d441a2f79fa8e2cf53324537439c17e7026cb52d91e1
    - tt_27c_3.63v-run3.log  sha256:eb2da5f2ae81b5f30947b31369c171b0474a79d10cd08775adecfc8c712ecbea
wall_time: 2.4m
---

## Result

- `period`: mean 5.797054e-10 over 4 seeds (sd 4.068275e-15, 0.0% of mean; min 5.797023e-10, max 5.797111e-10)
- `f_osc`: mean 1.725014e+09 over 4 seeds (sd 12105.8, 0.0% of mean; min 1.724997e+09, max 1.725023e+09)
- `slew_v_per_s`: mean 4.053439e+10 over 4 seeds (sd 6.366894e+07, 0.2% of mean; min 4.046372e+10, max 4.060176e+10)
- `sigma_1`: mean 7.700250e-14 over 4 seeds (sd 3.139602e-15, 4.1% of mean; min 7.433030e-14, max 8.140268e-14)
- `sigma_2`: mean 1.044194e-13 over 4 seeds (sd 6.153256e-15, 5.9% of mean; min 9.828981e-14, max 1.112533e-13)
- `sigma_4`: mean 1.426320e-13 over 4 seeds (sd 1.208178e-14, 8.5% of mean; min 1.250477e-13, max 1.526247e-13)
- `sigma_8`: mean 1.814079e-13 over 4 seeds (sd 2.643412e-14, 14.6% of mean; min 1.420861e-13, max 1.991828e-13)
- `sigma_16`: mean 2.413295e-13 over 4 seeds (sd 5.961480e-14, 24.7% of mean; min 1.530234e-13, max 2.831611e-13)
- `sigma_32`: mean 3.482795e-13 over 4 seeds (sd 8.787222e-14, 25.2% of mean; min 2.200158e-13, max 4.143232e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.63 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
