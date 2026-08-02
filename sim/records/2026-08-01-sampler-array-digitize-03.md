---
record: 2026-08-01-sampler-array-digitize-03
date: 2026-08-01T23:31:55Z
status: valid

testbench:
  path: sim/tb/sampler-array-digitize/tb_sampler_array_digitize.sp
  sha: be538466ba0a08bbe409ff485fd47b4aecf8c7f6
netlist:
  path: design/sampler_core.spice
  sha: 50bc082dc2798c8b98e4ced8ebb70432549aa2ec
repo_commit: dc8570a59d334bdeec04c2e284ed2dbe14a6e0de-dirty

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
  tstop: 132n
  tstep: 10p (print step; also ngspice's tmax. Matched to vn_dt = 10 ps, the noise sources' own breakpoint spacing, which already floors the solver step -- a finer print step would multiply output size and runtime without changing what the solver does)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 11 sources per ring, 22 in total
  runs: 3
seeds: [1001, 1002, 1003]

raw:
  path: sim/records/raw/2026-08-01-sampler-array-digitize-03/
  files:
    - tt_27c_3.30v-run0.spice  sha256:4b832054d0e0237ffb9d68451931ddf46457400500bd231810a54729779e4d5c
    - tt_27c_3.30v-run0.log  sha256:5d890da21d10ab6313d01032976356c41e8f792937f871909889593425d5b095
    - tt_27c_3.30v-run1.spice  sha256:55b0efe37c9aa1ff25af7c4bab71ecea34e237c7443b3d3e4f4b8bd6716c94b6
    - tt_27c_3.30v-run1.log  sha256:539e190cb9098633fbb11c5daa42df350b41acd6adb4ef2899e993c6c78b3f2e
    - tt_27c_3.30v-run2.spice  sha256:1751e8f363894d9a78320436d0de3817be0b2ebcc1b95878d53370d8e0a3674d
    - tt_27c_3.30v-run2.log  sha256:4770a890a7a6bffbd63495fc4beb8cfbbd4821b7fef00b87a85278ca832f0d9c
wall_time: 50.9m
---

## Result

- `rb_rst_v`: mean 9.223852e-08 over 3 seeds (sd 3.501471e-09, 3.8% of mean; min 8.850072e-08, max 9.544231e-08)
- `rv_rst_v`: mean 1.845141e-08 over 3 seeds (sd 2.886751e-14, 0.0% of mean; min 1.845138e-08, max 1.845143e-08)
- `b0_v`: mean -1.474221e-07 over 3 seeds (sd 4.082607e-09, 2.8% of mean; min -1.498664e-07, max -1.427090e-07)
- `b1_v`: mean 1.617320e-08 over 3 seeds (sd 2.816584e-09, 17.4% of mean; min 1.302610e-08, max 1.845736e-08)
- `b2_v`: mean 1.802427e-08 over 3 seeds (sd 2.099895e-09, 11.7% of mean; min 1.563629e-08, max 1.958258e-08)
- `b3_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `b4_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `b5_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `b6_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `b7_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `b8_v`: mean -1.602801e-07 over 3 seeds (sd 2.417794e-09, 1.5% of mean; min -1.630706e-07, max -1.588094e-07)
- `b9_v`: mean -1.612825e-06 over 3 seeds (sd 3.276488e-08, 2.0% of mean; min -1.648965e-06, max -1.585062e-06)
- `rv0_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `rv9_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `ones_count`: mean 5 over 3 seeds (sd 0, 0.0% of mean; min 5, max 5)
- `worst_rail_dev_v`: mean 1.849088e-08 over 3 seeds (sd 1.311465e-09, 7.1% of mean; min 1.703614e-08, max 1.958258e-08)
- `period_r1`: mean 7.120014e-09 over 3 seeds (sd 2.163144e-13, 0.0% of mean; min 7.119885e-09, max 7.120264e-09)
- `period_r2`: mean 6.713755e-09 over 3 seeds (sd 7.333966e-14, 0.0% of mean; min 6.713681e-09, max 6.713828e-09)
- `f_r1`: mean 1.404492e+08 over 3 seeds (sd 4266.94, 0.0% of mean; min 1.404442e+08, max 1.404517e+08)
- `f_r2`: mean 1.489479e+08 over 3 seeds (sd 1627.08, 0.0% of mean; min 1.489463e+08, max 1.489496e+08)
- `freq_ratio_r2_r1`: mean 1.06051 over 3 seeds (sd 4.261211e-05, 0.0% of mean; min 1.06048, max 1.06056)
- `ring_periods_per_sample`: mean 1.40449 over 3 seeds (sd 4.266936e-05, 0.0% of mean; min 1.40444, max 1.40452)
- `xo_swing_v`: mean 3.39378 over 3 seeds (sd 3.935869e-05, 0.0% of mean; min 3.39374, max 3.39382)
- `ring1_swing_v`: mean 3.50747 over 3 seeds (sd 0.00120653, 0.0% of mean; min 3.50624, max 3.50865)
- `xo_trans_per_s`: mean 5.787942e+08 over 3 seeds (sd 5961.71, 0.0% of mean; min 5.787876e+08, max 5.787993e+08)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-array-digitize --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1001 --no-write
python3 sim/run_corners.py sampler-array-digitize --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1002 --no-write
python3 sim/run_corners.py sampler-array-digitize --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1003 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
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
