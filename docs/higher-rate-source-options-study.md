# Design study: what a higher-rate entropy source would cost on gf180

Status: design study for issue [#629]. **It commits to nothing.** It changes no
row of the target specification, no decision record, no schematic, no layout
and no evidence record, and it ran no new simulation. Every figure below is
read from, or computed from, records already committed under `sim/records/`,
and is reproduced by one command:

```sh
python3 sim/tools/higher_rate_options.py            # the full table
python3 sim/tools/higher_rate_options.py --check    # holds every figure quoted here
```

`--check` is part of `npm run check:spec`, so a newly appended record that
moves one of these numbers fails CI until this document is updated.

**No entropy or `H` claim is made anywhere in this document.** `Q_H0` below is
DR-0007 §2's design *target*, not a measurement; DR-0004's tiering is
unchanged and [#12] owns `H`. The metastability option in particular gets **no
rate figure at all** beyond an upper bound on how often it can be strobed.

## The question

The shipped two-ring array meets DR-0007 §2's sizing inequality up to about
2.8 kbps at its entropy-binding corner, so the block is positioned as a
low-rate source (> 2 kbps raw, per
[`DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy`](../spec/decision-records/DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md)).
This study answers, with numbers, what it would take to reach a raw rate
hundreds to thousands of times higher, so that a later requirement can be
answered without redoing the analysis. Two routes are priced:

- **A — more combined rings** of the shipped starved cell
  ([`DR-0007`](../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)
  §2), in two topologies: the ratified one (XOR tree ahead of one sampler,
  DR-0007 §1) and a variant with one sampler per ring (A-post);
- **B — the metastability-hybrid tap**
  ([`DR-0011-metastability-hybrid-tap-claims-and-scope`](../spec/decision-records/DR-0011-metastability-hybrid-tap-claims-and-scope.md)),
  bounded by what that record does and does not establish.

Rate targets considered: **100 kbps** (an intermediate point), **1 Mbps** and
**4 Mbps** raw (the original DR-0003 row and its stretch value).

## How to read the labels

Every estimate carries one label:

- **[M] measured** — a value read directly from a named committed record.
- **[L] law** — derived from measured inputs through a named law: DR-0007 §2's
  sizing inequality and DR-0010's `(★)`, with the starved-cell constant below.
- **[A] assumed** — rests on an assumption stated next to it that no record
  in this repository tests.

## Inputs

### Which jitter-energy constant

`a = 7.322`, the **starved** cell's asymptotic (accumulating-component)
constant at its entropy-binding measured corner, `ss`/−40 °C/3.63 V, from
`python3 sim/tools/starved_cell_jitter_energy.py` over
`2026-08-01-ro-ring5-starved-jitter-long-{01,02,03}` (see
[`sim/characterization-starved-cell-jitter-energy.md`](../sim/characterization-starved-cell-jitter-energy.md)).
It is the value DR-0011-raw-rate §2 adopts, for the reasons given there: only
the accumulating component survives extrapolation to millisecond-scale sample
periods, and the corner that binds should supply its own constant.

The plain-cell `a = 1.79` that `sim/tools/array_sizing.py` still carries as its
stated constant is **not** used anywhere in this study: it was fitted to an
unstarved inverter ring this project does not ship. `higher_rate_options.py
--check` fails if the 7.322 it uses drifts from the live derivation by more
than 1 %.

### Array evidence and binding corners

The shipped array's per-ring period, per-ring power, XOR-tree power and
XOR-node transition rate come from `array_sizing.py`'s own loaders over the
27-point covered grid (`*-ro-array-core-pvt-q-*`, with
`*-ro-array-core-power-*`). Two corners are used, and every row of every
table says which:

- **Entropy-binding** (minimum `Q`): `ss`/+125 °C/3.63 V,
  `2026-08-02-ro-array-core-pvt-q-54`. Ring counts are sized here.
- **Power-binding** (maximum power): `ff`/−40 °C/3.63 V,
  `2026-08-02-ro-array-core-pvt-q-39`. Active power is quoted here, because
  that is where the README's Power row binds.

At the starved-cell `a`, the shipped two-ring array meets DR-0007 §2 up to
**2774 bps** at the entropy-binding corner **[L]**
(`python3 sim/tools/array_sizing.py --a 7.322` prints the same figure). Per
ring, the array delivers `g = Q/T_s = 8.3217 s⁻¹` there **[L]**.
`higher_rate_options.py --check` also fails unless the law, applied to the
shipped array at that rate, asks for exactly the shipped `N = 2`.

### The baseline the options are compared against

Read on this study's base from `README.md` and
[`docs/spec-row-status.md`](spec-row-status.md):

| Row | Target | Current status (README) |
|---|---|---|
| Power | < 500 µW active at `ff`/+10 % | **missed**: 758.2 µW active, 1.5× over; of which the analog block is 393.2 + 16.9 µW (entropy source 393.2 µW, measured) |
| Area | < 0.05 mm² (50 000 µm²) | **missed**: 175 789.9 µm² regenerated floorplan, 351.6 % of the row; the analog regions (two rings, combiner and samplers, guard rings and channels) are 7 026.4 µm², 14.05 % |
| Raw rate | the README row still reads > 1 Mbps (DR-0003) | DR-0011-raw-rate (`Accepted`) moved the value to > 2 kbps, but its mechanical edit set has not landed: [#585] and [#491] are open, and `array_sizing.py` still states `a = 1.79` and a 500 bps default. This study reads that 2 kbps-era tooling as it is on `main` and overrides only `a`, through the tool's own `--a` path. |

Every option below is therefore being compared against a block that already
misses its power and area rows.

## Option A — more combined rings

### The law, and why rings are not the lever

DR-0010's `(★)` collapses DR-0007 §2, for an array of one cell design, to

```
Q_array(T_s) = a · k_B · T · T_s · P_rings / E_cycle²
```

Solving `Q_array(1/R) ≥ M · Q_H0` for the rings' total power gives a floor
that does not depend on how many rings the power is split into:

```
P_rings ≥ M · Q_H0 · R · E_cycle² / (a · k_B · T)
```

With the shipped eleven-stage ring's `E_cycle = P_ring · T0 = 5.24 × 10⁻¹³ J`
at the entropy-binding corner, that floor is **40.93 µW of ring power per kbps
of raw rate** **[L]**. This confirms the hypothesis the issue states: at a fixed
cell and operating point, raw rate costs ring power linearly, and adding rings
is simply how that power is spent. The only lever in `(★)` that is not linear
is `E_cycle`, which enters squared.

### Ring count, power and area at each target

Rings are the shipped cell at the shipped operating point, so per-ring power
and area are the shipped ring's. `N` is the smallest count meeting DR-0007 §2
at the entropy-binding corner.

| Rate | `N` [L] | Ring power at power-binding corner [L] | `(★)` floor at entropy-binding corner [L] | XOR-tree power at power-binding corner [A] | Array area [A] | Mean interval between XOR-root transitions, entropy-binding corner [L] |
|---|---|---|---|---|---|---|
| (shipped) | 2 | 273 µW | — | 120 µW [M] | 1 389 µm² | 2.3 ns |
| 100 kbps | 73 | 9 969 µW | 4 093 µW | 27 119 µW | 51 620 µm² | 63.3 ps |
| 1 Mbps | 722 | 98 598 µW | 40 926 µW | 411 473 µW | 510 776 µm² | 6.40 ps |
| 4 Mbps | 2 885 | 393 983 µW | 163 706 µW | 1 990 219 µW | 2 041 059 µm² | 1.60 ps |

How each column is made:

- **Ring power** — `N` × the shipped ring's measured power at the
  power-binding corner (136.6 µW per ring, `…-pvt-q-39`). The `(★)` floor
  column is the same law at the entropy-binding corner, where rings burn
  ~2.4× less; the two agree to within the rounding of `N` up to an integer.
- **XOR-tree power [A]** — the measured energy per XOR-node transition at the
  power-binding corner (117 fJ, `…-pvt-q-39`: `P_tree / xo_trans_per_s`)
  times `N · r · log₂N` transitions per second, `r` the per-ring transition
  rate. That is exactly the one measured xor2 at `N = 2`; for larger `N` it
  assumes every level of a balanced tree carries all `N` rings' transitions
  and that no pulse is swallowed. It is the cost of a tree that works, and the
  last column says it would not.
- **Array area [A]** — `N` ring slots of 681.1 µm² each (the ring's guarded
  region, 546.1 µm², read from its committed assembled GDS in
  `layout/floorplan/reports/area.json`, plus one 20 µm isolation channel along
  its 6.75 µm side), plus `N − 1` xor2 cells at 26.3 µm². This assumes rings
  keep today's per-ring guard ring and channel and tile in one dimension; a
  shared guard ring would be smaller, at a cost in isolation that is exactly
  the risk below. It excludes the samplers and the digital section, which do
  not scale with `N`.
- **XOR-root interval [L]** — `1 / (N · r)` at the entropy-binding corner:
  the mean time between transitions at the tree's output.

**Against the baseline.** At 100 kbps, ring power alone is 20× the
`< 500 µW` row and the array alone is 1.03× the entire `< 0.05 mm²` area
row; at 1 Mbps the ring floor is ~82× the power row and the array ~10× the
area row; at 4 Mbps, ~330× and ~41×.

**The ratified topology does not scale to these `N` [A].** At 100 kbps the
XOR root would have to pass a transition every 63 ps on average, at the
*slowest* corner; at 1 Mbps, every 6.4 ps. For scale, one minimum-width
**unstarved** inverter stage — the tap's strobe path divided by three, at the
*fastest* measured corner — is 52.4 ps (`2026-08-01-ro-meta-tap-skew-01`,
`t_path_s`). No record here measures an xor2's delay, but an xor2 is slower
than an inverter, so a single-node XOR tree over tens to thousands of free
rings would swallow most transitions before the sampler sees them. The
evidence does not support DR-0007 §1's "XOR ahead of one sampler" past a
small `N`.

### Variant A-post: one sampler per ring, XOR after sampling

The usual way around the bandwidth limit is to sample each ring with its own
flop and XOR the sampled bits, so the combiner runs at the sample rate `R`
rather than at the rings' transition rate. Same rings and ring power as A;
the tree is replaced by per-ring flops:

| Rate | `N` [L] | Ring power at power-binding corner [L] | Per-ring sampler data power at power-binding corner [A] | Array area [A] |
|---|---|---|---|---|
| 100 kbps | 73 | 9 969 µW | 1 275 µW | 57 068 µm² |
| 1 Mbps | 722 | 98 598 µW | 12 608 µW | 564 664 µm² |
| 4 Mbps | 2 885 | 393 983 µW | 50 380 µW | 2 256 387 µm² |

- **Sampler data power [A]** — the charge a sampler flop's D input draws per
  ring transition, 9.36 fC (mean of the two flops in
  `2026-10-10-sampler-core-liveness-active-01`, measured at `tt`/27 °C/3.30 V
  only), × the per-ring transition rate × V at the power-binding corner. It
  assumes the per-transition charge holds at that corner. The flops' clock
  power at `R` ≤ 4 MHz and the digital XOR of `N` bits at `R` are not included.
- **Area [A]** — option A's ring slots, plus one `dffrnq_1` (74.6 µm²) per
  ring and `N − 1` xor2, priced from the same `area.json`.

A-post is architecturally a change, not a re-sizing: DR-0007 §1 places the XOR
ahead of a single sampler and DR-0001 defines the raw tap at that sampler's
output. DR-0007's alternatives section rejects a related form (time-interleaved
channels) and does not consider sample-then-XOR. Adopting it would need its own
decision record; this study only prices it.

### The `E_cycle` lever

Because `E_cycle` enters `(★)` squared, a shorter ring of the same cell lowers
the floor faster than anything else. DR-0010 §3 measured
`E_cycle(11 stages)/E_cycle(5 stages) = 2.21` on this cell at
`tt`/27 °C/3.30 V. Applied to the floor above **[L]**, a five-stage array of
the same cell needs **838 µW** of ring power at 100 kbps, **8 380 µW** at
1 Mbps and **33 518 µW** at 4 Mbps, at the entropy-binding corner (4.9× less
than eleven stages). That is still 1.7× to 67× the whole `< 500 µW` row before
tree, samplers or digital section, and DR-0010 §3 records why five stages is
unmeasured where it binds: the only five-stage ring of this cell swings 80 %
of the rail at nominal, with no swing data at the binding corners. The
three-stage floor was rejected on measured gain in the same record.

## Option B — the metastability-hybrid tap

### What can and cannot be said

DR-0011-metastability establishes four things about
`design/xschem/ro_meta_tap.sch` (hung off the array's XOR node in
`design/xschem/ro_array_core_meta.sch`) and **no entropy figure**: the tap does
not gate the ring core; its arbiter's regeneration behaviour is bounded to
roughly 3–300 fs, not a single time constant; its trim sensitivity and that
sensitivity's PVT drift are measured; and its power is measured. It declines a
resolution-time histogram, which is what an entropy figure would need
([`spec/entropy-architecture-survey.md`](../spec/entropy-architecture-survey.md)
§B.2). This study therefore gives the tap a **sampling-rate upper bound, a
power figure and an area estimate, and no rate claim**. A rate at which the
tap's bits carry any stated entropy cannot be derived from this repository's
evidence.

### Sampling-rate upper bound

The tap fires on transitions of the XOR node, so it cannot make more decisions
per second than that node toggles. Over the shipped array's covered grid the
slowest XOR-node rate is **3.376 × 10⁸ transitions/s**, at `ss`/+125 °C/2.97 V
(`2026-08-02-ro-array-core-pvt-q-52`) **[M]**: about 84× the 4 Mbps target. The
arbiter itself is not the limit: its strobe path plus resolution time is
0.20–0.28 ns at the three measured corners (`…-ro-meta-tap-skew-{01,02,03}`,
`t_path_s` + `t_res_05ff_s`). So **one tap** clears every target in this study
*as a strobe rate*. That is an upper bound on how often a bit can be read, not
on how many of those bits are random.

### Power and area

| Quantity | Value | Label and source |
|---|---|---|
| Tap power as built (strobed at every XOR transition) | 187.0 µW at `ff`/−40 °C/3.63 V; 120.2 µW at `ss`/−40 °C/3.63 V; 87.3 µW at `tt`/27 °C/3.30 V | [M] `2026-08-01-ro-array-core-meta-power-{01,02,03}`, `p_tap_w` |
| Energy per strobe | 194.8 fJ at `ff`/−40 °C/3.63 V (151–195 fJ over the three corners) | [L] `p_tap_w / xo_trans_per_s`, same records |
| Tap power if strobed only at the sample rate | 0.019 µW at 100 kbps; 0.195 µW at 1 Mbps; 0.779 µW at 4 Mbps | [A] energy per strobe × `R`; assumes a strobe gate the schematic does not have, and no static term |
| Tap cell area | 74.6 µm² | [A] six `meta_inv` and two `meta_nand2` priced as `inv_1` and `nand2_1` from `area.json`; no layout exists; its own `vddm` supply would add a guard region, which is not included |

The meta-power records were taken on the array before the ring-buffer adoption
(#78), so their ring figures differ slightly from the shipped core's; the
per-strobe energy is a property of the tap and is used on that assumption.

### What stands in the way: calibration

DR-0011-metastability §3 measures the tap's release skew at **13.23–19.12 ps
per fF** of trim imbalance, varying 1.45× over three corners
(`2026-08-01-ro-meta-tap-skew-{01,02,03}`, `dt_per_ff_s`). To place the skew
inside a regeneration window of 3–300 fs, the trim must therefore resolve
**0.157 aF to 22.7 aF** **[L]**, and hold it across a 45 % PVT swing in the
conversion before any device mismatch. That is the quantitative form of
§B.4's concern that a one-time trim cannot hold; it implies a continuously
re-centring calibration loop, and the survey's §B.4 notes that such a loop is
itself a new coupling path. Neither the loop nor its isolation argument exists.

## Comparison

All entries are for the entropy source alone (rings, combiner, samplers or
tap); none include the digital section, which is unchanged by any option.

| Rate | Option | Count | Area | Active power | Corner |
|---|---|---|---|---|---|
| 100 kbps | A (XOR tree) | 73 rings | 51 620 µm² [A] | 37 088 µW: rings 9 969 [L] + tree 27 119 [A]; **tree not viable** | `N`: `ss`/125/3.63; power: `ff`/−40/3.63 |
| 100 kbps | A-post | 73 rings + 73 flops | 57 068 µm² [A] | 11 244 µW: rings 9 969 [L] + samplers 1 275 [A] | same |
| 100 kbps | B | 1 tap | 74.6 µm² [A] | 0.019 µW gated [A]; 187.0 µW as built [M] | strobe bound: `ss`/125/2.97; power: `ff`/−40/3.63 |
| 1 Mbps | A (XOR tree) | 722 rings | 510 776 µm² [A] | 510 071 µW: 98 598 [L] + 411 473 [A]; **tree not viable** | as above |
| 1 Mbps | A-post | 722 + 722 | 564 664 µm² [A] | 111 206 µW: 98 598 [L] + 12 608 [A] | as above |
| 1 Mbps | B | 1 tap | 74.6 µm² [A] | 0.195 µW gated [A]; 187.0 µW as built [M] | as above |
| 4 Mbps | A (XOR tree) | 2 885 rings | 2 041 059 µm² [A] | 2 384 202 µW: 393 983 [L] + 1 990 219 [A]; **tree not viable** | as above |
| 4 Mbps | A-post | 2 885 + 2 885 | 2 256 387 µm² [A] | 444 363 µW: 393 983 [L] + 50 380 [A] | as above |
| 4 Mbps | B | 1 tap | 74.6 µm² [A] | 0.779 µW gated [A]; 187.0 µW as built [M] | as above |

**Option B's row is not comparable with option A's** in the way the table's
shape suggests: A's rows are sized to meet DR-0007 §2's entropy target (a
modelled target, not a measured `H`), while B's row states only that a bit can
be *read* that often. B has no entropy-per-bit figure, and none is claimed.

## Validity limits

- **One cell family.** `a` is measured on a five-stage, unloaded ring of the
  shipped starved cell. No five-to-eleven-stage check of `a` exists
  (DR-0011-raw-rate, Consequences), and every ring count here applies it to the
  eleven-stage ring.
- **Three corners for `a`, twenty-seven for the array.** `a` is measured at
  `ss`/−40, `tt`/27 and `ff`/−40 only. The array's entropy-binding corner is at
  +125 °C, where `a` is not measured; the 7.322 is applied there as
  DR-0011-raw-rate applies it.
- **The fixed-injection scaling error** (~2–4× on `a`, hence on every `N` and
  every power floor here) does not cancel between cells. All `N` are
  proportional to `1/a`.
- **White noise only.** Flicker is excluded (DR-0007 §2), which makes `Q`
  a lower bound and every `N` an upper bound on what the model requires.
- **Independence is assumed.** DR-0007 §2 sums variances over independent
  rings. Nothing in this repository measures ring-to-ring independence at
  more than two rings; at two, a shared XOR input stage was measured to
  couple neighbouring rings deterministically
  ([`sim/characterization-array-ring-coupling.md`](../sim/characterization-array-ring-coupling.md)).
- **Ring-only scope for A.** The tree, sampler and area models are
  assumed, as labelled; only ring power is derived from the law.
- **Option B** inherits every limit in DR-0011-metastability, including a
  regeneration bound that spans two orders of magnitude.
- **`fs`/`sf` corners** are not covered by the array grid (DR-0006).

## Conclusion

**Plausibility on gf180.** No option reaches 1 Mbps or 4 Mbps inside anything
near the block's current budgets, and only one option's rate can be stated
at all.

- **Option A in the ratified topology (XOR tree ahead of one sampler) is not
  plausible above a few tens of rings.** Its ring power is fixed by the law
  (40.9 µW per kbps at this cell and operating point, however it is split
  into rings), and the XOR root would have to pass transitions faster than one
  inverter delay of this process.
- **Option A-post is plausible as a circuit, at a cost the block cannot
  absorb.** At 100 kbps it needs ~11 mW and ~0.057 mm² for the entropy source
  alone (22× the power row, 1.1× the area row); at 1 Mbps, ~0.11 W and
  ~0.56 mm². Five-stage rings would cut ring power ~4.9× if they hold swing at
  the binding corners, which is unmeasured. It is also an architecture change
  needing its own decision record.
- **Option B is the only route whose cost does not grow with rate**: one tap
  of ~75 µm² clears every target as a strobe rate, at under a microwatt if
  gated, 87–187 µW as built. But this repository cannot say whether its bits
  are random, and it would need sub-attofarad, continuously recalibrated trim.
  It is plausible as a research direction, not as a design to size.

**Principal risks.**

- **Power**, for option A in any form: the law makes it linear in rate, with
  `E_cycle²` the only lever.
- **Shared-supply and substrate coupling, and injection locking**, for option
  A: hundreds of rings on one die is the configuration the survey's §A.4 flags,
  ring-to-ring coupling is already measured at two rings, and the sizing law's
  independence assumption is what every `N` rests on.
- **Calibration drift**, for option B: the measured 1.45× PVT swing in the
  trim conversion, and a calibration loop that would itself be a coupling path
  (§B.4).

**What would substantiate each.**

- **A / A-post:** `a` on the eleven-stage ring (the stage-count check
  DR-0011-raw-rate names); `a` at +125 °C; a multi-ring transient-noise run that
  measures whether the per-ring `σ` adds as independent at more than two rings,
  including through a shared supply; for the five-stage lever, the deterministic
  five-stage `ro-array-core-power`-style run DR-0010 §3 describes, reporting
  swing at `ss`/−40/3.63 and `ff`/−40/3.63; and for A-post, a measured xor2/flop
  combine at the sample rate. Multi-corner runs go through `klt sim` on the
  batch fleet.
- **B:** a technique that yields an entropy figure for the arbiter — the
  resolution-time distribution DR-0011-metastability declines, or an
  analytic alternative — plus a converged regeneration time constant (DC/AC
  loop-gain extraction or a finer solver configuration, per that record's
  Revisit-if), and a designed and isolated calibration loop.

**No row change is proposed here.** If a later requirement makes one of these
options worth pursuing, the change goes through a new decision record and the
evidence above, not through this document.

## Reproduce

```sh
python3 sim/tools/higher_rate_options.py            # every table above
python3 sim/tools/higher_rate_options.py --check    # the figures quoted here
python3 sim/tools/array_sizing.py --a 7.322         # the shipped array's 2774 bps edge
python3 sim/tools/starved_cell_jitter_energy.py     # where 7.322 comes from
python3 sim/tools/jitter_energy_law.py              # the plain-cell 1.79 this study does NOT use
```

[#12]: https://github.com/2AMLogic/gf180-trng/issues/12
[#491]: https://github.com/2AMLogic/gf180-trng/issues/491
[#585]: https://github.com/2AMLogic/gf180-trng/issues/585
[#629]: https://github.com/2AMLogic/gf180-trng/issues/629
