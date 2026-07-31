---
record: 2026-07-31-cinv-stage-noise-23
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-23/
  files:
    - ss_27c_3.30v.spice  sha256:b9df5acde79455b5c6f6d014a7fb4d07decd61adcfe79c0cb693c2b39bba3b2e
    - ss_27c_3.30v.log  sha256:3d4dad6e56fee2aa9eeab2dff8c8f657fa7ff7467e317decdb86c270c0ee3a43
wall_time: 1.4s
---

## Result

- `vtrip`: 1.50114
- `vbias_n`: 1.81555
- `vbias_p`: 0.939441
- `gain_1meg`: 23.5659
- `gain_100meg`: 20.5102
- `gain_1g`: 4.12345
- `inoise_dens_1meg`: 3.852809e-08
- `inoise_dens_10meg`: 1.628579e-08
- `inoise_dens_100meg`: 1.142965e-08
- `inoise_dens_1g`: 1.066623e-08
- `inoise_dens_10g`: 9.840821e-09
- `onoise_dens_1meg`: 9.079480e-07
- `onoise_dens_1g`: 4.398161e-08
- `onoise_rms_1k_100g`: 0.0051599
- `onoise_rms_100meg_100g`: 0.00353383

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners ss --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
