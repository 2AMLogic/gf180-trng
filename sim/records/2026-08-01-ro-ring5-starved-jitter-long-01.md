---
record: 2026-08-01-ro-ring5-starved-jitter-long-01
date: 2026-08-01T17:15:56Z
status: valid

testbench:
  path: sim/tb/ro-ring5-starved-jitter-long/tb_ro_ring5_starved_jitter_long.sp
  sha: 8ef7522612bb4242427416690db5e960b5ca153f
netlist:
  path: design/ro_array_sanity.spice
  sha: a05e5068d79a74012d22d80a28785c926c8786ce
repo_commit: 78a6ce1c4627d44fe7af63cb321ea0014b7f4932

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
  tstop: 2.4u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step -- measured 1.3 solver points per ps of simulated time at tt/27 C/3.30 V)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources, one in series with every stage input
  runs: 8
seeds: [1, 2, 3, 4, 5, 6, 7, 8]

raw:
  path: sim/records/raw/2026-08-01-ro-ring5-starved-jitter-long-01/
  files:
    - ss_-40c_3.63v-run0.spice  sha256:4100cbd671e793e2eca42f1af097ab4bd98030d1de7a24389b2daef1fd3f417f
    - ss_-40c_3.63v-run0.log  sha256:468c5f665d04f72fe5ad83c5aa8318c75be14840a54d9e7c94b3152093e6062f
    - ss_-40c_3.63v-run1.spice  sha256:4b37e50ee7e6726005d013fa5e521833b5a6039ca21a3358ee3833c21973bba0
    - ss_-40c_3.63v-run1.log  sha256:be5aedc0f1b767f1f42a6a2fa7149c8c2ca9425db79b3096aeb13a1c3e213c24
    - ss_-40c_3.63v-run2.spice  sha256:3fd381675b4ff984154931b7a0b1adbec89df1010ff3c123ce5c2d4fd95b1a2b
    - ss_-40c_3.63v-run2.log  sha256:35c84012e8860562fc64b5350c25c4e8914082a46f0c7e249eeb21d0c5b8e901
    - ss_-40c_3.63v-run3.spice  sha256:2743aa79502cab859a71802a1f8ab97155c8091d472bd8cc3c9309efaf6c7c14
    - ss_-40c_3.63v-run3.log  sha256:d05a1b6b7d412c82b07ffe05ea623c197b331b669c3451b1694daa9750cde364
    - ss_-40c_3.63v-run4.spice  sha256:7c6ca83ada059ab08562af37f519a36ecd25472a8f3ba5f144109d62011534a1
    - ss_-40c_3.63v-run4.log  sha256:ed72bc471cf6b4f8ab4c277ef5c85ab6a396a88e9bc5a236c5746411d91f9c1a
    - ss_-40c_3.63v-run5.spice  sha256:41b12295efd23e5cead422e1b4430888243b59c57384d63a9f1fcdbd904c847b
    - ss_-40c_3.63v-run5.log  sha256:b4cec8aa46eaf8498e54a684b6c8d26a71fb411ec1a15b032e05e957f4d1815a
    - ss_-40c_3.63v-run6.spice  sha256:161e11a9ee583c7ac65fa4959bd00ad09e25c50af1bccf4516cf0fa63e6c601f
    - ss_-40c_3.63v-run6.log  sha256:8aac34ab2f9461431a0236899085d28dfd7eaea2593d656f4d92cfe63ff5de2f
    - ss_-40c_3.63v-run7.spice  sha256:0a110ad18a96a8f046a3a33967f426fb1900fb52ddc3a5c6d6d2ffe2d976885e
    - ss_-40c_3.63v-run7.log  sha256:3ad148c4ebf91c1f3a12e4d7010825dbc535e62cce208ae20ae600baa98d2c5c
wall_time: 887.3m
---

## Result

