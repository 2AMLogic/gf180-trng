---
record: 2026-11-13-ro-ring5-starved-jitter-redsup-04
date: 2026-11-13T06:39:07Z
status: valid

testbench:
  path: sim/tb/ro-ring5-starved-jitter-long-batch/tb_ro_ring5_starved_jitter_long_batch.sp
  sha: 99f09daa483248d89f1fef87ba0731feb12c6734
netlist:
  path: design/ro_array_sanity.spice
  sha: 969b5873c37a527f15c86e6f5619304c9b7a9d33
repo_commit: fb8f44ee8f1ea0676c8c55e76fe41f5a7e732842-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  klt: 0.9.2.dev885+ge4c446bd91f2 (client; batch backend)
  ngspice: "ngspice-47 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ff
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: -40

analysis:
  type: tran-noise
  tstop: 1.7u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: "per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources, one in series with every stage input"
  runs: 8
seeds: [1, 2, 3, 4, 5, 6, 7, 8]
reproduction:
  scope: deck-and-configuration
  trnoise_waveform_replay: false
  basis: sim/tool-experiments/2026-10-11-ngspice-trnoise-seed-replay/
  decision: DR-0031-transient-noise-reproducibility

raw:
  path: sim/records/raw/2026-11-13-ro-ring5-starved-jitter-redsup-04/
  files:
    - report.json  sha256:feb736880a48a957e28e7e12711f4e22dd7e0c953fa593c8ff8bda255c2b8e1e
    - request.json  sha256:190e7b6e08aefa3859ef64a79eb52cd5ab0f410c4a1b77238de335502a6e99c8
    - stderr.txt  sha256:a7b928d8c0f964238480b7453751714baa3e8f9c8257c705e40544b6b18519db
wall_time: 12.1m
---

## Result

Executed on the batch fleet through `klt sim` (fleet jobs: klt-sim-ec5577a12d13, klt-sim-2f14261e6976, klt-sim-10d6c851a293, klt-sim-18e312e29a6b). Each unit returned the 769 rising mid-supply edge times of the ring output and the charge readings; the figures below are the family's estimators computed from them by `sim/tools/starved_hot_corner.py` (definitions as in `sim/tb/ro-ring5-starved-jitter-long/tb.json`). The `seeds` are unit indices, not noise seeds.

