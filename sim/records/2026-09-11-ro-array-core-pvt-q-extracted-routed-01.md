---
record: 2026-09-11-ro-array-core-pvt-q-extracted-routed-01
date: 2026-09-11T06:36:03Z
status: valid

testbench:
  path: sim/tb/ro-array-core-pvt-q-extracted-routed/tb_ro_array_core_pvt_q_extracted_routed.sp
  sha: 9689c8428b28cd498908d144a0d558bb103825ca
netlist:
  path: layout/pex/ro_array_core.routed.extracted.spice
  sha: e93c6e814579300acca643741bc1f2acffe87817
repo_commit: 383df4f16948d3118bbb9b3a4614e274b5875c9f-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /Users/rwalters/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6.2-arm64-arm-64bit-Mach-O

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
  path: sim/records/raw/2026-09-11-ro-array-core-pvt-q-extracted-routed-01/
  files:
    - ss_125c_3.63v.spice  sha256:8012f95d2e8958f3744fc2feaf54e9380a637a11a0d78f2f2f0146d161f70f99
    - ss_125c_3.63v.log  sha256:11c3b84bf042e54a818e6947d8abcc95b44b4c3c07653b63cc9d4b1280ae6d5b
wall_time: 54.2s
---

## Result

- `period_r1`: 1.742577e-08
- `period_r2`: 1.646151e-08
- `f_r1`: 5.738627e+07
- `f_r2`: 6.074777e+07
- `i_r1_a`: -1.387592e-05
- `i_r2_a`: -1.463571e-05
- `i_tree_a`: -1.999853e-05
- `e_cycle_r1_j`: -8.777289e-13
- `c_eff_node_r1_f`: -6.055562e-15
- `ring_swing_v`: 3.66814
- `xo_swing_v`: 3.70166
- `i_total_a`: -4.851016e-05
- `p_rings_w`: -1.034972e-04
- `p_total_w`: -1.760919e-04
- `xo_trans_per_s`: 2.362681e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-pvt-q-extracted-routed --corners ss --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.routed.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, ROUTING-level-parasitic-annotated for both rings (layout/pex/build.py); the buffer/XOR stage remains device-level (leaf-cell) -- see layout/pex/build.py's own module docstring, 'Two composed drop-ins, different scope', and sim/characterization-post-layout-extracted.md's 2026-09-11 delta section for exactly what this does and does not capture.
- Scoped to the single worst (minimum-Q) corner sim/characterization-worst-corner-and-mc-mismatch.md's full 27-point pre-layout grid identified (ss/+125 C/3.63 V), the same point issue #17's own leaf-level record used -- not the full grid.
- fs/sf process corners are NOT covered, per DR-0006's ratified reduced process axis.
- Deterministic (mismatch-free, noiseless) transient: one nominal device draw at this PVT point. Device mismatch is sim/tb/ro-array-core-mc-freq-extracted-routed/'s subject; nothing here measures it.
- The swing window (200-295 ns) and the 2nd-to-6th rising-edge measurement window are fixed in simulated time, not in ring periods, matching the leaf-level family's own convention.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
