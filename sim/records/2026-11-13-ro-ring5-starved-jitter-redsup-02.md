---
record: 2026-11-13-ro-ring5-starved-jitter-redsup-02
date: 2026-11-13T06:39:06Z
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
  - libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  klt: 0.9.2.dev885+ge4c446bd91f2 (client; batch backend)
  ngspice: "ngspice-47 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ss
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: tran-noise
  tstop: 4.2u
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
  path: sim/records/raw/2026-11-13-ro-ring5-starved-jitter-redsup-02/
  files:
    - report.json  sha256:fca4793c08198f1fae2bfecc1769a569c0f24efb68813dc84632507fcba48487
    - request.json  sha256:77ff980dcd70e641f50fb61cdfa641bd49f7241e8a6de994acfdb5dc7d6acb89
    - stderr.txt  sha256:83573cf276190c5f46988f8f8c8c1cde2b70ed24afb2acd6e40d8bcf83e7cae1
wall_time: 30.5m
---

## Result

Executed on the batch fleet through `klt sim` (fleet jobs: klt-sim-865f4da8f50d, klt-sim-76b7c2a29061, klt-sim-038d8496fd70, klt-sim-66540e705788). Each unit returned the 769 rising mid-supply edge times of the ring output and the charge readings; the figures below are the family's estimators computed from them by `sim/tools/starved_hot_corner.py` (definitions as in `sim/tb/ro-ring5-starved-jitter-long/tb.json`). The `seeds` are unit indices, not noise seeds.

- `period`: mean 4.847662e-09 over 8 seeds (sd 1.804044e-14, 0.0% of mean; min 4.847637e-09, max 4.847697e-09)
- `f_osc`: mean 2.062850e+08 over 8 seeds (sd 767.682, 0.0% of mean; min 2.062835e+08, max 2.062861e+08)
- `period_startup16`: mean 4.847658e-09 over 8 seeds (sd 1.527579e-13, 0.0% of mean; min 4.847430e-09, max 4.847878e-09)
- `period_b00`: mean 4.847629e-09 over 8 seeds (sd 1.108780e-13, 0.0% of mean; min 4.847463e-09, max 4.847817e-09)
- `period_b01`: mean 4.847604e-09 over 8 seeds (sd 1.092284e-13, 0.0% of mean; min 4.847384e-09, max 4.847735e-09)
- `period_b02`: mean 4.847650e-09 over 8 seeds (sd 4.986231e-14, 0.0% of mean; min 4.847586e-09, max 4.847730e-09)
- `period_b03`: mean 4.847612e-09 over 8 seeds (sd 8.266145e-14, 0.0% of mean; min 4.847484e-09, max 4.847726e-09)
- `period_b04`: mean 4.847634e-09 over 8 seeds (sd 9.337232e-14, 0.0% of mean; min 4.847531e-09, max 4.847779e-09)
- `period_b05`: mean 4.847577e-09 over 8 seeds (sd 4.815840e-14, 0.0% of mean; min 4.847505e-09, max 4.847645e-09)
- `period_b06`: mean 4.847674e-09 over 8 seeds (sd 6.356718e-14, 0.0% of mean; min 4.847552e-09, max 4.847764e-09)
- `period_b07`: mean 4.847647e-09 over 8 seeds (sd 9.666222e-14, 0.0% of mean; min 4.847495e-09, max 4.847784e-09)
- `period_b08`: mean 4.847638e-09 over 8 seeds (sd 5.416907e-14, 0.0% of mean; min 4.847567e-09, max 4.847716e-09)
- `period_b09`: mean 4.847674e-09 over 8 seeds (sd 7.257243e-14, 0.0% of mean; min 4.847567e-09, max 4.847752e-09)
- `period_b10`: mean 4.847671e-09 over 8 seeds (sd 8.756930e-14, 0.0% of mean; min 4.847488e-09, max 4.847763e-09)
- `period_b11`: mean 4.847681e-09 over 8 seeds (sd 1.032404e-13, 0.0% of mean; min 4.847552e-09, max 4.847847e-09)
- `period_b12`: mean 4.847657e-09 over 8 seeds (sd 7.989840e-14, 0.0% of mean; min 4.847556e-09, max 4.847793e-09)
- `period_b13`: mean 4.847699e-09 over 8 seeds (sd 8.752879e-14, 0.0% of mean; min 4.847543e-09, max 4.847836e-09)
- `period_b14`: mean 4.847657e-09 over 8 seeds (sd 7.556433e-14, 0.0% of mean; min 4.847504e-09, max 4.847732e-09)
- `period_b15`: mean 4.847681e-09 over 8 seeds (sd 8.454968e-14, 0.0% of mean; min 4.847538e-09, max 4.847802e-09)
- `sigma_1`: mean 9.058749e-13 over 8 seeds (sd 3.757940e-14, 4.1% of mean; min 8.601737e-13, max 9.604725e-13)
- `sigma_2`: mean 1.067121e-12 over 8 seeds (sd 4.700211e-14, 4.4% of mean; min 9.945181e-13, max 1.146173e-12)
- `sigma_4`: mean 1.354610e-12 over 8 seeds (sd 7.468489e-14, 5.5% of mean; min 1.204476e-12, max 1.443638e-12)
- `sigma_8`: mean 1.813784e-12 over 8 seeds (sd 1.543866e-13, 8.5% of mean; min 1.503219e-12, max 1.980471e-12)
- `sigma_16`: mean 2.448806e-12 over 8 seeds (sd 2.682784e-13, 11.0% of mean; min 2.013613e-12, max 2.921341e-12)
- `sigma_32`: mean 3.257897e-12 over 8 seeds (sd 6.502888e-13, 20.0% of mean; min 2.488481e-12, max 4.577083e-12)
- `sigma_64`: mean 4.570509e-12 over 8 seeds (sd 1.412883e-12, 30.9% of mean; min 3.112743e-12, max 7.736027e-12)
- `sigma_128`: mean 7.002744e-12 over 8 seeds (sd 3.231472e-12, 46.1% of mean; min 4.201531e-12, max 1.405620e-11)
- `sigma_startup16_1`: mean 8.880207e-13 over 8 seeds (sd 2.555770e-13, 28.8% of mean; min 4.933553e-13, max 1.266390e-12)
- `sigma_startup16_2`: mean 1.056662e-12 over 8 seeds (sd 2.916835e-13, 27.6% of mean; min 6.277515e-13, max 1.478590e-12)
- `sigma_startup16_4`: mean 1.179907e-12 over 8 seeds (sd 2.620910e-13, 22.2% of mean; min 7.509335e-13, max 1.542211e-12)
- `sigma_startup16_8`: mean 1.599973e-12 over 8 seeds (sd 5.918138e-13, 37.0% of mean; min 7.707875e-13, max 2.281007e-12)
- `i_ring_a`: mean 9.121147e-06 over 8 seeds (sd 2.011505e-11, 0.0% of mean; min 9.121117e-06, max 9.121180e-06)
- `p_active_w`: mean 2.708981e-05 over 8 seeds (sd 5.974171e-11, 0.0% of mean; min 2.708972e-05, max 2.708991e-05)
- `e_per_cycle_j`: mean 1.313222e-13 over 8 seeds (sd 2.626333e-19, 0.0% of mean; min 1.313218e-13, max 1.313227e-13)
- `c_eff_node_f`: mean 2.977524e-15 over 8 seeds (sd 5.954796e-21, 0.0% of mean; min 2.977515e-15, max 2.977536e-15)
- `vsup_v`: mean 2.97 over 8 seeds (sd 0.000000e+00, 0.0% of mean; min 2.97, max 2.97)

