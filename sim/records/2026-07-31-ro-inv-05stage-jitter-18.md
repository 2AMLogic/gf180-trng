---
record: 2026-07-31-ro-inv-05stage-jitter-18
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-18/
  files:
    - ff_125c_3.63v-run0.spice  sha256:e09b45471842643466d5309574dbff4aa150ea571d5bcf46fd5fd98c06d48a4a
    - ff_125c_3.63v-run0.log  sha256:0823de5e7c97e872f7aa973cf8ef94c86bfe21796f0a9f37ee1684a2deb3002e
    - ff_125c_3.63v-run1.spice  sha256:4d320399397067870c7d99d48aaca15c6c0b7740f7024260b6342e3015bd46b8
    - ff_125c_3.63v-run1.log  sha256:4a05a97bab2e537a72f42fc2ff557a2d9e616066b6b074ab8f2babca5f976a4c
    - ff_125c_3.63v-run2.spice  sha256:d5b5b469bdb1b5d6f560a68d2c9052273879c939035b6ab3e313fd06b0f25a55
    - ff_125c_3.63v-run2.log  sha256:13422cc96acc2381c610b856b7dd946e5c3db2f268d18111dded100ed5f876a4
    - ff_125c_3.63v-run3.spice  sha256:a05d3fe57450fd16b54ba703c32f598359af87f096ce870a50b9d0717acd4a20
    - ff_125c_3.63v-run3.log  sha256:4dcf2027285cccc5b0054ec6bacbde9907d64d94507854e622ca452926b94e19
wall_time: 2.1m
---

## Result

- `period`: mean 5.731462e-10 over 4 seeds (sd 2.391516e-15, 0.0% of mean; min 5.731440e-10, max 5.731487e-10)
- `f_osc`: mean 1.744756e+09 over 4 seeds (sd 7280.18, 0.0% of mean; min 1.744748e+09, max 1.744762e+09)
- `slew_v_per_s`: mean 3.964182e+10 over 4 seeds (sd 3.186154e+07, 0.1% of mean; min 3.960288e+10, max 3.968080e+10)
- `sigma_1`: mean 7.634285e-14 over 4 seeds (sd 6.570968e-15, 8.6% of mean; min 6.803955e-14, max 8.307175e-14)
- `sigma_2`: mean 9.577819e-14 over 4 seeds (sd 8.760906e-15, 9.1% of mean; min 8.947524e-14, max 1.087282e-13)
- `sigma_4`: mean 1.314205e-13 over 4 seeds (sd 1.393898e-14, 10.6% of mean; min 1.222083e-13, max 1.521692e-13)
- `sigma_8`: mean 1.819159e-13 over 4 seeds (sd 2.523058e-14, 13.9% of mean; min 1.583187e-13, max 2.167942e-13)
- `sigma_16`: mean 2.434660e-13 over 4 seeds (sd 4.480296e-14, 18.4% of mean; min 2.139472e-13, max 3.097746e-13)
- `sigma_32`: mean 3.212410e-13 over 4 seeds (sd 5.138388e-14, 16.0% of mean; min 2.723840e-13, max 3.718497e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 125 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
