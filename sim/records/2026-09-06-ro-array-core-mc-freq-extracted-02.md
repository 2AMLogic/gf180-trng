---
record: 2026-09-06-ro-array-core-mc-freq-extracted-02
date: 2026-09-06T23:08:21Z
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
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: Linux-7.0.0-1010-aws-x86_64-with-glibc2.39

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
  path: sim/records/raw/2026-09-06-ro-array-core-mc-freq-extracted-02/
  files:
    - tt_27c_3.30v-run0.spice  sha256:75f7d054e19e3c206133a4785e5c39f88dec67b5506f88b6fa71fe7e63e3c3e7
    - tt_27c_3.30v-run0.log  sha256:f21c81926d6950c057b7ef100871b816832e0932a8bcb8bf7376438e44674f0b
    - tt_27c_3.30v-run1.spice  sha256:9752dd793dab268eb8e254520703db710bbf923da9ed25ac4767d127d78174d0
    - tt_27c_3.30v-run1.log  sha256:20b5cc16a55e5d0392f7a7899a4c3b317ffe11a8c8fac837afe3d056a0fcc0c5
    - tt_27c_3.30v-run2.spice  sha256:b003111a7e059c735e895371d6e331818ec4eaf3dad8ff8b0b955030bf0d90fe
    - tt_27c_3.30v-run2.log  sha256:102c90e9b0a8493ce34ede3b687f1ada7f86a076d2d7c18932fc1c8678be4bca
    - tt_27c_3.30v-run3.spice  sha256:b0492e18acc639454d615b06c0a0d2d97553501a682724d13604b57a1f5823ca
    - tt_27c_3.30v-run3.log  sha256:69d5a1fc29da31fdb4ac9117026a5c86ad384b04fe4ef3278831874ccba9d72c
    - tt_27c_3.30v-run4.spice  sha256:7558b23aee21474cd504b4a4d13bac89b968f6d9fb69f77ce7b50fb2a1452263
    - tt_27c_3.30v-run4.log  sha256:2869eb95ea2e8abde9a8afd53dd03756ef82d67d46d5346937a97a73c62ee6da
    - tt_27c_3.30v-run5.spice  sha256:31d6c36e2d7d2706b9340daaf036604b54576efdaef5155d7a040cba4c809b74
    - tt_27c_3.30v-run5.log  sha256:7da7822e7bdab4af594e195bba07c4b63285c91c96ccfb240e9777860ea575bb
    - tt_27c_3.30v-run6.spice  sha256:ee8d268d949ba95e01731c786cd7e2de551b0f94ca31ff5436973be1a0eda1a4
    - tt_27c_3.30v-run6.log  sha256:7a02a104f2667beb3016eac16ac7a06ec84c1fd5ec435f9b2b334f85ee94895e
    - tt_27c_3.30v-run7.spice  sha256:2362675eea8da30e231a1b47e5f118a6400ad92d08b6f819181044cfdb58590b
    - tt_27c_3.30v-run7.log  sha256:a38a4b2e92483781dc8328de22bb14d27394b1c607def593ef0c8ee02e99bb89
wall_time: 9.4m
---

## Result

- `period_r1`: mean 8.399266e-09 over 8 seeds (sd 1.899443e-11, 0.2% of mean; min 8.363797e-09, max 8.429142e-09)
- `period_r2`: mean 7.887913e-09 over 8 seeds (sd 1.268423e-11, 0.2% of mean; min 7.871035e-09, max 7.904930e-09)
- `f_r1`: mean 1.190586e+08 over 8 seeds (sd 2.694761e+05, 0.2% of mean; min 1.186360e+08, max 1.195629e+08)
- `f_r2`: mean 1.267765e+08 over 8 seeds (sd 2.038318e+05, 0.2% of mean; min 1.265033e+08, max 1.270481e+08)
- `i_r1_a`: mean -1.900532e-05 over 8 seeds (sd 8.843149e-08, 0.5% of mean; min -1.917308e-05, max -1.886476e-05)
- `i_r2_a`: mean -2.020370e-05 over 8 seeds (sd 6.323368e-08, 0.3% of mean; min -2.030171e-05, max -2.010061e-05)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 5 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 6 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 7 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 8 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
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
