---
record: 2026-10-10-sampler-core-liveness-active-attempt-01
date: 2026-10-10T11:18:38Z
status: valid

testbench:
  path: sim/tb/sampler-core-liveness-active/tb_sampler_core_liveness_active.sp
  sha: d266f12cc238e26730e2f12a4651854fd2d2a4e8
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 870cb9ecd9e801f659fde2932233ec071cd9aae6-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
tool:
  klt: 0.7.0+gca3089cd4b9f (client)
  platform: Linux-7.0.0-1013-aws-x86_64-with-glibc2.39

corner:
  process: tt, ff, ss -- NOT SIMULATED
  voltage: 2.97 / 3.30 / 3.63 V -- NOT SIMULATED
  temperature: -40 / 27 / 125 -- NOT SIMULATED

analysis:
  type: tran (deterministic)
  tstop: 120n
  tstep: 5p (print step)
  runs: 0 (nothing executed)
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-10-sampler-core-liveness-active-attempt-01/
  files:
    - report-errored.json  sha256:350d8f661c61c05d5540e6848a10e805206bf037d194d1af0e5357f58d902863
wall_time: n/a (batch submission failed)
---

## Result

**Outcome: UNMEASURED.** 27 of 27 grid units were submitted to the batch fleet and none produced a measurement, so this record carries no measurement and no pass.

- fleet job: `klt-sim-36eae9fed238` (m6i.4xlarge, spot), diagnostics `batch_job_failed`, runner code `batch_runner_version_mismatch`
- runner klt 0.5.0 vs client 0.7.0+gca3089cd4b9f (`runner_compatibility: mismatch`)

The run was submitted once at the start of this work (UTC 11:16, one attempt, 51 s). The fleet accepted the job and the runner rejected it before any simulation: the runner image carries klt 0.5.0 and the submitting client is 0.7.0, the version skew already seen for sampler-array-fs-sf (see 2026-10-10-sampler-array-fs-sf-01 attempts 4-5: a 0.5.0 client has no batch backend, so no compatible pair exists). No new tool issue is filed; the condition is already tracked upstream. Single-point local probe tt/27/3.30 is the only measured corner (2026-10-10-sampler-core-liveness-active-01); the other 26 grid points are gaps.

The grid was **not** run as a local loop (shared-worker rule). Every corner not covered by a `valid` measured record of this family is an explicit gap in `power_rollup.py`.

## How to reproduce

```sh
python3 sim/tools/liveness_sampler_power.py emit --check
python3 sim/tools/liveness_sampler_power.py run --outdir DIR --backend batch
```

---

Written by `sim/tools/liveness_sampler_power.py record`. Append-only: never edit or delete this file.
