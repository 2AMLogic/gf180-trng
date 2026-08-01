---
record: 2026-08-01-sampler-array-digitize-01
date: 2026-08-01T17:59:14Z
status: valid

testbench:
  path: sim/tb/sampler-array-digitize/tb_sampler_array_digitize.sp
  sha: 3af00eb92e8e5e084600a8a649c44aa816fc2451
netlist:
  path: design/sampler_core.spice
  sha: b884211ac1a7fbaf020472ffc9354d86cb1df74c
repo_commit: 030796e106fe4b3c29f13540c8dbfcf3356a4807-dirty

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
  path: sim/records/raw/2026-08-01-sampler-array-digitize-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:f7b3bbbff4b2fdec2fbc138b8cfb343b6a3d0e091dcb532574da645eef358c26
    - tt_27c_3.30v-run0.log  sha256:26bc645114aa56940712a4577fe01c5f5a8103dfbd743c90f5a17afb80fe7b41
    - tt_27c_3.30v-run1.spice  sha256:7b637a584b6d1c66581331812cd215f56fb66f5f495ce333e27b84e0af171561
    - tt_27c_3.30v-run1.log  sha256:70ed2dbf8fb7f818b0a01b60ef1d396c738a64d21eb4d1275be05069d75c30f2
    - tt_27c_3.30v-run2.spice  sha256:0597b369e25e44d5aad2ccd8747f8ee03e4e5a181fbaa9705ddce646e37d998c
    - tt_27c_3.30v-run2.log  sha256:5e8bb417e39439733e85f19ed4a7ea9641c7a980a8d1332843bd63962df911f0
wall_time: 40.8m
---

## Result

- `rb_rst_v`: mean 6.732916e-08 over 3 seeds (sd 3.895395e-09, 5.8% of mean; min 6.286270e-08, max 7.002297e-08)
- `rv_rst_v`: mean 1.845144e-08 over 3 seeds (sd 1.266228e-13, 0.0% of mean; min 1.845130e-08, max 1.845154e-08)
- `b0_v`: mean -1.054307e-07 over 3 seeds (sd 1.758111e-09, 1.7% of mean; min -1.070135e-07, max -1.035384e-07)
- `b1_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `b2_v`: mean 1.610845e-08 over 3 seeds (sd 5.367446e-09, 33.3% of mean; min 9.924496e-09, max 1.955893e-08)
- `b3_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `b4_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `b5_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `b6_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `b7_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `b8_v`: mean -5.046958e-07 over 3 seeds (sd 3.180997e-08, 6.3% of mean; min -5.389422e-07, max -4.760721e-07)
- `b9_v`: mean -4.960535e-06 over 3 seeds (sd 3.370318e-08, 0.7% of mean; min -4.989274e-06, max -4.923440e-06)
- `rv0_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `rv9_v`: mean 3.3 over 3 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)
- `ones_count`: mean 6 over 3 seeds (sd 0, 0.0% of mean; min 6, max 6)
- `worst_rail_dev_v`: mean 1.610845e-08 over 3 seeds (sd 5.367446e-09, 33.3% of mean; min 9.924496e-09, max 1.955893e-08)
- `period_r1`: mean 7.124491e-09 over 3 seeds (sd 1.469906e-13, 0.0% of mean; min 7.124323e-09, max 7.124598e-09)
- `period_r2`: mean 6.712917e-09 over 3 seeds (sd 1.625342e-13, 0.0% of mean; min 6.712816e-09, max 6.713104e-09)
- `f_r1`: mean 1.403609e+08 over 3 seeds (sd 2895.92, 0.0% of mean; min 1.403588e+08, max 1.403642e+08)
- `f_r2`: mean 1.489665e+08 over 3 seeds (sd 3606.75, 0.0% of mean; min 1.489624e+08, max 1.489688e+08)
- `freq_ratio_r2_r1`: mean 1.06131 over 3 seeds (sd 4.734228e-05, 0.0% of mean; min 1.06126, max 1.06134)
- `ring_periods_per_sample`: mean 1.40361 over 3 seeds (sd 2.895920e-05, 0.0% of mean; min 1.40359, max 1.40364)
- `xo_swing_v`: mean 3.39122 over 3 seeds (sd 1.839513e-04, 0.0% of mean; min 3.3911, max 3.39143)
- `ring1_swing_v`: mean 3.52329 over 3 seeds (sd 7.012869e-04, 0.0% of mean; min 3.52273, max 3.52407)
- `xo_trans_per_s`: mean 5.786549e+08 over 3 seeds (sd 1945.69, 0.0% of mean; min 5.786532e+08, max 5.786570e+08)

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
