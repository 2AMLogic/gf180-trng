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

**Today: `tier: null`, T1 5 of 22 items met.** A `mixed-signal` block is
graded twice over, once per partition, so the eleven-item checklist renders
22 rows. The five met are item 3 (DRC) and item 4 (LVS) on **both**
partitions, and item 8 (characterization report) on the digital partition.
That is the honest state of the block; the rest of this file is why each of
the other seventeen reads the way it does.

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
  records/t1-tier-report.json                      the verdict of record (generated)
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
   for four of the five citations and `null` only for `4.analog`, whose
   envelope predates `provenance.input` (see "Item 4 is `met` twice"
   below). `check.py` covers the whole set regardless of envelope kind — it
   verified 5 of 5 on the run that produced the committed record. Edit
   `layout/blocks/combiner_sampler/combiner_sampler.gds`,
   `layout/digital/trng_top.gds`, `layout/digital/trng_top.extracted.spice`
   or `sim/characterization-digital-sta-area-power.md` without re-running the
   evidence behind them and this fails.
2. **The manifest and the envelope disagree about the pin**, so a
   half-finished re-pin fails loudly instead of silently rendering the item
   `stale_evidence`.
3. **`klt signoff --manifest` could not run** (exit 1 or 2 — a broken manifest
   or an unparseable tier doc; exit 0 and exit 3 are both clean runs).
