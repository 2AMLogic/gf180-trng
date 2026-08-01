---
record: 2026-08-01-ro-inv-05stage-stopped-leakage-22
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 27

analysis:
  type: dc
  tstop: n/a (operating-point analysis: no time axis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-inv-05stage-stopped-leakage-22/
  files:
    - ss_27c_2.97v.spice  sha256:bc7092d8d409121e335395dca96b6758077b64b3ca5d70fadd63cd4c07548364
    - ss_27c_2.97v.log  sha256:910d83b90688664d0ba04360d8e7d4e2807f62a8b62701acbffe1406548f3474
wall_time: 1.0s
---

## Result

- `i_leak_a`: 1.505195e-11
- `p_idle_w`: 4.470429e-11
- `v_n1`: 2.97
- `v_n2`: 5.512049e-09
- `v_n3`: 2.97
- `v_n4`: 5.512050e-09
- `v_n5`: 2.97
- `v_en`: 0

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-stopped-leakage --corners ss --temps 27 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 27 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
