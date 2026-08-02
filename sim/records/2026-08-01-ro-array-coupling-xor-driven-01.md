---
record: 2026-08-01-ro-array-coupling-xor-driven-01
date: 2026-08-01T23:20:57Z
status: valid

testbench:
  path: sim/tb/ro-array-coupling-xor-driven/tb_ro_array_coupling_xor_driven.sp
  sha: c4987ba76677020f2d6df6ffcb74dba01c659f83
netlist:
  path: design/ro_array_sanity.spice
  sha: 969b5873c37a527f15c86e6f5619304c9b7a9d33
repo_commit: ef0edb9c3ac4b9496477e459e576fac74603816d-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran-noise
  tstop: 2.9u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources per ring, 10 in total
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-01-ro-array-coupling-xor-driven-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:a24726d5e5ab209a5e9c520ab186a8be7de185ef89d536464bf7140768f7121d
    - tt_27c_3.30v-run0.log  sha256:6227878c2390aed0f9d05510bd23050397eaae513ac35bd6c94993128911376d
    - tt_27c_3.30v-run1.spice  sha256:8f64274a26c743db449b3a71f576c0934007d3da9ab83a4c17b1b4f28f067958
    - tt_27c_3.30v-run1.log  sha256:d57863f1af11ff3c5fbe42cce2d0aa3a191a34d9c33dfad5f9ec8c47a605d72c
    - tt_27c_3.30v-run2.spice  sha256:300c43b4b02c3ebbb9ed34d057a03c9ef86ba97a449085eb2119171f82e41ce2
    - tt_27c_3.30v-run2.log  sha256:2778ba23c8432c481b6e89a82bcaeaed974809c8db3deb4d1c7a34fda99550b5
    - tt_27c_3.30v-run3.spice  sha256:9410634e762baf4bcacd49c1d784e9309ba60a0fa07d53a42db01f65edefe76e
    - tt_27c_3.30v-run3.log  sha256:626ea71b64cbdced53b608183313d5b41b340731514a8798a33f6717b66f412f
wall_time: 1270.0m
---

## Result

