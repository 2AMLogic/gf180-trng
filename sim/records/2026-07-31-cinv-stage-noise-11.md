---
record: 2026-07-31-cinv-stage-noise-11
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-11/
  files:
    - ff_-40c_3.30v.spice  sha256:178164f24744d9e29524dddde2c5518da98532cc2e6a255a4cb4919ec2c8c8d3
    - ff_-40c_3.30v.log  sha256:2aecfe320ed3fcf6fee2f703d92439f13b024b4127b670f627ce87e481e9c281
wall_time: 1.7s
---

## Result

- `vtrip`: 1.49784
- `vbias_n`: 1.5123
- `vbias_p`: 1.26446
- `gain_1meg`: 18.4183
- `gain_100meg`: 17.623
- `gain_1g`: 5.79521
- `inoise_dens_1meg`: 3.620204e-08
- `inoise_dens_10meg`: 1.445537e-08
- `inoise_dens_100meg`: 9.354127e-09
- `inoise_dens_1g`: 8.422189e-09
- `inoise_dens_10g`: 7.908550e-09
- `onoise_dens_1meg`: 6.667797e-07
- `onoise_dens_1g`: 4.880832e-08
- `onoise_rms_1k_100g`: 0.00423246
- `onoise_rms_100meg_100g`: 0.00329425

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners ff --temps -40 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.30 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
