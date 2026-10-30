---
record: 2026-10-30-ro-array-core-startup-extracted-fullchip-control-01
date: 2026-10-30T17:19:08Z
status: valid
supersedes: 2026-09-12-ro-array-core-startup-extracted-fullchip-control-01

testbench:
  path: sim/tb/ro-array-core-startup-extracted-fullchip-control/tb_ro_array_core_startup_extracted_fullchip_control.sp
  sha: de7105e97fa94e59881d031499b1b58cd50d5b8a
netlist:
  path: layout/pex/sampler_core.routed.extracted.spice
  sha: 4bf8c65adc37dad04d75c4641f81e4bfbb09ee4d
repo_commit: 88bcc15c65fe5cf4c9e8616f6cec162db015f23e-dirty
manifest:
  path: sim/tb/ro-array-core-startup-extracted-fullchip-control/tb.json
  sha: 28901c4966e13fad5e48c76ed3ca95e8504acac1
  snapshot: tb.manifest.json
  sha256: 805b6f679e844544e42408561c2e2e799ee67d881dff92f7bc86fe93bd8e7c20
inputs:
  testbench_snapshot: tb.fragment.spice
  testbench_sha256: f99124c20438118d439cea5ab3a5b3d291b8d0e05fb436d0a6e36cc2c54a9f51
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
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: tran
  tstop: 280n
  tstep: 2p (print step; ngspice's own LTE sets the actual solver step; same window as the routing-level family -- see that family's own tb.json for the 180n->280n widening derivation this family inherits unchanged).
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

stored_evidence:
  manifest: manifests/artifacts/2026-10-30-ro-array-core-startup-extracted-fullchip-control-01.manifest.json
  files:
    - combiner_sampler.routed.extracted.spice  size:67970  sha256:859c0ccd81bf2911f3b4f32b05cad90430b8a192cc51c98429a48d7e490c61fc
    - dut.netlist.spice  size:1670  sha256:4a2277125643c21766860230555691d955cfdff0877bd375930300d4e27e6e2c
    - pdk-models.json  size:1116  sha256:3c690a5cf6bea35bf5041b4dc0f68f0964cfbb3d82c5cd15d75922f02bd56d96
    - ro_ring11.routed.extracted.spice  size:17250  sha256:39739d9926aa9fe15a3c1379bf7384c98da3f07175a9bbbe795483195e55cc57
    - ro_ring11_ring2.routed.extracted.spice  size:17279  sha256:4fc7769fb0429e7229bb43edab8447f5e7a002b0e4da629331895103e7e17bf0
    - spinit  size:579  sha256:d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
    - ss_125c_2.97v.log  size:46878  sha256:157c9aef7f01405d646116356c46e90287e1b7a2c0a363cff95146a32f4d07b1
    - ss_125c_2.97v.spice  size:4731  sha256:11f491bbe3c67edff2c6a04b5c6126463da3e3fb69868dc7c0a856ef80c60b82
    - tb.fragment.spice  size:1983  sha256:f99124c20438118d439cea5ab3a5b3d291b8d0e05fb436d0a6e36cc2c54a9f51
    - tb.manifest.json  size:6814  sha256:805b6f679e844544e42408561c2e2e799ee67d881dff92f7bc86fe93bd8e7c20
wall_time: 52.6s
---

## Result

- `en_assert_s`: 5.000000e-09
- `t1r1_s`: 2.771575e-08
- `t2r1_s`: 5.021660e-08
- `t3r1_s`: 7.286744e-08
- `t4r1_s`: 9.552654e-08
- `t5r1_s`: 1.181626e-07
- `t6r1_s`: 1.408128e-07
- `t7r1_s`: 1.633684e-07
- `t8r1_s`: 1.861248e-07
- `t9r1_s`: 2.087615e-07
- `t10r1_s`: 2.314696e-07
- `t1r2_s`: 2.610308e-08
- `t2r2_s`: 4.715414e-08
- `t3r2_s`: 6.827145e-08
- `t4r2_s`: 8.941549e-08
- `t5r2_s`: 1.105803e-07
- `t6r2_s`: 1.317999e-07
- `t7r2_s`: 1.529976e-07
- `t8r2_s`: 1.741327e-07
- `t9r2_s`: 1.954715e-07
- `t10r2_s`: 2.167401e-07
- `t1xo_s`: 2.888882e-08
- `t2xo_s`: 3.836649e-08
- `t3xo_s`: 5.000406e-08
- `t4xo_s`: 5.933416e-08
- `ring_swing_early_v`: 2.85446
- `ring_swing_late_v`: 2.83882
- `xo_swing_early_v`: 2.51369
- `xo_swing_late_v`: 2.98335
- `v_ro1_off_v`: 2.97
- `v_xo_off_v`: 2.531749e-07

