---
record: 2026-07-31-inv-stage-noise-13
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
  path: sim/records/raw/2026-07-31-inv-stage-noise-13/
  files:
    - ff_27c_2.97v.spice  sha256:027b0c5660f126e0d3cd68234c32e0a7d07ac314b8f834081a6ce518e1dcb981
    - ff_27c_2.97v.log  sha256:f3708b78552be5155d494e746f6d1df8c79d50ae6621541a3a9f96f1419669a7
wall_time: 1.4s
---

## Result

- `vtrip`: 1.37644
- `gain_1meg`: 16.3545
- `gain_100meg`: 16.1322
- `gain_1g`: 8.41892
- `inoise_dens_1meg`: 3.934845e-08
- `inoise_dens_10meg`: 1.457128e-08
- `inoise_dens_100meg`: 8.105842e-09
- `inoise_dens_1g`: 7.034232e-09
- `inoise_dens_10g`: 6.753162e-09
- `onoise_dens_1meg`: 6.435248e-07
- `onoise_dens_1g`: 5.922061e-08
- `onoise_rms_1k_100g`: 0.00416277
- `onoise_rms_100meg_100g`: 0.00340117

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners ff --temps 27 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 2.97 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
