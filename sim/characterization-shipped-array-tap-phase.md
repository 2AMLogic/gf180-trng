# What does the `clk`-locked digitizer disturbance cost the array that ships?

Status: **measured for issue [#87]; all four decks run.** Both pairs are on
file — each pair at `tt`/27 °C/3.30 V, four seeds per deck, and each pair's two
decks produced on one host as this family's pairing rule requires — so both
questions this document exists to answer have answers:

> **The array that ships carries a 3.46× `clk`-locked residual on its ring-1
> node (5.80× on ring 2), against the 19.9×
> [`sim/characterization-liveness-tap-phase-cost.md`](characterization-liveness-tap-phase-cost.md)
> recorded as an *upper bound* on exactly that number. The bound is confirmed,
> by 83 %**, and the structural reason #76 gave for calling it a bound — the
> shipped `ro_buf` output drives `xa1` as well as its own digitizer — is
> measured rather than argued. The residual is **not** removed: 3.46× is still
> outside the 3× band a variant reproducing its reference occupies, and the
> modulation is locked to `clk`.

> **The `xsb`-on-`xo` path is unreachable at this corner.** With the two
> per-ring liveness digitizers removed, so that the DR-0001 raw-tap digitizer's
> pass gate on the combiner output `xo` is the only `clk`-driven load left
> downstream of a ring, running `clk` moves ring 1's `σ₁` to **0.96×** its own
> `clk`-parked control (ring 2: **1.00×**) and leaves the per-block period
> swing at **0.006 %**, the same value the control shows. `xo` is two active
> stages from either ring node — `xa1`, then that ring's own `ro_buf` — and on
> this evidence nothing measurable survives them. "Unreachable" here means what
> [Caveats](#caveats) says it means: below what this measurement resolves, not
> proved zero.

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
  window, i.e. 1.46 `clk` periods. These decks' 11-stage ring runs at a
  measured 6.6702 ns, so reproducing 256/512 *periods* would need ~5.1 µs of
  transient noise. They open at 128 periods and span 256 instead: 0.85 µs of
  settling and a **1.71 µs** window, i.e. **1.71 `clk` periods** — longer in
  absolute time and covering more `clk` periods than #76's, which is what a
  `clk`-locked disturbance actually depends on. The lag ladder is truncated at
  64 (a quarter of the window), where #76's was truncated at 128 (a quarter of
  its window). (These decks were *designed* against a ~7.1 ns estimate of the
  11-stage period, which is where the "0.91 µs / 1.82 µs" figures in the
  records' own append-only Caveats notes come from; the periods above are the
  measured ones and are ~6 % shorter. Nothing in the geometry depends on the
  difference — the window is specified in ring periods, and it is the same 128
  and 256 either way.)
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

**All four decks have a record.** Each pair is four seeds at `tt`/27 °C/3.30 V
with `clk` as the only difference between its two decks, and **each pair's two
decks were produced on the same host as each other** — which "What the runs
cost" below explains is a requirement here and not a coincidence. The two pairs
were run on *different* hosts from each other, and that is admissible precisely
because nothing below crosses them: every ratio is taken inside one pair.

| | variant 1 [`…-clocked-01`](records/2026-08-03-array-liveness-tap-phase-clocked-01.md) `clk` running | variant 2 [`…-static-01`](records/2026-08-03-array-liveness-tap-phase-static-01.md) `clk` parked HIGH | variant 3 [`…-xsb-clocked-01`](records/2026-08-03-array-liveness-tap-phase-xsb-clocked-01.md) no `xsr1`/`xsr2`, `clk` running | variant 4 [`…-xsb-static-01`](records/2026-08-03-array-liveness-tap-phase-xsb-static-01.md) the same, `clk` parked HIGH |
|---|---|---|---|---|
| host (`platform:`) | `macOS-26.6-arm64` | `macOS-26.6-arm64` | `Linux-…-aws-x86_64` | `Linux-…-aws-x86_64` |
| `T₀` ring 1 / ring 2 | 6.6702 ns / 6.2344 ns | 6.6739 ns / 6.2378 ns | 6.6768 ns / 6.2405 ns | 6.6768 ns / 6.2405 ns |
| `σ₁` ring 1 (raw, fixed injected level) | **4.4490 ps** | **1.2864 ps** | **1.3966 ps** | **1.4581 ps** |
| `σ₁` ring 2 | 4.0233 ps | 0.6934 ps | 0.7312 ps | 0.7290 ps |
| accumulation exponent, lags 1…64 | 0.943 | 0.250 | 0.257 | 0.252 |
| seed-to-seed spread of `σ₁` | 1.37 % | 4.09 % | 1.23 % | 4.42 % |
| per-block period swing, 16 blocks | 0.136 % | 0.006 % | 0.006 % | 0.006 % |

The two questions this document exists to answer are the two within-pair ratios
of that table's `σ₁` row:

```
  pair                                             ring 1     ring 2
  shipped array (xa1 + both digitizers)             3.46x      5.80x
  xsb on xo only (no per-ring digitizer)            0.96x      1.00x
  #76's bound (5-stage, one consumer)              19.90x        n/a
```

### The shipped `clk`-locked residual is 3.46×, and #76's bound holds

```
shipped   σ₁(1 clocked) / σ₁(2 static)  =  4.4490 ps / 1.2864 ps  =  3.46×   (ring 1)
                                                                     5.80×   (ring 2)
#76's upper bound on that same number                             = 19.90×
```

**3.46× is 83 % below the 19.90×
[`sim/characterization-liveness-tap-phase-cost.md`](characterization-liveness-tap-phase-cost.md)
recorded as an upper bound on it, so the bound is confirmed** — by a margin far
outside the 10 % this family requires before calling a direction measured
rather than coincidental. The reason #76 gave for calling it a bound was
structural and untested: the shipped `ro_buf` output drives `xa1` as well as
its own digitizer, so the digitizer's `clk`-modulated capacitance is a smaller
share of that node's load than in #76's deck, where the buffer drives the
digitizer alone. That is now measured. Ring 2 — an independent replicate inside
the same runs, on the `wstv` = 0.240 µm ring — agrees in direction at 5.80×.

**It is not removed**, and it is unmistakably `clk`-locked rather than
incidental. The clocked deck's sixteen per-block mean periods alternate between
≈ 6.6740 ns and ≈ 6.6649 ns on a cycle of about six blocks; six blocks is 144
ring periods, which at 6.6702 ns is 0.96 µs — the 1.0007 µs `clk` period to
within the block quantisation. The static deck's blocks are flat at 0.006 %.
The accumulation exponent says the same from the other end: 0.943 with `clk`
running against 0.250 parked, where a phase random walk accumulates as `L^0.5`
and #76's quiet decks measured 0.35–0.42. An exponent near 1 is coherent
accumulation.

**The two diagnostics disagree about the magnitude, and that disagreement is
part of the result.** `σ₁` at 3.46× is outside the 1×–3× band this repository's
variant ladders treat as reproducing a reference. The per-block period swing —
which does not use the `σ` estimator at all — is 0.136 % against this family's
0.3 % materiality threshold, i.e. *below* it. Both are on file and neither is
dropped for the other: what the shipped array carries at this corner is large
enough to move a phase statistic and too small to count as a material period
modulation. Against #76's isolated buffered deck (0.96 % swing, 19.9×), the
shipped fan-out cuts the swing ~7× and the `σ₁` ratio ~5.8×.

**One of #76's signatures did not carry over, and is not claimed.** Its
buffered residual was deterministic on the seed-spread test — 0.12 % against a
2.69 % reference. The shipped one is 1.37 % against this window's 3.81 %
reference, *above* the ⅓-of-reference line, so it classifies as "not collapsed"
rather than deterministic. The weaker claim is the one stated.

Reproduce with `python3 sim/tools/array_liveness_tap_phase_variants.py`, which
recomputes both the 19.90× bound and the 3.46× ratio from the committed records
rather than from any literal in this document.

### The `xsb`-on-`xo` path does not reach a ring node

```
xsb-only  σ₁(3 xsb-clocked) / σ₁(4 xsb-static)  =  1.3966 ps / 1.4581 ps  =  0.96×  (ring 1)
                                                                             1.00×  (ring 2)
```

Variants 3 and 4 are the shipped array with the two DR-0016 per-ring liveness
digitizers **removed**, so the only `clk`-driven pass gate left anywhere
downstream of a ring is `xsb`'s, on the combiner output `xo`. Running `clk`
against parking it changes **nothing this measurement can resolve**:

- `σ₁` lands at **0.96×** its own static control on ring 1 and **1.00×** on
  ring 2 — inside the 1×–3× band this repository's variant ladders treat as a
  variant reproducing its reference. Ring 1's is *below* 1.00×, which is the
  direction a disturbance cannot produce: a `clk`-locked modulation adds to the
  period-to-period spread the estimator measures, so it can only push this
  ratio up. A ratio under 1 is estimator scatter, and 4 % of it is well inside
  one seed's worth — variant 4's own seed-to-seed spread of `σ₁` is 4.42 %;
- the **per-block period swing is 0.006 %** in both decks — the same value the
  shipped *static* control shows, against the 0.136 % the shipped clocked deck
  shows and a 0.3 % materiality threshold. This is the diagnostic that does not
  use the `σ` estimator at all, and it sees a flat ring;
- the **accumulation exponent is 0.257 clocked against 0.252 parked**, where
  the shipped clocked deck's is 0.943. Nothing is accumulating coherently.

Both of the two tests this document's [Caveats](#caveats) require for the word
"unreachable" are therefore satisfied — the ratio sits in the reproduce-your-
reference band *and* the swing stays under the materiality threshold — so the
derivation classifies this pair `unreachable` and
`RECORDED_XSB_VERDICT` is set to it.

**What that word does and does not mean.** It means the disturbance is below
what this measurement resolves at this corner, not that it is zero. `xo` is two
active stages from either ring node — `xa1`, then that ring's own `ro_buf` —
and #76's own feedthrough argument (a change in a gate's output load returns to
its input through the gate-drain capacitance of its own devices, attenuated,
never blocked) says the path is open in principle. What is measured is that two
stages of attenuation put whatever survives under a per-block swing of 0.006 %
and inside a 4 %-scatter `σ₁` estimate. The measurement's own floor is the
claim's ceiling.

