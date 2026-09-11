---
record: 2026-09-11-ro-array-core-mc-freq-extracted-routed-01
date: 2026-09-11T06:41:16Z
status: valid

testbench:
  path: sim/tb/ro-array-core-mc-freq-extracted-routed/tb_ro_array_core_mc_freq_extracted_routed.sp
  sha: 09d1055aaad1beb20c6b4409d18f9aa61ac71c6f
netlist:
  path: layout/pex/ro_array_core.routed.extracted.spice
  sha: e93c6e814579300acca643741bc1f2acffe87817
repo_commit: 383df4f16948d3118bbb9b3a4614e274b5875c9f-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /Users/rwalters/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6.2-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: mc
  tstop: 100n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 8
seeds: [1, 2, 3, 4, 5, 6, 7, 8]

raw:
  path: sim/records/raw/2026-09-11-ro-array-core-mc-freq-extracted-routed-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:a2a862f62dbce2a8fdb4a921bf95cb06b815ef413df77e7abd08e12caeb4ce4c
    - tt_27c_3.30v-run0.log  sha256:076d28aede78066f28ae9955c6cec3974442f7c61d89e0c7ecfc4a42223d5639
    - tt_27c_3.30v-run1.spice  sha256:cd3a5a6c9c83856e3d7a2be2cbc3bd17a2f48ab1c6950248de166175b9fb3e2f
    - tt_27c_3.30v-run1.log  sha256:7a82104d44d256dd7ccbc79a0dc10c727400adf34392aaabd46eb1621e343260
    - tt_27c_3.30v-run2.spice  sha256:9ba346ab74458a411dfb4a265eb46fd7df2bc33f6df9935131b2a1eb99ed311f
    - tt_27c_3.30v-run2.log  sha256:4427cfbbc3b5a1756af329ce162e5d8c4ef1b9496b65a2ccbf8dd830a2171154
    - tt_27c_3.30v-run3.spice  sha256:2d9ace77e4aa2ee1d16639c5d46519eafad07bd620cc13dc9fb4cb014f94890f
    - tt_27c_3.30v-run3.log  sha256:9ab0c5fd873ef43fa9ff675862dc22436a0122ba6a3a24b777323fd6a7d179e4
    - tt_27c_3.30v-run4.spice  sha256:9c04ac649b67286051700f1a3a8dd4710e725838d0ddbb6789444ade26fe9108
    - tt_27c_3.30v-run4.log  sha256:c00db3c0cb9224628a91ac55f71744f0fbaa54c43cca4d0f2bd55577b46b6389
    - tt_27c_3.30v-run5.spice  sha256:53683d4fffe128b9c39424387c40ffa22433c6d59c906918d9562fc14bc8d6d8
    - tt_27c_3.30v-run5.log  sha256:30b3c5e8c01423ab6496c68da49b3a9fe92297b20339dbff922a72d14bfe44bc
    - tt_27c_3.30v-run6.spice  sha256:8068821746572feb97e21ec449164c63071c730c5e5ffb2c606d4755823f4bd5
    - tt_27c_3.30v-run6.log  sha256:48487ee5dcd573737af156f960d7465304085ab85e92d8f6c48d755a96bbc3a9
    - tt_27c_3.30v-run7.spice  sha256:19636c1861054a147705ad5fb969325597812acadaa06056a8d24b4c611d1fdd
    - tt_27c_3.30v-run7.log  sha256:fc3a25c3d273a96da9b40f1b2666ebdc5eed91381aa9c489d49aaef13bd0777f
wall_time: 10.9m
---

## Result

- `period_r1`: mean 1.181151e-08 over 8 seeds (sd 1.535459e-11, 0.1% of mean; min 1.178832e-08, max 1.183484e-08)
- `period_r2`: mean 1.122630e-08 over 8 seeds (sd 2.899247e-11, 0.3% of mean; min 1.116137e-08, max 1.125924e-08)
- `f_r1`: mean 8.466333e+07 over 8 seeds (sd 1.100709e+05, 0.1% of mean; min 8.449625e+07, max 8.482975e+07)
- `f_r2`: mean 8.907707e+07 over 8 seeds (sd 2.308472e+05, 0.3% of mean; min 8.881592e+07, max 8.959476e+07)
- `i_r1_a`: mean -1.870275e-05 over 8 seeds (sd 4.976857e-08, 0.3% of mean; min -1.877645e-05, max -1.863108e-05)
- `i_r2_a`: mean -1.958411e-05 over 8 seeds (sd 8.399748e-08, 0.4% of mean; min -1.977440e-05, max -1.950916e-05)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 5 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 6 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 7 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 8 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.routed.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, ROUTING-level-parasitic-annotated for both rings (layout/pex/build.py); the buffer/XOR stage remains device-level (leaf-cell) -- see layout/pex/build.py's own module docstring, 'Two composed drop-ins, different scope', and sim/characterization-post-layout-extracted.md's 2026-09-11 delta section.
- Two PVT points, not a full corner sweep, matching the leaf-level family and issue #146's own scope note: tt/27C/3.30V paired with ss/125C/3.63V (DR-0015's own measured entropy-binding worst corner). `corners`/`temperatures_c` above list the two VALUES exercised -- they are not independently swept, so do not read this as a 2x2 grid.
- 8 mismatch seeds is enough to characterize the spread's rough magnitude, not to bound a tail probability.
- Each seed is an independent full-array mismatch draw (both rings' own routed extraction, redrawn together), the physically correct picture for one chip -- but the two rings' mismatch draws are correlated only through whatever global (not per-device) variation sw_stat_global would add, which this testbench leaves off.
- No deterministic negative control (sw_stat_mismatch=0) is re-run against this routed netlist, for the same reason the leaf-level family gives: gf180mcu's per-corner device libraries gate mismatch's EFFECT on the model by sw_stat_mismatch regardless of which netlist instantiates those same PDK device subcircuits.
- The mismatch model itself is unaffected by which composition path extracted the devices: layout/pex/build.py's `klt extract --parasitics` binds each drawn device to the SAME real PDK subcircuit name design/netlist.py's schematic already instantiates, whether extracted at leaf level or from the assembled ring GDS -- see layout/pex/build.py's own module docstring.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
