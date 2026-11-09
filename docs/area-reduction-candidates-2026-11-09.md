# Digital cell-area reduction candidates (2026-11-09)

Append-only analysis record for issue #799 (a ranked proposal under #793, part
of #700). It follows `docs/area-economy-accounting-2026-11-09.md` (the
"accounting record", not edited here) and answers one question: **which cells
in the committed digital netlist could be removed, and is the total enough to
close the digital cell-area gap?**

It changes no RTL, spec row, decision record, floorplan or generator. The
ratified Area row (< 0.05 mm^2) stays as written and its miss stays disclosed
as FAIL. Nothing was synthesized, placed, routed or simulated to produce this
record; every saving is an **estimate** from the committed netlist.

Measured on `main` at `044f02194cb72f8598122156625c820e4d495027`
(`klt 0.9.2.dev385+gfafa69b5f3b6`). `git diff` of `layout/digital/trng_top.pnr.v`
and of `design/{interface,conditioner,health_test,trng_top}` between the
accounting record's commit (`cdaf2fee`) and this one is empty, so the
accounting record's 59 264.8 um^2 lower bound applies unchanged.

## Method

1. Parse `layout/digital/trng_top.pnr.v` (1 423 logical cells). Group cells by
   instance-name prefix, as the accounting record did.
2. Price each cell as site footprint = (`klt economy` cell bbox width - 0.86 um)
   x 5.04 um. This reproduces the accounting record's 59 264.8 um^2 total
   exactly. Cross-check made here: for the cell types used below
   (`dffq_1`, `dffrnq_1`, `dffsnq_1`, `mux2_1`, `mux2_2`, `icgtp_1`, and the
   difference `dffrnq_1 - dffq_1`) the footprint equals the Liberty `area`
   attribute (tt_025C_5v00) to four digits, e.g. `dffq_1` 79.027, `dffrnq_1`
   90.317, `mux2_1` 36.691, `mux2_2` 42.336, `icgtp_1` 76.205 um^2.
3. Attribute cells to RTL registers by following netlist connectivity: a
   flip-flop's `Q` net name carries the RTL register name, and "hold mux" means
   a `mux2` whose output drives a flop `D` and whose `I0` or `I1` is that same
   flop's `Q`.
