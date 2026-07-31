---
record: 2026-07-31-ro-inv-03stage-jitter-03
date: 2026-07-31T19:25:56Z
status: valid

testbench:
  path: sim/tb/ro-inv-03stage-jitter/tb_ro_inv_03stage_jitter.sp
  sha: 8b4771cbd7ba0fabbb3c58f9067b5bf73d17caf8
netlist:
  path: sim/tb/ro-inv-03stage-jitter/tb_ro_inv_03stage_jitter.sp
  sha: 8b4771cbd7ba0fabbb3c58f9067b5bf73d17caf8
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
  tstop: 110n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-03stage-jitter-03/
  files:
    - ss_125c_2.97v-run0.spice  sha256:df6a599d0a675a90047c680d45f78b6812511b30607851c7e8c41996dfcf22eb
    - ss_125c_2.97v-run0.log  sha256:1f908984bb8abbf2224833231cbe1cc4259ab8951df6519da679e1f9258510a4
    - ss_125c_2.97v-run1.spice  sha256:6e0ed06a0c06f2bdbe6006aa72dbffb461891f4392d8cf2b1a6ba49c1203a28e
    - ss_125c_2.97v-run1.log  sha256:39f334f950250a77eedd733cf87143ee8f71ea0811cb2915b3a7b258d5be1fd3
    - ss_125c_2.97v-run2.spice  sha256:f04676b536b6241cb9a2f9a9c3b125694deae88dbfd3c01243ca6b65bf274ccf
    - ss_125c_2.97v-run2.log  sha256:83e12c3042b43278f4f4f544315f1b0d8eb60239d4db365c5a9b974cf9e4b7db
    - ss_125c_2.97v-run3.spice  sha256:29d8c2fca726355027c4296152bd8cdb0034a0570169a07b4adb6c6acc5d57b2
    - ss_125c_2.97v-run3.log  sha256:2e97977638c670f14861942149de1c36d84c655a89626ce620d2a6a495e820bc
wall_time: 4.5m
---

## Result

- `period`: mean 5.666424e-10 over 4 seeds (sd 1.216738e-14, 0.0% of mean; min 5.666299e-10, max 5.666572e-10)
- `f_osc`: mean 1.764781e+09 over 4 seeds (sd 37894.6, 0.0% of mean; min 1.764735e+09, max 1.764820e+09)
- `slew_v_per_s`: mean 2.069279e+10 over 4 seeds (sd 4.372362e+07, 0.2% of mean; min 2.062930e+10, max 2.072937e+10)
- `sigma_1`: mean 1.076680e-13 over 4 seeds (sd 9.420194e-15, 8.7% of mean; min 1.001989e-13, max 1.209201e-13)
- `sigma_2`: mean 1.427666e-13 over 4 seeds (sd 1.401199e-14, 9.8% of mean; min 1.296022e-13, max 1.625957e-13)
- `sigma_4`: mean 1.944935e-13 over 4 seeds (sd 2.308867e-14, 11.9% of mean; min 1.728463e-13, max 2.271916e-13)
- `sigma_8`: mean 2.644306e-13 over 4 seeds (sd 3.759498e-14, 14.2% of mean; min 2.349433e-13, max 3.194576e-13)
- `sigma_16`: mean 3.579271e-13 over 4 seeds (sd 7.767686e-14, 21.7% of mean; min 2.849652e-13, max 4.653930e-13)
- `sigma_32`: mean 5.113482e-13 over 4 seeds (sd 1.601567e-13, 31.3% of mean; min 3.662936e-13, max 7.327783e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-03stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-03stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-03stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-03stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