Runs: 8 of 8 successful. Summaries above use successful runs only.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

The request that produced this record carried 2 supplies x 8 units, so the fleet job id(s) above are those of the whole request; `raw/report.json` holds only this record's units, and `raw/request.json` is the whole request.

## How to reproduce

```sh
python3 sim/tools/starved_hot_corner.py emit --check
python3 sim/tools/starved_hot_corner.py run --outdir DIR --backend batch --grid ring5-redsup-ss125
python3 sim/tools/starved_hot_corner.py ingest --report DIR/ring5-redsup-ss125.report.json --grid ring5-redsup-ss125
```

These commands replay the deck and configuration. They do not reproduce the `trnoise` waveforms: on the ngspice-46 build measured in `sim/tool-experiments/2026-10-11-ngspice-trnoise-seed-replay/` a re-run draws a fresh noise realization, so its measured values will differ from the ones above. Exact waveform replay is not claimed. See `spec/decision-records/DR-0031-transient-noise-reproducibility.md`.

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- Same circuit and stimulus as `sim/tb/ro-ring5-starved-jitter-long/`, but the estimators are computed from fleet-measured edge times rather than inside ngspice; edge times come from `.meas ... when` cards, interpolated as in the family's own bench.
- `vsup_v` is the mean of v(vsup) over the whole run (the supply is an ideal DC source), not over the measurement window.
- The PDK model content on the fleet is the one named in `pdk:` above, which may differ from the PDK of the family's earlier records; compare `pdk:` lines before pooling across records.

---

Written by `sim/tools/starved_hot_corner.py ingest`. Append-only: never edit or delete this file -- a re-run or correction mints a new record and points back here via `supersedes` (see `sim/README.md`).
