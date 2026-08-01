---
record: 2026-08-01-ro-ring5-starved-jitter-long-03
date: 2026-08-01T17:16:09Z
status: valid

testbench:
  path: sim/tb/ro-ring5-starved-jitter-long/tb_ro_ring5_starved_jitter_long.sp
  sha: 8ef7522612bb4242427416690db5e960b5ca153f
netlist:
  path: design/ro_array_sanity.spice
  sha: a05e5068d79a74012d22d80a28785c926c8786ce
repo_commit: 78a6ce1c4627d44fe7af63cb321ea0014b7f4932-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran-noise
  tstop: 2.4u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step -- measured 1.3 solver points per ps of simulated time at tt/27 C/3.30 V)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources, one in series with every stage input
  runs: 8
seeds: [1, 2, 3, 4, 5, 6, 7, 8]

raw:
  path: sim/records/raw/2026-08-01-ro-ring5-starved-jitter-long-03/
  files:
    - ff_-40c_3.63v-run0.spice  sha256:754b0fd63cdcd4f07c45abd5f40f92418c5b1f59a46bca8393a9c3cb4652b919
    - ff_-40c_3.63v-run0.log  sha256:76a9239c86859acb8d635a8f6f2d8c755839571a16a13ba02d5624d6879a6439
    - ff_-40c_3.63v-run1.spice  sha256:02d1594fef1bd15ab59730d8dc97da88b9a5162e02a58097736792bcc8d44955
    - ff_-40c_3.63v-run1.log  sha256:f4b41f16c819929393218a7e46f27b9470821d61f6d8604a5ba95aa5f02a7155
    - ff_-40c_3.63v-run2.spice  sha256:0f7451f6f587dbe3052141a1fbe632ccda22241da73a24c012f604f9b551d53a
    - ff_-40c_3.63v-run2.log  sha256:82cb974d1e7365d74f27133d05297333dcb71f4543127639563e5135d2bcfaab
    - ff_-40c_3.63v-run3.spice  sha256:11dea2a0927d158117aa664dc39322e0d143d7d810d25d5a53b406780facd4cc
    - ff_-40c_3.63v-run3.log  sha256:a5cf258f197625a6a1f33a9babb556bce0de754f5dc3a47e7402cb60b5a1ccc9
    - ff_-40c_3.63v-run4.spice  sha256:352918dc638afebf0ae655f2633913c3f232f2c30bc0913a4e2008fd024e61e9
    - ff_-40c_3.63v-run4.log  sha256:e7bd03b795911975587ae1792d2f6bf36c78c8aa545797b73d0003b8c0c2e6ca
    - ff_-40c_3.63v-run5.spice  sha256:6f2d447348244ed12c5bf6a2ad5b60c638c9ebe945d32c5c83b9f0e102a6bec6
    - ff_-40c_3.63v-run5.log  sha256:36139e748e9b4a2b9bb2f0f247c4ab3e950d6a7707baacea289d87076103082b
    - ff_-40c_3.63v-run6.spice  sha256:8cb3eaeb471cbc668f6dfdc792336f91a3080878d8c55e9d4fc31e502fc34109
    - ff_-40c_3.63v-run6.log  sha256:7a2a1243376ab370d63d0b77fce7afa7cbaa78d99c82a4d494d3192ebc4db25f
    - ff_-40c_3.63v-run7.spice  sha256:14ab5a82f1bc6c37b595e76983ccdbbea0f013ade0dcd104a644f1f1be8d2a85
    - ff_-40c_3.63v-run7.log  sha256:8b0da06d3c5be77206ddcfc305607efb5ff37c8acb033e59fdceafe5ee740a21
wall_time: 885.2m
---

## Result

