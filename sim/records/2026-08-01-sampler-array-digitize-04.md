---
record: 2026-08-01-sampler-array-digitize-04
date: 2026-08-01T23:49:04Z
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
  path: sim/records/raw/2026-08-01-sampler-array-digitize-04/
  files:
    - ss_-40c_3.63v-run0.spice  sha256:a2d1cfab46914229ecb0fb5f06a1f6283ca0b031efda3fb7276db473d7113b3b
    - ss_-40c_3.63v-run0.log  sha256:3dc20a2442616f0aeeaf20e6858857625ce754f95bbc6f98b02603652b8a02bd
    - ss_-40c_3.63v-run1.spice  sha256:9ff736a60cf93ab3d2fc1e8ea2b617a9103266d05b90d175118f29c9148a10df
    - ss_-40c_3.63v-run1.log  sha256:12b614aacf24a92cc984242d8a85b2c21e77c18ad04741fbd33bec917091e128
    - ss_-40c_3.63v-run2.spice  sha256:4d0bbd330a85ee8dea3710ded47fe2d706c15d998bda3e447d98c38ed8d0c064
    - ss_-40c_3.63v-run2.log  sha256:c51a596512b74f33ac4020b3e8964de7cbfdadb486fa9d0895a83813e6695415
wall_time: 51.5m
---

## Result

- `rb_rst_v`: mean 3.789951e-05 over 3 seeds (sd 1.184359e-06, 3.1% of mean; min 3.676224e-05, max 3.912592e-05)
- `rv_rst_v`: mean 1.800216e-08 over 3 seeds (sd 1.096966e-13, 0.0% of mean; min 1.800207e-08, max 1.800228e-08)
- `b0_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b1_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b2_v`: mean 3.63002 over 3 seeds (sd 2.835489e-05, 0.0% of mean; min 3.62998, max 3.63004)
- `b3_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b4_v`: mean -5.914213e-06 over 3 seeds (sd 1.170050e-07, 2.0% of mean; min -6.046337e-06, max -5.823705e-06)
- `b5_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `b6_v`: mean -1.152206e-06 over 3 seeds (sd 3.107827e-08, 2.7% of mean; min -1.187886e-06, max -1.131040e-06)
- `b7_v`: mean -1.159137e-08 over 3 seeds (sd 3.134247e-08, 270.4% of mean; min -4.505467e-08, max 1.707787e-08)
- `b8_v`: mean 3.63002 over 3 seeds (sd 0, 0.0% of mean; min 3.63002, max 3.63002)
- `b9_v`: mean 3.63 over 3 seeds (sd 5.773503e-07, 0.0% of mean; min 3.63, max 3.63)
- `rv0_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `rv9_v`: mean 3.63 over 3 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)
- `ones_count`: mean 7 over 3 seeds (sd 0, 0.0% of mean; min 7, max 7)
- `worst_rail_dev_v`: mean 6.333336e-06 over 3 seeds (sd 9.237604e-06, 145.9% of mean; min 1.000003e-06, max 1.700000e-05)
- `period_r1`: mean 6.139328e-09 over 3 seeds (sd 1.353136e-13, 0.0% of mean; min 6.139176e-09, max 6.139437e-09)
- `period_r2`: mean 5.793235e-09 over 3 seeds (sd 1.092335e-13, 0.0% of mean; min 5.793120e-09, max 5.793337e-09)
- `f_r1`: mean 1.628843e+08 over 3 seeds (sd 3590.08, 0.0% of mean; min 1.628814e+08, max 1.628883e+08)
- `f_r2`: mean 1.726151e+08 over 3 seeds (sd 3254.73, 0.0% of mean; min 1.726121e+08, max 1.726186e+08)
- `freq_ratio_r2_r1`: mean 1.05974 over 3 seeds (sd 1.466267e-05, 0.0% of mean; min 1.05973, max 1.05976)
- `ring_periods_per_sample`: mean 1.62884 over 3 seeds (sd 3.590079e-05, 0.0% of mean; min 1.62881, max 1.62888)
- `xo_swing_v`: mean 3.74019 over 3 seeds (sd 3.988039e-05, 0.0% of mean; min 3.74016, max 3.74023)
- `ring1_swing_v`: mean 3.87372 over 3 seeds (sd 1.867110e-04, 0.0% of mean; min 3.87358, max 3.87393)
- `xo_trans_per_s`: mean 6.709988e+08 over 3 seeds (sd 12923.5, 0.0% of mean; min 6.709905e+08, max 6.710137e+08)

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
