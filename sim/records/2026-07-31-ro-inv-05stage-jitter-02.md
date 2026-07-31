---
record: 2026-07-31-ro-inv-05stage-jitter-02
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
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-02/
  files:
    - tt_-40c_3.30v-run0.spice  sha256:1bd69a86e9292e54d9a2f305b0598b63a38f2c5bf365e9f5a0ee9bf16bce805f
    - tt_-40c_3.30v-run0.log  sha256:02d12479ecb81a6880c98ba7faa0890b36ee64d210959771ebb52f786c6e4dab
    - tt_-40c_3.30v-run1.spice  sha256:f3d72160edaf996c8ecebf57dfce0977f2a344b918cb2772295bdbd888b32801
    - tt_-40c_3.30v-run1.log  sha256:0b46ce0100cbbf3b225def395109cfb920276b9a589cebe388cbf49c3d7680aa
    - tt_-40c_3.30v-run2.spice  sha256:7e8d89f28116f060565564d9d3dbacb69c510b459d11df09c1b2d35acc593c6d
    - tt_-40c_3.30v-run2.log  sha256:e1f721b9f9b94d58ee4bbeb476804cb15e31d8de12c4d14fb6568f92f58a5ae8
    - tt_-40c_3.30v-run3.spice  sha256:ad57e394243c9d31c0af2d0202ebc8cf79eae8515106a3b36694542a4947619f
    - tt_-40c_3.30v-run3.log  sha256:3f09049b9c6e45b35b05a09c0a7641ebe007c91852883c3918c38ba3236ea767
wall_time: 6.7m
---

## Result

- `period`: mean 5.459638e-10 over 4 seeds (sd 2.396706e-15, 0.0% of mean; min 5.459614e-10, max 5.459666e-10)
- `f_osc`: mean 1.831623e+09 over 4 seeds (sd 8040.56, 0.0% of mean; min 1.831614e+09, max 1.831631e+09)
- `slew_v_per_s`: mean 3.988950e+10 over 4 seeds (sd 7.500420e+07, 0.2% of mean; min 3.978780e+10, max 3.996609e+10)
- `sigma_1`: mean 7.800821e-14 over 4 seeds (sd 4.792539e-15, 6.1% of mean; min 7.125081e-14, max 8.256563e-14)
- `sigma_2`: mean 1.079621e-13 over 4 seeds (sd 1.740192e-14, 16.1% of mean; min 8.559076e-14, max 1.278768e-13)
- `sigma_4`: mean 1.490574e-13 over 4 seeds (sd 3.176356e-14, 21.3% of mean; min 1.063503e-13, max 1.830189e-13)
- `sigma_8`: mean 2.079704e-13 over 4 seeds (sd 5.653660e-14, 27.2% of mean; min 1.275161e-13, max 2.596392e-13)
- `sigma_16`: mean 3.095648e-13 over 4 seeds (sd 1.060003e-13, 34.2% of mean; min 1.607671e-13, max 4.023161e-13)
- `sigma_32`: mean 4.401925e-13 over 4 seeds (sd 2.077543e-13, 47.2% of mean; min 1.580065e-13, max 6.256543e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
