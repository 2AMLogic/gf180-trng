---
dr: DR-0008-raw-rate-moves-to-the-measured-jitter-energy-limit
title: Resolve the DR-0007-versus-Power-row collision by moving the raw-rate row to the rate a minimum-energy ring array delivers inside the ratified power budget
status: Proposed
date: 2026-08-01
deciders: Proposed by #7 (entropy-source array sizing). NOT ratified — acceptance is an operator decision, as DR-0001…DR-0004 and DR-0007 were.
supersedes: "DR-0003-throughput-defined-at-the-raw-tap — its rate VALUE only, and only on acceptance. DR-0003's definition of where the rate is measured (the raw tap), what 'sustained' means, and its binding corner all stand unchanged."
superseded_by: n/a
related: "#7 (origin — array sizing), #32/PR #38 (sim/characterization-supply-current-and-leakage.md), #29/#1 (DR-0007 ratification), #4 (sim/characterization-ro-delay-cell-jitter.md), #8 (conditioner K), #9 (sampler clock), #11 (health-test RTL), #12/#13 (array H and minimum-Q corner), #16 (isolation),
#46 (validating (★) on the shipped starved cell — this record's largest open risk); DR-0002 (H0, health-test cutoffs), DR-0003 (raw rate), DR-0004 (quality tiers), DR-0006 (PVT/seed coverage), DR-0007 §2 (sizing law) and §Revisit if; README §Target specification — Raw rate, Power"
---

# DR-0008: Resolve the DR-0007-versus-Power-row collision by moving the raw-rate row to the rate a minimum-energy ring array delivers inside the ratified power budget

## Status

- 2026-08-01: Proposed, by #7. Not ratified.

On acceptance, three edits follow and are deliberately **not** made by the pull
request that proposes this record:

1. `README.md`'s `Raw rate` row changes to this record's number and cites this
   record alongside DR-0003.
2. [`DR-0003`](DR-0003-throughput-defined-at-the-raw-tap.md) gains
   `superseded_by: DR-0008-raw-rate-moves-to-the-measured-jitter-energy-limit`
   and a status line, and nothing else — its text is not rewritten.
3. [`DR-0007`](DR-0007-multi-ro-xor-combined-entropy-source.md) §3's indicative
   `N₀ = 560` is annotated as answered by this record. Its §1 topology and §2
   sizing law are **not** touched; this record uses both unchanged.

Until then the ratified rows stand as written, and this record is a proposal
that must not be cited as though it were spec.

## Context

### The collision this record exists to resolve

[`DR-0007`](DR-0007-multi-ro-xor-combined-entropy-source.md) §2 binds the
entropy source to a sizing law: the array of N rings shall satisfy

```
Q_array(T_s) = Σ_i σ²_acc,i(T_s) / T₀,i²  ≥  M · Q_H₀ ,
Q_H₀ = 4.0 × 10⁻³ (H = 0.5),  M = 1.5
```

at the entropy-binding corner, and DR-0007 §6 makes it #7's obligation to fix N
against that law and report the resulting `Q_array`. DR-0007 §Consequences
recorded, as an order-of-magnitude estimate with no evidence behind it, that the
resulting N would collide with the README `Power` row, and filed #32 to measure
it.

#32's measurements closed that question in the negative. Per
[`sim/characterization-supply-current-and-leakage.md`](../../sim/characterization-supply-current-and-leakage.md)
(records `sim/records/2026-08-01-ro-inv-05stage-power-{01..27}.md`,
`…-ro-inv-05stage-stopped-leakage-{01..45}.md`,
`…-device-leakage-03v3-{01..45}.md`):

- a **single** ratified-characterization ring already exceeds the whole
  `< 500 µW` active budget at the binding corner, by a factor near four, so no
  `N ≥ 1` satisfies both rows;
- DR-0007's own `C_node = 5 fF` input is refuted — the measured effective
  switched capacitance per ring node is ~2.5× larger — so every power figure in
  DR-0007 is an **under**-estimate;
- DR-0007 §3's "shorter rings" lever does not reduce per-ring power at all, for
  a fixed delay cell.

That document explicitly declines to choose a resolution and hands it here, and
this is exactly the condition DR-0007 §"Revisit if" names. Something has to
move. This record moves the raw-rate row, and says why that row and not one of
the other three.

