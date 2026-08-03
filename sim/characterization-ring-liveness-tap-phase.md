# What does the DR-0016 liveness digitizer cost the ring it observes, in phase?

Status: measurement complete for issue [#76]. **On the raw ring node the
digitizer costs `σ₁` a factor of 550×, and the disturbance is phase-locked to
`clk` by construction — it *is* `clk`, re-drawn as a ring period.** The
[`DR-0018`](../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md)
per-ring buffer the shipped block has carried since [#82] removes **96.5 %** of
it and leaves **20×**, which is still deterministic and still `clk`-locked.

**This document is an ordinary summary, not evidence.** Every number below
cites the `sim/records/` stem that produced it — treat this document as a
reading guide over that evidence, not a substitute for it. Correcting a number
means re-running the testbench and citing the new record, per
[`sim/README.md`](README.md).

**No entropy-rate or spec-compliance claim is made anywhere in this document.**
[`DR-0004`](../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md)'s
tiering is unchanged, and nothing here measures a sampled bit.

## The question

[`sim/characterization-array-ring-coupling.md`](characterization-array-ring-coupling.md)
(issue [#51] / PR #67) indicts a specific arrangement: **a ring node driving
the input of a cell whose internal nodes something else is driving**. It
measured `σ₁` **28.6×** higher than the same ring with the neighbour held on a
rail, against **1.06×** for the same gate load with the neighbour quiet — so
the load was innocent and the neighbour's *switching* was the mechanism.

[`DR-0016`](../spec/decision-records/DR-0016-per-ring-liveness-monitor.md)'s
per-ring liveness digitizers put each ring's observation node on a
`sampler_dff` `d` input. That input is not a gate: it is one source/drain
terminal of the input transmission gate (`XMtdp`/`XMtdn` in
`design/sampler_core.spice`), whose other terminal is the master latch node
and whose gates are driven by **`clk`**.

`sim/tb/ring-liveness-tap-power/` measured what those digitizers cost the
rings in **power** (+28.53 µW at the power-binding corner, DR-0016
§Power/area cost). Nothing measured what they cost the rings in **phase**.
This document closes that gap.

## Why the mechanism is not the one #51 found, and has to be measured its own way

Issue #51's mechanism was charge injected backwards into a ring node through
the gate capacitance of a cell whose inputs a *neighbouring ring* was walking:
a disturbance at the beat frequency `|f₁ − f₂|`, incommensurate with anything.

A `clk`-driven pass gate does something different in kind. When `clk` is low
the gate is transparent and the ring node drives the master inverter's gate
through it; when `clk` is high the gate is opaque and the ring node sees only
the pass devices' junction and overlap capacitance. A running clock therefore
does not inject a rare impulse into the ring — it **modulates the ring's own
load between two values, at the clock rate**.

That shapes the whole experiment:

1. **The disturbance is predictable from runs in which nothing switches.**
   Measure the ring's period with the pass gate shut, and again with it open,
   and the amplitude of the modulation is known before any clocked run exists.
2. **It is phase-locked to `clk` by construction**, because `clk` *is* the
   modulating waveform. That is the property `layout/floorplan/README.md`
   flagged as the reason this case is not obviously smaller than #51's: an
   incommensurate ring-to-ring beat averages over many samples, a
   `clk`-correlated disturbance does not, and `clk` is an external pin
   ([`DR-0012`](../spec/decision-records/DR-0012-sampler-fixed-external-clock.md))
   whose rate is an integrator's — or an attacker's — choice.

So the load-bearing test is not "is `σ` bigger" but **"is the measured `σ₁`
the one a two-level modulation between the two static periods predicts"**:

```
p            = (T_open − T_bar) / (T_open − T_shut)     duty, from the clocked run's own mean period
σ₁_predicted = |T_open − T_shut| · sqrt(p · (1 − p))
```

Every term on the right is measured in a **different deck** from the `σ₁` on
the left. Nothing in it is fitted.

## Method

- **Harness**: `sim/run_corners.py`, ngspice-46, PDK
  `gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b`. One record per
  variant; four independent noise seeds per record, per
  [`sim/README.md`](README.md).
- **One corner, `tt`/27 °C/3.30 V** — the corner issue #51's variants were run
  at, so the two families are directly comparable. Nothing here is claimed at
  any other corner.
- **One window geometry, #51's**: opened 256 periods after start-up, spanning
  512 periods, so the accumulation exponent is fitted over lags 1…128. Every
  variant additionally reproduces, inside the same run, the 16-period
  start-up window (`sigma_startup16_*`).
- **One clock rate, 1 MHz.**
  [`DR-0003`](../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md)'s
  ratified raw-rate row is "> 1 Mbps" sustained at the raw tap and DR-0012
  makes the sample clock a fixed external input, so 1 MHz is the **slowest
  clock the shipped block is specified to run at** — the rate at which a
  `clk`-correlated disturbance arrives least often, and therefore the most
  favourable rate to the digitizer that the specification permits. It is
  deliberately not `ring-liveness-tap-power`'s 100 MHz measurement clock,
  whose own manifest says it bears no resemblance to DR-0012's real rate.
  Note the sign of the argument: the **amplitude** of this mechanism does not
  depend on the clock rate at all — a faster clock does not make the
  disturbance bigger, it makes it more frequent.
- **Six DUT variants plus #51's own control, each one change apart:**

  | | Testbench | Digitizer taps | `clk` |
  |---|---|---|---|
  | 0 | [`ro-ring5-starved-jitter-long`](tb/ro-ring5-starved-jitter-long/) | — (**control**, digitizers absent) | — |
  | 1 | [`ring-liveness-tap-phase-shut`](tb/ring-liveness-tap-phase-shut/) | the raw ring node | held HIGH (gate opaque) |
  | 2 | [`ring-liveness-tap-phase-open`](tb/ring-liveness-tap-phase-open/) | the raw ring node | held LOW (gate transparent) |
  | 3 | [`ring-liveness-tap-phase-clocked`](tb/ring-liveness-tap-phase-clocked/) | the raw ring node | **running, 1 MHz** |
  | 4 | [`ring-liveness-tap-phase-buffered-shut`](tb/ring-liveness-tap-phase-buffered-shut/) | a `ro_buf` output | held HIGH |
  | 5 | [`ring-liveness-tap-phase-buffered-open`](tb/ring-liveness-tap-phase-buffered-open/) | a `ro_buf` output | held LOW |
  | 6 | [`ring-liveness-tap-phase-buffered-clocked`](tb/ring-liveness-tap-phase-buffered-clocked/) | a `ro_buf` output | **running, 1 MHz** |

  Variant 0 is issue #51's own committed control — the same delay cell at the
  same injected density with nothing attached. It is the "digitizers absent"
  row issue #76 asks for, and it is **cited, not re-run**
  ([`2026-08-01-ro-ring5-starved-jitter-long-02`](records/2026-08-01-ro-ring5-starved-jitter-long-02.md)).

  Variants 1–3 are the arrangement issue #76 indicts: the digitizer on the
  ring's own oscillating node — what `sampler_core.sch` built between [#65]
  and [#82]. Variants 4–6 are the arrangement the block ships **today**, in
  which `ro_array_core` re-drives its exported `ro1`/`ro2` pins from a
  per-ring `ro_buf` ([`DR-0018`](../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md))
  and the digitizers therefore tap a buffer output.

  Variants 1/2 stand to variant 3 exactly as variants 4/5 stand to variant 6,
  so the buffered and unbuffered arrangements are judged by the same
  one-change ratio (does `clk` switch) and by the same static-pair prediction.

- **Raw σ, not scaled.** Every record is at the same corner with the same
  fixed injected density, so the per-corner device-noise scaling
  `starved_cell_jitter_energy.py` applies is a common factor and is
  deliberately omitted. The numbers below are directly comparable to each
  other and to #51's, and are **not** physical jitter.

Reproduce the whole comparison with:

```sh
python3 sim/tools/ring_liveness_tap_phase.py
python3 sim/tools/ring_liveness_tap_phase.py --check
```

## Results

All rows at `tt`/27 °C/3.30 V, 4 seeds each (the control's 8), σ raw at the
fixed injected level, same 512-period window opened 256 periods after
start-up:

| | variant | record | `T₀` | `σ₁` | `σ₁`/control | exponent | seed spread |
|---|---|---|---|---|---|---|---|
| 0 | control, nothing attached | [`…starved-jitter-long-02`](records/2026-08-01-ro-ring5-starved-jitter-long-02.md) | 2.5635 ns | 0.641 ps | 1.00× | 0.421 | 3.9 % |
| 1 | raw tap, `clk` HIGH | [`…tap-phase-shut-01`](records/2026-08-03-ring-liveness-tap-phase-shut-01.md) | 2.7472 ns | 0.647 ps | **1.01×** | 0.375 | 2.3 % |
| 2 | raw tap, `clk` LOW | [`…tap-phase-open-01`](records/2026-08-03-ring-liveness-tap-phase-open-01.md) | 3.4507 ns | 0.885 ps | **1.38×** | 0.368 | 1.8 % |
| 3 | raw tap, `clk` **running** | [`…tap-phase-clocked-01`](records/2026-08-03-ring-liveness-tap-phase-clocked-01.md) | 3.0818 ns | **352.9 ps** | **550.9×** | 0.953 | **0.01 %** |
| 4 | buffered tap, `clk` HIGH | [`…buffered-shut-01`](records/2026-08-03-ring-liveness-tap-phase-buffered-shut-01.md) | 2.8740 ns | 0.695 ps | 1.09× | 0.411 | 3.0 % |
| 5 | buffered tap, `clk` LOW | [`…buffered-open-01`](records/2026-08-03-ring-liveness-tap-phase-buffered-open-01.md) | 2.8466 ns | 0.673 ps | 1.05× | 0.450 | 1.3 % |
| 6 | buffered tap, `clk` **running** | [`…buffered-clocked-01`](records/2026-08-03-ring-liveness-tap-phase-buffered-clocked-01.md) | 2.8578 ns | **13.51 ps** | **21.1×** | 0.971 | **0.17 %** |

**Only the two clocked rows move**, and they move by a lot. Every static
load — both of the digitizer's operating points, buffered and unbuffered —
sits within 1.01×–1.38× of the digitizers-absent control, with an ordinary
jitter signature (exponent 0.37–0.45, seed spread 1.3–3.9 %). This is #51's
finding again, on a different cell: **the load is innocent; the switching is
the mechanism.**

### The one-change ratio

Numerator and denominator differ in exactly one thing — does `clk` switch:

| tap point | vs its `clk`-HIGH control | vs its `clk`-LOW control |
|---|---|---|
| the raw ring node | **545.7×** | 398.9× |
| a `ro_buf` output (shipped since [#82]) | **19.4×** | 20.1× |

Taking the larger of each pair, **the buffer removes 96.50 % of the
`clk`-switching excess and leaves 20.08×**. Squared — which is what
[`DR-0007`](../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)
§2 substitutes for a per-ring contribution — a **297 800×** over-statement
becomes a **403×** one.

For scale: the same one-change ratio for #51's XOR-combiner coupling is
**27.10×** unbuffered and **2.87×** buffered (8.24× squared), per
[`characterization-ring-buffer-mitigation.md`](characterization-ring-buffer-mitigation.md).
**This path is 20× larger than that one before the buffer (545.7× against
27.10×) and 7× larger after it (20.08× against 2.87×)** — 49× larger in the
squared form DR-0007 §2 actually uses.

### It is not "like" a clock disturbance — it *is* the clock

Three independent signatures, all agreeing, and the third is the strongest
evidence in this document.

**Seed independence.** A genuine 512-period `σ₁` estimate scatters ~2.7 %
seed to seed (calibrated on 27 plain-cell records, `reference_spread` in
`starved_cell_jitter_energy.py`). The five static rows scatter 1.3–3.9 %.
The clocked rows scatter **0.01 %** and **0.17 %**. Whatever they measure is
not noise.

**Accumulation exponent.** A phase random walk accumulates as `lag^0.5`. The
five static rows fit 0.37–0.45. The clocked rows fit **0.953** and **0.971** —
near-linear, the signature of a deterministic drift, over the whole lag range
1…128. There is no collapse anywhere in that range because the modulation
period (1 µs ≈ 324 ring periods at variant 3's `T₀`, half-period ≈ 162) is
beyond lag 128 at both ends; this is #51's beat signature with the beat
deliberately moved out past the window, by running the clock at the slowest
rate the specification permits.

**The prediction from two decks in which nothing switches.** This is the one
that closes the question:

| | Δ between the two static periods | duty at the shut point | `σ₁` **predicted** | `σ₁` **measured** | ratio |
|---|---|---|---|---|---|
| raw ring node | 703.51 ps | 0.524 | 351.3 ps | 352.9 ps | **1.004×** |
| buffered tap | 27.46 ps | 0.409 | 13.501 ps | 13.507 ps | **1.000×** |

Both predictions come entirely from decks whose clock never moves, and both
land on the clocked measurement — the buffered one to four significant
figures. The measured `σ₁` **is** the two-level load modulation, and the
modulating waveform is `clk`.

The same fact is visible directly, without any arithmetic, in the per-bin
period series (sixteen 48-period bins across the run, in ps):

```
variant 1 (clk HIGH)   2747.2 2747.2 2747.2 2747.2 2747.2 2747.1 2747.1 2747.2 …
variant 2 (clk LOW)    3450.6 3450.7 3450.7 3450.7 3450.7 3450.7 3450.7 3450.6 …
variant 3 (clk 1 MHz)  3146.5 2747.2 2747.2 2747.2 3198.0 3450.7 3450.7 3011.4
                       2747.2 2747.1 2747.2 3341.5 3450.7 3450.7 2878.0 2747.2
```

Variant 3's bin series is a **square wave between variants 1 and 2's own
periods**, to five significant figures, with the transitional bins landing at
intermediate values exactly where a 48-period bin straddles a clock edge. The
ring is not being perturbed by something clock-correlated; it is running at
one of two clean frequencies, and `clk` selects which.

### What the buffer does, and does not, do

The `DR-0018` buffer shrinks the modulation amplitude from **703.51 ps to
27.46 ps** — 96.10 % of the amplitude, 96.50 % of the `σ₁` excess. It does not
remove it, and what is left is a *different* mechanism, which the sign shows:

- **Unbuffered**, `clk` LOW (transparent) makes the ring **slower** (3.4507 ns
  against 2.7472 ns). The master inverter's gate is hung directly on the ring
  node; more load, longer period. Straightforward.
- **Buffered**, `clk` LOW makes the ring **faster** (2.8466 ns against
  2.8740 ns). The ring node's own load never changes — what changes is the
  load on the *buffer's output*, and a heavier output load slows the buffer's
  own transitions, which feeds back to the ring node through the buffer's
  gate-drain capacitance with the opposite sign.

So the residual 20× is reverse feedthrough through the buffer, not
transmission through it. That matters for what would fix it: more isolation
between the digitizer and the shared node (a second stage, or a digitizer
whose input load does not depend on `clk`), not a bigger buffer.

**The 20× is not the shipped array's number, and is an upper bound on it.**
In the shipped `ro_array_core` the buffer output drives `xa1` as well as the
digitizer; here it drives one digitizer only. The modulated capacitance is the
same either way, but it is a smaller fraction of a node that also carries
`xa1`'s input capacitance, so the shipped feedthrough can only be smaller.
How much smaller is **not measured here** — see Caveats.

### Secondary observation: what the tap costs in current, on this deck

Not a block-level power claim — this is one ring, not the array, and it is
not comparable to `sim/tools/power_rollup.py`'s rows. Reported because the
decks meter the digitizer's own supply branch separately and the numbers are
on file either way:

| variant | ring `i_ring` | digitizer `p_tap` | buffer `p_buf` |
|---|---|---|---|
| 1 raw tap, `clk` HIGH | 18.95 µA | 0.17 nW | — |
| 2 raw tap, `clk` LOW | 18.29 µA | 49.71 µW | — |
| 3 raw tap, `clk` 1 MHz | 18.60 µA | 26.56 µW | — |
| 4 buffered, `clk` HIGH | 18.82 µA | 0.14 nW | 25.77 µW |
| 5 buffered, `clk` LOW | 18.91 µA | 22.74 µW | 35.22 µW |
| 6 buffered, `clk` 1 MHz | 18.87 µA | 13.55 µW | 31.35 µW |

The digitizer's own dissipation is five orders of magnitude apart between its
two static states: opaque, it leaks; transparent, its master inverter is being
driven at the ring's own ~300 MHz and burns tens of microwatts. **The DR-0016
digitizer spends roughly half of every clock cycle being a ~300 MHz load**, and
that is the same fact `ring-liveness-tap-power`'s `p_tap_avg_w` already prices
at the block level — the block-level number is that deck's, not this one's.

## What this implies for DR-0007 §2 and for DR-0016

The measurement rule `layout/floorplan/README.md` adopted after #51 says a
per-ring `σ_acc,i` offered as DR-0007 §2 evidence must be measured with that
ring's **combiner neighbours** quiet. This measurement says that rule is
necessary but not sufficient:

> **A per-ring `σ_acc,i` measured with `clk` running is inadmissible for
> DR-0007 §2, buffered or not.** At `tt`/27 °C/3.30 V it is 550.9× inflated on
> an unbuffered tap and 21.1× inflated on the shipped buffered tap, the excess
> is deterministic in both cases, and squared it is a 297 800× / 403×
> over-statement of that ring's contribution to `Q_array` — in the unsafe
> direction, exactly as #51's was.

Nothing in the repository's current §2 path violates this: `array_sizing.py`
evaluates `Q_array` from the deterministic per-ring period and supply-current
records through the jitter-energy law, and none of those decks runs a sample
clock against a live ring. The rule binds **future** evidence, and it binds
[#12]'s empirical independence check in particular: a cross-correlation of
per-ring crossing residuals must be taken against the *sample clock* as well
as against the neighbour's phase.

**DR-0016 is not withdrawn or weakened by this.** Its detection mechanism,
`C_LIVE`, and its failure behaviour are untouched — this is a statement about
the digitizer's electrical tap, one level below where DR-0016 operates, and
about what may be substituted into a *different* record's sizing law. What
does change is that DR-0016's cost is now known on a second axis: it costs the
ring 28.53 µW at the binding corner (already recorded) **and** a
`clk`-locked period modulation which, on the arrangement DR-0016 originally
described, is a quarter of the ring's own period.

## What this does *not* claim, and the open question it raises

**Nothing here measures a sampled bit, a bias, or an entropy rate.** The
mechanism is a frequency modulation of the ring by the same waveform that
samples it, which is a suggestive arrangement — the phase advance between
successive sampling instants becomes an exact function of the clock waveform,
and `clk` is an external pin whose rate an integrator (or an attacker) picks.
DR-0007 §1's independence argument rests on there being no rational frequency
relationship between ring and sampler; a modulation that is locked to the
sampler is precisely the kind of thing that could create one.

That is an **argument, not a measurement**, and this repository does not act
on arguments. It is filed as [#86] rather than asserted here.

## Caveats

- **One corner.** `tt`/27 °C/3.30 V only. The modulation amplitude is a
  circuit-level difference between two operating points and there is no reason
  to expect it to be corner-independent; it has simply not been measured
  elsewhere.
- **One clock rate.** 1 MHz, the floor of DR-0003's ratified `> 1 Mbps` row.
  The *amplitude* of this mechanism is rate-independent by construction (it is
  a difference between two static loads), but `σ₁`'s dependence on the duty
  split within the measurement window is not: `σ₁ = Δ·sqrt(p(1−p))` is
  maximised at p = 0.5 and
  the window here spans 1.58 (variant 3) and 1.46 (variant 6) clock cycles, so
  p is 0.524 and 0.409 rather than exactly 0.5. Nothing here is measured at
  any other rate and no claim is made about one.
- **σ here is raw, at the fixed injected level, and is not physical jitter.**
  No entropy-rate or spec-compliance claim is made anywhere in this document.
- **The buffered rows are not the shipped array.** This deck's buffer drives
  one digitizer; the shipped one drives `xa1` and two digitizers. The
  argument above says the shipped residual can only be smaller than 20.08×,
  and that argument is a structural one about capacitance ratios, not a
  measurement. Measuring the shipped arrangement is [#87].
- **`xsb` on `xo` is not measured.** Issue #76 also names the raw-tap
  digitizer, which puts the same `clk`-driven pass gate on the XOR combiner's
  output. In the shipped design `xo` is two active stages away from either
  ring (`xa1`, then each ring's own `ro_buf`), so the same feedthrough
  argument predicts a much smaller effect there — but predicts, not measures.
  Also part of [#87].
- **`abstol = 1e-10`**, 100× looser than ngspice's default, on **every** deck
  in this family including the four whose clock never moves and which converge
  without it. Without it the two clocked decks abort with "Timestep too small
  … trouble with node `vtap#branch`" at a clock edge — the same abort
  `sim/tb/sampler-array-digitize/` bisected for the same cell. It is applied
  uniformly because this family's claims are ratios between decks, and a ratio
  taken across two solver tolerances would not be one. The check that it is
  benign is internal: the four static decks reproduce the plain control's
  `σ₁`, seed spread and exponent, and that control was taken at ngspice's
  default tolerances.
- **Ideal supply.** Ring, buffer and digitizer are metered on separate
  zero-volt sense sources off one *ideal* `vsup`, so these decks say nothing
  about supply-network coupling, which is a second path a real block has and
  these decks do not. The finding is a lower bound on what a built block
  shows, not an upper one.
- **Pre-layout.** Schematic-derived netlist (`design/sampler_core.spice`), no
  extracted parasitics. Layout adds coupling paths; it removes none.
- **One ring, not the array.** Every deck here carries a single 5-stage
  starved ring, so the currents in the secondary table are per-deck figures
  and are not the block's power. `sim/tb/ring-liveness-tap-power/` is the
  array-level measurement and it is unaffected by this work.
- **This does not supersede any existing record.** No testbench was re-run;
  six new ones were added.

[#12]: https://github.com/2AMLogic/gf180-trng/issues/12
[#51]: https://github.com/2AMLogic/gf180-trng/issues/51
[#65]: https://github.com/2AMLogic/gf180-trng/issues/65
[#75]: https://github.com/2AMLogic/gf180-trng/issues/75
[#76]: https://github.com/2AMLogic/gf180-trng/issues/76
[#82]: https://github.com/2AMLogic/gf180-trng/pull/82
[#86]: https://github.com/2AMLogic/gf180-trng/issues/86
[#87]: https://github.com/2AMLogic/gf180-trng/issues/87

