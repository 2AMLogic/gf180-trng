---
record: 2026-07-31-inv-stage-noise-15
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
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 27

analysis:
  type: noise
  tstop: n/a (small-signal: .ac and .noise, 1 kHz - 100 GHz)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-07-31-inv-stage-noise-15/
  files:
    - ff_27c_3.63v.spice  sha256:2fe7e2d133589b359411abcddab80e243482740b787daf6e3754f15cdcf1a714
    - ff_27c_3.63v.log  sha256:7785b15d370219c54996cfe450b52b63f64ec7ff1096980c66b8b2db75812e62
wall_time: 1.2s
---

## Result

- `vtrip`: 1.70195
- `gain_1meg`: 14.5818
- `gain_100meg`: 14.4526
- `gain_1g`: 8.72193
- `inoise_dens_1meg`: 4.561470e-08
- `inoise_dens_10meg`: 1.646539e-08
- `inoise_dens_100meg`: 8.572602e-09
- `inoise_dens_1g`: 7.190826e-09
- `inoise_dens_10g`: 6.892518e-09
- `onoise_dens_1meg`: 6.651439e-07
- `onoise_dens_1g`: 6.271790e-08
- `onoise_rms_1k_100g`: 0.004255
- `onoise_rms_100meg_100g`: 0.00349297

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners ff --temps 27 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
