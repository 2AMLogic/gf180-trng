---
record: 2026-09-11-sampler-array-digitize-extracted-routed-02
date: 2026-09-11T08:44:19Z
status: valid

testbench:
  path: sim/tb/sampler-array-digitize-extracted-routed/tb_sampler_array_digitize_extracted_routed.sp
  sha: 44a8debe76d12f3beb765849f88ed1f9d3e44503
netlist:
  path: layout/pex/ro_ring_pair.routed.ntap.extracted.spice
  sha: 79fa4013c68990cba19e5972a070112dd515bf3e
repo_commit: 5b2a4e5828c91805e2109d8092c8a4a8b4550084-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /Users/rwalters/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6.2-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran-noise
  tstop: 200n
  tstep: 10p (print step; also ngspice's tmax. Matched to vn_dt = 10 ps, the noise sources' own breakpoint spacing, which already floors the solver step -- a finer print step would multiply output size and runtime without changing what the solver does)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 11 sources per ring, 22 in total
  runs: 3
seeds: [1, 2, 3]

raw:
  path: sim/records/raw/2026-09-11-sampler-array-digitize-extracted-routed-02/
  files:
    - ss_-40c_3.63v-run0.spice  sha256:007c9b8cd34240c3bccaa81d4eb9c57a67f2673f73d1e1de76fb1659c9c08c94
    - ss_-40c_3.63v-run0.log  sha256:bb56946f842ecf8d0aaae387dad656b0bf317c3e2cef3242c0f3f0f3b1a66542
    - ss_-40c_3.63v-run1.spice  sha256:0a630834373785ac4b63b932026d51eb2dadeb00c7876996f7ecbf6932c0a39c
    - ss_-40c_3.63v-run1.log  sha256:44d2507b52b3185f69b470fa1cf5b04bbb40ad1b3377057858d2898d34cdd9c7
    - ss_-40c_3.63v-run2.spice  sha256:92cadd732c14d6961b13dfac673e817edfccbbb35840d9cfcab7c6ba9cb85351
    - ss_-40c_3.63v-run2.log  sha256:6c5448e8f60e66a610ed69e24f550480a7ffeb38d672531b537e49037a35e322
wall_time: 12.2m
---

## Result

