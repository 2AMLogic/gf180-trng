---
record: 2026-08-01-ro-inv-05stage-stopped-leakage-39
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: sf bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: sf
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: dc
  tstop: n/a (operating-point analysis: no time axis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-inv-05stage-stopped-leakage-39/
  files:
    - sf_-40c_3.63v.spice  sha256:45f38d7ee96bbf784cbfe288757761358c0b90341e6179fe4358200bc0820607
    - sf_-40c_3.63v.log  sha256:3f7031c8821b3181b9aa79a61809fbc8f5bcc50aac835b13438175490f0f98b8
wall_time: 1.0s
---

## Result

- `i_leak_a`: 1.914584e-11
- `p_idle_w`: 6.949939e-11
- `v_n1`: 3.63
- `v_n2`: 5.400624e-09
- `v_n3`: 3.63
- `v_n4`: 5.400624e-09
- `v_n5`: 3.63
- `v_en`: 0

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-stopped-leakage --corners sf --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (sf / 3.63 V / -40 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
