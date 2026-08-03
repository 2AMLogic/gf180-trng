---
record: 2026-08-03-ring-liveness-tap-phase-buffered-01
date: 2026-08-03T04:15:35Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-phase-buffered/tb_ring_liveness_tap_phase_buffered.sp
  sha: 196d327e7b9b6d85b599f522b630567ca887a14f
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: a1d86b3cf08426f173e49b7255a08033a17fdbba-dirty

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
  path: sim/records/raw/2026-08-03-ring-liveness-tap-phase-buffered-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:052a3277214997fb5f0ff368808b9c153707f428d56a198f61614198bb22b09f
    - tt_27c_3.30v-run0.log  sha256:f907151b3bb5ca61c64041ab80fda8bd642cc34de309cfb56025e12c6adbdf78
    - tt_27c_3.30v-run1.spice  sha256:948548ea93661c301965b9474b26a189dfccb8366e1351a15a461db59e6070ce
    - tt_27c_3.30v-run1.log  sha256:4ef0cafa0f9400584a74c4b8b03f6277cff6f302e6454e10195848057490d188
    - tt_27c_3.30v-run2.spice  sha256:5df02f3c320fccb0f4699ce8c1de093beb240c36ba3aafd713a58f28edeab66f
    - tt_27c_3.30v-run2.log  sha256:f5d1c4cd47aef1d6cf72a5d76792bc903c5245222945d069f15af80a304bf120
    - tt_27c_3.30v-run3.spice  sha256:42b4f4517f1fb15543460f604cd150930851d2fb52ac5a5a298b2c8c91262f6b
    - tt_27c_3.30v-run3.log  sha256:c3aa80468255cd3bcd2541a48bf28b69f059bd6040884f93621ad9ee3f4fc9e9
wall_time: 23.2m
---

## Result