### The measurement that makes the choice one-dimensional

The four candidate levers named in #32's handoff — the raw-rate row, the
entropy-per-raw-bit target, the delay-cell operating point, and the Power row —
look independent. They are not. This repository has already measured enough to
tie them into a single equation, and doing so is what turns this decision from
a judgement call into arithmetic.

For a ring whose phase performs a random walk, accumulated jitter obeys
`σ²_acc(t) = κ² t`, so DR-0007 §2's per-ring figure is `Q = κ² T_s / T₀²`.
Classical ring-oscillator noise theory says `κ²` is not a free variable: to
first order its product with the ring's dissipated power is set by temperature
alone. Evaluating that product at **every point** of the 27-point candidate-A
grid this repository has measured — combining
`sim/records/2026-07-31-ro-inv-05stage-jitter-{01..27}.md` (σ₁),
`sim/records/2026-07-31-inv-stage-noise-{01..27}.md` (the per-corner device-noise
density that scales the fixed injection to a physical one) and
`sim/records/2026-08-01-ro-inv-05stage-power-{01..27}.md` (P) — gives

```
a  ≡  κ² · P_ring / (k_B · T)   =   1.79 ± 0.14        (min 1.64, max 2.12)
```

**over a grid on which `P_ring` itself spans 3.36× and `κ²` spans 5.43×.** The
derivation reads only committed records, needs neither ngspice nor the PDK, and
is re-runnable:

```sh
python3 sim/tools/jitter_energy_law.py --check
```

Substituting `P_ring = E_cycle / T₀` with `E_cycle = n · C_eff · V²` (energy
switched per ring cycle, `n` stages) collapses DR-0007 §2's left-hand side, for
an array of one cell design, to

```
Q_array(T_s)  =  a · k_B · T · T_s · P_rings / E_cycle²                    (★)
```

`(★)` is the load-bearing statement of this record. Read it and the four levers
stop being four:

| Lever | How it enters `(★)` | Reach |
|---|---|---|
| Power row (`P_rings`) | linear, numerator | bounded by the row; the gap is ~2000× |
| Delay-cell operating point (`E_cycle = n·C_eff·V²`) | **inverse square**, denominator | the strongest lever, and floored by the PDK |
| Entropy target (`M · Q_H₀`) | linear, denominator | see below: ~2.5× before the model goes vacuous |
| Raw rate (`T_s = 1/R`) | linear, numerator | unbounded, and the only one with no model-validity limit |

Two structural consequences of `(★)` matter as much as the arithmetic:

- **`Q_array` does not depend on N or on ring frequency separately** — only on
  the array's *total* ring power and on the energy per ring cycle. N and `T₀`
  are therefore free to be chosen for independence and for what the sampler can
  resolve, not for entropy. That is why this record can fix N at a small number
  without paying for it in entropy, and why DR-0007 §3's `N₀ = 560` is not the
  shape of the answer.
- **`E_cycle` enters squared**, so the operating point is worth exercising to
  its floor before any row is moved. This record does that first, and asks the
  rate row only for what is left.

`(★)` inherits the ~1.5–2× accuracy on σ that
[`sim/characterization-ro-delay-cell-jitter.md`](../../sim/characterization-ro-delay-cell-jitter.md)
states for its fixed-injection scaling — i.e. ~2–4× on `Q`. The *constancy* of
`a` is the much stronger claim, because that scaling error is largely
common-mode across corners.

## Decision

We will **move the raw-rate row**, and only the raw-rate row, and we will move
it to the rate the entropy source delivers after its operating point has been
pushed to the floor the PDK allows.

### 1. The row that moves

> `Raw rate` — **> 500 bps sustained at the raw tap**, superseding DR-0003's
> `> 1 Mbps`. Everything else in DR-0003 is unchanged: the rate is still
> defined at the raw tap (DR-0001), still means *sustained* rather than burst,
> and still binds at `ss` / −10 % / +125 °C.

The number is derived in §3 from measurements of the array this record sizes,
and is deliberately quoted with the margin `(★)` gives rather than at the
inequality's edge.

### 2. The rows that do not move

