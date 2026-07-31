---
record: 2026-07-31-inv-stage-noise-02
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
  path: sim/records/raw/2026-07-31-inv-stage-noise-02/
  files:
    - tt_-40c_3.30v.spice  sha256:6ea2f9cf201210b1118fb7e0c5e8c98b3605e753cd7b85dcfd8229ad3842a195
    - tt_-40c_3.30v.log  sha256:e16b66ad0a23dc13913c201af2e3e6cbcb3aef33ac111a118f87b11c7af36f3b
wall_time: 1.8s
---

## Result

- `vtrip`: 1.52743
- `gain_1meg`: 19.3533
- `gain_100meg`: 19.0314
- `gain_1g`: 9.21594
- `inoise_dens_1meg`: 3.599867e-08
- `inoise_dens_10meg`: 1.325747e-08
- `inoise_dens_100meg`: 7.273904e-09
- `inoise_dens_1g`: 6.270834e-09
- `inoise_dens_10g`: 6.020145e-09
- `onoise_dens_1meg`: 6.966936e-07
- `onoise_dens_1g`: 5.779162e-08
- `onoise_rms_1k_100g`: 0.00426991
- `onoise_rms_100meg_100g`: 0.00339866

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners tt --temps -40 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
