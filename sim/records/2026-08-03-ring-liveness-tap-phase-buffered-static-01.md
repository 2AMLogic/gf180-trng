---
record: 2026-08-03-ring-liveness-tap-phase-buffered-static-01
date: 2026-08-03T05:49:15Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-phase-buffered-static/tb_ring_liveness_tap_phase_buffered_static.sp
  sha: 7c07574b1b62c4e9b55d0acfbac7db21d08709d8
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 7f1ef079da7441626a734000f85e5ffefc3c0bd0-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /home/ubuntu/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: Linux-7.0.0-1009-aws-x86_64-with-glibc2.39

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran-noise
  tstop: 2.600003u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources, one in series with every stage input
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-03-ring-liveness-tap-phase-buffered-static-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:1a84363a71b135d48d8a029c8ba1854a07ca34b2741427c14e391e6bc2aa3d39
    - tt_27c_3.30v-run0.log  sha256:fee6d77d4628fbc88dd92a72e9b94810e0421305c7f483c47f9ca1e9b3c648bb
    - tt_27c_3.30v-run1.spice  sha256:27d68c17c257b15bfb8537e775b2e53714b3f823f95f8d987a28afb3065654aa
    - tt_27c_3.30v-run1.log  sha256:6544577071a333c78a074f28aa6e84dbf75903c4d4ba3c6e890e6185d617dcaa
    - tt_27c_3.30v-run2.spice  sha256:7dfdc87e10259952551578302f73f009a591113643c7e2d6c6faddb0e943679a
    - tt_27c_3.30v-run2.log  sha256:8f965b167396872f4db77eca5109b40c2d0aa1d8ce09e75bae21085ccdef3c03
    - tt_27c_3.30v-run3.spice  sha256:8a18124d89d1be1ae2e0bc7acf73d8a252d6d71a3b67bf5b0bf67b4e7a509080
    - tt_27c_3.30v-run3.log  sha256:aed13cf87624a3d1b82f53f518ee6d2239ebe780f690676c6e89de3d8431e144
wall_time: 17.2m
---

## Result

