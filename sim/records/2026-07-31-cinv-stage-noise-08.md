---
record: 2026-07-31-cinv-stage-noise-08
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-08/
  files:
    - tt_125c_3.30v.spice  sha256:1903ae85ded60c27b78546b31420d9c5a7e9919d85fc8bd9e8f0daf2a6aa67bc
    - tt_125c_3.30v.log  sha256:86fca56a1c01f2b75abc93fd0bc9ca166e2dbe0a2c41f77d0f71800ed9db10c8
wall_time: 2.1s
---

## Result

- `vtrip`: 1.52088
- `vbias_n`: 1.77864
- `vbias_p`: 1.00499
- `gain_1meg`: 18.6162
- `gain_100meg`: 16.7314
- `gain_1g`: 3.76771
- `inoise_dens_1meg`: 4.351810e-08
- `inoise_dens_10meg`: 1.885970e-08
- `inoise_dens_100meg`: 1.363726e-08
- `inoise_dens_1g`: 1.277859e-08
- `inoise_dens_10g`: 1.155588e-08
- `onoise_dens_1meg`: 8.101414e-07
- `onoise_dens_1g`: 4.814599e-08
- `onoise_rms_1k_100g`: 0.00506747
- `onoise_rms_100meg_100g`: 0.00370545

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners tt --temps 125 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
