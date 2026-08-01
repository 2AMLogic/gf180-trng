---
record: 2026-08-01-device-leakage-03v3-02
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
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
  path: sim/records/raw/2026-08-01-device-leakage-03v3-02/
  files:
    - tt_-40c_3.30v.spice  sha256:ff6ecb4763b9809f35a052f9689ee87df724ce6a8c745bc8e24861d2442b34ee
    - tt_-40c_3.30v.log  sha256:7876cdca10a26d3e0a21338392f2296b9b6f9cf43210bf3e7b13b5c63469927e
wall_time: 1.0s
---

## Result

- `ioff_nfet_a`: 3.324532e-12
- `ioff_pfet_a`: 3.908085e-12
- `ioff_nfet_a_per_um`: 3.324532e-13
- `ioff_pfet_a_per_um`: 3.908085e-13

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py device-leakage-03v3 --corners tt --temps -40 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / -40 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
