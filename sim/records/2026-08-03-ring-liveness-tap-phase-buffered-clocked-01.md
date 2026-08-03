---
record: 2026-08-03-ring-liveness-tap-phase-buffered-clocked-01
date: 2026-08-03T05:08:53Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-phase-buffered-clocked/tb_ring_liveness_tap_phase_buffered_clocked.sp
  sha: 97ab19af1bce2a5af7bd3323340b0b1cf3de4cb5
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
  path: sim/records/raw/2026-08-03-ring-liveness-tap-phase-buffered-clocked-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:a067f80299c671f9c03f55238e444fc33a03a0b5ecd5ca41c2f3f04f3ff3edb9
    - tt_27c_3.30v-run0.log  sha256:382225693831eb619473568139f21d38bb452653bfa3a7db9c51c5427d14f25f
    - tt_27c_3.30v-run1.spice  sha256:53046c89866819d050cea48881ec9f8a4c952d87d2cda8e06a3d28abe7ca5747
    - tt_27c_3.30v-run1.log  sha256:96a226e979b6893a88cdc42227a1bdc50e6348a35c3ab478d795a6b4eccefd14
    - tt_27c_3.30v-run2.spice  sha256:b2faa48debf2c49d671da343198b28520229e491c83071e67f86aaddd3c80899
    - tt_27c_3.30v-run2.log  sha256:fa6b1ef83281a583fa47bda85351243465d8dda9d542f26be326cb43b2bf0b5e
    - tt_27c_3.30v-run3.spice  sha256:0305c83ec66a76e4a60d37d0ea7b808264a9985552f5c6276bde00204978a2a5
    - tt_27c_3.30v-run3.log  sha256:ff3fd09c76d8ed65f94af5bf87f237e371455853aa6bada9093f8bf67d91a2d0
wall_time: 143.7m
---

## Result

