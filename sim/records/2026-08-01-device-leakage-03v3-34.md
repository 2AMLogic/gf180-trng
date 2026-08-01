---
record: 2026-08-01-device-leakage-03v3-34
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: fs bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: fs
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: dc
  tstop: n/a (operating point; single DC bias solution, no sweep)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-device-leakage-03v3-34/
  files:
    - fs_125c_2.97v.spice  sha256:7288a868f03974f940fe5c9b315d9f08c462aa1fca170f658eba807088f628db
    - fs_125c_2.97v.log  sha256:81c211bb2e4d015a751f8a53f2c2a9becfa30fc477886faad684f0327c6b9104
wall_time: 0.8s
---

## Result

- `ioff_nfet_a`: 1.049816e-08
- `ioff_pfet_a`: 1.404088e-11
- `ioff_nfet_a_per_um`: 1.049816e-09
- `ioff_pfet_a_per_um`: 1.404088e-12

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py device-leakage-03v3 --corners fs --temps 125 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (fs / 2.97 V / 125 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
