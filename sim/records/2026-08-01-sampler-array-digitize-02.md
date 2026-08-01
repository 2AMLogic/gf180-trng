---
record: 2026-08-01-sampler-array-digitize-02
date: 2026-08-01T18:12:54Z
status: valid

testbench:
  path: sim/tb/sampler-array-digitize/tb_sampler_array_digitize.sp
  sha: 3af00eb92e8e5e084600a8a649c44aa816fc2451
netlist:
  path: design/sampler_core.spice
  sha: b884211ac1a7fbaf020472ffc9354d86cb1df74c
repo_commit: 723762cae73feac23c288d485f5e6ce26bbe4317-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran-noise
  tstop: 132n
  tstep: 10p (print step; also ngspice's tmax. Matched to vn_dt = 10 ps, the noise sources' own breakpoint spacing, which already floors the solver step -- a finer print step would multiply output size and runtime without changing what the solver does)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 11 sources per ring, 22 in total
  runs: 3
seeds: [1001, 1002, 1003]

raw:
  path: sim/records/raw/2026-08-01-sampler-array-digitize-02/
  files:
    - ss_-40c_3.63v-run0.spice  sha256:a8517cbc36278ceb802a27af4e887bb8a8105102923404bf6905ebfcbf4ab003
    - ss_-40c_3.63v-run0.log  sha256:08621dcf37853391dab69dc85b67b06ed9957e939d17fd5161d8b3954228fc38
    - ss_-40c_3.63v-run1.spice  sha256:bb3280f2994a209d469762301e53aba2aae7b0583412d7d37b26e44643433bd1
    - ss_-40c_3.63v-run1.log  sha256:145a5bf59c79e6600d4f7076358912ac1311fa42ec6181253a684f0504953ad4
    - ss_-40c_3.63v-run2.spice  sha256:49097bf9c9c760f0ac7b69e1f54bf6fc20c32207524806822223509bad3cdfdb
    - ss_-40c_3.63v-run2.log  sha256:83e69d6dfd175f90d2d97a60bbcf50b36cb34bafabaf8047062335e65ff03a62
wall_time: 57.9m
---

## Result

- `rb_rst_v`: mean 3.728483e-06 over 3 seeds (sd 1.906327e-06, 51.1% of mean; min 2.244743e-06, max 5.878533e-06)
- `rv_rst_v`: mean 1.800209e-08 over 3 seeds (sd 8.082904e-14, 0.0% of mean; min 1.800204e-08, max 1.800218e-08)
- `b0_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b1_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b2_v`: mean 3.62989 over 3 seeds (sd 5.131601e-06, 0.0% of mean; min 3.62989, max 3.6299)
- `b3_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b4_v`: mean -3.346434e-06 over 3 seeds (sd 2.631743e-08, 0.8% of mean; min -3.369588e-06, max -3.317812e-06)
- `b5_v`: mean 3.63 over 3 seeds (sd 5.773503e-07, 0.0% of mean; min 3.63, max 3.63)
- `b6_v`: mean -3.640844e-07 over 3 seeds (sd 1.791849e-08, 4.9% of mean; min -3.834418e-07, max -3.480779e-07)
- `b7_v`: mean -9.740908e-08 over 3 seeds (sd 5.432321e-08, 55.8% of mean; min -1.349559e-07, max -3.511914e-08)
- `b8_v`: mean 3.63002 over 3 seeds (sd 0, 0.0% of mean; min 3.63002, max 3.63002)
- `b9_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `rv0_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `rv9_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `ones_count`: mean 7 over 3 seeds (sd 0, 0.0% of mean; min 7, max 7)
- `worst_rail_dev_v`: mean 1.083333e-04 over 3 seeds (sd 5.131601e-06, 4.7% of mean; min 1.040000e-04, max 1.140000e-04)
- `period_r1`: mean 6.143071e-09 over 3 seeds (sd 8.358746e-14, 0.0% of mean; min 6.142983e-09, max 6.143149e-09)
- `period_r2`: mean 5.791620e-09 over 3 seeds (sd 1.540828e-13, 0.0% of mean; min 5.791455e-09, max 5.791760e-09)
- `f_r1`: mean 1.627850e+08 over 3 seeds (sd 2214.99, 0.0% of mean; min 1.627830e+08, max 1.627874e+08)
- `f_r2`: mean 1.726633e+08 over 3 seeds (sd 4593.64, 0.0% of mean; min 1.726591e+08, max 1.726682e+08)
- `freq_ratio_r2_r1`: mean 1.06068 over 3 seeds (sd 2.791028e-05, 0.0% of mean; min 1.06066, max 1.06071)
- `ring_periods_per_sample`: mean 1.62785 over 3 seeds (sd 2.214986e-05, 0.0% of mean; min 1.62783, max 1.62787)
- `xo_swing_v`: mean 3.74659 over 3 seeds (sd 1.719130e-04, 0.0% of mean; min 3.74641, max 3.74675)
- `ring1_swing_v`: mean 3.92316 over 3 seeds (sd 3.127386e-04, 0.0% of mean; min 3.92292, max 3.92351)
- `xo_trans_per_s`: mean 6.708966e+08 over 3 seeds (sd 11250.7, 0.0% of mean; min 6.708841e+08, max 6.709059e+08)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-array-digitize --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 1001 --no-write
python3 sim/run_corners.py sampler-array-digitize --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 1002 --no-write
python3 sim/run_corners.py sampler-array-digitize --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 1003 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- NOT a rate measurement. The sample clock here is 100 MHz (param tclk = 10 ns), two orders of magnitude above DR-0003's ratified > 1 Mbps raw target, chosen so that ten raw bits fit inside a transient-noise window this array can afford to simulate. Sampling faster than the target accumulates LESS jitter per bit, so this is the conservative direction for a functional demonstration and the wrong direction for any entropy claim.
- NOT an entropy measurement. The injected per-stage noise is a fixed synthetic white PSD (1e-16 V^2/Hz), not this cell's physical device noise, so the bit pattern below is evidence that the sampler digitizes a live, noisy source -- not evidence of how much min-entropy each bit carries. Recovering physical jitter needs sim/tb/rostage-noise/'s per-corner device-noise density and DR-0010's jitter-energy law.
- Ten bits is far too short a sequence for any statistical claim. No bias, correlation or randomness assertion is made or implied by the ones_count figure; it is reported so a reader can see the bits are not all identical, and for no other purpose.
- abstol is relaxed to 1e-10 (100x ngspice's 1e-12 default) because this deck does not converge at the default -- see the testbench header for the bisection that established it is not a noise, edge-rate or sampler-cell effect. 100 pA is ~5e-6 of this array's per-ring supply current, and the measured quantities are settled node voltages and ring periods rather than currents, but the relaxation is real and is stated rather than absorbed.
- The sample clock has a 1 ns edge (param tclk_tr) on a 10 ns period, so the effective sampling instant is defined only to within the clock's transit through the transmission gates' switching threshold. The sharp-edge (1 ps) case is covered at the real target period by sim/tb/sampler-dff-setup-hold/.
- The array's top-level wiring is restated in the testbench fragment rather than instantiated from sampler_core, because ngspice cannot insert a series noise source inside a subcircuit. Every device -- rings, XOR, and both samplers -- still comes from the schematic-derived netlist; only ro_array_core's two ring instantiations and its XOR connection are re-expressed. Compare against design/xschem/ro_array_core.sch when reviewing.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
