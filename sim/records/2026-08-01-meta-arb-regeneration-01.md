---
record: 2026-08-01-meta-arb-regeneration-01
date: 2026-08-01T16:21:58Z
status: valid

testbench:
  path: sim/tb/meta-arb-regeneration/tb_meta_arb_regeneration.sp
  sha: 367cab1eadbd7585365eb8b4db14df1543984df8
netlist:
  path: design/meta_arb.spice
  sha: bc2170a0476e46a0b8c29cdf62254799cae874b7
repo_commit: 762a90e86ec15db2231dd3dec8748ee7adec8fd2-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran
  tstop: 9n
  tstep: 0.5p (print step; also caps ngspice's internal tmax)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-meta-arb-regeneration-01/
  files:
    - ff_-40c_3.63v.spice  sha256:5590d1a15eb1934dfcf3616707be00ee1fb57de2a3e3972a3524afd03c83bfca
    - ff_-40c_3.63v.log  sha256:8d48ca2db116a12288f9848df79c650d45b355223d1bc8c0f646b891c650597f
wall_time: 2.2m
---

## Result

- `t_res_100p_s`: 2.994500e-11
- `t_res_10p_s`: 2.943700e-11
- `t_res_1p_s`: 3.086700e-11
- `t_res_100f_s`: 3.142800e-11
- `t_res_10f_s`: 3.149400e-11
- `t_res_1f_s`: 3.150100e-11
- `tau_100p_10p_s`: -2.206216e-13
- `tau_10p_1p_s`: 6.210411e-13
- `tau_1p_100f_s`: 2.436392e-13
- `tau_100f_10f_s`: 2.866344e-14
- `tau_10f_1f_s`: 3.040061e-15
- `v_q0_bal_v`: 2.485559e-06
- `v_qn0_bal_v`: 3.62994
- `v_diff_bal_v`: 3.62994

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py meta-arb-regeneration --corners ff --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist meta_arb.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
