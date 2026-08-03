# Does buffering each ring output remove the XOR-combiner coupling, and at what cost?

Status: measurement complete for issue [#75]. **The buffer removes 92.8 % of
the coupling, not all of it, and it does not cost power — it returns 19.1 µW.**
Both halves of that were unknown before this measurement, and the second one
has the opposite sign to the estimate it replaces. Adoption is [#78].

`sim/characterization-array-ring-coupling.md` (issue [#51] / PR #67) measured
that a ring driving the array's XOR combiner alongside a switching neighbour
shows `σ₁` **28.6×** higher than the same ring with a quiet neighbour, at
`tt`/27 °C/3.30 V — charge injected backwards into the ring node through the
gate-drain/gate-source capacitance of the combiner's input stage, a shared
electrical node by construction, not a layout adjacency.
[`layout/floorplan/README.md`](../layout/floorplan/README.md) (issue [#16])
proposes a mitigation — one minimum-width inverter buffer per ring, between
the ring node and every consumer — and explicitly declines to adopt it,
because nothing measured whether it works. This document closes that gap.

**This is an ordinary summary, not evidence.** Every number below cites the
`sim/records/` stem that produced it — treat this document as a reading guide
over that evidence, not a substitute for it.

**No entropy-rate or spec-compliance claim is made anywhere in this document.**
[`DR-0004`](../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md)'s
tiering is unchanged.

## The mitigation under test

One minimum-width inverter (`pfet_03v3 W=0.44u`, `nfet_03v3 W=0.22u`, both
`L=0.28u` — the same device sizing `xor2`'s own input stage and `ro_stage`'s
core inverter already use, carrying the same `ad`/`as`/`pd`/`ps`/`nrd`/`nrs`
diffusion-geometry expressions as every device in the committed netlists, so
the buffer's own drain junction capacitance is modelled rather than omitted)
spliced in between each ring's output node and the combiner's input. Both
rings get their own buffer instance — the "per-ring, never shared" requirement
`layout/floorplan/README.md` states, because a single buffer feeding both
combiner inputs recreates exactly the shared node the mitigation exists to
remove.

Three decks measure it, at the two corners the two questions in issue #75's
acceptance criteria need. Each differs from its unbuffered counterpart by
exactly the buffer insertion, per the one-change-per-variant discipline issue
#51 used:

| deck | unbuffered counterpart | what it measures | corner |
|---|---|---|---|
| [`ro-array-coupling-xor-driven-buffered`](tb/ro-array-coupling-xor-driven-buffered/) | [`…xor-driven`](tb/ro-array-coupling-xor-driven/) (the 28.6× case) | `σ₁` at the ring's own node, neighbour **switching** | `tt`/27 °C/3.30 V |
| [`ro-array-coupling-xor-static-buffered`](tb/ro-array-coupling-xor-static-buffered/) | [`…xor-static`](tb/ro-array-coupling-xor-static/) (the 1.06× control) | `σ₁` at the ring's own node, neighbour **on a rail** | `tt`/27 °C/3.30 V |
| [`ro-array-core-power-buffered`](tb/ro-array-core-power-buffered/) | [`…core-power`](tb/ro-array-core-power/) | each ring's, each buffer's and the combiner's current, separately metered | `ff`/−40 °C/3.63 V |

`σ₁` is measured at the RAW ring node `ro1`, **upstream of its own buffer** —
the question is whether the buffer keeps the ring's own oscillating node
quiet, not whether the buffered signal is quiet (which it trivially would be,
being a low-impedance driven node by construction).

### Why there are two coupling decks and not one

The buffer changes *two* things about the ring at once: it isolates it, and
it lightens its load from `xa1`'s 1.98 µm of gate to the buffer's 0.66 µm.
A lighter load makes the ring faster, and a faster ring is a **different
operating point** — issue #51's own variant-2 manifest says so about its own
pairing ("a slower ring is a different operating point, so a `σ` difference
between this variant and the control is not by itself evidence of anything
dynamic"). Reading the buffered *driven* deck against #51's *unbuffered*
controls would therefore span two changes and attribute neither.

So the buffered pair is measured, and the number this document leads with is
the ratio **within** that pair:

```
coupling factor  =  σ₁(neighbour switching)  /  σ₁(neighbour on a rail)
```

at one operating point, with one change between numerator and denominator.
Unbuffered, that ratio is issue #51's 28.6×. Buffered, it is measured here.

## Does it remove the coupling? Mostly — 93 % of it, not all of it

All rows at `tt`/27 °C/3.30 V, 4 seeds each (the control's 8), `σ` raw at the
fixed injected level, same 512-period window opened 256 periods after
start-up:

| | variant | `T₀` | `σ₁` | vs standalone control | expon. | seed spread of `σ₁` |
|---|---|---|---|---|---|---|
| 1 | [`ro-ring5-starved-jitter-long-02`](records/2026-08-01-ro-ring5-starved-jitter-long-02.md) (control) | 2.5635 ns | 0.641 ps | 1.00× | 0.421 | 3.9 % |
| 2 | [`…xor-static-01`](records/2026-08-01-ro-array-coupling-xor-static-01.md) | 3.3096 ns | 0.676 ps | 1.06× | 0.454 | 2.3 % |
| 3 | [`…xor-driven-01`](records/2026-08-01-ro-array-coupling-xor-driven-01.md) | 3.3043 ns | 18.32 ps | 28.6× | 0.036 | 0.1 % |
| 5 | [`…xor-static-buffered-01`](records/2026-08-02-ro-array-coupling-xor-static-buffered-01.md) | 2.8536 ns | 0.687 ps | **1.07×** | 0.421 | 4.5 % |
| 6 | [`…xor-driven-buffered-01`](records/2026-08-02-ro-array-coupling-xor-driven-buffered-01.md) | 2.8522 ns | 1.972 ps | **3.08×** | 0.141 | 1.1 % |

**The coupling factor — the one-change ratio, at one operating point:**

| | `σ₁` neighbour switching | `σ₁` neighbour on a rail | ratio | squared (what `DR-0007` §2 substitutes) |
|---|---|---|---|---|
| unbuffered (issue #51) | 18.32 ps | 0.676 ps | **27.10×** | 734× |
| **buffered** (this issue) | 1.972 ps | 0.687 ps | **2.87×** | **8.24×** |

**The buffer removes 92.8 % of the coupling excess. It does not remove the
coupling.**

Three things that follow, in decreasing order of how much they matter:

1. **A residual 2.87× survives, and it is still deterministic.** Seed-to-seed
   spread of `σ₁` goes from 0.1 % (unbuffered, i.e. essentially seed-
   independent) to 1.1 % — but a genuine jitter estimate over this window
   scatters ~2.7 % (`sim/characterization-array-ring-coupling.md`'s
   calibration), and the buffered *quiet-neighbour* control on the same deck
   scatters 4.5 %. The residual is attenuated, not converted into noise. The
   accumulation exponent says the same thing: 0.141 against the 0.421 that
   both the standalone control and the buffered quiet-neighbour control give,
   and the `σ_acc` series is still **non-monotonic** (5.59 ps at lag 8, 4.94 ps
   at lag 16, 3.66 ps at lag 64), which no accumulating jitter process can be.
   The beat is smaller; it is still a beat.
2. **The two controls agree, which is what makes row 6 readable.** The buffered
   quiet-neighbour control lands at **1.07×** the standalone control, against
   the unbuffered static control's 1.06×, with the same accumulation exponent
   (0.421 vs 0.421) and a seed spread in the same family. Two different loads
   at two different operating points give the same answer when the neighbour
   is quiet, so the 2.87× is not an artefact of the buffered ring being a
   different operating point.
3. **8.24× is still not admissible for `DR-0007` §2.** Squared, the residual
   still over-states one ring's contribution to `Q_array` by 8×, and it still
   over-states in the *unsafe* direction (an array sized on it would be
   undersized). The buffer is a large improvement and **not** a licence to
   measure per-ring `σ_acc,i` with the neighbours switching. The measurement
   rule `layout/floorplan/README.md` adopted stands unchanged, and this
   document does not amend `DR-0007` §2.

Reproduce the whole comparison with:

```sh
python3 sim/tools/array_coupling_buffer_variant.py
python3 sim/tools/array_coupling_buffer_variant.py --check
```

## What the buffer costs, measured rather than estimated

`layout/floorplan/README.md` estimated **≈24.4 µW** at `ff`/−40 °C/3.63 V from
`P = C_eff · V² · f`, using the *ring's own* measured `c_eff_node_r1` (an
average over all 11 of that ring's stages) as a stand-in for the buffer's own
switching capacitance — because no buffer had been built to measure directly.
[`2026-08-02-ro-array-core-power-buffered-01`](records/2026-08-02-ro-array-core-power-buffered-01.md)
measures the real buffered array instead, at the same corner, with each ring's
own current, each buffer's own current, and the combiner's current on separate
metered supply branches:

| quantity | unbuffered ([`…core-power-04`](records/2026-08-01-ro-array-core-power-04.md)) | buffered ([`…core-power-buffered-01`](records/2026-08-02-ro-array-core-power-buffered-01.md)) | Δ |
|---|---:|---:|---:|
| ring 1 own power | 130.70 µW | 132.49 µW | +1.79 µW (+1.4 %) |
| ring 2 own power | 138.82 µW | 140.64 µW | +1.83 µW (+1.3 %) |
| buffer 1 own power | — | 29.75 µW | new |
| buffer 2 own power | — | 32.07 µW | new |
| combiner (`xa1`) power | 145.75 µW | 60.10 µW | **−85.64 µW (−58.8 %)** |
| **total (entropy source)** | **415.27 µW** | **395.06 µW** | **−20.20 µW (−4.9 %)** |

Three findings, and **none** of them is what the estimate anticipated:

1. **The ring's own power does not drop from the load reduction.** The
   estimate deliberately did not credit this offset; measured, there is
   no offset to credit either — ring power is **flat to slightly up**
   (+1.3–1.4 %), not down. The buffer's lighter fanout (0.66 µm vs. `xa1`'s
   1.98 µm) does cut the ring's own per-cycle switching energy by 5.0 %
   (`e_cycle_r1_j`: 5.6018×10⁻¹³ J → 5.3200×10⁻¹³ J), but the lighter load
   also lets the ring oscillate faster (`f_r1`: 233.3 MHz → 249.0 MHz,
   +6.7 %), and the frequency increase slightly outweighs the per-cycle
   saving. **The answer to "does the ring's own power drop from the 3× load
   reduction" is: its per-cycle energy does, by 5.0 %; its average power does
   not, because the ring spends the saving on running faster.**
2. **The buffer's own cost is ~2.5× the estimate, not the estimate.** Measured
   combined buffer power is 61.83 µW against the ~24.4 µW estimated. The gap
   is the modelling choice the estimate had to make in the absence of a real
   buffer: `c_eff_node_r1` is an *average* over one ring's 11 stages, each of
   which (apart from the last) drives only the *next* ring stage's light
   0.66 µm gate. The buffer's real load is `xa1`'s full 1.98 µm gate — the
   same heavy load the ring used to drive directly — so an "average internal
   ring stage" understates what the buffer actually has to charge and
   discharge every cycle. **An estimate that landed within 4.3 % of a budget
   row was wrong by 2.5× on its own term.**
3. **The estimate's accounting missed the dominant effect, and it runs the
   other way.** Neither the estimate nor either finding above considered what
   happens inside the combiner itself. The ring's own current-starved output
   stage produces slow edges by design (that is what the series starve
   devices are for); the buffer's output has no starve devices and drives
   `xa1`'s input from an unimpeded rail. Faster edges into `xa1`'s gates cut
   the time its P and N stacks are partially on together, and `xa1`'s own
   current duly drops **58.8 %** once it is driven by the buffer instead of
   by the ring. That single effect (−85.64 µW) is larger than the ring
   flatness (+3.62 µW) and the buffer's own cost (+61.83 µW) combined, so the
   **net** effect on the entropy source's active power is a **decrease** of
   20.20 µW (−4.9 %), not the increase the estimate projected.

Substituting the buffered entropy source into the block's active rollup — the
same arithmetic `sim/tools/power_rollup.py` runs, with the entropy-source term
swapped and the sampler term re-priced at the buffered array's own (higher)
transition rate:

| | entropy source | sampler | digital (estimate) | **total** | vs the `< 500 µW` row |
|---|---:|---:|---:|---:|---:|
| unbuffered (shipped) | 415.3 µW | 15.76 µW | 23.12 µW | **454.2 µW** | 90.8 % |
| floorplan's *estimate* of buffered | ~439.7 µW | — | — | **≈478.6 µW** | 95.7 % |
| **buffered, measured** | 395.1 µW | 16.89 µW | 23.12 µW | **435.1 µW** | **87.0 %** |

Adopting the buffer is worth **−19.1 µW (−4.2 %)** on the block's worst active
corner — *better* than the unmitigated baseline, and 43.5 µW better than the
floorplan's own pessimistic estimate of it. Reproduce every number in this
section with:

```sh
python3 sim/tools/array_coupling_buffer_variant.py
python3 sim/tools/array_coupling_buffer_variant.py --check
```

## Is the buffer adopted?

**Yes, since [#78] / [`DR-0018`](../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md).**
This document recommended adoption and did not perform it, because adopting it
edits the shipped schematic and every downstream artefact derived from it, and
this repository puts a design change through a decision record rather than
through a summary document. `DR-0018` is that record; the paragraphs below are
kept in the tense they were written in, as the case that record acted on, with
[what actually landed](#what-actually-landed) noted at the end of this section.

What the evidence supports:

| question issue #75 asked | answer | evidence |
|---|---|---|
| does it remove the 28.6× coupling? | it removes **92.8 %** of the excess; a **2.87×** residual survives and is still deterministic | rows 5–6 above |
| what does it cost in power? | **nothing — it saves 19.1 µW** on the block's worst active corner (90.8 % → 87.0 % of the row), against a ~24.4 µW *cost* estimated | [`…core-power-buffered-01`](records/2026-08-02-ro-array-core-power-buffered-01.md) |
| does the ring's own power drop from the 3× load reduction? | per-cycle energy −5.0 %; average power **+1.4 %**, because the ring spends the saving on running 6.7 % faster | same record |
| does it let per-ring `σ_acc,i` be measured with neighbours switching? | **no.** 8.24× on `Q_array`, still in the unsafe direction | the coupling table above |

**Where the schematic change lands, when it is made:**
`design/xschem/ro_array_core.sch` — one inverter instance per ring between the
ring's own last stage and `xa1`'s input, with the cell's exported `ro1`/`ro2`
pins re-driven from the **buffer outputs** so that the `DR-0016` liveness
digitizers and the samplers downstream tap the buffered node too, per the
mitigation's "between the ring node and *every* consumer". `design/netlist.py`
then re-exports `design/ro_array_core.spice`. Both buffers are separate
instances; a shared one recreates the node the mitigation exists to remove.

Two consequences that adoption has to carry, neither of which is a blocker:

- **Polarity inverts.** `ro1`/`ro2` become the complement of their ring's
  internal node. `a ⊕ b` and `¬a ⊕ ¬b` are equal, so the combiner output is
  bit-identical; the liveness digitizer counts transitions and is
  polarity-blind; the samplers' entropy does not depend on polarity. Nothing
  downstream needs a matching change, but the pin's meaning changes and the
  schematic should say so.
- **Every record taken on the shipped array is a record of the unbuffered
  array.** Adoption invalidates none of them (`sim/records/` is append-only
  and they remain true of what they measured), but the array's frequency moves
  +6.7 % and its power −4.9 %, so the PVT and `Q` families would need re-running
  against the adopted netlist before they describe the shipped design again.
  That re-run, not this measurement, is the expensive part of adopting.

### What actually landed

[#78] carried out the adoption above, unchanged in shape: `design/xschem/ro_buf.sch`
is the buffer cell, `design/xschem/ro_array_core.sch` instantiates it twice
(`xb1`/`xb2`, never shared), and `ro1`/`ro2` are re-driven from the buffer
outputs. Both consequences listed above landed as described — the polarity of
`ro1`/`ro2` inverted with no downstream change needed, and three record
families (`ro-array-core-power`, `ro-array-core-pvt-q`,
`ro-array-core-startup`) were re-run against the adopted netlist. Two numbers
from this document are worth checking against those re-runs, since a
two-testbench measurement is not the same thing as the shipped array measured
in its own decks:

| | projected here (testbench) | measured after adoption (shipped netlist) |
|---|---|---|
| entropy source, `ff`/−40 °C/3.63 V | 395.1 µW | **393.2 µW** |
| block active rollup, same corner | 435.1 µW (87.0 % of the row) | **433.2 µW (86.6 %)** |

Both landed slightly better than projected. `DR-0018` records what was *not*
re-run: `sim/tb/ro-array-core-mc-freq/` and `sim/tools/worst_corner_entropy.py`'s
`DR-0015` corner-ranking and Monte Carlo mismatch sections still describe the
unbuffered array.

## Caveats

- **One corner per deck**, as issue #75 scopes: `tt`/27 °C/3.30 V for the
  coupling measurement (the mechanism corner issue #51 used), `ff`/−40 °C/
  3.63 V for the power measurement (the power-binding corner the estimate
  this document replaces was made at). Neither deck claims any other corner;
  the PVT sweep of the coupling factor is #13/#12's scope, not this issue's.
  **The 2.87× residual in particular is a circuit ratio with no reason to be
  corner-independent, and it is measured at one corner.**
- **Ideal supply**, same as every deck in the #51 family: every ring, buffer
  and tree supply branch here is a zero-impedance ammeter off one ideal
  `vsup`. These decks say nothing about supply-network coupling, which a real
  array has and these decks do not. The buffer isolates the *gate-capacitance*
  path it was proposed for; it does nothing about a supply path, and adding a
  buffer adds one more switching load to that supply.
- **Pre-layout.** Schematic-derived / hand-expanded netlists, no extracted
  parasitics. Layout adds coupling and loading paths; it removes none — the
  buffer's actual wiring capacitance to `xa1`'s input is not in this model,
  and a real buffer placed away from its ring would have a longer `ro1` net,
  not a shorter one.
- **The 58.8 % drop in `xa1`'s own current is a crowbar-current result at one
  corner**, inferred from the branch currents rather than measured as a
  short-circuit component directly. Nothing here separates crowbar current
  from the load-capacitance term inside that branch; what is measured is the
  branch total, which is what the budget rows are made of.
- **The power deck is deterministic** (no `trnoise()`), and the coupling decks
  are the noisy ones. No record here measures both effects on the same run.
- **`σ` here is raw, at the fixed injected level, and is not physical
  jitter**, exactly as in `sim/characterization-array-ring-coupling.md`. No
  entropy-rate or spec-compliance claim is made anywhere in this document, and
  [`DR-0004`](../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md)'s
  tiering is unchanged.

[#16]: https://github.com/2AMLogic/gf180-trng/issues/16
[#51]: https://github.com/2AMLogic/gf180-trng/issues/51
[#75]: https://github.com/2AMLogic/gf180-trng/issues/75
[#78]: https://github.com/2AMLogic/gf180-trng/issues/78
