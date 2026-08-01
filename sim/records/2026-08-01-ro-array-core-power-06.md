---
record: 2026-08-01-ro-array-core-power-06
date: 2026-08-01T12:46:55Z
status: valid

testbench:
  path: sim/tb/ro-array-core-power/tb_ro_array_core_power.sp
  sha: c542a00f2d0da65817f577351bef11876946a32a
netlist:
  path: design/ro_array_core.spice
  sha: 339e858e0010f1ca26412919af47621d40dedf93
repo_commit: c953bc4d235908b512d8c15b5a2e8b4a5bb6b5ec-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /home/ubuntu/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-42 : Circuit level simulation program"
  platform: Linux-7.0.0-1009-aws-x86_64-with-glibc2.39

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
  path: sim/records/raw/2026-08-01-ro-array-core-power-06/
  files:
    - tt_27c_3.30v.spice  sha256:2585238d30b569a3c2118512dc5fce02f495d0cb4f6bac48e9aa9817bd6298fd
    - tt_27c_3.30v.log  sha256:2f3cb589a094df9b0a9b3b2a5fa4396a19a9cb0e7ee991e9c2352903d0cf7fb0
wall_time: 11.5m
---

## Result

- `period_r1`: 7.136545e-09
- `period_r2`: 6.718008e-09
- `f_r1`: 1.401238e+08
- `f_r2`: 1.488537e+08
- `i_r1_a`: -1.868089e-05
- `i_r2_a`: -1.995349e-05
- `i_tree_a`: -1.953049e-05
- `e_cycle_r1_j`: -4.399461e-13
- `c_eff_node_r1_f`: -3.672645e-15
- `ring_swing_v`: 3.3832
- `xo_swing_v`: 3.34734
- `i_total_a`: -5.816487e-05
- `p_rings_w`: -1.274935e-04
- `p_total_w`: -1.919441e-04
- `xo_trans_per_s`: 5.779550e+08

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
