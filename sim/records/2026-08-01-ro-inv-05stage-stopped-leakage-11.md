---
record: 2026-08-01-ro-inv-05stage-stopped-leakage-11
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
  path: sim/records/raw/2026-08-01-ro-inv-05stage-stopped-leakage-11/
  files:
    - ff_-40c_3.30v.spice  sha256:e79d0380d613a73bb6cddbf13eeebebdf712bd25fcd2b0d25268c69845ba5344
    - ff_-40c_3.30v.log  sha256:435e50cd04f99eb0bbed058fbc3ff64affb190da3fdf10195ce131cf6c97c630
wall_time: 0.6s
---

## Result

- `i_leak_a`: 1.713795e-11
- `p_idle_w`: 5.655523e-11
- `v_n1`: 3.3
- `v_n2`: 4.236669e-09
- `v_n3`: 3.3
- `v_n4`: 4.236669e-09
- `v_n5`: 3.3
- `v_en`: 0

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-stopped-leakage --corners ff --temps -40 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.30 V / -40 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
