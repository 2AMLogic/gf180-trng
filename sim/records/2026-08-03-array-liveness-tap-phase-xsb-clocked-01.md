---
record: 2026-08-03-array-liveness-tap-phase-xsb-clocked-01
date: 2026-08-03T21:35:13Z
status: valid

testbench:
  path: sim/tb/array-liveness-tap-phase-xsb-clocked/tb_array_liveness_tap_phase_xsb_clocked.sp
  sha: 806d8fa5394697208a4d67a2ba8cc93c0b34408e
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 2ebde54a4a7be590af254d8958d57ba0938246af-dirty

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
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 22 sources, one in series with every stage input of both 11-stage rings
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-03-array-liveness-tap-phase-xsb-clocked-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:89b30f37013a1f9ce3d4d8ad60ce3b64f85fc3fc9e5c052af65f9bf8b58222e5
    - tt_27c_3.30v-run0.log  sha256:573cb0019518f3fcad4852b57d3ffc9616294c542fb5188c23a5a22bcc2210f4
    - tt_27c_3.30v-run1.spice  sha256:92b093e94bbd1aefbf7945d9aa3b1b6e5cc0dbbd2e7892bf17834884cbefddb4
    - tt_27c_3.30v-run1.log  sha256:6036000f33d95b26abe643a178aed23382bdedf7b588985465bc88f4fbcfa32a
    - tt_27c_3.30v-run2.spice  sha256:df801e2957b870626d0d497100c0f0f7311928c175fc0330af4bd5651a7afc25
    - tt_27c_3.30v-run2.log  sha256:8a1409db58e66321b3e4ea21dca3b1482e458adfdfb969a08e95aa036d9ef920
    - tt_27c_3.30v-run3.spice  sha256:c1403b22d32f6c0e3f559f13b6fca447dc31c25de9ab95ea037ebf6abeaff460
    - tt_27c_3.30v-run3.log  sha256:0dfdc92200881bca6ce2ea583fb22398f9a574d40f13293945c47ffebe727b65
wall_time: 75.5m
---

## Result