- **The `Power` row is unchanged** — `< 500 µW` active at `ff`/+10 %, `< 1 µA`
  idle at `ff`/+10 %/+125 °C. The array sized below fits it with the ring
  budget stated in §3, leaving the remainder for the sampler, health tests,
  conditioner and register file that do not exist yet.
- **DR-0002's `H₀ = 0.5`, α = 2⁻⁴⁰, W = 1024 and cutoff formulas are
  unchanged**, and so is DR-0007 §2's `Q_H₀ = 4.0 × 10⁻³` and `M = 1.5`.
- **DR-0007 §1's topology and §2's sizing law are unchanged and are used as
  written.** This record supplies N, the stage count and the operating point
  that §6 asks #7 for; it does not renegotiate the law they are checked against.
- **DR-0001's raw tap is unchanged**: at the sampler output, after the XOR,
  after digitisation. No per-ring node is exposed.
- **DR-0004's tiering is unchanged.** Nothing here is an entropy assessment;
  the array's `H` remains a simulation-derived design estimate carrying
  DR-0004's mandatory label until #12 measures it.

### 3. The array this rate is derived from

Schematics: `design/xschem/ro_array_core.sch` and the cells below it; exported
netlist `design/ro_array_core.spice`; design note `design/README.md`.

- **Delay cell** (`ro_stage`) — the minimum-width 3.3 V inverter the PDK allows
  (`pfet_03v3` W = 0.44 µm / `nfet_03v3` W = 0.22 µm, L = 0.28 µm) with **no**
  deliberate load capacitor, and with always-on **series** starve devices
  (W = `wstv`, L = 2 µm, gates tied to the opposite rail) setting the current.
  The starve devices are in series, not shunt capacitance, precisely because
  under `(★)` slowing a ring by loading it costs `Q_array` quadratically while
  slowing it by starving it costs nothing: starving moves `T₀` and `P_ring`
  together at constant `E_cycle`.
- **Ring** (`ro_ring11`) — a `ro_nand2` enable stage plus ten `ro_stage`,
  eleven in total, on its own supply pin. Eleven and not three: `E_cycle ∝ n`
  argues for the minimum inverting ring, but the starved cell measures a
  small-signal gain of only ~2.6 at 1 GHz at its own trip point
  (`sim/tb/rostage-noise/`), against the 2.0 per stage a three-stage ring needs
  to sustain a rail-to-rail oscillation — and a three-stage ring of this cell is
  observed to oscillate at roughly half amplitude instead. A degraded swing at
  the XOR node is a sampler problem, not a ring problem, and is not a trade this
  record is willing to make for a factor in `E_cycle`.
- **Array** (`ro_array_core`) — **N = 2** rings, two separate supply pins,
  skewed only by starve-device width (`wstv` = 0.220 / 0.240 µm) so the nominal
  frequency ratio has no small-integer factorisation, XOR-combined into the
  single node the sampler sees.

**Why N = 2, which is the uncomfortable part of this record.** Under `(★)`
entropy is indifferent to N at fixed *total* ring power, so N is free to be
chosen for independence — and what actually binds it is the combiner. Measured,
at the `ff`/+10 %/−40 °C power corner:

| Array | rings | XOR tree | total | vs `< 500 µW` | record |
|---|---|---|---|---|---|
| N = 4, `lstv` = 2 µm | 573 µW | **444 µW** | **1017 µW** | 2.0× over | `2026-08-01-ro-array-core-power-01.md` |
| N = 4, `lstv` = 6 µm | 414 µW | **525 µW** | **939 µW** | 1.9× over | `…-02.md` |
| **N = 2, `lstv` = 2 µm** | **270 µW** | **146 µW** | **415 µW** | **fits** | `…-04.md` |

Two things that table settles. First, the **XOR tree is not a rounding term** —
at N = 4 it is 44–56 % of the entropy source's whole active power. Second,
**slowing the rings does not fix it**: tripling the starve length cut the ring
power but the tree's energy per transition rose faster than its transition rate
fell (the ring's edges get slower, so the combining gates spend longer in
short-circuit), and the ring swing fell from 3.69 V to 3.19 V into the bargain.
Halving the ring count is the only lever that moved the total under the row,
because it halves the tree's transition rate *and* its depth at once.

N = 2 is the floor of what DR-0007 §1 means by an array, and this record does
not pretend otherwise — see Consequences.