4. A candidate is ranked only if its saving is a sum of specific cells found
   this way. Savings are cell area at 100 % utilization (the accounting
   record's lower-bound convention); they are **not** die-area savings.

**Stated uncertainty, carried on every figure:** the accounting record could
not reconcile 1 479 um^2 (2.5 %) between this footprint method and OpenROAD's
placed area. Treat every saving below as +/- that order of magnitude in the
absolute total, not as a per-candidate error bar. Logic that would change
alongside a removed register (incrementer bits, enables, compare terms) is
named but **not priced** unless stated.

## Cell inventory the candidates come from

Flops by RTL register (all counts from `Q` net names; 319 flops, 27 038.1 um^2):

| Register | Flops | Cell | um^2 |
|---|---:|---|---:|
| `u_interface/cond_mem` | 64 | `dffq_1` | 5 057.7 |
| `u_interface/raw_mem` | 64 | `dffq_1` | 5 057.7 |
| `u_interface/raw_shift` | 31 | `dffq_1` | 2 449.8 |
| `u_conditioner/state` | 32 | `dffrnq_1` | 2 890.1 |
| `cond_word` (conditioner output register) | 32 | `dffrnq_1` | 2 890.1 |
| `u_conditioner/count` | 8 | `dffrnq_1` | 722.5 |
| `u_interface/cond_count`, `raw_count_w` | 4 + 4 | `dffrnq_1` | 722.5 |
| `u_health_test` `apt_match`, `apt_pos`, `startup_count` | 11 each | `dffrnq_1` | 2 980.5 |
| rest (state, flags, small counters, ring liveness) | 47 | mixed | 4 267.2 |

**Hold muxes.** 191 flops hold their value through a feedback `mux2`
(`cond_word` 32, `cond_mem` 64, `raw_mem` 64, `raw_shift` 31): 7 341.0 um^2
(`cond_word` 1 337.8, `cond_mem` 2 517.6, `raw_mem` 2 348.2, `raw_shift`
1 137.4). The netlist contains no integrated clock-gating cell. This is the
same fact DR-0023 (decision 2) records: the synthesized netlist maps every
write-enable to a feedback `mux2`.

## Ranked candidates

"Evidence" is the netlist cells the saving is the sum of. "Behavior" says
whether externally visible behavior changes. Rows are ordered by saving.

| Rank | Candidate | Saving, um^2 | Evidence | Behavior / spec exposure |
|---:|---|---:|---|---|
| 1 | **C1: clock-gate the four storage registers' write enables** (6 `icgtp_1`: `cond_word`, 2 `cond_mem` words, 2 `raw_mem` words, `raw_shift`) in place of their hold muxes | 6 883.8 | 191 hold muxes 7 341.0 - 6 x 76.2 (`icgtp_1`) = 457.2 | No logical change. Introduces gated clocks into CTS and the timing flow; the saving excludes any extra clock-tree buffers. Not forbidden by any ratified row that I found; DR-0023 and DR-0019 both treat clock gating as the intended structure. Needs the power-intent and tap-distance checks re-run. |
| 2 | **C2: delete the conditioner's `cond_word` output register**; write `next_state` into the interface FIFO directly at block end | 2 966.3 incremental over C1 (4 227.9 if C1 is not taken) | 32 `dffrnq_1` 2 890.1 + (hold muxes 1 337.8, or with C1 the one gate 76.2) | **Changes cycle timing**: the word is pushed in the cycle `cond_valid` is asserted instead of the next cycle, so the interaction with `flush_cond`/`cond_ready` in that cycle moves by one. DR-0001/DR-0002 flush semantics and the word-for-word model comparison must be re-established; not a spec relaxation but not proven equivalent here. |
| 3 | **C3: remove the asynchronous reset from `u_conditioner/state` and `count`** (40 `dffrnq_1` -> `dffq_1`) | 451.6 | 40 x (90.317 - 79.027) | The LFSR and counter are cleared synchronously on every edge where `en` is low (`if (flush \|\| !en)`), and `en` is low until the start-up test passes, so no reset-dependent value is observable. The interface's `raw_shift` already uses this pattern. Needs a reset-state check against the behavioral model. |
| 4 | **C4: size the interface level counters for `FIFO_DEPTH`** (`cond_count`, `raw_count_w`: 4 -> 2 bits, zero-extend in `status_value`) | 361.3 + unpriced logic | 4 `dffrnq_1` (2 per counter); the upper two bits are provably 0 at depth 2 (`*_room` blocks a push at count 2) | None: the STATUS level fields keep their ratified 4-bit width (DR-0013) and read the same values. The adder/compare bits that disappear with them are real but not priced. |
| 5 | **C5: count APT mismatches instead of matches** (11 -> 8 bits, saturating) | at most 270.9 | 3 `dffrnq_1`; the pass condition `matches >= 824` over W = 1024 is `mismatches <= 200` | None if exact. The saturating logic may consume most of the saving, so this is an upper bound and may be near zero. |
| | **Sum of ranked candidates** | **10 933.9** | | 18.4 % of the 59 264.8 um^2 lower bound |

Candidates C1-C5 do not overlap, except that C2 and C1 both touch `cond_word`'s
hold muxes; row 2 is stated incrementally for that reason.

**Not priced, noted for the follow-up:** 11 buffers (874.9 um^2) drive only the
hold-mux select nets. Gating removes their fanout, but the gated clock needs
clock-tree buffers of its own; the net effect needs a real CTS run. The 31
`buf_8` cells in total (2 274.9 um^2) are timing-repair buffers from the flow
and are not RTL-owned.

## Flagged, not proposed

These save area but would weaken or reopen a ratified decision. They are
listed so the reader can see what the ranked list leaves out, not as
proposals.

| Idea | Cells | Saving, um^2 | Why not proposed |
|---|---|---:|---|
| `FIFO_DEPTH = 1` for either FIFO | 32 `dffq_1` + 32 hold `mux2_1` per word, plus pointer and read-mux logic | about 3 703 per FIFO, flops and muxes only | DR-0020 (Accepted) rejects depth 1 as a single-entry buffer with no elasticity. |
| Pack raw bits in place in the `raw_mem` slot, deleting `raw_shift` | 31 `dffq_1` + 31 hold muxes | 3 587.2 | A slot being filled is not available to queue, so total word storage falls from 3 to 2 and a full FIFO could no longer accept the completing word. That is the DR-0020 depth-1 trade by another route, and changes the OVF semantics of DR-0013. |
| Share `startup_count` with `apt_pos` | 11 `dffrnq_1` | up to 993.5 | Not equivalent: `startup_count` is also cleared by an RCT failure mid-window, `apt_pos` is not. Would change DR-0002 start-up behavior. |
| Drop the reset from health-test and liveness counters | `dffrnq_1` -> `dffq_1` | 11.29 per flop | With `CTRL.EN` resetting to 1 no `startup_req` clears them before first use, so reset is load-bearing there. |

## Does the list reach the target?

The accounting record's target is 50 000 um^2 of digital cell area against a
lower bound of 59 264.8, a gap of **9 264.8 um^2**.

- Against that digital-only gap, the ranked total is **10 933.9 um^2: it
  exceeds the gap by 1 669.1 um^2**, but only at **100 % utilization**, which
  no placed layout reaches (the committed block is at 43.4 %, the best swept
  point 90.4 %).
- The Area row (< 0.05 mm^2) covers the whole block, not just the digital
  section. Adding the analog guarded area from the accounting record's
  section 4 (6 526.4 um^2) to the digital lower bound gives 65 791.2 um^2, a
  gap of **15 791.2 um^2**. Against that, the ranked total falls
  **4 857.3 um^2 short**.
- Remaining digital cell lower bound after all ranked candidates:
  59 264.8 - 10 933.9 = 48 330.9 um^2, still 96.7 % of the 50 000 um^2 budget
  before any whitespace, margin, guard ring or the analog blocks.

**Statement: the ranked candidates do not reach the Area row.** They bring the
digital cell lower bound under 50 000 um^2 on paper, but the row is whole-block
and the placed block is a multiple of the cell bound. The row stays FAIL, and
the accounting record's placement and floorplan levers (#797 and the others it
ranks above cell area) remain necessary. These candidates are still the only
levers that reduce the multiplier's base, worth about 2.3 um^2 of die per
um^2 of cell removed at the 40 % point.