- `period`: mean 6.676783e-09 over 4 seeds (sd 1.037120e-14, 0.0% of mean; min 6.676770e-09, max 6.676795e-09)
- `f_osc`: mean 1.497727e+08 over 4 seeds (sd 232.642, 0.0% of mean; min 1.497725e+08, max 1.497730e+08)
- `period_startup16`: mean 6.676852e-09 over 4 seeds (sd 8.818408e-14, 0.0% of mean; min 6.676726e-09, max 6.676931e-09)
- `period_r2`: mean 6.240515e-09 over 4 seeds (sd 2.868256e-14, 0.0% of mean; min 6.240477e-09, max 6.240547e-09)
- `period_b00`: mean 6.676846e-09 over 4 seeds (sd 1.491814e-13, 0.0% of mean; min 6.676630e-09, max 6.676970e-09)
- `period_b01`: mean 6.676766e-09 over 4 seeds (sd 8.139236e-14, 0.0% of mean; min 6.676683e-09, max 6.676842e-09)
- `period_b02`: mean 6.676577e-09 over 4 seeds (sd 1.205936e-13, 0.0% of mean; min 6.676462e-09, max 6.676683e-09)
- `period_b03`: mean 6.676930e-09 over 4 seeds (sd 1.106261e-13, 0.0% of mean; min 6.676829e-09, max 6.677083e-09)
- `period_b04`: mean 6.676967e-09 over 4 seeds (sd 9.248375e-14, 0.0% of mean; min 6.676904e-09, max 6.677104e-09)
- `period_b05`: mean 6.676589e-09 over 4 seeds (sd 1.321727e-13, 0.0% of mean; min 6.676450e-09, max 6.676767e-09)
- `period_b06`: mean 6.676837e-09 over 4 seeds (sd 4.894726e-14, 0.0% of mean; min 6.676783e-09, max 6.676900e-09)
- `period_b07`: mean 6.676917e-09 over 4 seeds (sd 1.128339e-13, 0.0% of mean; min 6.676750e-09, max 6.677000e-09)
- `period_b08`: mean 6.676646e-09 over 4 seeds (sd 1.295469e-13, 0.0% of mean; min 6.676500e-09, max 6.676792e-09)
- `period_b09`: mean 6.676771e-09 over 4 seeds (sd 5.379144e-14, 0.0% of mean; min 6.676708e-09, max 6.676833e-09)
- `period_b10`: mean 6.676875e-09 over 4 seeds (sd 5.892557e-14, 0.0% of mean; min 6.676792e-09, max 6.676917e-09)
- `period_b11`: mean 6.676646e-09 over 4 seeds (sd 7.978561e-14, 0.0% of mean; min 6.676583e-09, max 6.676750e-09)
- `period_b12`: mean 6.676833e-09 over 4 seeds (sd 9.001027e-14, 0.0% of mean; min 6.676750e-09, max 6.676958e-09)
- `period_b13`: mean 6.676708e-09 over 4 seeds (sd 5.892557e-14, 0.0% of mean; min 6.676667e-09, max 6.676792e-09)
- `period_b14`: mean 6.676802e-09 over 4 seeds (sd 9.845448e-14, 0.0% of mean; min 6.676667e-09, max 6.676875e-09)
- `period_b15`: mean 6.676708e-09 over 4 seeds (sd 9.001027e-14, 0.0% of mean; min 6.676625e-09, max 6.676833e-09)
- `sigma_1`: mean 1.396568e-12 over 4 seeds (sd 1.711265e-14, 1.2% of mean; min 1.376273e-12, max 1.418135e-12)
- `sigma_2`: mean 1.799974e-12 over 4 seeds (sd 4.216169e-14, 2.3% of mean; min 1.741314e-12, max 1.836729e-12)
- `sigma_4`: mean 2.534141e-12 over 4 seeds (sd 1.233737e-13, 4.9% of mean; min 2.377605e-12, max 2.679133e-12)
- `sigma_8`: mean 3.181049e-12 over 4 seeds (sd 1.887062e-13, 5.9% of mean; min 2.927118e-12, max 3.383222e-12)
- `sigma_16`: mean 2.475899e-12 over 4 seeds (sd 2.309815e-13, 9.3% of mean; min 2.153185e-12, max 2.699829e-12)
- `sigma_32`: mean 3.496850e-12 over 4 seeds (sd 2.293196e-13, 6.6% of mean; min 3.278335e-12, max 3.752177e-12)
- `sigma_64`: mean 4.766609e-12 over 4 seeds (sd 1.063844e-13, 2.2% of mean; min 4.634414e-12, max 4.882780e-12)
- `sigma_r2_1`: mean 7.311617e-13 over 4 seeds (sd 1.568175e-14, 2.1% of mean; min 7.094253e-13, max 7.448874e-13)
- `sigma_r2_2`: mean 8.488940e-13 over 4 seeds (sd 1.335029e-14, 1.6% of mean; min 8.400107e-13, max 8.687663e-13)
- `sigma_r2_4`: mean 1.022877e-12 over 4 seeds (sd 4.861844e-14, 4.8% of mean; min 9.697129e-13, max 1.083343e-12)
- `sigma_r2_8`: mean 1.306597e-12 over 4 seeds (sd 1.391010e-13, 10.6% of mean; min 1.187140e-12, max 1.472478e-12)
- `sigma_r2_16`: mean 1.693973e-12 over 4 seeds (sd 2.946745e-13, 17.4% of mean; min 1.398788e-12, max 2.098895e-12)
- `sigma_r2_32`: mean 2.071718e-12 over 4 seeds (sd 4.826802e-13, 23.3% of mean; min 1.618882e-12, max 2.673003e-12)
- `sigma_r2_64`: mean 2.942856e-12 over 4 seeds (sd 1.124253e-12, 38.2% of mean; min 1.830816e-12, max 4.054859e-12)
- `sigma_startup16_1`: mean 1.283428e-12 over 4 seeds (sd 1.012097e-13, 7.9% of mean; min 1.189076e-12, max 1.425978e-12)
- `sigma_startup16_2`: mean 1.801338e-12 over 4 seeds (sd 2.289706e-13, 12.7% of mean; min 1.602335e-12, max 2.063980e-12)
- `sigma_startup16_4`: mean 3.093611e-12 over 4 seeds (sd 3.794841e-13, 12.3% of mean; min 2.725507e-12, max 3.502558e-12)
- `sigma_startup16_8`: mean 4.699076e-12 over 4 seeds (sd 4.014378e-13, 8.5% of mean; min 4.168667e-12, max 5.089965e-12)
- `i_ring_a`: mean 1.896215e-05 over 4 seeds (sd 2.291652e-11, 0.0% of mean; min 1.896213e-05, max 1.896218e-05)
- `p_active_w`: mean 6.257509e-05 over 4 seeds (sd 7.562541e-11, 0.0% of mean; min 6.257503e-05, max 6.257520e-05)
- `e_per_cycle_j`: mean 4.178002e-13 over 4 seeds (sd 8.015730e-19, 0.0% of mean; min 4.177993e-13, max 4.178011e-13)
- `c_eff_node_f`: mean 3.487772e-15 over 4 seeds (sd 6.691462e-21, 0.0% of mean; min 3.487765e-15, max 3.487780e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py array-liveness-tap-phase-xsb-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-xsb-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-xsb-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-xsb-clocked --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 86400 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
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