Runs: 1 of 1 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-startup-extracted-fullchip-control --corners ss --temps 125 --supply 2.97 --supply-tol 0 --timeout 1800 --no-write
```

The manifest used is snapshotted as `tb.manifest.json` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-startup-extracted-fullchip-control-01.manifest.json`) (sha256 `805b6f679e844544e42408561c2e2e799ee67d881dff92f7bc86fe93bd8e7c20`). The commands above read the CURRENT `sim/tb/ro-array-core-startup-extracted-fullchip-control/tb.json`; check out `repo_commit` and, if the snapshot differs from the tree (`diff`), restore the snapshot over it before re-running. See `sim/README.md`.

The SPICE inputs ngspice consumed are snapshotted next to the decks as `tb.fragment.spice` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-startup-extracted-fullchip-control-01.manifest.json`) and `dut.netlist.spice` in the stored evidence (`manifests/artifacts/2026-10-30-ro-array-core-startup-extracted-fullchip-control-01.manifest.json`) (the decks include these copies, not the working-tree files). `testbench.sha`/`netlist.sha` hash those same bytes; if they differ from the tree at `repo_commit`, the run used dirty-tree input -- restore the snapshots over the originals (in a scratch worktree) before re-running. See `sim/README.md`.

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- PDK model identity (pdk_content) covers only the 4 file(s) listed in pdk-models.json, reached from the deck's .include/.lib entry points; it was captured before the run and re-checked before this record was written, so an edit made and reverted between those two checks is not detected (see sim/README.md).
- DUT is the schematic-derived netlist sampler_core.routed.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- ZERO-DELTA CONTROL for sim/tb/ro-array-core-startup-extracted-fullchip/: this deck is byte-identical to that one except for its own header comment and the DUT subcircuit name (sampler_core_routed_extracted here, sampler_core_fullchip_extracted there), so the difference between this record and its -extracted-fullchip sibling at the same PVT point is EXACTLY what layout/pex/build.py's full-chip composition adds (DR-0025's ro1/ro2 inter-region trunk delta, plus the four disclosed driver-side-only output-load capacitors) and nothing else. It exists because the pre-existing -extracted-routed record of this family is composed from ro_array_core's topology, not sampler_core's, so it is NOT a valid subtraction baseline for the inter-region delta on its own -- see sim/characterization-post-layout-extracted.md section 8.
- Carries NO inter-region parasitic at all (that is the point of a control): the DUT is layout/pex/sampler_core.routed.extracted.spice, the same intra-region routing-level composition issue #217 recorded, per DR-0024.
- clk/rst_n are tied STATIC (clk=0, rst_n=vdd_val) -- this testbench measures the ring array's own start-up transient, not sampler activity.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for time-to-first-valid (ss/+125 C/2.97 V), the same point issues #17/#217's own records used -- not the full 27-point grid.
- Deterministic (noiseless) transient started from the operating point ngspice solves with en = 0, same as the leaf-level and routing-level families -- no .ic kick used or needed.
- v(xdut.rn1)/v(xdut.rn2) address the ring's own output AFTER the DR-0025 delta but BEFORE the buffer (this composition's own internal net names, unchanged from the routing-level family's identical convention); v(xdut.xcs.xo) moves one hierarchy hop deeper than the routing-level family's v(xo), because the buffer/XOR stage now lives inside the fully assembled combiner_sampler wrapper -- see this testbench's own .sp header.
- clk/rst_n arrival is still driven from an ideal, zero-impedance source at combiner_sampler's own pins (tied off entirely in this testbench) -- this record says nothing about clock-tree arrival at the sampler, per DR-0025.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
