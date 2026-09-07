---
record: 2026-09-06-sampler-array-digitize-extracted-03
date: 2026-09-06T22:53:26Z
status: valid
level: extracted

testbench:
  path: sim/tb/sampler-array-digitize-extracted/tb_sampler_array_digitize_extracted.sp
  sha: e8e617ee63a6341829121413f9eb28b586173f8f
netlist:
  path: layout/pex/sampler_core.extracted.spice
  sha: 1ac5fc2ec119729e3a5f3f7cc485fe8ddc145167
repo_commit: 01b6c4d060ddff949cba90c49762d7d9059c431a-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: Linux-7.0.0-1010-aws-x86_64-with-glibc2.39

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
seeds: [1, 2, 3]

raw:
  path: sim/records/raw/2026-09-06-sampler-array-digitize-extracted-03/
  files:
    - ss_-40c_3.63v-run0.spice  sha256:38188233289ca593f6b948094512ae98cbe9cf9ac75c1ba09b384a15c58b22b1
    - ss_-40c_3.63v-run0.log  sha256:701085ff970d8d53f1d926859946d99ee50a084fcbda2154e177fde3a7f0045f
    - ss_-40c_3.63v-run1.spice  sha256:12788aa7a642beed80f6bfd2e78559fecf6d91924adc9c0685bc9fa96939df57
    - ss_-40c_3.63v-run1.log  sha256:9c5c8a78fd8650b6b66d2e56fe40a4d2e271057abcf75c1b9af60a242ff3ce77
    - ss_-40c_3.63v-run2.spice  sha256:6d9dc142d87d4e9409d9243363cb11b76e062f1a1a88c678510c827c13d3af4d
    - ss_-40c_3.63v-run2.log  sha256:04a7c9a167475c47c06e0f4bd19f9ef5384be7c0edd2a6e5075dfcb559d1ea81
wall_time: 2.5m
---

## Result

- `rb_rst_v`: mean 3.686874e-04 over 3 seeds (sd 1.608008e-06, 0.4% of mean; min 3.673514e-04, max 3.704721e-04)
- `rv_rst_v`: mean 3.623906e-04 over 3 seeds (sd 1.586986e-06, 0.4% of mean; min 3.610560e-04, max 3.641454e-04)
- `b0_v`: mean 3.63043 over 3 seeds (sd 4.445597e-05, 0.0% of mean; min 3.63039, max 3.63048)
- `b1_v`: mean 0.00500443 over 3 seeds (sd 5.720221e-05, 1.1% of mean; min 0.00494462, max 0.0050586)
- `b2_v`: mean 3.62459 over 3 seeds (sd 3.394604e-05, 0.0% of mean; min 3.62456, max 3.62462)
- `b3_v`: mean 3.63004 over 3 seeds (sd 2.886751e-06, 0.0% of mean; min 3.63004, max 3.63004)
- `b4_v`: mean 3.63363 over 3 seeds (sd 1.266228e-05, 0.0% of mean; min 3.63362, max 3.63364)
- `b5_v`: mean 3.63001 over 3 seeds (sd 2.357965e-05, 0.0% of mean; min 3.62999, max 3.63003)
- `b6_v`: mean 0.00165608 over 3 seeds (sd 1.830358e-05, 1.1% of mean; min 0.00163585, max 0.0016715)
- `b7_v`: mean 3.62848 over 3 seeds (sd 2.460549e-04, 0.0% of mean; min 3.6283, max 3.62876)
- `b8_v`: mean 3.62743 over 3 seeds (sd 1.526772e-04, 0.0% of mean; min 3.62729, max 3.62759)
- `b9_v`: mean 0.00103318 over 3 seeds (sd 6.668606e-06, 0.6% of mean; min 0.00102916, max 0.00104088)
- `rv0_v`: mean 3.63181 over 3 seeds (sd 1.913984e-05, 0.0% of mean; min 3.63179, max 3.63183)
- `rv9_v`: mean 3.63166 over 3 seeds (sd 8.962886e-06, 0.0% of mean; min 3.63165, max 3.63167)
- `ones_count`: mean 7 over 3 seeds (sd 0, 0.0% of mean; min 7, max 7)
- `worst_rail_dev_v`: mean 0.00541367 over 3 seeds (sd 3.394604e-05, 0.6% of mean; min 0.005377, max 0.005444)
- `period_r1`: mean 7.850061e-09 over 3 seeds (sd 1.006587e-13, 0.0% of mean; min 7.849993e-09, max 7.850177e-09)
- `period_r2`: mean 7.455364e-09 over 3 seeds (sd 1.824848e-13, 0.0% of mean; min 7.455205e-09, max 7.455563e-09)
- `f_r1`: mean 1.273875e+08 over 3 seeds (sd 1633.44, 0.0% of mean; min 1.273857e+08, max 1.273887e+08)
- `f_r2`: mean 1.341316e+08 over 3 seeds (sd 3283.11, 0.0% of mean; min 1.341280e+08, max 1.341345e+08)
- `freq_ratio_r2_r1`: mean 1.05294 over 3 seeds (sd 1.296504e-05, 0.0% of mean; min 1.05293, max 1.05295)
- `ring_periods_per_sample`: mean 1.27388 over 3 seeds (sd 1.633436e-05, 0.0% of mean; min 1.27386, max 1.27389)
- `xo_swing_v`: mean 3.7104 over 3 seeds (sd 5.921485e-05, 0.0% of mean; min 3.71033, max 3.71045)
- `ring1_swing_v`: mean 3.72795 over 3 seeds (sd 6.748471e-04, 0.0% of mean; min 3.7275, max 3.72872)
- `xo_trans_per_s`: mean 5.230383e+08 over 3 seeds (sd 9778.06, 0.0% of mean; min 5.230274e+08, max 5.230463e+08)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-array-digitize-extracted --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py sampler-array-digitize-extracted --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py sampler-array-digitize-extracted --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, device-level-parasitic-annotated (layout/pex/build.py); NOT a full assembled-ring/inter-region routing extraction -- see layout/pex/build.py's own module docstring and sim/characterization-post-layout-extracted.md for exactly what this does and does not capture.
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
