---
record: 2026-07-31-ro-inv-05stage-lownoise-03
date: 2026-07-31T19:31:41Z
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
  noise_params: per-stage trnoise( NA=2.2361e-4 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-18 V^2/Hz (1e-09 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-lownoise-03/
  files:
    - ss_125c_2.97v-run0.spice  sha256:41b8d5686a63eb2629e80750dcf342ae288bb5dd33903641492974442e83c931
    - ss_125c_2.97v-run0.log  sha256:a834fb3407ab17aebfeb9d2e5304eb5ed6425689a7fd389ce57d431797099f37
    - ss_125c_2.97v-run1.spice  sha256:0897dd943be1b99cd50298ad7f175eb8a191a1391bdb6c8d5a4ae4a487c215ea
    - ss_125c_2.97v-run1.log  sha256:bfe7be60615d12b4bd23e46369babf98c365441d26f7bd3b915e6e3e174e8b77
    - ss_125c_2.97v-run2.spice  sha256:9d00b2c3816522d8e1e9b837334f2b5e57e5c5538d2159fd32da779bee15cc86
    - ss_125c_2.97v-run2.log  sha256:f5153bb0cc10796fb19ed33d139a8a38f4698b97f26c2d6a98257b7f0d5ef9ef
    - ss_125c_2.97v-run3.spice  sha256:e119ec22a83928a314ffe873830fd921a1be152fe552b4849363115e9909940d
    - ss_125c_2.97v-run3.log  sha256:142e5e7ab89861800b8d08591c3584966cb6ffdc193ab6400791d15b0921e42b
wall_time: 10.0m
---

## Result

- `period`: mean 9.723863e-10 over 4 seeds (sd 7.421830e-16, 0.0% of mean; min 9.723856e-10, max 9.723873e-10)
- `f_osc`: mean 1.028398e+09 over 4 seeds (sd 784.928, 0.0% of mean; min 1.028397e+09, max 1.028399e+09)
- `slew_v_per_s`: mean 2.067903e+10 over 4 seeds (sd 3.915308e+06, 0.0% of mean; min 2.067381e+10, max 2.068317e+10)
- `sigma_1`: mean 2.155183e-14 over 4 seeds (sd 1.742753e-15, 8.1% of mean; min 1.908085e-14, max 2.303621e-14)
- `sigma_2`: mean 2.611756e-14 over 4 seeds (sd 8.286638e-16, 3.2% of mean; min 2.536091e-14, max 2.705983e-14)
- `sigma_4`: mean 3.168581e-14 over 4 seeds (sd 2.465121e-15, 7.8% of mean; min 2.919021e-14, max 3.394928e-14)
- `sigma_8`: mean 3.821465e-14 over 4 seeds (sd 7.733095e-15, 20.2% of mean; min 3.134559e-14, max 4.845042e-14)
- `sigma_16`: mean 4.493244e-14 over 4 seeds (sd 1.001535e-14, 22.3% of mean; min 3.841447e-14, max 5.959715e-14)
- `sigma_32`: mean 5.850016e-14 over 4 seeds (sd 2.304822e-14, 39.4% of mean; min 4.616303e-14, max 9.306164e-14)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