### What five stages would buy, and why this record still ships eleven

The `ro_ring11` bullet above rejects a *three*-stage ring on measured gain, and
the Alternatives section below concedes that the same measurement puts the
practical floor at **five**, not three. Five is therefore the stage count that
actually costs this record something, and it is priced here rather than passed
over. A record that moves a ratified row by ~2000× owes the reader the one
alternative that recovers a large fraction of it.

**What it buys.** `E_cycle ∝ n` is not assumed here; it is measured, on the same
cell, at the same corner, with the same starve devices (`wstv` = 0.220 µm,
`lstv` = 2 µm, ring 1 of each array, `tt`/27 °C/3.30 V):

| Ring | `T₀` | `E_cycle` | ring supply power | record |
|---|---|---|---|---|
| 5-stage (`ro_ring5`) | 3.305 ns | 1.987 × 10⁻¹³ J | 60.1 µW | `2026-08-01-ro-array-sanity-jitter-01.md` |
| 11-stage (`ro_ring11`, shipped) | 7.137 ns | 4.399 × 10⁻¹³ J | 61.7 µW | `2026-08-01-ro-array-core-power-06.md` |

The `E_cycle` ratio is **2.21**, i.e. 11/5 to within 1 %, and per-ring power is
the same to within 2.5 %. That is the series starve device doing exactly what §3
claims for it: it fixes the ring's current, so stage count buys `E_cycle`
without buying power. Substituted into `(★)`, where `E_cycle` enters squared,
five stages is nominally worth **(2.21)² = 4.90×** on `Q_array` and therefore on
the rate row.

**What the combiner takes back.** `T₀` falls by the same 2.16×, so the XOR
node's transition rate rises by 2.16× and the tree's power rises with it. At the
`ff`/+10 %/−40 °C **power**-binding corner, where the shipped array measures
270 µW of rings and 146 µW of tree, the five-stage array of the same two rings
would be

```
P_rings ≈ 263 µW   (270 × 60.1/61.7)
P_tree  ≈ 315 µW   (146 × 2.16)
P_total ≈ 578 µW   —  1.16× over the ratified < 500 µW row
```

Getting back inside the row means starving harder, which scales ring power and
tree power together — under `(★)`, at constant `E_cycle`, `T₀ ∝ 1/P_ring`, and
the tree's transition rate follows `T₀` — while `Q_array` scales linearly with
`P_rings`. The factor needed is 500/578 = 0.87, so the **net** gain is
4.90 × 0.87 = **4.2×**, not 4.90×.

**So the price of eleven stages is a factor of ~4.2 on the headline row.** A
five-stage array would put §1 at roughly **2.1 kbps** — 2.8 kbps at the
inequality's edge, quoted with the same 1.30× margin this record uses elsewhere
— instead of 500 bps. That is the largest single number this record leaves on
the table and it is not recovered anywhere else in it.

**Why it is declined anyway.** Not because five stages is *disqualified* — the
evidence in hand does not reach that far — but because it is **unmeasured where
it binds**, and this record's whole method is to derive the rate row from
measurements of the array it actually ships:

- The only five-stage ring of this cell that has been simulated swings
  **2.643 V on a 3.30 V rail, 80 %** (`2026-08-01-ro-array-sanity-jitter-01.md`,
  `ring1_swing_v`), at `tt`/27 °C/3.30 V — the *most favourable* of the corners
  for the starved cell's gain, which falls from 2.59 at nominal to 1.68 at
  `ss`/125 °C/2.97 V (`2026-08-01-rostage-noise-{01,04}.md`, `gain_1g`). The
  eleven-stage ring measures rail-to-rail at every corner it has been run at,
  including both binding ones (3.38 V on 3.30 V; 3.65 V and 3.73 V on 3.63 V).
  No five-stage ring has been run at any corner but nominal.
- The three-stage datapoint shows how steeply swing falls once the margin over
  `1/cos(π/n)` runs out: margin **1.30× → 45 %** swing, **2.10×** (five stages,
  nominal) **→ 80 %**, **2.48×** (eleven, nominal) **→ rail to rail**. Five
  stages at `ss`/125 °C/2.97 V has a margin of **1.36×** — the same
  neighbourhood as the three-stage case that collapsed — and nothing in this
  repository measures what it does there.
