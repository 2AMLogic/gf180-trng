---
record: 2026-08-01-device-leakage-03v3-31
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
  temperature: 27

analysis:
  type: dc
  tstop: n/a (operating point; single DC bias solution, no sweep)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-device-leakage-03v3-31/
  files:
    - fs_27c_2.97v.spice  sha256:a963b930b34b390a9eaf241590652f9f93d283d88fe74eeb999e08c9a5b92d3f
    - fs_27c_2.97v.log  sha256:009b2b312814935694a54c1bf486f3ea9682b547d6724cdb772090717ab10c20
wall_time: 1.1s
---

## Result

- `ioff_nfet_a`: 6.560647e-11
- `ioff_pfet_a`: 3.097587e-12
- `ioff_nfet_a_per_um`: 6.560647e-12
- `ioff_pfet_a_per_um`: 3.097587e-13

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py device-leakage-03v3 --corners fs --temps 27 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (fs / 2.97 V / 27 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
