---
record: 2026-08-03-array-liveness-tap-phase-xsb-static-01
date: 2026-08-03T22:50:44Z
status: valid

testbench:
  path: sim/tb/array-liveness-tap-phase-xsb-static/tb_array_liveness_tap_phase_xsb_static.sp
  sha: ad4ae5f6842f25430aab865f7097032b84cc43af
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
  path: sim/records/raw/2026-08-03-array-liveness-tap-phase-xsb-static-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:9c00702be0ea26ac9656ff6fa87515e3a1ac175f60d73a8c63606681be51d1d0
    - tt_27c_3.30v-run0.log  sha256:ad97fbe213922ffd527b2739a4b49743a9beecfcb45bd9c6064f14db5e5060c8
    - tt_27c_3.30v-run1.spice  sha256:e7a85ed2d743d0ac1cdf8f0d45fa5d198b6e4c5e9d26111bf6c4894ffb87f09e
    - tt_27c_3.30v-run1.log  sha256:928daac9c211bcc5d8ed1dfef3d8e0b76fe6bc5fd7ca34641029bb1d5f11dd8e
    - tt_27c_3.30v-run2.spice  sha256:9cc1fc70073e4d8b0616f2ddb157310a6b3598a391cc50f225379622518bd103
    - tt_27c_3.30v-run2.log  sha256:d2756d4bbb0a0a7437b643eab636e6149731ec44dfc9065e89deb7f09f76bf90
    - tt_27c_3.30v-run3.spice  sha256:fc3e1925cdee5418031bd0f832da9f8cae3aa5f5dbb9c35d1ffdb644f5251a8b
    - tt_27c_3.30v-run3.log  sha256:6bbc9553181e3dc804eb5c3f585ec4bb23fe19748a72a8ee0c6326c2bb92152f
wall_time: 70.0m
---

## Result

