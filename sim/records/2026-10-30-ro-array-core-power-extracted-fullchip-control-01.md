---
record: 2026-10-30-ro-array-core-power-extracted-fullchip-control-01
date: 2026-10-30T17:17:48Z
status: valid
supersedes: 2026-09-12-ro-array-core-power-extracted-fullchip-control-01

testbench:
  path: sim/tb/ro-array-core-power-extracted-fullchip-control/tb_ro_array_core_power_extracted_fullchip_control.sp
  sha: c10ba6b1267ec1d6bac2a22e58584d4e6d71b9bd
netlist:
  path: layout/pex/sampler_core.routed.extracted.spice
  sha: 4bf8c65adc37dad04d75c4641f81e4bfbb09ee4d
repo_commit: 88bcc15c65fe5cf4c9e8616f6cec162db015f23e-dirty
manifest:
  path: sim/tb/ro-array-core-power-extracted-fullchip-control/tb.json
  sha: 8a633a5c837e8da205cc59657118a377ce875f62
  snapshot: tb.manifest.json
  sha256: 0fc8028800acbb0f390c2c2c243f46ecebcc093ce39388629299fdb557a7e77d
inputs:
  testbench_snapshot: tb.fragment.spice
  testbench_sha256: c5ee931e9af2e13908da03ed4cbb23027d586045a7b50d4695c67fb25cecd682
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
  manifest: manifests/artifacts/2026-10-30-ro-array-core-power-extracted-fullchip-control-01.manifest.json
  files:
    - combiner_sampler.routed.extracted.spice  size:67970  sha256:859c0ccd81bf2911f3b4f32b05cad90430b8a192cc51c98429a48d7e490c61fc
    - dut.netlist.spice  size:1670  sha256:4a2277125643c21766860230555691d955cfdff0877bd375930300d4e27e6e2c
    - ff_-40c_3.63v.log  size:37302  sha256:8321d23b80155b47b9af9813009bd85a7d043c4a0c67bdf7d121e4dac4e9589c
    - ff_-40c_3.63v.spice  size:3488  sha256:507303ab40c7da313160e6af4dea1ddc7021ea57539e992601be3db1fb4196ed
    - pdk-models.json  size:1116  sha256:d0b1d3df67c9eb5d23d205d6298e71dfef25926ec6eac7a2ce1cec40f513094c
    - ro_ring11.routed.extracted.spice  size:17250  sha256:39739d9926aa9fe15a3c1379bf7384c98da3f07175a9bbbe795483195e55cc57
    - ro_ring11_ring2.routed.extracted.spice  size:17279  sha256:4fc7769fb0429e7229bb43edab8447f5e7a002b0e4da629331895103e7e17bf0
    - spinit  size:579  sha256:d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
    - tb.fragment.spice  size:1618  sha256:c5ee931e9af2e13908da03ed4cbb23027d586045a7b50d4695c67fb25cecd682
    - tb.manifest.json  size:5049  sha256:0fc8028800acbb0f390c2c2c243f46ecebcc093ce39388629299fdb557a7e77d
wall_time: 18.6s
---

## Result

- `period_r1`: 7.172718e-09
- `period_r2`: 6.772302e-09
- `f_r1`: 1.394172e+08
- `f_r2`: 1.476603e+08
- `i_r1_a`: -3.534563e-05
- `i_r2_a`: -3.731126e-05
- `i_tree_a`: -1.911825e-04
- `e_cycle_r1_j`: -9.202928e-13
- `c_eff_node_r1_f`: -6.349216e-15
- `ring_swing_v`: 3.65198
- `xo_swing_v`: 3.63422
- `i_total_a`: -2.638394e-04
- `p_rings_w`: -2.637445e-04
- `p_total_w`: -9.577369e-04
- `xo_trans_per_s`: 5.741549e+08

Runs: 1 of 1 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power-extracted-fullchip-control --corners ff --temps -40 --supply 3.63 --supply-tol 0 --timeout 1800 --no-write
```

The manifest used is snapshotted as `tb.manifest.json` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-power-extracted-fullchip-control-01.manifest.json`) (sha256 `0fc8028800acbb0f390c2c2c243f46ecebcc093ce39388629299fdb557a7e77d`). The commands above read the CURRENT `sim/tb/ro-array-core-power-extracted-fullchip-control/tb.json`; check out `repo_commit` and, if the snapshot differs from the tree (`diff`), restore the snapshot over it before re-running. See `sim/README.md`.

The SPICE inputs ngspice consumed are snapshotted next to the decks as `tb.fragment.spice` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-power-extracted-fullchip-control-01.manifest.json`) and `dut.netlist.spice` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-power-extracted-fullchip-control-01.manifest.json`) (the decks include these copies, not the working-tree files). `testbench.sha`/`netlist.sha` hash those same bytes; if they differ from the tree at `repo_commit`, the run used dirty-tree input -- restore the snapshots over the originals (in a scratch worktree) before re-running. See `sim/README.md`.

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- PDK model identity (pdk_content) covers only the 4 file(s) listed in pdk-models.json, reached from the deck's .include/.lib entry points; it was captured before the run and re-checked before this record was written, so an edit made and reverted between those two checks is not detected (see sim/README.md).
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
