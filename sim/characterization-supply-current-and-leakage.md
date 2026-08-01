# Supply-current and leakage characterization: per-ring active power, stopped-ring leakage

Status: characterization complete for issue #32. Supplies the first
supply-current and leakage measurements this repository has ever had, and
answers the question [`DR-0007`](../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)
§Consequences left open: whether its N-ring sizing law and the README's
`Power` row can both hold.

**This document is an ordinary summary, not evidence.** Every measured number
below cites the `sim/records/` stem that produced it — treat this document as a
reading guide over that evidence, not a substitute for it. Every *projected*
number is labelled as a projection and shows its arithmetic, so a reader can
redo it from the cited records.

**No spec row is edited by this issue.** Two ratified rows are contradicted by
the measurements below. Per `CLAUDE.md`, a row the evidence contradicts is
**reported, not relaxed**: the contradiction is stated here with numbers and
handed to #7 (array sizing) and to whatever superseding decision record #7's
outcome requires ([`DR-0007`](../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)
§Revisit if). Nothing here decides what to do about it.

## What is and is not covered

Covered: **one candidate-A 5-stage ring oscillator**, free-running (active
supply current) and held stopped (static/leakage current), plus the gf180mcu
3.3 V core devices' off-state leakage per micron of gate width.

Not covered, and not projected except where explicitly labelled: the sampler,
the XOR tree, health tests, the conditioner, the register file, pads, or any
other digital logic — **none of it exists yet**, so none of its power is
measured here. The one place a digital-section number appears (the idle
projection) is an explicitly-flagged extrapolation from a measured per-micron
leakage coefficient onto an *assumed* gate width, and is labelled as such.

## Method

- **Harness**: `sim/run_corners.py`, ngspice-46, PDK `gf180mcuD @
  c6d73a35f524070e85faff4a6a9eef49553ebc2b` — the same harness, tool and PDK
  the RO jitter characterization used
  ([`sim/characterization-ro-delay-cell-jitter.md`](characterization-ro-delay-cell-jitter.md)).
- **Devices**: gf180mcu 3.3 V core devices (`nfet_03v3` / `pfet_03v3`) only.
- **Everything here is deterministic.** No transient-noise source, no Monte
  Carlo, no mismatch: the active measurement is a plain `.tran` and both
  leakage measurements are operating points. Every record therefore carries
  `seeds: n/a (deterministic analysis)`, which is what `sim/README.md`'s
  "no seed, no evidence" rule prescribes for a non-stochastic analysis. This
  is a real simplification over the jitter work — these numbers are
  bit-reproducible, not seed-averaged.
