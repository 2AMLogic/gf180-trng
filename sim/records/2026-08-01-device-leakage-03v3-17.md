---
record: 2026-08-01-device-leakage-03v3-17
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-08-01-device-leakage-03v3-17/
  files:
    - ff_125c_3.30v.spice  sha256:4da3db51cabba27c537be23ad6d4eb91112a36514fa9df4833d26328cd912589
    - ff_125c_3.30v.log  sha256:85a975be0e1e1f7643d222c8a92113ea6dfd00635170cd550f4d3e38078286ca
wall_time: 1.3s
---

## Result

- `ioff_nfet_a`: 2.351044e-08
- `ioff_pfet_a`: 9.236694e-10
- `ioff_nfet_a_per_um`: 2.351044e-09
- `ioff_pfet_a_per_um`: 9.236694e-11

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py device-leakage-03v3 --corners ff --temps 125 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.30 V / 125 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
