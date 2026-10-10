# signoff/ — this block's T1 state, graded rather than hand-read

`signoff/records/t1-tier-report.json` is **this block's verdict of record**
against the klayout-tools design-evidence ladder
([`docs/design-evidence-tiers.md`](https://github.com/2AMLogic/klayout-tools/blob/main/docs/design-evidence-tiers.md)).
It is not prose about where the block stands; it is the literal output of

```bash
klt signoff --manifest signoff/block-manifest.json --format json
```

re-run by CI on every push, so it cannot quietly go stale the way a
hand-maintained checkbox list does. Issue
[#124](https://github.com/2AMLogic/gf180-trng/issues/124) — this repo's
gap-to-T1 tracker — cites it and no longer keeps a parallel checklist of its
own.

<!-- current-t1-status:begin -->**Today: `tier: null`, T1 8 of 22 items met.**<!-- current-t1-status:end --> A `mixed-signal` block is
graded twice over, once per partition, so the eleven-item checklist renders
22 rows. The eight met are item 3 (DRC), item 4 (LVS), item 7 (post-layout
verification) and item 8 (characterization report) on **both** partitions.
Item 7 digital is
[#314](https://github.com/2AMLogic/gf180-trng/issues/314): see "Item 7 digital"
below for what that citation does and does not mean. Item 7 analog is
[#326](https://github.com/2AMLogic/gf180-trng/issues/326), and its `met` is
the weakest in this file: it cites ring1 alone, and the cited report's own
`body_bias.status` is `"unbiased"` — see "Item 7 analog" below before
reading anything into it. Item 8 analog is
[#313](https://github.com/2AMLogic/gf180-trng/issues/313): see "Item 8 is
`met` on both partitions" below. An item-8 `met` means a current aggregate
exists, not that the rows in it pass.
That is the honest state of the block; the rest of this file is why each of
the other fourteen reads the way it does.

Items 3 and 4 read `met` on the digital partition as of
[#273](https://github.com/2AMLogic/gf180-trng/issues/273), which moved the
count from 3 of 22 to 5 of 22. **No verification was added to reach it** —
the digital DRC and LVS runs had been clean and matching since #170/#187
(re-run at `FIFO_DEPTH = 2` by #255/#266); their reports were simply being
committed as reduced summaries instead of gradeable `klt` envelopes. The
re-run under klt 0.6.0 reproduced both verdicts exactly: `status: clean`,
`violation_count: 0` for DRC (byte-identical to the digest
`reports/place_and_route.json` already carried) and `status: match`,
`mismatch_count: 0` for LVS.

**This is a narrower reading than the prose checklist it replaces.** Issue
#124 last hand-read this block at 9 of 11 items passing. The two readings do
not disagree about the design — they disagree about what counts as evidence.
#124 was reading whether the *work* had been done; this file reads whether a
`klt` JSON envelope exists that a third party can re-grade without taking
anyone's word for it. Most of this repo's verification evidence is real,
committed, checksum-guarded, and in this repo's own Markdown record format
rather than in a `klt` envelope — so it is invisible to the grader. See "What
would move the needle" at the end: almost every gap below is an evidence-
*format* gap, not missing work.

## What is here

```
signoff/
  block-manifest.json                              the manifest: block, kind, per-item evidence
  evidence/characterization-digital.generic.json   item 8 (digital)'s generic evidence envelope
  evidence/characterization-analog.generic.json    item 8 (analog)'s generic evidence envelope
  records/t1-tier-report.json                      the verdict of record (generated)
  evidence/post-route/gate_klt_response.json       item 7 (digital)'s native klt functional-verification response
  evidence/post-route/publication.json            its freshness pins (netlist, SDF, raw evidence) and coverage limits
  publish_item7.py                                 publishes a successful post-route run as the 7.digital citation
  evidence/post-layout/ro_ring11.pex.json          item 7 (analog)'s native klt pex response over ring1's layout
  evidence/post-layout/ro_ring11.extracted.spice   the netlist that klt pex run extracted and simulated
  evidence/post-layout/publication.json            its testbench-side pins (request, testbench body, schematic DUT) and body_bias status
  publish_item7_analog.py                          runs klt pex over ring1 and publishes it as the 7.analog citation
  check.py                                         re-grade + freshness gate (CI runs this)
```

- `block` is `"gf180-trng"`. It is required: it is how this block's row is
  identified in the fleet roll-up (`klt signoff --fleet`, 2AMLogic/2am#956),
  which consumes exactly this manifest.
- `kind` is `"mixed-signal"`. Confirmed against the block rather than taken on
  faith — see the next section.

## The partition boundary

A `mixed-signal` claim must state the partition boundary explicitly, so a
reviewer can tell which evidence covers which silicon. It is declared in the
manifest itself, in `partition_boundary` (klayout-tools#2278), so it travels
with the claim rather than living only in prose — `klt signoff` echoes it on
every T1 row of the report, reported and never graded, since no tool can
check free text against silicon. This block genuinely has both partitions,
built by two different flows:

| | Analog partition | Digital partition |
|---|---|---|
| Regions | `ring1` (`ro_ring11`), `ring2` (`ro_ring11_ring2`), `combiner_sampler` (which contains both [DR-0018](../spec/decision-records/) `ro_buf` instances) | `digital` (top cell `trng_top`) |
| Sources | hand-captured xschem schematics under `design/xschem/`, netlisted by `design/netlist.py` | Verilog RTL under `design/trng_top/`, synthesized by `design/synth.py` (yosys) to `design/trng_top/trng_top.synth.v` |
| Layout | hand-drawn cells under `layout/cells/`, `layout/rings/`, `layout/blocks/` | `klt place-and-route` output, `layout/digital/build.py` → `layout/digital/trng_top.def`/`.gds` |
| Verification | ngspice PVT/Monte-Carlo sweeps under `sim/` | gate-level STA and post-route functional re-simulation |

The boundary itself — every net that crosses it, with the pin it lands on at
each end — is declared in `design/floorplan_netlist.py`'s `INTER_REGION_NETS`
and machine-checked against both sides' committed reference netlists by
`npm run check:floorplan-netlist` (issue #221). The crossing nets are:

- **signal**: `clk`, `rst_n` (chip pin → `digital` → `combiner_sampler`),
  `raw_bit`, `raw_valid` (`combiner_sampler` → `digital`), `ring_bit1` →
  `digital`'s `ring_bit[0]`, `ring_bit2` → `digital`'s `ring_bit[1]`;
- **supply**: `vddd` (digital only) and the one deliberately shared net,
  `vss`, which all four regions return to.

The ring supplies `vddr1`/`vddr2` and the combiner/sampler supply `vdd` are
analog-side star branches that never reach the digital region. So this is a
real two-column claim, not a single-column block wearing a mixed-signal
label.

## Running it

```bash
pip install "klayout-tools==0.6.0"   # the grader; no PDK, no KLayout GUI needed
python3 signoff/check.py             # verify (what CI runs)
python3 signoff/check.py --write     # regenerate the verdict of record
npm run check:signoff                # same as `python3 signoff/check.py`
```

`check.py` pins the klayout-tools version it grades against, and that pin is
load-bearing: `klt signoff` parses the T1 item list out of klayout-tools' own
`docs/design-evidence-tiers.md`, bundled inside the installed wheel, so **the
tool version is the yardstick**. klayout-tools 0.5.0 renders a ten-item
checklist and no item-11 row at all, because T1 item 11 ("Power delivery
(structural)", klayout-tools#2025) landed after that release. 0.6.0 renders
eleven. The record carries `build.version`, `build.git_commit`,
`build.grading_ruleset_id` and `source_doc_content_hash`, so which checklist
and which grading rules produced a given verdict is recorded in the verdict,
not inferred from the date on it.

`check.py` fails on four separable conditions, so a red build says which one:

1. **A cited envelope no longer describes the artifact it ran on.** The
   manifest's pin is compared by `klt signoff` against the *envelope's own*
   `provenance.input.content_hash` — two committed files agreeing with each
   other, which proves nothing if both came from the same stale run. Since
   klayout-tools#2196 the grader also re-hashes the artifact itself where it
   can (`citation.input_verified`), but only for a citation that both pins a
   hash and names a resolvable path: in the committed record that is `true`
   for every pinned citation of a met item except `8.digital` and
   `8.analog`, the two `generic` envelopes, whose backing documents the
   grader does not re-hash (`4.analog` joined the verified set in
   [#281](https://github.com/2AMLogic/gf180-trng/issues/281), `7.analog` in
   [#326](https://github.com/2AMLogic/gf180-trng/issues/326)).
   `check.py` covers the whole set regardless of envelope kind — it
   verified 12 of 12 on the run that produced the committed record (one of
   them the 7.digital publication, checked by its own pins, see "Item 7
   digital"; the 7.analog publication's testbench-side pins are checked on
   top, see "Item 7 analog"). Edit
   `layout/blocks/combiner_sampler/combiner_sampler.gds`,
   `layout/digital/trng_top.gds`, `layout/digital/trng_top.extracted.spice`,
   `sim/characterization-digital-sta-area-power.md` or
   `sim/characterization-analog-summary.md` without re-running the
   evidence behind them and this fails.
2. **The manifest and the envelope disagree about the pin**, so a
   half-finished re-pin fails loudly instead of silently rendering the item
   `stale_evidence`.
3. **`klt signoff --manifest` could not run** (exit 1 or 2 — a broken manifest
   or an unparseable tier doc; exit 0 and exit 3 are both clean runs).
4. **The committed record no longer matches a fresh run.** Either this block's
   evidence moved, or the checklist did, or the grader did. All three are real
   news, and none should be discoverable only by someone re-reading prose.

## Item 7 digital

The citation is the **native** response of `klt functional-verification` from
the SDF-annotated gate leg of `sim/tb/trng-top-post-route/` (8 of 8 scenarios
passed, `environment.sdf.annotated: true`), copied byte for byte. The pinned
grader (klt 0.6.0) grades it `met`: kind `functional-verification`, status
`pass`, annotated.

**Schema limitation.** That envelope carries no `provenance` block, so the
manifest cannot pin a `content_hash` for it (the grader would render
`unverifiable_provenance`), and the grader reports `input_verified: null`. The
entry is therefore unpinned, and freshness is enforced by `check.py` instead
(`verify_item7_publication`, always run, stdlib only): `publication.json` pins
the post-route netlist **and** the SDF separately by sha256, plus the raw
evidence of the run (both legs' responses, comparisons, transcripts, requests
and `verdict.json`). `check.py` fails if either input changed since the run,
if any raw file changed, if the verdict or any of its checks (gate-vs-RTL
equivalence, SDF annotation applied, annotation control fired, no X on a pin)
is not true, or if the envelope is not a pass or not annotated.
`publish_item7.py` refuses to write anything under the same conditions, so a
failed comparison or failed annotation control cannot become current evidence.

Cold start (the producer needs a cocotb-capable `klt`, see the testbench
README):

```bash
TRNG_POST_ROUTE_KLT=<venv>/bin/klt python3 sim/tb/trng-top-post-route/run_demo.py
python3 signoff/publish_item7.py
python3 signoff/check.py --write
```

**What it does not claim.** One corner (SDF `typ` from the `ss_125C_3v00`
liberty) — not a PVT claim. Cell `IOPATH` delay only; no interconnect delay.
Icarus 13.0 enforces no setup/hold/width check and drops SDF `TIMINGCHECK`, so
a timing violation not reported is not evidence of none. `ifnone`-qualified
edge-sensitive arcs (`xor`/`xnor`/`mux`/`addf`/`addh` select/toggle) run at the
library default delay. Functional equivalence with applied delays is narrower
than timing signoff, which stays with OpenROAD STA. The citation's `klt pex`
`body_bias` disclosure does not apply (no extracted netlist is simulated).

## Item 7 analog

The citation is the **native** JSON response of one `klt pex` run (#326),
copied byte for byte by `publish_item7_analog.py`. The pinned grader grades
it `met`: kind `pex`, `status: "pass"`, `content_hash` pinned to
`layout/rings/ro_ring11/ro_ring11.gds`, `input_verified: true`.

**Schematic DUT vs design source (#351).** Three identities are kept apart:
the *source* (`design/ro_array_core.spice`), the *generated fixture*
(`ro_ring11_schematic.spice`, sha256-pinned in `publication.json`) and the
*simulated fixture* (what the `klt pex` run hashed). The always-on check
re-renders the DUT with `build_dut.py`'s deterministic renderer, using the
port order read back from the committed DUT header, and requires an exact
match; it needs no klt, ngspice or PDK
(`python3 sim/tb/ro-ring11-pex/build_dut.py --check-source`). The source pin
covers the **consumed circuit sections**, not the whole file: the
`ro_ring11`, `ro_nand2` and `ro_stage` subcircuits (comments and whitespace
ignored) and ring1's `xr1` sizing, which `RING1_PARAMS` must equal. Edits to
other cells, to ring2, or to comments do not invalidate the evidence; a
consumed device or sizing change with an unchanged DUT fails with a diff.
`publication.json` records that identity as `source_sha256` for new
publications (older ones are not retro-fitted). Regenerating the DUT without
re-running `klt pex` fails the existing DUT hash pin; only a fresh
`publish_item7_analog.py` run over the regenerated DUT restores freshness.
This does not change the `body_bias` disclosure below (#339 is separate).

**What `klt pex` requires (0.6.0), and what that allowed.** A layout, an
extraction deck, and one or more `klt sim` request files. Each request's
testbench body must carry exactly one `.include`, naming a schematic DUT;
`klt pex` runs the request as written, then again with only that line
re-pointed at the netlist it extracted, and reuses the testbench's `xdut`
line byte for byte on both sides. So the schematic DUT has to declare the
extraction's own port list, position for position. Three consequences
shaped the run:

- *Which cell.* Ring1 (`ro_ring11`). Its extraction promotes fifteen ports
  — the eleven ring nodes, flat-named `a|y` .. `a|y$10`, then `en`, `vddr`,
  `vss`, `vsubs` — and each ring node is identified from the extracted
  netlist's own device geometry (`sim/tb/ro-ring11-pex/build_dut.py`), so a
  schematic DUT with the same header can be generated from
  `design/ro_array_core.spice`. The rows (period, supply current, swing) are
  ones the existing routing-level work already measures, at DR-0006's
  27-point grid. `combiner_sampler` would need a clocked two-ring stimulus
  and a schematic exposing internal buffer/XOR nets as ports, and is not
  attempted; ring2 is not part of this citation either. (#418 builds that
  fixture as separate, uncited coverage, see "Combiner/sampler post-layout
  coverage" below; #423 does the same for ring2, see "Ring2 native
  comparison".)
- *One `.include`.* `design.ngspice`'s switch parameters cannot be a second
  include, and folding them into the DUT drops them from the extracted side;
  they are restated as a `.param` card in the testbench body
  (klayout-tools#2871).
- *What the envelope pins.* Only the layout. The testbench request, body and
  schematic DUT are not fingerprinted (klayout-tools#2875), so
  `evidence/post-layout/publication.json` pins them and `check.py`
  re-verifies them, along with the committed extracted netlist's hash
  against the envelope's `extraction.netlist_sha256` and its ring positions
  against the DUT header. The envelope also drops each side's `klt sim`
  environment, so the backend and batch job ids are not in the evidence
  (klayout-tools#2876).

**What it says.** 27 corners x 3 rows, all 81 rows measured on both sides.
Ring1's period is **+86 % to +93 %** longer extracted than schematic at every
corner, the same order as the routing-level re-run (§7 of
`sim/characterization-post-layout-extracted.md`); average supply current
magnitude is 3 % to 15 % lower; the swing on `ro` is 5–6 % lower. No row
has a `limits` block, so `pass` means "measured on both sides", not "met a
spec": none of the three is a ratified spec row.

**`body_bias`, verbatim from the cited envelope** (only the 23-entry
`unbiased_pmos_body_nets` list is abridged):

```json
"body_bias": {
  "status": "unbiased",
  "unbiased_device_count": 23,
  "unbiased_nets": ["\\$28", "\\$30", "\\$32", "\\$34", "\\$36", "\\$38", "\\$40", "\\$42", "\\$44", "\\$46", "\\$48"],
  "unbiased_pmos_body_nets": [ ... 23 entries, one per PMOS device ... ]
}
```

Every PMOS device in ring1 (23 of 23) has its body on one of eleven
anonymous n-well nets, one per stage, with no DC path to anything: the
layout draws no well ties (layout/README.md, "Both bulk terminals are
approximated"). The schematic side ties PMOS bulk to `vddr`. `klt`'s own
documentation calls a re-simulation of such a netlist physically wrong, not
merely imprecise, and neither `klt pex` nor `klt signoff` grades on it. So
this `met` says that a full two-sided comparison over the real ring1 layout
ran at all 27 corners; it does **not** say the extracted-side numbers are
what silicon with this layout would do. The committed `layout/pex/`
netlists behind the Markdown records have the same floating wells.
[#339](https://github.com/2AMLogic/gf180-trng/issues/339) tracks measuring
how much that matters.

Cold start: see `sim/tb/ro-ring11-pex/README.md`, then
`python3 signoff/publish_item7_analog.py && python3 signoff/check.py --write`.

## Combiner/sampler post-layout coverage

Additional coverage, **not** a citation (#418). The item 7 analog citation
above stays ring1's, with its `body_bias` disclosure and #412's open
question unchanged; any future replacement or aggregation of that citation
must keep both scopes and #412's findings explicit.

`sim/tb/combiner-sampler-pex/` drives the assembled
`layout/blocks/combiner_sampler/combiner_sampler.gds` — both ring-output
buffers, the XOR combiner and all four sampling flip-flops — with a
deterministic two-input, clock and reset schedule, and compares schematic
against extracted through `klt pex` at DR-0006's 27-point grid. 62 rows hold
each flip-flop output and `xo`/`ro1`/`ro2` to the block's reset, capture and
`raw_valid` contract (90 %/10 % of supply); four more measure clock/reset-to-Q
without limits. The schematic DUT's ports are resolved from the extraction by
connectivity, and ambiguous or contradicting mappings are refused. Because
`klt pex` grades only the extracted side's limits (klayout-tools#2989),
`check.combiner_sampler_verdict()` holds both sides to them. It counts a
missing corner or a missing value as `unmeasured`, never `pass`. The testbench
README has the scenarios, settling windows and exclusions.

When the run is published, `publish_combiner_sampler_pex.py` writes the
native envelope byte for byte to `evidence/post-layout/combiner_sampler/`,
with a `publication.json`. That file pins the request, testbench, DUT, source
identity, port map, PDK/deck provenance and `body_bias`, and records the
verdict. `check.py` re-verifies all of it on every run (step 1d) and
recomputes the verdict, so neither can go stale or be hand-edited. A `fail`
verdict is published and kept as evidence.

**Status (2026-10-09): fixture built, grid not yet run.** Two submissions
of the 27-corner grid to the batch backend both failed with the fleet's
capacity refusal ("no capacity in any of the 30 pools after 3 attempt(s)").
The first failed on the extracted side after the schematic side had
finished; the second failed on the schematic side. `klt pex` aborts on such
a failure and discards the side that completed (klayout-tools#2990). The
grid was deliberately not re-run on the local backend. Nothing is published,
so step 1d currently has nothing to check. A single-corner debug probe
(tt / 3.30 V / 27 °C, local backend) measured all 66 rows on both sides
within limits, and extracted clock-to-Q was about 4x the schematic value.
That probe is a debug observation, not a PVT record.

**Attempt log (2026-10-10).** With the pinned producer
(`klayout-tools==0.6.0`, `klayout==0.30.10`), the offline checks and
`build_dut.py --check` passed. Two further `publish_combiner_sampler_pex.py
--backend batch` submissions both failed on the schematic side with
`batch-fleet-provision.sh launch failed (exit 1): error: no capacity in any of
the 30 pools after 3 attempt(s)`. `klt pex` reported
`nothing published`, so no evidence was written and the grid was again not run
locally. This remains unrun; see klayout-tools#2989 and #2990.

## Why each item reads the way it does

The grader's verdict is in `records/t1-tier-report.json`. This section is the
part the grader structurally cannot check — what was cited, what was
deliberately *not* cited, and the disclosures `design-evidence-tiers.md`
requires of the claimant rather than of the tool.

| # | analog | digital | Reading |
|---|---|---|---|
| 1 Design sources | `unmet` / `no_evidence` | `unmet` / `no_evidence` | Both partitions' artifacts exist and are guarded: `design/xschem/*.sch` → `design/netlist.py --check`, and `design/trng_top/*.v` → `design/synth.py --check` plus `design/interface/regmap.py --check`. None of those guards emits a `klt` envelope. Uncited on purpose — see "Items 1, 2, 9 and 10" below. |
| 2 Layout | `unmet` / `no_evidence` | `unmet` / `no_evidence` | Both layouts exist and are committed (`layout/cells/`, `layout/rings/`, `layout/blocks/`, `layout/digital/trng_top.gds`, composed into `layout/floorplan/`). Same reason: uncited on purpose, not absent. |
| 3 DRC clean | **`met`** | **`met`** | Analog cites `layout/reports/combiner_sampler.drc.json`, digital cites `layout/digital/reports/drc.json` — both `status: clean`, both against deck `gf180mcu` identified by content hash, both pinned and `input_verified: true`. The two partitions' decks are the same deck; their *coverage* is not, because the streams differ. Both enumerated below. |
| 4 LVS clean | **`met`** | **`met`** | Analog cites `layout/reports/combiner_sampler.lvs.json` (`status: match`, `mismatch_count: 3`, warnings only — `device.body_unverified` ×2, one per MOS class, and `topology` ×1); digital cites `layout/digital/reports/lvs.json` (`status: match`, `mismatch_count: 0`). Both citations carry a `content_hash` pin and read `input_verified: true` (analog since [#281](https://github.com/2AMLogic/gf180-trng/issues/281)). Neither compare verifies power connectivity or body ties: `power_connectivity.status` is `"unchecked"` on both, and `body_verification.status` is `"unverified"` (analog: all 104 MOS bodies untapped) and `"unchecked"` (digital). See "Item 4 is `met` twice, and both are pinned" for the verbatim blocks and what each compare did *not* verify. |
| 5 Corner verification | `unmet` / `no_evidence` | `unmet` / `no_evidence` | This block's largest *real* gap, and an evidence-format gap on top of it — but the two partitions' format gaps are not the same kind. README's ratified spec table still misses four rows (raw rate, raw min-entropy, area, power). The digital half accepts a `klt sta`/`klt functional-verification`/`klt sim` envelope and remains genuinely producible: the fifteen-corner digital STA sweep is recorded as Markdown rather than emitted in that form, and [#322](https://github.com/2AMLogic/gf180-trng/issues/322) found why that is not simply unperformed work: `klt sta` can time the committed DEF at the five liberty corners, but not as the same analysis the sweep records (see "Item 5 digital: what a `klt sta` envelope is, and is not" below), so no `5.digital` citation is made. The analog half is different in kind — `klt sim` emits `measurements[].spice` outside its own `.control` block and supports no caller-supplied one (klayout-tools#2533, filed from this repo's own friction protocol), so a spec whose rows need caller-side post-processing, as this block's ~950 corner records under `sim/records/` do, cannot cite a `klt sim` envelope at any released or unreleased build. Nothing here is gradeable yet, but only the digital half is a backlog item; the analog half is a closed door until #2533 resolves. |
| 6 Monte Carlo | `unmet` / `no_evidence` | `unmet` / `no_evidence` | `sim/characterization-worst-corner-and-mc-mismatch.md` is a real Monte Carlo campaign with recorded seeds, sample counts, two PVT points and a deterministic negative control. Item 6 accepts only a `klt yield` report, and none exists — nor is one reachable from any published klayout-tools release: `klt yield` requires the `klt_yield_native` Rust extension, which neither `pip install klayout-tools`/`uv tool install klayout-tools` nor the git-pinned form ships as a prebuilt wheel for (klayout-tools#2474's own item-6 text), so producing one needs a repo checkout with a Rust toolchain rather than the one-`pip install` reproduction the checklist is designed around. Still open upstream as klayout-tools#2531, after #2466 and #1061 closed without a wheel. Separately, klayout-tools#2480 makes the campaign's own `sample_size.verdict` and negative-control result (`undersized_sample` / `negative_control_not_detected`) grading inputs, so a `klt yield` report over this campaign is not automatically a `met` verdict even once one can be produced. |
| 7 Post-layout | **`met`** | **`met`** | **Analog** cites the native `klt pex` response over ring1's layout (`evidence/post-layout/ro_ring11.pex.json`), published by `publish_item7_analog.py` from `sim/tb/ro-ring11-pex/` (#326): 27 corners, 81 delta rows, every row measured on both sides, `input_verified: true`. Its `body_bias.status` is `"unbiased"` (23 of 23 PMOS bodies on floating wells), which the grader reports and does not grade — see "Item 7 analog" below; it covers ring1 only. **Digital** cites the native `klt functional-verification` response of the SDF-annotated post-route gate run (`evidence/post-route/gate_klt_response.json`), published by `publish_item7.py` from `sim/tb/trng-top-post-route/` (#314) — see "Item 7 digital" below; the claim is functional equivalence under cell delay at one corner, not timing signoff. The wider post-layout work (`sim/characterization-post-layout-extracted.md`, issues #17/#217/#232: the whole array, device-, routing- and inter-region-level) stays in this repo's Markdown records; `layout/pex/build.py` composes its own netlists and emits no `klt pex` report, and is unchanged. |
| 8 Characterization | **`met`** | **`met`** | Digital cites `evidence/characterization-digital.generic.json`, wrapping `sim/characterization-digital-sta-area-power.md`. Analog cites `evidence/characterization-analog.generic.json`, wrapping `sim/characterization-analog-summary.md` (#313). Both mean that a current aggregate exists. Neither means the rows in it pass. See below. |
| 9 Testbenches shipped | `unmet` / `no_evidence` | `unmet` / `no_evidence` | 64+ testbenches under `sim/tb/`, each with a documented cold-start invocation, and the PDK revision pinned in README and `pdk-nightly.yml`. Uncited on purpose. |
| 10 Repo hygiene | `unmet` / `no_evidence` | `unmet` / `no_evidence` | README, spec table, reproduction instructions, Apache-2.0 licence and green CI all exist. Uncited on purpose. |
| 11 Power delivery | `unmet` / `wrong_kind` | `unmet` / `wrong_kind` | `layout/digital/erc-supply-spec.json` and `layout/digital/reports/erc-supply.json` exist ([#268](https://github.com/2AMLogic/gf180-trng/issues/268)) and, as of [#276](https://github.com/2AMLogic/gf180-trng/issues/276), the spec's `ties[]` is declared and `erc.missing_tie` is computed and zero — see "Item 11's `ties[]`" below. `signoff/block-manifest.json` cites `11.digital` (the `erc-supply.json` report alone, pinned to the GDS it ran on) as of [#321](https://github.com/2AMLogic/gf180-trng/issues/321); no `11.analog` is cited. The digital column therefore reads `unmet` / `wrong_kind`, not `no_evidence`: item 11 is a compound claim, and the grader wants an `erc` envelope *and* an `lvs` one (and, for an RTL-flow block, a `place-and-route` one) in the same list, so a lone ERC citation is the wrong set rather than a missing one. As of [#327](https://github.com/2AMLogic/gf180-trng/issues/327) the analog column cites `11.analog` the same way (three `klt erc` reports under `layout/analog/reports/`, one per region cell, each pinned to its GDS) and reads `unmet` / `wrong_kind` for the same reason; that is the grader's real verdict, not progress toward `met`. The analog supply specs declare no `ties[]` and carry a `ties_disclosure` of kind `unexpressible` — see "Item 11's `ties[]`" below. Independent of the citation shape, the digital column's own extra requirement, `power_connectivity.status: "match"`, remains `"unchecked"` (see "Item 4 is `met` twice" above) — see "Item 11's `ties[]`" below. The item has a row here rather than being silently absent because it was added to the checklist on 2026-09-17 (klayout-tools#2025) and invalidated every hand-read that predates it. |

### Item 3 is `met` on both partitions — and here are each one's coverage gaps

`design-evidence-tiers.md` requires item 3's deck coverage gaps to be
enumerated *in the claim*, and is explicit that this is claimant-enforced:
`klt signoff` grades item 3 on `status: "clean"` alone, so a `met` verdict is
**not** evidence that the gaps were disclosed. Since klayout-tools#2002 the
grader *reports* them on the citation, so everything below is quoted from
`records/t1-tier-report.json`'s own `items[].citation.coverage` — **each
partition from its own citation**, because the two runs skipped different
rules and left different layers uncovered. They are not interchangeable, and
the digital column is not the analog column restated.

**Both partitions run the same deck**, and it transcribes the same ten
chapters of the gf180mcu DRM either way
(`coverage.deck_scope`, identical on both citations): 7.4 Nwell, 7.5 Comp,
7.7 Poly2, 7.12 Contact, 7.13 Metaln, 7.14 Vian, 7.15 MetalTop, 9.1 Bond Pad,
10.4.2 MIM Option B, 10.7 DRC_BJT Mark Layer. "DRC clean" on either partition
means clean *inside that scope*. Nothing here is a claim about MIM
capacitors, bond pads, or any rule class the deck does not carry.

**Analog** — `layout/reports/combiner_sampler.drc.json`:

- `coverage.layers_in_stream_without_rules` (2): `34/10`, `36/10` — layers
  drawn in this stream that the deck has no rule for.
- `coverage.rules_skipped` (21): `bjt.separation.comp.1`, `comp.space.mv.1`,
  `comp.width.mv.1`, `metal3.enclosing.via3.1`, `metal4.enclosing.via3.1`,
  `metal4.enclosing.via4.1`, `metal4.space.1`, `metal4.width.1`,
  `metal5.enclosing.via4.1`, `metal5.space.1`, `metal5.width.1`,
  `metaltop.space.1`, `metaltop.width.1`, `mim.enclosing.fusetop.1`,
  `mim.enclosing.via4.1`, `mim.space.1`, `pad.enclosing.metal5.1`,
  `via3.space.1`, `via3.width.1`, `via4.space.1`, `via4.width.1`.

The count was 19 before
[#281](https://github.com/2AMLogic/gf180-trng/issues/281) re-produced this
envelope under klt 0.6.0. The two additions, `metal4.space.1` and
`metal4.width.1`, are not coverage this run lost: they did not exist in the
older build's deck at all, and this stream draws no Metal4, so the newer deck
lists them as skipped (`"no_applicable_geometry"`). Every rule the older run
checked, this one checks too, and the layers checked are the same.

**Digital** — `layout/digital/reports/drc.json`:

- `coverage.layers_in_stream_without_rules` (11): `0/0`, `21/10`, `31/0`,
  `32/0`, `34/10`, `46/10`, `63/63`, `81/10`, `112/1`, `204/0`, `204/10` —
  more than the analog side, and that is expected rather than alarming: this
  stream is a DEF→GDS merge of a standard-cell library, so it carries the
  library's own label, boundary and annotation layers (`63/63`, `81/10`,
  `204/*`) that a hand-drawn analog cell simply does not draw. None of them
  is a *geometry* layer the deck declines to check.
- `coverage.rules_skipped` (7): `bjt.separation.comp.1`, `metaltop.space.1`,
  `metaltop.width.1`, `mim.enclosing.fusetop.1`, `mim.enclosing.via4.1`,
  `mim.space.1`, `pad.enclosing.metal5.1`.

The digital run skips **fewer** rules than the analog one (7 against 21), and
the difference is informative in the same direction both ways: a deck rule is
"skipped" when the stream draws none of the layers it needs, so the fourteen
rules the analog run skipped and the digital one did not — `comp.space.mv.1`,
`comp.width.mv.1`, `metal3.enclosing.via3.1`, `metal4.enclosing.via3.1`,
`metal4.enclosing.via4.1`, `metal4.space.1`, `metal4.width.1`,
`metal5.enclosing.via4.1`, `metal5.space.1`, `metal5.width.1`,
`via3.space.1`, `via3.width.1`, `via4.space.1`, `via4.width.1` — are rules
that were *checked* on the digital stream
(39 rules checked in all), because the routed PDN and signal routing actually
reach those layers. The seven both runs skip are the BJT-separation, MIM
capacitor, MetalTop and bond-pad rules, skipped on both because neither
stream contains a BJT, a MIM capacitor, a MetalTop shape or a pad. Every
digital-skipped rule is also analog-skipped; there is no rule the analog
partition checked and the digital one did not.

**Both citations' coverage blocks now have the same shape**, because both
were produced by klt 0.6.0 (see "Which `klt` produced what" below). Alongside
the two lists above each carries `coverage.skipped: []`,
`coverage.unknown: []`, `coverage.nothing_checked: false`, and a
`coverage.inapplicable` array that gives every skipped rule a
machine-readable reason (`"no_applicable_geometry"` for all 21 analog and all
7 digital) rather than leaving a reader to infer it. Until #281 only the
digital citation had these fields. The analog envelope also lists the 25
rules it did check (`coverage.checked`).

**One citation per partition, nine more clean analog reports.** `klt signoff`
takes one evidence entry per item per partition, so the manifest cites the
most complex analog cell and the digital top cell. Every other analog DRC
report committed here also reads `status: clean` with `violation_count: 0`:
`ro_buf`, `ro_nand2`, `ro_nand2_ring2`, `ro_ring11`, `ro_ring11_ring2`,
`ro_stage`, `ro_stage_ring2`, `sampler_dff`, `xor2`
(`layout/reports/*.drc.json`), plus the composed whole-block run in
`layout/floorplan/reports/floorplan.drc.json`. The deliberately-failing
fixtures `trng_tc_inv_drcbad`/`trng_tc_inv_lvsbad` are negative controls for
the flow, not evidence about the design.

### Which `klt` produced what

Three separate klayout-tools builds appear in this block's evidence, and
conflating them would make the table above unreadable. They are separate on
purpose:

| Role | Build | Where it is pinned |
|---|---|---|
| **Grader** — parses the T1 checklist and renders the verdict | `0.6.0` (released) | `signoff/check.py`'s `KLT_PIN`; CI's `signoff` job |
| **Producer, analog** — `layout/reports/*` | `0.6.0` (released; tag `v0.6.0`, commit `c622e8addb36`), with `klayout==0.30.10` | `.github/workflows/pdk-nightly.yml`, per [DR-0026](../spec/decision-records/DR-0026-normative-klt-build-for-floorplan-reports.md) as amended; `layout/reports/environment.json`'s `klt_origin` |
| **Producer, digital** — `layout/digital/reports/*` | `0.6.0` for DRC/LVS; `0.5.0+g32f69f811682` for the place-and-route that built the stream | recorded in each envelope's own `provenance.klt_version` |

The grader pin is deliberately independent of any producer pin — it grades
committed JSON and needs no PDK, so a third party reproduces the verdict with
one `pip install`. That the grader and the analog producer both read `0.6.0`
today is a coincidence of timing, not a coupling. The digital partition's DRC
and LVS were re-emitted under `0.6.0` by #273; the analog partition's
`layout/reports/` followed in
[#281](https://github.com/2AMLogic/gf180-trng/issues/281), once DR-0026
settled which build is normative. That was not a mechanical regeneration —
DR-0026's original "no verdict moved" measurement had gone stale at 0.6.0 —
so DR-0026 records the re-measurement: across all 13 `layout/verify.py`
fixtures, no DRC verdict, rule count, device or net count, extracted
netlist, or LVS status moved; `device.body_unverified` went from 1 to 2 per
LVS fixture (the PMOS half of an already-documented limitation, disclosed
again — see "What each compare did and did not verify" below); and the
newer deck lists two more skipped Metal4 rules. The DRC verdict is likewise
measured not to move on the digital side: #273's re-run under 0.6.0
reproduced `reports/place_and_route.json`'s existing nested `drc` digest
byte for byte.

**The grader pin has its own drift, measured the same way DR-0026 and #281
measure the producer pins'.** `v0.6.0..main` is 102 commits, of which 9 touch
`docs/design-evidence-tiers.md` — the document `klt signoff` parses the item
list from — moving both `build.grading_ruleset_id`
(`sha256:0d8cc27c…` → `sha256:88fdfb17…`) and `source_doc_content_hash`
(`sha256:63eeec72…` → `sha256:584c0c75…`) in the rendered report.
`signoff/check.py` compares a fresh grade *under the pinned build* against
the committed record, so it structurally cannot notice this drift on its
own: re-grading this block under upstream `main`
(`0.6.0+gd18467ec57b1`) reproduces `tier: null` and 5 of 22 with
byte-identical per-item statuses, so no graded row here is wrong — but the
yardstick behind the row text has moved further than a version string
discloses. Tracked upstream as klayout-tools#2526 ("a pinned klayout-tools
version does not pin the grading ruleset, so a committed verdict-of-record
cannot be re-verified").

### Item 4 is `met` twice, and both are pinned

The two partitions reach `met` from genuinely different evidence, so their
disclosures do not merge.

**Analog is pinned.** `4.analog` cites
`layout/reports/combiner_sampler.lvs.json` with
`content_hash: sha256:d66c91dc…`, matching the envelope's own
`provenance.input.content_hash` (`"role": "layout"`) and
`environment.layout_sha256`, all three naming
`layout/blocks/combiner_sampler/combiner_sampler.gds` — so `klt signoff`'s
own staleness gate reaches this row (`citation.input_verified: true`), and
`check.py` re-hashes the stream independently as well. Until
[#281](https://github.com/2AMLogic/gf180-trng/issues/281) this was the one
unpinned citation in the manifest: the envelope had been produced by klt
`0.4.0+g3fbb4478e301`, which predates klayout-tools#1969 and left
`provenance.input` `null`, so pinning a hash against it would have rendered
the item a false `stale_evidence`, and the grader reported
`citation.input_verified: null`. Re-producing the envelope under the 0.6.0
release (DR-0026, as amended) populated the field; the verdict did not move
(`status: match`, `error_count: 0`).

**Digital is pinned.** `4.digital` cites
`layout/digital/reports/lvs.json` with
`content_hash: sha256:d661d025…`, matching the envelope's own
`provenance.input.content_hash` and `environment.layout_sha256`, all three
naming `layout/digital/trng_top.extracted.spice` — so `klt signoff`'s own
staleness gate reaches this row (`citation.input_verified: true`) rather than
this repo standing in for it.

**The edge above these reports is guarded by this repo, not by `klt
signoff`.** The DRC, LVS and ERC envelopes each pin their own input (the GDS
or the extracted netlist). None of them pins the synthesized netlist the
layout was placed and routed from. That edge is recorded in one place only,
`layout/digital/reports/place_and_route.json`'s
`provenance.input.content_hash`, and nothing compared it with
`design/trng_top/trng_top.synth.v` until
[#293](https://github.com/2AMLogic/gf180-trng/issues/293). PR #292
re-synthesized that netlist without rebuilding the layout, and its summary
said no committed report recorded a hash of `trng_top.synth.v`. That was
wrong: `place_and_route.json` did. #293 re-ran the digital chain on the
current netlist. It also added a standing guard,
`python3 layout/digital/build.py --check-input`, which runs in
`npm run check:ci` and in the PR-blocking CI workflow. It is stdlib-only and
fails when the two hashes disagree. The rows these envelopes grade did not
change verdict: DRC clean, LVS match, ERC clean.

**What each compare did and did not verify.**

- *Analog*: `status: "match"`, `mismatch_count: 3`, `error_count: 0` —
  `category_counts: {"device.body_unverified": 2, "topology": 1}`, the same
  warnings-only shape every other analog region's compare carries. Both
  blocks that were `null` under klt 0.4.0 are now populated, and **neither is
  `"verified"`/`"match"`**:
  - `power_connectivity`, verbatim: `{"status": "unchecked", "reason":
    "reference.form is 'plain-element', whose reference netlist carries its
    own power/ground pins and nets -- they take part in the ordinary compare,
    so this check (which exists to cover the signal-only 'gate-level-verilog'
    form) does not apply", "power_pins": [], "power_pins_derivation": null,
    "instance_count": 0, "expected_nets": null, "unchecked_expected_pins":
    [], "findings": [], "finding_count": 0}`. As on the digital side, the
    supply nets *are* inside the ordinary compare, which matched — the
    envelope's `net_correspondence` pairs layout `d|vdd`, `vss` and `vsubs`
    with reference `VDD`, `VSS` and `VSUBS` — but not via this field.
    **`"unchecked"` is not a power-delivery verdict, and this re-run does not
    advance T1 item 11.** Item 11's Analog column does not ask for
    `power_connectivity` at all: it asks for `klt erc` supply evidence plus
    exactly that `net_correspondence` pairing. `11.analog` is cited as of #327
    (supply-ERC only, see "Item 11's `ties[]`" below), and the row still
    reads `unmet` / `wrong_kind`.
    The Digital column does ask for `power_connectivity.status: "match"`,
    and there `"unchecked"` explicitly does not satisfy it.
  - `body_verification`, verbatim: `{"status": "unverified", "reason": null,
    "device_classes": ["nfet", "pfet"], "device_count": 104, "findings":
    [{"class": "nfet", "device_count": 52}, {"class": "pfet",
    "device_count": 52}], "finding_count": 2}`. All 104 devices in the
    block — every NMOS and every PMOS — have a body terminal that reached no
    real net: NMOS bodies land on the deck-synthesized `vsubs`, PMOS bodies
    on an anonymous KLayout-synthesized well net, because the hand-drawn
    cells draw no substrate or well taps (`layout/README.md`, "Bulk terminals
    are approximated"). This is a *disclosure*, not a new defect: the same
    104 bodies were equally unverified under klt 0.4.0, which disclosed only
    the 52 NMOS. The PMOS half had been silenced by klayout-tools#1113's
    deck-level gate and is reported again per device since
    klayout-tools#2048 — that is the whole of the
    `device.body_unverified` 1 → 2 change.
- *Digital*: `mismatch_count: 0`, `error_count: 0`, `category_counts: {}` —
  no warnings at all. But `power_connectivity.status` is `"unchecked"` and so
  is `body_verification.status`, each with `klt`'s own stated reason in the
  envelope, and **neither is `"verified"`/`"match"`**:
  - `power_connectivity` is `unchecked` because this compare's
    `reference.form` is `plain-element` — the reference netlist declares its
    own `vddd`/`vss` pins and nets, so they take part in the ordinary compare
    and the separate power check (which exists to cover the signal-only
    `gate-level-verilog` form) does not apply. The PDN *is* inside this
    compare, in other words, but not via the field a reader might look at
    first. **T1 item 11's Digital column requires `power_connectivity.status:
    "match"` specifically, and `"unchecked"` does not satisfy it** — this row
    does not advance item 11, which remains `unmet` (see "Item 11's `ties[]`"
    above for the current state and #124 for the general tracker).
  - `body_verification` is `unchecked` because the request uses the
    pre-extracted `layout.netlist` form with no `layout.deck`, so nothing
    establishes this layout's substrate/well-tap convention. The envelope
    says it outright: "this run verified nothing about the device bodies
    either way". That is honest rather than alarming here — the digital
    compare is deliberately cell-instance-granularity (see
    `layout/digital/lvs.py`'s docstring), with every standard cell an opaque
    black box, so it extracts zero devices (`counts.devices: 0/0/0`) and has
    no device bodies of its own to verify. Each cell's internal transistor
    layout is the library's bring-up, not this block's.

**The digital reference is a mechanical transcription, not a schematic.**
The largest caveat on the digital `match` is not in the `klt` envelope at all,
which is why `layout/digital/lvs.py` records it in the report under
`reference_generation`: the reference netlist is generated from
`trng_top.pnr.v` (the as-built, post-CTS gate-level netlist OpenROAD wrote)
by this repo's own transcriber, not captured independently. So this compare
answers "does the routed layout's cell-to-cell connectivity match what P&R
actually built?" — a real and necessary question — and not "does the layout
match an independently-authored golden netlist?".

### Item 8 is `met` on both partitions, and neither means the rows pass

**Digital.** `sim/characterization-digital-sta-area-power.md` is the one aggregated,
current artifact item 8 asks a digital partition for: Fmax, placed area and
power across all fifteen corners, each number naming the `sim/records/`
evidence record it rests on, with §0/§0a/§0b carrying the `FIFO_DEPTH = 2`
re-measurement (issues #255, #264 and #293) that supersedes the depth-8 sections
retained below them as append-only history.

Item 8 asks for that aggregation artifact to exist and be current. It does
**not** ask for every row in it to pass, and this `met` verdict must not be
read as if it did. The disclosed exceptions, which travel with the claim
rather than being omitted from it: placed cell area is 62 081.5 µm², ×1.845
of the depth-2 pre-synthesis inventory and still over the ratified
`< 0.05 mm²` row on digital cells alone; and measured power remains well
above the library-based estimate at the same corner and rate. Both are item
5's subject matter, and item 5 is `unmet` above. (A third exception this
paragraph used to carry is closed: #255's first depth-2 build regressed the
library `max_transition` check to 11 of 15 corners, and
[#264](https://github.com/2AMLogic/gf180-trng/issues/264) re-tuned the
place-and-route constraint and rebuilt. The current DEF violates at 0 of 15.)

**Analog** ([#313](https://github.com/2AMLogic/gf180-trng/issues/313)).
`sim/characterization-analog-summary.md` is the analog partition's
aggregate. It is organized by the ratified spec rows, not by the fourteen
per-topic documents under `sim/` it draws on. For each applicable row it
gives the analog-partition result, its corner or scope, the `sim/records/`
evidence and `sim/tools/` derivation behind it, an evidence class
(measured, measured-extracted, derived, target arithmetic, estimate or
unmeasured) and its claim limit. It also states the partition boundary and
the post-layout extraction scope. `8.analog` cites
`evidence/characterization-analog.generic.json`, which pins that document's
sha256 in `provenance.input.content_hash`. The manifest pins the same
digest. Editing the summary without re-pinning both fails `check.py` step 1.
Re-pinning only one of the two fails step 2.

The pin proves the document has not changed since it was cited. It does not
prove the document still agrees with the evidence. That second guard is
`sim/tests/test_analog_characterization_summary.py` (`npm run test`), which
re-runs `power_rollup.py`, `time_to_first_valid.py` and
`worst_corner_entropy.py` and fails if any figure the summary quotes is no
longer what those tools print.

The same reading applies as on the digital side: **`met` means the
aggregate exists and is current, not that its rows pass.** Exactly one
analog-facing row is met (time-to-first-valid, 1.281 ms). The disclosed
exceptions travel with the claim. The DR-0007 sizing law holds at the
entropy-binding corner only up to 678–9412 bps, against the ratified 1 Mbps
raw rate. Raw min-entropy is unmeasured and cannot be measured by
transistor-level simulation at the rates under consideration, so the Tier 2
quality estimate is not delivered. The analog power and area terms fit
inside their rows, but the whole-block power and area rows are missed. All
of it is simulation, none of it is silicon, and none of it is an SP 800-90B
assessment. The README is still not cited: wrapping it would pin the
manifest to a file that changes for unrelated reasons several times a week,
which is why a dedicated document was written instead. Items 5, 6 and 7
stay `unmet` on the analog partition. The aggregate does not make any of
them gradeable.

Seven met rows out of 22 are not a claim about this block's performance.

Item 8 is also the only T1 item a `generic` envelope may satisfy. Every other
item rejects `"kind": "generic"` outright, so this hand-rolled wrapper cannot
be pointed at items 3–7 to make their rows go green.

### Item 11's `ties[]` is now declared and computed, and the item is still unmet

`layout/digital/erc-supply-spec.json` previously declared no `ties[]` at
all: klayout-tools#2169 made a declared tie collapse this routed
standard-cell design into one electrical island and report a false
`erc.supply_short`, so the spec omitted `ties[]` and carried a top-level
`ties_disclosure` (`kind: "tool_limitation"`) instead, standing in on
place-and-route's `power.tapcell_master` evidence and a matching LVS run.
klayout-tools#2186 (merged 2026-09-20, shipped in 0.6.0) scopes a tie's
well conduction to its own tap sites instead of registering the whole well
region as one blanket conductor, closing that gap. [#276](https://github.com/2AMLogic/gf180-trng/issues/276)
re-ran the spec on that build and declared two ties, one per well this GDS
draws:

- `nwell_tap` — `well_layer` 21/0 (Nwell), `tap_layer` 22/0 (Comp) narrowed
  by `tap_requires` 32/0 (Nplus): the `Comp ∩ Nplus` N+ well-strap boolean,
  connected to `Metal1`'s `VDD` rail.
- `pwell_tap` — `well_layer` 204/0 (LVPWELL, the PDK's own name for the
  P-type body-region marker this library draws per row), `tap_layer` 22/0
  narrowed by `tap_requires` 31/0 (Pplus): the mirror-image `Comp ∩ Pplus`
  boolean, connected to `Metal1`'s `VSS` rail.

The re-run (`layout/digital/reports/erc-supply.json`, `provenance.klt_version:
"0.6.0"`) reports both ties in `erc_coverage.checked` (not
`erc_coverage.skipped`, so neither is degenerate), `erc.missing_tie`
computed and zero, `erc_status: "clean"`, and `erc_findings: []` — the same
zero `erc.unconnected_net`/`erc.supply_short` on `VDD`/`VSS` the spec
already required. `ties_disclosure` is now `null`: the tie is declared, not
disclosed as omitted.

**This does not move item 11 to `met`.** As of
[#321](https://github.com/2AMLogic/gf180-trng/issues/321),
`signoff/block-manifest.json` cites `11.digital` as a single evidence
object: `layout/digital/reports/erc-supply.json`, pinned to the
`provenance.input.content_hash` of the GDS it ran on (the same
`sha256:b164476c...` the digital DRC citation pins). Under klt 0.6.0 the
grader's reading of the digital column moved from `unmet` / `no_evidence` to
`unmet` / `wrong_kind`. That is not progress toward `met`: it only says the
item is now cited, and cited with the wrong shape. Item 11's manifest entry
is a compound *list*; the grader needs an `erc`, an `lvs`, and (for an
RTL-flow block) a `place-and-route` part, and finding only the `erc` part it
reports `wrong_kind` without grading the ERC report's contents at all. So
the zero `erc.missing_tie` and clean supply nets above are not yet a graded
result.

Three things remain, none touched by this change:

- The compound list itself. A trial list of the ERC, LVS and
  place-and-route reports graded `unmet` / `lvs_supply_unproven`, i.e. it
  reaches the same `power_connectivity` gap below. It was not committed:
  `layout/digital/reports/place_and_route.json` names no input artifact, so
  `signoff/check.py`'s freshness step rejects it, and that report embeds an
  absolute worktree path. Citing it needs a check.py decision first.
- `11.analog` is cited as of [#327](https://github.com/2AMLogic/gf180-trng/issues/327)
  and reads `unmet` / `wrong_kind`, exactly like the digital column, for the
  same compound-claim reason (an `erc` part without an `lvs` part in the
  same list). The runs: `layout/analog/erc-supply-spec-rings.json` on
  `ro_ring11` (ring1) and `ro_ring11_ring2` (ring2), and
  `layout/analog/erc-supply-spec-combiner_sampler.json` on
  `combiner_sampler`; reports in `layout/analog/reports/`, each pinned to
  the `provenance.input.content_hash` of its GDS. All three read
  `erc_status: clean`, zero findings, one island per declared supply
  (`vddr`/`vss` on the rings, `vdd`/`vss` on combiner_sampler). What that
  does **not** cover: the specs declare no `ties[]` (these streams draw no
  Nplus/Pplus/LVPWELL, and the reference netlists give every PMOS a floating
  well), so `erc.missing_tie` is not computed and `ties_disclosure.kind` is
  `unexpressible`; `vsubs` is not declared because no label of that name
  exists in any of the three streams (the guard ring lives only in the
  floorplan abstract, which also contains the digital region); the supply
  names are the cell-level `vddr`, not the region-level `vddr1`/`vddr2`; and
  the LVS `power_connectivity` (`"unchecked"`) and `body_verification`
  (`"unverified"`) fields remain exactly as disclosed above. These three
  reports cover only the rings' and combiner's own GDS. The composed floorplan
  stream has its own whole-block run, `layout/floorplan/reports/erc-supply.json`
  (issue #447; five region-level supplies, Metal1-Metal5, clean), which is
  not cited by any manifest item here and changes no tier.
- The digital column's additional requirement, `power_connectivity.status:
  "match"` on item 4's LVS citation, stays `"unchecked"`, for the reason
  "Item 4 is `met` twice" above already documents. A `met` supply-spec run
  is necessary for item 11's digital column; it was never sufficient.

### Items 1, 2, 9 and 10 are uncited on purpose

`design-evidence-tiers.md` says plainly that these four have no tool behind
them. `klt signoff` therefore grades them on "some passing envelope was cited
at all", not on whether the cited evidence is topically relevant — it cannot
check that, and it does not try. Citing a clean DRC report for item 10 ("a
README, a licence, CI") would produce a `met` row the tool has no basis to
object to and that would mean nothing to a reader.

All four are, in substance, satisfied by this repo. They are still left
`unmet`/`no_evidence`, because that is the accurate machine-readable
statement: *no check backs this claim*. `klt signoff`'s own documentation
names this as the safest default.

### Disclosures the claimant owes, not the grader

- **Item 3's DRC coverage** — quoted in full above, **per partition**, from
  each citation's own `coverage` block rather than from memory or from the
  other partition's list.
- **Item 7's `body_bias`** is *reported* by `klt signoff` and never graded: a
  `klt pex` citation whose `body_bias.status` is `"unbiased"` still renders
  `met`, and a re-simulation of an unbiased extracted netlist is physically
  wrong rather than merely imprecise. **Not applicable** to the digital
  citation (a `klt functional-verification` response, no extracted netlist).
  **The analog citation's reads `"unbiased"`**: `unbiased_device_count: 23`,
  eleven anonymous well nets, every PMOS body in ring1. Its `met` is a
  completed two-sided comparison on a netlist whose wells float, not a
  physically valid post-layout result. See "Item 7 analog".
- **Item 4's `power_connectivity` and `body_verification`** —
  `power_connectivity` is `"unchecked"` on both citations;
  `body_verification` is `"unverified"` on the analog one (104 of 104 MOS
  bodies) and `"unchecked"` on the digital one, each with `klt`'s own stated
  reason. Neither partition's LVS verdict includes a verified body-tie or a
  `"match"` power-connectivity result; both are disclosed above rather than
  folded into the word "match".

## Evidence this repo has but cannot cite

Recording these separately from the gaps above, because they are a different
problem with a different fix:

- ~~**The digital partition's DRC and LVS envelopes are not committed as
  envelopes.**~~ **Closed by
  [#273](https://github.com/2AMLogic/gf180-trng/issues/273).**
  `layout/digital/reports/drc.json` and `lvs.json` used to be reduced
  summaries (`status`, counts, deck name) with no `schema_version`, no
  `violations`/`mismatches` array and no `provenance` block, so `klt signoff`
  could not classify them at all — while the runs behind them had been clean
  and matching since #170/#187. Both are now committed as full envelopes by
  `layout/digital/build.py` and `layout/digital/lvs.py`, and items 3 and 4
  read `met` on the digital partition. Kept here as the worked example of
  this whole category: the fix was a serialization change, not verification
  work.
- **The composed whole-block DRC envelope is nested inside a larger report.**
  `layout/floorplan/reports/floorplan.drc.json` *is* a full `klt drc` envelope
  — under a `"drc"` key, wrapped alongside a
  `new_violations_from_composition` field. `klt signoff` cites whole files
  only, so the strongest single DRC artifact in this repo (the composed
  four-region stream, `status: clean`) is not citable as it stands. Filed
  upstream as a tool gap, per this repo's friction protocol:
  [klayout-tools#2342](https://github.com/2AMLogic/klayout-tools/issues/2342).

## Item 5 digital: what a `klt sta` envelope is, and is not

[#322](https://github.com/2AMLogic/gf180-trng/issues/322) asked whether the
fifteen-corner digital STA sweep (`sim/tb/digital-sta-power/run_sta.py`) can
be emitted as a graded `klt` envelope. Findings against the pinned klt 0.6.0
(DR-0026):

- **What the grader accepts.** Item 5's digital column accepts a `klt sta`
  envelope (also `klt functional-verification`, and `klt sim`). A `sta`
  citation passes when every corner in the envelope's own `corners[]` has
  `timing_status: "constrained"` and non-negative setup and hold slack. The
  graded corner set is whatever the cited request declared in `pdk.corners`.
  The grader does **not** read this block's spec rows: a `met` would say
  nothing about the area and power rows the digital section misses.
- **What `klt sta` can produce here.** One request over the committed
  `layout/digital/trng_top.def` (with `--pdk gf180mcuD`; without it klt
  resolves a different PDK variant and fails to parse the DEF) with the five
  liberty corners the library ships in the 3.3 V family returns
  `constrained` at all five, worst setup +33.5 ns (`ss_125C_3v00`) and worst
  hold +0.647 ns (`ff_n40C_3v60`). Run as a probe against a scratch manifest,
  that envelope graded item 5 digital `met`.
- **Why it is not cited.** That envelope is a different, weaker analysis than
  the sweep it would stand beside: an ideal clock (the sweep propagates the
  CTS-built clock; klayout-tools#2739), no routing parasitics (the sweep
  annotates OpenRCX SPEF at min/nom/max interconnect; klt has no verb that
  extracts a routed DEF's parasitics at a chosen corner, and `spef` is one
  path per request), no per-port `set_input_transition` for the six trunk
  ports, and 5 liberty corners rather than the 15 (liberty x interconnect)
  points. Citing it would flip item 5 digital to `met` on an analysis the
  Markdown records do not describe, while the ratified area and power rows
  remain missed. This repo does not do that. The gaps are filed generically at
  klayout-tools#2858 (and #2739).
- **Result.** No `5.digital` entry is added to `block-manifest.json`; item 5
  stays `unmet` / `no_evidence` on both partitions and the verdict of record
  is unchanged. When the upstream gaps close, the sweep's producer is the
  caller that should switch to `klt sta`.

## What would move the needle

In dependency order, not effort order:

1. ~~**Re-commit the digital partition's DRC and LVS as full `klt`
   envelopes.**~~ **Done** —
   [#273](https://github.com/2AMLogic/gf180-trng/issues/273) moved items 3
   and 4 from 2 of 4 to 4 of 4, and the verdict of record from 3 of 22 to 5
   of 22, with no new verification work: only a different serialization of
   runs that had already happened.
2. ~~**Re-run the analog LVS under a settled producer pin.**~~ **Done** —
   [#281](https://github.com/2AMLogic/gf180-trng/issues/281) settled the
   producer pin (DR-0026, amended to the 0.6.0 release), re-produced
   `layout/reports/` under it, and pinned `4.analog`'s citation. The met
   count did not move — item 4 was already `met` on both partitions — but
   every citation in the manifest is now pinned, and the analog compare's
   `power_connectivity`/`body_verification` are real verdicts
   (`"unchecked"`/`"unverified"`) instead of `null`. Neither is a pass, and
   neither advances item 11.
3. **Emit corner evidence as a `klt sta`/`klt functional-verification`
   envelope** for the digital half, alongside this repo's Markdown records.
   [#322](https://github.com/2AMLogic/gf180-trng/issues/322) investigated and
   stopped at a finding rather than citing a weaker analysis: see "Item 5
   digital: what a `klt sta` envelope is, and is not". Blocked on
   klayout-tools#2739 (propagated clock) and klayout-tools#2858 (routed-DEF
   parasitics at a chosen interconnect corner, interconnect-corner matrix,
   per-port input transition). Item 5's *design* gap (four ratified
   rows still missed) is real and separate. The analog half is not on this
   list as work this block can do today: `klt sim` is uncitable for a spec
   needing caller-side post-processing until klayout-tools#2533 resolves --
   see item 5's row above.
4. ~~**A `klt pex` report** over the post-layout extraction that already
   exists (item 7).~~ **Done for ring1 only** —
   [#326](https://github.com/2AMLogic/gf180-trng/issues/326) cites a native
   `klt pex` report as `7.analog` and moved the verdict of record from 7 to
   8 of 22. Its `body_bias.status` is `"unbiased"`, so the number that would
   actually move the needle is a re-run on a layout with drawn well ties
   (see "Item 7 analog"). Item 6's `klt yield` report does not appear here as
   something this block can produce: it requires the `klt_yield_native` Rust
   extension, which is not reachable from any published klayout-tools
   release (klayout-tools#2531, and #2474 for the upstream item-6 text) —
   closing it needs a wheel upstream, not additional work here. Once one
   exists, klayout-tools#2480's sample-size and negative-control grading
   inputs still apply to the resulting report.
5. ~~**A `klt erc` supply spec and run**~~ **Done, in two steps** — the spec
   and report first landed via [#268](https://github.com/2AMLogic/gf180-trng/issues/268),
   and [#276](https://github.com/2AMLogic/gf180-trng/issues/276) declared
   the spec's `ties[]` once klayout-tools#2186 shipped, so `erc.missing_tie`
   is now computed and zero. Item 11 still does not read `met`: `11.digital` is cited
   (#321) as a lone ERC report and `11.analog` (#327) as three, and both
   read `unmet` / `wrong_kind`, and the digital column's `power_connectivity.status: "match"`
   requirement stays `"unchecked"` — see "Item 11's `ties[]`" above.

Items 1, 2, 9 and 10 need nothing built — only an honest artifact to cite, if
one ever exists.

Items 1 and 2 are tracked here as part of this block's own evidence-format
gap; item 11's remaining gaps are tracked under
[#124](https://github.com/2AMLogic/gf180-trng/issues/124), this repo's
general gap-to-T1 tracker. Tool-side friction this surfaces is filed at
`2AMLogic/klayout-tools`, per this repo's friction protocol (`CLAUDE.md`) —
so far klayout-tools#2342, #2531 (item 6's `klt yield` unreachable from any
published release), #2533 (item 5's analog half uncitable at any release)
and #2526 (a pinned klayout-tools version does not pin the grading
ruleset).

## Ring2 native comparison

Additional coverage, **not** a citation (#423). Ring2 is a separately sized
oscillator (`xr2`, `wstv=0.240u`), so ring1's comparison says nothing about it.
`sim/tb/ro-ring11-ring2-pex/` holds the same paired schematic-versus-extracted
`klt pex` request over `layout/rings/ro_ring11_ring2/ro_ring11_ring2.gds` (same
27-point grid and three rows as ring1's; `check.py` enforces the equality), with a
DUT generated by `build_dut.py --ring ring2` from the `xr2` sizing and ring2's
own extracted port order. `publish_item7_analog.py --ring ring2` would publish it
to `evidence/post-layout/ring2/` with a recomputed, never-passing-when-incomplete
verdict; `check.py` checks the fixture and any such publication in step 1c',
independently of ring1, and fails if the manifest cites it.

**Currently unrun.** The batch fleet refused the 27-corner submission for
capacity, and the grid was not run locally, so no ring2 result is committed. The
README in that directory has the reproduction commands. Whatever it eventually
reports describes a layout with floating PMOS wells (#339/#411) and is a
diagnostic under that limitation: no entropy, full-chip timing or
silicon-performance claim.
