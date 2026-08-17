# `layout/` — DRC and LVS

This directory holds the layout verification flow: [klayout-tools][klt]
(`klt`) driving gf180mcu DRC and LVS, and the fixtures that prove the flow
catches what it is supposed to catch.

**The cells in this directory are still overwhelmingly flow bring-up, not
the design.** `layout/testcells/` is a trivial CMOS inverter and two
deliberately broken copies of it, drawn to demonstrate the DRC/LVS flow —
nothing in `layout/reports/` under those three names should be read as a
statement about the TRNG.

**[`layout/floorplan/`](floorplan/), [`layout/cells/`](cells/),
[`layout/rings/`](rings/), [`layout/blocks/`](blocks/) and
[`layout/digital/`](digital/) are the five things here that are about the
TRNG.** The first four draw the entropy source's analog and mixed-signal
cells by hand, one at a time; `digital/` is the other kind of layout
problem entirely — the conditioner, health tests and interface synthesize to
2500-odd standard cells, so they are placed and routed by tool ([#111][gf111])
rather than drawn, and that directory's own README says exactly what its
routed result does and does not establish (it has a DEF and an as-built
netlist; it does not yet have a committed GDS, a DRC verdict or any power
delivery). `floorplan/` is the entropy source's
isolation rationale (#16) and the floorplan abstract that carries it: four
guarded regions, real generated guard rings, DRC'd as one stream, with an
area rollup against the `< 0.05 mm²` row. As of #110 and #135,
`ring1`/`ring2` and `combiner_sampler` all carry real, placed,
LVS-verified content (`combiner_sampler`'s real, LVS-matching assembled
block landed under `blocks/` in #134 — extended to include both `ro_buf`
instances by #151 — and #135, resolved by PR #139, sized its guarded region
from that block's own real bounding box and placed it there, re-measured
from the assembled geometry on every run); the `digital` *region* is still
*empty* — `layout/digital/`'s routed result is not placed inside it, and
nothing else puts content there either — so `floorplan/`
remains a floorplan and not a full layout, and
[`floorplan/README.md`](floorplan/README.md) is explicit about what a
clean-relative-to-baseline DRC result over it does and does not mean.
**Every cell here is DRC-clean again as of #162.** Pinning `klt` to a build
with the gf180mcu digital flow, `klt pex`, and `klt yield` (#142) also
pulled in a more complete gf180mcu DRC deck — Via1-Via4 width/space rules
(klayout-tools#546/#564) and the conductor-over-cut enclosures (#551) among
others — which flagged real violations on `ro_nand2`, `ro_nand2_ring2`,
`xor2`, `sampler_dff`, `ro_ring11`, `ro_ring11_ring2`, and
`combiner_sampler` that the previously-pinned PyPI release's deck never
checked for. #162 fixed the **geometry**, not the expectations: every via
in this tree is now drawn at the DRM's own fixed 0.26 µm size instead of a
contact-sized 0.22 µm, and every conductor that carries a via or a contact
runs past that cut instead of stopping flush with its edge. No rule was
waived and no expectation was relaxed — `layout/verify.py`'s `EXPECTATIONS`
table still declares all ten cells DRC-`clean` with empty `rule_counts`,
and passes. LVS match/mismatch verdicts were unaffected throughout, before
and after.
`cells/` (#106) is where drawn design cells land, one at a time, each
DRC-clean and LVS-matching before the next is started —
[`cells/README.md`](cells/README.md) says which cells are drawn and which of
the block's many remaining cells are not, and
["What has layout, and what does not"](#what-has-layout-and-what-does-not)
below is the one-table version of the same answer, indexed by netlist
subcircuit. `rings/` (#110) and `blocks/`
(#134, #151) are where those individually-verified cells get *assembled*:
`rings/` holds `ro_ring11` (ten `ro_stage` plus one `ro_nand2`, at both ring
sizings), `blocks/` holds `combiner_sampler` (two `ro_buf` plus one `xor2`
plus four `sampler_dff`) — see [`rings/README.md`](rings/README.md) and
[`blocks/README.md`](blocks/README.md) for scope, and
[`floorplan/README.md`](floorplan/README.md#placement--issue-110) for how
`ring1`/`ring2`'s own assembled blocks are placed inside `floorplan/`'s own
guarded regions, and
[the same file's #135 section](floorplan/README.md#placement--issue-135-combiner_sampler)
for `combiner_sampler`'s own placement, done the same way.

The flow is stood up before the layout it will check, for the same reason
`sim/` was stood up before the first result: a verification flow that first
runs on the thing you care about is a flow you cannot distinguish from a
flow that always says "clean".

---

## The one command

```sh
python3 layout/verify.py
```

It rebuilds the fixtures, runs DRC + extraction + LVS over each of them,
checks every result against a declared expectation, and confirms the
committed reports still match. It prints `PASS` and exits 0 only if all
three hold.

```
python3 layout/verify.py                 # run and check (exit 1 on any failure)
python3 layout/verify.py --write         # ... and refresh layout/reports/
python3 layout/verify.py --require-tools # fail rather than skip if klt/PDK absent
python3 layout/verify.py --list          # print the fixture/expectation table
```

Without `--require-tools` the script **skips with exit 0** when `klt` or the
PDK is missing, so a checkout without the toolchain is not a failing
checkout. This mirrors `sim/selftest.sh`, and it has the same caveat: a skip
is not a pass. `npm run check:layout` is the skipping form; `npm run
check:all` runs the demanding form.

### Prerequisites

| | |
|---|---|
| `klt` | [klayout-tools][klt] on `PATH`, pinned to the git ref CI installs — see ["Pinning the tool"](#pinning-the-tool) below. `pipx install klayout-tools` / `uv tool install klayout-tools` installs the latest PyPI release instead, which as of `v0.2.0` lacks the gf180mcu digital synthesize/place-and-route flow, `klt pex`, and `klt yield` (#142). Brings its own KLayout Python module — no GUI, no Qt, no standalone `klayout` binary. |
| PDK | A gf180mcu install, found through **`sim/harness/pdk.py`** — the same resolver the simulations use, so a DRC run and a SPICE run cannot silently disagree about which PDK is installed. Run `python3 sim/run_corners.py --check-env` for install instructions. |

The PDK variant is whatever `sim/pdk.json` pins (`gf180mcuD` today).
`klt`'s DRC and extraction decks are per-*family* rather than per-variant,
so the variant selects the install, not the rules.

### Pinning the tool

**`klt --version` does not identify a `klt` build.** It read `0.1.0` for every
build of klayout-tools for a long time, including installs taken straight off
the tip of its main branch — which is what both commands above give you. Two
installs reporting the same string can be months of development apart.

**Releasing `0.2.0` did not fix that.** Verified on 2026-08-16, on one
machine, on the same day: a `pip install klayout-tools==0.2.0` and a
`uv tool install` from `git+…@373181f` both report `klt 0.2.0` from
`klt --version` *and* from `provenance.klt_version`, yet disagree on
`provenance.deck.content_hash` (`sha256:1256c45b…` vs `sha256:457480f1…`) and
on the verdict for one unchanged committed stream —
`layout/cells/ro_nand2/ro_nand2.gds` **as committed that day** is `clean`
under the released deck and reports five `metal1.enclosing.contact.1`
violations under the git build's stricter one. (That geometry has since been
redrawn — #162 — so the same experiment run against today's stream is clean
under both decks; the point the two decks disagreed on stands as recorded.)
The git build's extra rules are legitimate; the problem is that
nothing in the version string says which deck generation ran. Re-filed as
fresh evidence on [klayout-tools#306][kt306]. **Consequence for anyone
reproducing this directory's reports:** `.github/workflows/pdk-nightly.yml`
pins `klayout-tools` to an explicit git ref/SHA rather than a PyPI release —
the latest release, `v0.2.0` (2026-08-04), predates the gf180mcu digital
synthesize/place-and-route flow, `klt pex`, and `klt yield` (#142) — so that
pinned commit, not any released wheel, is the reference this directory's
committed reports are written against. A locally-installed build from a
different commit (including a future PyPI release, once one is cut past
`v0.2.0`) may resolve a different deck; check `provenance.deck.content_hash`
before concluding the geometry moved.

This is not hypothetical. On 2026-08-02 the reports committed here stopped
matching a fresh run on the same machine, with `klt --version` and the
KLayout engine version (`0.30.10`) both unchanged. `klt` had gained new
checks and a richer report envelope, and nothing recorded here could say so
(#73). So:

- `layout/reports/environment.json` records **`klt_origin`** — the upstream
  URL and commit the installed `klt` was built from, read from the
  distribution's own `direct_url.json`. That is the field to quote when
  citing a result, not `klt`. It is best effort: an install from a released
  wheel has no commit to report and records `null`, which means *not
  recorded*, never *unchanged*.
- Every `*.drc.json` / `*.extract.json` / `*.lvs.json` carries `klt`'s own
  `provenance` block, including a content hash of the deck that produced it,
  and those **are** compared against the committed copy. A deck edit now
  fails the report check by name instead of surfacing as a mystery change in
  a rule count.
- `python3 layout/verify.py` prints the commit it ran and each LVS report's
  KLayout `engine_version`, so "did the tool move under me?" is answerable
  from a plain run.

**The flip side of "compare content, not the machine" is that the machine
itself must not count as content.** Two developers (or a developer and CI)
running the identical committed `.gds` through the identical `klt` build can
still get PDK install paths that disagree by construction —
`/Users/<you>/.volare` locally, `~/.ciel` in `pdk-nightly.yml` — with nothing
about the DRC/LVS *result* having moved. `layout/verify.py`'s `_stable()`
(the function `compare_reports()` runs both sides through before diffing)
drops exactly the fields that record *where a PDK install happened to sit on
this filesystem* — `pdk.root`, `provenance.pdk.source`, and the pre-existing
`environment.engine_version` — and nothing else; every content hash, verdict,
count, and the PDK `variant`/`version` actually targeted stay in the
comparison. See `_stable()`'s own docstring for the full, field-by-field
rationale and `layout/tests/test_verify.py` for the regression coverage (a
case per dropped field proving it doesn't matter, and a case per kept field
proving it still does) — issue #148, filed after the nightly job's freshness
check spent eight straight days red on exactly this false positive.

To reproduce a committed report exactly, install the commit
`environment.json` names:

```sh
uv tool install --force \
    "klayout-tools @ git+https://github.com/2AMLogic/klayout-tools@<commit>"
```

---

## What is here

```
layout/
  README.md                  this document
  verify.py                  the flow driver + the expectations that make it a test
  tests/
    test_verify.py            unit tests for verify.py's freshness-gate comparison (#148); no klt/PDK needed
  floorplan/
    README.md                the entropy-source isolation rationale (#16)
    floorplan.py             builds the floorplan abstract, DRCs it, prices it
    trng_floorplan.gds       the composed abstract (timestamps normalised)
    reports/area.json        the area rollup vs the < 0.05 mm^2 row
    reports/compose.json     the gen-compose request + response
    reports/floorplan.drc.json  verbatim `klt drc` output for the abstract
  testcells/
    gdsii.py                 minimal stdlib GDSII writer (see "Tool friction" #1)
    build.py                 fixture geometry; `--check` guards the committed .gds
    trng_tc_inv.gds          known-good inverter
    trng_tc_inv_drcbad.gds   ... with two deliberate geometry defects
    trng_tc_inv_lvsbad.gds   ... with a deliberate connectivity defect
    trng_tc_inv.spice        hand-written LVS reference (schematic side)
  cells/
    README.md                 scope: which design cells are drawn, which are deferred (#106)
    ro_stage/
      build.py                 hand-drawn geometry + the geometric reasoning behind it
      ro_stage.gds              the drawn cell (timestamps normalised)
      ro_stage.spice            hand-written LVS reference (schematic side)
    ro_stage_ring2/
      build.py                 ring2 sizing (wstv=0.240u) -- independently drawn, see cells/README.md
      ro_stage_ring2.gds        the drawn cell (timestamps normalised)
      ro_stage_ring2.spice      hand-written LVS reference (schematic side)
    ro_nand2/
      build.py                 the ring's one stoppable stage -- hand-drawn geometry + why
      ro_nand2.gds              the drawn cell (timestamps normalised)
      ro_nand2.spice            hand-written LVS reference (schematic side)
    ro_buf/
      build.py                 DR-0018's per-ring output buffer -- hand-drawn geometry + why
      ro_buf.gds                the drawn cell (timestamps normalised)
      ro_buf.spice              hand-written LVS reference (schematic side)
  rings/
    README.md                 scope: which blocks are assembled, which are deferred (#110)
    ro_ring11/
      build.py                 assembles ro_ring11 (ring1 sizing) from drawn cells + hand-routed wiring
      ro_ring11.gds              the assembled block (timestamps normalised)
      ro_ring11.spice            hand-written LVS reference (mechanically expanded, see the file's own header)
  blocks/
    README.md                 scope: which non-ring blocks are assembled (#134)
    combiner_sampler/
      build.py                 assembles combiner_sampler (2x ro_buf + xor2 + 4x sampler_dff) from drawn cells + hand-routed wiring
      combiner_sampler.gds       the assembled block (timestamps normalised)
      combiner_sampler.spice     hand-written LVS reference (mechanically expanded, see the file's own header)
  reports/
    environment.json         klt version, PDK provenance, platform
    <fixture>.drc.json       verbatim `klt drc` output
    <fixture>.extract.json   verbatim `klt extract` output
    <fixture>.extracted.spice   the layout-derived netlist
    <fixture>.lvs-request.json  the exact request `klt lvs` was handed
    <fixture>.lvs.json       verbatim `klt lvs` output
```

---

## What has layout, and what does not

The table below is the standing answer to "which of the design's devices are
drawn?", so that a reader does not have to reconstruct it from four
directories. **The reference is the shipped top-level netlist,
`design/trng_top.spice`** — a subcircuit that is not instantiated there is not
part of what this block ships, whatever else exists for it in `design/`.

| netlist subcircuit | in shipped `trng_top.spice`? | drawn cell | assembled into |
|---|---|---|---|
| `ro_stage`, `ro_nand2` (ring1 sizing) | yes | [`cells/ro_stage/`](cells/ro_stage/), [`cells/ro_nand2/`](cells/ro_nand2/) | [`rings/ro_ring11/`](rings/ro_ring11/), placed in `floorplan/`'s `ring1` region (#110) |
| `ro_stage`, `ro_nand2` (ring2 sizing) | yes | [`cells/ro_stage_ring2/`](cells/ro_stage_ring2/), [`cells/ro_nand2_ring2/`](cells/ro_nand2_ring2/) | [`rings/ro_ring11_ring2/`](rings/ro_ring11_ring2/), placed in `floorplan/`'s `ring2` region (#110) |
| `xor2`, `sampler_dff` | yes | [`cells/xor2/`](cells/xor2/), [`cells/sampler_dff/`](cells/sampler_dff/) | [`blocks/combiner_sampler/`](blocks/combiner_sampler/), placed in `floorplan/`'s `combiner_sampler` region (#135) |
| `ro_buf` (×2, `xb1`/`xb2`) | yes | [`cells/ro_buf/`](cells/ro_buf/) (#144) | [`blocks/combiner_sampler/`](blocks/combiner_sampler/) ([#151][gf151], and see below), placed in `floorplan/`'s `combiner_sampler` region (#135) |
| `ro_meta_tap`, `meta_arb`, `meta_inv`, `meta_nand2` | **no** | **none — out of scope**, see below | n/a |
| the digital section (2505 synthesized standard cells) | yes | none, and none is wanted — a P&R problem, not a hand-drawn-cell one ([#111][gf111]): [`digital/`](digital/) routes it | routed DEF + as-built netlist in [`digital/`](digital/); **not** yet placed in `floorplan/`'s `digital` region |

### `ro_buf`: drawn, assembled, and placed

`ro_buf` is drawn and verified as a cell, and both of its instances are priced
into `layout/floorplan/`'s `combiner_sampler` region — that region rather than
either ring's, because DR-0018 runs both buffers off the block supply `vdd`
and never off a ring's own `vddr`. As of [#151][gf151], both instances
(`xb1`/`xb2`) are also placed and wired inside `blocks/combiner_sampler/`,
alongside the combiner and samplers that block already assembled: the
block's own reference netlist (`combiner_sampler.spice`) now declares them,
so they no longer report as `device.unmatched`. `layout/floorplan/
reports/area.json`'s `combiner_sampler` region no longer carries a
`footprint_source.inventoried_but_not_in_assembly` entry for `ro_buf` —
both instances are `shipped: true`, and the region's own guarded footprint
is sized from (and fit-checked against, #135) the assembled block's real
bbox, which now contains them.

### The metastability-hybrid tap is deliberately not drawn

`ro_meta_tap`, `meta_arb`, `meta_inv` and `meta_nand2` have no layout here,
and that is a scope decision rather than an omission. Two reasons, both
checkable:

1. **They are not in the shipped top-level netlist.** The four subcircuits
   appear only in `design/ro_array_core_meta.spice`; `grep` finds zero
   occurrences of any of them in `design/trng_top.spice`,
   `design/ro_array_core.spice` or `design/sampler_core.spice` (verified
   against `main` @ `b8e3825`). Drawing a cell that the block does not
   instantiate would add DRC/LVS evidence about geometry that ships in
   nothing.
2. **[`DR-0011`][dr11] (Accepted) scopes the tap as a stretch item.** Its own
   words: a self-timed metastability hybrid "layered onto the RO core, never a
   free-standing source, and never gating the core's own output", carried with
   "no entropy, histogram, or calibration-viability claim", and explicitly
   *not* a rate-row contributor. DR-0011 further records that promoting the
   tap out of stretch status "requires reconciling +187 µW" against the
   `Power` row. A layout claim is a claim about what the block ships; making
   one for a stretch hook would overstate the tap's status in exactly the
   direction DR-0011 exists to prevent.

If the tap is ever promoted out of stretch status — which is a decision-record
change, not a layout decision — drawing these four cells to the same bar as
everything in [`cells/`](cells/) becomes in scope, and this section is the
thing to delete.

---

## The fixtures, and what each one proves

All three streams contain the same top cell name, `trng_tc_inv` — they are
three drawings of one cell, and the variant lives in the file name. (That is
load-bearing for LVS diagnosis, not cosmetic; see Tool friction #2.)

| fixture | DRC | LVS | what a passing run proves |
|---|---|---|---|
| `trng_tc_inv` | clean | match, 0 errors | the flow accepts a correct cell — no false positives from the deck, the layer numbering, or the extraction |
| `trng_tc_inv_drcbad` | `metal1.width.1` ×1, `metal1.space.1` ×1 | not run | DRC actually fires, and names the *specific* rules — not merely "some error" |
| `trng_tc_inv_lvsbad` | clean | mismatch, 2 errors (`net.unmatched` ×1, `device.unmatched` ×1) | LVS catches a defect DRC structurally cannot see |

Every LVS run — including the known-good one — also reports two categories
at `severity: "warning"`: `device.body_unverified` ×2 and `topology` ×1.
They describe the *deck*, not the fixture, so they are identical on all
three; ["Warnings every run carries"](#warnings-every-run-carries) below says
what each one means. `verify.py` pins them by exact count like everything
else, and separately pins the number of `severity: "error"` mismatches — the
column above — so that carrying two known warnings cannot quietly absorb a
future error arriving in the same category.

The third row is the interesting one. `trng_tc_inv_lvsbad` is the good cell
with its output strap cut in two: the NMOS drain and the PMOS drain end up
on different nets, an open circuit. Every geometric rule is satisfied — the
gap is 1.64 µm against a 0.23 µm Metal1 minimum — so DRC reports clean and
is *right* to. That is exactly the class of defect a DRC-only flow ships.

The expectations are compared for **exact equality**, not "at least". A
known-bad fixture that starts reporting a third rule has drifted, and its
committed report no longer says what this document says it says.

`layout/verify.py` was checked against its own failure modes during
bring-up: a corrupted `.gds` fails the staleness guard, a wrong expectation
fails the flow stage, and a missing tool skips (or fails, under
`--require-tools`) rather than passing vacuously.

---

## Running the tools by hand

`verify.py` is a convenience, not a moat. Every stage is a plain `klt`
invocation, runnable from the repo root:

```sh
# DRC.  Exit 0 = clean, 3 = violations found, 1 = could not run.
klt drc layout/testcells/trng_tc_inv.gds --deck gf180mcu --format json

# Extraction (layout -> schematic-equivalent SPICE, no parasitics).
klt extract layout/testcells/trng_tc_inv.gds \
    --deck gf180mcu --pdk gf180mcuD --top trng_tc_inv \
    -o layout/reports/trng_tc_inv.extracted.spice --format json

# LVS.  Exit 0 = match, 3 = mismatch, 1 = could not run.
klt lvs layout/reports/trng_tc_inv.lvs-request.json --format json
```

The committed `*.lvs-request.json` files are the full LVS invocation: they
name the layout stream, the extraction deck, the reference netlist, and the
top cell on each side. Paths inside a request resolve **relative to the
request file**, so a request moved to another directory means something
different.

---

## What the curated decks do and do not check

`klt`'s gf180mcu decks are a curated subset, not a sign-off deck, and the
reports here inherit exactly that scope. Stating the limits is the point:
an unstated limit is a defect.

**DRC** checks minimum widths, spacings, contact enclosures, and Nwell
enclosure of Comp. Read the scope off the report rather than off this
paragraph: every `*.drc.json` here carries a `coverage` block naming the
deck's layers, the layers it actually checked (Comp, Nwell, Poly2, Contact,
Metal1 — the only ones these fixtures draw), and every rule it skipped for
want of a layer. These fixtures skip eleven, all upper-metal, MiM, or BJT.
The deck does **not** cover implant layers, antenna rules, density,
latch-up, or any context-dependent rule needing connectivity (its own
comments flag several rules as approximations for exactly that reason — e.g.
Nwell spacing uses the equipotential value because the checker has no net
information). It is also not the PDK's own shipped deck, and cannot yet be
pointed at one ([klayout-tools#173][kt173]).

**Extraction** extracts no parasitics, and recognises the device classes the
deck declares — echoed into every `*.extract.json` and `*.lvs.json` as
`device_classes`, currently `nfet`, `pfet`, `bjt`, a MiM capacitor, and a
poly resistor. These fixtures contain MOS only, so the other three classes
are declared and unused; that is where the `topology` warning below comes
from. The extracted netlist is emitted as PDK subcircuit calls
(`X$1 … nfet_03v3`) rather than primitive `M` cards; the hand-written
reference still uses `M` cards with the generic `nfet`/`pfet` names, and
`klt lvs` reconciles the two — so the reference stays a statement about the
circuit rather than about the extractor's output format.

**Bulk terminals** are approximated, and the fixtures' reference netlist
says so explicitly:

- NMOS bulk is the deck's substrate global, `vsubs`. No substrate tap is
  extracted.
- PMOS bulk is a **floating net**. gf180mcu draws well taps on the same
  `Comp` layer as transistor active, so the deck deliberately does not tie
  an Nwell to the contacts inside it (doing so would short every device in
  the well together). The well therefore appears as an unnamed net with one
  connection.

The fixtures are drawn on the curated-deck layer subset only. Implant
(Nplus/Pplus) and the rest of the sign-off layer set are absent: adding them
would change no result these decks produce, and drawing them would imply a
fab-readiness these cells do not have.

### Warnings every run carries

`klt lvs` states two of the limits above per run rather than leaving them to
this document. Both arrive at `severity: "warning"`, both appear on all
three fixtures because both are properties of the deck, and neither changes
a verdict — `trng_tc_inv` is still `match` and `trng_tc_inv_lvsbad` is still
`mismatch`.

| category | count | what it says |
|---|---|---|
| `device.body_unverified` | 2 | One per MOS. Each device's body terminal was compared against a net the deck synthesized — `vsubs` for the NMOS, an anonymous well net for the PMOS — rather than a real schematic net. That terminal was therefore **not** verified. This is the bulk-terminal approximation above, restated by the tool. |
| `topology` | 1 | A device class the deck declares has no counterpart on the reference side *and* zero extracted devices. The tool's own text: "not a real topology mismatch". |

They are pinned in `EXPECTATIONS` at their exact counts rather than filtered
out, because "the tool says two body terminals are unverified" is a claim
that should fail loudly the day it becomes three. And because a warning
count alone cannot distinguish a disclosure from a finding, `verify.py` also
pins the number of `severity: "error"` mismatches per fixture: 0 for the
known-good cell, 2 for the known-bad one.

Both categories appeared on 2026-08-02 with every version string this repo
recorded unchanged, which is what prompted [Pinning the tool](#pinning-the-tool)
above and the upstream note in
[klayout-tools#306][kt306]. The `device.body_unverified` check is
[klayout-tools#281][kt281]; the `topology` entry follows from the deck
declaring device classes it did not previously have.

**Therefore: a clean report from this flow is not tapeout sign-off**, and
must never be cited as one. It is evidence that a specific, enumerated set
of rules passed on a specific stream, under the specific tool build recorded
as `klt_origin` in `layout/reports/environment.json` — and, for two MOS body
terminals, evidence the tool explicitly declines to give.

---

## Reports: regenerated, not append-only

`sim/records/` is append-only because a simulation result is a measurement:
it has a corner, it may have seeds, and a re-run is a new observation. A DRC
or LVS report is not a measurement. It is a deterministic function of a
committed stream, a deck, and a tool version — re-run it and you get the
same bytes back.

So the convention here is different, deliberately:

- `layout/reports/` holds **golden output**, regenerated with
  `python3 layout/verify.py --write`.
- `python3 layout/verify.py` (no flag) regenerates in memory and fails if
  the committed reports no longer match, so a report cannot silently rot.
  The comparison ignores exactly one field, each LVS report's
  `environment.engine_version`, which moves on a KLayout upgrade without any
  verdict changing. The rest of that block is `layout_sha256` /
  `reference_sha256` — hashes of the exact bytes LVS compared, a function of
  the committed fixtures and not of the machine — and is compared, as is
  `klt`'s `provenance` block including its deck content hash.

The reports are the tools' own output, with exactly one field restated. The
flow always extracts into the git-ignored scratch dir `layout/.work/`, so
that a check run cannot overwrite a committed artefact — and `klt extract`
echoes that `-o` path back as `netlist_path`. Recorded literally, every
committed `*.extract.json` would name a file absent from a fresh checkout,
so the committed copy names the netlist committed beside it instead. The
tool-emitted `netlist_sha256` next to it is compared unmodified, and the
extracted netlist is byte-compared, so the restated path cannot mask a
change. Nothing else in any report is rewritten.
- `python3 layout/testcells/build.py --check` rebuilds every `.gds` from
  `build.py` and byte-compares it, so a geometry edit that was not
  regenerated fails before anything downstream is trusted. (The GDSII writer
  zeroes every timestamp field for exactly this reason.)

This is a rule for *this* directory's flow fixtures. A real design cell has
now entered the flow (`layout/cells/ro_stage/`, #106) — its reports keep the
same "regenerated, not append-only" convention as everything above, as the
default this document already inherits, rather than a considered choice for
a claim the spec leans on. Whether a design cell's DRC/LVS-clean status
should instead be recorded as an append-only record under `sim/records/`'s
rules — or something equivalent — is still the open decision this paragraph
already flagged, now with a live cell to decide it about rather than a
hypothetical one; it belongs in a decision record, not a default inherited
by accident.

---

## Adding a cell to the flow

1. Put the stream under `layout/` and its schematic-side reference netlist
   next to it. Give the layout's **top cell the same name** as the
   reference's `.SUBCKT` (Tool friction #2 — no longer required, still
   advisable). A real design cell (as opposed to a flow-bringup fixture)
   lands under `layout/cells/<cell>/`, not `layout/testcells/` — see
   [`cells/README.md`](cells/README.md) and `cells/ro_stage/` for a worked
   example.
2. Add an entry to `EXPECTATIONS` in `layout/verify.py` saying what the flow
   must report — including, for a design cell, `status: clean`,
   `status: match`, and `error_count: 0`. Run it once to learn which
   deck-level warnings it carries, then pin those counts too rather than
   ignoring them. An entry outside `layout/testcells/` needs its own `dir`
   (and, if its top cell is not `trng_tc_inv`, `top`) key — `run_drc`/
   `run_extract`/`lvs_request` all read those with the testcells-shaped
   default, so an entry that omits them still behaves exactly as before.
3. Run `python3 layout/verify.py --write` and commit the reports with the
   layout.

An entry whose expectation is "clean and matching" is a regression guard
from that moment on: if a later edit breaks it, `npm run check:layout` says
so.

Write the LVS reference **by hand**, from the schematic. A reference netlist
copied out of `klt extract` output makes LVS a tautology — it can only ever
report a match, and it would report one for a layout that implements the
wrong circuit.

---

## Tool friction

Per [CLAUDE.md](../CLAUDE.md), friction found while using klayout-tools is
filed generically against the tool, not worked around silently. Bring-up
produced four, all four since fixed upstream. They are kept here because
each one still explains something about the shape of this directory, and
because "we filed it and it got fixed" is the record the friction protocol
exists to produce:

1. **[klayout-tools#230][kt230]** *(fixed — `klt draw`)* — no supported way to emit a deliberately
   rule-violating layout. `klt gen` validates params against PDK minimums
   (correctly), and no other verb writes a stream, so the known-bad half of
   a DRC fixture pair cannot be produced with `klt` at all. That is why
   `layout/testcells/gdsii.py` exists: a ~200-line stdlib GDSII writer,
   entirely outside the toolchain, whose only job is to place rectangles on
   named layers. It should not have to exist.
2. **[klayout-tools#231][kt231]** *(fixed)* — `klt lvs` pairs circuits by name and
   ignores the explicitly-declared `layout.top` / `reference.top`. With
   mismatched names the verdict is still correct but every finding collapses
   to a generic "circuit could not be matched to a counterpart". Naming all
   three fixtures' top cell `trng_tc_inv` was the workaround, and it is why
   `trng_tc_inv_lvsbad.lvs.json` names the broken net instead of shrugging.
   The naming convention is kept — it is good practice regardless — but it
   is no longer load-bearing.
3. **[klayout-tools#232][kt232]** *(fixed)* — `klt lvs` accepts only a request *file*
   path, no inline JSON or stdin, unlike `klt gen --params`.
4. **[klayout-tools#233][kt233]** *(fixed)* — `klt extract -o` errors out when the
   output directory does not exist rather than creating it, which every
   scripted flow hits once on a fresh checkout.

Running the flow since produced a fifth, of a different kind:

5. **[klayout-tools#306][kt306]** *(open)* — a `klt` build cannot be
   identified from anything it reports. `klt --version` and the
   `provenance.klt_version` inside every report both read `0.1.0` for every
   build to date, so a golden-report flow cannot tell "the tool changed"
   from "my inputs changed" — which is exactly the hour this directory lost
   on 2026-08-02. The workaround is `klt_origin` in
   `layout/reports/environment.json`, which reaches around the tool into its
   own install metadata for the commit; a version a downstream flow can pin
   would make that unnecessary.

Building the floorplan abstract in [`floorplan/`](floorplan/) produced three
more, all open and all listed with their workarounds in
[`floorplan/README.md`](floorplan/README.md#tool-friction):
[klayout-tools#320][kt320] (generated streams carry wall-clock GDSII
timestamps, so they cannot be committed and byte-diffed),
[klayout-tools#321][kt321] (`gen-compose` has no explicit x/y placement, so a
two-dimensional floorplan cannot be composed) and
[klayout-tools#322][kt322] (`gen mos_array` rejects widths the tool's own
gf180mcu DRC deck accepts).

[dr11]: ../spec/decision-records/DR-0011-metastability-hybrid-tap-claims-and-scope.md
[gf111]: https://github.com/2AMLogic/gf180-trng/issues/111
[gf151]: https://github.com/2AMLogic/gf180-trng/issues/151
[klt]: https://github.com/2AMLogic/klayout-tools
[kt173]: https://github.com/2AMLogic/klayout-tools/issues/173
[kt230]: https://github.com/2AMLogic/klayout-tools/issues/230
[kt231]: https://github.com/2AMLogic/klayout-tools/issues/231
[kt232]: https://github.com/2AMLogic/klayout-tools/issues/232
[kt233]: https://github.com/2AMLogic/klayout-tools/issues/233
[kt281]: https://github.com/2AMLogic/klayout-tools/issues/281
[kt306]: https://github.com/2AMLogic/klayout-tools/issues/306
[kt320]: https://github.com/2AMLogic/klayout-tools/issues/320
[kt321]: https://github.com/2AMLogic/klayout-tools/issues/321
[kt322]: https://github.com/2AMLogic/klayout-tools/issues/322
