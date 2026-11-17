---
record: 2026-11-15-sampler-array-fs-sf-05
date: 2026-11-15T21:36:41Z
status: valid

testbench:
  path: sim/tb/sampler-array-fs-sf/tb_sampler_array_fs_sf.sp
  sha: 66904c21fde604ddd1fff55d5c064a5ec86d1d488d354dbaa11714958d3950e7
netlist:
  path: design/sampler_core.spice
  sha: 1e0dcf608ac2e45a7552f33af5958eab14b8f34a5bbceb7052eec580038c4c1f
repo_commit: 791ad51cf11efbcec254050dc779dff9d91a856f

pdk: gf180mcuD -- open_pdks f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7 (fleet runner stamp sha256:4ca10280ae9f293aa1ff69f0060a52e0026929111bda881503717469b429ce67)
tool:
  ngspice: "ngspice-47" (fleet runner)
  klt: 0.9.3.dev16+gdcf18e2e0c03 (client) / 0.9.0 (runner); runner_compatibility: match
  platform: aws-batch-fleet (spot c7i.4xlarge, us-east-1c), job klt-sim-11b864997a0d

corner:
  process: tt (control request, 6 units)
  voltage: 3.30 V
  temperature: 27

analysis:
  type: tran (deterministic)
  tstop: 3620n
  tstep: 10p (print step; also tmax)
  runs: 6 units submitted and executed (~140 s each); returned results are CROSS-CONTAMINATED, see below
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-11-15-sampler-array-fs-sf-05/
  files:
    - batch-receipt.json  sha256:8b4ba71e4fba7831040e7b5deeaf0436cf09f2aa809384c4fb5149e54ddae108
    - report.json  sha256:334567e44bcd405b62b876009b4fa821ec8fb8521f95907550baf385ec5c8279
    - stderr.txt  sha256:cecd55c0090cb3a2177b9c8aed84dacbf176489bc701c2ee356e6c54c049cadf
wall_time: 3m07s (21:33:34 launch -> 21:36:41 terminal)
---

## Result

**Outcome: UNMEASURED. The batch submit executed all 6 units, but the returned
per-unit results are cross-contaminated by a klayout-tools corner-id collision,
so no measurement in this record is attributable to its stimulus. This record
carries no functional-capture result.**

This was the first submit after `2026-10-10-sampler-array-fs-sf-04` with the
capacity-wait fix (`batch.capacity_wait_s: 600` in both committed requests).
The fleet accepted it: no `batch_no_capacity`, client/runner pair compatible
(client `0.9.3.dev16+gdcf18e2e0c03`, runner `0.9.0`, `runner_compatibility:
match`) -- the exit-87 incompatibility of `-01` is gone.

Of the 6 control units, five (the four clock-phase units at 0 / 1.5 / 3 / 4.5
ns and the 20 ps clock-high control) returned **byte-identical** measurement
sets -- no clock-edge crossings measured, `raw_bit`/`raw_valid` pinned near 0 V
-- while the sixth (reset-release 1 s: the only unit whose formatted corner id
was unique) simulated correctly with a normal clock. Five units whose axis
values all format to the same three-decimal corner id
(`vph0.000_vrel0.000_vthw0.000`) collapsed into one directory and one result
set. The pulled-back artifact tree shows the same collision (five units, two
directories).

Root cause filed upstream as
[2AMLogic/klayout-tools#5870](https://github.com/2AMLogic/klayout-tools/issues/5870):
per-unit directory/id names format axis values to three decimals, so sub-milli
axis values (ns phases, ps/µs windows) collide silently. The 72-unit grid was
**deliberately not submitted** into this condition: its four phase units per
PVT point would collapse the same way and return one simulation mis-attributed
four times, i.e. poisoned evidence.

The remedy is in the deck, not the checker: the time axes are re-encoded in
nanoseconds so every unit id is distinct (`-06`), with stimulus identical to
the seconds encoding. Everything measured before this discovery (`-01` ..
`-04`) used units whose ids did not collide (single-point probes, negative
controls) and stands unchanged.

No entropy, jitter, randomness, silicon or post-layout claim is made, and no
specification target changed.

## How to reproduce

```sh
python3 sim/tools/fs_sf_capture.py run control-tt --outdir DIR --backend batch
python3 sim/tools/fs_sf_capture.py analyze DIR/control-tt.report.json
```

Request hashes (as committed at `791ad51c`): `request-control-tt.json` sha256
`92a36b4af96c5651a1eeef3855322d1ca3fd5107771f117a67d4b3d2c5938667`.
Environment: `KLT_SIM_BACKEND=batch`.
