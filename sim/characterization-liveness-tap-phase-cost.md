# What does the DR-0016 liveness digitizer cost its ring in phase?

Status: measurement complete for issue [#76]. **The pre-[#82] arrangement — the
digitizer's `d` input directly on the ring node — frequency-modulates its ring
by 25.6 % in lockstep with `clk`, putting `σ₁` at 541× the same deck's with
`clk` parked.** The per-ring output buffer [#82] had already adopted, on
evidence from a *different* path, removes 96.5 % of that. It does not remove
all of it: this document's buffered deck still carries a 19.9× `clk`-locked
residual, and that residual is deterministic.

> **The 19.9× is an isolated-ring number, and the array that ships carries
> 3.46×.** Every deck in this document has **one** ring whose buffer output
> drives **one** consumer, the digitizer. `design/ro_array_core.spice` has each
> buffer output driving the XOR combiner's input as well, so this document
> recorded 19.9× as an *upper bound* on the shipped residual rather than as the
> shipped number — see [issue #87](#the-shipped-array-carries-346-not-199) and
> [`sim/characterization-shipped-array-tap-phase.md`](characterization-shipped-array-tap-phase.md),
> which measured it at **3.46×** on the shipped topology at this same corner.
> The bound holds, by 83 %. **Read every 19.9× below as the isolated-ring
> measurement it is**; nothing in this document was re-run, and nothing in it
> is withdrawn.

**This is an ordinary summary, not evidence.** Every number below cites the
`sim/records/` stem that produced it — treat this document as a reading guide
over that evidence, not a substitute for it. Correcting a number means
re-running the testbench and citing the new record, per
[`sim/README.md`](README.md).

**No entropy-rate or spec-compliance claim is made anywhere in this document.**
[`DR-0004`](../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md)'s
tiering is unchanged.

## The question

[`sim/characterization-array-ring-coupling.md`](characterization-array-ring-coupling.md)
(issue [#51] / PR #67) indicted a specific arrangement: **a ring node driving
the input gate of a cell whose internal nodes something else is driving.** At
`tt`/27 °C/3.30 V that measured `σ₁` at **28.6×** the standalone ring's, against
**1.06×** for the same gate load with the neighbour held on a rail — so the
load was innocent and the *neighbour's switching* was the mechanism.

`design/sampler_core.spice` contained that shape a second time, and
[`layout/floorplan/README.md`](../layout/floorplan/README.md) said so while
writing [#16]'s isolation rationale: `xsr1` / `xsr2`, the DR-0016 per-ring
liveness digitizers shipped by #71, put each ring node on a `sampler_dff` `d`
input — which in that cell is the channel terminal of a transmission gate
whose **gates are driven by `clk`**:

```
XMtdp d clk  m vdd pfet_03v3 W=0.44u
XMtdn d clkb m vss nfet_03v3 W=0.22u
```

[`sim/tb/ring-liveness-tap-power/`](tb/ring-liveness-tap-power/) measured what
those digitizers cost the rings in **power** at three PVT points (DR-0016
§Power/area cost). **No testbench measured what they cost the rings in phase**,
and that gap was not obviously in the safe direction: `clk` is coherent with
the sampling instant by definition, so a `clk`-correlated disturbance does not
average over samples the way an incommensurate ring-to-ring beat does, and
`clk` is an *external* pin ([`DR-0012`](../spec/decision-records/DR-0012-sampler-fixed-external-clock.md))
whose rate is an attacker's choice rather than a design constant.

## What PR #82 changed underneath the question

While this experiment was being built, PR [#82] (issue [#75],
[`DR-0018`](../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md))
adopted a per-ring output buffer. `design/sampler_core.spice` now reads

```
xr1 en1 rn1 vddr1 vss ro_ring11 wstv=0.220u lstv=2u cld=0.5f
xb1 rn1 ro1 vdd  vss ro_buf
xsr1 ro1 clk rst_n ring_bit1 vdd vss sampler_dff
```

— the ring's own node is `rn1`, and the digitizer taps `ro1`, which is the
**buffer's output**. So the topology issue #76 was filed against is the one the
block shipped up to #82, and a different one ships now.

That does not make the question go away; it splits it in two, and this document
answers both halves:

1. **What did the pre-#82 direct tap cost the ring in phase?** Without that
   number there is no "before", and DR-0016's cost table stays a power-only
   account of a tap that was on the ring node for four commits.
2. **Does the buffer #82 adopted remove that cost on this path?** #82 adopted
   it on the strength of the *combiner*-path measurement
   ([`sim/characterization-ring-buffer-mitigation.md`](characterization-ring-buffer-mitigation.md)).
   Nothing measured what it did for the *digitizer* path, which is a separate
   consumer with a different input stage and a different aggressor.

## Method

- **Harness**: `sim/run_corners.py`, ngspice-46, PDK
  `gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b`. One record per
  variant, four independent noise seeds per record, per
  [`sim/README.md`](README.md).
- **One corner, `tt`/27 °C/3.30 V** — the corner #51's variants were run at, so
  the two ladders are directly comparable. This is a mechanism question, not a
  PVT one. Nothing here is claimed at any other corner.
- **One window geometry, #51's**: opened 256 periods after start-up, spanning
  512 periods, accumulation exponent fitted over lags 1…128. Every variant also
  reproduces, *inside the same run*, the 16-period start-up window
  (`sigma_startup16_*`) that
  `sim/records/2026-08-01-ro-array-sanity-jitter-01.md` used.
- **One ring**, device for device #51's: the shipped starved cell, a
  `ro_nand2` enable stage plus four `ro_stage`, `wstv = 0.220 µm`, with one
  `trnoise()` source in series with every stage input at the same fixed
  injected density (`1e-16 V²/Hz`).
- **`clk` at 1.0007 µs (~1 MHz)** in the two running-clock decks. DR-0003's
  ratified raw-rate row is "> 1 Mbps sustained at the raw tap" and DR-0012
  makes `clk` a fixed external pin with no divider, so this is the shipped
  operating point rather than a chosen stimulus.

Six DUT variants, each differing from its own reference in exactly one thing:

| | Testbench | What it adds | What it isolates |
|---|---|---|---|
| 1 | [`ro-ring5-starved-jitter-long`](tb/ro-ring5-starved-jitter-long/) | — (**control**) | — |
| 2 | [`ring-liveness-tap-phase-clk-high`](tb/ring-liveness-tap-phase-clk-high/) | the digitizer **on the ring node**, `clk` parked HIGH (master transmission gate **off**) | the lighter static endpoint |
| 3 | [`ring-liveness-tap-phase-clk-low`](tb/ring-liveness-tap-phase-clk-low/) | the same, `clk` parked LOW (master transmission gate **on**) | the heavier static endpoint |
| 4 | [`ring-liveness-tap-phase-clocked`](tb/ring-liveness-tap-phase-clocked/) | the same, `clk` **running** | the **pre-#82 shipped topology** |
| 5 | [`ring-liveness-tap-phase-buffered`](tb/ring-liveness-tap-phase-buffered/) | variant 4 with the shipped `ro_buf` between ring node and tap, `clk` running | the **post-#82 shipped topology** |
| 6 | [`ring-liveness-tap-phase-buffered-static`](tb/ring-liveness-tap-phase-buffered-static/) | variant 5 with `clk` parked HIGH | the buffered pair's static reference |

### Why there are two static references and not one

Inserting a buffer changes *two* things about a ring at once: it isolates the
node **and** it lightens the load on it — the argument
`sim/characterization-ring-buffer-mitigation.md` makes for its own decks. A
ratio taken across the buffer insertion therefore spans two changes and
attributes neither.

So the `clk` question is asked **inside each topology**, against that
topology's own static reference, with exactly one thing different between
numerator and denominator — whether `clk` toggles:

```
pre-#82    σ₁(4 clocked)  / σ₁(2 clk-high)
post-#82   σ₁(5 buffered) / σ₁(6 buf-static)
```

That is #51's variant-3-against-variant-2 discipline, applied twice.

Reproduce the whole comparison below with:

```sh
python3 sim/tools/liveness_tap_phase_variants.py
python3 sim/tools/liveness_tap_phase_variants.py --check
```

## Results

All rows at `tt`/27 °C/3.30 V, 4 seeds each (the control's 8), `σ` raw at the
fixed injected level, 512-period window opened 256 periods after start-up:

| | variant | differs from its reference by | `T₀` | `σ₁` | `σ₁` / control | seed spread of `σ₁` | accumulation exponent |
|---|---|---|---|---|---|---|---|
| 1 | [`ro-ring5-starved-jitter-long-02`](records/2026-08-01-ro-ring5-starved-jitter-long-02.md) | — (control) | 2.5635 ns | 0.6405 ps | 1.00× | 3.85 % | 0.421 |
| 2 | [`…-clk-high-01`](records/2026-08-03-ring-liveness-tap-phase-clk-high-01.md) | + tap on the ring node, `clk` high | 2.7472 ns | 0.6404 ps | **1.00×** | 3.26 % | 0.422 |
| 3 | [`…-clk-low-01`](records/2026-08-03-ring-liveness-tap-phase-clk-low-01.md) | + tap on the ring node, `clk` low | 3.4507 ns | 0.9031 ps | **1.41×** | 1.34 % | 0.355 |
| 4 | [`…-clocked-01`](records/2026-08-03-ring-liveness-tap-phase-clocked-01.md) | + tap on the ring node, `clk` **running** | 3.0444 ns | **346.64 ps** | **541×** | **0.01 %** | **0.954** |
| 5 | [`…-buffered-01`](records/2026-08-03-ring-liveness-tap-phase-buffered-01.md) | variant 4 + the shipped `ro_buf` | 2.8596 ns | **13.74 ps** | **21.4×** | **0.12 %** | **0.961** |
| 6 | [`…-buffered-static-01`](records/2026-08-03-ring-liveness-tap-phase-buffered-static-01.md) | variant 5, `clk` high | 2.8740 ns | 0.6902 ps | 1.08× | 2.19 % | 0.347 |

Reference for the seed-spread column: a genuine `σ₁` estimate over a
512-period window scatters **2.69 %** seed to seed, calibrated on 27 committed
plain-cell records (`sim/tools/starved_cell_jitter_energy.py`).

**The static load is innocent, exactly as it was in #51.** Variant 2 reproduces
the control's `σ₁` to three digits (1.00×) and variant 6 to 1.08×, both with
seed spreads and accumulation exponents in the band a quiet ring occupies.
Variant 3 — the heavier endpoint — is 1.41×, on a ring running 34.6 % slower;
that is a load effect on a different operating point, not a dynamic one. **Only
the two decks in which `clk` moves leave that band.**

### The disturbance is a `clk`-locked frequency modulation, not jitter

Which rail `clk` sits on decides how fast the ring runs, and by a lot:

```
clk HIGH (master transmission gate off)   T₀ = 2.7472 ns
clk LOW  (master transmission gate on )   T₀ = 3.4507 ns     25.61 % apart
```

That is the **rate-independent** part of the result: a 50 % duty-cycle clock
puts the ring in each state half the time whatever its frequency, so nothing
about that 25.61 % depends on the 1 MHz this deck ran at.

With `clk` running, the ring visits **exactly those two endpoints**. Variant
4's sixteen per-block mean periods (48 consecutive periods each, ~150 ns) are:

| block | b00 | b01 | b02 | b03 | b04 | b05 | b06 | b07 | b08 | b09 | b10 | b11 | b12 | b13 | b14 | b15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `T` (ns) | 2.7487 | *2.7472* | *2.7472* | 2.9027 | **3.4507** | **3.4506** | 3.3164 | *2.7472* | *2.7472* | *2.7472* | 3.0341 | **3.4506** | **3.4507** | 3.1851 | *2.7472* | *2.7472* |

The **bold** blocks reproduce variant 3's standalone `T₀` (3.450691 ns) to 1
part in 10⁵; the *italic* blocks reproduce variant 2's (2.747190 ns) to the
same. The blocks in between are the ones a `clk` edge falls inside. The pattern
repeats every ~7 blocks — and 7 blocks of 48 periods at these two periods is
**≈ 1.0 µs**, which is the clk period (1.0007 µs) this deck was driven at. The
ring is not being nudged: it is being switched between two operating points, in
lockstep with an external pin.

Three independent signatures say the resulting `σ` is **deterministic**, and
they are #51's own discriminators:

| signature | variant 4 | variant 5 | what a quiet ring shows (variants 1/2/6) |
|---|---|---|---|
| `σ₁` against its own static reference | **541×** | **19.9×** | 1.00×–1.08× |
| seed-to-seed spread of `σ₁` | **0.01 %** | **0.12 %** | 2.19 %–3.85 %, against a 2.69 % reference |
| accumulation exponent, lags 1…128 | **0.954** | **0.961** | 0.347–0.422 |

A phase random walk accumulates as `L^0.5`; both clocked decks accumulate as
`L^0.95`–`L^0.96`, the signature of a deterministic drift. And an estimate that
scatters 0.01 % across four independent noise seeds is not measuring noise —
the noise is the only thing that changed between those four runs.

### Why the coherence matters more than the rate

At 1 MHz against a ~330 MHz ring, a `clk` edge arrives once per ~330 ring
periods — roughly 300× less often than a neighbouring ring's transitions do in
#51's variant 3. That rarity is why the effect looks much smaller through a
short window: through the 16-period start-up window that
`sim/records/2026-08-01-ro-array-sanity-jitter-01.md` used — reproduced inside
these same runs — variant 4 is **30.6×** the control, against **541.2×** the
control over the 512-period window. A 16-period window usually falls entirely
inside one of the two states.

It is also why rate is the wrong axis to judge it on. What variant 4 measures
is not a rare transient; it is that the ring **runs at one of two different
frequencies depending on the state of an external pin**, and it changes
frequency at the sampling clock's own edges. A disturbance phase-locked to the
sampling instant does not average away over samples, and per
[`DR-0012`](../spec/decision-records/DR-0012-sampler-fixed-external-clock.md)
`clk` is an external pin whose rate is not a design constant.

### Cross-check against the one measurement that already existed

[`2026-08-02-ring-liveness-tap-power-04`](records/2026-08-02-ring-liveness-tap-power-04.md)
measured the shipped **11-stage** array at this corner with the same digitizers
attached: `period_r1` 7.5269 ns against
[`2026-08-01-ro-array-core-power-06`](records/2026-08-01-ro-array-core-power-06.md)'s
un-tapped 7.1365 ns, **+5.5 %**. That deck's clock ran at 100 MHz inside a 50 ns
window, so what it reported was the *average* over both tap states.

This family's time-averaged figure is variant 4's `T₀` = 3.0444 ns against
variant 1's 2.5635 ns, **+18.8 %** on a 5-stage ring. One tap node is 5/11 as
large a share of an 11-stage ring's delay, so the same effect on the shipped
ring is ≈ **+8.5 %** — the same size as the +5.5 % that record measured, from a
completely different deck. **The average was already visible in the power
record. The modulation was not, and nothing in that record could have shown
it**: averaging over both states is precisely what discards it.

## Does the buffer PR #82 adopted remove it? 96.5 % of it

Variant 5 is the topology the block ships today. Against its own static
reference (variant 6, one change: `clk` stops toggling):

| | `σ₁` / own static reference | per-block period swing | what remains |
|---|---|---|---|
| pre-#82, tap on the ring node | **541.3×** | **23.11 %** | — |
| post-#82, tap on the `ro_buf` output | **19.9×** | **0.96 %** | **96.5 %** of the `σ₁` excess and **95.8 %** of the swing removed |

Two independent measures of "how much is left" — one from the `σ` estimator,
one from the per-block mean periods, which does not use the estimator at all —
agree to within a percentage point. And 96.5 % is close to the **92.8 %** #75
measured for the same buffer on the combiner path, from decks that share
nothing with these but the cell.

**It is not removed.** 19.9× is far outside the 1.00×–1.08× band variants 2 and
6 occupy, the residual accumulates as `L^0.96`, and its seed spread is 0.12 %
against a 2.69 % reference — the residual is as deterministic as the thing it
is a residual of. The mechanism that survives the buffer is visible in the
netlist: the `clk`-dependent load now sits on the buffer's **output**, and a
change in output load changes the buffer's output slew, which the gate-drain
capacitance of the buffer's own devices carries back to its **input** — the
ring node. A buffer attenuates that path; it does not open it.

## The shipped array carries 3.46×, not 19.9×

Variant 5 is the *cell-for-cell* topology the block ships, but it is not the
*fan-out* the block ships. Its `ro_buf` output drives one consumer;
[`design/ro_array_core.spice`](../design/ro_array_core.spice) has each buffer
output driving the combiner as well:

```
xb1 rn1 ro1 vdd vss ro_buf
xa1 ro1 ro2 xo  vdd vss xor2              <- ro1's OTHER consumer
xsr1 ro1 clk rst_n ring_bit1 vdd vss      <- the digitizer
```

So the digitizer's `clk`-modulated capacitance is a smaller share of that
node's load in the shipped array than it is here, and the residual should be
smaller with it. **This document recorded 19.9× as an upper bound on the
shipped number for exactly that reason, and said so rather than claiming it as
the shipped number.** Issue [#87] measured the shipped number at the same
corner, on the two-ring `sampler_core` array with both buffers driving `xa1`
and their own digitizers:

| | `σ₁` / own static reference | per-block period swing | seed spread |
|---|---|---|---|
| this document's isolated buffered deck (variant 5) | **19.9×** | 0.96 % | 0.12 % |
| the shipped array, ring 1 ([`…-clocked-01`](records/2026-08-03-array-liveness-tap-phase-clocked-01.md) / [`…-static-01`](records/2026-08-03-array-liveness-tap-phase-static-01.md)) | **3.46×** | 0.136 % | 1.37 % |
| the shipped array, ring 2 (same runs) | **5.80×** | — | — |

**The bound holds, by 83 %, and the structural argument behind it is now
measured rather than argued.** Two consequences for how this document should be
read:

- Every **19.9×** in it is an **isolated-ring** figure. It is not withdrawn and
  nothing here was re-run — the decks, the records and the 96.5 % buffer
  attenuation are all unchanged — but where the question is what the *block*
  carries, 3.46× is the number, and `sim/characterization-shipped-array-tap-phase.md`
  is the document that owns it.
- The "**and that residual is deterministic**" finding is an isolated-ring
  finding too, and it did **not** carry over. The shipped residual's seed
  spread is 1.37 % against a 3.81 % reference for its window — above the
  ⅓-of-reference line, so "not collapsed" rather than deterministic — where
  this document's variant 5 was 0.12 % against 2.69 %. The shipped array's
  per-block swing also lands *below* its family's 0.3 % materiality threshold,
  where variant 5's 0.96 % is above. The `clk`-locking itself does reproduce:
  the shipped clocked deck's per-block periods alternate on a ~0.96 µs cycle
  against a 1.0007 µs `clk`.

Nothing in this section changes what `DR-0016`, `DR-0018` or `DR-0007` §2 say.
In particular the measurement-admissibility rule below is *strengthened*, not
weakened, by the shipped number being smaller: 3.46× squared is still a ~12×
over-statement of a ring's contribution to `Q_array`, in the unsafe direction.

**#87 also closed the other gap this document left**, which its own acceptance
criteria named and its decks did not cover: `xsb`, the DR-0001 raw-tap
digitizer, which puts the same `clk`-driven pass gate on the combiner output
`xo`. Measured the same way — the shipped array with the two per-ring
digitizers removed, so `xsb` is the only `clk`-driven load downstream of a
ring, against the identical deck with `clk` parked — running `clk` moves ring
1's `σ₁` to **0.96×** its own control (ring 2: **1.00×**) and leaves the
per-block period swing at **0.006 %**, the control's own value. `xo` is two
active stages from either ring node (`xa1`, then that ring's own `ro_buf`), and
that is enough to put the disturbance below what the measurement resolves. It
is **not** a proof of zero: the control's seed-to-seed spread is 4.42 %, which
is the floor the claim sits on.

## What this implies

1. **`DR-0007` §2's measurement rule extends to the sample clock.**
   `sim/characterization-array-ring-coupling.md` established that a per-ring
   `σ_acc,i` measured while the ring's *combiner neighbours* are switching is
   not admissible evidence for the sizing law. This measurement adds a second
   aggressor to that rule: a per-ring `σ_acc,i` measured while **`clk` is
   toggling** is not admissible either. At `tt`/27 °C/3.30 V the pre-#82
   topology inflates it 541× — squared, a ~2.9 × 10⁵ over-statement of that
   ring's contribution to `Q_array`, in the unsafe direction — and the
   post-#82 topology still inflates it, by 19.9× on this document's isolated
   deck (a ~400× over-statement) and by **3.46× on the shipped array** (a ~12×
   over-statement, per the section above). Smaller, and still disqualifying:
   the rule is that a per-ring `σ_acc,i` measured with `clk` toggling is not
   admissible, not that it is admissible below some threshold. **This is a
   statement about measurement admissibility, not a spec change**; `DR-0007` §2
   is unamended and this document does not amend it.
2. **No `sim/records/` entry in this repository is affected by that rule
   today.** Every committed per-ring `σ_acc` comes from a deck with no
   digitizer in it at all (`ro-ring5-starved-jitter-long`,
   `ro-inv-05stage-jitter`, `ro-array-sanity-jitter`, #51's ladder). The rule is
   forward-looking: it forbids a future `σ_acc` deck from carrying a live
   digitizer, which the shipped `sampler_core` netlist would otherwise make the
   natural thing to do.
3. **`DR-0016`'s cost table was a power-only account, and it under-reported.**
   The +28.53 µW loading delta it prices is the *average* of the two states.
   The record now carries the phase cost as well
   (`DR-0016` §"Phase cost", amendment A2).
4. **`DR-0018`'s adoption is supported on a second path, and its residual is
   larger there.** #82 adopted the buffer on the combiner-path evidence alone.
   On the digitizer path it removes a comparable fraction (96.5 % against
   92.8 %), so the adoption decision is corroborated rather than undermined —
   but the residual it leaves here (19.9×) is larger than the one it leaves
   there (2.87×), and it is `clk`-coherent rather than incommensurate. On the
   shipped fan-out those two residuals are much closer: 3.46× against 2.87×.

**Nothing here proposes a further design change.** What the remaining residual
should be done about — a bigger buffer, a `clk`-gated digitizer, sampling the
liveness bit off the combiner output instead of the ring, or nothing at all —
is a decision this document does not make and has no evidence for. It is filed
as follow-up work in its own right. Whoever picks it up should size the problem
from the shipped **3.46×**, not from this document's isolated 19.9×.

## Caveats

- **One corner.** `tt`/27 °C/3.30 V only, chosen to be directly comparable with
  #51's ladder. Nothing here is claimed at any other process, temperature or
  supply. The modulation depth is a ratio of two loaded ring periods and there
  is no reason to expect it to be corner-independent; it has simply not been
  measured elsewhere.
- **One clk rate**, 1.0007 µs (~1 MHz), for the two running-clock decks. The
  25.61 % endpoint gap is rate-independent by construction, but how the
  disturbance folds into any particular `σ_acc` window is not — variant 4's
  `σ₁` would be different at a different `clk` rate, and DR-0012 makes that
  rate external.
- **`σ` here is raw, at the fixed injected level, and is not physical jitter.**
  No entropy-rate or spec-compliance claim is made anywhere in this document;
  [`DR-0004`](../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md)'s
  tiering is unchanged. For variants 4 and 5, `σ` is not even a jitter estimate
  — the three signatures above say what it measures is deterministic.
- **5-stage ring, where the shipped array's rings have 11.** Deliberate, for
  comparability with #51, whose whole ladder is on this ring at this corner and
  window. The tap loads exactly one ring node either way, and one node is a
  larger share of a 5-stage ring's delay than of an 11-stage ring's, so the
  fractional period and phase effects here **over-state** the shipped ring's by
  roughly 11/5. The `+5.5 %` cross-check above is the only direct 11-stage
  measurement, and it is an average rather than a modulation depth.
- **Ideal supply.** Ring, buffer and digitizer are on separate zero-volt
  ammeter sources off one *ideal* `vsup`, which has no impedance for one
  branch's current to develop a voltage across. These decks therefore say
  nothing about supply-network coupling from the digitizer's own switching,
  which is a *second* path a real block has and these do not. The finding is a
  lower bound on what a built block will show, not an upper one.
- **Pre-layout**, schematic-derived netlist (`design/sampler_core.spice`), no
  extracted parasitics. Layout adds coupling paths between a clocked cell and a
  ring node; it removes none.
- **`rst_n` is held high throughout**, so the digitizer is out of reset and
  contributes no reset edge. DR-0014's gated reset behaviour is measured by
  `sim/tb/sampler-dff-reset-clocked/` and is not what these decks are about.
- **The buffered pair's static reference is `clk` HIGH only.** `clk` LOW was
  run for the unbuffered pair (variant 3) but not the buffered one, so the
  buffered topology's own endpoint gap is read off variant 5's per-block
  periods rather than from two standalone decks. That is the weaker of the two
  ways to get it, and it is the one this experiment has.
- **A solver limit, recorded so it is not rediscovered.** With a tap attached,
  a `PULSE`-source or `tstop` breakpoint landing exactly on one of the
  `trnoise()` sources' 10 ps breakpoints collapses ngspice-46's transient
  ("Timestep too small; timestep = 1.25e-24") at that instant, reproducibly.
  Every `clk` timing and `tstop` in this family is therefore deliberately off
  the 10 ps grid (`tclk_del` = 5.003 ns, `tclk_tr` = 0.203 ns, `tstop` =
  2.900003 µs and so on). The offsets are ~0.3 % of an edge and ~0.0005 % of a
  `clk` period; nothing measured here resolves them.
- **This does not re-measure the tap's power.**
  `sim/tb/ring-liveness-tap-power/` owns that at three PVT points, and each
  deck here supplies the digitizer outside the ring's charge integrator so its
  own switching current stays out of `i_ring_a`/`p_active_w`.


[#16]: https://github.com/2AMLogic/gf180-trng/issues/16
[#51]: https://github.com/2AMLogic/gf180-trng/issues/51
[#75]: https://github.com/2AMLogic/gf180-trng/issues/75
[#76]: https://github.com/2AMLogic/gf180-trng/issues/76
[#82]: https://github.com/2AMLogic/gf180-trng/pull/82
[#87]: https://github.com/2AMLogic/gf180-trng/issues/87
