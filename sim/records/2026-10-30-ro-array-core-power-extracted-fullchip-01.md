---
record: 2026-10-30-ro-array-core-power-extracted-fullchip-01
date: 2026-10-30T17:17:24Z
status: valid
supersedes: 2026-09-12-ro-array-core-power-extracted-fullchip-01

testbench:
  path: sim/tb/ro-array-core-power-extracted-fullchip/tb_ro_array_core_power_extracted_fullchip.sp
  sha: b9b2514475e95b5fe0fea92da6ea6ce823d9328f
netlist:
  path: layout/pex/sampler_core.fullchip.extracted.spice
  sha: 9928e2c57e02d9a2aa2da0cd9e223ae262b013c9
repo_commit: 88bcc15c65fe5cf4c9e8616f6cec162db015f23e-dirty
manifest:
  path: sim/tb/ro-array-core-power-extracted-fullchip/tb.json
  sha: a7d57503ac7fe315175add7a7813fcf3856b72f1
  snapshot: tb.manifest.json
  sha256: e6f6eb3ecca667aae6629af6645fc3d91a813e96b836a7a7844861e708e4b941
inputs:
  testbench_snapshot: tb.fragment.spice
  testbench_sha256: 2199823e1d5b11156136d4fed068629a4322bbdd8c22b79c13fd9a3ce35122f0
  netlist_snapshot: dut.netlist.spice
  netlist_sha256: ada1ba043ef0864fb77f7e0b9cd7d9dbb00216523295fdd84cd59cd6c905123c
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
  manifest: manifests/artifacts/2026-10-30-ro-array-core-power-extracted-fullchip-01.manifest.json
  files:
    - combiner_sampler.routed.extracted.spice  size:67970  sha256:859c0ccd81bf2911f3b4f32b05cad90430b8a192cc51c98429a48d7e490c61fc
    - dut.netlist.spice  size:2183  sha256:ada1ba043ef0864fb77f7e0b9cd7d9dbb00216523295fdd84cd59cd6c905123c
    - ff_-40c_3.63v.log  size:37590  sha256:8aa124dd2258b3a08cf58b8e942e19307fe38e48d47ab0b6dbfee44102cba2a4
    - ff_-40c_3.63v.spice  size:3464  sha256:e28e4dc3aa05ff69dea0fd0cb9b4a627e593274d11e133b93a3f953c56cc9627
    - pdk-models.json  size:1116  sha256:d0b1d3df67c9eb5d23d205d6298e71dfef25926ec6eac7a2ce1cec40f513094c
    - ro_ring11.routed.extracted.spice  size:17250  sha256:39739d9926aa9fe15a3c1379bf7384c98da3f07175a9bbbe795483195e55cc57
    - ro_ring11_ring2.routed.extracted.spice  size:17279  sha256:4fc7769fb0429e7229bb43edab8447f5e7a002b0e4da629331895103e7e17bf0
    - spinit  size:579  sha256:d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
    - tb.fragment.spice  size:1060  sha256:2199823e1d5b11156136d4fed068629a4322bbdd8c22b79c13fd9a3ce35122f0
    - tb.manifest.json  size:4565  sha256:e6f6eb3ecca667aae6629af6645fc3d91a813e96b836a7a7844861e708e4b941
wall_time: 19.1s
---

## Result

- `period_r1`: 7.960843e-09
- `period_r2`: 7.078095e-09
- `f_r1`: 1.256148e+08
- `f_r2`: 1.412810e+08
- `i_r1_a`: -3.605656e-05
- `i_r2_a`: -3.754323e-05
- `i_tree_a`: -1.920514e-04
- `e_cycle_r1_j`: -1.041957e-12
- `c_eff_node_r1_f`: -7.188595e-15
- `ring_swing_v`: 3.61657
- `xo_swing_v`: 3.6335
- `i_total_a`: -2.656512e-04
- `p_rings_w`: -2.671673e-04
- `p_total_w`: -9.643140e-04
- `xo_trans_per_s`: 5.337916e+08

Runs: 1 of 1 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power-extracted-fullchip --corners ff --temps -40 --supply 3.63 --supply-tol 0 --timeout 1800 --no-write
```

The manifest used is snapshotted as `tb.manifest.json` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-power-extracted-fullchip-01.manifest.json`) (sha256 `e6f6eb3ecca667aae6629af6645fc3d91a813e96b836a7a7844861e708e4b941`). The commands above read the CURRENT `sim/tb/ro-array-core-power-extracted-fullchip/tb.json`; check out `repo_commit` and, if the snapshot differs from the tree (`diff`), restore the snapshot over it before re-running. See `sim/README.md`.

The SPICE inputs ngspice consumed are snapshotted next to the decks as `tb.fragment.spice` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-power-extracted-fullchip-01.manifest.json`) and `dut.netlist.spice` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-power-extracted-fullchip-01.manifest.json`) (the decks include these copies, not the working-tree files). `testbench.sha`/`netlist.sha` hash those same bytes; if they differ from the tree at `repo_commit`, the run used dirty-tree input -- restore the snapshots over the originals (in a scratch worktree) before re-running. See `sim/README.md`.

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
