---
record: 2026-09-11-sampler-core-idle-leakage-extracted-routed-01
date: 2026-09-11T06:49:23Z
status: valid

testbench:
  path: sim/tb/sampler-core-idle-leakage-extracted-routed/tb_sampler_core_idle_leakage_extracted_routed.sp
  sha: d01d2a4fbd75910b95847e908f3472bc705c0043
netlist:
  path: layout/pex/sampler_core.routed.extracted.spice
  sha: 4bf8c65adc37dad04d75c4641f81e4bfbb09ee4d
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
  temperature: 125

analysis:
  type: tran
  tstop: 1u
  tstep: 200p (print step; ngspice's own LTE sets the actual solver step, which is very coarse here because nothing switches after 300 ns)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-09-11-sampler-core-idle-leakage-extracted-routed-01/
  files:
    - ff_125c_3.63v.spice  sha256:a6846dd9e33dc12beeef11b7858b735b7692953821a5d7f32d1e6b2b8a8f069b
    - ff_125c_3.63v.log  sha256:f6e969beb9bf8dd7848c3a7ad1b72d7d74f9b5d2c257fc4a48f34a54db8007c7
wall_time: 22.3s
---

## Result

- `i_idle_clklo_a`: 1.367970e-07
- `i_idle_clkhi_a`: 1.199745e-07
- `p_idle_clklo_w`: 4.965731e-07
- `p_idle_clkhi_w`: 4.355074e-07
- `i_idle_clklo_prev_a`: 1.380480e-07
- `i_idle_clkhi_prev_a`: 1.214625e-07
- `i_idle_worst_a`: 1.367970e-07
- `p_idle_worst_w`: 4.965731e-07
- `v_xo_v`: 8.759390e-06
- `v_n1_v`: 3.62962
- `v_n2_v`: 1.449894e-05
- `v_rawbit_clklo_v`: 2.064625e-06
- `v_rawvalid_clklo_v`: 3.62995
- `v_rawbit_clkhi_v`: 3.363872e-06
- `v_rawvalid_clkhi_v`: 3.62995
- `v_sup_v`: 3.63

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-core-idle-leakage-extracted-routed --corners ff --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.routed.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, ROUTING-level-parasitic-annotated for the entire block (both rings AND the fully assembled combiner_sampler -- buffers, XOR, all four samplers, together, exactly as physically wired) -- see layout/pex/build.py's own module docstring, 'Two composed drop-ins, different scope', and sim/characterization-post-layout-extracted.md's 2026-09-11 delta section for exactly what this does and does not capture.
- v_xo_v/v_n1_v/v_n2_v address `v(xduta.xcs.xo)`/`v(xduta.xr1.n1)`/`v(xduta.xr1.n2)` -- ONE HOP SHALLOWER than the leaf-level family's `v(xduta.xdut.xo)`/`v(xduta.xdut.xr1.n1)`/`v(xduta.xdut.xr1.n2)`, because sampler_core_routed_extracted (layout/pex/build.py's own `_sampler_core_routed_subckt`) instantiates its two ring wrappers and the combiner_sampler wrapper directly, with no intermediate ro_array_core_routed_extracted instance (that instance would have forced a duplicate, differently-loaded copy of the buffer/XOR/sampler devices -- see the module docstring). `xcs` is the combiner_sampler wrapper instance; `xo` there is a positively-identified, self-documenting internal net name (layout/pex/build.py's `_resolve_combiner_sampler_ports`), not the arbitrary `cN` placeholder an unresolved position would get. `n1`/`n2` name an arbitrary (klt-assigned) internal ring position, same caveat as the routed ro-array-core-level families.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for idle power (ff/+125 C/3.63 V), the same point issue #17's own leaf-level record used, not the full 45-point grid.
- This is the ANALOG side of the DR-0009 boundary only: two rings, the XOR combiner, two sampler_dff instances -- same scope as the leaf-level family.
- Reports STATIC current in a settled state -- same protocol (two parked-clock copies, charge-integrator measurement, self-check window pair) as the leaf-level family; see that family's own testbench header for the full method notes, unchanged here beyond the DUT and node-address changes above.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