- `period`: mean 2.874045e-09 over 4 seeds (sd 1.992276e-14, 0.0% of mean; min 2.874019e-09, max 2.874062e-09)
- `f_osc`: mean 3.479416e+08 over 4 seeds (sd 2411.93, 0.0% of mean; min 3.479396e+08, max 3.479449e+08)
- `period_startup16`: mean 2.873984e-09 over 4 seeds (sd 1.682157e-13, 0.0% of mean; min 2.873751e-09, max 2.874147e-09)
- `period_b00`: mean 2.874039e-09 over 4 seeds (sd 8.350481e-14, 0.0% of mean; min 2.873942e-09, max 2.874110e-09)
- `period_b01`: mean 2.874033e-09 over 4 seeds (sd 8.767136e-14, 0.0% of mean; min 2.873904e-09, max 2.874100e-09)
- `period_b02`: mean 2.874071e-09 over 4 seeds (sd 5.009756e-14, 0.0% of mean; min 2.874008e-09, max 2.874127e-09)
- `period_b03`: mean 2.874039e-09 over 4 seeds (sd 4.157977e-14, 0.0% of mean; min 2.874000e-09, max 2.874087e-09)
- `period_b04`: mean 2.874028e-09 over 4 seeds (sd 6.685087e-14, 0.0% of mean; min 2.873973e-09, max 2.874125e-09)
- `period_b05`: mean 2.874053e-09 over 4 seeds (sd 7.962904e-14, 0.0% of mean; min 2.873942e-09, max 2.874129e-09)
- `period_b06`: mean 2.874098e-09 over 4 seeds (sd 5.545997e-14, 0.0% of mean; min 2.874035e-09, max 2.874165e-09)
- `period_b07`: mean 2.874036e-09 over 4 seeds (sd 7.481407e-14, 0.0% of mean; min 2.873960e-09, max 2.874127e-09)
- `period_b08`: mean 2.874083e-09 over 4 seeds (sd 2.946278e-14, 0.0% of mean; min 2.874042e-09, max 2.874104e-09)
- `period_b09`: mean 2.874021e-09 over 4 seeds (sd 3.803628e-14, 0.0% of mean; min 2.873979e-09, max 2.874062e-09)
- `period_b10`: mean 2.874052e-09 over 4 seeds (sd 9.238982e-14, 0.0% of mean; min 2.873979e-09, max 2.874188e-09)
- `period_b11`: mean 2.874021e-09 over 4 seeds (sd 5.103101e-14, 0.0% of mean; min 2.873979e-09, max 2.874083e-09)
- `period_b12`: mean 2.874047e-09 over 4 seeds (sd 4.294900e-14, 0.0% of mean; min 2.874000e-09, max 2.874083e-09)
- `period_b13`: mean 2.874052e-09 over 4 seeds (sd 7.115936e-14, 0.0% of mean; min 2.873979e-09, max 2.874146e-09)
- `period_b14`: mean 2.874052e-09 over 4 seeds (sd 6.014064e-14, 0.0% of mean; min 2.873979e-09, max 2.874125e-09)
- `period_b15`: mean 2.873995e-09 over 4 seeds (sd 7.864411e-14, 0.0% of mean; min 2.873917e-09, max 2.874104e-09)
- `sigma_1`: mean 6.902371e-13 over 4 seeds (sd 1.508682e-14, 2.2% of mean; min 6.717394e-13, max 7.086617e-13)
- `sigma_2`: mean 8.210187e-13 over 4 seeds (sd 3.229870e-14, 3.9% of mean; min 7.904875e-13, max 8.503793e-13)
- `sigma_4`: mean 1.026466e-12 over 4 seeds (sd 2.696990e-14, 2.6% of mean; min 9.933983e-13, max 1.048817e-12)
- `sigma_8`: mean 1.330192e-12 over 4 seeds (sd 3.673006e-14, 2.8% of mean; min 1.294107e-12, max 1.381142e-12)
- `sigma_16`: mean 1.795178e-12 over 4 seeds (sd 1.450975e-13, 8.1% of mean; min 1.646347e-12, max 1.994441e-12)
- `sigma_32`: mean 2.427442e-12 over 4 seeds (sd 3.753950e-13, 15.5% of mean; min 1.940632e-12, max 2.856327e-12)
- `sigma_64`: mean 3.065277e-12 over 4 seeds (sd 8.159057e-13, 26.6% of mean; min 2.036425e-12, max 4.033069e-12)
- `sigma_128`: mean 3.198203e-12 over 4 seeds (sd 7.460306e-13, 23.3% of mean; min 2.187062e-12, max 3.914064e-12)
- `sigma_startup16_1`: mean 5.006939e-13 over 4 seeds (sd 8.458268e-14, 16.9% of mean; min 4.363318e-13, max 6.145534e-13)
- `sigma_startup16_2`: mean 6.322540e-13 over 4 seeds (sd 7.856246e-14, 12.4% of mean; min 5.553979e-13, max 7.394031e-13)
- `sigma_startup16_4`: mean 8.565950e-13 over 4 seeds (sd 1.463695e-13, 17.1% of mean; min 6.574571e-13, max 1.001325e-12)
- `sigma_startup16_8`: mean 1.050789e-12 over 4 seeds (sd 2.341188e-13, 22.3% of mean; min 8.287368e-13, max 1.351762e-12)
- `i_ring_a`: mean 1.881854e-05 over 4 seeds (sd 5.990546e-11, 0.0% of mean; min 1.881848e-05, max 1.881860e-05)
- `p_active_w`: mean 6.210117e-05 over 4 seeds (sd 1.976869e-10, 0.0% of mean; min 6.210097e-05, max 6.210140e-05)
- `e_per_cycle_j`: mean 1.784816e-13 over 4 seeds (sd 7.008805e-19, 0.0% of mean; min 1.784806e-13, max 1.784820e-13)
- `c_eff_node_f`: mean 3.277899e-15 over 4 seeds (sd 1.287203e-20, 0.0% of mean; min 3.277880e-15, max 3.277907e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered-static --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 3000 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Variant of issue #76's phase-cost experiment on the DR-0016 per-ring liveness digitizer. The comparison it exists for is against sim/tb/ro-ring5-starved-jitter-long/ (the CONTROL: the same ring, device for device, with nothing attached) and against the other variants of this family, which differ from each other only in what clk does. The ring, the injected noise density, the window geometry (opened 256 periods after start-up, spanning 512 periods), the print step and the corner are identical across the whole family and to #51's variants in sim/characterization-array-ring-coupling.md, which is what makes the two experiments directly comparable.
- The buffer is `ro_buf` out of design/sampler_core.spice -- this tb.json's own design netlist -- instantiated rather than restated, so the deck cannot drift from the cell it claims to measure. It is supplied through its own zero-volt ammeter source (vb1) off the same ideal vsup, exactly as sim/tb/ro-array-coupling-xor-driven-buffered/ does, so i_ring_a/p_active_w keep measuring the RING and stay comparable expression for expression to the control's. In the shipped block the buffers likewise run off the block supply vdd, never off a ring's vddr.
- clk and rst_n are DC sources: this deck contains no edge anywhere after start-up, which is what makes it the static reference for the buffered pair. It measures ONE of the two states the clocked buffered deck alternates between (master transmission gate OFF) and is not on its own a statement about the shipped, clocked arrangement -- sim/tb/ring-liveness-tap-phase-buffered/ is.
- This deck adopts nothing and re-opens nothing. PR #82 already adopted the per-ring buffer, and #75 / sim/characterization-ring-buffer-mitigation.md owns the combiner-side evidence for that decision (the buffer's own power, the ring power freed by the reduced load, and the block's active-power rollup). What this deck adds is the one path that decision was NOT measured on: whether the buffer removes the clk-locked phase disturbance on the DR-0016 digitizer tap.
- sigma_* here is NOT a jitter measurement if what it captures is deterministic. The estimator is the control's, but it measures the spread of period-to-period increments from whatever cause, and a load modulation locked to clk enters it exactly as noise would. The seed spread and the accumulation exponent reported alongside are what tell the two apart, and no entropy claim may be built on this record's sigma either way.
- The ring is 5-stage, where the shipped array's rings (design/ro_array_core.spice, ro_ring11) have 11. That is deliberate: #51's whole ladder is on this 5-stage ring at this corner and window, so this family drops straight into it. The tap loads exactly ONE ring node either way, and one node is a larger fraction of a 5-stage ring's delay than of an 11-stage ring's, so a fractional period or phase effect measured here OVER-states the shipped ring's by roughly 11/5.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used, so this family has a like-for-like row against #51's variants' own startup block. They are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.
- The digitizer is supplied from vsup directly rather than through the ring's sense source, so its own switching current is outside i_ring_a/p_active_w. Its own power is not re-measured here -- sim/tb/ring-liveness-tap-power/ measures it across three PVT points -- and p_active_w/e_per_cycle_j/c_eff_node_f here are the RING's, comparable expression for expression to the control's.
- rst_n is held at vdd for the whole run, so the digitizer is out of reset throughout and contributes no reset edge. DR-0014's gated reset behaviour is measured by sim/tb/sampler-dff-reset-clocked/ and is not what this deck is about.
- Pre-layout, schematic-derived netlist (design/sampler_core.spice), no extracted parasitics. Layout adds coupling paths between a clocked cell and a ring node; it removes none.
- The ring node this deck's buffer drives from is the deck's own ro1, and the deck's probe bx1 still watches that same ring node -- not the buffer output. The measurement is of the RING's phase, which is what issue #76 asks about; the buffer's own delay and its inversion of the node are downstream of the quantity measured and do not enter it.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
