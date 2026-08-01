---
record: 2026-08-01-ro-ring5-starved-jitter-long-02
date: 2026-08-01T17:16:03Z
status: valid

testbench:
  path: sim/tb/ro-ring5-starved-jitter-long/tb_ro_ring5_starved_jitter_long.sp
  sha: 8ef7522612bb4242427416690db5e960b5ca153f
netlist:
  path: design/ro_array_sanity.spice
  sha: a05e5068d79a74012d22d80a28785c926c8786ce
repo_commit: 78a6ce1c4627d44fe7af63cb321ea0014b7f4932-dirty

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
  tstop: 2.4u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step -- measured 1.3 solver points per ps of simulated time at tt/27 C/3.30 V)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources, one in series with every stage input
  runs: 8
seeds: [1, 2, 3, 4, 5, 6, 7, 8]

raw:
  path: sim/records/raw/2026-08-01-ro-ring5-starved-jitter-long-02/
  files:
    - tt_27c_3.30v-run0.spice  sha256:6deefadbe127198c9b42c5a2732a5989da8307b2df77ea032c7414b7c0e05bf3
    - tt_27c_3.30v-run0.log  sha256:134c3a311debea8f3ab8abc13452363c9670f603c454dff4c7b0f6e424399ff1
    - tt_27c_3.30v-run1.spice  sha256:554a66932c86e4ea8eead84b7741ec7baad4e9cde4885215d91a2055cc670a6d
    - tt_27c_3.30v-run1.log  sha256:a933a7066738114ecf11aca1e5ca58dd3cfdb0c93fc0eedef3911ef89435a22e
    - tt_27c_3.30v-run2.spice  sha256:0882dddac5d7b3ff3bf79c97226d94e7e2401b9a7bbd1ab7ade5238b6131193b
    - tt_27c_3.30v-run2.log  sha256:bdef5f9d1bde6df694eb61a64fb3c0ee41fc50475083ae97b4e1363e40703531
    - tt_27c_3.30v-run3.spice  sha256:883df772f738c2bfae6bd497364e3b4be286a4d9dfdab22d2bfcda871bafa090
    - tt_27c_3.30v-run3.log  sha256:74b5ce4f8c62f8bbc00e3a87aa69461550e73f85a73f90b49861a7601ae93830
    - tt_27c_3.30v-run4.spice  sha256:aa8a4a35ce417e1f16c73b55cadc29f6848cab43f8cd4b1f8084811c40d9bef0
    - tt_27c_3.30v-run4.log  sha256:a65661d2835b8a41335c0548b7034ba3953bac15ba80146124741dd63bcf4854
    - tt_27c_3.30v-run5.spice  sha256:48e1aa6ab5bbd186d58129bb0fb8c68cd871e44c96e4e7dc0105d6409947404a
    - tt_27c_3.30v-run5.log  sha256:8aa0f4b73fa4b4b4f152e37caf192a67ea11c69da9bf1954aef3fdfb311ea78a
    - tt_27c_3.30v-run6.spice  sha256:5946ff8e43c2ab0b704ee250b13440a9067ba808bce7c76ff23fea6fcd64a52c
    - tt_27c_3.30v-run6.log  sha256:e4a331c4b8f0f425ea53f340876b478ab31620d33ccedd69418eb6d6fd70f57a
    - tt_27c_3.30v-run7.spice  sha256:fe48566f79665954790b8e0be94297e95d84ce615f3cfd153ce0c2dc01f3fe5d
    - tt_27c_3.30v-run7.log  sha256:7e2bc2790a6bafd587d44c297333388693e69eb9b4868a4921bd730a58570403
wall_time: 906.2m
---

## Result

