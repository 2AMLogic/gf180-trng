---
record: 2026-11-13-ro-ring5-starved-jitter-redsup-05
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
  - libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 0.9.2.dev885+ge4c446bd91f2 (client; batch backend)
  ngspice: "ngspice-47 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: tt
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 27

analysis:
  type: tran-noise
  tstop: 2.8u
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
  path: sim/records/raw/2026-11-13-ro-ring5-starved-jitter-redsup-05/
  files:
    - report.json  sha256:f4df071f657d207f48a7153cac4971377b4a0d14feb57d6dfd409134bafd38b0
    - request.json  sha256:d78eac3480d2e00a57701f3703cf59b2eceaeab670ef29a31f0128a670c9bb68
    - stderr.txt  sha256:fb881756f2d3639f5c9c41c4bdd5797225f71ec6606e8caad9dc49f8b1c46424
wall_time: 20.3m
---

## Result

Executed on the batch fleet through `klt sim` (fleet jobs: klt-sim-c3776b087d22, klt-sim-0e64941d1fba). Each unit returned the 769 rising mid-supply edge times of the ring output and the charge readings; the figures below are the family's estimators computed from them by `sim/tools/starved_hot_corner.py` (definitions as in `sim/tb/ro-ring5-starved-jitter-long/tb.json`). The `seeds` are unit indices, not noise seeds.

- `period`: mean 2.899839e-09 over 8 seeds (sd 2.694597e-14, 0.0% of mean; min 2.899809e-09, max 2.899894e-09)
- `f_osc`: mean 3.448468e+08 over 8 seeds (sd 3204.37, 0.0% of mean; min 3.448402e+08, max 3.448503e+08)
- `period_startup16`: mean 2.899896e-09 over 8 seeds (sd 1.246493e-13, 0.0% of mean; min 2.899644e-09, max 2.900041e-09)
- `period_b00`: mean 2.899857e-09 over 8 seeds (sd 6.418838e-14, 0.0% of mean; min 2.899740e-09, max 2.899964e-09)
- `period_b01`: mean 2.899832e-09 over 8 seeds (sd 5.454031e-14, 0.0% of mean; min 2.899771e-09, max 2.899913e-09)
- `period_b02`: mean 2.899820e-09 over 8 seeds (sd 6.176984e-14, 0.0% of mean; min 2.899738e-09, max 2.899911e-09)
- `period_b03`: mean 2.899829e-09 over 8 seeds (sd 8.383103e-14, 0.0% of mean; min 2.899691e-09, max 2.899912e-09)
- `period_b04`: mean 2.899814e-09 over 8 seeds (sd 6.711292e-14, 0.0% of mean; min 2.899699e-09, max 2.899881e-09)
- `period_b05`: mean 2.899810e-09 over 8 seeds (sd 5.593839e-14, 0.0% of mean; min 2.899730e-09, max 2.899867e-09)
- `period_b06`: mean 2.899836e-09 over 8 seeds (sd 4.410556e-14, 0.0% of mean; min 2.899776e-09, max 2.899904e-09)
- `period_b07`: mean 2.899839e-09 over 8 seeds (sd 5.551898e-14, 0.0% of mean; min 2.899740e-09, max 2.899904e-09)
- `period_b08`: mean 2.899917e-09 over 8 seeds (sd 5.901024e-14, 0.0% of mean; min 2.899780e-09, max 2.899967e-09)
- `period_b09`: mean 2.899818e-09 over 8 seeds (sd 6.159089e-14, 0.0% of mean; min 2.899749e-09, max 2.899929e-09)
- `period_b10`: mean 2.899844e-09 over 8 seeds (sd 5.130719e-14, 0.0% of mean; min 2.899779e-09, max 2.899922e-09)
- `period_b11`: mean 2.899802e-09 over 8 seeds (sd 9.149248e-14, 0.0% of mean; min 2.899704e-09, max 2.899968e-09)
- `period_b12`: mean 2.899872e-09 over 8 seeds (sd 5.953754e-14, 0.0% of mean; min 2.899765e-09, max 2.899979e-09)
- `period_b13`: mean 2.899835e-09 over 8 seeds (sd 6.208602e-14, 0.0% of mean; min 2.899772e-09, max 2.899924e-09)
- `period_b14`: mean 2.899824e-09 over 8 seeds (sd 5.947236e-14, 0.0% of mean; min 2.899751e-09, max 2.899925e-09)
- `period_b15`: mean 2.899828e-09 over 8 seeds (sd 5.761546e-14, 0.0% of mean; min 2.899748e-09, max 2.899918e-09)
- `sigma_1`: mean 6.557147e-13 over 8 seeds (sd 2.330240e-14, 3.6% of mean; min 6.275401e-13, max 6.929605e-13)
- `sigma_2`: mean 8.036391e-13 over 8 seeds (sd 3.702852e-14, 4.6% of mean; min 7.608849e-13, max 8.542365e-13)
- `sigma_4`: mean 1.054055e-12 over 8 seeds (sd 4.446192e-14, 4.2% of mean; min 9.995034e-13, max 1.110081e-12)
- `sigma_8`: mean 1.436609e-12 over 8 seeds (sd 6.096666e-14, 4.2% of mean; min 1.354199e-12, max 1.547034e-12)
- `sigma_16`: mean 2.019311e-12 over 8 seeds (sd 8.890445e-14, 4.4% of mean; min 1.930084e-12, max 2.189387e-12)
- `sigma_32`: mean 2.854591e-12 over 8 seeds (sd 1.798501e-13, 6.3% of mean; min 2.646488e-12, max 3.110966e-12)
- `sigma_64`: mean 3.892337e-12 over 8 seeds (sd 5.808942e-13, 14.9% of mean; min 3.142516e-12, max 4.869305e-12)
- `sigma_128`: mean 4.934433e-12 over 8 seeds (sd 8.669761e-13, 17.6% of mean; min 3.780108e-12, max 6.109595e-12)
- `sigma_startup16_1`: mean 6.873966e-13 over 8 seeds (sd 1.239511e-13, 18.0% of mean; min 4.741313e-13, max 8.234036e-13)
- `sigma_startup16_2`: mean 8.936512e-13 over 8 seeds (sd 1.843961e-13, 20.6% of mean; min 6.256806e-13, max 1.183611e-12)
- `sigma_startup16_4`: mean 1.189364e-12 over 8 seeds (sd 2.882032e-13, 24.2% of mean; min 7.526569e-13, max 1.611078e-12)
- `sigma_startup16_8`: mean 1.398914e-12 over 8 seeds (sd 6.048116e-13, 43.2% of mean; min 7.205895e-13, max 2.594071e-12)
- `i_ring_a`: mean 1.469311e-05 over 8 seeds (sd 8.302257e-11, 0.0% of mean; min 1.469294e-05, max 1.469320e-05)
- `p_active_w`: mean 4.363852e-05 over 8 seeds (sd 2.465770e-10, 0.0% of mean; min 4.363802e-05, max 4.363881e-05)
- `e_per_cycle_j`: mean 1.265447e-13 over 8 seeds (sd 4.679351e-19, 0.0% of mean; min 1.265442e-13, max 1.265456e-13)
- `c_eff_node_f`: mean 2.869201e-15 over 8 seeds (sd 1.060969e-20, 0.0% of mean; min 2.869191e-15, max 2.869223e-15)
- `vsup_v`: mean 2.97 over 8 seeds (sd 0.000000e+00, 0.0% of mean; min 2.97, max 2.97)

