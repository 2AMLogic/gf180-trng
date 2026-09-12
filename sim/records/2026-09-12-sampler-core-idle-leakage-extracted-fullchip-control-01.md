---
record: 2026-09-12-sampler-core-idle-leakage-extracted-fullchip-control-01
date: 2026-09-12T08:44:23Z
status: valid

testbench:
  path: sim/tb/sampler-core-idle-leakage-extracted-fullchip-control/tb_sampler_core_idle_leakage_extracted_fullchip_control.sp
  sha: 7ab71142a54c11ddcec1177277a2cd96ab004446
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
  path: sim/records/raw/2026-09-12-sampler-core-idle-leakage-extracted-fullchip-control-01/
  files:
    - ff_125c_3.63v.spice  sha256:a152882f2da5db4074c74ff5a56a054c8a55400aff437b7b850206bfdb7e3941
    - ff_125c_3.63v.log  sha256:2334b5263d3ef77edba0446724f4695ed24c4997431a465495d03bbbac5b16c2
wall_time: 6.2m
---

## Result

- `i_idle_clklo_a`: 1.219040e-07
- `i_idle_clkhi_a`: 1.047660e-07
- `p_idle_clklo_w`: 4.425115e-07
- `p_idle_clkhi_w`: 3.803006e-07
- `i_idle_clklo_prev_a`: 1.224860e-07
- `i_idle_clkhi_prev_a`: 1.053394e-07
- `i_idle_worst_a`: 1.219040e-07
- `p_idle_worst_w`: 4.425115e-07
- `v_xo_v`: 6.401461e-06
- `v_n1_v`: 3.62966
- `v_n2_v`: 1.260737e-05
- `v_rawbit_clklo_v`: 1.619024e-06
- `v_rawvalid_clklo_v`: 3.62995
- `v_rawbit_clkhi_v`: 2.101277e-06
- `v_rawvalid_clkhi_v`: 3.62995
- `v_sup_v`: 3.63

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-core-idle-leakage-extracted-fullchip-control --corners ff --temps 125 --supply 3.63 --supply-tol 0 --timeout 3600 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.routed.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- ZERO-DELTA CONTROL for sim/tb/sampler-core-idle-leakage-extracted-fullchip/: this deck is byte-identical to that one except for its own header comment and the DUT subcircuit name (sampler_core_routed_extracted here, sampler_core_fullchip_extracted there), INCLUDING the widened 9.5 us / 1 us window, so the difference between this record and its -extracted-fullchip sibling is exactly what layout/pex/build.py's full-chip composition adds and nothing else -- not a window difference.
- Carries NO inter-region parasitic at all (that is the point of a control): the DUT is layout/pex/sampler_core.routed.extracted.spice, the same intra-region routing-level composition issue #217 recorded, per DR-0024.
- Runs at the WIDENED 9.5 us / 1 us window its -extracted-fullchip sibling needs, not the 1 us / 200 ns window the routing-level (#217) family used -- deliberately, so the two records this section subtracts are integrated over the same window. One consequence worth stating: this control's own reading is therefore NOT directly comparable to the #217 record's 136.80 nA either; the difference between those two is a window difference on the same DUT, which is itself reported in section 8.4.
- v_xo_v/v_n1_v/v_n2_v address `v(xduta.xcs.xo)`/`v(xduta.xr1.n1)`/`v(xduta.xr1.n2)` -- identical addresses to the routing-level family's own (`sampler_core_fullchip_extracted`'s `_sampler_core_fullchip_subckt` instantiates its two ring wrappers and the combiner_sampler wrapper the same way `_sampler_core_routed_subckt` does, with the DR-0025 delta and load capacitors inserted strictly between them). `n1`/`n2` name an arbitrary (klt-assigned) internal ring position, same caveat as every routed/fullchip family.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for idle power (ff/+125 C/3.63 V), the same point issues #17/#217's own records used, not the full 45-point grid.
- This is the ANALOG side of the DR-0009 boundary only: two rings, the XOR combiner, two sampler_dff instances -- same scope as the leaf-level and routing-level families.
- Reports STATIC current in a settled state -- same protocol (two parked-clock copies, charge-integrator measurement, self-check window pair) as the leaf-level and routing-level families; see the leaf-level family's own testbench header for the full method notes, unchanged here beyond the DUT and delta/load-capacitor additions above.
- clk/rst_n arrival is still driven from an ideal, zero-impedance ngspice source -- this record says nothing about clock-tree arrival at the sampler, per DR-0025.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
