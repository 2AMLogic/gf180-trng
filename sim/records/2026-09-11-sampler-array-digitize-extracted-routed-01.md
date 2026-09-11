---
record: 2026-09-11-sampler-array-digitize-extracted-routed-01
date: 2026-09-11T08:39:31Z
status: valid

testbench:
  path: sim/tb/sampler-array-digitize-extracted-routed/tb_sampler_array_digitize_extracted_routed.sp
  sha: 44a8debe76d12f3beb765849f88ed1f9d3e44503
netlist:
  path: layout/pex/ro_ring_pair.routed.ntap.extracted.spice
  sha: 79fa4013c68990cba19e5972a070112dd515bf3e
repo_commit: 5b2a4e5828c91805e2109d8092c8a4a8b4550084

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /Users/rwalters/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6.2-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran-noise
  tstop: 200n
  tstep: 10p (print step; also ngspice's tmax. Matched to vn_dt = 10 ps, the noise sources' own breakpoint spacing, which already floors the solver step -- a finer print step would multiply output size and runtime without changing what the solver does)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 11 sources per ring, 22 in total
  runs: 3
seeds: [1, 2, 3]

raw:
  path: sim/records/raw/2026-09-11-sampler-array-digitize-extracted-routed-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:30aa2ffeac1f8364087163817488129875cd7772035a1ec74d806e658ffce373
    - tt_27c_3.30v-run0.log  sha256:93a3dcaa560a50dea5c855113b82f8128d5bf1b5f8311fe0a67949c49c534da4
    - tt_27c_3.30v-run1.spice  sha256:df7292d49d6b5309488f376737a8afa90f16aa6b98171dc8d54cdb5417fc5cee
    - tt_27c_3.30v-run1.log  sha256:6b2835cb3b27788a391af8950c7603e95989b70c34d0a2de6c123d80d3f7715a
    - tt_27c_3.30v-run2.spice  sha256:06a164c3808efe549e57f663c2b3ef099247a37cfd6f862902d5aaa947e26121
    - tt_27c_3.30v-run2.log  sha256:16eb19f97bcca7160a4589e4fd6c99367736caaccac72e5a7b0010a3cb4dfb7d
wall_time: 12.4m
---

## Result

- `rb_rst_v`: mean 3.060056e-04 over 3 seeds (sd 1.891243e-06, 0.6% of mean; min 3.046939e-04, max 3.081735e-04)
- `rv_rst_v`: mean 3.717917e-04 over 3 seeds (sd 2.392817e-06, 0.6% of mean; min 3.692642e-04, max 3.740221e-04)
- `b0_v`: mean -0.00598755 over 3 seeds (sd 4.688462e-05, 0.8% of mean; min -0.00603814, max -0.00594556)
- `b1_v`: mean 0.00118419 over 3 seeds (sd 1.615209e-05, 1.4% of mean; min 0.00117431, max 0.00120283)
- `b2_v`: mean 3.29785 over 3 seeds (sd 1.732051e-06, 0.0% of mean; min 3.29785, max 3.29785)
- `b3_v`: mean 6.943656e-04 over 3 seeds (sd 1.204794e-05, 1.7% of mean; min 6.847951e-04, max 7.078948e-04)
- `b4_v`: mean 3.29926 over 3 seeds (sd 6.244998e-06, 0.0% of mean; min 3.29926, max 3.29927)
- `b5_v`: mean 3.2977 over 3 seeds (sd 2.138535e-05, 0.0% of mean; min 3.29767, max 3.29771)
- `b6_v`: mean -4.079504e-04 over 3 seeds (sd 1.376362e-05, 3.4% of mean; min -4.162045e-04, max -3.920616e-04)
- `b7_v`: mean 3.29748 over 3 seeds (sd 1.844813e-05, 0.0% of mean; min 3.29746, max 3.2975)
- `b8_v`: mean 3.29974 over 3 seeds (sd 1.252996e-05, 0.0% of mean; min 3.29973, max 3.29976)
- `b9_v`: mean 3.30514 over 3 seeds (sd 7.782673e-05, 0.0% of mean; min 3.30508, max 3.30523)
- `rv0_v`: mean 3.29274 over 3 seeds (sd 4.005413e-05, 0.0% of mean; min 3.2927, max 3.29277)
- `rv9_v`: mean 3.30295 over 3 seeds (sd 5.270041e-05, 0.0% of mean; min 3.30291, max 3.30301)
- `ones_count`: mean 6 over 3 seeds (sd 0, 0.0% of mean; min 6, max 6)
- `worst_rail_dev_v`: mean 0.00252033 over 3 seeds (sd 1.844813e-05, 0.7% of mean; min 0.0025, max 0.002536)
- `period_r1`: mean 1.285229e-08 over 3 seeds (sd 1.161428e-13, 0.0% of mean; min 1.285216e-08, max 1.285237e-08)
- `period_r2`: mean 1.225774e-08 over 3 seeds (sd 2.959380e-13, 0.0% of mean; min 1.225743e-08, max 1.225803e-08)
- `f_r1`: mean 7.780712e+07 over 3 seeds (sd 703.125, 0.0% of mean; min 7.780668e+07, max 7.780793e+07)
- `f_r2`: mean 8.158110e+07 over 3 seeds (sd 1969.61, 0.0% of mean; min 8.157920e+07, max 8.158314e+07)
- `freq_ratio_r2_r1`: mean 1.0485 over 3 seeds (sd 3.339489e-05, 0.0% of mean; min 1.04847, max 1.04854)
- `ring_periods_per_sample`: mean 0.778071 over 3 seeds (sd 7.031257e-06, 0.0% of mean; min 0.778067, max 0.778079)
- `xo_swing_v`: mean 3.36139 over 3 seeds (sd 9.678328e-06, 0.0% of mean; min 3.36138, max 3.3614)
- `ring1_swing_v`: mean 3.08321 over 3 seeds (sd 3.275212e-04, 0.0% of mean; min 3.08294, max 3.08358)
- `xo_trans_per_s`: mean 3.187765e+08 over 3 seeds (sd 2934.51, 0.0% of mean; min 3.187743e+08, max 3.187798e+08)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-array-digitize-extracted-routed --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 3600 --no-write
python3 sim/run_corners.py sampler-array-digitize-extracted-routed --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 3600 --no-write
python3 sim/run_corners.py sampler-array-digitize-extracted-routed --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 3600 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
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
