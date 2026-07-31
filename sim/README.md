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

## Pre-commit checklist

Mechanical; run through it before committing any record.

- [ ] Filename matches `<YYYY-MM-DD>-<testbench-slug>-<nn>.md` and `<nn>` is unused.
- [ ] Every required frontmatter field is present (`n/a` + reason where inapplicable).
- [ ] Seeds recorded for every stochastic run, in run order.
- [ ] `testbench.sha`, `netlist.sha`, and `repo_commit` captured from the tree that actually ran.
- [ ] `tool.ngspice` is the verbatim version string, not "latest".
- [ ] Corner is a single P/V/T point, and it is stated explicitly.
- [ ] Raw output committed under `sim/records/raw/<stem>/` with checksums listed.
- [ ] "How to reproduce" is copy-pasteable from the repo root.
- [ ] No claim in the record goes beyond what this run measured.
- [ ] No existing record was modified, except a permitted `status`/`superseded_by` edit.

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
