---
record: 2026-11-21-sampler-dff-mc-offset-sized-01
date: 2026-11-21T17:05:00Z
status: valid

testbench:
  path: sim/tb/sampler-dff-mc-offset/tb_sampler_dff_mc_offset_batch.sp
  sha: 456298d1d746a4c3e03cd00476e4f02e973c78691bfed87f00fb2125e66d7f32
netlist:
  path: design/sampler_core.spice
  sha: 1e0dcf608ac2e45a7552f33af5958eab14b8f34a5bbceb7052eec580038c4c1f
repo_commit: a523c7ffe8672501bfc0bbd6899098535e3ac512

pdk: gf180mcuD; client models lib sm141064.ngspice sha256 f6f4a96e18fc5ad11270ad3451aaecc7ac37fc81eb61e15b0d7d94c7bc594a24 (report environment, scope client)
tool:
  ngspice: "ngspice-47" (fleet runner, /usr/local/bin/ngspice)
  klt: 0.9.3.dev2586+g9bac82596e2f (submitting client, host provision; the reports carry no client-version field)
  platform: aws-batch-fleet (spot), 20 jobs total -- 8 (mc-tt), 8 (mc-ss), 2 (mc-control-tt), 2 (mc-control-ss); c7i/c6i/m6i/m7i workers, 7-45 s per job

corner:
  process: tt (27 C, 3.30 V) and ss (125 C, 3.63 V) -- DR-0033's two ratified PVT points, unchanged
  params: sw_stat_mismatch=1 on every unit; the control units additionally pin voff=-2.2 V (forced input-referred threshold offset)

analysis:
  type: dc sweep of the sampler input (nominal 0..supply; control 2.5..5 V, 500 points), Monte Carlo mismatch (klt vary=mismatch, per-sample seeds derived by klt's SHA-256 seed contract from the base seeds below)
  runs: 500 units -- nominal 220 per corner (seeds 10250201 tt / 10250202 ss), known-bad control 30 per corner (seeds 10250281 tt / 10250282 ss)
  measured: m_dtrip_v (input voltage at which v(xdut.mb) crosses half supply, fall=1) graded against the DR-0033 rail windows
seeds: 10250201, 10250202 (nominal), 10250281, 10250282 (control) -- recorded in sim/tools/mc_yield_campaign.py SEEDS and echoed by each report's environment.monte_carlo

raw:
  path: sim/records/raw/2026-11-21-sampler-dff-mc-offset-sized-01/
  files:
    - analysis.txt  sha256:1a642af7a729d820fdc47f2c12d53be5e90d64f62c43971ce024b306d7ff60fb
    - mc-control-ss.report.json  sha256:aa4f50b42e1d5ea0bf57d8de945dff18dfcbfe6d4b650b0928ec632a52897aea
    - mc-control-tt.report.json  sha256:ee41fe9b1062ab3631aa85805c3a8e43c5c4c4fce0edd9d8e1e95b37543e7c9c
    - mc-ss.report.json  sha256:b7b529d8b8490bf30d6652edcd279944d7008a6fbe50ac2ceb4dd445ba119ab7
    - mc-tt.report.json  sha256:6f3f8b1ed7f2356a5fd33894167fc76987c031ef4e045b8891fedff4ff7a138b
wall_time: mc-tt 67 s / mc-ss 145 s / mc-control-tt 20 s / mc-control-ss 21 s of fleet job time (per-job elapsed summed; the DC bench measures well under a second per unit)
---

## Result

**The `dtrip_v` mismatch campaign at the sample count the `klt yield` report
itself asks for: 220 seeded draws per DR-0033 corner (required_n 183, 1.2x
headroom so one stray failure still grades `sufficient`), zero failures at
both corners, and a seeded known-bad control caught 30/30 at both corners.**
No limit changed; no draw was dropped; no entropy, jitter or post-layout claim
is made here.

Nominal draws (m_dtrip_v, volts; DR-0033 rail windows (0, 3.30) tt exclusive /
(0, 3.63) ss exclusive):

| corner | n | mean | stddev | min | max | verdict |
|---|---|---|---|---|---|---|
| tt / 27 C / 3.30 V | 220 | 1.38641 | 0.0153 | 1.34215 | 1.43036 | 0/220 outside |
| ss / 125 C / 3.63 V | 220 | 1.54245 | 0.0155 | 1.50595 | 1.58766 | 0/220 outside |

Negative controls (the `klt yield` sense: a deterministic, seeded known-bad
variant graded against the nominal's own limits). A forced input-referred
threshold offset `voff = -2.2 V` pushes the master latch's switching
threshold past the positive supply rail; the control requests widen the .dc
sweep window to 2.5..5 V so the shifted crossing stays *measurable* -- the
graded limit is unchanged:

| corner | n | mean | stddev | window | verdict |
|---|---|---|---|---|---|
| tt | 30 | 3.58623 | 0.0133 | (0, 3.30) | 30/30 outside (detected) |
| ss | 30 | 3.74247 | 0.0112 | (0, 3.63) | 30/30 outside (detected) |

This is a fair known-bad case for the rail window because it degrades exactly
what the window guards -- that the sampling threshold sits inside the supply
rail the sampler must operate from -- through a single input-referred offset
knob, the perturbation form `klt yield`'s own documentation names; the
measurement definition, corner and grading path are the nominal's.

Why 30 control draws: detection, not precision (see the ring record's
arithmetic -- [0, 0.116] vs [0.983, 1.0] Clopper-Pearson intervals are
disjoint by a wide margin at these n).

Run notes:

- Per-unit runtime is sub-second (DC sweep); the 120 s per-unit timeout
  carried a >=100x margin and no unit timed out.
- Every request declares `batch.max_units_per_job` 29 (29 x 120 s + 120 s
  overhead = 3600 s <= the 3600 s whole-job ceiling, issues #974/#976) and
  `batch.capacity_wait_s` 600.

## Numerical limitations

- Mismatch spread is the deck's own Pelgrom model under klt's per-sample
  seed; it is a model of population spread, not measured silicon.
- The crossing is resolved by ngspice DC sweep interpolation over 500 points
  (~5-10 mV spacing at these windows).
- Two PVT points only (DR-0033's ratified subset); no claim about the rest of
  the corner space.

## How to reproduce

Use the recorded `repo_commit` for the exact deck bytes submitted to the fleet.

```sh
python3 sim/tools/mc_yield_campaign.py plan
python3 sim/tools/mc_yield_campaign.py run-set sampler --outdir DIR   # submits mc-tt, mc-ss, mc-control-tt, mc-control-ss to the batch fleet
python3 sim/tools/mc_yield_campaign.py analyze DIR/mc-tt/report.json DIR/mc-ss/report.json DIR/mc-control-tt/report.json DIR/mc-control-ss/report.json
```

Request files `mc-{tt,ss,control-tt,control-ss}.request.json` are
generated (`emit --check` guards against drift); environment:
`KLT_SIM_BACKEND=batch`. The committed reports' `netlist_closure` pins the
deck and `design/sampler_core.spice` to the hashes above.
