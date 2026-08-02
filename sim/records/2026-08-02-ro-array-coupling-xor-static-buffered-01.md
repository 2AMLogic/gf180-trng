---
record: 2026-08-02-ro-array-coupling-xor-static-buffered-01
date: 2026-08-02T22:19:36Z
status: valid

testbench:
  path: sim/tb/ro-array-coupling-xor-static-buffered/tb_ro_array_coupling_xor_static_buffered.sp
  sha: b1ae3c0f2050a45c9595cd78479a64822603183c
netlist:
  path: design/ro_array_sanity.spice
  sha: 969b5873c37a527f15c86e6f5619304c9b7a9d33
repo_commit: ada73c7672a11521b3b586f0a807b0739b303209-dirty

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
  path: sim/records/raw/2026-08-02-ro-array-coupling-xor-static-buffered-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:e0564f1d8853dfc28c66d897958482d4c2f3b89e4116ce3ac03ecf858055df73
    - tt_27c_3.30v-run0.log  sha256:b2de6d9fdc0ee3305fc8bab3947577e9fed89cb20f4dcad68c576397a9ea8518
    - tt_27c_3.30v-run1.spice  sha256:dc1f7f7248af3afe7a283027b895aa1fc47203e70abdc5ab54c97bed1e018129
    - tt_27c_3.30v-run1.log  sha256:58057eb658bb3378867f774d3d2fbfd661a8c676824445e0b2740b3afd7ab2c5
    - tt_27c_3.30v-run2.spice  sha256:ff65f464c981ef9da41538078b3b2442b4f7ab8f953dcf9ad552ddf9426952b0
    - tt_27c_3.30v-run2.log  sha256:632840bed8f8d02732f052da53af9c438ffaec53e9d551e4d477d69f53afee4a
    - tt_27c_3.30v-run3.spice  sha256:7d81b12ee87aa443821befa3b7d6a77f44ca165e458a5b906672ed6551769db0
    - tt_27c_3.30v-run3.log  sha256:b737196390baf5e02df5553044e9dc8f2ac0254c59f8a49b528e80fb753d0201
wall_time: 92.8m
---

## Result

