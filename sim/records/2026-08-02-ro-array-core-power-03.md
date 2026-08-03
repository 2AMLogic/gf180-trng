---
record: 2026-08-02-ro-array-core-power-03
date: 2026-08-02T23:56:52Z
status: valid

testbench:
  path: sim/tb/ro-array-core-power/tb_ro_array_core_power.sp
  sha: 07f62df20bff89c6c21be7d68f078fe23c717c6b
netlist:
  path: design/ro_array_core.spice
  sha: fd0aa75500320b36f980126377e3d07c71c0e6b1
repo_commit: fdbc373e5ede42fcecd66f63ba5e9b7bb911ba59-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran
  tstop: 50n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-02-ro-array-core-power-03/
  files:
    - tt_27c_3.30v.spice  sha256:6ad64b0305d4d726ce5b55364641cf2ef825029961798318b4b3cb453eb2bb93
    - tt_27c_3.30v.log  sha256:b64e6613b82f2a68b52e0c1a7f03db878679123560b5995231cde10f4094a42b
wall_time: 37.7s
---

## Result

- `period_r1`: 6.677432e-09
- `period_r2`: 6.240492e-09
- `f_r1`: 1.497582e+08
- `f_r2`: 1.602438e+08
- `i_r1_a`: -1.896104e-05
- `i_r2_a`: -2.022904e-05
- `i_tree_a`: -1.662699e-05
- `e_cycle_r1_j`: -4.178165e-13
- `c_eff_node_r1_f`: -3.487908e-15
- `ring_swing_v`: 3.45206
- `xo_swing_v`: 3.42216
- `i_total_a`: -5.581708e-05
- `p_rings_w`: -1.293273e-04
- `p_total_w`: -1.841964e-04
- `xo_trans_per_s`: 6.200038e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power --corners tt --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