- `rb_rst_v`: mean -4.237824e-05 over 3 seeds (sd 6.546741e-06, 15.4% of mean; min -4.834201e-05, max -3.537331e-05)
- `rv_rst_v`: mean -4.343225e-05 over 3 seeds (sd 6.509922e-06, 15.0% of mean; min -4.936324e-05, max -3.646718e-05)
- `b0_v`: mean 0.00218936 over 3 seeds (sd 1.034527e-05, 0.5% of mean; min 0.00218237, max 0.00220124)
- `b1_v`: mean -0.00273618 over 3 seeds (sd 4.647852e-06, 0.2% of mean; min -0.00273952, max -0.00273087)
- `b2_v`: mean -0.00254496 over 3 seeds (sd 6.455953e-06, 0.3% of mean; min -0.00254878, max -0.00253751)
- `b3_v`: mean -7.748864e-05 over 3 seeds (sd 7.724041e-06, 10.0% of mean; min -8.387747e-05, max -6.890461e-05)
- `b4_v`: mean 3.63034 over 3 seeds (sd 1.205543e-05, 0.0% of mean; min 3.63032, max 3.63035)
- `b5_v`: mean 3.63134 over 3 seeds (sd 1.001665e-05, 0.0% of mean; min 3.63133, max 3.63135)
- `b6_v`: mean 3.63156 over 3 seeds (sd 3.470351e-05, 0.0% of mean; min 3.63153, max 3.6316)
- `b7_v`: mean 3.64905 over 3 seeds (sd 1.400000e-05, 0.0% of mean; min 3.64903, max 3.64906)
- `b8_v`: mean 3.62315 over 3 seeds (sd 2.064784e-05, 0.0% of mean; min 3.62314, max 3.62317)
- `b9_v`: mean 3.63257 over 3 seeds (sd 8.216447e-05, 0.0% of mean; min 3.63248, max 3.63264)
- `rv0_v`: mean 3.632 over 3 seeds (sd 1.137248e-05, 0.0% of mean; min 3.63199, max 3.63201)
- `rv9_v`: mean 3.6301 over 3 seeds (sd 4.454211e-05, 0.0% of mean; min 3.63005, max 3.63014)
- `ones_count`: mean 6 over 3 seeds (sd 0, 0.0% of mean; min 6, max 6)
- `worst_rail_dev_v`: mean 0.00684867 over 3 seeds (sd 2.064784e-05, 0.3% of mean; min 0.006825, max 0.006863)
- `period_r1`: mean 1.072637e-08 over 3 seeds (sd 1.420935e-13, 0.0% of mean; min 1.072623e-08, max 1.072651e-08)
- `period_r2`: mean 1.025001e-08 over 3 seeds (sd 1.637548e-13, 0.0% of mean; min 1.024982e-08, max 1.025011e-08)
- `f_r1`: mean 9.322817e+07 over 3 seeds (sd 1235, 0.0% of mean; min 9.322695e+07, max 9.322942e+07)
- `f_r2`: mean 9.756086e+07 over 3 seeds (sd 1558.65, 0.0% of mean; min 9.755989e+07, max 9.756266e+07)
- `freq_ratio_r2_r1`: mean 1.04647 over 3 seeds (sd 2.967765e-05, 0.0% of mean; min 1.04645, max 1.04651)
- `ring_periods_per_sample`: mean 0.932282 over 3 seeds (sd 1.235003e-05, 0.0% of mean; min 0.932269, max 0.932294)
- `xo_swing_v`: mean 3.67854 over 3 seeds (sd 2.904992e-05, 0.0% of mean; min 3.6785, max 3.67856)
- `ring1_swing_v`: mean 3.41365 over 3 seeds (sd 2.296529e-04, 0.0% of mean; min 3.4134, max 3.41385)
- `xo_trans_per_s`: mean 3.815781e+08 over 3 seeds (sd 1492.79, 0.0% of mean; min 3.815764e+08, max 3.815792e+08)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-array-digitize-extracted-routed --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --timeout 3600 --no-write
python3 sim/run_corners.py sampler-array-digitize-extracted-routed --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --timeout 3600 --no-write
python3 sim/run_corners.py sampler-array-digitize-extracted-routed --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --timeout 3600 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_ring_pair.routed.ntap.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, ROUTING-level-parasitic-annotated for both rings (layout/pex/build.py): every drawn leaf cell's own device geometry and internal metal, PLUS each assembled ring's hand-routed metal1 stage-to-stage chain and metal2/via1 vddr/vss straps. Still NOT a full-chip extraction -- inter-region routing between layout/floorplan/'s guarded regions is not drawn (20 um isolation channel, no signal routing), so it cannot be extracted. See layout/pex/build.py's module docstring and sim/characterization-post-layout-extracted.md §7.
- NOT a rate measurement. The sample clock here is 100 MHz (param tclk = 10 ns), two orders of magnitude above DR-0003's ratified > 1 Mbps raw target, chosen so that ten raw bits fit inside a transient-noise window this array can afford to simulate. Sampling faster than the target accumulates LESS jitter per bit, so this is the conservative direction for a functional demonstration and the wrong direction for any entropy claim.
- NOT an entropy measurement. The injected per-stage noise is a fixed synthetic white PSD (1e-16 V^2/Hz), not this cell's physical device noise, so the bit pattern below is evidence that the sampler digitizes a live, noisy source -- not evidence of how much min-entropy each bit carries. Recovering physical jitter needs sim/tb/rostage-noise/'s per-corner device-noise density and DR-0010's jitter-energy law.
- Ten bits is far too short a sequence for any statistical claim. No bias, correlation or randomness assertion is made or implied by the ones_count figure; it is reported so a reader can see the bits are not all identical, and for no other purpose.
- abstol is relaxed to 1e-10 (100x ngspice's 1e-12 default) because this deck does not converge at the default -- see the testbench header for the bisection that established it is not a noise, edge-rate or sampler-cell effect. 100 pA is ~5e-6 of this array's per-ring supply current, and the measured quantities are settled node voltages and ring periods rather than currents, but the relaxation is real and is stated rather than absorbed.
- The sample clock has a 1 ns edge (param tclk_tr) on a 10 ns period, so the effective sampling instant is defined only to within the clock's transit through the transmission gates' switching threshold. The sharp-edge (1 ps) case is covered at the real target period by sim/tb/sampler-dff-setup-hold/.
- The array's top-level wiring is restated in the testbench fragment rather than instantiated from sampler_core, because ngspice cannot insert a series noise source inside a subcircuit. At routing level the inter-stage wire IS inside one, so each ring is instantiated from the _ntap variant layout/pex/build.py emits: it re-points each of the eleven ring nets' gate-side parasitic star resistors onto a second hub and promotes both hubs to ports, so tying a pair together is electrically identical to the untapped ring (a 0 V source is a short; same cards, same star resistances, same grounded capacitance) and the noise source goes across the pair. That equivalence is held to BYTE equality by layout/tests/test_pex_noise_tap.py, not asserted. One consequence is stated rather than hidden: each net's lumped grounded capacitance sits on the DRIVER side of the tap, as it does in the leaf-level deck (where the wire capacitance lives inside the driving cell's own extraction, ahead of the source).
- xor2 and both sampler_dff instances are LEAF-level in this deck, not routing-level. Deliberate: this deck's pre-layout ancestor wires them up itself (no ro_buf, no ring-liveness samplers), so substituting combiner_sampler_routed_extracted would have changed the topology as well as the parasitics and the leaf-vs-routed delta would no longer isolate the ring routing -- the only place this testbench's entropy comes from.
- The n11/n21 node names this deck's .ic lines address are bound to each ring wrapper's FIRST TAPPED NET IN klt extract's OWN HEADER ORDER, not to the NAND output the leaf-level deck's n11/n21 were. A flat extraction does not record which stage a net belonged to (klayout-tools#1666), and this deck does not need it to: all eleven noise sources are identical, each sits between one net's driver side and that same net's receiver side, and the .ic only has to kick the ring off its unstable symmetric DC equilibrium, which any single ring node does. Per-stage attribution of a particular measured quantity to a particular physical stage is NOT available from this deck and is not claimed.
- TRANSIENT WINDOW LENGTHENED relative to the -extracted family (tran 10p 132n -> tran 10p 200n), for one reason: the routed rings are ~37% slower, so the 14th rising edge the period measurement addresses no longer falls inside a 132 ns window and ngspice reports `out of interval` rather than a number. The same edges are addressed, the same 12 periods are averaged, and every sampled bit (39-129 ns) and swing window (30-130 ns) sits where it did. How much the lengthening itself perturbs the earlier part of the run was MEASURED rather than assumed, because a transient-noise run's solver path is not guaranteed independent of where it ends: the same seed at tstop = 200 ns and at tstop = 250 ns (tt/27 C/3.30 V, seed 1) returns the same ten bit DECISIONS and the same ones_count, with every period and swing agreeing to 5 significant figures and the near-rail bit voltages differing by at most 2.4e-4 V on a 3.3 V rail. That residual is this deck's own solver-path sensitivity, not a change in what was sampled, and it is smaller than the seed-to-seed spread the records already report.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