- `period`: mean 2.853602e-09 over 4 seeds (sd 1.123002e-14, 0.0% of mean; min 2.853592e-09, max 2.853618e-09)
- `f_osc`: mean 3.504343e+08 over 4 seeds (sd 1379.09, 0.0% of mean; min 3.504323e+08, max 3.504355e+08)
- `period_startup16`: mean 2.853569e-09 over 4 seeds (sd 1.769892e-13, 0.0% of mean; min 2.853337e-09, max 2.853721e-09)
- `period_b00`: mean 2.853623e-09 over 4 seeds (sd 3.487628e-14, 0.0% of mean; min 2.853597e-09, max 2.853675e-09)
- `period_b01`: mean 2.853611e-09 over 4 seeds (sd 4.417782e-14, 0.0% of mean; min 2.853546e-09, max 2.853642e-09)
- `period_b02`: mean 2.853641e-09 over 4 seeds (sd 8.224129e-15, 0.0% of mean; min 2.853631e-09, max 2.853648e-09)
- `period_b03`: mean 2.853647e-09 over 4 seeds (sd 6.089074e-14, 0.0% of mean; min 2.853587e-09, max 2.853725e-09)
- `period_b04`: mean 2.853633e-09 over 4 seeds (sd 3.683832e-14, 0.0% of mean; min 2.853606e-09, max 2.853685e-09)
- `period_b05`: mean 2.853565e-09 over 4 seeds (sd 2.607635e-14, 0.0% of mean; min 2.853546e-09, max 2.853602e-09)
- `period_b06`: mean 2.853578e-09 over 4 seeds (sd 4.354700e-14, 0.0% of mean; min 2.853521e-09, max 2.853617e-09)
- `period_b07`: mean 2.853591e-09 over 4 seeds (sd 8.264254e-14, 0.0% of mean; min 2.853492e-09, max 2.853692e-09)
- `period_b08`: mean 2.853604e-09 over 4 seeds (sd 6.588081e-14, 0.0% of mean; min 2.853521e-09, max 2.853667e-09)
- `period_b09`: mean 2.853594e-09 over 4 seeds (sd 7.887370e-14, 0.0% of mean; min 2.853542e-09, max 2.853708e-09)
- `period_b10`: mean 2.853630e-09 over 4 seeds (sd 5.208333e-14, 0.0% of mean; min 2.853563e-09, max 2.853687e-09)
- `period_b11`: mean 2.853568e-09 over 4 seeds (sd 2.621471e-14, 0.0% of mean; min 2.853542e-09, max 2.853604e-09)
- `period_b12`: mean 2.853635e-09 over 4 seeds (sd 6.909636e-14, 0.0% of mean; min 2.853563e-09, max 2.853729e-09)
- `period_b13`: mean 2.853661e-09 over 4 seeds (sd 6.669920e-14, 0.0% of mean; min 2.853604e-09, max 2.853729e-09)
- `period_b14`: mean 2.853630e-09 over 4 seeds (sd 6.220995e-14, 0.0% of mean; min 2.853563e-09, max 2.853708e-09)
- `period_b15`: mean 2.853557e-09 over 4 seeds (sd 2.621471e-14, 0.0% of mean; min 2.853521e-09, max 2.853583e-09)
- `sigma_1`: mean 6.871839e-13 over 4 seeds (sd 3.063570e-14, 4.5% of mean; min 6.505375e-13, max 7.206850e-13)
- `sigma_2`: mean 8.109166e-13 over 4 seeds (sd 3.724630e-14, 4.6% of mean; min 7.639823e-13, max 8.551118e-13)
- `sigma_4`: mean 1.034899e-12 over 4 seeds (sd 6.238304e-14, 6.0% of mean; min 9.593036e-13, max 1.109892e-12)
- `sigma_8`: mean 1.377479e-12 over 4 seeds (sd 9.451831e-14, 6.9% of mean; min 1.254686e-12, max 1.468627e-12)
- `sigma_16`: mean 1.937206e-12 over 4 seeds (sd 8.858170e-14, 4.6% of mean; min 1.866431e-12, max 2.061164e-12)
- `sigma_32`: mean 2.582317e-12 over 4 seeds (sd 3.050321e-13, 11.8% of mean; min 2.317969e-12, max 3.015378e-12)
- `sigma_64`: mean 3.541111e-12 over 4 seeds (sd 6.155652e-13, 17.4% of mean; min 3.009175e-12, max 4.423724e-12)
- `sigma_128`: mean 5.134334e-12 over 4 seeds (sd 1.302805e-12, 25.4% of mean; min 3.934441e-12, max 6.956777e-12)
- `sigma_startup16_1`: mean 5.229349e-13 over 4 seeds (sd 1.081568e-13, 20.7% of mean; min 4.285315e-13, max 6.455379e-13)
- `sigma_startup16_2`: mean 6.822826e-13 over 4 seeds (sd 1.620703e-13, 23.8% of mean; min 5.348335e-13, max 8.867203e-13)
- `sigma_startup16_4`: mean 8.904792e-13 over 4 seeds (sd 3.693549e-13, 41.5% of mean; min 6.171445e-13, max 1.435587e-12)
- `sigma_startup16_8`: mean 1.207466e-12 over 4 seeds (sd 6.454704e-13, 53.5% of mean; min 6.251336e-13, max 2.123715e-12)
- `i_ring_a`: mean 1.888508e-05 over 4 seeds (sd 6.594516e-11, 0.0% of mean; min 1.888500e-05, max 1.888515e-05)
- `i_buf1_a`: mean 9.247938e-06 over 4 seeds (sd 1.090200e-11, 0.0% of mean; min 9.247926e-06, max 9.247952e-06)
- `i_tree_a`: mean 8.759761e-06 over 4 seeds (sd 1.836166e-11, 0.0% of mean; min 8.759738e-06, max 8.759776e-06)
- `p_active_w`: mean 6.232077e-05 over 4 seeds (sd 2.176184e-10, 0.0% of mean; min 6.232049e-05, max 6.232101e-05)
- `p_buf1_w`: mean 3.051820e-05 over 4 seeds (sd 3.597704e-11, 0.0% of mean; min 3.051815e-05, max 3.051824e-05)
- `e_per_cycle_j`: mean 1.778387e-13 over 4 seeds (sd 1.924606e-19, 0.0% of mean; min 1.778384e-13, max 1.778389e-13)
- `c_eff_node_f`: mean 3.266091e-15 over 4 seeds (sd 3.534658e-21, 0.0% of mean; min 3.266087e-15, max 3.266095e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-coupling-xor-static-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 40000 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-static-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 40000 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-static-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 40000 --no-write
python3 sim/run_corners.py ro-array-coupling-xor-static-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 40000 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_sanity.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Issue #75's matched quiet-neighbour control. The ONLY circuit difference from sim/tb/ro-array-coupling-xor-static/ (issue #51's variant 2) is the buffer spliced in between the ring node and xa1's input; the ONLY circuit difference from sim/tb/ro-array-coupling-xor-driven-buffered/ is that the neighbour is a rail here rather than a second ring. That second pairing is the one this deck exists for: it is the same one-change comparison issue #51 used to attribute 28.6x, repeated at the buffered operating point.
- sigma_1 is measured at the RAW ring node v(ro1), upstream of the buffer -- not at the buffered node rb1. Measuring at the buffer output would read low regardless of whether the mitigation works, because a low-impedance driven node is quiet by construction.
- xa1's second input is tied to vss. Tying it to vdd would sit the gate's input stage at the other fixed operating point; this deck measures one of the two, not their average, exactly as issue #51's variant 2 does.
- The buffer lightens the ring's load (0.66 um of gate against xa1's 1.98 um), so this ring runs FASTER than variant 2's and its period sits between variant 2's ~3.31 ns and the unloaded control's 2.5635 ns. That is the whole reason this deck exists: a sigma read against issue #51's UNBUFFERED controls would mix the buffer's isolation with the buffer's lighter load, and this deck holds the load fixed so only the neighbour differs.
- The buffer has its own metered supply pin (vddb1), separate from the ring's (vddr1) and the tree's (vdd), purely for power bookkeeping. All branches are zero-volt ammeter sources off the same IDEAL vsup, so the metering split adds no electrical coupling path.
- tstop is 2.9 us, unchanged from variant 2, per the same-window-geometry requirement -- the buffered ring is faster, so 770 rises complete with more margin than variant 2 had, not less.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used. They are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
