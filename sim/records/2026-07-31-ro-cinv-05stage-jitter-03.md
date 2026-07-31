---
record: 2026-07-31-ro-cinv-05stage-jitter-03
date: 2026-07-31T19:41:51Z
status: valid

testbench:
  path: sim/tb/ro-cinv-05stage-jitter/tb_ro_cinv_05stage_jitter.sp
  sha: 7105b542b3496eee5482fbb24dee2f644b6f71c7
netlist:
  path: sim/tb/ro-cinv-05stage-jitter/tb_ro_cinv_05stage_jitter.sp
  sha: 7105b542b3496eee5482fbb24dee2f644b6f71c7
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
  tstop: 330n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-cinv-05stage-jitter-03/
  files:
    - ss_125c_2.97v-run0.spice  sha256:b456099b2261e65dae7b3d0438ed11f9d992bf08ff37e7aae3ca957d655dc76c
    - ss_125c_2.97v-run0.log  sha256:3d435cdf65c2b66447c7052a26a67164d9f79eab821113df52273e932382a4b2
    - ss_125c_2.97v-run1.spice  sha256:7b5b95199f12df568781c9e3fb86a803fb040f46864976ce26677ba5f3fe83d6
    - ss_125c_2.97v-run1.log  sha256:87f0707d802a9e340f78b30945863f12430697e81ccf39e6ef7129954fb01329
    - ss_125c_2.97v-run2.spice  sha256:6d9508f19611d610b8b9020d2daf9369f37ddd3075c1a30e20d9d027c8a237e7
    - ss_125c_2.97v-run2.log  sha256:fdc7c48c802cffe2d8c239c9c9fe8a2254378c974654329378a7d3e395c7e5e0
    - ss_125c_2.97v-run3.spice  sha256:ecaeb316ed568d7e864fde9589bea2d7787d0bad7dd3f5cb0459481bdc51eb92
    - ss_125c_2.97v-run3.log  sha256:9a1b3091601a9aec2d0b90df7c7e4b8aebdcba5ce55392b06cb91b45c552824c
wall_time: 17.6m
---

## Result

- `period`: mean 1.906281e-09 over 4 seeds (sd 1.408620e-14, 0.0% of mean; min 1.906262e-09, max 1.906295e-09)
- `f_osc`: mean 5.245816e+08 over 4 seeds (sd 3876.34, 0.0% of mean; min 5.245778e+08, max 5.245869e+08)
- `slew_v_per_s`: mean 9.072001e+09 over 4 seeds (sd 1.077925e+07, 0.1% of mean; min 9.057501e+09, max 9.082013e+09)
- `sigma_1`: mean 2.092613e-13 over 4 seeds (sd 2.534978e-14, 12.1% of mean; min 1.775016e-13, max 2.350664e-13)
- `sigma_2`: mean 2.800518e-13 over 4 seeds (sd 4.236202e-14, 15.1% of mean; min 2.232698e-13, max 3.153398e-13)
- `sigma_4`: mean 3.720456e-13 over 4 seeds (sd 7.274128e-14, 19.6% of mean; min 2.770222e-13, max 4.315583e-13)
- `sigma_8`: mean 5.056449e-13 over 4 seeds (sd 1.286557e-13, 25.4% of mean; min 3.530341e-13, max 6.342382e-13)
- `sigma_16`: mean 7.268150e-13 over 4 seeds (sd 2.235041e-13, 30.8% of mean; min 4.924418e-13, max 1.024459e-12)
- `sigma_32`: mean 1.160254e-12 over 4 seeds (sd 5.680418e-13, 49.0% of mean; min 6.791036e-13, max 1.953755e-12)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