- `period`: mean 2.857813e-09 over 4 seeds (sd 1.936873e-14, 0.0% of mean; min 2.857796e-09, max 2.857836e-09)
- `f_osc`: mean 3.499179e+08 over 4 seeds (sd 2371.55, 0.0% of mean; min 3.499152e+08, max 3.499201e+08)
- `period_startup16`: mean 2.846638e-09 over 4 seeds (sd 1.051069e-13, 0.0% of mean; min 2.846545e-09, max 2.846783e-09)
- `period_b00`: mean 2.854831e-09 over 4 seeds (sd 4.180414e-14, 0.0% of mean; min 2.854783e-09, max 2.854879e-09)
- `period_b01`: mean 2.874045e-09 over 4 seeds (sd 5.806924e-14, 0.0% of mean; min 2.873977e-09, max 2.874104e-09)
- `period_b02`: mean 2.873983e-09 over 4 seeds (sd 3.753855e-14, 0.0% of mean; min 2.873944e-09, max 2.874033e-09)
- `period_b03`: mean 2.874029e-09 over 4 seeds (sd 7.090223e-14, 0.0% of mean; min 2.873931e-09, max 2.874081e-09)
- `period_b04`: mean 2.855531e-09 over 4 seeds (sd 5.170698e-14, 0.0% of mean; min 2.855473e-09, max 2.855598e-09)
- `period_b05`: mean 2.846544e-09 over 4 seeds (sd 7.647800e-14, 0.0% of mean; min 2.846435e-09, max 2.846612e-09)
- `period_b06`: mean 2.846605e-09 over 4 seeds (sd 3.850878e-14, 0.0% of mean; min 2.846569e-09, max 2.846652e-09)
- `period_b07`: mean 2.847063e-09 over 4 seeds (sd 5.081441e-14, 0.0% of mean; min 2.847008e-09, max 2.847131e-09)
- `period_b08`: mean 2.874062e-09 over 4 seeds (sd 7.013548e-14, 0.0% of mean; min 2.874021e-09, max 2.874167e-09)
- `period_b09`: mean 2.874078e-09 over 4 seeds (sd 3.943689e-14, 0.0% of mean; min 2.874021e-09, max 2.874104e-09)
- `period_b10`: mean 2.874010e-09 over 4 seeds (sd 6.477349e-14, 0.0% of mean; min 2.873958e-09, max 2.874104e-09)
- `period_b11`: mean 2.863292e-09 over 4 seeds (sd 4.500516e-14, 0.0% of mean; min 2.863250e-09, max 2.863354e-09)
- `period_b12`: mean 2.846594e-09 over 4 seeds (sd 5.242941e-14, 0.0% of mean; min 2.846542e-09, max 2.846667e-09)
- `period_b13`: mean 2.846578e-09 over 4 seeds (sd 1.080860e-13, 0.0% of mean; min 2.846500e-09, max 2.846729e-09)
- `period_b14`: mean 2.846521e-09 over 4 seeds (sd 4.166670e-14, 0.0% of mean; min 2.846458e-09, max 2.846542e-09)
- `period_b15`: mean 2.866870e-09 over 4 seeds (sd 2.621471e-14, 0.0% of mean; min 2.866833e-09, max 2.866896e-09)
- `sigma_1`: mean 1.350721e-11 over 4 seeds (sd 2.287334e-14, 0.2% of mean; min 1.347462e-11, max 1.352401e-11)
- `sigma_2`: mean 2.696490e-11 over 4 seeds (sd 4.777104e-14, 0.2% of mean; min 2.689677e-11, max 2.700194e-11)
- `sigma_4`: mean 5.379778e-11 over 4 seeds (sd 9.941920e-14, 0.2% of mean; min 5.365535e-11, max 5.387125e-11)
- `sigma_8`: mean 1.070762e-10 over 4 seeds (sd 2.054669e-13, 0.2% of mean; min 1.067806e-10, max 1.072280e-10)
- `sigma_16`: mean 2.119104e-10 over 4 seeds (sd 4.052211e-13, 0.2% of mean; min 2.113185e-10, max 2.122148e-10)
- `sigma_32`: mean 4.134268e-10 over 4 seeds (sd 7.664669e-13, 0.2% of mean; min 4.122904e-10, max 4.139044e-10)
- `sigma_64`: mean 7.980924e-10 over 4 seeds (sd 1.680170e-12, 0.2% of mean; min 7.956717e-10, max 7.994048e-10)
- `sigma_128`: mean 1.466790e-09 over 4 seeds (sd 3.632707e-12, 0.2% of mean; min 1.461826e-09, max 1.470108e-09)
- `sigma_startup16_1`: mean 5.966818e-13 over 4 seeds (sd 7.120749e-14, 11.9% of mean; min 5.142325e-13, max 6.864262e-13)
- `sigma_startup16_2`: mean 6.633479e-13 over 4 seeds (sd 1.167909e-13, 17.6% of mean; min 5.515445e-13, max 8.247274e-13)
- `sigma_startup16_4`: mean 8.013042e-13 over 4 seeds (sd 1.488564e-13, 18.6% of mean; min 6.760657e-13, max 1.017099e-12)
- `sigma_startup16_8`: mean 1.176839e-12 over 4 seeds (sd 4.366276e-13, 37.1% of mean; min 8.587308e-13, max 1.814335e-12)
- `i_ring_a`: mean 1.887166e-05 over 4 seeds (sd 7.049384e-11, 0.0% of mean; min 1.887157e-05, max 1.887173e-05)
- `i_tap_a`: mean 4.104964e-06 over 4 seeds (sd 9.237032e-11, 0.0% of mean; min 4.104863e-06, max 4.105048e-06)
- `p_active_w`: mean 6.227647e-05 over 4 seeds (sd 2.326296e-10, 0.0% of mean; min 6.227619e-05, max 6.227671e-05)
- `p_tap_w`: mean 1.354638e-05 over 4 seeds (sd 3.048222e-10, 0.0% of mean; min 1.354605e-05, max 1.354666e-05)
- `e_per_cycle_j`: mean 1.779745e-13 over 4 seeds (sd 5.503739e-19, 0.0% of mean; min 1.779740e-13, max 1.779751e-13)
- `c_eff_node_f`: mean 3.268586e-15 over 4 seeds (sd 1.010786e-20, 0.0% of mean; min 3.268577e-15, max 3.268597e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `i_buf_a`: mean 9.498523e-06 over 4 seeds (sd 2.613822e-11, 0.0% of mean; min 9.498504e-06, max 9.498561e-06)
- `p_buf_w`: mean 3.134513e-05 over 4 seeds (sd 8.625622e-11, 0.0% of mean; min 3.134506e-05, max 3.134525e-05)
- `clk_period_s`: mean 1.000000e-06 over 4 seeds (sd 0, 0.0% of mean; min 1.000000e-06, max 1.000000e-06)
- `clk_periods_in_window`: mean 1.4632 over 4 seeds (sd 9.916779e-06, 0.0% of mean; min 1.46319, max 1.46321)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 172800 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- The buffer is DR-0018's shipped ro_buf subcircuit out of design/sampler_core.spice, unmodified -- the same cell design/xschem/ro_array_core.sch instantiates as xb1/xb2 since #82. This deck is therefore not testing a hypothetical mitigation; it is testing the arrangement the design already ships, in which the exported ro1/ro2 pins the DR-0016 digitizers tap are the BUFFER outputs and not the ring nodes.
- In the shipped array the buffer output drives the XOR combiner AND both digitizers; here it drives one digitizer only, so this deck's buffer is more lightly loaded than the shipped one. Two consequences, in opposite directions: i_buf_a is a FLOOR on the shipped buffer's own current, and the residual clk-locked disturbance measured on the ring node is an UPPER BOUND on the shipped arrangement's, because what the clock modulates is a fixed capacitance on the buffer's output node and the shipped node carries xa1's input capacitance in addition, which can only make the modulated fraction smaller. Neither is a measurement of the shipped arrangement, which this family does not contain.
- sigma is measured at v(ro1), the RAW ring node UPSTREAM of the buffer, exactly as sim/tb/ro-array-coupling-xor-driven-buffered/ measures it and for the same reason: the question is whether the buffer keeps the disturbance off the ring's own oscillating node. Probing the buffer output would answer a different and trivial question.
- Read against sim/tb/ring-liveness-tap-phase-buffered-shut/, not against the unbuffered controls: inserting the buffer changes the ring's load as well as isolating it, so the buffered pair is the one-change ratio and the unbuffered pair is its counterpart. Reading this deck against the unbuffered controls spans two changes and attributes neither.
- tclk = 1 us (1 MHz), the same rate and for the same reason as sim/tb/ring-liveness-tap-phase-clocked/ -- DR-0003's ratified raw-rate floor, which is the rate most favourable to the digitizer that the specification permits. Nothing here is measured at any other clock rate.
- tstop is 3.0 us rather than issue #51's 2.9 us because the digitizer-loaded ring is slower in the -open and -clocked variants of this family and 770 rises there take ~2.7 us; every deck in the family uses the same tstop so the runs are like-for-like. Nothing about the window changed: it still opens 256 periods after start-up and spans 512 periods.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used, exactly as issue #51's variants do. They are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.
- rst_n is held HIGH from t=0 with no edge. DR-0014's reset is an initialisation input; the digitizer's own output (ring_bit1) is not measured by this deck, which measures what the digitizer does to the RING.
- abstol=1e-10 (tb.json "options"), 100x looser than ngspice's 1e-12 default, on EVERY deck in this family -- including the four whose clock never moves and which converge without it. Without the relaxation the two clocked decks abort with "Timestep too small ... trouble with node vtap#branch" at a clock edge, exactly the abort sim/tb/sampler-array-digitize/ bisected and documented for the same cell driven from the same kind of external edge; softer edges (20 ns) and moving the first edge past ring start-up were both tried here and neither fixes it, matching that deck's own finding that edge rate is not the cause. The relaxation is applied to the static decks too, even though they do not need it, because this family's whole claim is a ratio between decks and a ratio between two different solver tolerances would not be one. 100 pA is ~3e-6 of this ring's ~35 uA supply current. The check that it is benign is internal to the family: the static decks' sigma_1 and seed spread can be read against sim/records/2026-08-01-ro-ring5-starved-jitter-long-02.md, which was taken at ngspice's default tolerances -- a relaxation that injected numerical jitter would show up there as an inflated sigma_1 with a collapsed seed spread.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
