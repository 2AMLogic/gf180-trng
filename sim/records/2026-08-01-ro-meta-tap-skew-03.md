---
record: 2026-08-01-ro-meta-tap-skew-03
date: 2026-08-01T16:45:24Z
status: valid

testbench:
  path: sim/tb/ro-meta-tap-skew/tb_ro_meta_tap_skew.sp
  sha: 87fd0e7593e5f88bd969d1957c799779284e6b79
netlist:
  path: design/ro_meta_tap.spice
  sha: dacc2368b27dc6ad20dd78572a75c68176c47190
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
  tstop: 12n
  tstep: 0.2p (print step; also caps ngspice's internal tmax)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-meta-tap-skew-03/
  files:
    - tt_27c_3.30v.spice  sha256:ef317619c6503cfd1d0e9d2f33f881c444bcd4b9e8e57543db9def34cd837fa6
    - tt_27c_3.30v.log  sha256:b5741f41ddb6ed36524948623b49c0a7d195c003d6b3a6e0069b8f8df9ce1dfc
wall_time: 8.8m
---

## Result

- `dt_005ff_s`: 1.002000e-12
- `dt_05ff_s`: 9.443000e-12
- `dt_1ff_s`: 1.860700e-11
- `dt_2ff_s`: 3.642700e-11
- `dt_per_ff_s`: 1.821350e-11
- `lin_2ff_over_1ff`: 1.9577
- `t_path_s`: 2.142160e-10
- `t_res_05ff_s`: 6.769200e-11
- `t_res_2ff_s`: 6.360000e-11
- `mo_final_v`: 3.3
- `i_tap_a`: -4.400024e-05
- `p_tap_w`: -1.452008e-04
- `e_period_j`: -3.025984e-13
- `f_drive_hz`: 4.798464e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-meta-tap-skew --corners tt --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_meta_tap.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
