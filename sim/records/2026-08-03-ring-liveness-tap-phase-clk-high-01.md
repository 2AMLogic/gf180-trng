---
record: 2026-08-03-ring-liveness-tap-phase-clk-high-01
date: 2026-08-03T05:13:31Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-phase-clk-high/tb_ring_liveness_tap_phase_clk_high.sp
  sha: 22cc01b407003a408bd2c2eab3b733111a8f239e
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
  tstop: 2.400003u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources, one in series with every stage input
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-03-ring-liveness-tap-phase-clk-high-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:be6e72567f37405aec2454cfc9ca17c1cd737e27ce51cc5c3c37c26b76f0e89b
    - tt_27c_3.30v-run0.log  sha256:e10fb487ecf0bd8d3ae782d1844776c6dc12a891f3cbd477af41cf2e149958fa
    - tt_27c_3.30v-run1.spice  sha256:461fd9b86a7c9d844ac4658d90b6ee91aaec0d22fde66e9574465f81edecd755
    - tt_27c_3.30v-run1.log  sha256:784bc3d85465b9443aba3fe582d49bce3e0661c7b809863875f1885ee506ca50
    - tt_27c_3.30v-run2.spice  sha256:53da3dce0434f4a52acfe72e414f63f236f95d9f8e8ef1d476af5cb22224ab6d
    - tt_27c_3.30v-run2.log  sha256:20d1b66198bd10a4b979c11c60272ae623a29f11aad8de1f30650a4d994e6107
    - tt_27c_3.30v-run3.spice  sha256:0ac7f114bbce1554b7d147cad9c7ade3dc96412f4825e569f505327f86a78945
    - tt_27c_3.30v-run3.log  sha256:96f2fa85f4786a271f812ef81b4e913c914e2ac7b1e56b60bcba39dfed1871e6
wall_time: 15.7m
---

## Result

