---
dr: DR-0032-stored-evidence-for-new-sim-runs
title: New run_corners.py runs store raw output in the artifact store and commit a manifest, not the bytes
status: Accepted
date: 2026-10-23
deciders: Builder of issue #686, implementing the issue's recipe; changes the record format but no ratified spec row and relaxes no evidence requirement, see Status.
supersedes: n/a
superseded_by: n/a
related: "#686 (origin); sim/README.md ('Record format', 'Stored evidence for new run_corners.py runs'); DR-0005 (one record per PVT point); DR-0031 (what a seed reproduces); the record writers in sim/harness/ and sim/tools/"
---

# DR-0032: New `run_corners.py` runs store raw output in the artifact store and commit a manifest

## Status

- 2026-10-23: **Accepted** by the Builder of #686. The evidence contract
  keeps its content: every number still ties to a hashed raw file. What
  changes is where the bytes live and which file in git carries the hash.
  Nothing in `spec/` is changed, no check is weakened, and no existing record
  is touched.
- 2026-10-24: **Amended** by the Builder of #693. The "no committed file holds
  the bytes of a stored object" check now skips manifest entries named for a
  harness input snapshot (`spinit`, `tb.fragment.spice`, `dut.netlist.spice`,
  `tb.manifest.json`). Those objects are byte copies of tracked files by
  construction, so every recorded run tripped the check on files the harness
  owns. The snapshots are still stored and hashed (reproducibility is
  unchanged), and the exemption is by entry name only: run output (`.log`,
  `.raw`, decks) and any identical bytes under another name still fail. The
  names of per-DUT dependency snapshots (`design_dependencies`) are the
  included files' own names, so they are not covered by this rule.

## Context

`sim/records/` holds 1042 records and about 75 MB of raw output (decks, logs,
snapshots), all committed, and three checks assume that: the record-checksum
check requires each record's `raw.files` to exist, hash correctly and be
tracked; `.gitignore` un-ignores `*.log`/`*.raw` under `sim/records/raw/`;
the history check treats `sim/records/` as append-only. Growing the repo with
every campaign is the cost; the benefit of committed bytes is that the hash
in a record can always be re-checked from a clone.

The fleet now provides a common artifact store reached through a broker
(`klt artifact put|get|verify`). Object bytes are private; a manifest naming
objects by sha256 reveals nothing and is safe in a public repository.

## Decision

From this change, every recorded `run_corners.py` point:

1. stages its raw output in the git-ignored `sim/.work/.stage/<stem>/`;
2. stores each file with `klt artifact put` and commits
   `manifests/artifacts/<stem>.manifest.json` (entries: name, size, sha256,
   `artifact:` URI) and the record, whose frontmatter carries a
   `stored_evidence` table (name, size, sha256) in place of the `raw:` block;
3. fails closed: with `$KLT_ARTIFACT_BROKER` unset, a `klt` lacking
   `artifact put`, or an unreachable broker the run exits nonzero and writes
   nothing under `manifests/` or `sim/records/`. There is no option that
   commits bytes instead.

Checks follow the new shape: the record-checksum check compares the table with
the manifest (and fails on a raw directory beside a stored record or a
manifest with no record); a new stdlib-only manifest check validates schema,
accepts only `artifact:` URIs, rejects storage names and fails if a stored
object's bytes are committed; the history check holds manifests append-only.
`klt artifact verify` re-hashes against the store and runs on a fleet worker.

Scope: manifest-forward only. Existing records, their raw directories and
history are not rewritten or migrated. Record writers other than
`run_corners.py` (the `sim/tb/*/run_*.py` callbacks that use
`report.finalize_record`, `signoff/`) keep committing raw output until a
separate issue moves them.

## Alternatives considered

### Commit the bytes when the store is unavailable

- **What**: fall back to today's behaviour if the broker cannot be reached.
- **Why plausible**: a run never fails for infrastructure reasons.
- **Why rejected**: it makes the repository's size and contents depend on
  broker uptime, and a quiet fallback is exactly how evidence ends up in the
  wrong place. Failing closed loses nothing: the staged bytes are kept and the
  put can be retried.

### Migrate the existing 1042 records

- **What**: store their raw directories and replace them with manifests.
- **Why plausible**: it would shrink the repository.
- **Why rejected**: it rewrites append-only evidence and history; the issue
  scopes this to new runs. Old records stay valid and checkable as they are.

### Keep a `raw:` block pointing at the stored objects

- **What**: reuse `raw.path`/`raw.files` with a URI as the path.
- **Why plausible**: no new frontmatter block.
- **Why rejected**: every existing consumer reads `raw.path` as a directory
  under `sim/records/raw/`, so a stored record would silently fail or be
  skipped there. A distinct `stored_evidence` block cannot be mistaken for it.

## Consequences

- **Positive**: campaigns stop growing the repository by raw bytes; a manifest
  is public-safe; the hash-per-file contract is unchanged and checked offline
  against the manifest.
- **Negative / accepted cost**: re-checking the bytes behind a stored record
  needs broker access (`klt artifact verify`), so CI checks the manifest and
  the table, not the stored bytes. A recorded run needs a fleet worker with
  `$KLT_ARTIFACT_BROKER`; elsewhere use `--no-write`.
- **Follow-up required**: confirm `klt artifact verify` exits 0 on the first
  real stored run from a fleet worker; move the other record writers
  separately if wanted.
- **Revisit if**: the store's retention or access model changes, or a campaign
  needs its bytes inspectable from a plain clone.
