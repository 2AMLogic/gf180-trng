---
record: 2026-08-03-ring-liveness-tap-phase-clocked-01
date: 2026-08-03T04:52:31Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-phase-clocked/tb_ring_liveness_tap_phase_clocked.sp
  sha: ddca65fb93846efc9c4ec047f1d59462500fc0a7
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: a1d86b3cf08426f173e49b7255a08033a17fdbba-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /home/ubuntu/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: Linux-7.0.0-1009-aws-x86_64-with-glibc2.39

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran-noise
  tstop: 2.900003u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources, one in series with every stage input
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-03-ring-liveness-tap-phase-clocked-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:024af9e07a9e85851a24bbd47d084e40fdee4ca7cf87190f7ac0dbd32affe1c5
    - tt_27c_3.30v-run0.log  sha256:47d8d577b2630bc1387bd98518e3851fc4bfff14737857d0756de0bf929ed6d5
    - tt_27c_3.30v-run1.spice  sha256:aeb130b930d699479e9583ae3dffffd7b13e13a4afbd25c6ee76bf8c09c31316
    - tt_27c_3.30v-run1.log  sha256:59111ab4ee2284d7087f823c33d033d58663fcf7783a3b3b8fc11f0f9b29aa8f
    - tt_27c_3.30v-run2.spice  sha256:cefba6542a45664c6cf80411418e814806e7e0078e4bc2a663b035323334cbd3
    - tt_27c_3.30v-run2.log  sha256:c26bdd2f42b5b0aff2f13bbae5d689c0e6db7040c49f74fefeacce9436822507
    - tt_27c_3.30v-run3.spice  sha256:8ef2bbfc3d3c7160616675e33bb909a45dd054fa481392ce773d5adf043f7357
    - tt_27c_3.30v-run3.log  sha256:10dca1e899688ed77149dc38ea2523740d54c3840595d7df78a14d4acfadfe3f
wall_time: 21.0m
---

## Result

