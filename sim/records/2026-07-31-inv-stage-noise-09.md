---
record: 2026-07-31-inv-stage-noise-09
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
  path: sim/records/raw/2026-07-31-inv-stage-noise-09/
  files:
    - tt_125c_3.63v.spice  sha256:f8412a8fb126196d973fcdb2f8b3f2350f119c62e7cd80e546df5dd523df922f
    - tt_125c_3.63v.log  sha256:def08b14a8d5ac161e0bf275d5257e77a4213141cb9e4a808302e0544e5bf4c3
wall_time: 1.8s
---

## Result

- `vtrip`: 1.71432
- `gain_1meg`: 15.6615
- `gain_100meg`: 15.3651
- `gain_1g`: 7.08069
- `inoise_dens_1meg`: 4.792779e-08
- `inoise_dens_10meg`: 1.789300e-08
- `inoise_dens_100meg`: 1.021404e-08
- `inoise_dens_1g`: 8.972458e-09
- `inoise_dens_10g`: 8.519999e-09
- `onoise_dens_1meg`: 7.506189e-07
- `onoise_dens_1g`: 6.353118e-08
- `onoise_rms_1k_100g`: 0.00472446
- `onoise_rms_100meg_100g`: 0.00378312

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners tt --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.63 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
