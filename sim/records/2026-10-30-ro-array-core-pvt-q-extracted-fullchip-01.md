---
record: 2026-10-30-ro-array-core-pvt-q-extracted-fullchip-01
date: 2026-10-30T17:16:26Z
status: valid
supersedes: 2026-09-12-ro-array-core-pvt-q-extracted-fullchip-01

testbench:
  path: sim/tb/ro-array-core-pvt-q-extracted-fullchip/tb_ro_array_core_pvt_q_extracted_fullchip.sp
  sha: 7e8cb785892082bd9f387042a82f40a22dd0e062
netlist:
  path: layout/pex/sampler_core.fullchip.extracted.spice
  sha: 9928e2c57e02d9a2aa2da0cd9e223ae262b013c9
repo_commit: 88bcc15c65fe5cf4c9e8616f6cec162db015f23e
manifest:
  path: sim/tb/ro-array-core-pvt-q-extracted-fullchip/tb.json
  sha: d0c724f01c835800874a11a1b257e08ac92ac9b8
  snapshot: tb.manifest.json
  sha256: d7e4d524fc215c21493c0639ba5ee274acbaf57e0990223ab1aa177d47926803
inputs:
  testbench_snapshot: tb.fragment.spice
  testbench_sha256: 5b760d6b7befb5e82c408aad0fac055244e7f1992aeaac5229c75e166ddabbcc
  netlist_snapshot: dut.netlist.spice
  netlist_sha256: ada1ba043ef0864fb77f7e0b9cd7d9dbb00216523295fdd84cd59cd6c905123c
  netlist_dependencies: ro_ring11.routed.extracted.spice, ro_ring11_ring2.routed.extracted.spice, combiner_sampler.routed.extracted.spice

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)
pdk_content:
  manifest_file: pdk-models.json
  sha256: 3c690a5cf6bea35bf5041b4dc0f68f0964cfbb3d82c5cd15d75922f02bd56d96
  identity: sha256:530873e7e8d8679de1db4277f07ea4cd627eae74c53428eed4bc1dd71813a193
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

stored_evidence:
  manifest: manifests/artifacts/2026-10-30-ro-array-core-pvt-q-extracted-fullchip-01.manifest.json
  files:
    - combiner_sampler.routed.extracted.spice  size:67970  sha256:859c0ccd81bf2911f3b4f32b05cad90430b8a192cc51c98429a48d7e490c61fc
    - dut.netlist.spice  size:2183  sha256:ada1ba043ef0864fb77f7e0b9cd7d9dbb00216523295fdd84cd59cd6c905123c
    - pdk-models.json  size:1116  sha256:3c690a5cf6bea35bf5041b4dc0f68f0964cfbb3d82c5cd15d75922f02bd56d96
    - ro_ring11.routed.extracted.spice  size:17250  sha256:39739d9926aa9fe15a3c1379bf7384c98da3f07175a9bbbe795483195e55cc57
    - ro_ring11_ring2.routed.extracted.spice  size:17279  sha256:4fc7769fb0429e7229bb43edab8447f5e7a002b0e4da629331895103e7e17bf0
    - spinit  size:579  sha256:d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
    - ss_125c_3.63v.log  size:38648  sha256:9ba40c04b25510b0c9bad34198a78ab4d9afba71cec3bf10d61263ce9c388458
    - ss_125c_3.63v.spice  size:3473  sha256:3d9f81573e3ae6509e13f5faa7f3ecc93ef7c2cd14308b158ea8699414777b33
    - tb.fragment.spice  size:2503  sha256:5b760d6b7befb5e82c408aad0fac055244e7f1992aeaac5229c75e166ddabbcc
    - tb.manifest.json  size:5454  sha256:d7e4d524fc215c21493c0639ba5ee274acbaf57e0990223ab1aa177d47926803
wall_time: 23.3s
---

## Result

- `period_r1`: 1.983559e-08
- `period_r2`: 1.746480e-08
- `f_r1`: 5.041444e+07
- `f_r2`: 5.725802e+07
- `i_r1_a`: -1.365305e-05
- `i_r2_a`: -1.436904e-05
- `i_tree_a`: -6.604508e-05
- `e_cycle_r1_j`: -9.830629e-13
- `c_eff_node_r1_f`: -6.782275e-15
- `ring_swing_v`: 3.67017
- `xo_swing_v`: 3.65805
- `i_total_a`: -9.406717e-05
- `p_rings_w`: -1.017202e-04
- `p_total_w`: -3.414638e-04
- `xo_trans_per_s`: 2.153449e+08

Runs: 1 of 1 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-pvt-q-extracted-fullchip --corners ss --temps 125 --supply 3.63 --supply-tol 0 --timeout 1800 --no-write
```

The manifest used is snapshotted as `tb.manifest.json` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-pvt-q-extracted-fullchip-01.manifest.json`) (sha256 `d7e4d524fc215c21493c0639ba5ee274acbaf57e0990223ab1aa177d47926803`). The commands above read the CURRENT `sim/tb/ro-array-core-pvt-q-extracted-fullchip/tb.json`; check out `repo_commit` and, if the snapshot differs from the tree (`diff`), restore the snapshot over it before re-running. See `sim/README.md`.

The SPICE inputs ngspice consumed are snapshotted next to the decks as `tb.fragment.spice` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-pvt-q-extracted-fullchip-01.manifest.json`) and `dut.netlist.spice` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-pvt-q-extracted-fullchip-01.manifest.json`) (the decks include these copies, not the working-tree files). `testbench.sha`/`netlist.sha` hash those same bytes; if they differ from the tree at `repo_commit`, the run used dirty-tree input -- restore the snapshots over the originals (in a scratch worktree) before re-running. See `sim/README.md`.

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- PDK model identity (pdk_content) covers only the 4 file(s) listed in pdk-models.json, reached from the deck's .include/.lib entry points; it was captured before the run and re-checked before this record was written, so an edit made and reverted between those two checks is not detected (see sim/README.md).
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
