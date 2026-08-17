---
record: 2026-08-17-ro-array-core-mc-freq-02
date: 2026-08-17T01:22:52Z
status: valid

testbench:
  path: sim/tb/ro-array-core-mc-freq/tb_ro_array_core_mc_freq.sp
  sha: 9a915d27dffc5e44112e9cdc67fdc4d15d761306
netlist:
  path: design/ro_array_core.spice
  sha: fd0aa75500320b36f980126377e3d07c71c0e6b1
repo_commit: 4da0bea1c43e66c3424fb5acd16a4cb30b538bba-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-47 : Circuit level simulation program"
  platform: macOS-26.6.1-arm64-arm-64bit-Mach-O

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
  path: sim/records/raw/2026-08-17-ro-array-core-mc-freq-02/
  files:
    - ss_125c_3.63v-run0.spice  sha256:a9a34a1d15962f99e50fa16c722842c14f6250b0d19d2b92af2c23e7e2090418
    - ss_125c_3.63v-run0.log  sha256:8af53c0a7abe2759a75aa3f6be7607e8780e606fa82fad62b4a53db3b0a7896c
    - ss_125c_3.63v-run1.spice  sha256:6207584c69e07b516d407b8863275604a08340948db49a9fc0f9b8f7852b646a
    - ss_125c_3.63v-run1.log  sha256:cc795cd3b7e31509ea4e948d707599bb06403639518af9da9b800f44d156f423
    - ss_125c_3.63v-run2.spice  sha256:5e50d3bb3552d3398497964f66085f0b720f35700f860d828a2fff0fa425d63f
    - ss_125c_3.63v-run2.log  sha256:a1cd1f2aa8ef369d01011079d220e4dcb7881455cbd774ee6ef5f70743f6290e
    - ss_125c_3.63v-run3.spice  sha256:22860203fb3533c28267e737f869d8a7ad8668418007e26c124741b162279f06
    - ss_125c_3.63v-run3.log  sha256:eddf4fb39cc1b03513e37d73272e64e1db12fa6135c674953454ba38ab54baef
    - ss_125c_3.63v-run4.spice  sha256:255383d139e7f3e27b25eb4b52f95b89f4fe994bda8ac807d47dc1311dd6105c
    - ss_125c_3.63v-run4.log  sha256:a087544001d55a924df0202e17e1174575ab592932a84cc2a16bd7a5caaa2d9b
    - ss_125c_3.63v-run5.spice  sha256:946c2c9d81f54b95258d1493fb7543cc714ccc28179915dbdf3f7e9748eac517
    - ss_125c_3.63v-run5.log  sha256:c3e0c0cce4b3a0ed5d0be9b4dab7d4eb1f7210dc6471951978f9537d2f103bc4
    - ss_125c_3.63v-run6.spice  sha256:b0a88bcc96089eb3ff752cb595ffc0e363baecf70409718c7f5cc7df553fca54
    - ss_125c_3.63v-run6.log  sha256:cc775b4af4a87be868d34a27b6d57634decfeaa2a83c2aab876eafd428f97376
    - ss_125c_3.63v-run7.spice  sha256:6cfc4f5d431b5691a3a8c41309209daf0e6dcfea6f27716150bed23e0c4b4c6a
    - ss_125c_3.63v-run7.log  sha256:04eed17c8eb8134b8d9c7ca7e252e1d42d63a3a516cfaa48a0e39b5a219c79bd
wall_time: 10.1m
---

## Result

- `period_r1`: mean 9.582451e-09 over 8 seeds (sd 1.030583e-11, 0.1% of mean; min 9.569330e-09, max 9.600578e-09)
- `period_r2`: mean 8.933668e-09 over 8 seeds (sd 1.234476e-11, 0.1% of mean; min 8.919292e-09, max 8.954485e-09)
- `f_r1`: mean 1.043575e+08 over 8 seeds (sd 1.121721e+05, 0.1% of mean; min 1.041604e+08, max 1.045005e+08)
- `f_r2`: mean 1.119363e+08 over 8 seeds (sd 1.545792e+05, 0.1% of mean; min 1.116759e+08, max 1.121165e+08)
- `i_r1_a`: mean -1.509650e-05 over 8 seeds (sd 4.657207e-08, 0.3% of mean; min -1.515962e-05, max -1.502736e-05)
- `i_r2_a`: mean -1.611399e-05 over 8 seeds (sd 4.312885e-08, 0.3% of mean; min -1.617744e-05, max -1.604901e-05)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-mc-freq --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 5 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 6 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 7 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 8 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
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
