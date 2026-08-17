# Entropy-source isolation: the floorplan and why it is shaped like this

This is the written isolation rationale for the RO-array entropy source
(issue #16), plus the floorplan abstract that carries it and the area rollup
that prices it.

**The premise, from the issue that asked for it:** deterministic coupling can
masquerade as entropy. A bitstream that is correlated with a neighbour's clock
or with a supply tone can pass every statistical battery and still be a
security failure, because a battery measures whether the stream *looks*
random, not whether an adversary can *predict* it. So the floorplan is
derived from a threat model rather than from a placement convenience, and
every mitigation below names the specific mechanism it addresses — and, more
importantly, the mechanisms it does **not** address.

There are three distinct coupling mechanisms in this block. Two of them are
what the layout literature means by "isolate the oscillator", and the
floorplan addresses them. **The third one is not a layout problem at all**, is
measured at 28.6× in this repository, and survives every mitigation the first
two get. Getting that distinction wrong is how an array that is correlated by
construction ends up documented as independent.

The circuit-level mitigation for that third mechanism — one buffer per ring
ahead of the combiner — has been **measured** ([#75]) and **adopted**
([#78]): it removes 92.8 % of the coupling and *returns* power rather than
costing it, and a 2.87× residual survives.

---

## The one command

```sh
python3 layout/floorplan/floorplan.py            # build, check, print the rollup
python3 layout/floorplan/floorplan.py --write    # ... and refresh the artefacts
python3 layout/floorplan/floorplan.py --list     # print the region table
```

It expands the *committed* netlists into a per-region cell inventory, prices
each region against the PDK's own standard-cell LEF and against measured
device footprints, generates a guard ring per region, composes them into one
stream with a declared isolation channel between neighbours, runs DRC on the
result, and compares everything against the committed artefacts under
[`reports/`](reports/). It prints `PASS` and exits 0 only if the composed
abstract is DRC-clean **and** the committed artefacts still match.

Like `layout/verify.py` it **skips with exit 0** when `klt` or the PDK is
absent, and `--require-tools` turns that skip into a failure. A skip is not a
pass.

Every number quoted below is produced by that script and lands in
[`reports/area.json`](reports/area.json); nothing here is a figure somebody
typed in.

---

## What is being isolated, and from what

The shipped block, per [`design/README.md`](../../design/README.md):

| | |
|---|---|
| Entropy source | `ro_array_core` — two eleven-stage current-starved rings (`ro_ring11`, `wstv` = 0.220 / 0.240 µm) on their own supply pins `vddr1` / `vddr2`, combined by one `xor2` |
| Sampler | `sampler_core` — four `sampler_dff`: `xsb` (raw bit), `xsv` (`raw_valid`), `xsr1`/`xsr2` (the DR-0016 per-ring liveness digitizers), all on the DR-0012 **fixed external** sample clock |
| Digital | conditioner (#8), health tests (#11), interface (#26) — 1655 standard cells, 658 flip-flops, all synchronous to that same external clock |

Two facts about that list drive the whole floorplan.

**The rings are the only thing in the block that is supposed to be
unpredictable.** Everything else — the sample clock, the conditioner's LFSR,
the health-test counters, the FIFO pointers — is deterministic by design and
switches in patterns an observer can predict or, in the clock's case,
*choose*.

**The sample clock is an external pin** ([DR-0012]). It is not derived from a
ring and it is not generated on die, which is the right decision for
independence — and it also means the block's largest, most regular switching
aggressor is under the control of whoever drives that pin. A disturbance
injected into a ring at the sample clock's own rate is the worst possible
disturbance, because it is *coherent with the sampling instant*: it does not
average away over many samples the way an incommensurate ring-to-ring beat
does. Keeping `clk` away from the ring nodes is therefore not general good
practice here; it is the specific consequence of DR-0012's choice.

---

## The regions

Four guarded regions, placed in this order, with a **20 µm isolation channel**
between neighbours:

| region | contents | own supply | role |
|---|---|---|---|
| `ring1` | `ro_ring11` (1 × `ro_nand2` + 10 × `ro_stage`), `wstv` = 0.220 µm | `vddr1` | entropy |
| `ring2` | `ro_ring11`, `wstv` = 0.240 µm | `vddr2` | entropy |
| `combiner_sampler` | `xor2` + 2 × `ro_buf` ([DR-0018][DR-0018]) + 4 × `sampler_dff` | `vdd` | boundary — carries `clk` |
| `digital` | conditioner + health tests + interface | `vddd` | deterministic aggressor |

The ordering is the argument: the **only** region that touches both the
entropy nodes and the sample clock is `combiner_sampler`, and it sits between
the rings and the digital section rather than beside them. Nothing in the
digital section is adjacent to a ring, and `clk` reaches the samplers from the
digital side without crossing either ring's guarded area.

Each region is enclosed by a p-substrate tap guard ring, 1.0 µm thick with tap
contacts every 2 µm, tied to that region's own `vss` return. The rings are
generated by `klt gen guard_ring` and are real geometry, not a drawing: they
are in the composed stream and they are what DRC checks.

The 20 µm channel is a **routing-derived floor, not a coupling-derived one**.
It is what each supply domain needs to reach its own region without sharing a
channel with another domain's straps, and it keeps neighbouring tap rings 20 µm
apart. **No substrate-coupling attenuation is claimed for it** — see
[What this floorplan does not establish](#what-this-floorplan-does-not-establish).

---

## Mechanism 1 — mutual injection locking between the rings

**What it is.** Two nominally identical oscillators that share a substrate, a
supply or a magnetic neighbourhood pull each other toward a rational frequency
ratio. When they lock, [DR-0007] §2's sum over independent rings collapses: the
array degenerates toward one ring's worth of jitter while the bitstream still
looks plausible. This is the failure mode [DR-0007] §6 names, and the one the
architecture survey's §A.4 injection-locking argument is about.

**What addresses it here.**

1. **Deliberately non-integer frequency ratios**, already in the schematic:
   the two rings differ only in starve-device width (0.220 vs 0.240 µm) and
   measure a frequency ratio of **1.057** at `ff`/−40 °C/3.63 V and **1.062**
   at `ss`/−40 °C/3.63 V (`sim/records/2026-08-01-ro-array-core-power-*.md`),
   holding at **1.060** with the sampler's load attached
   (`…-sampler-array-digitize-03/04.md`). No small-integer factorisation, at
   any measured corner. This is [DR-0007] §1's requirement, and it is a
   *schematic* property the layout must not undo.
2. **Per-ring supply routing**, also already in the schematic: `vddr1` and
   `vddr2` are separate pins on `ro_array_core`, so the two rings have no
   shared series supply impedance inside the block. The floorplan's job is to
   keep them separate all the way to the star point (below), rather than
   merging them at the first convenient strap.
3. **Physical separation and per-ring guard rings**: each ring sits inside its
   own tap ring, with a 20 µm channel between them.

**The layout decision that is easy to get backwards.** Standard analog layout
practice for a matched pair is common-centroid interdigitation with dummies —
`klt gen`'s own `diff_pair` and `mos_array` generators default to
`topology: "common_centroid"` for exactly that reason. **That practice is
actively wrong here.** The two rings are not a matched pair; they are
deliberately *mismatched*, and the mismatch is load-bearing — it is the entire
mechanism producing the non-integer frequency ratio above. Interdigitating
them would (a) pull their frequencies together, shrinking the very ratio that
mitigation 1 depends on, and (b) put each ring's devices immediately adjacent
to the other's, which is the arrangement injection locking wants. So:

> **The two rings are laid out as two separate, unmatched, individually
> guarded blocks. No common-centroid pairing, no interdigitation, no shared
> dummy row, no shared well.** Any future generator-driven layout of these
> cells must be given `topology: "array"`, not the default.

**Evidence that locking is not already happening at the schematic level.** The
four-ring sanity vehicle holds four distinct periods (3.305 / 3.105 / 2.876 /
2.678 ns) reproduced to within 0.0 % of the mean across three independent noise
seeds (`sim/records/2026-08-01-ro-array-sanity-jitter-01.md`), and in the
two-ring coupling study ring 2 free-runs at an unrelated frequency with ring 1's
mean period moving 0.16 %
([`sim/characterization-array-ring-coupling.md`](../../sim/characterization-array-ring-coupling.md)).
Those are pre-layout, ideal-supply results: they show the *schematic* does not
lock, and they are silent about a built array. Extraction adds coupling paths;
it removes none.

---

## Mechanism 2 — supply and substrate coupling

**What it is.** Every switching gate dumps a current transient into the supply
network and a displacement current into the substrate. Shared series impedance
turns those into voltage steps on a neighbour's rail; substrate injection turns
them into body-bias modulation. A ring's frequency is a direct function of both,
so a deterministic switching pattern anywhere in the block becomes a
deterministic phase modulation on every ring that shares a rail or a substrate
neighbourhood with it. The digital section is the loud one: 658 flops all
clocked by the same external `clk`.

**What addresses it here.**

1. **Star routing from a single point.** Four supply domains — `vddr1`,
   `vddr2`, `vdd` (combiner + samplers), `vddd` (digital) — each a separate
   branch from one star point at the block's supply pad, with **no shared
   series impedance between the entropy branches and the digital branch**. The
   schematic already provides the separate pins for the first three; the
   floorplan's contribution is the requirement that they stay separate to the
   pad, and that the digital domain never shares a strap segment with an
   entropy domain.

   As of [#171](https://github.com/2AMLogic/gf180-trng/issues/171) the
   digital section has a real PDN of its own
   ([`layout/digital/README.md`](../digital/README.md#power)), and it is
   built to this requirement rather than merely alongside it: its grid is on
   nets `vddd`/`vss`, it terminates at the block's own `vddd`/`vss` pins, and
   `layout/digital/build.py`'s `_power_isolation_check` reads the routed
   DEF's own `SPECIALNETS` section on every run and fails if it carries
   anything other than those two — in particular if it carries `vddr1`,
   `vddr2` or `vdd`. That is the layout-side half of this requirement,
   checked and committed (`checks.power_isolation` in
   `layout/digital/reports/place_and_route.json`). The other half — that the
   four branches stay separate *to the pad* — is still this floorplan's, and
   still unbuilt: the `digital` region below is empty, and nothing in this
   repository yet draws the star point.
2. **Per-domain guard rings**, tied to each region's own `vss` return. In a
   p-substrate process a p+ tap ring is a majority-carrier collector: it is the
   standard structure for keeping injected substrate current from reaching a
   sensitive device, and it is what the abstract draws (`add_well: false` — an
   n-well tie is a different structure for a different job).
3. **The digital section is not adjacent to a ring.** Its boundary is with
   `combiner_sampler`, across a 20 µm channel and two tap rings.
4. **Supply filtering is named as required and not yet designed.** On-die
   decoupling for the entropy domains is the obvious next structure. This
   floorplan reserves the channel it would sit in but does **not** size it —
   sizing needs a supply-network impedance target, and there is no measurement
   in this repository that sets one (see below).

**What is claimed, precisely.** That the *topology* removes shared series
supply impedance between the deterministic and entropy domains, and that each
region has a majority-carrier guard structure. **Not** that substrate coupling
is attenuated by any particular factor, and **not** that 20 µm is sufficient
separation — those are quantitative claims and this repository has no substrate
network model, no extracted parasitics and no supply-network testbench to
support them. The coupling study's own caveat says the same thing from the
other side: every deck in it supplies the rings from an **ideal** `vsup` with
no impedance for one ring's current to develop a voltage across, so its
measured coupling factor is a **lower bound** on a built array's, not an upper
one.

---

## Mechanism 3 — coupling through the XOR combiner, which is not a layout problem

This is the one that matters most, and the one the original acceptance
criteria did not cover.

**What was measured.** At `tt`/27 °C/3.30 V, over a 512-period window opened
256 periods after start-up, four variants that differ from a standalone-ring
control in exactly one thing each
([`sim/characterization-array-ring-coupling.md`](../../sim/characterization-array-ring-coupling.md),
issue #51 / PR #67):

| variant | differs by | `σ₁` | vs control |
|---|---|---|---|
| `ro-array-coupling-xor-static` | `xa1` present, second input on a rail | 0.676 ps | 1.06× |
| `ro-array-coupling-xor-driven` | `xa1` driven by ring 2 | 18.32 ps | **28.6×** |
| `ro-array-coupling-rings-only` | two rings, electrically unconnected | 0.642 ps | 1.00× |

The static combiner load is innocent. Two rings solved on the same adaptive
timestep with no wire between them are innocent to three digits. **Electrical
attachment through the combiner is the mechanism**, and its signature is a
deterministic beat at `|f₁ − f₂|`: `σ_acc` *collapses* 8.6× at the lag that
equals the beat period, which no accumulating jitter process can do.

**Why it is a different mechanism from injection locking, and why every
mitigation above misses it.**

- **The rings are not frequency-locked.** Ring 1's mean period moves 0.16 %
  between the switching-neighbour and quiet-neighbour cases; ring 2 free-runs
  at an unrelated frequency. Nothing is pulled to a rational ratio.
- **It survives arbitrary frequency separation.** The disturbance is a beat at
  `|f₁ − f₂|`, so the beat rate *is* the frequency separation. Skewing the
  rings further apart moves the tone; it does not remove it. Mitigation 1 does
  not apply.
- **It survives arbitrary physical separation.** The coupling path is charge
  injected into node `ro1` through the gate-drain / gate-source capacitance of
  `xa1`'s input stage — a **shared electrical node by construction**, not a
  layout adjacency. Put the two rings on opposite corners of the die and the
  wire from each to the combiner still exists, because the combiner is what
  the architecture is. Mitigations 2 and 3 do not apply.
- **The error is in the unsafe direction.** [DR-0007] §2 sums
  `σ²_acc,i / T₀,i²`. Locking makes that sum *collapse*; this makes it *inflate*
  — by the square of the coupling factor, ~820× at this corner — while every
  recorded number still says the array passes. And the excess carries no
  entropy: it is a fixed function of ring 2's phase, which the XOR already
  carries into the output. Counting it inside ring 1's `σ_acc` double-counts a
  quantity that is, from ring 1's point of view, not random at all.

**Therefore, stated once, plainly:**

> XOR-combiner coupling is a **distinct mechanism** from injection locking. It
> is **not mitigated by floorplan separation, by guard rings, by per-ring
> supply routing, or by frequency-ratio skew** — the combiner input stage is a
> shared electrical node by construction. An independence argument that cites
> only the [DR-0007] §6 mitigations is incomplete, and incomplete in the
> direction that overstates the array.

### The same topology exists a second time — and it was measured ([#76])

The measurement above indicts a specific arrangement: *a ring node driving the
input gate of a cell whose internal nodes something else is driving*. The block
contained that arrangement twice more, and the floorplan work is where it
surfaced:

- `xsr1` / `xsr2`, the DR-0016 per-ring liveness digitizers (#71), put each
  ring node `ro1` / `ro2` on a `sampler_dff` input — a transmission gate whose
  other terminal is the master latch node, and whose gate is driven by **`clk`**.
- `xsb` does the same on `xo` with the same clock.

This section previously said that nothing measured what those digitizers cost
the rings in **phase**, and filed it as [#76]. [#76] measured it, in
[`sim/characterization-liveness-tap-phase-cost.md`](../../sim/characterization-liveness-tap-phase-cost.md),
at `tt`/27 °C/3.30 V through #51's own window geometry. **The concern stated
here was correct, and the effect is larger than the one this document was
written about:**

| | `σ₁` against its own static reference | ring-period swing across the run |
|---|---|---|
| digitizer's `d` on the **ring node**, `clk` running (what shipped up to [#82]) | **541×** | **23.11 %** |
| digitizer's `d` on the **buffer output**, `clk` running (what ships now) | **19.9×** | **0.96 %** |

The mechanism is not the one the coupling section describes, and it is
simpler: the `sampler_dff` master transmission gate conducts while `clk` is
low, so the ring node drives the master latch's input inverter through a full
transition every ring cycle in one clock phase and sees only junction and
overlap capacitance in the other. The ring therefore runs at **two different
frequencies, 25.6 % apart** (2.7472 ns and 3.4507 ns on the 5-stage reference
ring), and a running `clk` switches it between them — block for block, at
exactly those two periods, with a repeat period equal to the clk period. Across
four independent noise seeds the resulting `σ₁` reproduces to 0.01 % where a
genuine estimate scatters 2.69 %, and it accumulates as `L^0.95` rather than a
random walk's `L^0.5`. It is deterministic, and unlike a ring-to-ring beat it is
coherent with the sampling instant by construction.

**The buffer this document proposed and [#78]/[DR-0018] adopted removes 96.5 %
of it** — a fraction close to the 92.8 % it removes on the combiner path, from
decks that share nothing with those but the cell. So the mitigation adopted for
one mechanism turns out to address the other as well. It does not remove it:
19.9× is far outside the 1.00×–1.08× band a quiet ring occupies, and the
residual is as deterministic as the thing it is a residual of. What reaches the
ring through a buffer is the `clk`-dependent load on the buffer's *output*,
changing the buffer's output slew, fed back through the buffer's own gate-drain
capacitance to its input.

**What this adds to the isolation rationale**, stated once and plainly:

> A `clk`-driven cell tapping a ring node is a **third** coupling mechanism,
> distinct from injection locking and from XOR-combiner coupling. Like combiner
> coupling it is **not mitigated by floorplan separation, guard rings, per-ring
> supply routing, or frequency-ratio skew** — the digitizer's input stage is a
> shared electrical node by construction. Unlike combiner coupling, its
> aggressor is an **external pin** ([DR-0012]), so its rate is not a design
> constant, and its disturbance is phase-locked to the sampling instant rather
> than incommensurate with it. The per-ring buffer attenuates it by ~30×; no
> floorplan measure attenuates it at all.

Nothing here proposes a further design change: what should be done about the
remaining 19.9×, if anything, is not decided by that document or this one.

### Adopted mitigation: one buffer per ring, ahead of everything

**The mitigation, adopted ([#78]).** One minimum-width inverter on each ring
output, between the ring node and *every* consumer — the combiner input and
that ring's liveness digitizer both drive off the buffer's output, not off
the ring node. [`DR-0018`](../../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md)
records the decision; `design/xschem/ro_array_core.sch` and the new
`design/xschem/ro_buf.sch`/`.sym` are where it lands.

Inverting one or both XOR inputs does not change the entropy at the combined
node (`a ⊕ b` and `¬a ⊕ b` differ by a constant inversion), so a single
inverter is sufficient; no non-inverting pair is needed.

**Why it should help, structurally.** The coupling path is charge injected
*backwards* through the consumer's input-stage capacitance into whatever node
drives it. With a buffer, that node is the buffer's output — a low-impedance,
actively-driven node — instead of the ring's own high-impedance oscillating
node. What reaches the ring is then attenuated by the buffer's reverse
isolation rather than landing on the ring directly.

A second, purely structural effect is visible in the netlist and needs no
simulation to state: `xa1`'s `a` input presents **1.98 µm of total gate width**
to `ro1` (`XMpiA` 0.44 + `XMniA` 0.22 + `XMp1` 0.88 + `XMn1` 0.44), while an
inverter buffer's input presents **0.66 µm**. Buffering therefore takes load
*off* the ring node as well as isolating it.

**What it costs — MEASURED, [#75].** This section previously carried an
estimate and a refusal to adopt on the grounds that nothing measured it.
[#75] measured it, in
[`sim/characterization-ring-buffer-mitigation.md`](../../sim/characterization-ring-buffer-mitigation.md).
The estimate is kept below because being wrong in an interesting way is worth
recording, not because it is still the number:

| | What was **estimated** here | What was **measured** ([#75]) |
|---|---|---|
| Area | 2 × `inv_1` = **17.6 µm²** cell, ~29 µm² placed at 60 % — **0.06 % of the < 0.05 mm² row** | not re-measured; this is a LEF area, not a simulation |
| Buffer power | **≈ 24.4 µW** at `ff`/−40 °C/3.63 V, from `P = C_eff · V² · f` with `c_eff_node_r1` = 3.865 fF | **61.8 µW** — 2.5× the estimate. `c_eff_node_r1` averages a ring stage driving the *next* ring stage's 0.66 µm; the buffer drives `xa1`'s full 1.98 µm |
| Ring power | offset from the 3× load reduction deliberately **not** priced | per-cycle energy −5.0 %, average power **+1.4 %** — the ring spends the saving on running 6.7 % faster |
| Combiner power | not considered | **−85.6 µW (−58.8 %)**. The buffer's un-starved output gives `xa1` fast edges where the starved ring gave it slow ones |
| **Block active rollup** | 454.2 µW (90.8 %) → **≈ 478.6 µW, 95.7 %** of the `< 500 µW` row | 454.2 µW (90.8 %) → **435.1 µW, 87.0 %** |

The estimate had the **sign** wrong, not just the magnitude: the mitigation
does not spend half the remaining headroom, it *returns* 19.1 µW of it. The
term the estimate omitted — what happens inside the combiner once it is driven
by fast edges — is larger than the two terms it included.

**What it buys, measured at `tt`/27 °C/3.30 V.** With a matched
quiet-neighbour control at the *same* buffered operating point
(`sim/tb/ro-array-coupling-xor-static-buffered/`, so the comparison spans one
change and not two), the coupling factor falls from **27.10× to 2.87×** —
**92.8 % of the excess removed**. It is **not** removed entirely, and the
residual is still deterministic (1.1 % seed spread against the ~2.7 % a real
jitter estimate scatters, accumulation exponent 0.141 against the control's
0.421, and a still-non-monotonic `σ_acc`). Squared, 2.87× is an **8.24×**
over-statement of one ring's contribution to `Q_array`, still in the unsafe
direction.

**The decision this document now records:**

> **The measurement rule below is unchanged and remains adopted** — an 8.24×
> residual is not a licence to measure per-ring `σ_acc,i` with the neighbours
> switching, and the buffer does not relax it. **The buffer is adopted**
> ([#78], [`DR-0018`](../../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md)):
> it removes 92.8 % of the coupling, costs 0.06 % of the area row, and
> *returns* headroom to the power row. Adoption was not a floorplan edit — it
> edited `design/xschem/ro_array_core.sch`, added `design/xschem/ro_buf.sch`,
> and obsoleted every shipped-array record's operating point (+6.7 %
> frequency, −4.9 % power), so it went through a decision record and a re-run
> of the `ro-array-core-power`, `ro-array-core-pvt-q` and
> `ro-array-core-startup` families. Against those re-run records the block's
> active rollup at the binding corner (`ff`/−40 °C/3.63 V) is **433.2 µW,
> 86.6 % of the `< 500 µW` row**, down from the pre-adoption 454.2 µW
> (90.8 %) — close to, and slightly better than, the 435.1 µW the
> testbench-only measurement projected.

The edge case the issue asks about is worth stating explicitly: **the buffers
must be per-ring, never shared.** A single buffer stage feeding both combiner
inputs would create exactly the shared node the mitigation exists to remove.

---

## The measurement rule (adopted)

> **Per-ring `σ_acc,i` offered as evidence for [DR-0007] §2 must be measured
> with that ring's combiner neighbours quiet** — the `ro-array-coupling-xor-static`
> arrangement, gate load present and neighbour held on a rail — **or with the
> deterministic component separated out and reported alongside.** A per-ring
> `σ` taken from a deck in which the neighbours switch is not admissible for
> §2.

**`sim/records/2026-08-01-ro-array-sanity-jitter-01.md`'s `σ_r1_*` figures do
not meet this bar.** They were taken with the combiner neighbours switching,
they are 28.6× inflated by a deterministic beat at the corner where that factor
is measured, and they must not be cited for independence or for sizing. That
record keeps `status: valid` and gets no `superseded_by` — per
[`sim/README.md`](../../sim/README.md), superseding it means re-running the
testbench, which is #46's work and not this issue's. This is a statement about
**admissibility**, not about the record's honesty.

**Nothing in the repository's current §2 path violates the rule**, and that is
checkable rather than asserted: `sim/tools/array_sizing.py` evaluates
`Q_array` from the *deterministic* per-ring period and supply-current records
(`ro-array-core-power`, `ro-array-core-pvt-q`) through the jitter-energy law,
and prints the sanity-jitter record's `κ²` only as a **reported, not enforced**
comparison. The rule therefore binds future evidence, and #12 inherits it: the
empirical independence check DR-0007 §6 assigns to #12 must target this path
specifically — cross-correlation of per-ring crossing residuals against the
neighbour's phase, not a frequency-ratio or locking check, which this mechanism
passes.

---

## Area against the `< 0.05 mm²` row

From `python3 layout/floorplan/floorplan.py` — full breakdown in
[`reports/area.json`](reports/area.json):

| region | cells | cell area | placed @ 60 % | guarded footprint |
|---|---:|---:|---:|---:|
| Entropy ring 1 | 11 | 164.4 µm² | 274.0 µm² | 546.1 µm² |
| Entropy ring 2 | 11 | 164.4 µm² | 274.0 µm² | 546.1 µm² |
| XOR combiner + 2 buffers + 4 samplers | 7 | 342.4 µm² | 570.8 µm² | 4 955.1 µm² |
| Conditioner + health tests + interface | 1655 | 74 485.3 µm² | 124 142.2 µm² | 125 556.8 µm² |
| **total** | | **75 156.6 µm²** | **125 261.0 µm²** | **131 604.2 µm²** |

The two [`DR-0018`][DR-0018] output buffers (`xb1`/`xb2`) joined this table in
issue [#144]. They are inventoried in `combiner_sampler` rather than in the
ring each one buffers, because DR-0018 runs both off the block supply `vdd` —
deliberately, so that neither ring's own `vddr1`/`vddr2` branch carries the
buffer's switching current. Priced at one `inv_1` each they add **17.6 µm²** of
cell area (**29.3 µm²** placed at 60 %, i.e. **0.06 %** of the `< 0.05 mm²`
row — the figure DR-0018 itself projected). No **guarded footprint** moves:
`combiner_sampler`'s is measured from the assembled row's own bbox, not from
this estimate, so every share-of-row figure below is unchanged. That is also
the caveat: the assembled row does not contain the buffers, so this region is
budgeted for them and not yet drawn with them ([#151]) — `reports/area.json`
records it per region under
`footprint_source.inventoried_but_not_in_assembly`.

`ring1`/`ring2`/`combiner_sampler`'s own `cell area`/`placed @ 60 %` columns
above are still the area/utilisation estimate (unchanged in method by this
section); only their **guarded footprint** is sized differently, and only for
those three rows (`ring1`/`ring2` since issue #119, `combiner_sampler` since
issue #135) — see [What the area model is](#what-the-area-model-is) below.

Isolation channels (20 µm × the taller neighbour): 135.0 + 352.8 + 7 086.8 =
**7 574.6 µm²** — the `ring2`|`combiner_sampler` channel *shrank* from
505.4 to 352.8 µm² even though `combiner_sampler`'s own region grew hugely,
because the channel is charged at 20 µm × the taller neighbour's height and
the real assembled row (15.64 µm tall, 17.64 µm guarded) is *shorter* than
the area-estimate square it replaced (23.27 µm tall, 25.27 µm guarded) —
`combiner_sampler`'s footprint got much wider and somewhat shorter, not
uniformly bigger.

| | area | share of the `< 0.05 mm²` row |
|---|---:|---:|
| **Entropy source + samplers + all isolation structures** | **6 535.2 µm²** | **13.07 %** |
| Digital section | 125 556.8 µm² | 251.1 % |
| **Floorplan total** | **139 178.8 µm²** = 0.13918 mm² | **278.4 %** |

Two findings, and they point in opposite directions.

**Isolation is cheap, but no longer negligible.** The entire isolated entropy
source — both rings, the combiner, all four samplers, four guard rings and
every isolation channel between them — is **13.1 % of the area row**. The
guard rings and channels cost ≈**5 445.7 µm²** of that, i.e. **≈10.9 % of the
row for the whole isolation structure** — both figures are up sharply from
the pre-#135 estimate (4.74 %, 2.56 %) because `combiner_sampler`'s guarded
footprint is now sized from its real assembled row (278.90 × 15.64 µm)
instead of the compact area/utilisation-estimate square it previously used
(23.27 × 23.27 µm), the same kind of resize issue #119 already did for
`ring1`/`ring2` — see [What the area model is](#what-the-area-model-is) and
issue #135. Nothing in `combiner_sampler`'s own cell content changed; only
how its region is sized did. This is a much bigger proportional jump than
issue #119's own ring resize (~+1 percentage point) because
`combiner_sampler`'s row is long and thin (278.9 µm) rather than a shorter
elongated ring geometry. In absolute terms it remains small next to the
budget miss below: the digital section alone is already 125 556.8 µm²
(251.1 % of the row, tracked separately by DR-0019), and this resize's own
+4 163.9 µm² floorplan-total increase is only ~5.5 % of the digital
section's own overage (125 556.8 − 50 000 µm² = 75 556.8 µm² over the
row). Nothing in this document's mitigations is
area-constrained, and the buffer mitigation this document proposed and
[DR-0018][DR-0018] adopted costs the 0.06 % it was projected to — now
counted in the table above rather than pending (issue [#144]).
*The isolation argument does not have to trade against the area budget, and
it should not be allowed to — but it is no longer a rounding error either.*

**The digital section misses the area row on standard-cell area alone** —
74 485 µm², i.e. **1.49× the whole row before any placement at all**, and
2.5× once placed at 60 % utilisation. (Real synthesis and placement have since
put that figure at **113 088 µm², 2.26× the row on cell area alone** — see
[The digital region has since been synthesized, placed and
measured](#the-digital-region-has-since-been-synthesized-placed-and-measured)
below. The estimate is left as written; the miss is larger, not smaller.) The two 8 × 32-bit output FIFOs are
**69.8 %** of it (512 `dffrnq_1` + 448 `mux2_1` + 16 `icgtp_1` =
51 982 µm²). This is the
same structure, in the same block, that [DR-0017] identifies as the reason the
`< 1 µA` idle row misses by 4.5× — one design decision showing up on two
different rows. **No row is edited here, and no design change is made here**:
this issue owns the entropy source's isolation, not the interface's FIFO depth.
The number is recorded so the conflict is visible rather than discovered later,
exactly as [DR-0010] §Consequences recorded the power collision.

The miss itself is now routed by **[DR-0019]** (`Proposed`, from #96), the way
the idle-current miss is routed by [DR-0017]: it states the row's status against
this estimate, prices the available responses (reduce the FIFO depth, raise the
row, hold the row, or split it), and carries the depth sensitivity — 269.4 % at
depth 8, 129.4 % at depth 2, 105.8 % at depth 1 and 88.5 % with both FIFOs gone,
all at this floorplan's own 60 % utilisation *as it stood when DR-0019 was
written*, before issue #119's and issue #135's own region resizes above (the
floorplan total is now **278.4 %**, not 269.4 %, entirely from `ring1`/
`ring2`'s (#119) and `combiner_sampler`'s (#135) guarded-footprint changes —
the digital section DR-0019's own table turns on is untouched by either).
Re-deriving DR-0019's depth-sensitivity table against the new total is
that record's own follow-up, not repeated here. Its finding on the shared root
cause is that the same lever reaches the two rows very differently: [DR-0017]
rejected a depth reduction because it never gets the idle current under 1 µA at
any depth, whereas on area it is most of an answer. Until that record is
ratified the `< 0.05 mm²` row stands as written.

### The digital region has since been synthesized, placed and measured

**The `digital` row above is superseded as a prediction, and kept as one.**
Issues [#143] and [#111] synthesized and placed-and-routed that region for
real, and [#145] measured what came out (`sim/characterization-digital-sta-area-power.md`,
records `sim/records/2026-08-17-digital-sta-power-*`):

| | cell area | cells | library |
|---|---:|---:|---|
| This table's estimate | 74 485.3 µm² | 1655 inventoried | `mcu7t5v0` (7-track) |
| Measured, placed ([#111]) | **113 087.9 µm²** | 2499 placed instances | `mcu9t5v0` (9-track) |
| | **×1.518** | ×1.510 | |

Pricing the *same as-built netlist* against the 7-track library separates the
two axes that moved at once: **×1.209 from cell count and mix** (real
synthesis needs 51 % more instances, averaging 36.04 µm² rather than the
inventory's assumed 45.01 µm²) and **×1.256 from 9-track rather than 7-track
rows**. The inventory got the block's shape right and its cell count wrong,
which is the error a bottom-up count from RTL `reg` declarations is structurally
exposed to.

Nothing in this document is edited to match. The numbers here remain what this
script produces and what [DR-0019] was written against; the measured figure is
larger, is recorded where it was measured, and is what any future re-derivation
of DR-0019's depth-sensitivity table should use. This section exists so that a
reader of the table above cannot mistake a pre-synthesis estimate for the
current state of knowledge.

The other three regions are unaffected: they are analog cells with no
synthesis path, drawn by hand, and `ring1`/`ring2`/`combiner_sampler` already
take their guarded footprints from committed assembled geometry rather than
from this estimate.

### What the area model is

A **bottom-up inventory estimate with a stated method**, not a synthesis result
and not a layout. No synthesiser, placer or router has been run on **the analog
cells** in this block, and none of them has been drawn from this model; the
digital region *has* been synthesized and placed since this model was written
(see the section above), and this model's own digital row is retained as the
pre-synthesis prediction it was.

- Gate-shaped cells (`ro_stage`'s core inverter, `ro_nand2`, `xor2`,
  `sampler_dff`) are priced at their nearest `gf180mcu_fd_sc_mcu7t5v0`
  equivalent's LEF area — the same method, and the same library, that
  [DR-0008]'s conditioner figure uses. That library is 7-track and uses wider
  devices than these hand-drawn minimum-width cells, so it **over-estimates**
  the analog side: the conservative direction.
- The series starve devices (`L` = 2 µm) have no standard-cell analogue and are
  priced at a real generated footprint from `klt gen mos_array`, DRC-checked in
  the same run (2.386 µm² n, 3.580 µm² p — up from 1.193/2.261 µm² in an
  earlier run of this script against an older `klt` build; this generator's
  own output is not pinned to a `klt` version, see
  [klayout-tools#623][kt623]). They are generated at `W` = 0.42 µm rather than
  their drawn 0.220 / 0.240 µm because the generator will not go narrower (see
  [Tool friction](#tool-friction)), which over-estimates them too.
- The digital side reuses the cell inventories
  `design/digital_power_estimate.py` already maintains — one copy of that list
  in the repository, already guarded by `sim/tests/test_power_rollups.py`.
- Placement utilisation is reported at both 60 % and 80 %, per [DR-0008]'s
  convention; the floorplan geometry is built at 60 %.
- **`ring1`/`ring2`/`combiner_sampler`'s guarded footprint is not from this
  model.** Every other region's guarded footprint is sized from this
  section's own sqrt(cell_area / utilisation) square, same as always —
  `ring1`/`ring2` (issue #119) and `combiner_sampler` (issue #135) are the
  exceptions: once each had committed, DRC-clean, LVS-matching assembled
  geometry, its real bounding box (read from the committed GDS via
  `klt stats`) replaced the square estimate for that region only.
    - `ring1`/`ring2`: `layout/rings/ro_ring11/` (#110/#120) and
      `layout/rings/ro_ring11_ring2/` (#118), real bbox **78.9 × 4.75 µm**
      each — the estimate would have given 16.55 × 16.55 µm each, a
      footprint the real row does not remotely fit inside.
    - `combiner_sampler`: `layout/blocks/combiner_sampler/` (#134), real
      bbox **278.90 × 15.64 µm** — the estimate would have given
      23.27 × 23.27 µm, roughly 11× narrower than the real assembled row.

  (See `region.footprint_source` in [`reports/area.json`](reports/area.json)
  for the exact numbers and which regions use which method.) Each region's
  *guarded* (outer) footprint is still sized from that same real bbox
  (**80.9 × 6.75 µm** guarded for each ring, **280.9 × 17.64 µm** guarded for
  `combiner_sampler`, `GUARD_RING_WIDTH_UM` = 1.0 µm in on every side) —
  issue #110's own placement clearance (below), extended to `combiner_sampler`
  by issue #135, only changes how that 1.0 µm is split between guard-ring
  material and clear silicon, not the region's own outer size, so
  `region.inner_w_um`/`inner_h_um` in `reports/area.json` now read
  **79.71 × 5.55 µm** (each ring) / **279.70 × 16.44 µm**
  (`combiner_sampler`) — real bbox **+ 2 ×** `RING_PLACEMENT_CLEARANCE_UM` —
  while `guarded_w_um`/`guarded_h_um` are unchanged by that split. `digital`
  still uses the square estimate and always will (no synthesis/placement
  step is in scope to replace it).
- `layout/floorplan/floorplan.py` also checks that the real assembled
  geometry actually *fits* inside the region it now sizes: it composes each
  such region's guard ring with the real assembled GDS and runs `klt drc`
  **and** `klt lvs` over the pair, comparing the DRC result against that
  GDS's own standalone DRC so a violation introduced by the fit is
  distinguishable from one already present in the assembled geometry on its
  own. All three regions (`ring1`, `ring2`, `combiner_sampler`) fit
  DRC-clean-relative-to-baseline and LVS-match today — see
  [`reports/ring_fit.json`](reports/ring_fit.json),
  [Placement](#placement--issue-110) below for why this is no longer a
  *zero*-clearance fit and what changed, and
  [Placement — issue #135](#placement--issue-135-combiner_sampler) for
  `combiner_sampler`'s own placement. (This regeneration's own standalone DRC
  for all three is clean — 0 violations — not the 49-per-ring pre-existing
  count issue #110 recorded: see [Tool friction](#tool-friction) for why
  that count is gone.)
- The composed abstract's row bounding box is **857.1 × 354.3 µm** (up from
  601.4 × 354.3 µm before issue #135's `combiner_sampler` resize — almost
  entirely the width of `combiner_sampler`'s own now much wider region).
  That is the
  tool's one-dimensional arrangement, not a packing proposal — the composer
  supports row placement only. The area figures above are region footprints
  plus channels, which do not depend on that arrangement.

One term is deliberately **excluded**: the DR-0016 ring-liveness monitor
(85 cells, 2 849.4 µm²) is shipped RTL as of #71, but
`design/digital_power_estimate.BLOCKS` still carries it as `shipped=False`. The
script reports exactly what that inventory declares and prices the monitor
separately rather than silently including or dropping it. Reconciling the flag
belongs with whoever owns that inventory.

---

## Placement — issue #110

`layout/rings/` ([#120][gf120], [#118][gf118]) assembled `ro_ring11` at both
sizings; issue #119 sized `ring1`/`ring2`'s guarded regions to those real,
committed bounding boxes instead of an area estimate. **What #119 explicitly
left open is what this section is about: actually placing the assembled ring
inside the region #119 sized for it.**

**The naive placement is a short, not just a stress test.** `ring1`/`ring2`'s
guarded-region inner cavity is sized to *exactly* each ring's own bbox
(#119), so the tightest — and, before this issue, only — placement puts the
ring's own drawn edge flush against the guard ring's inner wall on every
side, zero clearance. `layout/floorplan/floorplan.py`'s own `check_ring_fit`
already exercised exactly that placement as a DRC-only stress test for #119,
and it passed (0 new DRC violations). Extending the same check to `klt lvs`
— this issue's own test-plan requirement — found that DRC-clean is not the
same claim as connectivity-clean: `klt extract`'s own `merged_net_labels`
diagnostic reports the ring's own metal1 chain-signal wiring (which runs
right up to the row's own bbox edge — `layout/rings/ro_ring11/build.py`'s
`WRAP_TRACK`) shorting to `vss` once the guard ring's own p-substrate tap
diffusion sits flush against it. Two conductors on the same layer with zero
space between them are one net to a polygon-based extractor, guard ring or
not — the curated DRC deck simply has no rule that catches "this spacing is
zero" as a violation in a composed stream the way it would inside a single
generator's own output. `klt gen guard_ring`'s own response already names
the number that would have caught it: `drc_hints.min_spacing_um` is 0.4 µm
for this deck regardless of `ring_width_um` — `gen-compose` does not consult
it, which is filed generically against the tool as
[klayout-tools#692][kt692].

**The fix keeps the region's own committed outer footprint unchanged.**
`RING_PLACEMENT_CLEARANCE_UM` (0.4 µm, cross-checked at run time against
`gen_guard_ring`'s own reported `drc_hints.min_spacing_um` rather than
trusted blind) is carved *out of* the guard ring's own band width, not added
on top of the region's reserved area: the guard ring's inner cavity grows by
`2 × RING_PLACEMENT_CLEARANCE_UM` and its own `ring_width_um` shrinks by
`RING_PLACEMENT_CLEARANCE_UM` on each side, and the two exactly cancel
(`ring_band_width_um + RING_PLACEMENT_CLEARANCE_UM == GUARD_RING_WIDTH_UM`,
always) — `ring1`/`ring2`'s `guarded_w_um`/`guarded_h_um` in
[`reports/area.json`](reports/area.json) are byte-identical to what issue
#119 already committed. Only `inner_w_um`/`inner_h_um` (the cavity) and the
new `ring_band_width_um`/`ring_placement_clearance_um` fields change. At
that clearance, both rings compose DRC-clean-relative-to-baseline (0 new
violations vs. each ring's own standalone DRC) **and** `klt lvs`-match
`RING_LVS_REFERENCE` — the same reference netlist
[`layout/verify.py`](../verify.py) already uses for each ring standalone,
modulo only the same two deck-level disclosures (`device.body_unverified`,
`topology`) every other entry in this repository already carries. Verbatim
results: [`reports/ring_fit.json`](reports/ring_fit.json).

**The composed abstract now places real content, not just guard rings.**
`compose()` uses `placement.strategy: "explicit"` (#330) for every block —
`ring1`/`ring2`/`combiner_sampler`/`digital`'s own guard rings at the same
absolute origins `strategy: "row"` used to compute (so every region and
channel lands exactly where each region's own committed numbers already put
it), plus one more block each for `ring1`/`ring2`: the real assembled
`ro_ring11`/`ro_ring11_ring2` geometry, translated to
`(region's row offset + GUARD_RING_WIDTH_UM − ring bbox x0/y0)` — the same
"flush against the guard ring's own declared inner corner" formula
`check_ring_fit` already verifies clean, since `ring_band_width_um +
RING_PLACEMENT_CLEARANCE_UM == GUARD_RING_WIDTH_UM` makes that absolute
position independent of the clearance/band-width split. Issue #135 gives
`combiner_sampler` the same treatment, its own real assembled
`combiner_sampler.gds` content placed the same way — see
[Placement — issue #135](#placement--issue-135-combiner_sampler) below.
`digital` alone stays an empty guard ring — no digital-section placement is
in scope for either issue.

**No common-centroid pairing, verified, not just avoided by construction.**
`layout/floorplan/README.md`'s own [Mechanism 1](#mechanism-1--mutual-injection-locking-between-the-rings)
requires `ring1`/`ring2` to stay two separate, unmatched, individually
guarded blocks — no shared dummy row, no shared well, no interdigitation.
Nothing in this placement path is capable of doing any of those things:
`klt gen guard_ring` has no `topology` parameter to default away from (that
risk is specific to `klt gen`'s matched-pair generators, `diff_pair`/
`mos_array`, neither of which this placement calls), each ring gets its own
independent `gen_guard_ring` invocation (visible in the composed stream's
own structure names — four distinct `guard_ring`/`guard_ring$1`/
`guard_ring$2`/`guard_ring$3` instances, one per region, never reused across
regions), and each ring's own content is a separate top-level block with its
own row offset, 100.91 µm apart, comfortably outside the 20 µm channel.
Checked, not just argued: `klt extract` over the full composed
`trng_floorplan.gds` reports exactly 92 devices (46 + 46, one ring's own
device count each) and 97 nets, with `merged_net_labels` showing only the
expected within-ring `a,y` chain merges (nine per ring, the same "`y`→`a`"
same-net-label pattern `layout/rings/ro_ring11/build.py`'s own wiring
produces) — no net, and no device, spans both rings' own structures.

---

## Placement — issue #135 (`combiner_sampler`)

`layout/blocks/combiner_sampler/` (issue #134) assembled `xor2` + 4 ×
`sampler_dff` into a single, DRC-clean, LVS-matching row — but, unlike
`ring1`/`ring2`, that row is not two roughly-square rings; it is a single
5-cell row measuring **278.90 × 15.64 µm**, about 11× the width of the
region's prior area/utilisation-estimate square (23.27 × 23.27 µm). The
mismatch is exactly the same shape #119 found for `ring1`/`ring2` — an area
*estimate*, written before any cell existed to place, versus the real
geometry a hand-drawn, row-assembled block actually has once it exists — so
issue #135 resolved it the same way: `combiner_sampler` was added to
`floorplan.py`'s `ASSEMBLED_RING_GDS`/`RING_LVS_REFERENCE` machinery (issue
#110's own generalisation of `check_ring_fit`/`compose` to a non-ring
assembled block, anticipated but not exercised until now), sizing the
region's guarded footprint from `combiner_sampler.gds`'s own real bounding
box instead of the estimate.

**Same clearance mechanism, same result.** `RING_PLACEMENT_CLEARANCE_UM`
(0.4 µm) applies to `combiner_sampler` exactly as it does to `ring1`/`ring2`
— carved out of the guard ring's own band width, not added on top of the
region's reserved outer footprint (**280.90 × 17.64 µm** guarded, real bbox
**+ 2 ×** `GUARD_RING_WIDTH_UM`) — because the same zero-clearance short
issue #110 found for the rings' own metal1 chain wiring is a generic risk of
placing any real geometry flush against a guard ring's p+ tap diffusion, not
something specific to `ro_ring11`'s own layout. At that clearance,
`combiner_sampler` composes DRC-clean-relative-to-baseline (0 new violations
against its own standalone DRC) **and** `klt lvs`-matches
`RING_LVS_REFERENCE`'s `combiner_sampler.spice` reference — the same
reference `layout/verify.py` already uses for this block standalone, modulo
only the same two deck-level disclosures (`device.body_unverified`,
`topology`) every other entry in this repository already carries. Verbatim
result: [`reports/ring_fit.json`](reports/ring_fit.json)'s own
`combiner_sampler` entry (3 mismatches, all in the allowed categories, 100
devices and 54 nets all matched).

**The row reshapes, not just one region's square.** `combiner_sampler` sits
between `ring2` and `digital` in the composed row (see
[The regions](#the-regions) above), so widening it by roughly 255 µm moves
`digital`'s own row offset by the same amount and grows the composed
abstract's own row bounding box from 601.4 × 354.3 µm to
**857.1 × 354.3 µm**. The `ring2`|`combiner_sampler` channel's own area
*shrinks* (505.4 → 352.8 µm²) because the real row is shorter
(15.64 µm) than the estimate square was tall (23.27 µm), even though the
region widened enormously — a channel is priced by height, not width, so a
region that gets wider but shorter can cost *less* channel area even while
its own guarded footprint grows by more than 4 000 µm². See
[Area against the `< 0.05 mm²` row](#area-against-the--005-mm-row) above for
the full before/after area rollup this resize produces.

**What this does not do.** It does not place anything inside the `digital`
region, and it does not change `combiner_sampler`'s own internal
connectivity or cell content (`layout/blocks/combiner_sampler/build.py` is
untouched by this issue) — only where the floorplan reserves space for the
block it already assembled.

---

## DRC: what actually ran

`klt drc` was run — by this script, not by hand — on every generated device
footprint and on the composed floorplan abstract, with the same `gf180mcu` deck
and the same PDK resolver `layout/verify.py` uses. Verbatim output in
[`reports/floorplan.drc.json`](reports/floorplan.drc.json).

**Since issue #110, `ring1`/`ring2` carry their own real, placed content;
since issue #135, so does `combiner_sampler`.** `digital` alone is still
empty *in this composed abstract* — nothing in the digital section is
assembled at all. This regeneration's own composed abstract is fully clean:

```
composed abstract: status "clean", violation_count 0, rule_counts {}
new violations introduced by composing the regions together: 0
```

That is a change from what issue #110's own regeneration recorded here
(`status "violations", violation_count 98`, `rule_counts
{metal1.enclosing.contact.1: 10, via1.width.1: 88}` — exactly twice each
ring's own standalone 49). That 98 was a pre-existing deck-drift gap
([klayout-tools#623][kt623], discussed below) between the `klt` build that
produced `layout/reports/ro_ring11*.drc.json`'s own committed `clean`
verdict and the `klt` build issue #110's own regeneration ran against; this
regeneration's `ring_fit.json` shows `ring1`/`ring2`'s own standalone DRC is
*also* clean now (`reports/ring_fit.json`'s own `ring_standalone` entries),
so whatever `klt` build this run resolved on `PATH` evidently carries the
fix for that drift too — see [Tool friction](#tool-friction) for the detail.
Nothing about `combiner_sampler`'s own placement caused this; it is a
byproduct of re-running the whole flow against a newer `klt` build,
surfaced because this issue's own test plan required a full regeneration.

`floorplan.py`'s own pass/fail signal remains **not** "is the composed
abstract's raw violation count zero", because that is not guaranteed to stay
true as more regions gain real content or as the resolved `klt` build
drifts again — it is "does composing the regions together, and placing each
region's own real content inside its own guard ring, introduce anything
beyond what that region's own committed GDS already reports on its own"
(`reports/floorplan.drc.json`'s own `new_violations_from_composition` key,
and `reports/ring_fit.json`'s own `new_violations_from_fit`, for the same
question asked pairwise per region). Both report 0 — which, this run,
happens to coincide with the raw count also being 0.

**Read the scope off the report, not off this sentence.** The abstract draws
Comp, Contact and Metal1 only, so the deck checked **three layers** and
**skipped sixteen rules** for want of the layers they apply to (all upper
metal, MiM, BJT, poly and n-well). That is in the report's own `coverage`
block.

**What a clean-relative-to-baseline result here does and does not mean:**

- It **does** mean the isolation structures are legal geometry at these
  dimensions: four guard rings with those tap widths and contact pitches, at
  those sizes, with 20 µm between them, violate no rule in the curated deck —
  and that placing `ring1`/`ring2`'s and `combiner_sampler`'s own real
  content inside its own guard ring, at the clearance
  `RING_PLACEMENT_CLEARANCE_UM` establishes (below), introduces no *new*
  rule violation over what that region's own committed GDS already has.
- It does **not** mean the block is DRC-clean, full stop, as a general
  property of this check. `digital` is still an empty guard ring — no
  standard cell in that section has been placed — and a DRC run over a
  floorplan abstract can only check what the floorplan abstract actually
  contains: three layers (below), not the full deck. That this
  particular regeneration's own raw violation count happens to be zero too
  is a fact about this run, not a guarantee `floorplan.py` makes going
  forward.
- It is **not tapeout sign-off**, for all the reasons
  [`layout/README.md`](../README.md) already states: `klt`'s decks are a
  curated subset, not the PDK's own sign-off deck.

The generated streams also cannot be identified to a `klt` build by its own
version string alone (`klt --version` read `0.1.0` for every build through
issue #119 — [klayout-tools#306], closed; this regeneration's own
`klt --version` reads `0.2.0`, and `reports/*.json`'s own
`provenance.klt_version` field confirms it); `layout/reports/
environment.json` records the `klt_origin` commit for the same install this
flow ran on, and every report here carries `klt`'s own `provenance` block
including a content hash of the deck — the content hash, not the version
string, is what this document actually relies on for reproducibility.

---

## What this floorplan does not establish

Stated as a list because an unstated limit is a defect.

1. **No substrate-coupling attenuation figure.** 20 µm and a tap ring are a
   structure, not a number. Quantifying them needs a substrate network model
   and extracted parasitics, neither of which exists here.
2. **No supply-network coupling bound.** Every deck backing the coupling
   measurement uses an *ideal* supply. Real supply-network coupling is a second
   path those decks do not have, and the star topology above addresses it
   structurally without bounding it. `sim/tools/power_rollup.py` prices the
   *current*; nothing prices the *impedance*.
3. **No corner coverage on the coupling factor.** 28.6× is `tt`/27 °C/3.30 V
   only. It is a circuit ratio with no reason to be corner-independent, and the
   sweep belongs to #13/#12.
4. **No removal of the coupling — only 92.8 % of it.** The buffer mitigation
   is measured ([#75]) and adopted ([#78], [`DR-0018`](../../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md)):
   the schematic now ships buffered. What that does *not* establish is
   independence. A **2.87× residual** survives at `tt`/27 °C/3.30 V — an
   8.24× over-statement squared, still in the unsafe direction — so the
   measurement rule below is unchanged, and per-ring `σ_acc,i` taken with the
   neighbours switching stays inadmissible, buffered or not. The residual's
   own corner coverage is item 3's gap, not a separate one.
5. **No measurement of the `clk`-driven liveness-tap path**, as stated above —
   [#76].
6. **No attribution of the residual 1.21×** between one XOR gate with one
   neighbour (19.20 ps) and the full four-ring tree (23.21 ps). That needs a
   re-run of `sim/tb/ro-array-sanity-jitter/`, not a layout decision.
7. **No empirical independence check.** [DR-0007] §6 assigns that to #12, and
   this document only sharpens what it has to target.
8. **No decoupling capacitor sizing** for the entropy domains — the channel is
   reserved, the structure is not designed.
9. **No full layout, still.** `ring1`/`ring2` now carry real, placed,
   DRC/LVS-verified content ([Placement](#placement--issue-110), issue
   #110); `combiner_sampler`'s own contents (`xor2` + 4x `sampler_dff`,
   [#134][gf134]) are now placed too
   ([Placement — issue #135](#placement--issue-135-combiner_sampler)),
   its region resized to the block's own real footprint
   (278.90 × 15.64 µm) rather than the area/utilisation estimate that
   previously did not fit it — the same kind of resize issue #119 did for
   `ring1`/`ring2`, resolved for `combiner_sampler` by [#135][gf135]. Only
   `digital` remains an empty guard ring in this composed abstract — no
   standard cell in the digital section has been placed.

None of these is a reason to withhold the floorplan. All of them are reasons
not to read a clean DRC result as an independence argument.

---

## Tool friction

Per [CLAUDE.md](../../CLAUDE.md), friction found while using klayout-tools is
filed generically against the tool — the tool gap, never this repository's
design. This work produced four, all filed against
[klayout-tools][klt] and all worked around in
[`floorplan.py`](floorplan.py) rather than silently absorbed:

1. **[klayout-tools#320][kt320]** — generated streams are not byte-reproducible.
   `klt gen`, `klt gen-compose` and `klt draw` stamp wall-clock time into the
   GDSII `BGNLIB` / `BGNSTR` records, so two runs of the same generator on the
   same inputs differ in those bytes. A golden-artefact flow cannot diff that.
   `floorplan.py` zeroes those fields on the way in (`normalise_gds`), which is
   the same thing this repository's own writer `layout/testcells/gdsii.py`
   already does for the same reason.
2. **[klayout-tools#321][kt321]** — `klt gen-compose` supported only
   `placement.strategy: "row"` when this was filed. A floorplan is
   two-dimensional by nature and needs explicit per-block x/y placement with
   declared separations; a single row with one `spacing_um` is what this
   abstract's own four regions are still built as (no 2-D grid/auto-packing
   exists yet). `placement.strategy: "explicit"` (a caller-declared `{x, y}`
   origin per block, #321) has since shipped, and issue #119's own ring-fit
   check (see [What the area model is](#what-the-area-model-is)) uses exactly
   that to place a region's real ring geometry inside its guard ring's inner
   cavity — `layout/rings/ro_ring11/build.py` uses the same strategy to
   assemble the ring itself. (Two smaller things noted there have since been
   fixed upstream by [klayout-tools#328][kt328]: `blocks[].generator_report`
   paths now resolve against the request file's own directory rather than the
   working directory — matching `klt lvs`'s convention all along — and an
   unrecognised `pdk` key is now an application error instead of a silent
   fallback to the family default. `floorplan.py` was updated to the new
   `generator_report` resolution rule (gf180-trng#79); note that
   `options.output` is deliberately *not* covered by it and still resolves
   against the process's working directory, per `gen_compose.compose`'s
   docstring, so this flow's compose request keeps that path repo-root
   relative.)
3. **[klayout-tools#322][kt322]** — `klt gen mos_array` rejects `w_um` below
   0.42 µm, which is above the device minimum the tool's *own* curated
   gf180mcu DRC deck enforces (0.22 µm Comp width — this repository's
   `layout/testcells/build.py` draws against exactly that minimum and the deck
   passes it). A minimum-width digital-style device therefore cannot be
   generated at all, so the starve-device footprints here are measured at the
   floor and are over-estimates.
4. **[klayout-tools#692][kt692]** — `klt gen-compose`'s `strategy: "explicit"`
   does not consult a neighbouring `guard_ring` generator's own reported
   `drc_hints.min_spacing_um` at all, so it will happily compose a block
   flush (zero clearance) against a guard ring even though the generator's
   own response already names the minimum spacing that avoids a short. Found
   placing `ring1`/`ring2`'s real assembled content (issue #110,
   [Placement](#placement--issue-110) above): the zero-clearance placement
   `check_ring_fit` already exercised as a DRC-only stress test for issue
   #119 passes `klt drc` clean against the curated deck, and still shorts
   the ring's own signal wiring to `vss` once `klt lvs` is run over the same
   composed pair — `klt extract`'s own `merged_net_labels` names it
   directly. `floorplan.py` works around this by deriving its own placement
   clearance from the generator's `drc_hints.min_spacing_um` and
   cross-checking it at run time (`RING_PLACEMENT_CLEARANCE_UM`) rather than
   trusting a fixed number, but nothing in `gen-compose`'s own contract
   prompts a caller to do so.

Not new friction, but worth recording alongside the above: issue #110's own
regeneration found that `layout/rings/ro_ring11/ro_ring11.gds`'s and
`ro_ring11_ring2.gds`'s own standalone `klt drc` result no longer reproduced
the `clean` verdict committed in `layout/reports/ro_ring11*.drc.json` (#120,
#118) — same input content hash, but a different `provenance.deck.content_hash`
than the one that produced the committed report, because a different `klt`
build resolved on `PATH` when that regeneration ran. That was exactly the gap
[klayout-tools#623][kt623] (closed) already describes: no way to pin or
reproduce a specific historical rule-deck revision once a newer `klt` build
shadows it. **Issue #135's own regeneration (this document's current numbers)
no longer reproduces that drift**: `reports/ring_fit.json`'s own
`ring_standalone` entries for `ring1`/`ring2`/`combiner_sampler` are all
`clean` again, matching the originally-committed verdict, which is consistent
with `#623` genuinely being fixed in whatever `klt` build (`0.2.0`, per this
run's own `klt --version` and `provenance.klt_version`) resolved on `PATH`
this time. Nothing here re-verifies `ro_ring11`'s own DRC status as a
standalone-block concern — that is still a `layout/rings/` question, not a
floorplan-region-sizing one — and this script's own ring-fit check already
separates "violations already present in the assembled GDS alone" from
"violations introduced by fitting it into its region" (0 of the latter for
all three regions this run) precisely so a future recurrence of this drift
would not block that separate question.

[klt]: https://github.com/2AMLogic/klayout-tools
[kt320]: https://github.com/2AMLogic/klayout-tools/issues/320
[kt321]: https://github.com/2AMLogic/klayout-tools/issues/321
[kt322]: https://github.com/2AMLogic/klayout-tools/issues/322
[kt328]: https://github.com/2AMLogic/klayout-tools/issues/328
[kt623]: https://github.com/2AMLogic/klayout-tools/issues/623
[kt692]: https://github.com/2AMLogic/klayout-tools/issues/692
[klayout-tools#306]: https://github.com/2AMLogic/klayout-tools/issues/306

[#75]: https://github.com/2AMLogic/gf180-trng/issues/75
[#76]: https://github.com/2AMLogic/gf180-trng/issues/76
[#78]: https://github.com/2AMLogic/gf180-trng/issues/78
[#82]: https://github.com/2AMLogic/gf180-trng/pull/82
[gf118]: https://github.com/2AMLogic/gf180-trng/issues/118
[gf120]: https://github.com/2AMLogic/gf180-trng/pull/120
[gf134]: https://github.com/2AMLogic/gf180-trng/issues/134
[gf135]: https://github.com/2AMLogic/gf180-trng/issues/135
[#144]: https://github.com/2AMLogic/gf180-trng/issues/144
[#151]: https://github.com/2AMLogic/gf180-trng/issues/151

[DR-0007]: ../../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md
[DR-0008]: ../../spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md
[DR-0010]: ../../spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0012]: ../../spec/decision-records/DR-0012-sampler-fixed-external-clock.md
[DR-0017]: ../../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
[DR-0018]: ../../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md
[DR-0019]: ../../spec/decision-records/DR-0019-area-row-versus-output-fifo-dominated-digital-section.md
[#111]: https://github.com/2AMLogic/gf180-trng/issues/111
[#143]: https://github.com/2AMLogic/gf180-trng/issues/143
[#145]: https://github.com/2AMLogic/gf180-trng/issues/145
