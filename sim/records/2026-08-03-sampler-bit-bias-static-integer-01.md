---
record: 2026-08-03-sampler-bit-bias-static-integer-01
date: 2026-08-03T10:36:40Z
status: valid

testbench:
  path: sim/tb/sampler-bit-bias-static-integer/tb_sampler_bit_bias_static.sp
  sha: e1790649e7732cdfadaf198323e359387d4472a2
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: a5f47de8c57879a7a3ffd9f32e273f288371fcf0-dirty

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
  tstop: 3300.003000n
  tstep: 20p (print step; a fifth of vn_dt = 100 ps, the noise sources' own breakpoint spacing, which floors the solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=7.0713e-4 NT=1e-10 NALPHA=0 NAMP=0 ) -> injected white PSD 2*NA^2*NT = 1.0e-16 V^2/Hz (1e-08 V/sqrt(Hz)), band-limited to 5 GHz, 5 sources per ring, 10 in total
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-03-sampler-bit-bias-static-integer-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:ffe07f1eed489d6cda01a5c946d81aff6d02ebd772690093ea272f3e37986266
    - tt_27c_3.30v-run0.log  sha256:d9600cceb91015532976fba397a343a6ebccfd5bcdfda40ac732a805f84c2ef1
    - tt_27c_3.30v-run1.spice  sha256:fc6a4093be931b8c638956d13063d9ce33cf2bb3626d415099d8e1d7358341ac
    - tt_27c_3.30v-run1.log  sha256:7650ffb62b170a05084a896fab98c9e24add8010cda5f198e651c1928962917e
    - tt_27c_3.30v-run2.spice  sha256:08bb02cb2f9088c11c91eab957d84e935373b76ad8c5dd3ae858e8fc02beac79
    - tt_27c_3.30v-run2.log  sha256:1f7163abb1dd451a1e90c1f9ce22533c358b5577fd3544fa58b93b9ab7d4866b
    - tt_27c_3.30v-run3.spice  sha256:bdfdad51954309017ab6dcb99b49d7761601d911f48481417bba60076e8b63c1
    - tt_27c_3.30v-run3.log  sha256:df2363417c59ea3b023d64d065d0d1e1a2707bed6499b7e4db879c469e7df2eb
wall_time: 178.5m
---

## Result

- `period_r1`: mean 2.849278e-09 over 4 seeds (sd 1.450696e-14, 0.0% of mean; min 2.849264e-09, max 2.849298e-09)
- `period_r2`: mean 2.640152e-09 over 4 seeds (sd 1.189144e-14, 0.0% of mean; min 2.640140e-09, max 2.640165e-09)
- `f_r1`: mean 3.509661e+08 over 4 seeds (sd 1786.92, 0.0% of mean; min 3.509637e+08, max 3.509678e+08)
- `f_r2`: mean 3.787661e+08 over 4 seeds (sd 1705.99, 0.0% of mean; min 3.787641e+08, max 3.787678e+08)
- `ring1_periods_per_sample`: mean 3.98698 over 4 seeds (sd 2.029943e-05, 0.0% of mean; min 3.98695, max 3.98699)
- `ring2_periods_per_sample`: mean 4.30278 over 4 seeds (sd 1.938004e-05, 0.0% of mean; min 4.30276, max 4.3028)
- `tclk_s`: mean 1.136000e-08 over 4 seeds (sd 0, 0.0% of mean; min 1.136000e-08, max 1.136000e-08)
- `n_samples`: mean 256 over 4 seeds (sd 0, 0.0% of mean; min 256, max 256)
- `ones_frac`: mean 0.480469 over 4 seeds (sd 0.00843846, 1.8% of mean; min 0.472656, max 0.492188)
- `bit_mean`: mean -0.0390625 over 4 seeds (sd 0.0168769, 43.2% of mean; min -0.0546875, max -0.015625)
- `ones_frac_first128`: mean 0.498047 over 4 seeds (sd 0.00390625, 0.8% of mean; min 0.492188, max 0.5)
- `ones_frac_last128`: mean 0.462891 over 4 seeds (sd 0.0147888, 3.2% of mean; min 0.453125, max 0.484375)
- `worst_rail_dev_v`: mean 0.001274 over 4 seeds (sd 0, 0.0% of mean; min 0.001274, max 0.001274)
- `xo_swing_v`: mean 3.50245 over 4 seeds (sd 0.00168409, 0.0% of mean; min 3.50113, max 3.50485)
- `r_1`: mean -0.184314 over 4 seeds (sd 0.0286391, 15.5% of mean; min -0.215686, max -0.152941)
- `r_2`: mean -0.472441 over 4 seeds (sd 0, 0.0% of mean; min -0.472441, max -0.472441)
- `r_3`: mean 0.602767 over 4 seeds (sd 0.027668, 4.6% of mean; min 0.573123, max 0.636364)
- `r_4`: mean 0.0257937 over 4 seeds (sd 0.0299597, 116.2% of mean; min -0.015873, max 0.047619)
- `r_6`: mean 0.318 over 4 seeds (sd 0.0256125, 8.1% of mean; min 0.296, max 0.344)
- `r_8`: mean -0.481855 over 4 seeds (sd 0.027447, 5.7% of mean; min -0.516129, max -0.459677)
- `r_12`: mean 0.0307377 over 4 seeds (sd 0.027897, 90.8% of mean; min 0.00819672, max 0.0655738)
- `r_16`: mean 0.127083 over 4 seeds (sd 0.0219163, 17.2% of mean; min 0.108333, max 0.15)
- `bit_code_00`: mean 9333 over 4 seeds (sd 72.7645, 0.8% of mean; min 9270, max 9398)
- `bit_code_01`: mean 27867 over 4 seeds (sd 0, 0.0% of mean; min 27867, max 27867)
- `bit_code_02`: mean 46803 over 4 seeds (sd 128, 0.3% of mean; min 46739, max 46995)
- `bit_code_03`: mean 9801 over 4 seeds (sd 0, 0.0% of mean; min 9801, max 9801)
- `bit_code_04`: mean 9369 over 4 seeds (sd 0, 0.0% of mean; min 9369, max 9369)
- `bit_code_05`: mean 45637 over 4 seeds (sd 4, 0.0% of mean; min 45635, max 45643)
- `bit_code_06`: mean 14029 over 4 seeds (sd 0, 0.0% of mean; min 14029, max 14029)
- `bit_code_07`: mean 39801 over 4 seeds (sd 0, 0.0% of mean; min 39801, max 39801)
- `bit_code_08`: mean 37476 over 4 seeds (sd 0, 0.0% of mean; min 37476, max 37476)
- `bit_code_09`: mean 21065 over 4 seeds (sd 16384, 77.8% of mean; min 12873, max 45641)
- `bit_code_10`: mean 56100.2 over 4 seeds (sd 0.5, 0.0% of mean; min 56100, max 56101)
- `bit_code_11`: mean 37740 over 4 seeds (sd 0, 0.0% of mean; min 37740, max 37740)
- `bit_code_12`: mean 18871 over 4 seeds (sd 0, 0.0% of mean; min 18871, max 18871)
- `bit_code_13`: mean 39206 over 4 seeds (sd 0, 0.0% of mean; min 39206, max 39206)
- `bit_code_14`: mean 10020 over 4 seeds (sd 8927.03, 89.1% of mean; min 4900, max 23332)
- `bit_code_15`: mean 52658 over 4 seeds (sd 0, 0.0% of mean; min 52658, max 52658)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-bit-bias-static-integer --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-static-integer --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-static-integer --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-static-integer --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 72000 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- clk rate: 11.36 ns (~88.0 MHz). Chosen so the per-clk-cycle phase advance is ~4.00 ring-1 periods. This is the adversarial rate: a near-integer phase advance is where a circle map locks, so if the clk-locked modulation can pin the ring's sampled phase, this is the rate at which it does. Both this deck and its control are heavily correlated at this rate BY CONSTRUCTION -- that is a property of sampling a nearly-deterministic ring at a near-rational ratio, not of the digitizer, and the measurement is the difference between the two decks, not either one alone.
- 256 sampled bits per run. Binomial sampling noise alone puts ~1/sqrt(N) = 0.062 on the +/-1 bit mean of an independent stream, and these bits are NOT independent, so the effective resolution on bias is coarser than that -- sim/tools/sampler_bit_bias_variants.py computes it from the measured serial correlations rather than assuming independence.
- The noise sources' own time step is 100 ps here, where #51's coupling ladder and #76's phase family used 10 ps. The injected white PSD is the SAME 1e-16 V^2/Hz (NA is rescaled with NT so 2*NA^2*NT is unchanged); what changes is that the injected noise is band-limited to 5 GHz instead of 50 GHz, which is what makes microsecond-scale windows on a two-ring array affordable at all -- a trnoise() source plants a solver breakpoint at every NT, and 10 ps breakpoints cost ~4x the run time. Two consequences, both stated rather than absorbed: (a) both arms of every comparison in this family carry the identical stimulus, so the DIFFERENTIAL result this family exists for cannot move with it; (b) no per-period jitter or sigma may be read off these records and compared with the 10 ps families' -- this family reports no sigma and makes no jitter claim, by construction.
- NOT an entropy measurement and NOT a randomness claim. The injected per-stage noise is a fixed synthetic white PSD (1e-16 V^2/Hz), not this cell's physical device noise, and over any simulable window it accumulates far too little phase to randomize the sampled bit: at this corner sigma_1 is ~0.7 ps against a ~2.8 ns ring period (sim/records/2026-08-03-ring-liveness-tap-phase-buffered-01), so smearing the ring's phase over a full period would need ~2e7 ring periods (~60 ms) of accumulation. The sampled bit in every deck of this family is therefore essentially DETERMINISTIC, which is exactly what makes it a sensitive probe for a deterministic clk-locked mechanism -- and exactly why no bias figure here may be read as a statement about the shipped block's entropy. DR-0004's tiering is unchanged.
- The measurement is the DIFFERENCE between this deck and its one-line-different counterpart at the same clk rate (sampler-bit-bias-clocked-* against sampler-bit-bias-static-*), not this deck's bias in isolation. The two share seeds, noise sources and source order, so a given seed draws the same noise realization in both and the comparison is paired.
- One corner, tt/27 C/3.30 V, chosen so this family is directly comparable with #76's phase family and #51's coupling ladder. Nothing here is claimed at any other process, temperature or supply.
- 5-stage rings, where the shipped array's ro_ring11 has 11. Deliberate, for comparability with #51/#76, and conservative: the digitizer loads exactly one node either way, and one node is a larger share of a 5-stage ring's delay, so any modulation here over-states the shipped ring's by roughly 11/5.
- sampler_core's xsv (the raw_valid register) is not instantiated. Its only inputs are clk and vdd, both ideal sources here, so it can couple to nothing this deck measures. raw_valid's contract is sim/tb/sampler-array-digitize/'s subject.
- Ideal supply. Rings, buffers, combiner and samplers sit on zero-volt ammeter sources off one ideal vsup, which has no impedance for one branch's current to develop a voltage across, so this deck says nothing about supply-network coupling from the digitizers' own switching -- a second path a real block has and this one does not. The finding is a lower bound on what a built block will show, not an upper one.
- abstol is relaxed to 1e-10 (100x ngspice's 1e-12 default) for the reason sim/tb/sampler-array-digitize/ bisected and documented: two series-starved rings hold their devices at currents where a 1 pA absolute tolerance is a meaningful fraction of the branch currents solved, and an abrupt external edge in the same matrix then drives the timestep control to zero. 100 pA is ~5e-6 of the per-ring supply current, and everything measured here is a settled node voltage or a zero-crossing time rather than a current.
- Every clk timing is off the 10 ps grid the trnoise() sources place breakpoints on (tclk_del = 300.003 ns, tclk_tr = 0.203 ns, tclk_per a multiple of 20 ps, tstop carrying the same 3 ns offset). A PULSE or tstop breakpoint landing exactly on a trnoise breakpoint collapses ngspice-46's transient ('Timestep too small') at that instant, reproducibly -- the solver limit #76's family recorded so it would not be rediscovered.
- rst_n is held at vdd throughout, so every sampler is out of reset and no reset edge falls in the window. DR-0014's gated-reset behaviour is sim/tb/sampler-dff-reset-clocked/'s subject.
- Pre-layout, schematic-derived netlist (design/sampler_core.spice), no extracted parasitics. Layout adds coupling paths between a clocked cell and a ring node; it removes none.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
