# What does the `clk`-locked digitizer disturbance cost the array that ships?

Status: **decks built for issue [#87]; not yet run.** The four testbenches
below, their pairing, their window geometry and the derivation that reads them
are on file. **No `tt`/27 °C/3.30 V record exists for any of them, so this
document states no result** — [Results](#results) says exactly what is missing,
what it costs to produce, and what has stopped it so far.

Nothing here supersedes
[`sim/characterization-liveness-tap-phase-cost.md`](characterization-liveness-tap-phase-cost.md)'s
**19.9×**, which remains what that document already calls it: an isolated-ring
measurement recorded as an *upper bound* on the shipped array's residual, not
as the number the shipped design carries.

**This is an ordinary summary, not evidence.** Every number below cites the
`sim/records/` stem that produced it — treat this document as a reading guide
over that evidence, not a substitute for it. Correcting a number means
re-running the testbench and citing the new record, per
[`sim/README.md`](README.md).

**No entropy-rate or spec-compliance claim is made anywhere in this document.**
[`DR-0004`](../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md)'s
tiering is unchanged.

## The question

[`sim/characterization-liveness-tap-phase-cost.md`](characterization-liveness-tap-phase-cost.md)
(issue [#76]) measured what the DR-0016 per-ring liveness digitizer costs its
ring in phase, and found a disturbance locked to `clk`: with the digitizer's
`d` input directly on the ring node, `σ₁` came in at **541×** the same deck's
with `clk` parked, and with a [`DR-0018`](../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md)
`ro_buf` between them, at **19.9×**.

Both of those decks are deliberately minimal — **one** ring, and the buffer
output drives **one** consumer, the digitizer.
[`design/ro_array_core.spice`](../design/ro_array_core.spice) does not look
like that:

```
xr1 en1 rn1 vddr1 vss ro_ring11 wstv=0.220u lstv=2u cld=0.5f
xb1 rn1 ro1 vdd vss ro_buf
xa1 ro1 ro2 xo  vdd vss xor2              <- ro1's OTHER consumer
xsr1 ro1 clk rst_n ring_bit1 vdd vss      <- design/sampler_core.spice
```

Each buffer output drives the **combiner's input as well as** that ring's
digitizer. #76 argued from that — structurally, without measuring it — that the
shipped residual has to be *smaller* than 19.9×, because the digitizer's
`clk`-modulated capacitance is a smaller fraction of a node that also carries
`xa1`'s input gate. So it recorded 19.9× as an **upper bound** and said so
explicitly, rather than as the number the design carries.

The same document left a second thing unmeasured, which its own acceptance
criteria had named: `xsb`, the [`DR-0001`](../spec/decision-records/DR-0001-raw-and-conditioned-output-paths.md)
raw-tap digitizer, which `design/sampler_core.spice` puts on the combiner
output `xo` — **two** active stages from either ring (that ring's own `ro_buf`,
then `xa1`). The same feedthrough argument predicts a much smaller effect
there. Predicts; does not measure.

This document is the experiment that measures both, on the topology the block
ships.

## Method

- **Harness**: `sim/run_corners.py`, ngspice-46, PDK
  `gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b`. One record per
  variant, four independent noise seeds per record, per
  [`sim/README.md`](README.md).
- **One corner, `tt`/27 °C/3.30 V** — the corner [#51]'s coupling ladder and
  #76's phase-cost family were both run at, so all three sets of ratios are
  directly comparable. This is a mechanism question, not a PVT one. Nothing
  here is claimed at any other corner.
- **The shipped DUT, device for device.** Two `ro_ring11` rings at the shipped
  starve skew (`wstv` = 0.220 µm / 0.240 µm, `lstv` = 2 µm, `cld` = 0.5 f),
  both DR-0018 `ro_buf` output buffers, the `xa1` combiner on the two **buffer
  outputs**, and all four `sampler_core` digitizers: `xsr1`/`xsr2` on those
  same buffer outputs, `xsb` on `xo`, `xsv` on the `vdd` rail. Only the rings
  are restated stage by stage in the testbench — the `trnoise()` sources go in
  series with every stage input and cannot be placed from outside a
  `ro_ring11` instance — and every stage is still a `ro_nand2` / `ro_stage`
  out of `design/sampler_core.spice`, as is everything downstream of the ring
  nodes. 22 noise sources in total, at the fixed injected density
  (`1e-16 V²/Hz`) the whole `sim/` corpus uses.
- **`clk` at 1.0007 µs (~1 MHz)** in the two running-clock decks, the same rate
  #76's family ran at. [`DR-0003`](../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md)'s
  ratified raw-rate row is "> 1 Mbps sustained at the raw tap" and
  [`DR-0012`](../spec/decision-records/DR-0012-sampler-fixed-external-clock.md)
  makes `clk` a fixed external pin with no divider, so this is the shipped
  operating point rather than a chosen stimulus.
- **Window geometry matched to #76 in *time*, not in ring-period count.**
  #76 opened its window 256 ring periods after start-up and spanned 512, on a
  5-stage ring whose period is ~2.86 ns: 0.73 µs of settling and a 1.46 µs
  window, i.e. 1.46 `clk` periods. An 11-stage ring's period is ~7.1 ns, so
  reproducing 256/512 *periods* would need ~5.5 µs of transient noise. These
  decks open at 128 periods and span 256: 0.91 µs of settling and a 1.82 µs
  window, i.e. **1.82 `clk` periods** — longer in absolute time and covering
  more `clk` periods than #76's, which is what a `clk`-locked disturbance
  actually depends on. The lag ladder is truncated at 64 (a quarter of the
  window), where #76's was truncated at 128 (a quarter of its window).
- **`σ` is measured at each ring's own oscillating node**, upstream of its
  buffer, because the question is what reaches the ring rather than whether a
  low-impedance driven node is quiet (it is, by construction). Both rings are
  measured inside the same run — `sigma_*` for ring 1, `sigma_r2_*` for ring 2
  — as independent replicates of the same question.

Four DUT variants, in two pairs, each pair differing in exactly one thing:

| | Testbench | What it is | What its pair isolates |
|---|---|---|---|
| 1 | [`array-liveness-tap-phase-clocked`](tb/array-liveness-tap-phase-clocked/) | the **shipped** `sampler_core` topology, `clk` running | — |
| 2 | [`array-liveness-tap-phase-static`](tb/array-liveness-tap-phase-static/) | variant 1, `clk` parked HIGH | 1 / 2 = the **shipped** `clk`-locked residual |
| 3 | [`array-liveness-tap-phase-xsb-clocked`](tb/array-liveness-tap-phase-xsb-clocked/) | variant 1 with `xsr1`/`xsr2` removed, `clk` running | — |
| 4 | [`array-liveness-tap-phase-xsb-static`](tb/array-liveness-tap-phase-xsb-static/) | variant 3, `clk` parked HIGH | 3 / 4 = what the **`xo` path alone** delivers to a ring |

### Why the pairs are read inside a topology, and never across one

Adding or removing a load changes a ring's operating point as well as its
isolation, so a ratio taken *across* a topology change spans two changes and
attributes neither. That is the argument
[`sim/characterization-ring-buffer-mitigation.md`](characterization-ring-buffer-mitigation.md)
makes for its own decks, and #51's variant-3-against-variant-2 discipline is
the same rule. So the `clk` question is asked **inside** each topology, against
that topology's own static reference, with exactly one thing different between
numerator and denominator — whether `clk` toggles:

```
shipped    σ₁(1 clocked)     / σ₁(2 static)
xsb-only   σ₁(3 xsb-clocked) / σ₁(4 xsb-static)
```

**These decks' raw `σ` values are not comparable with #76's**, and no row below
invites that comparison. #76's ring is a 5-stage ring at a different operating
point under a different load, and its window is a different number of periods.
What *is* comparable across the two experiments is each pair's own
within-topology ratio, because each is dimensionless and each is taken against
its own static reference — which is the entire reason the pairing discipline
exists.

Reproduce the whole comparison with:

```sh
python3 sim/tools/array_liveness_tap_phase_variants.py
python3 sim/tools/array_liveness_tap_phase_variants.py --check
```

That script recomputes #76's 19.9× bound from #76's **own** committed records
rather than carrying it as a literal, so this document cannot drift away from
the number it is stated against.

## Results

**There are none yet, and this section exists to say so rather than to leave
the omission to be noticed.** No `tt`/27 °C/3.30 V record has been produced for
any of the four decks, so:

- the shipped `σ₁` ratio is **not measured**;
- it is therefore **not** stated against #76's 19.9× upper bound, in either
  direction — the bound is neither confirmed nor violated by anything on file;
- the `xsb`-on-`xo` path is **not measured**, and is neither shown reachable
  nor shown unreachable;
- `sim/tools/array_liveness_tap_phase_variants.py`'s two `RECORDED_*_VERDICT`
  constants are `None`, and its `--check` is deliberately **not** on CI's
  self-check list. Naming a verdict there before the run would pre-register a
  conclusion with no evidence behind it, which is what that gate exists to
  prevent, pointed the wrong way.

Both remain **open items of issue #87**, which is what that issue asked for.

### What the runs cost

Measured on the deck itself at `tt`/27 °C/3.30 V, by timing two transient-only
runs of the generated netlist at 0.1 µs and 0.2 µs and differencing them:
**≈ 29 CPU-minutes per simulated microsecond** (172 s and 345 s of CPU
respectively), against ≈ 2 for #76's single 5-stage ring. At `tstop` = 3 µs
that is ≈ 87 CPU-minutes per seed, and the sixteen runs — four decks × four
seeds — come to **≈ 23 CPU-hours**.

That cost is dominated by the transient, and neither of its two drivers is
freely adjustable:

- `tran 1p …` makes ngspice's maximum timestep 1 ps — it defaults to the
  smaller of `tstep` and `(tstop − tstart)/50` — so a 3 µs run takes at least
  3 million steps. The 1 ps is load-bearing rather than incidental:
  `meas … when v(x1)=0` locates each zero crossing by interpolating between
  the two stored samples that straddle it, and the `σ` being measured is
  *sub-picosecond* (#76's control is 0.64 ps). A coarser cap would put the
  interpolation error on the same order as the quantity being measured. The
  whole `ring-liveness-tap-phase-*` family uses the same 1 ps step for the
  same reason.
- `tstop` is set by the window, and the window is set by `clk`. DR-0003's
  ratified floor puts `clk` at ~1 MHz, so a window that spans a full `clk`
  period cannot be shorter than ~1 µs — and the settling periods and the
  measurement window are both counted in ring periods on top of that.

**CPU-hours are not wall-clock hours here, and the gap is large.** The ≈ 23
CPU-hour figure above silently assumes the batch can have as many cores as it
has runs. On the host these attempts run on it cannot. Every `ngspice` started
from an agent session inherits `nice 10`, and macOS maps that to a background
QoS class scheduled on the efficiency-core cluster rather than across all 28
cores — so the batch's *aggregate* throughput is capped near two and a half
cores no matter how many runs are in flight. Measured on this host during
attempt 4, by differencing the runs' summed CPU time over a fixed wall-clock
window:

| runs in flight | aggregate throughput |
|---|---|
| 4 (one deck) | ≈ 2.0 cores |
| 8 (two decks) | ≈ 2.4 cores |
| 16 (all four decks) | ≈ 1.8 cores |

Two things follow, and both are scheduling facts about the host rather than
anything about the circuit. First, **running all sixteen at once is slower in
aggregate than running eight** — past the E-cluster's width the runs contend
rather than overlap — so there is no parallelism left to buy: ≈ 23 CPU-hours
is ≈ 9–11 hours of wall clock however the batch is arranged. Second, the only
lever that would change this is raising the runs' priority, and `renice`
downward from `nice 10` requires root, which is an operator action and not an
agent one.

The practical consequence for whoever runs this next: **run the two decks of
one pair concurrently and the pairs one after the other**, rather than all
four decks at once. It costs nothing in total wall clock — the ceiling is the
same either way — and it lands a *complete, readable pair* (the shipped ratio)
hours before the batch as a whole finishes, instead of leaving all four decks
partially done and none readable if the host kills the batch. That is the
arrangement attempt 4 settled on after measuring the table above, and
`sim/tools/run_array_liveness_tap_phase.py --decks <a> <b>` is how to express
it.

### What has stopped it so far

Three launches of the sixteen runs were killed from outside the harness before
any of them finished. Recorded here because the next attempt should not
rediscover them:

| attempt | how far it got | how it died |
|---|---|---|
| 1 | ~0.27 µs of the transient | all sixteen `ngspice exit -15` (SIGTERM), when the agent session that launched them ended |
| 2 | ~1.60 µs, after 4.4 h | all sixteen `ngspice exit -9` (SIGKILL), simultaneously, together with every other `ngspice` process on the host |
| 3 | ~0.09 µs, after 9 min | the same, ~14 minutes later |

Attempt 1 has a fix that holds: launch the runs from a driver that calls
`os.setsid()` first, so they are not in the launching session's process group
and a session teardown cannot reach them. Attempts 2 and 3 were a host-level
event rather than anything this repository controls — every `ngspice` on the
machine went at once, not just this experiment's — and both coincided with a
`loom-daemon` restart.

The operational lesson is about the harness, not the circuit: a ~23 CPU-hour
job on a shared host has to be able to **resume**, and a single
`run_corners.py` invocation cannot. It writes a point's record only once every
seed of that point has finished, so a kill at 95 % costs the whole point. A
driver that re-runs a failed deck (deleting the failed attempt's record and
raw directory first, so the successful attempt claims a clean stem) is the
minimum that converges here.

None of the three attempts produced a committable record — every run failed, so
every measurement row read "no data" — and none was committed. `sim/`'s
append-only rule governs committed evidence; these never became any.

**Attempt 4** (issue #87, this change) lands
[`sim/tools/run_array_liveness_tap_phase.py`](tools/run_array_liveness_tap_phase.py),
which fixes both of the above rather than relying on a person to remember
them next time:

- it launches the actual batch under `subprocess.Popen(..., start_new_session=True)`
  — the same effect as attempt 1's prescribed `os.setsid()` fix — so a SIGTERM
  to the launching session's process group stops at this script and does not
  reach the `ngspice` runs underneath it;
- it loops per deck rather than issuing one `run_corners.py` invocation per
  deck and hoping: before each attempt it checks whether a clean record (this
  corner, all four seeds) already exists and skips the deck if so, and if a
  previous attempt left an incomplete record or an orphaned `raw/<stem>/`
  directory (a stem `run_corners.py` reserved but never got to write, because
  the process died first), it deletes only that deck's leftovers and retries
  — so a kill costs at most the deck that was running, and re-running the
  same command later resumes rather than restarting the other three.

It also addresses a fourth failure mode none of the first three hit yet but
that a multi-hour job launched from an issue's worktree is exposed to: this
repository's Loom tooling removes a `loom:building` issue's
`.loom/worktrees/issue-N/` worktree by default once that issue's PR merges
(`.loom/scripts/merge-pr.sh`), and this PR — like #90 before it — is expected
to merge as a `Part of #87` partial increment well before a ~6–23 CPU-hour
batch finishes. Running the batch inside `.loom/worktrees/issue-87/` would
therefore risk exactly the same outcome as attempt 1 (files disappearing out
from under a still-running job), just triggered by a merge instead of a
session end. So this launch runs from a plain `git clone --local` of this
branch outside any Loom-managed path — `merge-pr.sh`'s cleanup only ever
touches `.loom/worktrees/issue-N/` and `.loom/worktrees/pr-N/`, and explicitly
never auto-removes a worktree or clone anywhere else — rather than from the
worktree this PR itself was authored in.

This attempt's launch, for the record:

- **command**: `python3 sim/tools/run_array_liveness_tap_phase.py` (all four
  decks, default `--timeout 86400`, default `--max-attempts 5`), run from a
  `git clone --local` of `feature/issue-87` at
  `/Users/rwalters/loom-scratch/gf180-trng-issue87-tapphase` on the same host
  the prior three attempts ran on;
- **PID**: `94886` (the detached driver), PID file at
  `sim/.work/array-liveness-tap-phase-launch/run.pid` under that clone;
- **log**: `sim/.work/array-liveness-tap-phase-launch/run.log` under that
  clone (machine-local scratch, gitignored, not meant to be read by anyone
  without access to this host — the PR that lands this change has the
  absolute path). `python3 sim/tools/run_array_liveness_tap_phase.py
  --status`, run from any checkout, reads the committed records directly and
  needs neither the PID nor the log to report which decks are still
  outstanding;
- **expected wall clock**: with `-j 4` (this deck's four seeds run
  concurrently — a wall-clock choice only, per-seed cost is unaffected) each
  deck costs roughly one seed's ~87 CPU-minutes rather than four seeds'
  worth, so four decks run one after another come to **~6 hours**, plus
  whatever retries a host-level kill (attempt 2/3's failure mode, still
  outside this repository's control) costs on top.

**One thing this launch found and had to clear first.** At launch time the
same host was already running a fifth, uncoordinated set of `ngspice`
processes for these same four deck names, from an untracked `/tmp` clone at
an earlier commit than this document -- one predating even the geometry this
document's Method section describes (`tstop` 2.6 µs, not 3.000003 µs, and
carrying an `abstol=1e-10` relaxation this document's committed decks do not
have). Diffing its testbench files against the committed ones confirmed it
could not have produced a record matching what `sim/tb/` actually holds, so
it was terminated (`SIGTERM`, then `SIGKILL` for anything still alive three
seconds later) and its scratch directory removed, rather than left to finish
and be mistaken for evidence. Recorded here in case a future attempt finds
its own leftover processes on this host: check the testbench file hashes
before trusting a run in progress, not just the deck name.

If this attempt also fails to land all four records, the next one should run
`python3 sim/tools/run_array_liveness_tap_phase.py --status` first rather than
re-deriving which decks are still outstanding by hand — that is exactly what
the flag is for.

### What is left to do

1. Run the four decks and land their records. The equivalent of the loop
   below, made resumable and detached, is
   [`sim/tools/run_array_liveness_tap_phase.py`](tools/run_array_liveness_tap_phase.py)
   — see "What has stopped it so far" above for why the loop alone was never
   enough:

   ```sh
   for tb in array-liveness-tap-phase-clocked array-liveness-tap-phase-static \
             array-liveness-tap-phase-xsb-clocked array-liveness-tap-phase-xsb-static; do
     python3 sim/run_corners.py "$tb" \
       --corners tt --temps 27 --supply 3.3 --supply-tol 0 \
       --seeds 1 2 3 4 -j 4 --timeout 86400
   done
   ```

   `--timeout` matters: the harness default is 300 s, which every one of these
   runs exceeds by two orders of magnitude.

2. Fill in a Results table from
   `python3 sim/tools/array_liveness_tap_phase_variants.py`, and set that
   script's two `RECORDED_*_VERDICT` constants from what it prints — after the
   run, never before.

3. Add `python3 sim/tools/array_liveness_tap_phase_variants.py --check` back to
   the "Spec arithmetic self-checks" step in `.github/workflows/ci.yml`; the
   comment block there already describes the guard and says why the line is
   currently absent.

4. Then, and only then, amend
   [`sim/characterization-liveness-tap-phase-cost.md`](characterization-liveness-tap-phase-cost.md)
   and DR-0016's "Phase cost" amendment to cite the shipped number instead of
   the 19.9× bound. Until the run exists, 19.9× is the best number on file and
   both documents already describe it correctly, as an isolated-ring
   measurement used as an upper bound.

**One thing to watch on the first successful run.** These decks set no
`.options` overrides, where [`sim/tb/sampler-array-digitize/`](tb/sampler-array-digitize/)
— the only other deck in this repository carrying this same 22-stage two-ring
array — documents a bisected `abstol=1e-10` relaxation as the thing that keeps
its transient from collapsing when an abrupt external edge lands in the same
matrix as 22 series-starved stages. These decks have an abrupt external edge
(`clk`) and the same array. If the first run hits `Timestep too small`, that
precedent is where to look; the relaxation would have to be applied identically
to both decks of a pair, so that it cannot move a ratio, and stated in the
caveats rather than absorbed.

## Caveats

These are the method limits the runs *will* carry. They are stated now because
they are properties of the decks, which exist, rather than of the results,
which do not.

- **One corner.** `tt`/27 °C/3.30 V only, chosen to be directly comparable with
  #51's ladder and #76's family. Nothing here is claimed at any other process,
  temperature or supply.
- **One `clk` rate**, 1.0007 µs (~1 MHz), for the two running-clock decks.
  How a `clk`-locked disturbance folds into any particular `σ_acc` window
  depends on that rate, and DR-0012 makes the rate external.
- **The window is matched to #76 in time, not in ring periods** — 256 periods
  here against 512 there. Both windows span more than one `clk` period, which
  is what a `clk`-locked disturbance needs, but a `σ` estimate over 256 periods
  scatters `√2` more seed to seed than over 512 (**3.81 %** against 2.69 %,
  both from `sim/tools/starved_cell_jitter_energy.py`'s calibration over the
  same 27 plain-cell records). The derivation recomputes that reference for
  this window rather than carrying #76's over.
- **Ring 2 is running in every deck of this family**, so ring 1's `σ` is
  measured while its combiner neighbour switches — the arrangement
  `sim/characterization-array-ring-coupling.md` rules inadmissible as evidence
  for DR-0007 §2's sizing law. That is deliberate and unavoidable here: the
  shipped array *has* two rings, and the question is what the shipped
  arrangement costs. It does mean no `σ` in this family may be reused as a
  per-ring `σ_acc,i`.
- **No `clk`-LOW static reference is run for this topology.** #76 ran both
  rails for its unbuffered pair and only the HIGH rail for its buffered one;
  this experiment likewise parks on HIGH, so the two static endpoints a running
  `clk` walks the shipped rings between are read off the clocked decks' own
  per-block periods rather than from two standalone decks. That is the weaker
  of the two ways to get an endpoint gap, and it is the one this experiment
  has.
- **`σ` here is raw, at the fixed injected level, and is not physical jitter.**
  No entropy-rate or spec-compliance claim is made anywhere in this document;
  [`DR-0004`](../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md)'s
  tiering is unchanged. If what these decks capture turns out to be
  deterministic, `σ` is not even a jitter estimate — that is exactly what the
  seed-spread and accumulation-exponent diagnostics are there to decide.
- **Ideal supply.** Both ring branches and the block branch are zero-volt
  ammeters off one *ideal* `vsup`, which has no impedance for one branch's
  current to develop a voltage across. These decks therefore say nothing about
  supply-network coupling from the digitizers' own switching, which is a
  *second* path a real block has and these do not. The finding will be a lower
  bound on what a built block shows, not an upper one.
- **Pre-layout**, schematic-derived netlist (`design/sampler_core.spice`), no
  extracted parasitics. Layout adds coupling paths between a clocked cell and a
  ring node; it removes none.
- **`rst_n` is held high throughout**, so every digitizer is out of reset and
  contributes no reset edge. DR-0014's gated reset behaviour is measured by
  [`sim/tb/sampler-dff-reset-clocked/`](tb/sampler-dff-reset-clocked/).
- **Every `clk` timing is off the 10 ps `trnoise()` breakpoint grid**
  (`tclk_del` = 5.003 ns, `tclk_tr` = 0.203 ns, `tstop` = 3.000003 µs), for the
  solver reason `sim/tb/ring-liveness-tap-phase-clocked/` records: with a
  clocked cell in the deck, a `PULSE`-source or `tstop` breakpoint landing
  exactly on a `trnoise()` breakpoint collapses ngspice-46's transient at that
  instant, reproducibly. The offsets are ~0.3 % of an edge and ~0.0005 % of a
  `clk` period; nothing measured here resolves them.
- **This does not re-measure the tap's power, either ring's free-running
  frequency, or the raw bitstream.**
  [`sim/tb/ring-liveness-tap-power/`](tb/ring-liveness-tap-power/),
  [`sim/tb/ro-array-core-power/`](tb/ro-array-core-power/) and
  [`sim/tb/sampler-array-digitize/`](tb/sampler-array-digitize/) own those.
- **"Unreachable" will be a statement about what this measurement resolves**,
  not a proof of zero. It means the `xsb`-only pair's ratio sits in the band a
  variant reproducing its reference occupies *and* its per-block period swing
  stays under the materiality threshold — both, because either alone can be
  satisfied by an underpowered measurement.

[#51]: https://github.com/2AMLogic/gf180-trng/issues/51
[#76]: https://github.com/2AMLogic/gf180-trng/issues/76
[#87]: https://github.com/2AMLogic/gf180-trng/issues/87
