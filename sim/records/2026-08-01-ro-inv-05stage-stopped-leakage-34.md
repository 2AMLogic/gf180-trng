---
record: 2026-08-01-ro-inv-05stage-stopped-leakage-34
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
  tstop: n/a (operating-point analysis: no time axis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-inv-05stage-stopped-leakage-34/
  files:
    - fs_125c_2.97v.spice  sha256:ea70563f0b1b5560e388183d974ae8c40a5ab8f84dbf00b4fe9072eb66bf67af
    - fs_125c_2.97v.log  sha256:12ba43fe42202376e28c88ce962e8679a7a00d8d71b7481efbf9ee17af919a9c
wall_time: 0.7s
---

## Result

- `i_leak_a`: 3.391370e-09
- `p_idle_w`: 1.007237e-08
- `v_n1`: 2.96999
- `v_n2`: 1.162632e-08
- `v_n3`: 2.97
- `v_n4`: 1.162597e-08
- `v_n5`: 2.97
- `v_en`: 0

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-stopped-leakage --corners fs --temps 125 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (fs / 2.97 V / 125 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
