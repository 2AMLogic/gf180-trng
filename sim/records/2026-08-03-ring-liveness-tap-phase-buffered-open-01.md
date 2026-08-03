---
record: 2026-08-03-ring-liveness-tap-phase-buffered-open-01
date: 2026-08-03T05:44:52Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-phase-buffered-open/tb_ring_liveness_tap_phase_buffered_open.sp
  sha: a89aae722d487ca0ee4f15e87693b1d0759b359c
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
  path: sim/records/raw/2026-08-03-ring-liveness-tap-phase-buffered-open-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:b137d30fb9b0926444b6a6b65412f5cc96aa45507d2d67580a7f9a57aae2d85a
    - tt_27c_3.30v-run0.log  sha256:4f9ea34998571ab4fbeb398aaa6b90d655320fba3c60805be6761a3f674562db
    - tt_27c_3.30v-run1.spice  sha256:9a85ba363af8070b1fef59e3de440245ea5319b2378341319be20c03e7845636
    - tt_27c_3.30v-run1.log  sha256:d2a7efe034f5a15dd3d868b01998d8bf65fa5ec70c37677865c4c459693840ac
    - tt_27c_3.30v-run2.spice  sha256:28d3198509d5e9e86261748703518c9f2a1c51def3c2400598866721ce8925b7
    - tt_27c_3.30v-run2.log  sha256:473957b55d0af789aa0216af1c089a226ae3c2e6ddd1f626edaf1781e757c915
    - tt_27c_3.30v-run3.spice  sha256:820507c1ef743c4749aee1a9d4891b0584a113b4f235576937f2f92bfe03b1fc
    - tt_27c_3.30v-run3.log  sha256:ddc55f33220dda73d0e89164757e84dd2f92d6b0bf8925972c7ce4c1f44b58e2
wall_time: 211.6m
---

## Result

