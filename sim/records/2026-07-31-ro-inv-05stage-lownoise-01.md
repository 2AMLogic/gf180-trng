---
record: 2026-07-31-ro-inv-05stage-lownoise-01
date: 2026-07-31T19:21:43Z
status: valid

testbench:
  path: sim/tb/ro-inv-05stage-lownoise/tb_ro_inv_05stage_lownoise.sp
  sha: b4dbafe38b426aeb4a6dfbdce0e562ffa4502f75
netlist:
  path: sim/tb/ro-inv-05stage-lownoise/tb_ro_inv_05stage_lownoise.sp
  sha: b4dbafe38b426aeb4a6dfbdce0e562ffa4502f75
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
  noise_params: per-stage trnoise( NA=2.2361e-4 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-18 V^2/Hz (1e-09 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-lownoise-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:739bec234f8fce83e9e6e6e332e9caa8c322a35aa67de9febc0daad6c00272e0
    - tt_27c_3.30v-run0.log  sha256:940dbc5ba1858686274c470e98ef65588b77dd5f91c1cb66785119c8a6d36f1a
    - tt_27c_3.30v-run1.spice  sha256:cf19abc87b6ef709c1164f2ae1db6cf44f0074884cf1b1db620c333cd182bf06
    - tt_27c_3.30v-run1.log  sha256:41c4439ab4dee41c457537ae40732525bbc01ce6670e0474dd1e731ad47f96c6
    - tt_27c_3.30v-run2.spice  sha256:653d129ea20d506a57b65aaf3401426071164cc5b2ce555bc2d236bf46e79a84
    - tt_27c_3.30v-run2.log  sha256:166d8e33c287e9302a6ba6c240469af758cf479fb4d4215d6a7650b83e24f212
    - tt_27c_3.30v-run3.spice  sha256:5db91a9e50c59d114aa41498a11d977affb360433e614a553872bfaf2b5b96f8
    - tt_27c_3.30v-run3.log  sha256:40e377b2640045ca4a179d514ee9701e3d267c9a0c8fcf8e2c11c68235fe245e
wall_time: 9.7m
---

## Result

- `period`: mean 6.213392e-10 over 4 seeds (sd 3.455404e-16, 0.0% of mean; min 6.213387e-10, max 6.213394e-10)
- `f_osc`: mean 1.609427e+09 over 4 seeds (sd 895.036, 0.0% of mean; min 1.609426e+09, max 1.609428e+09)
- `slew_v_per_s`: mean 3.455678e+10 over 4 seeds (sd 3.303407e+06, 0.0% of mean; min 3.455316e+10, max 3.456040e+10)
- `sigma_1`: mean 9.605835e-15 over 4 seeds (sd 4.287663e-16, 4.5% of mean; min 9.257744e-15, max 1.022808e-14)
- `sigma_2`: mean 1.303652e-14 over 4 seeds (sd 1.198598e-15, 9.2% of mean; min 1.217906e-14, max 1.480338e-14)
- `sigma_4`: mean 1.810249e-14 over 4 seeds (sd 2.256883e-15, 12.5% of mean; min 1.501136e-14, max 2.040667e-14)
- `sigma_8`: mean 2.356772e-14 over 4 seeds (sd 3.616913e-15, 15.3% of mean; min 1.885097e-14, max 2.677516e-14)
- `sigma_16`: mean 2.839411e-14 over 4 seeds (sd 6.349819e-15, 22.4% of mean; min 2.159396e-14, max 3.692258e-14)
- `sigma_32`: mean 3.555791e-14 over 4 seeds (sd 1.200698e-14, 33.8% of mean; min 2.320147e-14, max 5.124568e-14)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
