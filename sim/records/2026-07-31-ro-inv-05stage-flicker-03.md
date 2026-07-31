---
record: 2026-07-31-ro-inv-05stage-flicker-03
date: 2026-07-31T19:31:45Z
status: valid

testbench:
  path: sim/tb/ro-inv-05stage-flicker/tb_ro_inv_05stage_flicker.sp
  sha: 12d732746920d22400f28b57b6f425b2622a0f96
netlist:
  path: sim/tb/ro-inv-05stage-flicker/tb_ro_inv_05stage_flicker.sp
  sha: 12d732746920d22400f28b57b6f425b2622a0f96
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
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=1 NAMP=5.4772e-5 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)) NALPHA=1 NAMP=5.4772e-5 (1/f corner intended at 3e+07 Hz)
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-flicker-03/
  files:
    - ss_125c_2.97v-run0.spice  sha256:91d38b0e7b58e304bcb9a3fdc24bb0bc9bd2fd411f1945ac527768eb7e97e72b
    - ss_125c_2.97v-run0.log  sha256:e8ea34994174696ddcc7938c9c46fb514c2c7dfb3519d4b12c8efc85c1937e9c
    - ss_125c_2.97v-run1.spice  sha256:793d6bceb416bd9d542bbd81227046e79e4f42aa708337e3dd1bb138ef06612f
    - ss_125c_2.97v-run1.log  sha256:d3a3fc2fdd84deebfa7af0c67a0d1e70e2ad91848b5c9fc1dd8b62de3248fa9e
    - ss_125c_2.97v-run2.spice  sha256:1a482f9e5aabd8625230996e24fd83d4c51fd1eb634f72a282379b3adadb8f43
    - ss_125c_2.97v-run2.log  sha256:0d829bb8461039950385ed14bcec3c367026beff2ac073d288d507cc31c47147
    - ss_125c_2.97v-run3.spice  sha256:7259ae91f6116f9885fffa9bbf7c901c5014da7f9494abd7d3a62a91fba3765f
    - ss_125c_2.97v-run3.log  sha256:dee38eb26c8e9cbdaa52850a415f99b820a5be0446766348f12b3fc1f281992e
wall_time: 10.1m
---

## Result

- `period`: mean 9.723898e-10 over 4 seeds (sd 1.062776e-14, 0.0% of mean; min 9.723771e-10, max 9.724031e-10)
- `f_osc`: mean 1.028394e+09 over 4 seeds (sd 11239.8, 0.0% of mean; min 1.028380e+09, max 1.028408e+09)
- `slew_v_per_s`: mean 2.067515e+10 over 4 seeds (sd 4.553939e+07, 0.2% of mean; min 2.063431e+10, max 2.073805e+10)
- `sigma_1`: mean 1.257201e-13 over 4 seeds (sd 3.591265e-15, 2.9% of mean; min 1.206682e-13, max 1.284577e-13)
- `sigma_2`: mean 1.649727e-13 over 4 seeds (sd 1.494289e-14, 9.1% of mean; min 1.511914e-13, max 1.859114e-13)
- `sigma_4`: mean 2.287269e-13 over 4 seeds (sd 3.407828e-14, 14.9% of mean; min 2.002568e-13, max 2.739212e-13)
- `sigma_8`: mean 3.272962e-13 over 4 seeds (sd 7.965951e-14, 24.3% of mean; min 2.670943e-13, max 4.381086e-13)
- `sigma_16`: mean 4.707395e-13 over 4 seeds (sd 1.849586e-13, 39.3% of mean; min 3.357847e-13, max 7.389098e-13)
- `sigma_32`: mean 6.457837e-13 over 4 seeds (sd 3.547468e-13, 54.9% of mean; min 3.493592e-13, max 1.157608e-12)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-flicker --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-flicker --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-flicker --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-flicker --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
