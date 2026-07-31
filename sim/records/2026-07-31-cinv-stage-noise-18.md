---
record: 2026-07-31-cinv-stage-noise-18
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-18/
  files:
    - ff_125c_3.63v.spice  sha256:3ed86c2bc37d4dad36706ccd400a1c1f0876ff288645a2fef280c99704c7636d
    - ff_125c_3.63v.log  sha256:cfb8e095ed2b64ccc91727a34fd6b20fc1cd42f85cc62aa3a5ec37d0f1b920b4
wall_time: 1.5s
---

## Result

- `vtrip`: 1.68227
- `vbias_n`: 1.75637
- `vbias_p`: 1.32535
- `gain_1meg`: 15.0448
- `gain_100meg`: 14.2439
- `gain_1g`: 4.28168
- `inoise_dens_1meg`: 4.622026e-08
- `inoise_dens_10meg`: 1.932384e-08
- `inoise_dens_100meg`: 1.339855e-08
- `inoise_dens_1g`: 1.233650e-08
- `inoise_dens_10g`: 1.128170e-08
- `onoise_dens_1meg`: 6.953743e-07
- `onoise_dens_1g`: 5.282101e-08
- `onoise_rms_1k_100g`: 0.00467594
- `onoise_rms_100meg_100g`: 0.00366932

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners ff --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
