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

<!-- current-t1-status:begin -->**Today: `tier: null`, T1 18 of 22 items met.**<!-- current-t1-status:end --> A `mixed-signal` block is
graded twice over, once per partition, so the eleven-item checklist renders
22 rows. The eighteen met are item 1 (design sources), item 2 (layout), item 3
(DRC), item 4 (LVS), item 7 (post-layout verification), item 8
(characterization report), item 9 (testbenches shipped) and item 10 (repo
hygiene) on **both** partitions, plus item 11 (power delivery)
([#662](https://github.com/2AMLogic/gf180-trng/issues/662): see "Item 11's
`ties[]`" below) and item 5 (corner verification,
[#699](https://github.com/2AMLogic/gf180-trng/issues/699)) on the
**digital** partition only. Item 5 digital's `met` is evidence-kind coverage
(a `klt sta` envelope over fifteen corners plus a `klt
functional-verification` envelope), **not** a statement that the block meets
its ratified spec: the grader does not read the spec rows, and the area and
power rows stay missed ([#700](https://github.com/2AMLogic/gf180-trng/issues/700)).
See "Item 5 digital" below. Items 1, 2, 9 and 10 are `met` on an
artifact-anchored inventory, which means something much narrower than their
names suggest: see "Items 1, 2, 9 and 10 are cited from hashed inventories"
below before reading anything into them.
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
the other four reads the way it does.

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
  evidence/digital-sta/klt_sta_response.json       item 5 (digital)'s native klt sta response, 15 corners
  evidence/digital-sta/request.json                its request (SPEF paths are regenerated, not committed)
  evidence/digital-sta/comparison.json             its worst setup/hold against the Markdown sweep records
  evidence/post-route/gate_klt_response.json       item 7 (digital)'s native klt functional-verification response
  evidence/post-route/publication.json            its freshness pins (netlist, SDF, raw evidence) and coverage limits
  publish_item7.py                                 publishes a successful post-route run as the 7.digital citation
  evidence/post-layout/ro_ring11.pex.json          item 7 (analog)'s native klt pex response over ring1's layout
  evidence/post-layout/ro_ring11.extracted.spice   the netlist that klt pex run extracted and simulated
  evidence/post-layout/publication.json            its testbench-side pins (request, testbench body, schematic DUT) and body_bias status
  publish_item7_analog.py                          runs klt pex over ring1 and publishes it as the 7.analog citation
  publish_common.py                                the klt pex publishers' shared run / refuse / write-or-restore steps
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
pip install "klayout-tools==0.8.0"   # the grader; no PDK, no KLayout GUI needed (klt-pin: grader)
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
eleven. 0.7.0 renders the same eleven and is the first release that grades the
artifact-anchored generic envelopes behind items 1, 2, 9 and 10. The record carries `build.version`, `build.git_commit`,
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
   verified 28 of 28 on the run that produced the committed record (one of
   them the 7.digital publication, checked by its own pins, see "Item 7
   digital"; the 7.analog publication's testbench-side pins are checked on
   top, see "Item 7 analog"; and eight of them the item 1/2/9/10 inventories,
   each re-derived member by member from the live tree, see "Items 1, 2, 9 and
   10 are cited from hashed inventories"). Edit
   `layout/blocks/combiner_sampler/combiner_sampler.gds`,
   `layout/digital/trng_top.gds`, `layout/digital/trng_top.extracted.spice`,
   `sim/characterization-digital-sta-area-power.md` or
   `sim/characterization-analog-summary.md`, or any file an item 1/2/9/10
   inventory lists, without re-running the evidence behind it (or, for an
   inventory, regenerating it with `--write`) and this fails.
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

**Attempt log (2026-10-10, second session).** Same pin, same host rules (grid
only through `klt pex --backend batch`; no local fallback). The offline
checks (`stimulus.py --check`, `build_dut.py --check-source`, the 34-test
regression, `build_dut.py --check`) passed. Four further
`publish_combiner_sampler_pex.py --backend batch` submissions were made and
none produced a complete two-sided response:

* The first failed on the schematic side with
  `batch-fleet-provision.sh launch failed (exit 1): error: no capacity in any
  of the 30 pools after 3 attempt(s)`.
* Two retries after a wait of about 150 s each returned `klt pex` exit 4 with
  a native envelope whose 1782 delta rows (27 corners x 66 rows) were all
  `status: error`, with no per-row reason in the envelope.
* A diagnostic re-run with `--format text` showed the schematic side
  completing and the extracted side failing with the same capacity refusal
  text as above.

The publisher refused to publish, so nothing was committed and no row counts
as a pass. The incomplete envelopes were not kept as evidence because they
carry no measurement. A run with the host-default `klt` (0.7.0, not the
pin) also errored and was discarded; it is not the producer of record. The
grid was not run locally. The item remains unrun and the issue open. See
klayout-tools#2989 and #2990.

**Attempt log (2026-10-10, third session).** Same pin and host rules (batch
only; no local fallback). The offline checks passed. Two
`publish_combiner_sampler_pex.py --backend batch` submissions, about 100 s
apart, both failed on the schematic side with
`batch-fleet-provision.sh launch failed (exit 1): error: no capacity in any of
the 30 pools after 3 attempt(s) — this is the capacity-refusal case, and it
is now visible instead of silent`. `klt pex` reported `nothing published`; the
partial extraction netlist it left behind was removed, so no evidence is
committed and no row counts as a pass. The grid remains unrun and #418 open.
See klayout-tools#2989 and #2990.

**Attempt log (2026-10-10, fourth session).** Same pin and host rules (batch
only; no local fallback). The offline checks, the 34-test regression and
`build_dut.py --check` passed. One `publish_combiner_sampler_pex.py --backend
batch` submission returned `klt pex` exit 4; a diagnostic `--format text`
re-run reported `corners: 27  rows: 1782  passed: 0  failed: 0  errored: 1782`
with every schematic and extracted value `None`. The publisher refused to
publish, the partial extraction netlist it left behind was removed, and no row
counts as a pass. The grid remains unrun and #418 open. See klayout-tools#2989
and #2990.

**Attempt log (2026-10-10, fifth session).** Same pin and host rules (batch
only; no local fallback). The offline checks, the 34-test regression and
`build_dut.py --check` passed. One `publish_combiner_sampler_pex.py --backend
batch` submission ran for about 100 s and `klt pex` exited 4 ("klt pex failed
(exit 4); nothing published"); a direct `klt pex ... --format text --backend
batch` re-run printed `status: error`, `corners: 27  rows: 1782  passed: 0
failed: 0  errored: 1782` and wrote nothing to stderr, so the cause (capacity
refusal or another fleet failure) is not distinguishable from the output. No
envelope was kept and no row counts as a pass. The grid remains unrun and #418
open. See klayout-tools#2989 and #2990.

## Why each item reads the way it does

The grader's verdict is in `records/t1-tier-report.json`. This section is the
part the grader structurally cannot check — what was cited, what was
deliberately *not* cited, and the disclosures `design-evidence-tiers.md`
requires of the claimant rather than of the tool.

| # | analog | digital | Reading |
|---|---|---|---|
| 1 Design sources | **`met`** | **`met`** | Cites `evidence/t1-item-1-{analog,digital}.json`, bound to `evidence/inventory-1-{analog,digital}.json`: every `design/xschem/*.sch`/`.sym` and the seven derived `design/*.spice` netlists (analog), and the RTL under `design/trng_top/`, `design/conditioner/`, `design/health_test/` and `design/interface/` with its synthesized netlist and generated register map (digital), each with its sha256. The regeneration gates are named, not run: `design/netlist.py --check` (xschem + PDK) and `design/synth.py --check` (`klt synthesize`) run only in `pdk-nightly.yml`; `design/netlist.py --lint` and `design/interface/regmap.py --check` are PDK-free and run in the PR-blocking job. See "Items 1, 2, 9 and 10 are cited from hashed inventories". |
| 2 Layout | **`met`** | **`met`** | Cites `evidence/t1-item-2-{analog,digital}.json`, bound to `evidence/inventory-2-{analog,digital}.json`: the hand-drawn cell, ring and block streams with their reference netlists and the composed `layout/floorplan/trng_floorplan.gds` (analog), and `layout/digital/trng_top.gds` with its DEF, as-built netlist, SDF and LVS reference (digital). The stream the item 3/4 citations pin (`layout/blocks/combiner_sampler/combiner_sampler.gds`, `layout/digital/trng_top.gds`) is a member of its inventory and `check.py` holds its hash to those manifest pins. DRC/LVS are not re-run: `layout/verify.py --require-tools` and the other tool-gated checks run only in `pdk-nightly.yml`. The `met` does not assert the layout meets the area budget. |
| 3 DRC clean | **`met`** | **`met`** | Analog cites `layout/reports/combiner_sampler.drc.json`, digital cites `layout/digital/reports/drc.json` — both `status: clean`, both against deck `gf180mcu` identified by content hash, both pinned and `input_verified: true`. The two partitions' decks are the same deck; their *coverage* is not, because the streams differ. Both enumerated below. |
| 4 LVS clean | **`met`** | **`met`** | Analog cites `layout/reports/combiner_sampler.lvs.json` (`status: match`, `mismatch_count: 3`, warnings only — `device.body_unverified` ×2, one per MOS class, and `topology` ×1); digital cites `layout/digital/reports/lvs.json` (`status: match`, `mismatch_count: 1`, the `topology.power_only_pruned` warning only). Both citations carry a `content_hash` pin and read `input_verified: true` (analog since [#281](https://github.com/2AMLogic/gf180-trng/issues/281)). Neither compare verifies body ties: `body_verification.status` is `"unverified"` (analog: all 104 MOS bodies untapped) and `"unchecked"` (digital). Power connectivity is `"unchecked"` on analog and a computed `"match"` on digital since [#662](https://github.com/2AMLogic/gf180-trng/issues/662). See "Item 4 is `met` twice, and both are pinned" for the verbatim blocks and what each compare did *not* verify. |
| 5 Corner verification | `unmet` / `no_evidence` | **`met`** | This block's largest *real* gap on the analog side, and a narrower one on the digital side. README's ratified spec table still misses four rows (raw rate, raw min-entropy, area, power), and the grader does not read them. **Digital** (#699) cites two native envelopes, both graded `met`: `evidence/digital-sta/klt_sta_response.json`, one `klt sta` request over the committed routed DEF at all fifteen (liberty × interconnect) points with a propagated CTS clock, per-corner OpenRCX SPEF and the trunk input transitions, pinned and `input_verified: true`; and `evidence/post-route/gate_klt_response.json`, the item-7 functional suite, at **one** corner. See "Item 5 digital" below for what that does and does not say; the area and power rows ([#700](https://github.com/2AMLogic/gf180-trng/issues/700)) are unchanged. The analog half is no longer blocked on the tool: klayout-tools#2533 shipped in 0.7.0, whose `klt sim` accepts a caller-side `expr` measurement. What blocks it now is that no ratified analog row carries a measured quantity to cite — see "Item 5 analog: which spec rows a `klt sim` envelope could cover" below, which enumerates every row and declares each gap. `5.analog` is not cited. |
| 6 Monte Carlo | `unmet` / `no_evidence` | `unmet` / `no_evidence` | `sim/characterization-worst-corner-and-mc-mismatch.md` is a real Monte Carlo campaign with recorded seeds, sample counts, two PVT points and a deterministic negative control. Item 6 accepts only a `klt yield` report, and none exists. As of 2026-10-17 no reproducible install route for `klt yield` exists at any released `klayout-tools`: the verb needs the `klt_yield_native` extension, and `uvx --from "klayout-tools[yield]==0.7.0" klt yield --help` fails to resolve (`klt-yield-native` is not on PyPI, HTTP 404 on its simple index), while the `klayout-tools` GitHub releases carry no wheel assets. The wheel publication is tracked upstream as klayout-tools#2900 (open); klayout-tools#2531 and #2714 are closed but did not make a wheel reachable. The only remaining route is an unpinned Rust source build, which is rejected as non-reproducible. See "Item 6: install route and statistical rows" below. Separately, klayout-tools#2480 makes the campaign's own `sample_size.verdict` and negative-control result (`undersized_sample` / `negative_control_not_detected`) grading inputs, so a `klt yield` report over this campaign is not automatically a `met` verdict even once one can be produced. |
| 7 Post-layout | **`met`** | **`met`** | **Analog** cites the native `klt pex` response over ring1's layout (`evidence/post-layout/ro_ring11.pex.json`), published by `publish_item7_analog.py` from `sim/tb/ro-ring11-pex/` (#326): 27 corners, 81 delta rows, every row measured on both sides, `input_verified: true`. Its `body_bias.status` is `"unbiased"` (23 of 23 PMOS bodies on floating wells), which the grader reports and does not grade — see "Item 7 analog" below; it covers ring1 only. **Digital** cites the native `klt functional-verification` response of the SDF-annotated post-route gate run (`evidence/post-route/gate_klt_response.json`), published by `publish_item7.py` from `sim/tb/trng-top-post-route/` (#314) — see "Item 7 digital" below; the claim is functional equivalence under cell delay at one corner, not timing signoff. The wider post-layout work (`sim/characterization-post-layout-extracted.md`, issues #17/#217/#232: the whole array, device-, routing- and inter-region-level) stays in this repo's Markdown records; `layout/pex/build.py` composes its own netlists and emits no `klt pex` report, and is unchanged. |
| 8 Characterization | **`met`** | **`met`** | Digital cites `evidence/characterization-digital.generic.json`, wrapping `sim/characterization-digital-sta-area-power.md`. Analog cites `evidence/characterization-analog.generic.json`, wrapping `sim/characterization-analog-summary.md` (#313). Both mean that a current aggregate exists. Neither means the rows in it pass. See below. |
| 9 Testbenches shipped | **`met`** | **`met`** | Cites `evidence/t1-item-9-{analog,digital}.json`, bound to `evidence/inventory-9-{analog,digital}.json`: every file of the `sim/tb/` testbench directories, split by partition (a directory with an ngspice `.sp` deck is analog; the nine behavioural/RTL/gate-level ones listed in `signoff/inventories.py`'s `DIGITAL_TESTBENCHES` are digital), each with its documented cold-start invocation, and the PDK revision `pdk-nightly.yml` pins (open_pdks `f6eeac7d…`, variant `gf180mcuD`), which `check.py` requires `README.md` to state too. A new `sim/tb/` directory that is neither fails the audit. No testbench is run here. |
| 10 Repo hygiene | **`met`** | **`met`** | Cites `evidence/t1-item-10-{analog,digital}.json`, bound to `evidence/inventory-10-{analog,digital}.json`: `README.md`, `LICENSE` (Apache-2.0), the ratified spec table, `sim/README.md` and `.github/workflows/ci.yml`, with assertions about each (the README's sections, that it documents how that partition is reproduced, that the workflow runs the named commands). **CI status is not captured**: the workflow file is hashed and its commands named, but whether its last run was green is a property of a run, not of a file, and is not part of what this `met` asserts. |
| 11 Power delivery | `unmet` / `supply_spec_disclosed_unexpressible` | **`met`** | Item 11 is a compound claim, and as of [#655](https://github.com/2AMLogic/gf180-trng/issues/655) both columns cite the whole set, so each reads a graded verdict instead of `wrong_kind`. **Analog** (`11.analog`): the three region `klt erc` supply reports under `layout/analog/reports/` ([#327](https://github.com/2AMLogic/gf180-trng/issues/327)) plus item 4's own LVS envelope `layout/reports/combiner_sampler.lvs.json`, each pinned. The grader reads the ERC specs' `ties_disclosure` (kind `unexpressible`, no `ties[]` declared): the streams draw no Nplus/Pplus/LVPWELL, so well-tie coverage and the `vsubs` body connection are unverified, not passed. **Digital** (`11.digital`): `layout/digital/reports/erc-supply.json` ([#268](https://github.com/2AMLogic/gf180-trng/issues/268), [#276](https://github.com/2AMLogic/gf180-trng/issues/276), [#321](https://github.com/2AMLogic/gf180-trng/issues/321); zero `erc.missing_tie`, clean supplies), item 4's LVS envelope `layout/digital/reports/lvs.json`, and the committed `klt place-and-route` response `layout/digital/reports/place_and_route.json`. Since [#662](https://github.com/2AMLogic/gf180-trng/issues/662) the LVS envelope compares against `trng_top.pnr.v` as `reference.form: "gate-level-verilog"`, so `power_connectivity.status` is a computed `"match"` (4788 instances, zero findings) and the row reads `met`. See "Item 11's `ties[]`" below. |

### Item 6: install route and statistical rows

**Install route (checked 2026-10-17, from a throwaway `uvx` environment, no
host tool touched).**

| Route | Result |
|---|---|
| `uvx --from "klayout-tools==0.7.0" klt --version` | works (`klt 0.7.0`), but `klt yield` needs the native extension <!-- klt-pin: historical --> |
| `uvx --from "klayout-tools[yield]==0.7.0" klt yield --help` | **fails to resolve**: `klt-yield-native>=0.1.0,<0.2` is not in the package registry |
| `klt-yield-native` wheel from a `klayout-tools` release asset | **none exists**: the GitHub releases (`v0.1.0`, `v0.2.0`, `v0.5.0`) carry zero assets |
| Unpinned source build (Rust toolchain) | rejected: not reproducible, and the dispatch hosts are not build boxes |

So no reproducible pin exists, and none is recorded here. This is the
"#2900 still blocks every reproducible route" outcome; it is not a statement
that item 6 is unattainable. When klayout-tools#2900 lands, re-check the first
two rows, pin the working `klayout-tools` version and route here (the item-3/4/7
grader stays pinned at `0.6.0` as above; item 6 may need a newer pin, which
should then be stated as a separate pin rather than a silent bump), and
continue with the steps below.

**Statistical rows.** The campaign's two Monte Carlo measurements are the
ring period spread (`period_r1`, `ro-array-core-mc-freq`) and the sampler
decision-threshold offset (`dtrip_v`, `sampler-dff-mc-offset`), each at
`tt`/27 °C/3.30 V and `ss`/+125 °C/3.63 V. They are matching and offset
quantities, so they are the statistical rows for the **analog** partition,
and item 6 needs MC evidence there. The ratified spec table
(`README.md`) states no numeric limit on either quantity: the rows they bear
on (Entropy source, Raw min-entropy per bit) are sizing-law and placeholder
rows. `klt yield` grades samples against a row's own limits, so the first
thing a report needs, beyond the install route, is a limit to grade against;
adding one is a spec change with a decision record (`spec/`), not something
this README can do. The campaign's own consequence check
(`sim/characterization-worst-corner-and-mc-mismatch.md` §4) compares the
spread with the conditioner and health-test margins instead.

For the **digital** partition no spec row is known to be statistical (the
conditioner, health tests and interface are deterministic logic). The
hash-bound "not applicable" statement that would record this is pending
klayout-tools#2865 reaching a release; none is committed.

**What a report needs once the route exists.** The sample-set document that
`klt yield` reads is `{"measurements": [{"name", "samples", "limits"}, ...]}`
(`sim/characterization-worst-corner-and-mc-mismatch.md` §3.5). The per-seed
values are in the Markdown records `sim/records/2026-08-17-ro-array-core-mc-freq-0{1,2}.md`
and `...-sampler-dff-mc-offset-0{2,3}.md`, with the controls in
`...-freq-control-0{1,2}.md` and `...-offset-control-0{1,2}.md`. Any re-run of
the campaign is a multi-seed grid and goes out as a `klt sim` request with
`monte_carlo` to the batch fleet, never as hand-launched `ngspice -b` loops.
Nothing is cited as `6.analog` or `6.digital`, and
`records/t1-tier-report.json` is unchanged.

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
| **Grader** — parses the T1 checklist and renders the verdict | `0.8.0` (released) | `signoff/check.py`'s `KLT_GRADER_PIN`; CI's `signoff` job |
| **Producer, analog** — `layout/reports/*` | `0.6.0` (released; tag `v0.6.0`, commit `c622e8addb36`), with `klayout==0.30.10` | `.github/workflows/pdk-nightly.yml`, per [DR-0026](../spec/decision-records/DR-0026-normative-klt-build-for-floorplan-reports.md) as amended; `layout/reports/environment.json`'s `klt_origin` |
| **Producer, digital** — `layout/digital/reports/*` | `0.6.0` for DRC/LVS; `0.5.0+g32f69f811682` for the place-and-route that built the stream | recorded in each envelope's own `provenance.klt_version` |

The grader pin is deliberately independent of any producer pin — it grades
committed JSON and needs no PDK, so a third party reproduces the verdict with
one `pip install`. The grader and the analog producer both read `0.6.0` from #281 until #653, a
coincidence of timing, not a coupling: #653 moved the grader to `0.7.0` (the
first release that grades items 1, 2, 9 and 10) and left the producer pins
alone. The digital partition's DRC
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
    exactly that `net_correspondence` pairing. `11.analog` is cited as of #655
    (supply-ERC plus this LVS envelope, see "Item 11's `ties[]`" below), and
    the row reads `unmet` / `supply_spec_disclosed_unexpressible`.
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
- *Digital*: `mismatch_count: 1`, `error_count: 0`, `category_counts:
  {"topology.power_only_pruned": 1}` — one warning, no errors. Since
  [#662](https://github.com/2AMLogic/gf180-trng/issues/662) the request's
  `reference.form` is `gate-level-verilog`, so `power_connectivity.status` is
  a computed `"match"`; `body_verification.status` stays `"unchecked"`, with
  `klt`'s own stated reason in the envelope, and is **not**
  `"verified"`:
  - `power_connectivity` is `match`: `power_pins: ["VDD", "VSS"]` (derived
    from the 83 instantiated masters' own library pin data),
    `instance_count: 4788`, `finding_count: 0`. This is what T1 item 11's
    Digital column requires, and it moved that row to `met` (see "Item 11's
    `ties[]`" above). The warning is `topology.power_only_pruned`: the nine
    tap/endcap/filler masters the Verilog never carries are removed from the
    layout side before comparing, so their rails are covered by the power
    check rather than the signal compare. Before #662 the reference was a
    `plain-element` SPICE transcription and this field read `"unchecked"`.
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

**The digital reference is the as-built netlist, not a schematic.**
The largest caveat on the digital `match` is not in the `klt` envelope at all,
which is why `layout/digital/lvs.py` records it in the report under
`reference_generation`: the reference is `trng_top.pnr.v` itself (the
as-built, post-CTS gate-level netlist OpenROAD wrote), read as
`gate-level-verilog` since #662 (a SPICE transcription of it before that),
not captured independently. So this compare
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
entropy-binding corner only up to 678–8810 bps, against DR-0003's original
1 Mbps raw rate (superseded; the ratified rate is now 2 kbps, DR-0011-rate). At 2 kbps
the law holds for the starved-cell constants (4141 and 8810 bps) and not for the
plain-cell 678 bps. Raw min-entropy is unmeasured and cannot be measured by
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

**This does not move item 11 to `met`.** *History, superseded by
[#655](https://github.com/2AMLogic/gf180-trng/issues/655) below:* as of
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

As of [#655](https://github.com/2AMLogic/gf180-trng/issues/655) item 11 is
cited as the compound list the grader asks for in both partitions, and it now
renders a graded verdict, not `wrong_kind`. Both are `unmet`, for specific
reasons:

- **Analog** cites the three region ERC reports plus the `4.analog` LVS
  envelope (`layout/reports/combiner_sampler.lvs.json`) and reads
  `unmet` / `supply_spec_disclosed_unexpressible`. The runs:
  `layout/analog/erc-supply-spec-rings.json` on `ro_ring11` (ring1) and
  `ro_ring11_ring2` (ring2), and
  `layout/analog/erc-supply-spec-combiner_sampler.json` on `combiner_sampler`;
  reports in `layout/analog/reports/`, each pinned to the
  `provenance.input.content_hash` of its GDS. All three read
  `erc_status: clean`, zero findings, one island per declared supply
  (`vddr`/`vss` on the rings, `vdd`/`vss` on combiner_sampler). What that
  does **not** cover: the specs declare no `ties[]` (these streams draw no
  Nplus/Pplus/LVPWELL, and the reference netlists give every PMOS a floating
  well), so `erc.missing_tie` is not computed and `ties_disclosure.kind` is
  `unexpressible`; `vsubs` is not declared because no label of that name
  exists in any of the three streams (the guard ring lives only in the
  floorplan abstract, which also contains the digital region); the supply
  names are the cell-level `vddr`, not the region-level `vddr1`/`vddr2`; and
  the LVS `body_verification` (`"unverified"`) field remains as disclosed
  above. These three reports cover only the rings' and combiner's own GDS. The
  composed floorplan stream has its own whole-block run,
  `layout/floorplan/reports/erc-supply.json` (issue #447; five region-level
  supplies, Metal1-Metal5, clean), which is not cited by any manifest item
  here and changes no tier.
- **Digital** cites the ERC report, the `4.digital` LVS envelope
  (`layout/digital/reports/lvs.json`) and the `klt place-and-route` response
  (`layout/digital/reports/place_and_route.json`) and reads
  `met` as of [#662](https://github.com/2AMLogic/gf180-trng/issues/662). It
  had read `unmet` / `lvs_supply_unproven` because the additional
  requirement, `power_connectivity.status: "match"` on item 4's LVS citation,
  was `"unchecked"` (reference form `plain-element`). `layout/digital/lvs.py`
  now requests `reference.form: "gate-level-verilog"` with
  `trng_top.pnr.v` as the reference and `gf180mcu_fd_sc_mcu9t5v0` as the
  library, so `klt lvs` computes the check itself: `power_connectivity.status:
  "match"`, `power_pins: ["VDD", "VSS"]`, `instance_count: 4788`,
  `finding_count: 0`. The compare's top-level `status` stays `"match"`; its one
  `mismatch_count` entry is the `topology.power_only_pruned` warning for the
  nine tap/endcap/filler masters, which the gate-level form removes from the
  layout side because the Verilog never carries them. This is a verdict
  *computed* by `klt` on the committed layout, not an edit to the report. The
  `4.digital` pin did not move: it is the extracted netlist's hash
  (`sha256:d661d025…`), and the extraction is unchanged; the regenerated
  report is a different file with the same pinned input.
- **The place-and-route citation is unpinned.** The response records
  `provenance.input.content_hash` (role `netlist`) but no `file`, `layout` or
  `source` field naming that input, and the digest matches no committed file,
  so `signoff/check.py`'s envelope-vs-input step has nothing to compare it
  against. `check.py` exempts it from that step (`PNR_ENVELOPE`), as it does
  `7.digital`'s envelope, and the manifest carries no `content_hash` for it.
  The cost is that drift in this file is not detected by `check.py`; the
  recorded verdict still changes if its `power` block changes, because the
  grader re-reads it. The tool gap, that the response gives no resolvable
  input path for consumer-side freshness checks, is filed generically as
  `2AMLogic/klayout-tools#3751`.

### Items 1, 2, 9 and 10 are cited from hashed inventories

`design-evidence-tiers.md` says plainly that these four have no tool behind
them, and until klayout-tools 0.7.0 `klt signoff` could grade them only on
"some passing envelope was cited at all", which a clean DRC report would
satisfy for item 10 without meaning anything. That is why they were left
`unmet` / `no_evidence` through 8 of 22 (#124): the honest artifact did not
exist as a format. klayout-tools#2718/#2843 (released in 0.7.0) added it: a
`kind: generic` envelope that declares `"t1_item": <n>` and binds the audited
artifact by path and content hash, so the row goes `met` only while that
artifact re-hashes to the pinned value (`citation.input_verified: true`, and an
`artifact_binding` block disclosing what was bound). Since
[#653](https://github.com/2AMLogic/gf180-trng/issues/653) each of the eight
rows cites one.

What is bound is an **inventory**, not the files themselves:
`signoff/evidence/inventory-{1,2,9,10}-{analog,digital}.json`, written by
`signoff/inventories.py` and cited through
`signoff/evidence/t1-item-{1,2,9,10}-{analog,digital}.json`. An inventory lists
every member file with its sha256 and the item's mechanical checks, with
where each one runs. `signoff/check.py` (step 1e) rebuilds every inventory
from the live tree and compares it member by member, so an inventoried file
that changed, was deleted or newly appeared fails by name even though the
inventory's own bytes did not move. `python3 signoff/check.py --write` is the
only thing that re-pins them, and it refuses to write an envelope when the
tree no longer supports the audit (a netlist with no schematic, a layout
directory with no stream, a `sim/tb/` directory nobody classified, a gate the
workflow does not run, a README that no longer states the pinned PDK commit).

**What a `met` here means, and does not.** It means the inventoried files still
hash to the values pinned when the inventory was written, and the inventory's
structural audit held on that tree. It does **not** mean the gates named in
the inventory passed today, and `signoff/check.py` does not run them:

| Item | Named gate | Runs without the PDK? | Where it runs |
|---|---|---|---|
| 1 analog | `design/netlist.py --check` | no (xschem + PDK) | `pdk-nightly.yml` |
| 1 analog | `design/netlist.py --lint` | yes | `ci.yml`, via `npm run lint` |
| 1 digital | `design/interface/regmap.py --check` | yes | `ci.yml`, via `npm run check:regmap` |
| 1 digital | `design/synth.py --check` | no (`klt synthesize`, Yosys) | `pdk-nightly.yml` |
| 2 analog | `design/floorplan_netlist.py --check` | yes | `ci.yml`, via `npm run check:floorplan-netlist` |
| 2 analog | `layout/verify.py --require-tools`, `layout/floorplan/floorplan.py --require-tools` | no (klt + PDK) | `pdk-nightly.yml` (the PR job's `check:layout` / `check:floorplan` self-skip) |
| 2 digital | `layout/digital/build.py --check-input` | yes | `ci.yml`, via `npm run check:digital-input` |
| 2 digital | `layout/digital/tap_distance.py --check --require-tools` | no (klt + PDK) | `pdk-nightly.yml` |
| 9 | `python3 sim/run_corners.py --check-env`, `sim/selftest.sh --require-pdk` | no (ngspice + PDK) | `pdk-nightly.yml` |
| 9 | `npm run test` (drives the behavioural benches; those needing Icarus Verilog self-skip) | yes | `ci.yml` |
| 10 | `python3 signoff/check.py --require-tools` | yes | `ci.yml` |

Each envelope's `summary` says the same thing about its own gates. Further
limits that travel with these citations:

- **Item 2 asserts the layout exists and is the one DRC/LVS graded**, not that
  it meets the area budget or that any region beyond the cited stream is
  clean. The analog inventory also lists streams (rings, cells, the composed
  floorplan) that no item 3/4 citation pins; their hashes are held fresh, not
  verified by a tool.
- **Item 9 does not run or re-derive any measurement**, and the digital
  benches' inventory says nothing about whether they pass. The analog
  partition's benches are started in several ways (`tb.json` corner runs via
  `sim/run_corners.py`, `klt sim` request decks, README-documented tools); the
  invocation, or the file that documents it, is recorded per directory.
- **Item 10 does not capture CI status.** See the row above.
- **The partition split of item 1 follows `design/`'s own layout**
  (`design/xschem/` + `design/*.spice` analog; the `.v` trees digital).
  `design/xschem/trng_top.sch` is analog-side capture of the top-level wiring.

**Grader pin move (0.7.0, #653).** These rows need klayout-tools 0.7.0, so
`signoff/check.py`'s new `KLT_GRADER_PIN` is `0.7.0`. `KLT_PIN` stays `0.6.0`:
it is the **producer** pin DR-0026 ratifies for the layout reports, and the
publishers and `layout/floorplan/erc_supply.py` refuse any other build. The
two had been equal since #281; they were already documented as independent
(see "Which `klt` produced what"). Effect of the move, measured by re-grading
the manifest as it stood before #653 under 0.7.0: **no row changed status or
reason**, 8 of 22 stayed 8 of 22, and only the report's `build.*`,
`grading_ruleset_id` and `source_doc_content_hash` (and the checklist prose
copied into each row) moved. The eight new `met` rows are therefore entirely
the new citations, not the pin.

**Grader pin move (0.8.0, #699).** Item 5 digital needs klayout-tools 0.8.0:
per-port `input_transitions`, a `spef` map keyed by interconnect corner and
`propagated_clock` (klayout-tools#3227, #3228, #2739) are what let one `klt
sta` request state the sweep's analysis. `KLT_GRADER_PIN` is `0.8.0`; `KLT_PIN`
(the producer pin) stays `0.6.0`. Measured by re-grading the manifest as it
stood before #699 under 0.8.0: **no row changed status or reason**; only
`build.*` and `grading_ruleset_id` moved. The one row change, item 5 digital
`unmet` to `met`, is the new citation.

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
  `power_connectivity` is `"unchecked"` on the analog citation and a
  computed `"match"` on the digital one since #662; `body_verification` is `"unverified"` on the analog one (104 of 104 MOS
  bodies) and `"unchecked"` on the digital one, each with `klt`'s own stated
  reason. Neither partition's LVS verdict includes a verified body-tie, and the
  analog one has no `"match"` power-connectivity result; both are disclosed
  above rather than folded into the word "match".

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

## Item 5 digital

The grader wants two kinds for the digital column: a `klt sta` envelope and a
`klt functional-verification` envelope (citing one grades `partial_coverage`).
[#322](https://github.com/2AMLogic/gf180-trng/issues/322) declined to cite a
`klt sta` run because klt 0.6.0 could not state the analysis the fifteen-corner
sweep (`sim/tb/digital-sta-power/run_sta.py`) records.
[#699](https://github.com/2AMLogic/gf180-trng/issues/699) cites both, after
klayout-tools#2858 and #2739 shipped in 0.8.0 and the grader pin moved to it.

**The `klt sta` envelope** (`evidence/digital-sta/klt_sta_response.json`) is
one request, `python3 sim/tb/digital-sta-power/run_sta.py --klt-sta`, over the
committed `layout/digital/trng_top.def`: `constraints.propagated_clock` (the
CTS-built tree, as the sweep does), the `spef` map keyed `min`/`nom`/`max`,
`input_transitions` for the trunk ports and a `pdk.corners` list of the five
liberty corners, so the response carries 5 × 3 = 15 `corners[]` entries. Every
one is `constrained`, setup and hold violation counts are 0, worst setup
+31.22 ns to +44.61 ns (50 ns constraint) and worst hold +0.695 ns
(`ff_n40C_3v60`, `min`) up to +2.38 ns.

**It is the same analysis as the Markdown records, and that is checked, not
asserted.** `run_sta.py --klt-sta` compares each point's worst setup and worst
hold against the newest committed `digital-sta-power` record of that point and
exits non-zero beyond 1 ps; `evidence/digital-sta/comparison.json` is the
committed result: the largest difference over all 30 numbers is 0.05 ps (a
rounding difference, klt reports five significant figures). Two stated
differences remain, neither of which moved a number:

- **No transition on `clk`.** `klt sta` rejects an `input_transitions` entry
  on the clock port, whereas the sweep also states the `clk` trunk's. The five
  other trunk ports are stated. Comparing against the records, the omission is
  below the 0.05 ps above.
- **The SPEFs are caller-side inputs.** klt has no verb that extracts a routed
  DEF's parasitics at a chosen corner (klayout-tools#2858's close note), so
  the three SPEFs are written by OpenRCX inside `run_sta.py` (one extraction
  per interconnect corner) and not committed, as with the sweep's own. The
  envelope records each one's `spef_path` (not a hash) and pins the DEF
  (`provenance.input.content_hash`, `input_verified: true`). `check.py`
  re-hashes the DEF through `def_path`; the SPEFs are regenerated by the command
  above, so their freshness is carried by the comparison against the records,
  not by a pin.
- **Annotation coverage.** Each corner's `spef_annotation` reports 1479 of 1513
  design nets annotated, the same 1479 nets the records' `spef_nets` counts;
  the unannotated drivers are the 28 floating CTS `clkload` cells and nets
  with no routed wire. It is reported, not graded.

**The functional envelope** is the item-7 digital citation
(`evidence/post-route/gate_klt_response.json`, 8 of 8 scenarios, SDF
annotated), cited again here, with its own limits (see "Item 7 digital"):
**one corner** (SDF `typ` generated from `ss_125C_3v00`), cell `IOPATH` delay
only. Item 5 asks for per-corner per-test results; this is not that, and the
README states why instead of presenting it as such. `layout/digital/gen_sdf.py`
writes one SDF at one liberty corner (its `min_typ_max` is "identical -- one
liberty corner only"), no multi-corner SDF exists, and Icarus enforces no
setup/hold check, so a run at another corner would exercise only cell delay
scaling against a 50 ns clock. Timing at the other fourteen points is the `klt
sta` envelope's job and is covered by it. A multi-corner SDF export plus
per-corner regressions would be new producers, not a re-publication, and are
not attempted.

**What `met` here does not say.** The grader does not read this block's spec
rows. Item 5 digital reads `met` while the ratified area and power rows are
still missed ([#700](https://github.com/2AMLogic/gf180-trng/issues/700),
`sim/characterization-digital-sta-area-power.md`), and the T1 tier is still
`null`. Do not read it as "the digital block meets its spec at every corner".

## Item 5 analog: which spec rows a `klt sim` envelope could cover

[#654](https://github.com/2AMLogic/gf180-trng/issues/654) asked whether
klayout-tools 0.7.0 (#2533: a `klt sim` `measurements[]` entry may carry a
single-line `expr`, evaluated inside `klt sim`'s own `.control` block) opens
`5.analog`. The tool no longer stands in the way. This section is the
enumeration the issue asked for, row by row, against the README's target
specification and the status tags defined in
[`docs/spec-row-status.md`](../docs/spec-row-status.md#status-tags). The
question for each row is whether a *measured quantity with a ratified bound*
exists for a `klt sim` envelope to report pass/fail on.

**Result: none does, so no envelope is written and `5.analog` stays uncited.**
Writing one anyway would have meant choosing a bound the spec does not state,
which is the thing this repository's spec process exists to prevent.

| Spec row | Status tag | Analog quantity | Expressed? | Why |
|---|---|---|---|---|
| Entropy source | `specified` | the jitter-budget inequality `Q_array ≥ 1.5 × 4.0×10⁻³` (DR-0007 §2) | declared gap | A design decision with no measured quantity to meet or miss. The inequality is evaluated by `sim/tools/array_sizing.py` from committed period and supply-current records plus a constant `a = 7.32` taken from a long-transient jitter measurement (`sim/tb/ro-ring5-starved-jitter-long-batch/request-ring5-hot.json`); the statistic over that long transient is not a scalar `expr`, and no transistor-level run of the array's own `σ_acc` is affordable. |
| Raw rate | unratified (`unmeasured`) | — | excluded | One of the four rows `README.md` says are still unratified. |
| Raw min-entropy per bit | unratified (`unmeasured placeholder`) | — | excluded | Same; no `H` figure is supportable by transistor-level simulation. |
| Quality | `specified` | none | declared gap | A conformance statement; 90B validation is deferred to measured silicon (DR-0004). |
| Conditioning | `specified` | none (digital, behavioral per DR-0009) | declared gap | Not an analog quantity; and ratified unmeasured. |
| Delivered rate | `derived from target` | none | declared gap | Arithmetic on the unmeasured raw-rate target. |
| Health tests | `specified` | none (closed-form, digital) | declared gap | No PVT dependence and no analog quantity. |
| Time-to-first-valid | `derived from target` | oscillator start-up, 27 points (`sim/tb/ro-array-core-startup/`) | declared gap | The row's bound (`≥ ~0.640 s`) is an arithmetic floor made of sample counts at the unmeasured 2 kbps; the oscillator term is 4–13 ns against it and has **no bound of its own**. The bench reports edge times and swings, and `sim/tools/time_to_first_valid.py` applies a 1 % first-and-thereafter convergence walk to them, a tolerance the records deliberately leave out. An envelope would need a start-up limit the spec does not state. |
| Power | unratified (`missed`) | — | excluded | The four-row exclusion. |
| Area | unratified (`missed`) | — | excluded | The four-row exclusion; not a simulation quantity. |
| Operating envelope | `specified` | the corner set itself | declared gap | Defines the corners every other row is evaluated over; it is not a quantity with a pass/fail. |
| Interface | `specified` | none | declared gap | A digital interface decision. |

No row has a `met` or `missed` tag outside the four-row exclusion, which is
the repository's own definition of "has a measured quantity". Counting rows
with a measured analog quantity *and* a ratified bound gives zero, so there
are no per-corner values to compare against `sim/records/`: the agreement
check in the issue has nothing to compare, and no existing record or spec
bound is touched.

Two facts about the grader bear on any later attempt:

- The grader pin stays at 0.6.0. Citing an `expr` measurement needs the 0.7.0
  bump, but with nothing to cite the bump would only re-render the record.
- The 0.7.0 wheel grades item 5 from **one** `sim` envelope per partition. The
  declared-row-set support for several envelopes (klayout-tools#2959, closed
  2026-10-15) is not in the 0.7.0 `signoff.py`. A block whose analog spec
  needs several testbenches therefore cannot cite them as a set at a released
  build yet; this is already tracked upstream, so no new issue is filed.

What would change this: a ratified bound on a quantity a bench measures (a
start-up limit, a jitter figure, a rate), by a superseding decision record,
not by an edit here.

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
3. ~~**Emit corner evidence as a `klt sta`/`klt functional-verification`
   envelope** for the digital half~~ — done in
   [#699](https://github.com/2AMLogic/gf180-trng/issues/699): see "Item 5
   digital". What remains: the functional envelope covers one corner, and item
   5's *design* gap (four ratified rows still missed, #700) is real and
   separate. The analog half is not on this list as work this block can do
   today: `klt sim` can express a caller-side post-processed measurement since
   klayout-tools 0.7.0 (#2533), but no ratified analog row has a measured
   quantity and a bound to put in one -- see "Item 5 analog: which spec rows a
   `klt sim` envelope could cover".
4. ~~**A `klt pex` report** over the post-layout extraction that already
   exists (item 7).~~ **Done for ring1 only** —
   [#326](https://github.com/2AMLogic/gf180-trng/issues/326) cites a native
   `klt pex` report as `7.analog` and moved the verdict of record from 7 to
   8 of 22. Its `body_bias.status` is `"unbiased"`, so the number that would
   actually move the needle is a re-run on a layout with drawn well ties
   (see "Item 7 analog"). Item 6's `klt yield` report is still not something this block can
   produce: as of 2026-10-17 klayout-tools#2900 (open) leaves every reproducible
   install route blocked — the `[yield]` extra does not resolve and no
   release-asset wheel exists (see "Item 6: install route and statistical
   rows"). Once a pinned route exists, the steps there apply, and
   klayout-tools#2480's sample-size and negative-control grading inputs still
   apply to the resulting report.
5. ~~**A `klt erc` supply spec and run**~~ **Done, in two steps** — the spec
   and report first landed via [#268](https://github.com/2AMLogic/gf180-trng/issues/268),
   and [#276](https://github.com/2AMLogic/gf180-trng/issues/276) declared
   the spec's `ties[]` once klayout-tools#2186 shipped, so `erc.missing_tie`
   is now computed and zero. Item 11 reads `met` on digital only: `11.digital` is cited
   (#321) and `11.analog` (#327) with ERC reports, and as of #655 both cite the
   full compound set and read a graded verdict (analog `unmet` /
   `supply_spec_disclosed_unexpressible`); `11.digital` has read `met` since #662, once the LVS
   reference became gate-level Verilog and `power_connectivity.status` became
   `"match"` — see "Item 11's `ties[]`" above.

Items 1, 2, 9 and 10 were the ones that needed nothing built — only an honest
artifact to cite. [#653](https://github.com/2AMLogic/gf180-trng/issues/653)
did that (see "Items 1, 2, 9 and 10 are cited from hashed inventories").

Item 11's remaining gaps are tracked under
[#124](https://github.com/2AMLogic/gf180-trng/issues/124), this repo's
general gap-to-T1 tracker. Tool-side friction this surfaces is filed at
`2AMLogic/klayout-tools`, per this repo's friction protocol (`CLAUDE.md`) —
so far klayout-tools#2342, #2531 (item 6's `klt yield` unreachable from any
published release), #2533 (item 5's analog half uncitable before 0.7.0; resolved there)
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

**Currently unrun.** The batch fleet first refused the 27-corner submission for
capacity. A second attempt (#476) ran on the fleet, but every corner on both
sides errored unmeasured, because the pinned 0.6.0 client does not ship the
`.include`d DUT and the fleet runner is klt 0.5.0
(`sim/records/2026-10-10-ro-ring11-ring2-pex-attempt-01.md`). The grid was
not run locally, so no ring2 result is committed. The README in that directory
has the reproduction commands. Whatever it eventually
reports describes a layout with floating PMOS wells (#339/#411) and is a
diagnostic under that limitation: no entropy, full-chip timing or
silicon-performance claim.
