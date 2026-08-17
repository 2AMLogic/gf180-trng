# `sim/` — evidence records

Everything in `sim/` exists to answer one question about any number this
project ever claims: **who produced it, under what conditions, and can I
reproduce it?**

A simulation result that is not recorded here in this format is not
evidence, and must not be cited in `spec/`, in an issue, or in a summary
document.

This is a **metadata and file-layout convention, not a tool contract**. It
does not assume any particular harness or runner. If the sim harness later
adopts a conflicting convention, reconcile the two with a decision record
(see [`spec/decision-records/TEMPLATE.md`](../spec/decision-records/TEMPLATE.md))
rather than silently editing records or this document's rules.

---

## The two rules

1. **Append-only.** A record is written once. Re-running a testbench —
   for any reason, including fixing a mistake — produces a **new** record.
   Records are never edited to change results and never deleted.
2. **No seed, no evidence.** Any stochastic analysis (ngspice transient
   noise, Monte Carlo) must record every seed it used. A transient-noise
   record without its seed(s) is unreproducible and therefore is not
   evidence, regardless of how good the numbers look.

Everything below is mechanics in service of those two rules.

---

## Layout

```
sim/
  README.md                     this document
  tb/                           testbench sources (mutable, reviewed like code)
    <testbench-slug>/           one directory per testbench
  records/                      APPEND-ONLY evidence records
    <YYYY-MM-DD>-<testbench-slug>-<nn>.md
    raw/
      <YYYY-MM-DD>-<testbench-slug>-<nn>/   raw output for that record
```

