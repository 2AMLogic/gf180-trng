---
record: 2026-07-31-ro-inv-05stage-jitter-10
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
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: -40

analysis:
  type: tran-noise
  tstop: 170n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-10/
  files:
    - ff_-40c_2.97v-run0.spice  sha256:0a3befc7cbbe52fc30c3ff3ee04f95e567c33dfbe6da36c11926bd11452bc50c
    - ff_-40c_2.97v-run0.log  sha256:f3715baa0148b077207317907e7f4abcc5824ca401ce6ad5f379ad46d249bbce
    - ff_-40c_2.97v-run1.spice  sha256:c6a70d109c2c9905648cbe001e183682f7107c263a1eaf1940c02102f31dc836
    - ff_-40c_2.97v-run1.log  sha256:ddcd7a7273a8e021f5d7b266a840fb8d1e91a5219fe5aa72deffdfbde95c0b2a
    - ff_-40c_2.97v-run2.spice  sha256:0c27aee9364b881473315633b30f91a9175874964d6b3a39cfe68e151bed6ec4
    - ff_-40c_2.97v-run2.log  sha256:d78a8dff38c4c00ba500943171e9d7725f736d1feb3420750fbafdcd41a8372a
    - ff_-40c_2.97v-run3.spice  sha256:0159452c0eab814f53691e612cb0a18ee237e03c6a0eb47813e99d3a85c47b91
    - ff_-40c_2.97v-run3.log  sha256:4f32746b5c97e344eb4b6eb5bc14a7471d43f8f3f81ba2f623438e6339afc93c
wall_time: 2.4m
---

## Result

- `period`: mean 4.941802e-10 over 4 seeds (sd 5.753015e-15, 0.0% of mean; min 4.941733e-10, max 4.941853e-10)
- `f_osc`: mean 2.023553e+09 over 4 seeds (sd 23557.3, 0.0% of mean; min 2.023533e+09, max 2.023582e+09)
- `slew_v_per_s`: mean 3.857409e+10 over 4 seeds (sd 8.975397e+07, 0.2% of mean; min 3.847898e+10, max 3.868447e+10)
- `sigma_1`: mean 8.433202e-14 over 4 seeds (sd 6.370897e-15, 7.6% of mean; min 7.650033e-14, max 9.190415e-14)
- `sigma_2`: mean 1.160656e-13 over 4 seeds (sd 1.238604e-14, 10.7% of mean; min 1.015628e-13, max 1.305620e-13)
- `sigma_4`: mean 1.628019e-13 over 4 seeds (sd 1.890843e-14, 11.6% of mean; min 1.369583e-13, max 1.813975e-13)
- `sigma_8`: mean 2.262630e-13 over 4 seeds (sd 3.395171e-14, 15.0% of mean; min 1.754013e-13, max 2.451515e-13)
- `sigma_16`: mean 3.251098e-13 over 4 seeds (sd 8.113734e-14, 25.0% of mean; min 2.099105e-13, max 3.987230e-13)
- `sigma_32`: mean 4.879962e-13 over 4 seeds (sd 1.524185e-13, 31.2% of mean; min 3.010010e-13, max 6.738156e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 2.97 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
