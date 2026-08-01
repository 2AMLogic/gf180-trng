---
record: 2026-08-01-device-leakage-03v3-04
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
  path: sim/records/raw/2026-08-01-device-leakage-03v3-04/
  files:
    - tt_27c_2.97v.spice  sha256:166d60c855509cc8c7f2e990fa76206069e4fe9f384530a46d9a55d35d8f25c3
    - tt_27c_2.97v.log  sha256:ef54d5db467367ea55fa1edd08ccff25a6c265bfe9f1b9a79aa5912b75a2366e
wall_time: 0.8s
---

## Result

- `ioff_nfet_a`: 9.672288e-12
- `ioff_pfet_a`: 3.190483e-12
- `ioff_nfet_a_per_um`: 9.672288e-13
- `ioff_pfet_a_per_um`: 3.190483e-13

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py device-leakage-03v3 --corners tt --temps 27 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / 27 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
