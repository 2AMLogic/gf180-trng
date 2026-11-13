---
record: 2026-11-13-rostage-noise-02
date: 2026-11-13T06:35:04Z
status: valid

testbench:
  path: sim/tb/rostage-noise/tb_rostage.sp
  sha: 6cb9857afd7816599a1e2937d381885bc84310be
netlist:
  path: design/ro_array_core.spice
  sha: fd0aa75500320b36f980126377e3d07c71c0e6b1
repo_commit: fb8f44ee8f1ea0676c8c55e76fe41f5a7e732842-dirty
manifest:
  path: sim/tb/rostage-noise/tb.json
  sha: ec69fff4fb10d1ba05805fa02468dc4f7d3d4a1f
  snapshot: tb.manifest.json
  sha256: 60f3b6ab99244b284a68c9f0277b4a5cdefe0af2764d151f5aec80bba0216841
inputs:
  testbench_snapshot: tb.fragment.spice
  testbench_sha256: b4fd7c36df138eab5eb4751899c9c123f85f4e662fdf4c45c9610b1e4fad9060
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
  ngspice: "ngspice-47 : Circuit level simulation program"
  ngspice_startup: no-user-init+pinned-spinit/1
  ngspice_startup_flags: "-n"
  ngspice_startup_spinit: sim/harness/ngspice_scripts/spinit
  ngspice_startup_spinit_sha256: d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
  ngspice_startup_spinit_snapshot: spinit
  platform: Linux-7.0.0-1014-aws-x86_64-with-glibc2.39

corner:
  process: ff
  voltage: 3.300 V (nominal 3.3 V)
  temperature: -40

analysis:
  type: noise
  tstop: n/a (small-signal: .ac and .noise, 1 kHz - 100 GHz)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

stored_evidence:
  manifest: manifests/artifacts/2026-11-13-rostage-noise-02.manifest.json
  files:
    - dut.netlist.spice  size:8241  sha256:754c20ae6474a82b1b1c7eddd566df21f70fedaafaa80350233ecc76755f931d
    - ff_-40c_3.30v.log  size:1247  sha256:42c831895bf7df0506690afbf948de7cae62b311a8dfc125f92d1fccd3bc0c24
    - ff_-40c_3.30v.spice  size:2680  sha256:c2373e45d68b2afdb7d2c15287f3c41d68c3b914d11ef17aac45c974ece20169
    - pdk-models.json  size:1116  sha256:d0b1d3df67c9eb5d23d205d6298e71dfef25926ec6eac7a2ce1cec40f513094c
    - spinit  size:579  sha256:d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
    - tb.fragment.spice  size:2324  sha256:b4fd7c36df138eab5eb4751899c9c123f85f4e662fdf4c45c9610b1e4fad9060
    - tb.manifest.json  size:1320  sha256:60f3b6ab99244b284a68c9f0277b4a5cdefe0af2764d151f5aec80bba0216841
wall_time: 0.1s
---

## Result

- `vtrip`: 1.11026
- `v_starve_p_node`: 2.41664
- `v_starve_n_node`: 0.216464
- `gain_1meg`: 19.1829
- `gain_100meg`: 16.771
- `gain_1g`: 3.65294
- `inoise_dens_1meg`: 9.719636e-08
- `inoise_dens_10meg`: 4.045881e-08
- `inoise_dens_100meg`: 2.761223e-08
- `inoise_dens_1g`: 2.444460e-08
- `inoise_dens_10g`: 1.582347e-08
- `onoise_dens_1meg`: 1.864504e-06
- `onoise_dens_1g`: 8.929463e-08
- `onoise_rms_1k_100g`: 0.0104357
- `onoise_rms_100meg_100g`: 0.00719583

Runs: 1 of 1 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py rostage-noise --corners ff --temps -40 --supply 3.3 --supply-tol 0 --no-write
```

The manifest used is snapshotted as `tb.manifest.json` in the stored evidence (`manifests/artifacts/2026-11-13-rostage-noise-02.manifest.json`) (sha256 `60f3b6ab99244b284a68c9f0277b4a5cdefe0af2764d151f5aec80bba0216841`). The commands above read the CURRENT `sim/tb/rostage-noise/tb.json`; check out `repo_commit` and, if the snapshot differs from the tree (`diff`), restore the snapshot over it before re-running. See `sim/README.md`.

The SPICE inputs ngspice consumed are snapshotted next to the decks as `tb.fragment.spice` in the stored evidence (`manifests/artifacts/2026-11-13-rostage-noise-02.manifest.json`) and `dut.netlist.spice` in the stored evidence (`manifests/artifacts/2026-11-13-rostage-noise-02.manifest.json`) (the decks include these copies, not the working-tree files). `testbench.sha`/`netlist.sha` hash those same bytes; if they differ from the tree at `repo_commit`, the run used dirty-tree input -- restore the snapshots over the originals (in a scratch worktree) before re-running. See `sim/README.md`.

## Caveats

- Single corner (ff / 3.30 V / -40 C). Says nothing about any other corner.
- PDK model identity (pdk_content) covers only the 4 file(s) listed in pdk-models.json, reached from the deck's .include/.lib entry points; it was captured before the run and re-checked before this record was written, so an edit made and reverted between those two checks is not detected (see sim/README.md).
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
