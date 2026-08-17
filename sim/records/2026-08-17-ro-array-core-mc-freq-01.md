---
record: 2026-08-17-ro-array-core-mc-freq-01
date: 2026-08-17T01:20:28Z
status: valid
supersedes: 2026-08-01-ro-array-core-mc-freq-01

testbench:
  path: sim/tb/ro-array-core-mc-freq/tb_ro_array_core_mc_freq.sp
  sha: 9a915d27dffc5e44112e9cdc67fdc4d15d761306
netlist:
  path: design/ro_array_core.spice
  sha: fd0aa75500320b36f980126377e3d07c71c0e6b1
repo_commit: 4da0bea1c43e66c3424fb5acd16a4cb30b538bba-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-47 : Circuit level simulation program"
  platform: macOS-26.6.1-arm64-arm-64bit-Mach-O

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
  path: sim/records/raw/2026-08-17-ro-array-core-mc-freq-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:8da1e826b7e20947225b6985ccc1c44b13f9b29e6ba41c2cd1ad0adba5ca7523
    - tt_27c_3.30v-run0.log  sha256:89e295efd1c9e63f02767291a4b9cfeacefe799206d6d4b205e32223584bafec
    - tt_27c_3.30v-run1.spice  sha256:149c30a5c0cfd8fd15ac59ae6392c5ccf2190f4ede89851bda272fd8db04c660
    - tt_27c_3.30v-run1.log  sha256:cbf20556e2d70290adc1be0dc3b0a68c45af3c918e378501ffc87708cef6f14f
    - tt_27c_3.30v-run2.spice  sha256:b2c5943994aec72a26ef32f20f88c914468624c1e5feb0fcc88afe01aae1407b
    - tt_27c_3.30v-run2.log  sha256:9321939557597e25ba7788ee392907cdc45e82034f314b53b145542e66af3255
    - tt_27c_3.30v-run3.spice  sha256:ab13edb9bba9af40d825ef3d1118fbe0842bbc239f8420ff55f614abf13d9716
    - tt_27c_3.30v-run3.log  sha256:d1a57bedb5d4ecce846d929d535d0ed24fa9482ab35a37b8afc755ba929d8553
    - tt_27c_3.30v-run4.spice  sha256:f3123ca52f4a18c17286a17e1b4d5934db4ccb959b9fdda5679274239dd8fb75
    - tt_27c_3.30v-run4.log  sha256:d38bed998f3f267127d701d60d22d1cf9f010da7a3602dfe12f14ff789338e88
    - tt_27c_3.30v-run5.spice  sha256:0788bbc617827e48be488cc162d39856dc7b0749bf9204c9d8cf1a2ea27e7976
    - tt_27c_3.30v-run5.log  sha256:ff93a21d3c22688e934a5b12d70b0e74539e3f665e0c87ad577a83322c933c5c
    - tt_27c_3.30v-run6.spice  sha256:1cb0432a305d40de15cdcc37fc8610ffe1e005f68c39256c908b08b2025aebe4
    - tt_27c_3.30v-run6.log  sha256:7989a6f9aa4b4b885608b91d6b2781f9e58968bd626df86ceca9f90b23db2ad1
    - tt_27c_3.30v-run7.spice  sha256:bb76201a6f1757f4edda5a03df5ba647fea0899abd2b7217dbe36581d093a155
    - tt_27c_3.30v-run7.log  sha256:79ddc1fcdfc3c618c8c9f70e285f9e024bfa9b1e74b312b94e69fbbd9aac4b8f
wall_time: 9.6m
---

## Result

- `period_r1`: mean 6.678353e-09 over 8 seeds (sd 8.425279e-12, 0.1% of mean; min 6.665373e-09, max 6.691380e-09)
- `period_r2`: mean 6.246468e-09 over 8 seeds (sd 1.021637e-11, 0.2% of mean; min 6.233927e-09, max 6.263407e-09)
- `f_r1`: mean 1.497377e+08 over 8 seeds (sd 1.888652e+05, 0.1% of mean; min 1.494460e+08, max 1.500291e+08)
- `f_r2`: mean 1.600908e+08 over 8 seeds (sd 2.616560e+05, 0.2% of mean; min 1.596575e+08, max 1.604125e+08)
- `i_r1_a`: mean -1.899629e-05 over 8 seeds (sd 6.734832e-08, 0.4% of mean; min -1.908701e-05, max -1.889389e-05)
- `i_r2_a`: mean -2.021180e-05 over 8 seeds (sd 6.109261e-08, 0.3% of mean; min -2.030106e-05, max -2.012425e-05)

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
- Run concurrently (-j 6); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Issue #146: two PVT points, not a full corner sweep. tt/27C/3.30V (the pre-existing nominal record) paired with ss/125C/3.63V, DR-0015's own measured entropy-binding worst corner over the array's full covered PVT grid -- a justified subset, not the harness's full `mos` corner set (tt/ff/ss/fs/sf) x 3 temperatures x 3 supplies (45 points), which at this testbench's ~30s/seed x 8 seeds/point cost would be affordable in wall-clock terms but was not run: the two points chosen are the ones a reader most needs (the pre-existing baseline, and the corner DR-0015 already flags as worst for this array's entropy-relevant metric). `corners`/`temperatures_c` above list the two VALUES exercised (tt paired with 27C/3.30V, ss paired with 125C/3.63V) -- they are not independently swept, so do not read this as a 2x2 grid.
- Until issue #146, `corner.process` was bookkeeping only for this testbench: `extra_lib_sections: ["statistical"]` unconditionally replaced whichever corner's own per-family sections would otherwise load (see sim/harness/runner.py's compose_deck), so every `corners` entry other than `tt` was silently a no-op -- the 2026-08-01 tt-only record's own caveat said as much. #146 removed `extra_lib_sections`: every gf180mcu per-corner device library (nfet_03v3_t/_f/_s/_fs/_sf and their pfet counterparts) already implements the identical `sw_stat_mismatch`-gated local (Pelgrom) mismatch model the `statistical` section used, so dropping `extra_lib_sections` and keeping `sw_stat_mismatch=1` lets the harness's normal per-corner `.lib` selection combine with mismatch directly -- verified empirically (composed decks differ by corner, and seeded re-runs at a fixed corner still diverge) and numerically (tt/27C spread magnitude is consistent between the two mechanisms to within the seed-to-seed noise floor) before this manifest changed.
- 8 mismatch seeds is enough to characterize the spread's rough magnitude, not to bound a tail probability -- a claim about the FRACTION of parts that would violate the non-integer-ratio requirement needs many more samples than this record provides.
- Each seed is an independent full-array mismatch draw (both rings, the XOR gate, everything in design/ro_array_core.spice redrawn together), which is the physically correct picture for one chip -- but it means the two rings' mismatch draws are correlated only through whatever global (not per-device) variation `sw_stat_global` would add, which this testbench leaves off (sw_stat_mismatch=1, sw_stat_global=0 default): local/intra-die mismatch only, no die-to-die global corner spread on top of whichever corner is already selected.
- The deterministic negative control (mismatch disabled, sw_stat_mismatch=0) is a separate testbench, sim/tb/ro-array-core-mc-freq-control/ -- tb.json's design_params are fixed per testbench, so there is no CLI flag to flip sw_stat_mismatch for a single run of this manifest.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
