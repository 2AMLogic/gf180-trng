---
record: 2026-07-31-ro-cinv-05stage-jitter-04
date: 2026-07-31T19:58:46Z
status: valid
supersedes: 2026-07-31-ro-cinv-05stage-jitter-01

testbench:
  path: sim/tb/ro-cinv-05stage-jitter/tb_ro_cinv_05stage_jitter.sp
  sha: 7105b542b3496eee5482fbb24dee2f644b6f71c7
netlist:
  path: sim/tb/ro-cinv-05stage-jitter/tb_ro_cinv_05stage_jitter.sp
  sha: 7105b542b3496eee5482fbb24dee2f644b6f71c7
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
  tstop: 330n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-cinv-05stage-jitter-04/
  files:
    - tt_27c_3.30v-run0.spice  sha256:b5b85e61473ce88d81eac11083a0187307e2ea6f7908ec5ca3571fc34f5eb23d
    - tt_27c_3.30v-run0.log  sha256:fefa7c280f99b93ab033779aba5d6685f32992a9e720e4fdd7fa0535e45cbf5b
    - tt_27c_3.30v-run1.spice  sha256:d09db8a70c097213368a8cb95ee37426345d7387664b5801678790973288e00a
    - tt_27c_3.30v-run1.log  sha256:bfc2129b91affeb2e58a4dfaed3efd82ac47bea0c3df3d5ce0ccc45725cc9165
    - tt_27c_3.30v-run2.spice  sha256:3b9973cdabb8cea576ace7f952135257f6eb3f50d9e706be9d54e987ef660e96
    - tt_27c_3.30v-run2.log  sha256:5a0d37f616f7d75e13d949e8c38ff1fadaad8ddbc6d3886c218026b409fc084e
    - tt_27c_3.30v-run3.spice  sha256:81b73391b11ced4948feb52496bb8d650466dc0e021b2ff06596f73769de9c59
    - tt_27c_3.30v-run3.log  sha256:7fc9d2352e339bdfc5a3ea34c9696928495aa1d0c1c5100bb8363fd4e365892d
wall_time: 5.1m
---

## Result

- `period`: mean 1.253887e-09 over 4 seeds (sd 1.693258e-14, 0.0% of mean; min 1.253866e-09, max 1.253904e-09)
- `f_osc`: mean 7.975200e+08 over 4 seeds (sd 10769.8, 0.0% of mean; min 7.975092e+08, max 7.975335e+08)
- `slew_v_per_s`: mean 1.474160e+10 over 4 seeds (sd 5.384933e+06, 0.0% of mean; min 1.473412e+10, max 1.474663e+10)
- `sigma_1`: mean 1.902850e-13 over 4 seeds (sd 9.054757e-15, 4.8% of mean; min 1.773064e-13, max 1.967384e-13)
- `sigma_2`: mean 2.729681e-13 over 4 seeds (sd 2.289370e-14, 8.4% of mean; min 2.508379e-13, max 3.009479e-13)
- `sigma_4`: mean 3.512110e-13 over 4 seeds (sd 4.470784e-14, 12.7% of mean; min 3.172962e-13, max 4.135986e-13)
- `sigma_8`: mean 4.424704e-13 over 4 seeds (sd 1.043848e-13, 23.6% of mean; min 3.782291e-13, max 5.983771e-13)
- `sigma_16`: mean 6.492805e-13 over 4 seeds (sd 1.669167e-13, 25.7% of mean; min 5.499942e-13, max 8.977468e-13)
- `sigma_32`: mean 9.438791e-13 over 4 seeds (sd 6.371872e-14, 6.8% of mean; min 8.551358e-13, max 1.006845e-12)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
