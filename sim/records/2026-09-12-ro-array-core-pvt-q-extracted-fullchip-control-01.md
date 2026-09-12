---
record: 2026-09-12-ro-array-core-pvt-q-extracted-fullchip-control-01
date: 2026-09-12T07:57:55Z
status: valid

testbench:
  path: sim/tb/ro-array-core-pvt-q-extracted-fullchip-control/tb_ro_array_core_pvt_q_extracted_fullchip_control.sp
  sha: 48031ab7ba0d1e31c3df4d9bb6dc6ef3b79a475b
netlist:
  path: layout/pex/sampler_core.routed.extracted.spice
  sha: 4bf8c65adc37dad04d75c4641f81e4bfbb09ee4d
repo_commit: f03b78efa77b0bf73b7ae3c144fd936b00d78c68-dirty

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
  tstep: 5p (print step; it also caps ngspice's own solver step, same convention as the routing-level family)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-09-12-ro-array-core-pvt-q-extracted-fullchip-control-01/
  files:
    - ss_125c_3.63v.spice  sha256:d382a798a67f97c6080ece89fce2a5f07f8de129654d70f70b8d4be18d3baa3a
    - ss_125c_3.63v.log  sha256:db86758091fed9abc4f9c4788167a7e73ff8b3c5f408c2399f637640f38871fb
wall_time: 4.0m
---

## Result

- `period_r1`: 1.778767e-08
- `period_r2`: 1.666732e-08
- `f_r1`: 5.621871e+07
- `f_r2`: 5.999765e+07
- `i_r1_a`: -1.346459e-05
- `i_r2_a`: -1.430090e-05
- `i_tree_a`: -6.580831e-05
- `e_cycle_r1_j`: -8.693987e-13
- `c_eff_node_r1_f`: -5.998091e-15
- `ring_swing_v`: 3.69664
- `xo_swing_v`: 3.65785
- `i_total_a`: -9.357381e-05
- `p_rings_w`: -1.007887e-04
- `p_total_w`: -3.396729e-04
- `xo_trans_per_s`: 2.324327e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-pvt-q-extracted-fullchip-control --corners ss --temps 125 --supply 3.63 --supply-tol 0 --timeout 1800 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.routed.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- ZERO-DELTA CONTROL for sim/tb/ro-array-core-pvt-q-extracted-fullchip/: this deck is byte-identical to that one except for its own header comment and the DUT subcircuit name (sampler_core_routed_extracted here, sampler_core_fullchip_extracted there), so the difference between this record and its -extracted-fullchip sibling at the same PVT point is EXACTLY what layout/pex/build.py's full-chip composition adds (DR-0025's ro1/ro2 inter-region trunk delta, plus the four disclosed driver-side-only output-load capacitors) and nothing else. It exists because the pre-existing -extracted-routed record of this family is composed from ro_array_core's topology, not sampler_core's, so it is NOT a valid subtraction baseline for the inter-region delta on its own -- see sim/characterization-post-layout-extracted.md section 8.
- Carries NO inter-region parasitic at all (that is the point of a control): the DUT is layout/pex/sampler_core.routed.extracted.spice, the same intra-region routing-level composition issue #217 recorded, per DR-0024.
- clk/rst_n are tied STATIC (clk=0, rst_n=vdd_val) rather than toggled -- this testbench measures the ring array's own oscillation, not sampler activity, and a static tie avoids adding unrelated switching current. Consequence: p_total_w now includes the four sampler_dff instances' own static bias current on the vdd rail (this DUT's vdd rail is the fully assembled combiner_sampler block), a disclosed SCOPE BROADENING relative to ro-array-core-pvt-q-extracted-routed's own rings+XOR-only p_total_w -- not directly comparable without accounting for that difference.
- Scoped to the single worst (minimum-Q) corner (ss/+125 C/3.63 V), the same point issues #17/#217's own records used -- not the full 27-point grid.
- fs/sf process corners are NOT covered, per DR-0006's ratified reduced process axis.
- Deterministic (mismatch-free, noiseless) transient: one nominal device draw at this PVT point. Device mismatch is not exercised here.
- clk/rst_n arrival is still driven from an ideal, zero-impedance source at combiner_sampler's own pins (they are tied off entirely in this testbench) -- this record says nothing about clock-tree arrival at the sampler, per DR-0025.
- The swing window (200-295 ns) and the 2nd-to-6th rising-edge measurement window are fixed in simulated time, not in ring periods, matching the routing-level family's own convention.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