- `period`: mean 3.304321e-09 over 4 seeds (sd 1.228388e-14, 0.0% of mean; min 3.304310e-09, max 3.304337e-09)
- `f_osc`: mean 3.026340e+08 over 4 seeds (sd 1125.05, 0.0% of mean; min 3.026326e+08, max 3.026350e+08)
- `period_r2`: mean 3.105404e-09 over 4 seeds (sd 3.534955e-14, 0.0% of mean; min 3.105372e-09, max 3.105453e-09)
- `period_startup16`: mean 3.304667e-09 over 4 seeds (sd 6.476079e-14, 0.0% of mean; min 3.304577e-09, max 3.304732e-09)
- `period_b00`: mean 3.304586e-09 over 4 seeds (sd 7.024256e-14, 0.0% of mean; min 3.304529e-09, max 3.304683e-09)
- `period_b01`: mean 3.304321e-09 over 4 seeds (sd 7.869701e-14, 0.0% of mean; min 3.304233e-09, max 3.304423e-09)
- `period_b02`: mean 3.303713e-09 over 4 seeds (sd 4.649150e-14, 0.0% of mean; min 3.303650e-09, max 3.303748e-09)
- `period_b03`: mean 3.303269e-09 over 4 seeds (sd 4.140107e-14, 0.0% of mean; min 3.303215e-09, max 3.303315e-09)
- `period_b04`: mean 3.303380e-09 over 4 seeds (sd 1.013562e-13, 0.0% of mean; min 3.303296e-09, max 3.303525e-09)
- `period_b05`: mean 3.304009e-09 over 4 seeds (sd 2.401865e-14, 0.0% of mean; min 3.303979e-09, max 3.304035e-09)
- `period_b06`: mean 3.303920e-09 over 4 seeds (sd 4.437384e-14, 0.0% of mean; min 3.303879e-09, max 3.303981e-09)
- `period_b07`: mean 3.304411e-09 over 4 seeds (sd 7.864411e-14, 0.0% of mean; min 3.304313e-09, max 3.304500e-09)
- `period_b08`: mean 3.304359e-09 over 4 seeds (sd 3.125000e-14, 0.0% of mean; min 3.304313e-09, max 3.304375e-09)
- `period_b09`: mean 3.304198e-09 over 4 seeds (sd 6.477345e-14, 0.0% of mean; min 3.304125e-09, max 3.304271e-09)
- `period_b10`: mean 3.304286e-09 over 4 seeds (sd 6.220997e-14, 0.0% of mean; min 3.304229e-09, max 3.304375e-09)
- `period_b11`: mean 3.304604e-09 over 4 seeds (sd 7.607258e-14, 0.0% of mean; min 3.304521e-09, max 3.304688e-09)
- `period_b12`: mean 3.304458e-09 over 4 seeds (sd 9.470961e-14, 0.0% of mean; min 3.304333e-09, max 3.304542e-09)
- `period_b13`: mean 3.304437e-09 over 4 seeds (sd 1.701032e-14, 0.0% of mean; min 3.304417e-09, max 3.304458e-09)
- `period_b14`: mean 3.304542e-09 over 4 seeds (sd 4.500512e-14, 0.0% of mean; min 3.304479e-09, max 3.304583e-09)
- `period_b15`: mean 3.304245e-09 over 4 seeds (sd 1.133137e-13, 0.0% of mean; min 3.304083e-09, max 3.304333e-09)
- `sigma_1`: mean 1.831606e-11 over 4 seeds (sd 1.884224e-14, 0.1% of mean; min 1.829219e-11, max 1.833390e-11)
- `sigma_2`: mean 3.344932e-11 over 4 seeds (sd 2.615010e-14, 0.1% of mean; min 3.342149e-11, max 3.347491e-11)
- `sigma_4`: mean 5.608320e-11 over 4 seeds (sd 3.564418e-14, 0.1% of mean; min 5.604665e-11, max 5.612056e-11)
- `sigma_8`: mean 7.130454e-11 over 4 seeds (sd 2.504678e-14, 0.0% of mean; min 7.128528e-11, max 7.133874e-11)
- `sigma_16`: mean 8.299303e-12 over 4 seeds (sd 5.152279e-14, 0.6% of mean; min 8.240820e-12, max 8.363171e-12)
- `sigma_32`: mean 1.605571e-11 over 4 seeds (sd 5.687119e-14, 0.4% of mean; min 1.600544e-11, max 1.613514e-11)
- `sigma_64`: mean 3.121683e-11 over 4 seeds (sd 1.144395e-13, 0.4% of mean; min 3.110110e-11, max 3.136916e-11)
- `sigma_128`: mean 6.010178e-11 over 4 seeds (sd 2.456931e-13, 0.4% of mean; min 5.996077e-11, max 6.046911e-11)
- `sigma_startup16_1`: mean 1.920107e-11 over 4 seeds (sd 1.834115e-13, 1.0% of mean; min 1.893196e-11, max 1.932453e-11)
- `sigma_startup16_2`: mean 3.639822e-11 over 4 seeds (sd 2.937590e-13, 0.8% of mean; min 3.607407e-11, max 3.677129e-11)
- `sigma_startup16_4`: mean 6.653920e-11 over 4 seeds (sd 4.349911e-13, 0.7% of mean; min 6.615464e-11, max 6.708535e-11)
- `sigma_startup16_8`: mean 1.056751e-10 over 4 seeds (sd 8.238628e-13, 0.8% of mean; min 1.049507e-10, max 1.065558e-10)
- `i_ring_a`: mean 1.821558e-05 over 4 seeds (sd 3.998548e-11, 0.0% of mean; min 1.821553e-05, max 1.821563e-05)
- `i_tree_a`: mean 3.662618e-05 over 4 seeds (sd 1.347843e-09, 0.0% of mean; min 3.662480e-05, max 3.662793e-05)
- `p_active_w`: mean 6.011141e-05 over 4 seeds (sd 1.319520e-10, 0.0% of mean; min 6.011125e-05, max 6.011157e-05)
- `e_per_cycle_j`: mean 1.986274e-13 over 4 seeds (sd 4.387236e-19, 0.0% of mean; min 1.986268e-13, max 1.986278e-13)
- `c_eff_node_f`: mean 3.647886e-15 over 4 seeds (sd 8.057358e-21, 0.0% of mean; min 3.647875e-15, max 3.647894e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-coupling-xor-driven --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-driven --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-driven --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-driven --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_sanity.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Variant 3 of issue #51's four-variant experiment. The comparison it exists for is against variant 2 (sim/tb/ro-array-coupling-xor-static/), which carries the SAME XOR load with the neighbour input tied to a rail: between those two decks the only difference is that the neighbour switches. Against variant 4 (sim/tb/ro-array-coupling-rings-only/) the only difference is that the two rings are electrically attached. Against the control (sim/tb/ro-ring5-starved-jitter-long/) there are two differences, so that comparison bounds the total effect and attributes none of it.
- sigma_* here is NOT a jitter measurement if the perturbation it captures is deterministic. The estimator is the same one the control uses, but it measures the spread of period-to-period increments from whatever cause; a beat between two incommensurate ring frequencies enters it exactly as noise would. The seed spread and the accumulation exponent reported alongside are what tell the two apart, and no entropy claim may be built on this record's sigma either way.
- tstop is 2.9 us rather than the control's 2.4 us because the loaded ring is slower and 770 rises take ~2.55 us. Nothing else about the window changed: it still opens 256 periods after start-up and spans 512 periods.
- The two rings' supplies are separate zero-volt ammeter sources off the same IDEAL vsup, so the only path between them in this deck is xa1's input stage. This deck therefore says nothing about supply-network coupling in a real array, where the supply is not ideal.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used. They are a like-for-like comparison with that record and are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