- `sim/tb/` is ordinary source. Edit it, review it, refactor it.
- `sim/records/` is the evidence area and is append-only. Changes to
  anything already committed under `sim/records/` are a review-blocking
  defect, with one exception: adding a `superseded_by` field to an existing
  record (see [Superseding](#superseding-a-record)).

### Record naming

```
<YYYY-MM-DD>-<testbench-slug>-<nn>.md
```

- `<YYYY-MM-DD>` — UTC date the run **completed**.
- `<testbench-slug>` — matches the directory name under `sim/tb/`.
- `<nn>` — two-digit sequence, `01`-based, unique within that date +
  testbench pair. Never reuse a number, even if a record is superseded.

Example: `2026-08-14-ro-delay-cell-jitter-03.md`, with its raw ngspice
output under `sim/records/raw/2026-08-14-ro-delay-cell-jitter-03/`.

`sim/run_corners.py` claims each `<nn>` by *creating* that raw directory
(an atomic `mkdir`, so exactly one process can win it) before the first
simulation starts, and re-hashes every `raw.files` entry before it reports
success. Two invocations for the same date and testbench — two terminals,
a retried CI step, an agent that re-launches a long background run — are
therefore safe to overlap: they get disjoint numbers, and a run whose raw
output changed underneath it fails loudly instead of writing a record whose
checksums match nothing.

One record covers **one testbench at one corner** (one process/voltage/
temperature point). A PVT sweep produces one record per corner, not one
record with a table of corners. This keeps a corner citable by record ID
and keeps a re-run of a single corner from invalidating the rest.

---

## Record format

A record is a Markdown file with a YAML frontmatter block (machine-readable
metadata) followed by prose (the summary and any caveats). No tooling reads
the frontmatter today; it is structured so tooling *can* later without
re-parsing prose.

### Required frontmatter fields

| Field | Meaning |
|---|---|
| `record` | The record's own filename stem. Self-identifying. |
| `date` | UTC date/time the run completed, ISO 8601 (`2026-08-14T09:12:00Z`). |
| `status` | `valid`, or `superseded` (see [Superseding](#superseding-a-record)). |
| `level` | `transistor`, `behavioral` or `gate` — what produced this. The first two are the two sides of the [DR-0009](../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md) boundary; `gate` is static analysis of a synthesized/placed netlist against the PDK's characterised libraries ([DR-0021](../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)), which is neither. Absent means `transistor` (records predating DR-0009); new records state it. |
| `testbench.path` | Repo-relative path to the testbench entry point. |
| `testbench.sha` | `git rev-parse HEAD:<path>` — blob SHA of the testbench at run time. |
| `netlist.path` | Repo-relative path to the DUT netlist/schematic-derived netlist. |
| `netlist.sha` | Blob SHA of the netlist at run time. |
| `repo_commit` | `git rev-parse HEAD` at run time; `-dirty` suffix if the tree was dirty. |
| `pdk` | PDK name and version/tag (e.g. `gf180mcuC @ <version>`). |
| `pdk.models` | The corner model file(s) actually included. |
| `tool.ngspice` | Full `ngspice -v` version string. |
| `tool.platform` | OS/arch the run executed on. |
| `corner.process` | `tt` / `ss` / `ff` / `sf` / `fs` (as named by the PDK). |
| `corner.voltage` | Supply(s) in volts, with the nominal noted. |
| `corner.temperature` | Degrees C. |
| `analysis.type` | `tran`, `tran-noise`, `noise`, `ac`, `dc`, `mc`. |
| `analysis.tstop` | Run length (simulated time), or the sweep range for `ac`/`dc`/`noise`. |
| `analysis.tstep` / `analysis.tmax` | Timestep controls that materially affect the result. |
| `analysis.noise_params` | For `tran-noise`: `NOISETSTEP` / `NOISEFMAX` / equivalent, verbatim. |
| `analysis.runs` | Number of independent runs aggregated into this record. |
| `seeds` | **Every** seed used, in run order. Required whenever the analysis is stochastic; write `seeds: n/a (deterministic analysis)` otherwise. |
| `raw.path` | Repo-relative path to the raw-output directory for this record. |
| `raw.files` | Raw output filenames with SHA-256 checksums. |
| `wall_time` | Wall-clock cost of the run. Makes future coverage/cost trade-offs honest. |

If a required field genuinely does not apply, write the field with an
explicit `n/a` and a reason. Do not omit it — a missing field is
indistinguishable from a forgotten one.

### Required prose sections

- **Result** — the numbers, with units and the run-to-run spread when
  `analysis.runs > 1`. Numbers only; no entropy-rate or spec-compliance
  claims.
- **How to reproduce** — the exact command(s), runnable from the repo root,
  including the seed(s). Someone with the repo and ngspice must be able to
  copy-paste this.
- **Caveats** — what this run does *not* show (method limits, truncated
  accumulation time, known weak spots such as flicker-noise handling in
  transient noise). Stating a limit is not a weakness in the record; an
  unstated limit is a defect.

---

## Behavioral-level records

Blocks downstream of the [DR-0001] raw tap — the conditioner, the health
tests, the FIFO/register file, the estimator pipeline — contain no device
models, so a record of one has no process/voltage/temperature point and
never invokes ngspice. [DR-0009] fixes where that boundary sits and what
such a record may be used for. In this format that means:

- `level: behavioral`.
- `pdk`, `pdk.models`, `tool.ngspice`, `corner.process`, `corner.voltage`
  and `corner.temperature` are written as `n/a` **with the reason** — the
  same rule as any other inapplicable field. They are not omitted.
- The record **names its input source**: either *transistor-derived* (a raw
  bitstream captured from a transistor-level sampler run, cited by record
  stem) or *declared synthetic* (a source model, with its parameters and
  seed stated). A run driven by a synthetic source is evidence about the
  **block**, never about the source.
- **A behavioral record may not be cited for any claim that depends on
  process, voltage or temperature** — rate, power, jitter, metastability,
  timing closure, min-entropy. It can establish functional behaviour,
  bit-exactness, block structure and arithmetic, and nothing that moves
  with a corner.

Behavioral testbenches live under `sim/tb/<slug>/` like any other but have
**no `tb.json`**, so `sim/run_corners.py` cannot discover them and cannot
sweep them across a PVT grid they have no meaning on. Each carries a
`README.md` saying how it is run. See `sim/tb/conditioner-crc32/` for the
first one.

This is the one bounded exception to CLAUDE.md's "PVT corners on every
recorded result". The rule is unchanged for every claim that *has* a corner.

---

## Gate-level records

[DR-0021] adds a third `level:` value for a kind of evidence neither of the
other two describes: **static analysis of a synthesized or placed-and-routed
gate-level netlist against the PDK's own characterised standard-cell
libraries** — static timing analysis, liberty-table power, and geometry read
from a placed/routed database. No device model is instantiated and ngspice is
never invoked, but a liberty deck *is* a process/voltage/temperature point, so
unlike a behavioral record a gate record **has a corner and states it**. In
this format:

- `level: gate`.
- `corner.process`, `corner.voltage` and `corner.temperature` are filled in
  from the liberty deck's own operating conditions — never `n/a` — alongside
  two fields only this level has: `corner.liberty` (the deck, since P/V/T
  alone does not say which library or which characterisation) and
  `corner.interconnect` (the parasitic corner, which moves independently of
  the device corner for a routed block).
- `pdk.models` lists the liberty deck, both LEFs and the extraction rule deck,
  each content-hashed — the gate-level equivalent of a transistor record
  naming its model sections.
- `tool.ngspice` is `n/a` **with the reason**, and the tool that did produce
  the numbers is named with its version.
- A gate record may be cited for timing closure, Fmax, standard-cell area and
  liberty-model power at the corner it names — as a property of *that*
  implementation. It may **not** be cited as a measured supply current, for
  anything the library itself is the source of truth for, for any raw-tap
  claim (entropy, jitter, metastability), or as signoff. [DR-0021] §3 is the
  full rule; each record restates it in its own Caveats.

[DR-0005]'s one-record-per-corner rule is unchanged: a 5-liberty × 3-interconnect
sweep is fifteen records. Like behavioral testbenches, a gate-level testbench
carries **no `tb.json`** — `sim/run_corners.py` must not sweep it across the
analog P/V/T grid, because a liberty deck is a characterised bundle rather
than a free choice of the three axes. See `sim/tb/digital-sta-power/` for the
first one.

[DR-0001]: ../spec/decision-records/DR-0001-raw-and-conditioned-output-paths.md
[DR-0005]: ../spec/decision-records/DR-0005-sim-harness-record-granularity.md
[DR-0009]: ../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0021]: ../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md

---

## Superseding a record

Mistaken, misconfigured, or invalidated runs are **not** deleted or edited.

1. Write a **new** record for the corrected run, with a
   `supersedes: <old-record-stem>` field and a one-line reason in its prose.
2. In the old record, make the **only** permitted post-hoc edit: change
   `status: valid` to `status: superseded` and add
   `superseded_by: <new-record-stem>`. Change nothing else — not the
   numbers, not the metadata, not the prose.
3. If a run was invalid and there is no corrected re-run yet, still write a
   short record documenting the run and why it is not usable, and set the
   old record's `status: superseded` only once a replacement exists. An
   invalid result that is never recorded is a result that gets re-derived by
   the next person.

The commit that supersedes a record should say so in its message, so
`git log -- sim/records/<stem>.md` tells the whole story.

---

## Hung and timed-out runs

Every corner `run_corners.py` simulates is bounded by `--timeout` (default
`runner.DEFAULT_TIMEOUT_S`, currently 300s). The bound is enforced two ways
at once, precisely because a hung ngspice once outlived the harness process
that launched it and burned a worker offline for hours undetected (issue
#83):

- An OS-level watchdog — coreutils `timeout(1)` (`gtimeout` on macOS via
  Homebrew's `coreutils`; `--check-env` reports which, if either, is on
  `PATH`) — wraps the ngspice invocation directly. It runs as ngspice's
  parent, independent of `run_corners.py` staying alive, so it still fires
  and kills the whole process group even if the harness itself is killed
  mid-run.
- An in-process `Popen.communicate(timeout=...)` guard is a secondary
  backstop for the common case (harness alive for the whole run), and the
  sole enforcement when no watchdog binary is available on `PATH` (a
  degraded mode `--check-env` warns about, since it cannot survive the
  harness process itself dying).

A killed corner reports `FAILED-TIMEOUT` in the printed summary (not a
plain `FAIL`, and never silently missing), and — same as any other
completed point — still gets a normal written record under
`sim/records/`, whose "Run failures" line and raw log name the deck and
the elapsed/bound time, so a reviewing Judge sees the hang instead of an
absent result. A record built this way is evidence that the run hung, not
evidence about the device; `sim/README.md`'s "no claim beyond what this
run measured" rule applies as usual.

---

## Pre-commit checklist

Mechanical; run through it before committing any record.

- [ ] Filename matches `<YYYY-MM-DD>-<testbench-slug>-<nn>.md` and `<nn>` is unused.
- [ ] Every required frontmatter field is present (`n/a` + reason where inapplicable).
- [ ] Seeds recorded for every stochastic run, in run order.
- [ ] `testbench.sha`, `netlist.sha`, and `repo_commit` captured from the tree that actually ran.
- [ ] `tool.ngspice` is the verbatim version string, not "latest".
- [ ] Corner is a single P/V/T point, and it is stated explicitly — or the
      record is `level: behavioral` and every device-model field carries
      `n/a` plus a reason, and the input source is named. A `level: gate`
      record states its corner like a transistor one, and additionally names
      its liberty deck and its interconnect corner (DR-0021).
- [ ] Raw output committed under `sim/records/raw/<stem>/` with checksums listed —
      `python3 sim/tools/verify_record_checksums.py --changed` exits 0 (see below).
- [ ] "How to reproduce" is copy-pasteable from the repo root.
- [ ] No claim in the record goes beyond what this run measured.
- [ ] No existing record was modified, except a permitted `status`/`superseded_by` edit.

### Checking the raw-output checksums

The checksum item is the one item on this list a human cannot do by eye, so it
is a command:

```sh
python3 sim/tools/verify_record_checksums.py --changed   # records this branch adds
python3 sim/tools/verify_record_checksums.py             # every record in the repo
python3 sim/tools/verify_record_checksums.py <record.md>...
```

It re-hashes every file listed in `raw.files` and fails on a digest that no
longer matches, a listed file that is missing, a file sitting in the raw
directory that the record never listed, or raw output that was never `git
add`ed (`--no-git` drops that last check). Exit 0 means the item is satisfied.
CI runs it over every record on every pull request, and `sim/selftest.sh`
runs it as stage 2.

---

## Worked example (ILLUSTRATIVE ONLY — not evidence)

> **The block below is a format illustration. Every number, SHA, seed, and
> path in it is fabricated.** It is deliberately kept inline in this README
> and is *not* committed as a file under `sim/records/`, so it can never be
> mistaken for real evidence. Copy its shape, never its contents.

````markdown
---
record: 2026-08-14-ro-delay-cell-jitter-03
date: 2026-08-14T09:12:00Z
status: valid
supersedes: 2026-08-13-ro-delay-cell-jitter-01   # optional; omit if none

testbench:
  path: sim/tb/ro-delay-cell-jitter/tb_jitter.sp
  sha: 0000000000000000000000000000000000000000    # illustrative
netlist:
  path: design/ro/ro_core_9stage.spice
  sha: 1111111111111111111111111111111111111111    # illustrative
repo_commit: 2222222222222222222222222222222222222222

pdk: gf180mcuC @ <pdk-version-tag>
pdk.models:
  - <pdk-root>/models/ngspice/design.ngspice (section: <corner-section>)

tool:
  ngspice: "ngspice-<version> : Circuit level simulation program"   # verbatim `ngspice -v`
  platform: macOS 15.x arm64

corner:
  process: ff
  voltage: 3.63 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran-noise
  tstop: 200u
  tstep: 1p
  noise_params: "NOISETSTEP=1p NOISEFMAX=100G"    # verbatim from the deck
  runs: 5
seeds: [1001, 1002, 1003, 1004, 1005]

raw:
  path: sim/records/raw/2026-08-14-ro-delay-cell-jitter-03/
  files:
    - run-1001.raw  sha256:aaaa…    # illustrative
    - run-1002.raw  sha256:bbbb…
    - ngspice.log   sha256:cccc…
wall_time: 41m
---

## Result

Illustrative placeholders — do not cite:

| Quantity | Mean over 5 seeds | Run-to-run spread (min–max) |
|---|---|---|
| Period jitter, 1σ (per stage) | `<value> ps` | `<min>–<max> ps` |
| Accumulated jitter @ 1 µs | `<value> ns` | `<min>–<max> ns` |
| Accumulated jitter @ 4 µs | `<value> ns` | `<min>–<max> ns` |

Numbers only. No entropy-rate claim is made or implied by this record.

## How to reproduce

```sh
# from repo root, one invocation per seed
ngspice -b -r sim/records/raw/2026-08-14-ro-delay-cell-jitter-03/run-1001.raw \
  -D seed=1001 sim/tb/ro-delay-cell-jitter/tb_jitter.sp
```

## Caveats

- Single corner (`ff` / +10% / −40 °C). Says nothing about any other corner.
- 200 µs accumulation bounds the √t check over one decade only; longer-time
  behavior is not covered.
- Transient-noise flicker handling is a known method limit — low-frequency
  jitter accumulation from this run should not be extrapolated past the
  simulated window.
````

---

## What does *not* belong here

- Summary/characterization documents that aggregate many records. Those are
  ordinary documents; they **cite** record stems rather than restating
  metadata, and they live outside `sim/records/`.
- Decisions. A choice that changes the design or the spec goes in
  `spec/decision-records/` (see
  [`spec/decision-records/TEMPLATE.md`](../spec/decision-records/TEMPLATE.md)),
  citing the records that informed it.
- Claims the run did not measure — entropy rates, spec pass/fail,
  architecture recommendations.
