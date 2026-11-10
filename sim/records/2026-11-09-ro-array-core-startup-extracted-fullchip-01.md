---
record: 2026-11-09-ro-array-core-startup-extracted-fullchip-01
date: 2026-11-09T21:51:59Z
status: valid
supersedes: 2026-10-30-ro-array-core-startup-extracted-fullchip-01

testbench:
  path: sim/tb/ro-array-core-startup-extracted-fullchip/tb_ro_array_core_startup_extracted_fullchip.sp
  sha: 7ad9155c1029a188a15cd11e94c1e4ccb9c06452
netlist:
  path: layout/pex/sampler_core.fullchip.extracted.spice
  sha: a588b74150f65f3d43e96067b9c1f03815007be4
repo_commit: 910461f4e20a99fe6369fa53beccde60370754b3-dirty
manifest:
  path: sim/tb/ro-array-core-startup-extracted-fullchip/tb.json
  sha: d5cba4f73a58c53d97c008348d6a8a9227aa17a9
  snapshot: tb.manifest.json
  sha256: c3f9bd6ef0a74091ca599bd5d2662ccdeb793b315284f3fe923d8863f740fa6b
inputs:
  testbench_snapshot: tb.fragment.spice
  testbench_sha256: a374110bc3fbd56ad6db4907a8d79d66146bf5e765fa1b01ab3424f3c319d59c
  netlist_snapshot: dut.netlist.spice
  netlist_sha256: 42db129f01dc1ba3ce4dc06d4b71cf07e7b9c1d84a546b3a5a955abb1a14b09d
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
  ngspice: "ngspice-46 : Circuit level simulation program"
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
  manifest: manifests/artifacts/2026-11-09-ro-array-core-startup-extracted-fullchip-01.manifest.json
  files:
    - combiner_sampler.routed.extracted.spice  size:68125  sha256:2e1076888602f7561a615935877f36f457678a6b59af3257071abd5c82d3bbe5
    - dut.netlist.spice  size:2183  sha256:42db129f01dc1ba3ce4dc06d4b71cf07e7b9c1d84a546b3a5a955abb1a14b09d
    - pdk-models.json  size:1116  sha256:3c690a5cf6bea35bf5041b4dc0f68f0964cfbb3d82c5cd15d75922f02bd56d96
    - ro_ring11.routed.extracted.spice  size:17465  sha256:eaba0a3c422896c360a9847017fb373856a583064b3ef1b9843ef5377dcda9e8
    - ro_ring11_ring2.routed.extracted.spice  size:17497  sha256:25835ccfb419970b26ce53280ea86562720cd33165ea4335095d64a389cffc6c
    - spinit  size:579  sha256:d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
    - ss_125c_2.97v.log  size:48223  sha256:4ce37b8a28f40cd7bbad6e8e7ec2761d1775487ab54716cbfbbe385278e7ca1b
    - ss_125c_2.97v.spice  size:4707  sha256:ef3623b27d037c0b0b9c340fb946911473143a4516ce2b929b82fd9fcb2be3ff
    - tb.fragment.spice  size:1421  sha256:a374110bc3fbd56ad6db4907a8d79d66146bf5e765fa1b01ab3424f3c319d59c
    - tb.manifest.json  size:6328  sha256:c3f9bd6ef0a74091ca599bd5d2662ccdeb793b315284f3fe923d8863f740fa6b
wall_time: 58.0s
---

## Result

- `en_assert_s`: 5.000000e-09
- `t1r1_s`: 3.143788e-08
- `t2r1_s`: 5.695068e-08
- `t3r1_s`: 8.235019e-08
- `t4r1_s`: 1.079980e-07
- `t5r1_s`: 1.335328e-07
- `t6r1_s`: 1.590127e-07
- `t7r1_s`: 1.847692e-07
- `t8r1_s`: 2.104429e-07
- `t9r1_s`: 2.362945e-07
- `t10r1_s`: 2.619269e-07
- `t1r2_s`: 2.741560e-08
- `t2r2_s`: 4.957521e-08
- `t3r2_s`: 7.183828e-08
- `t4r2_s`: 9.412088e-08
- `t5r2_s`: 1.164939e-07
- `t6r2_s`: 1.388084e-07
- `t7r2_s`: 1.613228e-07
- `t8r2_s`: 1.839029e-07
- `t9r2_s`: 2.063780e-07
- `t10r2_s`: 2.288701e-07
- `t1xo_s`: 3.036138e-08
- `t2xo_s`: 3.982809e-08
- `t3xo_s`: 5.252539e-08
- `t4xo_s`: 6.183398e-08
- `ring_swing_early_v`: 2.55432
- `ring_swing_late_v`: 2.55329
- `xo_swing_early_v`: 2.9681
- `xo_swing_late_v`: 2.97815
- `v_ro1_off_v`: 2.97
- `v_xo_off_v`: 2.828846e-07

