---
record: 2026-10-13-ro-ring5-starved-jitter-long-01
date: 2026-10-13T22:45:23Z
status: valid

testbench:
  path: sim/tb/ro-ring5-starved-jitter-long-batch/tb_ro_ring5_starved_jitter_long_batch.sp
  sha: 99f09daa483248d89f1fef87ba0731feb12c6734
netlist:
  path: design/ro_array_sanity.spice
  sha: 969b5873c37a527f15c86e6f5619304c9b7a9d33
repo_commit: acbbcffbea4d61147fb2e4a7f160dd89e7c16942-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  klt: 0.7.1.dev342+gea2ac1a4ba65 (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: tran-noise
  tstop: 3.1u
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
  path: sim/records/raw/2026-10-13-ro-ring5-starved-jitter-long-01/
  files:
    - report.json  sha256:7026ccc5a8fc7538e6698f36d84f95ebdebd63fbe493cac002861531bef05111
    - request.json  sha256:ac2eeec9f33d93d2482c52bf869ecebb5f9419bdb397dd84ec59db8ab675cad7
    - stderr.txt  sha256:e08bed87efd6e3b028853e93d5d52fe8f7348d9a76cfe29bfd9e930116d476fd
wall_time: 21.5m
---

## Result

Executed on the batch fleet through `klt sim` (fleet jobs: klt-sim-5bfb15075b37, klt-sim-e0542f3bff80). Each unit returned the 769 rising mid-supply edge times of the ring output and the charge readings; the figures below are the family's estimators computed from them by `sim/tools/starved_hot_corner.py` (definitions as in `sim/tb/ro-ring5-starved-jitter-long/tb.json`). The `seeds` are unit indices, not noise seeds.

- `period`: mean 3.780681e-09 over 8 seeds (sd 1.677290e-14, 0.0% of mean; min 3.780660e-09, max 3.780709e-09)
- `f_osc`: mean 2.645026e+08 over 8 seeds (sd 1173.46, 0.0% of mean; min 2.645006e+08, max 2.645041e+08)
- `period_startup16`: mean 3.780688e-09 over 8 seeds (sd 8.285105e-14, 0.0% of mean; min 3.780569e-09, max 3.780793e-09)
- `period_b00`: mean 3.780682e-09 over 8 seeds (sd 4.563383e-14, 0.0% of mean; min 3.780624e-09, max 3.780751e-09)
- `period_b01`: mean 3.780702e-09 over 8 seeds (sd 5.293046e-14, 0.0% of mean; min 3.780634e-09, max 3.780767e-09)
- `period_b02`: mean 3.780700e-09 over 8 seeds (sd 6.705133e-14, 0.0% of mean; min 3.780599e-09, max 3.780778e-09)
- `period_b03`: mean 3.780672e-09 over 8 seeds (sd 8.770557e-14, 0.0% of mean; min 3.780527e-09, max 3.780805e-09)
- `period_b04`: mean 3.780665e-09 over 8 seeds (sd 6.150563e-14, 0.0% of mean; min 3.780524e-09, max 3.780717e-09)
- `period_b05`: mean 3.780680e-09 over 8 seeds (sd 8.946442e-14, 0.0% of mean; min 3.780531e-09, max 3.780787e-09)
- `period_b06`: mean 3.780643e-09 over 8 seeds (sd 3.885190e-14, 0.0% of mean; min 3.780604e-09, max 3.780705e-09)
- `period_b07`: mean 3.780693e-09 over 8 seeds (sd 4.682074e-14, 0.0% of mean; min 3.780638e-09, max 3.780771e-09)
- `period_b08`: mean 3.780682e-09 over 8 seeds (sd 3.582726e-14, 0.0% of mean; min 3.780634e-09, max 3.780745e-09)
- `period_b09`: mean 3.780686e-09 over 8 seeds (sd 1.056112e-13, 0.0% of mean; min 3.780521e-09, max 3.780796e-09)
- `period_b10`: mean 3.780688e-09 over 8 seeds (sd 4.452985e-14, 0.0% of mean; min 3.780630e-09, max 3.780778e-09)
- `period_b11`: mean 3.780696e-09 over 8 seeds (sd 6.263840e-14, 0.0% of mean; min 3.780609e-09, max 3.780764e-09)
- `period_b12`: mean 3.780662e-09 over 8 seeds (sd 6.952466e-14, 0.0% of mean; min 3.780568e-09, max 3.780765e-09)
- `period_b13`: mean 3.780682e-09 over 8 seeds (sd 7.986476e-14, 0.0% of mean; min 3.780523e-09, max 3.780750e-09)
- `period_b14`: mean 3.780681e-09 over 8 seeds (sd 6.553601e-14, 0.0% of mean; min 3.780568e-09, max 3.780757e-09)
- `period_b15`: mean 3.780691e-09 over 8 seeds (sd 7.163518e-14, 0.0% of mean; min 3.780604e-09, max 3.780810e-09)
- `sigma_1`: mean 6.296451e-13 over 8 seeds (sd 2.288474e-14, 3.6% of mean; min 6.060012e-13, max 6.720222e-13)
- `sigma_2`: mean 7.574251e-13 over 8 seeds (sd 2.515122e-14, 3.3% of mean; min 7.246382e-13, max 7.970297e-13)
- `sigma_4`: mean 9.848235e-13 over 8 seeds (sd 2.741809e-14, 2.8% of mean; min 9.480446e-13, max 1.021724e-12)
- `sigma_8`: mean 1.328873e-12 over 8 seeds (sd 3.851857e-14, 2.9% of mean; min 1.269718e-12, max 1.393931e-12)
- `sigma_16`: mean 1.800947e-12 over 8 seeds (sd 9.243545e-14, 5.1% of mean; min 1.669125e-12, max 1.951283e-12)
- `sigma_32`: mean 2.442767e-12 over 8 seeds (sd 2.329625e-13, 9.5% of mean; min 2.187650e-12, max 2.714975e-12)
- `sigma_64`: mean 3.550913e-12 over 8 seeds (sd 7.626759e-13, 21.5% of mean; min 2.460445e-12, max 4.385239e-12)
- `sigma_128`: mean 4.742440e-12 over 8 seeds (sd 1.510256e-12, 31.8% of mean; min 2.431244e-12, max 7.381251e-12)
- `sigma_startup16_1`: mean 6.526522e-13 over 8 seeds (sd 1.269061e-13, 19.4% of mean; min 4.737374e-13, max 7.785227e-13)
- `sigma_startup16_2`: mean 7.352183e-13 over 8 seeds (sd 2.235305e-13, 30.4% of mean; min 4.017724e-13, max 1.026458e-12)
- `sigma_startup16_4`: mean 1.017831e-12 over 8 seeds (sd 3.642594e-13, 35.8% of mean; min 5.070441e-13, max 1.446233e-12)
- `sigma_startup16_8`: mean 1.295618e-12 over 8 seeds (sd 5.520428e-13, 42.6% of mean; min 6.506872e-13, max 2.143289e-12)
- `i_ring_a`: mean 1.535701e-05 over 8 seeds (sd 3.668262e-11, 0.0% of mean; min 1.535694e-05, max 1.535706e-05)
- `p_active_w`: mean 5.574594e-05 over 8 seeds (sd 1.331579e-10, 0.0% of mean; min 5.574570e-05, max 5.574613e-05)
- `e_per_cycle_j`: mean 2.107576e-13 over 8 seeds (sd 5.473980e-19, 0.0% of mean; min 2.107567e-13, max 2.107584e-13)
- `c_eff_node_f`: mean 3.198896e-15 over 8 seeds (sd 8.308449e-21, 0.0% of mean; min 3.198881e-15, max 3.198908e-15)
- `vsup_v`: mean 3.63 over 8 seeds (sd 0.000000e+00, 0.0% of mean; min 3.63, max 3.63)

Runs: 8 of 8 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/starved_hot_corner.py emit --check
python3 sim/tools/starved_hot_corner.py run --outdir DIR --backend batch
python3 sim/tools/starved_hot_corner.py ingest --report DIR/ring5-hot.report.json
```

These commands replay the deck and configuration. They do not reproduce the `trnoise` waveforms: on the ngspice-46 build measured in `sim/tool-experiments/2026-10-11-ngspice-trnoise-seed-replay/` a re-run draws a fresh noise realization, so its measured values will differ from the ones above. Exact waveform replay is not claimed. See `spec/decision-records/DR-0031-transient-noise-reproducibility.md`.

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- Same circuit and stimulus as `sim/tb/ro-ring5-starved-jitter-long/`, but the estimators are computed from fleet-measured edge times rather than inside ngspice; edge times come from `.meas ... when` cards, interpolated as in the family's own bench.
- `vsup_v` is the mean of v(vsup) over the whole run (the supply is an ideal DC source), not over the measurement window.
- The PDK model content on the fleet is the one named in `pdk:` above, which may differ from the PDK of the family's earlier records; compare `pdk:` lines before pooling across records.

---

Written by `sim/tools/starved_hot_corner.py ingest`. Append-only: never edit or delete this file -- a re-run or correction mints a new record and points back here via `supersedes` (see `sim/README.md`).
