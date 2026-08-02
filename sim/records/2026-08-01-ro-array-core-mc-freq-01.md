---
record: 2026-08-01-ro-array-core-mc-freq-01
date: 2026-08-01T23:46:53Z
status: valid

testbench:
  path: sim/tb/ro-array-core-mc-freq/tb_ro_array_core_mc_freq.sp
  sha: fc6fad15774723d8d6104dac70af7d0240080da3
netlist:
  path: design/ro_array_core.spice
  sha: 7e3fd56790c30d8501c5b8164dfa0be03f2d1c7e
repo_commit: dc8570a59d334bdeec04c2e284ed2dbe14a6e0de-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: statistical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

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
  path: sim/records/raw/2026-08-01-ro-array-core-mc-freq-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:f2113f427a5ed91f81fe62793beef22db880a3887bff70e8b4c960c511c27391
    - tt_27c_3.30v-run0.log  sha256:4edb285ddf9dee15e88107d8a8faff9fa3d0e418cafa8d7c762961ad8b1dc0ae
    - tt_27c_3.30v-run1.spice  sha256:db3f9a7c492ddb95e8c71e28ba84bc101cc26650c4ce1a56e0aafde523f3555b
    - tt_27c_3.30v-run1.log  sha256:bf85a9b1c4665658a424711092e7b6bb0db79a86138584e183884bd00f18e83d
    - tt_27c_3.30v-run2.spice  sha256:60dd02f3c0af071861855692db34841337d36137db3d554aafde4e734dbcbfe8
    - tt_27c_3.30v-run2.log  sha256:f0643b43ecdf14d6f65f994c9ac8f2a0dfc026ef307be485e5f7b62c4acb2bf0
    - tt_27c_3.30v-run3.spice  sha256:024c55db73cc3b267cb77c961cd0d4ac5e3e1cadce3bca6f04d3e183f6580b82
    - tt_27c_3.30v-run3.log  sha256:9e6661924c124f754c2847d059bdb96e4b3f3b659195ebf5d7d4c17ca6d154ec
    - tt_27c_3.30v-run4.spice  sha256:df8c2e1dbf7988abb687b740721558588c380ddb0b26dc8c7fe2f8f22abacfe4
    - tt_27c_3.30v-run4.log  sha256:dc96b326c4e5a6c47fbac87815f1a428a3e0eedc5b4781d8166df4f65a2c5206
    - tt_27c_3.30v-run5.spice  sha256:0ca9427f54e5a438fb9aea770f2c5b8afad4043211d6a9cff6d4ef9bfc546ae3
    - tt_27c_3.30v-run5.log  sha256:d206f827116600c7b249c90151957ef7913547e3c800ccdedb828b4d8828b59d
    - tt_27c_3.30v-run6.spice  sha256:2c2ceec209c86a31f84e9613b5c1233fe4de59f61c716f985e72d7abaeeeb67e
    - tt_27c_3.30v-run6.log  sha256:d252f7f5bef9c175841376f005a1e9af4d759af577844a9662c2f1c17c3d1e94
    - tt_27c_3.30v-run7.spice  sha256:5db4d4fd70cbdf7f46cee85c03f624b5d2b225c0a10018b69f9e3151a2a373f0
    - tt_27c_3.30v-run7.log  sha256:76e83fd4ed3b04377d84971113409f584061ab0d3b062e0ded9875aa5520b899
wall_time: 127.6m
---

## Result

- `period_r1`: mean 7.143293e-09 over 8 seeds (sd 1.679544e-11, 0.2% of mean; min 7.115543e-09, max 7.163750e-09)
- `period_r2`: mean 6.724558e-09 over 8 seeds (sd 1.130248e-11, 0.2% of mean; min 6.707478e-09, max 6.739162e-09)
- `f_r1`: mean 1.399921e+08 over 8 seeds (sd 3.293159e+05, 0.2% of mean; min 1.395917e+08, max 1.405374e+08)
- `f_r2`: mean 1.487090e+08 over 8 seeds (sd 2.500357e+05, 0.2% of mean; min 1.483864e+08, max 1.490873e+08)
- `i_r1_a`: mean -1.866785e-05 over 8 seeds (sd 9.527569e-08, 0.5% of mean; min -1.882451e-05, max -1.853640e-05)
- `i_r2_a`: mean -1.993360e-05 over 8 seeds (sd 6.714772e-08, 0.3% of mean; min -2.003787e-05, max -1.987118e-05)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-mc-freq --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 5 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 6 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 7 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 8 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- corner.process (tt) is bookkeeping only for this testbench -- the actually-loaded model section is statistical (see pdk.models), which replaces the plain per-family corner sections.
- Nominal corner only (tt/27C/3.30V). gf180mcu's `statistical` library section supplies intra-die mismatch on top of whichever corner's devices are loaded; this run does not repeat the mismatch draw at ff/ss or at temperature/supply extremes, so it says nothing about whether mismatch spread widens or narrows at those corners.
- 8 mismatch seeds is enough to characterize the spread's rough magnitude, not to bound a tail probability -- a claim about the FRACTION of parts that would violate the non-integer-ratio requirement needs many more samples than this record provides.
- Each seed is an independent full-array mismatch draw (both rings, the XOR gate, everything in design/ro_array_core.spice redrawn together), which is the physically correct picture for one chip -- but it means the two rings' mismatch draws are correlated only through whatever global (not per-device) variation `sw_stat_global` would add, which this testbench leaves off (sw_stat_mismatch=1, sw_stat_global=0 default): local/intra-die mismatch only, no die-to-die global corner spread on top of the tt corner already selected.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
