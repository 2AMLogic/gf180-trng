# Digital section: Fmax, area and power across the corner set

Status: measurement complete for issue [#145] — the digital column of [#124]'s
T1 checklist items **5** (full corner verification) and **8**
(characterization report), both of which [#140] recorded as FAIL with the same
one-line reason: *no static timing analysis exists at all, no real-layout
area, and no power across corners.* Also carries [#233]'s answer to
[DR-0025]'s deferred question about the six inter-region trunks that land on
this block's own pins — see §2a, including the max-transition violation
([#237]) that asking it uncovered and [#240] closed (2026-09-15).

All three now exist, from one measurement pass over one fixed piece of
geometry — the committed routed DEF `layout/digital/trng_top.def` ([#111],
[#171], [#240]), re-timed at fifteen corners with real extracted parasitics.
Four findings:

1. **Timing closes at every corner of the set**, with the worst setup slack
   +24.88 ns against the 50 ns constraint it was built to, binding at
   `ss_125C_3v00` with `max` interconnect. Fmax floor **39.80 MHz**, 2.0× the
   20 MHz the design was implemented at and 39.8× [DR-0003]'s ratified > 1 MHz
   raw rate. Hold closes everywhere too, worst +0.707 ns at `ff_n40C_3v60`
   with `min` interconnect.
2. **The real placed standard-cell area is 118 975 µm²** — **1.60×** the
   pre-synthesis inventory estimate of 74 485 µm², and **238 %** of the whole
   `< 0.05 mm²` README row on digital cell area alone. The 1.60× splits
   cleanly: ×1.24 from cell count/mix, ×1.26 from 9-track rather than 7-track
   rows — plus a small, new third term: [#171]'s tapcell/endcap/filler
   population, priced by OpenROAD's own `report_design_area` but invisible to
   that per-cell decomposition (§3). [#240]'s buffering (below) accounts for
   28 of the logical instances in this figure.
3. **Measured power is 11–14× the library-based estimate** at the same corner,
   the same 1 MHz rate and the same switching-activity assumption. **Leakage
   no longer tracks the estimate as tightly as it did**: 0.92–3.75× of it,
   against 0.63–1.32× before [#171] added a tapcell/endcap/filler population
   to the DEF — real cells with their own leakage that the estimate was never
   asked to price, and whose *relative* contribution is largest exactly where
   the logic's own leakage is smallest (§4.1). The dynamic-power gap is still
   entirely a modelling one the estimate could not have avoided before
   synthesis existed: it prices a flip-flop's clock-edge internal energy at
   the *data* activity, and a flop pays that energy on every clock edge
   whether its data moves or not.
4. **The six digital-facing inter-region trunks ([#233]) were never the
   problem — and the something else that was is now fixed.** The trunks' own
   Metal4 RC, stated as a `set_input_transition` on
   `clk`/`rst_n`/`raw_bit`/`raw_valid`/`ring_bit[0]`/`ring_bit[1]` and derived
   from the as-built geometry, is 2.1–8.2 **ps** against a library
   `max_transition` of 4.4–13.2 ns: **none of the six violates at any of the
   fifteen corners**, with ≥ 535× margin at the tightest of them, and neither
   Fmax nor worst slack moves measurably (§2a). Asking that question for the
   first time, however, also asked OpenSTA for the design's *own*
   max-transition check — and, on the DEF committed before [#240], **9 of the
   15 corners violated it, at 33–94 internal pins, worst −1.59 ns at
   `tt_025C_3v30`/`max`** (§2a). That was pre-existing, present with no
   interface load at all, and on none of the six trunk nets. [#237] measured
   it per net and per corner: **four high-fanout nets** across `u_interface`
   and `u_conditioner`, carrying ≤ 1.84 % of total power — but the design's
   critical path passed through them at every violating corner, so §2's old
   +21.94 ns margin was a margin on an *extrapolated* path. [#240] stated
   `max_transition_ns`/`max_capacitance_pf` to `layout/digital/build.py`
   once [klayout-tools#1860][klt1860] made that expressible, rebuilt, and
   the re-minted fifteen-corner family reports **zero** `max_transition`/
   `max_capacitance` violations at every corner — closed, not merely bounded
   (§2a).

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

## 0. Update — re-measured at DR-0020's `FIFO_DEPTH = 2` (issue [#255])

> **Superseded in part by §0a ([#264]).** The "depth 2" column below
> describes [#255]'s first depth-2 build, which violated the library's own
> `max_transition` check. [#264] rebuilt it with a re-tuned constraint; §0a
> carries the figures for the DEF committed today. This section is kept
> verbatim as append-only history.

**Sections 1–5a below describe the `FIFO_DEPTH = 8` build** (the `sim/
records/2026-09-15-digital-sta-power-*.md` family, [#111]/[#171]/[#240]'s
DEF). They are retained verbatim as an append-only historical record, the
same treatment `layout/digital/README.md` gives the pre-[#171]/pre-[#240]
numbers — they no longer describe `layout/digital/`'s current committed
artefacts.

[#254] set [DR-0020]'s ratified `FIFO_DEPTH = 2` in the regmap, the RTL
parameter default and the pre-synthesis inventory estimate, but deliberately
did not re-synthesize or re-place-and-route — that was this issue's own job.
[#255] regenerated `design/trng_top/trng_top.synth.v` (`design/synth.py`)
and `layout/digital/trng_top.def`/`.gds`/`.pnr.v`/`.sdf`
(`layout/digital/build.py`, `gen_sdf.py`) at the new depth, LVS-matched the
new layout against its own as-built netlist (`layout/digital/lvs.py`,
`status: match`, `mismatch_count: 0`), and re-ran this document's own
fifteen-corner sweep against the new DEF. New records:
`sim/records/2026-09-19-digital-sta-power-{01..15}.md`.

| | depth 8 (§1–§4, historical) | depth 2 (current) |
|---|---:|---:|
| Placed instances | 8594 DEF `COMPONENTS` (2533 logical) | 4436 DEF `COMPONENTS` (1458 logical) |
| Setup binding slack | +24.876 ns at `ss_125C_3v00`/`max` | +23.880 ns at `ss_125C_3v00`/`max` |
| Hold binding slack | +0.7071 ns at `ff_n40C_3v60`/`min` | +0.6935 ns at `ff_n40C_3v60`/`min` |
| Fmax floor | 39.803 MHz at `ss_125C_3v00`/`max` | 38.284 MHz at `ss_125C_3v00`/`max` |
| Placed cell area | 118 975.4 µm² | **59 465.1 µm²** |
| vs the pre-synthesis inventory (now depth-2, 863 cells, 33 654.6 µm²) | ×1.597 (vs the depth-8, 1655-cell, 74 485.3 µm² inventory) | **×1.767** |
| Active power @ 1 MHz (max) | 712.4 µW at `ff_125C_3v60`/`max` | **358.5 µW** at `ff_125C_3v60`/`max` |
| Leakage (max) | 14.62 µW / 4.062 µA at `ff_125C_3v60` | **7.107 µW / 1.974 µA** at `ff_125C_3v60` |
| Library `max_transition` violations | 0 of 15 corners ([#240] closed [#237]'s 9-of-15 residual) | **11 of 15 corners** — see below |
| #233 trunk-net `max_transition` violations | 0 of 15 corners | 0 of 15 corners (unchanged) |

**The area ratio moved from ×1.597 to ×1.767 even though both sides are now
priced at the same depth.** That is expected, not a regression: §3's own
decomposition (cell-count/mix term, 9-track-vs-7-track term) is a property of
*how* the estimate under- or over-counts a design's shape, not of its raw
size, and a much smaller FIFO removes area from both sides unevenly (the two
FIFOs' `dffrnq_1`/`mux2_1`/`icgtp_1` rows are a smaller share of a depth-2
design's total logic than of a depth-8 one). Re-deriving §3's full
cell-count/track-height/PDN-population split for the depth-2 netlist is
follow-up work, not repeated here in the summary.

**The library's own `max_transition` check regressed: 0 → 11 of 15
corners.** `layout/digital/build.py`'s `CONSTRAINTS` (`max_transition_ns:
8.0`, `max_capacitance_pf: 0.35`, [#240]) were tuned against the depth-8
topology's own four high-fanout nets and reused unchanged for this
depth-2 re-place-and-route. They no longer clear every corner on the smaller
design's different net topology: the depth-2 DEF violates at **11 of 15**
corners, worst −1.6041 ns at `tt_025C_3v30`/`max` with 75 violating pins
(records' own `max_slew_slack_ns`/`max_slew_violations` fields) — worse than
the nine corners [#237] originally found and [#240] closed at depth 8. The
one invariant that does still hold: **none of the six #233 trunk-net pins
violates, at any of the fifteen corners** (`interface_load_max_slew_violations:
0` in every one of the fifteen new records) — the regression is
internal to the design, not on the inter-region interface. Re-tuning
`CONSTRAINTS` for the depth-2 topology (the same lever [#240] pulled for
depth 8) is a natural follow-up, not performed here: this issue's job was to
regenerate the physical artefacts and characterize what they measure, not to
re-close a design-rule residual its own predecessor issue already accepted
once as bounded rather than eliminated.

`sim/tools/digital_corner_characterization.py`'s `RECORDED` table and
`MEASURED_NETLIST_FIFO_DEPTH` constant now reflect this depth-2 family;
`--check` (wired into `npm run check:spec`) gates on it, not on the
historical depth-8 figures sections 1–5a quote.

---

## 0a. Update — `max_transition` re-tuned for the depth-2 topology (issue [#264])

**§0 above found the depth-2 re-place-and-route ([#255]) violating the
library's own `max_transition` at 11 of the 15 corners**, because it reused
`layout/digital/build.py`'s `CONSTRAINTS` (`max_transition_ns: 8.0`,
`max_capacitance_pf: 0.35`) unchanged from [#240]'s depth-8 tuning. This
issue re-derives `max_transition_ns` for the depth-2 topology, the same way
[#240] derived it at depth 8 — per-net decomposition over the committed DEF,
via `sim/tb/digital-sta-power/max_transition_probe.py` — and rebuilds.

### What the probe found on the (still-violating) depth-2 DEF

The residual was two nets, not [#237]'s original four:

| net | pins | driver | driver cell |
|---|---:|---|---|
| `net4` | 42 | `fanout4/Z` | `gf180mcu_fd_sc_mcu9t5v0__dlyd_1` |
| `u_interface/_0519_` | 33 | `u_interface/_0975_/Z` | `gf180mcu_fd_sc_mcu9t5v0__and4_1` |

Neither is on one of [#233]'s six trunk nets. The probe's own
`pnr_corner_target` derivation (the same arithmetic [#240]'s docstring
walks through) computed a naive required `set_max_transition` at the P&R
corner (`ss_125C_3v00`) of **10.99 ns**, binding at `ff_125C_3v60`/`rc-min`
— but that number describes what the *measured* slew would need to be, not
what value to hand `repair_design`, and the existing `8.0 ns` constraint was
already tighter than 10.99 ns while still leaving the design's own P&R
corner measuring a worst slew of **14.1 ns** (above its own 13.2 ns limit).
That gap between the constraint `repair_design` is handed and the slew the
rebuilt, fully-extracted DEF actually measures — the same
placement-estimate-versus-extracted-parasitics gap [#240]'s own docstring
describes — is wider for this topology's two nets than it was for depth-8's
four, so the naive figure could not be used directly.

### The fix: `max_transition_ns: 8.0` → `4.0`, unchanged `max_capacitance_pf: 0.35`

Rather than iterate from the naive 10.99 ns figure, `layout/digital/
build.py`'s `CONSTRAINTS.max_transition_ns` was tightened directly to
**4.0 ns** — chosen to match the family's own tightest corner limit
(`ff_n40C_3v60`, 4.4 ns) rather than a fraction of the P&R corner's 13.2 ns
limit the way [#240]'s 8.0 ns (60.6 % of that limit) was. Rebuilding once
against that target cleared the design on the first attempt:
`sim/tb/digital-sta-power/max_transition_probe.py`'s post-rebuild survey
reports **zero** `max_transition` and **zero** `max_capacitance` violations
at all fifteen corners, with the worst measured slew at 21–39 % of its
corner's own limit (lowest `ss_n40C_3v00/rc-min`: 2.34 ns against 11.2 ns;
highest `ff_125C_3v60/rc-max`: 2.04 ns against 5.2 ns; the P&R corner
`ss_125C_3v00/rc-max`: 4.11 ns against 13.2 ns).

The pre-rebuild figures above (the two nets and the 10.99 ns derivation)
can be reproduced by running `max_transition_probe.py` without `--check`
against [#255]'s DEF (the parent commit of this change). The 14.1 ns
figure is [#255]'s own `ss_125C_3v00`/`max` record: a 13.2 ns limit with
−0.905 ns slack.

### What `layout/digital/reports/place_and_route.json`'s per-corner counts mean

The klt version used for this rebuild adds per-corner
`max_transition_violation_count`/`max_capacitance_violation_count` fields
to the place-and-route report. Its aggregate reads 720 and 3. **These are
not the library check this section gates on, and they do not contradict
the zero above.** klt's retained OpenROAD logs show both counts are checked
against the **design-level limits this build stated to `repair_design`**
(`set_max_transition 4.0`, `set_max_capacitance 0.35`), using klt's own
nominal-interconnect parasitics, across every `.lib` deck the library
ships:

- **Transition (720):** every violating pin is at a 1.62 V or 1.80 V deck
  (`ss_125C_1v62` 720, `ss_n40C_1v62` 554, `tt_025C_1v80` 20). This block
  does not run at those voltages. At the other twelve decks, including all
  five in this block's 3.3 V family, the count is 0 against the 4.0 ns
  target.
- **Capacitance (3):** 1–3 pins at 11 of the 15 decks, always from the
  same three buffers that `repair_design` inserted itself
  (`u_interface/place67`, `u_interface/max_cap68`, `u_interface/max_cap69`).
  Each drives 0.35–0.38 pF against the 0.35 pF target, which misses by at
  most 0.03 pF. Those pins' own library `max_capacitance` limits are not
  exceeded at any of the fifteen swept corners, per the probe's table.

So this rebuild clears the library's own checks everywhere. It misses its
own self-imposed `max_capacitance_pf: 0.35` guard-band by up to 0.03 pF on
three inserted buffers. That target was never binding (see
`layout/digital/build.py`'s comment), so this is recorded here rather than
treated as a residual to fix. The report itself does not say which limit
its counts were checked against; the only way to tell is to read the raw
OpenROAD logs. That is filed as a tool gap, [klt2357].

The re-minted fifteen-corner family this document's own sweep produces is
`sim/records/2026-09-22-digital-sta-power-{01..15}.md`; every one reports
`max_slew_violations: 0` and `interface_load_max_slew_violations: 0`.

### Cost of the tighter constraint

The extra buffering the tighter target adds is small (+30 logical
instances). `repair_design` applies the tighter target design-wide, so the
buffering is not guaranteed to land only on the two nets the probe named:
the rebuild's worst-fanout net moved too (to `u_interface/net71`, 38 loads).

| | before (#255, `max_transition_ns: 8.0`, violating) | after (#264, `max_transition_ns: 4.0`, clean) |
|---|---:|---:|
| Placed cell area | 59 465.1 µm² | 61 692.0 µm² (+3.7 %) |
| Achieved utilization | 41.56 % | 43.11 % (+3.7 %, same die) |
| Routed wirelength | 72 050 µm | 72 152 µm (+0.14 %) |
| Die area | 159 117 µm² (unchanged — set by the floorplan's 40 % utilization target, not by cell count) | 159 117 µm² |
| Library `max_transition` violations | 11 of 15 corners | **0 of 15 corners** |
| #233 trunk-net `max_transition` violations | 0 of 15 corners | 0 of 15 corners (unchanged) |

### Current depth-2 figures (supersede §0's "depth 2" column)

Every timing, area and power figure moved with the rebuild, not just the
`max_transition` fields. Records:
`sim/records/2026-09-22-digital-sta-power-{01..15}.md`.

| | [#255] depth 2 (§0, superseded) | [#264] depth 2 (current) |
|---|---:|---:|
| Placed instances | 4436 DEF `COMPONENTS` (1458 logical) | 4483 DEF `COMPONENTS` (1488 logical) |
| Setup binding slack | +23.880 ns at `ss_125C_3v00`/`max` | +31.413 ns at `ss_125C_3v00`/`max` |
| Hold binding slack | +0.6935 ns at `ff_n40C_3v60`/`min` | +0.6902 ns at `ff_n40C_3v60`/`min` |
| Fmax floor | 38.284 MHz at `ss_125C_3v00`/`max` | **53.801 MHz** at `ss_125C_3v00`/`max` |
| Placed cell area | 59 465.1 µm² | **61 692.0 µm²** |
| vs the pre-synthesis inventory (depth-2, 863 cells, 33 654.6 µm²) | ×1.767 | **×1.833** |
| Active power @ 1 MHz (max) | 358.5 µW at `ff_125C_3v60`/`max` | **345.6 µW** at `ff_125C_3v60`/`max` |
| Leakage (max) | 7.107 µW / 1.974 µA at `ff_125C_3v60` | **7.515 µW / 2.088 µA** at `ff_125C_3v60` |
| Library `max_transition` violations | 11 of 15 corners | **0 of 15 corners** |

The Fmax floor rose by about 40 %. That fits §2a's depth-8 reading, where the
critical path ran through the slew-violating nets: fixing their transitions
also shortens the binding setup path. This document does not break that down
path by path. The placed area moved *away* from the `< 0.05 mm²` README row,
not toward it. That row's disposition stays with [#150]/[DR-0019], as the
header above says; this issue does not touch it.

`sim/tools/digital_corner_characterization.py`'s `RECORDED` table now
reflects this rebuilt depth-2 DEF, and `--check` (wired into
`npm run check:spec`) gates on it.

---

## 1. What ran

| | |
|---|---|
| DUT | `layout/digital/trng_top.def` — the committed routed DEF from [#111]/[#172], re-placed and re-CTS'd by [#171] to add the vddd/vss power delivery network (tapcells, endcaps and filler), then rebuilt again by [#240] (2026-09-15) to state `max_transition_ns`/`max_capacitance_pf` to `repair_design` and clear the residual §2a describes. 8594 DEF `COMPONENTS`: 2533 logical instances + 6061 tapcell/endcap/filler cells, all `gf180mcu_fd_sc_mcu9t5v0` |
| Driver | `sim/tb/digital-sta-power/run_sta.py` (gate-level testbench, [DR-0021]) |
| Engine | OpenSTA + OpenRCX inside OpenROAD `26Q3-1278-g4421880472` ([#145]'s original pass; [#233]'s re-run below used `26Q3-1510-g6cb3f2b704`, an unrelated later OpenROAD build — see each record's own `tool:` field) |
| PDK | `gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b` |
| Parasitics | OpenRCX extraction of the real routing → SPEF → `read_spef`. Not estimated: `rules.openrcx.gf180mcuD.{min,nom,max}` as shipped by the PDK |
| Clock | `clk`, **propagated** through the CTS-built tree in the DEF (not ideal), 50 ns / 20 MHz — the P&R run's own constraint |
| Interface load | [#233]: `set_input_transition` on the six `digital`-facing inter-region trunks, derived from `layout/floorplan/reports/interregion.json` at run time — permanent, every run (§2a). Trunk-only Metal4 arithmetic; per [#232]/[#242] and §8.5 of [the full-chip PEX characterization](characterization-post-layout-extracted.md), this is a **floor**, not the measured load — see §2a's own caveat below |
| Grid | 5 liberty decks × 3 interconnect decks = **15 corners**, one record each |
| Records | `sim/records/2026-09-15-digital-sta-power-{01..15}.md` ([#240]: rebuilt DEF, `max_transition`/`max_capacitance` violations cleared, nothing else), superseding `sim/records/2026-09-12-digital-sta-power-{01..15}.md` (still committed, still accurate about the pre-[#240] DEF they name — §2a), which itself superseded `sim/records/2026-08-18-digital-sta-power-{01..15}.md` (still committed, still accurate about the pre-[#233] SDC they name — §2a), which itself superseded `sim/records/2026-08-17-digital-sta-power-{01..15}.md` (still committed, still accurate about the pre-[#171] DEF they name — [#183]) |

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

## 2. Timing: it closes everywhere, and Fmax has a floor of 39.8 MHz

Status: re-measured against the [#240] rebuild (2026-09-15); see §2a for why
the DEF changed and §3/§4 for the area/power consequences.

| corner | setup slack | hold slack | clock skew | Fmax |
|---|---:|---:|---:|---:|
| **`ss_125C_3v00` / `max`** — setup binds | **+24.876 ns** | +2.422 ns | −0.142 ns | **39.80 MHz** |
| `ss_125C_3v00` / `nom` | +25.503 ns | +2.416 ns | −0.122 ns | 40.82 MHz |
| `ss_125C_3v00` / `min` | +26.018 ns | +2.412 ns | −0.105 ns | 41.70 MHz |
| `ss_n40C_3v00` / `max` | +32.895 ns | +1.684 ns | −0.105 ns | 58.46 MHz |
| `ss_n40C_3v00` / `nom` | +33.416 ns | +1.680 ns | −0.089 ns | 60.30 MHz |
| `ss_n40C_3v00` / `min` | +33.772 ns | +1.678 ns | −0.077 ns | 61.62 MHz |
| `tt_025C_3v30` / `max` | +37.331 ns | +1.223 ns | −0.078 ns | 78.93 MHz |
| `tt_025C_3v30` / `nom` | +37.657 ns | +1.220 ns | −0.067 ns | 81.01 MHz |
| `tt_025C_3v30` / `min` | +37.924 ns | +1.218 ns | −0.058 ns | 82.81 MHz |
| `ff_125C_3v60` / `max` | +39.013 ns | +1.020 ns | −0.065 ns | 91.02 MHz |
| `ff_125C_3v60` / `nom` | +39.301 ns | +1.018 ns | −0.056 ns | 93.46 MHz |
| `ff_125C_3v60` / `min` | +39.537 ns | +1.016 ns | −0.048 ns | 95.58 MHz |
| `ff_n40C_3v60` / `max` | +42.616 ns | +0.710 ns | −0.049 ns | 135.42 MHz |
| `ff_n40C_3v60` / `nom` | +42.811 ns | +0.709 ns | −0.042 ns | 139.11 MHz |
| **`ff_n40C_3v60` / `min`** — hold binds | +42.972 ns | **+0.707 ns** | −0.036 ns | 142.27 MHz |

Total negative slack is **0 ns on both the setup and the hold side at all
fifteen corners**, so those two columns are the whole verdict: there is no
violating path anywhere in the set, not merely a positive worst case. Clock
skew is negative at every corner of this rebuild (it was positive at every
corner of the pre-[#240] DEF) — a property of which specific flops the CTS
tree the rebuild produced favors, not a regression: skew this small next to
tens of nanoseconds of setup margin does not move any verdict on this page.

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
**0.0070 %** worst case over the fifteen corners — which is the evidence that
licenses quoting either. `--check` fails if that agreement ever exceeds 1 %,
because a design whose slack is no longer linear in the clock period is one
where the extrapolated number has quietly stopped meaning anything.

The Fmax spread over the set is **39.80 → 142.27 MHz, 3.57×**, and the
interconnect axis alone moves it 4.6 % at the slow corner (41.70 → 39.80 MHz)
against the liberty axis's 3.4×. Wires matter here; devices matter much more.

### Reconciling with the place-and-route report

`layout/digital/reports/place_and_route.json` — rebuilt by [#240] alongside
the DEF — reports **+28.434 ns** at `ss_125C_3v00` (`worst_slack_ns`, the
single-corner figure at the request's own corner —
`layout/digital/README.md` explains why that is a different metric from the
same report's swept `worst_setup_slack_ns`), and this sweep reports
**+25.503 ns** at the same liberty corner with `nom` interconnect. Both are
right; they are different measurements, and each record carries the
intermediate figure that separates them:

| | slack at `ss_125C_3v00` |
|---|---:|
| P&R report — ideal clock, global-routing-*estimated* parasitics | +28.434 ns |
| this sweep, ideal clock, OpenRCX-*extracted* parasitics (`worst_setup_slack_ideal_clock_ns`) | +25.535 ns |
| this sweep, propagated clock, extracted parasitics (the headline) | +25.503 ns |

So of the 2.930 ns difference, **2.899 ns is extraction versus estimation**
and **0.031 ns is the real clock tree** (`clock_tree_cost_ns`, the largest
such cost in the set is 0.062 ns). Real extraction is materially more
pessimistic than the router's own RC estimate at this corner, and the CTS
tree is nearly free — which is worth knowing before anyone tries to explain a
slack difference by the clock model. Both terms moved from the pre-[#240]
measurement (which found 4.768 ns / 0.100 ns at the same corner,
2026-09-12 family, against that family's own +27.766 ns P&R-report figure) —
[#240]'s rebuild adds buffering on top of the same placement (§2a, §3), not a
fresh placement from scratch, so a shift here is expected and is not read as
a regression. [#171]'s own earlier re-run (a genuinely different placement
and clock tree, not the same layout with rails added — `layout/digital/
README.md`'s "The power distribution network" section) is a deeper layer of
the same history and is not re-derived here.

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

## 2a. The six digital-facing inter-region trunks ([#233]): clean by three orders of magnitude — and one pre-existing violation they uncovered

[DR-0025] scoped the full-chip parasitic-extraction increment ([#232]) away
from the six inter-region trunks that terminate on `digital`'s own pins
(`clk`, `rst_n`, `raw_bit`, `raw_valid`, `ring_bit[0]`, `ring_bit[1]`) —
`digital`'s ~2500 standard cells are abstracted in every existing
extraction, so an ngspice run over an ideal clock source would have priced a
couple of picoseconds of RC against edges measured in tens to hundreds of
ps, "a no-op dressed as a measurement" in that record's own words. [DR-0025]
handed the real question here instead: what does each trunk's own Metal4 RC
do to the edge arriving at `digital`'s pin, asked of a characterised library
rather than of an unmodelled ngspice source.

### What was added, and in what units

`run_sta.py`'s `_tcl()` reads `layout/floorplan/reports/interregion.json` at
run time — never a transcribed length — and states each trunk's own lumped
R·C as a `set_input_transition` on the corresponding port, in every session
of every corner. The DEF's own pin names come from each route's `digital`
endpoint, so the two bus-notation ports (`ring_bit[0]`/`ring_bit[1]`, whose
interregion net names are `ring_bit1`/`ring_bit2`) are matched rather than
silently skipped.

A transition time is meaningless without the thresholds it is measured
between, and these decks declare their own: 30 %/70 % thresholds *and*
`slew_derate_from_library 0.5` — a factor of two between the edge a scope
would measure and the number in the tables. `set_input_transition` and
`max_transition` are both in the **table** domain, which this repository
verified against the tool rather than against a reading of the Liberty
spec: walking a stated transition across `ss_125C_3v00`'s 13.2 ns limit,
13.1 is clean and 13.3 violates by exactly 0.10, with no derate applied
(`sim/tb/digital-sta-power/sdc_treatment_probe.py --domain`). So the stated
number is `ln(7/3) / 0.5 = 1.6946 × R × C`, with all three attributes read
from the deck at run time, and each record also carries the textbook 10–90 %
figure (`ln 9 × R × C`) for comparison. Two deliberate conservatisms make
every figure below an upper bound rather than a best estimate: lumped
R times lumped C (a distributed line of the same totals responds roughly
twice as fast), and an ideal source, so the number prices the wire and
nothing upstream of it.

**The `R` and `C` themselves are a floor, not the measured load
([#232], [#242]).** The 0.09 Ω/sq / 0.007602 fF/µm² / 0.028153 fF/µm
Metal4 coefficients below price only the trunk's own Metal4 sheet; they
omit the Metal3 risers and vias a real full-chip extraction includes. On
`ro1`/`ro2` — the two nets in [#232]'s full-chip `klt extract --parasitics`
measurement where a trunk-only estimate and a real extraction close
like-for-like — this same arithmetic undercounts real added capacitance by
~14 % and real added resistance by ~48 % (§8.5 of
[the full-chip PEX characterization](characterization-post-layout-extracted.md)).
`ro1`/`ro2` are the *shortest* measured trunks, and §8.5 explains why a
trunk-only estimate should be worst there; the six trunks in the table below
are 2–4× longer, where that fixed riser/via cost should be a *smaller*
share of the total, but no measurement of any of these six trunks exists to
turn that expectation into a correction factor — so the numbers below are
stated with the floor disclosed, not adjusted by an unmeasured multiplier.

| port | net | trunk | R | C | R·C | stated transition | 10–90 % reference |
|---|---|---:|---:|---:|---:|---:|---:|
| `clk` | `clk` | 353.78 µm | 106.13 Ω | 20.727 fF | 2.200 ps | 3.728 ps | 4.833 ps |
| `rst_n` | `rst_n` | 339.34 µm | 101.80 Ω | 19.881 fF | 2.024 ps | 3.430 ps | 4.447 ps |
| `raw_bit` | `raw_bit` | 524.77 µm | 157.43 Ω | 30.744 fF | 4.840 ps | 8.202 ps | 10.635 ps |
| `raw_valid` | `raw_valid` | 446.61 µm | 133.98 Ω | 26.165 fF | 3.506 ps | 5.941 ps | 7.703 ps |
| `ring_bit[0]` | `ring_bit1` | 343.16 µm | 102.95 Ω | 20.105 fF | 2.070 ps | 3.507 ps | 4.548 ps |
| `ring_bit[1]` | `ring_bit2` | 265.47 µm | 79.64 Ω | 15.553 fF | 1.239 ps | 2.099 ps | 2.722 ps |

Metal4 coefficients are [DR-0025]'s own (0.09 Ω/sq, 0.007602 fF/µm²,
0.028153 fF/µm at the `WIRE_W = 0.30 µm` every trunk is drawn at); the
lengths are `interregion.json`'s as-built `trunk_length_um`, and both the
file's sha256 and the per-port arithmetic are in every record's
`interface_loads:` block.

### Why `set_load` is not used — for any of the six

[#233] was filed expecting `set_load` on the four `combiner_sampler`-driven
ports, with `clk`/`rst_n` to be decided separately. It is not used for
either group, and the reason is stronger than the port direction: all six
are `DIRECTION INPUT` on `trng_top` (`layout/digital/trng_top.def`'s own
`PINS` section) with **no driver inside this single-region netlist** —
`combiner_sampler` drives four of them and an off-chip pad drives
`clk`/`rst_n`, and neither exists here — so there is no driver arc at the
port for a load to attach to. Measured, not assumed, at
`ss_125C_3v00`/`rc-min` over five otherwise identical sessions:

| session | worst setup slack | worst hold slack | total power (20 MHz) | worst slew at the six ports |
|---|---:|---:|---:|---:|
| no interface constraint | 23.685763 ns | 2.4247368557 ns | 8.44065938 mW | 0.000000 ns |
| `set_load`, as-built 15.6–30.7 fF | 23.685763 ns | 2.4247368557 ns | 8.44065938 mW | 0.000000 ns |
| `set_load`, 10 pF | 23.685763 ns | 2.4247368557 ns | 8.44065938 mW | 0.000000 ns |
| `set_input_transition`, derived | 23.685763 ns | 2.4247370778 ns | 8.44064821 mW | 0.008202 ns |
| `set_input_transition`, 10× | 23.685763 ns | 2.4247370778 ns | 8.44054576 mW | 0.082021 ns |

Both `set_load` rows are **bit-identical** to the unconstrained one — every
slack, every power column, every slew, and the design-wide worst max-slew
slack. A `set_load` line here would have been a no-op wearing the costume of
a measurement: exactly what [DR-0025] declined to do with an ngspice run,
one level removed. `set_input_transition` is the one construct that states
what these ports genuinely have, which is an edge arriving from off this
netlist already degraded by the trunk's RC.
`sdc_treatment_probe.py` re-runs that comparison on demand, and `--check`
fails if any of it stops holding.

### Result: no violation, ≥ 536× margin, no measurable slack cost

Status: the controlled with/without comparison below is against the DEF
committed at the time ([#233], pre-[#240]) — a fixed binary and a fixed DEF
is the point of a controlled comparison, and the trunk-load figures
(ports/transition/margin/violations) are unaffected by [#240]'s rebuild
either way (they are geometry- and library-derived, not a function of
internal buffering). The Fmax-floor/setup/hold row is quoted as it read
*then*; §2 carries what those two figures read today (39.80 MHz /
+24.876 ns / +0.707 ns, post-[#240]) — this table is not the place to look
for the current headline number.

| | value |
|---|---|
| Ports priced this way | **6 of 6**, at all 15 corners (`interface_load_ports`) |
| Worst stated transition | **8.202 ps** (`raw_bit`, the longest trunk) |
| Library `max_transition` | 13.2 ns (`ss_125C_3v00`), 11.2, 6.0, 5.2, **4.4 ns** (`ff_n40C_3v60`) |
| Margin at the tightest deck | **4.3918 ns — a factor of 536** (`interface_load_transition_margin_ns`) |
| Trunk ports violating it | **0 of 6, at every one of the 15 corners** (`interface_load_max_slew_violations`) |
| Fmax floor (pre-[#240] DEF) | **35.63 MHz, unmoved by turning the interface load on** (`ss_125C_3v00`/`max`) |
| Worst setup / hold slack (pre-[#240] DEF) | **+21.935 ns / +0.712 ns, unmoved by turning the interface load on** |

The slack columns cannot move much, and the reason is structural rather
than lucky: `raw_bit`/`raw_valid`/`ring_bit[0]`/`ring_bit[1]` carry no
`set_input_delay`, so no reg-to-reg path starts at one (§2, "What is not
timed") and those four trunks cannot touch a reported slack at all. `clk`
and `rst_n` do reach the clock tree and the flops' reset pins — and in the
controlled comparison above, worst setup slack was unchanged in **every
digit of double precision** while worst hold slack moved by **+0.22 ps**.
Note the sign: that is an *improvement*, and it stays an improvement when
all six transitions are overstated 10×. Launch and capture share the clock
root, so a slower root edge largely cancels, and the residual's sign is not
guaranteed to be a degradation — anyone reading a sub-picosecond slack shift
here as "the trunk RC cost us timing" would be reading numerical residue.
The effect that *is* monotonic in the trunks' RC is the slew at the six
ports and at the pins they drive, and that is where it is reported.

A note on comparing record families: the `2026-08-18` family was produced by
OpenROAD `26Q3-1278-g4421880472` and this one by `26Q3-1510-g6cb3f2b704`, so
a cross-family diff conflates the interface load with a tool upgrade. (It
is small either way: every slack and Fmax figure is identical to the digits
reported, and total 1 MHz power differs by ≤ 3 nW, both signs.) The
controlled with/without comparison is the probe table above, one binary, one
corner, one DEF.

### What asking the question uncovered: 9 of 15 corners already violate `max_transition`

**Status: fixed by [#240] (2026-09-15) — this subsection is history, kept for
how the finding was made.** The DEF and table below are the pre-fix ones
[#233]/[#237] measured; "### The verdict" further down describes the current,
post-fix state and is the section to read for what is true of the design
today.

Answering [#233]'s third acceptance criterion meant asking OpenSTA for the
library's own max-transition check (`report_check_types -max_slew`) for the
first time in this repository. The six trunk ports are clean. The design is
not:

| corner | library limit | worst max-slew slack | violating pins | on a trunk net |
|---|---:|---:|---:|---:|
| `ss_125C_3v00`/`min` | 13.2 ns | +0.1625 ns | 0 | 0 |
| `ss_125C_3v00`/`nom` | 13.2 ns | **−0.5651 ns** | 33 | 0 |
| `ss_125C_3v00`/`max` | 13.2 ns | **−1.4487 ns** | 46 | 0 |
| `ss_n40C_3v00`/`min,nom,max` | 11.2 ns | +2.7907 … +1.7354 ns | 0 | 0 |
| `tt_025C_3v30`/`min,nom,max` | 6.0 ns | **−0.7562 … −1.5930 ns** | 46, 46, 94 | 0 |
| `ff_125C_3v60`/`min,nom,max` | 5.2 ns | **−0.8471 … −1.5884 ns** | 46, 46, 94 | 0 |
| `ff_n40C_3v60`/`min,nom` | 4.4 ns | +0.4511, +0.2320 ns | 0 | 0 |
| `ff_n40C_3v60`/`max` | 4.4 ns | **−0.0183 ns** | 33 | 0 |

This is **pre-existing and not [#233]'s**: the unconstrained `baseline`
session in the probe table above reports the identical worst max-slew slack,
and `interface_load_max_slew_violations` is 0 at every corner — none of the
violating pins is on one of the six trunk nets. It was simply never asked
about before. Per [#233]'s fourth acceptance criterion it was written up with
its own follow-up, [#237], rather than absorbed here; the next subsection is
that follow-up's answer.

### The verdict ([#237], fixed by [#240]): constrained, rebuilt, re-verified — zero violations at every corner

**Status (2026-09-15).** [#237] measured the finding below and could not act
on it: `klt place-and-route`'s request contract had no design-rule constraint
field at all. [klayout-tools#1860][klt1860] added
`max_transition_ns`/`max_capacitance_pf`/`max_fanout` to that contract on
2026-09-15, and [#240] used it the same day: `layout/digital/build.py`'s
`CONSTRAINTS` now states `max_transition_ns: 8.0` and
`max_capacitance_pf: 0.35`, the DEF was rebuilt, and the full fifteen-corner
`digital-sta-power` family was re-minted against it
(`sim/records/2026-09-15-digital-sta-power-{01..15}.md`, superseding
`2026-09-12` for [DR-0021]'s "latest per corner wins" rule — the
`2026-09-12` records stay committed and still accurately describe the DEF
they name). The result: **`max_slew_violations` is 0 and
`max_capacitance_violations` is 0 at all fifteen corners** — not a bounded
residual, a closed one. `sim/tb/digital-sta-power/max_transition_probe.py
--check` and `sim/tools/digital_corner_characterization.py --check` both
gate this state now, the same way they gated the residual before.

A violation count says which corners are unhappy and nothing else. Deciding
what to do needed four more things — which nets, whether the reported timing
and power ride on them, what it costs, and what a constraint would have to
say — so [#237] measured them, and that measurement is what [#240] acted on.
`sim/tb/digital-sta-power/max_transition_probe.py` is that measurement: one
OpenROAD session per corner over the committed DEF, the same 50 ns
constraint and the same six trunk `set_input_transition` lines the sweep
itself uses, reproducing every record's `max_slew_slack_ns` to the digit and
then decomposing it.

**One structure, four nets — and not all of it was in `u_interface`.** Every
violating pin, at every corner of the *pre-fix* DEF, resolved to one of four
nets, each a single-cell driver into a large load-pin count:

| net | pins on net | driver | corners it violated at (pre-fix) | worst violating pins (pre-fix) |
|---|---:|---|---:|---:|
| `u_interface/_0999_` | 34 | `u_interface/_1760_/Z` (`or2_1`) | 2 | 34 |
| `u_interface/_1190_` | 33 | `u_interface/_2212_/ZN` (`nor2_2`) | **9** | 33 |
| `u_conditioner/_095_` | 14 | `u_conditioner/_209_/ZN` (`xnor2_1`) | 2 | 14 |
| `u_interface/_0606_` | 13 | `u_interface/_1304_/ZN` (`nor2_1`) | 7 | 13 |

`u_interface/_1190_` — the `mux2_1` select net [#237] traced by hand — was the
one that violated everywhere; the other three joined it as the corner
tightened, and the 94-pin worst corners were exactly 34 + 33 + 14 + 13.
[#237]'s own issue text called the violators "internal to `u_interface`",
which the measurement corrected: `u_conditioner/_095_` was not. What the four
had in common was not a sub-block but a shape — a low-drive cell into a wide
fanout — which is a drive-strength outcome of synthesis + place-and-route,
not of any spec row or RTL structure. None of the four violates
`max_transition` anywhere in the rebuilt DEF.

**The design's critical path *was* an extrapolated path — and no longer is.**
At all nine pre-fix violating corners, the worst setup slack of any path
passing through a violating pin (`report_checks -through`, over the whole
violator set) equalled the design-wide worst setup slack to every digit —
including the +21.935 ns at `ss_125C_3v00`/`rc-max` that §2 used to quote as
this design's timing margin. So the honest reading of that margin used to be
not "21.9 ns of slack on a path we understand" but "21.9 ns of slack on a
path whose cell delays are looked up outside the range the library
characterises". Post-fix, no pin violates `max_transition` anywhere, so there
is no violator for a path to pass through and no qualifier left to carry —
§2's current +24.876 ns margin (rebuilt DEF, ss_125C_3v00/rc-max) is an
ordinary margin on a path inside the library's characterised range.

**The cost, priced — before the fix.** The instances owning a violating pin
(plus the four drivers) carried at most **1.84 %** of total power
(`ff_125C_3v60`/`rc-max`) on the pre-fix DEF, so the extrapolated
internal-energy tables could not have moved §4's figures materially even
unfixed. The same probe found the library's sibling `max_capacitance` check
violated too, at **11 of 15 corners** (worst 6 pins, −0.154 pF against a
0.373 pF limit at `ff_125C_3v60`/`rc-max`) — the same four nets, the same
cause, and equally never asked about before [#237]. Both checks are 0
violations at every corner on the rebuilt DEF.

**What the constraint says, and what it took to find the right number.**
`layout/digital/build.py` reads exactly one liberty deck (`ss_125C_3v00`), so
OpenROAD's `repair_design` — which the flow already runs after global
placement, and which exists to fix precisely this — only ever sees that
deck's own 13.2 ns limit stated on top of whatever `max_transition_ns` this
script adds. Meeting the library's own limit would not have been enough,
because the limit and the slew do not scale together across the shipped
decks: the probe derived, from the pre-fix measured per-corner slews, that
the slew at `ss_125C_3v00` would have to be held to **11.21 ns** for every
corner to come out clean, binding at `ff_125C_3v60`/`rc-min`. That was 84.9 %
of the implementation deck's own limit — a derived, guard-banded number, not
a library constant, and (per [#240]'s own test plan) a number to verify
against, not assume:

| corner | limit | worst slew (pre-fix) | slew ÷ P&R corner | required P&R-corner slew |
|---|---:|---:|---:|---:|
| `ss_125C_3v00`/`min,nom,max` | 13.2 ns | 13.04 … 14.65 ns | 1.000 | 13.20 ns |
| `ss_n40C_3v00`/`min,nom,max` | 11.2 ns | 8.41 … 9.46 ns | 0.645 … 0.646 | 17.33 … 17.36 ns |
| `tt_025C_3v30`/`min,nom,max` | 6.0 ns | 6.76 … 7.59 ns | 0.518 | 11.58 ns |
| `ff_125C_3v60`/`min,nom,max` | 5.2 ns | 6.05 … 6.79 ns | 0.463 … 0.464 | **11.21 … 11.22 ns** |
| `ff_n40C_3v60`/`min,nom,max` | 4.4 ns | 3.95 … 4.42 ns | 0.302 … 0.303 | 14.53 … 14.59 ns |

[#240] took two rebuilds, not one, because the "verify, don't assume" caveat
above turned out to matter: a first attempt at `max_transition_ns: 10.0`
(below the 11.21 ns derived above by roughly the same margin, and a
reasonable guess given `repair_design` optimises against placement-estimated
parasitics rather than the post-route extraction that 11.21 ns figure is
built from) was re-verified against a full re-mint of the fifteen-corner
family rather than trusted, and the re-mint found it was not enough:
`max_slew_violations` was still 13 at two corners
(`tt_025C_3v30`/`rc-max`, `ff_125C_3v60`/`rc-max`). Tightening to
`max_transition_ns: 8.0` (60.6 % of the implementation deck's own 13.2 ns
limit) and rebuilding a second time cleared it everywhere.
`max_capacitance_pf: 0.35` was stated alongside it but is not shown to be the
lever that cleared `max_capacitance`'s violations: the library's own per-pin
limit already measures below 0.35 pF at every corner of the rebuilt DEF, so
it is the same slew-driven buffering that clears both checks, as a byproduct
of one drive-strength fix rather than two independent ones.
`layout/digital/build.py`'s `CONSTRAINTS` comment carries the same account,
in full, at the point of use.

**Nor could the synthesis stage have said it instead.** [#237] asked about
"synthesis/P&R time", so `design/synth.py`'s side was checked too, and it is
the same answer for the same reason, unchanged by [#240] (which only touches
`place-and-route`): `klt synthesize`'s `request.constraints` reads exactly
one field, `clock_period_ns`, which it turns into ABC's `-D` picosecond delay
target. The `abc -constr` file the command writes is two fixed lines
(`set_driving_cell` / `set_load`) built from `klt`'s own per-library table,
not from anything the request can influence — so there is no synthesis-side
surface for a design-rule constraint either. That is the correct place for
it to be missing, in any case: the violation was created by drive-strength
and placement decisions that the mapped netlist does not fix, and
`repair_design` after global placement is where the flow has the information
to repair it.

**`set_max_fanout` was rejected on its own merits, not on availability — and
[klayout-tools#1860][klt1860] shipped it anyway, unused here.**
`gf180mcu_fd_sc_mcu9t5v0` declares
no `default_max_fanout` and no per-pin `max_fanout` anywhere, so there is no
library limit to enforce and `sta::max_fanout_check_limit` returns the 1e30
sentinel. More to the point, fanout did not predict this violation on the
pre-fix DEF: its highest-fanout net was `rst_n` at **201 load pins** — nearly
six times the largest of the four offenders — and it was clean at every
corner, while a 13-load net violated at seven (77 nets carried ≥ 16 loads in
all). What bound was load capacitance against drive strength, which is what
`max_transition`/`max_capacitance` measure directly, and `layout/digital/
build.py` does not set `max_fanout` even though
[klayout-tools#1860][klt1860] added the field.
(`sta::max_fanout_violation_count` is also still not safe to call — it takes
OpenROAD down with SIGSEGV inside `sta::CheckFanouts::check` on this design
at every corner, which is why the probe walks the topology instead; noted in
the upstream issue.) One topology fact moved anyway, as a side effect rather
than a lever: `max_transition_ns: 8.0`'s buffering reshaped `rst_n` along
with the four originally-violating nets, and the rebuilt DEF's own
worst-fanout net is smaller and different — `u_interface/_0862_` at 33 loads.

**What closing this changes, and what it does not.** No spec row was ever at
risk: setup and hold closed at every corner before the fix and close with
more margin after it (§2), and [DR-0003]'s ratified raw rate needs 1 MHz
against an Fmax floor that moved from 35.6 MHz to **39.8 MHz**. The
previously-affected nets sat inside `u_interface`'s register-file logic and
`u_conditioner`'s CRC32 — both *downstream* of the raw tap that rate is
defined at, and none of them on the sampler's own path — so the fix changes
a signoff-quality qualifier on already-passing numbers, not a pass/fail
verdict. What moved measurably is cost: §3's area is up from 116 001 to
**118 975 µm²** (2 974.8 µm², 2.6 %, +31 logical instances against the
pre-fix DEF) and §4's power moved by well under 1 % at
the binding corner, both because clearing four nets' drive-strength
violation — plus `rst_n`'s topology as a side effect — costs area and
switching power, which §3/§4 now quote directly rather than assume
unchanged. The closure is gated rather than asserted, same as the residual
was: `max_transition_probe.py --check` fails if a violation reappears on any
net, at any corner, or on a trunk net;
`sim/tools/digital_corner_characterization.py --check` (the PDK-free gate CI
runs) fails if the record family's violation count, worst corner, worst
slack or worst pin count moves away from zero in either the record-file or
the derived-summary sense — a document that fails to notice a regression is
no more trustworthy than one that overstated a defect that no longer exists.

### Permanent, not a one-off scenario

[#233]'s open question was whether this belongs in the STA setup permanently
or as a one-off. **Permanent**, and the deciding argument is that it can be
*derived*: the SDC lines are regenerated from `interregion.json` and the
corner's own liberty deck on every invocation, so a floorplan or routing
change ([#222]-style) is picked up the next time the sweep runs. A pinned
constant would have been the thing to keep out of the permanent setup, and
there is none here — not the trunk lengths, not the slew convention, not the
library limit the margin is quoted against. `check_environment()` now fails
the sweep outright if `interregion.json` is missing rather than quietly
timing the design without its interface load.

---

## 3. Area: 118 975 µm² placed, 1.60× the inventory estimate

Status: re-measured against the [#240] rebuild (`max_transition_ns`/
`max_capacitance_pf` stated to `layout/digital/build.py`'s `CONSTRAINTS`,
2026-09-15). The area moved because buffering four high-fanout nets — and,
as a topology side effect, `rst_n` — adds cells; per [#240]'s own test plan,
this is re-stated rather than assumed unchanged from the pre-fix figures
this section used to quote.

| | cell area | cells | library |
|---|---:|---:|---|
| **Measured** — OpenROAD `report_design_area` over the routed DEF | **118 975.4 µm²** | 8594 DEF `COMPONENTS` (2533 logical + 6061 tapcell/endcap/filler, [#171]) | `mcu9t5v0` (9-track) |
| Estimate — `layout/floorplan/reports/area.json`, region `digital` | 74 485.3 µm² | 1655 inventoried cells | `mcu7t5v0` (7-track) |
| Delta | **+44 490.1 µm² = ×1.597** | +878 logical | — |

> **The estimate row is the figure `reports/area.json` carried at the
> *measured* depth, and that is now a pin.** Issue [#254] set [DR-0020]'s
> ratified `FIFO_DEPTH = 2` in the regmap, the RTL parameter default and the
> inventory estimate, so that report's `digital` region now prices **33 654.6
> µm² in 863 cells** — but `layout/digital/trng_top.def`, which the measured
> column is read from, is still the depth-8 synthesis and placement, because
> re-synthesizing at the new depth is explicitly outside #254. Dividing one
> into the other would report a depth change as a library/cell-count gap
> (×3.54 instead of ×1.597), so `sim/tools/digital_corner_characterization.py`
> holds the estimate side of this comparison at the depth-8 figures above
> while the two disagree, prints the live depth-2 figures alongside them, and
> drops the pin by itself once a depth-2 re-synthesis makes the depths agree.
> **No measured number in this document moved**, and none of the three terms
> in the decomposition below is FIFO-depth-dependent on the measured side.

Both figures are *standard-cell* area, which is what makes them comparable.
The **die** figure in the place-and-route report (301 209 µm²) is not
comparable to either: it follows arithmetically from that run's own 40 %
utilization target, which was chosen to leave routing headroom on a first
attempt, and `layout/digital/README.md` says so at length. This document does
not difference it against anything.

**Where the 1.60× comes from.** Pricing the *same as-built netlist* against
the 7-track library separates the two axes that moved at once — but only over
the **2533 logical** instances in `trng_top.pnr.v`; [#171]'s 6061
tapcell/endcap/filler cells have no functional pins and so never appear in a
gate-level Verilog netlist, and are handled separately below:

| | cell area | µm²/cell | step |
|---|---:|---:|---|
| inventory estimate, 7-track | 74 485.3 µm² | 45.01 | — |
| as-built **logical** netlist priced 7-track | 92 560.6 µm² | 36.54 | **×1.243** cell count / mix |
| as-built **logical** netlist, 9-track (what was built) | 116 305.5 µm² | 45.92 | **×1.257** track height |
| + [#171]'s tapcell/endcap/filler population | +2 669.9 µm² | n/a (no logical netlist entry) | **×1.023** PDN population |
| = measured, `report_design_area` | 118 975.4 µm² | — | **×1.597** total |

Three things follow, and the tapcell/endcap/filler term is the one that did
not exist before [#171] (the [#240] rebuild moved the numbers on this row,
not the shape of the argument):

- **The inventory under-counted cells by 53 %** (1655 → 2533) but
  **over-priced the average cell by 23 %** (45.01 vs 36.54 µm² in like-for-like
  7-track terms). Those errors partly cancel, which is why the naive
  per-instance averages (45.01 estimated, 45.92 measured) look like a
  vindication of the estimate and are not one. A bottom-up inventory built
  from RTL `reg` declarations plus a structural guess at the combinational
  logic got the *shape* of the block right and the *count* wrong in a way no
  amount of care would have fixed without running a synthesiser -- and [#240]
  adds 28 buffer instances on top of that gap (2533 logical vs 2505
  synthesized, per `layout/digital/reports/place_and_route.json`), the price
  of clearing `max_transition`/`max_capacitance` at every corner.
- **The 9-track library costs 25.7 % more area than the 7-track one for
  identical logic.** That is a pure library choice, not a design property, and
  it is the one term on this list that could be recovered by changing a
  parameter — `mcu7t5v0` is what `design/conditioner/area_estimate.py` and the
  floorplan already assume, and `mcu9t5v0` is what [#143] synthesized against
  and [#111] placed. Nothing in this repository has decided that question; it
  is recorded here so that it is decided rather than inherited.
- **[#171]'s power-delivery cells cost a further 2.3 % on top.** 6061
  tapcell/endcap/filler instances (71 % of the DEF's 8594 `COMPONENTS`, by
  count) are placement/DRC infrastructure, not logic, so they carry no port
  list and are invisible to a netlist-driven crosscheck — this is why the
  "as-built logical netlist, 9-track" row above (116 305.5 µm², summed from
  `trng_top.pnr.v`'s instances against the liberty deck) does not equal
  OpenROAD's own `report_design_area` (118 975.4 µm²): they are 2.24 % apart,
  and the gap is entirely those 6061 cells.
  `sim/tools/digital_corner_characterization.py --estimate` prints this gap as
  "liberty sum vs OpenROAD's own `report_design_area`" so a future re-run
  cannot silently start treating the two figures as interchangeable again.

**Against the ratified row.** The `< 0.05 mm²` README row is 50 000 µm² for
the *whole block*. The digital section's placed cell area alone is
**238.0 %** of it (the estimate was 149 %), and at a realistic 60 % / 80 %
placement utilization the digital section alone implies **198 292 / 148 719
µm²**, i.e. 397 % / 297 % of the row. The entropy source, samplers, guard
rings and isolation channels together are 13.1 % of the row
(`layout/floorplan/README.md`).

The row is **not edited, and no design change is proposed here.** [DR-0019]
(`Proposed`) already routes this miss and prices the available responses
against FIFO depth; [DR-0020] (`Proposed`) proposes the depth change itself;
[#150] owns the row. What this section adds is that the miss is now measured
rather than estimated, and 59.7 % larger than the estimate [DR-0019] was
written against — so whichever response is chosen, it has to close a bigger
gap than that record's own sensitivity table assumed. Re-deriving [DR-0019]'s
depth table against this measurement is that record's follow-up, not this
document's.

---

## 4. Power: 11–14× the estimate on dynamic, and leakage now carries a PDN term

Status: re-measured against the [#240] rebuild (2026-09-15). Every power
figure below is re-stated, not assumed unchanged, per that issue's own test
plan — buffering four high-fanout nets (and, as a topology side effect,
`rst_n`) moves cell count, and cell count moves power.

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
| `ss_n40C_3v00` | 408.6 µW | 8.17 mW | 91.0 µW | 318.5 nW | 106.2 nA |
| `ss_125C_3v00` | 437.6 µW | 8.68 mW | 99.1 µW | 3.941 µW | 1.314 µA |
| `tt_025C_3v30` | 522.8 µW | 10.45 mW | 118.1 µW | 413.8 nW | 125.4 nA |
| `ff_n40C_3v60` | 638.6 µW | 12.76 mW | 146.2 µW | 478.9 nW | 133.0 nA |
| **`ff_125C_3v60`** — both maxima | **699.4 µW** | **13.71 mW** | 159.8 µW | **14.62 µW** | **4.062 µA** |

Active power binds at `ff_125C_3v60`/`max` (712.4 µW at 1 MHz, 13.97 mW at
20 MHz) and leakage binds at the same liberty corner — hot, fast,
high-supply, which is where the README's Power row already binds its idle
half (`ff` / +10 % / +125 °C). Its active half names `ff` / +10 % without a
temperature; on this sweep the hot `ff` deck is the worse of the two `ff`
decks for total power as well, by 10 %. Leakage is interconnect-independent,
as it must be, so its binding corner is a liberty corner rather than a pair.

**Two things this does not say.** It does not say the block's active power is
699 µW: the digital section is one of three contributors and the whole-block
rollup (`sim/tools/power_rollup.py`) is what adds them up. And it does not
supersede that rollup's own digital term today — see §4.4.

**Against the `< 1 µA` idle row.** [DR-0017] records a 4.5× miss on that row
and attributes it to ungated standard-cell leakage in the digital section,
from the same library-based estimate (4.43 µA of digital idle leakage at
`ff` / +125 °C / 3.60 V, the row's own binding corner). The measurement at
that corner is **4.062 µA — 406 % of the row**, i.e. the miss is real and
unchanged in kind, and now **0.92× the size** the estimate predicted (was
0.63× against the pre-[#171] DEF, 0.89× against the pre-[#240] DEF — [#240]'s
28 added buffer/inverter instances cost a further sliver of leakage on top of
[#171]'s tapcell/endcap/filler term, not a new mechanism). The whole of that
shift — leakage 42 % higher than the pre-[#171] DEF at this corner, and a much
larger *relative* jump at the slow/cold corners (§4.2) — is still principally
[#171]'s tapcell/endcap/filler population: those cells are real, placed,
laid-out gf180mcu instances with their own leakage, and OpenSTA's
`report_power` prices every cell OpenROAD placed, not only the ones with a
functional pin `trng_top.pnr.v` names. Two caveats before either number is
used anywhere: it is the library's state-independent default leakage, where
the estimate carries an input-state range (2.86 .. 4.43 µA); and the
measurement covers the whole synthesized digital section *plus* its
power-delivery infrastructure, a broader scope than the estimate's
three-block logic-only inventory in both the [#171]/[#240] direction (extra
cells) and the pre-[#171] direction (no PDN estimate exists to compare
against). [DR-0017] remains the record that routes this row, and its proposed
replacement figure was set from the estimate, not from this.

### 4.2 Measured versus the library-based estimate

Both at 1 MHz, both at the same liberty corner, both at 0.25 transitions/cycle:

| corner | measured | estimate (headline) | estimate (ungated) | ×headline | ×ungated | leakage ratio |
|---|---:|---:|---:|---:|---:|---:|
| `ss_n40C_3v00` | 408.6 µW | 15.29 µW | 29.57 µW | 26.7× | 13.8× | 1.44× |
| `ss_125C_3v00` | 437.6 µW | 16.69 µW | 31.59 µW | 26.2× | 13.9× | 3.75× |
| `tt_025C_3v30` | 522.8 µW | 19.13 µW | 36.79 µW | 27.3× | 14.2× | 1.47× |
| `ff_n40C_3v60` | 638.6 µW | 23.12 µW | 44.33 µW | 27.6× | 14.4× | 1.56× |
| `ff_125C_3v60` | 699.4 µW | 39.38 µW | 65.77 µW | 17.8× | 10.6× | 0.92× |

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
longer does: 0.92× to **3.75×**, and the spread is not noise. [#171] added
(and [#240]'s rebuild carries) 6061 tapcell/endcap/filler instances to the DEF
that the estimate has no way to know about (it inventories logic, not
power-delivery infrastructure), and their leakage is a roughly *fixed*
addition per corner (the same physical cells regardless of liberty deck)
landing on top of a logic leakage that itself varies by three orders of
magnitude across the corner set (318.5 nW at `ss_n40C_3v00` to 14.62 µW at
`ff_125C_3v60`, §4.1). A fixed addition is a small fraction of a large number
and a large fraction of a small one — which is exactly the pattern above: the
ratio is worst (3.75×) at `ss_125C_3v00`, where the logic's own leakage is
smallest among the corners this table shows, and closest to holding (0.92×)
at `ff_125C_3v60`, where it is largest. The dynamic-power gap, below, is
unaffected by any of this: it was never a leakage question.

### 4.3 Where the dynamic gap is

At `tt_025C_3v30`/`nom`, 1 MHz, measured 522.8 µW against the ungated estimate's
36.79 µW:

| term | measured | estimate (ungated) | ratio |
|---|---:|---:|---:|
| cell internal energy (`Sequential` + `Combinational` internal) | 316.1 µW | 4.50 µW (`p_internal`) | 70× |
| clock delivery (`Clock` group: tree buffers + clock net) | 118.1 µW | 24.05 µW (`p_clock`) | 4.9× |
| data-net switching (`Sequential` + `Combinational` switching) | 88.4 µW | 7.91 µW (`p_data`) | 11.2× |
| leakage | 0.414 µW | 0.324 µW | 1.28× |

The two partitions are not identical — OpenSTA attributes a flop's clock-pin
capacitance to the clock net's driver and its clock-edge energy to the flop —
so the rows above are a decomposition, not a line-by-line identity. The
dominant term is unambiguous all the same, and it can be checked by hand
against the library:

> `gf180mcu_fd_sc_mcu9t5v0__dffq_1`'s `CLK` pin declares an `internal_power`
> table of **0.111 pJ rise + 0.167 pJ fall = 0.278 pJ per clock cycle**,
> unconditional on `D`. The netlist has **708 flip-flops**, unchanged by
> [#240] (`repair_design`'s buffering adds combinational buffer/inverter
> cells, not flops). At 1 MHz that is **196.8 µW before anything toggles** —
> on its own, 5.3× the estimate's entire ungated active figure.

The estimate multiplies each cell's internal energy by the *data* activity
(`p_internal += n * sec_activity * mean_int * freq`), i.e. it charges a flop
its clock-edge energy only on the 12.5 % of cycles where its data moves. That
is the single biggest error in the estimate, it is worth ~8× on the largest
term, and — the point worth keeping — **it was not visible before a netlist
existed.** A gate inventory can count flops; only a netlist and a library
together can say what each flop costs per edge.

The clock-delivery term's 4.9× has the same character: the estimate priced the
flops' own clock-pin capacitance plus a flat 2 fF-per-net wiring allowance,
against a real clock tree — 100 buffer and inverter cells inserted by CTS
(`clkbuf_*`/`clkload_*` in the as-built netlist; [#240]'s rebuild landed at
100, versus 101 for [#171]'s own rebuild and 100 for the DEF before either —
CTS tree size is not claimed stable run to run, and none of these differences
change the argument) — driving real routed wire. The extracted wiring is
**4.95 fF per net** at `nom` (4.36 at `min`, 5.77 at `max`), i.e. the flat
allowance was low by ~2–3×, plus 16.1 pF of inter-net coupling capacitance the
estimate had no term for at all. The data-net switching term's ratio moved
from 10.6× to **11.2×** because [#240]'s buffering adds switching nets to
drive; the leakage row's 1.28× is §4.2's PDN-leakage story again at this one
corner, not a new effect.

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

> **Update — [#240] (2026-09-15) moved the digital leakage term the rollup
> reads.** The active-row verdict is unchanged ("missed, 224.5 %" — the
> binding corner's 1 MHz digital term happens to barely move, §4.1). The
> idle miss widens slightly from **3.979 µA/~4.0×** to **4.095 µA/~4.1×**:
> [#240]'s 28 added buffer/inverter instances (§3) carry a small amount of
> their own leakage on top of [#171]'s tapcell/endcap/filler term, at the
> same `ff_125C_3v60` binding corner. `npm run check:spec` passes against
> this arithmetic too.

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
  with 24.9 ns of setup margin and 0.7 ns of hold margin at the respective
  binding corners, and an Fmax floor of 39.8 MHz — 39.8× [DR-0003]'s ratified
  raw-rate row and 9.95× its stretch row.
- The six inter-region trunks that land on this block's pins are **priced from
  as-built geometry and carried permanently**, and none of them violates the
  library's max-transition constraint at any corner ([#233], §2a) — which is
  what [DR-0025] deferred to this path rather than to an ngspice run.
- The digital section itself is now clean against the library's own
  design-rule checks too: **zero `max_transition`/`max_capacitance`
  violations at any of the fifteen corners** ([#237] found nine corners
  violating; [#240] constrained, rebuilt and closed it, §2a) — a
  signoff-quality gap this document itself surfaced is now resolved rather
  than merely bounded.
- The digital section's **area is measured**: 118 975 µm² of placed cell
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
  (§2). [#233] adds the six `digital`-facing inter-region trunks' own RC as an
  input transition on the ports they land on, which prices the *wire* and
  nothing upstream of it — it is not an arrival/required-time contract for
  those ports, and the four `combiner_sampler`-driven ones still start no
  timed path (§2a).
- **A clean max-transition result, as of [#240] — but read the caveats
  anyway.** The six trunk ports pass the library's `max_transition` check
  with ≥ 536× margin, and (since [#240]'s 2026-09-15 rebuild) so does every
  other pin in the design at every one of the fifteen corners: zero
  violations, where nine of fifteen corners violated before ([#237], §2a).
  This removes one extrapolation caveat this document used to carry — every
  delay and energy figure above is now inside the library's characterised
  slew range — but does not change any of the other "does not establish"
  items on this list.
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
  all three legs — the ×1.257 track-height term in §3 is that sensitivity
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

# §2a's two modelling decisions, re-measured rather than re-read: set_load
# vs set_input_transition on these ports, and which slew domain the stated
# transition is in (~1 min; needs openroad + the PDK)
python3 sim/tb/digital-sta-power/sdc_treatment_probe.py
python3 sim/tb/digital-sta-power/sdc_treatment_probe.py --check

# §2a's max-transition verdict (#237, closed by #240), per net and per
# corner: which nets violated, what the constraint had to say, and that the
# rebuilt DEF now reports zero violations everywhere
# (~4 min, all 15 corners; needs openroad + the PDK)
python3 sim/tb/digital-sta-power/max_transition_probe.py
python3 sim/tb/digital-sta-power/max_transition_probe.py --check
```

Records: `sim/records/2026-09-22-digital-sta-power-{01..15}.md`, the current
`FIFO_DEPTH = 2` family ([#264], §0a), one per corner, each with the generated
Tcl and the full OpenROAD log as committed raw output. The SPEF is not
committed (3.3 MB × 15); each record carries its sha256, byte count and
summed capacitance so a re-run can be checked against it. The pre-[#264]
`sim/records/2026-09-19-digital-sta-power-{01..15}.md` ([#255], §0) remain
committed as append-only evidence about the first depth-2 DEF (the one that
violated `max_transition` at 11 of 15 corners). The pre-[#255]
`sim/records/2026-09-15-digital-sta-power-{01..15}.md` remain committed as
append-only evidence about the `FIFO_DEPTH = 8` DEF they name and hash, but
no longer describe `layout/digital/`'s current committed artefacts (§0). The
pre-[#240] `sim/records/2026-09-12-digital-sta-power-{01..15}.md`
remain committed as append-only evidence about the DEF before
`max_transition_ns`/`max_capacitance_pf` were stated to `repair_design`
(§2a). The pre-[#233] `sim/records/2026-08-18-digital-sta-power-{01..15}.md`
remain committed as append-only evidence about the pre-interface-load SDC,
and every slack, Fmax and area figure they carry (against the pre-[#240] DEF)
is identical to the digits reported by the pre-[#240] family (§2a — the two
families were produced by different OpenROAD builds, so that is a
reconciliation rather than a controlled comparison; the controlled one is
`sdc_treatment_probe.py`'s). The pre-[#171] `sim/records/2026-08-17-digital-sta-power-{01..15}.md`
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
[#232]: https://github.com/2AMLogic/gf180-trng/issues/232
[#233]: https://github.com/2AMLogic/gf180-trng/issues/233
[#237]: https://github.com/2AMLogic/gf180-trng/issues/237
[#240]: https://github.com/2AMLogic/gf180-trng/issues/240
[#242]: https://github.com/2AMLogic/gf180-trng/issues/242
[#254]: https://github.com/2AMLogic/gf180-trng/issues/254
[#255]: https://github.com/2AMLogic/gf180-trng/issues/255
[#264]: https://github.com/2AMLogic/gf180-trng/issues/264
[klt1091]: https://github.com/2AMLogic/klayout-tools/issues/1091
[klt1099]: https://github.com/2AMLogic/klayout-tools/issues/1099
[klt1100]: https://github.com/2AMLogic/klayout-tools/issues/1100
[klt1709]: https://github.com/2AMLogic/klayout-tools/issues/1709
[klt1860]: https://github.com/2AMLogic/klayout-tools/pull/1860
[klt2357]: https://github.com/2AMLogic/klayout-tools/issues/2357
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
[DR-0025]: ../spec/decision-records/DR-0025-full-chip-pex-scope.md
