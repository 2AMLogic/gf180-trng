# Digital section: Fmax, area and power across the corner set

Status: measurement complete for issue [#145] — the digital column of [#124]'s
T1 checklist items **5** (full corner verification) and **8**
(characterization report), both of which [#140] recorded as FAIL with the same
one-line reason: *no static timing analysis exists at all, no real-layout
area, and no power across corners.*

All three now exist, from one measurement pass over one fixed piece of
geometry — the committed routed DEF `layout/digital/trng_top.def` ([#111],
[#171]), re-timed at fifteen corners with real extracted parasitics. Three
findings:

1. **Timing closes at every corner of the set**, with the worst setup slack
   +21.94 ns against the 50 ns constraint it was built to, binding at
   `ss_125C_3v00` with `max` interconnect. Fmax floor **35.63 MHz**, 1.8× the
   20 MHz the design was implemented at and 35.6× [DR-0003]'s ratified > 1 MHz
   raw rate. Hold closes everywhere too, worst +0.712 ns at `ff_n40C_3v60`
   with `min` interconnect.
2. **The real placed standard-cell area is 116 001 µm²** — **1.56×** the
   pre-synthesis inventory estimate of 74 485 µm², and **232 %** of the whole
   `< 0.05 mm²` README row on digital cell area alone. The 1.56× splits
   cleanly: ×1.21 from cell count/mix, ×1.26 from 9-track rather than 7-track
   rows — plus a small, new third term: [#171]'s tapcell/endcap/filler
   population, priced by OpenROAD's own `report_design_area` but invisible to
   that per-cell decomposition (§3).
3. **Measured power is 11–14× the library-based estimate** at the same corner,
   the same 1 MHz rate and the same switching-activity assumption. **Leakage
   no longer tracks the estimate as tightly as it did**: 0.89–3.76× of it,
   against 0.63–1.32× before [#171] added a tapcell/endcap/filler population
   to the DEF — real cells with their own leakage that the estimate was never
   asked to price, and whose *relative* contribution is largest exactly where
   the logic's own leakage is smallest (§4.1). The dynamic-power gap is still
   entirely a modelling one the estimate could not have avoided before
   synthesis existed: it prices a flip-flop's clock-edge internal energy at
   the *data* activity, and a flop pays that energy on every clock edge
   whether its data moves or not.

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
| DUT | `layout/digital/trng_top.def` — the committed routed DEF from [#111]/[#172], re-placed and re-CTS'd by [#171] to add the vddd/vss power delivery network (tapcells, endcaps and filler), unchanged and never re-placed by this sweep. 8638 DEF `COMPONENTS`: 2502 logical instances + 6136 tapcell/endcap/filler cells, all `gf180mcu_fd_sc_mcu9t5v0` |
| Driver | `sim/tb/digital-sta-power/run_sta.py` (gate-level testbench, [DR-0021]) |
| Engine | OpenSTA + OpenRCX inside OpenROAD `26Q3-1278-g4421880472` |
| PDK | `gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b` |
| Parasitics | OpenRCX extraction of the real routing → SPEF → `read_spef`. Not estimated: `rules.openrcx.gf180mcuD.{min,nom,max}` as shipped by the PDK |
| Clock | `clk`, **propagated** through the CTS-built tree in the DEF (not ideal), 50 ns / 20 MHz — the P&R run's own constraint |
| Grid | 5 liberty decks × 3 interconnect decks = **15 corners**, one record each |
| Records | `sim/records/2026-08-18-digital-sta-power-{01..15}.md`, superseding `sim/records/2026-08-17-digital-sta-power-{01..15}.md` (still committed, still accurate about the pre-[#171] DEF they name — [#183]) |

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

## 2. Timing: it closes everywhere, and Fmax has a floor of 35.6 MHz

| corner | setup slack | hold slack | clock skew | Fmax |
|---|---:|---:|---:|---:|
| **`ss_125C_3v00` / `max`** — setup binds | **+21.935 ns** | +2.440 ns | 0.201 ns | **35.63 MHz** |
| `ss_125C_3v00` / `nom` | +22.898 ns | +2.431 ns | 0.171 ns | 36.90 MHz |
| `ss_125C_3v00` / `min` | +23.686 ns | +2.425 ns | 0.153 ns | 38.00 MHz |
| `ss_n40C_3v00` / `max` | +30.925 ns | +1.699 ns | 0.151 ns | 52.42 MHz |
| `ss_n40C_3v00` / `nom` | +31.595 ns | +1.693 ns | 0.128 ns | 54.33 MHz |
| `ss_n40C_3v00` / `min` | +32.143 ns | +1.688 ns | 0.113 ns | 56.00 MHz |
| `tt_025C_3v30` / `max` | +35.853 ns | +1.234 ns | 0.113 ns | 70.69 MHz |
| `tt_025C_3v30` / `nom` | +36.355 ns | +1.230 ns | 0.096 ns | 73.29 MHz |
| `tt_025C_3v30` / `min` | +36.763 ns | +1.226 ns | 0.084 ns | 75.54 MHz |
| `ff_125C_3v60` / `max` | +37.876 ns | +1.029 ns | 0.094 ns | 82.48 MHz |
| `ff_125C_3v60` / `nom` | +38.301 ns | +1.026 ns | 0.079 ns | 85.47 MHz |
| `ff_125C_3v60` / `min` | +38.646 ns | +1.022 ns | 0.070 ns | 88.07 MHz |
| `ff_n40C_3v60` / `max` | +41.788 ns | +0.717 ns | 0.071 ns | 121.76 MHz |
| `ff_n40C_3v60` / `nom` | +42.084 ns | +0.714 ns | 0.060 ns | 126.32 MHz |
| **`ff_n40C_3v60` / `min`** — hold binds | +42.321 ns | **+0.712 ns** | 0.054 ns | 130.22 MHz |

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
**0.0082 %** worst case over the fifteen corners — which is the evidence that
licenses quoting either. `--check` fails if that agreement ever exceeds 1 %,
because a design whose slack is no longer linear in the clock period is one
where the extrapolated number has quietly stopped meaning anything.

The Fmax spread over the set is **35.63 → 130.22 MHz, 3.65×**, and the
interconnect axis alone moves it 6.2 % at the slow corner (38.00 → 35.63 MHz)
against the liberty axis's 3.4×. Wires matter here; devices matter much more.

### Reconciling with the place-and-route report

`layout/digital/reports/place_and_route.json` — rebuilt by [#171] alongside
the DEF, so this is the post-PDN report — reports **+27.7656 ns** at
`ss_125C_3v00`, and this sweep reports **+22.898 ns** at the same liberty
corner with `nom` interconnect. Both are right; they are different
measurements, and each record carries the intermediate figure that separates
them:

| | slack at `ss_125C_3v00` |
|---|---:|
| P&R report — ideal clock, global-routing-*estimated* parasitics | +27.766 ns |
| this sweep, ideal clock, OpenRCX-*extracted* parasitics (`worst_setup_slack_ideal_clock_ns`) | +22.998 ns |
| this sweep, propagated clock, extracted parasitics (the headline) | +22.898 ns |

So of the 4.87 ns difference, **4.77 ns is extraction versus estimation** and
**0.100 ns is the real clock tree** (`clock_tree_cost_ns`, the largest such
cost in the set is 0.119 ns). Real extraction is materially more pessimistic
than the router's own RC estimate at this corner, and the CTS tree is nearly
free — which is worth knowing before anyone tries to explain a slack
difference by the clock model. Both terms moved from the pre-[#171]
measurement (which found 3.83 ns / 0.145 ns at the same corner) — [#171]'s
re-run is a genuinely different placement and clock tree, not the same layout
with rails added (`layout/digital/README.md`'s "The power distribution
network" section), so a shift here is expected and is not read as a
regression.

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

## 3. Area: 116 001 µm² placed, 1.56× the inventory estimate

| | cell area | cells | library |
|---|---:|---:|---|
| **Measured** — OpenROAD `report_design_area` over the routed DEF | **116 000.6 µm²** | 8638 DEF `COMPONENTS` (2502 logical + 6136 tapcell/endcap/filler, [#171]) | `mcu9t5v0` (9-track) |
| Estimate — `layout/floorplan/reports/area.json`, region `digital` | 74 485.3 µm² | 1655 inventoried cells | `mcu7t5v0` (7-track) |
| Delta | **+41 515.3 µm² = ×1.557** | +847 logical | — |

Both figures are *standard-cell* area, which is what makes them comparable.
The **die** figure in the place-and-route report (301 198 µm²) is not
comparable to either: it follows arithmetically from that run's own 40 %
utilization target, which was chosen to leave routing headroom on a first
attempt, and `layout/digital/README.md` says so at length. This document does
not difference it against anything.

**Where the 1.56× comes from.** Pricing the *same as-built netlist* against
the 7-track library separates the two axes that moved at once — but only over
the **2502 logical** instances in `trng_top.pnr.v`; [#171]'s 6136
tapcell/endcap/filler cells have no functional pins and so never appear in a
gate-level Verilog netlist, and are handled separately below:

| | cell area | µm²/cell | step |
|---|---:|---:|---|
| inventory estimate, 7-track | 74 485.3 µm² | 45.01 | — |
| as-built **logical** netlist priced 7-track | 90 244.7 µm² | 36.07 | **×1.212** cell count / mix |
| as-built **logical** netlist, 9-track (what was built) | 113 330.6 µm² | 45.30 | **×1.256** track height |
| + [#171]'s tapcell/endcap/filler population | +2 670.0 µm² | n/a (no logical netlist entry) | **×1.024** PDN population |
| = measured, `report_design_area` | 116 000.6 µm² | — | **×1.557** total |

Three things follow, and the tapcell/endcap/filler term is the one that did
not exist before [#171]:

- **The inventory under-counted cells by 51 %** (1655 → 2502) but
  **over-priced the average cell by 25 %** (45.01 vs 36.07 µm² in like-for-like
  7-track terms). Those errors partly cancel, which is why the naive
  per-instance averages (45.01 estimated, 45.30 measured) look like a
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
- **[#171]'s power-delivery cells cost a further 2.4 % on top.** 6136
  tapcell/endcap/filler instances (75 % of the DEF's 8638 `COMPONENTS`, by
  count) are placement/DRC infrastructure, not logic, so they carry no port
  list and are invisible to a netlist-driven crosscheck — this is why the
  "as-built logical netlist, 9-track" row above (113 330.6 µm², summed from
  `trng_top.pnr.v`'s instances against the liberty deck) no longer equals
  OpenROAD's own `report_design_area` (116 000.6 µm²) the way it did before
  [#171]: they agreed to rounding when the DEF carried no `SPECIALNETS` and no
  fill; now they are 2.30 % apart, and the gap is entirely those 6136 cells.
  `sim/tools/digital_corner_characterization.py --estimate` prints this gap as
  "liberty sum vs OpenROAD's own `report_design_area`" so a future re-run
  cannot silently start treating the two figures as interchangeable again.

**Against the ratified row.** The `< 0.05 mm²` README row is 50 000 µm² for
the *whole block*. The digital section's placed cell area alone is
**232.0 %** of it (the estimate was 149 %), and at a realistic 60 % / 80 %
placement utilization the digital section alone implies **193 334 / 145 001
µm²**, i.e. 387 % / 290 % of the row. The entropy source, samplers, guard
rings and isolation channels together are 13.1 % of the row
(`layout/floorplan/README.md`).

The row is **not edited, and no design change is proposed here.** [DR-0019]
(`Proposed`) already routes this miss and prices the available responses
against FIFO depth; [DR-0020] (`Proposed`) proposes the depth change itself;
[#150] owns the row. What this section adds is that the miss is now measured
rather than estimated, and 55.7 % larger than the estimate [DR-0019] was
written against — so whichever response is chosen, it has to close a bigger
gap than that record's own sensitivity table assumed. Re-deriving [DR-0019]'s
depth table against this measurement is that record's follow-up, not this
document's.

---

## 4. Power: 11–14× the estimate on dynamic, and leakage now carries a PDN term

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
| `ss_n40C_3v00` | 401.7 µW | 8.03 mW | 90.5 µW | 314.8 nW | 104.9 nA |
| `ss_125C_3v00` | 431.8 µW | 8.56 mW | 98.6 µW | 3.950 µW | 1.317 µA |
| `tt_025C_3v30` | 517.7 µW | 10.35 mW | 117.4 µW | 409.2 nW | 124.0 nA |
| `ff_n40C_3v60` | 635.5 µW | 12.70 mW | 145.4 µW | 473.4 nW | 131.5 nA |
| **`ff_125C_3v60`** — both maxima | **698.4 µW** | **13.70 mW** | 158.9 µW | **14.21 µW** | **3.946 µA** |

Active power binds at `ff_125C_3v60`/`max` (712.4 µW at 1 MHz, 13.98 mW at
20 MHz) and leakage binds at the same liberty corner — hot, fast,
high-supply, which is where the README's Power row already binds its idle
half (`ff` / +10 % / +125 °C). Its active half names `ff` / +10 % without a
temperature; on this sweep the hot `ff` deck is the worse of the two `ff`
decks for total power as well, by 10 %. Leakage is interconnect-independent,
as it must be, so its binding corner is a liberty corner rather than a pair.

**Two things this does not say.** It does not say the block's active power is
698 µW: the digital section is one of three contributors and the whole-block
rollup (`sim/tools/power_rollup.py`) is what adds them up. And it does not
supersede that rollup's own digital term today — see §4.4.

**Against the `< 1 µA` idle row.** [DR-0017] records a 4.5× miss on that row
and attributes it to ungated standard-cell leakage in the digital section,
from the same library-based estimate (4.43 µA of digital idle leakage at
`ff` / +125 °C / 3.60 V, the row's own binding corner). The measurement at
that corner is **3.946 µA — 395 % of the row**, i.e. the miss is real and
unchanged in kind, and now **0.89× the size** the estimate predicted (was
0.63× against the pre-[#171] DEF). The whole of that shift — leakage 42 %
higher at this corner, and a much larger *relative* jump at the slow/cold
corners (§4.2) — is [#171]'s tapcell/endcap/filler population: those cells
are real, placed, laid-out gf180mcu instances with their own leakage, and
OpenSTA's `report_power` prices every cell OpenROAD placed, not only the ones
with a functional pin `trng_top.pnr.v` names. Two caveats before either
number is used anywhere: it is the library's state-independent default
leakage, where the estimate carries an input-state range (2.86 .. 4.43 µA);
and the measurement covers the whole synthesized digital section *plus* its
power-delivery infrastructure, a broader scope than the estimate's
three-block logic-only inventory in both the [#171] direction (extra cells)
and the pre-[#171] direction (no PDN estimate exists to compare against).
[DR-0017] remains the record that routes this row, and its proposed
replacement figure was set from the estimate, not from this.

### 4.2 Measured versus the library-based estimate

Both at 1 MHz, both at the same liberty corner, both at 0.25 transitions/cycle:

| corner | measured | estimate (headline) | estimate (ungated) | ×headline | ×ungated | leakage ratio |
|---|---:|---:|---:|---:|---:|---:|
| `ss_n40C_3v00` | 401.7 µW | 15.29 µW | 29.57 µW | 26.3× | 13.6× | 1.42× |
| `ss_125C_3v00` | 431.8 µW | 16.69 µW | 31.59 µW | 25.9× | 13.7× | 3.76× |
| `tt_025C_3v30` | 517.7 µW | 19.13 µW | 36.79 µW | 27.1× | 14.1× | 1.45× |
| `ff_n40C_3v60` | 635.5 µW | 23.12 µW | 44.33 µW | 27.5× | 14.3× | 1.54× |
| `ff_125C_3v60` | 698.4 µW | 39.38 µW | 65.77 µW | 17.7× | 10.6× | 0.89× |

**Why two estimate columns.** `design/digital_power_estimate.py`'s headline
credits the two output FIFOs with clock gating — `clock_duty` of 1/256 and
1/2048 on 512 of the 658 inventoried flops, which its own comment calls "the
single largest error available in the dynamic term". The synthesized netlist
settles that assumption: it contains **no integrated clock gates at all**.
Yosys mapped the RTL's write enables to ordinary feedback multiplexing instead
— the netlist carries **553 `mux2` cells and zero clock-gating cells** — so
every one of the 708 flip-flops in `layout/digital/trng_top.pnr.v` is clocked
on every cycle. The estimate's own `interface_mux_feedback` variant is
therefore the like-for-like column, and both are shown so that the comparison
cannot be read as turning on which one is picked.

**Leakage no longer holds up the way it did.** The estimate's leakage column
has no modelling freedom in it — it is read straight out of characterised
library data for the 1655 inventoried *logic* cells — and before [#171] that
made it the column that agreed best with measurement (0.63× to 1.32×). It no
longer does: 0.89× to **3.76×**, and the spread is not noise. [#171] added
6136 tapcell/endcap/filler instances to the DEF that the estimate has no way
to know about (it inventories logic, not power-delivery infrastructure), and
their leakage is a roughly *fixed* addition per corner (the same physical
cells regardless of liberty deck) landing on top of a logic leakage that
itself varies by three orders of magnitude across the corner set (314.8 nW at
`ss_n40C_3v00` to 14.21 µW at `ff_125C_3v60`, §4.1). A fixed addition is a
small fraction of a large number and a large fraction of a small one — which
is exactly the pattern above: the ratio is worst (3.76×) at `ss_125C_3v00`,
where the logic's own leakage is smallest among the corners this table shows,
and closest to holding (0.89×) at `ff_125C_3v60`, where it is largest. The
dynamic-power gap, below, is unaffected by any of this: it was never a
leakage question.

### 4.3 Where the dynamic gap is

At `tt_025C_3v30`/`nom`, 1 MHz, measured 517.7 µW against the ungated estimate's
36.79 µW:

| term | measured | estimate (ungated) | ratio |
|---|---:|---:|---:|
| cell internal energy (`Sequential` + `Combinational` internal) | 316.5 µW | 4.50 µW (`p_internal`) | 70× |
| clock delivery (`Clock` group: tree buffers + clock net) | 117.4 µW | 24.05 µW (`p_clock`) | 4.9× |
| data-net switching (`Sequential` + `Combinational` switching) | 83.5 µW | 7.91 µW (`p_data`) | 10.6× |
| leakage | 0.409 µW | 0.324 µW | 1.26× |

The two partitions are not identical — OpenSTA attributes a flop's clock-pin
capacitance to the clock net's driver and its clock-edge energy to the flop —
so the rows above are a decomposition, not a line-by-line identity. The
dominant term is unambiguous all the same, and it can be checked by hand
against the library:

> `gf180mcu_fd_sc_mcu9t5v0__dffq_1`'s `CLK` pin declares an `internal_power`
> table of **0.111 pJ rise + 0.167 pJ fall = 0.278 pJ per clock cycle**,
> unconditional on `D`. The netlist has **708 flip-flops**. At 1 MHz that is
> **196.8 µW before anything toggles** — on its own, 5.3× the estimate's entire
> ungated active figure.

The estimate multiplies each cell's internal energy by the *data* activity
(`p_internal += n * sec_activity * mean_int * freq`), i.e. it charges a flop
its clock-edge energy only on the 12.5 % of cycles where its data moves. That
is the single biggest error in the estimate, it is worth ~8× on the largest
term, and — the point worth keeping — **it was not visible before a netlist
existed.** A gate inventory can count flops; only a netlist and a library
together can say what each flop costs per edge.

The clock-delivery term's 4.9× has the same character: the estimate priced the
flops' own clock-pin capacitance plus a flat 2 fF-per-net wiring allowance,
against a real clock tree — 101 buffer and inverter cells inserted by CTS
(`clkbuf_*`/`clkload_*` in the as-built netlist; [#171]'s re-run built a
slightly different tree than the 100 cells the pre-[#171] DEF carried) —
driving real routed wire. The extracted wiring is **4.98 fF per net** at
`nom` (4.39 at `min`, 5.81 at `max`), i.e. the flat allowance was low by
~2–3×, plus 15.7 pF of inter-net coupling capacitance the estimate had no
term for at all. The leakage row's 1.26× is §4.2's PDN-leakage story again at
this one corner, not a new effect.

### 4.4 What this does and does not change downstream

> **Update — [#174]/[DR-0023] (Proposed, 2026-08-21) has since made the
> substitution this section deferred.** `sim/tools/power_rollup.py` now reads
> its digital term from this document's own measured record family via
> `sim/tools/digital_corner_characterization.py`, not from
> `design/digital_power_estimate.py` — the whole-block active row moves from
> "met, 86.6 %" to "missed, 224.5 %", and [DR-0017]'s idle miss narrows from
> 4.46 µA/4.5× to 3.979 µA/~4.0×. `design/digital_power_estimate.py` is
> unchanged and still runs, printed as context. `npm run check:spec` passes
> against the new arithmetic; the paragraphs below are left as this section's
> author wrote them, because the deferral they describe was real at the time
> and the record that resolved it (DR-0023) is not ratified — the row's own
> ratified target text is unedited either way. See [DR-0023] for the decision
> and its reasoning, and `README.md`'s Power row for the current evidenced
> figures.

`sim/tools/power_rollup.py` still uses `design/digital_power_estimate.py` for
its digital term, and `npm run check:spec` still passes unchanged. That is
deliberate:

- The rollup's README-row verdicts are an operator-facing claim about a
  ratified row, and swapping in a number 11–14× larger changes that verdict.
  Doing it inside this issue would be exactly the "relax or re-decide a
  ratified row to make results fit" move CLAUDE.md forbids, in the opposite
  direction.
- The measured figure is not a drop-in replacement either. It covers *all* of
  `trng_top`'s digital logic as synthesized (2502 instances) plus [#171]'s
  power-delivery cells, not the three blocks the estimate inventories; it
  carries a uniform activity model where the estimate carries a per-section
  one; and it is a liberty-model result at gate level, which [DR-0021] §3
  explicitly does not let stand in for a measured supply current.

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
  with 21.9 ns of setup margin and 0.7 ns of hold margin at the respective
  binding corners, and an Fmax floor of 35.6 MHz — 35.6× [DR-0003]'s ratified
  raw-rate row and 8.9× its stretch row.
- The digital section's **area is measured**: 116 001 µm² of placed cell
  area, decomposed into a cell-count term, a library-track term, and (new
  since [#171]) a power-delivery-cell term.
- The digital section's **power is swept across the corner set** from the
  as-built netlist, and the previous estimate's error is not only quantified
  but attributed to specific modelling assumptions, two of which the netlist
  falsifies outright (clock gating that was never synthesized; flop internal
  energy priced at data activity) — plus, since [#171], a real
  tapcell/endcap/filler leakage term the estimate has no way to price at all.

**Does not establish.**

- **Not signoff.** Real extraction of a real routed DEF — [#171] means it is
  no longer true that the DEF carries no power geometry at all, so this
  extraction now sees the `SPECIALNETS` rail/strap network OpenRCX did not
  before — but it is still not a foundry-signed extraction, still carries no
  IR drop (a static per-cell parasitic extraction is not an IR-drop
  analysis, and none is run here), no on-chip variation derating, and no
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

## 5a. The functional half of item 7, and what it does and does not add here

This document is the **static** half of T1 item 7's digital column: STA, area
and liberty power over the same routed database. The **dynamic** half is
[#147]'s post-route gate-level re-run of the digital functional suite,
`sim/tb/trng-top-post-route/`, recorded at
[`level: gate-simulation`][DR-0022] (a sibling of this document's
[`level: gate`][DR-0021], deliberately *not* the same value) — currently
`sim/records/2026-08-18-trng-top-post-route-01.md`, re-run against the same
powered `trng_top.pnr.v`/`trng_top.sdf` this document's own DEF pairs with
([#171], [#183]); its pre-[#171] predecessor,
`sim/records/2026-08-17-trng-top-post-route-01.md`, remains committed as
append-only evidence about the netlist it names. Cite the current one for
what it establishes and not for anything on this page:

| | this document (`level: gate`) | the re-run (`level: gate-simulation`) |
|---|---|---|
| What runs | OpenSTA + liberty power over the routed DEF, 15 corners | Icarus + cocotb over `trng_top.pnr.v`, SDF cell delays annotated, 1 corner |
| Establishes | timing closure, Fmax floor, placed area, swept power | that the as-built netlist reproduces the RTL's cycle-by-cycle behaviour, bit-exactly, over the digital suite's stimulus |
| Must not be cited for | measured supply current, signoff, I/O timing | **timing of any kind** — the simulator applies no timing checks at all, so a clean run there says nothing about margin |

Two things the re-run contributes that this page cannot:

- **The netlist is functionally the RTL.** Every number here is a property of
  *this* synthesis, placement and routing (§5, "Not a claim about the RTL"). The
  re-run closes the complementary question — that the thing whose timing and
  power are reported above still *does* what the RTL does — with identical
  output-trace hashes over 3197 cycles of the digital suite's own stimulus.
- **Zero `x` on a pin out of reset**, across those cycles, despite 512 of the
  708 flops having no reset port. That is a property of the netlist's own
  availability gating and is invisible to static analysis.

And one thing it does **not** contribute, contrary to what §5's
"Not a supply-current measurement" bullet anticipates: a switching-activity
annotation. The re-run produces per-cycle output traces at the *pins*, not
per-net toggle counts, so wiring its activity into a liberty power run is still
future work rather than something already available.

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

Records: `sim/records/2026-08-18-digital-sta-power-{01..15}.md`, one per
corner, each with the generated Tcl and the full OpenROAD log as committed raw
output. The SPEF is not committed (3.3 MB × 15); each record carries its
sha256, byte count and summed capacitance so a re-run can be checked against
it. The pre-[#171] `sim/records/2026-08-17-digital-sta-power-{01..15}.md`
remain committed as append-only evidence about the DEF they name and hash,
but no longer describe `layout/digital/`'s current artefacts (§1, [#183]).

[#111]: https://github.com/2AMLogic/gf180-trng/issues/111
[#124]: https://github.com/2AMLogic/gf180-trng/issues/124
[#140]: https://github.com/2AMLogic/gf180-trng/issues/140
[#143]: https://github.com/2AMLogic/gf180-trng/issues/143
[#145]: https://github.com/2AMLogic/gf180-trng/issues/145
[#147]: https://github.com/2AMLogic/gf180-trng/issues/147
[#150]: https://github.com/2AMLogic/gf180-trng/issues/150
[#171]: https://github.com/2AMLogic/gf180-trng/issues/171
[#172]: https://github.com/2AMLogic/gf180-trng/issues/172
[#174]: https://github.com/2AMLogic/gf180-trng/issues/174
[#183]: https://github.com/2AMLogic/gf180-trng/issues/183
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
[DR-0022]: ../spec/decision-records/DR-0022-post-route-gate-level-simulation-records.md
[DR-0023]: ../spec/decision-records/DR-0023-power-rollup-digital-term-becomes-measured-gate-level-power.md
