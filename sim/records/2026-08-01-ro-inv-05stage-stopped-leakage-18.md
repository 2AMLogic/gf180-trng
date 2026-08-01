---
record: 2026-08-01-ro-inv-05stage-stopped-leakage-18
date: 2026-08-01T00:27:23Z
status: valid

testbench:
  path: sim/tb/ro-inv-05stage-stopped-leakage/tb_ro_inv_05stage_stopped.sp
  sha: ecb7c9eda686997addbb061ee366374a6efc21d6
netlist:
  path: sim/tb/ro-inv-05stage-stopped-leakage/tb_ro_inv_05stage_stopped.sp
  sha: ecb7c9eda686997addbb061ee366374a6efc21d6
repo_commit: f03dd6c3036d67bd4f2245b92bb7765e23396d55-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: dc
  tstop: n/a (operating-point analysis: no time axis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-inv-05stage-stopped-leakage-18/
  files:
    - ff_125c_3.63v.spice  sha256:dd9cb0887edde296d8db8c09d4a7844bc08bd8b29985ae19d65f674276a41fae
    - ff_125c_3.63v.log  sha256:3287824237043769de45c27543c72c989524035fcad44cda04936fb980900f11
wall_time: 1.0s
---

## Result

- `i_leak_a`: 1.047121e-08
- `p_idle_w`: 3.801048e-08
- `v_n1`: 3.62999
- `v_n2`: 4.735274e-07
- `v_n3`: 3.62999
- `v_n4`: 4.734666e-07
- `v_n5`: 3.62999
- `v_en`: 0

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-stopped-leakage --corners ff --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / 125 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
