---
record: 2026-07-31-inv-stage-noise-22
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
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
  path: sim/records/raw/2026-07-31-inv-stage-noise-22/
  files:
    - ss_27c_2.97v.spice  sha256:f9ce773375f1182452bf0a1f19ea5cf57b341bb67e4b1da51b33b588c3e5e299
    - ss_27c_2.97v.log  sha256:6b6c620ed212dcff32a468c47570482ea6e341c72c44b0cc09c8b8164c6ab194
wall_time: 1.3s
---

## Result

- `vtrip`: 1.36673
- `gain_1meg`: 23.1946
- `gain_100meg`: 21.9846
- `gain_1g`: 6.6134
- `inoise_dens_1meg`: 3.677790e-08
- `inoise_dens_10meg`: 1.420215e-08
- `inoise_dens_100meg`: 8.665059e-09
- `inoise_dens_1g`: 7.810601e-09
- `inoise_dens_10g`: 7.345253e-09
- `onoise_dens_1meg`: 8.530493e-07
- `onoise_dens_1g`: 5.165459e-08
- `onoise_rms_1k_100g`: 0.00485818
- `onoise_rms_100meg_100g`: 0.00357366

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners ss --temps 27 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
