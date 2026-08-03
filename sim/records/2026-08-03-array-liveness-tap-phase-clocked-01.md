---
record: 2026-08-03-array-liveness-tap-phase-clocked-01
date: 2026-08-03T16:07:29Z
status: valid

testbench:
  path: sim/tb/array-liveness-tap-phase-clocked/tb_array_liveness_tap_phase_clocked.sp
  sha: 53ff0444e1e1c44d3ebf56cb187e8e6c0e5d7c5b
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 56e6ef50ef1cb752a29ed66e91664774e8af108b

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
  path: sim/records/raw/2026-08-03-array-liveness-tap-phase-clocked-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:c9a60b89459c7e850e7dcede8eeec364f778e925a7bc5e07d2d93beab19067a4
    - tt_27c_3.30v-run0.log  sha256:5b0c353abc2d0425bd45635f5601560dccd511b69fa3306fc323b6d50522cf41
    - tt_27c_3.30v-run1.spice  sha256:a09b19f1d328a4ae25a8f5865cc2c9f5fc3e4fd44d3bdc356c208fa82ee9a745
    - tt_27c_3.30v-run1.log  sha256:4fa89c640806f089d5cde1412717fa49e954624eba1dda053e097db0083f3e0c
    - tt_27c_3.30v-run2.spice  sha256:95846c00ab348d686e347ea466d5642a83351e41678564b1357118905af1e516
    - tt_27c_3.30v-run2.log  sha256:34160cb896e70d6a1549e24787531c5b6d1183af627d4c64201c057da539bda0
    - tt_27c_3.30v-run3.spice  sha256:5ed5a9f9b1b48d2e503cf5c9d9794193ac8c008f851c0770cdc6e329771a40c3
    - tt_27c_3.30v-run3.log  sha256:ea160ade787adcff9cfd4a7f47fa13ae014646ab8119937a8a5c8ec9ab24b5c6
wall_time: 799.8m
---

## Result

