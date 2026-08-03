---
record: 2026-08-03-ring-liveness-tap-phase-clocked-01
date: 2026-08-03T04:37:33Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-phase-clocked/tb_ring_liveness_tap_phase_clocked.sp
  sha: ba88476470cc841089b88832c845482f52e044bb
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
  path: sim/records/raw/2026-08-03-ring-liveness-tap-phase-clocked-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:bb301d0dae56c90a2f51976869c9bc7cbf0211830ae9dd06d2882ef00f8a61b6
    - tt_27c_3.30v-run0.log  sha256:b1fb8609a15f7e755e57f0c135cf398d28c36070f241637b487d7d5e09f2c58a
    - tt_27c_3.30v-run1.spice  sha256:9248d84daf3f3afbd586dea6ebdb0ca888f7cebecd1ddaf86ee7f9ae6bdcb51a
    - tt_27c_3.30v-run1.log  sha256:8b3b8726a1c5117b524e45db13f494e483d205b973d9e99670f18cd8de6a9005
    - tt_27c_3.30v-run2.spice  sha256:f14228f876edb07339bce4e95b419f7ed7fa8b1bb86783d1bf38bf964370076c
    - tt_27c_3.30v-run2.log  sha256:46d3fd760ff636cb2c96621ed3228a4003a01ee66ff5a87261c3072226155de9
    - tt_27c_3.30v-run3.spice  sha256:8816640f5e00cd85a71a7e68c0b376cf4fe0af652897f1e15bbc0b1d761d2067
    - tt_27c_3.30v-run3.log  sha256:81795fe221a0302e550d2e3f9071d13b824e58d2615b71db2c5080c15e5b75df
wall_time: 125.1m
---

## Result

