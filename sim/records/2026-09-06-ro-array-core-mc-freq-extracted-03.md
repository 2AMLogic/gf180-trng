---
record: 2026-09-06-ro-array-core-mc-freq-extracted-03
date: 2026-09-06T23:17:58Z
status: valid
level: extracted

testbench:
  path: sim/tb/ro-array-core-mc-freq-extracted/tb_ro_array_core_mc_freq_extracted.sp
  sha: 7715d7beac4c9cfbc348553b8a01e1d06e4c71ba
netlist:
  path: layout/pex/ro_array_core.extracted.spice
  sha: 5a3aefd5e03c44c66f87213e6491332cd6650d60
repo_commit: 01b6c4d060ddff949cba90c49762d7d9059c431a-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: Linux-7.0.0-1010-aws-x86_64-with-glibc2.39

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: mc
  tstop: 100n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 8
seeds: [1, 2, 3, 4, 5, 6, 7, 8]

raw:
  path: sim/records/raw/2026-09-06-ro-array-core-mc-freq-extracted-03/
  files:
    - ss_125c_3.63v-run0.spice  sha256:495d5ad54700d9b3cd6d697b5f59848a4e070e3fdc2e594e5d871ea0592fd048
    - ss_125c_3.63v-run0.log  sha256:10774999a85f8d8d1269514cec389076e302eca8bac3061218604a1b34bfa04c
    - ss_125c_3.63v-run1.spice  sha256:3e4bb2a93e9e97fa861fed6cb47d19955d6baf9044805cde22ad843a511be722
    - ss_125c_3.63v-run1.log  sha256:cad2cc3c618db4fd8c89c88761701fb9e363fc22b9d3d9abc57ad89825099ac5
    - ss_125c_3.63v-run2.spice  sha256:5e24c5ff4996bb4635a9ed1f413ada16bd1824214d18898c351bab3dfa107c12
    - ss_125c_3.63v-run2.log  sha256:aa2a5e28b07130cccd443765be76ce0c541a6c95a38f54c49f9b18519457ac71
    - ss_125c_3.63v-run3.spice  sha256:32b8d2e4198e0f6cba5acf7fa71e626d2351b2c668c34107c6dc54200f4f3212
    - ss_125c_3.63v-run3.log  sha256:eccf879b26b79628cbeb13926c17a674a0f99e9db62e57a92a862a632df54609
    - ss_125c_3.63v-run4.spice  sha256:41b48e99dda674d2e57c3c0d032482be054c6bd05681aea08bb27c51da08ee60
    - ss_125c_3.63v-run4.log  sha256:524278d12483d14128e67c854f4d8a3a2db10da2c28dcaed4211c2e48087a1b4
    - ss_125c_3.63v-run5.spice  sha256:b7431bc506fcdef813afe072b077719bab949ef3384ea2cdcee62deaf133666e
    - ss_125c_3.63v-run5.log  sha256:6fb34d4e6187cc4d6970cff65561a6bb79105b86a011c904bb1c7088701ee523
    - ss_125c_3.63v-run6.spice  sha256:894126681cb09f1e8ce3ef76d8f29789389506ea0c329c414857c7e7ddc27799
    - ss_125c_3.63v-run6.log  sha256:4ae85c0fc82c3b35f79a8e6b2d2328db6e2dc77a1ebb941eb65e50b436b79d05
    - ss_125c_3.63v-run7.spice  sha256:36b4762aec4555fc70cc8b4d9b336ede97ea7ff41c329f6a9fb47b21ff7186aa
    - ss_125c_3.63v-run7.log  sha256:5bba9bbcf89de913813117c54c690f4d7cb1d539f53289e90051e5668e20a398
wall_time: 7.8m
---

## Result

- `period_r1`: mean 1.235345e-08 over 8 seeds (sd 2.463272e-11, 0.2% of mean; min 1.230631e-08, max 1.239287e-08)
- `period_r2`: mean 1.156108e-08 over 8 seeds (sd 1.697346e-11, 0.1% of mean; min 1.153980e-08, max 1.158232e-08)
- `f_r1`: mean 8.094934e+07 over 8 seeds (sd 1.615459e+05, 0.2% of mean; min 8.069156e+07, max 8.125911e+07)
- `f_r2`: mean 8.649725e+07 over 8 seeds (sd 1.269665e+05, 0.1% of mean; min 8.633847e+07, max 8.665660e+07)
- `i_r1_a`: mean -1.417476e-05 over 8 seeds (sd 5.564440e-08, 0.4% of mean; min -1.428173e-05, max -1.408330e-05)
- `i_r2_a`: mean -1.512363e-05 over 8 seeds (sd 3.902038e-08, 0.3% of mean; min -1.517855e-05, max -1.505720e-05)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 5 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 6 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 7 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 8 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, device-level-parasitic-annotated (layout/pex/build.py); NOT a full assembled-ring/inter-region routing extraction -- see layout/pex/build.py's own module docstring and sim/characterization-post-layout-extracted.md for exactly what this does and does not capture.
- Issue #146's scope note applies unchanged: two PVT points, not a full corner sweep. tt/27C/3.30V (the pre-existing nominal record) paired with ss/125C/3.63V, DR-0015's own measured entropy-binding worst corner over the array's full covered pre-layout PVT grid -- a justified subset, not the harness's full `mos` corner set (tt/ff/ss/fs/sf) x 3 temperatures x 3 supplies (45 points). `corners`/`temperatures_c` above list the two VALUES exercised (tt paired with 27C/3.30V, ss paired with 125C/3.63V) -- they are not independently swept, so do not read this as a 2x2 grid.
- 8 mismatch seeds is enough to characterize the spread's rough magnitude, not to bound a tail probability -- a claim about the FRACTION of parts that would violate the non-integer-ratio requirement needs many more samples than this record provides.
- Each seed is an independent full-array mismatch draw (both rings, the XOR gate, everything in layout/pex/ro_array_core.extracted.spice redrawn together), which is the physically correct picture for one chip -- but it means the two rings' mismatch draws are correlated only through whatever global (not per-device) variation `sw_stat_global` would add, which this testbench leaves off (sw_stat_mismatch=1, sw_stat_global=0 default): local/intra-die mismatch only, no die-to-die global corner spread on top of whichever corner is already selected.
- No deterministic negative control (sw_stat_mismatch=0) is re-run against this extracted netlist. Issue #146's pre-layout control (sim/tb/ro-array-core-mc-freq-control/, sim/records/2026-08-17-ro-array-core-mc-freq-control-{01,02}.md) already established the causal mechanism -- gf180mcu's per-corner device libraries gate mismatch's EFFECT on the model by sw_stat_mismatch regardless of which netlist instantiates those same PDK device subcircuits -- so re-running it here would confirm a mechanism this testbench's own DUT does not change, not test something new about the extracted netlist. See sim/characterization-post-layout-extracted.md.
- The mismatch model itself (gf180mcu's per-corner nfet_03v3/pfet_03v3 sw_stat_mismatch-gated local Pelgrom offsets) is unaffected by parasitic extraction: layout/pex/build.py's `klt extract --parasitics` binds each drawn device to the SAME real PDK subcircuit name design/netlist.py's schematic already instantiates (not a generic nfet/pfet class), so the corner library's mismatch model applies transparently -- see layout/pex/build.py's own module docstring.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