- `period`: mean 1.801135e-09 over 8 seeds (sd 2.300550e-14, 0.0% of mean; min 1.801087e-09, max 1.801164e-09)
- `f_osc`: mean 5.552056e+08 over 8 seeds (sd 7091.6, 0.0% of mean; min 5.551966e+08, max 5.552203e+08)
- `period_startup16`: mean 1.801227e-09 over 8 seeds (sd 1.027703e-13, 0.0% of mean; min 1.801083e-09, max 1.801367e-09)
- `period_b00`: mean 1.801188e-09 over 8 seeds (sd 7.177554e-14, 0.0% of mean; min 1.801080e-09, max 1.801291e-09)
- `period_b01`: mean 1.801152e-09 over 8 seeds (sd 3.428442e-14, 0.0% of mean; min 1.801093e-09, max 1.801197e-09)
- `period_b02`: mean 1.801153e-09 over 8 seeds (sd 6.240484e-14, 0.0% of mean; min 1.801055e-09, max 1.801222e-09)
- `period_b03`: mean 1.801114e-09 over 8 seeds (sd 3.722594e-14, 0.0% of mean; min 1.801037e-09, max 1.801158e-09)
- `period_b04`: mean 1.801131e-09 over 8 seeds (sd 9.859379e-14, 0.0% of mean; min 1.801032e-09, max 1.801294e-09)
- `period_b05`: mean 1.801116e-09 over 8 seeds (sd 6.347141e-14, 0.0% of mean; min 1.801055e-09, max 1.801250e-09)
- `period_b06`: mean 1.801157e-09 over 8 seeds (sd 4.158450e-14, 0.0% of mean; min 1.801113e-09, max 1.801203e-09)
- `period_b07`: mean 1.801134e-09 over 8 seeds (sd 9.317944e-14, 0.0% of mean; min 1.801006e-09, max 1.801286e-09)
- `period_b08`: mean 1.801132e-09 over 8 seeds (sd 4.253131e-14, 0.0% of mean; min 1.801074e-09, max 1.801192e-09)
- `period_b09`: mean 1.801136e-09 over 8 seeds (sd 7.017589e-14, 0.0% of mean; min 1.800994e-09, max 1.801226e-09)
- `period_b10`: mean 1.801134e-09 over 8 seeds (sd 7.755036e-14, 0.0% of mean; min 1.801036e-09, max 1.801264e-09)
- `period_b11`: mean 1.801121e-09 over 8 seeds (sd 6.063295e-14, 0.0% of mean; min 1.801011e-09, max 1.801216e-09)
- `period_b12`: mean 1.801143e-09 over 8 seeds (sd 5.127168e-14, 0.0% of mean; min 1.801088e-09, max 1.801246e-09)
- `period_b13`: mean 1.801134e-09 over 8 seeds (sd 7.854901e-14, 0.0% of mean; min 1.800957e-09, max 1.801209e-09)
- `period_b14`: mean 1.801136e-09 over 8 seeds (sd 6.247511e-14, 0.0% of mean; min 1.801022e-09, max 1.801210e-09)
- `period_b15`: mean 1.801143e-09 over 8 seeds (sd 7.170852e-14, 0.0% of mean; min 1.801034e-09, max 1.801224e-09)
- `sigma_1`: mean 4.892312e-13 over 8 seeds (sd 1.029506e-14, 2.1% of mean; min 4.743071e-13, max 5.027815e-13)
- `sigma_2`: mean 6.460634e-13 over 8 seeds (sd 3.342374e-14, 5.2% of mean; min 5.872484e-13, max 6.968651e-13)
- `sigma_4`: mean 8.898958e-13 over 8 seeds (sd 7.059819e-14, 7.9% of mean; min 7.576244e-13, max 9.654835e-13)
- `sigma_8`: mean 1.259281e-12 over 8 seeds (sd 1.260177e-13, 10.0% of mean; min 1.050969e-12, max 1.442199e-12)
- `sigma_16`: mean 1.761779e-12 over 8 seeds (sd 2.045064e-13, 11.6% of mean; min 1.475182e-12, max 2.121848e-12)
- `sigma_32`: mean 2.376956e-12 over 8 seeds (sd 3.118901e-13, 13.1% of mean; min 2.063682e-12, max 3.061179e-12)
- `sigma_64`: mean 3.197066e-12 over 8 seeds (sd 4.091724e-13, 12.8% of mean; min 2.728340e-12, max 3.878388e-12)
- `sigma_128`: mean 4.380797e-12 over 8 seeds (sd 1.023351e-12, 23.4% of mean; min 3.103202e-12, max 6.019581e-12)
- `sigma_startup16_1`: mean 4.504013e-13 over 8 seeds (sd 9.739478e-14, 21.6% of mean; min 3.382641e-13, max 6.536595e-13)
- `sigma_startup16_2`: mean 5.525738e-13 over 8 seeds (sd 1.136703e-13, 20.6% of mean; min 3.792918e-13, max 7.278946e-13)
- `sigma_startup16_4`: mean 6.863919e-13 over 8 seeds (sd 2.126966e-13, 31.0% of mean; min 4.943618e-13, max 1.146258e-12)
- `sigma_startup16_8`: mean 8.962502e-13 over 8 seeds (sd 2.334880e-13, 26.1% of mean; min 4.346517e-13, max 1.175152e-12)
- `i_ring_a`: mean 2.340593e-05 over 8 seeds (sd 1.431576e-10, 0.0% of mean; min 2.340573e-05, max 2.340615e-05)
- `p_active_w`: mean 6.951561e-05 over 8 seeds (sd 4.251781e-10, 0.0% of mean; min 6.951500e-05, max 6.951628e-05)
- `e_per_cycle_j`: mean 1.252070e-13 over 8 seeds (sd 9.534032e-19, 0.0% of mean; min 1.252048e-13, max 1.252079e-13)
- `c_eff_node_f`: mean 2.838871e-15 over 8 seeds (sd 2.161691e-20, 0.0% of mean; min 2.838823e-15, max 2.838892e-15)
- `vsup_v`: mean 2.97 over 8 seeds (sd 0.000000e+00, 0.0% of mean; min 2.97, max 2.97)

Runs: 8 of 8 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

The request that produced this record carried 2 supplies x 8 units, so the fleet job id(s) above are those of the whole request; `raw/report.json` holds only this record's units, and `raw/request.json` is the whole request.

## How to reproduce

```sh
python3 sim/tools/starved_hot_corner.py emit --check
python3 sim/tools/starved_hot_corner.py run --outdir DIR --backend batch --grid ring5-redsup-ff-40
python3 sim/tools/starved_hot_corner.py ingest --report DIR/ring5-redsup-ff-40.report.json --grid ring5-redsup-ff-40
```

These commands replay the deck and configuration. They do not reproduce the `trnoise` waveforms: on the ngspice-46 build measured in `sim/tool-experiments/2026-10-11-ngspice-trnoise-seed-replay/` a re-run draws a fresh noise realization, so its measured values will differ from the ones above. Exact waveform replay is not claimed. See `spec/decision-records/DR-0031-transient-noise-reproducibility.md`.

## Caveats

- Single corner (ff / 2.97 V / -40 C). Says nothing about any other corner.
- Same circuit and stimulus as `sim/tb/ro-ring5-starved-jitter-long/`, but the estimators are computed from fleet-measured edge times rather than inside ngspice; edge times come from `.meas ... when` cards, interpolated as in the family's own bench.
- `vsup_v` is the mean of v(vsup) over the whole run (the supply is an ideal DC source), not over the measurement window.
- The PDK model content on the fleet is the one named in `pdk:` above, which may differ from the PDK of the family's earlier records; compare `pdk:` lines before pooling across records.

---

Written by `sim/tools/starved_hot_corner.py ingest`. Append-only: never edit or delete this file -- a re-run or correction mints a new record and points back here via `supersedes` (see `sim/README.md`).