- `period`: mean 6.676763e-09 over 4 seeds (sd 2.650765e-14, 0.0% of mean; min 6.676725e-09, max 6.676787e-09)
- `f_osc`: mean 1.497732e+08 over 4 seeds (sd 594.621, 0.0% of mean; min 1.497726e+08, max 1.497740e+08)
- `period_startup16`: mean 6.676723e-09 over 4 seeds (sd 1.020244e-13, 0.0% of mean; min 6.676616e-09, max 6.676858e-09)
- `period_r2`: mean 6.240495e-09 over 4 seeds (sd 3.386274e-14, 0.0% of mean; min 6.240475e-09, max 6.240545e-09)
- `period_b00`: mean 6.676815e-09 over 4 seeds (sd 5.425526e-14, 0.0% of mean; min 6.676744e-09, max 6.676876e-09)
- `period_b01`: mean 6.676819e-09 over 4 seeds (sd 6.816887e-14, 0.0% of mean; min 6.676746e-09, max 6.676904e-09)
- `period_b02`: mean 6.676559e-09 over 4 seeds (sd 6.781776e-14, 0.0% of mean; min 6.676475e-09, max 6.676638e-09)
- `period_b03`: mean 6.676790e-09 over 4 seeds (sd 1.032179e-13, 0.0% of mean; min 6.676658e-09, max 6.676887e-09)
- `period_b04`: mean 6.676894e-09 over 4 seeds (sd 6.601240e-14, 0.0% of mean; min 6.676842e-09, max 6.676988e-09)
- `period_b05`: mean 6.676528e-09 over 4 seeds (sd 1.196784e-14, 0.0% of mean; min 6.676521e-09, max 6.676546e-09)
- `period_b06`: mean 6.676848e-09 over 4 seeds (sd 6.504092e-14, 0.0% of mean; min 6.676767e-09, max 6.676908e-09)
- `period_b07`: mean 6.676896e-09 over 4 seeds (sd 1.717961e-13, 0.0% of mean; min 6.676750e-09, max 6.677083e-09)
- `period_b08`: mean 6.676573e-09 over 4 seeds (sd 1.095815e-13, 0.0% of mean; min 6.676458e-09, max 6.676667e-09)
- `period_b09`: mean 6.676771e-09 over 4 seeds (sd 7.216879e-14, 0.0% of mean; min 6.676708e-09, max 6.676875e-09)
- `period_b10`: mean 6.676875e-09 over 4 seeds (sd 5.892557e-14, 0.0% of mean; min 6.676792e-09, max 6.676917e-09)
- `period_b11`: mean 6.676625e-09 over 4 seeds (sd 9.001028e-14, 0.0% of mean; min 6.676500e-09, max 6.676708e-09)
- `period_b12`: mean 6.676729e-09 over 4 seeds (sd 7.978556e-14, 0.0% of mean; min 6.676667e-09, max 6.676833e-09)
- `period_b13`: mean 6.676792e-09 over 4 seeds (sd 1.226634e-13, 0.0% of mean; min 6.676625e-09, max 6.676917e-09)
- `period_b14`: mean 6.676823e-09 over 4 seeds (sd 1.147411e-13, 0.0% of mean; min 6.676708e-09, max 6.676958e-09)
- `period_b15`: mean 6.676646e-09 over 4 seeds (sd 7.216876e-14, 0.0% of mean; min 6.676542e-09, max 6.676708e-09)
- `sigma_1`: mean 1.458062e-12 over 4 seeds (sd 6.442012e-14, 4.4% of mean; min 1.411389e-12, max 1.553273e-12)
- `sigma_2`: mean 1.860134e-12 over 4 seeds (sd 6.970993e-14, 3.7% of mean; min 1.774828e-12, max 1.943937e-12)
- `sigma_4`: mean 2.590741e-12 over 4 seeds (sd 1.601776e-13, 6.2% of mean; min 2.372450e-12, max 2.743560e-12)
- `sigma_8`: mean 3.219200e-12 over 4 seeds (sd 2.264545e-13, 7.0% of mean; min 2.901514e-12, max 3.431580e-12)
- `sigma_16`: mean 2.490801e-12 over 4 seeds (sd 2.363844e-13, 9.5% of mean; min 2.268193e-12, max 2.797316e-12)
- `sigma_32`: mean 3.573386e-12 over 4 seeds (sd 3.761185e-13, 10.5% of mean; min 3.236520e-12, max 3.922521e-12)
- `sigma_64`: mean 4.891652e-12 over 4 seeds (sd 6.339146e-13, 13.0% of mean; min 4.067357e-12, max 5.600114e-12)
- `sigma_r2_1`: mean 7.290256e-13 over 4 seeds (sd 3.880434e-14, 5.3% of mean; min 6.978240e-13, max 7.849066e-13)
- `sigma_r2_2`: mean 8.259160e-13 over 4 seeds (sd 6.339277e-14, 7.7% of mean; min 7.706903e-13, max 8.814546e-13)
- `sigma_r2_4`: mean 1.015981e-12 over 4 seeds (sd 7.683112e-14, 7.6% of mean; min 9.207786e-13, max 1.092001e-12)
- `sigma_r2_8`: mean 1.302913e-12 over 4 seeds (sd 2.046689e-13, 15.7% of mean; min 1.128959e-12, max 1.532357e-12)
- `sigma_r2_16`: mean 1.852107e-12 over 4 seeds (sd 4.330486e-13, 23.4% of mean; min 1.388012e-12, max 2.330682e-12)
- `sigma_r2_32`: mean 2.519839e-12 over 4 seeds (sd 5.535650e-13, 22.0% of mean; min 1.850454e-12, max 3.180608e-12)
- `sigma_r2_64`: mean 3.337078e-12 over 4 seeds (sd 5.624890e-13, 16.9% of mean; min 2.595260e-12, max 3.963218e-12)
- `sigma_startup16_1`: mean 1.227042e-12 over 4 seeds (sd 5.344339e-14, 4.4% of mean; min 1.163666e-12, max 1.290348e-12)
- `sigma_startup16_2`: mean 1.802828e-12 over 4 seeds (sd 1.498932e-13, 8.3% of mean; min 1.668302e-12, max 2.017074e-12)
- `sigma_startup16_4`: mean 2.678146e-12 over 4 seeds (sd 5.078247e-13, 19.0% of mean; min 2.369135e-12, max 3.435878e-12)
- `sigma_startup16_8`: mean 4.043346e-12 over 4 seeds (sd 7.855016e-13, 19.4% of mean; min 3.596746e-12, max 5.217139e-12)
- `i_ring_a`: mean 1.896216e-05 over 4 seeds (sd 1.377205e-11, 0.0% of mean; min 1.896215e-05, max 1.896218e-05)
- `p_active_w`: mean 6.257514e-05 over 4 seeds (sd 4.544865e-11, 0.0% of mean; min 6.257510e-05, max 6.257518e-05)
- `e_per_cycle_j`: mean 4.177994e-13 over 4 seeds (sd 1.479149e-18, 0.0% of mean; min 4.177973e-13, max 4.178006e-13)
- `c_eff_node_f`: mean 3.487765e-15 over 4 seeds (sd 1.234783e-20, 0.0% of mean; min 3.487748e-15, max 3.487775e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py array-liveness-tap-phase-xsb-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-xsb-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-xsb-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 86400 --no-write
python3 sim/run_corners.py array-liveness-tap-phase-xsb-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 86400 --no-write
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
- clk and rst_n are DC sources: this deck contains no edge anywhere after start-up, which is what makes it the static reference for its pair. It measures ONE of the two states its clocked partner alternates between (every sampler_dff's master transmission gate OFF) and is not on its own a statement about the shipped, clocked arrangement.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
