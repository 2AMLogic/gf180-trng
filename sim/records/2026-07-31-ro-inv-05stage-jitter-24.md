---
record: 2026-07-31-ro-inv-05stage-jitter-24
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-24/
  files:
    - ss_27c_3.63v-run0.spice  sha256:10d9e925f56525437f71621aaa95108dbd98760d195bd589df21d667cc3e2d1d
    - ss_27c_3.63v-run0.log  sha256:ed5b17cb6f4394bbba1c8ff00e821e90928c6a15a707b8ad23dfc4928457282d
    - ss_27c_3.63v-run1.spice  sha256:3c02995ba633184d558aee3e32e011361501517aeb251d9ac869b8173ddc7d1f
    - ss_27c_3.63v-run1.log  sha256:e18343439eca15f9644cccaf79d6e74a8d427a1db41a6285385fbec9ce5b88b3
    - ss_27c_3.63v-run2.spice  sha256:e0d35f424e833bd2879e5149ee96d87650b29e51b6f334a28753325160b98478
    - ss_27c_3.63v-run2.log  sha256:cd62af5b31cdb763e71a8a6ffecf4e92a1e18fad87f1ddb4a60ea5caf59a549f
    - ss_27c_3.63v-run3.spice  sha256:858d5f57445c7741214a7f6fb93d352d31860ed05ae8493f5011f84c60293d56
    - ss_27c_3.63v-run3.log  sha256:8184aac44729c43533d5810e35238e19d1131e3875458f52b04be8e27e4e802a
wall_time: 1.8m
---

## Result

- `period`: mean 6.968092e-10 over 4 seeds (sd 1.777798e-15, 0.0% of mean; min 6.968071e-10, max 6.968113e-10)
- `f_osc`: mean 1.435113e+09 over 4 seeds (sd 3661.46, 0.0% of mean; min 1.435109e+09, max 1.435117e+09)
- `slew_v_per_s`: mean 3.492193e+10 over 4 seeds (sd 4.271819e+07, 0.1% of mean; min 3.486362e+10, max 3.495931e+10)
- `sigma_1`: mean 8.041854e-14 over 4 seeds (sd 1.764037e-15, 2.2% of mean; min 7.802136e-14, max 8.183143e-14)
- `sigma_2`: mean 1.073844e-13 over 4 seeds (sd 8.473462e-15, 7.9% of mean; min 9.596285e-14, max 1.155588e-13)
- `sigma_4`: mean 1.468929e-13 over 4 seeds (sd 9.769126e-15, 6.7% of mean; min 1.379360e-13, max 1.578253e-13)
- `sigma_8`: mean 2.001238e-13 over 4 seeds (sd 2.137297e-14, 10.7% of mean; min 1.711633e-13, max 2.200573e-13)
- `sigma_16`: mean 2.876815e-13 over 4 seeds (sd 6.880935e-14, 23.9% of mean; min 2.061578e-13, max 3.502694e-13)
- `sigma_32`: mean 4.207413e-13 over 4 seeds (sd 1.737146e-13, 41.3% of mean; min 2.477859e-13, max 6.188445e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
