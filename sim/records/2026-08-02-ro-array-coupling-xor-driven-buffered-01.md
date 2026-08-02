---
record: 2026-08-02-ro-array-coupling-xor-driven-buffered-01
date: 2026-08-02T22:08:37Z
status: valid

testbench:
  path: sim/tb/ro-array-coupling-xor-driven-buffered/tb_ro_array_coupling_xor_driven_buffered.sp
  sha: 5fe5e0877816ce805b2b8947905b18cb11cec6db
netlist:
  path: design/ro_array_sanity.spice
  sha: 969b5873c37a527f15c86e6f5619304c9b7a9d33
repo_commit: 12110608f16a0f90f2b69d67350cb4d0f684d13b-dirty

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
  path: sim/records/raw/2026-08-02-ro-array-coupling-xor-driven-buffered-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:bf5c604b168a766615e6505ebc090e1042d97c6e74b111f606cfce2a6302cbbd
    - tt_27c_3.30v-run0.log  sha256:44d14b795e1be8fd9efe768010f0684c118d9c6603b2c9358f3268c22a2dee41
    - tt_27c_3.30v-run1.spice  sha256:fca1b9fd49dc040a2f5cf682772907a4c111ef7a02293630e86b47000a3aab78
    - tt_27c_3.30v-run1.log  sha256:0b017fdf158ea1ba0ecc4df34abb5606fdd738866dec1058bbef710243da554c
    - tt_27c_3.30v-run2.spice  sha256:e0dae5f6a3d8ab7ec1c49f59f7b836fbaf1f3b142e59f7aab6af522abc6a4e50
    - tt_27c_3.30v-run2.log  sha256:68475d6f429dfd91da24c4cb3dcae903889043217abd4b0c91a5adb39dbb2008
    - tt_27c_3.30v-run3.spice  sha256:0f2ff95fbe70cda3727609c669c5df70fbc941f8d3e1e89ee523699ad4a858af
    - tt_27c_3.30v-run3.log  sha256:21fcb45ecc56eaf37906a9c566e38beecf9715667e3c1f482bd9734a11dfabd4
wall_time: 144.1m
---

## Result

