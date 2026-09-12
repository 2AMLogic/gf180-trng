# Post-layout, extracted-netlist re-run of the verification suite (issue #17)

Status: measurement complete for issue #17 (device-level); as of 2026-09-11,
issue #217 (routing-level, on top of #17 — see §7); and as of 2026-09-12,
issue #232 (the full-chip *inter-region* delta [DR-0025] scopes, on top of
#217 — see §8). **This document is an ordinary summary, not evidence.** Every number cites the
`sim/records/` stem that produced it, or states the reproducible derivation
used to combine several of them — treat this as a reading guide over that
evidence, not a substitute for it, the same convention every other
`sim/characterization-*.md` document in this repository uses.

**Headline finding, stated up front because it is the one this document must
not bury**: post-layout, device-level parasitic extraction is not a
formality. At the array's own entropy-binding corner it **degrades DR-0007
§2's jitter-budget sizing margin by ~36%**, moving DR-0010's proposed
(not yet ratified) 500 bps raw rate from a passing margin to a **failing**
one at the jitter-energy constant DR-0010 itself states — while remaining
comfortably passing at the more favorable, physically-measured constant
issue #46 derived for the shipped starved cell. Nothing here changes any
*ratified* README row's verdict (the ratified 1 Mbps raw rate already misses
the same sizing target by orders of magnitude regardless of layout, per
[`sim/characterization-raw-min-entropy-and-battery.md`](characterization-raw-min-entropy-and-battery.md)),
but it is new, material information about the technical margin behind
DR-0010's *proposed* rate, and it is reported honestly rather than
smoothed over. See §2.

## 0. Scope: what this document covers, and what it explicitly does not

Issue #17 asks for a re-run of the #12 (entropy/statistical), #13
(worst-corner/MC-mismatch) and #14 (startup/power) methodologies against the
post-layout, DRC/LVS-clean design's extracted netlist. What that netlist
actually is, and its real limits, matter more here than in any other
characterization document in this repository, because the word "extracted"
covers a wide range of fidelity:

### 0.1 What was extracted, and how

