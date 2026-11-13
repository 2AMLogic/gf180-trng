---
record: 2026-11-13-ro-ring5-starved-jitter-redsup-03
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
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-11-13-ro-ring5-starved-jitter-redsup-03/
  files:
    - report.json  sha256:a06f25111606de573799dedc6a402e5e71c1c3bf84697df40bec8fd9d344b9fe
    - request.json  sha256:190e7b6e08aefa3859ef64a79eb52cd5ab0f410c4a1b77238de335502a6e99c8
    - stderr.txt  sha256:a7b928d8c0f964238480b7453751714baa3e8f9c8257c705e40544b6b18519db
wall_time: 12.1m
---

## Result

Executed on the batch fleet through `klt sim` (fleet jobs: klt-sim-ec5577a12d13, klt-sim-2f14261e6976, klt-sim-10d6c851a293, klt-sim-18e312e29a6b). Each unit returned the 769 rising mid-supply edge times of the ring output and the charge readings; the figures below are the family's estimators computed from them by `sim/tools/starved_hot_corner.py` (definitions as in `sim/tb/ro-ring5-starved-jitter-long/tb.json`). The `seeds` are unit indices, not noise seeds.

- `period`: mean 1.626782e-09 over 8 seeds (sd 1.794807e-14, 0.0% of mean; min 1.626763e-09, max 1.626817e-09)
- `f_osc`: mean 6.147104e+08 over 8 seeds (sd 6781.97, 0.0% of mean; min 6.146974e+08, max 6.147176e+08)
- `period_startup16`: mean 1.626785e-09 over 8 seeds (sd 8.279816e-14, 0.0% of mean; min 1.626644e-09, max 1.626901e-09)
- `period_b00`: mean 1.626773e-09 over 8 seeds (sd 2.443209e-14, 0.0% of mean; min 1.626736e-09, max 1.626817e-09)
- `period_b01`: mean 1.626788e-09 over 8 seeds (sd 5.865428e-14, 0.0% of mean; min 1.626721e-09, max 1.626885e-09)
- `period_b02`: mean 1.626755e-09 over 8 seeds (sd 4.025234e-14, 0.0% of mean; min 1.626708e-09, max 1.626813e-09)
- `period_b03`: mean 1.626770e-09 over 8 seeds (sd 5.278262e-14, 0.0% of mean; min 1.626670e-09, max 1.626856e-09)
- `period_b04`: mean 1.626796e-09 over 8 seeds (sd 3.851386e-14, 0.0% of mean; min 1.626727e-09, max 1.626842e-09)
- `period_b05`: mean 1.626782e-09 over 8 seeds (sd 5.814445e-14, 0.0% of mean; min 1.626707e-09, max 1.626866e-09)
- `period_b06`: mean 1.626767e-09 over 8 seeds (sd 3.813301e-14, 0.0% of mean; min 1.626723e-09, max 1.626819e-09)
- `period_b07`: mean 1.626760e-09 over 8 seeds (sd 4.271192e-14, 0.0% of mean; min 1.626713e-09, max 1.626851e-09)
- `period_b08`: mean 1.626769e-09 over 8 seeds (sd 8.889377e-14, 0.0% of mean; min 1.626664e-09, max 1.626945e-09)
- `period_b09`: mean 1.626782e-09 over 8 seeds (sd 5.322455e-14, 0.0% of mean; min 1.626701e-09, max 1.626852e-09)
- `period_b10`: mean 1.626793e-09 over 8 seeds (sd 4.754426e-14, 0.0% of mean; min 1.626725e-09, max 1.626871e-09)
- `period_b11`: mean 1.626786e-09 over 8 seeds (sd 5.846773e-14, 0.0% of mean; min 1.626689e-09, max 1.626869e-09)
- `period_b12`: mean 1.626816e-09 over 8 seeds (sd 9.133880e-14, 0.0% of mean; min 1.626721e-09, max 1.626984e-09)
- `period_b13`: mean 1.626785e-09 over 8 seeds (sd 6.876806e-14, 0.0% of mean; min 1.626648e-09, max 1.626843e-09)
- `period_b14`: mean 1.626773e-09 over 8 seeds (sd 4.038785e-14, 0.0% of mean; min 1.626699e-09, max 1.626831e-09)
- `period_b15`: mean 1.626800e-09 over 8 seeds (sd 7.208863e-14, 0.0% of mean; min 1.626694e-09, max 1.626895e-09)
- `sigma_1`: mean 4.169416e-13 over 8 seeds (sd 1.283541e-14, 3.1% of mean; min 3.885031e-13, max 4.327250e-13)
- `sigma_2`: mean 5.548057e-13 over 8 seeds (sd 2.223816e-14, 4.0% of mean; min 5.284380e-13, max 5.856821e-13)
- `sigma_4`: mean 7.608573e-13 over 8 seeds (sd 3.501636e-14, 4.6% of mean; min 7.010136e-13, max 7.998615e-13)
- `sigma_8`: mean 1.066134e-12 over 8 seeds (sd 1.005116e-13, 9.4% of mean; min 9.731076e-13, max 1.217347e-12)
- `sigma_16`: mean 1.557045e-12 over 8 seeds (sd 1.997775e-13, 12.8% of mean; min 1.359485e-12, max 1.892889e-12)
- `sigma_32`: mean 2.234199e-12 over 8 seeds (sd 3.897842e-13, 17.4% of mean; min 1.741814e-12, max 2.967534e-12)
- `sigma_64`: mean 3.172226e-12 over 8 seeds (sd 8.639708e-13, 27.2% of mean; min 2.023482e-12, max 4.787291e-12)
- `sigma_128`: mean 4.144484e-12 over 8 seeds (sd 1.269405e-12, 30.6% of mean; min 2.333243e-12, max 5.769816e-12)
- `sigma_startup16_1`: mean 3.698594e-13 over 8 seeds (sd 7.267240e-14, 19.6% of mean; min 3.007805e-13, max 4.740616e-13)
- `sigma_startup16_2`: mean 4.968525e-13 over 8 seeds (sd 1.173899e-13, 23.6% of mean; min 3.225351e-13, max 7.279014e-13)
- `sigma_startup16_4`: mean 6.998507e-13 over 8 seeds (sd 2.626140e-13, 37.5% of mean; min 3.828495e-13, max 1.273613e-12)
- `sigma_startup16_8`: mean 9.999841e-13 over 8 seeds (sd 5.713183e-13, 57.1% of mean; min 3.488847e-13, max 2.203518e-12)
- `i_ring_a`: mean 3.015810e-05 over 8 seeds (sd 1.706206e-10, 0.0% of mean; min 3.015779e-05, max 3.015831e-05)
- `p_active_w`: mean 9.952174e-05 over 8 seeds (sd 5.630481e-10, 0.0% of mean; min 9.952072e-05, max 9.952242e-05)
- `e_per_cycle_j`: mean 1.619002e-13 over 8 seeds (sd 9.004274e-19, 0.0% of mean; min 1.618991e-13, max 1.619020e-13)
- `c_eff_node_f`: mean 2.973374e-15 over 8 seeds (sd 1.653678e-20, 0.0% of mean; min 2.973354e-15, max 2.973406e-15)
- `vsup_v`: mean 3.3 over 8 seeds (sd 0.000000e+00, 0.0% of mean; min 3.3, max 3.3)

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

- Single corner (ff / 3.3 V / -40 C). Says nothing about any other corner.
- Same circuit and stimulus as `sim/tb/ro-ring5-starved-jitter-long/`, but the estimators are computed from fleet-measured edge times rather than inside ngspice; edge times come from `.meas ... when` cards, interpolated as in the family's own bench.
- `vsup_v` is the mean of v(vsup) over the whole run (the supply is an ideal DC source), not over the measurement window.
- The PDK model content on the fleet is the one named in `pdk:` above, which may differ from the PDK of the family's earlier records; compare `pdk:` lines before pooling across records.

---

Written by `sim/tools/starved_hot_corner.py ingest`. Append-only: never edit or delete this file -- a re-run or correction mints a new record and points back here via `supersedes` (see `sim/README.md`).
