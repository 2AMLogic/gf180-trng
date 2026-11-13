---
record: 2026-11-13-ro-ring5-starved-jitter-redsup-01
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
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-11-13-ro-ring5-starved-jitter-redsup-01/
  files:
    - report.json  sha256:2caf8d97dd91e9fba7e1b48f59ce6c686e696a80bf40817ac7ad7dffbbaa6fa9
    - request.json  sha256:77ff980dcd70e641f50fb61cdfa641bd49f7241e8a6de994acfdb5dc7d6acb89
    - stderr.txt  sha256:83573cf276190c5f46988f8f8c8c1cde2b70ed24afb2acd6e40d8bcf83e7cae1
wall_time: 30.6m
---

## Result

Executed on the batch fleet through `klt sim` (fleet jobs: klt-sim-865f4da8f50d, klt-sim-76b7c2a29061, klt-sim-038d8496fd70, klt-sim-66540e705788). Each unit returned the 769 rising mid-supply edge times of the ring output and the charge readings; the figures below are the family's estimators computed from them by `sim/tools/starved_hot_corner.py` (definitions as in `sim/tb/ro-ring5-starved-jitter-long/tb.json`). The `seeds` are unit indices, not noise seeds.

- `period`: mean 4.226441e-09 over 8 seeds (sd 1.839300e-14, 0.0% of mean; min 4.226407e-09, max 4.226464e-09)
- `f_osc`: mean 2.366057e+08 over 8 seeds (sd 1029.68, 0.0% of mean; min 2.366044e+08, max 2.366076e+08)
- `period_startup16`: mean 4.226388e-09 over 8 seeds (sd 1.117570e-13, 0.0% of mean; min 4.226251e-09, max 4.226500e-09)
- `period_b00`: mean 4.226458e-09 over 8 seeds (sd 7.499533e-14, 0.0% of mean; min 4.226345e-09, max 4.226577e-09)
- `period_b01`: mean 4.226464e-09 over 8 seeds (sd 8.708765e-14, 0.0% of mean; min 4.226360e-09, max 4.226592e-09)
- `period_b02`: mean 4.226439e-09 over 8 seeds (sd 9.691153e-14, 0.0% of mean; min 4.226279e-09, max 4.226554e-09)
- `period_b03`: mean 4.226451e-09 over 8 seeds (sd 7.163743e-14, 0.0% of mean; min 4.226317e-09, max 4.226530e-09)
- `period_b04`: mean 4.226467e-09 over 8 seeds (sd 6.147908e-14, 0.0% of mean; min 4.226400e-09, max 4.226577e-09)
- `period_b05`: mean 4.226422e-09 over 8 seeds (sd 8.931236e-14, 0.0% of mean; min 4.226250e-09, max 4.226525e-09)
- `period_b06`: mean 4.226465e-09 over 8 seeds (sd 7.416102e-14, 0.0% of mean; min 4.226377e-09, max 4.226562e-09)
- `period_b07`: mean 4.226443e-09 over 8 seeds (sd 2.957324e-14, 0.0% of mean; min 4.226404e-09, max 4.226491e-09)
- `period_b08`: mean 4.226433e-09 over 8 seeds (sd 8.618520e-14, 0.0% of mean; min 4.226306e-09, max 4.226569e-09)
- `period_b09`: mean 4.226434e-09 over 8 seeds (sd 7.565262e-14, 0.0% of mean; min 4.226304e-09, max 4.226560e-09)
- `period_b10`: mean 4.226448e-09 over 8 seeds (sd 8.182709e-14, 0.0% of mean; min 4.226335e-09, max 4.226583e-09)
- `period_b11`: mean 4.226390e-09 over 8 seeds (sd 3.748785e-14, 0.0% of mean; min 4.226319e-09, max 4.226434e-09)
- `period_b12`: mean 4.226475e-09 over 8 seeds (sd 7.329915e-14, 0.0% of mean; min 4.226393e-09, max 4.226611e-09)
- `period_b13`: mean 4.226442e-09 over 8 seeds (sd 5.972265e-14, 0.0% of mean; min 4.226383e-09, max 4.226550e-09)
- `period_b14`: mean 4.226456e-09 over 8 seeds (sd 6.107665e-14, 0.0% of mean; min 4.226345e-09, max 4.226526e-09)
- `period_b15`: mean 4.226430e-09 over 8 seeds (sd 6.468219e-14, 0.0% of mean; min 4.226327e-09, max 4.226511e-09)
- `sigma_1`: mean 7.377472e-13 over 8 seeds (sd 3.649673e-14, 4.9% of mean; min 6.879289e-13, max 7.875871e-13)
- `sigma_2`: mean 9.021212e-13 over 8 seeds (sd 2.875578e-14, 3.2% of mean; min 8.701069e-13, max 9.531586e-13)
- `sigma_4`: mean 1.132114e-12 over 8 seeds (sd 4.851668e-14, 4.3% of mean; min 1.089090e-12, max 1.217828e-12)
- `sigma_8`: mean 1.497943e-12 over 8 seeds (sd 7.845323e-14, 5.2% of mean; min 1.390606e-12, max 1.664859e-12)
- `sigma_16`: mean 2.010911e-12 over 8 seeds (sd 1.769396e-13, 8.8% of mean; min 1.736380e-12, max 2.345523e-12)
- `sigma_32`: mean 2.729554e-12 over 8 seeds (sd 3.052830e-13, 11.2% of mean; min 2.268453e-12, max 3.262068e-12)
- `sigma_64`: mean 3.496254e-12 over 8 seeds (sd 6.504491e-13, 18.6% of mean; min 2.692417e-12, max 4.477768e-12)
- `sigma_128`: mean 4.698927e-12 over 8 seeds (sd 1.698408e-12, 36.1% of mean; min 2.736370e-12, max 7.921180e-12)
- `sigma_startup16_1`: mean 7.545432e-13 over 8 seeds (sd 6.896073e-14, 9.1% of mean; min 6.301988e-13, max 8.201217e-13)
- `sigma_startup16_2`: mean 9.166694e-13 over 8 seeds (sd 8.212579e-14, 9.0% of mean; min 7.789500e-13, max 1.051387e-12)
- `sigma_startup16_4`: mean 1.111017e-12 over 8 seeds (sd 2.078094e-13, 18.7% of mean; min 8.178835e-13, max 1.482881e-12)
- `sigma_startup16_8`: mean 1.590347e-12 over 8 seeds (sd 4.128420e-13, 26.0% of mean; min 1.103620e-12, max 2.289614e-12)
- `i_ring_a`: mean 1.206552e-05 over 8 seeds (sd 2.447982e-11, 0.0% of mean; min 1.206549e-05, max 1.206556e-05)
- `p_active_w`: mean 3.981621e-05 over 8 seeds (sd 8.078339e-11, 0.0% of mean; min 3.981613e-05, max 3.981634e-05)
- `e_per_cycle_j`: mean 1.682809e-13 over 8 seeds (sd 4.293920e-19, 0.0% of mean; min 1.682800e-13, max 1.682814e-13)
- `c_eff_node_f`: mean 3.090558e-15 over 8 seeds (sd 7.885987e-21, 0.0% of mean; min 3.090542e-15, max 3.090568e-15)
- `vsup_v`: mean 3.3 over 8 seeds (sd 0.000000e+00, 0.0% of mean; min 3.3, max 3.3)

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

- Single corner (ss / 3.3 V / 125 C). Says nothing about any other corner.
- Same circuit and stimulus as `sim/tb/ro-ring5-starved-jitter-long/`, but the estimators are computed from fleet-measured edge times rather than inside ngspice; edge times come from `.meas ... when` cards, interpolated as in the family's own bench.
- `vsup_v` is the mean of v(vsup) over the whole run (the supply is an ideal DC source), not over the measurement window.
- The PDK model content on the fleet is the one named in `pdk:` above, which may differ from the PDK of the family's earlier records; compare `pdk:` lines before pooling across records.

---

Written by `sim/tools/starved_hot_corner.py ingest`. Append-only: never edit or delete this file -- a re-run or correction mints a new record and points back here via `supersedes` (see `sim/README.md`).
