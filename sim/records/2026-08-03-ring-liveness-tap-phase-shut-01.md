---
record: 2026-08-03-ring-liveness-tap-phase-shut-01
date: 2026-08-03T04:37:33Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-phase-shut/tb_ring_liveness_tap_phase_shut.sp
  sha: beafa1a98b8609136e21b38342a741fc3f6cdcb6
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: a1d86b3cf08426f173e49b7255a08033a17fdbba-dirty

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
  tstop: 3.0u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources, one in series with every stage input
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-03-ring-liveness-tap-phase-shut-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:6ba169b86a19e3f356fd3a281757fe37689db1cc855960ff2f22106bbac14a14
    - tt_27c_3.30v-run0.log  sha256:2b848122f34c721726eb71d7675bf0c392a55f222851cbee015f591d8fd8e003
    - tt_27c_3.30v-run1.spice  sha256:e38889e64abb9e88f95bd6fd0ca5580c363264d90a43831f335d6757d37347f2
    - tt_27c_3.30v-run1.log  sha256:e57a5c34dc609777b301f4d5ba12dc8c462a3b75abe215aacb37a64ac45d3692
    - tt_27c_3.30v-run2.spice  sha256:d68649c0d7c2669453e105450c3db769a536a49fcb019a2dd3fb3374ab11450f
    - tt_27c_3.30v-run2.log  sha256:50282a18e34b334bbddfa9ab680c24c010146c160841148d1e2df7eaa010239b
    - tt_27c_3.30v-run3.spice  sha256:fb6cba3cd33090bfa103bf85ccd3118a01a26d376e66e10749c73d189f5bdcb3
    - tt_27c_3.30v-run3.log  sha256:ad4098af975fbc08bdad0a69c9767c914028b892ef840dca07a13f8929182ce8
wall_time: 124.8m
---

## Result

