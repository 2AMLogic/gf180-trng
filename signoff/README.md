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

**Today: `tier: null`, T1 3 of 22 items met.** A `mixed-signal` block is
graded twice over, once per partition, so the eleven-item checklist renders
22 rows. The three met are item 3 (DRC) and item 4 (LVS) on the analog
partition, and item 8 (characterization report) on the digital partition.
That is the honest state of the block; the rest of this file is why each of
the other nineteen reads the way it does.

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
   for item 3's `drc` citation and `null` for item 4's `lvs` and item 8's
   `generic` ones. `check.py` covers the whole set regardless of envelope
   kind. Edit `layout/blocks/combiner_sampler/combiner_sampler.gds` or
   `sim/characterization-digital-sta-area-power.md` without re-running the
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
| 3 DRC clean | **`met`** | `unmet` / `no_evidence` | Analog cites `layout/reports/combiner_sampler.drc.json` (`status: clean`, deck `gf180mcu` identified by content hash). Digital's DRC *did* run clean, but `layout/digital/reports/drc.json` is a reduced summary, not the `klt drc` envelope — see "Evidence this repo has but cannot cite". |
| 4 LVS clean | **`met`** | `unmet` / `no_evidence` | Analog cites `layout/reports/combiner_sampler.lvs.json` (`status: match`). Same digital story as item 3: `layout/digital/reports/lvs.json` is a summary, not an envelope. See "Item 4 is cited without a pin" for the disclosures this verdict does *not* carry. |
| 5 Corner verification | `unmet` / `no_evidence` | `unmet` / `no_evidence` | This block's largest *real* gap, and an evidence-format gap on top of it. README's ratified spec table still misses four rows (raw rate, raw min-entropy, area, power). Separately, item 5 accepts only a `klt sim` envelope (analog) or `klt sta`/`klt functional-verification`/`klt sim` (digital); this repo's ~950 corner records under `sim/records/` are its own Markdown format, and the fifteen-corner digital STA sweep is likewise recorded as Markdown. Nothing here is gradeable yet. |
| 6 Monte Carlo | `unmet` / `no_evidence` | `unmet` / `no_evidence` | `sim/characterization-worst-corner-and-mc-mismatch.md` is a real Monte Carlo campaign with recorded seeds, sample counts, two PVT points and a deterministic negative control. Item 6 accepts only a `klt yield` report, and none exists. |
| 7 Post-layout | `unmet` / `no_evidence` | `unmet` / `no_evidence` | Real post-layout work exists on both sides — device- *and* routing-level parasitic re-simulation (`sim/characterization-post-layout-extracted.md`, issues #17/#217/#232) and an SDF-annotated post-route gate-level functional run (`sim/tb/trng-top-post-route/`, #147). Item 7 accepts only a `klt pex` envelope (analog) or `klt pex`/an SDF-annotated `klt functional-verification` envelope (digital), and neither exists in envelope form: `layout/pex/build.py` drives `klt extract --parasitics` and composes the result itself rather than emitting a `klt pex` report. |
| 8 Characterization | `unmet` / `no_evidence` | **`met`** | Digital cites `evidence/characterization-digital.generic.json`, wrapping `sim/characterization-digital-sta-area-power.md`. Analog is uncited — see below. |
| 9 Testbenches shipped | `unmet` / `no_evidence` | `unmet` / `no_evidence` | 64+ testbenches under `sim/tb/`, each with a documented cold-start invocation, and the PDK revision pinned in README and `pdk-nightly.yml`. Uncited on purpose. |
| 10 Repo hygiene | `unmet` / `no_evidence` | `unmet` / `no_evidence` | README, spec table, reproduction instructions, Apache-2.0 licence and green CI all exist. Uncited on purpose. |
| 11 Power delivery | `unmet` / `no_evidence` | `unmet` / `no_evidence` | No `klt erc` supply spec and no ERC report exist anywhere in this repo. Tracked as [#268](https://github.com/2AMLogic/gf180-trng/issues/268). The item has a row here, `unmet`, rather than being silently absent: it was added to the checklist on 2026-09-17 (klayout-tools#2025) and invalidated every hand-read that predates it. |

### Item 3 is `met` — and here are its coverage gaps

`design-evidence-tiers.md` requires item 3's deck coverage gaps to be
enumerated *in the claim*, and is explicit that this is claimant-enforced:
`klt signoff` grades item 3 on `status: "clean"` alone, so a `met` verdict is
**not** evidence that the gaps were disclosed. Since klayout-tools#2002 the
grader *reports* them on the citation, so these are quoted from
`records/t1-tier-report.json`'s own `items[].citation.coverage`, not from
memory:

- `coverage.layers_in_stream_without_rules`: `34/10`, `36/10` — layers drawn
  in this stream that the deck has no rule for.
- `coverage.rules_skipped` (19): `bjt.separation.comp.1`, `comp.space.mv.1`,
  `comp.width.mv.1`, `metal3.enclosing.via3.1`, `metal4.enclosing.via3.1`,
  `metal4.enclosing.via4.1`, `metal5.enclosing.via4.1`, `metal5.space.1`,
  `metal5.width.1`, `metaltop.space.1`, `metaltop.width.1`,
  `mim.enclosing.fusetop.1`, `mim.enclosing.via4.1`, `mim.space.1`,
  `pad.enclosing.metal5.1`, `via3.space.1`, `via3.width.1`, `via4.space.1`,
  `via4.width.1`.
- `coverage.deck_scope` — the chapters of the gf180mcu DRM this deck
  transcribes at all: 7.4 Nwell, 7.5 Comp, 7.7 Poly2, 7.12 Contact, 7.13
  Metaln, 7.14 Vian, 7.15 MetalTop, 9.1 Bond Pad, 10.4.2 MIM Option B, 10.7
  DRC_BJT Mark Layer.

"DRC clean" here means clean *inside that scope*. Nothing above is a claim
about MIM capacitors, bond pads, or any rule class the deck does not carry.

**One citation, nine clean reports.** `klt signoff` takes one evidence entry
per item, so the manifest cites the most complex analog cell. Every other
analog DRC report committed here also reads `status: clean` with
`violation_count: 0`: `ro_buf`, `ro_nand2`, `ro_nand2_ring2`, `ro_ring11`,
`ro_ring11_ring2`, `ro_stage`, `ro_stage_ring2`, `sampler_dff`, `xor2`
(`layout/reports/*.drc.json`), plus the composed whole-block run in
`layout/floorplan/reports/floorplan.drc.json`. The deliberately-failing
fixtures `trng_tc_inv_drcbad`/`trng_tc_inv_lvsbad` are negative controls for
the flow, not evidence about the design.

### Item 4 is `met` — and it is cited without a pin

Two disclosures travel with this verdict.

**It carries no freshness pin, and that is a property of the evidence, not a
shortcut.** Every other citation in the manifest pins a `content_hash`.
Item 4's cannot: `klt lvs` only began populating
`provenance.input.content_hash` in klayout-tools#1969, and this repo's
committed LVS reports were produced by klt 0.4.0, which leaves it `null`.
Pinning a hash against a `null` would render the item `stale_evidence`, which
would be a *false* negative. The freshness claim is still enforced here — the
same digest is recorded as `environment.layout_sha256`, and `check.py`
re-hashes `layout/blocks/combiner_sampler/combiner_sampler.gds` against it on
every run — it is simply enforced by this repo rather than by `klt signoff`'s
own staleness gate. Re-running LVS under a current `klt` would let the pin
move into the manifest where it belongs.

**What the compare did and did not verify.** `power_connectivity` is `null`
and `body_verification` is `null` in this envelope: klt 0.4.0 predates both
blocks, so the power/ground half of the compare was never run and the body
ties were never verified. `design-evidence-tiers.md` is explicit that
`"unchecked"` is not `"verified"`, and `null` is weaker still. The report also
carries `mismatch_count: 2` with `error_count: 0` —
`category_counts: {"topology": 1, "device.body_unverified": 1}` — the same
warnings-only shape every other analog region's compare carries. Those are
warnings, and they are listed here rather than folded into the word "match".

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

- **Item 3's DRC coverage** — quoted in full above, from the citation, not
  from memory.
- **Item 7's `body_bias`** is *reported* by `klt signoff` and never graded: a
  `klt pex` citation whose `body_bias.status` is `"unbiased"` still renders
  `met`, and a re-simulation of an unbiased extracted netlist is physically
  wrong rather than merely imprecise. **Not applicable yet** — item 7 is
  `unmet` with no citation. Note that this repo's own extraction reports
  already carry an `unbiased_pmos_body_nets` field, so a future item-7 claim
  has to read it and state what it says.
- **Item 4's `power_connectivity` and `body_verification`** — both `null` in
  the cited envelope, disclosed above.

## Evidence this repo has but cannot cite

Recording these separately from the gaps above, because they are a different
problem with a different fix:

- **The digital partition's DRC and LVS envelopes are not committed as
  envelopes.** `layout/digital/reports/drc.json` and `lvs.json` are reduced
  summaries (`status`, counts, deck name) with no `schema_version`, no
  `violations`/`mismatches` array and no `provenance` block, so
  `klt signoff` cannot classify them at all. The underlying runs were clean
  and matched; the artifacts just were not kept in gradeable form. Items 3 and
  4 on the digital partition are one re-run away, tracked as
  [#273](https://github.com/2AMLogic/gf180-trng/issues/273).
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

1. **Re-commit the digital partition's DRC and LVS as full `klt` envelopes.**
   That alone moves items 3 and 4 from 2 of 4 to 4 of 4, and it produces no
   new verification work — only a different serialization of runs that
   already happened. Tracked as
   [#273](https://github.com/2AMLogic/gf180-trng/issues/273).
2. **Re-run the analog LVS under a current `klt`**, so item 4's citation can
   carry a `provenance.input.content_hash` pin and a real
   `power_connectivity`/`body_verification` verdict instead of `null`. Same
   issue, [#273](https://github.com/2AMLogic/gf180-trng/issues/273).
3. **Emit corner evidence as `klt sim`/`klt sta` envelopes** alongside this
   repo's Markdown records. Item 5's *design* gap (four ratified rows still
   missed) is real and separate, but today the item cannot even be graded.
4. **A `klt yield` report** over the Monte Carlo campaign that already exists
   (item 6), and **a `klt pex` report** over the post-layout extraction that
   already exists (item 7).
5. **A `klt erc` supply spec and run** (item 11, tracked as #268).

Items 1, 2, 9 and 10 need nothing built — only an honest artifact to cite, if
one ever exists.

Items 1 and 2 are tracked here as part of this block's own evidence-format
gap; item 11 is tracked as #268. Tool-side friction this surfaces is filed at
`2AMLogic/klayout-tools`, per this repo's friction protocol (`CLAUDE.md`) —
so far klayout-tools#2342.
