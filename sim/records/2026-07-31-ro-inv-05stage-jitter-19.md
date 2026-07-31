---
record: 2026-07-31-ro-inv-05stage-jitter-19
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-19/
  files:
    - ss_-40c_2.97v-run0.spice  sha256:1ac0ba6de1bfe214f649608095079ce9986667782e06494d6911d97ce8bdda73
    - ss_-40c_2.97v-run0.log  sha256:a2406dd1b64e780f268818fdde2acc885023b71d52b7c5d8655188d477a41031
    - ss_-40c_2.97v-run1.spice  sha256:d9e1dc3253821d857cc48a02100498e46bc91ea1a77e941a0a56e095c260a456
    - ss_-40c_2.97v-run1.log  sha256:bf2f26e3fdb5e86acf6ea25d748ef2a6dde26be66d7a2158c653a8f011636cf8
    - ss_-40c_2.97v-run2.spice  sha256:cc43746577c3ecea4c0176be8e31537baa6490aa688c77c693f02683ce29fcd2
    - ss_-40c_2.97v-run2.log  sha256:641624d5e05ad6e9323a2a369ba6596398718b85191a5ef3374cfa99c099f408
    - ss_-40c_2.97v-run3.spice  sha256:068dcd7c741a938e6727ec9b6af5ea339f966ef2f5e1f18e7d02727c0ba88312
    - ss_-40c_2.97v-run3.log  sha256:f7fd8cf2ec4bc1bd3b051314bb7a28273bd50855825cb857d3dbb942fb13fb06
wall_time: 2.2m
---

## Result

- `period`: mean 7.323175e-10 over 4 seeds (sd 9.417129e-15, 0.0% of mean; min 7.323045e-10, max 7.323260e-10)
- `f_osc`: mean 1.365528e+09 over 4 seeds (sd 17560, 0.0% of mean; min 1.365512e+09, max 1.365552e+09)
- `slew_v_per_s`: mean 2.788057e+10 over 4 seeds (sd 6.496358e+07, 0.2% of mean; min 2.778557e+10, max 2.792928e+10)
- `sigma_1`: mean 1.113195e-13 over 4 seeds (sd 5.307986e-15, 4.8% of mean; min 1.055978e-13, max 1.181683e-13)
- `sigma_2`: mean 1.492433e-13 over 4 seeds (sd 1.145207e-14, 7.7% of mean; min 1.370568e-13, max 1.642542e-13)
- `sigma_4`: mean 1.988806e-13 over 4 seeds (sd 1.854007e-14, 9.3% of mean; min 1.805517e-13, max 2.245277e-13)
- `sigma_8`: mean 2.715477e-13 over 4 seeds (sd 3.140975e-14, 11.6% of mean; min 2.323298e-13, max 2.995971e-13)
- `sigma_16`: mean 3.943003e-13 over 4 seeds (sd 1.087183e-13, 27.6% of mean; min 2.633711e-13, max 5.229669e-13)
- `sigma_32`: mean 6.139901e-13 over 4 seeds (sd 2.740460e-13, 44.6% of mean; min 3.022435e-13, max 9.596366e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps -40 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
