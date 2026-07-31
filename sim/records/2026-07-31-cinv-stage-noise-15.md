---
record: 2026-07-31-cinv-stage-noise-15
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-15/
  files:
    - ff_27c_3.63v.spice  sha256:dcfb477f58f6bbb6a11dab745b6b3a54a10aaf1e7394772ec4c34333fd6dbb71
    - ff_27c_3.63v.log  sha256:74e84fbaafeb23103fe087d770e27b343670da595aa91aa679bcfac321bf3325
wall_time: 1.4s
---

## Result

- `vtrip`: 1.66045
- `vbias_n`: 1.65955
- `vbias_p`: 1.40727
- `gain_1meg`: 16.4224
- `gain_100meg`: 15.7053
- `gain_1g`: 5.14516
- `inoise_dens_1meg`: 4.150841e-08
- `inoise_dens_10meg`: 1.677442e-08
- `inoise_dens_100meg`: 1.108111e-08
- `inoise_dens_1g`: 1.003696e-08
- `inoise_dens_10g`: 9.338959e-09
- `onoise_dens_1meg`: 6.816697e-07
- `onoise_dens_1g`: 5.164177e-08
- `onoise_rms_1k_100g`: 0.00444284
- `onoise_rms_100meg_100g`: 0.00348759

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners ff --temps 27 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