- `period`: mean 6.670222e-09 over 4 seeds (sd 8.713476e-15, 0.0% of mean; min 6.670213e-09, max 6.670234e-09)
- `f_osc`: mean 1.499200e+08 over 4 seeds (sd 195.844, 0.0% of mean; min 1.499198e+08, max 1.499202e+08)
- `period_startup16`: mean 6.673894e-09 over 4 seeds (sd 7.315326e-14, 0.0% of mean; min 6.673828e-09, max 6.673997e-09)
- `period_r2`: mean 6.234370e-09 over 4 seeds (sd 2.682735e-14, 0.0% of mean; min 6.234350e-09, max 6.234409e-09)
- `period_b00`: mean 6.673937e-09 over 4 seeds (sd 4.501076e-14, 0.0% of mean; min 6.673905e-09, max 6.674002e-09)
- `period_b01`: mean 6.673944e-09 over 4 seeds (sd 8.068716e-14, 0.0% of mean; min 6.673833e-09, max 6.674025e-09)
- `period_b02`: mean 6.673785e-09 over 4 seeds (sd 6.314480e-14, 0.0% of mean; min 6.673704e-09, max 6.673858e-09)
- `period_b03`: mean 6.665829e-09 over 4 seeds (sd 1.005195e-13, 0.0% of mean; min 6.665737e-09, max 6.665967e-09)
- `period_b04`: mean 6.665084e-09 over 4 seeds (sd 9.648780e-14, 0.0% of mean; min 6.664967e-09, max 6.665192e-09)
- `period_b05`: mean 6.664935e-09 over 4 seeds (sd 9.804217e-14, 0.0% of mean; min 6.664804e-09, max 6.665042e-09)
- `period_b06`: mean 6.671920e-09 over 4 seeds (sd 7.510605e-14, 0.0% of mean; min 6.671858e-09, max 6.672017e-09)
- `period_b07`: mean 6.673969e-09 over 4 seeds (sd 8.589805e-14, 0.0% of mean; min 6.673875e-09, max 6.674042e-09)
- `period_b08`: mean 6.673677e-09 over 4 seeds (sd 8.589805e-14, 0.0% of mean; min 6.673583e-09, max 6.673750e-09)
- `period_b09`: mean 6.668146e-09 over 4 seeds (sd 4.166670e-14, 0.0% of mean; min 6.668083e-09, max 6.668167e-09)
- `period_b10`: mean 6.665146e-09 over 4 seeds (sd 1.048588e-13, 0.0% of mean; min 6.665042e-09, max 6.665292e-09)
- `period_b11`: mean 6.664885e-09 over 4 seeds (sd 7.115936e-14, 0.0% of mean; min 6.664792e-09, max 6.664958e-09)
- `period_b12`: mean 6.669906e-09 over 4 seeds (sd 1.041667e-13, 0.0% of mean; min 6.669792e-09, max 6.670042e-09)
- `period_b13`: mean 6.673927e-09 over 4 seeds (sd 3.989278e-14, 0.0% of mean; min 6.673875e-09, max 6.673958e-09)
- `period_b14`: mean 6.673802e-09 over 4 seeds (sd 1.196784e-13, 0.0% of mean; min 6.673708e-09, max 6.673958e-09)
- `period_b15`: mean 6.670250e-09 over 4 seeds (sd 1.443376e-13, 0.0% of mean; min 6.670042e-09, max 6.670375e-09)
- `sigma_1`: mean 4.449025e-12 over 4 seeds (sd 6.108038e-14, 1.4% of mean; min 4.399024e-12, max 4.537650e-12)
- `sigma_2`: mean 8.725651e-12 over 4 seeds (sd 1.023160e-13, 1.2% of mean; min 8.631087e-12, max 8.870888e-12)
- `sigma_4`: mean 1.719022e-11 over 4 seeds (sd 1.995200e-13, 1.2% of mean; min 1.699675e-11, max 1.746817e-11)
- `sigma_8`: mean 3.361695e-11 over 4 seeds (sd 3.938023e-13, 1.2% of mean; min 3.321388e-11, max 3.415449e-11)
- `sigma_16`: mean 6.461736e-11 over 4 seeds (sd 8.240029e-13, 1.3% of mean; min 6.381749e-11, max 6.574680e-11)
- `sigma_32`: mean 1.223434e-10 over 4 seeds (sd 1.752676e-12, 1.4% of mean; min 1.208651e-10, max 1.247868e-10)
- `sigma_64`: mean 2.189734e-10 over 4 seeds (sd 3.247905e-12, 1.5% of mean; min 2.161526e-10, max 2.234799e-10)
- `sigma_r2_1`: mean 4.023300e-12 over 4 seeds (sd 1.897502e-14, 0.5% of mean; min 3.998073e-12, max 4.043027e-12)
- `sigma_r2_2`: mean 7.953121e-12 over 4 seeds (sd 4.493752e-14, 0.6% of mean; min 7.894597e-12, max 7.989109e-12)
- `sigma_r2_4`: mean 1.577628e-11 over 4 seeds (sd 9.913691e-14, 0.6% of mean; min 1.564616e-11, max 1.586639e-11)
- `sigma_r2_8`: mean 3.120368e-11 over 4 seeds (sd 2.058137e-13, 0.7% of mean; min 3.093147e-11, max 3.139456e-11)
- `sigma_r2_16`: mean 6.097295e-11 over 4 seeds (sd 4.179499e-13, 0.7% of mean; min 6.043457e-11, max 6.136920e-11)
- `sigma_r2_32`: mean 1.142468e-10 over 4 seeds (sd 9.694449e-13, 0.8% of mean; min 1.130211e-10, max 1.151792e-10)
- `sigma_r2_64`: mean 1.969254e-10 over 4 seeds (sd 1.969550e-12, 1.0% of mean; min 1.945291e-10, max 1.991771e-10)
- `sigma_startup16_1`: mean 1.095659e-12 over 4 seeds (sd 1.435975e-13, 13.1% of mean; min 9.064140e-13, max 1.249456e-12)
- `sigma_startup16_2`: mean 1.421374e-12 over 4 seeds (sd 2.291791e-13, 16.1% of mean; min 1.200892e-12, max 1.741150e-12)
- `sigma_startup16_4`: mean 2.084094e-12 over 4 seeds (sd 2.372417e-13, 11.4% of mean; min 1.928937e-12, max 2.435643e-12)
- `sigma_startup16_8`: mean 3.120730e-12 over 4 seeds (sd 2.481473e-13, 8.0% of mean; min 2.783731e-12, max 3.333400e-12)
- `i_ring_a`: mean 1.897669e-05 over 4 seeds (sd 2.947931e-11, 0.0% of mean; min 1.897667e-05, max 1.897672e-05)
- `p_active_w`: mean 6.262309e-05 over 4 seeds (sd 9.728100e-11, 0.0% of mean; min 6.262299e-05, max 6.262318e-05)
- `e_per_cycle_j`: mean 4.177099e-13 over 4 seeds (sd 3.222670e-19, 0.0% of mean; min 4.177095e-13, max 4.177103e-13)
- `c_eff_node_f`: mean 3.487018e-15 over 4 seeds (sd 2.690293e-21, 0.0% of mean; min 3.487015e-15, max 3.487021e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py array-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 86400 --no-write
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
- One clk rate, tclk_per = 1.0007 us (~1 MHz). DR-0003's ratified raw-rate row is "> 1 Mbps sustained at the raw tap" and DR-0012 makes clk a fixed EXTERNAL pin with no divider, so ~1 MHz is the shipped operating point rather than a chosen stimulus -- but it is also not a design constant an attacker cannot move. How the disturbance folds into any particular sigma window is rate-dependent; the per-block mean periods reported alongside are the rate-independent view of it.
- Every clk timing in this family is deliberately off the 10 ps grid that the trnoise() sources place breakpoints on (vn_dt = 1e-11): tclk_del = 5.003 ns, tclk_tr = 0.203 ns, tstop = 3.000003 us rather than round values. With a clocked cell attached, a PULSE-source or tstop breakpoint landing exactly on a trnoise breakpoint collapses ngspice-46's transient ("Timestep too small; timestep = 1.25e-24") at that instant, reproducibly -- the solver limit sim/characterization-liveness-tap-phase-cost.md records. The offsets are ~0.3 % of an edge time and ~0.0005 % of a clk period and nothing measured here resolves them.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
