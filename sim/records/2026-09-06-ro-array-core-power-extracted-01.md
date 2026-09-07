---
record: 2026-09-06-ro-array-core-power-extracted-01
date: 2026-09-06T22:45:50Z
status: valid
level: extracted

testbench:
  path: sim/tb/ro-array-core-power-extracted/tb_ro_array_core_power_extracted.sp
  sha: 02b4d7a80c5c0546075a9b9da200413938d08d0a
netlist:
  path: layout/pex/ro_array_core.extracted.spice
  sha: 5a3aefd5e03c44c66f87213e6491332cd6650d60
repo_commit: 01b6c4d060ddff949cba90c49762d7d9059c431a-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: Linux-7.0.0-1010-aws-x86_64-with-glibc2.39

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran
  tstop: 50n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-09-06-ro-array-core-power-extracted-01/
  files:
    - ff_-40c_3.63v.spice  sha256:22f4a4cbfb47da891cd8ac18a4ad9093bf1a35517dd852bf218569a3cbfc2e68
    - ff_-40c_3.63v.log  sha256:a2d74690174300f399e331d1f4625f91d744dc53ae45fb686c2faf67d34939d4
wall_time: 20.6s
---

## Result

- `period_r1`: 5.041499e-09
- `period_r2`: 4.765660e-09
- `f_r1`: 1.983537e+08
- `f_r2`: 2.098345e+08
- `i_r1_a`: -3.612418e-05
- `i_r2_a`: -3.814699e-05
- `i_tree_a`: -5.499156e-05
- `e_cycle_r1_j`: -6.610957e-13
- `c_eff_node_r1_f`: -4.560982e-15
- `ring_swing_v`: 3.75213
- `xo_swing_v`: 3.68062
- `i_total_a`: -1.292627e-04
- `p_rings_w`: -2.696044e-04
- `p_total_w`: -4.692237e-04
- `xo_trans_per_s`: 8.163764e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power-extracted --corners ff --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, device-level-parasitic-annotated (layout/pex/build.py); NOT a full assembled-ring/inter-region routing extraction -- see layout/pex/build.py's own module docstring and sim/characterization-post-layout-extracted.md for exactly what this does and does not capture.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for active power (ff/-40 C/3.63 V), per issue #17's acceptance criteria ('spec table confirmed at the worst corner post-layout'), not the full grid.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
