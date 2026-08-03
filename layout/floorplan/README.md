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
| `combiner_sampler` | `xor2` + 4 × `sampler_dff` | `vdd` | boundary — carries `clk` |
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

### The same topology exists a second time — measured, and it is the larger of the two ([#76])

The measurement above indicts a specific arrangement: *a ring node driving the
input gate of a cell whose internal nodes something else is driving*. The
shipped block contains that arrangement twice more, and the floorplan work is
where it surfaced:

- `xsr1` / `xsr2`, the DR-0016 per-ring liveness digitizers (#71), put each
  ring node `ro1` / `ro2` on a `sampler_dff` input — a transmission gate whose
  other terminal is the master latch node, and whose gate is driven by **`clk`**.
- `xsb` does the same on `xo` with the same clock.

`sim/tb/ring-liveness-tap-power/` measured what those digitizers cost the rings
in **power** at three PVT points, and DR-0016 §Power/area cost prices it. This
section previously recorded that **nothing measured what they cost the rings in
phase**, and filed that gap as [#76] rather than assuming it away.

**[#76] measured it, and the concern was justified**
([`sim/characterization-ring-liveness-tap-phase.md`](../../sim/characterization-ring-liveness-tap-phase.md),
six new testbenches at `tt`/27 °C/3.30 V):

| digitizer tapping | `σ₁` vs a matched quiet control | period modulation | seed spread | exponent |
|---|---|---|---|---|
| the raw ring node (as shipped #65 → [#82]) | **545.7×** | **703.51 ps** (25 % of the period) | 0.01 % | 0.953 |
| a `ro_buf` output (as shipped today, [DR-0018]) | **20.08×** | **27.46 ps** | 0.17 % | 0.971 |

The mechanism is not #51's. A `sampler_dff` `d` input is one terminal of a
transmission gate, so a running `clk` does not inject a rare impulse into the
ring — it **modulates the ring's load between two values at the clock rate**,
and the modulating waveform *is* `clk`. The proof is a prediction rather than a
correlation: the two static operating points (gate shut, gate open), measured
in decks whose clock never moves, predict the clocked deck's `σ₁` to **1.004×**
unbuffered and **1.000×** buffered.

The per-ring buffer this section goes on to adopt removes **96.5 %** of it —
the same buffer, measured on a second consumer — but the residual **20.08×** is
seven times #75's residual on the combiner path (2.87×), and **403×** rather
than 8.24× once squared into [DR-0007] §2's sum. **The buffer is not a fix for
this path**, and the sign of the residual says why: buffered, the modulation
reaches the ring *backwards* through the buffer's own gate-drain capacitance
rather than forwards through its input, so more isolation is what would help,
not a bigger buffer.

Two questions #76 raised and did not settle are filed rather than asserted:
whether the `clk`-locked modulation biases the **sampled bit** ([#86] — a
phase measurement may not make a bit-level claim), and what the **shipped
array's** own residual is, given that its buffer output also drives `xa1`
([#87], which also covers the unmeasured `xsb`-on-`xo` path).

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
> arrangement, gate load present and neighbour held on a rail — **and with the
> sample clock quiet** — the `ring-liveness-tap-phase-shut`/`-open`
> arrangement, digitizer present and `clk` held on a rail — **or with the
> deterministic component separated out and reported alongside.** A per-ring
> `σ` taken from a deck in which the neighbours switch, *or* in which `clk`
> switches, is not admissible for §2.

The `clk` half of that rule is [#76]'s addition and is the larger of the two
terms: 545.7× on an unbuffered digitizer tap and 20.08× on the buffered tap the
block ships, against 27.10× / 2.87× for the combiner path. Both halves are
about a *shared electrical node*, not a layout adjacency, and neither is
mitigated by separation.

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
empirical independence check DR-0007 §6 assigns to #12 must target **both**
paths specifically — cross-correlation of per-ring crossing residuals against
the neighbour's phase *and* against the sample clock — not a frequency-ratio or
locking check, which both mechanisms pass.

---

## Area against the `< 0.05 mm²` row

From `python3 layout/floorplan/floorplan.py` — full breakdown in
[`reports/area.json`](reports/area.json):

| region | cells | cell area | placed @ 60 % | guarded footprint |
|---|---:|---:|---:|---:|
| Entropy ring 1 | 11 | 136.8 µm² | 228.0 µm² | 292.4 µm² |
| Entropy ring 2 | 11 | 136.8 µm² | 228.0 µm² | 292.4 µm² |
| XOR combiner + 4 samplers | 5 | 324.9 µm² | 541.5 µm² | 638.6 µm² |
| Conditioner + health tests + interface | 1655 | 74 485.3 µm² | 124 142.2 µm² | 125 556.8 µm² |
| **total** | | **75 083.8 µm²** | **125 139.6 µm²** | **126 780.2 µm²** |

Isolation channels (20 µm × the taller neighbour): 342.0 + 505.4 + 7 086.8 =
**7 934.2 µm²**.

| | area | share of the `< 0.05 mm²` row |
|---|---:|---:|
| **Entropy source + samplers + all isolation structures** | **2 070.8 µm²** | **4.14 %** |
| Digital section | 125 556.8 µm² | 251.1 % |
| **Floorplan total** | **134 714.4 µm²** = 0.1347 mm² | **269.4 %** |

Two findings, and they point in opposite directions.

**Isolation is cheap.** The entire isolated entropy source — both rings, the
combiner, all four samplers, four guard rings and every isolation channel
between them — is **4.1 % of the area row**. The guard rings and channels cost
1 070 µm² of that, i.e. **2.1 % of the row for the whole isolation structure**.
Nothing in this document's mitigations is area-constrained, and the proposed
buffer mitigation adds 0.06 % more. *The isolation argument does not have to
trade against the area budget, and it should not be allowed to.*

**The digital section misses the area row on standard-cell area alone** —
74 485 µm², i.e. **1.49× the whole row before any placement at all**, and
2.5× once placed at 60 % utilisation. The two 8 × 32-bit output FIFOs are
**69.8 %** of it (512 `dffrnq_1` + 448 `mux2_1` + 16 `icgtp_1` =
51 982 µm²). This is the
same structure, in the same block, that [DR-0017] identifies as the reason the
`< 1 µA` idle row misses by 4.5× — one design decision showing up on two
different rows. **No row is edited here, and no design change is made here**:
this issue owns the entropy source's isolation, not the interface's FIFO depth.
The number is recorded so the conflict is visible rather than discovered later,
exactly as [DR-0010] §Consequences recorded the power collision.

### What the area model is

A **bottom-up inventory estimate with a stated method**, not a synthesis result
and not a layout. No synthesiser, placer or router has been run on this block,
and none of the analog cells has been drawn.

- Gate-shaped cells (`ro_stage`'s core inverter, `ro_nand2`, `xor2`,
  `sampler_dff`) are priced at their nearest `gf180mcu_fd_sc_mcu7t5v0`
  equivalent's LEF area — the same method, and the same library, that
  [DR-0008]'s conditioner figure uses. That library is 7-track and uses wider
  devices than these hand-drawn minimum-width cells, so it **over-estimates**
  the analog side: the conservative direction.
- The series starve devices (`L` = 2 µm) have no standard-cell analogue and are
  priced at a real generated footprint from `klt gen mos_array`, DRC-checked in
  the same run (1.193 µm² n, 2.261 µm² p). They are generated at `W` = 0.42 µm
  rather than their drawn 0.220 / 0.240 µm because the generator will not go
  narrower (see [Tool friction](#tool-friction)), which over-estimates them
  too.
- The digital side reuses the cell inventories
  `design/digital_power_estimate.py` already maintains — one copy of that list
  in the repository, already guarded by `sim/tests/test_power_rollups.py`.
- Placement utilisation is reported at both 60 % and 80 %, per [DR-0008]'s
  convention; the floorplan geometry is built at 60 %.
- The composed abstract's row bounding box is **473.8 × 354.3 µm**. That is the
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

## DRC: what actually ran

`klt drc` was run — by this script, not by hand — on every generated device
footprint and on the composed floorplan abstract, with the same `gf180mcu` deck
and the same PDK resolver `layout/verify.py` uses. Verbatim output in
[`reports/floorplan.drc.json`](reports/floorplan.drc.json).

```
composed abstract: status "clean", violation_count 0, rule_counts {}
```

**Read the scope off the report, not off this sentence.** The abstract draws
Comp, Contact and Metal1 only, so the deck checked **three layers** and
**skipped sixteen rules** for want of the layers they apply to (all upper
metal, MiM, BJT, poly and n-well). That is in the report's own `coverage`
block.

**What a clean result here does and does not mean:**

- It **does** mean the isolation structures are legal geometry at these
  dimensions: four guard rings with those tap widths and contact pitches, at
  those sizes, with 20 µm between them, violate no rule in the curated deck.
- It does **not** mean the block is DRC-clean. **The regions are empty.** No
  ring, no combiner, no sampler and no standard cell has been drawn. A DRC run
  over a floorplan abstract can only check the floorplan abstract.
- It is **not tapeout sign-off**, for all the reasons
  [`layout/README.md`](../README.md) already states: `klt`'s decks are a
  curated subset, not the PDK's own sign-off deck.

The generated streams also cannot be identified to a `klt` build by anything
`klt` reports (`klt --version` reads `0.1.0` for every build to date —
[klayout-tools#306]); `layout/reports/environment.json` records the `klt_origin`
commit for the same install this flow ran on, and every report here carries
`klt`'s own `provenance` block including a content hash of the deck.

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
9. **No layout.** This is a floorplan abstract with empty regions.

None of these is a reason to withhold the floorplan. All of them are reasons
not to read a clean DRC result as an independence argument.

---

## Tool friction

Per [CLAUDE.md](../../CLAUDE.md), friction found while using klayout-tools is
filed generically against the tool — the tool gap, never this repository's
design. This work produced three, all filed against
[klayout-tools][klt] and all worked around in
[`floorplan.py`](floorplan.py) rather than silently absorbed:

1. **[klayout-tools#320][kt320]** — generated streams are not byte-reproducible.
   `klt gen`, `klt gen-compose` and `klt draw` stamp wall-clock time into the
   GDSII `BGNLIB` / `BGNSTR` records, so two runs of the same generator on the
   same inputs differ in those bytes. A golden-artefact flow cannot diff that.
   `floorplan.py` zeroes those fields on the way in (`normalise_gds`), which is
   the same thing this repository's own writer `layout/testcells/gdsii.py`
   already does for the same reason.
2. **[klayout-tools#321][kt321]** — `klt gen-compose` supports only
   `placement.strategy: "row"`. A floorplan is two-dimensional by nature and
   needs explicit per-block x/y placement with declared separations; a single
   row with one `spacing_um` is what this abstract had to be built as. (Two
   smaller things noted there have since been fixed upstream by
   [klayout-tools#328][kt328]: `blocks[].generator_report` paths now resolve
   against the request file's own directory rather than the working
   directory — matching `klt lvs`'s convention all along — and an
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

[klt]: https://github.com/2AMLogic/klayout-tools
[kt320]: https://github.com/2AMLogic/klayout-tools/issues/320
[kt321]: https://github.com/2AMLogic/klayout-tools/issues/321
[kt322]: https://github.com/2AMLogic/klayout-tools/issues/322
[kt328]: https://github.com/2AMLogic/klayout-tools/issues/328
[klayout-tools#306]: https://github.com/2AMLogic/klayout-tools/issues/306

[#75]: https://github.com/2AMLogic/gf180-trng/issues/75
[#76]: https://github.com/2AMLogic/gf180-trng/issues/76
[#78]: https://github.com/2AMLogic/gf180-trng/issues/78
[#82]: https://github.com/2AMLogic/gf180-trng/pull/82
[#86]: https://github.com/2AMLogic/gf180-trng/issues/86
[#87]: https://github.com/2AMLogic/gf180-trng/issues/87

[DR-0007]: ../../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md
[DR-0018]: ../../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md
[DR-0008]: ../../spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md
[DR-0010]: ../../spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0012]: ../../spec/decision-records/DR-0012-sampler-fixed-external-clock.md
[DR-0017]: ../../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
