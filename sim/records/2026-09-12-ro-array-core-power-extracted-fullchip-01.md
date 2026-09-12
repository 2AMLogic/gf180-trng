---
record: 2026-09-12-ro-array-core-power-extracted-fullchip-01
date: 2026-09-12T08:26:18Z
status: valid

testbench:
  path: sim/tb/ro-array-core-power-extracted-fullchip/tb_ro_array_core_power_extracted_fullchip.sp
  sha: b9b2514475e95b5fe0fea92da6ea6ce823d9328f
netlist:
  path: layout/pex/sampler_core.fullchip.extracted.spice
  sha: 9c992f581fb2fb86afa46685aded83ca58413428
repo_commit: f03b78efa77b0bf73b7ae3c144fd936b00d78c68-dirty

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
  path: sim/records/raw/2026-09-12-ro-array-core-power-extracted-fullchip-01/
  files:
    - ff_-40c_3.63v.spice  sha256:8fdde94cd02957e5b34099b579567786f21d2ee965484a7389950fa65b9ff324
    - ff_-40c_3.63v.log  sha256:f4e42d08b617a78352f8def4de23f1591e6d57a38f624d44f01d772524ad772a
wall_time: 3.4m
---

## Result

- `period_r1`: 7.957853e-09
- `period_r2`: 7.075085e-09
- `f_r1`: 1.256620e+08
- `f_r2`: 1.413411e+08
- `i_r1_a`: -3.609077e-05
- `i_r2_a`: -3.756148e-05
- `i_tree_a`: -1.923190e-04
- `e_cycle_r1_j`: -1.042554e-12
- `c_eff_node_r1_f`: -7.192712e-15
- `ring_swing_v`: 3.61657
- `xo_swing_v`: 3.63399
- `i_total_a`: -2.659712e-04
- `p_rings_w`: -2.673577e-04
- `p_total_w`: -9.654755e-04
- `xo_trans_per_s`: 5.340062e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power-extracted-fullchip --corners ff --temps -40 --supply 3.63 --supply-tol 0 --timeout 1800 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.fullchip.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, FULL-CHIP-DELTA-annotated for the ro1/ro2 inter-region trunks ONLY (layout/pex/build.py); every other inter-region trunk is unpriced by this composition -- see DR-0025 and layout/pex/build.py's own module docstring for the full accounting.
- CELL-INSTANCE GRANULARITY, NOT TRANSISTOR LEVEL (DR-0025): the inter-region parasitics this DUT carries were measured by a full-chip `klt extract --parasitics` run over layout/floorplan/trng_floorplan.gds in which every one of digital's ~2500 gf180mcu_fd_sc_mcu9t5v0__* standard-cell instances was abstracted as an opaque black box -- the same granularity the composed LVS already uses. No number in this record is evidence about any standard cell's own devices, and digital is not instantiated in this deck at all.
- clk/rst_n are tied STATIC (clk=0, rst_n=vdd_val) rather than toggled. Consequence: p_total_w now includes the four sampler_dff instances' own static bias current on the vdd rail (this DUT's vdd rail is the fully assembled combiner_sampler block), a disclosed SCOPE BROADENING relative to ro-array-core-power-extracted-routed's own rings+XOR-only p_total_w -- not directly comparable without accounting for that difference.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for active power (ff/-40 C/3.63 V), the same point issues #17/#217's own records used -- not the full grid.
- clk/rst_n arrival is still driven from an ideal, zero-impedance source at combiner_sampler's own pins (tied off entirely in this testbench) -- this record says nothing about clock-tree arrival at the sampler, per DR-0025.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
