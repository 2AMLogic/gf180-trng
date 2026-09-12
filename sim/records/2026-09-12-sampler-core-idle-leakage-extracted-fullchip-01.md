---
record: 2026-09-12-sampler-core-idle-leakage-extracted-fullchip-01
date: 2026-09-12T08:37:25Z
status: valid

testbench:
  path: sim/tb/sampler-core-idle-leakage-extracted-fullchip/tb_sampler_core_idle_leakage_extracted_fullchip.sp
  sha: a472f4173c3dc2b1b899fa5012073d870e99fa02
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
  temperature: 125

analysis:
  type: tran
  tstop: 9.5u
  tstep: 200p (print step; ngspice's own LTE sets the actual solver step, which is very coarse here because nothing switches after 300 ns)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-09-12-sampler-core-idle-leakage-extracted-fullchip-01/
  files:
    - ff_125c_3.63v.spice  sha256:2db43a97437a6c71f25b86be6302da18c42cc32ee166d5636284b8c04aa041a7
    - ff_125c_3.63v.log  sha256:882c854e549d1c6eeeb6ab100425bc5f3afd3dcdc0adfd18232d14327d9b6ceb
wall_time: 5.9m
---

## Result

- `i_idle_clklo_a`: 1.270370e-07
- `i_idle_clkhi_a`: 1.091160e-07
- `p_idle_clklo_w`: 4.611443e-07
- `p_idle_clkhi_w`: 3.960911e-07
- `i_idle_clklo_prev_a`: 1.285150e-07
- `i_idle_clkhi_prev_a`: 1.104510e-07
- `i_idle_worst_a`: 1.270370e-07
- `p_idle_worst_w`: 4.611443e-07
- `v_xo_v`: 6.222695e-06
- `v_n1_v`: 3.62965
- `v_n2_v`: 1.252705e-05
- `v_rawbit_clklo_v`: 3.132333e-07
- `v_rawvalid_clklo_v`: 3.62995
- `v_rawbit_clkhi_v`: 7.934852e-07
- `v_rawvalid_clkhi_v`: 3.62995
- `v_sup_v`: 3.63

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-core-idle-leakage-extracted-fullchip --corners ff --temps 125 --supply 3.63 --supply-tol 0 --timeout 3600 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.fullchip.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, FULL-CHIP-DELTA-annotated for the ro1/ro2 inter-region trunks AND the four disclosed driver-side-only output-load capacitors on raw_bit/raw_valid/ring_bit1/ring_bit2 (layout/pex/build.py); every other inter-region trunk (clk, rst_n, vss, the supply branches) is unpriced by this composition -- see DR-0025 and layout/pex/build.py's own module docstring for the full accounting.
- CELL-INSTANCE GRANULARITY, NOT TRANSISTOR LEVEL (DR-0025): the inter-region parasitics this DUT carries were measured by a full-chip `klt extract --parasitics` run over layout/floorplan/trng_floorplan.gds in which every one of digital's ~2500 gf180mcu_fd_sc_mcu9t5v0__* standard-cell instances was abstracted as an opaque black box -- the same granularity the composed LVS already uses. No number in this record is evidence about any standard cell's own devices, and digital is not instantiated in this deck at all.
- A WIDENED measurement window was needed, and the widening is itself evidence. The routing-level family's own 1 us tstop / 200 ns integration window does NOT settle on this DUT. Two discarded first attempts, reported rather than hidden (neither minted a record, the same way sections 7.2 and 7.3's own failed first attempts did not): at 1 us / 200 ns, i_idle_clklo_a = 190.99 nA against its own previous-window self-check i_idle_clklo_prev_a = 205.61 nA, a 7.7 % disagreement; at 5 us / 1 us, 138.07 nA against 143.52 nA, 3.9 %. For scale, the routing-level record's own self-check pair agrees to 0.9 % (136.80 nA vs 138.05 nA). The cause is physical, not numerical: the ~237 fF of added driver-side output load on raw_bit/raw_valid/ring_bit1/ring_bit2 takes materially longer to settle at leakage-level currents, so a short window integrates a settling transient rather than a static leakage. This deck's window is 9.5 us with a 1 us integration window -- as long as the shared idle-state protocol allows (rst_n's own pulse falls at 10.1 us, clk1's at 10.2 us), which is stated because it is a real ceiling on how far this can be pushed without changing the protocol itself. Any residual self-check disagreement in the record below is a stated upper bound on how much settling transient remains in the reported figure, always in the direction of OVER-reporting idle current.
- v_xo_v/v_n1_v/v_n2_v address `v(xduta.xcs.xo)`/`v(xduta.xr1.n1)`/`v(xduta.xr1.n2)` -- identical addresses to the routing-level family's own (`sampler_core_fullchip_extracted`'s `_sampler_core_fullchip_subckt` instantiates its two ring wrappers and the combiner_sampler wrapper the same way `_sampler_core_routed_subckt` does, with the DR-0025 delta and load capacitors inserted strictly between them). `n1`/`n2` name an arbitrary (klt-assigned) internal ring position, same caveat as every routed/fullchip family.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for idle power (ff/+125 C/3.63 V), the same point issues #17/#217's own records used, not the full 45-point grid.
- This is the ANALOG side of the DR-0009 boundary only: two rings, the XOR combiner, two sampler_dff instances -- same scope as the leaf-level and routing-level families.
- Reports STATIC current in a settled state -- same protocol (two parked-clock copies, charge-integrator measurement, self-check window pair) as the leaf-level and routing-level families; see the leaf-level family's own testbench header for the full method notes, unchanged here beyond the DUT and delta/load-capacitor additions above.
- clk/rst_n arrival is still driven from an ideal, zero-impedance ngspice source -- this record says nothing about clock-tree arrival at the sampler, per DR-0025.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