- `period`: mean 2.747190e-09 over 4 seeds (sd 3.551943e-14, 0.0% of mean; min 2.747146e-09, max 2.747220e-09)
- `f_osc`: mean 3.640083e+08 over 4 seeds (sd 4706.42, 0.0% of mean; min 3.640044e+08, max 3.640141e+08)
- `period_startup16`: mean 2.747152e-09 over 4 seeds (sd 1.078198e-13, 0.0% of mean; min 2.747044e-09, max 2.747257e-09)
- `period_b00`: mean 2.747186e-09 over 4 seeds (sd 6.730005e-14, 0.0% of mean; min 2.747094e-09, max 2.747255e-09)
- `period_b01`: mean 2.747180e-09 over 4 seeds (sd 5.104520e-14, 0.0% of mean; min 2.747104e-09, max 2.747213e-09)
- `period_b02`: mean 2.747229e-09 over 4 seeds (sd 3.535532e-14, 0.0% of mean; min 2.747196e-09, max 2.747271e-09)
- `period_b03`: mean 2.747184e-09 over 4 seeds (sd 5.520833e-14, 0.0% of mean; min 2.747115e-09, max 2.747240e-09)
- `period_b04`: mean 2.747242e-09 over 4 seeds (sd 6.060496e-14, 0.0% of mean; min 2.747169e-09, max 2.747298e-09)
- `period_b05`: mean 2.747196e-09 over 4 seeds (sd 4.605378e-14, 0.0% of mean; min 2.747152e-09, max 2.747248e-09)
- `period_b06`: mean 2.747191e-09 over 4 seeds (sd 6.079858e-14, 0.0% of mean; min 2.747135e-09, max 2.747277e-09)
- `period_b07`: mean 2.747206e-09 over 4 seeds (sd 6.404060e-14, 0.0% of mean; min 2.747123e-09, max 2.747258e-09)
- `period_b08`: mean 2.747161e-09 over 4 seeds (sd 5.737053e-14, 0.0% of mean; min 2.747104e-09, max 2.747229e-09)
- `period_b09`: mean 2.747177e-09 over 4 seeds (sd 1.134731e-13, 0.0% of mean; min 2.747083e-09, max 2.747333e-09)
- `period_b10`: mean 2.747177e-09 over 4 seeds (sd 6.250001e-14, 0.0% of mean; min 2.747104e-09, max 2.747229e-09)
- `period_b11`: mean 2.747167e-09 over 4 seeds (sd 7.013544e-14, 0.0% of mean; min 2.747125e-09, max 2.747271e-09)
- `period_b12`: mean 2.747198e-09 over 4 seeds (sd 2.083335e-14, 0.0% of mean; min 2.747187e-09, max 2.747229e-09)
- `period_b13`: mean 2.747203e-09 over 4 seeds (sd 7.090476e-14, 0.0% of mean; min 2.747104e-09, max 2.747271e-09)
- `period_b14`: mean 2.747203e-09 over 4 seeds (sd 1.053749e-13, 0.0% of mean; min 2.747083e-09, max 2.747333e-09)
- `period_b15`: mean 2.747208e-09 over 4 seeds (sd 9.771697e-14, 0.0% of mean; min 2.747104e-09, max 2.747333e-09)
- `sigma_1`: mean 6.404262e-13 over 4 seeds (sd 2.089173e-14, 3.3% of mean; min 6.162362e-13, max 6.631364e-13)
- `sigma_2`: mean 7.677772e-13 over 4 seeds (sd 1.787136e-14, 2.3% of mean; min 7.464337e-13, max 7.896121e-13)
- `sigma_4`: mean 9.775655e-13 over 4 seeds (sd 2.666466e-14, 2.7% of mean; min 9.390916e-13, max 9.974572e-13)
- `sigma_8`: mean 1.301970e-12 over 4 seeds (sd 2.181832e-14, 1.7% of mean; min 1.271003e-12, max 1.320756e-12)
- `sigma_16`: mean 1.735083e-12 over 4 seeds (sd 6.278837e-14, 3.6% of mean; min 1.669536e-12, max 1.792349e-12)
- `sigma_32`: mean 2.390115e-12 over 4 seeds (sd 2.020846e-13, 8.5% of mean; min 2.119931e-12, max 2.568113e-12)
- `sigma_64`: mean 3.430325e-12 over 4 seeds (sd 5.345702e-13, 15.6% of mean; min 2.851438e-12, max 4.085393e-12)
- `sigma_128`: mean 4.831631e-12 over 4 seeds (sd 1.871584e-12, 38.7% of mean; min 3.128451e-12, max 7.252149e-12)
- `sigma_startup16_1`: mean 4.858769e-13 over 4 seeds (sd 5.848235e-14, 12.0% of mean; min 4.069802e-13, max 5.337477e-13)
- `sigma_startup16_2`: mean 5.691565e-13 over 4 seeds (sd 9.171090e-14, 16.1% of mean; min 4.666068e-13, max 6.739051e-13)
- `sigma_startup16_4`: mean 7.396713e-13 over 4 seeds (sd 1.115484e-13, 15.1% of mean; min 6.121986e-13, max 8.546527e-13)
- `sigma_startup16_8`: mean 1.029608e-12 over 4 seeds (sd 2.482910e-13, 24.1% of mean; min 6.723277e-13, max 1.220579e-12)
- `i_ring_a`: mean 1.895191e-05 over 4 seeds (sd 1.159872e-10, 0.0% of mean; min 1.895181e-05, max 1.895207e-05)
- `p_active_w`: mean 6.254131e-05 over 4 seeds (sd 3.827565e-10, 0.0% of mean; min 6.254096e-05, max 6.254183e-05)
- `e_per_cycle_j`: mean 1.718129e-13 over 4 seeds (sd 1.215385e-18, 0.0% of mean; min 1.718115e-13, max 1.718141e-13)
- `c_eff_node_f`: mean 3.155425e-15 over 4 seeds (sd 2.232117e-20, 0.0% of mean; min 3.155400e-15, max 3.155447e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-phase-clk-high --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clk-high --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clk-high --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --timeout 3000 --no-write
python3 sim/run_corners.py ring-liveness-tap-phase-clk-high --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --timeout 3000 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Variant of issue #76's phase-cost experiment on the DR-0016 per-ring liveness digitizer. The comparison it exists for is against sim/tb/ro-ring5-starved-jitter-long/ (the CONTROL: the same ring, device for device, with nothing attached) and against the other variants of this family, which differ from each other only in what clk does. The ring, the injected noise density, the window geometry (opened 256 periods after start-up, spanning 512 periods), the print step and the corner are identical across the whole family and to #51's variants in sim/characterization-array-ring-coupling.md, which is what makes the two experiments directly comparable.
- Topology note (PR #82). This variant puts the digitizer's d input DIRECTLY on the ring node -- the arrangement design/sampler_core.spice shipped when issue #76 was filed, and the one #76 indicts. Since #82 the shipped netlist interposes a per-ring output buffer (xb1: rn1 -> ro1) and the digitizer taps the buffer output, which is what sim/tb/ring-liveness-tap-phase-buffered/ measures. This deck is therefore the PRE-#82 topology, kept and measured because #82 adopted the buffer on combiner-path evidence (#75) and never measured the digitizer path -- so without this row there is no before to compare the after against. design/sampler_core.spice is named here only as the source of the sampler_dff (and, in the buffered variant, ro_buf) cell definitions; every device in the ring is instantiated by the deck itself.
- clk and rst_n are DC sources: this deck contains no edge anywhere after start-up, which is what makes it a static reference. It measures ONE of the two states the clocked tap alternates between and is not on its own a statement about the shipped, clocked arrangement -- sim/tb/ring-liveness-tap-phase-clocked/ is.
- sigma_* here is NOT a jitter measurement if what it captures is deterministic. The estimator is the control's, but it measures the spread of period-to-period increments from whatever cause, and a load modulation locked to clk enters it exactly as noise would. The seed spread and the accumulation exponent reported alongside are what tell the two apart, and no entropy claim may be built on this record's sigma either way.
- The ring is 5-stage, where the shipped array's rings (design/ro_array_core.spice, ro_ring11) have 11. That is deliberate: #51's whole ladder is on this 5-stage ring at this corner and window, so this family drops straight into it. The tap loads exactly ONE ring node either way, and one node is a larger fraction of a 5-stage ring's delay than of an 11-stage ring's, so a fractional period or phase effect measured here OVER-states the shipped ring's by roughly 11/5.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used, so this family has a like-for-like row against #51's variants' own startup block. They are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.
- The digitizer is supplied from vsup directly rather than through the ring's sense source, so its own switching current is outside i_ring_a/p_active_w. Its own power is not re-measured here -- sim/tb/ring-liveness-tap-power/ measures it across three PVT points -- and p_active_w/e_per_cycle_j/c_eff_node_f here are the RING's, comparable expression for expression to the control's.
- rst_n is held at vdd for the whole run, so the digitizer is out of reset throughout and contributes no reset edge. DR-0014's gated reset behaviour is measured by sim/tb/sampler-dff-reset-clocked/ and is not what this deck is about.
- Pre-layout, schematic-derived netlist (design/sampler_core.spice), no extracted parasitics. Layout adds coupling paths between a clocked cell and a ring node; it removes none.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
