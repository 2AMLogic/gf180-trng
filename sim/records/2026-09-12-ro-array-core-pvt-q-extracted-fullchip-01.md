---
record: 2026-09-12-ro-array-core-pvt-q-extracted-fullchip-01
date: 2026-09-12T08:01:57Z
status: valid

testbench:
  path: sim/tb/ro-array-core-pvt-q-extracted-fullchip/tb_ro_array_core_pvt_q_extracted_fullchip.sp
  sha: 7e8cb785892082bd9f387042a82f40a22dd0e062
netlist:
  path: layout/pex/sampler_core.fullchip.extracted.spice
  sha: 9c992f581fb2fb86afa46685aded83ca58413428
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
  path: sim/records/raw/2026-09-12-ro-array-core-pvt-q-extracted-fullchip-01/
  files:
    - ss_125c_3.63v.spice  sha256:876a02b048b67fe6b658c32b53e58d12c5018213714ab1c4074e437979ffefc0
    - ss_125c_3.63v.log  sha256:18527bd3807beb1e2a67eb4500f851211e9848cace83bd094b9ec38fb8c2ef27
wall_time: 4.1m
---

## Result

- `period_r1`: 1.982547e-08
- `period_r2`: 1.745810e-08
- `f_r1`: 5.044016e+07
- `f_r2`: 5.728001e+07
- `i_r1_a`: -1.366755e-05
- `i_r2_a`: -1.437222e-05
- `i_tree_a`: -6.597651e-05
- `e_cycle_r1_j`: -9.836056e-13
- `c_eff_node_r1_f`: -6.786019e-15
- `ring_swing_v`: 3.67137
- `xo_swing_v`: 3.65877
- `i_total_a`: -9.401628e-05
- `p_rings_w`: -1.017844e-04
- `p_total_w`: -3.412791e-04
- `xo_trans_per_s`: 2.154403e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-pvt-q-extracted-fullchip --corners ss --temps 125 --supply 3.63 --supply-tol 0 --timeout 1800 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.fullchip.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, FULL-CHIP-DELTA-annotated for the ro1/ro2 inter-region trunks ONLY (layout/pex/build.py); every other inter-region trunk (clk, rst_n, raw_bit, raw_valid, ring_bit1, ring_bit2, vss, the supply branches) is unpriced by this composition -- see DR-0025 and layout/pex/build.py's own module docstring for the full accounting.
- CELL-INSTANCE GRANULARITY, NOT TRANSISTOR LEVEL (DR-0025): the inter-region parasitics this DUT carries were measured by a full-chip `klt extract --parasitics` run over layout/floorplan/trng_floorplan.gds in which every one of digital's ~2500 gf180mcu_fd_sc_mcu9t5v0__* standard-cell instances was abstracted as an opaque black box -- the same granularity the composed LVS already uses. No number in this record is evidence about any standard cell's own devices, and digital is not instantiated in this deck at all.
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
