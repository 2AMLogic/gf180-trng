# Why one ring measures ~40× more jitter inside the array deck

Status: measurement complete for issue [#51]. **The answer is ring-to-ring
coupling through the XOR combiner's input stage.** One XOR gate and one
neighbouring ring reproduce every signature of the four-ring array record;
two rings solved in the same deck with no wire between them reproduce none of
them.

**This document is an ordinary summary, not evidence.** Every number below
cites the `sim/records/` stem that produced it — treat this document as a
reading guide over that evidence, not a substitute for it. Correcting a number
means re-running the testbench and citing the new record, per
[`sim/README.md`](README.md).

**No entropy-rate or spec-compliance claim is made anywhere in this document.**
[`DR-0004`](../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md)'s
tiering is unchanged.

## The question

[`2026-08-01-ro-array-sanity-jitter-01`](records/2026-08-01-ro-array-sanity-jitter-01.md)
— four rings plus a three-gate XOR tree — measures `σ_r1_1 = 23.2 ps` on
ring 1. The same delay cell, at the same fixed injected noise density, at the
same corner (`tt`/27 °C/3.30 V), over the same 16-period window shape, measures
**0.587 ps** standing alone
([`2026-08-01-ro-ring5-starved-jitter-long-02`](records/2026-08-01-ro-ring5-starved-jitter-long-02.md),
field `sigma_startup16_1`).

That is a factor of ~40 on the same cell, and the array record carries two
further signatures:

- its `σ` varies **0.3 %** across independent noise seeds, where a genuine
  16-period estimate scatters ~15 % (calibration in
  [`characterization-starved-cell-jitter-energy.md`](characterization-starved-cell-jitter-energy.md));
- it accumulates as **`lag^0.81`**, not the `lag^0.5` of a phase random walk.

Both say the same thing: whatever that `σ` measures is **deterministic**.

[#46] closed the *number* — `a` for the shipped starved cell is 13.9× the plain
cell's, not the 1.3 × 10⁴ × the array record implies — and in doing so refuted
the diagnosis that was on record. `DR-0010` §Consequences and #46's own body
both blamed the array run's **measurement window** (16 periods, opened at the
second edge after start-up). The long-window testbench reports that same window
geometry inside its own runs, and it comes back healthy: 16.0 % seed spread at
`tt`, and an `a` within 1.8× of the 512-period figure. **A short window is
imprecise on this cell. It is not pathological.**

So the window is not the explanation, and two candidates were left. Both
predict a deterministic, seed-independent, faster-than-`√t` perturbation that a
standalone ring does not show, so **neither is distinguishable from the array
record alone**:

- **coupling** — ring 2's phase perturbs ring 1's threshold crossings through
  the shared gate structure of the combiner's input stage. In
  `sim/tb/ro-array-sanity-jitter/`, `xa1 ro1 ro2 t1 vdd 0 xor2` puts ring 1's
  output node on four transistor gates whose internal nodes ring 2 drives;
- **numerical** — ngspice solves the whole deck (4 rings + 3 XOR gates + 20
  `trnoise()` sources) on one shared adaptive timestep, so a second ring at an
  incommensurate frequency moves where ring 1's own timepoints land, and the
  crossing times `meas` interpolates from move with them.

The distinction is not bookkeeping. If it is coupling, it is a **ring-
independence** finding, which is what
[`DR-0007` §2](../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)'s
`Q_array = Σ κᵢ² T_s / T₀ᵢ²` assumes away and what [#16] owns in the floorplan.
If it is numerical, it is a **method** limit that bounds what any multi-ring
transient-noise run in this repository can claim.

## Method

- **Harness**: `sim/run_corners.py`, ngspice-46, PDK
  `gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b`. One record per
  variant; four independent noise seeds per record for variants 2–4, and the
  control's eight, per [`sim/README.md`](README.md).
- **One corner, `tt`/27 °C/3.30 V.** This is a mechanism question, not a PVT
  one, and it is the corner the array-sanity record was taken at. Nothing here
  is claimed at any other corner.
- **One window geometry, the control's**: opened 256 periods after start-up,
  spanning 512 periods, so the accumulation exponent is fitted over lags 1…128.
  Every variant additionally reproduces, **inside the same run**, the 16-period
  window opened at the second rise that the array-sanity record used
  (`sigma_startup16_*`), so there is a like-for-like row against that record as
  well as a precise one.
- **Four DUT variants, each differing from the control in exactly one thing**:

  | | Testbench | What it adds to the control | What it isolates |
  |---|---|---|---|
  | 1 | [`ro-ring5-starved-jitter-long`](tb/ro-ring5-starved-jitter-long/) | — (**control**) | — |
  | 2 | [`ro-array-coupling-xor-static`](tb/ro-array-coupling-xor-static/) | the array's own `xa1`, second input tied to `vss` | the **static** combiner load |
  | 3 | [`ro-array-coupling-xor-driven`](tb/ro-array-coupling-xor-driven/) | `xa1` with its second input driven by a second ring (`wstv` = 0.240 µm) | the **coupling** path |
  | 4 | [`ro-array-coupling-rings-only`](tb/ro-array-coupling-rings-only/) | a second ring in the same deck, **electrically unconnected** | the **numerical** path |

  Variant 4 is the decisive one: it contains everything the numerical
  explanation needs (two rings at incommensurate frequencies, ten `trnoise()`
  sources, one shared adaptive timestep) and nothing the coupling explanation
  needs (no shared node, device or supply pin — `vr1` and `vr2` are separate
  zero-volt ammeter sources off the same *ideal* `vsup`, which has no impedance
  for one ring's current to develop a voltage across).

- **Raw σ, not scaled.** Every record here is at the same corner with the same
  fixed injected density, so the per-corner device-noise scaling that
  `starved_cell_jitter_energy.py` applies is a common factor and is
  deliberately omitted. The numbers below are directly comparable to each other
  and to the array-sanity record's raw `σ_r1_*`, and are **not** physical
  jitter.

Reproduce the whole comparison below with:

```sh
python3 sim/tools/array_coupling_variants.py
python3 sim/tools/array_coupling_variants.py --check
```

## Results

All four variants, `tt`/27 °C/3.30 V, 4 seeds each (the control has 8), σ raw
at the fixed injected level:

| | variant | differs from the control by | `T₀` | `σ₁` | `σ₁`/control |
|---|---|---|---|---|---|
| 1 | [`ro-ring5-starved-jitter-long-02`](records/2026-08-01-ro-ring5-starved-jitter-long-02.md) | — (control) | 2.5635 ns | 0.641 ps | 1.00× |
| 2 | [`ro-array-coupling-xor-static-01`](records/2026-08-01-ro-array-coupling-xor-static-01.md) | `xa1`, 2nd input on a rail | 3.3096 ns | 0.676 ps | **1.06×** |
| 3 | [`ro-array-coupling-xor-driven-01`](records/2026-08-01-ro-array-coupling-xor-driven-01.md) | `xa1` driven by ring 2 | 3.3043 ns | 18.32 ps | **28.6×** |
| 4 | [`ro-array-coupling-rings-only-01`](records/2026-08-01-ro-array-coupling-rings-only-01.md) | 2 rings, unconnected | 2.5635 ns | 0.642 ps | **1.00×** |

**Only variant 3 moves.** The static combiner load is innocent (1.06×), and a
second ring solved on the same shared adaptive timestep with no electrical
path to the first is innocent to three digits (1.00×). What separates variant 3
from variant 2 is that the neighbour switches; what separates it from variant 4
is that the neighbour is *attached*. Both differences are the same difference,
and it is the only one left.

### The variant-4 null is the load-bearing one

Variant 4 carries everything the numerical explanation needs — two rings at
incommensurate frequencies (390.1 MHz and 422.1 MHz, beating every 12.2 ring-1
periods), ten `trnoise()` sources, one shared adaptive timestep — and its ring 1
reproduces the standalone control's period to **4 parts in 10⁶**
(2.563519 ns against 2.563509 ns) and its `σ₁` to 0.2 %. Solving a second
asynchronous ring in the same deck does nothing measurable to the first.
**The numerical hypothesis is refuted, not merely unsupported.**

### Variant 3 reproduces the array record quantitatively

Read against the 16-period window opened at the second rise that
`2026-08-01-ro-array-sanity-jitter-01` itself used — reproduced *inside*
variant 3's own runs, so this is a like-for-like row and not a rescaling:

| | variant 3 (1 ring + `xa1` + 1 neighbour) | the array record (4 rings + 3-gate tree) |
|---|---|---|
| ring 1 `T₀` | 3.3047 ns | 3.3054 ns |
| ring 2 `T₀` | 3.1054 ns | 3.1052 ns |
| `σ₁` | 19.20 ps | 23.21 ps |
| accumulation exponent, lags 1…8 | 0.825 | 0.810 |
| seed-to-seed spread of `σ₁` | 1.0 % | 0.3 % |
| what that spread should be | ~15.2 % | ~15.2 % |

Four signatures, four matches, with **one** XOR gate and **one** neighbour.
The residual 1.21× on `σ₁` is the part the other two rings and the other two
tree gates account for; nothing in this experiment measures that split, and
nothing here claims it.

### The perturbation is a beat, and the data proves it is deterministic

Ring 1 runs at 302.63 MHz and ring 2 at 322.02 MHz in variant 3, so
`|f₁ − f₂|` = 19.39 MHz — **one beat every 15.6 ring-1 periods**. That number
is visible directly in the accumulation:

| lag `L` | 1 | 2 | 4 | 8 | **16** | 32 | 64 | 128 |
|---|---|---|---|---|---|---|---|---|
| `σ_acc` (ps) | 18.3 | 33.4 | 56.1 | 71.3 | **8.3** | 16.1 | 31.2 | 60.1 |

`σ` at lag 16 is **8.6× smaller than at lag 8**. No random process can do
that: for any stationary increment process `σ_acc(L)` is non-decreasing in `L`.
A perturbation that nearly cancels when the two samples are one beat period
apart is periodic and phase-locked to the neighbour, i.e. deterministic — which
is the same thing the 1.0 % seed spread says, arrived at independently. Beyond
one beat period `σ` grows as `L^0.95`, near-linear, the signature of a
deterministic drift rather than the `L^0.5` of a random walk.

The control, variant 2 and variant 4 all accumulate at `L^0.42`–`L^0.45` with
seed spreads of 3.9 %, 2.3 % and 6.0 % against a 2.7 % reference. They are
measuring jitter. Variant 3 is not.

### It is not injection locking

Ring 1's period is 3.3043 ns with the neighbour switching (variant 3) and
3.3096 ns with the same gate's other input tied to a rail (variant 2) — a
0.16 % difference, and ring 2 free-runs at 3.1054 ns rather than being pulled
to any rational ratio of ring 1. The two rings are **not** frequency-locked.
What ring 2 does is displace ring 1's threshold *crossing times* by up to tens
of picoseconds without moving its average frequency: charge injected into node
`ro1` through the gate-drain/gate-source capacitance of `xa1`'s input stage
each time the neighbour switches. That is the failure mode `DR-0007` §6 does
**not** warn about — §6 warns about locking, which collapses `Q_array`; this
inflates it.

## What this implies for `DR-0007` §2 at N = 2

`DR-0007` §2's sizing law is

```
Q_array(T_s) = Σ_{i=1..N} σ²_acc,i(T_s) / T₀,i²        (independent rings)
```

and #7 may not close on an N without showing `Q_array ≥ M · Q_H₀` at the
entropy-binding corner. This measurement does not change the law. It changes
**what may be substituted into it**:

1. **A `σ_acc` measured on a ring while its array neighbours are switching is
   not that ring's `σ_acc,i`.** At `tt`/27 °C/3.30 V it is 28.6× larger at
   lag 1, and the excess is deterministic. Squared, that is a **~820×**
   over-statement of one ring's contribution to `Q_array`.
2. **The excess carries no entropy.** It is a fixed function of ring 2's phase.
   The XOR combiner already carries ring 2's phase into the output; counting
   ring 2's phase a second time inside ring 1's `σ_acc` is double-counting a
   quantity that is, from ring 1's point of view, not random at all.
3. **The error is in the unsafe direction.** `DR-0007` §6 flags injection
   locking, which makes `Q_array` collapse while the bitstream still looks
   plausible. This is the mirror image: it makes `Q_array` look *far better
   than it is*, and an array sized on such a `σ_acc` would be undersized by
   the square of the coupling factor while every recorded number said it
   passed.
4. **At N = 2 this is the whole array**, which is `DR-0010` §Consequences'
   standing point about a single correlated pair — here made concrete with a
   measured factor rather than a worry.

**Practical consequence for #7 / #12 / #16**: per-ring `σ_acc,i` fed into §2
must be measured with the ring's combiner neighbours *quiet* (variant 2's
arrangement: the gate load present, the neighbour on a rail), or with the
deterministic component separated out and reported. A per-ring `σ` taken from a
deck in which the neighbours switch is not admissible evidence for §2, and
`sim/records/2026-08-01-ro-array-sanity-jitter-01.md`'s `σ_r1_*` are exactly
that kind of number.

This is a statement about **measurement admissibility**, not a spec change.
`DR-0007` §2 is unamended and this document does not amend it; if #7 or #16
concludes the sizing law itself needs a correlation term, that is a decision
record, not a summary document.

## Caveats

- **One corner.** `tt`/27 °C/3.30 V only. Nothing here is claimed at any other
  process, temperature or supply. The coupling factor is a circuit-level ratio
  and there is no reason to expect it to be corner-independent; it has simply
  not been measured elsewhere.
- **σ here is raw, at the fixed injected level, and is not physical jitter.**
  No entropy-rate or spec-compliance claim is made anywhere in this document;
  [`DR-0004`](../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md)'s
  tiering is unchanged.
- **The array-sanity record was taken on a different ngspice and a different
  host** (ngspice-42, Linux x86-64) from every variant here (ngspice-46,
  macOS arm64). That difference is a live confounder for the residual 1.21× on
  `σ₁` between variant 3 and that record. It is *not* a candidate explanation
  for the effect itself, because the 28.6× separation is measured **between
  variants run on the same build, host and day**.
- **The comparison of variant 3 against the control spans two changes** (the
  gate load and the switching neighbour), so it bounds the total effect and
  attributes none of it. The attributing comparisons are variant 3 against
  variant 2 (only the neighbour switches) and variant 3 against variant 4
  (only the attachment differs), and both are reported above.
- **Ideal supply.** In every variant the ring supplies are separate zero-volt
  ammeter sources off one *ideal* `vsup`, which has no impedance for one ring's
  current to develop a voltage across. These decks therefore say nothing about
  supply-network coupling, which is a *second* path that a real array has and
  these decks do not. The finding is a lower bound on the coupling a built
  array will show, not an upper one.
- **Pre-layout.** Schematic-derived netlist (`design/ro_array_sanity.spice`),
  no extracted parasitics. Layout adds coupling paths; it removes none.
- **`xa1`'s second input is tied to `vss` in variant 2**, not `vdd`. That sits
  the gate's input stage at one of its two fixed operating points; the other
  was not measured, and the difference between them is not bounded here.
- **The `σ_startup16_*` block in every variant is deliberately imprecise** — a
  16-period estimate carries ~15 % seed-to-seed spread by construction. It
  exists to be comparable with the array record's window, not to be the precise
  measurement. The 512-period `σ_*` series is the precise one.
- **This diagnoses `2026-08-01-ro-array-sanity-jitter-01`; it does not replace
  it.** That testbench was not re-run here, so per
  [`sim/README.md`](README.md) that record keeps `status: valid` and gets no
  `superseded_by`. Replacing it means re-running
  `sim/tb/ro-array-sanity-jitter/`, which is not this issue's work.

[#12]: https://github.com/2AMLogic/gf180-trng/issues/12
[#16]: https://github.com/2AMLogic/gf180-trng/issues/16
[#46]: https://github.com/2AMLogic/gf180-trng/issues/46
[#51]: https://github.com/2AMLogic/gf180-trng/issues/51