- `period`: mean 2.563509e-09 over 8 seeds (sd 2.030063e-14, 0.0% of mean; min 2.563476e-09, max 2.563530e-09)
- `f_osc`: mean 3.900903e+08 over 8 seeds (sd 3089.17, 0.0% of mean; min 3.900872e+08, max 3.900954e+08)
- `period_startup16`: mean 2.563480e-09 over 8 seeds (sd 1.235876e-13, 0.0% of mean; min 2.563207e-09, max 2.563587e-09)
- `period_b00`: mean 2.563490e-09 over 8 seeds (sd 8.174902e-14, 0.0% of mean; min 2.563362e-09, max 2.563626e-09)
- `period_b01`: mean 2.563488e-09 over 8 seeds (sd 4.020886e-14, 0.0% of mean; min 2.563429e-09, max 2.563535e-09)
- `period_b02`: mean 2.563516e-09 over 8 seeds (sd 6.196137e-14, 0.0% of mean; min 2.563431e-09, max 2.563579e-09)
- `period_b03`: mean 2.563494e-09 over 8 seeds (sd 9.601068e-14, 0.0% of mean; min 2.563369e-09, max 2.563640e-09)
- `period_b04`: mean 2.563503e-09 over 8 seeds (sd 5.945978e-14, 0.0% of mean; min 2.563398e-09, max 2.563575e-09)
- `period_b05`: mean 2.563480e-09 over 8 seeds (sd 6.281604e-14, 0.0% of mean; min 2.563402e-09, max 2.563560e-09)
- `period_b06`: mean 2.563490e-09 over 8 seeds (sd 5.193430e-14, 0.0% of mean; min 2.563406e-09, max 2.563533e-09)
- `period_b07`: mean 2.563541e-09 over 8 seeds (sd 6.726331e-14, 0.0% of mean; min 2.563452e-09, max 2.563650e-09)
- `period_b08`: mean 2.563469e-09 over 8 seeds (sd 5.138748e-14, 0.0% of mean; min 2.563427e-09, max 2.563585e-09)
- `period_b09`: mean 2.563477e-09 over 8 seeds (sd 6.904025e-14, 0.0% of mean; min 2.563354e-09, max 2.563542e-09)
- `period_b10`: mean 2.563549e-09 over 8 seeds (sd 6.193945e-14, 0.0% of mean; min 2.563458e-09, max 2.563646e-09)
- `period_b11`: mean 2.563523e-09 over 8 seeds (sd 5.504947e-14, 0.0% of mean; min 2.563417e-09, max 2.563604e-09)
- `period_b12`: mean 2.563557e-09 over 8 seeds (sd 3.477179e-14, 0.0% of mean; min 2.563521e-09, max 2.563625e-09)
- `period_b13`: mean 2.563492e-09 over 8 seeds (sd 5.885976e-14, 0.0% of mean; min 2.563396e-09, max 2.563583e-09)
- `period_b14`: mean 2.563513e-09 over 8 seeds (sd 7.125010e-14, 0.0% of mean; min 2.563417e-09, max 2.563604e-09)
- `period_b15`: mean 2.563492e-09 over 8 seeds (sd 7.790149e-14, 0.0% of mean; min 2.563396e-09, max 2.563604e-09)
- `sigma_1`: mean 6.405461e-13 over 8 seeds (sd 2.467451e-14, 3.9% of mean; min 5.951761e-13, max 6.730902e-13)
- `sigma_2`: mean 7.657996e-13 over 8 seeds (sd 3.257302e-14, 4.3% of mean; min 7.006122e-13, max 8.023436e-13)
- `sigma_4`: mean 9.808594e-13 over 8 seeds (sd 4.591804e-14, 4.7% of mean; min 9.161997e-13, max 1.043232e-12)
- `sigma_8`: mean 1.299374e-12 over 8 seeds (sd 8.174369e-14, 6.3% of mean; min 1.204337e-12, max 1.427431e-12)
- `sigma_16`: mean 1.792947e-12 over 8 seeds (sd 1.160988e-13, 6.5% of mean; min 1.653641e-12, max 1.969430e-12)
- `sigma_32`: mean 2.423352e-12 over 8 seeds (sd 1.825705e-13, 7.5% of mean; min 2.101129e-12, max 2.652950e-12)
- `sigma_64`: mean 3.372290e-12 over 8 seeds (sd 3.556844e-13, 10.5% of mean; min 2.942652e-12, max 4.031527e-12)
- `sigma_128`: mean 4.784211e-12 over 8 seeds (sd 1.359038e-12, 28.4% of mean; min 2.706203e-12, max 7.218494e-12)
- `sigma_startup16_1`: mean 5.873713e-13 over 8 seeds (sd 9.417280e-14, 16.0% of mean; min 4.684697e-13, max 7.291098e-13)
- `sigma_startup16_2`: mean 7.980676e-13 over 8 seeds (sd 7.857955e-14, 9.8% of mean; min 7.083672e-13, max 9.042797e-13)
- `sigma_startup16_4`: mean 1.028366e-12 over 8 seeds (sd 1.708028e-13, 16.6% of mean; min 7.207194e-13, max 1.256995e-12)
- `sigma_startup16_8`: mean 1.521339e-12 over 8 seeds (sd 4.795421e-13, 31.5% of mean; min 7.479814e-13, max 2.097182e-12)
- `i_ring_a`: mean 1.925253e-05 over 8 seeds (sd 8.891167e-11, 0.0% of mean; min 1.925244e-05, max 1.925266e-05)
- `p_active_w`: mean 6.353335e-05 over 8 seeds (sd 2.934078e-10, 0.0% of mean; min 6.353305e-05, max 6.353378e-05)
- `e_per_cycle_j`: mean 1.628683e-13 over 8 seeds (sd 6.340874e-19, 0.0% of mean; min 1.628673e-13, max 1.628689e-13)
- `c_eff_node_f`: mean 2.991154e-15 over 8 seeds (sd 1.164534e-20, 0.0% of mean; min 2.991135e-15, max 2.991165e-15)
- `vsup_v`: mean 3.3 over 8 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 5 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 6 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 7 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 8 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 8); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_sanity.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
