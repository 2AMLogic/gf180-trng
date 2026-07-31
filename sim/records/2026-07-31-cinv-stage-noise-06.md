---
record: 2026-07-31-cinv-stage-noise-06
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-06/
  files:
    - tt_27c_3.63v.spice  sha256:f6360dddfd89398b8cdff9237ff25fe6d3632716008c20e1ffdc9132bf85f78b
    - tt_27c_3.63v.log  sha256:e0e9efcb78fd71391b3802a53700c2c6c0d8e34fd7cd89847137cf51f34d7a3f
wall_time: 1.6s
---

## Result

- `vtrip`: 1.65669
- `vbias_n`: 1.784
- `vbias_p`: 1.27158
- `gain_1meg`: 19.1244
- `gain_100meg`: 17.8275
- `gain_1g`: 4.80012
- `inoise_dens_1meg`: 4.043723e-08
- `inoise_dens_10meg`: 1.656861e-08
- `inoise_dens_100meg`: 1.116487e-08
- `inoise_dens_1g`: 1.023755e-08
- `inoise_dens_10g`: 9.532567e-09
- `onoise_dens_1meg`: 7.733372e-07
- `onoise_dens_1g`: 4.914151e-08
- `onoise_rms_1k_100g`: 0.00475137
- `onoise_rms_100meg_100g`: 0.00355755

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners tt --temps 27 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.63 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
