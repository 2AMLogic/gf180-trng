---
record: 2026-08-01-device-leakage-03v3-38
date: 2026-08-01T00:28:19Z
status: valid

testbench:
  path: sim/tb/device-leakage-03v3/tb_device_leakage.sp
  sha: e7880addef5814f81010137d1b973cadc5f1a9ee
netlist:
  path: sim/tb/device-leakage-03v3/tb_device_leakage.sp
  sha: e7880addef5814f81010137d1b973cadc5f1a9ee
repo_commit: f03dd6c3036d67bd4f2245b92bb7765e23396d55-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: sf bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: sf
  voltage: 3.300 V (nominal 3.3 V)
  temperature: -40

analysis:
  type: dc
  tstop: n/a (operating point; single DC bias solution, no sweep)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-device-leakage-03v3-38/
  files:
    - sf_-40c_3.30v.spice  sha256:985f7ae8d191ddbf14f2b332f45b354e6c5bc2c60aec5ebe1752de38d4019405
    - sf_-40c_3.30v.log  sha256:d01de9bdfad1fcce75cd6b7ee5a0bda073110d9183948a0e7a27342ee82b2c4b
wall_time: 1.2s
---

## Result

- `ioff_nfet_a`: 3.311826e-12
- `ioff_pfet_a`: 4.107184e-12
- `ioff_nfet_a_per_um`: 3.311826e-13
- `ioff_pfet_a_per_um`: 4.107184e-13

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py device-leakage-03v3 --corners sf --temps -40 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (sf / 3.30 V / -40 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