- The 578 µW estimate above is optimistic in a direction already measured here:
  it assumes the tree's energy per transition is unchanged, whereas the `lstv`
  2 → 6 µm experiment showed that figure *rising* when the ring's edges degrade.
  Partial-swing inputs degrade it the same way, so the real five-stage total is
  above 578 µW, not below.

**In fairness to the five-stage case**, the thing it is usually assumed to break
it does not: the same record measures the XOR node at **3.521 V on a 3.30 V
rail** while its rings swing 2.64 V, so an `xor2` tree does restore full swing
from 80 %-swing inputs at nominal. The objection is therefore *not* "the sampler
is handed an analog level" — that is not established, and this record does not
claim it. It is that the ring's own swing margin is 20 percentage points thinner
at the single corner it has been measured at, and there is no swing data at all
at the corners the spec binds on.

**What would reopen it.** A `ro-array-core-power`-style run of a five-stage
`ro_array_core` at `ss`/−40 °C/3.63 V and `ff`/−40 °C/3.63 V — a deterministic
power run, not a transient-noise one, so hours rather than days — reporting
`ring_swing_v` rail-to-rail and a re-starved `P_total` inside `< 500 µW`. If it
comes back clean, the rate row is worth ~4× more than §1 states and should be
moved there by a superseding record. This record does not claim five stages is
wrong. It claims eleven is what has been measured, and `CLAUDE.md` does not
allow a headline number to be quoted from the other one.

### The §2 inequality, at the entropy-binding corner

`sim/tools/array_sizing.py` evaluates DR-0007 §2 from the committed records
(per-ring period and per-ring supply current, via `(★)`); `--check` is the
acceptance criterion DR-0007 §6 demands, in runnable form:

```sh
python3 sim/tools/array_sizing.py --check
```

| Corner | `T₀` ring 1 | `P_rings` | `P_tree` | `P_total` | ring swing | `xo` swing | `Q_array` @ 500 bps | max rate meeting §2 |
|---|---|---|---|---|---|---|---|---|
| **`ss`/−40 °C/3.63 V (entropy-binding)** | 6.154 ns | 165 µW | 71 µW | **237 µW** | 3.73 V | 3.71 V | **7.82 × 10⁻³** | **651 bps** |
| **`ff`/−40 °C/3.63 V (power-binding)** | 4.286 ns | 270 µW | 146 µW | **415 µW** | 3.65 V | 3.70 V | 9.85 × 10⁻³ | 820 bps |
| `tt`/27 °C/3.30 V (nominal) | 7.137 ns | 127 µW | 64 µW | 192 µW | 3.38 V | 3.35 V | 9.72 × 10⁻³ | 810 bps |

(`sim/records/2026-08-01-ro-array-core-power-{04,05,06}.md`.)

**`Q_array = 7.82 × 10⁻³ ≥ M · Q_H₀ = 6.0 × 10⁻³` at the entropy-binding
corner — a margin of 1.30× on top of DR-0007's own `M = 1.5`.** That is the
showing DR-0007 §6 requires, and it is why the row in §1 is stated at 500 bps
rather than at the 651 bps the inequality would just tolerate.

Two more measured facts the array has to satisfy and does: both rings swing
rail to rail and so does the XOR node (3.65–3.73 V on a 3.63 V supply), and the
two rings sit at a frequency ratio of 1.057 (`ff`) / 1.062 (`ss`) — a ratio with
no small-integer factorisation, which is the schematic-level half of the
injection-locking argument DR-0007 §1 requires.

### 4. Entropy-binding corner

The corner this array is sized at is the **measured minimum-`Q` corner**, which
DR-0007 §4 states as cold / +10 % supply with the process letter TBD. The array
resolves the letter the same way the candidate-A grid does — `ss` / −40 °C /
3.63 V, where `Q_array` is 0.79× its value at `ff` / −40 °C / 3.63 V — and #13
still owns confirming it over the full grid. The `Power` row's active corner is
`ff` / −40 °C / 3.63 V. Both are cold/+10 %; they differ only in the process
letter, and the array must satisfy the power row at `ff` while delivering
`Q_array` at `ss`. Only those two corners are measured for the shipped array,
which is why §4 claims a resolution over the corners measured rather than over
the grid; the `fs`/`sf` exclusion of DR-0006 also still applies.

