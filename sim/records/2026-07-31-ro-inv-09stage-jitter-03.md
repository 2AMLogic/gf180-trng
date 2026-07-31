---
record: 2026-07-31-ro-inv-09stage-jitter-03
date: 2026-07-31T19:41:51Z
status: valid

testbench:
  path: sim/tb/ro-inv-09stage-jitter/tb_ro_inv_09stage_jitter.sp
  sha: 1f809993aec2923642e9c288b788eb8d602a48ad
netlist:
  path: sim/tb/ro-inv-09stage-jitter/tb_ro_inv_09stage_jitter.sp
  sha: 1f809993aec2923642e9c288b788eb8d602a48ad
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
  tstop: 300n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-09stage-jitter-03/
  files:
    - ss_125c_2.97v-run0.spice  sha256:c1ac03c1729a1a3c278102a85274b421b3e7951fd4b55eb34c98fbdcfd030d9c
    - ss_125c_2.97v-run0.log  sha256:1f13bd1ee10427c23d7494b5630e871731ca1bab4b1508dd5f8cc4333d04592b
    - ss_125c_2.97v-run1.spice  sha256:033b352dfce5bea09e749a2de791de28e9f2d2c544dea8aa461c9f96258b362c
    - ss_125c_2.97v-run1.log  sha256:28634925697d749d591ebc7d2ea3a5658c86845b45997e5e3f578c4aff27942f
    - ss_125c_2.97v-run2.spice  sha256:3286a8bc42a99ac4638d18815d9ac737f1a1bbeefa324ad1da5f0b89c6076334
    - ss_125c_2.97v-run2.log  sha256:4b0f8475554001f30cc65f60baffbb3f2b93e341ea63a18cd4775cad3adb2a8d
    - ss_125c_2.97v-run3.spice  sha256:0a7c19563d2bf882ede822943b50de32677d56161cd78dfd051b0b882f41f5df
    - ss_125c_2.97v-run3.log  sha256:4aa9ea97719544088cd795364b8ee3fa491340327c0f321df1218d36dc0a8348
wall_time: 14.3m
---

## Result

- `period`: mean 1.751639e-09 over 4 seeds (sd 1.306646e-14, 0.0% of mean; min 1.751626e-09, max 1.751654e-09)
- `f_osc`: mean 5.708939e+08 over 4 seeds (sd 4258.61, 0.0% of mean; min 5.708890e+08, max 5.708980e+08)
- `slew_v_per_s`: mean 2.065632e+10 over 4 seeds (sd 5.809872e+07, 0.3% of mean; min 2.061283e+10, max 2.074167e+10)
- `sigma_1`: mean 1.652717e-13 over 4 seeds (sd 3.459192e-15, 2.1% of mean; min 1.612593e-13, max 1.682248e-13)
- `sigma_2`: mean 2.219266e-13 over 4 seeds (sd 6.908994e-15, 3.1% of mean; min 2.154523e-13, max 2.300792e-13)
- `sigma_4`: mean 3.136565e-13 over 4 seeds (sd 9.046176e-15, 2.9% of mean; min 3.063671e-13, max 3.264171e-13)
- `sigma_8`: mean 4.540534e-13 over 4 seeds (sd 2.461056e-14, 5.4% of mean; min 4.262845e-13, max 4.773824e-13)
- `sigma_16`: mean 6.388398e-13 over 4 seeds (sd 4.938284e-14, 7.7% of mean; min 6.012916e-13, max 7.090149e-13)
- `sigma_32`: mean 8.630731e-13 over 4 seeds (sd 2.411588e-13, 27.9% of mean; min 6.788131e-13, max 1.200619e-12)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
