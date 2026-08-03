---
record: 2026-08-03-ring-liveness-tap-phase-open-01
date: 2026-08-03T05:08:53Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-phase-open/tb_ring_liveness_tap_phase_open.sp
  sha: 9dc3e1210b35ac3593b1f00df4b8ad174b2d5dcc
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
  path: sim/records/raw/2026-08-03-ring-liveness-tap-phase-open-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:40efc0eec8e37127076e949d051d41e0a1590d0623782f8f53398087d83e5255
    - tt_27c_3.30v-run0.log  sha256:bfeadd6f6c84e8cfa6899500ceb9b1e8d983a127c0a73b966d0312e6b494be1b
    - tt_27c_3.30v-run1.spice  sha256:a3247f2dca89e7afe896d1c6eccc8154f08c586838382d9d07df6e4b0839cbb8
    - tt_27c_3.30v-run1.log  sha256:7ec964e57cba53aee20171732dd235dcc476b49d23cbf00f80b1d0a09896b6a5
    - tt_27c_3.30v-run2.spice  sha256:91ea37d53dd50b93023978984bee41eabde95c6e994cce8b8ab434211933b1a9
    - tt_27c_3.30v-run2.log  sha256:4a88968f432a74f36841a3dcae2af9671ee7324d2f108bef775bc9c0a81cd815
    - tt_27c_3.30v-run3.spice  sha256:867814a883848af7d3f4c9395fc369ee5585c0802f8e884eaae78ea1a915465e
    - tt_27c_3.30v-run3.log  sha256:00255361f5a20cf5917213f61a42d220933ba4c01503741ef8a107fdec90d1da
wall_time: 140.3m
---

## Result

