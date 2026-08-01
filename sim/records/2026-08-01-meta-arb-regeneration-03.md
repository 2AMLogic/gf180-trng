---
record: 2026-08-01-meta-arb-regeneration-03
date: 2026-08-01T16:26:23Z
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
  tstop: 9n
  tstep: 0.5p (print step; also caps ngspice's internal tmax)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-meta-arb-regeneration-03/
  files:
    - tt_27c_3.30v.spice  sha256:0e8b7bd38ca2d783e1213e4d5c6190cdf126234ac20bb74ca2f3648699dba539
    - tt_27c_3.30v.log  sha256:4de94603f52ea0b1b2468e4091100e72aa7ed4ba3d367ec06f9b9f197599306e
wall_time: 2.0m
---

## Result

- `t_res_100p_s`: 4.241500e-11
- `t_res_10p_s`: 4.190700e-11
- `t_res_1p_s`: 4.439800e-11
- `t_res_100f_s`: 4.506300e-11
- `t_res_10f_s`: 4.513700e-11
- `t_res_1f_s`: 4.514500e-11
- `tau_100p_10p_s`: -2.206216e-13
- `tau_10p_1p_s`: 1.081828e-12
- `tau_1p_100f_s`: 2.888058e-13
- `tau_100f_10f_s`: 3.213779e-14
- `tau_10f_1f_s`: 3.474356e-15
- `v_q0_bal_v`: 3.29987
- `v_qn0_bal_v`: 6.292731e-06
- `v_diff_bal_v`: 3.29986

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py meta-arb-regeneration --corners tt --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist meta_arb.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
