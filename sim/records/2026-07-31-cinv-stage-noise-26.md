---
record: 2026-07-31-cinv-stage-noise-26
date: 2026-07-31T19:21:24Z
status: valid

testbench:
  path: sim/tb/cinv-stage-noise/tb_cinv_stage.sp
  sha: 35985181857b11df10f9a71f1306c2ed4a1eb34a
netlist:
  path: sim/tb/cinv-stage-noise/tb_cinv_stage.sp
  sha: 35985181857b11df10f9a71f1306c2ed4a1eb34a
repo_commit: 5988414021b3c1b1ea109dadc6097ae4e62000b3-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-26/
  files:
    - ss_125c_3.30v.spice  sha256:3a7f0b8bb7fe9547f2ce3e9d8326e31bb9f6dd2f2fef08aa5e2366bcdc108917
    - ss_125c_3.30v.log  sha256:dc01f0aee9855fc5bbd2dd32857a0ce515e1e16d50008e5cf3933ff2712e178a
wall_time: 1.3s
---

## Result

- `vtrip`: 1.51738
- `vbias_n`: 1.89649
- `vbias_p`: 0.898061
- `gain_1meg`: 21.6647
- `gain_100meg`: 18.2264
- `gain_1g`: 3.35643
- `inoise_dens_1meg`: 4.306474e-08
- `inoise_dens_10meg`: 1.909328e-08
- `inoise_dens_100meg`: 1.414362e-08
- `inoise_dens_1g`: 1.337435e-08
- `inoise_dens_10g`: 1.193222e-08
- `onoise_dens_1meg`: 9.329849e-07
- `onoise_dens_1g`: 4.489013e-08
- `onoise_rms_1k_100g`: 0.00546768
- `onoise_rms_100meg_100g`: 0.00371146

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners ss --temps 125 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.30 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
