---
record: 2026-07-31-cinv-stage-noise-14
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-14/
  files:
    - ff_27c_3.30v.spice  sha256:75474c504e801e05319730c2e44b2295bfbff71411c000bd10fdaa0e7fc7525b
    - ff_27c_3.30v.log  sha256:fae109ac20609d6eff7f0c907e272604d6c9ce507c33975707e696f987c510e4
wall_time: 1.4s
---

## Result

- `vtrip`: 1.50587
- `vbias_n`: 1.57755
- `vbias_p`: 1.19263
- `gain_1meg`: 17.3154
- `gain_100meg`: 16.4202
- `gain_1g`: 4.99235
- `inoise_dens_1meg`: 3.973142e-08
- `inoise_dens_10meg`: 1.627283e-08
- `inoise_dens_100meg`: 1.095449e-08
- `inoise_dens_1g`: 1.000507e-08
- `inoise_dens_10g`: 9.292257e-09
- `onoise_dens_1meg`: 6.879637e-07
- `onoise_dens_1g`: 4.994881e-08
- `onoise_rms_1k_100g`: 0.00445509
- `onoise_rms_100meg_100g`: 0.0034593

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners ff --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
