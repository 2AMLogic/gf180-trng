---
record: 2026-11-09-ro-array-core-power-split-02
date: 2026-11-09T21:56:36Z
status: valid

testbench:
  path: sim/tb/ro-array-core-power-split/tb_ro_array_core_power_split.sp
  sha: 55a62749c34d220e65be363dd5c5e93b666823cf
netlist:
  path: design/ro_array_core.spice
  sha: fd0aa75500320b36f980126377e3d07c71c0e6b1
repo_commit: 910461f4e20a99fe6369fa53beccde60370754b3-dirty
manifest:
  path: sim/tb/ro-array-core-power-split/tb.json
  sha: 287102276faa91e3b3e5b991b027ac5075cd7d62
  snapshot: tb.manifest.json
  sha256: 7907dce4a68807157e035e03b67300567da3106d9cdf2a5d50f350088cfbce6e
inputs:
  testbench_snapshot: tb.fragment.spice
  testbench_sha256: fcfd0d1406280b8aaacf03666e0100d91ff5ea3b9ac0aa069ded5dc586a06322
  netlist_snapshot: dut.netlist.spice
  netlist_sha256: 754c20ae6474a82b1b1c7eddd566df21f70fedaafaa80350233ecc76755f931d

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
  tstop: 300n
  tstep: 5p (print step; it also caps ngspice's own solver step, as in ro-array-core-pvt-q)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

stored_evidence:
  manifest: manifests/artifacts/2026-11-09-ro-array-core-power-split-02.manifest.json
  files:
    - dut.netlist.spice  size:8241  sha256:754c20ae6474a82b1b1c7eddd566df21f70fedaafaa80350233ecc76755f931d
    - ff_-40c_3.63v.log  size:8988  sha256:e2b75dc14c493fa2a108b71e063c83ba950a097691b12612f6709c6d6348e0d2
    - ff_-40c_3.63v.spice  size:3962  sha256:5f8e8fa9a92eb84a1d93d110d2ea585f1296dc59c54104e75a2eeae168c7a7e5
    - pdk-models.json  size:1116  sha256:d0b1d3df67c9eb5d23d205d6298e71dfef25926ec6eac7a2ce1cec40f513094c
    - spinit  size:579  sha256:d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
    - tb.fragment.spice  size:2369  sha256:fcfd0d1406280b8aaacf03666e0100d91ff5ea3b9ac0aa069ded5dc586a06322
    - tb.manifest.json  size:4472  sha256:7907dce4a68807157e035e03b67300567da3106d9cdf2a5d50f350088cfbce6e
wall_time: 10.5s
---

## Result

- `period_r1`: 4.015721e-09
- `period_r2`: 3.773217e-09
- `f_r1`: 2.490213e+08
- `f_r2`: 2.650258e+08
- `i_r1_a`: -3.649720e-05
- `i_r2_a`: -3.874381e-05
- `i_buf1_a`: -8.196189e-06
- `i_buf2_a`: -8.835825e-06
- `i_xor_a`: -1.656296e-05
- `i_tree_a`: -3.359497e-05
- `ring_swing_v`: 3.80883
- `xo_swing_v`: 3.76987
- `p_rings_w`: -2.731249e-04
- `p_buf1_w`: -2.975216e-05
- `p_buf2_w`: -3.207405e-05
- `p_bufs_w`: -6.182621e-05
- `p_xor_w`: -6.012355e-05
- `p_tree_w`: -1.219498e-04
- `p_total_w`: -3.950746e-04
- `xo_trans_per_s`: 1.028094e+09

Runs: 1 of 1 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power-split --corners ff --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

The manifest used is snapshotted as `tb.manifest.json` in the stored evidence (`manifests/artifacts/2026-11-09-ro-array-core-power-split-02.manifest.json`) (sha256 `7907dce4a68807157e035e03b67300567da3106d9cdf2a5d50f350088cfbce6e`). The commands above read the CURRENT `sim/tb/ro-array-core-power-split/tb.json`; check out `repo_commit` and, if the snapshot differs from the tree (`diff`), restore the snapshot over it before re-running. See `sim/README.md`.

The SPICE inputs ngspice consumed are snapshotted next to the decks as `tb.fragment.spice` in the stored evidence (`manifests/artifacts/2026-11-09-ro-array-core-power-split-02.manifest.json`) and `dut.netlist.spice` in the stored evidence (`manifests/artifacts/2026-11-09-ro-array-core-power-split-02.manifest.json`) (the decks include these copies, not the working-tree files). `testbench.sha`/`netlist.sha` hash those same bytes; if they differ from the tree at `repo_commit`, the run used dirty-tree input -- restore the snapshots over the originals (in a scratch worktree) before re-running. See `sim/README.md`.

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- PDK model identity (pdk_content) covers only the 4 file(s) listed in pdk-models.json, reached from the deck's .include/.lib entry points; it was captured before the run and re-checked before this record was written, so an edit made and reverted between those two checks is not detected (see sim/README.md).
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Single corner (ff / -40 C / 3.63 V), the corner at which the array term of the whole-block active power binds. Says nothing about any other corner.
- The deck instantiates ro_ring11, ro_buf and xor2 directly because ro_array_core has one vdd pin; sim/tests/test_active_power_breakdown.py pins the instance set and connectivity to design/ro_array_core.spice. The only electrical difference from the shipped array is the metering split of vdd into vddb1, vddb2 and vddx, all zero-impedance taps off the same ideal vsup.
- Reconciliation target: sim/records/2026-08-02-ro-array-core-pvt-q-39.md (same corner), whose p_total_w - p_rings_w is 120.033 uW. This deck's p_tree_w (buffers + XOR) is 121.950 uW, +1.60 % from it, inside the 2 % tolerance sim/tools/active_power_breakdown.py enforces. The residual is not attributed: the two records were minted on different hosts and PDK checkouts, and the rings agree to 0.0004 % (273.125 vs 273.125 uW), so it sits in the tree branch.
- p_bufs_w + p_xor_w (= p_tree_w) is the whole power of the buffers and the XOR, not a recoverable amount: they must still drive the sampler. It is an upper bound on what any trim in that row could return.
- The XOR current depends on input activity; its inputs here are the free-running rings' buffered outputs, as in ro-array-core-pvt-q.
- Deterministic (mismatch-free, noiseless) transient: one nominal device draw. Neither mismatch nor jitter is measured.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