- `period`: mean 2.852173e-09 over 4 seeds (sd 3.289856e-14, 0.0% of mean; min 2.852128e-09, max 2.852205e-09)
- `f_osc`: mean 3.506099e+08 over 4 seeds (sd 4044.15, 0.0% of mean; min 3.506060e+08, max 3.506154e+08)
- `period_r2`: mean 2.642637e-09 over 4 seeds (sd 2.177293e-14, 0.0% of mean; min 2.642608e-09, max 2.642660e-09)
- `period_startup16`: mean 2.852328e-09 over 4 seeds (sd 9.761309e-14, 0.0% of mean; min 2.852205e-09, max 2.852426e-09)
- `period_b00`: mean 2.852201e-09 over 4 seeds (sd 3.299336e-14, 0.0% of mean; min 2.852161e-09, max 2.852236e-09)
- `period_b01`: mean 2.852183e-09 over 4 seeds (sd 7.593935e-14, 0.0% of mean; min 2.852071e-09, max 2.852238e-09)
- `period_b02`: mean 2.852158e-09 over 4 seeds (sd 5.382843e-14, 0.0% of mean; min 2.852083e-09, max 2.852210e-09)
- `period_b03`: mean 2.852042e-09 over 4 seeds (sd 6.417601e-14, 0.0% of mean; min 2.851981e-09, max 2.852127e-09)
- `period_b04`: mean 2.852164e-09 over 4 seeds (sd 7.758841e-14, 0.0% of mean; min 2.852085e-09, max 2.852271e-09)
- `period_b05`: mean 2.852280e-09 over 4 seeds (sd 6.388227e-14, 0.0% of mean; min 2.852217e-09, max 2.852369e-09)
- `period_b06`: mean 2.852226e-09 over 4 seeds (sd 7.508435e-14, 0.0% of mean; min 2.852119e-09, max 2.852292e-09)
- `period_b07`: mean 2.852199e-09 over 4 seeds (sd 4.374584e-14, 0.0% of mean; min 2.852135e-09, max 2.852233e-09)
- `period_b08`: mean 2.852042e-09 over 4 seeds (sd 7.795120e-14, 0.0% of mean; min 2.851958e-09, max 2.852146e-09)
- `period_b09`: mean 2.852115e-09 over 4 seeds (sd 8.068716e-14, 0.0% of mean; min 2.852042e-09, max 2.852229e-09)
- `period_b10`: mean 2.852224e-09 over 4 seeds (sd 2.621471e-14, 0.0% of mean; min 2.852187e-09, max 2.852250e-09)
- `period_b11`: mean 2.852198e-09 over 4 seeds (sd 3.989283e-14, 0.0% of mean; min 2.852146e-09, max 2.852229e-09)
- `period_b12`: mean 2.852281e-09 over 4 seeds (sd 6.477346e-14, 0.0% of mean; min 2.852187e-09, max 2.852333e-09)
- `period_b13`: mean 2.852078e-09 over 4 seeds (sd 7.090476e-14, 0.0% of mean; min 2.851979e-09, max 2.852146e-09)
- `period_b14`: mean 2.852073e-09 over 4 seeds (sd 4.959326e-14, 0.0% of mean; min 2.852000e-09, max 2.852104e-09)
- `period_b15`: mean 2.852245e-09 over 4 seeds (sd 6.883409e-14, 0.0% of mean; min 2.852167e-09, max 2.852333e-09)
- `sigma_1`: mean 1.972285e-12 over 4 seeds (sd 2.173592e-14, 1.1% of mean; min 1.942092e-12, max 1.989164e-12)
- `sigma_2`: mean 3.197293e-12 over 4 seeds (sd 2.620436e-14, 0.8% of mean; min 3.176715e-12, max 3.232536e-12)
- `sigma_4`: mean 5.136772e-12 over 4 seeds (sd 5.022874e-14, 1.0% of mean; min 5.101829e-12, max 5.211301e-12)
- `sigma_8`: mean 5.592385e-12 over 4 seeds (sd 7.955191e-14, 1.4% of mean; min 5.539536e-12, max 5.709506e-12)
- `sigma_16`: mean 4.943180e-12 over 4 seeds (sd 1.007269e-13, 2.0% of mean; min 4.828556e-12, max 5.060533e-12)
- `sigma_32`: mean 6.396289e-12 over 4 seeds (sd 1.217714e-13, 1.9% of mean; min 6.243659e-12, max 6.499127e-12)
- `sigma_64`: mean 3.662134e-12 over 4 seeds (sd 2.847550e-13, 7.8% of mean; min 3.513537e-12, max 4.089098e-12)
- `sigma_128`: mean 5.375336e-12 over 4 seeds (sd 5.593021e-13, 10.4% of mean; min 4.744028e-12, max 6.099830e-12)
- `sigma_startup16_1`: mean 1.948433e-12 over 4 seeds (sd 1.161730e-13, 6.0% of mean; min 1.798649e-12, max 2.053307e-12)
- `sigma_startup16_2`: mean 3.170237e-12 over 4 seeds (sd 1.744316e-13, 5.5% of mean; min 2.912850e-12, max 3.299976e-12)
- `sigma_startup16_4`: mean 5.749670e-12 over 4 seeds (sd 3.863222e-13, 6.7% of mean; min 5.339281e-12, max 6.127733e-12)
- `sigma_startup16_8`: mean 8.495123e-12 over 4 seeds (sd 9.559230e-13, 11.3% of mean; min 7.323606e-12, max 9.322616e-12)
- `i_ring_a`: mean 1.888955e-05 over 4 seeds (sd 1.165027e-10, 0.0% of mean; min 1.888946e-05, max 1.888971e-05)
- `i_buf1_a`: mean 9.554354e-06 over 4 seeds (sd 9.430855e-11, 0.0% of mean; min 9.554288e-06, max 9.554492e-06)
- `i_buf2_a`: mean 1.011634e-05 over 4 seeds (sd 3.313309e-10, 0.0% of mean; min 1.011606e-05, max 1.011672e-05)
- `i_tree_a`: mean 1.904528e-05 over 4 seeds (sd 1.115161e-09, 0.0% of mean; min 1.904403e-05, max 1.904659e-05)
- `p_active_w`: mean 6.233553e-05 over 4 seeds (sd 3.844589e-10, 0.0% of mean; min 6.233521e-05, max 6.233605e-05)
- `p_buf1_w`: mean 3.152937e-05 over 4 seeds (sd 3.112184e-10, 0.0% of mean; min 3.152915e-05, max 3.152982e-05)
- `p_buf2_w`: mean 3.338393e-05 over 4 seeds (sd 1.093392e-09, 0.0% of mean; min 3.338300e-05, max 3.338518e-05)
- `e_per_cycle_j`: mean 1.777917e-13 over 4 seeds (sd 9.836560e-19, 0.0% of mean; min 1.777904e-13, max 1.777928e-13)
- `c_eff_node_f`: mean 3.265229e-15 over 4 seeds (sd 1.806537e-20, 0.0% of mean; min 3.265205e-15, max 3.265249e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-coupling-xor-driven-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 40000 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-driven-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 40000 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-driven-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 40000 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-driven-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 40000 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_sanity.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Issue #75's buffered variant of issue #51's variant 3 (sim/tb/ro-array-coupling-xor-driven/). The ONLY circuit difference from that deck is the insertion of one minimum-width inverter buffer per ring between the ring node and xa1's input (xa1 now sees rb1/rb2, not ro1/ro2). Everything else -- both rings, the injected noise, the corner, the window geometry, tstop, seed count -- is identical, per issue #51's one-change-per-variant discipline extended to this second-order comparison.
- sigma_1 here is measured at the RAW ring node v(ro1)/v(ro2), upstream of that ring's own buffer -- not at the buffered node rb1/rb2. This deck asks whether the buffer keeps the ring's own oscillating node quiet, which is the question the mitigation exists to answer; measuring at the buffer output would trivially read low regardless of whether the mitigation works, because a low-impedance driven node is quiet by construction.
- Each buffer has its own metered supply pin (vddb1/vddb2), separate from its ring's own pin (vddr1/vddr2), purely for power bookkeeping -- the same reason the tree current (vtr) is metered separately from the ring currents in the unbuffered variant. Both branches are still zero-impedance taps off the same ideal vsup, so the metering split adds or removes no electrical coupling path; it only lets 'the ring's own current under a lighter load' and 'the buffer's own current' be read as two independent numbers.
- The buffer device sizing (pfet_03v3 w=0.44u, nfet_03v3 w=0.22u, both l=0.28u) matches xor2's own input stage and ro_stage's core inverter -- the same minimum-width 3.3 V inverter this design already uses elsewhere, not a new device size.
- tstop is unchanged at 2.9 us from the unbuffered variant, per the 'same window geometry' requirement -- even though the buffered ring's own load is lighter (0.66 um vs xa1's 1.98 um) and its period is expected to be shorter, so 770 rises should complete with margin before tstop rather than needing it extended.
- The two rings' supplies (and each ring's buffer supply) are separate zero-volt ammeter sources off the same IDEAL vsup, so the only electrical path between the two rings in this deck is through xa1's input stage, now fed by the buffer outputs rather than the ring nodes directly. This deck therefore says nothing about supply-network coupling in a real array, where the supply is not ideal -- the same caveat the unbuffered variant carries.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used. They are a like-for-like comparison with that record and are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
