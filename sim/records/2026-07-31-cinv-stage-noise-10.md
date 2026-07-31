---
record: 2026-07-31-cinv-stage-noise-10
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-10/
  files:
    - ff_-40c_2.97v.spice  sha256:f564d5c46eb84d4fe0f4b0624b693e7bcb068fbe8460d2f02fc3d15096227b39
    - ff_-40c_2.97v.log  sha256:6c81ff7b19673f3edaf04592f55e8b544e825e1158dc96c96c4e63b2021596c1
wall_time: 1.7s
---

## Result

- `vtrip`: 1.34529
- `vbias_n`: 1.4382
- `vbias_p`: 1.04361
- `gain_1meg`: 19.6374
- `gain_100meg`: 18.6036
- `gain_1g`: 5.60339
- `inoise_dens_1meg`: 3.478053e-08
- `inoise_dens_10meg`: 1.401872e-08
- `inoise_dens_100meg`: 9.199674e-09
- `inoise_dens_1g`: 8.352681e-09
- `inoise_dens_10g`: 7.838686e-09
- `onoise_dens_1meg`: 6.830008e-07
- `onoise_dens_1g`: 4.680332e-08
- `onoise_rms_1k_100g`: 0.0042549
- `onoise_rms_100meg_100g`: 0.00325519

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners ff --temps -40 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 2.97 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
