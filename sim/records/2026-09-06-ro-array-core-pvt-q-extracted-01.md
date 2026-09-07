---
record: 2026-09-06-ro-array-core-pvt-q-extracted-01
date: 2026-09-06T22:36:28Z
status: valid
level: extracted

testbench:
  path: sim/tb/ro-array-core-pvt-q-extracted/tb_ro_array_core_pvt_q_extracted.sp
  sha: 889d54d300092d341334ae6fd9b923b4139ed07b
netlist:
  path: layout/pex/ro_array_core.extracted.spice
  sha: 5a3aefd5e03c44c66f87213e6491332cd6650d60
repo_commit: 01b6c4d060ddff949cba90c49762d7d9059c431a-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: Linux-7.0.0-1010-aws-x86_64-with-glibc2.39

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: tran
  tstop: 300n
  tstep: 5p (print step; it also caps ngspice's own solver step, which is the reason it is stated rather than left at the default)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-09-06-ro-array-core-pvt-q-extracted-01/
  files:
    - ss_125c_3.63v.spice  sha256:9e013d841ef9499835ddb009ece1a6ea38b09a93ee253b3f3946abcca46e6dd4
    - ss_125c_3.63v.log  sha256:b8028874562c11340ea93ac5421cc69be8eda919c8f47ab5f57f10f4de8c7acf
wall_time: 29.9s
---

## Result

- `period_r1`: 1.234873e-08
- `period_r2`: 1.156055e-08
- `f_r1`: 8.097999e+07
- `f_r2`: 8.650109e+07
- `i_r1_a`: -1.417002e-05
- `i_r2_a`: -1.512144e-05
- `i_tree_a`: -2.024719e-05
- `e_cycle_r1_j`: -6.351838e-13
- `c_eff_node_r1_f`: -4.382213e-15
- `ring_swing_v`: 3.75156
- `xo_swing_v`: 3.71523
- `i_total_a`: -4.953865e-05
- `p_rings_w`: -1.063280e-04
- `p_total_w`: -1.798253e-04
- `xo_trans_per_s`: 3.349622e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-pvt-q-extracted --corners ss --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, device-level-parasitic-annotated (layout/pex/build.py); NOT a full assembled-ring/inter-region routing extraction -- see layout/pex/build.py's own module docstring and sim/characterization-post-layout-extracted.md for exactly what this does and does not capture.
- Scoped to the single worst (minimum-Q) corner sim/characterization-worst-corner-and-mc-mismatch.md's full 27-point pre-layout grid identified (ss/+125 C/3.63 V), per issue #17's acceptance criteria ('spec table confirmed at the worst corner post-layout'), not the full grid -- a full post-layout 27-point re-run was not run.
- fs/sf process corners are NOT covered, per DR-0006's ratified reduced process axis.
- Deterministic (mismatch-free, noiseless) transient: one nominal device draw at this PVT point. Device mismatch is sim/tb/ro-array-core-mc-freq-extracted/'s subject; nothing here measures it.
- The swing window (200-295 ns) and the 2nd-to-6th rising-edge measurement window are fixed in simulated time, not in ring periods, matching the pre-layout family's own convention (sim/tb/ro-array-core-pvt-q/tb.json).

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
