# Worst-corner entropy degradation and Monte Carlo mismatch bias

Status: measurement complete for issue [#13]. It reports two things and a
consequence:

1. The entropy-binding (minimum-`Q`) PVT corner of the shipped array,
   measured over the **full covered 27-point grid** rather than inferred from
   three points — and it is **not** the corner
   [DR-0012-sampler-fixed-external-clock] predicted. That is recorded, not
   reconciled away: [DR-0014] is the superseding decision record, filed under
   DR-0012's own "Revisit if" trigger.
2. What intra-die device **mismatch** does to the array's ring-frequency
   ratio and to the sampler's decision threshold, from two new Monte Carlo
   testbenches, and whether the conditioner and health-test margins in the
   spec cover the resulting raw-bit bias.

**This document is an ordinary summary, not evidence.** Every number below
cites the `sim/records/` stem that produced it, or the `sim/tools/` script
that derived it from committed records — treat this document as a reading
guide over that evidence, not a substitute for it. One command reproduces
every figure here:

```sh
python3 sim/tools/worst_corner_entropy.py --full
```

**No min-entropy claim is made anywhere in this document.** The `H` figures in
§4 are explicitly-constructed *ceilings* from a stated bias model, used to ask
whether bias is anywhere near being the binding constraint. [DR-0004]'s
tiering is unchanged; measuring `H` is [#12]'s job.

---

## 1. The measurement, and why it needed a new testbench

`sim/tb/ro-array-core-power/` measures the shipped two-ring array's per-ring
period and supply current — everything [DR-0007] §2's sizing inequality needs
— but only ever ran at three PVT points, and it *cannot* run at the rest of
the grid: its transient window is 50 ns and it reads the ring period between
the 2nd and 6th rising edge, which at `ss`/+125 °C/2.97 V falls outside that
window entirely.

`sim/tb/ro-array-core-pvt-q/` is the same DUT, the same rails, the same
start-up kick and the same measurement expressions, with the window widened to
300 ns. To keep the per-point cost flat across a 6× longer window, the
print/solver step relaxes 1 ps → 5 ps — a methodology change, so it is
checked rather than asserted. The two families overlap at three PVT points:

| shared corner | largest relative difference across `period_r1`, `period_r2`, `i_r1_a`, `i_r2_a`, `i_tree_a`, `e_cycle_r1_j`, `p_total_w` |
|---|---|
| `tt`/27 °C/3.30 V | 2.1×10⁻⁵ |
| `ss`/−40 °C/3.63 V | 3.4×10⁻⁵ |
| `ff`/−40 °C/3.63 V | 3.4×10⁻⁵ |

Three parts in 100 000. `worst_corner_entropy.py --check` holds that agreement
to 1 %, so the two families cannot drift apart unnoticed. (The `ring_swing_v`
/ `xo_swing_v` figures differ by 1–5 %, and are deliberately *not* held to
that tolerance: they are max/min over a fixed-length window, and the two
families' windows differ in both length and position, so a different number
there is a different statistic rather than a disagreement.)

Records: `sim/records/2026-08-02-ro-array-core-pvt-q-{01..27}.md`.
`sim/tools/array_sizing.py` now reads both families, so DR-0007 §2's
`--check` gate is evaluated at all 27 corners rather than at three.

## 2. The entropy-binding corner is `ss` / +125 °C / 3.63 V

Under [DR-0012-sampler-fixed-external-clock]'s fixed external sample clock,
the entropy-binding metric is `Q ∝ σ₁²/T₀³` — evaluated by
`sim/tools/array_sizing.py`'s `ArrayPoint` machinery, unchanged, as
`Q_array(T_s) = Σ_i a·k_B·T/(P_i·T0_i²)·T_s`. The minimum over the covered
grid sits at the **hot** end of the `ss`/3.63 V edge, not the cold end:

| corner | `T₀` (ring 1) | `P_rings` | `Q_array` @ 500 bps | margin over `M·Q_H0` | `R_max` |
|---|---|---|---|---|---|
| **`ss`/+125 °C/3.63 V** — measured minimum | 10.214 ns | 111.9 µW | **7.185×10⁻³** | **1.20×** | **598.8 bps** |
| `ss`/+27 °C/3.63 V | 7.759 ns | — | 7.630×10⁻³ | 1.27× | 635.9 bps |
| `ss`/−40 °C/3.63 V — [DR-0012]'s prediction | 6.154 ns | 165.5 µW | 7.816×10⁻³ | 1.30× | 651.3 bps |
| `tt`/+125 °C/3.63 V | 8.567 ns | — | 7.960×10⁻³ | 1.33× | 663.3 bps |
| … 22 further rows … | | | | | |
| `ff`/−40 °C/2.97 V — grid maximum | 5.171 ns | — | 1.313×10⁻² | 2.19× | 1094 bps |

(at [DR-0010]'s plain-cell `a = 1.79`; `--full` prints all 27 rows.)

**Why the prediction missed.** `Q ∝ T/(P·T₀²)`. Warming `ss`/3.63 V from
−40 °C to +125 °C lengthens `T₀` by 66 % (6.154 → 10.214 ns); that `1/T₀²`
factor of 0.36 outweighs the 1.71× more `kT` and the 0.68× ring power, for a
net 8 % *reduction* in `Q`. The three-point set DR-0012 was written against
contained no hot, high-supply point, so the temperature axis was never
exercised at the corner that turned out to matter. Nothing about the metric
changed and nothing was re-fitted.

The ranking is identical at all three measured jitter-energy constants,
because `a` multiplies every corner's `Q` by the same factor. Only the margin
moves:

| `a` | source | `Q_array` at `ss`/125/3.63 (500 bps) | margin | `R_max` |
|---|---|---|---|---|
| 1.79 | plain cell, [DR-0010]'s stated constant | 7.185×10⁻³ | 1.20× | 598.8 bps |
| 11.77 | starved cell, asymptotic slope ([#52]) | 4.724×10⁻² | 7.87× | 3937 bps |
| 24.84 | starved cell, lag-1 ([#52]) | 9.972×10⁻² | 16.62× | 8310 bps |

So **[DR-0007] §2's inequality still holds at the newly-identified worst
corner**, at every constant, and both proposed raw-rate rows survive there
([DR-0010]'s 500 bps needs 598.8 bps of headroom at `a = 1.79`; [DR-0011]'s
2 kbps needs 3937 bps at `a = 11.77`). This is a moved corner, not a failed
spec — but the margin at the plain-cell constant is 1.20×, not the 1.30× the
previously-named corner implied.

Two further things the grid settles:

- The **rate**-binding corner and the **entropy**-binding corner are
  different points. The slowest ring on the grid is `ss`/+125 °C/2.97 V
  (`T₀` = 13.151 ns), which [DR-0003] binds the raw-rate row at — and its `Q`
  is 8.902×10⁻³, 24 % *above* the minimum. Conflating the two would name the
  wrong corner for the entropy claim.
- The maximum-power corner is unchanged: `ff`/−40 °C/3.63 V, 415.3 µW total
  for the entropy source.

`fs`/`sf` remain uncovered ([DR-0006]); no minimum claimed here extends to
them. [DR-0014] carries that as an explicit follow-up, sharpened by the fact
that an edge-triggered sampler now exists downstream ([#9]) — which is the
condition DR-0006 itself named for adding those corners.

## 3. Monte Carlo mismatch

Every record in §2 is a single, mismatch-free device draw. Two new
nominal-corner Monte Carlo testbenches close that gap, both following
`sim/tb/nfet-mismatch-seed/`'s pattern (gf180mcu's `statistical` library
section, `sw_stat_mismatch=1`, one ngspice `.option seed` per draw).

### 3.1 RO array frequency spread (`sim/tb/ro-array-core-mc-freq/`)

8 independent full-array mismatch draws at `tt`/27 °C/3.30 V —
`sim/records/2026-08-01-ro-array-core-mc-freq-01.md`, seeds 1–8. The
per-seed pairing below is read from that record's raw ngspice logs rather
than from its marginal per-ring statistics, because the question
[DR-0007] §1 asks is about the *ratio within one draw*: whether some chip's
mismatch could pull the two rings towards a common frequency and open the
door to injection locking.

| Quantity | Value |
|---|---|
| `period_r1` seed-to-seed CV | 0.24 % |
| `period_r2` seed-to-seed CV | 0.17 % |
| Ring frequency ratio `f_r2/f_r1`, per-draw | mean 1.0623, sd 0.0034 (0.32 % of mean) |
| Distance of the mean ratio from the nearest integer | 18.2 sd |
| Closest any single draw came to an integer ratio | 0.057 |

The array's deliberate ~6 % frequency skew (`design/README.md`: 1.057 at
`ff`/−40 °C/3.63 V to 1.062 at `ss`/−40 °C/3.63 V, mismatch-free) is roughly
**18× larger than the mismatch-driven scatter around it**. Mismatch moves the
ratio; it does not come close to erasing the design's own margin against the
integer-ratio condition.

For `Q`: at fixed ring power `Q ∝ 1/T₀²`, so a 0.24 % period spread moves
`Q_array` by ~0.5 % — negligible against the 1.20×–16.62× margins in §2.

### 3.2 Sampler decision threshold (`sim/tb/sampler-dff-mc-offset/`)

`sampler_dff` has no analog comparator input by design — it is an ordinary
static CMOS transmission-gate flip-flop. Its closest analogue to an
input-referred offset is the master latch's own switching threshold: the `d`
voltage at which its first inversion (node `mb`) crosses mid-supply, with
`clk` held at 0 so that the master is in its open-loop, non-bistable phase and
a `.dc` sweep has a single-valued solution. 30 independent mismatch draws at
`tt`/27 °C/3.30 V — `sim/records/2026-08-01-sampler-dff-mc-offset-01.md`.

| Quantity | Value |
|---|---|
| Decision threshold, mean over 30 seeds | 1.4392 V |
| Decision threshold, seed-to-seed sd (**mismatch-driven**) | 16.37 mV (0.50 % of VDD) |
| **Systematic** offset from ideal mid-supply (1.65 V) | **−210.8 mV** |

The −211 mV is present at *every* seed alike: it is a property of this cell's
P/N sizing (0.44 µm/0.22 µm, matching `xor2`/`ro_stage`) on this PDK's device
models, not a mismatch effect, and it would be there in a mismatch-free
simulation too. It is reported because it is what the testbench measures and
because it dominates the mismatch term by 13×, but it is a design observation
rather than this issue's deliverable; no design change is proposed here.

### 3.3 The slew rate the conversion needs — measured, not assumed

Neither offset says anything about raw-bit probability on its own. A
threshold offset `dV` displaces the captured crossing in *time* by `dV/slew`,
and it is that time offset, against the ring's accumulated jitter, that biases
the bit. An earlier draft of this analysis stood in for `slew` with a proxy
built from already-committed records — the XOR node's swing divided by a full
ring period — and the conclusion turned out to be sensitive to it, so the slew
was measured instead: `sim/tb/ro-array-core-xo-slew/`,
`sim/records/2026-08-02-ro-array-core-xo-slew-{01..10}.md`.

That testbench takes two independent readings, because `xo` is the XOR of two
independent rings and its transitions are aperiodic (so a `rise=N` edge count
can mis-pair levels across a runt pulse), while a ring node is periodic and
safe for either method:

- `max|dV/dt|` over a settled window — needs no edge identification, works on
  `xo`, but reports the *steepest* point of the edge;
- a 40 %–60 % band crossing time on the ring node — an average across the
  decision band, and the check that keeps the derivative method honest.

The headline figure is `xo`'s own peak slew scaled by the ring node's
measured band/peak shape factor, i.e. a band-average slew for `xo` built from
`xo`'s peak and a shape factor measured where both methods are safe:

| corner | `xo` peak `dV/dt` | ring-node band/peak shape | headline `xo` slew | swing-over-period proxy | ratio |
|---|---|---|---|---|---|
| `tt`/27 °C/3.30 V | 3.294×10¹⁰ V/s | 0.454 | 1.494×10¹⁰ V/s | 4.75×10⁸ V/s | 31× |
| `ss`/−40 °C/3.63 V | 4.037×10¹⁰ V/s | 0.517 | 2.089×10¹⁰ V/s | 6.10×10⁸ V/s | 34× |
| `ss`/+125 °C/3.63 V | 2.639×10¹⁰ V/s | 0.523 | 1.380×10¹⁰ V/s | 3.63×10⁸ V/s | 38× |

The proxy was conservative in the safe direction, but conservative by a factor
of 31–38 is not a usable engineering statement — and at the proxy's numbers
the systematic offset would have looked like a third of the jitter budget at
the binding corner. That is why it was replaced by a measurement rather than
reasoned around. (Ten records were written, covering `ff` and `ss` at −40 °C
and `ss` at +125 °C across ±10 % supply as well as the nominal point; the
three used above are the ones the bias analysis quotes.)

## 4. Do the conditioner and health-test margins cover the observed spread?

**The model, stated once.** The ring's crossing time at the sampler is
Gaussian with sd `σ_acc(T_s) = √(κ²·T_s)`; a threshold offset displaces that
crossing by `dt = offset/slew`; the captured bit's probability is
`p = Φ(dt/σ_acc)`. The `H` this yields is a **ceiling** — what `H` could be
if bias were the *only* departure from ideal — so the question it answers is
not "what is `H`" but "is bias anywhere near being the binding constraint".

The tool evaluates it at three corners. At **`ss`/+125 °C/3.63 V, the
entropy-binding corner** ([DR-0014]) — measured slew 1.380×10¹⁰ V/s,
`σ_acc` = 1.547 ns at [DR-0010]'s 500 bps:

| case | `dt/σ_acc` | `p_major` | `H` ceiling | vs H₀ = 0.5 | vs [DR-0008] break-even |
|---|---|---|---|---|---|
| mismatch spread, 1 sd | 0.001 | 0.5003 | 0.9991 | 2.00× | 9.39× |
| mismatch spread, 3 sd | 0.002 | 0.5009 | 0.9974 | 1.99× | 9.37× |
| systematic offset alone | 0.010 | 0.5039 | 0.9887 | 1.98× | 9.29× |
| systematic + 3 sd mismatch | 0.012 | 0.5049 | 0.9861 | 1.97× | 9.26× |

At `tt`/27 °C/3.30 V (where the offset itself was measured, and where `κ²` is
directly measured rather than law-derived) and at `ss`/−40 °C/3.63 V, the same
four rows land within 0.003 of these — the three corners' slews and jitter sds
move in the same direction and largely cancel. The worst of all twelve rows,
anywhere, is `p_major` = 0.5065.

**The mismatch-driven bias — issue #13's actual question — is ~1 ps of timing
offset against a 1.2–1.5 ns jitter sd, i.e. one part in a thousand.** Even the
13×-larger systematic offset costs 10–16 ps, ~1 % of the jitter budget.

Against the spec's own margins, at the worst of those twelve rows
(`p_major` = 0.5065):

| Margin | Requirement | At the modelled worst case | Headroom |
|---|---|---|---|
| [DR-0008] conditioner: K = 8 CRC-32 earns the full 0.85 bit/bit non-vetted cap at `H` ≥ 0.106456 | `H` ≥ 0.106456 | bias-only ceiling 0.981 | **9.2×** |
| [DR-0002] RCT, cutoff `C_RCT` = 81 frozen at H₀ = 0.5, α = 2⁻⁴⁰ | `Pr(81 identical consecutive)` ≤ 9.095×10⁻¹³ | 2.3×10⁻²⁴ | 11 orders of magnitude |
| [DR-0002] APT, cutoff `C_APT` = 824 in W = 1024, α = 2⁻⁴⁰ | `Pr(X ≥ 824 \| X ~ Bin(1024, p))` ≤ 9.095×10⁻¹³ | 3.1×10⁻⁸⁷ | expected majority count 519 vs the 824 cutoff — **19.1 sd** |

**The conditioner and health-test margins cover the observed mismatch spread
with room to spare**, which is the question issue #13 asks. Note what that
statement does and does not say: it says device mismatch is not what will
limit this block's entropy, and that the health tests will not false-trip on
it. It says nothing about what `H` actually is — that is [#12]'s measurement,
and these are ceilings.

## Caveats

- **Both MC testbenches are nominal-corner-only.** Neither repeats the
  mismatch draw at `ff`/`ss` or at temperature/supply extremes, so nothing
  here says whether mismatch spread widens or narrows at the entropy-binding
  corner itself. §4's non-nominal rows carry the *nominal* corner's measured
  offset over to another corner's own slew and jitter; the offset's own corner
  dependence is unmeasured. See each testbench's header for the cost
  rationale.
- **Seed counts (30 for the sampler, 8 for the RO array) characterize the
  spread's rough magnitude, not a tail probability.** A claim about the
  *fraction* of fabricated parts that would violate a margin needs many more
  samples than either record provides.
- **`κ²` at the binding corner is law-derived, not measured.**
  `sim/tb/ro-ring5-starved-jitter-long/` ran at three corners, none of them
  `ss`/+125 °C/3.63 V, so `σ_acc` there comes from [DR-0010]'s jitter-energy
  law applied to a measured period and current. That is exactly how DR-0007
  §2 intends `Q` to be evaluated, but it is a model at the one corner that
  matters most; [DR-0014] carries the follow-up.
- **The minimum is flat along temperature.** 7.185×10⁻³ at +125 °C against
  7.816×10⁻³ at −40 °C is an 8 % separation on a metric whose constant `a` is
  itself known to ±8 %. "The minimum is on the `ss`/3.63 V edge" is a much
  more robust statement than "it is at the hot end of that edge".
- **§4's bias model is one stated linear model**, not a min-entropy
  derivation: voltage offset → timing offset via a measured edge slew → a
  Gaussian crossing-time model → `p`. Measuring `H` — with or without
  mismatch folded in — remains [#12]'s job.
- **Mismatch draws in `sim/tb/ro-array-core-mc-freq/` are per-array, not
  per-ring-independent**: each seed redraws every device in
  `design/ro_array_core.spice` together (both rings, the XOR gate), which is
  the physically correct picture for one chip. `sw_stat_global` is left off,
  so this is local/intra-die mismatch only — no die-to-die global spread on
  top of the `tt` corner already selected.
- **The slew testbench drives an unloaded `xo`.** In
  `design/xschem/sampler_core.sch` that node also drives `sampler_dff`'s data
  transmission gate, which would slow the edge. The measured slew is
  therefore an upper bound on the loaded one — but it exceeds the old proxy by
  31×, so §4's conclusion has a very large amount of room in it.
- **Not an entropy assessment.** [DR-0004]'s tiering is unchanged.

[#9]: https://github.com/2AMLogic/gf180-trng/issues/9
[#12]: https://github.com/2AMLogic/gf180-trng/issues/12
[#13]: https://github.com/2AMLogic/gf180-trng/issues/13
[#52]: https://github.com/2AMLogic/gf180-trng/issues/52
[DR-0002]: ../spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md
[DR-0003]: ../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0004]: ../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0006]: ../spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md
[DR-0007]: ../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md
[DR-0008]: ../spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md
[DR-0010]: ../spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0011]: ../spec/decision-records/DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md
[DR-0012]: ../spec/decision-records/DR-0012-sampler-fixed-external-clock.md
[DR-0012-sampler-fixed-external-clock]: ../spec/decision-records/DR-0012-sampler-fixed-external-clock.md
[DR-0014]: ../spec/decision-records/DR-0014-entropy-binding-corner-moves-to-the-hot-slow-corner.md
