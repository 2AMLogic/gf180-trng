---
record: 2026-07-31-inv-stage-noise-26
date: 2026-07-31T19:21:24Z
status: valid

testbench:
  path: sim/tb/inv-stage-noise/tb_inv_stage.sp
  sha: 2e89f1cafd31c265306f1ffda5be7181c34909fe
netlist:
  path: sim/tb/inv-stage-noise/tb_inv_stage.sp
  sha: 2e89f1cafd31c265306f1ffda5be7181c34909fe
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
  path: sim/records/raw/2026-07-31-inv-stage-noise-26/
  files:
    - ss_125c_3.30v.spice  sha256:684e723b51770e4e7a421fad3c2f1e80e14e34f8a60641151658cafcfa1bdd8c
    - ss_125c_3.30v.log  sha256:c0b768a86444937e94b736e60baed22203b4c267e41a969bb5d2087f2fb7f83b
wall_time: 1.4s
---

## Result

- `vtrip`: 1.54476
- `gain_1meg`: 19.4163
- `gain_100meg`: 18.5541
- `gain_1g`: 5.99213
- `inoise_dens_1meg`: 4.319523e-08
- `inoise_dens_10meg`: 1.683883e-08
- `inoise_dens_100meg`: 1.049619e-08
- `inoise_dens_1g`: 9.535369e-09
- `inoise_dens_10g`: 8.902846e-09
- `onoise_dens_1meg`: 8.386917e-07
- `onoise_dens_1g`: 5.713714e-08
- `onoise_rms_1k_100g`: 0.00504737
- `onoise_rms_100meg_100g`: 0.00383883

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners ss --temps 125 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.30 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
