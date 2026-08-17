# Digital section: Fmax, area and power across the corner set

Status: measurement complete for issue [#145] — the digital column of [#124]'s
T1 checklist items **5** (full corner verification) and **8**
(characterization report), both of which [#140] recorded as FAIL with the same
one-line reason: *no static timing analysis exists at all, no real-layout
area, and no power across corners.*

All three now exist, from one measurement pass over one fixed piece of
geometry — the committed routed DEF `layout/digital/trng_top.def` ([#111]),
re-timed at fifteen corners with real extracted parasitics. Three findings:

1. **Timing closes at every corner of the set**, with the worst setup slack
   +23.00 ns against the 50 ns constraint it was built to, binding at
   `ss_125C_3v00` with `max` interconnect. Fmax floor **37.04 MHz**, 1.9× the
   20 MHz the design was implemented at and 37× [DR-0003]'s ratified > 1 MHz
   raw rate. Hold closes everywhere too, worst +0.707 ns at `ff_n40C_3v60`
   with `min` interconnect.
2. **The real placed standard-cell area is 113 088 µm²** — **1.52×** the
   pre-synthesis inventory estimate of 74 485 µm², and **226 %** of the whole
   `< 0.05 mm²` README row on digital cell area alone. The 1.52× splits
   cleanly: ×1.21 from cell count/mix, ×1.26 from 9-track rather than 7-track
   rows.
3. **Measured power is 10–14× the library-based estimate** at the same corner,
   the same 1 MHz rate and the same switching-activity assumption — while
   **leakage lands within 0.63–1.32× of it**. The gap is entirely in the
   dynamic term, and most of it is one modelling error the estimate could not
   have avoided before synthesis existed: it prices a flip-flop's clock-edge
   internal energy at the *data* activity, and a flop pays that energy on
   every clock edge whether its data moves or not.

**This document is an ordinary summary, not evidence.** Every number below
cites the `sim/records/` stem family that produced it or the committed
artefact it was read from. One command reproduces every figure here:

```sh
python3 sim/tools/digital_corner_characterization.py --estimate
```

and `--check` (wired into `npm run check:spec`) fails if the records stop
supporting what is written here.

**No README row is edited, proposed or evaluated by this document.** The area
row's disposition is [#150]'s decision, already framed by [DR-0019]; the idle
row's is [DR-0017]'s. What is new here is that both now have a *measured*
number to be decided against instead of an estimate.

---

## 1. What ran

| | |
|---|---|
| DUT | `layout/digital/trng_top.def` — the committed routed DEF from [#111], 2499 placed instances of `gf180mcu_fd_sc_mcu9t5v0`, unchanged and never re-placed |
| Driver | `sim/tb/digital-sta-power/run_sta.py` (gate-level testbench, [DR-0021]) |
| Engine | OpenSTA + OpenRCX inside OpenROAD `26Q3-1278-g4421880472` |
| PDK | `gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b` |
| Parasitics | OpenRCX extraction of the real routing → SPEF → `read_spef`. Not estimated: `rules.openrcx.gf180mcuD.{min,nom,max}` as shipped by the PDK |
| Clock | `clk`, **propagated** through the CTS-built tree in the DEF (not ideal), 50 ns / 20 MHz — the P&R run's own constraint |
| Grid | 5 liberty decks × 3 interconnect decks = **15 corners**, one record each |
| Records | `sim/records/2026-08-17-digital-sta-power-{01..15}.md` |

The liberty decks are the five `gf180mcu_fd_sc_mcu9t5v0` characterises in the
block's ratified 3.3 V family: `ss_125C_3v00`, `ss_n40C_3v00`, `tt_025C_3v30`,
`ff_125C_3v60`, `ff_n40C_3v60`. That is **not** the analog side's 27-point
grid, and it cannot be: `sim/harness/corners.py` sweeps process, voltage and
temperature as independent axes because a device model takes them that way,
while a liberty deck is a characterised bundle of all three. The five decks
are the corners of the same P/V/T box the analog grid spans; the library
simply does not characterise its interior. [DR-0021] §4 records that
difference so a "worst corner" from this family and one from a transistor-level
family are never read as minima over the same set.

The second axis is the one a routed block gets for free and a schematic never
had: the **interconnect corner**. Wire resistance and capacitance have their
own min/nom/max decks, they move independently of the device corner, and
nothing in this repository had a basis for guessing which pairing binds — so
all three are swept against all five.

### Why not `klt`

Every other physical-flow driver here goes through `klt` (`layout/_klt.py`).
This one does not, because no `klt` verb re-times an already-routed DEF. `klt
place-and-route` runs OpenSTA, but only inside a place-and-route run, at the
one corner the request names, over an ideal clock, with placement-estimated
parasitics and no interconnect-corner control (its tech LEF is pinned to the
PDK's `nom` deck). Re-running the flow per corner would also hand each corner
a *different placement*, which is exactly what a corner sweep must not do.
Filed generically upstream per this repository's friction protocol:
[klayout-tools#1099][klt1099] (a signoff-STA verb over an existing
DEF/netlist) and [klayout-tools#1100][klt1100] (parasitic-corner selection).
`run_sta.py` is the caller that should switch to them when they land.

---

## 2. Timing: it closes everywhere, and Fmax has a floor of 37 MHz

| corner | setup slack | hold slack | clock skew | Fmax |
|---|---:|---:|---:|---:|
| **`ss_125C_3v00` / `max`** — setup binds | **+23.000 ns** | +2.418 ns | 0.248 ns | **37.04 MHz** |
| `ss_125C_3v00` / `nom` | +23.763 ns | +2.413 ns | 0.216 ns | 38.11 MHz |
| `ss_125C_3v00` / `min` | +24.395 ns | +2.410 ns | 0.191 ns | 39.05 MHz |
| `ss_n40C_3v00` / `max` | +31.629 ns | +1.682 ns | 0.185 ns | 54.43 MHz |
| `ss_n40C_3v00` / `nom` | +32.198 ns | +1.678 ns | 0.161 ns | 56.17 MHz |
| `ss_n40C_3v00` / `min` | +32.643 ns | +1.675 ns | 0.141 ns | 57.61 MHz |
| `tt_025C_3v30` / `max` | +36.407 ns | +1.223 ns | 0.137 ns | 73.57 MHz |
| `tt_025C_3v30` / `nom` | +36.808 ns | +1.220 ns | 0.119 ns | 75.80 MHz |
| `tt_025C_3v30` / `min` | +37.136 ns | +1.218 ns | 0.104 ns | 77.73 MHz |
| `ff_125C_3v60` / `max` | +38.329 ns | +1.021 ns | 0.086 ns | 85.68 MHz |
| `ff_125C_3v60` / `nom` | +38.672 ns | +1.018 ns | 0.097 ns | 88.27 MHz |
| `ff_125C_3v60` / `min` | +38.953 ns | +1.016 ns | 0.085 ns | 90.52 MHz |
| `ff_n40C_3v60` / `max` | +42.070 ns | +0.710 ns | 0.086 ns | 126.10 MHz |
| `ff_n40C_3v60` / `nom` | +42.330 ns | +0.708 ns | 0.073 ns | 130.37 MHz |
| **`ff_n40C_3v60` / `min`** — hold binds | +42.523 ns | **+0.707 ns** | 0.065 ns | 133.74 MHz |

Total negative slack is **0 ns on both the setup and the hold side at all
fifteen corners**, so those two columns are the whole verdict: there is no
violating path anywhere in the set, not merely a positive worst case.

**The two binding corners are different corners, and always will be.** Setup
binds slow/hot/low-supply with the heaviest wires (`ss_125C_3v00`/`max`);
hold binds fast/cold/high-supply with the lightest (`ff_n40C_3v60`/`min`).
Naming one "the worst corner" would be wrong on the other side. This is the
same shape as the analog side's own split between the rate-binding and
entropy-binding corners (`sim/characterization-worst-corner-and-mc-mismatch.md`
§2), for the same structural reason.

**Fmax is bisected, not extrapolated.** For each corner the driver searches
the clock period for the smallest one at which worst setup slack is still
≥ 0, to 1 ps. The conventional `1/(T − WNS)` extrapolation (what the P&R
flow's own `report_fmax_metric` reports) agrees with the bisection to
**0.0098 %** worst case over the fifteen corners — which is the evidence that
licenses quoting either. `--check` fails if that agreement ever exceeds 1 %,
because a design whose slack is no longer linear in the clock period is one
where the extrapolated number has quietly stopped meaning anything.

The Fmax spread over the set is **37.04 → 133.74 MHz, 3.6×**, and the
interconnect axis alone moves it 5.4 % at the slow corner (39.05 → 37.04 MHz)
against the liberty axis's 3.4×. Wires matter here; devices matter much more.

### Reconciling with the place-and-route report

`layout/digital/reports/place_and_route.json` reports **+27.7354 ns** at
`ss_125C_3v00`, and this sweep reports **+23.763 ns** at the same liberty
corner with `nom` interconnect. Both are right; they are different
measurements, and each record carries the intermediate figure that separates
them:

| | slack at `ss_125C_3v00` |
|---|---:|
| P&R report — ideal clock, global-routing-*estimated* parasitics | +27.735 ns |
| this sweep, ideal clock, OpenRCX-*extracted* parasitics (`worst_setup_slack_ideal_clock_ns`) | +23.908 ns |
| this sweep, propagated clock, extracted parasitics (the headline) | +23.763 ns |

So of the 3.97 ns difference, **3.83 ns is extraction versus estimation** and
**0.145 ns is the real clock tree** (`clock_tree_cost_ns`, the largest such
cost in the set is 0.163 ns). Real extraction is materially more pessimistic
than the router's own RC estimate at this corner, and the CTS tree is nearly
free — which is worth knowing before anyone tries to explain a slack
difference by the clock model.

### What is not timed

The design carries no `set_input_delay`/`set_output_delay` — the same
constraint set the P&R run used — so **68 endpoints are unconstrained**
(42 input ports and 66 output ports have no delay declared) and every number
above is a **reg-to-reg** result. That is a real limit of this pass, not a
rounding one: nothing here says the block's ports meet any interface timing.
The register file *is* synchronous to `clk` ([DR-0013], `always @(posedge
clk...)` in `design/interface/trng_interface.v`), so those paths are real —
what does not exist is any statement of when a host presents address/write
data relative to that edge, or when it expects read data back. [DR-0013]
itself records that gap ("digital timing closure ... remains owed ... nobody
owns it"). Constraining them here would mean inventing arrival and required
times and then checking the invention, which is not a verification result.
Specifying the block's I/O timing contract, and re-running this sweep against
it, is the natural follow-on and is not this issue's scope.

---

## 3. Area: 113 088 µm² placed, 1.52× the inventory estimate

| | cell area | cells | library |
|---|---:|---:|---|
| **Measured** — OpenROAD `report_design_area` over the routed DEF | **113 087.9 µm²** | 2499 placed instances | `mcu9t5v0` (9-track) |
| Estimate — `layout/floorplan/reports/area.json`, region `digital` | 74 485.3 µm² | 1655 inventoried cells | `mcu7t5v0` (7-track) |
| Delta | **+38 602.6 µm² = ×1.518** | +844 | — |

Both figures are *standard-cell* area, which is what makes them comparable.
The **die** figure in the place-and-route report (301 198 µm²) is not
comparable to either: it follows arithmetically from that run's own 40 %
utilization target, which was chosen to leave routing headroom on a first
attempt, and `layout/digital/README.md` says so at length. This document does
not difference it against anything.

**Where the 1.52× comes from.** Pricing the *same as-built netlist* against
the 7-track library separates the two axes that moved at once:

| | cell area | µm²/cell | step |
|---|---:|---:|---|
| inventory estimate, 7-track | 74 485.3 µm² | 45.01 | — |
| as-built netlist priced 7-track | 90 055.9 µm² | 36.04 | **×1.209** cell count / mix |
| as-built netlist, 9-track (what was built) | 113 087.9 µm² | 45.25 | **×1.256** track height |

Two things follow, and the second is the more useful one:

- **The inventory under-counted cells by 51 %** (1655 → 2499) but
  **over-priced the average cell by 25 %** (45.01 vs 36.04 µm² in like-for-like
  7-track terms). Those errors partly cancel, which is why the naive
  per-instance averages (45.01 estimated, 45.25 measured) look like a
  vindication of the estimate and are not one. A bottom-up inventory built
  from RTL `reg` declarations plus a structural guess at the combinational
  logic got the *shape* of the block right and the *count* wrong in a way no
  amount of care would have fixed without running a synthesiser.
- **The 9-track library costs 25.6 % more area than the 7-track one for
  identical logic.** That is a pure library choice, not a design property, and
  it is the one term on this list that could be recovered by changing a
  parameter — `mcu7t5v0` is what `design/conditioner/area_estimate.py` and the
  floorplan already assume, and `mcu9t5v0` is what [#143] synthesized against
  and [#111] placed. Nothing in this repository has decided that question; it
  is recorded here so that it is decided rather than inherited.

**Against the ratified row.** The `< 0.05 mm²` README row is 50 000 µm² for
the *whole block*. The digital section's placed cell area alone is
**226.2 %** of it (the estimate was 149 %), and at a realistic 60 % / 80 %
placement utilization the digital section alone implies **188 480 / 141 360
µm²**, i.e. 377 % / 283 % of the row. The entropy source, samplers, guard
rings and isolation channels together are 13.1 % of the row
(`layout/floorplan/README.md`).

The row is **not edited, and no design change is proposed here.** [DR-0019]
(`Proposed`) already routes this miss and prices the available responses
against FIFO depth; [DR-0020] (`Proposed`) proposes the depth change itself;
[#150] owns the row. What this section adds is that the miss is now measured
rather than estimated, and 52 % larger than the estimate [DR-0019] was written
against — so whichever response is chosen, it has to close a bigger gap than
that record's own sensitivity table assumed. Re-deriving [DR-0019]'s depth
table against this measurement is that record's follow-up, not this
document's.

---

## 4. Power: 10–14× the estimate on dynamic, and the estimate was right on leakage

Every power figure carries a **declared, uniform switching activity of 0.25
transitions per net per clock cycle at 50 % duty** — deliberately the same
assumption `design/digital_power_estimate.py` makes (its `DEFAULT_ACTIVITY =
0.125` counts *rising* transitions, so the same assumption is 0.25 total).
Neither side is a measured supply current. What follows is a comparison of two
models over the same design at the same corner and rate, where one of them now
knows what the netlist looks like.

### 4.1 The corner sweep

At [DR-0003]'s ratified 1 MHz raw rate (`nom` interconnect shown; the
interconnect axis moves total power by under 3 % end to end):

| liberty corner | total @ 1 MHz | total @ 20 MHz | clock group @ 1 MHz | leakage | leakage current |
|---|---:|---:|---:|---:|---:|
| `ss_n40C_3v00` | 396.7 µW | 7.93 mW | 87.8 µW | 204 nW | 68.0 nA |
| `ss_125C_3v00` | 423.8 µW | 8.45 mW | 93.2 µW | 1.387 µW | 462 nA |
| `tt_025C_3v30` | 510.4 µW | 10.20 mW | 113.9 µW | 275 nW | 83.3 nA |
| `ff_n40C_3v60` | 625.6 µW | 12.51 mW | 140.9 µW | 314 nW | 87.2 nA |
| **`ff_125C_3v60`** — both maxima | **683.2 µW** | **13.47 mW** | 150.2 µW | **10.03 µW** | **2.785 µA** |

Active power binds at `ff_125C_3v60`/`max` (695.1 µW at 1 MHz, 13.71 mW at
20 MHz) and leakage binds at the same liberty corner — hot, fast,
high-supply, which is where the README's Power row already binds its idle
half (`ff` / +10 % / +125 °C). Its active half names `ff` / +10 % without a
temperature; on this sweep the hot `ff` deck is the worse of the two `ff`
decks for total power as well, by 9 %. Leakage is interconnect-independent, as
it must be, so its binding corner is a liberty corner rather than a pair.

**Two things this does not say.** It does not say the block's active power is
683 µW: the digital section is one of three contributors and the whole-block
rollup (`sim/tools/power_rollup.py`) is what adds them up. And it does not
supersede that rollup's own digital term today — see §4.4.

**Against the `< 1 µA` idle row.** [DR-0017] records a 4.5× miss on that row
and attributes it to ungated standard-cell leakage in the digital section,
from the same library-based estimate (4.43 µA of digital idle leakage at
`ff` / +125 °C / 3.60 V, the row's own binding corner). The measurement at
that corner is **2.785 µA — 279 % of the row**, i.e. the miss is real and
unchanged in kind, but **0.63× the size** the estimate predicted. Two caveats
before that number is used anywhere: it is the library's state-independent
default leakage, where the estimate carries an input-state range (2.86 ..
4.43 µA); and it covers the whole synthesized digital section, which is a
slightly different scope from the estimate's three-block inventory. [DR-0017]
remains the record that routes this row, and its proposed replacement figure
was set from the estimate, not from this.

### 4.2 Measured versus the library-based estimate

Both at 1 MHz, both at the same liberty corner, both at 0.25 transitions/cycle:

| corner | measured | estimate (headline) | estimate (ungated) | ×headline | ×ungated | leakage ratio |
|---|---:|---:|---:|---:|---:|---:|
| `ss_n40C_3v00` | 396.7 µW | 15.29 µW | 29.57 µW | 25.9× | 13.4× | 0.92× |
| `ss_125C_3v00` | 423.8 µW | 16.69 µW | 31.59 µW | 25.4× | 13.4× | 1.32× |
| `tt_025C_3v30` | 510.4 µW | 19.13 µW | 36.79 µW | 26.7× | 13.9× | 0.98× |
| `ff_n40C_3v60` | 625.6 µW | 23.12 µW | 44.33 µW | 27.1× | 14.1× | 1.02× |
| `ff_125C_3v60` | 683.2 µW | 39.38 µW | 65.77 µW | 17.4× | 10.4× | 0.63× |

**Why two estimate columns.** `design/digital_power_estimate.py`'s headline
credits the two output FIFOs with clock gating — `clock_duty` of 1/256 and
1/2048 on 512 of the 658 inventoried flops, which its own comment calls "the
single largest error available in the dynamic term". The synthesized netlist
settles that assumption: it contains **no integrated clock gates at all**.
Yosys mapped the RTL's write enables to ordinary feedback multiplexing instead
— the netlist carries **553 `mux2` cells and zero clock-gating cells** — so
every one of the 706 flip-flops in `layout/digital/trng_top.pnr.v` is clocked
on every cycle. The estimate's own `interface_mux_feedback` variant is
therefore the like-for-like column, and both are shown so that the comparison
cannot be read as turning on which one is picked.

**Leakage — the column with no modelling freedom in it — holds up.** 0.63× to
1.32× against a 7-track inventory with 34 % fewer cells is close to the best
that column could have done, and it is the part of the estimate that was read
straight out of characterised library data. The whole gap is in the dynamic
term.

### 4.3 Where the dynamic gap is

At `tt_025C_3v30`/`nom`, 1 MHz, measured 510.4 µW against the ungated estimate's
36.79 µW:

| term | measured | estimate (ungated) | ratio |
|---|---:|---:|---:|
| cell internal energy (`Sequential` + `Combinational` internal) | 315.0 µW | 4.50 µW (`p_internal`) | 70× |
| clock delivery (`Clock` group: tree buffers + clock net) | 113.9 µW | 24.05 µW (`p_clock`) | 4.7× |
| data-net switching (`Sequential` + `Combinational` switching) | 81.2 µW | 7.91 µW (`p_data`) | 10× |
| leakage | 0.275 µW | 0.324 µW | 0.85× |

The two partitions are not identical — OpenSTA attributes a flop's clock-pin
capacitance to the clock net's driver and its clock-edge energy to the flop —
so the rows above are a decomposition, not a line-by-line identity. The
dominant term is unambiguous all the same, and it can be checked by hand
against the library:

> `gf180mcu_fd_sc_mcu9t5v0__dffq_1`'s `CLK` pin declares an `internal_power`
> table of **0.111 pJ rise + 0.167 pJ fall = 0.278 pJ per clock cycle**,
> unconditional on `D`. The netlist has **706 flip-flops**. At 1 MHz that is
> **196 µW before anything toggles** — on its own, 5.3× the estimate's entire
> ungated active figure.

The estimate multiplies each cell's internal energy by the *data* activity
(`p_internal += n * sec_activity * mean_int * freq`), i.e. it charges a flop
its clock-edge energy only on the 12.5 % of cycles where its data moves. That
is the single biggest error in the estimate, it is worth ~8× on the largest
term, and — the point worth keeping — **it was not visible before a netlist
existed.** A gate inventory can count flops; only a netlist and a library
together can say what each flop costs per edge.

The clock-delivery term's 4.7× has the same character: the estimate priced the
flops' own clock-pin capacitance plus a flat 2 fF-per-net wiring allowance,
against a real clock tree — 100 buffer and inverter cells inserted by CTS
(`clkbuf_*`/`clkload_*`/`clone_*` in the as-built netlist) — driving real
routed wire. The extracted wiring is **3.94 fF per net** at `nom` (3.51 at
`min`, 4.52 at `max`), i.e. the flat allowance was low by ~2×, plus 16.5 pF of
inter-net coupling capacitance the estimate had no term for at all.

### 4.4 What this does and does not change downstream

`sim/tools/power_rollup.py` still uses `design/digital_power_estimate.py` for
its digital term, and `npm run check:spec` still passes unchanged. That is
deliberate:

- The rollup's README-row verdicts are an operator-facing claim about a
  ratified row, and swapping in a number 10–14× larger changes that verdict.
  Doing it inside this issue would be exactly the "relax or re-decide a
  ratified row to make results fit" move CLAUDE.md forbids, in the opposite
  direction.
- The measured figure is not a drop-in replacement either. It covers *all* of
  `trng_top`'s digital logic as synthesized (2499 instances), not the three
  blocks the estimate inventories; it carries a uniform activity model where
  the estimate carries a per-section one; and it is a liberty-model result at
  gate level, which [DR-0021] §3 explicitly does not let stand in for a
  measured supply current.

What this document does is put the measurement on the record so the
substitution can be *decided* — with the delta, its causes, and its
uncertainty all stated — rather than performed silently here. **[#174]** owns
that decision, alongside [#150]'s area row and [DR-0017]'s idle row, all three
of which are now facing measured numbers instead of estimates.

---

## 5. What this establishes, and what it does not

**Establishes.**

- A gf180mcu static-timing and power flow exists, runs cold-start from one
  committed script over committed geometry, and covers the digital section at
  fifteen corners with extracted parasitics and a propagated clock. [DR-0009]
  rule 6's standing gap — *"digital timing closure is not covered by either
  side and remains owed"* — is closed, with a level ([DR-0021]) and a citation
  rule for the evidence it produces.
- The digital section **closes timing at every corner of the covered set**,
  with 23 ns of setup margin and 0.7 ns of hold margin at the respective
  binding corners, and an Fmax floor of 37 MHz — 37× [DR-0003]'s ratified
  raw-rate row and 9× its stretch row.
- The digital section's **area is measured**: 113 088 µm² of placed cell area,
  decomposed into a cell-count term and a library-track term.
- The digital section's **power is swept across the corner set** from the
  as-built netlist, and the previous estimate's error is not only quantified
  but attributed to specific modelling assumptions, two of which the netlist
  falsifies outright (clock gating that was never synthesized; flop internal
  energy priced at data activity).

**Does not establish.**

- **Not signoff.** Real extraction, but not a foundry-signed one; no IR drop
  (the DEF has no `SPECIALNETS` — the flow builds no power delivery at all,
  [#171] / [klayout-tools#1091][klt1091]); no on-chip variation derating; no
  multi-mode analysis.
- **Not an I/O timing result.** 68 unconstrained endpoints, by construction
  (§2).
- **Not a supply-current measurement.** Liberty power under a declared uniform
  activity. The real design's activity is data-dependent and, for a TRNG,
  deliberately unpredictable; a switching-activity annotation from the
  post-route gate-level run [#147] owns would be the next real improvement
  here, and would need no new tooling.
- **Not a whole-block figure.** Digital only. The entropy source and samplers
  are measured at transistor level in their own record families, and
  `sim/tools/power_rollup.py` is where the three are added up.
- **Not a claim about the RTL.** Every number is a property of *this*
  synthesis, *this* placement and *this* routing. A different synthesis run,
  a different utilization target or a different standard-cell library moves
  all three legs — the ×1.256 track-height term in §3 is that sensitivity
  made explicit.
- **Not corner coverage equal to the analog side's.** Five liberty decks, not
  27 P/V/T points, and `fs`/`sf` remain uncovered here as they are there
  ([DR-0006]).

---

## 6. Reproducing this

```sh
# the fifteen-corner sweep itself (~2 min; needs openroad + the gf180mcu PDK)
python3 sim/tb/digital-sta-power/run_sta.py --no-write

# one corner
python3 sim/tb/digital-sta-power/run_sta.py --liberty ss_125C_3v00 --rc max --no-write

# every figure in this document, from the committed records (no PDK needed)
python3 sim/tools/digital_corner_characterization.py

# ... plus the estimate comparison and the area decomposition (needs the PDK)
python3 sim/tools/digital_corner_characterization.py --estimate

# the gate CI runs
python3 sim/tools/digital_corner_characterization.py --check
```

Records: `sim/records/2026-08-17-digital-sta-power-{01..15}.md`, one per
corner, each with the generated Tcl and the full OpenROAD log as committed raw
output. The SPEF is not committed (3.3 MB × 15); each record carries its
sha256, byte count and summed capacitance so a re-run can be checked against
it.

[#111]: https://github.com/2AMLogic/gf180-trng/issues/111
[#124]: https://github.com/2AMLogic/gf180-trng/issues/124
[#140]: https://github.com/2AMLogic/gf180-trng/issues/140
[#143]: https://github.com/2AMLogic/gf180-trng/issues/143
[#145]: https://github.com/2AMLogic/gf180-trng/issues/145
[#147]: https://github.com/2AMLogic/gf180-trng/issues/147
[#150]: https://github.com/2AMLogic/gf180-trng/issues/150
[#171]: https://github.com/2AMLogic/gf180-trng/issues/171
[#174]: https://github.com/2AMLogic/gf180-trng/issues/174
[klt1091]: https://github.com/2AMLogic/klayout-tools/issues/1091
[klt1099]: https://github.com/2AMLogic/klayout-tools/issues/1099
[klt1100]: https://github.com/2AMLogic/klayout-tools/issues/1100
[DR-0003]: ../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0006]: ../spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md
[DR-0009]: ../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0013]: ../spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md
[DR-0017]: ../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
[DR-0019]: ../spec/decision-records/DR-0019-area-row-versus-output-fifo-dominated-digital-section.md
[DR-0020]: ../spec/decision-records/DR-0020-fifo-depth-set-to-two-against-power-area-and-streaming.md
[DR-0021]: ../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
