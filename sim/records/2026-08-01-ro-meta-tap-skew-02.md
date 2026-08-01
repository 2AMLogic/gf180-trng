---
record: 2026-08-01-ro-meta-tap-skew-02
date: 2026-08-01T16:35:39Z
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
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
  path: sim/records/raw/2026-08-01-ro-meta-tap-skew-02/
  files:
    - ss_-40c_3.63v.spice  sha256:3bc46a547579b4dc76131f94284234df701a9473347b9f5252f03dd8e2d22c0d
    - ss_-40c_3.63v.log  sha256:3e5eb15ee30f91bca8b15c3959e8ecc587ed25fdb818d0642d66a6289f94a2c4
wall_time: 9.7m
---

## Result

- `dt_005ff_s`: 1.036000e-12
- `dt_05ff_s`: 9.879000e-12
- `dt_1ff_s`: 1.950700e-11
- `dt_2ff_s`: 3.824600e-11
- `dt_per_ff_s`: 1.912300e-11
- `lin_2ff_over_1ff`: 1.96063
- `t_path_s`: 2.136860e-10
- `t_res_05ff_s`: 6.415000e-11
- `t_res_2ff_s`: 6.166600e-11
- `mo_final_v`: 3.63
- `i_tap_a`: -4.806069e-05
- `p_tap_w`: -1.744603e-04
- `e_period_j`: -3.635753e-13
- `f_drive_hz`: 4.798464e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-meta-tap-skew --corners ss --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_meta_tap.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
