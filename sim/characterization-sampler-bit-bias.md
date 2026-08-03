# Does the `clk`-locked liveness modulation reach the sampled bit?

Status: measurement complete for issue [#86]. **No. At `tt`/27 °C/3.30 V, over
three `clk` rates including DR-0003's ratified floor and a rate chosen to put
the ring's phase advance within 0.004 of a whole period per sample, running the
DR-0016 liveness digitizers' clock instead of parking it does not move the
sampled bit's bias or its short-lag serial correlation outside the resolution
of the measurement, and does not pull either ring towards lock with `clk`.**
What it does do is shift the ring's mean frequency by **+0.225 %** — a
static-load offset of the same size at every rate, which is the signature of
extra capacitance and not of injection pulling.

**This is an ordinary summary, not evidence.** Every number below cites the
`sim/records/` stem that produced it — treat this document as a reading guide
over that evidence, not a substitute for it. Correcting a number means
re-running the testbench and citing the new record, per
[`sim/README.md`](README.md).

**No entropy-rate or spec-compliance claim is made anywhere in this document.**
[`DR-0004`](../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md)'s
tiering is unchanged, and nothing here amends
[`DR-0007`](../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)
§2's sizing law.

## The question

[`sim/characterization-liveness-tap-phase-cost.md`](characterization-liveness-tap-phase-cost.md)
(issue [#76], [`DR-0016`](../spec/decision-records/DR-0016-per-ring-liveness-monitor.md)
amendment A2) measured that the DR-0016 per-ring liveness digitizer
**frequency-modulates the ring it observes, in lockstep with `clk`**: 25.6 %
apart on the raw ring node, and — on the shipped [`DR-0018`](../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md)-buffered
tap — a **19.9×** `clk`-locked residual that is deterministic (0.12 % seed
spread, `L^0.96` accumulation).

That is a measurement about **phase**, and #76 said so and declined to make a
bit-level claim from it. #86 is where that claim has to be earned, because
`DR-0007` §1's topology requirement reads

> **N free-running ring oscillators**, no phase-locking of any kind between
> them, deliberately non-integer nominal frequency ratios …

and that sentence is about rings whose frequency is nobody's function. What #76
measured is a ring whose instantaneous frequency is an exact function of the
sampling clock's own waveform, and per
[`DR-0012`](../spec/decision-records/DR-0012-sampler-fixed-external-clock.md)
`clk` is an external pin whose rate an integrator — or an attacker with access
to it — chooses.

## The mechanism the experiment has to be able to see

The modulation repeats exactly once per `clk` period, so **to first order the
deterministic phase advance between successive sampling instants is a
constant** — exactly as it would be for a free-running ring, just a different
constant. That is why the answer is not obvious in either direction, and it is
what the issue itself says.

What is *not* constant is the ring phase at which each `clk` **edge** lands
inside the ring's own cycle, and the phase kick that edge delivers depends on
where it lands. That makes the sample-to-sample map a **circle map** rather
than a pure rotation, and a circle map *locks*: if the kick is large enough and
the phase advance per sample is near an integer number of ring periods, the
ring's phase at the sampling instant stops advancing and the sampled bit stops
being a fresh draw. Locking, and pulling short of locking, is the failure this
experiment is built to catch.

Two properties of that mechanism set the sweep, and both cut in the direction
of measuring at *fast* `clk`:

- the dangerous rates are those where the per-`clk`-cycle phase advance is
  **near an integer** number of ring periods, because that is where a circle
  map's Arnold tongues are;
- there are exactly **two `clk` edges per `clk` period whatever the rate**, so
  the deterministic kick per sample is rate-independent, while the jitter that
  would smear it grows with the sample period. A fast `clk` is therefore the
  conservative direction, and DR-0003's floor is the *shipped* operating point
  rather than the worst one.

## Method

- **Harness**: `sim/run_corners.py`, ngspice-46, PDK
  `gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b`. One record per deck,
  four independent noise seeds per record, per [`sim/README.md`](README.md).
- **One corner, `tt`/27 °C/3.30 V** — the corner #51's coupling ladder and
  #76's phase family were run at, so all three are directly comparable. This is
  a mechanism question, not a PVT one. Nothing here is claimed at any other
  corner.
- **One circuit**: `design/sampler_core.spice`'s own wiring — two skewed rings,
  the DR-0018 per-ring output buffers, the DR-0007 §1 XOR combiner, the DR-0001
  raw tap `xsb`, and **both** DR-0016 liveness digitizers — with 5-stage rings
  in place of the shipped `ro_ring11`, the same substitution and for the same
  reason as #51 and #76 (see Caveats).
- **One change per pair**: whether the two liveness digitizers' clock pin is
  driven by the same running `clk` that drives the raw tap, or parked on the
  high rail. Both decks instantiate both digitizers and carry their static
  load; both sample the raw bit at the same instants; a given seed draws the
  same noise realization in both, so every comparison is paired.

| | rate | `clk` period | phase advance per sample (ring 1) | why this rate |
|---|---|---|---|---|
| A | near-integer | 11.36 ns | ~4.00 periods | where a circle map locks |
| B | generic | 12.46 ns | ~4.38 periods | fractional part far from a low-order rational: the quiet background |
| C | DR-0003 floor | 1.0007 µs | ~352 periods | the shipped operating point (DR-0003 rate, DR-0012 pin) |

Six decks, `sim/tb/sampler-bit-bias-{clocked,static}-{integer,generic,clk-floor}/`.

Reproduce the whole comparison below with:

```sh
python3 sim/tools/sampler_bit_bias_variants.py
python3 sim/tools/sampler_bit_bias_variants.py --check
```

### What is compared, and what deliberately is not

Running the digitizers' clock instead of parking it changes **two** things
about the ring at once, and only one of them is the question:

1. the **mean** load on the buffer output moves, because a 50 % duty-cycle
   clock spends half its time at each endpoint load while a parked clock spends
   all of it at one. That shifts the ring's mean *frequency* — a static-load
   effect that any added capacitance would produce, and one #51's ladder
   already established is innocent;
2. the load is **modulated in lockstep with `clk`**, which is #76's finding and
   #86's question.

Effect 1 makes the two decks' raw bit **sequences** incomparable, and that is
worth stating rather than quietly reporting a large number. A ~0.2 % difference
in mean ring period, accumulated over the ~1000 ring periods a 256-sample
window spans, is more than a full ring cycle of relative phase: the two decks
sample the same source at slightly different effective ratios, so their bit
streams decorrelate completely no matter what the modulation does. The Hamming
distance between them is therefore reported **as a diagnostic**, beside the
`N/2` that a pair of decorrelated streams would give, and is deliberately kept
out of the gate.

What is compared, and gated, is four things — each of which would have failed
on its own:

| | bound | what it would catch |
|---|---|---|
| a | the bit stream's **bias** | a tilt in the sampled bit |
| b | its **short-lag serial correlation** | a rearrangement that preserves the mean |
| c | ring 1's **phase advance per sample**, measured on the ring | a ring locked to `clk`, which the XOR could hide behind its still-free twin |
| d | the **rate-dependence** of the frequency shift | injection pulling short of lock, told apart from a static-load offset by whether it grows towards the integer ratio |

## Results

All rows at `tt`/27 °C/3.30 V, 4 seeds each, one record per deck.

### The sampling geometry the runs actually achieved

The phase advance per sample is a *measured* quantity here, not a designed one:
each deck reports its own ring periods over the same window it sampled bits in.

| rate | deck | `T_clk` | `T₀` ring 1 | ring-1 periods per sample | distance to nearest whole number |
|---|---|---|---|---|---|
| near-integer | clocked | 11.36 ns | 2.84288 ns | **3.99595** | **0.00405** |
| | static | 11.36 ns | 2.84928 ns | 3.98698 | 0.01302 |
| generic | clocked | 12.46 ns | 2.84276 ns | 4.38306 | 0.38306 |
| | static | 12.46 ns | 2.84926 ns | 4.37306 | 0.37306 |
| DR-0003 floor | clocked | 1.0007 µs | 2.84288 ns | **351.99400** | **0.00600** |
| | static | 1.0007 µs | 2.84928 ns | 351.21100 | 0.21100 |

Two of the three rates landed on a resonance, and only one of them on purpose.
The DR-0003 floor — 1.0007 µs, chosen by `DR-0003`'s ratified raw-rate row and
`DR-0012`'s no-divider external pin, not by this experiment — happens to put
ring 1 within **0.006** of a **352 : 1** ratio with `clk`. The shipped
operating point is therefore itself a near-resonant one, which makes it a
better test than it was picked to be.

### The sampled bit, at the DR-0001 raw tap

| rate | deck | `N` | ones fraction | bias (±1 mean) | resolution | `ρ₁` | `ρ₂` | `ρ₃` | `ρ₄` |
|---|---|---|---|---|---|---|---|---|---|
| near-integer | [clocked](records/2026-08-03-sampler-bit-bias-clocked-integer-01.md) | 256 | 0.4971 | −0.0059 | ±0.0625 | −0.251 | −0.461 | +0.751 | −0.052 |
| | [static](records/2026-08-03-sampler-bit-bias-static-integer-01.md) | 256 | 0.4805 | −0.0391 | ±0.0625 | −0.186 | −0.475 | +0.602 | +0.024 |
| generic | [clocked](records/2026-08-03-sampler-bit-bias-clocked-generic-01.md) | 256 | 0.5303 | +0.0605 | ±0.0624 | −0.055 | −0.063 | +0.199 | −0.414 |
| | [static](records/2026-08-03-sampler-bit-bias-static-generic-01.md) | 256 | 0.4941 | −0.0117 | ±0.0625 | −0.043 | −0.055 | +0.320 | −0.349 |
| DR-0003 floor | [clocked](records/2026-08-03-sampler-bit-bias-clocked-clk-floor-01.md) | 12 | 0.4167 | −0.1667 | ±0.2846 | +0.439 | −0.234 | −0.829 | −0.800 |
| | [static](records/2026-08-03-sampler-bit-bias-static-clk-floor-01.md) | 12 | 0.5625 | +0.1250 | ±0.2864 | +0.261 | −0.422 | −0.580 | −0.333 |

**Read the `ρ` columns as the property of the source they are, not as a
verdict on either deck.** Both arrangements are heavily serially correlated at
these rates, and they have to be: at ~4 ring periods per sample the injected
noise accumulates ~1.4 ps of phase between samples against a 2.84 ns period,
so the sampled bit is very nearly a deterministic function of where the window
started. That is a statement about sampling a ring 400× faster than the block
does, not about the block. The experiment is the **difference** between the two
columns of each pair.

### The four bounds

| rate | \|Δ bias\| | combined SE | σ | worst \|Δρ\| (lag) | σ |
|---|---|---|---|---|---|
| near-integer | 0.0332 | 0.0884 | **0.38** | 0.1488 (lag 3) | **1.68** |
| generic | 0.0723 | 0.0883 | **0.82** | 0.0645 (lag 4) | **0.73** |
| DR-0003 floor | 0.2917 | 0.4038 | **0.72** | 0.4667 (lag 4) | **1.14** |

Nothing reaches the 3 σ this experiment declared, before running, that it would
require before calling a difference measured. And there is no trend with rate:
0.38 σ / 0.82 σ / 0.72 σ across three rates spanning two decades of `clk` is
scatter, not tuning.

| rate | ring-1 periods per sample (clocked) | distance to whole number | `Δf/f` vs static |
|---|---|---|---|
| near-integer | 3.99595 | 0.00405 | **+0.225 %** |
| generic | 4.38306 | 0.38306 | **+0.228 %** |
| DR-0003 floor | 351.99400 | 0.00600 | **+0.223 %** |

This is the decisive table, and it does not go through the XOR at all.

- **Neither near-resonant rate locks.** A ring pulled into lock by `clk` runs
  at exactly `T_clk / N`, i.e. lands at distance 0 to within the ~5 × 10⁻⁵
  seed-to-seed scatter these records show on that quantity. The two resonant
  rates sit **81×** and **120×** that scatter away from lock.
- **The frequency shift is not resonance-dependent.** `Δf/f` is +0.225 %,
  +0.228 % and +0.223 % — the same number to three digits at a near-4:1 ratio,
  at an off-resonance ratio, and at a near-352:1 ratio two decades away. An
  injection-pulling term grows as the ratio approaches a rational, by
  definition. A static-load offset does not depend on the ratio at all. The
  measurement says this is the second thing: the ratio of the shift on
  resonance to off it is **0.99×**.

### The diagnostic that is deliberately not a bound

| rate | bits differing, clocked vs static, same seed | what two unrelated streams would give | what redrawing the noise alone gives | ring-1 cycles the two decks slip apart |
|---|---|---|---|---|
| near-integer | 100.3 / 256 | 128.0 / 256 | 2.9 / 256 | 2.30 |
| generic | 91.3 / 256 | 128.1 / 256 | 4.1 / 256 | 2.56 |
| DR-0003 floor | 10.3 / 12 | 6.1 / 12 | 0.3 / 12 | 9.40 |

A third of the sampled bits move when the digitizers' clock is switched on, and
**that number means almost nothing**, which is why it is here with its
explanation rather than in the tables above. The +0.225 % frequency shift alone
slides the two decks' ring phases 2.3–9.4 whole cycles apart across their
windows, so the two streams sample the same source at slightly different
effective ratios and decorrelate for that reason alone — as the "unrelated
streams" column shows they roughly have. The 12-sample floor row is worse than
uninformative on this diagnostic and is printed only for completeness.

The noise-baseline column is the one honest thing this table does say: over 256
samples, **redrawing the noise seed alone moves 1.1 %–1.6 % of the sampled
bits**. The source is alive at this sampling rate, even sampled 400× faster
than the block runs, and the bits above are not a purely deterministic
sequence.

### One cross-check against #76

`Δf/f` = **+0.225 %** here, against **+0.502 %** for the same before/after pair
in #76's buffered family
([`…-buffered-01`](records/2026-08-03-ring-liveness-tap-phase-buffered-01.md)'s
2.859605 ns against
[`…-buffered-static-01`](records/2026-08-03-ring-liveness-tap-phase-buffered-static-01.md)'s
2.874045 ns) — **2.23× smaller**. The two decks differ in one structural thing:
#76's buffer output drives the digitizer and *nothing else*, where the shipped
arrangement measured here has the DR-0007 §1 XOR on the same node. The
digitizer's input stage presents 0.66 µm of gate width against `xor2`'s
1.98 µm, so it owns ~25 % of that node's gate load instead of 100 %. A ~2.2×
dilution against a ~4× load-share argument is the right order, from decks that
share nothing but the cell library.

This is a mean-frequency ratio and **not** a modulation depth — #76 owns that
measurement and this family does not repeat it — but it is a second,
independent sign that what the shipped topology carries is smaller than the
tap-only deck implies.


## What this implies

### Does `DR-0007` §1's independence argument need a term for this?

**No — and the reason is a measurement, not an assumption. But §1's premise is
approximate, and this document is where that is written down and bounded.**

Taking the two halves in turn.

1. **§1's requirement is met, and the measurement that says so is the one that
   could have said otherwise.** §1 asks for rings that are free-running with
   "no phase-locking of any kind" and non-integer frequency ratios. At two
   near-integer `clk` ratios — one placed there deliberately at 4 : 1, one
   arrived at by DR-0003's own ratified rate at 352 : 1 — ring 1 stays 81× and
   120× the measurement's own scatter clear of lock, and the frequency shift
   the digitizers' clock causes is the *same fraction* on resonance as off it.
   Injection pulling has a signature and this is not it. There is no locking
   term to add, because there is no pulling term to widen into one.

2. **§1's premise, read strictly, is not exactly true of the shipped block, and
   was not made true by this measurement.** "Free-running" describes a ring
   whose frequency is nobody's function. #76 established that these rings'
   instantaneous frequency is a function of `clk`, and this document adds that
   the *mean* frequency moves +0.225 % when `clk` runs. That is a real
   departure from the literal sentence. What #86 contributes is its **size and
   its consequence**: at `tt`/27 °C/3.30 V it does not move the sampled bit's
   bias or its short-lag serial correlation outside a 3 σ bound at any of three
   `clk` rates, and it does not pull the ring.

So: **no amendment to `DR-0007`.** Amending §1 to admit a `clk`-coupling term
would be asserting a mechanism this repository has now looked for and not
found, and `DR-0007` §2's sizing law — the part of that record that carries
arithmetic — is untouched either way. The record that the premise is
approximate, and the bound on how approximate, belong with the tap's other
costs, which is `DR-0016`'s cost account and this document.

### Is any bias `clk`-tunable?

**Not within this measurement's resolution, and not in the direction that would
matter.** Two things have to be kept apart:

- the **absolute** bias of the sampled stream does move with `clk` rate —
  −0.006, +0.061 and −0.167 across the three rates. That is the ordinary
  behaviour of sampling a nearly-deterministic ring at different ratios, it is
  present *identically in the control*, and it is not a property of the
  digitizers;
- the **difference** between the clocked and static arrangements — the only
  quantity the digitizers can be responsible for — is 0.38 σ, 0.82 σ and
  0.72 σ across those same three rates, with no trend. On this evidence an
  attacker who owns `clk` (which `DR-0012` grants them) gains no lever *through
  the liveness digitizers*.

What an attacker who owns `clk` can still do is choose a rate at which the
sampling ratio is near-rational and the accumulated jitter per sample is small.
That is a property of any jitter-sampled RO, it is what `DR-0007` §2's sizing
law and `DR-0010`'s rate ceiling exist to bound, and it is **not** what #86
asked about. Nothing here weakens or strengthens it.

### What would change this answer

Stated plainly, because a null result is only as good as its stated reach:

- a corner at which the modulation depth is materially larger than at
  `tt`/27 °C/3.30 V. #76's own caveats already say the depth is a ratio of two
  loaded ring periods with no reason to be corner-independent, and neither
  family has measured it anywhere else;
- a `clk` rate closer to resonance than 0.004 periods per sample. This is a
  **sweep of three rates, not a scan**: a locking tongue narrower than the
  closest point probed would be missed by construction. What bounds that risk
  is bound (d) rather than the sweep's density — a tongue is opened by a
  resonance-dependent pulling term, and the measured resonance-dependence of
  the frequency shift is 0.99×, i.e. none;
- extracted layout. Every deck here is pre-layout and on an ideal supply, so
  the two coupling paths a built block has and these decks do not — supply
  network and parasitic capacitance between a clocked cell and a ring node —
  are absent. As in #76, that makes this a **lower bound** on what a built
  block will show.

### What this does not touch

- `DR-0004`'s tiering, `DR-0007` §2's sizing law, `DR-0010`'s rate ceiling and
  `DR-0003`'s ratified rate row are all unchanged, and no number here may be
  read as evidence about entropy, min-entropy or randomness — see the first
  caveat below.
- `DR-0016`'s phase-cost account (amendment A2) is unchanged. This document
  adds a bit-level result *beside* it, which is what #76 said would have to be
  earned separately, and does not restate or revise the phase numbers.
- `sim/characterization-liveness-tap-phase-cost.md`'s measurement-admissibility
  rule — that a per-ring `σ_acc` measured with `clk` toggling is not admissible
  evidence for the sizing law — stands untouched. Nothing here is a `σ_acc`.


## Caveats

- **Nothing here is an entropy, min-entropy or randomness measurement, and the
  bias figures must not be read as one.** The injected per-stage noise is a
  fixed synthetic white PSD (1 × 10⁻¹⁶ V²/Hz), not this cell's physical device
  noise, and at ~4 ring periods per sample it accumulates ~1.4 ps of phase
  against a 2.84 ns period. Smearing the ring's phase over a full period at
  this injected level would take ~2 × 10⁷ ring periods (~60 ms) of
  accumulation — orders of magnitude past anything simulable. Every bit in this
  family is therefore very nearly deterministic, which is precisely what makes
  it a sensitive probe for a deterministic `clk`-locked mechanism and precisely
  why no bias figure here says anything about the shipped block's entropy.
  [`DR-0004`](../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md)'s
  tiering is unchanged.
- **Two of the three rates are far above the shipped one.** 11.36 ns and
  12.46 ns are ~88 MHz and ~80 MHz against `DR-0003`'s ratified > 1 Mbps raw
  target, chosen so that 256 sampled bits fit inside a transient-noise window a
  two-ring array can afford. That is the conservative direction for this
  question — the deterministic kick per sample is set by the two `clk` edges
  and is rate-independent, while the jitter that smears it grows with the
  sample period — but it is the wrong direction for any entropy claim, which is
  one more reason none is made.
- **Twelve bits at the DR-0003 floor.** A 1 MHz `clk` costs ~1 µs of
  transient-noise simulation per sampled bit; twelve bits is what 13 µs of
  window buys, and it bounds that rate's bias only to ±0.28 on the ±1 mean.
  The floor row's *bit* statistics are therefore weak, and they are not what
  carries the conclusion at that rate — the locking and pulling test is, and it
  is a per-run measurement of ring frequency whose seed-to-seed scatter is
  5 × 10⁻⁵, not a 12-sample statistic.
- **A sweep of three rates is not a scan.** See "What would change this answer".
- **The noise sources' time step is 100 ps here, where #51's coupling ladder
  and #76's phase family used 10 ps.** The injected white PSD is the same
  1 × 10⁻¹⁶ V²/Hz (`NA` is rescaled with `NT` so `2·NA²·NT` is unchanged); what
  changes is that the injection is band-limited to 5 GHz instead of 50 GHz,
  which is what makes microsecond windows on a two-ring array affordable at all
  — a `trnoise()` source plants a solver breakpoint at every `NT`. Both arms of
  every comparison carry the identical stimulus, so nothing differential can
  move with it, but **no per-period jitter or `σ` may be read off these records
  and compared with the 10 ps families'.** This family reports no `σ`, by
  construction.
- **One corner**, `tt`/27 °C/3.30 V, chosen to be comparable with #51's ladder
  and #76's family. Nothing here is claimed at any other process, temperature
  or supply.
- **5-stage rings, where the shipped array's `ro_ring11` has 11.** Deliberate,
  for comparability with #51 and #76, and conservative: the digitizer loads
  exactly one node either way, and one node is a larger share of a 5-stage
  ring's delay, so any modulation here over-states the shipped ring's by
  roughly 11/5.
- **`sampler_core`'s `xsv` (the `raw_valid` register) is not instantiated.**
  Its only inputs are `clk` and `vdd`, both ideal sources in these decks, so it
  can couple to nothing measured here. `raw_valid`'s own contract is
  `sim/tb/sampler-array-digitize/`'s subject.
- **Ideal supply, pre-layout.** Rings, buffers, combiner and samplers sit on
  zero-volt ammeter sources off one *ideal* `vsup`, which has no impedance for
  one branch's current to develop a voltage across, and the netlist is
  schematic-derived with no extracted parasitics. Both of the coupling paths a
  built block has and these decks do not — supply network, and layout
  capacitance between a clocked cell and a ring node — are absent. As in #76,
  this is a lower bound on what a built block will show, not an upper one.
- **`abstol` is relaxed to 1 × 10⁻¹⁰**, 100× ngspice's default, for the reason
  `sim/tb/sampler-array-digitize/` bisected and documented: two series-starved
  rings hold their devices at currents where a 1 pA absolute tolerance is a
  meaningful fraction of the branch currents solved. 100 pA is ~5 × 10⁻⁶ of the
  per-ring supply current, and everything measured here is a settled node
  voltage or a zero-crossing time rather than a current.
- **Every sampled level landed on a rail.** The worst distance any of the
  1 048 recorded samples sits from a supply rail is 1.27 mV, so none of these
  bit statistics is taken off a capture that failed to resolve. The
  `--check` gate fails on any future record where that stops being true, which
  is the one way this measurement could quietly stop being about a bit.
- **`rst_n` is held at `vdd` throughout**, so every sampler is out of reset and
  no reset edge falls in the window. `DR-0014`'s gated-reset behaviour is
  `sim/tb/sampler-dff-reset-clocked/`'s subject.
- **Wall-clock figures in these records are inflated.** The runs shared a
  machine with other concurrent simulation, and `run_corners.py` reports summed
  per-run elapsed time; the records say so in their own notes.


[#51]: https://github.com/2AMLogic/gf180-trng/issues/51
[#75]: https://github.com/2AMLogic/gf180-trng/issues/75
[#76]: https://github.com/2AMLogic/gf180-trng/issues/76
[#82]: https://github.com/2AMLogic/gf180-trng/pull/82
[#86]: https://github.com/2AMLogic/gf180-trng/issues/86
