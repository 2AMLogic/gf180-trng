---
record: 2026-08-03-sampler-bit-bias-static-generic-01
date: 2026-08-03T10:36:40Z
status: valid

testbench:
  path: sim/tb/sampler-bit-bias-static-generic/tb_sampler_bit_bias_static.sp
  sha: a3015b144fc56630ba8906bd21654f9ddcf7d5f0
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
  tstop: 3600.003000n
  tstep: 20p (print step; a fifth of vn_dt = 100 ps, the noise sources' own breakpoint spacing, which floors the solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=7.0713e-4 NT=1e-10 NALPHA=0 NAMP=0 ) -> injected white PSD 2*NA^2*NT = 1.0e-16 V^2/Hz (1e-08 V/sqrt(Hz)), band-limited to 5 GHz, 5 sources per ring, 10 in total
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-03-sampler-bit-bias-static-generic-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:b5bd89b9c0aa1275457554378c5b196228201ffa38d80634c7b63b426394a04e
    - tt_27c_3.30v-run0.log  sha256:6625777c8c405f5a55711d490ea84c523c7cbf6b9c58b9da9e1055032b5e759a
    - tt_27c_3.30v-run1.spice  sha256:856012dbdae419e55d7d04dbdf6f6f5d2284c12d28c5f928166ddf997ca4b641
    - tt_27c_3.30v-run1.log  sha256:56b9862e55e743834da9d969b0039cddfde7b8ad34ec991a2e26cd4eda44a5da
    - tt_27c_3.30v-run2.spice  sha256:884e16891b382e5e683b1ccdd0725993fca04f653e21dc4463bea40022f4ec72
    - tt_27c_3.30v-run2.log  sha256:d603f9f806965155fd2e8a9a5cfedba343ae61d9a5b4f32c319485d582eef44e
    - tt_27c_3.30v-run3.spice  sha256:f51b52c177d237b2981716194998ff1532785b6b606efcc9b080f65730d94d90
    - tt_27c_3.30v-run3.log  sha256:aa7e605603a3b7f483589b27131109e0119e7fdabee1974309c6966e082ce95e
wall_time: 191.0m
---

## Result

- `period_r1`: mean 2.849263e-09 over 4 seeds (sd 3.767148e-15, 0.0% of mean; min 2.849259e-09, max 2.849267e-09)
- `period_r2`: mean 2.640155e-09 over 4 seeds (sd 1.447029e-14, 0.0% of mean; min 2.640138e-09, max 2.640171e-09)
- `f_r1`: mean 3.509680e+08 over 4 seeds (sd 464.031, 0.0% of mean; min 3.509675e+08, max 3.509684e+08)
- `f_r2`: mean 3.787657e+08 over 4 seeds (sd 2075.96, 0.0% of mean; min 3.787633e+08, max 3.787680e+08)
- `ring1_periods_per_sample`: mean 4.37306 over 4 seeds (sd 5.781840e-06, 0.0% of mean; min 4.37305, max 4.37307)
- `ring2_periods_per_sample`: mean 4.71942 over 4 seeds (sd 2.586641e-05, 0.0% of mean; min 4.71939, max 4.71945)
- `tclk_s`: mean 1.246000e-08 over 4 seeds (sd 0, 0.0% of mean; min 1.246000e-08, max 1.246000e-08)
- `n_samples`: mean 256 over 4 seeds (sd 0, 0.0% of mean; min 256, max 256)
- `ones_frac`: mean 0.494141 over 4 seeds (sd 0.00390625, 0.8% of mean; min 0.488281, max 0.496094)
- `bit_mean`: mean -0.0117188 over 4 seeds (sd 0.0078125, 66.7% of mean; min -0.0234375, max -0.0078125)
- `ones_frac_first128`: mean 0.503906 over 4 seeds (sd 0.0078125, 1.6% of mean; min 0.492188, max 0.507812)
- `ones_frac_last128`: mean 0.484375 over 4 seeds (sd 0, 0.0% of mean; min 0.484375, max 0.484375)
- `worst_rail_dev_v`: mean 0.00126 over 4 seeds (sd 0, 0.0% of mean; min 0.00126, max 0.00126)
- `xo_swing_v`: mean 3.50961 over 4 seeds (sd 0.00311113, 0.1% of mean; min 3.50568, max 3.513)
- `r_1`: mean -0.0431373 over 4 seeds (sd 0.0181129, 42.0% of mean; min -0.0588235, max -0.027451)
- `r_2`: mean -0.0551181 over 4 seeds (sd 0, 0.0% of mean; min -0.0551181, max -0.0551181)
- `r_3`: mean 0.320158 over 4 seeds (sd 0.012909, 4.0% of mean; min 0.304348, max 0.335968)
- `r_4`: mean -0.349206 over 4 seeds (sd 0.0129603, 3.7% of mean; min -0.365079, max -0.333333)
- `r_6`: mean 0.104 over 4 seeds (sd 0.0184752, 17.8% of mean; min 0.088, max 0.12)
- `r_8`: mean 0.0564516 over 4 seeds (sd 0, 0.0% of mean; min 0.0564516, max 0.0564516)
- `r_12`: mean 0.295082 over 4 seeds (sd 0.00946476, 3.2% of mean; min 0.286885, max 0.303279)
- `r_16`: mean -0.627083 over 4 seeds (sd 0.00416667, 0.7% of mean; min -0.633333, max -0.625)
- `bit_code_00`: mean 62043 over 4 seeds (sd 0, 0.0% of mean; min 62043, max 62043)
- `bit_code_01`: mean 1444 over 4 seeds (sd 0, 0.0% of mean; min 1444, max 1444)
- `bit_code_02`: mean 53341 over 4 seeds (sd 0, 0.0% of mean; min 53341, max 53341)
- `bit_code_03`: mean 10166 over 4 seeds (sd 0, 0.0% of mean; min 10166, max 10166)
- `bit_code_04`: mean 53373 over 4 seeds (sd 0, 0.0% of mean; min 53373, max 53373)
- `bit_code_05`: mean 14226 over 4 seeds (sd 0, 0.0% of mean; min 14226, max 14226)
- `bit_code_06`: mean 58989 over 4 seeds (sd 1024, 1.7% of mean; min 57453, max 59501)
- `bit_code_07`: mean 38530 over 4 seeds (sd 16384, 42.5% of mean; min 13954, max 46722)
- `bit_code_08`: mean 59700 over 4 seeds (sd 9.2376, 0.0% of mean; min 59692, max 59708)
- `bit_code_09`: mean 46595 over 4 seeds (sd 0, 0.0% of mean; min 46595, max 46595)
- `bit_code_10`: mean 27068 over 4 seeds (sd 0, 0.0% of mean; min 27068, max 27068)
- `bit_code_11`: mean 38403 over 4 seeds (sd 16384, 42.7% of mean; min 13827, max 46595)
- `bit_code_12`: mean 25012 over 4 seeds (sd 0, 0.0% of mean; min 25012, max 25012)
- `bit_code_13`: mean 6990 over 4 seeds (sd 510, 7.3% of mean; min 6735, max 7755)
- `bit_code_14`: mean 26032 over 4 seeds (sd 0, 0.0% of mean; min 26032, max 26032)
- `bit_code_15`: mean 6990.5 over 4 seeds (sd 1, 0.0% of mean; min 6989, max 6991)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-bit-bias-static-generic --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-static-generic --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-static-generic --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-static-generic --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 72000 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- clk rate: 12.46 ns (~80.3 MHz). Chosen so the per-clk-cycle phase advance is ~4.38 ring-1 periods -- a fractional part well away from any low-order rational, which is the regime in which a deterministically-sampled ring produces a near-balanced, near-uncorrelated bit sequence. That makes this the QUIET BACKGROUND of the family: a bias or serial correlation introduced by the clk-locked modulation has nothing here to hide behind.
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
