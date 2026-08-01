---
record: 2026-08-01-ro-inv-05stage-stopped-leakage-14
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
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-08-01-ro-inv-05stage-stopped-leakage-14/
  files:
    - ff_27c_3.30v.spice  sha256:fe5be870ae4ec64378bd15cbfb37c37764310ec868302f94dbd87d4ea98dccd3
    - ff_27c_3.30v.log  sha256:5ea04a6955cdc9b62737b982a4740321e66519aa4b5d6e9525c2ab492974d0b0
wall_time: 0.6s
---

## Result

- `i_leak_a`: 7.087423e-11
- `p_idle_w`: 2.338849e-10
- `v_n1`: 3.3
- `v_n2`: 5.718157e-09
- `v_n3`: 3.3
- `v_n4`: 5.718156e-09
- `v_n5`: 3.3
- `v_en`: 0

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-stopped-leakage --corners ff --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.30 V / 27 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
