---
record: 2026-07-31-inv-stage-noise-10
date: 2026-07-31T19:21:24Z
status: valid

testbench:
  path: sim/tb/inv-stage-noise/tb_inv_stage.sp
  sha: 2e89f1cafd31c265306f1ffda5be7181c34909fe
netlist:
  path: sim/tb/inv-stage-noise/tb_inv_stage.sp
  sha: 2e89f1cafd31c265306f1ffda5be7181c34909fe
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
  type: noise
  tstop: n/a (small-signal: .ac and .noise, 1 kHz - 100 GHz)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-07-31-inv-stage-noise-10/
  files:
    - ff_-40c_2.97v.spice  sha256:7e62198e8343dc3d77a7a2d25a07f1cbc5aea0bdc9d0c433df945613b11e1cae
    - ff_-40c_2.97v.log  sha256:a8fb96bc16da0ceb96c6ffd5bab88049ab7c403b267b2c99dff6d1d48c6c41b0
wall_time: 1.5s
---

## Result

- `vtrip`: 1.37239
- `gain_1meg`: 17.5849
- `gain_100meg`: 17.3795
- `gain_1g`: 9.56935
- `inoise_dens_1meg`: 3.553242e-08
- `inoise_dens_10meg`: 1.300925e-08
- `inoise_dens_100meg`: 7.010979e-09
- `inoise_dens_1g`: 5.988624e-09
- `inoise_dens_10g`: 5.765485e-09
- `onoise_dens_1meg`: 6.248349e-07
- `onoise_dens_1g`: 5.730726e-08
- `onoise_rms_1k_100g`: 0.00398518
- `onoise_rms_100meg_100g`: 0.00325173

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners ff --temps -40 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 2.97 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
