---
record: 2026-10-10-sampler-array-fs-sf-01
date: 2026-10-10T08:23:30Z
status: valid

testbench:
  path: sim/tb/sampler-array-fs-sf/tb_sampler_array_fs_sf.sp
  sha: c5dbf2351cb172a88bb46229d645e2a8ef628f12
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: cfef09511d819642ac66dcdb05c0a0ca1249eabc-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - ~/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sha256:6edba54d23b38a2c60f8ffdbaa3eb75a7568c615e4820808969bd1121b77b1aa)
tool:
  klt: 0.7.0+g8eec069c7576 (client); fleet runner klt 0.5.0
  platform: Linux-7.0.0-1013-aws-x86_64-with-glibc2.39

corner:
  process: fs, sf (grid) and tt (control) -- NOT SIMULATED
  voltage: 2.97 / 3.30 / 3.63 V -- NOT SIMULATED
  temperature: -40 / 27 / 125 -- NOT SIMULATED

analysis:
  type: tran (deterministic)
  tstop: 3620n
  tstep: 10p (print step; also tmax)
  runs: 0 (nothing executed)
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-10-sampler-array-fs-sf-01/
  files:
    - attempt1-grid-stderr.json  sha256:2a23a48a41ab75ac3b66c024685450b741ce2ba9cfb3e7d22c799277a8b01420
    - attempt2-control-tt-stderr.json  sha256:2a23a48a41ab75ac3b66c024685450b741ce2ba9cfb3e7d22c799277a8b01420
    - attempt3-grid-stderr.json  sha256:2a23a48a41ab75ac3b66c024685450b741ce2ba9cfb3e7d22c799277a8b01420
    - attempt4-control-tt-report.json  sha256:0d6f584b779d0e8976447ab6ef1f3660e171623e59773d4d81e7ef444f262175
    - attempt5-control-tt-klt050-stderr.txt  sha256:10e92b115d086a30d53d090099b408cb040ac9228bd61fe14916f88a930a6d6d
wall_time: n/a (batch submissions refused or rejected)
---

## Result

**Outcome: UNMEASURED.** No simulation unit of either request ran on the fleet, so
this record carries no measurement and no pass. It exists so the attempts are
append-only evidence rather than a silent omission.

| # | UTC | request | outcome |
|---|---|---|---|
| 1 | 08:13-08:16 | `request-grid.json` (72 units) | `batch_no_capacity`: no capacity in any of the 30 pools after 3 attempts |
| 2 | 08:16-08:18 | `request-control-tt.json` (6 units) | `batch_no_capacity`, same message |
| 3 | 08:18-08:20 | `request-grid.json` | `batch_no_capacity`, same message |
| 4 | 08:20-08:23 | `request-control-tt.json` | fleet job `klt-sim-d40243c0c1ee` (c7i.4xlarge Spot) acquired, then rejected by the runner: exit 87, `runner_compatibility: mismatch` (runner klt 0.5.0, client klt 0.7.0+g8eec069c7576); all 6 units `batch_job_failed`, no measurements, 4 s |
| 5 | 08:23 | `request-control-tt.json` with a klt 0.5.0 client (throwaway `uvx` environment) | refused by the client: `unsupported backend 'batch' (supported: local, local-parallel, remote)` |

Attempts 1-3 are the capacity-refusal case also logged for #418; attempt 4 is the
runner/client version skew already tracked upstream (klayout-tools#2948,
#2851, #3015); attempt 5 shows no compatible client/runner pair exists today. No
new tool issue is warranted. The grid was **not** run as a local loop: attempt 4's
`control-tt` report and the error envelopes of attempts 1-3 and 5 are the raw
files.

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/fs_sf_capture.py emit --check
python3 sim/tools/fs_sf_capture.py run grid --outdir DIR --backend batch
python3 sim/tools/fs_sf_capture.py run control-tt --outdir DIR --backend batch
python3 sim/tools/fs_sf_capture.py analyze DIR/grid.report.json DIR/control-tt.report.json
```

Environment on the submitting host: `KLT_SIM_BACKEND=batch`,
`KLT_BATCH_PROVISION_SCRIPT` set by the dispatch worker, klt
0.7.0+g8eec069c7576. The requests are committed at `sim/tb/sampler-array-fs-sf/`; the report of
attempt 4 names the deck and netlist closure hashes (`environment.netlist_sha256` 3b7131cd..., `design/sampler_core.spice`
1e0dcf60...).