## Alternatives considered

### Move the `Power` row instead

- **What**: raise the active budget until DR-0007's `N` fits.
- **Why plausible**: it is the row that has no measurement behind it — it was
  written as a target, not derived — and moving it would leave the *product*
  claim (1 Mbps of `H = 0.5` raw bits) intact, which is the claim with the most
  downstream consumers (#8's compression ratio, #11's α-vs-false-alarm
  arithmetic, the time-to-first-valid row).
- **Why rejected**: the required move is ~2000×, i.e. from 500 µW to of order a
  watt (`sim/characterization-supply-current-and-leakage.md` §Projection). That
  is not a budget revision, it is a different product: an on-chip TRNG that
  dissipates a watt cannot be integrated into anything this block is meant for.
  The idle row fails independently and for an unrelated reason — 560 stopped
  rings alone leak ~6× the `< 1 µA` row before any digital logic exists — so
  even a generous active-power revision would not rescue the sizing. And unlike
  the rate row, no prior record left this one live as a superseding path.

### Move the entropy-per-raw-bit target `H₀` instead

- **What**: lower `H₀` below 0.5, shrinking `Q_H₀` and therefore the required
  `Q_array`, and let the conditioner (#8, DR-0004) recover entropy density from
  a weaker raw stream.
- **Why plausible**: it is architecturally the cheapest lever — it costs no
  power, no area and no rate — and DR-0004 already contemplates the conditioner
  making up entropy density. DR-0007 itself listed a variant of this as one of
  the three ratifiable resolutions of the original gap.
- **Why rejected**: the bound that defines `Q_H₀` will not carry it. DR-0007 §2
  takes `Q_H₀` from Baudet et al.'s
  `H ≥ 1 − (4/(π² ln 2))·exp(−4π² Q)`, whose value at `Q = 0` is
  `1 − 4/(π² ln 2) = 0.4154`. The bound is therefore **vacuous for any
  `H₀ < 0.4154`**: it is satisfied by a ring with no jitter at all, which is
  physically false (min-entropy really does go to zero as `Q` does) and is an
  artifact of using the expression outside its asymptotic regime. Inside the
  usable range the leverage is small — `H₀ = 0.45` reduces the required `Q` by
  only ~2.5×, against a gap of ~2000× — and it collapses to nothing at the
  knife-edge. Buying three orders of magnitude from a bound's singularity is
  precisely the failure mode DR-0007 rejected the piling-up-lemma argument for,
  and rejecting it there and accepting it here would be incoherent. Separately,
  DR-0002's APT parameterisation admits no valid cutoff at `H ≤ 0.03`, so this
  lever also has a hard floor well above where it would need to go.

### Push the delay-cell operating point further, and keep 1 Mbps

- **What**: keep the rate and buy the remaining factor from `E_cycle`, whose
  inverse-square entry in `(★)` makes it the strongest lever available.
- **Why plausible**: it is the lever this record *does* exercise, and it is the
  only one that costs no spec row at all. If it reached far enough, nothing
  would have to move.
- **Why rejected**: it does not reach, and its three factors are each at a hard
  floor. `V` is the block's ratified 3.3 V supply — an internal lower rail would
  need a regulator this project has not designed, would be a new spec row of its
  own, and the gf180mcu 3.3 V devices are not characterised for it. `C_eff` is
  already the minimum-width device with no added load. `n ≥ 3` for an inverting
  ring, and the measured gain of the starved cell puts the practical floor at
  five, not three — and §3's *What five stages would buy* prices that floor
  rather than waving at it: five stages is worth **4.2× net** (not the 4.9× the
  inverse square alone suggests, once the XOR tree's 2.16× higher transition
  rate is paid for inside the unmoved `Power` row), which would put the rate row
  near 2.1 kbps. **Even taking it, this alternative fails by ~500×**, which is
  why it is listed here as a lever that does not reach rather than as the
  resolution. It is declined on its own terms too, for the measured reason
  in §3. The full exercise of this lever is in the Decision above and it leaves
  a shortfall that only the rate row can close. This is why the record moves one
  row rather than none — and also why it does not move that row further than it
  has to.

### Keep every row and under-size the array

- **What**: build the array that fits the power budget, keep `> 1 Mbps` and
  `H₀ = 0.5` in the README, and let #12 discover the shortfall later.
- **Why plausible**: no spec churn, no decision record, and every downstream
  issue keeps the numbers it has already been curated against.
- **Why rejected**: it is the failure mode DR-0007 §2 was written to make
  impossible ("under-sizing becomes a visible spec violation instead of a silent
  entropy shortfall") and it is what `CLAUDE.md` forbids in as many words —
  agents do not relax, or quietly fail, the ratified spec to make results pass.
  It also lands the block below DR-0002's APT degeneracy floor, where the
  health-test parameterisation the safety story rests on has no valid cutoff.

### Time-interleave N independent RO+sampler channels

- **What**: N channels each sampled at `R/N`, outputs concatenated.
- **Why plausible**: each channel accumulates N× more jitter per sample, so the
  arithmetic of `(★)` is unchanged while the rate row stays put.
- **Why rejected**: DR-0007 already considered and rejected it, on grounds this
  record does not disturb — it multiplies DR-0001's single raw tap by N and
  gives an attacker N separately-observable, individually-weak streams. `(★)`
  adds a second reason: the total jitter budget is conserved either way, so it
  buys no entropy per unit power; it only relabels where the rate is lost.

## Consequences

- **Positive**:
  - The collision `sim/characterization-supply-current-and-leakage.md` handed to
    #7 is resolved quantitatively, with one row moved and the reason stated,
    rather than by adjusting a number until the arithmetic closes.
  - `(★)` gives every future sizing argument a single equation and a
    machine-checkable premise (`sim/tools/jitter_energy_law.py --check`) instead
    of a chain of separate order-of-magnitude estimates. It also predicts,
    rather than assumes, what a change of cell or supply would buy.
  - N drops from DR-0007 §3's indicative 560 to 2, and the area pressure
    DR-0007 §Consequences flagged goes with it. The internal shared-supply
    coupling risk that "N rings switching at GHz rates" created is reduced to a
    two-ring problem at ~200 MHz, which is what #16 now has to argue about.
  - The `Power` row survives untouched, which keeps the block integrable — and
    the entropy source is measured against it rather than projected: 415 µW at
    the corner the row binds at.

- **Negative / accepted cost**:
  - **The headline rate falls by ~2000×.** A 500 bps raw TRNG is a materially
    different product claim from a 1 Mbps one, and DR-0007 said exactly that
    when it rejected this lever the first time. Every downstream consumer of the
    rate row has to be re-derived: #8's conditioner compression ratio and its
    output rate, #11's health-test window and false-alarm arithmetic at the new
    rate (a `W = 1024` window is now ~2 s long, not ~1 ms), and the README's
    time-to-first-valid row, which is a *rate* consequence and gets ~2000×
    worse. This is the single largest cost in this record and it should not be
    accepted without weighing it against the alternatives above.
  - **N = 2 is the floor of DR-0007 §1's array, and it is set by the combiner,
    not by entropy.** Two rings give the weakest version of the
    injection-locking defence the array exists to provide, and a single stuck
    ring costs half the jitter budget rather than a quarter. If #16's isolation
    work finds two rings insufficient, **the `Power` row is the next thing that
    has to give** — this record names it as the live successor path, exactly as
    DR-0007 named the rate row for this one. The lever that would buy N back
    without touching the Power row is a cheaper combiner (the XOR tree is
    35–56 % of the measured total — 35.2 % at N = 2, 43.7 % and 55.9 % in the
    two N = 4 arrays of §3's table), which is design work nobody has scheduled.
  - **The entropy source uses 83 % of the active budget** (415 µW of 500 µW at
    `ff`/+10 %/−40 °C), leaving ~85 µW for the sampler, health tests,
    conditioner and register file — none of which exist or are measured. That
    is a tight allocation and it is stated here rather than discovered later.
  - **The rate row and the entropy row are now coupled by `(★)`.** Any future
    change to the delay cell, the supply, or the ring power budget moves the
    achievable rate quadratically or linearly, and cannot be made without
    re-deriving it. That coupling was always physically there; this record makes
    it explicit and therefore unavoidable.
  - **`(★)` is a model, fitted to one cell family on one PVT grid, and the
    array's own transient-noise run does not yet confirm it.** The constant is
    derived from a *plain inverter* over
    `{tt,ff,ss} × {−40,27,125} °C × {2.97,3.30,3.63} V`; the shipped cell is a
    starved minimum-width cell. The first array transient-noise run
    (`sim/records/2026-08-01-ro-array-sanity-jitter-01.md`) returns a `κ²` four
    orders of magnitude **above** `(★)` — but that run's `σ` is not usable as
    evidence either way: it varies by 0.3 % across three independent noise
    seeds (a genuine 16-period jitter estimate would vary by ~20 %, and the
    ratified 128-period per-ring records vary by 4.8 %), and it accumulates as
    lag^0.81 rather than the lag^0.5 of a random walk. Both say the same thing:
    over a window that short, opened that soon after start-up, what is being
    measured is a deterministic settling drift, not jitter. So the discrepancy
    is unresolved in **both** directions and `(★)` is used here as the
    conservative estimate rather than the confirmed one. **#46** owns settling
    it. If it shows the starved cell really does deliver far more jitter per
    unit power than the plain one, the rate row moves back up — by a superseding
    record.
  - **The flicker exclusion still stands** (DR-0007 §2): `σ_acc(T_s)` is
    extrapolated from a short white-noise window by √t, so the measured `Q` is a
    lower bound on the physical one and the rate here is correspondingly
    conservative. If #12/#13 resolve the 1/f contribution, the rate row may move
    back up — which would be a superseding record, not a silent edit.

- **Follow-up required**:
  - **#8, #11 and the README's time-to-first-valid row** must be re-derived at
    the new rate on acceptance. None of them can simply keep their current
    numbers.
  - **#46 is this record's largest open risk**: the first real test of `(★)` on
    the shipped *starved* cell, by a transient-noise run whose measurement
    window opens well after start-up and spans orders of magnitude more than the
    16 periods the sanity run managed. It is filed as its own issue rather than
    left with #12 on purpose — #12 is blocked on #8, #9 and #10 because its
    scope is min-entropy on *bitstreams* from the sampler chain, whereas this
    measurement is `σ_acc(t)` on a ring node and needs none of them. Parking the
    validation of this record's central model behind three unrelated blockers
    would have been a filing error, not a schedule.
  - **#12** measures `H` for the *array* at the actual sample interval rather
    than by √t extrapolation, and reports an empirical independence check
    across the two rings. Its scope is unchanged by this record.
  - **#13** confirms the minimum-`Q` corner and its process letter over the full
    grid; §4 above resolves it only over the corners this issue measured.
  - **#9** pins the sampler clock source, which selects the corner metric
    (DR-0007 §4) and fixes the transition density the XOR node must present.
  - **#16** owns the two-ring isolation argument at floorplan level; this
    record supplies the schematic-level half (per-ring supply pins, continuous
    frequency skew — measured ratio 1.06, no small-integer factorisation) and
    flags that with N = 2 the consequence of getting it wrong is worse.
  - **A cheaper combiner** is the one piece of design work that would buy N back
    inside the ratified Power row, and it is not scheduled anywhere.
  - **Per-ring liveness monitoring (#44)** and the **metastability-hybrid
    stretch tap (#43)** are both deferred out of #7 to their own issues;
    `design/README.md` records the mechanism each is deferred *against*, so
    neither is foreclosed. #44 matters more under this record than it did
    under DR-0007: at N = 2 a single dead ring is half the array.
    #43 matters more too — a metastability tap is not rate-limited by
    accumulated phase noise, so it is the one architectural option that could
    raise the rate row back up without spending power.

- **Revisit if**: #46 measures `σ_acc(T_s)` for the shipped cell over a window
  long enough to be jitter rather than settling drift, and finds `a` in `(★)`
  is materially different for a series-starved cell than for a plain inverter —
  the first array run hints strongly that it is, in the favourable direction,
  and if that survives a proper measurement the rate row moves back up; or
  #12/#13's flicker resolution changes `Q₁` by more than the `M = 1.5` margin;
  or #16 finds two rings insufficient for the independence the sizing law
  assumes, in which case the `Power` row is what gives next; or a future cell or
  supply change moves `E_cycle` (the rate moves as its inverse square, and `(★)`
  says by how much).
