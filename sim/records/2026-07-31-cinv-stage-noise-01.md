---
record: 2026-07-31-cinv-stage-noise-01
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-01/
  files:
    - tt_-40c_2.97v.spice  sha256:9e80765cb6bb7928fa3bc49eb657f5efc15e3fddd54a98f540ad8819022785c8
    - tt_-40c_2.97v.log  sha256:ff0cfa45fcdc70b3664c2fe178bce825bba5655403836248b7fa6d5dd093d69d
wall_time: 1.8s
---

## Result

- `vtrip`: 1.34328
- `vbias_n`: 1.5522
- `vbias_p`: 0.91789
- `gain_1meg`: 23.0923
- `gain_100meg`: 21.1255
- `gain_1g`: 5.12608
- `inoise_dens_1meg`: 3.434471e-08
- `inoise_dens_10meg`: 1.397551e-08
- `inoise_dens_100meg`: 9.303395e-09
- `inoise_dens_1g`: 8.537292e-09
- `inoise_dens_10g`: 8.016340e-09
- `onoise_dens_1meg`: 7.930980e-07
- `onoise_dens_1g`: 4.376287e-08
- `onoise_rms_1k_100g`: 0.00458523
- `onoise_rms_100meg_100g`: 0.00329136

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners tt --temps -40 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
