---
record: 2026-07-31-ro-inv-05stage-jitter-09
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-09/
  files:
    - tt_125c_3.63v-run0.spice  sha256:5b6635de537e8d4e4786807d9908b49105bb7fd07fa4a3721ca37c334dffca87
    - tt_125c_3.63v-run0.log  sha256:5abe6d68e8c3d97f21bcb5edf7e63f99dfe43c6dc062ff3de619f85092220e3c
    - tt_125c_3.63v-run1.spice  sha256:23d3aa63a7df819cf7ee256ca813f98b461cdf5f4040406eac9762802d1a0b2f
    - tt_125c_3.63v-run1.log  sha256:9c09e22f15d397a9037d7bffc890b9b3f519362d2a0935bc29905cba8f10189b
    - tt_125c_3.63v-run2.spice  sha256:02ee9ad9c82c967e0a8e9c19ba9493ac21533fb998afba921c4ed5359c646f1e
    - tt_125c_3.63v-run2.log  sha256:9fafceaa9aafe595c31411456da964805abc8da3bfe8bde2b3087bd0d9a6f855
    - tt_125c_3.63v-run3.spice  sha256:ba08c59c71ad227d3c3bb07bd354975042ef2ff7317acc56bd5ab8f3a9ad6f35
    - tt_125c_3.63v-run3.log  sha256:25b3d7347e9cff623bbbeda574356e89d4d65ed1249ce6786ca156e84acc46d9
wall_time: 3.6m
---

## Result

- `period`: mean 6.772052e-10 over 4 seeds (sd 7.962769e-15, 0.0% of mean; min 6.771967e-10, max 6.772141e-10)
- `f_osc`: mean 1.476657e+09 over 4 seeds (sd 17362.9, 0.0% of mean; min 1.476638e+09, max 1.476676e+09)
- `slew_v_per_s`: mean 3.466853e+10 over 4 seeds (sd 7.114151e+07, 0.2% of mean; min 3.456484e+10, max 3.472687e+10)
- `sigma_1`: mean 8.189471e-14 over 4 seeds (sd 1.305035e-15, 1.6% of mean; min 8.001461e-14, max 8.279073e-14)
- `sigma_2`: mean 1.120474e-13 over 4 seeds (sd 4.203272e-15, 3.8% of mean; min 1.058573e-13, max 1.147533e-13)
- `sigma_4`: mean 1.526663e-13 over 4 seeds (sd 1.277096e-14, 8.4% of mean; min 1.371357e-13, max 1.636693e-13)
- `sigma_8`: mean 2.056296e-13 over 4 seeds (sd 2.492953e-14, 12.1% of mean; min 1.846010e-13, max 2.376705e-13)
- `sigma_16`: mean 2.855292e-13 over 4 seeds (sd 6.585900e-14, 23.1% of mean; min 2.391256e-13, max 3.810135e-13)
- `sigma_32`: mean 4.086269e-13 over 4 seeds (sd 1.311493e-13, 32.1% of mean; min 3.180782e-13, max 5.991546e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.63 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
