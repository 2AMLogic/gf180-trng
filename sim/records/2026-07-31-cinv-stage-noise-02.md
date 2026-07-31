---
record: 2026-07-31-cinv-stage-noise-02
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-02/
  files:
    - tt_-40c_3.30v.spice  sha256:d45e93988e386d6fe4ce489a1802556022f409576f665449fab41db934c708de
    - tt_-40c_3.30v.log  sha256:197b87d3b9145016c643b6a63bb24f9f31ec95403e11f19fed9a5b45a8770cd8
wall_time: 1.8s
---

## Result

- `vtrip`: 1.49455
- `vbias_n`: 1.63146
- `vbias_p`: 1.13226
- `gain_1meg`: 21.4927
- `gain_100meg`: 20.0397
- `gain_1g`: 5.39658
- `inoise_dens_1meg`: 3.540092e-08
- `inoise_dens_10meg`: 1.428079e-08
- `inoise_dens_100meg`: 9.389667e-09
- `inoise_dens_1g`: 8.557727e-09
- `inoise_dens_10g`: 8.055365e-09
- `onoise_dens_1meg`: 7.608619e-07
- `onoise_dens_1g`: 4.618250e-08
- `onoise_rms_1k_100g`: 0.00452733
- `onoise_rms_100meg_100g`: 0.0033466

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners tt --temps -40 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
