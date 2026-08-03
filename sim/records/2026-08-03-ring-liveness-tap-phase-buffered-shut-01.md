---
record: 2026-08-03-ring-liveness-tap-phase-buffered-shut-01
date: 2026-08-03T05:44:52Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-phase-buffered-shut/tb_ring_liveness_tap_phase_buffered_shut.sp
  sha: 1aceebab88364722d149c9df878359d36ce1b447
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
  path: sim/records/raw/2026-08-03-ring-liveness-tap-phase-buffered-shut-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:83d9abbaaf158813a0fa60f435ebccd3b517f401daa2bb2fc98006c3f15bf5c6
    - tt_27c_3.30v-run0.log  sha256:774df00377a1e55cf3221407af2274653e750cc79f960f60ebf1fdc68cfbf2ba
    - tt_27c_3.30v-run1.spice  sha256:e21b760ff2974d5ec2f4b060daf8064e0afccd4e0c93dee073aec398d77487e2
    - tt_27c_3.30v-run1.log  sha256:4274525fe590eebde8a8a3c4cf8444f26551cf0b38e45ae1e1e4b6cf5ba89bb1
    - tt_27c_3.30v-run2.spice  sha256:cf454c98122ce6454ee83b1454b595d0511e268e246d804f4f4fcbf4e5ed2629
    - tt_27c_3.30v-run2.log  sha256:d5fd70bb7b62861669d4495eea7f642aba63d6dbf4bc121160c74785efdbe7b4
    - tt_27c_3.30v-run3.spice  sha256:7df93ae41f2916f4b027618bd2730c89e895e8b5892f3bb0996f66cb91358a3c
    - tt_27c_3.30v-run3.log  sha256:cdd4ba81b67805dab9917b29865a994209668010de9334d322fd7afcd1c1e030
wall_time: 211.5m
---

## Result