- `period`: mean 3.044376e-09 over 4 seeds (sd 9.112789e-15, 0.0% of mean; min 3.044364e-09, max 3.044385e-09)
- `f_osc`: mean 3.284746e+08 over 4 seeds (sd 983.229, 0.0% of mean; min 3.284736e+08, max 3.284758e+08)
- `period_startup16`: mean 2.751802e-09 over 4 seeds (sd 5.228215e-14, 0.0% of mean; min 2.751735e-09, max 2.751853e-09)
- `period_b00`: mean 2.748717e-09 over 4 seeds (sd 2.811872e-14, 0.0% of mean; min 2.748680e-09, max 2.748747e-09)
- `period_b01`: mean 2.747210e-09 over 4 seeds (sd 7.064927e-14, 0.0% of mean; min 2.747150e-09, max 2.747313e-09)
- `period_b02`: mean 2.747192e-09 over 4 seeds (sd 7.597742e-14, 0.0% of mean; min 2.747131e-09, max 2.747300e-09)
- `period_b03`: mean 2.902746e-09 over 4 seeds (sd 5.821849e-14, 0.0% of mean; min 2.902667e-09, max 2.902802e-09)
- `period_b04`: mean 3.450722e-09 over 4 seeds (sd 9.233303e-14, 0.0% of mean; min 3.450606e-09, max 3.450815e-09)
- `period_b05`: mean 3.450620e-09 over 4 seeds (sd 8.854166e-14, 0.0% of mean; min 3.450498e-09, max 3.450706e-09)
- `period_b06`: mean 3.316364e-09 over 4 seeds (sd 6.022478e-14, 0.0% of mean; min 3.316317e-09, max 3.316450e-09)
- `period_b07`: mean 2.747214e-09 over 4 seeds (sd 3.557968e-14, 0.0% of mean; min 2.747167e-09, max 2.747250e-09)
- `period_b08`: mean 2.747161e-09 over 4 seeds (sd 1.158391e-13, 0.0% of mean; min 2.747000e-09, max 2.747271e-09)
- `period_b09`: mean 2.747182e-09 over 4 seeds (sd 3.124999e-14, 0.0% of mean; min 2.747146e-09, max 2.747208e-09)
- `period_b10`: mean 3.034115e-09 over 4 seeds (sd 9.697390e-14, 0.0% of mean; min 3.034021e-09, max 3.034250e-09)
- `period_b11`: mean 3.450646e-09 over 4 seeds (sd 1.089194e-13, 0.0% of mean; min 3.450542e-09, max 3.450750e-09)
- `period_b12`: mean 3.450729e-09 over 4 seeds (sd 5.379144e-14, 0.0% of mean; min 3.450667e-09, max 3.450792e-09)
- `period_b13`: mean 3.185089e-09 over 4 seeds (sd 9.528069e-14, 0.0% of mean; min 3.184979e-09, max 3.185187e-09)
- `period_b14`: mean 2.747177e-09 over 4 seeds (sd 4.336805e-14, 0.0% of mean; min 2.747125e-09, max 2.747229e-09)
- `period_b15`: mean 2.747234e-09 over 4 seeds (sd 4.619489e-14, 0.0% of mean; min 2.747167e-09, max 2.747271e-09)
- `sigma_1`: mean 3.466405e-10 over 4 seeds (sd 1.753746e-14, 0.0% of mean; min 3.466238e-10, max 3.466648e-10)
- `sigma_2`: mean 6.928118e-10 over 4 seeds (sd 3.855112e-14, 0.0% of mean; min 6.927737e-10, max 6.928604e-10)
- `sigma_4`: mean 1.383130e-09 over 4 seeds (sd 8.930926e-14, 0.0% of mean; min 1.383046e-09, max 1.383242e-09)
- `sigma_8`: mean 2.754187e-09 over 4 seeds (sd 1.967200e-13, 0.0% of mean; min 2.754000e-09, max 2.754438e-09)
- `sigma_16`: mean 5.453994e-09 over 4 seeds (sd 4.261039e-13, 0.0% of mean; min 5.453619e-09, max 5.454535e-09)
- `sigma_32`: mean 1.065216e-08 over 4 seeds (sd 9.578237e-13, 0.0% of mean; min 1.065131e-08, max 1.065337e-08)
- `sigma_64`: mean 1.990426e-08 over 4 seeds (sd 2.036553e-12, 0.0% of mean; min 1.990219e-08, max 1.990683e-08)
- `sigma_128`: mean 3.340266e-08 over 4 seeds (sd 4.282050e-12, 0.0% of mean; min 3.339798e-08, max 3.340821e-08)
- `sigma_startup16_1`: mean 1.796642e-11 over 4 seeds (sd 5.286903e-14, 0.3% of mean; min 1.789495e-11, max 1.801619e-11)
- `sigma_startup16_2`: mean 1.976437e-11 over 4 seeds (sd 1.849687e-13, 0.9% of mean; min 1.961953e-11, max 2.002023e-11)
- `sigma_startup16_4`: mean 2.662156e-11 over 4 seeds (sd 2.576927e-13, 1.0% of mean; min 2.648994e-11, max 2.700808e-11)
- `sigma_startup16_8`: mean 5.128256e-11 over 4 seeds (sd 4.407955e-13, 0.9% of mean; min 5.068123e-11, max 5.174173e-11)
- `i_ring_a`: mean 1.863497e-05 over 4 seeds (sd 9.768762e-11, 0.0% of mean; min 1.863483e-05, max 1.863505e-05)
- `p_active_w`: mean 6.149541e-05 over 4 seeds (sd 3.223684e-10, 0.0% of mean; min 6.149495e-05, max 6.149566e-05)
- `e_per_cycle_j`: mean 1.872151e-13 over 4 seeds (sd 5.939392e-19, 0.0% of mean; min 1.872143e-13, max 1.872156e-13)
- `c_eff_node_f`: mean 3.438295e-15 over 4 seeds (sd 1.090794e-20, 0.0% of mean; min 3.438279e-15, max 3.438303e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 3000 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Variant of issue #76's phase-cost experiment on the DR-0016 per-ring liveness digitizer. The comparison it exists for is against sim/tb/ro-ring5-starved-jitter-long/ (the CONTROL: the same ring, device for device, with nothing attached) and against the other variants of this family, which differ from each other only in what clk does. The ring, the injected noise density, the window geometry (opened 256 periods after start-up, spanning 512 periods), the print step and the corner are identical across the whole family and to #51's variants in sim/characterization-array-ring-coupling.md, which is what makes the two experiments directly comparable.
- Topology note (PR #82). This variant puts the digitizer's d input DIRECTLY on the ring node -- the arrangement design/sampler_core.spice shipped when issue #76 was filed, and the one #76 indicts. Since #82 the shipped netlist interposes a per-ring output buffer (xb1: rn1 -> ro1) and the digitizer taps the buffer output, which is what sim/tb/ring-liveness-tap-phase-buffered/ measures. This deck is therefore the PRE-#82 topology, kept and measured because #82 adopted the buffer on combiner-path evidence (#75) and never measured the digitizer path -- so without this row there is no before to compare the after against. design/sampler_core.spice is named here only as the source of the sampler_dff (and, in the buffered variant, ro_buf) cell definitions; every device in the ring is instantiated by the deck itself.
- tclk_per = 1.0007 us (~1 MHz nominal). DR-0003's ratified raw-rate row is "> 1 Mbps sustained at the raw tap" and DR-0012 makes clk a fixed EXTERNAL pin with no divider, so ~1 MHz is the shipped operating point rather than a chosen stimulus -- but it is also not a design constant an attacker cannot move. This deck measures one rate; the two static variants (clk-high / clk-low) bound the endpoints the tap swings between at ANY rate, which is the rate-independent part of the result.
- Every clk timing in this deck is deliberately off the 10 ps grid that this testbench's trnoise() sources place breakpoints on (vn_dt = 1e-11): tclk_del = 5.003 ns, tclk_tr = 0.203 ns, and tstop = 2.900003 us rather than round values. With the tap attached, a PULSE-source or tstop breakpoint that lands exactly on a trnoise breakpoint makes ngspice-46's transient collapse -- "Timestep too small; timestep = 1.25e-24" -- at that instant, reproducibly. The offsets are ~0.3 % of an edge time and ~0.0005 % of a clk period and nothing measured here resolves them. Recorded so the next transient-noise deck with a clocked cell in it does not rediscover the failure.
- The 512-period measurement window spans ~1.6 clk periods at this clk rate, so the per-block period series period_b00..period_b15 (16 blocks of 48 periods each, ~150 ns per block) is the part of this record that shows the modulation directly; sigma_* aggregates it into a single number whose exact value depends on where the window happens to fall relative to clk, and which is therefore a demonstration that a clk-locked component EXISTS rather than a stable figure of merit for it.
- sigma_* here is NOT a jitter measurement if what it captures is deterministic. The estimator is the control's, but it measures the spread of period-to-period increments from whatever cause, and a load modulation locked to clk enters it exactly as noise would. The seed spread and the accumulation exponent reported alongside are what tell the two apart, and no entropy claim may be built on this record's sigma either way.
- The ring is 5-stage, where the shipped array's rings (design/ro_array_core.spice, ro_ring11) have 11. That is deliberate: #51's whole ladder is on this 5-stage ring at this corner and window, so this family drops straight into it. The tap loads exactly ONE ring node either way, and one node is a larger fraction of a 5-stage ring's delay than of an 11-stage ring's, so a fractional period or phase effect measured here OVER-states the shipped ring's by roughly 11/5.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used, so this family has a like-for-like row against #51's variants' own startup block. They are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.
- The digitizer is supplied from vsup directly rather than through the ring's sense source, so its own switching current is outside i_ring_a/p_active_w. Its own power is not re-measured here -- sim/tb/ring-liveness-tap-power/ measures it across three PVT points -- and p_active_w/e_per_cycle_j/c_eff_node_f here are the RING's, comparable expression for expression to the control's.
- rst_n is held at vdd for the whole run, so the digitizer is out of reset throughout and contributes no reset edge. DR-0014's gated reset behaviour is measured by sim/tb/sampler-dff-reset-clocked/ and is not what this deck is about.
- Pre-layout, schematic-derived netlist (design/sampler_core.spice), no extracted parasitics. Layout adds coupling paths between a clocked cell and a ring node; it removes none.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