- `period`: mean 2.846584e-09 over 4 seeds (sd 2.886070e-14, 0.0% of mean; min 2.846562e-09, max 2.846625e-09)
- `f_osc`: mean 3.512982e+08 over 4 seeds (sd 3561.69, 0.0% of mean; min 3.512932e+08, max 3.513009e+08)
- `period_startup16`: mean 2.846666e-09 over 4 seeds (sd 1.538225e-13, 0.0% of mean; min 2.846465e-09, max 2.846812e-09)
- `period_b00`: mean 2.846657e-09 over 4 seeds (sd 6.478405e-14, 0.0% of mean; min 2.846596e-09, max 2.846724e-09)
- `period_b01`: mean 2.846580e-09 over 4 seeds (sd 5.680982e-14, 0.0% of mean; min 2.846523e-09, max 2.846658e-09)
- `period_b02`: mean 2.846551e-09 over 4 seeds (sd 7.793958e-14, 0.0% of mean; min 2.846473e-09, max 2.846638e-09)
- `period_b03`: mean 2.846621e-09 over 4 seeds (sd 3.321921e-14, 0.0% of mean; min 2.846573e-09, max 2.846648e-09)
- `period_b04`: mean 2.846591e-09 over 4 seeds (sd 3.170388e-14, 0.0% of mean; min 2.846560e-09, max 2.846635e-09)
- `period_b05`: mean 2.846559e-09 over 4 seeds (sd 4.746161e-14, 0.0% of mean; min 2.846510e-09, max 2.846623e-09)
- `period_b06`: mean 2.846647e-09 over 4 seeds (sd 6.509376e-14, 0.0% of mean; min 2.846585e-09, max 2.846735e-09)
- `period_b07`: mean 2.846570e-09 over 4 seeds (sd 8.372088e-14, 0.0% of mean; min 2.846488e-09, max 2.846681e-09)
- `period_b08`: mean 2.846557e-09 over 4 seeds (sd 8.568727e-14, 0.0% of mean; min 2.846458e-09, max 2.846667e-09)
- `period_b09`: mean 2.846609e-09 over 4 seeds (sd 9.061106e-14, 0.0% of mean; min 2.846521e-09, max 2.846729e-09)
- `period_b10`: mean 2.846615e-09 over 4 seeds (sd 2.689571e-14, 0.0% of mean; min 2.846583e-09, max 2.846646e-09)
- `period_b11`: mean 2.846531e-09 over 4 seeds (sd 4.959323e-14, 0.0% of mean; min 2.846479e-09, max 2.846583e-09)
- `period_b12`: mean 2.846625e-09 over 4 seeds (sd 4.166665e-14, 0.0% of mean; min 2.846604e-09, max 2.846687e-09)
- `period_b13`: mean 2.846578e-09 over 4 seeds (sd 8.735937e-14, 0.0% of mean; min 2.846458e-09, max 2.846667e-09)
- `period_b14`: mean 2.846599e-09 over 4 seeds (sd 1.039929e-13, 0.0% of mean; min 2.846458e-09, max 2.846708e-09)
- `period_b15`: mean 2.846531e-09 over 4 seeds (sd 7.701762e-14, 0.0% of mean; min 2.846437e-09, max 2.846604e-09)
- `sigma_1`: mean 6.725796e-13 over 4 seeds (sd 8.707008e-15, 1.3% of mean; min 6.597816e-13, max 6.790262e-13)
- `sigma_2`: mean 7.987848e-13 over 4 seeds (sd 1.496880e-14, 1.9% of mean; min 7.833616e-13, max 8.117822e-13)
- `sigma_4`: mean 1.013738e-12 over 4 seeds (sd 1.861250e-14, 1.8% of mean; min 9.958562e-13, max 1.031907e-12)
- `sigma_8`: mean 1.363729e-12 over 4 seeds (sd 2.295644e-14, 1.7% of mean; min 1.334432e-12, max 1.386403e-12)
- `sigma_16`: mean 1.906065e-12 over 4 seeds (sd 8.270035e-14, 4.3% of mean; min 1.794119e-12, max 1.992436e-12)
- `sigma_32`: mean 2.697777e-12 over 4 seeds (sd 3.025517e-13, 11.2% of mean; min 2.443498e-12, max 3.132797e-12)
- `sigma_64`: mean 3.835468e-12 over 4 seeds (sd 9.747469e-13, 25.4% of mean; min 2.788583e-12, max 5.146220e-12)
- `sigma_128`: mean 5.796830e-12 over 4 seeds (sd 2.157693e-12, 37.2% of mean; min 3.313240e-12, max 8.482087e-12)
- `sigma_startup16_1`: mean 4.939098e-13 over 4 seeds (sd 1.318166e-13, 26.7% of mean; min 3.252945e-13, max 6.250954e-13)
- `sigma_startup16_2`: mean 6.432443e-13 over 4 seeds (sd 1.485099e-13, 23.1% of mean; min 4.416375e-13, max 7.856736e-13)
- `sigma_startup16_4`: mean 8.357693e-13 over 4 seeds (sd 1.686053e-13, 20.2% of mean; min 5.947377e-13, max 9.860541e-13)
- `sigma_startup16_8`: mean 1.299129e-12 over 4 seeds (sd 3.806378e-13, 29.3% of mean; min 8.754590e-13, max 1.683996e-12)
- `i_ring_a`: mean 1.890862e-05 over 4 seeds (sd 1.096270e-10, 0.0% of mean; min 1.890848e-05, max 1.890871e-05)
- `i_tap_a`: mean 6.890721e-06 over 4 seeds (sd 5.966595e-11, 0.0% of mean; min 6.890638e-06, max 6.890765e-06)
- `p_active_w`: mean 6.239846e-05 over 4 seeds (sd 3.617685e-10, 0.0% of mean; min 6.239797e-05, max 6.239875e-05)
- `p_tap_w`: mean 2.273938e-05 over 4 seeds (sd 1.968976e-10, 0.0% of mean; min 2.273911e-05, max 2.273952e-05)
- `e_per_cycle_j`: mean 1.776225e-13 over 4 seeds (sd 7.758953e-19, 0.0% of mean; min 1.776219e-13, max 1.776236e-13)
- `c_eff_node_f`: mean 3.262121e-15 over 4 seeds (sd 1.424971e-20, 0.0% of mean; min 3.262111e-15, max 3.262141e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `i_buf_a`: mean 1.067387e-05 over 4 seeds (sd 1.035298e-10, 0.0% of mean; min 1.067374e-05, max 1.067397e-05)
- `p_buf_w`: mean 3.522377e-05 over 4 seeds (sd 3.416480e-10, 0.0% of mean; min 3.522334e-05, max 3.522409e-05)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-open --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-open --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-open --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-open --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 172800 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- The buffer is DR-0018's shipped ro_buf subcircuit out of design/sampler_core.spice, unmodified -- the same cell design/xschem/ro_array_core.sch instantiates as xb1/xb2 since #82. This deck is therefore not testing a hypothetical mitigation; it is testing the arrangement the design already ships, in which the exported ro1/ro2 pins the DR-0016 digitizers tap are the BUFFER outputs and not the ring nodes.
- In the shipped array the buffer output drives the XOR combiner AND both digitizers; here it drives one digitizer only, so this deck's buffer is more lightly loaded than the shipped one. Two consequences, in opposite directions: i_buf_a is a FLOOR on the shipped buffer's own current, and the residual clk-locked disturbance measured on the ring node is an UPPER BOUND on the shipped arrangement's, because what the clock modulates is a fixed capacitance on the buffer's output node and the shipped node carries xa1's input capacitance in addition, which can only make the modulated fraction smaller. Neither is a measurement of the shipped arrangement, which this family does not contain.
- sigma is measured at v(ro1), the RAW ring node UPSTREAM of the buffer, exactly as sim/tb/ro-array-coupling-xor-driven-buffered/ measures it and for the same reason: the question is whether the buffer keeps the disturbance off the ring's own oscillating node. Probing the buffer output would answer a different and trivial question.
- This is the denominator of the buffered pair's one-change ratio. Inserting the buffer changes two things about the ring at once (isolation, and a different load hence a different operating point), so the buffered clocked deck has to be read against a buffered quiet deck rather than against the unbuffered controls -- the same lesson sim/characterization-ring-buffer-mitigation.md (issue #75) records for its own pair.
- clk is held at vss here and at vdd in sim/tb/ring-liveness-tap-phase-buffered-shut/. With the buffer in place the ring node does not see the digitizer's load directly, so the period difference between those two decks is not a load change seen by the ring: it is the part of the buffer's OUTPUT load change that reaches the ring node backwards through the buffer's own gate-drain capacitance. That residual is the quantity the buffered clocked deck's sigma_1 is predicted from, which is why both static points are measured here where issue #51 measured only one.
- tstop is 3.0 us rather than issue #51's 2.9 us because the digitizer-loaded ring is slower in the -open and -clocked variants of this family and 770 rises there take ~2.7 us; every deck in the family uses the same tstop so the runs are like-for-like. Nothing about the window changed: it still opens 256 periods after start-up and spans 512 periods.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used, exactly as issue #51's variants do. They are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.
- rst_n is held HIGH from t=0 with no edge. DR-0014's reset is an initialisation input; the digitizer's own output (ring_bit1) is not measured by this deck, which measures what the digitizer does to the RING.
- abstol=1e-10 (tb.json "options"), 100x looser than ngspice's 1e-12 default, on EVERY deck in this family -- including the four whose clock never moves and which converge without it. Without the relaxation the two clocked decks abort with "Timestep too small ... trouble with node vtap#branch" at a clock edge, exactly the abort sim/tb/sampler-array-digitize/ bisected and documented for the same cell driven from the same kind of external edge; softer edges (20 ns) and moving the first edge past ring start-up were both tried here and neither fixes it, matching that deck's own finding that edge rate is not the cause. The relaxation is applied to the static decks too, even though they do not need it, because this family's whole claim is a ratio between decks and a ratio between two different solver tolerances would not be one. 100 pA is ~3e-6 of this ring's ~35 uA supply current. The check that it is benign is internal to the family: the static decks' sigma_1 and seed spread can be read against sim/records/2026-08-01-ro-ring5-starved-jitter-long-02.md, which was taken at ngspice's default tolerances -- a relaxation that injected numerical jitter would show up there as an inflated sigma_1 with a collapsed seed spread.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
