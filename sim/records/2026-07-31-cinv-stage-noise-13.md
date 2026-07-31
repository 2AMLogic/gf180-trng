---
record: 2026-07-31-cinv-stage-noise-13
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-13/
  files:
    - ff_27c_2.97v.spice  sha256:9a35c0be2dbb15dd7f7aac04f2c4ac38bffc9e4f6eb92f2a7c274cf0626cee11
    - ff_27c_2.97v.log  sha256:7c631f0ad40ac9153da5e12877c1b9f233e1f3a2be22888c7579ed4efb6e3f0f
wall_time: 1.5s
---

## Result

- `vtrip`: 1.35279
- `vbias_n`: 1.49237
- `vbias_p`: 0.983927
- `gain_1meg`: 18.4113
- `gain_100meg`: 17.2438
- `gain_1g`: 4.78579
- `inoise_dens_1meg`: 3.822009e-08
- `inoise_dens_10meg`: 1.586793e-08
- `inoise_dens_100meg`: 1.087598e-08
- `inoise_dens_1g`: 1.001310e-08
- `inoise_dens_10g`: 9.272407e-09
- `onoise_dens_1meg`: 7.036811e-07
- `onoise_dens_1g`: 4.792055e-08
- `onoise_rms_1k_100g`: 0.0044885
- `onoise_rms_100meg_100g`: 0.00342548

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners ff --temps 27 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 2.97 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