Runs: 8 of 8 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/starved_hot_corner.py emit --check
python3 sim/tools/starved_hot_corner.py run --outdir DIR --backend batch --grid ring5-redsup-tt27
python3 sim/tools/starved_hot_corner.py ingest --report DIR/ring5-redsup-tt27.report.json --grid ring5-redsup-tt27
```

These commands replay the deck and configuration. They do not reproduce the `trnoise` waveforms: on the ngspice-46 build measured in `sim/tool-experiments/2026-10-11-ngspice-trnoise-seed-replay/` a re-run draws a fresh noise realization, so its measured values will differ from the ones above. Exact waveform replay is not claimed. See `spec/decision-records/DR-0031-transient-noise-reproducibility.md`.

## Caveats

- Single corner (tt / 2.97 V / 27 C). Says nothing about any other corner.
- Same circuit and stimulus as `sim/tb/ro-ring5-starved-jitter-long/`, but the estimators are computed from fleet-measured edge times rather than inside ngspice; edge times come from `.meas ... when` cards, interpolated as in the family's own bench.
- `vsup_v` is the mean of v(vsup) over the whole run (the supply is an ideal DC source), not over the measurement window.
- The PDK model content on the fleet is the one named in `pdk:` above, which may differ from the PDK of the family's earlier records; compare `pdk:` lines before pooling across records.

---

Written by `sim/tools/starved_hot_corner.py ingest`. Append-only: never edit or delete this file -- a re-run or correction mints a new record and points back here via `supersedes` (see `sim/README.md`).
