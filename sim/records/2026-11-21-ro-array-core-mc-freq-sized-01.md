---
record: 2026-11-21-ro-array-core-mc-freq-sized-01
date: 2026-11-21T17:05:00Z
status: valid

testbench:
  path: sim/tb/ro-array-core-mc-freq/tb_ro_array_core_mc_freq_batch.sp
  sha: c4858d254ccd1d857f4e5b43d5984970aeb284622462da824f8ac34277c93955
netlist:
  path: design/ro_array_core.spice
  sha: 754c20ae6474a82b1b1c7eddd566df21f70fedaafaa80350233ecc76755f931d
repo_commit: a523c7ffe8672501bfc0bbd6899098535e3ac512

pdk: gf180mcuD; client models lib sm141064.ngspice sha256 f6f4a96e18fc5ad11270ad3451aaecc7ac37fc81eb61e15b0d7d94c7bc594a24 (report environment, scope client)
tool:
  ngspice: "ngspice-47" (fleet runner, /usr/local/bin/ngspice)
  klt: 0.9.3.dev2586+g9bac82596e2f (submitting client, host provision; the reports carry no client-version field)
  platform: aws-batch-fleet (spot), 38 jobs total -- 16 (mc-tt), 16 (mc-ss), 3 (mc-control-tt), 3 (mc-control-ss); c7i/m6i/m7i.4xlarge and c6i.8xlarge workers, 35-71 s per job

corner:
  process: tt (27 C, 3.30 V) and ss (125 C, 3.63 V) -- DR-0033's two ratified PVT points, unchanged
  params: sw_stat_mismatch=1 on every unit; the control units additionally pin ro_lstv=3.4e-6 m (ring 1 per-stage channel length, fabricated long)

