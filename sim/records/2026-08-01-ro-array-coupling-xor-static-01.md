---
record: 2026-08-01-ro-array-coupling-xor-static-01
date: 2026-08-01T23:20:57Z
status: valid

testbench:
  path: sim/tb/ro-array-coupling-xor-static/tb_ro_array_coupling_xor_static.sp
  sha: 77aa2837850dff61d11f61f896a9ef37c5b46601
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
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources, one in series with every stage input
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-01-ro-array-coupling-xor-static-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:bdf27c10eb4357fc536eb697a31a44a1e0a93582f40e656470e1a528832c29fd
    - tt_27c_3.30v-run0.log  sha256:827043158942db25591bf5bc45209fe9b541caeb7dc23422f87510e17173eea4
    - tt_27c_3.30v-run1.spice  sha256:86a639adc6d2b5c9ed43d3bb79bed806a8814309d5abd23a8e72981bc7d16399
    - tt_27c_3.30v-run1.log  sha256:5ef063a367384bcc1b470e9497bf6b6a4f94cf0701fefb5da525c08a7002a7cc
    - tt_27c_3.30v-run2.spice  sha256:733538745c842f9368e06697509a91173581d0a0fd7fdb2e2e84c603737fdafd
    - tt_27c_3.30v-run2.log  sha256:886ea19b8d99920b49100b7f86fd8ea39dc7ac9b68e714c21189eb87fd243205
    - tt_27c_3.30v-run3.spice  sha256:fb506bed5d9c4fb4418ef7d88b6784a151f5bf97a39d856c34e1d949a4b3709f
    - tt_27c_3.30v-run3.log  sha256:e0adc514100890591e500233ffa745ad7443d627926bac2ec2b102815d416b0a
wall_time: 808.3m
---

## Result

