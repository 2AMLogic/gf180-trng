---
record: 2026-08-01-ro-inv-05stage-stopped-leakage-07
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
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
  path: sim/records/raw/2026-08-01-ro-inv-05stage-stopped-leakage-07/
  files:
    - tt_125c_2.97v.spice  sha256:a64a8790a82ff6871fa2ed60470a440eabad41b7fac3460505019b73bbdce98d
    - tt_125c_2.97v.log  sha256:be1d6ae6d335493b1f98e05d08507f840fad7c7ddf0f6e4976cd8689883f4771
wall_time: 0.9s
---

## Result

- `i_leak_a`: 6.566319e-10
- `p_idle_w`: 1.950197e-09
- `v_n1`: 2.97
- `v_n2`: 4.407955e-08
- `v_n3`: 2.97
- `v_n4`: 4.407916e-08
- `v_n5`: 2.97
- `v_en`: 0

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-stopped-leakage --corners tt --temps 125 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / 125 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