4. **The committed record no longer matches a fresh run.** Either this block's
   evidence moved, or the checklist did, or the grader did. All three are real
   news, and none should be discoverable only by someone re-reading prose.

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
| 4 LVS clean | **`met`** | **`met`** | Analog cites `layout/reports/combiner_sampler.lvs.json` (`status: match`, `mismatch_count: 2`, warnings only); digital cites `layout/digital/reports/lvs.json` (`status: match`, `mismatch_count: 0`). Only the digital citation carries a freshness pin — see "Item 4 is `met` twice, and only one of the two is pinned" for that and for what each compare did *not* verify. |
| 5 Corner verification | `unmet` / `no_evidence` | `unmet` / `no_evidence` | This block's largest *real* gap, and an evidence-format gap on top of it. README's ratified spec table still misses four rows (raw rate, raw min-entropy, area, power). Separately, item 5 accepts only a `klt sim` envelope (analog) or `klt sta`/`klt functional-verification`/`klt sim` (digital); this repo's ~950 corner records under `sim/records/` are its own Markdown format, and the fifteen-corner digital STA sweep is likewise recorded as Markdown. Nothing here is gradeable yet. |
| 6 Monte Carlo | `unmet` / `no_evidence` | `unmet` / `no_evidence` | `sim/characterization-worst-corner-and-mc-mismatch.md` is a real Monte Carlo campaign with recorded seeds, sample counts, two PVT points and a deterministic negative control. Item 6 accepts only a `klt yield` report, and none exists. |
| 7 Post-layout | `unmet` / `no_evidence` | `unmet` / `no_evidence` | Real post-layout work exists on both sides — device- *and* routing-level parasitic re-simulation (`sim/characterization-post-layout-extracted.md`, issues #17/#217/#232) and an SDF-annotated post-route gate-level functional run (`sim/tb/trng-top-post-route/`, #147). Item 7 accepts only a `klt pex` envelope (analog) or `klt pex`/an SDF-annotated `klt functional-verification` envelope (digital), and neither exists in envelope form: `layout/pex/build.py` drives `klt extract --parasitics` and composes the result itself rather than emitting a `klt pex` report. |
| 8 Characterization | `unmet` / `no_evidence` | **`met`** | Digital cites `evidence/characterization-digital.generic.json`, wrapping `sim/characterization-digital-sta-area-power.md`. Analog is uncited — see below. |
| 9 Testbenches shipped | `unmet` / `no_evidence` | `unmet` / `no_evidence` | 64+ testbenches under `sim/tb/`, each with a documented cold-start invocation, and the PDK revision pinned in README and `pdk-nightly.yml`. Uncited on purpose. |
| 10 Repo hygiene | `unmet` / `no_evidence` | `unmet` / `no_evidence` | README, spec table, reproduction instructions, Apache-2.0 licence and green CI all exist. Uncited on purpose. |
| 11 Power delivery | `unmet` / `no_evidence` | `unmet` / `no_evidence` | `layout/digital/erc-supply-spec.json` and `layout/digital/reports/erc-supply.json` exist ([#268](https://github.com/2AMLogic/gf180-trng/issues/268)) and, as of [#276](https://github.com/2AMLogic/gf180-trng/issues/276), the spec's `ties[]` is declared and `erc.missing_tie` is computed and zero — see "Item 11's `ties[]`" below. The row still reads `unmet`/`no_evidence` because `signoff/block-manifest.json` cites no `11.analog`/`11.digital` evidence yet, and — independent of that — the digital column's own extra requirement, `power_connectivity.status: "match"`, remains `"unchecked"` (see "Item 4 is `met` twice" above). The item has a row here rather than being silently absent because it was added to the checklist on 2026-09-17 (klayout-tools#2025) and invalidated every hand-read that predates it. |

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
- `coverage.rules_skipped` (19): `bjt.separation.comp.1`, `comp.space.mv.1`,
  `comp.width.mv.1`, `metal3.enclosing.via3.1`, `metal4.enclosing.via3.1`,
  `metal4.enclosing.via4.1`, `metal5.enclosing.via4.1`, `metal5.space.1`,
  `metal5.width.1`, `metaltop.space.1`, `metaltop.width.1`,
  `mim.enclosing.fusetop.1`, `mim.enclosing.via4.1`, `mim.space.1`,
  `pad.enclosing.metal5.1`, `via3.space.1`, `via3.width.1`, `via4.space.1`,
  `via4.width.1`.

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

The digital run skips **fewer** rules than the analog one (7 against 19), and
the difference is informative in the same direction both ways: a deck rule is
"skipped" when the stream draws none of the layers it needs, so the twelve
rules the analog run skipped and the digital one did not — `comp.space.mv.1`,
`comp.width.mv.1`, `metal3.enclosing.via3.1`, `metal4.enclosing.via3.1`,
`metal4.enclosing.via4.1`, `metal5.enclosing.via4.1`, `metal5.space.1`,
`metal5.width.1`, `via3.space.1`, `via3.width.1`, `via4.space.1`,
`via4.width.1` — are rules that were *checked* on the digital stream
(39 rules checked in all), because the routed PDN and signal routing actually
reach those layers. The seven both runs skip are the BJT-separation, MIM
capacitor, MetalTop and bond-pad rules, skipped on both because neither
stream contains a BJT, a MIM capacitor, a MetalTop shape or a pad. Every
digital-skipped rule is also analog-skipped; there is no rule the analog
partition checked and the digital one did not.

**The digital citation's coverage block is the stronger of the two**, because
it was produced by a newer `klt` (see "Which `klt` produced what" below).
Alongside the two lists above it carries `coverage.skipped: []`,
`coverage.unknown: []`, `coverage.nothing_checked: false`, and an
`coverage.inapplicable` array that gives each of the seven a machine-readable
reason (`"no_applicable_geometry"` for all seven) rather than leaving a
reader to infer it. Those fields do not exist on the analog citation, which
predates them — one more reason #281 is worth doing.

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
| **Producer, analog** — `layout/reports/*` | `0.4.0+g3fbb4478e301` | `.github/workflows/pdk-nightly.yml` |
| **Producer, digital** — `layout/digital/reports/*` | `0.6.0` for DRC/LVS; `0.5.0+g32f69f811682` for the place-and-route that built the stream | recorded in each envelope's own `provenance.klt_version` |

The grader pin is deliberately independent of any producer pin — it grades
committed JSON and needs no PDK, so a third party reproduces the verdict with
one `pip install`. The digital partition's DRC and LVS were re-emitted under
`0.6.0` by #273, which is also why they carry envelope fields the analog ones
do not (`provenance.input`, `power_connectivity`, `body_verification`, the
richer `coverage` schema). Re-running the analog side to match is #281, and
it is not a mechanical regeneration: it is entangled with
[DR-0026](../spec/decision-records/DR-0026-normative-klt-build-for-floorplan-reports.md)
(status `Proposed`), whose "no verdict moved" measurement #281 shows has gone
stale at 0.6.0. The DRC verdict, at least, is measured not to move: #273's
re-run under 0.6.0 reproduced `reports/place_and_route.json`'s existing
nested `drc` digest byte for byte.

### Item 4 is `met` twice, and only one of the two is pinned

The two partitions reach `met` from genuinely different evidence, so their
disclosures do not merge.

**Analog carries no freshness pin, and that is a property of the evidence,
not a shortcut.** Every other citation in the manifest pins a `content_hash`.
`4.analog`'s cannot: `klt lvs` only began populating
`provenance.input.content_hash` in klayout-tools#1969, and
`layout/reports/combiner_sampler.lvs.json` was produced by klt
`0.4.0+g3fbb4478e301`, which leaves it `null`. Pinning a hash against a
`null` would render the item `stale_evidence`, which would be a *false*
negative. The freshness claim is still enforced here — the same digest is
recorded as `environment.layout_sha256`, and `check.py` re-hashes
`layout/blocks/combiner_sampler/combiner_sampler.gds` against it on every run
— it is simply enforced by this repo rather than by `klt signoff`'s own
staleness gate, which is why the grader reports
`citation.input_verified: null` for that row and `true` for the other four.
Moving that pin into the manifest is tracked as
[#281](https://github.com/2AMLogic/gf180-trng/issues/281); it needs the
producer-build question settled first, and #281 records the measurement of
what moves when it is.

**Digital is pinned.** `4.digital` cites
`layout/digital/reports/lvs.json` with
`content_hash: sha256:26983bc3…`, matching the envelope's own
`provenance.input.content_hash` and `environment.layout_sha256`, all three
naming `layout/digital/trng_top.extracted.spice` — so `klt signoff`'s own
staleness gate reaches this row (`citation.input_verified: true`) rather than
this repo standing in for it.

**What each compare did and did not verify.**

- *Analog*: `power_connectivity` and `body_verification` are both `null` —
  klt 0.4.0 predates both blocks, so the power/ground half of the compare was
  never run and the body ties were never verified. `design-evidence-tiers.md`
  is explicit that `"unchecked"` is not `"verified"`, and `null` is weaker
  still. The report carries `mismatch_count: 2` with `error_count: 0` —
  `category_counts: {"topology": 1, "device.body_unverified": 1}` — the same
  warnings-only shape every other analog region's compare carries.
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

### Item 8 is `met` for the digital partition only

`sim/characterization-digital-sta-area-power.md` is the one aggregated,
current artifact item 8 asks a digital partition for: Fmax, placed area and
power across all fifteen corners, each number naming the `sim/records/`
evidence record it rests on, with §0/§0a carrying the `FIFO_DEPTH = 2`
re-measurement (issues #255 and #264) that supersedes the depth-8 sections
retained below them as append-only history.

Item 8 asks for that aggregation artifact to exist and be current. It does
**not** ask for every row in it to pass, and this `met` verdict must not be
read as if it did. The disclosed exceptions, which travel with the claim
rather than being omitted from it: placed cell area is 61 692.0 µm², ×1.833
of the depth-2 pre-synthesis inventory and still over the ratified
`< 0.05 mm²` row on digital cells alone; and measured power remains well
above the library-based estimate at the same corner and rate. Both are item
5's subject matter, and item 5 is `unmet` above. (A third exception this
paragraph used to carry is closed: #255's first depth-2 build regressed the
library `max_transition` check to 11 of 15 corners, and
[#264](https://github.com/2AMLogic/gf180-trng/issues/264) re-tuned the
place-and-route constraint and rebuilt. The current DEF violates at 0 of 15.) One met row out of 22 is not a
claim about this block's performance.

**Item 8 analog is uncited on purpose.** The analog partition has fourteen
per-topic characterization documents under `sim/` and a cross-cutting spec
table in the top-level README, but no single aggregated per-spec-row
characterization artifact of its own. Item 8 asks for *one aggregated,
current artifact*; fourteen topic reports plus a README section is not that,
and wrapping the README in a generic envelope would pin the manifest to a
file that changes for unrelated reasons several times a week. This row is the
clearest example of the machine reading being stricter than the hand read:
issue #124 recorded item 8 as a pass on exactly the "digital doc + README
table" combination.

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

**This does not move item 11 to `met`.** Two separate gaps remain, neither
touched by this change: `signoff/block-manifest.json` does not yet cite any
`11.analog`/`11.digital` evidence (wiring that in is future work, not yet
tracked by a dedicated issue — see [#124](https://github.com/2AMLogic/gf180-trng/issues/124),
this repo's general gap-to-T1 tracker), and the digital column's own
additional requirement — `power_connectivity.status: "match"` on item 4's
LVS citation — stays `"unchecked"`, for the reason "Item 4 is `met` twice"
above already documents. A `met` supply-spec run is necessary for item 11's
digital column; it was never sufficient on its own.

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
  wrong rather than merely imprecise. **Not applicable yet** — item 7 is
  `unmet` with no citation. Note that this repo's own extraction reports
  already carry an `unbiased_pmos_body_nets` field, so a future item-7 claim
  has to read it and state what it says.
- **Item 4's `power_connectivity` and `body_verification`** — `null` on the
  analog citation and `"unchecked"` on the digital one, with `klt`'s own
  stated reason for each. Neither partition's LVS verdict includes a verified
  body-tie or a `"match"` power-connectivity result; both are disclosed above
  rather than folded into the word "match".

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

## What would move the needle

In dependency order, not effort order:

1. ~~**Re-commit the digital partition's DRC and LVS as full `klt`
   envelopes.**~~ **Done** —
   [#273](https://github.com/2AMLogic/gf180-trng/issues/273) moved items 3
   and 4 from 2 of 4 to 4 of 4, and the verdict of record from 3 of 22 to 5
   of 22, with no new verification work: only a different serialization of
   runs that had already happened.
2. **Re-run the analog LVS under a settled producer pin**, so `4.analog`'s
   citation can carry a `provenance.input.content_hash` pin and a real
   `power_connectivity`/`body_verification` verdict instead of `null`.
   Tracked as [#281](https://github.com/2AMLogic/gf180-trng/issues/281).
   This does **not** move the met count — item 4 is already `met` on both
   partitions — it strengthens a citation that is currently the only unpinned
   one in the manifest. It is blocked on DR-0026, which is `Proposed`, and
   whose zero-verdict-change measurement #281 shows has gone stale.
3. **Emit corner evidence as `klt sim`/`klt sta` envelopes** alongside this
   repo's Markdown records. Item 5's *design* gap (four ratified rows still
   missed) is real and separate, but today the item cannot even be graded.
4. **A `klt yield` report** over the Monte Carlo campaign that already exists
   (item 6), and **a `klt pex` report** over the post-layout extraction that
   already exists (item 7).
5. ~~**A `klt erc` supply spec and run**~~ **Done, in two steps** — the spec
   and report first landed via [#268](https://github.com/2AMLogic/gf180-trng/issues/268),
   and [#276](https://github.com/2AMLogic/gf180-trng/issues/276) declared
   the spec's `ties[]` once klayout-tools#2186 shipped, so `erc.missing_tie`
   is now computed and zero. Item 11 still does not read `met` — see "Item
   11's `ties[]`" above for the two remaining gaps (no `11.analog`/
   `11.digital` citation in `signoff/block-manifest.json` yet, and the
   digital column's `power_connectivity.status: "match"` requirement, which
   stays `"unchecked"`).

Items 1, 2, 9 and 10 need nothing built — only an honest artifact to cite, if
one ever exists.

Items 1 and 2 are tracked here as part of this block's own evidence-format
gap; item 11's remaining gaps are tracked under
[#124](https://github.com/2AMLogic/gf180-trng/issues/124), this repo's
general gap-to-T1 tracker. Tool-side friction this surfaces is filed at
`2AMLogic/klayout-tools`, per this repo's friction protocol (`CLAUDE.md`) —
so far klayout-tools#2342.
