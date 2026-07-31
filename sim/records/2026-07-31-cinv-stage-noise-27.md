---
record: 2026-07-31-cinv-stage-noise-27
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
  voltage: 3.630 V (nominal 3.3 V, +10%)
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-27/
  files:
    - ss_125c_3.63v.spice  sha256:56b4b416e424d23a80c73790d7c49448b4848367b93ff4b1f4a67918c9aab371
    - ss_125c_3.63v.log  sha256:eaf2b31c7f4762043fdfd562a2298b9ee4b1b9d9a6c7ffbcd700426b29058c8b
wall_time: 1.2s
---

## Result

- `vtrip`: 1.67481
- `vbias_n`: 2.0052
- `vbias_p`: 1.07503
- `gain_1meg`: 20.3968
- `gain_100meg`: 17.7397
- `gain_1g`: 3.56597
- `inoise_dens_1meg`: 4.442368e-08
- `inoise_dens_10meg`: 1.933582e-08
- `inoise_dens_100meg`: 1.405724e-08
- `inoise_dens_1g`: 1.321799e-08
- `inoise_dens_10g`: 1.192659e-08
- `onoise_dens_1meg`: 9.061016e-07
- `onoise_dens_1g`: 4.713493e-08
- `onoise_rms_1k_100g`: 0.00540335
- `onoise_rms_100meg_100g`: 0.00378031

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners ss --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