- `period`: mean 3.081766e-09 over 4 seeds (sd 1.773467e-14, 0.0% of mean; min 3.081747e-09, max 3.081786e-09)
- `f_osc`: mean 3.244892e+08 over 4 seeds (sd 1867.34, 0.0% of mean; min 3.244871e+08, max 3.244912e+08)
- `period_startup16`: mean 3.450752e-09 over 4 seeds (sd 1.101400e-13, 0.0% of mean; min 3.450671e-09, max 3.450914e-09)
- `period_b00`: mean 3.146491e-09 over 4 seeds (sd 4.559507e-14, 0.0% of mean; min 3.146460e-09, max 3.146558e-09)
- `period_b01`: mean 2.747235e-09 over 4 seeds (sd 6.245369e-14, 0.0% of mean; min 2.747144e-09, max 2.747277e-09)
- `period_b02`: mean 2.747213e-09 over 4 seeds (sd 4.530553e-14, 0.0% of mean; min 2.747152e-09, max 2.747254e-09)
- `period_b03`: mean 2.747191e-09 over 4 seeds (sd 4.678616e-14, 0.0% of mean; min 2.747158e-09, max 2.747258e-09)
- `period_b04`: mean 3.197957e-09 over 4 seeds (sd 8.560277e-14, 0.0% of mean; min 3.197881e-09, max 3.198065e-09)
- `period_b05`: mean 3.450686e-09 over 4 seeds (sd 5.841697e-14, 0.0% of mean; min 3.450604e-09, max 3.450742e-09)
- `period_b06`: mean 3.450661e-09 over 4 seeds (sd 1.071702e-13, 0.0% of mean; min 3.450567e-09, max 3.450810e-09)
- `period_b07`: mean 3.011411e-09 over 4 seeds (sd 2.265475e-13, 0.0% of mean; min 3.011104e-09, max 3.011646e-09)
- `period_b08`: mean 2.747229e-09 over 4 seeds (sd 7.216876e-14, 0.0% of mean; min 2.747167e-09, max 2.747333e-09)
- `period_b09`: mean 2.747125e-09 over 4 seeds (sd 5.641692e-14, 0.0% of mean; min 2.747083e-09, max 2.747208e-09)
- `period_b10`: mean 2.747198e-09 over 4 seeds (sd 3.608438e-14, 0.0% of mean; min 2.747167e-09, max 2.747250e-09)
- `period_b11`: mean 3.341516e-09 over 4 seeds (sd 5.479075e-14, 0.0% of mean; min 3.341458e-09, max 3.341563e-09)
- `period_b12`: mean 3.450667e-09 over 4 seeds (sd 8.838833e-14, 0.0% of mean; min 3.450583e-09, max 3.450771e-09)
- `period_b13`: mean 3.450719e-09 over 4 seeds (sd 3.989278e-14, 0.0% of mean; min 3.450667e-09, max 3.450750e-09)
- `period_b14`: mean 2.877995e-09 over 4 seeds (sd 4.294904e-14, 0.0% of mean; min 2.877958e-09, max 2.878042e-09)
- `period_b15`: mean 2.747182e-09 over 4 seeds (sd 2.621471e-14, 0.0% of mean; min 2.747146e-09, max 2.747208e-09)
- `sigma_1`: mean 3.528826e-10 over 4 seeds (sd 2.653926e-14, 0.0% of mean; min 3.528603e-10, max 3.529146e-10)
- `sigma_2`: mean 7.031868e-10 over 4 seeds (sd 3.275903e-14, 0.0% of mean; min 7.031534e-10, max 7.032283e-10)
- `sigma_4`: mean 1.401610e-09 over 4 seeds (sd 4.368323e-14, 0.0% of mean; min 1.401554e-09, max 1.401659e-09)
- `sigma_8`: mean 2.789394e-09 over 4 seeds (sd 9.127004e-14, 0.0% of mean; min 2.789277e-09, max 2.789468e-09)
- `sigma_16`: mean 5.525460e-09 over 4 seeds (sd 1.678050e-13, 0.0% of mean; min 5.525244e-09, max 5.525631e-09)
- `sigma_32`: mean 1.080951e-08 over 4 seeds (sd 2.997511e-13, 0.0% of mean; min 1.080913e-08, max 1.080982e-08)
- `sigma_64`: mean 2.030804e-08 over 4 seeds (sd 5.474845e-13, 0.0% of mean; min 2.030764e-08, max 2.030884e-08)
- `sigma_128`: mean 3.336644e-08 over 4 seeds (sd 9.975162e-13, 0.0% of mean; min 3.336581e-08, max 3.336793e-08)
- `sigma_startup16_1`: mean 8.005612e-13 over 4 seeds (sd 1.621750e-13, 20.3% of mean; min 6.316336e-13, max 1.021450e-12)
- `sigma_startup16_2`: mean 9.965442e-13 over 4 seeds (sd 1.171247e-13, 11.8% of mean; min 8.469837e-13, max 1.122251e-12)
- `sigma_startup16_4`: mean 1.136757e-12 over 4 seeds (sd 4.623201e-13, 40.7% of mean; min 5.614046e-13, max 1.680410e-12)
- `sigma_startup16_8`: mean 1.310158e-12 over 4 seeds (sd 4.330719e-13, 33.1% of mean; min 7.873940e-13, max 1.764806e-12)
- `i_ring_a`: mean 1.859840e-05 over 4 seeds (sd 1.097408e-10, 0.0% of mean; min 1.859825e-05, max 1.859849e-05)
- `i_tap_a`: mean 8.049998e-06 over 4 seeds (sd 3.929516e-10, 0.0% of mean; min 8.049429e-06, max 8.050332e-06)
- `p_active_w`: mean 6.137471e-05 over 4 seeds (sd 3.621445e-10, 0.0% of mean; min 6.137421e-05, max 6.137502e-05)
- `p_tap_w`: mean 2.656499e-05 over 4 seeds (sd 1.296740e-09, 0.0% of mean; min 2.656312e-05, max 2.656610e-05)
- `e_per_cycle_j`: mean 1.891425e-13 over 4 seeds (sd 4.542323e-19, 0.0% of mean; min 1.891420e-13, max 1.891429e-13)
- `c_eff_node_f`: mean 3.473691e-15 over 4 seeds (sd 8.342168e-21, 0.0% of mean; min 3.473683e-15, max 3.473699e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `clk_period_s`: mean 1.000000e-06 over 4 seeds (sd 0, 0.0% of mean; min 1.000000e-06, max 1.000000e-06)
- `clk_periods_in_window`: mean 1.57786 over 4 seeds (sd 9.080152e-06, 0.0% of mean; min 1.57785, max 1.57787)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 172800 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 172800 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- The measurement deck of issue #76's six-variant experiment (see the deck header for the whole set). The attributing comparisons are this deck against sim/tb/ring-liveness-tap-phase-shut/ and against sim/tb/ring-liveness-tap-phase-open/: same ring, same attached cell, same window, same seeds, and the only difference is whether clk switches.
- tclk = 1 us (1 MHz). DR-0012 makes the sample clock a fixed EXTERNAL input and DR-0003's ratified raw-rate row is '> 1 Mbps sustained at the raw tap', so this is the SLOWEST clock the shipped block is specified to run at -- the rate at which a clk-correlated disturbance arrives least often, and therefore the most favourable rate to the digitizer that the specification permits. It is deliberately not the 100 MHz measurement clock sim/tb/ring-liveness-tap-power/ used, whose own caveats say it bears no resemblance to DR-0012's real rate. Nothing here is measured at any other clock rate, and no claim is made about one.
- The 512-period window spans about 1.6 clock cycles at this rate (clk_periods_in_window reports the measured figure per run), so roughly half the sampled periods fall in each clock phase but not exactly half. sigma_1 of a two-level modulation with duty p is delta*sqrt(p*(1-p)), which is within 3 % of delta/2 for any p between 0.4 and 0.6 -- so the aggregate is insensitive to the exact split, but it is not independent of it, and the split is not controlled here.
- period_b00..period_b15 bin the run into sixteen 48-period bins, each roughly a sixth of a clock half-period at this rate. They exist so the clk-locked modulation is directly readable off the record as a square wave across the bin series, rather than only as an aggregate sigma. They are a shape, not a precise per-phase period.
- tstop is 3.0 us rather than issue #51's 2.9 us because the digitizer-loaded ring is slower in the -open and -clocked variants of this family and 770 rises there take ~2.7 us; every deck in the family uses the same tstop so the runs are like-for-like. Nothing about the window changed: it still opens 256 periods after start-up and spans 512 periods.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used. tclk0 = 100 ns places the clock's FIRST edge after that window closes (16 periods of the transparent-load ring is ~62 ns), so in this deck the start-up window measures the ring at the clk-low/transparent operating point with no clock edge inside it -- it is comparable with sim/tb/ring-liveness-tap-phase-open/'s start-up window, not with this deck's own sigma_* series.
- rst_n is held HIGH from t=0 with no edge. DR-0014's reset is an initialisation input; the digitizer's own output (ring_bit1) is not measured by this deck, which measures what the digitizer does to the RING.
- i_tap_a is the digitizer's own average supply current over the 512-period window, on its own metered branch (vddtap) -- an average over both clock phases, not a per-clock-cycle energy.
- abstol=1e-10 (tb.json "options"), 100x looser than ngspice's 1e-12 default, on EVERY deck in this family -- including the four whose clock never moves and which converge without it. Without the relaxation the two clocked decks abort with "Timestep too small ... trouble with node vtap#branch" at a clock edge, exactly the abort sim/tb/sampler-array-digitize/ bisected and documented for the same cell driven from the same kind of external edge; softer edges (20 ns) and moving the first edge past ring start-up were both tried here and neither fixes it, matching that deck's own finding that edge rate is not the cause. The relaxation is applied to the static decks too, even though they do not need it, because this family's whole claim is a ratio between decks and a ratio between two different solver tolerances would not be one. 100 pA is ~3e-6 of this ring's ~35 uA supply current. The check that it is benign is internal to the family: the static decks' sigma_1 and seed spread can be read against sim/records/2026-08-01-ro-ring5-starved-jitter-long-02.md, which was taken at ngspice's default tolerances -- a relaxation that injected numerical jitter would show up there as an inflated sigma_1 with a collapsed seed spread.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
