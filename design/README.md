# `design/` — schematics and their exported netlists

This directory holds the block's xschem schematics (`design/xschem/`) and the
SPICE netlists exported from them (`design/*.spice`). The netlists are
**generated files under version control**: they are committed so that every
evidence record under `sim/records/` can name a `netlist.path` /`netlist.sha`
that a reader can actually fetch, and they are regenerated — never hand-edited
— by `design/netlist.py`.

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
uses, absolute paths rewritten to repo-relative).

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

Exported netlists: `design/ro_array_core.spice`, `design/ro_array_sanity.spice`.

---

## The entropy source, and why it is shaped like this

The topology is not a free choice: [`DR-0007`](../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)
§1 makes it binding — N independent, separately-supplied, free-running rings at
deliberately non-integer frequency ratios, XOR-combined into the single node one
sampler observes. What this issue owned was the *sizing*: the delay cell, the
stage count, N, and the operating point. The reasoning is in
[`DR-0008`](../spec/decision-records/DR-0008-raw-rate-moves-to-the-measured-jitter-energy-limit.md);
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

### `ro_ring11`: eleven stages, and why not three

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

A ring that does not reach the rails hands the XOR tree, and through it the
sampler, an analog level. That is a different and worse problem than a slow
ring, and it is not a trade this design makes for a factor in `E_cycle`.

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

N = 2 is the floor of what DR-0007 §1 means by an array. `DR-0008` says so
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
DR-0007's own `M = 1.5` — at the 500 bps raw rate `DR-0008` proposes. The tool
evaluates the inequality from the committed per-ring period and supply-current
records via the jitter-energy law, refuses to use records of a different array
size than the one in `design/`, and exits non-zero if the inequality fails.

### The raw tap is not in this directory

`xo` is the noise source's output, not the block's raw tap. DR-0001 puts the raw
tap at the **sampler** output, after digitisation, and no per-ring signal leaves
`ro_array_core` at all — which is why `ro_array_sanity`, and not
`ro_array_core`, is the cell with `ro*` observation pins. The sampler and its
clock are #9's, and #9's choice of clock source selects which corner metric
DR-0007 §4 applies; nothing here assumes one.

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
logic, it belongs with the health tests, and it is deferred to its own issue.
What this issue owed was that the mechanism exists and is not foreclosed by the
schematic. With N = 2 the stakes are higher than DR-0007 anticipated — one dead
ring is half the array — which is stated in `DR-0008` §Consequences.

### Metastability-hybrid tap

The survey (§Recommendation 2) and DR-0007 §1 keep the metastability hybrid as a
*stretch* item — a secondary tap layered on this RO core, never a free-standing
source. It is not in these schematics. It is deferred to its own issue, for the
reason #7 itself names as its first deferral candidate: the core plus its
superseding decision record is already the whole of this deliverable, and a
half-argued second tap would be worse than none.

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

  That is a real finding and it is the reason the array's `Q_array` in DR-0008
  is derived from the jitter-energy law and the deterministic power grid rather
  than from this record. It also sets a concrete requirement for #12: the
  measurement window must open well after start-up and span orders of magnitude
  more periods than 16.

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

## Simulation vehicles for these cells

| Testbench | What it measures |
|---|---|
| [`sim/tb/rostage-noise/`](../sim/tb/rostage-noise/) | `ro_stage` device-noise density, gain and bias point at its trip point |
| [`sim/tb/ro-array-core-power/`](../sim/tb/ro-array-core-power/) | the shipped array: per-ring period and supply current, XOR-tree current, ring and XOR-node swing |
| [`sim/tb/ro-array-sanity-jitter/`](../sim/tb/ro-array-sanity-jitter/) | the five-stage array under transient noise: per-ring period and jitter accumulation, frequency independence, XOR-node swing |

Testbenches that instantiate a cell from here set `design_netlist` in their
`tb.json`; the harness then `.include`s the schematic-derived netlist and records
*its* path and SHA in the record's `netlist.path` / `netlist.sha` fields, rather
than pointing those fields back at the testbench fragment (which is what a
bootstrap testbench with no `design/` DUT has to do).
