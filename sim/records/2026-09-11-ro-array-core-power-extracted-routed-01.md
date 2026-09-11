---
record: 2026-09-11-ro-array-core-power-extracted-routed-01
date: 2026-09-11T06:37:01Z
status: valid

testbench:
  path: sim/tb/ro-array-core-power-extracted-routed/tb_ro_array_core_power_extracted_routed.sp
  sha: 7b861a6cc5986e3ffe04b11e3cff0762acdfe4c4
netlist:
  path: layout/pex/ro_array_core.routed.extracted.spice
  sha: e93c6e814579300acca643741bc1f2acffe87817
repo_commit: 383df4f16948d3118bbb9b3a4614e274b5875c9f-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /Users/rwalters/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6.2-arm64-arm-64bit-Mach-O

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
  path: sim/records/raw/2026-09-11-ro-array-core-power-extracted-routed-01/
  files:
    - ff_-40c_3.63v.spice  sha256:9343847c4eb0268a60199fe9f841ae9f4a82744b301c7256ec608c0cae0ebfbc
    - ff_-40c_3.63v.log  sha256:6c1ef1a992d412638e55ef05511d1c5af961150e92ae5397ac3d7af6a6d3819b
wall_time: 35.3s
---

## Result

- `period_r1`: 7.029758e-09
- `period_r2`: 6.718483e-09
- `f_r1`: 1.422524e+08
- `f_r2`: 1.488431e+08
- `i_r1_a`: -3.641821e-05
- `i_r2_a`: -3.801713e-05
- `i_tree_a`: -6.053293e-05
- `e_cycle_r1_j`: -9.293205e-13
- `c_eff_node_r1_f`: -6.411499e-15
- `ring_swing_v`: 3.73394
- `xo_swing_v`: 3.66065
- `i_total_a`: -1.349683e-04
- `p_rings_w`: -2.702003e-04
- `p_total_w`: -4.899348e-04
- `xo_trans_per_s`: 5.821911e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power-extracted-routed --corners ff --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.routed.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, ROUTING-level-parasitic-annotated for both rings (layout/pex/build.py); the buffer/XOR stage remains device-level (leaf-cell) -- see layout/pex/build.py's own module docstring, 'Two composed drop-ins, different scope', and sim/characterization-post-layout-extracted.md's 2026-09-11 delta section.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for active power (ff/-40 C/3.63 V), the same point issue #17's own leaf-level record used -- not the full grid.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