- `period`: mean 2.279141e-09 over 8 seeds (sd 1.027681e-14, 0.0% of mean; min 2.279125e-09, max 2.279158e-09)
- `f_osc`: mean 4.387618e+08 over 8 seeds (sd 1978.4, 0.0% of mean; min 4.387585e+08, max 4.387648e+08)
- `period_startup16`: mean 2.279099e-09 over 8 seeds (sd 7.026268e-14, 0.0% of mean; min 2.278952e-09, max 2.279165e-09)
- `period_b00`: mean 2.279118e-09 over 8 seeds (sd 6.155996e-14, 0.0% of mean; min 2.279009e-09, max 2.279196e-09)
- `period_b01`: mean 2.279133e-09 over 8 seeds (sd 5.286613e-14, 0.0% of mean; min 2.279063e-09, max 2.279227e-09)
- `period_b02`: mean 2.279128e-09 over 8 seeds (sd 4.238865e-14, 0.0% of mean; min 2.279052e-09, max 2.279183e-09)
- `period_b03`: mean 2.279130e-09 over 8 seeds (sd 2.327739e-14, 0.0% of mean; min 2.279098e-09, max 2.279158e-09)
- `period_b04`: mean 2.279149e-09 over 8 seeds (sd 2.385784e-14, 0.0% of mean; min 2.279100e-09, max 2.279175e-09)
- `period_b05`: mean 2.279110e-09 over 8 seeds (sd 3.802542e-14, 0.0% of mean; min 2.279046e-09, max 2.279156e-09)
- `period_b06`: mean 2.279142e-09 over 8 seeds (sd 4.135300e-14, 0.0% of mean; min 2.279087e-09, max 2.279223e-09)
- `period_b07`: mean 2.279139e-09 over 8 seeds (sd 4.923459e-14, 0.0% of mean; min 2.279063e-09, max 2.279215e-09)
- `period_b08`: mean 2.279147e-09 over 8 seeds (sd 3.678213e-14, 0.0% of mean; min 2.279073e-09, max 2.279183e-09)
- `period_b09`: mean 2.279141e-09 over 8 seeds (sd 5.046826e-14, 0.0% of mean; min 2.279079e-09, max 2.279229e-09)
- `period_b10`: mean 2.279143e-09 over 8 seeds (sd 3.766087e-14, 0.0% of mean; min 2.279083e-09, max 2.279208e-09)
- `period_b11`: mean 2.279148e-09 over 8 seeds (sd 4.514842e-14, 0.0% of mean; min 2.279063e-09, max 2.279208e-09)
- `period_b12`: mean 2.279141e-09 over 8 seeds (sd 2.670291e-14, 0.0% of mean; min 2.279104e-09, max 2.279187e-09)
- `period_b13`: mean 2.279161e-09 over 8 seeds (sd 5.193430e-14, 0.0% of mean; min 2.279104e-09, max 2.279229e-09)
- `period_b14`: mean 2.279148e-09 over 8 seeds (sd 6.534924e-14, 0.0% of mean; min 2.279083e-09, max 2.279271e-09)
- `period_b15`: mean 2.279120e-09 over 8 seeds (sd 3.100097e-14, 0.0% of mean; min 2.279063e-09, max 2.279146e-09)
- `sigma_1`: mean 5.172396e-13 over 8 seeds (sd 2.145094e-14, 4.1% of mean; min 4.884889e-13, max 5.455924e-13)
- `sigma_2`: mean 5.998058e-13 over 8 seeds (sd 1.632249e-14, 2.7% of mean; min 5.778548e-13, max 6.237569e-13)
- `sigma_4`: mean 7.289961e-13 over 8 seeds (sd 2.858191e-14, 3.9% of mean; min 6.961898e-13, max 7.764914e-13)
- `sigma_8`: mean 9.171196e-13 over 8 seeds (sd 6.255582e-14, 6.8% of mean; min 8.288081e-13, max 1.036343e-12)
- `sigma_16`: mean 1.216040e-12 over 8 seeds (sd 1.461655e-13, 12.0% of mean; min 1.015087e-12, max 1.454858e-12)
- `sigma_32`: mean 1.682785e-12 over 8 seeds (sd 2.079065e-13, 12.4% of mean; min 1.479392e-12, max 1.993842e-12)
- `sigma_64`: mean 2.361661e-12 over 8 seeds (sd 4.394516e-13, 18.6% of mean; min 1.834344e-12, max 3.243312e-12)
- `sigma_128`: mean 3.447497e-12 over 8 seeds (sd 1.029751e-12, 29.9% of mean; min 2.051139e-12, max 5.285289e-12)
- `sigma_startup16_1`: mean 3.876807e-13 over 8 seeds (sd 6.844313e-14, 17.7% of mean; min 2.687700e-13, max 5.150632e-13)
- `sigma_startup16_2`: mean 4.695724e-13 over 8 seeds (sd 1.132036e-13, 24.1% of mean; min 3.206014e-13, max 6.997431e-13)
- `sigma_startup16_4`: mean 6.215330e-13 over 8 seeds (sd 1.598545e-13, 25.7% of mean; min 4.106311e-13, max 8.339896e-13)
- `sigma_startup16_8`: mean 8.989514e-13 over 8 seeds (sd 2.744925e-13, 30.5% of mean; min 5.351590e-13, max 1.350954e-12)
- `i_ring_a`: mean 2.247133e-05 over 8 seeds (sd 4.838840e-11, 0.0% of mean; min 2.247127e-05, max 2.247140e-05)
- `p_active_w`: mean 8.157094e-05 over 8 seeds (sd 1.756498e-10, 0.0% of mean; min 8.157070e-05, max 8.157118e-05)
- `e_per_cycle_j`: mean 1.859117e-13 over 8 seeds (sd 5.595390e-19, 0.0% of mean; min 1.859109e-13, max 1.859125e-13)
- `c_eff_node_f`: mean 2.821781e-15 over 8 seeds (sd 8.492721e-21, 0.0% of mean; min 2.821770e-15, max 2.821794e-15)
- `vsup_v`: mean 3.63 over 8 seeds (sd 0, 0.0% of mean; min 3.63, max 3.63)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 5 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 6 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 7 --no-write
python3 sim/run_corners.py ro-ring5-starved-jitter-long --corners ss --temps -40 --supply 3.63 --supply-tol 0 --seeds 8 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 8); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_sanity.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
