---
record: 2026-09-11-ro-array-core-mc-freq-extracted-routed-02
date: 2026-09-11T07:18:36Z
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
  - /Users/rwalters/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6.2-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: mc
  tstop: 160n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step). Window widened from the leaf-level family's 100n -- see the 'widened window' caveat below.
  tmax: n/a
  noise_params: n/a
  runs: 8
seeds: [1, 2, 3, 4, 5, 6, 7, 8]

raw:
  path: sim/records/raw/2026-09-11-ro-array-core-mc-freq-extracted-routed-02/
  files:
    - ss_125c_3.63v-run0.spice  sha256:9329bb4879701f02ae8247cacc58cf83ca5a98eecd1b681d88000527402356a8
    - ss_125c_3.63v-run0.log  sha256:78ae2365eab47842eb0b86136cdd8ce72c310f0db83896075546213c794c4c19
    - ss_125c_3.63v-run1.spice  sha256:197167d20cf54ce10d3498dc4f40ecb99ef27d1fa4685a40ae66b725073ff7ba
    - ss_125c_3.63v-run1.log  sha256:f172be8c9aec88a0d95d8f900fd43d904bc2d7efabd7125e114318c639fa4b8e
    - ss_125c_3.63v-run2.spice  sha256:96a02b5e20e49df528947131aa24a9bd6898f0f3c88b2caa6067d86fdd0926a0
    - ss_125c_3.63v-run2.log  sha256:df4ac3fb2ec2b43e995087e451fcdd3a088174ba57c8ba17116501f1bcbf43e8
    - ss_125c_3.63v-run3.spice  sha256:5485f6d074b4a4cb5f4e383162718d874be6f017139081dfcbbe73839313af3d
    - ss_125c_3.63v-run3.log  sha256:01457b66ad20cfb8de568d2aa4779795ff72333842e7555794bbc2bf30d324de
    - ss_125c_3.63v-run4.spice  sha256:4af66702ba1a5393325b154aad3102f484af5e2ffb0d836f47fd61c90a67c8d2
    - ss_125c_3.63v-run4.log  sha256:a2fce65a3e52621ab15beaaabb5a2d879e0dce3182996292139b813c01ca6553
    - ss_125c_3.63v-run5.spice  sha256:e4eac25a0fb8ffb354170611b01ce783df65c82a4ebd26057dce38302b83e6c9
    - ss_125c_3.63v-run5.log  sha256:0efc821443a89f9b8a471a489fe5fb8af2604cb7f386ce65fd754dc96e0bd9a8
    - ss_125c_3.63v-run6.spice  sha256:4c76e2454d81584f4e1aea2818cc78884bdf5bf7738e70388cab25d3734e9e83
    - ss_125c_3.63v-run6.log  sha256:21c1d9926c5df35819abadb73de99b8eea9deb48658cd0afdc53d05aa6dc059e
    - ss_125c_3.63v-run7.spice  sha256:df476713f36b826e57f5d7e98f8b955db311b401455ea6375ce5da463680866c
    - ss_125c_3.63v-run7.log  sha256:cad6a568845da0bd3ee95c0a989f7f1b8bef18a3aad056cef1627a4b53cf50cd
wall_time: 25.1m
---

## Result

- `period_r1`: mean 1.741262e-08 over 6 seeds (sd 2.384813e-11, 0.1% of mean; min 1.738650e-08, max 1.745142e-08)
- `period_r2`: mean 1.647366e-08 over 6 seeds (sd 4.200349e-11, 0.3% of mean; min 1.639478e-08, max 1.651969e-08)
- `f_r1`: mean 5.742971e+07 over 6 seeds (sd 78613.8, 0.1% of mean; min 5.730194e+07, max 5.751590e+07)
- `f_r2`: mean 6.070331e+07 over 6 seeds (sd 1.551922e+05, 0.3% of mean; min 6.053382e+07, max 6.099503e+07)
- `i_r1_a`: mean -1.389167e-05 over 6 seeds (sd 3.287778e-08, 0.2% of mean; min -1.393146e-05, max -1.384364e-05)
- `i_r2_a`: mean -1.462616e-05 over 6 seeds (sd 6.104674e-08, 0.4% of mean; min -1.474270e-05, max -1.457232e-05)

Run failures:
- seed 1: timeout -- ngspice timed out: no result after 300.3s (bound 300s + 30s kill-grace), killed by timeout(1)/gtimeout via process-group SIGKILL; deck ss_125c_3.63v-run0.spice
- seed 2: timeout -- ngspice timed out: no result after 300.2s (bound 300s + 30s kill-grace), killed by timeout(1)/gtimeout via process-group SIGKILL; deck ss_125c_3.63v-run1.spice

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 5 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 6 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 7 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-extracted-routed --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 8 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.routed.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, ROUTING-level-parasitic-annotated for both rings (layout/pex/build.py); the buffer/XOR stage remains device-level (leaf-cell) -- see layout/pex/build.py's own module docstring, 'Two composed drop-ins, different scope', and sim/characterization-post-layout-extracted.md's 2026-09-11 delta section.
- Two PVT points, not a full corner sweep, matching the leaf-level family and issue #146's own scope note: tt/27C/3.30V paired with ss/125C/3.63V (DR-0015's own measured entropy-binding worst corner). `corners`/`temperatures_c` above list the two VALUES exercised -- they are not independently swept, so do not read this as a 2x2 grid.
- 8 mismatch seeds is enough to characterize the spread's rough magnitude, not to bound a tail probability.
- Each seed is an independent full-array mismatch draw (both rings' own routed extraction, redrawn together), the physically correct picture for one chip -- but the two rings' mismatch draws are correlated only through whatever global (not per-device) variation sw_stat_global would add, which this testbench leaves off.
- No deterministic negative control (sw_stat_mismatch=0) is re-run against this routed netlist, for the same reason the leaf-level family gives: gf180mcu's per-corner device libraries gate mismatch's EFFECT on the model by sw_stat_mismatch regardless of which netlist instantiates those same PDK device subcircuits.
- The mismatch model itself is unaffected by which composition path extracted the devices: layout/pex/build.py's `klt extract --parasitics` binds each drawn device to the SAME real PDK subcircuit name design/netlist.py's schematic already instantiates, whether extracted at leaf level or from the assembled ring GDS -- see layout/pex/build.py's own module docstring.
- WIDENED MEASUREMENT WINDOW (100n -> 160n) relative to the leaf-level family: at the ss/125C/3.63V point, the routed rings' own real hand-routed inter-stage parasitics slow the deterministic (mismatch-free) steady-state period to ~17.4 ns/~16.5 ns (sim/tb/ro-array-core-pvt-q-extracted-routed/'s own figure at this identical PVT point) -- six rising edges (needed for the 2nd-to-6th-edge period measurement) land close to or past a 100n tstop even before mismatch-driven seed-to-seed variance is added. A first attempt at the leaf-level family's own 100n window failed outright at this corner (`t1b`/`t2b` 'out of interval' on the one seed that did not additionally fail from apparent numerical/resource pressure) -- widened to 160n, comfortably past six edges (~104-140 ns across the mismatch-drawn seeds) with margin. The tt/27C/3.30V point (already comfortably inside 100n at its own ~11.8/11.2 ns period) is unaffected by the widening beyond its own slightly longer run time.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
