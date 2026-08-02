# `layout/` — DRC and LVS

This directory holds the layout verification flow: [klayout-tools][klt]
(`klt`) driving gf180mcu DRC and LVS, and the fixtures that prove the flow
catches what it is supposed to catch.

**There is no design layout here yet.** The only cells in this directory are
a trivial CMOS inverter and two deliberately broken copies of it. They exist
to demonstrate the flow, and nothing in `layout/reports/` should be read as
a statement about the TRNG.

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
| `klt` | [klayout-tools][klt] on `PATH`. `pipx install klayout-tools` / `uv tool install klayout-tools`. Brings its own KLayout Python module — no GUI, no Qt, no standalone `klayout` binary. |
| PDK | A gf180mcu install, found through **`sim/harness/pdk.py`** — the same resolver the simulations use, so a DRC run and a SPICE run cannot silently disagree about which PDK is installed. Run `python3 sim/run_corners.py --check-env` for install instructions. |

The PDK variant is whatever `sim/pdk.json` pins (`gf180mcuD` today).
`klt`'s DRC and extraction decks are per-*family* rather than per-variant,
so the variant selects the install, not the rules.

---

## What is here

```
layout/
  README.md                  this document
  verify.py                  the flow driver + the expectations that make it a test
  testcells/
    gdsii.py                 minimal stdlib GDSII writer (see "Tool friction" #1)
    build.py                 fixture geometry; `--check` guards the committed .gds
    trng_tc_inv.gds          known-good inverter
    trng_tc_inv_drcbad.gds   ... with two deliberate geometry defects
    trng_tc_inv_lvsbad.gds   ... with a deliberate connectivity defect
    trng_tc_inv.spice        hand-written LVS reference (schematic side)
  reports/
    environment.json         klt version, PDK provenance, platform
    <fixture>.drc.json       verbatim `klt drc` output
    <fixture>.extract.json   verbatim `klt extract` output
    <fixture>.extracted.spice   the layout-derived netlist
    <fixture>.lvs-request.json  the exact request `klt lvs` was handed
    <fixture>.lvs.json       verbatim `klt lvs` output
```

---

## The fixtures, and what each one proves

All three streams contain the same top cell name, `trng_tc_inv` — they are
three drawings of one cell, and the variant lives in the file name. (That is
load-bearing for LVS diagnosis, not cosmetic; see Tool friction #2.)

| fixture | DRC | LVS | what a passing run proves |
|---|---|---|---|
| `trng_tc_inv` | clean | match | the flow accepts a correct cell — no false positives from the deck, the layer numbering, or the extraction |
| `trng_tc_inv_drcbad` | `metal1.width.1` ×1, `metal1.space.1` ×1 | not run | DRC actually fires, and names the *specific* rules — not merely "some error" |
| `trng_tc_inv_lvsbad` | clean | mismatch (`net.unmatched` ×1, `device.unmatched` ×1) | LVS catches a defect DRC structurally cannot see |

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

**DRC** checks thirteen rules over Nwell, Comp, Poly2, Contact, Metal1 and
the BJT mark layer — minimum widths, spacings, contact enclosures, and Nwell
enclosure of Comp. It does **not** cover implant layers, upper metal
(Metal2–Metal5) or vias, antenna rules, density, latch-up, or any
context-dependent rule needing connectivity (the deck's own comments flag
several rules as approximations for exactly that reason — e.g. Nwell
spacing uses the equipotential value because the checker has no net
information). Several of these gaps are tracked upstream
([klayout-tools#188][kt188], [#173][kt173]).

**Extraction** recognises MOS devices only, through one drawn well layer and
one metal level, and extracts no parasitics. There is no resistor,
capacitor, or bipolar device class ([klayout-tools#219][kt219]), and only
one metal level is declared ([klayout-tools#220][kt220]).

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

**Therefore: a clean report from this flow is not tapeout sign-off**, and
must never be cited as one. It is evidence that a specific, enumerated set
of rules passed on a specific stream, under a specific tool version recorded
in `layout/reports/environment.json`.

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
  The comparison ignores each report's `environment` block, which carries
  the KLayout engine version and moves on a tool upgrade without any verdict
  changing.

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

This is a rule for *this* directory's flow fixtures. When a real design cell
enters the flow (#16, #17) and its DRC/LVS status becomes a claim the spec
leans on, whether that claim is recorded as an append-only record under
`sim/records/`'s rules — or something equivalent — is a decision to take
then, in a decision record, not a default to inherit by accident.

---

## Adding a cell to the flow

1. Put the stream under `layout/` and its schematic-side reference netlist
   next to it. Give the layout's **top cell the same name** as the
   reference's `.SUBCKT` (Tool friction #2).
2. Add an entry to `EXPECTATIONS` in `layout/verify.py` saying what the flow
   must report — including, for a design cell, `status: clean` and
   `status: match`.
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
produced four:

1. **[klayout-tools#230][kt230]** — no supported way to emit a deliberately
   rule-violating layout. `klt gen` validates params against PDK minimums
   (correctly), and no other verb writes a stream, so the known-bad half of
   a DRC fixture pair cannot be produced with `klt` at all. That is why
   `layout/testcells/gdsii.py` exists: a ~200-line stdlib GDSII writer,
   entirely outside the toolchain, whose only job is to place rectangles on
   named layers. It should not have to exist.
2. **[klayout-tools#231][kt231]** — `klt lvs` pairs circuits by name and
   ignores the explicitly-declared `layout.top` / `reference.top`. With
   mismatched names the verdict is still correct but every finding collapses
   to a generic "circuit could not be matched to a counterpart". Naming all
   three fixtures' top cell `trng_tc_inv` is the workaround, and it is why
   `trng_tc_inv_lvsbad.lvs.json` names the broken net instead of shrugging.
3. **[klayout-tools#232][kt232]** — `klt lvs` accepts only a request *file*
   path, no inline JSON or stdin, unlike `klt gen --params`.
4. **[klayout-tools#233][kt233]** — `klt extract -o` errors out when the
   output directory does not exist rather than creating it, which every
   scripted flow hits once on a fresh checkout.

[klt]: https://github.com/2AMLogic/klayout-tools
[kt173]: https://github.com/2AMLogic/klayout-tools/issues/173
[kt188]: https://github.com/2AMLogic/klayout-tools/issues/188
[kt219]: https://github.com/2AMLogic/klayout-tools/issues/219
[kt220]: https://github.com/2AMLogic/klayout-tools/issues/220
[kt230]: https://github.com/2AMLogic/klayout-tools/issues/230
[kt231]: https://github.com/2AMLogic/klayout-tools/issues/231
[kt232]: https://github.com/2AMLogic/klayout-tools/issues/232
[kt233]: https://github.com/2AMLogic/klayout-tools/issues/233
