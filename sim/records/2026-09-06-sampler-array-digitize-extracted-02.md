---
record: 2026-09-06-sampler-array-digitize-extracted-02
date: 2026-09-06T22:51:05Z
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
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: Linux-7.0.0-1010-aws-x86_64-with-glibc2.39

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
seeds: [1, 2, 3]

raw:
  path: sim/records/raw/2026-09-06-sampler-array-digitize-extracted-02/
  files:
    - tt_27c_3.30v-run0.spice  sha256:b3da7d926e1cc6e94e1a6a9f5712a86845efcc50c5d4f83b4ad143245cd4573a
    - tt_27c_3.30v-run0.log  sha256:74a36a4ccaea4356480870e3a4746976a3909752420413ff4c15c957739cfa82
    - tt_27c_3.30v-run1.spice  sha256:af67f8d68a8c3c08812cdaa2bbf9a763e0a93d047c5e1cf762ce1abb4d00dff4
    - tt_27c_3.30v-run1.log  sha256:a7c67564cd2852a89ae98b06b9cf0bd7dc6a9612008aa5d0a034d92abc5e40f9
    - tt_27c_3.30v-run2.spice  sha256:ab855464f5160799747957f1acef24cb0c5d696732542d25c3ca4415c432fb33
    - tt_27c_3.30v-run2.log  sha256:c92d0a10d0f23f929d1ad685463231ac32aca892fb5999f65f9334b2dc9c768c
wall_time: 2.1m
---

## Result

- `rb_rst_v`: mean 8.097041e-04 over 3 seeds (sd 1.600959e-05, 2.0% of mean; min 7.915236e-04, max 8.216943e-04)
- `rv_rst_v`: mean 3.387077e-04 over 3 seeds (sd 1.480735e-05, 4.4% of mean; min 3.220426e-04, max 3.503513e-04)
- `b0_v`: mean -3.263566e-04 over 3 seeds (sd 1.163361e-05, 3.6% of mean; min -3.377880e-04, max -3.145308e-04)
- `b1_v`: mean 0.00402574 over 3 seeds (sd 4.300775e-05, 1.1% of mean; min 0.00398581, max 0.00407128)
- `b2_v`: mean 3.31144 over 3 seeds (sd 8.804734e-05, 0.0% of mean; min 3.31135, max 3.31153)
- `b3_v`: mean 3.30087 over 3 seeds (sd 3.511885e-06, 0.0% of mean; min 3.30087, max 3.30087)
- `b4_v`: mean 3.29751 over 3 seeds (sd 6.658328e-06, 0.0% of mean; min 3.2975, max 3.29751)
- `b5_v`: mean 3.28549 over 3 seeds (sd 7.925486e-05, 0.0% of mean; min 3.28541, max 3.28557)
- `b6_v`: mean 3.31587 over 3 seeds (sd 2.007486e-05, 0.0% of mean; min 3.31585, max 3.31589)
- `b7_v`: mean 3.29573 over 3 seeds (sd 6.421059e-05, 0.0% of mean; min 3.29567, max 3.2958)
- `b8_v`: mean 3.30228 over 3 seeds (sd 1.159023e-05, 0.0% of mean; min 3.30227, max 3.30229)
- `b9_v`: mean 3.2921 over 3 seeds (sd 3.857460e-05, 0.0% of mean; min 3.29205, max 3.29213)
- `rv0_v`: mean 3.29973 over 3 seeds (sd 1.652271e-05, 0.0% of mean; min 3.29971, max 3.29974)
- `rv9_v`: mean 3.29451 over 3 seeds (sd 3.157531e-05, 0.0% of mean; min 3.29448, max 3.29454)
- `ones_count`: mean 8 over 3 seeds (sd 0, 0.0% of mean; min 8, max 8)
- `worst_rail_dev_v`: mean 0.0145117 over 3 seeds (sd 7.925486e-05, 0.5% of mean; min 0.014429, max 0.014587)
- `period_r1`: mean 9.387076e-09 over 3 seeds (sd 8.297564e-14, 0.0% of mean; min 9.387020e-09, max 9.387172e-09)
- `period_r2`: mean 8.902303e-09 over 3 seeds (sd 1.789327e-13, 0.0% of mean; min 8.902106e-09, max 8.902455e-09)
- `f_r1`: mean 1.065294e+08 over 3 seeds (sd 941.649, 0.0% of mean; min 1.065284e+08, max 1.065301e+08)
- `f_r2`: mean 1.123305e+08 over 3 seeds (sd 2257.81, 0.0% of mean; min 1.123286e+08, max 1.123330e+08)
- `freq_ratio_r2_r1`: mean 1.05445 over 3 seeds (sd 2.997818e-05, 0.0% of mean; min 1.05443, max 1.05449)
- `ring_periods_per_sample`: mean 1.06529 over 3 seeds (sd 9.416490e-06, 0.0% of mean; min 1.06528, max 1.0653)
- `xo_swing_v`: mean 3.38367 over 3 seeds (sd 1.103733e-04, 0.0% of mean; min 3.38357, max 3.38379)
- `ring1_swing_v`: mean 3.36659 over 3 seeds (sd 9.192528e-04, 0.0% of mean; min 3.36599, max 3.36765)
- `xo_trans_per_s`: mean 4.377198e+08 over 3 seeds (sd 2885.72, 0.0% of mean; min 4.377169e+08, max 4.377227e+08)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-array-digitize-extracted --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py sampler-array-digitize-extracted --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py sampler-array-digitize-extracted --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
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
