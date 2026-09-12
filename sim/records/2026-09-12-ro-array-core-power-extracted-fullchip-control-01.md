---
record: 2026-09-12-ro-array-core-power-extracted-fullchip-control-01
date: 2026-09-12T08:22:52Z
status: valid

testbench:
  path: sim/tb/ro-array-core-power-extracted-fullchip-control/tb_ro_array_core_power_extracted_fullchip_control.sp
  sha: c10ba6b1267ec1d6bac2a22e58584d4e6d71b9bd
netlist:
  path: layout/pex/sampler_core.routed.extracted.spice
  sha: 4bf8c65adc37dad04d75c4641f81e4bfbb09ee4d
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
  path: sim/records/raw/2026-09-12-ro-array-core-power-extracted-fullchip-control-01/
  files:
    - ff_-40c_3.63v.spice  sha256:8a6402f6c99ffa5a9aae6e63104a882e3f1a137f9991fa646a32ce4f62642759
    - ff_-40c_3.63v.log  sha256:d0dd0ad0d3089bfac480fc60ada394bbca55dc48808ddcb4c80189533d3e4ec0
wall_time: 3.4m
---

## Result

- `period_r1`: 7.174830e-09
- `period_r2`: 6.774383e-09
- `f_r1`: 1.393761e+08
- `f_r2`: 1.476149e+08
- `i_r1_a`: -3.531905e-05
- `i_r2_a`: -3.728354e-05
- `i_tree_a`: -1.912598e-04
- `e_cycle_r1_j`: -9.198716e-13
- `c_eff_node_r1_f`: -6.346310e-15
- `ring_swing_v`: 3.65183
- `xo_swing_v`: 3.63436
- `i_total_a`: -2.638624e-04
- `p_rings_w`: -2.635474e-04
- `p_total_w`: -9.578206e-04
- `xo_trans_per_s`: 5.739821e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power-extracted-fullchip-control --corners ff --temps -40 --supply 3.63 --supply-tol 0 --timeout 1800 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.routed.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- ZERO-DELTA CONTROL for sim/tb/ro-array-core-power-extracted-fullchip/: this deck is byte-identical to that one except for its own header comment and the DUT subcircuit name (sampler_core_routed_extracted here, sampler_core_fullchip_extracted there), so the difference between this record and its -extracted-fullchip sibling at the same PVT point is EXACTLY what layout/pex/build.py's full-chip composition adds (DR-0025's ro1/ro2 inter-region trunk delta, plus the four disclosed driver-side-only output-load capacitors) and nothing else. It exists because the pre-existing -extracted-routed record of this family is composed from ro_array_core's topology, not sampler_core's, so it is NOT a valid subtraction baseline for the inter-region delta on its own -- see sim/characterization-post-layout-extracted.md section 8.
- Carries NO inter-region parasitic at all (that is the point of a control): the DUT is layout/pex/sampler_core.routed.extracted.spice, the same intra-region routing-level composition issue #217 recorded, per DR-0024.
- clk/rst_n are tied STATIC (clk=0, rst_n=vdd_val) rather than toggled. Consequence: p_total_w now includes the four sampler_dff instances' own static bias current on the vdd rail (this DUT's vdd rail is the fully assembled combiner_sampler block), a disclosed SCOPE BROADENING relative to ro-array-core-power-extracted-routed's own rings+XOR-only p_total_w -- not directly comparable without accounting for that difference.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for active power (ff/-40 C/3.63 V), the same point issues #17/#217's own records used -- not the full grid.
- clk/rst_n arrival is still driven from an ideal, zero-impedance source at combiner_sampler's own pins (tied off entirely in this testbench) -- this record says nothing about clock-tree arrival at the sampler, per DR-0025.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