Runs: 1 of 1 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-startup-extracted-fullchip --corners ss --temps 125 --supply 2.97 --supply-tol 0 --timeout 1800 --no-write
```

The manifest used is snapshotted as `tb.manifest.json` in the stored evidence (`manifests/artifacts/2026-11-09-ro-array-core-startup-extracted-fullchip-01.manifest.json`) (sha256 `c3f9bd6ef0a74091ca599bd5d2662ccdeb793b315284f3fe923d8863f740fa6b`). The commands above read the CURRENT `sim/tb/ro-array-core-startup-extracted-fullchip/tb.json`; check out `repo_commit` and, if the snapshot differs from the tree (`diff`), restore the snapshot over it before re-running. See `sim/README.md`.

The SPICE inputs ngspice consumed are snapshotted next to the decks as `tb.fragment.spice` in the stored evidence (`manifests/artifacts/2026-11-09-ro-array-core-startup-extracted-fullchip-01.manifest.json`) and `dut.netlist.spice` in the stored evidence (`manifests/artifacts/2026-11-09-ro-array-core-startup-extracted-fullchip-01.manifest.json`) (the decks include these copies, not the working-tree files). `testbench.sha`/`netlist.sha` hash those same bytes; if they differ from the tree at `repo_commit`, the run used dirty-tree input -- restore the snapshots over the originals (in a scratch worktree) before re-running. See `sim/README.md`.

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- PDK model identity (pdk_content) covers only the 4 file(s) listed in pdk-models.json, reached from the deck's .include/.lib entry points; it was captured before the run and re-checked before this record was written, so an edit made and reverted between those two checks is not detected (see sim/README.md).
- DUT is the schematic-derived netlist sampler_core.fullchip.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, FULL-CHIP-DELTA-annotated for the ro1/ro2 inter-region trunks ONLY (layout/pex/build.py); every other inter-region trunk is unpriced by this composition -- see DR-0025 and layout/pex/build.py's own module docstring for the full accounting.
- CELL-INSTANCE GRANULARITY, NOT TRANSISTOR LEVEL (DR-0025): the inter-region parasitics this DUT carries were measured by a full-chip `klt extract --parasitics` run over layout/floorplan/trng_floorplan.gds in which every one of digital's ~2500 gf180mcu_fd_sc_mcu9t5v0__* standard-cell instances was abstracted as an opaque black box -- the same granularity the composed LVS already uses. No number in this record is evidence about any standard cell's own devices, and digital is not instantiated in this deck at all.
- clk/rst_n are tied STATIC (clk=0, rst_n=vdd_val) -- this testbench measures the ring array's own start-up transient, not sampler activity.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for time-to-first-valid (ss/+125 C/2.97 V), the same point issues #17/#217's own records used -- not the full 27-point grid.
- Deterministic (noiseless) transient started from the operating point ngspice solves with en = 0, same as the leaf-level and routing-level families -- no .ic kick used or needed.
- v(xdut.rn1)/v(xdut.rn2) address the ring's own output AFTER the DR-0025 delta but BEFORE the buffer (this composition's own internal net names, unchanged from the routing-level family's identical convention); v(xdut.xcs.xo) moves one hierarchy hop deeper than the routing-level family's v(xo), because the buffer/XOR stage now lives inside the fully assembled combiner_sampler wrapper -- see this testbench's own .sp header.
- clk/rst_n arrival is still driven from an ideal, zero-impedance source at combiner_sampler's own pins (tied off entirely in this testbench) -- this record says nothing about clock-tree arrival at the sampler, per DR-0025.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
