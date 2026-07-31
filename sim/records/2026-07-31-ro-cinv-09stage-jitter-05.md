---
record: 2026-07-31-ro-cinv-09stage-jitter-05
date: 2026-07-31T20:14:23Z
status: valid
supersedes: 2026-07-31-ro-cinv-09stage-jitter-02

testbench:
  path: sim/tb/ro-cinv-09stage-jitter/tb_ro_cinv_09stage_jitter.sp
  sha: 14f2ebcbd6b97b99223bc5dbdb17b2ee56493df2
netlist:
  path: sim/tb/ro-cinv-09stage-jitter/tb_ro_cinv_09stage_jitter.sp
  sha: 14f2ebcbd6b97b99223bc5dbdb17b2ee56493df2
repo_commit: 5988414021b3c1b1ea109dadc6097ae4e62000b3-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran-noise
  tstop: 580n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-cinv-09stage-jitter-05/
  files:
    - ff_-40c_3.63v-run0.spice  sha256:a13a51d8136a04786b8adfdcdcc1b22168acce85cfba578ea96e8ee11ce416b8
    - ff_-40c_3.63v-run0.log  sha256:6f2a6ad39ea3a01bfd41fdcd5fd3626ec34294d7d492d8d83594a067f60d2005
    - ff_-40c_3.63v-run1.spice  sha256:798a5dd7150edf151270d47e92399943cc09b2ab88daadf23df65544f3932a6e
    - ff_-40c_3.63v-run1.log  sha256:ee01c350bfa325266c725c50f94de9744d5acf94805779b17bf0e7cae24e15bd
    - ff_-40c_3.63v-run2.spice  sha256:beeb47766384eb1f900ddc522cbbe1b3eda1c6f6dedeae9de5daa622f7842b15
    - ff_-40c_3.63v-run2.log  sha256:4c96a7b284aa52482effa3bd79905e41fcdad33e57c236cecf100caa5a5ec922
    - ff_-40c_3.63v-run3.spice  sha256:2d463b031e1c459f3fc72b9611fd9199cdffc5381441484709608ba5edb4d4c3
    - ff_-40c_3.63v-run3.log  sha256:97b9d6a18cb4600ed6f15b33fabbb98e43a7ccb4301ec56ba7b07fcc278e6779
wall_time: 21.0m
---

## Result

- `period`: mean 1.691900e-09 over 4 seeds (sd 1.268451e-14, 0.0% of mean; min 1.691890e-09, max 1.691918e-09)
- `f_osc`: mean 5.910514e+08 over 4 seeds (sd 4431.21, 0.0% of mean; min 5.910453e+08, max 5.910549e+08)
- `slew_v_per_s`: mean 2.129658e+10 over 4 seeds (sd 1.765023e+07, 0.1% of mean; min 2.128096e+10, max 2.131720e+10)
- `sigma_1`: mean 1.906455e-13 over 4 seeds (sd 9.268861e-15, 4.9% of mean; min 1.769968e-13, max 1.966750e-13)
- `sigma_2`: mean 2.414100e-13 over 4 seeds (sd 9.104790e-15, 3.8% of mean; min 2.325399e-13, max 2.524400e-13)
- `sigma_4`: mean 3.095111e-13 over 4 seeds (sd 2.785600e-14, 9.0% of mean; min 2.689303e-13, max 3.315371e-13)
- `sigma_8`: mean 4.077699e-13 over 4 seeds (sd 4.477268e-14, 11.0% of mean; min 3.407925e-13, max 4.334103e-13)
- `sigma_16`: mean 5.621825e-13 over 4 seeds (sd 8.125291e-14, 14.5% of mean; min 4.455464e-13, max 6.212724e-13)
- `sigma_32`: mean 7.802877e-13 over 4 seeds (sd 1.455630e-13, 18.7% of mean; min 5.754421e-13, max 8.993040e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
