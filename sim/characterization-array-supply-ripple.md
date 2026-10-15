# Deterministic supply-ripple susceptibility of the buffered RO array

Issue [#414](https://github.com/2AMLogic/gf180-trng/issues/414). Status:
**complete for the declared grid.** The beat-frequency requests and both
convergence re-runs are recorded; the 2 MHz points are recorded from six
smaller requests (`nominal-lowf-p1..p3`, `binding-lowf-p1..p3`) carrying the
same 14 units that a single 7-unit request per corner could not finish within
the fleet's per-job ceiling. See "Results" and "Run status".

This is characterization of one named coupling path, not a verdict. It changes
no spec target, no decision record and no signoff verdict, and it makes no
claim about min-entropy, supply-filter sizing or a supply-network impedance
target.

## The gap it addresses

[`characterization-array-ring-coupling.md`](characterization-array-ring-coupling.md)
(Caveats, "Ideal supply") states that every coupling deck connects both ring
supplies through zero-volt ammeters to one *ideal* source, which has no
impedance for one ring's current to develop a voltage across; supply-network
coupling is a second path those decks cannot see. The array deck
`sim/tb/ro-array-core-pvt-q/` has the same structure, and
`layout/floorplan/README.md` records that supply filtering is unsized because no
supply-network impedance target exists. So the isolation argument has no
quantified answer to a *deterministic* supply disturbance at the ring pins.

## What the campaign tests

An ideal series sinusoid on a ring supply pin of the shipped buffered array
(`design/ro_array_core.spice`, blob `fd0aa75500320b36f980126377e3d07c71c0e6b1`),
read out as the edge-time displacement of each ring and of the rings' relative
phase at the injected frequency. Declared before any run (`sim/tb/ro-array-supply-ripple/README.md`,
`python3 sim/tools/supply_ripple.py plan`):

- corners: `tt`/27 C/3.30 V and the entropy-binding `ss`/125 C/3.63 V;
- placement: ring 1 only, and both rings in phase;
- amplitude: 0 (control), 10, 50, 150 mV peak;
- frequency: 2 MHz, and the corner's observed ring-frequency difference
  (10.50 MHz nominal, 7.65 MHz binding);
- numerical checks: the binding-corner beat point re-run at 5 ps and 2.5 ps
  against the 10 ps main grid, and a one-cycle-shorter fit window on every unit;
- 36 simulation units in 10 `klt sim` requests, about 1.3 CPU-hours (a planning
  estimate from one local probe; `python3 sim/tools/supply_ripple.py plan`),
  nothing run by CI or `sim/selftest.sh`. The 2 MHz grid of each corner is
  submitted as three requests of a control plus two perturbed units, the
  control repeated with an identical deck; the unit set, amplitudes,
  placements, frequency, corner and solver step are those of the original
  7-unit request. (The first declaration was 32 units in 6 requests; only the
  batching of the 2 MHz units changed.)

Because the binding corner already sits at the top of the 2.97-3.63 V envelope,
any positive excursion there leaves it; each perturbed rail is labelled `in` or
`OUT` of the envelope from its measured minimum and maximum rather than assumed.

## Results

Each row is a record under `sim/records/` (raw `report.json`, `request.json` and
`stderr.txt` beside it); the tables are the output of
`python3 sim/tools/supply_ripple.py analyze` and are reproduced in the records.
`x` is the displacement amplitude of the ring's edge times at the injected
frequency; `ffm` is the fractional-frequency modulation per millivolt of
injected ripple. The amplitude-0 row is the control: its tone is the fit and
quantization floor. The simulation is deterministic (no noise, no mismatch, no
seeds). Schematic-level deterministic susceptibility of
`design/ro_array_core.spice` (blob `fd0aa75500320b36f980126377e3d07c71c0e6b1`)
to an ideal series sinusoid on the ring supply pins; PDK `gf180mcuD`,
open_pdks `c6d73a35f524070e85faff4a6a9eef49553ebc2b`, ngspice-46.

Nominal, `tt`/27 C/3.30 V, 10.5 MHz, 10 ps step, 0.7 us
(`2026-10-15-ro-array-supply-ripple-nominal-beat-01`):

| placement | amp (mV) | rails | ring1 x (ps) | ring2 x (ps) | beat-phase x (ps) | ring1 ffm (ppm/mV) |
|---|---|---|---|---|---|---|
| control | 0 | - | 2.19 | 1.13 | 2.92 | n/a |
| ring1 | 10 | in | 48.8 | 1.13 | 49.3 | 322 |
| ring1 | 50 | in | 251 | 1.19 | 252 | 331 |
| ring1 | 150 | in | 756 | 1.16 | 756 | 332 |
| both | 10 | in | 48.9 | 49.4 | 4.26 | 323 |
| both | 50 | in | 251 | 248 | 12 | 331 |
| both | 150 | in | 756 | 747 | 32.7 | 332 |

Entropy-binding, `ss`/125 C/3.63 V, 7.65 MHz, 10 ps step, 0.7 us
(`2026-10-15-ro-array-supply-ripple-binding-beat-01`). The nominal rail already
sits at the top of the envelope, so every perturbed rail leaves it (`OUT`); these
are out-of-envelope excursions, reported as such, not in-envelope claims:

| placement | amp (mV) | rails | ring1 x (ps) | ring2 x (ps) | beat-phase x (ps) | ring1 ffm (ppm/mV) |
|---|---|---|---|---|---|---|
| control | 0 | - | 2.55 | 1.95 | 3.94 | n/a |
| ring1 | 10 | OUT | 64.2 | 1.97 | 64.8 | 309 |
| ring1 | 50 | OUT | 328 | 2.05 | 329 | 315 |
| ring1 | 150 | OUT | 988 | 1.87 | 988 | 317 |
| both | 10 | OUT | 63.9 | 64.5 | 6.01 | 307 |
| both | 50 | OUT | 328 | 325 | 16.8 | 315 |
| both | 150 | OUT | 987 | 976 | 45.6 | 316 |

Observations (synthetic aggressor only):

- The control tone (about 1-4 ps) is two orders of magnitude below the 10 mV
  response (about 49-65 ps), i.e. negligible by comparison, but it is not zero:
  it is a floor of the extraction, and the 10 mV rows are the smallest response
  clearly above it.
- The response is close to linear in amplitude from 10 to 150 mV (ffm 307-332
  ppm/mV across both corners; the 10 mV rows sit 2-3 percent below the 50 and
  150 mV rows at each corner), and the per-millivolt sensitivity is slightly
  lower at the binding corner (about 315 ppm/mV) than at nominal (about 331).
- A ring that does not carry the ripple does not respond (ring 2 stays at the
  control floor when only ring 1 is perturbed), so in this model the ripple does
  not couple between rings except through the injected pins.
- With both rails driven in phase the two rings move together and the relative
  (beat-phase) displacement is about 4-5 percent of a single-ring displacement
  at 50 and 150 mV (about 9 percent at 10 mV, nearer the extraction floor).
  In-phase ripple is therefore largely common-mode to the ring difference; this
  says nothing about unequal-phase or unequal-amplitude ripple (untested).

Numerical sensitivity, binding corner, 7.65 MHz, `both` 50 mV and the control,
re-run at finer steps (`...-conv-binding-beat-5p-01`, `...-conv-binding-beat-2p5-01`):

| step | control ring1 x (ps) | control ring2 x (ps) | both 50 mV ring1 x (ps) | ring2 x (ps) | beat-phase x (ps) | ffm (ppm/mV) |
|---|---|---|---|---|---|---|
| 10 ps | 2.55 | 1.95 | 328 | 325 | 16.8 | 315 |
| 5 ps | 2.58 | 1.98 | 328 | 325 | 16.8 | 315 |
| 2.5 ps | 2.57 | 1.99 | 328 | 325 | 16.8 | 315 |

The three-digit values do not change between 10 ps and 2.5 ps, so the step is
not what limits these numbers. The control floor moves by about 0.03 ps.

2 MHz points, 10 ps step, 2.7 us window. Each part carries its own control
(identical deck, so the three controls agree to the digit shown). Rows below are
in grid order; the records are
`2026-10-15-ro-array-supply-ripple-<corner>-lowf-p<k>-01` (k = 1..3).

Nominal, `tt`/27 C/3.30 V:

| placement | amp (mV) | rails | ring1 x (ps) | ring2 x (ps) | beat-phase x (ps) | ring1 ffm (ppm/mV) |
|---|---|---|---|---|---|---|
| control | 0 | - | 0.145 | 0.0821 | 0.214 | n/a |
| ring1 | 10 | in | 265 | 0.029 | 265 | 333 |
| ring1 | 50 | in | 1320 | 0.136 | 1320 | 333 |
| ring1 | 150 | in | 3970 | 0.146 | 3970 | 333 |
| both | 10 | in | 264 | 261 | 14.7 | 332 |
| both | 50 | in | 1320 | 1310 | 72.7 | 333 |
| both | 150 | in | 3970 | 3920 | 218 | 333 |

Entropy-binding, `ss`/125 C/3.63 V (every perturbed rail is `OUT` of the envelope,
as at 7.65 MHz):

| placement | amp (mV) | rails | ring1 x (ps) | ring2 x (ps) | beat-phase x (ps) | ring1 ffm (ppm/mV) |
|---|---|---|---|---|---|---|
| control | 0 | - | 0.0968 | 0.108 | 0.142 | n/a |
| ring1 | 10 | OUT | 252 | 0.165 | 252 | 316 |
| ring1 | 50 | OUT | 1260 | 0.305 | 1260 | 317 |
| ring1 | 150 | OUT | 3780 | 0.0619 | 3780 | 317 |
| both | 10 | OUT | 252 | 249 | 14.7 | 317 |
| both | 50 | OUT | 1260 | 1240 | 73.1 | 317 |
| both | 150 | OUT | 3780 | 3730 | 219 | 317 |

Observations at 2 MHz (synthetic aggressor only):

- The control tone (0.1-0.2 ps) is three orders of magnitude below the 10 mV
  response (252-265 ps).
- The response per millivolt (ffm 316-333 ppm/mV) is the same as at the beat
  frequency within about 5 percent at each corner, and linear in amplitude to
  within 0.5 percent; the 2 MHz displacement is about 5 times the beat-frequency
  one because the same fractional-frequency modulation integrates over a
  period 3.8-5.3 times longer.
- A ring that does not carry the ripple stays at the control floor, as before.
- In-phase ripple on both rails leaves a relative (beat-phase) displacement of
  5.5-5.8 percent of a single-ring displacement (14.7 ps against 265 ps at 10 mV,
  72.7 ps against 1320 ps at 50 mV; 219 ps against 3780 ps at 150 mV in the binding
  corner), i.e. largely common-mode, as at the beat frequency. This says nothing
  about unequal-phase or unequal-amplitude ripple (untested).
- At 150 mV the single-ring fit residual rises (nominal 16.5-16.9 ps against
  2.2-2.8 ps at lower amplitudes; binding 8.7-9.8 ps), so the single-tone model
  explains slightly less there (`tone explains` still rounds to 1.0000); read the
  150 mV rows as having a larger harmonic or non-sinusoidal remainder.
- No separate step-convergence or shorter-window re-run was made at 2 MHz; the
  convergence check above is at the beat point only, so numerical sensitivity at
  2 MHz is not bounded independently.

## Run status

The two `klt sim --backend batch` submits made from this issue's worktree did
not run:

1. the first stopped with `batch_no_capacity` (no Spot capacity in any pool);
2. a retry obtained a fleet job, which the runner rejected with
   `batch_runner_version_mismatch`: the fleet runner image carries klt 0.5.0
   and the submitting client is 0.7.0. The older client that matches the runner
   (`uvx --from klayout-tools==0.5.0`) has no `batch` backend, so no compatible <!-- klt-pin: historical -->
   client/runner pair exists today.

This is the fleet-image problem already tracked in
[2AMLogic/klayout-tools#2948](https://github.com/2AMLogic/klayout-tools/issues/2948)
and [#2851](https://github.com/2AMLogic/klayout-tools/issues/2851); no new
tool issue is warranted. The grid was **not** run as a local loop. Once the
runner image accepts the client, run the six requests with
`supply_ripple.py run` and mint records with the repository's append-only
conventions.

A further single-request retry on 2026-10-09 (`supply_ripple.py run nominal-beat`,
fleet job `klt-sim-d94c2476733f`, c7i.8xlarge Spot) was accepted by the fleet but
failed identically: exit 87, `runner_compatibility: mismatch` (runner klt 0.5.0,
client klt 0.7.0), all 7 units `batch_job_failed`, no measurements. The other
five requests were not submitted, and nothing was run as a local loop. No record
was minted; results remain pending.

The only simulation performed was an unrecorded two-unit local pipeline smoke
check (a control and one 150 mV unit at `tt`/27 C/3.30 V, 10.5 MHz, one corner)
to confirm that the deck's `alter` parameters take effect, that the `.meas` edge
rows come back, and that `supply_ripple.py analyze` reads a real `klt` report.
It is not evidence and is not recorded; no value from it appears here.

### Update 2026-10-15 (re-run after the runner image was redeployed)

The fleet now accepts the client (`runner_compatibility: match`, runner klt
0.7.0). Requests were submitted one at a time with `supply_ripple.py run`
(`KLT_SIM_BACKEND=batch`), nothing as a local grid:

- `nominal-beat` (job `klt-sim-8fa7c38d7357`), `binding-beat`,
  `conv-binding-beat-5p` and `conv-binding-beat-2p5`: all units `pass`;
  recorded (see "Results").
- `nominal-lowf` (job `klt-sim-10085c978b78`) and `binding-lowf` (job
  `klt-sim-4c7212e74d48`): the fleet job ran to its 3600 s whole-job ceiling
  (`state: timeout`, `exit_code: 124`, `elapsed_seconds: 3604`, m7i.4xlarge,
  `concurrency: 1`) and was killed; all 7 units of each were reported
  `batch_job_timeout` with no measurements. `klt` also warned that the request's
  `options.timeout_s` of 7200 s times 7 units exceeds the ceiling. That warning is
  advisory: the same warning was printed by the requests that did pass, and
  lowering `timeout_s` to 3480 s cannot make a job that is killed at 3600 s
  finish, so the committed requests were not edited.
- Two single-unit local diagnostic probes of the `nominal-lowf` deck (the
  control and the `both` 150 mV unit; one corner each, not recorded as evidence
  and not used in any table) each finished in about 48 s wall, so the units are
  not intrinsically long. The fleet jobs are far slower than that for the same
  deck (the passing `nominal-beat` job needed 2329 s for 7 units of a shorter
  window), consistent with the per-corner cost that grows with corners per job
  already described in 2AMLogic/klayout-tools#2970; no new tool issue was filed.
  Splitting the 2 MHz requests was left for a later increment (below).
- The `wall_time` in each record is the longest unit's `runtime_s` (units of a
  job report a job-scale time), not a sum.

### Update 2026-10-15 (2 MHz requests split into parts)

Each 2 MHz request was replaced by three requests (`<corner>-lowf-p1..p3`) that
together carry exactly the same 7 units (a test asserts the union equals the
declared grid); each part leads with its own zero-amplitude control. The
superseded `request-nominal-lowf.json` and `request-binding-lowf.json` are
removed from the generator; their fleet failures above stand as recorded. The
parts were submitted one at a time with `supply_ripple.py run`
(`KLT_SIM_BACKEND=batch`, nothing as a local grid), and all units of all six
parts passed on the first submit, each job finishing in well under a minute
(longest unit 33.7-39.9 s):

| request | fleet job |
|---|---|
| `nominal-lowf-p1` | `klt-sim-be91bc34af67` |
| `nominal-lowf-p2` | `klt-sim-4bbe251252a5` |
| `nominal-lowf-p3` | `klt-sim-bccb21ba5196` |
| `binding-lowf-p1` | `klt-sim-819597cbfe6b` |
| `binding-lowf-p2` | `klt-sim-668edd045d0a` |
| `binding-lowf-p3` | `klt-sim-35fa68b49079` |

So the 7-unit jobs were limited by units-per-job, not by the deck (consistent
with 2AMLogic/klayout-tools#2970). The bounded exit for a repeat timeout was not
needed.

## Tested versus not tested

Tested offline (`sim/tests/test_supply_ripple.py`): tone extraction recovers a
known amplitude and phase under drift; a zero-amplitude control yields a
negligible tone; a deterministic tone is distinguished from a seeded stochastic
residual (the tone is detected and the residual rms equals the noise sigma, while
pure noise is not detected); ring edge-time displacement and relative-phase
extraction recover known displacements, including common-mode cancellation; the
committed requests match the declared grid; the cited PVT records' ring
frequencies still match the grid's provenance.

Not tested, and unbounded by this work even once the campaign runs:

- the actual supply network: source impedance, shared-trunk IR drop, return
  paths, decoupling, and any aggressor that would produce the ripple;
- ripple on the buffer/combiner rail (`vdd`) or on ground/substrate, and ripple
  with unequal phase or amplitude between the two rings;
- extracted parasitics (this is the schematic DUT; the extracted-PMOS
  body-bias and well-tie questions, #339/#411, are separate);
- stochastic behaviour: no noise or mismatch is simulated, so the experiment
  separates nothing from jitter and adds no seeds;
- other PVT corners, other frequencies and amplitudes, and large-signal
  (harmonic) ripple.

## How to read a result when it exists

A sensitivity is a number of picoseconds of edge-time displacement (or ppm of
fractional frequency) per millivolt of injected ripple, for a synthetic ideal
aggressor. It is deterministic, so it must not be added to the sizing law as
random jitter, and it says nothing about a built chip's supply noise until a
supply-network model exists to supply the ripple.