- `period`: mean 1.506723e-09 over 8 seeds (sd 1.949478e-14, 0.0% of mean; min 1.506705e-09, max 1.506759e-09)
- `f_osc`: mean 6.636918e+08 over 8 seeds (sd 8587.1, 0.0% of mean; min 6.636762e+08, max 6.636997e+08)
- `period_startup16`: mean 1.506756e-09 over 8 seeds (sd 9.374836e-14, 0.0% of mean; min 1.506659e-09, max 1.506940e-09)
- `period_b00`: mean 1.506777e-09 over 8 seeds (sd 2.415960e-14, 0.0% of mean; min 1.506748e-09, max 1.506811e-09)
- `period_b01`: mean 1.506748e-09 over 8 seeds (sd 7.386005e-14, 0.0% of mean; min 1.506691e-09, max 1.506920e-09)
- `period_b02`: mean 1.506755e-09 over 8 seeds (sd 2.810431e-14, 0.0% of mean; min 1.506710e-09, max 1.506800e-09)
- `period_b03`: mean 1.506733e-09 over 8 seeds (sd 3.851150e-14, 0.0% of mean; min 1.506677e-09, max 1.506794e-09)
- `period_b04`: mean 1.506741e-09 over 8 seeds (sd 5.600628e-14, 0.0% of mean; min 1.506658e-09, max 1.506831e-09)
- `period_b05`: mean 1.506752e-09 over 8 seeds (sd 4.568087e-14, 0.0% of mean; min 1.506692e-09, max 1.506815e-09)
- `period_b06`: mean 1.506715e-09 over 8 seeds (sd 4.950694e-14, 0.0% of mean; min 1.506654e-09, max 1.506802e-09)
- `period_b07`: mean 1.506730e-09 over 8 seeds (sd 7.283585e-14, 0.0% of mean; min 1.506590e-09, max 1.506813e-09)
- `period_b08`: mean 1.506713e-09 over 8 seeds (sd 3.182872e-14, 0.0% of mean; min 1.506660e-09, max 1.506748e-09)
- `period_b09`: mean 1.506718e-09 over 8 seeds (sd 5.015400e-14, 0.0% of mean; min 1.506640e-09, max 1.506775e-09)
- `period_b10`: mean 1.506727e-09 over 8 seeds (sd 3.255102e-14, 0.0% of mean; min 1.506679e-09, max 1.506777e-09)
- `period_b11`: mean 1.506727e-09 over 8 seeds (sd 7.551442e-14, 0.0% of mean; min 1.506627e-09, max 1.506881e-09)
- `period_b12`: mean 1.506752e-09 over 8 seeds (sd 6.034415e-14, 0.0% of mean; min 1.506681e-09, max 1.506873e-09)
- `period_b13`: mean 1.506723e-09 over 8 seeds (sd 3.701321e-14, 0.0% of mean; min 1.506677e-09, max 1.506775e-09)
- `period_b14`: mean 1.506721e-09 over 8 seeds (sd 2.209710e-14, 0.0% of mean; min 1.506687e-09, max 1.506750e-09)
- `period_b15`: mean 1.506708e-09 over 8 seeds (sd 6.954358e-14, 0.0% of mean; min 1.506604e-09, max 1.506792e-09)
- `sigma_1`: mean 4.153690e-13 over 8 seeds (sd 2.431231e-14, 5.9% of mean; min 3.895982e-13, max 4.711017e-13)
- `sigma_2`: mean 5.237762e-13 over 8 seeds (sd 2.666510e-14, 5.1% of mean; min 4.920288e-13, max 5.724168e-13)
- `sigma_4`: mean 6.963202e-13 over 8 seeds (sd 5.414537e-14, 7.8% of mean; min 6.314304e-13, max 7.957426e-13)
- `sigma_8`: mean 9.558009e-13 over 8 seeds (sd 8.362948e-14, 8.7% of mean; min 8.687945e-13, max 1.113159e-12)
- `sigma_16`: mean 1.342875e-12 over 8 seeds (sd 1.721937e-13, 12.8% of mean; min 1.182018e-12, max 1.602034e-12)
- `sigma_32`: mean 1.886689e-12 over 8 seeds (sd 3.553390e-13, 18.8% of mean; min 1.415072e-12, max 2.443245e-12)
- `sigma_64`: mean 2.646091e-12 over 8 seeds (sd 6.814077e-13, 25.8% of mean; min 1.797648e-12, max 3.925780e-12)
- `sigma_128`: mean 3.628286e-12 over 8 seeds (sd 1.256252e-12, 34.6% of mean; min 2.127830e-12, max 6.274859e-12)
- `sigma_startup16_1`: mean 3.533526e-13 over 8 seeds (sd 8.556331e-14, 24.2% of mean; min 2.045645e-13, max 4.574828e-13)
- `sigma_startup16_2`: mean 4.916548e-13 over 8 seeds (sd 1.017471e-13, 20.7% of mean; min 3.200764e-13, max 6.208555e-13)
- `sigma_startup16_4`: mean 6.634611e-13 over 8 seeds (sd 1.548467e-13, 23.3% of mean; min 4.461637e-13, max 8.354359e-13)
- `sigma_startup16_8`: mean 9.513896e-13 over 8 seeds (sd 2.850858e-13, 30.0% of mean; min 5.580303e-13, max 1.393844e-12)
- `i_ring_a`: mean 3.738670e-05 over 8 seeds (sd 2.665388e-10, 0.0% of mean; min 3.738624e-05, max 3.738696e-05)
- `p_active_w`: mean 1.357137e-04 over 8 seeds (sd 9.675383e-10, 0.0% of mean; min 1.357120e-04, max 1.357147e-04)
- `e_per_cycle_j`: mean 2.044830e-13 over 8 seeds (sd 1.318753e-18, 0.0% of mean; min 2.044818e-13, max 2.044858e-13)
- `c_eff_node_f`: mean 3.103659e-15 over 8 seeds (sd 2.001614e-20, 0.0% of mean; min 3.103640e-15, max 3.103702e-15)
- `vsup_v`: mean 3.63 over 8 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 5 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 6 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 7 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 8 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 8); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_sanity.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