- `period`: mean 3.309601e-09 over 4 seeds (sd 1.478971e-14, 0.0% of mean; min 3.309588e-09, max 3.309620e-09)
- `f_osc`: mean 3.021512e+08 over 4 seeds (sd 1350.23, 0.0% of mean; min 3.021495e+08, max 3.021524e+08)
- `period_startup16`: mean 3.309591e-09 over 4 seeds (sd 9.243708e-14, 0.0% of mean; min 3.309506e-09, max 3.309698e-09)
- `period_b00`: mean 3.309607e-09 over 4 seeds (sd 2.942942e-14, 0.0% of mean; min 3.309576e-09, max 3.309644e-09)
- `period_b01`: mean 3.309594e-09 over 4 seeds (sd 5.496211e-14, 0.0% of mean; min 3.309531e-09, max 3.309656e-09)
- `period_b02`: mean 3.309528e-09 over 4 seeds (sd 1.117063e-13, 0.0% of mean; min 3.309400e-09, max 3.309652e-09)
- `period_b03`: mean 3.309597e-09 over 4 seeds (sd 1.935748e-14, 0.0% of mean; min 3.309571e-09, max 3.309617e-09)
- `period_b04`: mean 3.309586e-09 over 4 seeds (sd 4.202967e-14, 0.0% of mean; min 3.309525e-09, max 3.309619e-09)
- `period_b05`: mean 3.309597e-09 over 4 seeds (sd 8.775588e-14, 0.0% of mean; min 3.309535e-09, max 3.309727e-09)
- `period_b06`: mean 3.309650e-09 over 4 seeds (sd 5.963335e-14, 0.0% of mean; min 3.309604e-09, max 3.309735e-09)
- `period_b07`: mean 3.309552e-09 over 4 seeds (sd 3.608439e-14, 0.0% of mean; min 3.309521e-09, max 3.309583e-09)
- `period_b08`: mean 3.309568e-09 over 4 seeds (sd 6.220995e-14, 0.0% of mean; min 3.309500e-09, max 3.309646e-09)
- `period_b09`: mean 3.309620e-09 over 4 seeds (sd 3.557971e-14, 0.0% of mean; min 3.309583e-09, max 3.309667e-09)
- `period_b10`: mean 3.309542e-09 over 4 seeds (sd 5.103104e-14, 0.0% of mean; min 3.309479e-09, max 3.309604e-09)
- `period_b11`: mean 3.309526e-09 over 4 seeds (sd 3.557968e-14, 0.0% of mean; min 3.309479e-09, max 3.309562e-09)
- `period_b12`: mean 3.309589e-09 over 4 seeds (sd 5.208334e-14, 0.0% of mean; min 3.309521e-09, max 3.309646e-09)
- `period_b13`: mean 3.309656e-09 over 4 seeds (sd 4.959327e-14, 0.0% of mean; min 3.309583e-09, max 3.309688e-09)
- `period_b14`: mean 3.309682e-09 over 4 seeds (sd 3.125000e-14, 0.0% of mean; min 3.309667e-09, max 3.309729e-09)
- `period_b15`: mean 3.309630e-09 over 4 seeds (sd 4.922726e-14, 0.0% of mean; min 3.309562e-09, max 3.309667e-09)
- `sigma_1`: mean 6.759436e-13 over 4 seeds (sd 1.568216e-14, 2.3% of mean; min 6.540289e-13, max 6.877696e-13)
- `sigma_2`: mean 7.936790e-13 over 4 seeds (sd 1.729755e-14, 2.2% of mean; min 7.785600e-13, max 8.116931e-13)
- `sigma_4`: mean 9.991787e-13 over 4 seeds (sd 3.720339e-14, 3.7% of mean; min 9.538466e-13, max 1.040821e-12)
- `sigma_8`: mean 1.284702e-12 over 4 seeds (sd 1.033403e-13, 8.0% of mean; min 1.174034e-12, max 1.394069e-12)
- `sigma_16`: mean 1.822707e-12 over 4 seeds (sd 2.519926e-13, 13.8% of mean; min 1.605227e-12, max 2.139361e-12)
- `sigma_32`: mean 2.762748e-12 over 4 seeds (sd 3.997854e-13, 14.5% of mean; min 2.383387e-12, max 3.253185e-12)
- `sigma_64`: mean 3.972055e-12 over 4 seeds (sd 5.810454e-13, 14.6% of mean; min 3.258410e-12, max 4.590519e-12)
- `sigma_128`: mean 5.753199e-12 over 4 seeds (sd 4.650952e-13, 8.1% of mean; min 5.104892e-12, max 6.195760e-12)
- `sigma_startup16_1`: mean 5.144179e-13 over 4 seeds (sd 1.258952e-13, 24.5% of mean; min 3.754986e-13, max 6.786677e-13)
- `sigma_startup16_2`: mean 6.569027e-13 over 4 seeds (sd 9.753977e-14, 14.8% of mean; min 5.426334e-13, max 7.773713e-13)
- `sigma_startup16_4`: mean 8.294207e-13 over 4 seeds (sd 1.334385e-13, 16.1% of mean; min 6.467247e-13, max 9.649114e-13)
- `sigma_startup16_8`: mean 1.384209e-12 over 4 seeds (sd 3.832180e-13, 27.7% of mean; min 9.263462e-13, max 1.758567e-12)
- `i_ring_a`: mean 1.808572e-05 over 4 seeds (sd 7.241181e-11, 0.0% of mean; min 1.808567e-05, max 1.808583e-05)
- `i_tree_a`: mean 1.441105e-05 over 4 seeds (sd 9.373695e-11, 0.0% of mean; min 1.441091e-05, max 1.441113e-05)
- `p_active_w`: mean 5.968289e-05 over 4 seeds (sd 2.389590e-10, 0.0% of mean; min 5.968271e-05, max 5.968324e-05)
- `e_per_cycle_j`: mean 1.975266e-13 over 4 seeds (sd 6.601849e-19, 0.0% of mean; min 1.975258e-13, max 1.975273e-13)
- `c_eff_node_f`: mean 3.627669e-15 over 4 seeds (sd 1.212463e-20, 0.0% of mean; min 3.627655e-15, max 3.627682e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-coupling-xor-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_sanity.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Variant 2 of issue #51's four-variant experiment. It is comparable to sim/tb/ro-ring5-starved-jitter-long/ (the control) ONLY because the delay cell, the injected noise density, the window geometry, the print step and the corner are identical; the one intended difference is the XOR gate hung on the ring output. That load slows the ring (period ~3.31 ns here against the control's 2.5635 ns), and a slower ring is a different operating point, so a sigma difference between this variant and the control is not by itself evidence of anything dynamic -- which is exactly why the comparison that matters is this variant against variant 3 (sim/tb/ro-array-coupling-xor-driven/), where the load is the same and only the neighbour's switching differs.
- xa1's second input is tied to vss. Tying it to vdd would sit the gate's input stage at the other fixed operating point; this variant measures one of the two, not their average, and the difference between them is not measured here.
- tstop is 2.9 us rather than the control's 2.4 us because the loaded ring is slower and 770 rises take ~2.55 us. Nothing else about the window changed: it still opens 256 periods after start-up and spans 512 periods.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used. They are a like-for-like comparison with that record and are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
