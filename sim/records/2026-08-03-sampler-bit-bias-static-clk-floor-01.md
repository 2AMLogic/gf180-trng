---
record: 2026-08-03-sampler-bit-bias-static-clk-floor-01
date: 2026-08-03T10:36:40Z
status: valid

testbench:
  path: sim/tb/sampler-bit-bias-static-clk-floor/tb_sampler_bit_bias_static.sp
  sha: 093f11511e09919fd4372c5e5d94d0d5c68fb646
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
  tstop: 13000.003000n
  tstep: 20p (print step; a fifth of vn_dt = 100 ps, the noise sources' own breakpoint spacing, which floors the solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=7.0713e-4 NT=1e-10 NALPHA=0 NAMP=0 ) -> injected white PSD 2*NA^2*NT = 1.0e-16 V^2/Hz (1e-08 V/sqrt(Hz)), band-limited to 5 GHz, 5 sources per ring, 10 in total
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-03-sampler-bit-bias-static-clk-floor-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:2245c48e74d95b7f5b8fa2b5b54b3b7c5b9601a782a544826c80b902666d8c97
    - tt_27c_3.30v-run0.log  sha256:028eebb5e53689369be43e347e0e30046e55dca1400adf8bc398544326053d16
    - tt_27c_3.30v-run1.spice  sha256:2233f78299c2ecaf22bdb484437ee5ef828c4d1548a5cd2ba56e7fbdc0e3ad36
    - tt_27c_3.30v-run1.log  sha256:1329b48ae53d9e97362b96e93ed79cecf16946a6c2d7fa5a732f4cb9c18b7a52
    - tt_27c_3.30v-run2.spice  sha256:08131d8145fc5d9ababe30ee24441ecde2e5d97879545876022fd572db16fad7
    - tt_27c_3.30v-run2.log  sha256:7fc26abcaa9da0070bb86ce0209969fe92f70bc762cf052dabb041ed346edbda
    - tt_27c_3.30v-run3.spice  sha256:d3b1f66e0c36f9451b2e167aab57a0886cf4ccb572b489f4cbf8af029be6a38e
    - tt_27c_3.30v-run3.log  sha256:16b5cbf150bb0c2fa8bdae131ac8676f274e7bd86d86fbdb5069d99a216d7996
wall_time: 507.3m
---

## Result

- `period_r1`: mean 2.849285e-09 over 4 seeds (sd 1.214726e-14, 0.0% of mean; min 2.849273e-09, max 2.849298e-09)
- `period_r2`: mean 2.640165e-09 over 4 seeds (sd 8.160589e-15, 0.0% of mean; min 2.640155e-09, max 2.640173e-09)
- `f_r1`: mean 3.509653e+08 over 4 seeds (sd 1496.26, 0.0% of mean; min 3.509636e+08, max 3.509668e+08)
- `f_r2`: mean 3.787642e+08 over 4 seeds (sd 1170.73, 0.0% of mean; min 3.787630e+08, max 3.787656e+08)
- `ring1_periods_per_sample`: mean 351.211 over 4 seeds (sd 0.00149731, 0.0% of mean; min 351.209, max 351.212)
- `ring2_periods_per_sample`: mean 379.029 over 4 seeds (sd 0.00117155, 0.0% of mean; min 379.028, max 379.031)
- `tclk_s`: mean 1.000700e-06 over 4 seeds (sd 0, 0.0% of mean; min 1.000700e-06, max 1.000700e-06)
- `n_samples`: mean 12 over 4 seeds (sd 0, 0.0% of mean; min 12, max 12)
- `ones_frac`: mean 0.5625 over 4 seeds (sd 0.0416667, 7.4% of mean; min 0.5, max 0.583333)
- `bit_mean`: mean 0.125 over 4 seeds (sd 0.0833333, 66.7% of mean; min 0, max 0.166667)
- `ones_frac_first6`: mean 0.666667 over 4 seeds (sd 0, 0.0% of mean; min 0.666667, max 0.666667)
- `ones_frac_last6`: mean 0.458333 over 4 seeds (sd 0.0833333, 18.2% of mean; min 0.333333, max 0.5)
- `worst_rail_dev_v`: mean 0.00125575 over 4 seeds (sd 5.000000e-07, 0.0% of mean; min 0.001255, max 0.001256)
- `xo_swing_v`: mean 3.44305 over 4 seeds (sd 9.799106e-04, 0.0% of mean; min 3.44168, max 3.44401)
- `r_1`: mean 0.272727 over 4 seeds (sd 0, 0.0% of mean; min 0.272727, max 0.272727)
- `r_2`: mean -0.4 over 4 seeds (sd 0, 0.0% of mean; min -0.4, max -0.4)
- `r_3`: mean -0.555556 over 4 seeds (sd 0, 0.0% of mean; min -0.555556, max -0.555556)
- `r_4`: mean -0.3125 over 4 seeds (sd 0.125, 40.0% of mean; min -0.5, max -0.25)
- `bit_code_00`: mean 1788 over 4 seeds (sd 128, 7.2% of mean; min 1596, max 1852)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-bit-bias-static-clk-floor --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-static-clk-floor --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-static-clk-floor --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-static-clk-floor --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 72000 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- clk rate: 1.0007 us (~1 MHz). DR-0003's ratified raw-rate row is '> 1 Mbps sustained at the raw tap' and DR-0012 makes clk a fixed external pin with no divider, so this is the shipped operating point. It is the same rate #76's clocked decks ran at, and it is deliberately not a round number (see the canonical deck's note on the trnoise breakpoint grid).
- 12 sampled bits per run. Binomial sampling noise alone puts ~1/sqrt(N) = 0.289 on the +/-1 bit mean of an independent stream, and these bits are NOT independent, so the effective resolution on bias is coarser than that -- sim/tools/sampler_bit_bias_variants.py computes it from the measured serial correlations rather than assuming independence.
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
