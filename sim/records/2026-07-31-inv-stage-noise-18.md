---
record: 2026-07-31-inv-stage-noise-18
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
  temperature: 125

analysis:
  type: noise
  tstop: n/a (small-signal: .ac and .noise, 1 kHz - 100 GHz)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-07-31-inv-stage-noise-18/
  files:
    - ff_125c_3.63v.spice  sha256:47b2feab1499128bed02e0c099ee6b1dd51b7539be183f8fe969929345f19c55
    - ff_125c_3.63v.log  sha256:976697b69dab6c9fc74437ccbd244e674872c8908f6b58271bad073c5d451401
wall_time: 1.1s
---

## Result

- `vtrip`: 1.71927
- `gain_1meg`: 13.3221
- `gain_100meg`: 13.1813
- `gain_1g`: 7.51105
- `inoise_dens_1meg`: 5.110601e-08
- `inoise_dens_10meg`: 1.867747e-08
- `inoise_dens_100meg`: 1.010660e-08
- `inoise_dens_1g`: 8.658527e-09
- `inoise_dens_10g`: 8.268861e-09
- `onoise_dens_1meg`: 6.808384e-07
- `onoise_dens_1g`: 6.503459e-08
- `onoise_rms_1k_100g`: 0.00444112
- `onoise_rms_100meg_100g`: 0.00365711

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners ff --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
