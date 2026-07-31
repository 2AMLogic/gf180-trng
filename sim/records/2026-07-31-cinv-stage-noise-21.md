---
record: 2026-07-31-cinv-stage-noise-21
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-21/
  files:
    - ss_-40c_3.63v.spice  sha256:ccd1e18ae7ec48b6a36f666b8250f392c98441d8a283228aea056bc61d00fa84
    - ss_-40c_3.63v.log  sha256:bb8781b2676dfe7769b275ef20f8f5a80132a0343628cc042b67b80aa1fa6a9e
wall_time: 1.4s
---

## Result

- `vtrip`: 1.646
- `vbias_n`: 1.8327
- `vbias_p`: 1.21768
- `gain_1meg`: 23.3014
- `gain_100meg`: 21.2756
- `gain_1g`: 5.11514
- `inoise_dens_1meg`: 3.595337e-08
- `inoise_dens_10meg`: 1.459669e-08
- `inoise_dens_100meg`: 9.697548e-09
- `inoise_dens_1g`: 8.889879e-09
- `inoise_dens_10g`: 8.386630e-09
- `onoise_dens_1meg`: 8.377628e-07
- `onoise_dens_1g`: 4.547299e-08
- `onoise_rms_1k_100g`: 0.00481042
- `onoise_rms_100meg_100g`: 0.00343413

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners ss --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
