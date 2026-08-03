---
record: 2026-08-03-sampler-bit-bias-clocked-generic-01
date: 2026-08-03T10:03:44Z
status: valid

testbench:
  path: sim/tb/sampler-bit-bias-clocked-generic/tb_sampler_bit_bias_clocked.sp
  sha: 26967b9045298340ce7fed8e64bb4e8baf9d0067
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: a5f47de8c57879a7a3ffd9f32e273f288371fcf0

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
  path: sim/records/raw/2026-08-03-sampler-bit-bias-clocked-generic-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:9013115f58e35048a5d3d24633b2342b6102d1b85975d0259d3ad12441e322e3
    - tt_27c_3.30v-run0.log  sha256:e65e248c1385652b9d726476e70e6777cbc4d06d09c2557c3c93edfc97f61b06
    - tt_27c_3.30v-run1.spice  sha256:58fcfd6495c0af5fc655876c7549402056bf5e48ecce9292cf45d0a5a79a9072
    - tt_27c_3.30v-run1.log  sha256:9ea84d988be7407a197c9ce0859765da77d209b87e53ede657a80b85d11bc73a
    - tt_27c_3.30v-run2.spice  sha256:ce98a348792cc645cd27d3283dfa39e95a805fb3538759911304a50f2a7c04b1
    - tt_27c_3.30v-run2.log  sha256:b0639150b2b681ecd7128b058b3cffc7b89a7726712f796c9c300eb02edad1d5
    - tt_27c_3.30v-run3.spice  sha256:3ce40b2a09c08577ca4c8c28f75668c895a99b444bd553560fc575f29035314c
    - tt_27c_3.30v-run3.log  sha256:0d8d26c7716dee7a08521ed6f95e56d8705874702d369e438066dc8b03115d62
wall_time: 144.8m
---

## Result

- `period_r1`: mean 2.842763e-09 over 4 seeds (sd 2.921497e-14, 0.0% of mean; min 2.842725e-09, max 2.842793e-09)
- `period_r2`: mean 2.634208e-09 over 4 seeds (sd 6.366007e-15, 0.0% of mean; min 2.634203e-09, max 2.634217e-09)
- `f_r1`: mean 3.517705e+08 over 4 seeds (sd 3615.15, 0.0% of mean; min 3.517668e+08, max 3.517751e+08)
- `f_r2`: mean 3.796207e+08 over 4 seeds (sd 917.417, 0.0% of mean; min 3.796194e+08, max 3.796215e+08)
- `ring1_periods_per_sample`: mean 4.38306 over 4 seeds (sd 4.504469e-05, 0.0% of mean; min 4.38301, max 4.38312)
- `ring2_periods_per_sample`: mean 4.73007 over 4 seeds (sd 1.143098e-05, 0.0% of mean; min 4.73006, max 4.73008)
- `tclk_s`: mean 1.246000e-08 over 4 seeds (sd 0, 0.0% of mean; min 1.246000e-08, max 1.246000e-08)
- `n_samples`: mean 256 over 4 seeds (sd 0, 0.0% of mean; min 256, max 256)
- `ones_frac`: mean 0.530273 over 4 seeds (sd 0.00585938, 1.1% of mean; min 0.523438, max 0.535156)
- `bit_mean`: mean 0.0605469 over 4 seeds (sd 0.0117188, 19.4% of mean; min 0.046875, max 0.0703125)
- `ones_frac_first128`: mean 0.509766 over 4 seeds (sd 0.0117188, 2.3% of mean; min 0.492188, max 0.515625)
- `ones_frac_last128`: mean 0.550781 over 4 seeds (sd 0.0078125, 1.4% of mean; min 0.539062, max 0.554688)
- `worst_rail_dev_v`: mean 0.001261 over 4 seeds (sd 0, 0.0% of mean; min 0.001261, max 0.001261)
- `xo_swing_v`: mean 3.49411 over 4 seeds (sd 0.00429576, 0.1% of mean; min 3.48876, max 3.4979)
- `r_1`: mean -0.0509804 over 4 seeds (sd 0.0202509, 39.7% of mean; min -0.0745098, max -0.027451)
- `r_2`: mean -0.0590551 over 4 seeds (sd 0.00787402, 13.3% of mean; min -0.0629921, max -0.0472441)
- `r_3`: mean 0.201581 over 4 seeds (sd 0.012909, 6.4% of mean; min 0.185771, max 0.217391)
- `r_4`: mean -0.40873 over 4 seeds (sd 0.00793651, 1.9% of mean; min -0.412698, max -0.396825)
- `r_6`: mean 0.176 over 4 seeds (sd 0.0092376, 5.2% of mean; min 0.168, max 0.184)
- `r_8`: mean 0.185484 over 4 seeds (sd 0.0093121, 5.0% of mean; min 0.177419, max 0.193548)
- `r_12`: mean 0.057377 over 4 seeds (sd 0.0133852, 23.3% of mean; min 0.0409836, max 0.0737705)
- `r_16`: mean -0.254167 over 4 seeds (sd 0.0159571, 6.3% of mean; min -0.266667, max -0.233333)
- `bit_code_00`: mean 14859 over 4 seeds (sd 0, 0.0% of mean; min 14859, max 14859)
- `bit_code_01`: mean 44212 over 4 seeds (sd 0, 0.0% of mean; min 44212, max 44212)
- `bit_code_02`: mean 49385 over 4 seeds (sd 0, 0.0% of mean; min 49385, max 49385)
- `bit_code_03`: mean 42870 over 4 seeds (sd 128, 0.3% of mean; min 42678, max 42934)
- `bit_code_04`: mean 23301.5 over 4 seeds (sd 3, 0.0% of mean; min 23297, max 23303)
- `bit_code_05`: mean 5790 over 4 seeds (sd 0, 0.0% of mean; min 5790, max 5790)
- `bit_code_06`: mean 31084 over 4 seeds (sd 0, 0.0% of mean; min 31084, max 31084)
- `bit_code_07`: mean 61658 over 4 seeds (sd 0, 0.0% of mean; min 61658, max 61658)
- `bit_code_08`: mean 28133 over 4 seeds (sd 0, 0.0% of mean; min 28133, max 28133)
- `bit_code_09`: mean 36675 over 4 seeds (sd 2364.83, 6.4% of mean; min 34627, max 38723)
- `bit_code_10`: mean 13750 over 4 seeds (sd 2364.83, 17.2% of mean; min 11702, max 15798)
- `bit_code_11`: mean 55389 over 4 seeds (sd 0, 0.0% of mean; min 55389, max 55389)
- `bit_code_12`: mean 46326 over 4 seeds (sd 18918.6, 40.8% of mean; min 29942, max 62710)
- `bit_code_13`: mean 52065 over 4 seeds (sd 0, 0.0% of mean; min 52065, max 52065)
- `bit_code_14`: mean 1795 over 4 seeds (sd 141.911, 7.9% of mean; min 1683, max 2003)
- `bit_code_15`: mean 20269 over 4 seeds (sd 0, 0.0% of mean; min 20269, max 20269)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-bit-bias-clocked-generic --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 36000 --no-write
python3 sim/run_corners.py sampler-bit-bias-clocked-generic --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 36000 --no-write
python3 sim/run_corners.py sampler-bit-bias-clocked-generic --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 36000 --no-write
python3 sim/run_corners.py sampler-bit-bias-clocked-generic --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 36000 --no-write
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
