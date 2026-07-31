---
record: 2026-07-31-inv-stage-noise-01
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
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
  path: sim/records/raw/2026-07-31-inv-stage-noise-01/
  files:
    - tt_-40c_2.97v.spice  sha256:e3b304caf9c66b45915a89b8591fbcfaa44f2f36ffdc18da9daf606de01a1fcd
    - tt_-40c_2.97v.log  sha256:f6ff14199d9f78efe9230394de45566719adadb7c5818f2e25e0ad87be93b976
wall_time: 1.6s
---

## Result

- `vtrip`: 1.36579
- `gain_1meg`: 20.9323
- `gain_100meg`: 20.4649
- `gain_1g`: 8.83112
- `inoise_dens_1meg`: 3.401709e-08
- `inoise_dens_10meg`: 1.265859e-08
- `inoise_dens_100meg`: 7.115572e-09
- `inoise_dens_1g`: 6.203591e-09
- `inoise_dens_10g`: 5.947627e-09
- `onoise_dens_1meg`: 7.120561e-07
- `onoise_dens_1g`: 5.478465e-08
- `onoise_rms_1k_100g`: 0.00427167
- `onoise_rms_100meg_100g`: 0.00334065

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners tt --temps -40 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
