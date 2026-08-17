# Worst-corner entropy degradation and Monte Carlo mismatch bias

Status: measurement complete for issue [#13]. It reports two things and a
consequence:

1. The entropy-binding (minimum-`Q`) PVT corner of the shipped array,
   measured over the **full covered 27-point grid** rather than inferred from
   three points — and it is **not** the corner
   [DR-0012-sampler-fixed-external-clock] predicted. That is recorded, not
   reconciled away: [DR-0015] is the superseding decision record, filed under
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
them. [DR-0015] carries that as an explicit follow-up, sharpened by the fact
that an edge-triggered sampler now exists downstream ([#9]) — which is the
condition DR-0006 itself named for adding those corners.

## 3. Monte Carlo mismatch

Every record in §2 is a single, mismatch-free device draw. Two Monte Carlo
testbenches close that gap. **Issue #146** extended both beyond the nominal
corner and added a deterministic negative control per testbench:

- **Combined with process/temperature/supply corners** (§3.1, §3.2): each
  testbench now runs its mismatch draw at two PVT points, not one —
  `tt`/27 °C/3.30 V (the pre-existing nominal record) and `ss`/+125 °C/3.63 V
  ([DR-0015]'s measured entropy-binding worst corner over the array's full
  covered PVT grid). This is a justified **subset**, not the harness's full
  `mos` corner set (`tt`/`ff`/`ss`/`fs`/`sf`) × 3 temperatures × 3 supplies
  (45 points): the two points chosen are the ones a reader most needs — the
  pre-existing baseline and the corner DR-0015 already flags as worst — and
  each testbench's own `tb.json` `caveats` state this explicitly rather than
  silently narrowing.
- **A mechanism fix, not just new points.** Before #146, both manifests set
  `extra_lib_sections: ["statistical"]`, which unconditionally replaces
  whichever corner's own per-family model sections would otherwise load
  (`sim/harness/runner.py`'s `compose_deck`) — so setting `corners` to
  anything other than `tt` was silently a no-op (the pre-#146 records' own
  caveats said as much). #146 removed `extra_lib_sections`: every gf180mcu
  per-corner device library already implements the identical
  `sw_stat_mismatch`-gated local (Pelgrom) mismatch model the `statistical`
  section used, so `sw_stat_mismatch=1` alone, with the harness's normal
  per-corner `.lib` selection, combines mismatch with a real process corner.
  Because the mechanism changed, the pre-#146 nominal-corner records for both
  testbenches are marked `superseded` and re-run under the corrected
  manifest (new stems below) — same DUT, same seed counts, numerically
  consistent spread magnitude (the small shift in exact values is the
  seeded-RNG draw order changing along with which `.lib` sections load, not
  a change in what is being modelled).
- **Deterministic negative control** (§3.4): a sibling testbench per MC
  testbench (`sim/tb/ro-array-core-mc-freq-control/`,
  `sim/tb/sampler-dff-mc-offset-control/`) with `sw_stat_mismatch=0`, run at
  the same two PVT points — showing the seed-to-seed spread collapses to
  (numerically) exactly zero when the switch that produces it is off.

### 3.1 RO array frequency spread (`sim/tb/ro-array-core-mc-freq/`)

8 independent full-array mismatch draws per corner. The per-seed pairing
below is read from each record's raw ngspice logs rather than from its
marginal per-ring statistics, because the question [DR-0007] §1 asks is about
the *ratio within one draw*: whether some chip's mismatch could pull the two
rings towards a common frequency and open the door to injection locking.

| Quantity | `tt`/27 °C/3.30 V (`…-mc-freq-01`) | `ss`/+125 °C/3.63 V (`…-mc-freq-02`) |
|---|---|---|
| `period_r1` seed-to-seed CV | 0.13 % | 0.11 % |
| `period_r2` seed-to-seed CV | 0.16 % | 0.14 % |
| Ring frequency ratio `f_r2/f_r1`, per-draw | mean 1.0691, sd 0.0018 (0.17 % of mean) | mean 1.0726, sd 0.0013 (0.12 % of mean) |
| Distance of the mean ratio from the nearest integer | 39.1 sd | 54.4 sd |
| Closest any single draw came to an integer ratio | 0.067 | 0.072 |

(`sim/records/2026-08-17-ro-array-core-mc-freq-01.md`, seeds 1–8;
`sim/records/2026-08-17-ro-array-core-mc-freq-02.md`, seeds 1–8. The former
`supersedes: 2026-08-01-ro-array-core-mc-freq-01`, the pre-#146 nominal-only
record, for the mechanism-fix reason above.)

The array's deliberate ~6 % frequency skew (`design/README.md`: 1.057 at
`ff`/−40 °C/3.63 V to 1.062 at `ss`/−40 °C/3.63 V, mismatch-free) is roughly
**60–90× larger than the mismatch-driven scatter around it at either measured
corner**. Mismatch moves the ratio; it does not come close to erasing the
design's own margin against the integer-ratio condition, and the binding
corner's scatter is if anything *tighter* (0.12 % vs 0.17 % of mean) than the
nominal corner's, not wider.

For `Q`: at fixed ring power `Q ∝ 1/T₀²`, so a 0.11–0.13 % period spread moves
`Q_array` by ~0.2–0.3 % — negligible against the 1.20×–16.62× margins in §2 at
either corner.

**Negative control** (§3.4 below): `sim/records/2026-08-17-ro-array-core-mc-freq-control-{01,02}.md`
report the identical measurement with `sw_stat_mismatch=0` at both corners —
`period_r1` sd is exactly `0` over 3 seeds at each, i.e. the spread above
collapses to nothing when the mechanism producing it is switched off.

### 3.2 Sampler decision threshold (`sim/tb/sampler-dff-mc-offset/`)

`sampler_dff` has no analog comparator input by design — it is an ordinary
static CMOS transmission-gate flip-flop. Its closest analogue to an
input-referred offset is the master latch's own switching threshold: the `d`
voltage at which its first inversion (node `mb`) crosses mid-supply, with
`clk` held at 0 so that the master is in its open-loop, non-bistable phase and
a `.dc` sweep has a single-valued solution. 30 independent mismatch draws per
corner.

| Quantity | `tt`/27 °C/3.30 V (`…-mc-offset-03`) | `ss`/+125 °C/3.63 V (`…-mc-offset-02`) |
|---|---|---|
| Decision threshold, mean over 30 seeds | 1.3848 V | 1.5402 V |
| Decision threshold, seed-to-seed sd (**mismatch-driven**) | 14.78 mV (0.45 % of VDD) | 15.02 mV (0.41 % of VDD) |
| **Systematic** offset from ideal mid-supply | **−265.2 mV** (vs 1.65 V) | **−274.8 mV** (vs 1.815 V) |

(`sim/records/2026-08-17-sampler-dff-mc-offset-03.md`, seeds 1–30, `tt`
corner, `supersedes: 2026-08-02-sampler-dff-mc-offset-01` for the
mechanism-fix reason above; `sim/records/2026-08-17-sampler-dff-mc-offset-02.md`,
seeds 1–30, `ss`/+125 °C/3.63 V corner, new.)

The systematic offset is present at *every* seed alike, at both corners: it
is a property of the cell's structure on this PDK's device models, not a
mismatch effect, and it would be there in a mismatch-free simulation too.
Since
[`DR-0014-sampler-reset-gated-into-the-storage-loops`](../spec/decision-records/DR-0014-sampler-reset-gated-into-the-storage-loops.md)
(#59) the master's first inversion is a reset-gated NAND2 with a
width-compensated NMOS stack rather than a plain 0.44 µm/0.22 µm inverter; a
series stack does not compensate exactly, which is where the offset comes
from. It is reported because it is what the testbench measures and because it
dominates the mismatch term by ~18×, but it is a design observation rather
than this issue's deliverable; no design change is proposed here.

**The binding corner does not widen the mismatch-driven spread relative to
nominal** (15.02 mV vs 14.78 mV, a 1.6 % difference) and moves the systematic
offset by only −9.6 mV — §4 below no longer needs to assume this; it is now a
measurement, reported next to the extrapolation §4 previously had to rely on
for lack of one.

**Negative control** (§3.4 below):
`sim/records/2026-08-17-sampler-dff-mc-offset-control-{01,02}.md` report the
identical measurement with `sw_stat_mismatch=0` at both corners — `dtrip_v`
sd is exactly `0` over 3 seeds at each.

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
the systematic offset would have looked like roughly *half* the jitter budget
at the binding corner, i.e. like a live spec problem, when the measured slew
puts it at 1.5 %. That is why the proxy was replaced by a measurement rather
than reasoned around. (Ten records were written, covering `ff` and `ss` at −40 °C
and `ss` at +125 °C across ±10 % supply as well as the nominal point; the
three used above are the ones the bias analysis quotes.)

### 3.4 Deterministic negative control (issue #146, Leg 2)

A seeded Monte Carlo record with a visible spread is not, by itself, proof
that the spread comes from device mismatch rather than some other source of
run-to-run variation in the harness or the deck. The checklist item this
whole section closes ([#140]'s T1 verdict, item 6) asked for the thing that
tells the two apart: a control run with mismatch mechanically disabled
(`sw_stat_mismatch=0`), at the same corners, so a reader can see the spread
collapse rather than take it on faith.

| Testbench | Corner | `sw_stat_mismatch=1` sd | `sw_stat_mismatch=0` sd | Record |
|---|---|---|---|---|
| RO array `period_r1` | `tt`/27 °C/3.30 V | 8.43 ps (0.13 %) | **0** (exact, 3 seeds) | `2026-08-17-ro-array-core-mc-freq-control-01.md` |
| RO array `period_r1` | `ss`/125 °C/3.63 V | 10.31 ps (0.11 %) | **0** (exact, 3 seeds) | `2026-08-17-ro-array-core-mc-freq-control-02.md` |
| Sampler `dtrip_v` | `tt`/27 °C/3.30 V | 14.78 mV (0.45 %) | **0** (exact, 3 seeds) | `2026-08-17-sampler-dff-mc-offset-control-01.md` |
| Sampler `dtrip_v` | `ss`/125 °C/3.63 V | 15.02 mV (0.41 %) | **0** (exact, 3 seeds) | `2026-08-17-sampler-dff-mc-offset-control-02.md` |

The mechanism: gf180mcu's per-corner device libraries compute each device's
local (Pelgrom) mismatch offset unconditionally (`mis_vth = agauss(...)`) and
only gate its *effect* on the model by multiplying it by `sw_stat_mismatch` —
with that switch at 0, the offset is always multiplied to exactly zero
regardless of which `.option seed` is active, so every seed of a control run
produces bit-for-bit identical output. That is exactly what the four rows
above show: `sd = 0` over 3 distinct seeds at every corner, for both
testbenches, against a nonzero, corner-consistent spread when mismatch is
on. Each control testbench's own `tb.json` caveats spell out why 3 seeds
(not the mismatch-enabled record's full count) is enough here: a single seed
would already be sufficient given the mechanism, but distinct seeds
collapsing to the same number is more convincing than asserting invariance
from the mechanism alone.

### 3.5 `klt yield` (issue #146, Leg 3 — not run)

The `klt yield` verb (Monte Carlo sample set + spec limits -> yield
estimate with CIs) **is present** on the `klt` build this repository now
uses: [gf180-trng#142] re-pinned `klt` off the floating PyPI `v0.2.0`
release onto a specific `klayout-tools` git commit
(`a482d3934bd644b763cf925f6344ac05f54a1623`, `layout/_klt.py`'s pin,
[#163]) specifically to pick up the gf180mcu digital flow, `klt pex` and
`klt yield` that had landed on `klayout-tools` `main` but never reached a
release -- `klt yield --help` resolves against that pin, confirmed both
during [gf180-trng#142]'s own verification and again here.

**But it does not run.** Constructing the sample-set document `klt yield`
expects (`{"measurements": [{"name", "samples", "limits"}, ...]}`) from
this section's own MC records (e.g. `period_r1`'s 8-seed sample vector) and
invoking `klt yield` against it, confirmed empirically today:

```
$ klt yield sample_set.json
klt yield: the klt_yield_native extension is not installed -- from a repo
checkout, run `maturin develop --release` inside native/yield/ (or `uv sync
--group yield`); see docs/cli/yield.md#building-the-native-extension
```

The verb's statistics run in a native Rust extension (`klt_yield_native`,
`native/yield/` in the `klayout-tools` source tree) that is not published
as a prebuilt wheel and is not built by a `pip`/`git+https://...` install
(the install method `.github/workflows/pdk-nightly.yml` and this repo's
`layout/README.md` both document) -- building it needs a full source
checkout of `klayout-tools` and a Rust toolchain, which is that repository's
own build system, not this one's, and out of scope for this issue (per
#146's own leg-3 scope note: "only address it if trivially available,
otherwise record why it's absent"; it is not). That gap -- the CLI surface
existing on a git-pinned install while the verb it names is unreachable
from that same install method -- is filed generically (tool gap, not this
block's design) at
[klayout-tools#1061](https://github.com/2AMLogic/klayout-tools/issues/1061),
per this repository's friction protocol. Once that lands (a prebuilt wheel,
or a documented pip-reachable build path), the corresponding report belongs
here, backed by its own evidence record under `sim/records/` for whichever
of this section's MC records it is run against.

## 4. Do the conditioner and health-test margins cover the observed spread?

**The model, stated once.** The ring's crossing time at the sampler is
Gaussian with sd `σ_acc(T_s) = √(κ²·T_s)`; a threshold offset displaces that
crossing by `dt = offset/slew`; the captured bit's probability is
`p = Φ(dt/σ_acc)`. The `H` this yields is a **ceiling** — what `H` could be
if bias were the *only* departure from ideal — so the question it answers is
not "what is `H`" but "is bias anywhere near being the binding constraint".

Since issue #146, a REAL sampler-offset MC measurement exists at
`ss`/+125 °C/3.63 V (§3.2), not just at nominal — the systematic offset there
is −274.8 mV against the nominal corner's −265.2 mV (a −9.6 mV corner delta)
and the mismatch sd is 15.02 mV against 14.78 mV. The table below still uses
the **nominal** offset carried over to each corner's own slew/jitter — the
tool's stated methodology, unchanged — but the close agreement between that
extrapolation and the real measurement (§3.2) is itself evidence the
extrapolation was not hiding anything large.

The tool evaluates it at three corners. At **`ss`/+125 °C/3.63 V, the
entropy-binding corner** ([DR-0015]) — measured slew 1.380×10¹⁰ V/s,
`σ_acc` = 1.538 ns at [DR-0010]'s 500 bps:

| case | `dt/σ_acc` | `p_major` | `H` ceiling | vs H₀ = 0.5 | vs [DR-0008] break-even |
|---|---|---|---|---|---|
| mismatch spread, 1 sd | 0.001 | 0.5003 | 0.9992 | 2.00× | 9.39× |
| mismatch spread, 3 sd | 0.002 | 0.5008 | 0.9976 | 2.00× | 9.37× |
| systematic offset alone | 0.012 | 0.5050 | 0.9857 | 1.97× | 9.26× |
| systematic + 3 sd mismatch | 0.015 | 0.5058 | 0.9833 | 1.97× | 9.24× |

At `tt`/27 °C/3.30 V (where the offset itself was measured, and where `κ²` is
directly measured rather than law-derived) and at `ss`/−40 °C/3.63 V, the same
four rows land within 0.003 of these — the three corners' slews and jitter sds
move in the same direction and largely cancel. The worst of all twelve rows,
anywhere, is `p_major` = 0.5078, at `ss`/−40 °C/3.63 V (systematic + 3 sd
mismatch).

**The mismatch-driven bias — issue #13's actual question — is ~1 ps of timing
offset against a 0.76–1.54 ns jitter sd, i.e. one part in a thousand.** Even
the ~18×-larger systematic offset costs 13–18 ps, ~1.2–1.9 % of the jitter
budget.

Against the spec's own margins, at the worst of those twelve rows
(`p_major` = 0.5078):

| Margin | Requirement | At the modelled worst case | Headroom |
|---|---|---|---|
| [DR-0008] conditioner: K = 8 CRC-32 earns the full 0.85 bit/bit non-vetted cap at `H` ≥ 0.106456 | `H` ≥ 0.106456 | bias-only ceiling 0.9777 | **9.18×** |
| [DR-0002] RCT, cutoff `C_RCT` = 81 frozen at H₀ = 0.5, α = 2⁻⁴⁰ | `Pr(81 identical consecutive)` ≤ 9.095×10⁻¹³ | 2.8×10⁻²⁴ | 11 orders of magnitude |
| [DR-0002] APT, cutoff `C_APT` = 824 in W = 1024, α = 2⁻⁴⁰ | `Pr(X ≥ 824 \| X ~ Bin(1024, p))` ≤ 9.095×10⁻¹³ | 1.4×10⁻⁸⁶ | expected majority count 520 vs the 824 cutoff — **19.0 sd** |

**The conditioner and health-test margins cover the observed mismatch spread
with room to spare**, which is the question issue #13 asks. Note what that
statement does and does not say: it says device mismatch is not what will
limit this block's entropy, and that the health tests will not false-trip on
it. It says nothing about what `H` actually is — that is [#12]'s measurement,
and these are ceilings.

## Caveats

- **Two PVT points per MC testbench (issue #146), not a full corner sweep.**
  Both testbenches now repeat the mismatch draw at `tt`/27 °C/3.30 V and
  `ss`/+125 °C/3.63 V ([DR-0015]'s binding corner) — a justified subset of
  the harness's full `mos` corner set (`tt`/`ff`/`ss`/`fs`/`sf`) × 3
  temperatures × 3 supplies (45 points), not the full grid; see §3's intro
  and each testbench's own `tb.json` caveats for the rationale. §3.2 now
  reports a REAL measured sampler offset at the binding corner (not just an
  extrapolation), and it agrees closely with the nominal-corner value §4's
  table still extrapolates from — but the RO array's frequency-ratio spread
  (§3.1) and §4's `σ_acc`/slew inputs at `ss`/−40 °C/3.63 V remain unmeasured
  at that specific third corner (no MC record exists there — DR-0015's own
  grid does not repeat mismatch draws either).
- **Seed counts (30 for the sampler, 8 for the RO array) characterize the
  spread's rough magnitude, not a tail probability.** A claim about the
  *fraction* of fabricated parts that would violate a margin needs many more
  samples than either record provides.
- **`κ²` at the binding corner is law-derived, not measured.**
  `sim/tb/ro-ring5-starved-jitter-long/` ran at three corners, none of them
  `ss`/+125 °C/3.63 V, so `σ_acc` there comes from [DR-0010]'s jitter-energy
  law applied to a measured period and current. That is exactly how DR-0007
  §2 intends `Q` to be evaluated, but it is a model at the one corner that
  matters most; [DR-0015] carries the follow-up.
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
  top of whichever corner (`tt` or `ss`) is already selected.
- **The slew testbench drives an unloaded `xo`.** In
  `design/xschem/sampler_core.sch` that node also drives `sampler_dff`'s data
  transmission gate, which would slow the edge. The measured slew is
  therefore an upper bound on the loaded one — but §4's worst case sits at
  1.5 % of the jitter budget, so the loaded edge would have to be ~30× slower
  than the measured one before the conclusion moved.
- **Not an entropy assessment.** [DR-0004]'s tiering is unchanged.

[#9]: https://github.com/2AMLogic/gf180-trng/issues/9
[#12]: https://github.com/2AMLogic/gf180-trng/issues/12
[#13]: https://github.com/2AMLogic/gf180-trng/issues/13
[#52]: https://github.com/2AMLogic/gf180-trng/issues/52
[#140]: https://github.com/2AMLogic/gf180-trng/issues/140
[#146]: https://github.com/2AMLogic/gf180-trng/issues/146
[gf180-trng#142]: https://github.com/2AMLogic/gf180-trng/issues/142
[#163]: https://github.com/2AMLogic/gf180-trng/pull/163
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
[DR-0015]: ../spec/decision-records/DR-0015-entropy-binding-corner-moves-to-the-hot-slow-corner.md