- `period`: mean 2.874046e-09 over 4 seeds (sd 3.454190e-14, 0.0% of mean; min 2.874004e-09, max 2.874088e-09)
- `f_osc`: mean 3.479415e+08 over 4 seeds (sd 4181.76, 0.0% of mean; min 3.479364e+08, max 3.479466e+08)
- `period_startup16`: mean 2.874038e-09 over 4 seeds (sd 5.879547e-14, 0.0% of mean; min 2.873986e-09, max 2.874094e-09)
- `period_b00`: mean 2.874054e-09 over 4 seeds (sd 9.873800e-14, 0.0% of mean; min 2.873910e-09, max 2.874127e-09)
- `period_b01`: mean 2.874088e-09 over 4 seeds (sd 4.992400e-14, 0.0% of mean; min 2.874044e-09, max 2.874131e-09)
- `period_b02`: mean 2.874004e-09 over 4 seeds (sd 4.443498e-14, 0.0% of mean; min 2.873965e-09, max 2.874067e-09)
- `period_b03`: mean 2.874099e-09 over 4 seeds (sd 7.014579e-14, 0.0% of mean; min 2.874002e-09, max 2.874162e-09)
- `period_b04`: mean 2.874056e-09 over 4 seeds (sd 7.869011e-14, 0.0% of mean; min 2.873965e-09, max 2.874135e-09)
- `period_b05`: mean 2.874020e-09 over 4 seeds (sd 9.601996e-14, 0.0% of mean; min 2.873925e-09, max 2.874133e-09)
- `period_b06`: mean 2.874113e-09 over 4 seeds (sd 4.790157e-14, 0.0% of mean; min 2.874073e-09, max 2.874175e-09)
- `period_b07`: mean 2.873975e-09 over 4 seeds (sd 5.384520e-14, 0.0% of mean; min 2.873898e-09, max 2.874023e-09)
- `period_b08`: mean 2.874062e-09 over 4 seeds (sd 6.133165e-14, 0.0% of mean; min 2.874000e-09, max 2.874146e-09)
- `period_b09`: mean 2.874062e-09 over 4 seeds (sd 5.103104e-14, 0.0% of mean; min 2.874000e-09, max 2.874125e-09)
- `period_b10`: mean 2.874026e-09 over 4 seeds (sd 5.208334e-14, 0.0% of mean; min 2.873958e-09, max 2.874083e-09)
- `period_b11`: mean 2.873979e-09 over 4 seeds (sd 5.379144e-14, 0.0% of mean; min 2.873917e-09, max 2.874042e-09)
- `period_b12`: mean 2.874047e-09 over 4 seeds (sd 5.208333e-14, 0.0% of mean; min 2.873979e-09, max 2.874104e-09)
- `period_b13`: mean 2.874109e-09 over 4 seeds (sd 6.883411e-14, 0.0% of mean; min 2.874062e-09, max 2.874208e-09)
- `period_b14`: mean 2.874073e-09 over 4 seeds (sd 1.208812e-13, 0.0% of mean; min 2.873917e-09, max 2.874208e-09)
- `period_b15`: mean 2.874047e-09 over 4 seeds (sd 5.479075e-14, 0.0% of mean; min 2.874000e-09, max 2.874125e-09)
- `sigma_1`: mean 6.952884e-13 over 4 seeds (sd 2.094741e-14, 3.0% of mean; min 6.757611e-13, max 7.245211e-13)
- `sigma_2`: mean 8.131116e-13 over 4 seeds (sd 2.610049e-14, 3.2% of mean; min 7.739654e-13, max 8.265016e-13)
- `sigma_4`: mean 1.012682e-12 over 4 seeds (sd 4.196422e-14, 4.1% of mean; min 9.598092e-13, max 1.047258e-12)
- `sigma_8`: mean 1.330624e-12 over 4 seeds (sd 9.512556e-14, 7.1% of mean; min 1.210069e-12, max 1.419094e-12)
- `sigma_16`: mean 1.768921e-12 over 4 seeds (sd 1.319270e-13, 7.5% of mean; min 1.589108e-12, max 1.903132e-12)
- `sigma_32`: mean 2.417872e-12 over 4 seeds (sd 3.894250e-13, 16.1% of mean; min 2.021345e-12, max 2.814816e-12)
- `sigma_64`: mean 3.501353e-12 over 4 seeds (sd 7.780324e-13, 22.2% of mean; min 2.741511e-12, max 4.288526e-12)
- `sigma_128`: mean 4.937430e-12 over 4 seeds (sd 1.375583e-12, 27.9% of mean; min 3.666278e-12, max 6.373109e-12)
- `sigma_startup16_1`: mean 5.440146e-13 over 4 seeds (sd 6.821937e-14, 12.5% of mean; min 4.577890e-13, max 6.246938e-13)
- `sigma_startup16_2`: mean 6.454558e-13 over 4 seeds (sd 1.865303e-13, 28.9% of mean; min 3.898922e-13, max 8.162475e-13)
- `sigma_startup16_4`: mean 8.775450e-13 over 4 seeds (sd 3.085855e-13, 35.2% of mean; min 4.610657e-13, max 1.150330e-12)
- `sigma_startup16_8`: mean 1.258755e-12 over 4 seeds (sd 6.809195e-13, 54.1% of mean; min 6.669843e-13, max 2.015807e-12)
- `i_ring_a`: mean 1.881852e-05 over 4 seeds (sd 1.249733e-10, 0.0% of mean; min 1.881837e-05, max 1.881868e-05)
- `i_tap_a`: mean 4.195489e-11 over 4 seeds (sd 1.161276e-12, 2.8% of mean; min 4.108587e-11, max 4.359793e-11)
- `p_active_w`: mean 6.210113e-05 over 4 seeds (sd 4.124106e-10, 0.0% of mean; min 6.210063e-05, max 6.210163e-05)
- `p_tap_w`: mean 1.384511e-10 over 4 seeds (sd 3.832209e-12, 2.8% of mean; min 1.355834e-10, max 1.438732e-10)
- `e_per_cycle_j`: mean 1.784815e-13 over 4 seeds (sd 9.610537e-19, 0.0% of mean; min 1.784804e-13, max 1.784827e-13)
- `c_eff_node_f`: mean 3.277897e-15 over 4 seeds (sd 1.765013e-20, 0.0% of mean; min 3.277876e-15, max 3.277919e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `i_buf_a`: mean 7.810580e-06 over 4 seeds (sd 7.200322e-11, 0.0% of mean; min 7.810507e-06, max 7.810677e-06)
- `p_buf_w`: mean 2.577491e-05 over 4 seeds (sd 2.376105e-10, 0.0% of mean; min 2.577467e-05, max 2.577523e-05)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-shut --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-shut --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-shut --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-shut --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 172800 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- The buffer is DR-0018's shipped ro_buf subcircuit out of design/sampler_core.spice, unmodified -- the same cell design/xschem/ro_array_core.sch instantiates as xb1/xb2 since #82. This deck is therefore not testing a hypothetical mitigation; it is testing the arrangement the design already ships, in which the exported ro1/ro2 pins the DR-0016 digitizers tap are the BUFFER outputs and not the ring nodes.
- In the shipped array the buffer output drives the XOR combiner AND both digitizers; here it drives one digitizer only, so this deck's buffer is more lightly loaded than the shipped one. Two consequences, in opposite directions: i_buf_a is a FLOOR on the shipped buffer's own current, and the residual clk-locked disturbance measured on the ring node is an UPPER BOUND on the shipped arrangement's, because what the clock modulates is a fixed capacitance on the buffer's output node and the shipped node carries xa1's input capacitance in addition, which can only make the modulated fraction smaller. Neither is a measurement of the shipped arrangement, which this family does not contain.
- sigma is measured at v(ro1), the RAW ring node UPSTREAM of the buffer, exactly as sim/tb/ro-array-coupling-xor-driven-buffered/ measures it and for the same reason: the question is whether the buffer keeps the disturbance off the ring's own oscillating node. Probing the buffer output would answer a different and trivial question.
- This is the denominator of the buffered pair's one-change ratio. Inserting the buffer changes two things about the ring at once (isolation, and a different load hence a different operating point), so the buffered clocked deck has to be read against a buffered quiet deck rather than against the unbuffered controls -- the same lesson sim/characterization-ring-buffer-mitigation.md (issue #75) records for its own pair.
- clk is held at vdd here and at vss in sim/tb/ring-liveness-tap-phase-buffered-open/. With the buffer in place the ring node does not see the digitizer's load directly, so the period difference between those two decks is not a load change seen by the ring: it is the part of the buffer's OUTPUT load change that reaches the ring node backwards through the buffer's own gate-drain capacitance. That residual is the quantity the buffered clocked deck's sigma_1 is predicted from, which is why both static points are measured here where issue #51 measured only one.
- tstop is 3.0 us rather than issue #51's 2.9 us because the digitizer-loaded ring is slower in the -open and -clocked variants of this family and 770 rises there take ~2.7 us; every deck in the family uses the same tstop so the runs are like-for-like. Nothing about the window changed: it still opens 256 periods after start-up and spans 512 periods.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used, exactly as issue #51's variants do. They are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.
- rst_n is held HIGH from t=0 with no edge. DR-0014's reset is an initialisation input; the digitizer's own output (ring_bit1) is not measured by this deck, which measures what the digitizer does to the RING.
- abstol=1e-10 (tb.json "options"), 100x looser than ngspice's 1e-12 default, on EVERY deck in this family -- including the four whose clock never moves and which converge without it. Without the relaxation the two clocked decks abort with "Timestep too small ... trouble with node vtap#branch" at a clock edge, exactly the abort sim/tb/sampler-array-digitize/ bisected and documented for the same cell driven from the same kind of external edge; softer edges (20 ns) and moving the first edge past ring start-up were both tried here and neither fixes it, matching that deck's own finding that edge rate is not the cause. The relaxation is applied to the static decks too, even though they do not need it, because this family's whole claim is a ratio between decks and a ratio between two different solver tolerances would not be one. 100 pA is ~3e-6 of this ring's ~35 uA supply current. The check that it is benign is internal to the family: the static decks' sigma_1 and seed spread can be read against sim/records/2026-08-01-ro-ring5-starved-jitter-long-02.md, which was taken at ngspice's default tolerances -- a relaxation that injected numerical jitter would show up there as an inflated sigma_1 with a collapsed seed spread.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
