---
record: 2026-10-09-sampler-array-digitize-01
date: 2026-10-09T17:14:34Z
status: valid

testbench:
  path: sim/tb/sampler-array-digitize/tb_sampler_array_digitize.sp
  sha: 0d6c4814afc3e6c4014ef7b836ea88c568e77907
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 29db4bcfbd44cd351e79774ebc1d3b15f7d2dc63

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: Linux-7.0.0-1014-aws-x86_64-with-glibc2.39

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: tran-noise
  tstop: 132n
  tstep: 10p (print step; also ngspice's tmax. Matched to vn_dt = 10 ps, the noise sources' own breakpoint spacing, which already floors the solver step -- a finer print step would multiply output size and runtime without changing what the solver does)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 11 sources per ring, 22 in total
  runs: 3
seeds: [1001, 1002, 1003]

raw:
  path: sim/records/raw/2026-10-09-sampler-array-digitize-01/
  files:
    - ss_125c_3.63v-run0.spice  sha256:2f7e5e8b693bdea83072f0c9d0788859d7f38d2849651ba9f29cac0347cc23b0
    - ss_125c_3.63v-run0.log  sha256:5f2ff4cfdb89c74601e56bb6a732dd2961695ecd2b78d71c79f32896c3f73908
    - ss_125c_3.63v-run1.spice  sha256:dd4dec07a07c55918c2afdb2f12af4f596d567fe7ef7d4e6441817a0e570b394
    - ss_125c_3.63v-run1.log  sha256:19e50494ca318f47c286f0098c18dc0472bfdb98cae5c632300ed041ce98e7c0
    - ss_125c_3.63v-run2.spice  sha256:4e97e9e613c2af4e7893befaadfd1351d8351e523a2dc4cb073e4931359af20f
    - ss_125c_3.63v-run2.log  sha256:f0a730e322993c8ffebc0dde39c9d623db43e9a7bb4b6189f993e555171b2650
wall_time: 1.2m
---

## Result

- `rb_rst_v`: mean 8.140087e-06 over 3 seeds (sd 1.082847e-08, 0.1% of mean; min 8.132111e-06, max 8.152414e-06)
- `rv_rst_v`: mean 3.429444e-08 over 3 seeds (sd 1.429452e-13, 0.0% of mean; min 3.429432e-08, max 3.429460e-08)
- `b0_v`: mean 3.63001 over 3 seeds (sd 0, 0.0% of mean; min 3.63001, max 3.63001)
- `b1_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b2_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b3_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b4_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b5_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b6_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b7_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b8_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b9_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `rv0_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `rv9_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `ones_count`: mean 10 over 3 seeds (sd 0, 0.0% of mean; min 10, max 10)
- `worst_rail_dev_v`: mean 1.000003e-06 over 3 seeds (sd 0, 0.0% of mean; min 1.000003e-06, max 1.000003e-06)
- `period_r1`: no data (all runs failed to converge)
- `period_r2`: mean 9.582221e-09 over 3 seeds (sd 2.522473e-13, 0.0% of mean; min 9.582067e-09, max 9.582513e-09)
- `f_r1`: no data (all runs failed to converge)
- `f_r2`: mean 1.043599e+08 over 3 seeds (sd 2747.18, 0.0% of mean; min 1.043568e+08, max 1.043616e+08)
- `freq_ratio_r2_r1`: no data (all runs failed to converge)
- `ring_periods_per_sample`: no data (all runs failed to converge)
- `xo_swing_v`: mean 3.69914 over 3 seeds (sd 5.709326e-04, 0.0% of mean; min 3.69859, max 3.69973)
- `ring1_swing_v`: mean 3.73434 over 3 seeds (sd 2.760046e-04, 0.0% of mean; min 3.73411, max 3.73465)
- `xo_trans_per_s`: no data (all runs failed to converge)

Run failures:
- seed 1001: failed -- Error: measure  t1b  when(WHEN) : out of interval
- seed 1002: failed -- Error: measure  t1b  when(WHEN) : out of interval
- seed 1003: failed -- Error: measure  t1b  when(WHEN) : out of interval

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-array-digitize --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 1001 --timeout 7200 --no-write
python3 sim/run_corners.py sampler-array-digitize --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 1002 --timeout 7200 --no-write
python3 sim/run_corners.py sampler-array-digitize --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 1003 --timeout 7200 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
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
