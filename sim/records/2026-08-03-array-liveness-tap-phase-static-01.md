---
record: 2026-08-03-array-liveness-tap-phase-static-01
date: 2026-08-03T17:43:31Z
status: valid

testbench:
  path: sim/tb/array-liveness-tap-phase-static/tb_array_liveness_tap_phase_static.sp
  sha: d7bc2ab99b3bff1a2211cd7435c0dd7230f3947c
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 56e6ef50ef1cb752a29ed66e91664774e8af108b-dirty

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
  tstop: 3.000003u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 22 sources, one in series with every stage input of both 11-stage rings
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-03-array-liveness-tap-phase-static-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:eeefb2bcf990b1112035ca18cfcce797825d395ad9a5d1fa3792a0e98d7ab413
    - tt_27c_3.30v-run0.log  sha256:9b37427da0e3b62e62c735b5587659add1238b06760ba8248d0b318270841419
    - tt_27c_3.30v-run1.spice  sha256:c9ce63ed2151f0994973fb0d3ceb6588dd871caa921f6d4073cf8689355ff94b
    - tt_27c_3.30v-run1.log  sha256:ccd44218b4ca9aca1f87369b1dbb0a31a6ab8d916f618b8191b7ba1b93b74fb9
    - tt_27c_3.30v-run2.spice  sha256:fab565aee83cc6ae5a589c7d45b181cb2e017ddc16ac761223c5f85fc443b68a
    - tt_27c_3.30v-run2.log  sha256:2128ab911699fa7e72cb29ab6b514d566859dec98f7c97f11c712b287212cdc7
    - tt_27c_3.30v-run3.spice  sha256:d0565d30714095f28ebd789b8e2711fe1bd71be697ad4f3f00aeb3f2ddcc912b
    - tt_27c_3.30v-run3.log  sha256:1cd56bd276b6e2ac4f6be7eac0febbe674f3fcf9781db6fd3f336d75933f5ebe
wall_time: 726.8m
---

## Result

