---
record: 2026-10-10-sampler-array-fs-sf-04
date: 2026-10-10T08:36:36Z
status: valid

testbench:
  path: sim/tb/sampler-array-fs-sf/tb_sampler_array_fs_sf.sp
  sha: c5dbf2351cb172a88bb46229d645e2a8ef628f12
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 7c4872deac825124f1053eead181ba3b8d3adb01

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
tool:
  klt: 0.7.0+g5e5b55992a7f (client)
  platform: Linux-7.0.0-1014-aws-x86_64-with-glibc2.39

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
  path: sim/records/raw/2026-10-10-sampler-array-fs-sf-04/
  files:
    - attempt1-control-tt-stderr.txt  sha256:0cf3259682af08e994fd38d3bdc49005ab36b5295eebd631cb0d9cae32aa9616
    - attempt2-grid-stderr.txt  sha256:0cf3259682af08e994fd38d3bdc49005ab36b5295eebd631cb0d9cae32aa9616
wall_time: n/a (batch submissions refused)
---

## Result

**Outcome: UNMEASURED.** A second round of batch submits, after
`2026-10-10-sampler-array-fs-sf-01`, was refused again. No simulation unit ran, so
this record carries no measurement and no pass.

| # | UTC | request | outcome |
|---|---|---|---|
| 1 | 08:33-08:34 | `request-control-tt.json` (6 units), `--backend batch` | `batch_no_capacity`: no capacity in any of the 30 pools after 3 attempts |
| 2 | 08:34-08:36 | `request-grid.json` (72 units), `--backend batch` | `batch_no_capacity`, same message |

The error envelopes are byte-identical, hence the identical checksums (the
`klt` warning about two PDK installs is also in each file). The capacity
refusal is the known upstream condition; no new tool issue was filed. The grid
was **not** run locally. Still unmeasured: 16 of 18 asymmetric PVT points, 3 of 4
phases at the other two, and the tt capture control. No entropy, silicon or
post-layout claim is made.

## How to reproduce

```sh
python3 sim/tools/fs_sf_capture.py run control-tt --outdir DIR --backend batch
python3 sim/tools/fs_sf_capture.py run grid --outdir DIR --backend batch
```

Request hashes: `request-grid.json` sha256
`009288979f5efb217b6001aa9d7affddb279f2ad754ff7fcb8abdf4ae7933962`,
`request-control-tt.json` sha256
`8982793bf1190167e4f39ec37b213140549a1f19a0735196ce7f71aa1456e7bd`.
Environment: `KLT_SIM_BACKEND=batch`, klt 0.7.0+g5e5b55992a7f.
