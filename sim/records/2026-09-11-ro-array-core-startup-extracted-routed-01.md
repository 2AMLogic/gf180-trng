---
record: 2026-09-11-ro-array-core-startup-extracted-routed-01
date: 2026-09-11T06:39:51Z
status: valid

testbench:
  path: sim/tb/ro-array-core-startup-extracted-routed/tb_ro_array_core_startup_extracted_routed.sp
  sha: a6497ccb9fe43ddd6dea18221868a20319c06a5a
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
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: tran
  tstop: 280n
  tstep: 2p (print step; ngspice's own LTE sets the actual solver step). 2p resolves an edge crossing to well under a picosecond after `meas`'s linear interpolation. Window widened from the leaf-level family's 180n -- see the 'widened window' caveat below.
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-09-11-ro-array-core-startup-extracted-routed-01/
  files:
    - ss_125c_2.97v.spice  sha256:c510d48f0ddab2bf9eae3f7562b312efe35097b04d949bab79628e217124b047
    - ss_125c_2.97v.log  sha256:7e706ffde31d100b4eb6df5c0c07d01be8f38f2e55c0119b06cee59fe050db89
wall_time: 1.4m
---

## Result

- `en_assert_s`: 5.000000e-09
- `t1r1_s`: 2.757075e-08
- `t2r1_s`: 5.046588e-08
- `t3r1_s`: 7.335814e-08
- `t4r1_s`: 9.637666e-08
- `t5r1_s`: 1.194706e-07
- `t6r1_s`: 1.425835e-07
- `t7r1_s`: 1.657491e-07
- `t8r1_s`: 1.891422e-07
- `t9r1_s`: 2.124372e-07
- `t10r1_s`: 2.358680e-07
- `t1r2_s`: 2.627310e-08
- `t2r2_s`: 4.781653e-08
- `t3r2_s`: 6.943121e-08
- `t4r2_s`: 9.106856e-08
- `t5r2_s`: 1.127379e-07
- `t6r2_s`: 1.345034e-07
- `t7r2_s`: 1.564230e-07
- `t8r2_s`: 1.783975e-07
- `t9r2_s`: 2.003953e-07
- `t10r2_s`: 2.220459e-07
- `t1xo_s`: 2.693918e-08
- `t2xo_s`: 3.703893e-08
- `t3xo_s`: 4.848784e-08
- `t4xo_s`: 5.855826e-08
- `ring_swing_early_v`: 2.87339
- `ring_swing_late_v`: 2.95691
- `xo_swing_early_v`: 3.03496
- `xo_swing_late_v`: 3.0446
- `v_ro1_off_v`: 2.97
- `v_xo_off_v`: 1.310802e-07

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-startup-extracted-routed --corners ss --temps 125 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.routed.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, ROUTING-level-parasitic-annotated for both rings (layout/pex/build.py); the buffer/XOR stage remains device-level (leaf-cell) -- see layout/pex/build.py's own module docstring, 'Two composed drop-ins, different scope', and sim/characterization-post-layout-extracted.md's 2026-09-11 delta section.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for time-to-first-valid (ss/+125 C/2.97 V), the same point issue #17's own leaf-level record used -- not the full 27-point grid.
- Deterministic (noiseless) transient started from the operating point ngspice solves with en = 0, same as the leaf-level family -- no .ic kick used or needed (see the leaf-level testbench's own header for why).
- v(xdut.rn1)/v(xdut.rn2) address the SAME physical node (each ring's own output, before the per-ring buffer) as the leaf-level family -- `rn1`/`rn2` remain ro_array_core_routed_extracted's own internal net names between the ring instance and the buffer instance, unchanged by the routing-level composition (layout/pex/build.py's own `_ro_array_core_routed_subckt`).
- WIDENED MEASUREMENT WINDOW (180n -> 280n) relative to the leaf-level family: at this corner the routed ring's own real hand-routed inter-stage metal1/metal2/via1 parasitics slow oscillation enough that the leaf-level family's 180n budget no longer fits all ten rising edges -- a first attempt at the leaf-level family's own 180n tstop failed `meas ... t8r1` ('out of interval') outright, and the seven edges that DID resolve in that attempt showed a ~23.2 ns period, ~76% longer than the leaf-level family's own 13.2 ns at this same PVT point (sim/tb/ro-array-core-pvt-q-extracted/'s own steady-state figure). This is itself a real, reportable routing-parasitic effect, not a testbench artefact -- see sim/characterization-post-layout-extracted.md's 2026-09-11 delta section. The late swing window moved from 150-180n to 250-280n to stay inside the widened tstop, comfortably past the tenth edge (~236 ns) with margin; the early window (20-50n) is unchanged.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