- `period`: mean 6.673868e-09 over 4 seeds (sd 1.252996e-14, 0.0% of mean; min 6.673851e-09, max 6.673881e-09)
- `f_osc`: mean 1.498381e+08 over 4 seeds (sd 281.316, 0.0% of mean; min 1.498378e+08, max 1.498385e+08)
- `period_startup16`: mean 6.673895e-09 over 4 seeds (sd 8.603158e-14, 0.0% of mean; min 6.673772e-09, max 6.673961e-09)
- `period_r2`: mean 6.237828e-09 over 4 seeds (sd 2.652131e-14, 0.0% of mean; min 6.237791e-09, max 6.237850e-09)
- `period_b00`: mean 6.673968e-09 over 4 seeds (sd 8.215943e-14, 0.0% of mean; min 6.673881e-09, max 6.674070e-09)
- `period_b01`: mean 6.673933e-09 over 4 seeds (sd 1.090256e-13, 0.0% of mean; min 6.673808e-09, max 6.674046e-09)
- `period_b02`: mean 6.673758e-09 over 4 seeds (sd 5.475115e-14, 0.0% of mean; min 6.673696e-09, max 6.673829e-09)
- `period_b03`: mean 6.673776e-09 over 4 seeds (sd 1.029302e-13, 0.0% of mean; min 6.673662e-09, max 6.673900e-09)
- `period_b04`: mean 6.674014e-09 over 4 seeds (sd 8.984138e-14, 0.0% of mean; min 6.673933e-09, max 6.674142e-09)
- `period_b05`: mean 6.673717e-09 over 4 seeds (sd 9.724205e-14, 0.0% of mean; min 6.673617e-09, max 6.673850e-09)
- `period_b06`: mean 6.673893e-09 over 4 seeds (sd 7.331242e-14, 0.0% of mean; min 6.673817e-09, max 6.673979e-09)
- `period_b07`: mean 6.673990e-09 over 4 seeds (sd 7.115936e-14, 0.0% of mean; min 6.673917e-09, max 6.674083e-09)
- `period_b08`: mean 6.673729e-09 over 4 seeds (sd 7.216879e-14, 0.0% of mean; min 6.673625e-09, max 6.673792e-09)
- `period_b09`: mean 6.673833e-09 over 4 seeds (sd 9.001027e-14, 0.0% of mean; min 6.673750e-09, max 6.673958e-09)
- `period_b10`: mean 6.673979e-09 over 4 seeds (sd 7.978556e-14, 0.0% of mean; min 6.673917e-09, max 6.674083e-09)
- `period_b11`: mean 6.673625e-09 over 4 seeds (sd 1.178511e-13, 0.0% of mean; min 6.673458e-09, max 6.673708e-09)
- `period_b12`: mean 6.673938e-09 over 4 seeds (sd 7.216879e-14, 0.0% of mean; min 6.673875e-09, max 6.674042e-09)
- `period_b13`: mean 6.673948e-09 over 4 seeds (sd 8.589806e-14, 0.0% of mean; min 6.673833e-09, max 6.674042e-09)
- `period_b14`: mean 6.673833e-09 over 4 seeds (sd 9.001031e-14, 0.0% of mean; min 6.673708e-09, max 6.673917e-09)
- `period_b15`: mean 6.673854e-09 over 4 seeds (sd 1.295469e-13, 0.0% of mean; min 6.673708e-09, max 6.674000e-09)
- `sigma_1`: mean 1.286420e-12 over 4 seeds (sd 5.261458e-14, 4.1% of mean; min 1.223672e-12, max 1.338864e-12)
- `sigma_2`: mean 1.638655e-12 over 4 seeds (sd 5.226641e-14, 3.2% of mean; min 1.587393e-12, max 1.689209e-12)
- `sigma_4`: mean 2.266776e-12 over 4 seeds (sd 7.697506e-14, 3.4% of mean; min 2.187639e-12, max 2.345565e-12)
- `sigma_8`: mean 2.841587e-12 over 4 seeds (sd 8.327898e-14, 2.9% of mean; min 2.766718e-12, max 2.954108e-12)
- `sigma_16`: mean 2.379911e-12 over 4 seeds (sd 1.851440e-13, 7.8% of mean; min 2.102224e-12, max 2.475997e-12)
- `sigma_32`: mean 3.092944e-12 over 4 seeds (sd 2.571932e-13, 8.3% of mean; min 2.842382e-12, max 3.401296e-12)
- `sigma_64`: mean 4.168572e-12 over 4 seeds (sd 4.341071e-13, 10.4% of mean; min 3.769508e-12, max 4.700697e-12)
- `sigma_r2_1`: mean 6.934221e-13 over 4 seeds (sd 2.371045e-14, 3.4% of mean; min 6.689177e-13, max 7.185288e-13)
- `sigma_r2_2`: mean 8.023630e-13 over 4 seeds (sd 1.867912e-14, 2.3% of mean; min 7.834985e-13, max 8.213148e-13)
- `sigma_r2_4`: mean 9.967521e-13 over 4 seeds (sd 4.447046e-14, 4.5% of mean; min 9.380617e-13, max 1.037337e-12)
- `sigma_r2_8`: mean 1.256982e-12 over 4 seeds (sd 7.695671e-14, 6.1% of mean; min 1.168873e-12, max 1.335598e-12)
- `sigma_r2_16`: mean 1.602562e-12 over 4 seeds (sd 2.229838e-13, 13.9% of mean; min 1.361296e-12, max 1.809650e-12)
- `sigma_r2_32`: mean 1.911674e-12 over 4 seeds (sd 3.734666e-13, 19.5% of mean; min 1.560208e-12, max 2.306582e-12)
- `sigma_r2_64`: mean 2.343975e-12 over 4 seeds (sd 7.718151e-13, 32.9% of mean; min 1.589648e-12, max 3.146158e-12)
- `sigma_startup16_1`: mean 1.167429e-12 over 4 seeds (sd 1.317599e-13, 11.3% of mean; min 1.016036e-12, max 1.280709e-12)
- `sigma_startup16_2`: mean 1.563011e-12 over 4 seeds (sd 2.998215e-13, 19.2% of mean; min 1.141864e-12, max 1.798942e-12)
- `sigma_startup16_4`: mean 2.238232e-12 over 4 seeds (sd 8.062065e-13, 36.0% of mean; min 1.257027e-12, max 3.127493e-12)
- `sigma_startup16_8`: mean 3.591127e-12 over 4 seeds (sd 1.172521e-12, 32.7% of mean; min 1.955529e-12, max 4.631218e-12)
- `i_ring_a`: mean 1.896883e-05 over 4 seeds (sd 4.171531e-11, 0.0% of mean; min 1.896878e-05, max 1.896887e-05)
- `p_active_w`: mean 6.259714e-05 over 4 seeds (sd 1.376605e-10, 0.0% of mean; min 6.259697e-05, max 6.259726e-05)
- `e_per_cycle_j`: mean 4.177650e-13 over 4 seeds (sd 6.931866e-19, 0.0% of mean; min 4.177641e-13, max 4.177657e-13)
- `c_eff_node_f`: mean 3.487478e-15 over 4 seeds (sd 5.786644e-21, 0.0% of mean; min 3.487471e-15, max 3.487484e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py array-liveness-tap-phase-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 86400 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Issue #87's shipped-array phase-cost family. Every deck in it carries the SHIPPED design/sampler_core.spice topology -- two 11-stage rings, both DR-0018 per-ring output buffers, the XOR combiner, and the sampler_dff instances named in this deck's own description -- and the four decks differ from each other in exactly two axes: whether clk toggles, and whether the two DR-0016 per-ring liveness digitizers (xsr1/xsr2) are present. Every ratio this family reports is taken across ONE of those axes with the other held fixed, which is the one-change discipline sim/characterization-array-ring-coupling.md (#51) and sim/characterization-liveness-tap-phase-cost.md (#76) both use.
- Window geometry is matched to #76's family in TIME rather than in ring-period count, and that is a deliberate departure that must be read before comparing the two. #76 opened its window 256 ring periods after start-up and spanned 512 ring periods on a ~2.86 ns 5-stage ring: 0.73 us of settling, a 1.46 us window, 1.46 clk periods. An 11-stage ring's period is ~7.1 ns, so this family opens at 128 ring periods and spans 256: 0.91 us of settling, a 1.82 us window, 1.82 clk periods. Both are LONGER in absolute time and cover MORE clk periods than #76's, which is what a clk-locked disturbance depends on -- but sigma_N is a period-count statistic, so the two families' sigma values are NOT interchangeable and only their within-family clocked/static RATIOS are compared. The lag ladder is truncated at 64 (a quarter of the window) where #76's was truncated at 128 (a quarter of its window).
- Both rings are restated stage by stage rather than instantiated as ro_ring11, because the trnoise() sources go in series with every stage input and cannot be placed from outside the subckt. Every stage is nonetheless an instance of ro_nand2 / ro_stage out of design/sampler_core.spice -- this tb.json's own design netlist -- wired as ro_ring11 wires them, with ro_array_core's own per-ring wstv (0.220u for ring 1, 0.240u for ring 2). Everything downstream of the ring nodes (both ro_buf, the xor2, every sampler_dff) is instantiated from that netlist unmodified. sim/tb/ro-array-coupling-xor-driven/ makes the same compromise for the same reason. `python3 design/netlist.py --check` ties the netlist to the schematic; nothing ties this deck's restated ring wiring to ro_ring11's except review.
- sigma_* here is NOT a jitter measurement if what it captures is deterministic. The estimator is the control's, but it measures the spread of period-to-period increments from whatever cause, and a load modulation locked to clk enters it exactly as noise would. The seed spread and the accumulation exponent reported alongside are what tell the two apart, and no entropy claim may be built on this record's sigma either way.
- Ring 2 is running in every deck of this family, so ring 1's sigma_* is measured while its combiner neighbour switches -- exactly the arrangement sim/characterization-array-ring-coupling.md rules INADMISSIBLE as evidence for DR-0007 SS2's per-ring sizing law. That is intended and is not a defect here: this family reports RATIOS taken inside one topology with clk as the only difference, so the neighbour's contribution is present identically in numerator and denominator. No absolute sigma_acc from this family may be cited for the sizing law.
- sigma_r2_* are the same ladder on ring 2 (wstv = 0.240u), measured inside the same run. Ring 2 is an independent replicate of the same question on the array's other ring, not a second experiment: it shares this deck's clk, its supply and its seed.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used. They are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 256-period window is the precise measurement.
- i_ring_a / p_active_w / e_per_cycle_j / c_eff_node_f are RING 1's alone -- the block-side supply vd is a separate ammeter, so the buffers', combiner's and digitizers' own switching current is outside them. Their own power is not re-measured here; sim/tb/ring-liveness-tap-power/ owns that at three PVT points.
- rst_n is held at vdd for the whole run, so every digitizer is out of reset throughout and contributes no reset edge. DR-0014's gated reset behaviour is measured by sim/tb/sampler-dff-reset-clocked/ and is not what this deck is about.
- Ideal supply. vr1/vr2 meter each ring and vd meters the whole block side (both buffers, the combiner, every digitizer) as sampler_core wires them, but all three are zero-volt ammeters off ONE ideal vsup with no impedance for one branch's current to develop a voltage across. This deck therefore says nothing about supply-network coupling from the digitizers' own switching, which is a SECOND path a real block has and this one does not. The finding is a lower bound on what a built block will show, not an upper one.
- Pre-layout, schematic-derived netlist (design/sampler_core.spice), no extracted parasitics. Layout adds coupling paths between a clocked cell and a ring node; it removes none.
- clk and rst_n are DC sources: this deck contains no edge anywhere after start-up, which is what makes it the static reference for its pair. It measures ONE of the two states its clocked partner alternates between (every sampler_dff's master transmission gate OFF) and is not on its own a statement about the shipped, clocked arrangement.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