- **Ring identity.** The ring measured for active power is the *same* ring
  `sim/tb/ro-inv-05stage-jitter/` measured the jitter of: same delay cell
  (`pfet_03v3 w=2u l=0.28u` / `nfet_03v3 w=1u l=0.28u`, `cload 5f`), same stage
  count, same `.ic` start-up. Only the five series `trnoise()` sources are
  omitted; they are ideal 0 V DC sources that inject noise but no power. That
  this changed nothing about the ring's operation is not asserted, it is
  checked — see [Cross-check against the jitter grid](#cross-check-against-the-jitter-grid).
  Keeping the ring identical matters because DR-0007's projection multiplies a
  per-ring power by an N fixed from a per-ring jitter budget; if those were two
  different rings the product would be meaningless.
- **Active-current method**: charge integration between two like-edged
  crossings of the same node, an **exact integer number (32) of ring periods**
  apart. An ideal current-mirror-plus-capacitor integrator (`fq`/`cq`) makes
  `v(q)` the charge drawn from the supply since `t = 0`; the mean current is
  the difference of `v(q)` at the two crossings divided by the elapsed time.
  Averaging over a fixed time window instead would carry a partial-cycle bias
  set by wherever the window happened to cut the last cycle. Each record also
  reports the mean current over the *first* 16 and the *last* 16 periods of
  that window separately: at all 27 points these agree to within ~2 parts per
  million, so the window is fully past start-up and the figure is not drifting.

### Testbenches

| Testbench | What it measures | Analysis | Grid |
|---|---|---|---|
| [`sim/tb/ro-inv-05stage-power/`](tb/ro-inv-05stage-power/) | mean supply current, active power, energy per cycle, effective per-node switched capacitance of one free-running candidate-A 5-stage ring | `tran` (deterministic) | `{tt,ff,ss} × {−40,27,125} °C × {2.97,3.30,3.63} V` = 27 points |
| [`sim/tb/ro-inv-05stage-stopped-leakage/`](tb/ro-inv-05stage-stopped-leakage/) | static supply current of one candidate-A 5-stage ring **held stopped** by its enable | `op` | `{tt,ff,ss,fs,sf} × {−40,27,125} °C × {2.97,3.30,3.63} V` = 45 points |
| [`sim/tb/device-leakage-03v3/`](tb/device-leakage-03v3/) | off-state drain leakage per micron of gate width, `nfet_03v3` and `pfet_03v3` | `op` | 45 points, same grid |

Why the stopped ring needs an enable, and why that is a measurement construct
rather than a design decision: a ring of five plain inverters cannot be stopped
at all, and its only DC operating point is the unstable one with every stage at
its trip point drawing hundreds of microamps of crowbar current — an operating
point analysis of it measures a state the ring never occupies, not leakage. So
the stoppable netlist replaces stage 1 with a 2-input NAND whose second input
is the enable (series NMOS doubled to 2 µm each, parallel PMOS 2 µm each, so
drive strength is unchanged); with `en = 0` the ring latches in a unique static
state with every stage at a rail. **#7 owns how the array's rings are actually
stopped** — NAND stage, supply gating, or otherwise. What is recorded here is
what an *un-power-gated* stopped ring leaks, which is the pessimistic case any
gating scheme improves on. Each leakage record prints all five ring node
voltages alongside the current, so the record itself proves the ring is latched
in the expected state (`n1,n3,n5` at the rail, `n2,n4` at ~0) rather than
sitting somewhere ambiguous.

`fs`/`sf` are covered for the two operating-point testbenches (they cost ~2 s
per point and they skew NMOS and PMOS in opposite directions, which is exactly
what a leakage question needs) but **not** for the transient active-power
testbench (~9–20 s per point), where `{tt,ff,ss}` brackets the answer and keeps
the grid point-for-point comparable with the jitter grid it has to be
multiplied against. This is the same coverage boundary
[`DR-0006`](../spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md)
drew, for the same cost reason.

## Active supply current: one free-running candidate-A 5-stage ring

Full 27-point grid, `sim/records/2026-08-01-ro-inv-05stage-power-{01..27}.md`
(record `NN` is the same grid point as `sim/records/2026-07-31-ro-inv-05stage-jitter-NN.md`).

| Corner | `NN` | Period (s) | `f_osc` (Hz) | `I_supply` (A) | `P_active` (W) | `C_eff` per node (F) |
|---|---|---|---|---|---|---|
| tt/−40/2.97 | 01 | 5.95125e-10 | 1.68032e9 | 3.05346e-04 | 9.06877e-04 | 1.2237e-14 |
| tt/−40/3.30 | 02 | 5.45971e-10 | 1.83160e9 | 3.75344e-04 | 1.23863e-03 | 1.2420e-14 |
| tt/−40/3.63 | 03 | 5.10073e-10 | 1.96050e9 | 4.48638e-04 | 1.62856e-03 | 1.2608e-14 |
| tt/27/2.97 | 04 | 6.77548e-10 | 1.47591e9 | 2.72834e-04 | 8.10317e-04 | 1.2448e-14 |
| **tt/27/3.30 (nominal)** | 05 | 6.21343e-10 | 1.60942e9 | **3.35315e-04** | **1.10654e-03** | 1.2627e-14 |
| tt/27/3.63 | 06 | 5.79709e-10 | 1.72500e9 | 4.00955e-04 | 1.45547e-03 | 1.2807e-14 |
| tt/125/2.97 | 07 | 7.90827e-10 | 1.26450e9 | 2.40005e-04 | 7.12815e-04 | 1.2781e-14 |
| tt/125/3.30 | 08 | 7.26224e-10 | 1.37699e9 | 2.94288e-04 | 9.71150e-04 | 1.2953e-14 |
| tt/125/3.63 | 09 | 6.77205e-10 | 1.47666e9 | 3.51595e-04 | 1.27629e-03 | 1.3119e-14 |
| ff/−40/2.97 | 10 | 4.94183e-10 | 2.02354e9 | 3.70544e-04 | 1.10052e-03 | 1.2331e-14 |
| ff/−40/3.30 | 11 | 4.59742e-10 | 2.17513e9 | 4.50044e-04 | 1.48515e-03 | 1.2540e-14 |
| **ff/−40/3.63 (active binding corner)** | 12 | 4.34250e-10 | 2.30282e9 | **5.32807e-04** | **1.93409e-03** | 1.2748e-14 |
| ff/27/2.97 | 13 | 5.61475e-10 | 1.78102e9 | 3.32535e-04 | 9.87628e-04 | 1.2573e-14 |
| ff/27/3.30 | 14 | 5.21816e-10 | 1.91638e9 | 4.03839e-04 | 1.33267e-03 | 1.2772e-14 |
| **ff/27/3.63 (binding corner, +27 °C)** | 15 | 4.92012e-10 | 2.03247e9 | **4.78307e-04** | **1.73625e-03** | 1.2966e-14 |
| ff/125/2.97 | 16 | 6.54802e-10 | 1.52718e9 | 2.93971e-04 | 8.73094e-04 | 1.2963e-14 |
| ff/125/3.30 | 17 | 6.08711e-10 | 1.64282e9 | 3.56289e-04 | 1.17576e-03 | 1.3144e-14 |
| **ff/125/3.63 (binding corner, +125 °C)** | 18 | 5.73152e-10 | 1.74474e9 | **4.21720e-04** | **1.53084e-03** | 1.3317e-14 |
| ss/−40/2.97 | 19 | 7.32326e-10 | 1.36551e9 | 2.47736e-04 | 7.35776e-04 | 1.2217e-14 |
| ss/−40/3.30 | 20 | 6.62528e-10 | 1.50937e9 | 3.08095e-04 | 1.01671e-03 | 1.2371e-14 |
| ss/−40/3.63 | 21 | 6.12313e-10 | 1.63315e9 | 3.71614e-04 | 1.34896e-03 | 1.2537e-14 |
| ss/27/2.97 | 22 | 8.33825e-10 | 1.19929e9 | 2.20883e-04 | 6.56023e-04 | 1.2403e-14 |
| ss/27/3.30 | 23 | 7.54596e-10 | 1.32521e9 | 2.74586e-04 | 9.06132e-04 | 1.2558e-14 |
| ss/27/3.63 | 24 | 6.96807e-10 | 1.43512e9 | 3.31296e-04 | 1.20260e-03 | 1.2719e-14 |
| **ss/125/2.97 (grid minimum power)** | 25 | 9.72390e-10 | 1.02839e9 | **1.93766e-04** | **5.75486e-04** | 1.2688e-14 |
| ss/125/3.30 | 26 | 8.82250e-10 | 1.13347e9 | 2.40211e-04 | 7.92696e-04 | 1.2844e-14 |
| ss/125/3.63 | 27 | 8.14999e-10 | 1.22700e9 | 2.89491e-04 | 1.05085e-03 | 1.2999e-14 |

**Headline numbers.**

- **Per-ring active power at the `ff`/+10 % binding corner, across the whole
  temperature axis: 1.53 mW (+125 °C) → 1.74 mW (+27 °C) → 1.93 mW (−40 °C).**
  The row's stated binding rationale — "fastest RO, max measured `f_osc`
  2.30 GHz at −40 °C" — is confirmed by the measurement: the maximum active
  power over all 27 points is at `ff`/−40 °C/3.63 V, exactly where the ratified
  row says it binds.
- **Per-ring active power at nominal (`tt`/27 °C/3.30 V): 1.11 mW.**
- **Minimum over the whole grid: 0.575 mW** at `ss`/+125 °C/2.97 V — the
  slowest, lowest-supply point.
- Supply current spans 194 µA … 533 µA per ring over the grid.

All trends are physically sensible: power rises with supply (≈`V²`, and the
frequency rises with `V` too), rises with process speed, and falls with
temperature at fixed supply (the ring slows down faster than short-circuit
current grows).

### Cross-check against the jitter grid

The measured period at **every one of the 27 shared grid points** agrees with
the seed-averaged period recorded in
`sim/records/2026-07-31-ro-inv-05stage-jitter-{01..27}.md` to all four
significant figures that characterization reports (e.g. `ff`/−40/3.63:
4.34250e-10 s here vs 4.342e-10 s there; `ss`/125/2.97: 9.72390e-10 vs
9.724e-10; nominal: 6.21343e-10 vs 6.213e-10). Two independent testbenches,
one with five injected noise sources and one without, one measuring edge
statistics and one measuring charge, reproduce the same oscillator. That is
the evidence for the claim above that removing the `trnoise()` sources did not
change the ring, and it is what licenses multiplying a per-ring power from this
grid by an N derived from that one.

### The node-capacitance assumption: refuted, and by exactly the right factor

DR-0007 §Consequences estimated per-ring power as
`n · C_node · V² · f ≈ 5 × 5 fF × (3.3 V)² × 1.6 GHz ≈ 0.4 mW`, and said
explicitly that no evidence record stood behind it. The assumption in that
expression is **`C_node` = 5 fF**, which is the explicit `cload y vss 5f` in
the candidate-A delay cell — i.e. it counted the deliberate load capacitor and
nothing else.

The measurement inverts that expression instead of assuming it. Each record
reports

```
C_eff = E_cycle / (n · V²) = I_supply · T₀ / (n · V)      (n = 5 stages)
```

the **effective switched capacitance per ring node**, which is what the
`n·C·V²·f` model would need in order to be true.

| Quantity | DR-0007 assumption | Measured |
|---|---|---|
| `C_node` (per ring node) | 5 fF | **12.22–13.32 fF** over the 27-point grid (mean 12.69 fF) |
| Per-ring power at `tt`/27 °C/3.30 V | ≈0.44 mW (formula, at the measured 1.609 GHz) | **1.107 mW** (record `-05`) |
| Ratio | — | **2.53×** |

**The 5 fF assumption is refuted: the real per-node switched capacitance is
2.4–2.7× larger.** The missing ~7.7 fF is the next stage's gate capacitance,
the driving stage's own drain/overlap capacitance, and the short-circuit
(crowbar) charge that a `CV²f` model folds into `C_eff`. And the discrepancy is
*entirely* accounted for by that factor: `0.44 mW × 2.53 = 1.11 mW`, the
measured value. DR-0007's formula was right; its capacitance input was low by
2.5×, and therefore **every power figure in DR-0007 is an under-estimate by
that factor**, not an over-estimate.

Two caveats on `C_eff`:

- It is an **upper bound** on the true node capacitance, because short-circuit
  current is lumped into it. How much of it is short-circuit current is bounded
  by its own stability: `C_eff` varies by only 8.7 % of its mean across the
  entire 27-point PVT grid, and moves in the direction short-circuit current
  would (lowest at −40 °C, highest at +125 °C), so the short-circuit share is
  small — of order a femtofarad-equivalent, not half the total.
- It is the capacitance of *this* testbench's cell including its explicit 5 fF
  load. A cell with different routing load would have a different `C_eff`; what
  transfers to #7 is the method and the ~2.5× correction factor over
  "explicit load capacitor only", not the 12.7 fF itself.

## Idle (stopped-ring) leakage

The README's ratified definition of "idle": *all ring oscillators stopped, no
bits produced, block powered with register state retained* — leakage plus
static bias only. Below is the entropy source's share of that: one ring held
stopped, supply up.

Full 45-point grid, `sim/records/2026-08-01-ro-inv-05stage-stopped-leakage-{01..45}.md`.
Selected points (all 45 are in the records):

| Corner | `NN` | `I_leak` per stopped ring (A) | `P_idle` per ring (W) |
|---|---|---|---|
| **ff/125/3.63 (idle binding corner)** | 18 | **1.04712e-08** | 3.80105e-08 |
| ff/125/3.30 | 17 | 8.06414e-09 | 2.66117e-08 |
| ff/125/2.97 | 16 | 6.33421e-09 | 1.88126e-08 |
| fs/125/3.63 | 36 | 5.61943e-09 | 2.03985e-08 |
| ff/27/3.63 | 15 | 9.45205e-11 | 3.43109e-10 |
| tt/125/3.63 | 09 | 1.03332e-09 | 3.75094e-09 |
| **tt/27/3.30 (nominal)** | 05 | **1.95093e-11** | 6.43806e-11 |
| sf/125/3.63 | 45 | 4.81166e-10 | 1.74663e-09 |
| ss/125/3.63 | 27 | 1.25566e-10 | 4.55805e-10 |
| ff/−40/3.63 | 12 | 1.96811e-11 | 7.14423e-11 |
| ss/−40/2.97 (grid minimum) | 19 | 1.49327e-11 | 4.43502e-11 |

**Headline numbers.**

- **Per stopped ring at the `ff`/+10 %/+125 °C binding corner: 10.47 nA
  (38.0 nW).**
- **At nominal (`tt`/27 °C/3.30 V): 19.5 pA** — 537× below the binding corner.
  Leakage is overwhelmingly a hot-corner phenomenon: ×111 from 27 °C to 125 °C
  at `ff`/3.63 V alone.
- **The ratified idle binding corner is confirmed by measurement.** `ff`/+10 %/
  +125 °C is the maximum of all 45 points, including the split corners the
  active grid does not cover: `fs`/125/3.63 is 5.62 nA (0.54× of `ff`),
  `sf`/125/3.63 is 0.481 nA, `tt` 1.03 nA, `ss` 0.126 nA. The row's stated
  binding corner is where leakage actually peaks; nothing in `fs`/`sf`
  outflanks it.
- Ring leakage is NMOS-dominated, which is why `fs` (fast NMOS) is the runner-up
  and `sf` (slow NMOS) is 22× below `ff`.

## Device off-state leakage per micron

`sim/records/2026-08-01-device-leakage-03v3-{01..45}.md`, same 45-point grid.
This exists so the block-level idle projection rests on a measured coefficient
rather than a textbook range.

| Corner | `NN` | `nfet_03v3` `I_off` (A/µm) | `pfet_03v3` `I_off` (A/µm) |
|---|---|---|---|
| **ff/125/3.63 (idle binding corner)** | 18 | **3.06999e-09** | **1.04690e-10** |
| ff/125/3.30 | 17 | 2.35104e-09 | 9.23669e-11 |
| fs/125/3.63 | 36 | 1.73384e-09 | 1.85329e-12 |
| tt/125/3.63 | 09 | 3.02567e-10 | 9.07318e-12 |
| ss/125/3.63 | 27 | 3.25184e-11 | 1.23967e-12 |
| sf/125/3.63 | 45 | 5.47803e-11 | 5.66513e-11 |
| **tt/27/3.30 (nominal)** | 05 | **1.21810e-12** | **3.97275e-13** |
| ff/−40/3.63 | 12 | 4.51073e-13 | 6.69613e-13 |

**The issue's own order-of-magnitude premise was "0.1–1 nA/µm at `ff`/125 °C".
Measured at that corner: NMOS 3.07 nA/µm — 3× above the top of that range —
and PMOS 0.105 nA/µm, at its bottom.** So the premise was right in spirit and
low by ~3× for the device that dominates.

### Cross-check: the two leakage testbenches agree

The stopped ring's 10.47 nA at `ff`/+10 %/+125 °C should decompose into the
per-device figures above. In the latched state, two inverters have their input
low (NMOS `w = 1 µm` off) and two have it high (PMOS `w = 2 µm` off):

```
2 × (1 µm × 3.070 nA/µm)  +  2 × (2 µm × 0.1047 nA/µm)  =  6.56 nA
```

leaving **3.91 nA** for the NAND stage, whose off device is a 2 µm NMOS in a
series stack — an unstacked 2 µm NMOS would leak 6.14 nA, so the residual
implies a ~1.6× stack-effect reduction. That is the textbook magnitude for a
two-high NMOS stack. Two independently-written testbenches, one at device level
and one at gate level, reconcile to within the stack effect.

### Leakage per micron of total device width

Normalizing the stopped ring by its own total device width gives a coefficient
that can be carried to logic that has not been designed yet. The stopped ring
contains 4 × (2 µm PMOS + 1 µm NMOS) + (2 × 2 µm PMOS + 2 × 2 µm NMOS) =
**20 µm** of total device width, so at `ff`/+10 %/+125 °C:

```
10.47 nA / 20 µm = 0.524 nA per µm of total device width
```

This is a static-CMOS-at-a-rail figure (about half the width is off at any
time, and stacks reduce it further); it is the number to multiply an
un-power-gated digital section's total device width by, and it is measured, not
assumed.

## Projection to the N-ring array

Everything in this section is **arithmetic on the measured numbers above**, not
a measurement. The arithmetic is shown so it can be re-derived or corrected.

### Active

DR-0007 §2's sizing law fixes N at the *entropy*-binding corner; the Power row
binds at the *active*-power corner. They are different corners, so the
projection is: take N from DR-0007, evaluate power at `ff`/+10 %/−40 °C.

| N | Source of N | Array active power at `ff`/−40 °C/3.63 V | vs `< 500 µW` |
|---|---|---|---|
| 1 | — | 1.93 mW | **3.87× over** |
| 95 | max N the idle row allows (below) | 184 mW | 367× over |
| 170 | DR-0007 §3's 3-stage lever, low end | ~339 mW (projected ring power, see below) | ~677× over |
| **560** | **DR-0007 §3 first-cut `N₀`** | **1.083 W** | **2166× over** |

- At nominal instead of the binding corner, `N₀ = 560` projects **620 mW** —
  which supersedes DR-0007's own "~250 mW" order-of-magnitude figure by the
  2.53× capacitance factor established above.
- **A single ring already exceeds the entire active budget by 3.9× at the
  binding corner.** Even at the most favourable point in the whole 27-point
  grid (`ss`/125 °C/2.97 V, 0.575 mW), one ring is 1.15× the budget. **There is
  no N ≥ 1 that satisfies the `< 500 µW` active row with this delay cell at
  this oscillation frequency.** This is the single most important sentence in
  this document: the active row is not failed by a *sizing* decision, it is
  failed by the *operating point of one ring*.
- **DR-0007 §3's "shorter rings" lever does not reduce per-ring power.** For a
  fixed delay cell, `P ≈ n · C_eff · V² · f_osc` and `f_osc ∝ 1/n`, so `n·f_osc`
  — and hence power — is set by the cell's delay, not by the stage count.
  Projecting the measured 5-stage power onto the measured 3-stage period
  (`sim/records/2026-07-31-ro-inv-03stage-jitter-*.md`, `T₀` = 2.531e-10 s at
  `ff`/−40/3.63): `1.934 mW × (4.3425/2.531) × (3/5) = 1.99 mW` per 3-stage
  ring, i.e. **3 % higher, not lower**. The 3-stage lever buys `Q` (fewer
  rings) at flat per-ring power, so it moves the array total roughly as N does:
  N ≈ 170 → ~339 mW. Still ~677× over. (This row is a projection from a
  measured period and a measured power, not a measured 3-stage power; a
  3-stage `ro-inv-03stage-power` run would settle it, and is cheap.)
- **What the budget actually allows**, as coefficients #7 can size against, at
  `ff`/+10 %: with `C_eff = 12.75 fF` and `V = 3.63 V`, `500 µW` supports
  `n · f_osc ≤ 2.98 GHz` summed over the whole array. That is **one 5-stage
  ring at ≤ 596 MHz**, or **560 rings at ≤ 1.07 MHz each** — against a measured
  2.30 GHz. Any resolution has to find its factor of 2166 inside
  `N · n · C_eff · V² · f_osc`, and this document's measurements pin three of
  those five factors.

### Idle

| N | Array stopped-ring leakage at `ff`/+10 %/+125 °C | vs `< 1 µA` |
|---|---|---|
| 1 | 10.5 nA | 0.010× — fits with 95× margin |
| **95** | **0.994 µA** | **the largest N that fits, rings only, with nothing else in the block** |
| **560** (DR-0007 `N₀`) | **5.86 µA** | **5.9× over** |

Plus the digital section, which is not designed and therefore not measured. The
issue's framing — "an ungated few-kGE digital section is order 10⁴ µm of
leaking width" — can now be evaluated with a measured coefficient instead of a
textbook one:

```
10⁴ µm × 0.524 nA/µm  =  5.24 µA        (assumed width, measured coefficient)
```

**5.2× the entire idle row, from the digital section alone, before a single
ring is added.** Equivalently: the `< 1 µA` row is exhausted by **1.9 × 10³ µm**
of un-power-gated total device width at that corner. The width is an assumption
and is flagged as one — but the coefficient behind it is now evidence, and the
conclusion is insensitive to a factor of two in the width.

## Verdict: can DR-0007's sizing law and the Power row both hold?

**No — and not by a margin any refinement of either number closes.**

1. **Active row (`< 500 µW` at `ff`/+10 %): not satisfiable at any N ≥ 1.** One
   candidate-A 5-stage ring measures 1.93 mW at the binding corner, 3.9× the
   whole budget. DR-0007 §2 requires N ≥ 552 at today's `Q₁`; that array
   projects 1.08 W, **2166× the row**. DR-0007 §3's stage-count lever does not
   help, because per-ring power is stage-count-independent for a fixed cell.
2. **Idle row (`< 1 µA` at `ff`/+10 %/+125 °C): not satisfiable at DR-0007's
   N, and separately not satisfiable for an un-power-gated digital section.**
   560 stopped rings leak 5.86 µA (5.9× the row) with the rest of the block
   still at zero; a 10⁴ µm ungated digital section adds a projected 5.24 µA on
   its own. The rings alone fit only up to N ≈ 95.
3. **The direction of DR-0007's own uncertainty makes this worse, not better.**
   DR-0007 §2 records that its `Q₁` is a *lower* bound (flicker excluded), so
   the N it derives is a *lower* bound too. And §Consequences' power estimate
   is now measured to be low by 2.53×. Both of the recorded uncertainties push
   the collision further apart.
4. **The two rows' binding corners are confirmed, not merely asserted.** The
   maximum active power over the covered grid is at `ff`/−40 °C/3.63 V and the
   maximum leakage over a 45-point grid including `fs`/`sf` is at
   `ff`/+125 °C/3.63 V — exactly the corners the ratified row names. Whatever
   else is wrong with the Power row, its corner bindings are right.

This is precisely the condition DR-0007 §Revisit if names ("#7's array
power/area projection, informed by the new characterization issue, shows the
§2-compliant N cannot fit the Power/Area rows"). **Handing it on, as this
issue's scope requires, without deciding it**: #7 owns array sizing, and a
superseding decision record owns whichever of the raw-rate row, the
entropy-per-raw-bit target, the delay-cell operating point, or the Power row
itself moves. This document deliberately makes no recommendation among those.

What it does supply, so that decision is quantitative rather than another
order-of-magnitude argument:

- per-ring active power at both binding corners and at nominal, on a full PVT
  grid (27 points);
- the measured `C_eff` = 12.7 fF that any future `CV²f` estimate must use in
  place of 5 fF;
- the observation that `P_ring` is stage-count-independent for a fixed cell, so
  the levers are `C_eff`, `V²`, `f_osc`, N, and duty cycle — and that DR-0003's
  *sustained* 1 Mbps rules duty cycling out while streaming;
- per-ring stopped leakage and a measured 0.524 nA/µm coefficient for
  projecting any un-power-gated logic at the idle binding corner;
- the maximum N each row admits in isolation (active: < 1; idle: 95).

## Caveats

- **Nothing downstream of the entropy source is measured.** No sampler, XOR
  tree, health tests, conditioner, register file or pad power appears in any
  number above except the explicitly-labelled 10⁴ µm digital-section leakage
  projection. Adding them can only make both rows worse.
- **The active grid does not cover `fs`/`sf`** (documented, same rationale as
  DR-0006). The leakage grids do.
- **Per-ring active power is measured for the 5-stage candidate-A ring only.**
  The 3-stage figure in the projection table is arithmetic on a measured
  5-stage power and a measured 3-stage period, not a measured 3-stage power.
  Candidate B (current-starved) is not measured at all here.
- **The stopped-ring netlist is not the free-running netlist.** The stopped
  ring has a NAND enable stage (2 extra devices); the free-running one does
  not. The active power of a NAND-enabled ring is not measured, and would be
  slightly higher than the plain ring's. Conversely the plain ring's leakage
  cannot be measured at all, for the reason given in
  [Testbenches](#testbenches).
- **`C_eff` includes short-circuit current** and is therefore an upper bound on
  physical node capacitance; the 8.7 % PVT spread bounds that share as small
  but does not separate it.
- **Leakage is a model-level result.** Subthreshold and junction leakage come
  from the PDK's BSIM4 corner decks as-is; gate leakage returns to the tied-off
  gate node and is not in the reported drain current (negligible for 3.3 V
  thick-oxide devices, but stated rather than assumed). Simulated leakage in
  any PDK is a weaker predictor of silicon than simulated switching current.
- **No power gating is designed, evaluated or recommended here** — out of scope
  for this issue by construction.

## Klayout-tools friction

None encountered. This issue's entire scope is ngspice/PDK-model-level
simulation (`sim/`); no `klayout-tools` (`klt`) invocation was needed or
attempted. Per CLAUDE.md's friction protocol, a friction issue is filed only
when the tool is actually exercised and found lacking — nothing to file here.

## What does *not* belong in this document (see `sim/README.md`)

Spec edits, architecture recommendations, and any decision about how to resolve
the collision above. Those belong to #7 and to a superseding decision record
under `spec/decision-records/`, citing the records above as their evidentiary
basis.
