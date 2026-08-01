---
record: 2026-08-01-ro-meta-tap-skew-01
date: 2026-08-01T16:23:33Z
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
  tstop: 12n
  tstep: 0.2p (print step; also caps ngspice's internal tmax)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-meta-tap-skew-01/
  files:
    - ff_-40c_3.63v.spice  sha256:758520a980d4c0d7cd081c57520fca8f1db62c986d4ef25243e9cbbdece76608
    - ff_-40c_3.63v.log  sha256:31b647249d3d8b6c600c8583abffd33fde9efc38c7dad2c67369d461cb280ae2
wall_time: 12.0m
---

## Result

- `dt_005ff_s`: 7.380000e-13
- `dt_05ff_s`: 6.816000e-12
- `dt_1ff_s`: 1.345100e-11
- `dt_2ff_s`: 2.645200e-11
- `dt_per_ff_s`: 1.322600e-11
- `lin_2ff_over_1ff`: 1.96655
- `t_path_s`: 1.572200e-10
- `t_res_05ff_s`: 4.604000e-11
- `t_res_2ff_s`: 4.332800e-11
- `mo_final_v`: 3.63
- `i_tap_a`: -5.159040e-05
- `p_tap_w`: -1.872732e-04
- `e_period_j`: -3.902773e-13
- `f_drive_hz`: 4.798464e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-meta-tap-skew --corners ff --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_meta_tap.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
