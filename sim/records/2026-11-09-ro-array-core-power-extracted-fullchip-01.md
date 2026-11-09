---
record: 2026-11-09-ro-array-core-power-extracted-fullchip-01
date: 2026-11-09T21:50:06Z
status: valid
supersedes: 2026-10-30-ro-array-core-power-extracted-fullchip-01

testbench:
  path: sim/tb/ro-array-core-power-extracted-fullchip/tb_ro_array_core_power_extracted_fullchip.sp
  sha: b9b2514475e95b5fe0fea92da6ea6ce823d9328f
netlist:
  path: layout/pex/sampler_core.fullchip.extracted.spice
  sha: a588b74150f65f3d43e96067b9c1f03815007be4
repo_commit: 910461f4e20a99fe6369fa53beccde60370754b3-dirty
manifest:
  path: sim/tb/ro-array-core-power-extracted-fullchip/tb.json
  sha: a7d57503ac7fe315175add7a7813fcf3856b72f1
  snapshot: tb.manifest.json
  sha256: e6f6eb3ecca667aae6629af6645fc3d91a813e96b836a7a7844861e708e4b941
inputs:
  testbench_snapshot: tb.fragment.spice
  testbench_sha256: 2199823e1d5b11156136d4fed068629a4322bbdd8c22b79c13fd9a3ce35122f0
  netlist_snapshot: dut.netlist.spice
  netlist_sha256: 42db129f01dc1ba3ce4dc06d4b71cf07e7b9c1d84a546b3a5a955abb1a14b09d
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
  ngspice: "ngspice-46 : Circuit level simulation program"
  ngspice_startup: no-user-init+pinned-spinit/1
  ngspice_startup_flags: "-n"
  ngspice_startup_spinit: sim/harness/ngspice_scripts/spinit
  ngspice_startup_spinit_sha256: d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
  ngspice_startup_spinit_snapshot: spinit
  platform: Linux-7.0.0-1014-aws-x86_64-with-glibc2.39

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

stored_evidence:
  manifest: manifests/artifacts/2026-11-09-ro-array-core-power-extracted-fullchip-01.manifest.json
  files:
    - combiner_sampler.routed.extracted.spice  size:68125  sha256:2e1076888602f7561a615935877f36f457678a6b59af3257071abd5c82d3bbe5
    - dut.netlist.spice  size:2183  sha256:42db129f01dc1ba3ce4dc06d4b71cf07e7b9c1d84a546b3a5a955abb1a14b09d
    - ff_-40c_3.63v.log  size:38052  sha256:bc185978403d343c2028f8c81a198a74d8073dea982224234c9cf864165f6289
    - ff_-40c_3.63v.spice  size:3464  sha256:d905cd1a420cabe1b17ac64e2645478ffa4f53c223f4988d6a846d7a6aab574d
    - pdk-models.json  size:1116  sha256:d0b1d3df67c9eb5d23d205d6298e71dfef25926ec6eac7a2ce1cec40f513094c
    - ro_ring11.routed.extracted.spice  size:17465  sha256:eaba0a3c422896c360a9847017fb373856a583064b3ef1b9843ef5377dcda9e8
    - ro_ring11_ring2.routed.extracted.spice  size:17497  sha256:25835ccfb419970b26ce53280ea86562720cd33165ea4335095d64a389cffc6c
    - spinit  size:579  sha256:d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
    - tb.fragment.spice  size:1060  sha256:2199823e1d5b11156136d4fed068629a4322bbdd8c22b79c13fd9a3ce35122f0
    - tb.manifest.json  size:4565  sha256:e6f6eb3ecca667aae6629af6645fc3d91a813e96b836a7a7844861e708e4b941
wall_time: 20.9s
---

## Result

- `period_r1`: 7.957732e-09
- `period_r2`: 7.074628e-09
- `f_r1`: 1.256639e+08
- `f_r2`: 1.413502e+08
- `i_r1_a`: -3.607276e-05
- `i_r2_a`: -3.755599e-05
- `i_tree_a`: -1.919613e-04
- `e_cycle_r1_j`: -1.042018e-12
- `c_eff_node_r1_f`: -7.189015e-15
- `ring_swing_v`: 3.61644
- `xo_swing_v`: 3.63381
- `i_total_a`: -2.655900e-04
- `p_rings_w`: -2.672724e-04
- `p_total_w`: -9.640918e-04
- `xo_trans_per_s`: 5.340283e+08

Runs: 1 of 1 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power-extracted-fullchip --corners ff --temps -40 --supply 3.63 --supply-tol 0 --timeout 1800 --no-write
```

The manifest used is snapshotted as `tb.manifest.json` in the stored evidence (`manifests/artifacts/2026-11-09-ro-array-core-power-extracted-fullchip-01.manifest.json`) (sha256 `e6f6eb3ecca667aae6629af6645fc3d91a813e96b836a7a7844861e708e4b941`). The commands above read the CURRENT `sim/tb/ro-array-core-power-extracted-fullchip/tb.json`; check out `repo_commit` and, if the snapshot differs from the tree (`diff`), restore the snapshot over it before re-running. See `sim/README.md`.

The SPICE inputs ngspice consumed are snapshotted next to the decks as `tb.fragment.spice` in the stored evidence (`manifests/artifacts/2026-11-09-ro-array-core-power-extracted-fullchip-01.manifest.json`) and `dut.netlist.spice` in the stored evidence (`manifests/artifacts/2026-11-09-ro-array-core-power-extracted-fullchip-01.manifest.json`) (the decks include these copies, not the working-tree files). `testbench.sha`/`netlist.sha` hash those same bytes; if they differ from the tree at `repo_commit`, the run used dirty-tree input -- restore the snapshots over the originals (in a scratch worktree) before re-running. See `sim/README.md`.

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- PDK model identity (pdk_content) covers only the 4 file(s) listed in pdk-models.json, reached from the deck's .include/.lib entry points; it was captured before the run and re-checked before this record was written, so an edit made and reverted between those two checks is not detected (see sim/README.md).
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