## Spec rows and decision records touched

None edited. Exposure by candidate: C1 (DR-0017 and `design/power-intent.md`
clock/always-on structure; DR-0023 treats gated clocks as the intended
structure), C2 (DR-0001, DR-0002 flush and gate timing; DR-0008 word-for-word
conditioner model), C3 (DR-0008 reset/flush description), C4 (DR-0013 register
map: unchanged by construction), C5 (DR-0002 APT parameters: unchanged cutoff).
The ratified Area row is not relaxed.

## Limits

- Savings are estimates, not re-synthesis; synthesis may restructure logic
  (for example merge a removed register's logic into neighbours), moving a
  figure in either direction.
- C1 and C2 add or move timing paths that were not analyzed; C2 and C3 need a
  cycle-accurate equivalence run before any RTL issue is filed.
- The 1 479 um^2 unreconciled difference (accounting record, section 3) applies
  to all absolute figures.
- Footprint pricing excludes tap, endcap and fill cells and the guard ring.

## Reproduce

```sh
klt economy layout/digital/trng_top.gds --attribute --format json > econ.json
```

Then, per the Method section: parse `layout/digital/trng_top.pnr.v`, price each
instance at (`bbox width` - 0.86 um) x 5.04 um using the `cells` list in
`econ.json`, key flops by their `Q` net name, and find hold muxes as `mux2`
cells whose `I0` or `I1` equals the driven flop's `Q`. Expected checks: total
59 264.8 um^2 over 1 423 cells; 191 hold muxes totalling 7 341.0 um^2.
