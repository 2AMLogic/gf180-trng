---
record: 2026-08-03-sampler-bit-bias-clocked-integer-01
date: 2026-08-03T10:36:40Z
status: valid

testbench:
  path: sim/tb/sampler-bit-bias-clocked-integer/tb_sampler_bit_bias_clocked.sp
  sha: 8a50e95a9aa8331fbdeaf869197973aa56d9d50e
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
  path: sim/records/raw/2026-08-03-sampler-bit-bias-clocked-integer-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:18404fa59dcb1e698a3bb1f2ae6f36e1d17d21a9a2ff991090ded60c35b77929
    - tt_27c_3.30v-run0.log  sha256:46e6c0bb6b7112e86902af4c0f427df8a9be290194289dab85e03f96b4e5a9f9
    - tt_27c_3.30v-run1.spice  sha256:a764b900d1e59af6681a74fd6ec8b706058d59d18b495d7da4a842b21219e015
    - tt_27c_3.30v-run1.log  sha256:e8605b6503ce2112a18fbbccdf05e584e7549f11c30eec1323fb685f49884802
    - tt_27c_3.30v-run2.spice  sha256:c729a738807318d35df4db3367c512ad323104759fddaae3e838a295b5b37eb7
    - tt_27c_3.30v-run2.log  sha256:dbd637316471c1184add591288fed6d69aab968e42ba12d2882c5f87601106d7
    - tt_27c_3.30v-run3.spice  sha256:cafa351362dadaa226d59f7c4733ab9f9854b0c6ba7db4e663d794c583cd6304
    - tt_27c_3.30v-run3.log  sha256:e0b7f38d8047fffa76b43008ad942327828fcf6a1ec8ceeb5190c57dec5429b6
wall_time: 180.1m
---

## Result

- `period_r1`: mean 2.842875e-09 over 4 seeds (sd 1.699923e-14, 0.0% of mean; min 2.842856e-09, max 2.842897e-09)
- `period_r2`: mean 2.634162e-09 over 4 seeds (sd 1.894647e-14, 0.0% of mean; min 2.634145e-09, max 2.634187e-09)
- `f_r1`: mean 3.517566e+08 over 4 seeds (sd 2103.36, 0.0% of mean; min 3.517539e+08, max 3.517589e+08)
- `f_r2`: mean 3.796273e+08 over 4 seeds (sd 2730.5, 0.0% of mean; min 3.796237e+08, max 3.796298e+08)
- `ring1_periods_per_sample`: mean 3.99595 over 4 seeds (sd 2.389416e-05, 0.0% of mean; min 3.99592, max 3.99598)
- `ring2_periods_per_sample`: mean 4.31257 over 4 seeds (sd 3.101846e-05, 0.0% of mean; min 4.31253, max 4.31259)
- `tclk_s`: mean 1.136000e-08 over 4 seeds (sd 0, 0.0% of mean; min 1.136000e-08, max 1.136000e-08)
- `n_samples`: mean 256 over 4 seeds (sd 0, 0.0% of mean; min 256, max 256)
- `ones_frac`: mean 0.49707 over 4 seeds (sd 0.00373995, 0.8% of mean; min 0.492188, max 0.5)
- `bit_mean`: mean -0.00585938 over 4 seeds (sd 0.0074799, 127.7% of mean; min -0.015625, max 0)
- `ones_frac_first128`: mean 0.443359 over 4 seeds (sd 0.00390625, 0.9% of mean; min 0.4375, max 0.445312)
- `ones_frac_last128`: mean 0.550781 over 4 seeds (sd 0.0078125, 1.4% of mean; min 0.539062, max 0.554688)
- `worst_rail_dev_v`: mean 0.0012735 over 4 seeds (sd 5.773503e-07, 0.0% of mean; min 0.001273, max 0.001274)
- `xo_swing_v`: mean 3.49802 over 4 seeds (sd 0.00254968, 0.1% of mean; min 3.49579, max 3.50154)
- `r_1`: mean -0.25098 over 4 seeds (sd 0.00784314, 3.1% of mean; min -0.262745, max -0.247059)
- `r_2`: mean -0.46063 over 4 seeds (sd 0.00787402, 1.7% of mean; min -0.472441, max -0.456693)
- `r_3`: mean 0.750988 over 4 seeds (sd 0.00790514, 1.1% of mean; min 0.747036, max 0.762846)
- `r_4`: mean -0.0515873 over 4 seeds (sd 0.00793651, 15.4% of mean; min -0.0634921, max -0.047619)
- `r_6`: mean 0.516 over 4 seeds (sd 0.008, 1.6% of mean; min 0.512, max 0.528)
- `r_8`: mean -0.657258 over 4 seeds (sd 0.00806452, 1.2% of mean; min -0.66129, max -0.645161)
- `r_12`: mean 0.0737705 over 4 seeds (sd 0.0163934, 22.2% of mean; min 0.0655738, max 0.0983607)
- `r_16`: mean 0.733333 over 4 seeds (sd 0, 0.0% of mean; min 0.733333, max 0.733333)
- `bit_code_00`: mean 14025 over 4 seeds (sd 0, 0.0% of mean; min 14025, max 14025)
- `bit_code_01`: mean 13897 over 4 seeds (sd 0, 0.0% of mean; min 13897, max 13897)
- `bit_code_02`: mean 13897 over 4 seeds (sd 0, 0.0% of mean; min 13897, max 13897)
- `bit_code_03`: mean 13897 over 4 seeds (sd 0, 0.0% of mean; min 13897, max 13897)
- `bit_code_04`: mean 13897 over 4 seeds (sd 0, 0.0% of mean; min 13897, max 13897)
- `bit_code_05`: mean 13897 over 4 seeds (sd 0, 0.0% of mean; min 13897, max 13897)
- `bit_code_06`: mean 13641 over 4 seeds (sd 512, 3.8% of mean; min 12873, max 13897)
- `bit_code_07`: mean 45641 over 4 seeds (sd 0, 0.0% of mean; min 45641, max 45641)
- `bit_code_08`: mean 49737 over 4 seeds (sd 8192, 16.5% of mean; min 37449, max 53833)
- `bit_code_09`: mean 51638 over 4 seeds (sd 0, 0.0% of mean; min 51638, max 51638)
- `bit_code_10`: mean 51638 over 4 seeds (sd 0, 0.0% of mean; min 51638, max 51638)
- `bit_code_11`: mean 51638 over 4 seeds (sd 0, 0.0% of mean; min 51638, max 51638)
- `bit_code_12`: mean 51638 over 4 seeds (sd 0, 0.0% of mean; min 51638, max 51638)
- `bit_code_13`: mean 52662 over 4 seeds (sd 0, 0.0% of mean; min 52662, max 52662)
- `bit_code_14`: mean 12086 over 4 seeds (sd 256, 2.1% of mean; min 11702, max 12214)
- `bit_code_15`: mean 14025 over 4 seeds (sd 0, 0.0% of mean; min 14025, max 14025)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-bit-bias-clocked-integer --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-clocked-integer --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-clocked-integer --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 72000 --no-write
python3 sim/run_corners.py sampler-bit-bias-clocked-integer --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 72000 --no-write
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
