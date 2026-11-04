---
record: 2026-10-30-ro-array-core-pvt-q-extracted-fullchip-control-01
date: 2026-10-30T17:16:54Z
status: valid
supersedes: 2026-09-12-ro-array-core-pvt-q-extracted-fullchip-control-01

testbench:
  path: sim/tb/ro-array-core-pvt-q-extracted-fullchip-control/tb_ro_array_core_pvt_q_extracted_fullchip_control.sp
  sha: 48031ab7ba0d1e31c3df4d9bb6dc6ef3b79a475b
netlist:
  path: layout/pex/sampler_core.routed.extracted.spice
  sha: 4bf8c65adc37dad04d75c4641f81e4bfbb09ee4d
repo_commit: 88bcc15c65fe5cf4c9e8616f6cec162db015f23e-dirty
manifest:
  path: sim/tb/ro-array-core-pvt-q-extracted-fullchip-control/tb.json
  sha: 032ee7d36482d0b5602844d97a8d0202aac8f8cb
  snapshot: tb.manifest.json
  sha256: a2e9e1f252009a34852c6cd7be46b360da28fc80224974590bd02253d06437f4
inputs:
  testbench_snapshot: tb.fragment.spice
  testbench_sha256: 8fa5928ff92f4a438a49a783e700d9845caf20f44f3203022071b6a9b8414a0d
  netlist_snapshot: dut.netlist.spice
  netlist_sha256: 4a2277125643c21766860230555691d955cfdff0877bd375930300d4e27e6e2c
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
  manifest: manifests/artifacts/2026-10-30-ro-array-core-pvt-q-extracted-fullchip-control-01.manifest.json
  files:
    - combiner_sampler.routed.extracted.spice  size:67970  sha256:859c0ccd81bf2911f3b4f32b05cad90430b8a192cc51c98429a48d7e490c61fc
    - dut.netlist.spice  size:1670  sha256:4a2277125643c21766860230555691d955cfdff0877bd375930300d4e27e6e2c
    - pdk-models.json  size:1116  sha256:3c690a5cf6bea35bf5041b4dc0f68f0964cfbb3d82c5cd15d75922f02bd56d96
    - ro_ring11.routed.extracted.spice  size:17250  sha256:39739d9926aa9fe15a3c1379bf7384c98da3f07175a9bbbe795483195e55cc57
    - ro_ring11_ring2.routed.extracted.spice  size:17279  sha256:4fc7769fb0429e7229bb43edab8447f5e7a002b0e4da629331895103e7e17bf0
    - spinit  size:579  sha256:d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
    - ss_125c_3.63v.log  size:38999  sha256:9c8635356d161be69507594eb01d701e744d375c125902e542800c1f591b216f
    - ss_125c_3.63v.spice  size:3497  sha256:9ced524e5bb92b4140be1ca6962778bd5fe7615d970f5e354629e96299a19d34
    - tb.fragment.spice  size:3061  sha256:8fa5928ff92f4a438a49a783e700d9845caf20f44f3203022071b6a9b8414a0d
    - tb.manifest.json  size:5657  sha256:a2e9e1f252009a34852c6cd7be46b360da28fc80224974590bd02253d06437f4
wall_time: 25.3s
---

## Result

- `period_r1`: 1.774373e-08
- `period_r2`: 1.662657e-08
- `f_r1`: 5.635794e+07
- `f_r2`: 6.014471e+07
- `i_r1_a`: -1.352932e-05
- `i_r2_a`: -1.436983e-05
- `i_tree_a`: -6.570763e-05
- `e_cycle_r1_j`: -8.714201e-13
- `c_eff_node_r1_f`: -6.012037e-15
- `ring_swing_v`: 3.69416
- `xo_swing_v`: 3.65056
- `i_total_a`: -9.360679e-05
- `p_rings_w`: -1.012739e-04
- `p_total_w`: -3.397926e-04
- `xo_trans_per_s`: 2.330053e+08

Runs: 1 of 1 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-pvt-q-extracted-fullchip-control --corners ss --temps 125 --supply 3.63 --supply-tol 0 --timeout 1800 --no-write
```

The manifest used is snapshotted as `tb.manifest.json` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-pvt-q-extracted-fullchip-control-01.manifest.json`) (sha256 `a2e9e1f252009a34852c6cd7be46b360da28fc80224974590bd02253d06437f4`). The commands above read the CURRENT `sim/tb/ro-array-core-pvt-q-extracted-fullchip-control/tb.json`; check out `repo_commit` and, if the snapshot differs from the tree (`diff`), restore the snapshot over it before re-running. See `sim/README.md`.

The SPICE inputs ngspice consumed are snapshotted next to the decks as `tb.fragment.spice` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-pvt-q-extracted-fullchip-control-01.manifest.json`) and `dut.netlist.spice` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-pvt-q-extracted-fullchip-control-01.manifest.json`) (the decks include these copies, not the working-tree files). `testbench.sha`/`netlist.sha` hash those same bytes; if they differ from the tree at `repo_commit`, the run used dirty-tree input -- restore the snapshots over the originals (in a scratch worktree) before re-running. See `sim/README.md`.

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- PDK model identity (pdk_content) covers only the 4 file(s) listed in pdk-models.json, reached from the deck's .include/.lib entry points; it was captured before the run and re-checked before this record was written, so an edit made and reverted between those two checks is not detected (see sim/README.md).
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