analysis:
  type: tran (1p 100n), Monte Carlo mismatch (klt vary=mismatch, per-sample seeds derived by klt's SHA-256 seed contract from the base seeds below)
  runs: 500 units -- nominal 220 per corner (seeds 10250101 tt / 10250102 ss), known-bad control 30 per corner (seeds 10250181 tt / 10250182 ss)
  measured: m_period_r1 (four-period average, TRIG/TARG rise 2->6 / 4) graded against the DR-0033 period ceilings; m_period_r2, m_f_r1, m_f_r2 recorded ungraded
seeds: 10250101, 10250102 (nominal), 10250181, 10250182 (control) -- recorded in sim/tools/mc_yield_campaign.py SEEDS and echoed by each report's environment.monte_carlo

raw:
  path: sim/records/raw/2026-11-21-ro-array-core-mc-freq-sized-01/
  files:
    - analysis.txt  sha256:8a6304bf2d4f51a5734e09cd75835e5990a4f4214774bbcb36d763a52d0645f9
    - mc-control-ss.report.json  sha256:cf57407f862c9ae0f4c667e7a808189640989333dc271eef3b54c89247b7ba2d
    - mc-control-tt.report.json  sha256:cb95031d0dd606bcfe270c4393eae8f52815c961991f76a100f2effdf9ef7d5e
    - mc-ss.report.json  sha256:3cb056ae823dabb55a16964acf70924513505f240014922d17b9a8e5f9223b2d
    - mc-tt.report.json  sha256:0c9dae6917b368adbb607904a0a619a204c0307d40ae37d97ba967a9340ce1ce
wall_time: mc-tt 834 s / mc-ss 794 s / mc-control-tt 181 s / mc-control-ss 181 s of fleet job time (per-job elapsed summed; wall clock is less -- shards of one request run concurrently within the fleet's vCPU budget)
---

## Result

**The `period_r1` mismatch campaign at the sample count the `klt yield` report
itself asks for: 220 seeded draws per DR-0033 corner (required_n 183, 1.2x
headroom so one stray failure still grades `sufficient`), zero failures at
both corners, and a seeded known-bad control caught 30/30 at both corners.**
No limit changed; no draw was dropped; no entropy, jitter or post-layout claim
is made here.

Nominal draws (m_period_r1, seconds; DR-0033 ceilings 9.151e-9 tt /
1.128e-8 ss):

| corner | n | mean | stddev | min | max | limit | verdict |
|---|---|---|---|---|---|---|---|
| tt / 27 C / 3.30 V | 220 | 6.67902e-9 | 1.29e-11 | 6.64248e-9 | 6.71784e-9 | 9.151e-9 | 0/220 outside |
| ss / 125 C / 3.63 V | 220 | 9.58440e-9 | 1.60e-11 | 9.53805e-9 | 9.63189e-9 | 1.128e-8 | 0/220 outside |

Negative controls (the `klt yield` sense: a deterministic, seeded known-bad
variant graded against the nominal's own limits). Ring 1's per-stage channel
is fabricated long (`ro_lstv` 2e-6 -> 3.4e-6 m), a slow-device defect that
moves the mismatch-free period far past both corners' ceilings while the
seeded mismatch population keeps it a distribution, not a point:

| corner | n | mean | stddev | limit | verdict |
|---|---|---|---|---|---|
| tt | 30 | 9.50861e-9 | 1.67e-11 | 9.151e-9 | 30/30 outside (detected) |
| ss | 30 | 1.40511e-8 | 1.98e-11 | 1.128e-8 | 30/30 outside (detected) |

This is a fair known-bad case for the period ceiling because it degrades
exactly the quantity the limit guards -- ring 1's oscillation period through
one channel-length knob -- without touching the measurement definition, the
corner, or the grading path; ring 2 (untouched, m_period_r2 mean 6.24e-9 tt)
stays inside its sibling's ceiling in the same units, so the failure is
attributable to the defect, not the harness.

Why 30 control draws: the control is sized for detection, not precision. All
30 failing gives a Clopper-Pearson yield interval of [0, 0.116] against the
nominal's [0.983, 1.0] at n=220 -- disjoint by a wide margin; ~3 failures
would already separate them at this n.

Run notes:

- The first `mc-control-ss` submit lost one shard to a fleet interruption (10
  of 30 draws `lost_shard`, 20 measured, all failing). A `--resume` of that
  request was refused by the client (`params_unsupported_worker`: the
  re-dispatched 10-point shard came back with 30 corner reports), so the
  committed `mc-control-ss.report.json` is a clean fresh 30-unit re-submit
  with the same request file and base seed 10250182. The interrupted report
  is not committed; nothing from it enters any publication.
- Per-unit wall time on the fleet was 17-25 s class (transient bench, 100 ns
  of 150 MHz-class rings at 1 ps print step); the 240 s per-unit timeout
  carried a >=10x margin and no unit timed out.
- Every request declares `batch.max_units_per_job` 14 (14 x 240 s + 120 s
  overhead = 3480 s <= the 3600 s whole-job ceiling, issues #974/#976) and
  `batch.capacity_wait_s` 600.

## Numerical limitations

- Mismatch spread is the deck's own Pelgrom model under klt's per-sample
  seed; it is a model of population spread, not measured silicon.
- `.meas` edge times are interpolated between 1 ps solver steps (four-period
  averaging damps, but does not remove, that quantization).
- Two PVT points only (DR-0033's ratified subset); no claim about the rest of
  the corner space.

## How to reproduce

Use the recorded `repo_commit` for the exact deck bytes submitted to the fleet.

```sh
python3 sim/tools/mc_yield_campaign.py plan
python3 sim/tools/mc_yield_campaign.py run-set ro --outdir DIR   # submits mc-tt, mc-ss, mc-control-tt, mc-control-ss to the batch fleet
python3 sim/tools/mc_yield_campaign.py analyze DIR/mc-tt/report.json DIR/mc-ss/report.json DIR/mc-control-tt/report.json DIR/mc-control-ss/report.json
```

Request files `mc-{tt,ss,control-tt,control-ss}.request.json` are
generated (`emit --check` guards against drift); environment:
`KLT_SIM_BACKEND=batch`. The committed reports' `netlist_closure` pins the
deck and `design/ro_array_core.spice` to the hashes above.
