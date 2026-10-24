---
record: 2026-10-13-rostage-noise-01
date: 2026-10-13T22:30:49Z
status: valid

testbench:
  path: sim/tb/rostage-noise/tb_rostage.sp
  sha: 6cb9857afd7816599a1e2937d381885bc84310be
netlist:
  path: design/ro_array_core.spice
  sha: fd0aa75500320b36f980126377e3d07c71c0e6b1
repo_commit: acbbcffbea4d61147fb2e4a7f160dd89e7c16942
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
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: noise
  tstop: n/a (small-signal: .ac and .noise, 1 kHz - 100 GHz)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-10-13-rostage-noise-01/
  files:
    - ss_125c_3.63v.spice  sha256:9648e6f9341df61551ac2cabb865288ebf52fc2f51348c3e8609b61829e9e4f9
    - ss_125c_3.63v.log  sha256:d167d1568a806f1049bed455fd079fd5bbafb817f20c81eff899456445a584b9
    - tb.manifest.json  sha256:60f3b6ab99244b284a68c9f0277b4a5cdefe0af2764d151f5aec80bba0216841
    - tb.fragment.spice  sha256:b4fd7c36df138eab5eb4751899c9c123f85f4e662fdf4c45c9610b1e4fad9060
    - dut.netlist.spice  sha256:754c20ae6474a82b1b1c7eddd566df21f70fedaafaa80350233ecc76755f931d
    - spinit  sha256:d09f10cc519effe56d97820ea6da54750a66c9ddc4561e7bda9aa77486bc5941
    - pdk-models.json  sha256:3c690a5cf6bea35bf5041b4dc0f68f0964cfbb3d82c5cd15d75922f02bd56d96
wall_time: 0.1s
---

## Result

- `vtrip`: 1.27563
- `v_starve_p_node`: 2.70795
- `v_starve_n_node`: 0.264564
- `gain_1meg`: 21.3298
- `gain_100meg`: 12.4687
- `gain_1g`: 1.91486
- `inoise_dens_1meg`: 1.249140e-07
- `inoise_dens_10meg`: 6.214340e-08
- `inoise_dens_100meg`: 5.037990e-08
- `inoise_dens_1g`: 4.170026e-08
- `inoise_dens_10g`: 2.520279e-08
- `onoise_dens_1meg`: 2.664393e-06
- `onoise_dens_1g`: 7.985005e-08
- `onoise_rms_1k_100g`: 0.013793
- `onoise_rms_100meg_100g`: 0.00734919

Runs: 1 of 1 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py rostage-noise --corners ss --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

The manifest used is snapshotted as `sim/records/raw/2026-10-13-rostage-noise-01/tb.manifest.json` (sha256 `60f3b6ab99244b284a68c9f0277b4a5cdefe0af2764d151f5aec80bba0216841`). The commands above read the CURRENT `sim/tb/rostage-noise/tb.json`; check out `repo_commit` and, if the snapshot differs from the tree (`diff`), restore the snapshot over it before re-running. See `sim/README.md`.

The SPICE inputs ngspice consumed are snapshotted next to the decks as `sim/records/raw/2026-10-13-rostage-noise-01/tb.fragment.spice` and `sim/records/raw/2026-10-13-rostage-noise-01/dut.netlist.spice` (the decks include these copies, not the working-tree files). `testbench.sha`/`netlist.sha` hash those same bytes; if they differ from the tree at `repo_commit`, the run used dirty-tree input -- restore the snapshots over the originals (in a scratch worktree) before re-running. See `sim/README.md`.

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- PDK model identity (pdk_content) covers only the 4 file(s) listed in pdk-models.json, reached from the deck's .include/.lib entry points; it was captured before the run and re-checked before this record was written, so an edit made and reverted between those two checks is not detected (see sim/README.md).
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
