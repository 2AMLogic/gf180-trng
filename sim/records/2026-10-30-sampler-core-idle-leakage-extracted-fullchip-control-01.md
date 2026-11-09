---
record: 2026-10-30-sampler-core-idle-leakage-extracted-fullchip-control-01
date: 2026-10-30T17:20:51Z
status: valid
supersedes: 2026-09-12-sampler-core-idle-leakage-extracted-fullchip-control-01

testbench:
  path: sim/tb/sampler-core-idle-leakage-extracted-fullchip-control/tb_sampler_core_idle_leakage_extracted_fullchip_control.sp
  sha: 7ab71142a54c11ddcec1177277a2cd96ab004446
netlist:
  path: layout/pex/sampler_core.routed.extracted.spice
  sha: 4bf8c65adc37dad04d75c4641f81e4bfbb09ee4d
repo_commit: 88bcc15c65fe5cf4c9e8616f6cec162db015f23e-dirty
manifest:
  path: sim/tb/sampler-core-idle-leakage-extracted-fullchip-control/tb.json
  sha: d94f881b070ea3275f92be6fd5321fcb9bd41a83
  snapshot: tb.manifest.json
  sha256: a592beb33068cc57eb6a85627d3a521ae8ddb2f5aa5e4e44cf19fa65ef42a8c9
inputs:
  testbench_snapshot: tb.fragment.spice
  testbench_sha256: e8376ca422956f56f076cbd1bfa9158e90ef485b17a11e47ba8ae53b8b3c374c
  netlist_snapshot: dut.netlist.spice
  netlist_sha256: 4a2277125643c21766860230555691d955cfdff0877bd375930300d4e27e6e2c
  netlist_dependencies: ro_ring11.routed.extracted.spice, ro_ring11_ring2.routed.extracted.spice, combiner_sampler.routed.extracted.spice

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)
pdk_content:
  manifest_file: pdk-models.json
  sha256: d0b1d3df67c9eb5d23d205d6298e71dfef25926ec6eac7a2ce1cec40f513094c
  identity: sha256:1a5bde3746d5c8b6b008f4a54d22dd4f2fbad6649c4ccc934137329cc699f0b0
  file_count: 4
  complete: true
  problems: 0

tool:
  ngspice: "ngspice-42 : Circuit level simulation program"
  ngspice_startup: no-user-init+pinned-spinit/1
  ngspice_startup_flags: "-n"
  ngspice_startup_spinit: sim/harness/ngspice_scripts/spinit
  ngspice_startup_spinit_sha256: d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
  ngspice_startup_spinit_snapshot: spinit
  platform: Linux-7.0.0-1014-aws-x86_64-with-glibc2.39

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

stored_evidence:
  manifest: manifests/artifacts/2026-10-30-sampler-core-idle-leakage-extracted-fullchip-control-01.manifest.json
  files:
    - combiner_sampler.routed.extracted.spice  size:67970  sha256:859c0ccd81bf2911f3b4f32b05cad90430b8a192cc51c98429a48d7e490c61fc
    - dut.netlist.spice  size:1670  sha256:4a2277125643c21766860230555691d955cfdff0877bd375930300d4e27e6e2c
    - ff_125c_3.63v.log  size:76906  sha256:d4ebd57f74741dd16ad38299678de6062781b9b2c0a1ac95e3b4cd91fba9de5a
    - ff_125c_3.63v.spice  size:3225  sha256:65d152d0a3ad84a5f4f1e9641e522e99b21b4031b8df1ad5039e981c192ed6cb
    - pdk-models.json  size:1116  sha256:d0b1d3df67c9eb5d23d205d6298e71dfef25926ec6eac7a2ce1cec40f513094c
    - ro_ring11.routed.extracted.spice  size:17250  sha256:39739d9926aa9fe15a3c1379bf7384c98da3f07175a9bbbe795483195e55cc57
    - ro_ring11_ring2.routed.extracted.spice  size:17279  sha256:4fc7769fb0429e7229bb43edab8447f5e7a002b0e4da629331895103e7e17bf0
    - spinit  size:579  sha256:d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
    - tb.fragment.spice  size:2586  sha256:e8376ca422956f56f076cbd1bfa9158e90ef485b17a11e47ba8ae53b8b3c374c
    - tb.manifest.json  size:5134  sha256:a592beb33068cc57eb6a85627d3a521ae8ddb2f5aa5e4e44cf19fa65ef42a8c9
wall_time: 56.2s
---

## Result

- `i_idle_clklo_a`: 1.223040e-07
- `i_idle_clkhi_a`: 1.051930e-07
- `p_idle_clklo_w`: 4.439635e-07
- `p_idle_clkhi_w`: 3.818506e-07
- `i_idle_clklo_prev_a`: 1.228980e-07
- `i_idle_clkhi_prev_a`: 1.057013e-07
- `i_idle_worst_a`: 1.223040e-07
- `p_idle_worst_w`: 4.439635e-07
- `v_xo_v`: 1.025041e-05
- `v_n1_v`: 3.62966
- `v_n2_v`: 1.542839e-05
- `v_rawbit_clklo_v`: 4.308810e-06
- `v_rawvalid_clklo_v`: 3.62996
- `v_rawbit_clkhi_v`: 4.787078e-06
- `v_rawvalid_clkhi_v`: 3.62996
- `v_sup_v`: 3.63

Runs: 1 of 1 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-core-idle-leakage-extracted-fullchip-control --corners ff --temps 125 --supply 3.63 --supply-tol 0 --timeout 1800 --no-write
```

The manifest used is snapshotted as `tb.manifest.json` in the stored evidence (`manifests/artifacts/2026-10-30-sampler-core-idle-leakage-extracted-fullchip-control-01.manifest.json`) (sha256 `a592beb33068cc57eb6a85627d3a521ae8ddb2f5aa5e4e44cf19fa65ef42a8c9`). The commands above read the CURRENT `sim/tb/sampler-core-idle-leakage-extracted-fullchip-control/tb.json`; check out `repo_commit` and, if the snapshot differs from the tree (`diff`), restore the snapshot over it before re-running. See `sim/README.md`.

The SPICE inputs ngspice consumed are snapshotted next to the decks as `tb.fragment.spice` in the stored evidence (`manifests/artifacts/2026-10-30-sampler-core-idle-leakage-extracted-fullchip-control-01.manifest.json`) and `dut.netlist.spice` in the stored evidence (`manifests/artifacts/2026-10-30-sampler-core-idle-leakage-extracted-fullchip-control-01.manifest.json`) (the decks include these copies, not the working-tree files). `testbench.sha`/`netlist.sha` hash those same bytes; if they differ from the tree at `repo_commit`, the run used dirty-tree input -- restore the snapshots over the originals (in a scratch worktree) before re-running. See `sim/README.md`.

## Caveats

- Single corner (ff / 3.63 V / 125 C). Says nothing about any other corner.
- PDK model identity (pdk_content) covers only the 4 file(s) listed in pdk-models.json, reached from the deck's .include/.lib entry points; it was captured before the run and re-checked before this record was written, so an edit made and reverted between those two checks is not detected (see sim/README.md).
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