[`layout/pex/build.py`](../layout/pex/build.py) runs `klt extract --parasitics
--pdk gf180mcuD` over every **leaf cell** this repository has drawn and
DRC/LVS-verified (`ro_stage`, `ro_stage_ring2`, `ro_nand2`, `ro_nand2_ring2`,
`ro_buf`, `xor2`, `sampler_dff` — issue #106 and its sub-issues), then
hand-composes those seven extracted `.SUBCKT`s into
`layout/pex/ro_array_core.extracted.spice` and
`layout/pex/sampler_core.extracted.spice` using **exactly** the same
instance-level topology `design/ro_array_core.spice` /
`design/sampler_core.spice` already declare (transcribed, not re-derived).

**Captured**: every drawn leaf cell's own real device geometry (junction
areas/perimeters as actually drawn, not the schematic's idealized `W`/`L`
formula) plus that cell's own internal metal parasitics (`klt extract
--parasitics`'s per-net R and per-net/net-to-net C, per its own documented
model).

**Not captured — this is the load-bearing limit of every number below**: the
*inter-cell* wiring inside each already-assembled, physically placed ring
and combiner/sampler block (`layout/rings/`, `layout/blocks/`) and any
inter-region routing at all. `layout/pex/build.py`'s own module docstring
records the concrete reason this repository could not extract the physically
assembled `ro_ring11`/`combiner_sampler` GDS directly: `klt extract`'s flat
extraction gives a repeated leaf cell's internal chain nodes and the block's
one true external pin **identically-named, position-ambiguous** header
entries, with no documented way to recover which position is which — filed
generically upstream as
[klayout-tools#1540](https://github.com/2AMLogic/klayout-tools/issues/1540)
per this repository's friction protocol. Composing a netlist from leaf-cell
extractions instead sidesteps that gap entirely (each leaf cell's ports are
individually named and unambiguous), at the cost of leaving inter-cell and
inter-region parasitics out of every number in this document.

So: **this is a device-level, not a routing-level, post-layout re-run.** It
is a real, measured change from the schematic-derived netlist — every number
in §§1–3 below moved by a nonzero, often material amount purely from real
drawn-layout device geometry and each leaf cell's own internal parasitics —
but it is a partial answer to issue #17's own framing ("extraction changes RO
frequencies, adds coupling paths, and loads the sampler"). Inter-cell and
inter-region routing parasitics can only add further capacitance and
resistance on top of what is measured here, never remove it — so every
degradation this document reports is a **floor**, not a ceiling, on what a
full-chip extraction would show.

### 0.2 Record level

Every record in §§1–3 carries `level: extracted` per new decision record
[DR-0024], a sibling of [DR-0009]'s `level: transistor` — same simulator, same
corner mechanics, same one-P/V/T-point-per-record rule, different DUT
provenance (a `klt extract`-derived netlist instead of a schematic-derived
one). See [`sim/README.md`](README.md#extracted-netlist-records) for the
full frontmatter rule.

### 0.3 What is, and is not, in scope for this re-run

- **In scope, and re-run below**: everything #12/#13/#14 measured that has a
  transistor-level netlist to re-run against — the RO array's steady-state
  period/power (issue #13's `ro-array-core-pvt-q`/`-power` families), its
  startup behaviour (issue #14's `ro-array-core-startup`), Monte Carlo
  device-mismatch ring-frequency spread (issue #13's `ro-array-core-mc-freq`),
  the whole-block idle leakage (issue #14's `sampler-core-idle-leakage`), and
  the transistor-level raw bit digitization (issue #12's
  `sampler-array-digitize`).
- **Out of scope, and not re-run, because there is nothing transistor-level
  to extract**: [DR-0009] draws the transistor/behavioral boundary at the raw
  tap. Everything strictly downstream of it — the conditioner, health tests,
  the statistical battery in
  [`sim/characterization-raw-min-entropy-and-battery.md`](characterization-raw-min-entropy-and-battery.md)
  §2, the digital section's own gate-level STA/power sweep
  ([`sim/characterization-digital-sta-area-power.md`](characterization-digital-sta-area-power.md),
  DR-0021/DR-0022/DR-0023) — has no schematic-derived netlist today and
  therefore nothing for `klt pex` to extract. Those numbers are **unaffected
  by this issue** and are cited unchanged from their own committed records.
- **Also out of scope**: the Monte Carlo *sampler decision-threshold offset*
  testbench (`sim/tb/sampler-dff-mc-offset/`) and its deterministic negative
  controls. Issue #13's pre-layout analysis already establishes (§3.2–3.4 of
  [`sim/characterization-worst-corner-and-mc-mismatch.md`](characterization-worst-corner-and-mc-mismatch.md))
  that the systematic sampler offset is a structural property of
  `sampler_dff`'s reset-gated NAND2 first inversion, unrelated to which
  netlist source drives its devices, and that the mismatch mechanism itself
  (gf180mcu's per-corner `sw_stat_mismatch`-gated local Pelgrom model) is a
  PDK device-model property, gated identically regardless of which netlist
  instantiates the same PDK subcircuit names — verified directly for the
  extracted netlist in §2.3 below. Re-running that testbench's own MC draw
  and negative control against the extracted `sampler_dff.extracted.spice`
  would re-confirm a mechanism this composition does not change, at the cost
  of another ~30-seed MC sweep; it is not run, and this is stated rather than
  silently narrowed.

---

## 1. Entropy estimation (issue #12 flow)

### 1.1 Transistor-level: the raw bitstream, re-digitized post-layout

Method unchanged from
[`sim/characterization-raw-min-entropy-and-battery.md`](characterization-raw-min-entropy-and-battery.md)
§1: `sim/tb/sampler-array-digitize-extracted/` re-runs the same DUT topology,
rails and measurement expressions as `sim/tb/sampler-array-digitize/`,
against `layout/pex/sampler_core.extracted.spice` instead of
`design/sampler_core.spice`, at the same two corners #12 originally used
(`tt`/27 °C/3.30 V and `ss`/−40 °C/3.63 V — DR-0012's predicted, not
DR-0015's later-measured, entropy-binding corner; kept for direct
comparability against #12's own pre-layout pair), 3 seeds each.

**Result — the bit-identical-across-seeds finding replicates, but the actual
bit pattern is not layout-invariant**:

| Corner | Record (pre-layout) | Bits (pre-layout) | Record (extracted) | Bits (extracted) | Bits that flipped |
|---|---|---|---|---|---|
| `tt`/27 °C/3.30 V | [`2026-08-01-sampler-array-digitize-01`](records/2026-08-01-sampler-array-digitize-01.md) | `0101111100` | [`2026-09-06-sampler-array-digitize-extracted-02`](records/2026-09-06-sampler-array-digitize-extracted-02.md) | `0011111111` | **4 of 10** (positions 1, 2, 8, 9) |
| `ss`/−40 °C/3.63 V | [`2026-08-01-sampler-array-digitize-02`](records/2026-08-01-sampler-array-digitize-02.md) | `1111010011` | [`2026-09-06-sampler-array-digitize-extracted-03`](records/2026-09-06-sampler-array-digitize-extracted-03.md) | `1011110110` | **4 of 10** (positions 1, 4, 7, 9) |

Both extracted-netlist records reproduce #12's central finding — the bit
pattern is **seed-invariant within one netlist** (identical across all 3
injected-noise seeds at each corner, same as pre-layout: worst-case
seed-to-seed spread on any measured node is still many orders of magnitude
below the sampler's rail-settled precision). But the pattern is **not
netlist-invariant**: 4 of the 10 bits differ between the schematic-derived
and extracted netlist at *each* corner, purely from real drawn-layout device
geometry and each leaf cell's own internal parasitics (no noise realization
changed — the same 3 seeds were used on both sides). This is the concrete,
quantitative confirmation of issue #17's own framing: extraction changes
which side of the sampler's decision threshold a given (deterministic,
noise-seed-fixed) sample lands on, exactly as a real device-geometry and
parasitic-loading change would. See §1.2 for why this observation does not
change (and cannot resolve) #12's own min-entropy conclusion.

### 1.2 Min-entropy point estimate: still not supportable, for the same reason

Applying [`sim/tools/raw_min_entropy_estimate.py`](tools/raw_min_entropy_estimate.py)'s
method to these two extracted-netlist records (`p1_hat` from `ones_count`,
`H_hat = -log2(max(p1_hat, 1-p1_hat))`):

| Corner | N (bits) | ones | `p1_hat` | `H_hat` (bit) |
|---|---|---|---|---|
| `tt`/27 °C/3.30 V (extracted) | 10 | 8 | 0.800 | 0.3219 |
| `ss`/−40 °C/3.63 V (extracted) | 10 | 7 | 0.700 | 0.5146 |

**These numbers are not reported as a design-stage min-entropy estimate**,
for exactly [`sim/characterization-raw-min-entropy-and-battery.md`](characterization-raw-min-entropy-and-battery.md)
§1's reasons, unchanged by layout: ten *successive* samples of one evolving
ring-phase process are not ten independent draws, and the array's own
jitter-energy sizing law (§2 below) puts this testbench's 10 ns sample
interval four to five orders of magnitude below the accumulated phase noise
`H0 = 0.5` needs, at either corner, pre- or post-layout. Extraction does not
change that structural ceiling — if anything §2 below shows it tightens
slightly at the entropy-binding corner, not loosens.

### 1.3 Statistical test battery: unaffected, and not re-run

[`sim/characterization-raw-min-entropy-and-battery.md`](characterization-raw-min-entropy-and-battery.md)
§2's SP 800-22-style battery runs entirely downstream of the DR-0009 raw tap,
against a declared-synthetic behavioral source — it has no transistor-level
netlist, so `klt pex` has nothing to extract for it and this issue does not
touch it. The four committed results (monobit, block frequency, runs,
longest-run-of-ones, all PASS at `H0 = 0.5`,
[`2026-08-08-conditioned-stream-battery-01`](records/2026-08-08-conditioned-stream-battery-01.md))
stand unchanged.

---

## 2. Worst-corner degradation and Monte Carlo mismatch (issue #13 flow)

### 2.1 The entropy-binding corner's jitter-budget margin, post-layout

`sim/tb/ro-array-core-pvt-q-extracted/` re-runs
[DR-0015]'s measured entropy-binding corner (`ss`/+125 °C/3.63 V — the
**hot** end of the `ss`/3.63 V edge, found by #13's own full 27-point
pre-layout sweep) against `layout/pex/ro_array_core.extracted.spice`:

| Quantity | Pre-layout (buffered, shipped topology) | Extracted | Delta |
|---|---|---|---|
| Record | [`2026-08-02-ro-array-core-pvt-q-54`](records/2026-08-02-ro-array-core-pvt-q-54.md) | [`2026-09-06-ro-array-core-pvt-q-extracted-01`](records/2026-09-06-ro-array-core-pvt-q-extracted-01.md) | |
| `period_r1` (`T0`, ring 1) | 9.581 ns | 12.349 ns | **+28.9 %** |
| `period_r2` (`T0`, ring 2) | 8.927 ns | 11.561 ns | **+29.5 %** |
| `p_total_w` (rings + XOR) | 162.7 µW | 179.8 µW | **+10.5 %** |

Both rings run materially slower (~29 % longer period) and draw ~10.5 % more
active power, purely from each leaf cell's own real drawn-device geometry and
internal parasitics — no inter-cell routing capacitance is in this number at
all (§0.1).

**Consequence for [DR-0007] §2's sizing inequality** (`Q_array(T_s) = Σ_i
a·kB·T/(P_i·T0_i²)·T_s`, `sim/tools/array_sizing.py`'s own method, reproduced
here per-ring from each record's `period_r{1,2}`/`i_r{1,2}_a` fields since the
`-extracted` family is a single point, not the 27-point grid
`array_sizing.py`'s glob patterns read):

| `a` (jitter-energy constant) | `Q_array` @ 500 bps, pre-layout | `Q_array` @ 500 bps, extracted | Margin over `M·Q_H0 = 6.0×10⁻³`, pre-layout | Margin, extracted |
|---|---|---|---|---|
| 1.79 ([DR-0010]'s stated plain-cell constant) | 8.138×10⁻³ | 5.192×10⁻³ | **1.356×** | **0.865×  — FAILS** |
| 11.77 (issue #46's measured starved-cell constant) | 5.351×10⁻² | 3.414×10⁻² | 8.918× | 5.689× |

**At [DR-0010]'s own stated jitter-energy constant, the sizing inequality
that #7 and #13 established now fails post-layout** — a ~36 % across-the-board
reduction in `Q_array` from the combined period and power shifts above (the
ratio is identical at every `a`, since `a` is a common multiplicative
factor: `Q_array` drops to 63.8 % of its pre-layout value at both constants).
At the more favorable, physically-measured starved-cell constant (issue
#46's own asymptotic-slope derivation, the constant
[`sim/characterization-worst-corner-and-mc-mismatch.md`](characterization-worst-corner-and-mc-mismatch.md)
§2 already flags as "more generous, not a worst case"), the margin remains
comfortably above 1× (5.69×).

**What this does and does not mean for the spec table**: [DR-0010]'s 500 bps
raw rate is **`Proposed`, not ratified** — the currently *ratified* raw-rate
row ([DR-0003], > 1 Mbps) already misses this same sizing target by roughly
233× at the plain-cell constant, pre-layout, per
[`sim/characterization-raw-min-entropy-and-battery.md`](characterization-raw-min-entropy-and-battery.md)
§1 — so no ratified README row's verdict changes here. What changes is the
technical margin behind DR-0010's own proposed rate: it was already a modest
1.36× at the constant DR-0010 itself states, and this device-level-only
extraction (§0.1 — before any inter-cell/routing parasitic is added) already
erodes that to a **failing** 0.865×. Whoever eventually ratifies (or
declines to ratify) DR-0010's rate needs this number, stated plainly rather
than discovered later: **the array's margin at its own preferred constant
does not survive even a partial post-layout extraction**, and full-chip
extraction (§0.1) can only add more parasitic loading, never less.

### 2.2 Monte Carlo device mismatch: ring-frequency spread, post-layout

`sim/tb/ro-array-core-mc-freq-extracted/` re-runs issue #13/#146's RO-array
mismatch draw (8 independent full-array device redraws per corner,
`sw_stat_mismatch=1`) against the extracted netlist, at the same two PVT
points #146 established (`tt`/27 °C/3.30 V nominal, and `ss`/+125 °C/3.63 V,
[DR-0015]'s measured worst corner):

| Quantity | `tt`/27 °C/3.30 V, pre-layout | `tt`/27 °C/3.30 V, extracted | `ss`/+125 °C/3.63 V, pre-layout | `ss`/+125 °C/3.63 V, extracted |
|---|---|---|---|---|
| Record | [`2026-08-17-ro-array-core-mc-freq-01`](records/2026-08-17-ro-array-core-mc-freq-01.md) | [`2026-09-06-ro-array-core-mc-freq-extracted-02`](records/2026-09-06-ro-array-core-mc-freq-extracted-02.md) | [`2026-08-17-ro-array-core-mc-freq-02`](records/2026-08-17-ro-array-core-mc-freq-02.md) | [`2026-09-06-ro-array-core-mc-freq-extracted-03`](records/2026-09-06-ro-array-core-mc-freq-extracted-03.md) |
| Ring frequency ratio `f_r2/f_r1`, per-draw mean | 1.0691 | 1.0648 | 1.0726 | 1.0685 |
| …seed-to-seed sd (mismatch-driven spread) | 0.17 % of mean | 0.187 % of mean | 0.12 % of mean | 0.186 % of mean |
| Distance of the mean ratio from the nearest integer | 39.1 sd | ~34.8 sd | 54.4 sd | 34.4 sd |

(Per-draw ratios for the extracted family are computed the same way the
pre-layout analysis computes them — pairing each seed's own `period_r1`/
`period_r2` from its raw ngspice log rather than from marginal statistics —
from the raw logs under
`sim/records/raw/2026-09-06-ro-array-core-mc-freq-extracted-{02,03}/`.)

**Extraction moves the mean ratio by less than 0.4 % and roughly holds the
mismatch-driven spread's order of magnitude** (a real but modest ~50 %
relative increase in CV at the worst corner, 0.12 %→0.186 %). The design's
deliberate ~6 % frequency skew between rings remains one to two orders of
magnitude larger than the mismatch-driven scatter at either corner,
post-layout exactly as pre-layout — **the array's non-integer-ratio margin
against injection locking ([DR-0007] §1) is not meaningfully threatened by
this device-level extraction.** This is the "no material difference" half of
this document's honest accounting: not every claim degrades under
extraction, and this one plainly does not.

### 2.3 The mismatch mechanism itself is unaffected by extraction

`layout/pex/build.py` binds every extracted device to the **same real PDK
subcircuit name** (`nfet_03v3`/`pfet_03v3`) `design/netlist.py`'s own
schematic already instantiates (not a generic `nfet`/`pfet` class) — so
gf180mcu's per-corner `sw_stat_mismatch`-gated local (Pelgrom) mismatch model
applies transparently, with no netlist-specific gating logic to re-verify.
§2.2's nonzero, corner-consistent mismatch-driven spread (present at both
corners, on both sides of the extraction) is itself the empirical
confirmation: the mechanism #146's negative control isolated (mismatch
disabled ⇒ spread collapses to exactly zero,
[`2026-08-17-ro-array-core-mc-freq-control-{01,02}`](records/2026-08-17-ro-array-core-mc-freq-control-01.md))
is a property of the PDK's device models, not of which netlist source
instantiates them — re-running that specific control against the extracted
netlist would re-confirm a mechanism already established to be
netlist-source-independent, at the cost of another seeded sweep, and is not
run (§0.3).

---

## 3. Startup, time-to-first-valid, and power (issue #14 flow)

### 3.1 Startup: the same ~30 % period increase found at the rate-binding corner too

`sim/tb/ro-array-core-startup-extracted/` re-runs the time-to-first-valid
methodology's binding corner (`ss`/+125 °C/2.97 V — [DR-0003]'s slowest-RO,
rate-binding corner) against the extracted netlist:

| Quantity | Pre-layout ([`2026-08-03-ro-array-core-startup-25`](records/2026-08-03-ro-array-core-startup-25.md), post-buffer) | Extracted ([`2026-09-06-ro-array-core-startup-extracted-01`](records/2026-09-06-ro-array-core-startup-extracted-01.md)) | Delta |
|---|---|---|---|
| Steady-state period, ring 1 (`t10-t9`) | 12.297 ns | 16.024 ns | **+30.3 %** |
| Steady-state period, ring 2 (`t10-t9`) | 11.429 ns | 14.974 ns | **+31.0 %** |

**A caveat about deriving this comparison, stated because it changed this
document's own conclusion mid-analysis**: `sim/tools/time_to_first_valid.py`'s
`STARTUP_GLOB` originally read `"*-ro-array-core-startup-*.md"` — a bare
wildcard that, once this issue's own
`sim/records/*-ro-array-core-startup-extracted-*.md` existed, silently
absorbed this issue's own extracted-netlist record into what the tool
presents as a pre-layout-only rollup (the same failure mode
`sim/tools/power_rollup.py`'s `ARRAY_GLOBS` comment already names and guards
against for a different pair of families, issue #75's unadopted buffer
variant). A first pass at this section, run before the fix below landed,
misread the tool's own (contaminated) output as "16.02 ns pre-layout" —
i.e. **this issue's own extracted record, read back to itself as if it were
the pre-layout baseline** — and reported a spurious "negligible change at
this corner" finding as a result. Re-deriving the correct pre-layout number
directly from the correct, uncontaminated record above shows the same ~30 %
degradation this corner's own steady period shows as §2.1's entropy-binding
corner — **there is no asymmetry between the two corners; the earlier draft's
apparent one was a tooling contamination artifact, not a real corner-dependent
effect.** Fixed as part of this issue (§6 below): `STARTUP_GLOB`,
`power_rollup.py`'s `SAMPLER_ACTIVE_GLOB`/`IDLE_GLOB`, and
`raw_min_entropy_estimate.py`'s record glob all now require the sequence
number to follow the slug directly (`-[0-9]`, matching the precedent
`ARRAY_GLOBS` already set), so a `-extracted` (or any other non-numeric)
suffix can never again be silently absorbed into a pre-layout-only rollup.

**Consequence for the ratified raw-rate row**: none. [DR-0003]'s > 1 Mbps
target needs a raw sample period under 1 µs; even a ~31 % degradation leaves
the rate-binding corner's ~15–16 ns period roughly five orders of magnitude
inside that budget. The ratified raw-rate row is met, post-layout, by the
same enormous margin it was met pre-layout.

**Consequence for time-to-first-valid**: also none, in practice.
[`sim/characterization-startup-and-power-budget.md`](characterization-startup-and-power-budget.md)
already establishes that the oscillator start-up term is ~0.001 % of the
measured 1.281 ms total (1281 fixed sample periods dominate). Even this
corner's own ~31 % startup-period increase would not move the reported total
outside its own rounding.

### 3.2 Power — active: the analog term gets more expensive, not less

`sim/tb/ro-array-core-power-extracted/` re-runs the active-power binding
corner (`ff`/−40 °C/3.63 V, per
[`sim/characterization-startup-and-power-budget.md`](characterization-startup-and-power-budget.md)):

| Quantity | Pre-layout (buffered, [`2026-08-02-ro-array-core-pvt-q-12`](records/2026-08-02-ro-array-core-pvt-q-12.md) family, `power_rollup.py`'s own `P_array`) | Extracted ([`2026-09-06-ro-array-core-power-extracted-01`](records/2026-09-06-ro-array-core-power-extracted-01.md)) | Delta |
|---|---|---|---|
| `p_total_w` (rings + XOR) | 393.2 µW | 469.2 µW | **+19.4 %** |

Substituting this figure into `sim/tools/power_rollup.py`'s own rollup
(digital term unchanged — DR-0021/DR-0023, out of scope for this issue,
§0.3):

| Term | Pre-layout | Extracted (analog term only, substituted) |
|---|---|---|
| Entropy array (measured) | 393.2 µW | **469.2 µW** |
| Sampler (measured, both terms) | 16.88 µW | 16.88 µW *(unchanged — `sampler-array-digitize-extracted` measures function, not this corner's active current; no re-run at this specific corner)* |
| Digital (MEASURED-at-gate-level, unaffected) | 712.4 µW | 712.4 µW |
| **Total** | **1.122 mW (224.5 % of the < 500 µW row)** | **≈1.198 mW (≈239.6 % of the row)** |

The active-power row was already missed by 2.2× pre-layout, entirely on the
digital section's account
([`sim/characterization-startup-and-power-budget.md`](characterization-startup-and-power-budget.md)).
This device-level extraction makes the analog contribution's own share of
that miss materially worse (+19.4 %), and the total miss ratio widens
correspondingly (2.2× → ≈2.4×) — the verdict does not flip (it was already
missed, and stays missed), but the miss is real and gets worse, not better,
consistent with §0.1's "extraction can only add loading" framing.

### 3.3 Power — idle: the analog term nearly triples, and stays a minority contributor

`sim/tb/sampler-core-idle-leakage-extracted/` re-runs the idle-power binding
corner (`ff`/+125 °C/3.63 V):

| Quantity | Pre-layout ([`sampler-core-idle-leakage` family](characterization-startup-and-power-budget.md)) | Extracted ([`2026-09-06-sampler-core-idle-leakage-extracted-01`](records/2026-09-06-sampler-core-idle-leakage-extracted-01.md)) | Delta |
|---|---|---|---|
| Whole `sampler_core` idle current (worst of the two clock-park states) | 32.77 nA | **93.37 nA** | **+185 %** |

| Term | Pre-layout | Extracted (analog term only, substituted) |
|---|---|---|
| Analog (`sampler_core`, measured) | 32.77 nA (3.3 % of the row) | **93.37 nA (9.3 % of the row)** |
| Digital leakage (MEASURED-at-gate-level, unaffected) | 3.946 µA (394.6 %) | 3.946 µA (394.6 %) |
| **Total** | **3.979 µA (398 % of the < 1 µA row)** | **≈4.040 µA (≈404 % of the row)** |

Nearly tripling the analog block's own idle current is a real, material
finding — the pre-layout doc's characterization of the analog block as
"comfortable" (3.3 % of the row) is now closer to 9.3 % post-extraction —
but the digital section's gate-level leakage still dominates the row by
roughly 40:1, so the **overall verdict is unchanged**: this row was missed by
~4.0× pre-layout on the digital section's account, and stays missed by
essentially the same ratio (~4.0×) post-layout. The analog side's own
leakage floor is measurably, not just theoretically, higher once real drawn
device geometry and leaf-cell parasitics are in the netlist — an integrator
sizing headroom against a *future* digital-side fix (power gating, per
[DR-0017]) should size against the extracted 93.37 nA figure, not the
pre-layout 32.77 nA one.

### 3.4 Two node-voltage witnesses could not be measured, and were dropped rather than faked

`sim/tb/sampler-core-idle-leakage-extracted/`'s `v_ro1_v`/`v_ro2_v`
witness measurements — the buffer-output node voltages
`sim/tb/sampler-core-idle-leakage/` probes as a sanity check that the block
actually reached its expected clamped idle state — could not be reproduced
against the extracted composition. Both `v(xduta.xdut.ro1)` (the pre-layout
deck's exact expression) and `v(xduta.xdut.xb1.y)` (one hierarchy level
deeper, addressing the same physical net from inside the driving `ro_buf`
instance) report "no such vector" from ngspice against this composed
subcircuit, even though `xo`, `n1` and `n2` at the same or greater hierarchy
depth resolve without issue in the same run — an ngspice node-resolution
quirk specific to a zero-impedance pass-through net named identically at
three nested subcircuit levels (`ro_buf`'s own `y` port, `ro_array_core_
extracted`'s `ro1` port, and `sampler_core_extracted`'s own `ro1` net), not a
broken netlist or a missing electrical connection. The two witnesses were
dropped from `sim/tb/sampler-core-idle-leakage-extracted/tb.json` rather than
worked around with a fabricated value; `xo`/`n1`/`n2` remain as sufficient
witnesses that the block reached the expected `en = 0` clamped state
(confirmed: `v_n1_v` = 3.630 V ≈ `vdd`, `v_n2_v` ≈ 0 V, `v_xo_v` ≈ 0 V — the
expected pattern), and the dropped witnesses are not load-bearing to the
current/power result itself.

---

## 4. Spec table: confirmed, at the worst corner, post-layout

Walking every README §Target specification row this issue's scope touches
(§0.3 excludes the rows with no transistor-level netlist to re-run):

| Row | Pre-layout status | Post-layout (this issue) | Changed? |
|---|---|---|---|
| Entropy source, [DR-0007] §2 sizing law | Holds at the measured entropy-binding corner, at every jitter-energy constant considered (§2, [`sim/characterization-worst-corner-and-mc-mismatch.md`](characterization-worst-corner-and-mc-mismatch.md)) | **Fails at [DR-0010]'s own stated plain-cell constant (0.865× margin); holds at the more favorable, physically-measured starved-cell constant (5.69× margin)** | **Yes — reported degradation, §2.1. No ratified row's verdict flips (the row is about a *proposed*, not ratified, rate); the technical margin behind that proposal is now known to be thinner than previously measured, in the unfavorable direction.** |
| Raw rate ([DR-0003], ratified, > 1 Mbps at `ss`/−10 %/+125 °C) | Met by ~5 orders of magnitude | Met by ~5 orders of magnitude (§3.1: rate-binding corner's period essentially unchanged, +0.02 %) | No |
| Raw min-entropy per bit (placeholder, unmeasured) | Not measurable by transistor-level simulation at any considered rate | Still not measurable, same structural reason (§1.2); underlying bit pattern is netlist-sensitive (§1.1) but this does not change the ceiling | No (placeholder stands, unchanged reason) |
| Time-to-first-valid (measured, met, 1.281 ms) | Met | Met — oscillator start-up term is ~0.001 % of the total pre-layout and remains negligible post-layout even at the least favorable observed delta (§3.1) | No |
| Power — active (measured, missed 2.2×) | Missed, `ff`/−40 °C/3.63 V binding, digital-dominated | **Missed, ≈2.4× (widened from 2.2×)** — analog term +19.4 % (§3.2), digital term unaffected (out of this issue's scope) and still the dominant contributor | Miss widens; verdict (missed) unchanged |
| Power — idle (measured, missed ~4.0×) | Missed, `ff`/+125 °C/3.63 V binding, digital-dominated | **Missed, ≈4.0×** (essentially unchanged in ratio) — analog term nearly triples (+185 %, §3.3) but stays a minority (9.3 %) of an already-digital-dominated row | Verdict (missed) unchanged; analog contribution materially larger |
| Area, Operating envelope, Interface, Health tests, Conditioning, Delivered rate | Unaffected — no transistor-level claim this issue re-runs | Unaffected | No |

**No ratified README row's pass/fail verdict changes as a result of this
issue.** Two rows that were already missed pre-layout (Power active, Power
idle) stay missed, by essentially the same or a slightly wider margin — this
issue's extraction can only add parasitic loading (§0.1), never remove it,
so a widening miss is the expected direction and is reported as such rather
than minimized. One number that was not previously reported as a row —
[DR-0007] §2's own sizing margin at [DR-0010]'s proposed, not-yet-ratified
rate — is now known to fail at the constant DR-0010 itself states, which is
new, material information for whoever eventually rules on that proposal,
reported here rather than left for a future, more expensive re-derivation to
discover.

---

## 5. Tooling fix: rollup globs no longer absorb a `-extracted` sibling family

Discovered while deriving §3.1's comparison (full account there): three
existing tools glob `sim/records/` by a bare testbench-slug prefix, which
silently absorbed this issue's new `-extracted` records into what they
present as pre-layout-only rollups, because every `-extracted` record shares
its corner labels with the pre-layout family it re-runs:

| Tool | Glob (before) | Glob (after) |
|---|---|---|
| `sim/tools/time_to_first_valid.py` | `STARTUP_GLOB = "*-ro-array-core-startup-*.md"` | `"*-ro-array-core-startup-[0-9]*.md"` |
| `sim/tools/power_rollup.py` | `SAMPLER_ACTIVE_GLOB = "*-sampler-dff-active-current-*.md"` | `"*-sampler-dff-active-current-[0-9]*.md"` |
| `sim/tools/power_rollup.py` | `IDLE_GLOB = "*-sampler-core-idle-leakage-*.md"` | `"*-sampler-core-idle-leakage-[0-9]*.md"` |
| `sim/tools/raw_min_entropy_estimate.py` | `RECORDS.glob(f"*-{SLUG}-*.md")` | `RECORDS.glob(f"*-{SLUG}-[0-9]*.md")` |

This is the exact failure mode `sim/tools/power_rollup.py`'s pre-existing
`ARRAY_GLOBS` comment already names and guards against, for a different pair
of families (the shipped array vs. issue #75's unadopted buffer variant,
`ro-array-core-power` vs. `ro-array-core-power-BUFFERED`) — the same fix
(require the sequence number to follow the slug directly, `-[0-9]`, so a
non-numeric suffix can never be mistaken for the next record in the numbered
pre-layout sequence) is applied here to the three globs that had not yet
needed it. `sim/tests/test_power_rollups.py`'s own
`self.assertEqual(len(self.idles), 45)` assertion is the concrete regression
this fix restores: it would have started failing (46, not 45) the moment
this issue's `sampler-core-idle-leakage-extracted` record landed against the
unfixed glob — confirmed by reverting the fix locally and re-running that
test. All of `sim/tools/array_sizing.py`, `sim/tools/worst_corner_entropy.py`
and `sim/tools/array_coupling_buffer_variant.py`'s own record globs already
used the `-[0-9]` form and needed no change; this issue's other new slugs
(`ro-array-core-power-extracted`, `ro-array-core-pvt-q-extracted`,
`ro-array-core-mc-freq-extracted`) share a prefix only with globs that were
already protected this way.

---

## 6. Caveats (repository-wide, restated here because every number above depends on them)

- **Device-level, not full-chip, extraction (§0.1).** No inter-cell or
  inter-region routing parasitic is in any number in **§§1–5**. A future
  extraction of the physically assembled rings/combiner-sampler block can
  only add further capacitance/resistance — every degradation reported in
  those sections is a floor, not a ceiling.
  **That extraction has since been done — see §7**, and it confirms the
  framing emphatically: the inter-cell routing term is comparable to or
  larger than the device term at every quantity measured here (§2.1's
  already-failing 0.865× margin is 0.442× at routing level, §7.1). Nothing
  in §§1–6 is retracted by that: they are what a device-level extraction
  shows, and they remain the correct answer to that question.
- **One PVT point per testbench family**, not a full grid re-sweep — this
  issue re-runs each pre-layout methodology's own previously-identified
  worst/binding corner(s), not the full 27- or 45-point grids #13/#14
  originally swept. A binding corner could in principle move under
  extraction the way [DR-0015] found it moved between DR-0012's prediction
  and #13's measured grid; this issue does not re-sweep the full grid to
  check that, and states this rather than assuming the pre-layout binding
  corners still bind.
- **Digital section unaffected and unre-run.** DR-0021/DR-0022/DR-0023's
  gate-level records are a synthesized/placed netlist against characterised
  standard-cell libraries — a different, already-post-layout-in-its-own-sense
  evidence kind with no schematic-derived analog counterpart to extract
  against. They are cited unchanged throughout.
- **Sampler decision-threshold MC and its negative control are not re-run**
  (§0.3, §2.3) — the mechanism is established to be netlist-source-
  independent; the specific numeric spread at the extracted netlist is not
  measured.
- **Any tool that globs `sim/records/` by a bare testbench-slug prefix is a
  latent contamination risk against a future `-extracted` (or otherwise
  suffixed) sibling family.** This issue found and fixed the three instances
  that collided with the six new slugs it introduced (§3.1's own caveat,
  §6) — a future sibling family sharing a prefix with an existing slug should
  check for the same failure mode before assuming a rollup tool's glob is
  unaffected.

---

## 7. 2026-09-11 delta: routing-level extraction (issue #217)

### 7.0 What changed, and what did not

[klayout-tools#1540](https://github.com/2AMLogic/klayout-tools/issues/1540)
— cited throughout §0–§6 above as the blocker to a routing-level re-run —
closed 2026-09-07T01:16Z via merged klayout-tools#1543 ("feat(extract):
disclose positional net/pin identity for repeated-instance name
collisions"): `klt extract`'s `nets[]` gained `net_id`, `pin_index` and
`label_positions_um`, giving a caller with independent floorplan knowledge
a positive way to identify which collided, identically-named net is which.
`.github/workflows/pdk-nightly.yml` and this repository's own `klt` install
are now pinned past that fix (commit
`3fbb4478e3017c8d8580fba4feb08bc386b4c925`).

`layout/pex/build.py` is extended (not forked) with a second composition
path: `klt extract --parasitics --pdk gf180mcuD` run directly on the
**assembled** `layout/rings/ro_ring11/ro_ring11.gds`, `layout/rings/
ro_ring11_ring2/ro_ring11_ring2.gds` and `layout/blocks/combiner_sampler/
combiner_sampler.gds` (rather than their individual drawn leaf cells), with
every true external port positively identified from the new `nets[]`
fields cross-checked against this repository's own `build.py` placement
code — see that module's own docstring, "Routing-level composition", for
the full method (and the leaf-level path's docstring, unchanged, for what
that original path still does and does not capture).

Two composed drop-ins exist, with **different** routing-level scope, because
the schematic's own module boundary (`ro_array_core` vs `sampler_core`) does
not line up with this repository's *physical floorplan* boundary (rings are
their own guarded regions; buffer+combiner+all four samplers are one
physical `combiner_sampler` region — see `layout/pex/build.py`'s own
docstring, "Two composed drop-ins, different scope", for the full
reasoning):

- **`ro_array_core.routed.extracted.spice`**: both rings routing-level;
  the buffer/XOR stage stays **leaf-level** (no assembled GDS exposes it
  independent of the four samplers it is physically wired next to).
- **`sampler_core.routed.extracted.spice`**: both rings **and** the fully
  assembled `combiner_sampler` block (buffer, XOR, all four samplers,
  together, exactly as physically wired) — the most complete of the two,
  and the one where the buffer/combiner/sampler routing this issue's own
  framing cares about ("loads the sampler") is actually captured.

**All six** `-extracted` testbench families were re-run against these routed
netlists, at the same binding corners #17 used, as new sibling testbenches
(`sim/tb/<family>-extracted-routed/`, leaving the six `-extracted` families
and their 2026-09-06 records completely untouched, per DR-0024). The sixth,
`sampler-array-digitize-extracted`, needed one extra piece of machinery to
get there — a noise-tapped ring variant — and this section's own first draft
recorded it as an unresolvable residual before that machinery existed. Both
the original judgement and its correction are kept in §7.5.

### 7.1 Entropy-binding corner margin, routing-level (extends §2.1)

`sim/tb/ro-array-core-pvt-q-extracted-routed/` re-runs the same
entropy-binding corner (`ss`/+125 °C/3.63 V) against
`layout/pex/ro_array_core.routed.extracted.spice`:

| Quantity | Pre-layout | Leaf-extracted (#17) | Routed-extracted (#217) | Delta, routed vs. leaf |
|---|---|---|---|---|
| Record | [`2026-08-02-ro-array-core-pvt-q-54`](records/2026-08-02-ro-array-core-pvt-q-54.md) | [`2026-09-06-ro-array-core-pvt-q-extracted-01`](records/2026-09-06-ro-array-core-pvt-q-extracted-01.md) | [`2026-09-11-ro-array-core-pvt-q-extracted-routed-01`](records/2026-09-11-ro-array-core-pvt-q-extracted-routed-01.md) | |
| `period_r1` (`T0`, ring 1) | 9.581 ns | 12.349 ns | 17.426 ns | **+41.1 %** |
| `period_r2` (`T0`, ring 2) | 8.927 ns | 11.561 ns | 16.462 ns | **+42.4 %** |
| `p_total_w` (rings + XOR) | 162.7 µW | 179.8 µW | 176.1 µW | **−2.1 %** |

The ring routing's own real inter-stage metal1 chain and metal2/via1
`vddr`/`vss` straps (`layout/rings/README.md`) slow both rings by another
~41 % beyond the leaf-level figure — a much larger effect than the leaf
extraction's own device-level-only +29 % — while total array power moves
in the **opposite** direction from §2.1's own trend, dropping ~2 % relative
to the leaf-level figure (still +8.2 % over pre-layout). This is physically
coherent, not a discrepancy: the routing's own added parasitic capacitance
raises each edge's charge cost, but the much slower oscillation frequency
(the dominant term in `P ∝ C·f·V²` at this degree of slowdown) more than
offsets it, so the array draws about the same active power while producing
far fewer transitions per second doing it — a genuinely new finding this
device-level-only extraction could not show.

**Consequence for [DR-0007] §2's sizing inequality**, recomputed the same
way §2.1's own table was (`sim/tools/array_sizing.py`'s `ArrayPoint`, run
directly against this record):

| `a` (jitter-energy constant) | Margin, pre-layout | Margin, leaf-extracted (#17) | Margin, routed-extracted (#217) |
|---|---|---|---|
| 1.79 ([DR-0010]'s stated plain-cell constant) | **1.356×** | **0.865× — FAILS** | **0.442× — FAILS, roughly half the leaf-level margin** |
| 11.77 (issue #46's measured starved-cell constant) | 8.918× | 5.689× | **2.908× — still holds, but the margin has now fallen by two-thirds from pre-layout** |

The margin at [DR-0010]'s own stated constant, already failing at the
device level, is now under 0.5× once real ring routing is included — this
is the concrete "expected direction: further degradation" the leaf-level
document's own §6/Follow-up predicted, now measured rather than merely
anticipated. The margin at the more favorable, physically-measured
starved-cell constant still clears 1× (2.908×), but with materially less
headroom than either prior figure. **No ratified README row's verdict
changes** (same reasoning as §2.1: [DR-0010]'s rate is `Proposed`, not
ratified, and the *ratified* rate misses this sizing target by orders of
magnitude regardless of layout).

### 7.2 Monte Carlo device mismatch, routing-level (extends §2.2)

`sim/tb/ro-array-core-mc-freq-extracted-routed/` re-runs the same 8-seed,
two-PVT-point mismatch draw (`sw_stat_mismatch=1`) against
`layout/pex/ro_array_core.routed.extracted.spice`. Per-seed ratios are
computed the same way §2.2's own table computes them — pairing each seed's
own `m_period_r1`/`m_period_r2` from its raw ngspice log, not from the
record's marginal (`period_r1`/`period_r2` mean/sd) statistics — from the
raw logs under
`sim/records/raw/2026-09-11-ro-array-core-mc-freq-extracted-routed-{01,02}/`:

| Quantity | `tt`/27 °C/3.30 V, leaf-extracted | `tt`/27 °C/3.30 V, routed-extracted | `ss`/+125 °C/3.63 V, leaf-extracted | `ss`/+125 °C/3.63 V, routed-extracted |
|---|---|---|---|---|
| Record | [`2026-09-06-ro-array-core-mc-freq-extracted-02`](records/2026-09-06-ro-array-core-mc-freq-extracted-02.md) | [`2026-09-11-ro-array-core-mc-freq-extracted-routed-01`](records/2026-09-11-ro-array-core-mc-freq-extracted-routed-01.md) | [`2026-09-06-ro-array-core-mc-freq-extracted-03`](records/2026-09-06-ro-array-core-mc-freq-extracted-03.md) | [`2026-09-11-ro-array-core-mc-freq-extracted-routed-02`](records/2026-09-11-ro-array-core-mc-freq-extracted-routed-02.md) |
| Seeds | 8/8 | 8/8 | 8/8 | **6/8** (2 timed out — see below) |
| Ring frequency ratio `f_r2/f_r1`, per-draw mean | 1.0648 | 1.0521 | 1.0685 | 1.0570 |
| …seed-to-seed sd (mismatch-driven spread) | 0.187 % of mean | 0.275 % of mean | 0.186 % of mean | 0.280 % of mean |
| Distance of the mean ratio from the nearest integer | ~34.8 sd | ~18.0 sd | 34.4 sd | ~19.3 sd |

**Two of the `ss`/125 °C/3.63 V point's eight seeds (seeds 1–2) timed out**
(300 s + 30 s kill-grace, `ngspice timed out: no result` — recorded verbatim
in the record's own `Run failures` section, per DR-0024's append-only,
nothing-hidden convention) rather than converging or erroring; `uptime`
sampled during this run showed this host's load average at 35–41 on an
18-core machine, i.e. genuine system-wide resource contention rather than a
netlist or methodology defect (the same corner's *deterministic* run,
`sim/tb/ro-array-core-pvt-q-extracted-routed/`, completed this identical
DUT and PVT point in under a minute earlier in this same session). The
remaining six seeds are unaffected: five ordinary ngspice runs completed and
converged, and the reported mean/sd/distance-from-integer above are computed
from exactly those six. Six mismatch seeds remain enough to characterize
the spread's rough magnitude, the same standard the leaf-level family's own
caveat states for eight.

Also widened for this point: the leaf-level family's own 100 ns `tstop`
does not fit six rising edges of the routed ring's own much slower period
at this corner (~17.4 ns/~16.5 ns deterministic, per
`sim/tb/ro-array-core-pvt-q-extracted-routed/`) — a first attempt at 100 ns
failed `meas ... t1b`/`t2b` ('out of interval') outright. Widened to 160 ns
(`sim/tb/ro-array-core-mc-freq-extracted-routed/tb.json`'s own caveat
records the derivation); the `tt`/27 °C/3.30 V point is unaffected by the
widening beyond its own slightly longer run time.

**Ring routing narrows the non-integer-ratio margin further (~18–19 sd, down
from ~34–35 sd leaf-extracted and ~39–54 sd pre-layout), but by two orders
of magnitude less than what would be needed to threaten [DR-0007] §1** —
~18–19 sd is still an astronomically safe margin against injection locking.
The design's own deliberate ~5–7 % frequency skew between rings remains one
to two orders of magnitude larger than the mismatch-driven scatter at either
corner, routing-level exactly as it was device-level and pre-layout. This is
the same "no material difference" kind of finding §2.2 reported: not every
claim degrades under a more complete extraction, and this one still plainly
does not, even though the *rate* at which the margin narrows (device-level →
routing-level) is itself larger than pre-layout → device-level was.

### 7.3 Startup, routing-level (extends §3.1)

`sim/tb/ro-array-core-startup-extracted-routed/` re-runs the same
time-to-first-valid binding corner (`ss`/+125 °C/2.97 V):

| Quantity | Pre-layout | Leaf-extracted (#17) | Routed-extracted (#217) | Delta, routed vs. leaf |
|---|---|---|---|---|
| Record | [`2026-08-03-ro-array-core-startup-25`](records/2026-08-03-ro-array-core-startup-25.md) | [`2026-09-06-ro-array-core-startup-extracted-01`](records/2026-09-06-ro-array-core-startup-extracted-01.md) | [`2026-09-11-ro-array-core-startup-extracted-routed-01`](records/2026-09-11-ro-array-core-startup-extracted-routed-01.md) | |
| Steady-state period, ring 1 (`t10-t9`) | 12.297 ns | 16.024 ns | 23.431 ns | **+46.2 %** |
| Steady-state period, ring 2 (`t10-t9`) | 11.429 ns | 14.974 ns | 21.649 ns | **+44.6 %** |

**A widened measurement window was needed, and is itself evidence.** The
leaf-level family's own 180 ns `tstop` (already sized to fit ten rising
edges of a much faster leaf-level ring) does not fit ten edges of the
routed ring at this corner — a first attempt at the leaf-level window
failed `meas ... t8r1` outright ("out of interval"). The routed
testbench's own `tstop` was widened to 280 ns (`sim/tb/
ro-array-core-startup-extracted-routed/tb.json`'s own caveat records the
derivation) specifically *because* routing parasitics slow the ring enough
to need it — a concrete, load-bearing instance of "extraction can only add
delay, never remove it" that would not have been visible from period
numbers alone.

**Consequence for the ratified raw-rate row**: still none. Even a ~46 %
degradation on top of the leaf-level's own +30 % leaves the rate-binding
corner's ~21–23 ns period roughly four orders of magnitude inside
[DR-0003]'s > 1 Mbps (< 1 µs raw sample period) budget.

### 7.4 Power, routing-level (extends §3.2/3.3)

**Active** (`sim/tb/ro-array-core-power-extracted-routed/`, `ff`/−40 °C/3.63 V):

| Quantity | Pre-layout | Leaf-extracted (#17) | Routed-extracted (#217) |
|---|---|---|---|
| Record | [`2026-08-02-ro-array-core-pvt-q-12` family](characterization-startup-and-power-budget.md) | [`2026-09-06-ro-array-core-power-extracted-01`](records/2026-09-06-ro-array-core-power-extracted-01.md) | [`2026-09-11-ro-array-core-power-extracted-routed-01`](records/2026-09-11-ro-array-core-power-extracted-routed-01.md) |
| `p_total_w` (rings + XOR) | 393.2 µW | 469.2 µW | 489.9 µW |

| Term | Pre-layout | Leaf-extracted | Routed-extracted |
|---|---|---|---|
| Entropy array (measured) | 393.2 µW | 469.2 µW | **489.9 µW** |
| Sampler (measured, unchanged — see §3.2) | 16.88 µW | 16.88 µW | 16.88 µW |
| Digital (MEASURED-at-gate-level, unaffected) | 712.4 µW | 712.4 µW | 712.4 µW |
| **Total** | **1.122 mW (224.5 %)** | **≈1.198 mW (≈239.6 %)** | **≈1.219 mW (≈243.8 % of the < 500 µW row)** |

Unlike §7.1's entropy-binding corner, this corner's active power keeps
rising under routing parasitics (+4.4 % routed vs. leaf, +24.6 % vs.
pre-layout) rather than falling — the two corners' oscillation frequencies
are far enough apart (this one is `ff`/−40 °C, the array's *fastest*
corner) that the period-vs-capacitance tradeoff §7.1 describes resolves in
the opposite direction here. The row was already missed pre-layout, on the
digital section's account; the miss widens further (2.2× → ≈2.4×
pre-layout-to-leaf, then ≈2.4× essentially unchanged leaf-to-routed) but
the verdict does not flip.

**Idle** (`sim/tb/sampler-core-idle-leakage-extracted-routed/`, `ff`/+125 °C/3.63 V):

| Quantity | Pre-layout | Leaf-extracted (#17) | Routed-extracted (#217) |
|---|---|---|---|
| Record | [`sampler-core-idle-leakage` family](characterization-startup-and-power-budget.md) | [`2026-09-06-sampler-core-idle-leakage-extracted-01`](records/2026-09-06-sampler-core-idle-leakage-extracted-01.md) | [`2026-09-11-sampler-core-idle-leakage-extracted-routed-01`](records/2026-09-11-sampler-core-idle-leakage-extracted-routed-01.md) |
| Whole-block idle current (worst of the two clock-park states) | 32.77 nA | 93.37 nA | **136.8 nA** |

| Term | Pre-layout | Leaf-extracted | Routed-extracted |
|---|---|---|---|
| Analog (`sampler_core`, measured) | 32.77 nA (3.3 %) | 93.37 nA (9.3 %) | **136.8 nA (≈13.7 % of the row)** |
| Digital leakage (MEASURED-at-gate-level, unaffected) | 3.946 µA (394.6 %) | 3.946 µA (394.6 %) | 3.946 µA (394.6 %) |
| **Total** | **3.979 µA (398 %)** | **≈4.040 µA (≈404 %)** | **≈4.083 µA (≈408.3 % of the < 1 µA row)** |

Unlike the leaf-level composition, **this figure is the most complete of
this issue's evidence**: `sampler_core.routed.extracted.spice` routes the
entire block (both rings and the fully assembled `combiner_sampler`), so
this 136.8 nA is the first idle-current number in this repository's
evidence that includes the real Metal3/Via2 block-level wiring inside
`combiner_sampler` and the real fan-out load the four samplers place on the
ring-facing nodes (`layout/pex/build.py`'s own docstring, "Two composed
drop-ins"). The analog term's own share of the row keeps climbing
(3.3 % → 9.3 % → 13.7 %) but the digital section's gate-level leakage still
dominates by roughly 29:1 — the **overall verdict is unchanged** (missed by
essentially the same ~4.0× the row was already missed by pre-layout), and a
future integrator sizing headroom against a digital-side power-gating fix
([DR-0017]) should size against this 136.8 nA figure, the most complete one
available.

### 7.5 The sixth family, and a correction to this section's first draft

> **Corrected 2026-09-11, same day, before this document's own §7.5 residual
> was ever cited elsewhere.** This section first recorded
> `sampler-array-digitize-extracted` as the one family of six that *could
> not* be re-run at routing level, blocked on per-instance device
> addressability and filed upstream as
> [klayout-tools#1666](https://github.com/2AMLogic/klayout-tools/issues/1666).
> **That was wrong about what the testbench needs**, and the family has since
> been re-run. The original claim is kept below rather than deleted, because
> a superseded technical judgement is worth more in the open than in a
> squashed diff, and because the upstream issue it produced is still open and
> a reader may arrive here from it.

**What the first draft said.** `sim/tb/sampler-array-digitize-extracted/`
injects per-stage `trnoise` sources in series with each individual ring
stage's own output node, and its own header states the constraint: *"ngspice
cannot insert a series noise source inside a subcircuit."* The leaf-level
composition (#17) satisfies it because each stage is its own separately
instantiated leaf-cell subcircuit call. `klt extract` on the *assembled*
ring flattens all eleven stages' devices into one list with no per-instance
boundary — §7.0's positional resolution identifies which single **net** is
the ring's true external `ro` port, but says nothing about which **devices**
belonged to which stage, because `klt extract` never recorded that
association. That was filed generically, per this repository's friction
protocol, as klayout-tools#1666.

**Why that was the wrong requirement.** A series source does not need to
know which stage a device came from. It needs one **net** broken between its
driver side and its receiver side — and `klt extract --parasitics` already
discloses exactly that, in the netlist it writes:

- every net's lumped resistance arrives as a **star of per-terminal cards**,
  `R<name> <terminal> <hub> <ohms>`, one per device terminal on that net (the
  extractor's own documented model, restated in every generated file's
  banner), so each terminal is individually addressable whether or not its
  instance is;
- every device card names its own **gate** node, so each terminal on a net is
  classifiable as receiver-side (a gate) or driver-side (anything else) with
  no instance tag at all.

`layout/pex/build.py` therefore emits a `<ring>_ntap` variant alongside each
untapped routing-level ring: the eleven ring nets' gate-side star resistors
are re-pointed onto a second hub and both hubs are promoted to ports. **Tie a
pair together and the tapped ring is the untapped ring** — a 0 V source is a
short, so every star resistance, the net's grounded capacitance and therefore
every terminal-to-terminal path are untouched. That is not asserted here:
`layout/tests/test_pex_noise_tap.py` un-taps the committed netlist and
compares it **byte-for-byte** against the committed untapped one (and checks
that every tap really is split on both sides, and that the wrapper's
positional port order is the one its own banner publishes). No lumped
single-tap substitution was invented, and issue #12's per-stage
phase-noise-accumulation methodology is unchanged: eleven sources per ring,
the same injected PSD, the same node names, the same measurement expressions.

klayout-tools#1666 is **left open upstream** and has been
[commented on](https://github.com/2AMLogic/klayout-tools/issues/1666) rather
than closed: the generic gap it describes — nothing associates a `devices[]`
entry with the GDS instance it came from — is real and still matters for
genuinely instance-scoped work. What is withdrawn is the *motivating
example*, since "insert a series element between two repeated instances" turns
out to be achievable with the schema as shipped.

**Result** (`sim/tb/sampler-array-digitize-extracted-routed/`, same two
corners #12 and #17 used, 3 seeds each). Note `xor2` and both `sampler_dff`
instances stay **leaf-level** on purpose: this deck's pre-layout ancestor
wires them itself (no `ro_buf`, no ring-liveness samplers), so substituting
the routed `combiner_sampler` block would have changed the topology as well
as the parasitics and the delta would stop isolating the ring routing — the
only place this testbench's entropy comes from.

| Corner | Pre-layout | Leaf-extracted (#17) | Routed-extracted (#217) |
|---|---|---|---|
| `tt`/27 °C/3.30 V, record | [`2026-08-01-sampler-array-digitize-01`](records/2026-08-01-sampler-array-digitize-01.md) | [`2026-09-06-…-extracted-02`](records/2026-09-06-sampler-array-digitize-extracted-02.md) | [`2026-09-11-…-extracted-routed-01`](records/2026-09-11-sampler-array-digitize-extracted-routed-01.md) |
| …bits | `0101111100` | `0011111111` | **`0010110111`** |
| …flipped vs. the column to its left | — | 4 of 10 | **2 of 10** (positions 3, 6) |
| …`period_r1` | — | 9.387 ns | **12.852 ns (+36.9 %)** |
| …`ring1_swing_v` | — | 3.367 V | **3.083 V (−0.283 V)** |
| `ss`/−40 °C/3.63 V, record | [`2026-08-01-sampler-array-digitize-02`](records/2026-08-01-sampler-array-digitize-02.md) | [`2026-09-06-…-extracted-03`](records/2026-09-06-sampler-array-digitize-extracted-03.md) | [`2026-09-11-…-extracted-routed-02`](records/2026-09-11-sampler-array-digitize-extracted-routed-02.md) |
| …bits | `1111010011` | `1011110110` | **`0000111111`** |
| …flipped vs. the column to its left | — | 4 of 10 | **5 of 10** (positions 0, 2, 3, 6, 9) |
| …`period_r1` | — | 7.850 ns | **10.726 ns (+36.6 %)** |
| …`ring1_swing_v` | — | 3.728 V | **3.414 V (−0.314 V)** |

**§1.1's two findings both replicate, and the netlist-sensitivity one gets
stronger.** The bit pattern is still **seed-invariant within one netlist**
(identical across all 3 seeds at each corner). It is still **not
netlist-invariant** — 2 of 10 bits flip at `tt` and 5 of 10 at `ss` purely
from adding the rings' own routing parasitics, with no noise realization
changed; counted against the pre-layout schematic netlist rather than
against #17's leaf composition, 6 of 10 and 7 of 10 respectively now differ.
Every sampled level is still settled to within 6.9 mV of a rail
(`worst_rail_dev_v`), so no bit is ambiguous: which side of the sampler's
decision threshold a deterministic sample lands on is simply
parasitic-sensitive, exactly as issue #17's own framing predicted.

Applying [`sim/tools/raw_min_entropy_estimate.py`](tools/raw_min_entropy_estimate.py)'s
method by hand (that tool's own glob deliberately excludes these records —
§5's `-[0-9]` fix): both routed corners read `ones = 6`, `p1_hat = 0.600`,
`H_hat = 0.7370 bit`. **This is not reported as a design-stage min-entropy
estimate**, for §1.2's reasons, unchanged by routing: ten *successive*
samples of one evolving ring-phase process are not ten independent draws, and
§7.1's sizing law puts this deck's 10 ns sample interval four to five orders
of magnitude below the accumulated phase noise `H0 = 0.5` needs. That `H_hat`
reads *higher* than at leaf level is an artefact of ten samples landing 6/4
instead of 8/2, not evidence of more entropy.

One methodology note the new manifest carries: `ring_periods_per_sample` at
`tt` falls from 1.065 to **0.778**, i.e. at this deck's deliberately-too-fast
100 MHz demonstration clock the sampler now takes *less* than one ring period
per sample. That makes this deck an even weaker basis for an entropy claim
than it already was — which is why it still makes none.

The transient window lengthens (`tran 10p 132n` → `10p 200n`) for one reason:
the routed rings are ~37 % slower, so the 14th rising edge the period
measurement addresses no longer lands inside 132 ns and ngspice reports `out
of interval`. The same edges are addressed, the same 12 periods are averaged,
and every sampled bit (39–129 ns) and swing window (30–130 ns) sits where it
did. How much the lengthening itself perturbs the earlier part of a
transient-**noise** run was measured rather than assumed: the same seed at
`tstop` = 200 ns and 250 ns returns the same ten bit decisions and the same
`ones_count`, agrees to five significant figures on every period and swing,
and differs by at most 2.4e-4 V on a near-rail reading — smaller than the
seed-to-seed spread these records already report.

### 7.6 Spec table: routing-level does not flip any ratified verdict either

Extending §4's own table with the routing-level column:

| Row | Post-layout (leaf, #17) | Post-layout (routed, #217) | Changed further? |
|---|---|---|---|
| Entropy source, [DR-0007] §2 sizing law | Fails at [DR-0010]'s plain-cell constant (0.865×); holds at the starved-cell constant (5.69×) | **Fails further at the plain-cell constant (0.442×); still holds at the starved-cell constant, with less headroom (2.91×)** | Yes — degrades further, §7.1. Still no ratified row flips ([DR-0010]'s rate is `Proposed`). |
| Raw rate ([DR-0003], ratified) | Met by ~5 orders of magnitude | Met by ~4 orders of magnitude (§7.3) | No — still met by a wide margin. |
| Raw min-entropy per bit (placeholder) | Not measurable, unchanged reason | Still not measurable, same structural reason (§1.2); the routing-level *functional* digitization evidence now exists (§7.5) and the underlying bit pattern is parasitic-sensitive, but that does not move the ceiling | No (placeholder stands) |
| Time-to-first-valid (measured, met) | Met | Met — even the widened §7.3 startup term stays ~0.001 % of the 1.281 ms total | No |
| Power — active (measured, missed) | Missed ≈2.4× | **Missed ≈2.4× (essentially unchanged in ratio; analog term +4.4 % over leaf, §7.4)** | Miss ratio essentially flat; verdict unchanged |
| Power — idle (measured, missed) | Missed ≈4.0× | **Missed ≈4.0× (essentially unchanged in ratio; analog term +46.5 % over leaf, now the most complete figure available, §7.4)** | Verdict unchanged; analog contribution materially larger and more complete |
| Area, Operating envelope, Interface, Health tests, Conditioning, Delivered rate | Unaffected | Unaffected | No |

**No ratified README row's pass/fail verdict changes as a result of this
routing-level increment**, consistent with §4's own framing: this issue's
extraction can only add parasitic loading, never remove it, and every
number above moved in that expected direction except where a corner's own
frequency response reverses the power-vs-period tradeoff (§7.1, §7.4
active). The one number that was not previously a row —
[DR-0007] §2's own sizing margin at [DR-0010]'s proposed rate — is now
known to fail more than twice as hard at the constant DR-0010 itself
states (0.865× → 0.442×), which is new, material information for whoever
eventually rules on that proposal.

### 7.7 2026-09-12 scope decision: what a *full-chip* path would and would not show (issue #225, [DR-0025])

> **Superseded in the only sense that matters, later the same day, by §8
> (issue #232): the increment scoped here was then built, and every estimate
> below now has a measured counterpart.** Nothing here is retracted or
> rewritten — this subsection is what was *predicted from committed geometry
> before any extraction was read*, and §8 is what the extraction actually
> reported, so the two are deliberately left side by side. §8.2 compares them
> line by line, including where the prediction was wrong.

**Nothing in §§1–7.6 changes here. No record was produced, no extraction
output informed anything below, and no number below is a simulation
result.** This subsection exists because the standing "full-chip extraction"
follow-up below stopped being blocked and started being a *choice*, and
because a choice that big should be written down before anyone spends a
corner sweep on it. (A full-chip `klt extract --parasitics` run *was*
started while [DR-0025] was being written, purely as a runtime feasibility
probe; it did not complete within ~19.5 minutes and was terminated, and its
output was never read. That is disclosed in DR-0025's own Status and
Consequences, and is a cost input for whoever builds the increment — not a
source for anything here.)

**What unblocked.** Issue #222 (phase 2 of #219) drew real Metal4 trunks and
Metal3 risers across the four regions' isolation channels for every net
`design/floorplan_netlist.py` declares. Verified against the committed
artefacts rather than the merge description:
`layout/floorplan/reports/floorplan.drc.json` records `status: "clean"`, and
`layout/floorplan/reports/interregion.json`'s `check.lvs` records
`status: "match"` (`mismatch_count: 2`, both `topology.flattened`). The
sentence §0.1 and §7.0 both lean on — "the four floorplan regions are
electrically unjoined, so there is nothing to extract" — is **no longer
true**, and every place this document says it should be read as historical.

**What was decided**, in full in
[`spec/decision-records/DR-0025-full-chip-pex-scope.md`][DR-0025]: a
full-chip PEX increment is worth building, but **only** for the inter-region
nets that have a transistor-level device at *both* ends. Today that filter
admits exactly two of the fourteen drawn nets — `ro1` (`ring1.ro` →
`combiner_sampler.rn1`, a 128.40 µm Metal4 trunk) and `ro2` (`ring2.ro` →
`combiner_sampler.rn2`, 35.92 µm). A blanket transistor-level extraction of
the composed stream — the ~2500 `gf180mcu_fd_sc_mcu9t5v0__*` instances
included — is **rejected**, primarily because the digital section's timing
and power are already owned by a better evidence path
([DR-0021]/[DR-0022]/[DR-0023], post-route gate-level against the real
routed DEF) that an ngspice re-derivation would not improve on.

**Why those two nets and not the longer ones.** The trunk lengths are read
off `layout/floorplan/reports/interregion.json`; the R/C figures are
first-order arithmetic over that geometry and the `klt` gf180mcu deck's own
published Metal4 coefficients (0.09 Ω/sq, 0.007602 fF/µm², 0.028153 fF/µm at
`WIRE_W = 0.30 µm`) — **estimates, not extraction output, and not cited as
measurements anywhere**:

| Net | Trunk | Est. C | Both ends transistor-level? | In DR-0025's scope? |
|---|---:|---:|---|---|
| `raw_bit` | 524.77 µm | ≈30.8 fF | No — driver only (`sampler_dff` → abstracted `digital`) | Driver-side load only |
| `raw_valid` | 446.61 µm | ≈26.2 fF | No — driver only | Driver-side load only |
| `vss` | 430.23 µm | ≈25.2 fF | n/a (shared return) | No — IR drop is a separate analysis |
| `clk` | 353.78 µm | ≈20.7 fF | No — driven *from* abstracted `digital` | **No** |
| `ring_bit1` | 343.16 µm | ≈20.1 fF | No — driver only | Driver-side load only |
| `rst_n` | 339.34 µm | ≈19.9 fF | No — driven *from* abstracted `digital` | **No** |
| `ring_bit2` | 265.47 µm | ≈15.6 fF | No — driver only | Driver-side load only |
| **`ro1`** | **128.40 µm** | **≈7.5 fF** | **Yes** (`ro_stage` → `ro_buf`, both extracted) | **Yes** |
| **`ro2`** | **35.92 µm** | **≈2.1 fF** | **Yes** | **Yes** |
| `en1`/`en2`/`vddr1`/`vddr2`/`vdd` | 3.30 µm each | ≈0.2 fF | n/a (DC control / supply stubs) | No — negligible |

The two shortest signal trunks are the two that matter because of *where*
they land. `layout/pex/ro_ring11.routed.extracted.spice`, already committed,
gives each ring's eleven inter-stage nets **24.87 fF** in total, of which the
`ro` wrap net alone carries 8.16 fF (ring 1) / 7.89 fF (ring 2) — the
lightest, most delay-sensitive nodes in the design. `ro1`'s ≈7.5 fF would
land on top of exactly that node, roughly doubling it.

**Which measurement it would change.** §7.1's own already-measured
routed-vs-leaf pair is the sensitivity: ring 1 went 12.349 ns → 17.426 ns
when 24.87 fF of ring-internal signal-net capacitance appeared, i.e.
≈0.20 ns/fF at the entropy-binding corner. Linearizing that (a sizing
argument from two measured points, **not** a result):

- `ring1`: +≈7.5 fF ⇒ ≈ **+1.5 ns, ≈ +9 %** on `period_r1`.
- `ring2`: +≈2.1 fF ⇒ ≈ **+0.4 ns, ≈ +3 %** on `period_r2`.

That is the reason DR-0025 says "build it" rather than "defer": a ≈9 %
correction is far outside rounding, and §7.6's own last paragraph is
precisely about a number ([DR-0007] §2's sizing margin at [DR-0010]'s
proposed rate, 0.865× → 0.442×) that whoever rules on DR-0010 should not
have to rule on with a known, unpriced 9 %-scale correction outstanding.

**What such a path would still not show**, and what therefore may not be
claimed from it when it exists:

- Nothing about `digital`'s own devices — the standard cells stay
  abstracted, at cell-instance granularity, exactly as the composed LVS
  already treats them.
- No arrival-time or clock-tree claim across a region boundary. Every deck
  in `sim/tb/` drives `clk`/`rst_n` from an ideal zero-impedance ngspice
  source, so the trunk's ≈106 Ω in front of it is ≈2 ps of RC on edges
  measured in tens to hundreds of ps. The real `clk` question — can
  `digital`'s clock driver drive ≈21 fF? — is a post-route STA question
  ([DR-0022]'s path), and DR-0025's Follow-up sends it there.
- Only driver-side loading on `raw_bit`/`raw_valid`/`ring_bit1`/`ring_bit2`:
  real added output load on a real extracted `sampler_dff`, with **no
  receiver gate capacitance behind it**. `raw_bit`'s trunk is the largest
  single parasitic on the chip and would remain only partly priced.
- No IR-drop verdict on the shared `vss` trunk, and nothing about
  `digital`'s `vddd`/`vss` PDN tie (gf180-trng#224).

**Record level: unchanged.** Records from such a path stay `level: extracted`
([DR-0024]). No new `level:` value is added and DR-0024 is not amended —
DR-0024's own Consequences already legislate this case ("a record with
fuller routing coverage says so in its own Caveats rather than needing a new
`level:` value"), and its Decision already requires every `level: extracted`
record's Caveats to state whether inter-region routing parasitics are
included. A floorplan-level record satisfies that rule by answering "yes,
for `ro1` and `ro2`" instead of "no". DR-0025 adds two further Caveats
requirements of its own for such records: that the digital section is at
cell-instance granularity, and that `clk`/`rst_n` arrival is still from an
ideal source.

**"Floor, not ceiling" survives.** §0.1's framing is unaffected: inter-region
parasitics can only add R and C, so every degradation §§1–7.6 report remains
a lower bound on the full chip — and would remain one even after the
increment DR-0025 authorises lands, because the receiver-side capacitance on
the six `digital`-facing trunks stays unpriced.

---

## 8. 2026-09-12 delta: full-chip *inter-region* extraction, scoped to `ro1`/`ro2` (issue #232, [DR-0025])

### 8.0 What changed, what did not, and why every number below has a control

§7.7 wrote down, from committed geometry and the deck's own published
coefficients, what a full-chip extraction *would* show. This section is what
it **did** show. The increment [DR-0025] authorised is built:
`layout/pex/build.py` gained a third composition path, the delta report it
produces is committed at
[`layout/pex/reports/fullchip_parasitics.json`](../layout/pex/reports/fullchip_parasitics.json),
and the netlist it composes is
[`layout/pex/sampler_core.fullchip.extracted.spice`](../layout/pex/sampler_core.fullchip.extracted.spice).

**What the path does**, in one paragraph: `klt extract --parasitics` over
the composed, routed `layout/floorplan/trng_floorplan.gds` — the same
invocation `layout/floorplan/floorplan.py`'s own `run_extract_composed` is
held to (so the extraction the composed LVS is checked against and the
extraction the parasitics come from are one run shape, not two), plus
`--parasitics`, with `digital`'s ~2500 `gf180mcu_fd_sc_mcu9t5v0__*`
instances abstracted. From that run it takes **only** the inter-region
nets' R/C, and only as a **delta** over what the intra-region extractions
already carry, because the full-chip extraction merges the ring's own wrap
wire, the Metal4 trunk, the Metal3 risers and `combiner_sampler`'s own input
stub into one electrical net. Summing rather than subtracting would
double-count the first and last of those. The subtraction is held, not
asserted: `layout/pex/build.py`'s `_reconcile_delta` raises `FlowError`
rather than composing if a merged net comes back *smaller* than the sum of
its own already-extracted parts (physically impossible — more wire only adds
R and C — so it can only mean a net-identification bug), and
[`layout/tests/test_pex_fullchip.py`](../layout/tests/test_pex_fullchip.py)
holds both the arithmetic and the committed report/netlist pair to that rule.

**The measured delta.** Every figure below is read out of the committed
report, which records the merged total and each subtracted part alongside
the delta so the arithmetic can be re-checked by hand:

| Net | Full-chip merged | − ring's own | − `combiner_sampler`'s own | **= delta** |
|---|---|---|---|---|
| `ro1` | 251.50 Ω / 16.992 fF | 105.83 Ω / 7.890 fF | 88.12 Ω / 0.585 fF | **57.55 Ω / 8.517 fF** |
| `ro2` | 224.18 Ω / 11.663 fF | 105.83 Ω / 7.890 fF | 88.12 Ω / 0.585 fF | **30.22 Ω / 3.188 fF** |
| `raw_bit` | 557.89 Ω / 92.234 fF | — | 123.57 Ω / 4.231 fF | **88.003 fF** (C only) |
| `raw_valid` | 577.80 Ω / 96.634 fF | — | 123.57 Ω / 4.231 fF | **92.403 fF** (C only) |
| `ring_bit1` | 265.95 Ω / 32.181 fF | — | 123.57 Ω / 4.231 fF | **27.950 fF** (C only) |
| `ring_bit2` | 270.59 Ω / 33.172 fF | — | 123.57 Ω / 4.231 fF | **28.942 fF** (C only) |

`ro1`/`ro2` are composed as a symmetric lumped-pi segment (C/2 at each end,
R in series) between each ring wrapper's own `ro` port and
`combiner_sampler`'s `rn1`/`rn2`. That split is a **disclosed modelling
choice, not an extraction output**: `klt extract --parasitics` reports one
lumped total R and one lumped ground C per net, with no per-position
breakdown, so a delta computed from two scalars cannot reconstruct the
trunk's internal distribution, and the symmetric pi is the standard lumped
equivalent available from two scalars. The four `digital`-facing taps get
their capacitance only and **no series R** — DR-0025's own filter excludes
them from being simulated as two-ended nets, and a resistor ending in an
open node passes no current and would change nothing electrically.

**Two things the delta deliberately leaves out**, both in the direction of
*under*-reporting:

- **Net-to-net coupling.** `klt extract --parasitics` keeps a net's ground
  capacitance separate from the net-to-net capacitors it shares with the
  nets it crosses, and a coupling capacitor belongs to a *pair* of nets, so
  it has no intra-region counterpart to subtract. It is reported next to
  each delta instead of folded into it. For the two simulated nets it is
  negligible (`ro1`: 0.077 fF, `ro2`: 0.067 fF — under 1 % and 3 % of their
  own deltas respectively), so nothing below turns on it.
- **Receiver-side gate capacitance on the four `digital`-facing taps**,
  exactly as §7.7 said: real added output load on a real extracted
  `sampler_dff`, with nothing modelled behind it.

**Why every comparison below is against a *control*, not against §7's own
routing-level records.** The routing-level records for §7.1/§7.3/§7.4-active
are composed from `ro_array_core`'s topology (two routed rings, leaf-level
buffer/XOR, no samplers), while [DR-0025] requires this increment to be
composed from `sampler_core`'s (two routed rings plus the fully assembled
`combiner_sampler`, samplers and all). Subtracting those two would measure
the *composition* difference, not the inter-region delta: the whole-block
supply rail alone is about twice as large in the `sampler_core` composition
(the four `sampler_dff` instances' own static bias appears in it). So each
family here has a **zero-delta control** — the identical deck, identical
window, identical PVT point, against `layout/pex/sampler_core.routed.extracted.spice`,
i.e. the same composition with the inter-region delta absent. Every "delta"
column below is fullchip-minus-control, and each control record's own
Caveats say what it is.

That control is also a check on itself: at the entropy-binding corner it
reproduces the routing-level record's [DR-0007] §2 sizing margin to 0.6 %
(0.440× vs §7.1's 0.442×), confirming that swapping the composition does not
move the number this document actually turns on — only the rail scope.

### 8.1 Entropy-binding corner margin, full-chip (extends §7.1)

`sim/tb/ro-array-core-pvt-q-extracted-fullchip/` and its control, both at
`ss`/+125 °C/3.63 V:

| Quantity | Routed (#217, §7.1) | **Control** (same composition, no inter-region delta) | **Full-chip** (#232) | Delta, full-chip vs. control |
|---|---|---|---|---|
| Record | [`2026-09-11-…-extracted-routed-01`](records/2026-09-11-ro-array-core-pvt-q-extracted-routed-01.md) | [`2026-09-12-…-fullchip-control-01`](records/2026-09-12-ro-array-core-pvt-q-extracted-fullchip-control-01.md) | [`2026-09-12-…-fullchip-01`](records/2026-09-12-ro-array-core-pvt-q-extracted-fullchip-01.md) | |
| `period_r1` | 17.426 ns | 17.788 ns | 19.826 ns | **+2.038 ns, +11.5 %** |
| `period_r2` | 16.462 ns | 16.667 ns | 17.458 ns | **+0.791 ns, +4.7 %** |
| `p_rings_w` (two rings only) | 103.5 µW | 100.8 µW | 101.8 µW | +1.0 % |
| `xo_trans_per_s` | 236.3 M/s | 232.4 M/s | 215.4 M/s | −7.3 % |

Ring 1 is the one that matters, and it moves the way §7.7 predicted it
would: its `ro` wrap node is the lightest node in the design, and the `ro1`
trunk lands 8.5 fF and 57.5 Ω straight on top of it. Ring 2's much shorter
trunk moves it about a third as much.

**Consequence for [DR-0007] §2's sizing inequality**, recomputed exactly the
way §2.1 and §7.1 computed theirs (`sim/tools/array_sizing.py`'s
`ArrayPoint`, run directly against each record, at [DR-0010]'s proposed
500 bps):

| `a` (jitter-energy constant) | Leaf (#17) | Routed (#217) | **Control** | **Full-chip (#232)** |
|---|---|---|---|---|
| 1.79 ([DR-0010]'s stated plain-cell constant) | 0.865× — FAILS | 0.442× — FAILS | 0.440× | **0.374× — FAILS, another 14.8 % down** |
| 11.77 (issue #46's measured starved-cell constant) | 5.689× | 2.908× | 2.890× | **2.462× — still holds** |

The margin at [DR-0010]'s own stated constant, already failing at device
level and failing twice as hard at routing level, loses a further **14.8 %**
once the two inter-region entropy trunks are priced (0.440× → 0.374×
against the like-for-like control; 0.442× → 0.374× against §7.1's own
routing-level record). At the physically-measured starved-cell constant it
still clears 1× with 2.46× of margin, down 14.8 % from the control.

**No ratified README row's verdict changes** — same reasoning as §2.1 and
§7.1: [DR-0010]'s rate is `Proposed`, not ratified, and the *ratified* rate
misses this sizing target by orders of magnitude regardless of layout. What
is new is that whoever rules on [DR-0010] no longer has to rule on a number
with a known-but-unpriced correction outstanding: the correction is priced,
it is −15 %, and it is in the record.

### 8.2 Monte Carlo device mismatch: not re-run at full-chip level, and why

§7.2's family (`ro-array-core-mc-freq-extracted-routed`) is **not** re-run
here. [DR-0025] scopes this increment to §7.1/§7.3/§7.4 and does not ask for
it, and the reason it does not is worth restating rather than leaving as an
omission: §7.2's finding is about the *ratio* `f_r2/f_r1` and its
seed-to-seed spread, and the inter-region delta moves both rings' periods in
the same direction by a known amount (§8.1: +11.5 % and +4.7 %), which
shifts the mean ratio by ~6 % while leaving the mismatch-driven scatter —
a device-model property, §2.3 — untouched. §7.2's own margin against
injection locking is ~18–19 sd; a 6 % shift in a ratio that sits ~5–7 %
away from an integer is not capable of closing an 18-sd gap. That is a
stated argument from already-measured numbers, **not a measurement**, and it
is why the family is skipped rather than a claim that skipping it is free.

### 8.3 Startup, full-chip (extends §7.3)

`sim/tb/ro-array-core-startup-extracted-fullchip/` and its control, both at
`ss`/+125 °C/2.97 V:

| Quantity | Routed (#217, §7.3) | **Control** | **Full-chip** (#232) | Delta, full-chip vs. control |
|---|---|---|---|---|
| Record | [`2026-09-11-…-extracted-routed-01`](records/2026-09-11-ro-array-core-startup-extracted-routed-01.md) | [`2026-09-12-…-fullchip-control-01`](records/2026-09-12-ro-array-core-startup-extracted-fullchip-control-01.md) | [`2026-09-12-…-fullchip-01`](records/2026-09-12-ro-array-core-startup-extracted-fullchip-01.md) | |
| First rising edge after `en` (`t1r1`) | 27.571 ns | 27.716 ns | 31.442 ns | **+3.727 ns, +13.4 %** |
| Steady-state period, ring 1 (`t10−t9`) | 23.431 ns | 22.708 ns | 25.619 ns | **+2.911 ns, +12.8 %** |
| Steady-state period, ring 2 (`t10−t9`) | 21.651 ns | 21.269 ns | 22.484 ns | **+1.215 ns, +5.7 %** |
| 4th `xo` edge (`t4xo`) | 58.558 ns | 59.334 ns | 61.814 ns | +4.2 % |

The steady-state periods agree with §8.1's independent measurement of the
same quantity at a different supply, and the start-up transient degrades by
about the same fraction as the period does — the ring starts later because
each lap takes longer, not because the trunk changes the start-up mechanism.

**Consequence for the ratified raw-rate row**: still none, and not close.
Even stacking this on §7.3's own +46 %, the rate-binding corner's ~26 ns
period stays roughly four orders of magnitude inside [DR-0003]'s > 1 Mbps
(< 1 µs raw sample period) budget.

### 8.4 Power, full-chip (extends §7.4)

**Active** (`sim/tb/ro-array-core-power-extracted-fullchip/`, `ff`/−40 °C/3.63 V):

| Quantity | **Control** | **Full-chip** (#232) | Delta |
|---|---|---|---|
| Record | [`2026-09-12-…-fullchip-control-01`](records/2026-09-12-ro-array-core-power-extracted-fullchip-control-01.md) | [`2026-09-12-…-fullchip-01`](records/2026-09-12-ro-array-core-power-extracted-fullchip-01.md) | |
| `p_rings_w` (the two rings' own term) | 263.5 µW | 267.4 µW | **+1.45 %** |
| `p_total_w` (this composition's whole-block rail) | 957.8 µW | 965.5 µW | **+0.80 %** |
| `period_r1` | 7.175 ns | 7.958 ns | +10.9 % |

**§7.4's active-power rollup is deliberately not restated here.** This DUT's
`p_total_w` is a `sampler_core`-scope rail (both rings, the buffers, the XOR
*and* all four samplers), roughly twice §7.4's `ro_array_core`-scope
489.9 µW, so dropping it into that table's "entropy array (measured)" row
would silently change what the row means. What this increment contributes to
that row is a **+1.45 % correction on the rings' own term**, which does not
move §7.4's ≈2.4× miss in any visible digit. The verdict is unchanged and
the row was already missed on the digital section's account.

**Idle** (`sim/tb/sampler-core-idle-leakage-extracted-fullchip/`, `ff`/+125 °C/3.63 V):

| Quantity | Routed (#217, §7.4) | **Control** | **Full-chip** (#232) | Delta, full-chip vs. control |
|---|---|---|---|---|
| Record | [`2026-09-11-…-extracted-routed-01`](records/2026-09-11-sampler-core-idle-leakage-extracted-routed-01.md) | [`2026-09-12-…-fullchip-control-01`](records/2026-09-12-sampler-core-idle-leakage-extracted-fullchip-control-01.md) | [`2026-09-12-…-fullchip-01`](records/2026-09-12-sampler-core-idle-leakage-extracted-fullchip-01.md) | |
| Integration window | 1 µs tstop / 200 ns | **9.5 µs / 1 µs** | **9.5 µs / 1 µs** | |
| Whole-block idle current (worst clock-park state) | 136.80 nA | 121.90 nA | 127.04 nA | **+5.13 nA, +4.2 %** |
| Self-check (previous-window) disagreement | 0.9 % | 0.5 % | 1.2 % | |

**A widened measurement window was needed, and finding that out is itself a
result.** The ~237 fF of added driver-side output load on
`raw_bit`/`raw_valid`/`ring_bit1`/`ring_bit2` settles slowly at
leakage-level currents. Two first attempts were discarded before any record
was minted — the same convention §7.2 and §7.3 used for their own failed
first windows, and both are reported rather than hidden:

| Window | `i_idle_clklo_a` | Its own self-check pair | Disagreement |
|---|---|---|---|
| 1 µs / 200 ns (the routing-level family's own) | 190.99 nA | 205.61 nA | 7.7 % — **not settled** |
| 5 µs / 1 µs | 138.07 nA | 143.52 nA | 3.9 % — still drifting |
| **9.5 µs / 1 µs** (this deck) | **127.04 nA** | 128.51 nA | **1.2 % — settled** |

9.5 µs is as far as this can be pushed without changing the shared
idle-state protocol itself (`rst_n`'s own pulse falls at 10.1 µs), which is
stated because it is a real ceiling.

**One consequence has to be said plainly, because it cuts against a number
this document already published.** The control — the *identical* netlist the
#217 record measured, same blob SHA — reads **121.90 nA** over the widened
window against that record's **136.80 nA** over the 1 µs one. The difference
is a measurement-window difference on the same DUT, not a design change and
not a correction to the #217 record, which stands unedited as the
append-only rule requires. But it means §7.4's closing advice ("a future
integrator sizing headroom … should size against this 136.8 nA figure, the
most complete one available") should now read **127.04 nA** — the most
complete *and* the most settled figure, and still the conservative one of
the two settled readings. The rollup verdict does not move: at 127.04 nA the
analog term is ≈12.8 % of the < 1 µA row against `digital`'s unchanged
3.946 µA of gate-level leakage, and the row stays missed by ≈4.07×, the same
≈4× it was already missed by pre-layout.

### 8.5 [DR-0025]'s own first-order estimate, against what was measured

[DR-0025]'s "Revisit if" clause asks for exactly this comparison, and says a
materially different result means the sizing argument that justified the
scope was wrong and the scope should be re-derived from measured values.
Taking it seriously, in both directions:

| Quantity | §7.7 / DR-0025 estimate | Measured | Ratio |
|---|---|---|---|
| `ro1` delta C | ≈7.5 fF | 8.517 fF | 1.14× |
| `ro1` delta R | ≈39 Ω | 57.55 Ω | 1.48× |
| `ro2` delta C | ≈2.1 fF | 3.188 fF | 1.52× |
| `ro2` delta R | ≈11 Ω | 30.22 Ω | 2.75× |
| `period_r1` shift | ≈+1.5 ns, **≈+9 %** | +2.038 ns, **+11.5 %** | 1.27× |
| `period_r2` shift | ≈+0.4 ns, ≈+3 % | +0.791 ns, +4.7 % | 1.98× |

**Verdict on `ro1`, the load-bearing one: the estimate holds.** +11.5 %
measured against ≈+9 % predicted is a 27 % relative error on a first-order,
trunk-only, lumped, deck-coefficient calculation that was explicitly
labelled an estimate — it is not the kind of discrepancy DR-0025's "Revisit
if" is about, and the scoping argument it justified (that a ~9 %-scale
correction on `period_r1` was too big to leave unpriced) is if anything
strengthened: the correction is bigger than predicted, not smaller. **No
re-derivation of the scope is called for, and none is made here.**

Three reasons the measurement lands above the estimate, all of them
reasons the estimate itself disclosed:

1. **Trunk-only geometry.** DR-0025's arithmetic priced the Metal4 trunk and
   said so ("risers, vias and vertical-overlap coupling … are not in it").
   The measured delta includes the Metal3 risers and vias, which is most of
   the +14 % on `ro1`'s capacitance and nearly all of the +48 % on its
   resistance.
2. **The linearisation ignored series R entirely.** §7.7's ≈0.20 ns/fF
   sensitivity was derived from a pure-capacitance step (ring-internal
   wiring). The `ro1` trunk also puts 57.5 Ω in series between the ring's
   last stage and the buffer's gate; 0.20 ns/fF × 8.517 fF is +1.70 ns,
   and the measured +2.04 ns leaves ≈0.34 ns that the capacitance term does
   not account for.
3. **`ro2`'s relative error is large and its absolute error is not.** 1.52×
   on a 2.1 fF estimate is 1.1 fF. Short trunks are exactly where a
   trunk-only estimate should be worst, because the fixed riser/via cost is
   a larger share of the total.

**The four `digital`-facing taps look far worse than the estimate, and the
comparison is not like-for-like — both halves of that are worth stating.**

| Net | DR-0025's trunk-only estimate | Measured full-chip delta C | Ratio |
|---|---|---|---|
| `raw_bit` | ≈30.8 fF | 88.00 fF | 2.86× |
| `raw_valid` | ≈26.2 fF | 92.40 fF | 3.53× |
| `ring_bit1` | ≈20.1 fF | 27.95 fF | 1.39× |
| `ring_bit2` | ≈15.6 fF | 28.94 fF | 1.86× |

**These two columns do not measure the same thing, and the difference is
structural.** `--abstract-cells` abstracts the standard *cells*, not the
routing between them, so a `digital`-facing net's own routed metal **inside**
the `digital` region is real drawn geometry and is in the full-chip
extraction. The measured column is therefore "cs stub + riser + trunk +
digital-side routing, less the cs stub", while the estimate column is "trunk
only". Splitting the measured total back into those pieces is exactly the
attribution the extractor cannot do
([klayout-tools#1699](https://github.com/2AMLogic/klayout-tools/issues/1699)
§2), so **this section does not claim that DR-0025's ≈30.8 fF is 2.86× too
low** — only that the trunk is not the whole story on those nets, and that
the real added load sits somewhere between the two columns.

What *is* directly comparable is `ro1`/`ro2`, where both endpoints are
inside blocks this repository extracts separately and the subtraction
therefore closes cleanly. There, a trunk-only Metal4 arithmetic undercounts
the real added capacitance by ~14 % and the real added resistance by ~48 %
(the risers and vias). **That is the transferable finding**, and it is the
one that matters to [#233](https://github.com/2AMLogic/gf180-trng/issues/233)
(merged 2026-09-12), which loads these six trunks into the post-route STA
from the same trunk-only, Metal4-only arithmetic read live out of
`layout/floorplan/reports/interregion.json`. Its *scope* is right — the
post-route STA already models the digital-side routing, so a trunk-only
interface load is what it should add, not the merged total above — but on
the `ro1`/`ro2` evidence its numbers are a **floor**: the real riser-plus-via
contribution is not in them. Flagged on #233 rather than left to be
rediscovered; #233 has since merged and closed, so the live tracker for this
disclosure is [#242](https://github.com/2AMLogic/gf180-trng/issues/242) (see
the Follow-up section below).

### 8.6 Spec table: full-chip does not flip any ratified verdict either

Extending §7.6's table with the full-chip column:

| Row | Post-layout (routed, #217) | **Post-layout (full-chip, #232)** | Changed further? |
|---|---|---|---|
| Entropy source, [DR-0007] §2 sizing law | Fails at the plain-cell constant (0.442×); holds at the starved-cell constant (2.91×) | **Fails further at the plain-cell constant (0.374×); still holds at the starved-cell constant (2.46×)** | Yes — degrades a further 14.8 %, §8.1. Still no ratified row flips ([DR-0010]'s rate is `Proposed`). |
| Raw rate ([DR-0003], ratified) | Met by ~4 orders of magnitude | Met by ~4 orders of magnitude (§8.3) | No |
| Raw min-entropy per bit (placeholder) | Not measurable, same structural reason | Unchanged — this increment adds no entropy measurement | No |
| Time-to-first-valid (measured, met) | Met | Met — the start-up term grows 13 % and stays ~0.001 % of the 1.281 ms total | No |
| Power — active (measured, missed) | Missed ≈2.4× | Missed ≈2.4× (rings' own term +1.45 %, §8.4) | No |
| Power — idle (measured, missed) | Missed ≈4.0× | **Missed ≈4.07×**, on a more complete *and* better-settled 127.04 nA analog term (§8.4) | Verdict unchanged |
| Area, Operating envelope, Interface, Health tests, Conditioning, Delivered rate | Unaffected | Unaffected | No |

**No ratified README row's pass/fail verdict changes as a result of this
full-chip increment either.** The one number that is not a row — [DR-0007]
§2's sizing margin at [DR-0010]'s proposed rate — has now moved
1.356× (pre-layout) → 0.865× (device-level) → 0.442× (routing-level) →
**0.374×** (with the two inter-region entropy trunks priced).

### 8.7 What this still does not price, and what it cost

**Still unpriced, and therefore still a floor.** §0.1's "floor, not ceiling"
framing survives this increment exactly as §7.7 said it would:

- Twelve of the fourteen drawn inter-region nets are not simulated at all.
  `clk` and `rst_n` are driven from an ideal zero-impedance source in every
  deck in `sim/tb/`, so their trunks' R in front of it is a no-op
  ([DR-0025] Alternative B); `vss`'s IR drop is
  [#234](https://github.com/2AMLogic/gf180-trng/issues/234)'s question, now
  answered in [`characterization-vss-trunk-ir-drop.md`](characterization-vss-trunk-ir-drop.md);
  the supply and control stubs are ≈0.2 fF each.
- The four `digital`-facing taps carry **driver-side load only** — no
  receiver gate capacitance — and §8.5 shows the capacitance actually
  hanging off those nets is 1.4×–3.5× the trunk-only estimate (because the
  net's own routed metal inside `digital` is in the extraction too), which
  makes that hole bigger than it looked, not smaller.
- Nothing here is evidence about any `gf180mcu_fd_sc_mcu9t5v0__*` cell's own
  devices. The digital section stays at cell-instance granularity, and every
  record minted in this section carries that caveat in its own Caveats
  block, per [DR-0025].
- Net-to-net coupling capacitance is reported but not composed (§8.0).

**Record level: unchanged.** Every record in this section is `level:
extracted` per [DR-0024], which already legislated this case — "a record
with fuller routing coverage says so in its own Caveats rather than needing
a new `level:` value". No new `level:` value is added and [DR-0024] is not
amended, exactly as [DR-0025] Alternative D decided.

**Runtime, measured properly this time.** [DR-0025] could only record that
its own feasibility probe "had not completed after ~19.5 minutes" on a
partly-contended host. Two instrumented runs of the identical invocation on
the same host say:

| Run | Wall clock | CPU time (user) | Peak RSS | Host 1-min load average (28 cores) |
|---|---|---|---|---|
| Out-of-band, `/usr/bin/time -l` | 2283.9 s (**38.1 min**) | 1052.3 s (**17.5 min**) | 286 MB | ~25–29 |
| In-tool, `build.py --fullchip-extract` (the committed report) | 2194.8 s (**36.6 min**) | — | — | 25.7 (recorded in the report) |

Both runs are on the same host, the same `klt 0.4.0+gc903103cba9e`, the same
stream, with the identical invocation the committed report echoes — and they
produced **bit-identical parasitics** (the composed netlist rebuilt from
either is byte-identical, which is what `build.py --check` compares). Two
independent 36–38-minute extractions agreeing to the last decimal place is
worth recording on its own: this step is expensive, but it is reproducible.

The load figure is recorded beside the wall clock deliberately: DR-0025's
probe had to be discounted precisely because it was contended and nobody
wrote down by how much. The **CPU-time** figure (~17.5 min) is the
contention-independent one, and it is the number to budget against; the
wall-clock figure is roughly double it on a host running at ~28/28 cores'
worth of other work. Either way the conclusion DR-0025 drew stands: this is
a tens-of-minutes step and it must not sit on an interactive check's path.
It does not — `layout/pex/build.py --check` never re-runs it, and composes
from the committed report instead, reconciling that report against a fresh
(cheap) intra-region extraction on every run so a stale report fails loudly
rather than silently.

**Friction filed upstream**, per this repository's protocol: the measured
cost above was added to
[klayout-tools#1699](https://github.com/2AMLogic/klayout-tools/issues/1699)
("`klt extract --parasitics` is whole-layout and total-only, so pricing a
few top-level nets costs a full pass and needs hand-subtraction to avoid
double-counting"), which [DR-0025] filed generically from the same gap. Both
halves of that gap are what made this increment expensive: a full pass to
price six nets, and a hand-written subtraction (`_reconcile_delta`) to avoid
double-counting them.

---

## Follow-up

- ~~**Full-chip (inter-cell + inter-region routed) extraction**, once
  [klayout-tools#1540](https://github.com/2AMLogic/klayout-tools/issues/1540)
  is resolved — the natural next increment of this issue's own scope, and the
  only way to know whether §2.1's already-failing DR-0010-constant margin
  degrades further once real routing parasitics are included (expected
  direction: further degradation, per §0.1).~~ **Struck 2026-09-11 (issue
  #217): klayout-tools#1540 closed and the *intra-region* half of this item
  is done** — §7 re-runs the entropy-binding, MC-mismatch, startup and power
  methodologies against the assembled, routed rings and combiner/sampler
  block, confirming §2.1's margin degrades further as expected (0.865× →
  0.442× at [DR-0010]'s own constant, §7.1). **What remains of this item**:
  *inter-region* routing (the four floorplan regions are still electrically
  unjoined, §0.1/§7.0 — full-chip extraction needs a floorplan-level routing
  step first, out of #217's own scope per its own Out-of-scope section,
  tracked as [#219](https://github.com/2AMLogic/gf180-trng/issues/219)). The
  sixth family's own routing-level sibling, first recorded here as an
  unresolvable residual, **has since been built** — see §7.5's correction.
- **Re-sweep the full PVT grid** against the extracted netlist, not just the
  previously-identified binding corners, to confirm those corners still bind
  post-layout (this document's own caveat above) — still open, now for
  *both* the leaf-level and routed-level netlists.
- **DR-0010's ratification decision** should read §7.1 (not just §2.1)
  before proceeding: the proposed rate's margin at its own stated
  jitter-energy constant is now known to fail more than twice as hard
  (0.865× → 0.442×) once real ring routing parasitics, not just device-level
  ones, are included.
- ~~**`sampler-array-digitize-extracted-routed`** (§7.5): build a
  routing-level sibling of this family once either klayout-tools#1666 gives a
  way to address a specific repeated-instance boundary inside an
  assembled-block extraction, or an in-repo alternative per-stage noise
  injection method is found.~~ **DONE 2026-09-11**, by the second route: the
  per-stage sources needed a *net* split, not per-instance device
  addressability, and `klt extract --parasitics`' own per-terminal resistance
  star plus its device cards' gate nodes already disclose enough to do it.
  Issue #12's methodology is unchanged. See §7.5.
- ~~**Inter-region floorplan routing**, tracked as
  [#219](https://github.com/2AMLogic/gf180-trng/issues/219) per #217's own
  Out-of-scope section — now the only remaining gap between this document's
  routing-level evidence and a genuine full-chip post-layout re-run. Note it
  is a *layout* task, not an extraction one: the four guarded regions are
  placed with a 20 um isolation channel and no signal routing between them,
  so there is nothing to extract until they are joined.~~ **The layout half
  is DONE** (issue #222, phase 2 of #219): the inter-region nets
  `design/floorplan_netlist.py` declares are drawn, and the composed,
  routed floorplan is DRC-clean and LVS-matches that declaration — see
  `layout/floorplan/README.md`, "Inter-region routing". So there *is* now a
  joined full-chip composition to extract. The remaining gap is the
  extraction half: no full-chip PEX path exists over it, which is its own
  follow-up (see `layout/pex/build.py`'s own "Full-chip (inter-region) delta
  composition" section for what such a path would have to price). Nothing in
  this document's own routing-level records changes as a result — they are
  all intra-region.
  **Scoped 2026-09-12 (issue #225, [DR-0025], §7.7)**: the extraction half
  is now a decided, narrow piece of work rather than an open question —
  price the two inter-region nets with a transistor-level device at both
  ends (`ro1`, `ro2`), keep `digital` abstracted, and re-run §7.1/§7.3/§7.4
  at their existing binding corners. ~~**Still open**: building it, filed as
  [#232](https://github.com/2AMLogic/gf180-trng/issues/232). No record in
  this repository may be cited as full-chip post-layout evidence until it
  exists.~~ **Struck 2026-09-12 (issue #232): built.** The extraction half
  exists now too — `layout/pex/build.py`'s third path, its committed
  `layout/pex/reports/fullchip_parasitics.json` delta report and the composed
  `layout/pex/sampler_core.fullchip.extracted.spice` — and §8 records what it
  measured. The "may not be cited as full-chip post-layout evidence" bar is
  cleared **only for the two nets [DR-0025] scopes** (`ro1`, `ro2`) plus the
  four disclosed driver-side-only output loads; every other inter-region net
  is still unpriced, and §8 states that up front rather than in a footnote.
- ~~**Feed the six `digital`-facing trunks' capacitance into the post-route
  STA** as an interface load, under [DR-0022]'s path — new, from §7.7, filed
  as [#233](https://github.com/2AMLogic/gf180-trng/issues/233). This is where
  the `clk` drive-strength question belongs (can `digital`'s clock driver
  drive the trunk's ≈21 fF?); [DR-0025] Alternative B declines to answer it
  with an ngspice run over an ideal source, and routes it here instead.~~
  **DONE (issue #233, merged 2026-09-12)**: `sim/tb/digital-sta-power/
  run_sta.py` states each trunk's lumped Metal4 RC as a `set_input_transition`
  on the corresponding port, every run (`sim/characterization-digital-sta-
  area-power.md` §2a). Per §8.5 above, that trunk-only Metal4 arithmetic is a
  **floor**, not the measured load — #233 is closed, so this caveat's live
  tracker is
  [#242](https://github.com/2AMLogic/gf180-trng/issues/242), which disclosed
  the floor at every site the number is computed or reported rather than
  leaving it findable only in this section.
- **IR drop on the shared 430.23 µm `vss` trunk** — new, from §7.7, filed as
  [#234](https://github.com/2AMLogic/gf180-trng/issues/234). A static supply
  analysis with its own methodology, needing a current profile the
  extracted-netlist path does not produce. Not owed by [DR-0025]'s
  increment.

[DR-0009]: ../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0015]: ../spec/decision-records/DR-0015-entropy-binding-corner-moves-to-the-hot-slow-corner.md
[DR-0017]: ../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
[DR-0021]: ../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
[DR-0022]: ../spec/decision-records/DR-0022-post-route-gate-level-simulation-records.md
[DR-0023]: ../spec/decision-records/DR-0023-power-rollup-digital-term-becomes-measured-gate-level-power.md
[DR-0024]: ../spec/decision-records/DR-0024-extracted-netlist-record-level.md
[DR-0025]: ../spec/decision-records/DR-0025-full-chip-pex-scope.md