- `period`: mean 2.747180e-09 over 4 seeds (sd 1.878354e-14, 0.0% of mean; min 2.747155e-09, max 2.747196e-09)
- `f_osc`: mean 3.640096e+08 over 4 seeds (sd 2488.89, 0.0% of mean; min 3.640076e+08, max 3.640130e+08)
- `period_startup16`: mean 2.747236e-09 over 4 seeds (sd 5.795621e-14, 0.0% of mean; min 2.747205e-09, max 2.747323e-09)
- `period_b00`: mean 2.747192e-09 over 4 seeds (sd 7.933614e-14, 0.0% of mean; min 2.747095e-09, max 2.747285e-09)
- `period_b01`: mean 2.747249e-09 over 4 seeds (sd 4.619492e-15, 0.0% of mean; min 2.747244e-09, max 2.747254e-09)
- `period_b02`: mean 2.747208e-09 over 4 seeds (sd 5.718107e-14, 0.0% of mean; min 2.747173e-09, max 2.747294e-09)
- `period_b03`: mean 2.747222e-09 over 4 seeds (sd 5.799440e-14, 0.0% of mean; min 2.747135e-09, max 2.747252e-09)
- `period_b04`: mean 2.747220e-09 over 4 seeds (sd 6.415347e-14, 0.0% of mean; min 2.747129e-09, max 2.747279e-09)
- `period_b05`: mean 2.747148e-09 over 4 seeds (sd 4.827387e-14, 0.0% of mean; min 2.747106e-09, max 2.747213e-09)
- `period_b06`: mean 2.747149e-09 over 4 seeds (sd 7.403652e-14, 0.0% of mean; min 2.747042e-09, max 2.747200e-09)
- `period_b07`: mean 2.747169e-09 over 4 seeds (sd 7.207600e-14, 0.0% of mean; min 2.747106e-09, max 2.747271e-09)
- `period_b08`: mean 2.747146e-09 over 4 seeds (sd 0, 0.0% of mean; min 2.747146e-09, max 2.747146e-09)
- `period_b09`: mean 2.747208e-09 over 4 seeds (sd 2.946278e-14, 0.0% of mean; min 2.747187e-09, max 2.747250e-09)
- `period_b10`: mean 2.747203e-09 over 4 seeds (sd 3.125001e-14, 0.0% of mean; min 2.747167e-09, max 2.747229e-09)
- `period_b11`: mean 2.747193e-09 over 4 seeds (sd 4.922726e-14, 0.0% of mean; min 2.747125e-09, max 2.747229e-09)
- `period_b12`: mean 2.747208e-09 over 4 seeds (sd 2.946278e-14, 0.0% of mean; min 2.747187e-09, max 2.747250e-09)
- `period_b13`: mean 2.747172e-09 over 4 seeds (sd 7.864411e-14, 0.0% of mean; min 2.747063e-09, max 2.747250e-09)
- `period_b14`: mean 2.747177e-09 over 4 seeds (sd 1.202811e-14, 0.0% of mean; min 2.747167e-09, max 2.747187e-09)
- `period_b15`: mean 2.747182e-09 over 4 seeds (sd 8.735933e-14, 0.0% of mean; min 2.747063e-09, max 2.747271e-09)
- `sigma_1`: mean 6.466089e-13 over 4 seeds (sd 1.503140e-14, 2.3% of mean; min 6.286206e-13, max 6.653501e-13)
- `sigma_2`: mean 7.616981e-13 over 4 seeds (sd 1.663037e-14, 2.2% of mean; min 7.461298e-13, max 7.849522e-13)
- `sigma_4`: mean 9.705442e-13 over 4 seeds (sd 2.507208e-14, 2.6% of mean; min 9.354345e-13, max 9.947897e-13)
- `sigma_8`: mean 1.231616e-12 over 4 seeds (sd 5.325984e-14, 4.3% of mean; min 1.177419e-12, max 1.299934e-12)
- `sigma_16`: mean 1.596534e-12 over 4 seeds (sd 1.140433e-13, 7.1% of mean; min 1.497957e-12, max 1.759642e-12)
- `sigma_32`: mean 2.090587e-12 over 4 seeds (sd 3.602374e-13, 17.2% of mean; min 1.661067e-12, max 2.400596e-12)
- `sigma_64`: mean 2.840343e-12 over 4 seeds (sd 6.235078e-13, 22.0% of mean; min 2.279554e-12, max 3.593716e-12)
- `sigma_128`: mean 3.962066e-12 over 4 seeds (sd 8.066516e-13, 20.4% of mean; min 3.120175e-12, max 5.060202e-12)
- `sigma_startup16_1`: mean 5.144294e-13 over 4 seeds (sd 1.704511e-13, 33.1% of mean; min 3.765598e-13, max 7.610851e-13)
- `sigma_startup16_2`: mean 7.022426e-13 over 4 seeds (sd 2.689746e-13, 38.3% of mean; min 4.880537e-13, max 1.086636e-12)
- `sigma_startup16_4`: mean 9.457491e-13 over 4 seeds (sd 4.149806e-13, 43.9% of mean; min 6.875435e-13, max 1.563856e-12)
- `sigma_startup16_8`: mean 1.194580e-12 over 4 seeds (sd 6.551670e-13, 54.8% of mean; min 7.536190e-13, max 2.156309e-12)
- `i_ring_a`: mean 1.895191e-05 over 4 seeds (sd 4.869569e-11, 0.0% of mean; min 1.895186e-05, max 1.895197e-05)
- `i_tap_a`: mean 5.010624e-11 over 4 seeds (sd 5.763406e-15, 0.0% of mean; min 5.009842e-11, max 5.011222e-11)
- `p_active_w`: mean 6.254129e-05 over 4 seeds (sd 1.606962e-10, 0.0% of mean; min 6.254114e-05, max 6.254151e-05)
- `p_tap_w`: mean 1.653506e-10 over 4 seeds (sd 1.901924e-14, 0.0% of mean; min 1.653248e-10, max 1.653703e-10)
- `e_per_cycle_j`: mean 1.718122e-13 over 4 seeds (sd 8.108016e-19, 0.0% of mean; min 1.718112e-13, max 1.718130e-13)
- `c_eff_node_f`: mean 3.155412e-15 over 4 seeds (sd 1.489079e-20, 0.0% of mean; min 3.155394e-15, max 3.155426e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-phase-shut --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-shut --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-shut --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-shut --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 172800 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Control A of issue #76's six-variant experiment (see the deck header for the whole set). It is comparable to sim/tb/ro-ring5-starved-jitter-long/ (the digitizers-absent control) ONLY because the delay cell, the injected noise density, the window geometry, the print step and the corner are identical; the one intended difference is the sampler_dff hung on the ring output. That load slows the ring, and a slower ring is a different operating point, so a sigma difference between this variant and that control is not by itself evidence of anything dynamic -- which is why the comparison that matters is this variant against sim/tb/ring-liveness-tap-phase-clocked/, where the attached cell is the same and only the clock's switching differs.
- clk is held at vdd here, so the digitizer's input transmission gate is opaque and the ring node sees only the pass devices' junction and gate-overlap capacitance. sim/tb/ring-liveness-tap-phase-open/ measures the OTHER fixed operating point (clk at vss, gate transparent, master latch attached). Neither is the average of the two; the clocked variant is what walks between them.
- tstop is 3.0 us rather than issue #51's 2.9 us because the digitizer-loaded ring is slower in the -open and -clocked variants of this family and 770 rises there take ~2.7 us; every deck in the family uses the same tstop so the runs are like-for-like. Nothing about the window changed: it still opens 256 periods after start-up and spans 512 periods.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used, exactly as issue #51's variants do. They are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.
- rst_n is held HIGH from t=0 with no edge. DR-0014's reset is an initialisation input; the digitizer's own output (ring_bit1) is not measured by this deck, which measures what the digitizer does to the RING.
- i_tap_a is the digitizer's own average supply current over the 512-period window, on its own metered branch (vddtap). It is an average bound, not a per-clock-cycle energy: with clk static there is no clock cycle to divide by.
- abstol=1e-10 (tb.json "options"), 100x looser than ngspice's 1e-12 default, on EVERY deck in this family -- including the four whose clock never moves and which converge without it. Without the relaxation the two clocked decks abort with "Timestep too small ... trouble with node vtap#branch" at a clock edge, exactly the abort sim/tb/sampler-array-digitize/ bisected and documented for the same cell driven from the same kind of external edge; softer edges (20 ns) and moving the first edge past ring start-up were both tried here and neither fixes it, matching that deck's own finding that edge rate is not the cause. The relaxation is applied to the static decks too, even though they do not need it, because this family's whole claim is a ratio between decks and a ratio between two different solver tolerances would not be one. 100 pA is ~3e-6 of this ring's ~35 uA supply current. The check that it is benign is internal to the family: the static decks' sigma_1 and seed spread can be read against sim/records/2026-08-01-ro-ring5-starved-jitter-long-02.md, which was taken at ngspice's default tolerances -- a relaxation that injected numerical jitter would show up there as an inflated sigma_1 with a collapsed seed spread.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
