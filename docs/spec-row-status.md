# Target specification: row status and evidence history

This document holds the evidence narrative behind each row of the ratified
target specification in [`README.md`](../README.md#target-specification-ratified-2026-07-31).
The README table is the contract — target, stretch and a one-line status tag
per row. This document is the record of how each row's measured figures were
reached and how they moved: which issue measured what, which decision record
accepted or diagnosed it, and where the evidence lives under `sim/`, `layout/`
and `spec/`.

It changes nothing about the specification. No target value is set or moved
here; per `CLAUDE.md`, a row that cannot be met is answered by a superseding
decision record under `spec/decision-records/`, not by an edit to this file or
to the README.

**Append-only in spirit.** One section per row, in the README table's order.
When a figure moves, add a new dated `###` entry at the end of that row's
section — the issue, the new figure, and the record it comes from — and update
the README Status tag to match. Do not rewrite an earlier entry; a superseded
figure stays, marked as superseded by the entry that replaced it.

The 2026-10-10 entries are the row text and the "Ratified, with four rows
explicitly unmeasured" note exactly as they stood in `README.md` on that date,
moved here unchanged in substance by #481 (only relative link paths and
blockquote markers were adjusted for this file's location). Status words in
them — *placeholder*, *measured*, *met*, *missed*, *derived from a target* —
are the claims of record.

## Status tags

| Tag | Meaning |
|---|---|
| `met` | measured, and the measurement satisfies the target |
| `missed` | measured (or measured at gate level, per [DR-0021], or read from the regenerated floorplan rollup for Area), and the figure does not satisfy the target |
| `unmeasured` | no measurement exists; the row is a target or placeholder, not a claim (an estimate, where one exists, is stated as an estimate) |
| `derived from target` | computed from another row's *target*, so it carries that row's status and becomes measured only when that row does |
| `specified` | a design or interface decision with no measured quantity to meet or miss; its decision record is the source |

## Ratification: four rows explicitly unmeasured

### 2026-07-31 — ratification (2026-10-10: relocated from `README.md`, #481)

**Ratified, with four rows explicitly unmeasured.** The table was ratified
on 2026-07-31 by engineering (Robb) — see
[`spec/ratification-2026-07-31-target-spec.md`](../spec/ratification-2026-07-31-target-spec.md)
and issue #1 — together with the amendment package in #29. Every decision
record the rows above cite is `Accepted` except [DR-0017], which is
`Proposed` (its idle-current options are unchosen; see the Power note below);
[DR-0015] was `Accepted` 2026-10-10 via the two-key ratification mechanism,
#480; a row that cannot be met is a **superseding decision record**,
not an edit. What ratification does *not* do is turn placeholders into
claims:

- Raw min-entropy per bit — see [Raw min-entropy per bit](#raw-min-entropy-per-bit).
- Conditioning / delivered rate — see [Conditioning](#conditioning) and
  [Delivered (post-conditioning) rate](#delivered-post-conditioning-rate).
- Power — see [Power](#power).
- Area — see [Area](#area).

Each bullet's full text, as it stood on 2026-10-10, is reproduced under its row.

## Entropy source

### 2026-10-10 — relocated from `README.md` (#481)

The README row carried no evidence narrative beyond its own target text, which stays in the README table unchanged. Row text as it stood on relocation:

**Target cell:** **N-way array of independent free-running ring oscillators, XOR-combined ahead of a single sampler**, N fixed by the jitter-budget sizing law `Q_array ≥ 1.5 × 4.0×10⁻³` at the entropy-binding corner ([DR-0007])

**Stretch cell:** metastability hybrid, scoped as a *secondary tap on the RO core* — not a free-standing source

Sizing context recorded in the [Power](#power) section: [DR-0007]'s first-cut array size projected far more active power than the Power row allows, resolved by [DR-0010] shrinking the array to N = 2.

## Raw rate

### 2026-10-10 — relocated from `README.md` (#481)

The README row carried no evidence narrative beyond its own target text, which stays in the README table unchanged. Row text as it stood on relocation:

**Target cell:** > 1 Mbps sustained at the raw tap (sampler output), binding at the slowest-RO corner: `ss` / −10 % / +125 °C ([DR-0003])

**Stretch cell:** > 4 Mbps, same definition

The row's open question — that the rates [DR-0010] and [DR-0011-rate] re-derive sit far below it — is recorded under [Binding corners and the rate row](#binding-corners-and-the-rate-row). The [Delivered (post-conditioning) rate](#delivered-post-conditioning-rate) row inherits this row's status.

## Raw min-entropy per bit

### 2026-10-10 — relocated from `README.md` (#481)

Row text as it stood on relocation (the README keeps the placeholder statement, the binding corner and what is still owed; the measurement history below moved here):

**Target cell:** **placeholder — H₀ = 0.5 bit/sample is a design *target*, not a measurement.** Stated at the entropy-binding corner, which #13 measured over the full covered 27-point grid as **`ss` / +125 °C / 3.63 V** — the hot end of the `ss`/+10 % edge, *not* the cold end [DR-0012] predicted from three points ([DR-0015]; `fs`/`sf` remain uncovered per [DR-0006]). #12 applied the #10 methodology to the real sampler bitstream at the corners [DR-0012] predicted before that grid landed (`tt`/27 °C/3.30 V and `ss`/−40 °C/3.63 V) and found no non-trivial `H` figure is supportable by transistor-level simulation at any rate under consideration — the array's own sizing law predicts `H0 = 0.5` is plausible only near DR-0010's proposed (not yet ratified) 500 bps, and no affordable simulation reaches that rate. See [`sim/characterization-raw-min-entropy-and-battery.md`](../sim/characterization-raw-min-entropy-and-battery.md). The same analysis was then re-run at #13's actual worst corner (`ss`/+125 °C/3.63 V, #406): ten of ten sampled bits were `1` at every seed, a ten-bit stuck-high observation that supports no `H` figure either — the same ceiling, not a number. Still owed: measured silicon ([DR-0004] Tier 3)

From the ratification note ("Ratified, with four rows explicitly unmeasured"):

- **Raw min-entropy per bit** is a design target (H₀ = 0.5). The entropy
  source is *sized* to hit it ([DR-0007]); the corner it has to hold at is
  now measured over the whole covered grid and moved as a result
  ([DR-0015], from #13). #12 attempted the `H` measurement at the corner
  [DR-0012] predicted before that grid landed and found it is not
  supportable by transistor-level simulation at any rate under
  consideration (see
  [`sim/characterization-raw-min-entropy-and-battery.md`](../sim/characterization-raw-min-entropy-and-battery.md));
  confirmation at #13's actual worst corner is still owed.

## Quality

### 2026-10-10 — relocated from `README.md` (#481)

The README row carried no evidence narrative beyond its own target text, which stays in the README table unchanged. Row text as it stood on relocation:

**Target cell:** designed-for-SP 800-90B (raw access + RCT/APT + entropy-source model), plus a **simulation-derived design-stage min-entropy estimate** within the #10 claim limits; 90B validation itself deferred to measured silicon ([DR-0004])

**Stretch cell:** AIS-31 PTG.2 — same three-tier treatment (structure now, conformance deferred)

## Conditioning

### 2026-10-10 — relocated from `README.md` (#481)

The README row carried no evidence narrative beyond its own target text, which stays in the README table unchanged. Row text as it stood on relocation:

**Target cell:** **non-vetted** 32-bit CRC-32 LFSR compression (Galois, poly `0xEDB88320`), state cleared every block, **K = 8** — 256 raw bits in : one 32-bit word out. Creditable output entropy **0.85 bit per output bit** (SP 800-90B's non-vetted cap) for any raw stream at or above **H = 0.107 bit/sample**; a 4.70× margin under the H₀ = 0.5 target. ~0.005–0.008 mm² ([DR-0008])

**Stretch cell:** a 90B-*vetted* conditioning function — **rejected on area**: a compact serialised AES-128 is 88–124 % of the whole block budget ([DR-0008] §4). Live again only if the area budget grows

From the ratification note ("Ratified, with four rows explicitly unmeasured"), shared with the [Delivered (post-conditioning) rate](#delivered-post-conditioning-rate) row:

- **Conditioning / delivered rate** were deferred to #8; [DR-0008] has since
  filled both rows in. The delivered rate is still `R_raw / K` derived from a
  *target* raw rate — filling in K does not turn the raw-rate row into a
  measurement.

## Delivered (post-conditioning) rate

### 2026-10-10 — relocated from `README.md` (#481)

Row text as it stood on relocation (the README keeps the target; the "derived from a target" status became its Status tag):

**Target cell:** **`R_cond = R_raw / K` > 125 kbps** at the raw-rate row's binding corner (`ss` / −10 % / +125 °C), K = 8; > 500 kbps at the stretch raw rate. **Derived from a target, not measured** — it inherits the raw-rate row's status exactly, and becomes a measured figure only when `R_raw` does ([DR-0003] §6, [DR-0008] §3)

See also the ratification-note bullet under [Conditioning](#conditioning).

## Health tests

### 2026-10-10 — relocated from `README.md` (#481)

The README row carried no evidence narrative beyond its own target text, which stays in the README table unchanged. Row text as it stood on relocation:

**Target cell:** continuous RCT + APT on the **raw** stream, α = 2⁻⁴⁰, APT window W = 1024, cutoffs as formulas in min-entropy H (at H₀ = 0.5 → `C_RCT` = 81, `C_APT` = 824); failure latches a flag and gates the conditioned path until explicit clear + start-up test. The parameterization has a hard floor: **no valid APT cutoff exists at H ≤ 0.03** ([DR-0002])

## Time-to-first-valid

### 2026-10-10 — relocated from `README.md` (#481)

Row text as it stood on relocation (the README keeps the arithmetic floor; the measurement moved here):

**Target cell:** **≥ ~1.28 ms** at 1 Mbps — an arithmetic floor: 1024 consecutive raw samples for the start-up health test (1.024 ms) plus 256 samples of conditioner latency (0.256 ms), which do **not** overlap because the conditioner is held flushed while gated. Applies at power-on and after every alarm clear; binds at `ss` / −10 % / +125 °C (slowest sampling) ([DR-0002] §Failure behavior, [DR-0008] §7). **Now measured (#14): 1.281 ms**, the floor plus one sampler clock plus a 4.1–12.4 ns oscillator start-up (4.4–13.4 ns before #78's buffer adoption) — the row is met and the floor is confirmed as a floor ([`sim/characterization-startup-and-power-budget.md`](../sim/characterization-startup-and-power-budget.md))

The caveat #14 added about this row's binding corner is under [Binding corners and the rate row](#binding-corners-and-the-rate-row).

## Power

### 2026-10-10 — relocated from `README.md` (#481)

Row text as it stood on relocation (the README keeps the two targets and their binding corners; the measurement history moved here):

**Target cell:** < 500 µW active, binding at `ff` / +10 % supply (fastest RO — max measured `f_osc` 2.30 GHz at −40 °C); < 1 µA idle, binding at `ff` / +10 % / +125 °C (max leakage). **Now evidenced (#14, re-measured after #78's buffer adoption, #174/[DR-0023]'s substitution of #145's measured gate-level digital figure for the pre-synthesis estimate, #255/#266's re-synthesis and re-place-and-route of the digital section at [DR-0020]'s ratified `FIFO_DEPTH = 2`, #264/#277's re-tune of that depth-2 build's `max_transition_ns` (8.0 → 4.0) and rebuild, and #293's re-run of the same place-and-route on #292's re-baselined netlist, with #145's fifteen-corner `level: gate` sweep re-run against each rebuild — the current family is `sim/records/2026-10-07-digital-sta-power-{01..15}.md`): active 758.2 µW — missed by 1.5×, at 151.6 % of the row. Idle 2.21 µA — missed by ~2.2×**, and the cause on both halves is still the synthesized-and-placed digital section (348.2 µW active / 7.842 µW — 2.178 µA — leakage, MEASURED-at-gate-level, down from 712.4 µW / 4.062 µA at the depth-8 build #174/[DR-0023] first measured), not the analog block (393.2 + 16.9 µW active / 32.8 nA idle, measured, unchanged by the digital section's depth). Neither miss is absorbed: see [`sim/characterization-startup-and-power-budget.md`](../sim/characterization-startup-and-power-budget.md), §0a/§0b of [`sim/characterization-digital-sta-area-power.md`](../sim/characterization-digital-sta-area-power.md), [DR-0023] (`Accepted` 2026-09-07 via the two-key ratification mechanism, #213 — the active miss and the idle figure's revision, both stated there against the depth-8 build; `sim/tools/power_rollup.py` reads the digital term live from the committed record family, so #255/#266's depth-2 re-run, #264/#277's re-tuned rebuild and #293's re-run update the tool's own verdict without a new decision record) and [DR-0017] (`Proposed`, the idle row's own diagnosis and options, unsuperseded — not part of the #213 ratification batch), and the note below

From the ratification note ("Ratified, with four rows explicitly unmeasured"; "the note below" in the row text above is this one):

- **Power** was ratified with no supply-current or leakage measurement
  anywhere in `sim/`. "Idle" means: all ring oscillators stopped and no bits
  being produced, with the block powered and register state retained — i.e.
  leakage plus static bias only. #32 measured the delay cell, #7 the shipped
  array, #14 closed both halves of the row against a pre-synthesis digital
  estimate, **#174/[DR-0023] then substituted #145's measured gate-level
  digital figure for that estimate — both halves were missed** at the
  `FIFO_DEPTH = 8` build #145 measured, and **#255/#266 then re-synthesized
  and re-placed-and-routed the digital section at [DR-0020]'s ratified
  `FIFO_DEPTH = 2`** — the depth actually shipped since #254 — **and re-ran
  #145's same fifteen-corner sweep against it**. That first depth-2 build
  violated the library's own `max_transition` check at 11 of the 15 corners,
  so **#264/#277 re-tuned `max_transition_ns` (8.0 → 4.0) for the depth-2
  topology, rebuilt, and re-ran the same sweep once more**. **#293 then
  re-ran that place-and-route on #292's re-baselined netlist** (one
  drive-strength swap, which #292 committed without rebuilding the layout
  downstream of it) and re-ran the sweep again — the current build is the
  committed `sim/records/2026-10-07-digital-sta-power-{01..15}.md` family
  (the 2026-09-22 family is #264/#277's), and
  `power_rollup.py` picks each of these up automatically because its digital
  term already reads live from that family ([DR-0023], §0a/§0b of
  [`sim/characterization-digital-sta-area-power.md`](../sim/characterization-digital-sta-area-power.md)).
  #293's re-run moved the digital terms by under 1 % active and +4.4 %
  leakage, mostly from the OpenROAD build that re-ran it rather than from
  the netlist; §0b separates the two with a control run.
  **Both halves are still missed, by a materially narrower active margin
  than at depth 8 — and, on the idle half, by a slightly wider one than the
  violating depth-2 build showed**:
  - **Active: missed, by 1.5×** (was 2.2×). 758.2 µW at `ff`/−40 °C/3.63 V —
    entropy source 393 µW (measured), sampler 16.9 µW (measured), digital
    section 348.2 µW (**MEASURED-at-gate-level** at its own worst corner,
    `ff_125C_3v60`/`rc-max`, [DR-0021]; 345.6 µW at #264/#277's build
    before #293's re-run, down from 358.5 µW at #255/#266's
    violating depth-2 build, from 712.4 µW at the depth-8 build, and from a
    [DR-0004] Tier 2 pre-synthesis estimate of 23 µW before any netlist
    existed to synthesize). [DR-0010]'s stated worry,
    that the array leaves only ~85 µW for everything downstream, is still
    realized rather than merely tight, just less severely: the digital
    section alone is now 3.3× everything the array leaves, versus 6.7× at
    depth 8. #14 first measured this row at **454 µW** (entropy source
    415 µW, digital still estimated); #78 then adopted the per-ring output
    buffer ([DR-0018]), which *returns* power rather than spending it,
    moving the row to **433 µW (met, at 86.6 %)**; #174/[DR-0023] then
    replaced the digital estimate with the depth-8 measured gate-level
    figure (1.122 mW, 224.5 %, missed by 2.2×); #255/#266's depth-2
    re-synthesis (768.5 µW, 153.7 %) is the reason the miss narrows,
    #264/#277's re-tuned rebuild gave 755.6 µW (151.1 %), and #293's
    re-run on the re-baselined netlist is the number above. The
    entropy source's own share (393 + 17 µW) is unchanged by any of these
    substitutions — the digital section's own build is the only thing that
    moved.
  - **Idle: missed, by ~2.2×** (2.12 µA at #264/#277's build before #293's
    re-run, ~2.0× at the violating depth-2 build, ~4.1× at depth 8, 4.5×
    estimated). 2.21 µA at
    `ff`/+125 °C/3.63 V — analog block 32.8 nA (3.3 % of the row, measured
    across 45 corners, unchanged), digital leakage 2.178 µA / 7.842 µW
    (**MEASURED-at-gate-level**; 2.087 µA at #264/#277's build, and §0b of
    the characterization's control run splits the +0.091 µA since then into
    +0.087 µA from the OpenROAD build #293 re-ran on and +0.004 µA from
    #292's netlist; down from 4.062 µA at the depth-8 build and
    from 4.43 µA estimated before any netlist existed, but *up* from the
    1.974 µA #255/#266's violating depth-2 build measured: #264/#277's
    tighter transition target buys its clean `max_transition` and its lower
    dynamic power with +30 logical instances and +3.7 % placed cell area,
    which is static current the earlier build did not pay). The
    ratification note above guessed the cause exactly — the entire
    remaining miss is standard-cell leakage in the conditioner, health
    tests, interface and #171's power-delivery cells. `gf180mcu_fd_sc_mcu7t5v0`
    ships no retention flop and no power-switch cell, so the obvious fix is
    not a library instantiation; shrinking the FIFOs ([DR-0020]) is the
    lever that produced this narrower miss, and [DR-0017] §B already
    projected that no `FIFO_DEPTH` closes it.

  Per `CLAUDE.md` no row is edited here: the digital-term substitution and
  the active miss it causes are recorded in [DR-0023] (`Accepted` 2026-09-07
  via the two-key ratification mechanism, `2AMLogic/2am#372`/#213); [DR-0017]
  (`Proposed`, not part of the #213 ratification batch) remains the record
  for the idle row's diagnosis and its four priced options, unsuperseded —
  [DR-0023] only narrows its headline figure.
  [DR-0007]'s separate conflict — that its first-cut array size projected far
  more active power than this row allows — was resolved by [DR-0010]
  shrinking the array to N = 2, which is the 415 µW measured above.

## Area

### 2026-10-10 — relocated from `README.md` (#481)

The README row carried no evidence narrative beyond its own target text, which stays in the README table unchanged. Row text as it stood on relocation:

**Target cell:** < 0.05 mm²

From the ratification note ("Ratified, with four rows explicitly unmeasured"):

- **Area: the regenerated floorplan misses by 3.5×.** The row is
  `< 0.05 mm²`. The current figure is the regenerated depth-2 floorplan
  rollup in `layout/floorplan/reports/area.json` (#256, via #454):
  **175 789.9 µm² including isolation channels, 351.6 % of the row** (a
  floorplan-area sum; the row bounding box, 934.4 × 416.7 µm, is reported
  separately). The rest of this bullet is historical context from before
  that regeneration. #16's floorplan work had priced the block bottom-up
  against the PDK's own standard-cell LEF:
  **0.06885 mm², 137.7 % of the row** at the shipped `FIFO_DEPTH = 2`
  (**0.13918 mm², 278.4 %** at the depth-8 default the paragraph below and
  [DR-0019] were written against)
  ([`layout/floorplan/reports/area.json`](../layout/floorplan/reports/area.json),
  breakdown under *Area against the `< 0.05 mm²` row* in
  [`layout/floorplan/README.md`](../layout/floorplan/README.md)).
  The split matters — the isolated entropy source, samplers, guard rings and
  isolation channels together are **14.05 %** of the row (the 4.7 % this line
  used to quote predates #135/#209/#210's analog-region resizes; the figure
  here is what the same re-run prints), and the whole miss is
  the digital section at **251 %**, of which the two 8 × 32-bit output FIFOs
  are 69.8 % (both figures at depth 8; at depth 2 the digital section is
  114.1 % of the row and the FIFOs are 11 626 µm², 34.5 % of its cell area).
  That is the same structure [DR-0017] blames for the idle-current
  miss: one design decision showing up on two rows. It is an inventory
  estimate with a stated method — no synthesiser, placer or router has run on
  this block — so it is not a measurement, and per `CLAUDE.md` the row is not
  edited here: the miss is recorded in [DR-0019] (`Accepted` 2026-09-07 via
  the two-key ratification mechanism, `2AMLogic/2am#372`/#213), which priced
  four available responses and found that the shared FIFO-depth lever
  reaches the two rows very differently — futile on idle current at every
  depth ([DR-0017] §B), but worth 269.4 % → 105.8 % of the area row between
  depth 8 and depth 1. Its ratified Decision (option C) therefore holds the
  row rather than moving it, and sequences the response behind the
  `FIFO_DEPTH` decision jointly owned with [DR-0017] and [DR-0013]. That
  joint decision is itself now [DR-0020] (also `Accepted` 2026-09-07,
  same mechanism): `FIFO_DEPTH = 2`. **That value is now shipped** — issue
  #254 carried it into `design/interface/regmap.py`, the RTL parameter
  default and both inventory estimates — and re-running the floorplan at it
  brings the estimate from **278.4 % to 137.7 %** of the row (0.13918 mm² →
  **0.06885 mm²**; the digital section's own cell area falls 74 485 µm² →
  33 655 µm², and 40 357 µm² of that 40 831 µm² drop is FIFO storage, read
  mux and per-word clock gates). At that
  time it was still a miss, by 1.4×, and it moved the *estimate* only: the
  composed figure in `area.json` was then **642.9 %**, measured from
  `layout/digital/trng_top.gds`, the depth-8 place-and-route, which #254 did
  not re-synthesize (superseded by the #256 regeneration, above). The 129.4 % [DR-0020] itself quotes is superseded by the
  137.7 % above: that figure predated issues #119/#135's analog-region
  resizes and was computed against the older 269.4 % baseline.

## Operating envelope

### 2026-10-10 — relocated from `README.md` (#481)

The README row carried no evidence narrative beyond its own target text, which stays in the README table unchanged. Row text as it stood on relocation:

**Target cell:** −40 … +125 °C, 3.3 V ± 10 % (2.97–3.63 V). Every entropy, rate and health-test claim above holds **over this envelope and only over it**; the envelope is the security boundary, since an attacker chooses the operating point. Outside it, behavior is health-test-detected, not specified

## Interface

### 2026-10-10 — relocated from `README.md` (#481)

The README row carried no evidence narrative beyond its own target text, which stays in the README table unchanged. Row text as it stood on relocation:

**Target cell:** streaming, mode-selectable raw / conditioned (`OUT_MODE`), + register read (`DATA` conditioned, `RAW_DATA` raw); raw access always available and never gated ([DR-0001]). Instantiated as four word-addressed registers — `CTRL`, `STATUS`, `DATA`, `RAW_DATA` — plus a 32-bit valid/ready streaming port, with a health-test gate that flushes the conditioned path and **never** the raw one ([DR-0013])

## Binding corners and the rate row

### 2026-10-10 — relocated from `README.md` (#481)

Note also that rows bind at **different** corners, and none at nominal: rate
at the slowest-RO corner, min-entropy per bit at the *least*-jitter
(minimum-`Q`) corner, power at the fastest/leakiest corner, time-to-first-valid
at the slowest-sampling corner. One caveat #14 added to that last one:
[DR-0012] made the sample clock a *fixed external* clock, so the sample
period does not move with PVT, and 99.999 % of the time-to-first-valid row is
1281 fixed sample periods. Its stated binding corner is formally correct and
practically vacuous — the spread across the whole covered grid is 9 ns on
1.281 ms. What does move that row is the **rate**, and the rate row is
unsettled: at [DR-0010]'s 500 bps (`Accepted` 2026-10-10, #480, via the
two-key ratification mechanism) the same 1281 samples take **2.562 s**, and at
the 2 kbps [DR-0011-rate] re-derived from the shipped starved cell (also
`Accepted` 2026-10-10, superseding DR-0010 §1's value only) they take
**641 ms**. Ratifying the two records did not move the `Raw rate` row: the
row edit their Decisions direct is a separate follow-up. Both sit far below
the `> 1 Mbps` row as it still stands — 2000× and 500× below it respectively
— and that gap, not the arithmetic above it, is the
open question.

[DR-0001]: ../spec/decision-records/DR-0001-raw-and-conditioned-output-paths.md
[DR-0002]: ../spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md
[DR-0003]: ../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0004]: ../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0006]: ../spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md
[DR-0007]: ../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md
[DR-0008]: ../spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md
[DR-0009]: ../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0010]: ../spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0011-rate]: ../spec/decision-records/DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md
[DR-0012]: ../spec/decision-records/DR-0012-sampler-fixed-external-clock.md
[DR-0013]: ../spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md
[DR-0015]: ../spec/decision-records/DR-0015-entropy-binding-corner-moves-to-the-hot-slow-corner.md
[DR-0017]: ../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
[DR-0018]: ../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md
[DR-0019]: ../spec/decision-records/DR-0019-area-row-versus-output-fifo-dominated-digital-section.md
[DR-0020]: ../spec/decision-records/DR-0020-fifo-depth-set-to-two-against-power-area-and-streaming.md
[DR-0021]: ../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
[DR-0023]: ../spec/decision-records/DR-0023-power-rollup-digital-term-becomes-measured-gate-level-power.md