- `period`: mean 2.859605e-09 over 4 seeds (sd 3.540871e-15, 0.0% of mean; min 2.859600e-09, max 2.859608e-09)
- `f_osc`: mean 3.496987e+08 over 4 seeds (sd 433.006, 0.0% of mean; min 3.496983e+08, max 3.496992e+08)
- `period_startup16`: mean 2.873799e-09 over 4 seeds (sd 1.120644e-13, 0.0% of mean; min 2.873656e-09, max 2.873928e-09)
- `period_b00`: mean 2.874004e-09 over 4 seeds (sd 6.632232e-14, 0.0% of mean; min 2.873931e-09, max 2.874092e-09)
- `period_b01`: mean 2.874048e-09 over 4 seeds (sd 7.404874e-14, 0.0% of mean; min 2.874000e-09, max 2.874158e-09)
- `period_b02`: mean 2.873999e-09 over 4 seeds (sd 4.597518e-14, 0.0% of mean; min 2.873965e-09, max 2.874067e-09)
- `period_b03`: mean 2.863867e-09 over 4 seeds (sd 5.736738e-14, 0.0% of mean; min 2.863792e-09, max 2.863923e-09)
- `period_b04`: mean 2.846600e-09 over 4 seeds (sd 3.515015e-14, 0.0% of mean; min 2.846563e-09, max 2.846644e-09)
- `period_b05`: mean 2.846560e-09 over 4 seeds (sd 5.988453e-14, 0.0% of mean; min 2.846471e-09, max 2.846600e-09)
- `period_b06`: mean 2.846549e-09 over 4 seeds (sd 3.157238e-14, 0.0% of mean; min 2.846523e-09, max 2.846590e-09)
- `period_b07`: mean 2.866092e-09 over 4 seeds (sd 5.621142e-14, 0.0% of mean; min 2.866038e-09, max 2.866167e-09)
- `period_b08`: mean 2.874047e-09 over 4 seeds (sd 8.568723e-14, 0.0% of mean; min 2.873938e-09, max 2.874146e-09)
- `period_b09`: mean 2.874078e-09 over 4 seeds (sd 5.983920e-14, 0.0% of mean; min 2.874042e-09, max 2.874167e-09)
- `period_b10`: mean 2.871885e-09 over 4 seeds (sd 3.989283e-14, 0.0% of mean; min 2.871833e-09, max 2.871917e-09)
- `period_b11`: mean 2.846609e-09 over 4 seeds (sd 5.208333e-14, 0.0% of mean; min 2.846542e-09, max 2.846667e-09)
- `period_b12`: mean 2.846589e-09 over 4 seeds (sd 2.621471e-14, 0.0% of mean; min 2.846563e-09, max 2.846625e-09)
- `period_b13`: mean 2.846578e-09 over 4 seeds (sd 5.737052e-14, 0.0% of mean; min 2.846521e-09, max 2.846646e-09)
- `period_b14`: mean 2.858260e-09 over 4 seeds (sd 6.477349e-14, 0.0% of mean; min 2.858208e-09, max 2.858354e-09)
- `period_b15`: mean 2.874036e-09 over 4 seeds (sd 5.208334e-14, 0.0% of mean; min 2.873979e-09, max 2.874104e-09)
- `sigma_1`: mean 1.373725e-11 over 4 seeds (sd 1.626794e-14, 0.1% of mean; min 1.371610e-11, max 1.375437e-11)
- `sigma_2`: mean 2.740722e-11 over 4 seeds (sd 3.458147e-14, 0.1% of mean; min 2.736200e-11, max 2.744279e-11)
- `sigma_4`: mean 5.466931e-11 over 4 seeds (sd 6.742797e-14, 0.1% of mean; min 5.458597e-11, max 5.474802e-11)
- `sigma_8`: mean 1.088484e-10 over 4 seeds (sd 1.405530e-13, 0.1% of mean; min 1.086767e-10, max 1.090101e-10)
- `sigma_16`: mean 2.156734e-10 over 4 seeds (sd 2.819621e-13, 0.1% of mean; min 2.153233e-10, max 2.159779e-10)
- `sigma_32`: mean 4.220611e-10 over 4 seeds (sd 5.519285e-13, 0.1% of mean; min 4.213335e-10, max 4.226512e-10)
- `sigma_64`: mean 7.930570e-10 over 4 seeds (sd 1.018978e-12, 0.1% of mean; min 7.916453e-10, max 7.940791e-10)
- `sigma_128`: mean 1.394383e-09 over 4 seeds (sd 2.086347e-12, 0.1% of mean; min 1.391545e-09, max 1.396142e-09)
- `sigma_startup16_1`: mean 1.541424e-12 over 4 seeds (sd 1.623199e-13, 10.5% of mean; min 1.368896e-12, max 1.731310e-12)
- `sigma_startup16_2`: mean 1.941652e-12 over 4 seeds (sd 1.576471e-13, 8.1% of mean; min 1.732619e-12, max 2.092768e-12)
- `sigma_startup16_4`: mean 2.563337e-12 over 4 seeds (sd 3.527152e-13, 13.8% of mean; min 2.301031e-12, max 3.069090e-12)
- `sigma_startup16_8`: mean 4.646623e-12 over 4 seeds (sd 4.786791e-13, 10.3% of mean; min 4.180266e-12, max 5.246858e-12)
- `i_ring_a`: mean 1.886578e-05 over 4 seeds (sd 1.876481e-11, 0.0% of mean; min 1.886576e-05, max 1.886580e-05)
- `p_active_w`: mean 6.225707e-05 over 4 seeds (sd 6.192345e-11, 0.0% of mean; min 6.225701e-05, max 6.225715e-05)
- `e_per_cycle_j`: mean 1.780306e-13 over 4 seeds (sd 2.900391e-19, 0.0% of mean; min 1.780304e-13, max 1.780310e-13)
- `c_eff_node_f`: mean 3.269616e-15 over 4 seeds (sd 5.326724e-21, 0.0% of mean; min 3.269612e-15, max 3.269624e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-phase-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-buffered --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 3000 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Variant of issue #76's phase-cost experiment on the DR-0016 per-ring liveness digitizer. The comparison it exists for is against sim/tb/ro-ring5-starved-jitter-long/ (the CONTROL: the same ring, device for device, with nothing attached) and against the other variants of this family, which differ from each other only in what clk does. The ring, the injected noise density, the window geometry (opened 256 periods after start-up, spanning 512 periods), the print step and the corner are identical across the whole family and to #51's variants in sim/characterization-array-ring-coupling.md, which is what makes the two experiments directly comparable.
- tclk_per = 1.0007 us (~1 MHz nominal). DR-0003's ratified raw-rate row is "> 1 Mbps sustained at the raw tap" and DR-0012 makes clk a fixed EXTERNAL pin with no divider, so ~1 MHz is the shipped operating point rather than a chosen stimulus -- but it is also not a design constant an attacker cannot move. This deck measures one rate; the two static variants (clk-high / clk-low) bound the endpoints the tap swings between at ANY rate, which is the rate-independent part of the result.
- Every clk timing in this deck is deliberately off the 10 ps grid that this testbench's trnoise() sources place breakpoints on (vn_dt = 1e-11): tclk_del = 5.003 ns, tclk_tr = 0.203 ns, and tstop = 2.600003 us rather than round values. With the tap attached, a PULSE-source or tstop breakpoint that lands exactly on a trnoise breakpoint makes ngspice-46's transient collapse -- "Timestep too small; timestep = 1.25e-24" -- at that instant, reproducibly. The offsets are ~0.3 % of an edge time and ~0.0005 % of a clk period and nothing measured here resolves them. Recorded so the next transient-noise deck with a clocked cell in it does not rediscover the failure.
- The buffer is `ro_buf` out of design/sampler_core.spice -- this tb.json's own design netlist -- instantiated rather than restated, so the deck cannot drift from the cell it claims to measure. It is supplied through its own zero-volt ammeter source (vb1) off the same ideal vsup, exactly as sim/tb/ro-array-coupling-xor-driven-buffered/ does, so i_ring_a/p_active_w keep measuring the RING and stay comparable expression for expression to the control's. In the shipped block the buffers likewise run off the block supply vdd, never off a ring's vddr.
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
