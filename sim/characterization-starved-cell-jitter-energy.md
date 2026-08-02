# Jitter-energy law on the shipped starved delay cell

Status: measurement complete for issue [#46]. Validates — on the cell this
project actually ships — the empirical invariant that
[`DR-0010`](../spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md)
calls `(★)` and names as its own largest open risk.

**This document is an ordinary summary, not evidence.** Every number below
cites the `sim/records/` stem that produced it — treat this document as a
reading guide over that evidence, not a substitute for it. Correcting a number
means re-running the testbench and citing the new record, per
[`sim/README.md`](README.md).

**No entropy-rate or spec-compliance claim is made anywhere in this document.**
Everything here is a simulated circuit figure — period, accumulated jitter,
supply power — and an arithmetic combination of them. DR-0004's tiering is
unchanged; measuring `H` is [#12]'s job.

## The question

DR-0010 derives its proposed raw-rate row from

```
a  ≡  κ² · P_ring / (k_B · T)   =   1.79 ± 0.14        (min 1.64, max 2.12)
```

`κ²` is the random-walk rate constant of a ring's phase
(`σ²_acc(t) = κ² · t`), so `a` says the entropy a ring delivers is fixed by the
power it burns and is not a free design variable. `python3
sim/tools/jitter_energy_law.py` derives that constant from committed records,
over the 27-point candidate-A grid — but every one of those records is a
**plain, unstarved** 5-stage inverter ring. The cell this project ships is a
minimum-width, series-**starved** inverter. DR-0010 §Consequences states the
gap plainly:

> `(★)` is a model, fitted to one cell family on one PVT grid, and the array's
> own transient-noise run does not yet confirm it.

This document closes that gap by measuring `a` for the starved cell.

## Why the existing shipped-cell run could not answer it

The one transient-noise run of the shipped-cell family before this work,
[`2026-08-01-ro-array-sanity-jitter-01`](records/2026-08-01-ro-array-sanity-jitter-01.md),
returns a `κ²` **1.3 × 10⁴ above** what `(★)` predicts. Taken at face value
that would move DR-0010's rate row up by four orders of magnitude. It cannot be
taken at face value, and the record itself contains the two reasons:

1. **Its σ barely moves between independent noise seeds.** `sigma_r1_1` varies
   0.3 % across seeds 1/2/3. A σ estimated from a finite window is itself a
   random variable; a genuine 16-period estimate of it scatters ~15 % seed to
   seed (calibration below). A 0.3 % spread is not a precise measurement, it is
   every seed tracing the *same deterministic curve*.
2. **It accumulates as `lag^0.81`, not `lag^0.5`.** From that record's own
   `sigma_r1_{1,2,4,8}`. A phase random walk driven by white noise gives
   exactly `lag^0.5`; a deterministic frequency drift gives `lag^1.0`. 0.81 is
   most of the way to drift.

Both say the same thing about what that record contains: something
deterministic, not jitter. The *diagnosis* on record — DR-0010's, and issue
#46's — was that the cause is the window: 16 periods, opened at the second edge
after start-up. That diagnosis turns out to be wrong, and this document says so
in [§4](#4-what-this-does-and-does-not-settle-about-the-array-sanity-run). The
conclusion it supported — that the record's `σ` is not usable — stands.

## Method

- **Harness**: `sim/run_corners.py`, ngspice-46, PDK
  `gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b`. One record per PVT
  point, eight independent noise seeds per record, per
  [`sim/README.md`](README.md).
- **Testbench**: [`sim/tb/ro-ring5-starved-jitter-long/`](tb/ro-ring5-starved-jitter-long/).
  One 5-stage ring of the shipped `ro_stage` / `ro_nand2` cells
  (`wstv` = 0.220 µm, `lstv` = 2 µm, `cld` = 0.5 fF), device for device the
  same as ring 1 of `sim/tb/ro-array-sanity-jitter/`, with one `trnoise()`
  source in series with every stage input at the same fixed injected density.
  Three things are different from that testbench, and only three:
  - the measurement window opens **256 periods** after start-up rather than at
    the second edge;
  - it spans **512 periods** rather than 16, so the accumulation exponent is
    fitted over lags 1…128, i.e. **2.11 decades**;
  - the other three rings and the XOR tree are absent. The three other rings
    share no node with ring 1, so dropping them changes nothing electrically.
    The XOR tree does: in the array, `ro1` drives four transistor gates of
    `xa1`. Removing it leaves `ro1` unloaded — which is exactly the topology
    of the plain-cell reference family `sim/tb/ro-inv-05stage-jitter/`, whose
    ring output is likewise probe-only. Since the point of this measurement is
    to compare a starved cell against a plain one, the delay cell has to be the
    only variable and the output loading must not be. The consequence is
    visible in the period and is quantified in the Results below.
- **Fixed injection, per-corner scaling.** As everywhere else in this
  repository (see
  [`characterization-ro-delay-cell-jitter.md`](characterization-ro-delay-cell-jitter.md)),
  the injected per-stage noise density is held at 1 × 10⁻⁸ V/√Hz across the
  whole grid, so what varies corner to corner is the circuit's noise-to-jitter
  conversion rather than the stimulus. Recovering a physical σ means scaling by
  the cell's own `.noise` density at that corner. For the starved cell that is
  `inoise_dens_1g` from `sim/tb/rostage-noise/`; for the plain cell it is
  `inoise_dens_1g` from `sim/tb/inv-stage-noise/`. **Those two testbenches
  define the quantity identically** — same `.noise v(out) vn dec 10 1e3 1e11 1`
  sweep, same 1 GHz spectrum index — so the ratio of the two cells' `a` does not
  depend on the definition, only on the devices.
- **Power from the same run.** A charge integrator (`fq1`/`cq1`/`rq1`) runs
  alongside and is read across *the jitter window*, not the whole run, so the
  `P_ring` in `a = κ² P / (k_B T)` and the `κ²` come from the same seeded
  simulation over the same interval. Relating them across two runs would import
  a cross-run assumption that `(★)` does not need.
- **PVT**: the entropy-binding corner `ss` / −40 °C / 3.63 V, nominal
  `tt` / 27 °C / 3.30 V, and the power-binding corner `ff` / −40 °C / 3.63 V,
  per [`DR-0006`](../spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md)
  and DR-0010 §3's binding corners.

### The two diagnostics, and how their expectations are calibrated

Both failure signatures of the array-sanity run are computed for every record by
`python3 sim/tools/starved_cell_jitter_energy.py`, so the same mistake cannot
pass silently a second time.

**Seed spread.** The scatter of a σ estimate scales as `√(L / N)` for lag `L`
over an `N`-period window. Its *absolute* scale is not taken from a formula
here: the textbook standard error `√(L / 2N)` treats the `N/L` increments as
disjoint, whereas these estimators use all `N − L` **overlapping** ones, so it
is an upper bound. The reference is instead measured, from the committed
plain-cell family (`2026-07-31-ro-inv-05stage-jitter-{01..27}`, 128-period
window, 4 seeds each — lag-1 spread **5.4 %** against the 6.3 % the formula
predicts) and rescaled by `√(N_ref / N)`. Calibrating on the plain cell rather
than the starved one is deliberate: the reference must not come from the
records the check is judging.

**Accumulation exponent.** A log–log fit of `σ_acc` against lag over all
measured lags, and again over the top decade alone. Random walk ⇒ 0.5;
deterministic drift ⇒ 1.0.

`--check` gates on the seed spread only. The exponent is deliberately *not*
gated: a starved ring whose accumulation genuinely departs from `√t` is a
finding this repository wants recorded, not a build failure.

**Per-block periods.** Every record also carries sixteen block-mean periods
across the whole run, so the settling transient the window skips is visible in
the record rather than asserted. The tool reports their peak-to-peak spread
separately over the blocks entirely *before* the window (is the discard long
enough?) and entirely *inside* it (is there residual drift left to inflate the
long-lag σ?).

## Results

Three records, one per corner, eight seeds each,
`tstop` = 2.4 µs, ~111 min of ngspice per seeded run:

| Corner | Record |
|---|---|
| `ss` / −40 °C / 3.63 V (entropy-binding) | [`2026-08-01-ro-ring5-starved-jitter-long-01`](records/2026-08-01-ro-ring5-starved-jitter-long-01.md) |
| `tt` / 27 °C / 3.30 V (nominal) | [`…-02`](records/2026-08-01-ro-ring5-starved-jitter-long-02.md) |
| `ff` / −40 °C / 3.63 V (power-binding) | [`…-03`](records/2026-08-01-ro-ring5-starved-jitter-long-03.md) |

Reproduce the whole derivation below with:

```sh
python3 sim/tools/starved_cell_jitter_energy.py
python3 sim/tools/starved_cell_jitter_energy.py --check
```

### 1. The window is measuring jitter, not settling

The axes on which the array-sanity run fails, on the same three corners:

| Corner | Block-period drift, before the window | …inside the window | `σ₁` seed spread | reference | 16-period start-up window, `σ₁` seed spread | reference |
|---|---|---|---|---|---|---|
| `ss`/−40/3.63 | 14 ppm | 18 ppm | **4.1 %** | 2.7 % | **17.7 %** | 15.2 % |
| `tt`/27/3.30 | 11 ppm | 34 ppm | **3.9 %** | 2.7 % | **16.0 %** | 15.2 % |
| `ff`/−40/3.63 | 29 ppm | 29 ppm | **5.9 %** | 2.7 % | **24.2 %** | 15.2 % |
| *for contrast:* `2026-08-01-ro-array-sanity-jitter-01` | not reported | not reported | — | — | **0.3 %** | 15.2 % |

and the seed spread scales with lag the way a genuine estimate must — the
√L law, over more than two decades of lag, is reproduced without being
assumed:

| Lag `L` | 1 | 8 | 128 |
|---|---|---|---|
| Reference (plain family, rescaled) | 2.7 % | 7.0 % | 31.2 % [^ext] |
| `ss`/−40/3.63 measured | 4.1 % | 6.8 % | 29.9 % |
| `tt`/27/3.30 measured | 3.9 % | 6.3 % | 28.4 % |
| `ff`/−40/3.63 measured | 5.9 % | 8.7 % | 34.6 % |

[^ext]: The plain family only measures lags up to 32, so its `L` = 128
    reference is its own `L` = 32 figure extrapolated by `√(128/32)`.

The period itself is flat: the block-mean period varies by **11–34 ppm**
peak-to-peak across the whole 768-period run, and the 16-period figure taken
right after start-up (`period_startup16`) agrees with the 512-period window
mean to **11–22 ppm** at every corner. There is no measurable start-up
transient in this deck at all.

### 2. `σ_acc` accumulates as a random walk

`σ_acc` at lag `L`, scaled to each corner's own device-noise density:

| Corner | `L`=1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 |
|---|---|---|---|---|---|---|---|---|
| `ss`/−40/3.63 | 1.387 ps | 1.609 | 1.955 | 2.459 | 3.261 | 4.513 | 6.333 | 9.245 |
| `tt`/27/3.30 | 2.041 ps | 2.440 | 3.125 | 4.140 | 5.713 | 7.722 | 10.75 | 15.24 |
| `ff`/−40/3.63 | 1.004 ps | 1.266 | 1.684 | 2.311 | 3.247 | 4.562 | 6.398 | 8.773 |

| Corner | exponent, lags 1…128 | exponent, lags 16…128 |
|---|---|---|
| `ss`/−40/3.63 | 0.394 | **0.500** |
| `tt`/27/3.30 | 0.421 | **0.472** |
| `ff`/−40/3.63 | 0.457 | **0.479** |
| *for contrast: array-sanity run, lags 1…8* | *0.807* | — |

**Over the top decade of lag the exponent is 0.47–0.50 — a random walk, to
three significant figures at the entropy-binding corner.** That answers issue
#46's fourth acceptance criterion in the affirmative: this cell's jitter *is*
simulable as `√t` accumulation, and the `√t` extrapolation DR-0007 §2 and
DR-0010 rely on is sound for it.

Over *all* lags the exponent is 0.39–0.46, i.e. `σ` at short lags sits above
the `√L` line drawn through the long-lag behaviour. That is a
**non-accumulating** phase-noise component, not a defect, and it is **not
peculiar to the starved cell**: the same fit over the plain-cell family
(`2026-07-31-ro-inv-05stage-jitter-{01..27}`, lags 1…32) gives **0.471 mean,
0.404–0.551 over the grid** — statistically the same shape. Comparing the two
cells at lag 1 is therefore like-for-like.

### 3. `a` for the shipped starved cell

`a = κ² · P_ring / (k_B · T)`, with `κ²` taken two ways — at lag 1, as
`jitter_energy_law.py` takes it for the plain cell; and as the zero-intercept
slope of `σ²_acc` against elapsed time over the top decade of lag, which is the
part that actually accumulates and therefore the part DR-0007 §2's
extrapolation to a millisecond-scale sample period depends on:

| Corner | `T₀` | `P_ring` | `σ₁` | `κ²` (lag 1) | `κ²` (asymptotic) | **`a` (lag 1)** | **`a` (asymptotic)** |
|---|---|---|---|---|---|---|---|
| `ss`/−40/3.63 | 2.279 ns | 81.57 µW | 1.387 ps | 8.442 × 10⁻¹⁶ s | 2.889 × 10⁻¹⁶ s | **21.39** | **7.32** |
| `tt`/27/3.30 | 2.564 ns | 63.53 µW | 2.041 ps | 1.625 × 10⁻¹⁵ s | 7.093 × 10⁻¹⁶ s | **24.91** | **10.87** |
| `ff`/−40/3.63 | 1.507 ns | 135.7 µW | 1.004 ps | 6.694 × 10⁻¹⁶ s | 4.058 × 10⁻¹⁶ s | **28.22** | **17.11** |
| | | | | | mean | **24.84** | **11.77** |
| | | | | | spread max/min | **1.32×** | 2.34× |
| **plain cell**, 27-point grid | | | | | | **1.79** (spread 1.29×) | — |

**The ratio this issue exists to state: `a` for the shipped starved cell is
13.9× the plain cell's, taken like-for-like at lag 1; 6.6× taken on the
accumulating component alone.**

The *form* of the invariant survives intact. `a` at lag 1 varies **1.32×**
across a grid on which `P_ring` itself spans 2.14× and `κ²` spans 2.43× — the
same constancy the plain-cell fit shows (1.29× over its own grid). What moved
is the value, and it moved a long way.

### 4. What this does and does not settle about the array-sanity run

**That record is not superseded by this work**, in the formal sense
`sim/README.md` gives the word: nothing here re-runs its testbench, so it keeps
`status: valid` and no `superseded_by` field. What follows is a reading of it
alongside a different measurement.

It settles the number: the `κ²` in
[`2026-08-01-ro-array-sanity-jitter-01`](records/2026-08-01-ro-array-sanity-jitter-01.md)
is 1.3 × 10⁴ above `(★)`, and the correct figure for the same cell is
**7–14×** above it, three orders of magnitude lower than that record implies.

It does **not** settle *why* that record is wrong, and this document will not
pretend otherwise. The hypothesis in DR-0010 and in issue #46 was that a
16-period window opened at the second edge cannot measure jitter. **This
measurement refutes that as a complete explanation**: the same testbench
reports a 16-period, opened-at-start-up window *inside the same run*
(`sigma_startup16_*`), and that window behaves like a genuine, merely noisy,
jitter estimate — 16–24 % seed spread against a 15 % reference, and an `a`
within 1.8× of the 512-period figure. A short window is imprecise here; it is
not pathological.

So the remaining difference is the **device environment**, not the window:
`sim/tb/ro-array-sanity-jitter/` simulates four rings and an XOR tree in one
deck, with `ro1` driving the `a` input of `xa1`. The leading hypothesis is
therefore that ring 1's crossings in that deck are perturbed
**deterministically by ring 2 through the shared `xa1` input stage** — which
would be seed-independent (0.3 % spread), would accumulate faster than `√t`
(`lag^0.81`), and is a beat between two rings rather than noise in either.
That was a hypothesis when this document was first written. [#51] has since
measured it, with four DUT variants that differ from this deck by one thing
each, and **it is confirmed**: one ring plus the array's own `xa1` driven by
one neighbouring ring reproduces `σ₁` to 0.83×, the accumulation exponent to
0.825 against 0.810, and the anomalous 1.0 % seed spread, while the same two
rings with no wire between them reproduce this deck's `σ₁` to 1.00×. The
mechanism is electrical coupling through the combiner's input stage, not a
shared-timestep numerical artefact. See
[`characterization-array-ring-coupling.md`](characterization-array-ring-coupling.md).

The honest reading is therefore: **`a` is measured here for the cell, on a ring
loaded exactly as the plain-cell reference ring is; the array record's `σ_r1_*`
is dominated by a deterministic neighbour-driven beat and is not that ring's
jitter.** What the array's own `σ` is, with that term removed, is still
unmeasured — `sim/tb/ro-array-sanity-jitter/` has not been re-run.

## What this means for DR-0010 §1

**The rate row moves — up — and it moves by a superseding decision record, not
by an edit here.** That record is
[`DR-0011`](../spec/decision-records/DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md).
The arithmetic it rests on is reproducible from this tree:

```sh
python3 sim/tools/array_sizing.py --a 7.322      # the entropy-binding corner's own constant
```

| `a` | `Q_array` at `ss`/−40/3.63, 500 bps | Highest rate meeting DR-0007 §2 there |
|---|---|---|
| 1.79 — DR-0010, plain cell | 7.82 × 10⁻³ | 651 bps |
| **7.32** — starved cell, asymptotic, at that corner | 3.20 × 10⁻² | **2664 bps** |
| 11.77 — starved cell, asymptotic, mean of three corners | 5.14 × 10⁻² | 4282 bps |
| 24.84 — starved cell, lag 1, mean of three corners | 1.09 × 10⁻¹ | 9040 bps |

`sim/tools/array_sizing.py`'s stated `A_JITTER_ENERGY` is **deliberately left
at 1.79** by this work. It is the constant DR-0010 §3's published table and
`design/README.md` are quoted against, and `--check` holds it to the plain-cell
derivation; moving it is what accepting DR-0011 means, and DR-0011 lists the
exact edits that acceptance implies. The `--a` flag exists so this document can
price the alternative without any of them.

## Caveats

- **Fixed-injection scaling.** Every `σ` here is a fixed-injection figure
  scaled by a single-frequency (1 GHz) proxy for the device noise density.
  `characterization-ro-delay-cell-jitter.md` states that scaling is good to
  ~1.5–2× on `σ`, hence ~2–4× on `κ²` and on `a`. **The 13.9× ratio is outside
  that band, but not by a large factor**, and — unlike the corner-to-corner
  comparison, where the scaling error is largely common-mode — a cell-to-cell
  comparison is exactly where that error does *not* cancel. The two supporting
  facts that do not depend on the absolute scaling are that the two
  `.noise` testbenches define `inoise_dens_1g` identically (same sweep, same
  spectrum index), and that `a`'s **constancy** across corners (1.32×) is as
  tight for the starved cell as for the plain one.
- **The ring is unloaded**, matching the plain-cell reference ring, and so
  `T₀`, `P_ring` and `E_cycle` here are **not** the shipped array's. Ring 1 of
  the array runs at 3.305 ns and 1.987 × 10⁻¹³ J per cycle against this deck's
  2.564 ns and 1.629 × 10⁻¹³ J at the same corner — the `xa1` input load is
  worth ~29 % of the period and ~22 % of the switched energy. Cite
  `*-ro-array-core-power-*` for the array as built; this document is about the
  cell.
- **Five stages, not the shipped eleven.** `ro_ring5`, matching the plain-cell
  reference's stage count so the delay cell is the only variable. `a` is
  stage-count-free by construction (it relates `κ²` to `P_ring`, both measured
  on the same ring), and DR-0010 §3 measures `E_cycle ∝ n` to within 1 % on
  this cell — but no five-to-eleven check of `a` itself exists.
- **White noise only.** `trnoise()` here injects a white PSD
  (`NALPHA` = `NAMP` = 0); the flicker exclusion of DR-0007 §2 stands
  unchanged, so `κ²` is a lower bound on the physical one.
- **`tstep` = 1 ps**, matching the plain-cell reference family. At 10 ps the
  solver takes 2.6× fewer points and the same deck's mean period agrees to five
  significant figures, but no `σ` comparison at the two settings was run, so
  every figure here is at 1 ps.
- **The testbench's own header carries the pre-measurement hypothesis.**
  `sim/tb/ro-ring5-starved-jitter-long/tb_ro_ring5_starved_jitter_long.sp`
  states, as its reason for existing, that the array-sanity run measured
  "deterministic settling drift". §4 above shows that explanation is
  incomplete. The header is left as it was written because its blob SHA is
  recorded in all three records (`testbench.sha`), and editing it after the run
  would break the provenance those records exist to provide. §4, not the
  header, is the current reading.
- **Not an entropy assessment.** DR-0004's tiering is unchanged.

[#12]: https://github.com/2AMLogic/gf180-trng/issues/12
[#51]: https://github.com/2AMLogic/gf180-trng/issues/51
[#46]: https://github.com/2AMLogic/gf180-trng/issues/46
