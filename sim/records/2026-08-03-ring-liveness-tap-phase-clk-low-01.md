---
record: 2026-08-03-ring-liveness-tap-phase-clk-low-01
date: 2026-08-03T05:29:15Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-phase-clk-low/tb_ring_liveness_tap_phase_clk_low.sp
  sha: e75e7ace759ecb5ae66932ee74c56acf07706d56
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 7f1ef079da7441626a734000f85e5ffefc3c0bd0-dirty

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
  tstop: 3.000003u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources, one in series with every stage input
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-03-ring-liveness-tap-phase-clk-low-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:0930e4157fb7acdbfbc515b35f81e3abab10b3e62ef2ac92897e6619431aa5af
    - tt_27c_3.30v-run0.log  sha256:4dea56c56d731c533696d7f0bd18d0ca0905a7dd8d68ee3a88060098cb1dded4
    - tt_27c_3.30v-run1.spice  sha256:87617a882e49cb78883a39a6d73f8b87f2f8ba26a52e51dfe12fa6d5ba2ad78d
    - tt_27c_3.30v-run1.log  sha256:528a8b96eae8b74ca21fc4c1db2fb0c82e7985f86065dec78f91511e77ebdddc
    - tt_27c_3.30v-run2.spice  sha256:32eaac647bc3a5fbbfcfb48c801a5788c0ecb45a6eaf4aa3dbce4bb00e4efe30
    - tt_27c_3.30v-run2.log  sha256:e8d300c2377208790d7497e6e58522b03f3b5b567d848e4390a263ffce57aed4
    - tt_27c_3.30v-run3.spice  sha256:0c4a6e18376fa55536a2181ada1715416745ac4d75c24888f4013cb181e551d6
    - tt_27c_3.30v-run3.log  sha256:0bab38374787c9c5dce3d51b6235d5fde829a7a482a82d829118511a524f6302
wall_time: 20.0m
---

## Result

