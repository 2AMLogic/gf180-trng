# `design/` — schematics and their exported netlists

This file covers the block's **analog** half: the xschem schematics
(`design/xschem/`) and the SPICE netlists exported from them
(`design/*.spice`). The netlists are **generated files under version control**:
they are committed so that every evidence record under `sim/records/` can name
a `netlist.path` /`netlist.sha` that a reader can actually fetch, and they are
regenerated — never hand-edited — by `design/netlist.py`.

The digital half lives beside it in three directories, each a behavioural
model plus synthesisable RTL with its own README:
[`design/conditioner/`](conditioner/) (the post-processing stage),
[`design/health_test/`](health_test/) (the on-die RCT/APT health tests and
the start-up test, #11), and
[`design/interface/`](interface/) (the register file, output FIFOs,
`OUT_MODE` mux and gate/flush machine). None has a schematic or a netlist,
so `design/netlist.py` neither reads nor checks them; the boundary between the
analog and digital halves is the raw tap, per
[`DR-0009`](../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md).

The digital half is not unguarded, though — it carries the same
*deterministic-export* discipline in the form it actually has. The interface
block's register map lives in one normative table
(`design/interface/regmap.py`) that generates both the RTL's included header
and the integrator-facing pinout document, with
`python3 design/interface/regmap.py --check` as the staleness guard. Unlike
`netlist.py --check` it needs no PDK and no external tool, so it runs inside
the PR-blocking unit-test set rather than nightly.

```sh
python3 design/netlist.py            # (re-)export every top cell
python3 design/netlist.py --check    # fail if a committed netlist is stale
```

`--check` is the staleness guard. It re-exports into a temporary directory and
diffs; it never writes. A committed netlist whose SHA appears in an evidence
record is only meaningful if it provably comes from the schematic it claims to,
and `--check` is what makes that provable rather than asserted. See the script's
own module docstring for how it makes xschem's output machine-independent
(generated rc file, PDK resolved through the same chain `sim/harness/pdk.py`
uses, absolute paths rewritten to repo-relative, and SPICE continuation lines
re-wrapped at a column the script owns).

That last one exists because xschem 3.4.4 and 3.4.7 emit byte-identical netlist
*content* for these schematics but break long device lines onto `+`
continuations at different columns. Left alone that made `--check` a test of the
developer's distro rather than of the schematics: the same commit passed on one
xschem and failed on the other, with nothing having changed. Since SPICE joins
`+` continuations back into one logical line before parsing, the wrap point
carries no information, so `netlist.py` now discards xschem's choice and applies
its own. Content changes still fail `--check` loudly, which is the part worth
being loud about.

---

## What is here

| Cell | Role |
|---|---|
| `ro_stage` | the delay cell: a minimum-width 3.3 V inverter with always-on series starve devices |
| `ro_nand2` | the same cell with a second input, so a ring can be stopped in a defined static state |
| `ro_ring11` | one ring of the shipped array: `ro_nand2` + ten `ro_stage`, closed on itself, on its own supply pin |
| `ro_ring5` | the five-stage variant, used only by the transient-noise sanity testbench |
| `xor2` | one node of the combining tree (static CMOS, minimum width) |
| **`ro_array_core`** | **the entropy source**: two `ro_ring11` with skewed starve widths and separate supply pins, XOR-combined into one output |
| `ro_array_sanity` | a four-ring array built from `ro_ring5`, with the ring outputs brought out for observation; a simulation vehicle, not a shipped cell |
| `meta_inv` / `meta_nand2` | unstarved minimum-width delay/logic cells for the metastability-hybrid tap (`ro_stage`/`ro_nand2` want the opposite: the sharpest edge the tap wants is the wrong thing for a ring) |
| `meta_arb` | the tap's metastable element: a cross-coupled NAND2 SR latch, symmetric by construction |
| `ro_meta_tap` | the metastability-hybrid **stretch tap** (issue #43, [`DR-0011`](../spec/decision-records/DR-0011-metastability-hybrid-tap-claims-and-scope.md)): a self-timed matched-delay strobe off an RO transition into `meta_arb`, on its own supply pin `vddm` |
| `ro_array_core_meta` | `ro_array_core` (unmodified, instantiated) plus `ro_meta_tap` hanging off `xo`; exists only to simulate the tap in situ, nothing on `main` instantiates it by default |
| `sampler_dff` | **the sampler/digitizer**: a transmission-gate master-slave D flip-flop, positive-edge, async active-low reset gated into the storage loops' own inverters ([`DR-0014`](../spec/decision-records/DR-0014-sampler-reset-gated-into-the-storage-loops.md)) — the cell that turns `xo`'s analog swing into a logic-level raw bit |
| **`sampler_core`** | **the sampler, wired to the source**: `ro_array_core` + two `sampler_dff` (one for `raw_bit`, one for the `raw_valid` reset-release indicator), clocked by a fixed external clock — see [The sampler](#the-sampler-9) below |

Exported netlists: `design/ro_array_core.spice`, `design/ro_array_sanity.spice`,
`design/meta_arb.spice`, `design/ro_meta_tap.spice`, `design/ro_array_core_meta.spice`,
`design/sampler_core.spice`.

---

## The entropy source, and why it is shaped like this

The topology is not a free choice: [`DR-0007`](../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)
§1 makes it binding — N independent, separately-supplied, free-running rings at
deliberately non-integer frequency ratios, XOR-combined into the single node one
sampler observes. What this issue owned was the *sizing*: the delay cell, the
stage count, N, and the operating point. The reasoning is in
[`DR-0010`](../spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md);
this section is the short version, mapped onto the cells above.

### The one equation the sizing turns on

For a ring whose phase performs a random walk, `sigma_acc^2(t) = kappa^2 t`, and
DR-0007 §2's array figure of merit is `Q_array(T_s) = sum_i kappa_i^2 T_s /
T0_i^2`. This repository's own PVT grid says `kappa^2` is not a free variable —
its product with the ring's power is fixed by temperature alone:

```
a = kappa^2 * P_ring / (kB * T)      = 1.79 +/- 0.14   (27-point grid, spread 1.29x)
```

Re-derive it from the committed records at any time:

```sh
python3 sim/tools/jitter_energy_law.py --check
```

Substituting `P_ring = E_cycle / T0` with `E_cycle = n * C_eff * V^2` collapses
the array figure of merit to

```
Q_array(T_s) = a * kB * T * T_s * P_rings / E_cycle^2
```

Every sizing decision below is that equation being read in one direction or
another:

- **`Q_array` does not depend on N or on ring frequency separately** — only on
  the array's *total* ring power and on the energy switched per ring cycle. N
  and `T0` are therefore free to be chosen for independence and for sampler
  bandwidth, not for entropy.
- **Energy per ring cycle enters squared.** It is the only strong lever, and
  `E_cycle = n * C_eff * V^2` names its three factors.

### `ro_stage`: minimum energy per cycle, at every factor

- `V` is the block's ratified 3.3 V supply. Not this issue's to move.
- `C_eff` is minimised by using the smallest inverter the gf180mcu 3.3 V core
  devices allow (`pfet_03v3` W = 0.44 µm, `nfet_03v3` W = 0.22 µm, L = 0.28 µm)
  and by adding **no** deliberate load capacitor. The ratified characterization
  cell (`sim/tb/inv-stage-noise/`) is 4-5x wider and carries an explicit 5 fF
  load; it measures `C_eff` = 12.7 fF per node
  (`sim/characterization-supply-current-and-leakage.md`).
- `n` is set by the *ring*, not by the cell — see below.

Frequency is then set by the **series starve devices** `Mph` / `Mnt`, whose
gates are tied to the opposite rail so they are always on and act as fixed
resistances. This is the load-bearing detail: starving lowers the ring's current
and therefore its frequency **without adding switched capacitance to the output
node**, so it moves `T0` and `P_ring` together at constant `E_cycle`. Under the
equation above that means starving trades ring frequency against ring count at
constant `Q_array` — it buys N, and it costs nothing in entropy.

Slowing a ring the other way — by loading its output — would raise `C_eff` and
cost `Q_array` quadratically. That is why the starve device is a series element
and not a capacitor.

### `ro_ring11`: eleven stages, and why not three — or five

`E_cycle` is proportional to the stage count, so entropy per unit of ring power
would prefer the minimum inverting ring, three stages. Measurement says
otherwise, and the mechanism is small-signal gain.

`sim/tb/rostage-noise/` measures the starved cell's gain at its own trip point —
the operating point a ring stage passes through while switching. It is **2.59 at
1 GHz at nominal and 1.68 at `ss`/125 °C/2.97 V**
(`sim/records/2026-08-01-rostage-noise-{01,04}.md`). An `n`-stage inverting ring
needs a per-stage gain of `1/cos(π/n)` to sustain a rail-to-rail oscillation:
**2.00 for three stages, 1.24 for five, 1.06 for eleven.** Three stages
therefore has no margin at nominal and is under water at the slow/hot/low-supply
corner. Simulated directly with this cell, the consequence is visible:

| Ring | measured output swing | supply |
|---|---|---|
| 3-stage | ~1.48 V (45 %) | 3.30 V |
| 5-stage | 2.64 V (80 %) | 3.30 V (`…-ro-array-sanity-jitter-01.md`, `ring1_swing_v`) |
| 11-stage | rail to rail | 3.30 / 3.63 V (`…-ro-array-core-power-*.md`, `ring_swing_v`) |

A ring that does not reach the rails is a ring whose swing margin is being spent
rather than banked. The five-stage case is the one that costs something real —
about 4.2× on the raw-rate row — and `DR-0010` §3 (*What five stages would buy*)
prices it against exactly these swing figures rather than leaving the trade
unquantified. Note in fairness that the XOR node in that same sanity record does
restore to 3.52 V on a 3.30 V rail from 2.64 V inputs, so "the sampler is handed
an analog level" is not established at nominal; what is established is that a
five-stage ring has 20 percentage points less swing margin at the one corner it
has been measured at, and no measurement at all at the corners the spec binds
on.

A second constraint points the same way: the combined node sees
`R_x = 2 N / T0` transitions per second and is driven by ordinary minimum-width
static gates. Keeping `R_x` inside what those gates sustain needs a ring period
of several nanoseconds, and a three-stage ring cannot be starved that far
without losing the swing above.

`ro_ring5` exists for the transient-noise sanity testbench only. It is not a
shipped cell; see [The sanity vehicle](#the-sanity-vehicle) below.

### `ro_array_core`: N = 2, and why the combiner sets it

Under the equation above, entropy is indifferent to N at fixed *total* ring
power, so N is free to be chosen for independence — and what binds it is the
XOR tree. Measured at the `ff`/+10 %/−40 °C power corner:

| Array | rings | XOR tree | total | vs `< 500 µW` | record |
|---|---|---|---|---|---|
| N = 4, `lstv` = 2 µm | 573 µW | 444 µW | 1017 µW | 2.0× over | `…-ro-array-core-power-01.md` |
| N = 4, `lstv` = 6 µm | 414 µW | 525 µW | 939 µW | 1.9× over | `…-02.md` |
| **N = 2, `lstv` = 2 µm (shipped)** | **270 µW** | **146 µW** | **415 µW** | **fits** | `…-04.md` |

Two things that table settles:

- **The XOR tree is 35–56 % of the entropy source's active power**, not a
  rounding term. At N = 4 it is a two-level tree carrying every ring's
  transitions twice.
- **Slowing the rings does not fix it.** Tripling the starve length (2 µm →
  6 µm) cut ring power, but the tree's energy per transition rose faster than
  its transition rate fell — slower ring edges leave the combining gates longer
  in short circuit — and the ring swing fell from 3.69 V to 3.19 V as a bonus
  penalty. Halving the ring count is the only lever that moved the total under
  the row, because it halves the tree's transition rate *and* its depth at once.

So the shipped array is `lstv = 2 µm` with **N = 2**: two rings at
`wstv` = 0.220 / 0.240 µm, on their own supply pins, combined by one `xor2`. The
measured frequency ratio is 1.057 at `ff`/−40 °C/3.63 V and 1.062 at
`ss`/−40 °C/3.63 V — no small-integer factorisation, which is the
schematic-level half of the injection-locking argument. Both ring outputs and
the XOR node swing rail to rail (3.65–3.73 V on a 3.63 V supply).

N = 2 is the floor of what DR-0007 §1 means by an array. `DR-0010` says so
explicitly and names the `Power` row as the next thing that has to give if #16's
isolation work finds two rings insufficient. The lever that would buy N back
without touching that row is a cheaper combiner, which nobody has scheduled.

For reference, per-ring active power is ~135 µW at that corner — **a factor ~14
below the ratified characterization cell's 1.93 mW at the same corner**
(`sim/characterization-supply-current-and-leakage.md`). That is what the
minimum-width, unloaded, series-starved cell buys, and it is why an array is
affordable at all.

### Does the array meet DR-0007 §2?

Yes, with margin, and it is checkable rather than asserted:

```sh
python3 sim/tools/array_sizing.py --check
```

At the entropy-binding corner (`ss`/−40 °C/3.63 V), `Q_array = 7.82 × 10⁻³`
against the required `M · Q_H₀ = 6.0 × 10⁻³` — a 1.30× margin on top of
DR-0007's own `M = 1.5` — at the 500 bps raw rate `DR-0010` proposes. The tool
evaluates the inequality from the committed per-ring period and supply-current
records via the jitter-energy law, refuses to use records of a different array
size than the one in `design/`, and exits non-zero if the inequality fails.

### The raw tap is not in this directory

`xo` is the noise source's output, not the block's raw tap. DR-0001 puts the raw
tap at the **sampler** output, after digitisation, and no per-ring signal leaves
`ro_array_core` at all — which is why `ro_array_sanity`, and not
`ro_array_core`, is the cell with `ro*` observation pins. The sampler is
`sampler_core` (see [The sampler](#the-sampler-9) below), and its clock source
— a fixed external clock, per DR-0012 — pins DR-0007 §4's corner metric to
`Q ∝ σ₁²/T₀³`, minimum at `ss`/−40 °C/3.63 V.

### Per-ring liveness

A stuck or dead ring is invisible at `xo`: it contributes a constant, the XOR
still toggles, and the bit stream still looks plausible while the array has
quietly lost half its jitter budget. DR-0007 §Consequences flags this as a
design question this issue inherits, and the schematic answers it by making it
*observable*, in two independent places:

1. **The per-ring supply pin.** A stopped ring's supply current collapses by
   more than four orders of magnitude — from tens of microamps to tens of
   nanoamps (`sim/records/2026-08-01-ro-array-core-power-*.md` against
   `sim/records/2026-08-01-ro-inv-05stage-stopped-leakage-*.md`). Because each
   ring has its own supply node, that collapse is per-ring and unambiguous.
2. **The per-ring output inside the block.** `ro1` and `ro2` are ordinary
   internal nets of `ro_array_core`. A liveness monitor can divide each of them
   down and check for toggling without either becoming an exposed tap —
   DR-0001 constrains what the block *publishes*, not what it monitors
   internally.

Designing the monitor is deliberately **not** in this directory: it is digital
logic, it belongs with the health tests, and it is deferred to #44.
What this issue owed was that the mechanism exists and is not foreclosed by the
schematic. With N = 2 the stakes are higher than DR-0007 anticipated — one dead
ring is half the array — which is stated in `DR-0010` §Consequences.

### Metastability-hybrid tap

The survey (§Recommendation 2) and DR-0007 §1 keep the metastability hybrid as a
*stretch* item — a secondary tap layered on this RO core, never a free-standing
source. Originally deferred out of #7 for the reason #7 itself named as its
first deferral candidate — the core plus its superseding decision record was
already the whole of that deliverable, and a half-argued second tap would have
been worse than none — it is built by #43 as `ro_meta_tap`
(`design/xschem/ro_meta_tap.sch`), instantiated alongside the unmodified core
in `ro_array_core_meta.sch`. Nothing on `main` instantiates
`ro_array_core_meta` by default; the shipped `ro_array_core` is untouched.

**[`DR-0011`](../spec/decision-records/DR-0011-metastability-hybrid-tap-claims-and-scope.md)**
states what is and is not claimed for it, addressing the survey's B.2
(ngspice-substantiability) and B.4 (PVT/mismatch balance-point drift)
objections head-on rather than assuming them away:

- **Claimed, measured**: the tap does not perturb the core (period, per-ring
  current, ring power and ring swing move under 0.03 % at three PVT corners
  with the tap present; `xo_swing_v` moves −0.07 % to −0.13 %, the one real
  residual coupling path, through the combining gate's own load).
- **Claimed, with a stated limit**: the survey's own "directly substantiable"
  method (Kinniment/Chester regeneration-time-constant characterization) does
  not converge to a single `tau` on this solver — it bounds the arbiter's
  regeneration behavior to roughly 3–300 fs and fails in a physically
  explicable way outside that range, which is new information, not a design
  parameter.
- **Claimed, measured**: the tap's trim-to-skew sensitivity drifts up to 1.45×
  across the three PVT corners tested — a direct, quantified answer to the
  survey's concern that a one-time trim cannot be assumed to hold.
- **Claimed, measured, and NOT counted against the ratified `< 500 µW` row**
  (which is measured against `ro_array_core` alone): the tap costs ~187 µW at
  the power-binding corner — adopting it as shipped would put the combined
  total 1.21× over that row, unresolved by this record.
- **Not claimed, at any point**: entropy, a resolution-time histogram, or that
  any calibration scheme could hold the tap's balance point over PVT and
  mismatch. Evidence: `sim/tb/ro-array-core-meta-power/`,
  `sim/tb/meta-arb-regeneration/`, `sim/tb/ro-meta-tap-skew/`, each at
  `ff`/−40 °C/3.63 V, `ss`/−40 °C/3.63 V and `tt`/27 °C/3.30 V — see
  `sim/records/2026-08-01-{ro-array-core-meta-power,meta-arb-regeneration,ro-meta-tap-skew}-{01,02,03}.md`.

## The sampler (#9)

`xo` is not a chip output. The raw tap DR-0001 requires is the **sampler's**
output, and that is what `sampler_core` produces: `ro_array_core` plus two
`sampler_dff` instances, one registering `xo` into `raw_bit` and one
registering a constant `1` into `raw_valid` (a one-cycle reset-release
indicator sharing the same clock and cell as the data path, rather than a
second bespoke circuit). The port shape — `clk` / `rst_n` / `raw_bit` /
`raw_valid` — matches [`design/conditioner/README.md`](conditioner/README.md)'s
already-fixed input contract exactly.

### `sampler_dff`: why a transmission-gate master-slave DFF

The sampling flip-flop's own metastability behavior is part of the entropy
story, not just a hazard to be designed around — the original issue is
explicit about this. A static, fully-complementary transmission-gate
master-slave DFF (the standard "TGFF" topology: two opposite-phase TG
latches, each closed by a *second* inverter feeding its hold loop rather
than a single inverter looped directly through a TG — the one-inverter form
is not bistable, it settles at a metastable half-rail voltage by
construction, not merely under adversarial timing) was chosen for the same
reason `xor2` is fully static and complementary rather than pass-transistor:
the node that decides the raw bit must not have its drive strength depend on
its own data, and its resolution behavior must be characterizable rather
than assumed. Reset is async and reset-dominant, because a sampler that can
power up in an undefined state is not a sampler with a defined raw tap.

### Reset is gated into the storage loops, not forced onto the storage nodes

**How reset works in the shipped cell.** Exactly one inverter in each latch's
hold loop is a 2-input NAND2 whose second input is `rst_n`:

- **master**, the *forward* inverter `m → mb` (`Mimpa`/`Mimpb`/`Mimna`/`Mimnb`);
- **slave**, the *feedback* inverter `q → qb` (`Mis2pa`/`Mis2pb`/`Mis2na`/`Mis2nb`).

A PMOS gated by `rst_n` is ON exactly when reset is asserted, so neither NAND2
needs an active-high copy of `rst_n` and the cell contains no local reset
inverter. While `rst_n` is low both NAND2s are forced HIGH, so `mb = 1` and
`qb = 1` — and those are the *only* two signals that can drive the slave's
storage node `s` (`mb` through `TG_S` while `clk = 1`, `qb` through `TG_FBS`
while `clk = 0`). They agree, so `s = 1` and `Q = 0` in either clock phase and
across every clock edge, and the master's node `m` is pulled to 0 through the
master's own feedback path (`mb = 1 → INVM2 → mc = 0 → TG_FBM`) on every
`clk = 1` phase. **No reset device shares a node with a transmission gate**,
which is the whole point: there is nothing left for the transparent input path
to fight. Device count is unchanged at 22 — four devices added (two per NAND2)
against four removed (the two old storage-node pull devices and the local
`rst_n` inverter that fed one of them).

**What that replaced, and why.** The cell previously reset by brute force:
oversized pull devices directly on both storage nodes, active regardless of
clock phase. That works, but while `rst_n` is low **and** `clk` is low the
master's input transmission gate is transparent, so whatever drives `D` has a
conducting path through that gate into the reset pull-down.
[#48](https://github.com/2AMLogic/gf180-trng/issues/48) measured that path, at
both instances `sampler_core` actually contains and across the full 45-point
PVT grid (`sim/records/2026-08-01-sampler-dff-reset-current-{xsv,xsb}-{01..45}.md`):

| Instance (**pre-#53 cell**) | Nominal (`tt`/27 °C/3.30 V) | Binding corner (`ff`/−40 °C/3.63 V) | Grid minimum (`ss`/125 °C/2.97 V) |
|---|---|---|---|
| `xsv` (`D` tied to `vdd`: continuous conduction) | 195 µA / 644 µW | 314 µA / 1.141 mW | 110 µA / 326 µW |
| `xsb` (`D` = `xo`, ≈50 % duty) | 97.7 µA / 322 µW | 157 µA / 570 µW | 55.2 µA / 164 µW |
| **Both instances simultaneously** (the real `sampler_core` reset window) | **967 µW** | **1.71 mW** | — |

A single instance's reset-window current alone exceeded the entire `< 500 µW`
active-power row at every PVT point measured, and both `sampler_core` instances
share `rst_n` and assert together — 1.9–3.4× the whole block's active-power
budget for as long as reset was held with `clk` low, on top of the entropy
source's own 415 µW. That is what [#53](https://github.com/2AMLogic/gf180-trng/issues/53)
removed, and why the fix is a schematic change rather than a sizing tweak. The
decision, its rejected alternatives and its evidence are
[`DR-0014`](../spec/decision-records/DR-0014-sampler-reset-gated-into-the-storage-loops.md).

**The same two testbenches, unchanged, against the shipped cell**
(`sim/records/2026-08-02-sampler-dff-reset-current-{xsv,xsb}-{01..45}.md` — the
decks were deliberately not touched, so this is the same measurement on two
cells rather than a comparison of methods):

| Instance (**shipped cell**) | Nominal (`tt`/27 °C/3.30 V) | #48's binding corner (`ff`/−40 °C/3.63 V) | Grid maximum |
|---|---|---|---|
| `xsv` (`D` tied to `vdd`) | 50.5 pA / 167 pW | 54.0 pA / 196 pW | 5.09 nA / 18.5 nW (`ff`/125 °C/3.63 V) |
| `xsb` (`D` = `xo`, ≈50 % duty) | 20.1 nA / 66.2 nW | 17.3 nA / 63.0 nW | 29.2 nA / 106 nW (`ss`/125 °C/3.63 V) |
| **Both instances simultaneously** | **66.3 nW** | **63.2 nW** | **119 nW** (`ff`/125 °C/3.63 V) |

That is a factor of **≈14,600 at nominal** (967 µW → 66.3 nW) and **≈14,400
between the two grids' worst points** (1.71 mW → 119 nW); at #48's own binding
corner the same-corner ratio is ≈27,000. The reset window's worst-case draw is
now **0.024 % of the `< 500 µW` row** instead of 3.4× it. The residual is not a
contention path at all — with no reset device on a storage node there is no DC
path from `D` to `vss`, and what the `xsv` deck reads at that bias (tens of
picoamps) is ordinary off-device leakage, comparable to
`sim/tb/device-leakage-03v3/` rather than orders of magnitude above it. Reset
still takes: `xsv`'s `Q` stays within 0.68 µV of `vss` at every one of the 45
points, `xsb`'s within 31.8 µV.

**Reset with the clock running, which the DC decks cannot see.** Both
reset-current testbenches hold `clk` at a fixed level, and
`sim/tb/sampler-dff-setup-hold/` releases reset before the clock starts —
neither exercises a `clk` edge while `rst_n` is low. A *gated* reset acts
through the loops, so that case is now a property of which inverter is gated
rather than something a pull device guaranteed outright, and it needs its own
evidence. `sim/tb/sampler-dff-reset-clocked/` supplies it: `rst_n` held low
across three full periods of the running 1 MHz sample clock with `D` tied high
(the worst case — it forces the master to disagree with the reset state at
*every* rising edge — and also literally `xsv`'s condition in the shipped
block), 45-point grid,
`sim/records/2026-08-01-sampler-dff-reset-clocked-{01..45}.md`:

| Quantity | Result over all 45 points |
|---|---|
| Worst excursion of `Q` from its reset value, over the whole reset window | 114 mV (`fs`/125 °C/2.97 V) … 152 mV (`sf`/−40 °C/3.63 V) |
| …as a fraction of the supply | 3.82 % … 4.22 % |
| `mb` held high by the master NAND2 | ≥ 95.2 % of supply at every point |
| `Q` immediately before `rst_n` releases | ≤ 4.03 µV |
| `Q` after the first rising edge following release (`D` = 1) | full rail at every point (within ±3.4 ppm of supply) |

The excursion is capacitive coupling from the clock through the latches'
transmission gates, not a logic-level disturbance: at worst 4.22 % of supply,
it is more than a factor of ten below any logic threshold, and it decays inside
the same clock phase. The last two rows are there so a cell that "passed" by
being broken — stuck low, never capturing — would not pass.

### Clock-source decision (binding, DR-0012): fixed external, not RO-divided

DR-0007 §6 makes this issue's clock-source choice binding: it selects which
corner metric §4 applies, so #13's worst-corner analysis cannot proceed
without it. **`sampler_core.clk` is a fixed external clock — not divided down
from either entropy-source ring.**

Two consequences drive the choice, both argued in full in
[`DR-0012`](../spec/decision-records/DR-0012-sampler-fixed-external-clock.md):

- **Independence.** Deriving the sample clock from one of the two rings that
  also feed the XOR node the sampler digitizes creates exactly the
  deterministic source/sampler relationship the original issue calls out to
  avoid — the sampled ring's own jitter would partially cancel between its
  role as entropy source and its role as timing reference. An external clock
  with no frequency relationship to either ring has no such coupling.
- **Corner-metric resolution.** DR-0007 §4: with a fixed clock the entropy
  metric is `Q ∝ σ₁²/T₀³` (measured minimum at `ss`/−40 °C/3.63 V, ~1.5× worse
  than `ff`); with an RO-divided clock it collapses to `Q ∝ σ₁/T₀`, under
  which `ss` and `ff` are within 4 % — unresolvable at this repository's
  4-seed grid. The fixed-clock choice is the one that leaves #13 a corner to
  find.

The cost is an external clock pin instead of an on-chip divider chain — this
schematic contains no clock-generation circuitry, which is the decision, not
an omission.

### Rate target: DR-0003's ratified `> 1 Mbps`, not DR-0010's proposed `> 500 bps`

Two rate figures are live in this repository at once. [`DR-0003`](../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md)
(`> 1 Mbps` raw, binding at `ss`/−10 %/+125 °C) is the **ratified** README
figure as of this writing. [`DR-0010`](../spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md)
(`> 500 bps`) is **proposed**, not ratified — its own §Status is explicit that
the README edit is deliberately withheld until an operator accepts it. This
issue targets **DR-0003's ratified 1 Mbps**, and does not pre-empt DR-0010's
acceptance.

The fixed-external-clock architecture makes re-targeting later a one-line
change, not a redesign: because `clk` is external and carries no frequency
relationship to either ring, `R_raw = f(clk)` by construction, at every
corner — retargeting 1 Mbps to 500 bps (or anything else) is choosing a
different external clock frequency, and does not touch the clock-source
decision above. The two questions the original issue's curation flagged as
independent (clock source, target rate) stay independent in the schematic:
nothing here assumes 1 Mbps beyond the clock frequency `sim/tb/sampler-dff-setup-hold/`
happens to drive.

One consequence of the fixed-clock choice is worth stating plainly: DR-0003's
"report `R_raw` at the binding corner, sustained" obligation is satisfied
*architecturally* rather than by a long transient-noise run. Because the
sample rate does not depend on ring speed, `R_raw` equals the external clock
frequency at every corner as long as the sampler resolves correctly there —
which is a setup/hold/metastability question, not a rate-measurement one, and
is exactly what `sim/tb/sampler-dff-setup-hold/` is for.

### Setup/hold and metastability, measured

Setup and hold violations at this flip-flop are **not** a fault to be designed
out. `xo` is asynchronous to `clk` by construction — that is the whole point of
DR-0012's clock-source choice — so the data edge lands at an arbitrary phase
relative to the sampling edge, and some samples necessarily arrive inside the
aperture. What the design has to guarantee is not "no violation" but **bounded
resolution**: that a struck edge settles to a rail quickly and never leaves the
raw tap parked at a half-rail level the conditioner would read as noise-shaped
garbage.

`sim/tb/sampler-dff-setup-hold/` measures that over the full 45-point PVT grid
(5 process corners × 3 temperatures × 3 supplies), one record per point. The
shipped gated-reset cell was re-characterized over the same grid by #53
(`sim/records/2026-08-02-sampler-dff-setup-hold-01…45.md`; the pre-#53 cell's
own grid is `2026-08-01-sampler-dff-setup-hold-01…45.md`, and the two are
directly comparable — the testbench did not change):

| Quantity | Result over all 45 points (shipped cell) | Pre-#53 cell |
|---|---|---|
| `clk`→`Q` delay, rising | 71.4 ps (`ff`/−40 °C/3.63 V) … 170.4 ps (`ss`/+125 °C/2.97 V) | 82.3 … 194.3 ps |
| `clk`→`Q` delay, falling | 80.0 ps (`ff`/−40 °C/3.63 V) … 193.0 ps (`ss`/+125 °C/2.97 V) | 81.0 … 203.0 ps |
| `Q` after asynchronous reset | ≤ 0.68 µV at every point | ≤ 0.68 µV |
| Capture at generous margin (4 clean edges) | correct at every point (worst deviation 18 µV) | correct at every point |
| Settling after a **zero-margin** (zero setup *and* zero hold) edge | within 0.37 mV of a rail at +1 ns; within 6.3 µV at +100 ns | 0.33 mV; 6.4 µV |
| Settling after a **59 ps** setup margin | within 5.5 mV of a rail at +1 ns; within 20 µV at +100 ns | 8.1 mV; 10 µV |
| Settling after a **500 ps** setup margin | within 3.1 mV of a rail at +1 ns; within 10 µV at +100 ns | 6.4 mV; 10 µV |

**No point on the grid shows a metastable hang**, on either cell. Every stressed
edge is resolved to within millivolts of a rail one nanosecond later — three
orders of magnitude inside the 1 µs sample period the ratified rate implies —
and to within tens of microvolts by 100 ns. That is the property the raw tap
depends on, and #53's change to the storage loops does not disturb it.

The propagation delays got **faster** — 12–13 % on the rising edge, 1–5 % on
the falling one — which is the expected direction rather than a surprise: #53
deleted an 0.88 µm PMOS from the
slave's storage node `s` and an 0.44 µm NMOS from the master's node `m` (the
two reset pull devices), and the `clk`→`Q` path runs straight through `s`. The
NAND2s that replaced two of the loop inverters sit on `mb` and `qb`, neither of
which is on that path, and their series legs are sized 2× the device they
replace so the loop's own drive is unchanged.

The two marginal edges also **bracket the cell's setup time**, and the bracket
moves with the corner exactly as it should:

| Corner family | Captured data arriving 59 ps before the edge? | Pre-#53 |
|---|---|---|
| `ff` | 7 of 9 points (all of −40 °C and +27 °C, plus +125 °C at 3.63 V) | 6 of 9 |
| `fs` | 4 of 9 (all of −40 °C, plus +27 °C at 3.63 V) | 3 of 9 |
| `tt` | 4 of 9 (all of −40 °C, plus +27 °C at 3.63 V) | 2 of 9 |
| `sf` | 4 of 9 (all of −40 °C, plus +27 °C at 3.63 V) | 2 of 9 |
| `ss` | 1 of 9 (−40 °C, 3.63 V) | 0 of 9 |

Data arriving **500 ps** before the edge is captured at **all 45 points**, and
the zero-margin edge is captured at none of them, on both cells. So the setup
time is under 500 ps everywhere and crosses 59 ps somewhere inside the grid —
fast-and-cold captures at 59 ps, slow-or-hot does not. It crosses at 20 of 45
points on the shipped cell against 13 of 45 before, i.e. the setup time moved
*down* alongside the propagation delay, for the same reason. This is a
bracket, not a measurement: the testbench probes two offsets rather than
sweeping the data-to-clock offset, so it bounds the setup time and does not
resolve it. #26 has the number it needs to budget a clock/data relationship at
the pin; anyone who needs it tighter should sweep the offset.

Note what this does **not** say. A missed capture at 59 ps margin is not an
error at this flip-flop — with an asynchronous source, "captured the previous
value" is a legitimate outcome of an edge that arrived too late, and it is one
of the mechanisms by which ring phase becomes bit value. The number matters for
the *system* (what `clk` may be asked to do relative to other logic), not as a
pass/fail on the sampler.

### The source, digitised end to end

`sim/tb/sampler-array-digitize/` closes the loop: the shipped two-ring array
under transient noise, its XOR node sampled by the shipped `sampler_dff`, ten
raw bits out. It exists to answer whether the sampler produces a clean logic
level from a real analog `xo` swing, and whether `raw_valid` follows the
conditioner's contract. It answers both, at both corners run
(`sim/records/2026-08-01-sampler-array-digitize-03…04.md`, the shipped
gated-reset cell; `…-01…02.md` are the same two corners on the pre-#53 cell):

| | `tt` / 27 °C / 3.30 V (`…-03`) | `ss` / −40 °C / 3.63 V (`…-04`) |
|---|---|---|
| Ten raw bits (`b0`…`b9`) | `0001111100` | `1111010011` |
| Worst distance from a rail, any bit | 18 nV | 6.3 µV |
| `raw_bit` / `raw_valid` during reset | 92 nV / 18 nV | 38 µV / 18 nV |
| `raw_valid` at first and last sample | high | high |
| Ring frequency ratio | 1.0605 | 1.0597 |
| `xo` swing | 3.394 V | 3.740 V |
| Ring periods accumulated per sample | 1.404 | 1.629 |

- Every bit sits within **20 µV of a rail at worst** — the sampler is not
  handing the conditioner a half-resolved level at either corner.
- The `ss` bitstream is bit-identical to the pre-#53 cell's (`…-02`); the `tt`
  one differs in `b1` (`0101111100` → `0001111100`). That is expected and is
  not a functional change: at this deck's 10 ns clock the bitstream is a
  deterministic function of the ring phases at the sampling instants (see
  below), and #53 moved the sampler's input-node parasitics slightly, so a
  sample taken near a `xo` transition can land on the other side of it. Both
  corners' ring frequencies, swing and periods-per-sample are unchanged to
  within 0.1 %.
- `raw_bit` and `raw_valid` are both low through reset, and `raw_valid` is
  high from the first clock edge after `rst_n` releases and stays high, which
  is exactly what `design/conditioner/README.md` specifies.
- The two rings keep their own frequencies with the sampler's load hung on the
  XOR node, and the ratio stays comfortably non-integer — the schematic-level
  half of the injection-locking argument. At `tt`/27 °C/3.30 V it is 1.0613
  with the sampler attached against 1.0623 for the same array without it
  (`…-ro-array-core-power-06.md`), a 0.1 % shift. Treat that cross-record
  comparison as indicative rather than exact: the two testbenches differ in
  measurement window and in whether noise sources are present, not only in
  sampler load.

**And at both corners the ten bits are identical across all three noise
seeds.** That is not a defect in the run; it is the run telling the truth
about its own clock rate. At `tclk` = 10 ns the sampler accumulates only
1.4–1.6 ring periods of jitter per bit, nowhere near enough for the injected
noise to move a sampling decision — the noise perturbs the sampled analog
levels by microvolts (visible as the seed-to-seed spread on `b2` at `ss`) and
never crosses a decision boundary. The bitstream is therefore a deterministic
function of the ring phases, not of the noise.

That is precisely what makes this a *functional* demonstration and not an
entropy measurement, and it is an independent, bit-level illustration of the
argument [`DR-0010`](../spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md)
makes from the jitter-energy law: a raw rate anywhere near this one buys no
entropy at all. Sampling slowly enough to accumulate usable jitter is the
whole of DR-0010's case, and this is what that case looks like from the
bitstream end. It is evidence *about the sampler*, and deliberately not
evidence about how much entropy a raw bit carries.

## The sanity vehicle

`ro_array_sanity` is a separately-supplied, XOR-combined array built from
`ro_ring5` at `lstv = 2 µm`, with the ring outputs brought out as pins. It
deviates from the shipped cell in two ways, both to make a transient-noise run
finish: **five stages instead of eleven**, which also matches
`sim/tb/ro-inv-05stage-jitter/` so the per-ring figures are comparable to the
ratified characterization stage for stage; and **four rings instead of two**,
which is a strictly stronger independence test than the shipped array needs —
mutual injection locking is easier to provoke among four neighbours than two,
so a negative result here covers the shipped case.

What the first run
(`sim/records/2026-08-01-ro-array-sanity-jitter-01.md`, `tt`/27 °C/3.30 V,
3 seeds) establishes:

- **No injection locking.** The four rings hold four distinct periods —
  3.305 / 3.105 / 2.876 / 2.678 ns, i.e. frequency ratios 1.064 / 1.149 / 1.234
  — reproduced to within 0.0 % of the mean across three independent noise seeds,
  and matching the `wstv` skew they were designed with. Four rings simulated
  together on separate supplies do not pull into lock.
- **The XOR node is alive and rail-to-rail**: 3.52 V swing on a 3.30 V supply,
  at 2.69 × 10⁹ transitions per second, driven by rings whose own swing is only
  2.64 V.
- **What it does *not* establish is jitter.** The `sigma_r1_*` figures in that
  record vary by **0.3 %** across three independent noise seeds. Genuine jitter
  estimated from a 16-period window would vary by order 20 % seed to seed — as
  the ratified per-ring records do (4.8 % on `sigma_1` from a 128-period
  window). A seed-independent "jitter" is not jitter: it is a deterministic
  drift of the period across a measurement window that opens too early and is
  far too short for a ring this slow. The accumulation exponent says the same
  thing — `sigma` grows as roughly lag^0.81 rather than the lag^0.5 of a random
  walk.

  That is a real finding and it is the reason the array's `Q_array` in DR-0010
  is derived from the jitter-energy law and the deterministic power grid rather
  than from this record. It also sets a concrete requirement for **#46**, which
  owns re-running this measurement properly: the window must open well after
  start-up and span orders of magnitude more periods than 16. (#46 rather than
  #12 — #12 is blocked on the conditioner, the sampler and the methodology
  issue, because its scope is min-entropy on *bitstreams*; what is needed here
  is `σ_acc(t)` on a ring node, which needs none of them.)

## Reading the recorded currents

`sim/tb/ro-array-core-power/` and `sim/tb/ro-array-sanity-jitter/` integrate
each supply branch with an ideal current-mirror-and-capacitor pair
(`fq`/`cq`/`rq`), the same construction `sim/tb/ro-inv-05stage-power/` uses. The
sense sources in these two testbenches are oriented so that `v(q)` accumulates
the charge *delivered into* the branch, which makes the recorded `i_*_a`,
`p_*_w` and `e_cycle_*_j` values **negative**. The magnitudes are the physical
ones; `sim/tools/array_sizing.py` takes absolute values, and every figure quoted
from those records in `design/` and `spec/` is a magnitude. The opposite sign
convention in `sim/tb/ro-inv-05stage-power/`'s records is noted here rather than
corrected there, because `sim/records/` is append-only.

### Erratum: a stale caveat in the first records of these testbenches

Eight records minted while this block was being built carry a caveat line that
was already false when it was written:

> Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists
> yet for this block, so testbench.path and netlist.path are the same
> self-contained demo fragment.

The records are `2026-08-01-ro-array-core-power-{01,02,03}.md`,
`2026-08-01-ro-array-sanity-jitter-01.md` and
`2026-08-01-rostage-noise-{01..04}.md`. Their own frontmatter refutes the
sentence two lines above it: `netlist.path` is `design/ro_array_core.spice` or
`design/ro_array_sanity.spice`, not the testbench fragment. The cause was
ordering — those runs were made before `sim/harness/cli.py` learned that a
testbench with a `design_netlist` needs the *other* caveat.

Nothing is corrected in place: `sim/records/` is append-only, and a record that
is silently edited after the fact is worth less than a record with a known,
documented error. The three things that close this out instead:

1. `sim/harness/cli.py` now emits the correct caveat whenever a testbench
   declares a `design_netlist`, so no future record repeats it — visible in
   `2026-08-01-ro-array-core-power-{04,05,06}.md`, which carry the right text.
2. The frontmatter of the affected records is correct and is what tooling reads;
   only the prose caveat is wrong.
3. This note is the erratum, in the one place that is not append-only.

### Erratum: the sampler records' `netlist.sha` / `testbench.sha` predate a rebase

The 47 sampler records (`2026-08-01-sampler-dff-setup-hold-{01..45}.md` and
`2026-08-01-sampler-array-digitize-{01,02}.md`) were run before this work was
rebased onto the metastability-tap change ([#47](https://github.com/2AMLogic/gf180-trng/pull/47)).
Two of the files they pin by SHA changed during that rebase, so their
`netlist.sha` and `testbench.sha` name blobs that are not the ones now
committed:

- `design/sampler_core.spice` — regenerated by `design/netlist.py`, because #47
  moved continuation-line wrapping from xschem into the exporter. The **token
  stream is unchanged**; only wrap points and inter-token whitespace moved. That
  is the same property `sim/tests/test_netlist_export.py` asserts for the
  netlists #47 itself reformatted, and it is checkable by joining `+`
  continuations and normalising whitespace on both files.
- `sim/tb/sampler-{dff-setup-hold,array-digitize}/tb_sampler_*.sp` — a comment
  line each, renumbering the sampler decision record from `DR-0011` to `DR-0012`
  after #47 landed a different `DR-0011` first (see below). No `.control` block,
  no source, no measurement, no device statement changed.

Nothing is corrected in place, for the same reason as the erratum above:
`sim/records/` is append-only, and a SHA silently updated after the fact records
nothing. The recorded SHAs remain the honest statement of what was simulated;
this note is the mapping from them to what is committed. Neither edit can change
a simulation result, and neither was made to make one pass.

## Simulation vehicles for these cells

| Testbench | What it measures |
|---|---|
| [`sim/tb/rostage-noise/`](../sim/tb/rostage-noise/) | `ro_stage` device-noise density, gain and bias point at its trip point |
| [`sim/tb/ro-array-core-power/`](../sim/tb/ro-array-core-power/) | the shipped array: per-ring period and supply current, XOR-tree current, ring and XOR-node swing |
| [`sim/tb/ro-array-sanity-jitter/`](../sim/tb/ro-array-sanity-jitter/) | the five-stage array under transient noise: per-ring period and jitter accumulation, frequency independence, XOR-node swing |
| [`sim/tb/ro-array-core-meta-power/`](../sim/tb/ro-array-core-meta-power/) | the shipped array with the metastability tap attached, measurement-for-measurement identical to `ro-array-core-power/`, plus the tap's own supply current on `vddm` |
| [`sim/tb/meta-arb-regeneration/`](../sim/tb/meta-arb-regeneration/) | the tap's arbiter (`meta_arb`): regeneration time constant via the Kinniment/Chester decade-pair method |
| [`sim/tb/ro-meta-tap-skew/`](../sim/tb/ro-meta-tap-skew/) | the tap (`ro_meta_tap`): trim-load-to-skew sensitivity and its own supply energy per event |
| [`sim/tb/sampler-array-digitize/`](../sim/tb/sampler-array-digitize/) | `sampler_core` end to end: `xo` under transient noise, sampled by the real `sampler_dff` into `raw_bit`/`raw_valid` — a functional raw-bitstream demonstration, not a rate or entropy measurement |
| [`sim/tb/sampler-dff-setup-hold/`](../sim/tb/sampler-dff-setup-hold/) | `sampler_dff` alone, at the real 1 Mbps target clock period, across the full PVT grid: correct capture at normal setup margin and at a clock-aligned (worst-case) data transition |
| [`sim/tb/sampler-dff-reset-current-xsv/`](../sim/tb/sampler-dff-reset-current-xsv/) | `sampler_dff`'s `xsv` instance (`D` tied to `vdd`), biased at `clk=0`/`rst_n=0`: static reset-window supply current, full PVT grid — the contention path #48 measured on the pre-#53 cell, and its absence on the shipped one (#53) |
| [`sim/tb/sampler-dff-reset-current-xsb/`](../sim/tb/sampler-dff-reset-current-xsb/) | `sampler_dff`'s `xsb` instance (`D` an ideal representative square wave standing in for `xo`), `clk=0`/`rst_n=0` held: duty-cycled reset-window supply current, full PVT grid — same before/after pair as `…-xsv/` |
| [`sim/tb/sampler-dff-reset-clocked/`](../sim/tb/sampler-dff-reset-clocked/) | `sampler_dff` with `rst_n` held low across three periods of the *running* sample clock: how far `Q` and the slave storage node depart from the reset state at a `clk` edge, and that the cell captures normally once reset releases — the case the two DC reset-current decks cannot see (#53) |

Testbenches that instantiate a cell from here set `design_netlist` in their
`tb.json`; the harness then `.include`s the schematic-derived netlist and records
*its* path and SHA in the record's `netlist.path` / `netlist.sha` fields, rather
than pointing those fields back at the testbench fragment (which is what a
bootstrap testbench with no `design/` DUT has to do).