- `period`: mean 3.450694e-09 over 4 seeds (sd 3.530329e-14, 0.0% of mean; min 3.450671e-09, max 3.450747e-09)
- `f_osc`: mean 2.897968e+08 over 4 seeds (sd 2964.82, 0.0% of mean; min 2.897924e+08, max 2.897987e+08)
- `period_startup16`: mean 3.450701e-09 over 4 seeds (sd 9.360324e-14, 0.0% of mean; min 3.450568e-09, max 3.450771e-09)
- `period_b00`: mean 3.450648e-09 over 4 seeds (sd 5.075492e-14, 0.0% of mean; min 3.450605e-09, max 3.450719e-09)
- `period_b01`: mean 3.450677e-09 over 4 seeds (sd 8.608943e-14, 0.0% of mean; min 3.450621e-09, max 3.450804e-09)
- `period_b02`: mean 3.450670e-09 over 4 seeds (sd 5.290668e-14, 0.0% of mean; min 3.450594e-09, max 3.450715e-09)
- `period_b03`: mean 3.450691e-09 over 4 seeds (sd 5.983919e-14, 0.0% of mean; min 3.450635e-09, max 3.450773e-09)
- `period_b04`: mean 3.450736e-09 over 4 seeds (sd 9.632274e-14, 0.0% of mean; min 3.450602e-09, max 3.450808e-09)
- `period_b05`: mean 3.450692e-09 over 4 seeds (sd 6.802015e-14, 0.0% of mean; min 3.450640e-09, max 3.450792e-09)
- `period_b06`: mean 3.450734e-09 over 4 seeds (sd 4.051799e-14, 0.0% of mean; min 3.450679e-09, max 3.450777e-09)
- `period_b07`: mean 3.450646e-09 over 4 seeds (sd 9.001027e-14, 0.0% of mean; min 3.450563e-09, max 3.450771e-09)
- `period_b08`: mean 3.450719e-09 over 4 seeds (sd 3.608438e-14, 0.0% of mean; min 3.450687e-09, max 3.450771e-09)
- `period_b09`: mean 3.450708e-09 over 4 seeds (sd 9.470961e-14, 0.0% of mean; min 3.450583e-09, max 3.450792e-09)
- `period_b10`: mean 3.450698e-09 over 4 seeds (sd 6.477349e-14, 0.0% of mean; min 3.450646e-09, max 3.450792e-09)
- `period_b11`: mean 3.450641e-09 over 4 seeds (sd 5.983918e-14, 0.0% of mean; min 3.450563e-09, max 3.450708e-09)
- `period_b12`: mean 3.450677e-09 over 4 seeds (sd 1.055464e-13, 0.0% of mean; min 3.450604e-09, max 3.450833e-09)
- `period_b13`: mean 3.450708e-09 over 4 seeds (sd 2.946278e-14, 0.0% of mean; min 3.450687e-09, max 3.450750e-09)
- `period_b14`: mean 3.450740e-09 over 4 seeds (sd 8.068715e-14, 0.0% of mean; min 3.450646e-09, max 3.450833e-09)
- `period_b15`: mean 3.450672e-09 over 4 seeds (sd 3.125001e-14, 0.0% of mean; min 3.450646e-09, max 3.450708e-09)
- `sigma_1`: mean 8.846411e-13 over 4 seeds (sd 1.631396e-14, 1.8% of mean; min 8.710428e-13, max 9.038892e-13)
- `sigma_2`: mean 9.981828e-13 over 4 seeds (sd 8.751157e-15, 0.9% of mean; min 9.853241e-13, max 1.004094e-12)
- `sigma_4`: mean 1.234498e-12 over 4 seeds (sd 1.020904e-14, 0.8% of mean; min 1.228308e-12, max 1.249763e-12)
- `sigma_8`: mean 1.598493e-12 over 4 seeds (sd 6.585369e-14, 4.1% of mean; min 1.510553e-12, max 1.667427e-12)
- `sigma_16`: mean 2.120557e-12 over 4 seeds (sd 1.113992e-13, 5.3% of mean; min 1.992858e-12, max 2.229479e-12)
- `sigma_32`: mean 2.906343e-12 over 4 seeds (sd 2.017134e-13, 6.9% of mean; min 2.748140e-12, max 3.180558e-12)
- `sigma_64`: mean 3.785953e-12 over 4 seeds (sd 4.267886e-13, 11.3% of mean; min 3.295398e-12, max 4.235384e-12)
- `sigma_128`: mean 4.836003e-12 over 4 seeds (sd 1.008479e-12, 20.9% of mean; min 3.467205e-12, max 5.888320e-12)
- `sigma_startup16_1`: mean 7.825539e-13 over 4 seeds (sd 2.766407e-13, 35.4% of mean; min 4.962226e-13, max 1.026869e-12)
- `sigma_startup16_2`: mean 1.017934e-12 over 4 seeds (sd 2.647348e-13, 26.0% of mean; min 7.046150e-13, max 1.315403e-12)
- `sigma_startup16_4`: mean 1.218436e-12 over 4 seeds (sd 3.057808e-13, 25.1% of mean; min 8.117132e-13, max 1.518993e-12)
- `sigma_startup16_8`: mean 1.494675e-12 over 4 seeds (sd 7.043653e-13, 47.1% of mean; min 4.797066e-13, max 2.106201e-12)
- `i_ring_a`: mean 1.829192e-05 over 4 seeds (sd 9.746664e-11, 0.0% of mean; min 1.829177e-05, max 1.829199e-05)
- `i_tap_a`: mean 1.506331e-05 over 4 seeds (sd 1.125286e-10, 0.0% of mean; min 1.506315e-05, max 1.506339e-05)
- `p_active_w`: mean 6.036332e-05 over 4 seeds (sd 3.216403e-10, 0.0% of mean; min 6.036285e-05, max 6.036357e-05)
- `p_tap_w`: mean 4.970894e-05 over 4 seeds (sd 3.713443e-10, 0.0% of mean; min 4.970838e-05, max 4.970918e-05)
- `e_per_cycle_j`: mean 2.082954e-13 over 4 seeds (sd 1.031250e-18, 0.0% of mean; min 2.082948e-13, max 2.082969e-13)
- `c_eff_node_f`: mean 3.825443e-15 over 4 seeds (sd 1.893940e-20, 0.0% of mean; min 3.825433e-15, max 3.825471e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-phase-open --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-open --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-open --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-open --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 172800 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Control B of issue #76's six-variant experiment (see the deck header for the whole set). clk is held at 0 here, so the digitizer's input transmission gate is transparent and the ring node is connected straight through to the master latch node -- it drives the master inverter's 0.88 um of gate on top of the pass devices' own junction and overlap capacitance. sim/tb/ring-liveness-tap-phase-shut/ measures the OTHER fixed operating point (clk at vdd, gate opaque). Neither is the average of the two; the clocked variant is what walks between them.
- period here MINUS period in sim/tb/ring-liveness-tap-phase-shut/ is the amplitude of the load modulation a running clk imposes on this ring. That difference is a PREDICTION for sim/tb/ring-liveness-tap-phase-clocked/'s sigma_1 (which should come back near half of it, since sigma_1 of a two-level square modulation with duty p is delta*sqrt(p*(1-p))), not merely a second data point. Both numbers are measured at the same corner, in the same window geometry, with the same seeds.
- tstop is 3.0 us rather than issue #51's 2.9 us because the digitizer-loaded ring is slower in the -open and -clocked variants of this family and 770 rises there take ~2.7 us; every deck in the family uses the same tstop so the runs are like-for-like. Nothing about the window changed: it still opens 256 periods after start-up and spans 512 periods.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used, exactly as issue #51's variants do. They are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.
- rst_n is held HIGH from t=0 with no edge. DR-0014's reset is an initialisation input; the digitizer's own output (ring_bit1) is not measured by this deck, which measures what the digitizer does to the RING.
- i_tap_a is the digitizer's own average supply current over the 512-period window, on its own metered branch (vddtap). With clk static there is no clock cycle to divide by, so it is an average bound rather than a per-cycle energy -- but note that with the gate transparent the digitizer's master latch is being driven by the ring at the RING's rate, which is what that current is mostly made of.
- abstol=1e-10 (tb.json "options"), 100x looser than ngspice's 1e-12 default, on EVERY deck in this family -- including the four whose clock never moves and which converge without it. Without the relaxation the two clocked decks abort with "Timestep too small ... trouble with node vtap#branch" at a clock edge, exactly the abort sim/tb/sampler-array-digitize/ bisected and documented for the same cell driven from the same kind of external edge; softer edges (20 ns) and moving the first edge past ring start-up were both tried here and neither fixes it, matching that deck's own finding that edge rate is not the cause. The relaxation is applied to the static decks too, even though they do not need it, because this family's whole claim is a ratio between decks and a ratio between two different solver tolerances would not be one. 100 pA is ~3e-6 of this ring's ~35 uA supply current. The check that it is benign is internal to the family: the static decks' sigma_1 and seed spread can be read against sim/records/2026-08-01-ro-ring5-starved-jitter-long-02.md, which was taken at ngspice's default tolerances -- a relaxation that injected numerical jitter would show up there as an inflated sigma_1 with a collapsed seed spread.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