**The direction agrees with the shipped pair**, which is the consistency check
worth stating: one `clk`-driven pass gate one stage from the ring (`xsr1` on
`ro1`, behind that ring's `ro_buf`) is worth 3.46×, and one `clk`-driven pass
gate two stages from the ring (`xsb` on `xo`) is worth nothing measurable. The
per-stage attenuation implied by #76's ladder — 541× on the raw node down to
19.9× behind one buffer — is more than enough to account for that.

#### Why these ratios are host-sound

"What the runs cost" below records that this experiment's runs were launched on
two machines that do not produce bit-identical floating point, and draws the
rule that follows: **a control has to be produced on the same host as its
numerator**, or the ratio spans two changes and attributes neither. Every ratio
above satisfies that:

| ratio | host of numerator and denominator |
|---|---|
| shipped, 3.46× / 5.80× | `macOS-26.6-arm64-arm-64bit-Mach-O`, both records |
| `xsb`-only, 0.96× / 1.00× | `Linux-7.0.0-1009-aws-x86_64-with-glibc2.39`, both records |
| #76's bound, 19.90× | `Linux-7.0.0-1009-aws-x86_64-with-glibc2.39`, both records |

The two pairs of *this* experiment are on different hosts from each other, and
that is admissible for exactly one reason: **no arithmetic anywhere in this
document divides a number from one pair by a number from another.** Each ratio
is dimensionless and taken within one host against its own control, so the
comparison between ratios is sound. No raw `σ` is carried across a host
boundary; the `σ₁` row of the Results table is printed per deck for
transparency, not to be divided across columns 2 and 3.

### Issue #87's acceptance criteria

| criterion | state |
|---|---|
| `σ_acc` on the shipped array vs. a matched `clk`-quiet control, one change | **met** — variants 1/2, 3.46× (ring 1), 5.80× (ring 2) |
| the shipped ratio stated explicitly against #76's 19.9× upper bound | **met** — confirmed below it, by 83 % |
| the `xsb`-on-`xo` path measured, or shown unreachable with reasoning | **met** — variants 3/4, `unreachable` at this corner, reasoning above |
| reported at `tt`/27 °C/3.30 V; the summary document cites the shipped number | **met** — all four decks at that corner; [`sim/characterization-liveness-tap-phase-cost.md`](characterization-liveness-tap-phase-cost.md) and `DR-0016` amendment A4 both cite 3.46× |

### What the runs cost

Measured on the deck itself at `tt`/27 °C/3.30 V, by timing two transient-only
runs of the generated netlist at 0.1 µs and 0.2 µs and differencing them:
**≈ 29 CPU-minutes per simulated microsecond** (172 s and 345 s of CPU
respectively), against ≈ 2 for #76's single 5-stage ring. At `tstop` = 3 µs
that is ≈ 87 CPU-minutes per seed, and the sixteen runs — four decks × four
seeds — come to **≈ 23 CPU-hours**. (That was measured on the macOS host. The
same measurement on the Linux host gives ≈ 36 CPU-minutes per simulated
microsecond, and CPU-hours turn out to be the wrong planning unit for this
experiment in any case — see "Correction: the Linux host is not slow, the
concurrency was" below, which is a *measured retraction* of what this section
previously concluded about that host.)

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
has runs. On the **macOS/arm64 host** attempt 4 ran on it cannot. Every
`ngspice` started from an agent session inherits `nice 10`, and macOS maps that
to a background QoS class scheduled on the efficiency-core cluster rather than
across all 28 cores — so the batch's *aggregate* throughput is capped near two
and a half cores no matter how many runs are in flight. Measured on that host
during attempt 4, by differencing the runs' summed CPU time over a fixed
wall-clock window:

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

The practical consequence, on that host: **run one pair at a time rather than
all four decks at once.** It costs nothing in total wall clock — the ceiling is
the same either way — and it lands a *complete, readable pair* (the shipped
ratio) hours before the batch as a whole finishes, instead of leaving all four
decks partially done and none readable if the host kills the batch. That is
the arrangement attempt 4 settled on after measuring the table above, and
`sim/tools/run_array_liveness_tap_phase.py --decks <a> <b>` is how to express
it. **A pair is the unit of work on either host; how many `ngspice` run at once
inside it is a separate, host-specific question**, and the correction below
answers it for the Linux host (the answer there is one).

#### Correction: the Linux host is not slow, the concurrency was

**An earlier revision of this section reported "≈ 8.7 ps of transient per
second of wall clock" for the Linux/AWS host and concluded from it that a deck
pair costs "on the order of 100 h" there and that these decks must be run on
macOS. That conclusion was wrong, and the `xsb` pair was subsequently measured
on the Linux host in 2.42 h.** The 8.7 ps/s figure itself is not withdrawn —
it was correctly measured — but it is a *per-run rate inside an eight-wide
concurrent batch*, and it was read as if it were a property of the host. It is
a property of the arrangement.

The mistake had a single mechanical cause:
`sim/tools/run_array_liveness_tap_phase.py` hardcoded `-j 4` in `CORNER_ARGS`,
on the assumption that one `ngspice` process is single-threaded and four of
them therefore fit on any multi-core host for free. **ngspice-46 on this Linux
host is not single-threaded on this deck.** Measured directly, by running
transient-only copies of the generated `xsb-clocked` netlist (`tt`/27 °C, the
2.97 V grid point of the same sweep) at two `tstop` values on the
otherwise-idle host and reading wall and CPU time off each:

| `tstop` | wall | CPU | CPU / wall |
|---|---|---|---|
| 0.05 µs | 16.26 s | 123.06 s | 7.57 cores |
| 0.10 µs | 30.29 s | 231.32 s | 7.64 cores |
| difference (0.05 µs of transient) | 14.03 s | 108.26 s | 7.72 cores |

So **one run of this deck already occupies ~7.6 of the host's 8 cores**, and
running four or eight alongside it puts 30–60 runnable threads on 8 cores.
Measured aggregate throughput does not saturate under that; it *collapses*:

| arrangement | transient per second of wall clock |
|---|---|
| 1 run alone (the difference row above) | **3564 ps/s** |
| 8 runs concurrently (attempt 5) | 8.7 ps/s each, **69.7 ps/s in aggregate** |

That is ~51× less total throughput from eight times the processes. The single
`ngspice` measured at "7.8 ps/s" in the earlier revision was itself started
while the eight-wide batch was running, which is why it agreed with them; on a
quiet host the same deck runs ~450× faster than that.

**What the corrected arrangement actually cost.** With `DEFAULT_JOBS = 1` — one
seed at a time, ngspice's own internal parallelism left alone — the `xsb` pair
ran to completion on the Linux/AWS host in one attempt, no retries:

| deck | seeds | wall clock (`wall_time:` in the record) |
|---|---|---|
| `array-liveness-tap-phase-xsb-clocked` | 4, sequential | 75.5 min (1.26 h) |
| `array-liveness-tap-phase-xsb-static` | 4, sequential | 70.0 min (1.17 h) |
| **the pair** | 8 runs | **145.5 min = 2.42 h** |

≈ 17.5–19 min per seed for a 3.000003 µs transient, i.e. ≈ 2600–2900 ps/s
including the harness's own netlist generation and measurement parsing. At
`-j 1` a deck's `wall_time:` is both its summed per-run cost *and* its elapsed
time, since only one run is ever in flight — so those two figures are committed
evidence in the records themselves, not a number read off a scratch log. (The
launcher's own log agrees: `21:35:13Z` start, `batch finished in 2.42h` at
`2026-08-04T00:00:42Z`. It lives under `sim/.work/`, is gitignored, and is not
evidence for anything the records do not already carry.)

Two honest qualifications on this correction:

- **It does not overturn the macOS numbers above.** Those were measured at
  `-j 4` on that host, and nobody has since measured that host at `-j 1`. The
  `nice`-and-E-cluster analysis stands as written for the arrangement it
  describes; whether macOS at `-j 1` would also be several times faster than
  macOS at `-j 4` is *not measured*, and is the obvious next thing to check
  before planning another batch there.
- **It reinforces this section's "more parallelism is worse past a pair"
  finding rather than contradicting it.** The macOS table already showed
  aggregate throughput *falling* from 8 runs to 16. On Linux the same effect
  is present at far greater strength and starts at 2 runs rather than at 16,
  because a single run there is already using the whole machine.

The Linux host also does *more* CPU work per simulated microsecond than the
macOS figure at the top of this section: 108.26 CPU-s per 0.05 µs is ≈ **36
CPU-minutes per simulated microsecond**, against ≈ 29 measured on macOS. It
finishes far sooner anyway, because it spends ~7.6 cores on one run instead of
~0.5 cores on each of four. **CPU-hours were the wrong planning unit for this
experiment throughout**; wall clock per seed at a stated concurrency is the
right one, and that is what the table above reports.

**And the two hosts must not be mixed inside a pair.** Each pair's ratio is
only a one-change comparison if `clk` toggling is the *only* difference between
numerator and denominator. `sigma_1` here is a few picoseconds on a transient
driven by 22 `trnoise()` sources; x86-64 and arm64 do not produce
bit-identical floating point (FMA contraction, `libm`, extended-precision
intermediates), so the two hosts do not walk the same trajectory. Both pairs
satisfy the rule: the shipped pair's two records both carry `platform:
macOS-26.6-arm64-arm-64bit-Mach-O`, and the `xsb` pair's two both carry
`platform: Linux-7.0.0-1009-aws-x86_64-with-glibc2.39`. Each published ratio is
therefore a one-change ratio in this respect as well as in the circuit — which
is the exact failure the pairing discipline in "Why the pairs are read inside a
topology" exists to prevent. Two pairs on two hosts is fine; one pair split
across two hosts would not have been.

This is also worth noting against #76's family, every record of which carries
the `Linux-…-aws-…` platform: comparing this experiment's *ratio* with #76's
*ratio* is still sound, because each is dimensionless and taken within one host
against its own control, but no raw `σ` may be carried across the two. Results
compares only the ratios, and no raw `σ` from either family appears in the
other's arithmetic.

### What stopped it, five times, and what finally worked

**It took six launches to land these four decks.** Four were killed from
outside the harness before any of their runs finished — the first three of the
full sixteen, and a later concurrent one of eight on the other host. Attempts 4
and 6 are the ones that produced the committed records: attempt 4 the shipped
pair on the macOS host, attempt 6 the `xsb` pair on the Linux host. All six are
written up below, because a ~20-CPU-hour experiment that fails five times is
itself a finding about this repository's tooling, and the next long batch
should not rediscover any of it.

The failures split into three unrelated causes, and it is worth naming them
separately because fixing one did nothing for the others: **(a)** the runs
being reachable by a session teardown (attempts 1, 5); **(b)** a host-level
event outside this repository's control (attempts 2, 3); **(c)** the launcher
oversubscribing the host so badly that no run could finish inside any
reasonable timeout (attempt 5's real cause, diagnosed only after attempt 6 —
see the correction under "What the runs cost").

| attempt | how far it got | how it died |
|---|---|---|
| 1 | ~0.27 µs of the transient | all sixteen `ngspice exit -15` (SIGTERM), when the agent session that launched them ended |
| 2 | ~1.60 µs, after 4.4 h | all sixteen `ngspice exit -9` (SIGKILL), simultaneously, together with every other `ngspice` process on the host |
| 3 | ~0.09 µs, after 9 min | the same, ~14 minutes later |
| 5 (concurrent, Linux host) | 0.184 µs, after 5 h 52 min | all eight `ngspice exit -15` (SIGTERM) at 2026-08-03T20:42:27Z, ~8 min *before* their own `timeout 21600s` deadline; the driver and the second wave it had just launched went with them |

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

None of the first three attempts produced a committable record — every run failed, so
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

**Attempt 5** ran at the same time as attempt 4, on the *other* host, and is
the row above. It is recorded because of what it cost and what it shows, not
because it produced anything: a `clocked` + `static` pair, four seeds each,
eight `ngspice` in flight, launched 2026-08-03T14:50:40Z from a scratch driver
inside `.loom/worktrees/issue-87/` on the Linux/AWS host. It ran 5 h 52 min,
reached 184 ns of the 3.000003 µs transient, and was SIGTERMed — so
`run_corners.py` wrote both records with every measurement row reading `no
data (all runs failed to converge)`, and neither was committed. Three things
it establishes for whoever runs this next:

1. **Attempt 5 was doomed at launch and no kill was needed to make it fail**:
   at the 8.7 ps/s each of its eight concurrent runs was managing, a 3 µs
   transient needs ~96 h, against the 6 h `timeout` its driver gave it.
   ~~*The Linux host cannot finish this deck; launch these decks on the macOS
   host.*~~ **That was this document's original conclusion and it was wrong.**
   The 96 h followed from the *concurrency*, not from the host: attempt 6 ran
   the same two decks on the same Linux host one seed at a time and finished
   the pair in 2.42 h. See "Correction: the Linux host is not slow, the
   concurrency was" above; the struck-through sentence is left visible rather
   than silently deleted, because it is the claim this document got wrong and
   a reader who saw it before should be able to find it retracted.
2. **A `--timeout` that a run cannot finish inside is a silent failure**, not a
   loud one. `run_corners.py` returned `rc=0` and the driver logged `END … rc=0`
   for both decks; only the per-point line (`FAIL … ngspice exit -15, no
   measurements parsed`) and the record's own `no data` rows say otherwise. A
   driver that gates on the shell exit status of `run_corners.py` will conclude
   a dead batch succeeded and move on — attempt 5's driver did exactly that,
   launching its second wave into the same trap.
3. **Running the batch inside `.loom/worktrees/issue-87/` is still the wrong
   place**, for the reason attempt 4 already gives above, and attempt 5 is the
   worked example: its raw output sat untracked inside a Loom-managed worktree
   for six hours, where any worktree teardown or `git clean` would have taken it.
   That output is now preserved outside the repository rather than committed —
   `sim/`'s append-only rule governs evidence, and a record whose every row
   reads `no data` is not evidence.

**Attempt 6** landed the `xsb` pair, on the Linux/AWS host, in one attempt with
no retries. It changed exactly one thing against attempt 5: **seeds run one at
a time instead of four at a time.** Nothing about the decks, the geometry, the
corner or the host differed.

- **command**: `python3 sim/tools/run_array_liveness_tap_phase.py --foreground
  --jobs 1 --max-attempts 5 --decks array-liveness-tap-phase-xsb-clocked
  array-liveness-tap-phase-xsb-static`, started 2026-08-03T21:35:13Z;
- **finished** 2026-08-04T00:00:42Z — `batch finished in 2.42h; failed decks:
  none`;
- **result**: both records `status: valid` with every measurement row
  populated, four seeds each, both `platform:
  Linux-7.0.0-1009-aws-x86_64-with-glibc2.39`.

Two things this attempt establishes, on top of the throughput correction it
produced:

1. **`-j 4` was the root cause of attempt 5, not a wall-clock preference.** The
   launcher hardcoded it in `CORNER_ARGS`, which meant every launch on this
   host oversubscribed it ~4× over an already-saturating single run. The
   default is now `DEFAULT_JOBS = 1`, with a `--jobs` flag and a comment block
   recording the measurement, so raising it again requires measuring first.
2. **A `--status` flag that reads committed records, not PIDs, is what made
   resuming cheap across five dead sessions.** Every attempt after the first
   started by asking the repository which decks still had no clean record,
   rather than reconstructing that by hand from logs on a host the next agent
   might not even be on.

It also ran **inside `.loom/worktrees/issue-87/`**, which attempt 4's write-up
above argues against and attempt 5 was the worked example against. That was
survivable here only because no PR merged during the 2.42 h it took; the
argument is unchanged and the scratch-clone arrangement is still the right one
for a batch expected to outlive a merge. Recorded rather than tidied away.

### What is left to do

**Nothing, for issue #87's own acceptance criteria** — all four are met (see
"Issue #87's acceptance criteria" above), all four decks have committed
records, `RECORDED_SHIPPED_VERDICT` and `RECORDED_XSB_VERDICT` are both set
from what the derivation printed after the runs,
`python3 sim/tools/array_liveness_tap_phase_variants.py --check` is on
`.github/workflows/ci.yml`'s "Spec arithmetic self-checks" list, and
[`DR-0016`](../spec/decision-records/DR-0016-per-ring-liveness-monitor.md)'s
"Phase cost" section carries amendment A4 citing the shipped 3.46× alongside
the isolated-ring 19.9× and the `xsb`-unreachable result.

What this experiment leaves open for someone else, none of it blocking:

1. **Only one corner.** Everything here is `tt`/27 °C/3.30 V. Whether the 3.46×
   residual grows or shrinks at the DR-0015 entropy-binding corner is not
   measured, and the ratio is not obviously corner-independent — it is a ratio
   of two loaded ring periods.
2. **Only one `clk` rate.** DR-0012 makes `clk` external, so the rate is not a
   design constant an attacker cannot move; #86 swept three rates for the
   *bit-level* question and found no rate dependence there, but this document's
   phase question has been asked at one rate only.
3. **What to do about the 3.46×, if anything.** This document measures; it
   proposes no design change. A bigger buffer, a `clk`-gated digitizer, or
   nothing at all are all still open, and whoever picks that up should size the
   problem from 3.46× rather than from #76's isolated 19.9×.
4. **Whether the macOS host is also faster at `-j 1`.** Its throughput table
   was measured at `-j 4` and has not been re-measured since the Linux
   correction. Worth one afternoon before planning another batch there.

**The `abstol` worry did not materialise, and can be dropped.** This section
previously flagged that these decks set no `.options` overrides, where
[`sim/tb/sampler-array-digitize/`](tb/sampler-array-digitize/) -- the only other
deck in this repository carrying this same 22-stage two-ring array -- needs a
bisected `abstol=1e-10` relaxation to keep its transient from collapsing when
an abrupt external edge lands in the same matrix as 22 series-starved stages.
These decks have an abrupt external edge (`clk`) and the same array, so the
concern was well founded. It did not happen: **all sixteen runs of all four
decks** converged with no override, and the only diagnostic in any of their logs
is the PDK's routine `m=xx on .subckt line` warning. No deck in this family
needs an `.options` line the others do not, so no ratio in it can be moved by
one.

## Caveats

These are the method limits this family carries. They are properties of the
decks, so they apply equally to both pairs' results above.

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
- **"Unreachable" is a statement about what this measurement resolves**, not a
  proof of zero. It means the `xsb`-only pair's ratio sits in the band a variant
  reproducing its reference occupies *and* its per-block period swing stays
  under the materiality threshold — both, because either alone can be satisfied
  by an underpowered measurement. Both are satisfied (0.96× and 0.006 %), and
  the floor is what it is: variant 4's own seed-to-seed spread of `σ₁` is
  4.42 %, so this pair could not have resolved a disturbance smaller than a few
  per cent of `σ₁` however it came out. A path with two stages of attenuation
  on it is exactly where that floor bites first.
- **The two pairs are on different hosts.** The shipped pair is
  `macOS-26.6-arm64`, the `xsb` pair `Linux-…-aws-x86_64`. Each ratio is taken
  within its own pair on its own host, which is the property the one-change
  discipline needs, but no raw `σ` may be divided across the two — see "Why
  these ratios are host-sound". None is, anywhere in this document.

[#51]: https://github.com/2AMLogic/gf180-trng/issues/51
[#76]: https://github.com/2AMLogic/gf180-trng/issues/76
[#87]: https://github.com/2AMLogic/gf180-trng/issues/87