- `period`: mean 3.450691e-09 over 4 seeds (sd 3.138657e-14, 0.0% of mean; min 3.450660e-09, max 3.450721e-09)
- `f_osc`: mean 2.897970e+08 over 4 seeds (sd 2635.92, 0.0% of mean; min 2.897945e+08, max 2.897997e+08)
- `period_startup16`: mean 3.450697e-09 over 4 seeds (sd 1.328285e-13, 0.0% of mean; min 3.450508e-09, max 3.450807e-09)
- `period_b00`: mean 3.450741e-09 over 4 seeds (sd 8.381338e-14, 0.0% of mean; min 3.450660e-09, max 3.450848e-09)
- `period_b01`: mean 3.450652e-09 over 4 seeds (sd 8.849263e-14, 0.0% of mean; min 3.450540e-09, max 3.450752e-09)
- `period_b02`: mean 3.450710e-09 over 4 seeds (sd 7.097614e-14, 0.0% of mean; min 3.450629e-09, max 3.450802e-09)
- `period_b03`: mean 3.450688e-09 over 4 seeds (sd 2.097177e-14, 0.0% of mean; min 3.450658e-09, max 3.450708e-09)
- `period_b04`: mean 3.450671e-09 over 4 seeds (sd 1.419256e-13, 0.0% of mean; min 3.450460e-09, max 3.450769e-09)
- `period_b05`: mean 3.450696e-09 over 4 seeds (sd 3.621946e-14, 0.0% of mean; min 3.450648e-09, max 3.450735e-09)
- `period_b06`: mean 3.450647e-09 over 4 seeds (sd 1.500615e-13, 0.0% of mean; min 3.450525e-09, max 3.450840e-09)
- `period_b07`: mean 3.450693e-09 over 4 seeds (sd 9.528072e-14, 0.0% of mean; min 3.450583e-09, max 3.450812e-09)
- `period_b08`: mean 3.450724e-09 over 4 seeds (sd 9.061106e-14, 0.0% of mean; min 3.450646e-09, max 3.450854e-09)
- `period_b09`: mean 3.450703e-09 over 4 seeds (sd 9.528073e-14, 0.0% of mean; min 3.450583e-09, max 3.450812e-09)
- `period_b10`: mean 3.450708e-09 over 4 seeds (sd 1.306589e-13, 0.0% of mean; min 3.450563e-09, max 3.450875e-09)
- `period_b11`: mean 3.450693e-09 over 4 seeds (sd 7.487453e-14, 0.0% of mean; min 3.450625e-09, max 3.450792e-09)
- `period_b12`: mean 3.450693e-09 over 4 seeds (sd 8.900007e-14, 0.0% of mean; min 3.450583e-09, max 3.450792e-09)
- `period_b13`: mean 3.450667e-09 over 4 seeds (sd 8.157875e-14, 0.0% of mean; min 3.450583e-09, max 3.450771e-09)
- `period_b14`: mean 3.450766e-09 over 4 seeds (sd 5.208333e-14, 0.0% of mean; min 3.450708e-09, max 3.450833e-09)
- `period_b15`: mean 3.450641e-09 over 4 seeds (sd 6.220997e-14, 0.0% of mean; min 3.450563e-09, max 3.450708e-09)
- `sigma_1`: mean 9.031253e-13 over 4 seeds (sd 1.212540e-14, 1.3% of mean; min 8.859980e-13, max 9.121362e-13)
- `sigma_2`: mean 1.007985e-12 over 4 seeds (sd 6.430796e-14, 6.4% of mean; min 9.255662e-13, max 1.082636e-12)
- `sigma_4`: mean 1.261190e-12 over 4 seeds (sd 9.706665e-14, 7.7% of mean; min 1.158841e-12, max 1.384153e-12)
- `sigma_8`: mean 1.624111e-12 over 4 seeds (sd 5.703736e-14, 3.5% of mean; min 1.556620e-12, max 1.677465e-12)
- `sigma_16`: mean 2.241840e-12 over 4 seeds (sd 1.762656e-13, 7.9% of mean; min 2.030626e-12, max 2.416150e-12)
- `sigma_32`: mean 3.097594e-12 over 4 seeds (sd 4.234442e-13, 13.7% of mean; min 2.560533e-12, max 3.585167e-12)
- `sigma_64`: mean 3.688272e-12 over 4 seeds (sd 1.030208e-12, 27.9% of mean; min 2.661433e-12, max 5.055410e-12)
- `sigma_128`: mean 4.435654e-12 over 4 seeds (sd 9.710260e-13, 21.9% of mean; min 3.386482e-12, max 5.573192e-12)
- `sigma_startup16_1`: mean 8.068629e-13 over 4 seeds (sd 2.301533e-13, 28.5% of mean; min 6.141501e-13, max 1.124139e-12)
- `sigma_startup16_2`: mean 9.421556e-13 over 4 seeds (sd 2.969235e-13, 31.5% of mean; min 6.847836e-13, max 1.274586e-12)
- `sigma_startup16_4`: mean 1.370807e-12 over 4 seeds (sd 4.997993e-13, 36.5% of mean; min 8.441317e-13, max 2.012085e-12)
- `sigma_startup16_8`: mean 1.786394e-12 over 4 seeds (sd 7.978514e-13, 44.7% of mean; min 9.593299e-13, max 2.869686e-12)
- `i_ring_a`: mean 1.829190e-05 over 4 seeds (sd 1.048417e-10, 0.0% of mean; min 1.829181e-05, max 1.829202e-05)
- `p_active_w`: mean 6.036328e-05 over 4 seeds (sd 3.459774e-10, 0.0% of mean; min 6.036296e-05, max 6.036368e-05)
- `e_per_cycle_j`: mean 2.082950e-13 over 4 seeds (sd 7.318099e-19, 0.0% of mean; min 2.082943e-13, max 2.082957e-13)
- `c_eff_node_f`: mean 3.825437e-15 over 4 seeds (sd 1.344005e-20, 0.0% of mean; min 3.825424e-15, max 3.825450e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-phase-clk-low --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clk-low --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clk-low --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clk-low --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 3000 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Variant of issue #76's phase-cost experiment on the DR-0016 per-ring liveness digitizer. The comparison it exists for is against sim/tb/ro-ring5-starved-jitter-long/ (the CONTROL: the same ring, device for device, with nothing attached) and against the other variants of this family, which differ from each other only in what clk does. The ring, the injected noise density, the window geometry (opened 256 periods after start-up, spanning 512 periods), the print step and the corner are identical across the whole family and to #51's variants in sim/characterization-array-ring-coupling.md, which is what makes the two experiments directly comparable.
- Topology note (PR #82). This variant puts the digitizer's d input DIRECTLY on the ring node -- the arrangement design/sampler_core.spice shipped when issue #76 was filed, and the one #76 indicts. Since #82 the shipped netlist interposes a per-ring output buffer (xb1: rn1 -> ro1) and the digitizer taps the buffer output, which is what sim/tb/ring-liveness-tap-phase-buffered/ measures. This deck is therefore the PRE-#82 topology, kept and measured because #82 adopted the buffer on combiner-path evidence (#75) and never measured the digitizer path -- so without this row there is no before to compare the after against. design/sampler_core.spice is named here only as the source of the sampler_dff (and, in the buffered variant, ro_buf) cell definitions; every device in the ring is instantiated by the deck itself.
- clk and rst_n are DC sources: this deck contains no edge anywhere after start-up, which is what makes it a static reference. It measures ONE of the two states the clocked tap alternates between and is not on its own a statement about the shipped, clocked arrangement -- sim/tb/ring-liveness-tap-phase-clocked/ is.
- tstop is 3.000003 us rather than the clk-high deck's 2.400003 us because this deck's ring is slower and 770 rises take longer. Nothing else about the window changed: it still opens 256 periods after start-up and spans 512 periods.
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
