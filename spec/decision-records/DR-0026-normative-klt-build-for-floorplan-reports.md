---
dr: DR-0026-normative-klt-build-for-floorplan-reports
title: Re-pin pdk-nightly.yml forward to the klayout-tools build layout/floorplan/reports/ already reflects, rather than regenerating those reports under the older pin
status: Accepted
date: 2026-09-15
deciders: Proposed by the Builder of #230 (2026-09-15). Amended and accepted 2026-10-08 — the amendment option ("amend-060") was chosen in the decision comment on #281 dated 2026-10-08, and the amended record is ratified through ordinary review of the pull request that carries it (#281's), per the ratification-via-PR convention this record was proposed under. See Status.
supersedes: n/a
superseded_by: n/a
related: "#230 (origin — this record IS the decision it asks for), #281 (the re-measurement that fired this record's 'Revisit if' clause, the decision comment that chose the amendment, and the re-pin itself), #256 (sibling — regenerates layout/floorplan/reports/ under whichever build this record makes normative), #226 (the PR that regenerated layout/floorplan/reports/ against the newer build, surfacing the drift), #217 (the PR that set the superseded 3fbb4478e3017c8d8580fba4feb08bc386b4c925 nightly ref), #227 (sibling issue — the CI gate that makes this class of drift detectable, closed independently of this decision via merged PR #235); klayout-tools#1969 (LVS provenance.input.content_hash, the capability the amended target exists for), klayout-tools#2048 (the per-device PMOS body check behind the measured category-count change); layout/README.md 'Pinning the tool' (the klt-build-identity problem this record's evidence method is built on); .github/workflows/pdk-nightly.yml (the pin this record moves, as of #281)"
---

# DR-0026: Re-pin `pdk-nightly.yml` forward to the klayout-tools build `layout/floorplan/reports/` already reflects, rather than regenerating those reports under the older pin

## Status

- 2026-09-15: **Proposed** by the Builder of #230. Not accepted directly —
  per rjwalters' 2026-09-15 comment on #230, "which build is normative" is a
  decision record drafted and evidence-backed by a Builder, then ratified
  via ordinary PR review, not a call made out-of-band before work starts.
  This record stays `Proposed` until a human or Champion approves the PR
  that carries it.
- 2026-09-23: this record's own "Revisit if" clause (end of Consequences)
  **fired**. #281 measured `klt lvs` under the klayout-tools `0.6.0` release
  — 368 commits past `c903103cba9e` — and an LVS category count moved
  (`device.body_unverified` 1 → 2 on `combiner_sampler`), contradicting the
  "no LVS category moved" basis the Decision below rests on. The record
  stayed `Proposed`; ratifying it as written would have ratified a stale
  measurement.
- 2026-10-08: **Accepted, as amended.** The question was put as three
  options — ratify amended to the 0.6.0 release, ratify as written
  (`c903103cba9e`), or reject (keep `3fbb4478`, Alternative A below). The
  decision comment on #281 dated 2026-10-08 chose the amendment, posted by
  an agent session acting for the repository operator; the other two options
  were rejected. Ratification itself is the ordinary review of the pull
  request that carries this amendment (#281's), as this record's 2026-09-15
  entry requires — the comment chose *which* record to ratify, and the
  review ratifies it. The amendment, its re-measurement, and the re-pin it
  authorizes are in "Amendment (2026-10-08)" directly below. The original
  Context, Decision, Alternatives and Consequences that follow it are kept
  unedited as the record of what was proposed and why; where they name
  `c903103cba9e` as the target, the amendment supersedes them.

## Amendment (2026-10-08): the target is the klayout-tools 0.6.0 release

### What changes, and what does not

The **direction** of the Decision stands: move the producer pin forward to
the build the newer evidence was made with, do not regenerate under the
older `3fbb4478` pin (Alternative A stays rejected, for the reasons given
there). What changes is the **target**: not `c903103cba9e` "or later", but
the tagged **klayout-tools `0.6.0` PyPI release**, installed as
`pip install "klayout-tools==0.6.0" "klayout==0.30.10"`.

Why the release rather than `c903103cba9e`:

- **It is the build that does the job #281 needs.** `c903103cba9e`
  (2026-09-11) predates klayout-tools#1969 (closed 2026-09-17), which is
  what makes `klt lvs` populate `provenance.input.content_hash`. Without it
  `signoff/block-manifest.json`'s `4.analog` citation cannot carry a pin;
  ratifying the record as written would have needed a second re-pin and
  record almost immediately.
- **A release is reproducible with one `pip install`.** The reason this
  file's pin history is a list of git SHAs — the latest release predated
  the gf180mcu flow this repository uses — no longer holds. The release is
  tag `v0.6.0` → commit `c622e8addb362491664d44ba4d717f354ca88bbd`
  (`gh api repos/2AMLogic/klayout-tools/git/ref/tags/v0.6.0`, dereferenced),
  469 commits ahead of `3fbb4478` and 368 ahead of `c903103cba9e`, both with
  `behind_by: 0` (`gh api .../compare/<base>...c622e8a`, 2026-10-08). The
  wheel records that commit itself (`klt version --format json` →
  `"git_commit": "c622e8addb36…"`, `"git_tag": "v0.6.0"`, `"dirty": false`,
  `"is_release": true`; klayout-tools#1202), so `layout/reports/
  environment.json`'s `klt_origin.commit` is filled from the install, not
  asserted.
- **`klayout==0.30.10` is pinned with it** because that is the engine the
  release records it was tested against (`klayout_version_expected`). Left
  floating, pip resolves `0.30.12` and every DRC/LVS report carries
  `provenance.klayout_version_mismatch: true`. Measured: running all 13
  fixtures under `0.30.12` and `0.30.10` differs only in
  `provenance.klayout_version` and `provenance.klayout_version_mismatch`.

### The re-measurement

Method, chosen so that every difference is attributable to the tool build
and nothing else:

1. **Control first.** On the measuring host, the committed `layout/reports/`
   were reproduced *exactly* under the old pin before anything was changed:
   `klayout-tools @ git+…@3fbb4478` (`klt 0.4.0+g3fbb4478e301`) in a
   throwaway venv, with the PDK provisioned at the same `open_pdks` commit
   `pdk-nightly.yml` pins (`f6eeac7d…`, via `ciel 2.6.1`), gave
   `python3 layout/verify.py --require-tools` → `committed reports match
   this run`, `PASS`. (Against a different `open_pdks` commit the 13
   `extract` reports differ in `pdk.version` alone — which is why the PDK
   commit is part of the method.)
2. **Then the release**, same host, same PDK, in its own venv: `klt 0.6.0`
   with `klayout==0.30.10`. Each committed report was compared with the live
   run through `layout/verify.py`'s own `_stable()`.

Result, all 13 fixtures (`trng_tc_inv`, `trng_tc_inv_drcbad`,
`trng_tc_inv_lvsbad`, `ro_stage`, `ro_stage_ring2`, `ro_nand2`,
`ro_nand2_ring2`, `ro_buf`, `xor2`, `sampler_dff`, `ro_ring11`,
`ro_ring11_ring2`, `combiner_sampler`):

- **Unchanged**: every DRC `status`, `rule_counts` and `violation_count`;
  every DRC run's checked layers; every extract `device_count`, `net_count`
  and `netlist_sha256`; all 13 `*.extracted.spice` and all 12
  `*.lvs-request.json` byte-for-byte; every LVS `status` (`match` on 11,
  `mismatch` on `trng_tc_inv_lvsbad`) and every `severity: "error"`
  mismatch (still exactly `net.unmatched` ×1 + `device.unmatched` ×1 on
  `trng_tc_inv_lvsbad`, and none elsewhere).
- **The one count that moved — the measured category split.** On every one
  of the 12 LVS fixtures, `category_counts["device.body_unverified"]` goes
  1 → 2 and `mismatch_count` goes up by exactly one, and in every case the
  delta is **one added `severity: "warning"` entry for device class `pfet`**
  — the old `mismatches[]` list is a strict subset of the new one. Per
  fixture (NMOS count = the old, only disclosure; unchanged):

  | fixture | nfet | pfet | `body_verification.device_count` = extracted devices |
  |---|---|---|---|
  | `trng_tc_inv`, `trng_tc_inv_lvsbad`, `ro_buf` | 1 | 1 | 2 |
  | `ro_stage`, `ro_stage_ring2` | 2 | 2 | 4 |
  | `ro_nand2`, `ro_nand2_ring2` | 3 | 3 | 6 |
  | `xor2` | 6 | 6 | 12 |
  | `sampler_dff` | 11 | 11 | 22 |
  | `ro_ring11`, `ro_ring11_ring2` | 23 | 23 | 46 |
  | `combiner_sampler` | 52 | 52 | 104 |

  This is a disclosure change, not a design or verdict change: these
  hand-drawn cells draw no well taps, so every PMOS body lands on an
  anonymous KLayout-synthesized net — as `layout/README.md` ("Bulk terminals
  are approximated") had already stated and verified against `klt extract`.
  The old build did not say so because klayout-tools#1113 had made the PMOS
  warning deck-structural (silent whenever the deck merely *declared* a
  well-tap mechanism); klayout-tools#2048 made it per-device again. The new
  `body_verification` block (`"status": "unverified"`, one finding per
  class) states the same fact machine-readably.
- **Additive or provenance-only, on every report**: `provenance.klt_version`
  `0.4.0` → `0.6.0`; `provenance.deck.content_hash`
  `sha256:79e71a1e…` → `sha256:95c2eb91…` with `released: true` → `false`
  (the deck hash's own notion of "released" — not the tool's; the tool is a
  release, per `klt version`); `provenance.input` now populated
  (`content_hash` + `role`), which is the capability this amendment exists
  for; `schema_version` 1 → 2 on DRC; new `metrics`, `subcircuit`,
  `hints_applied`, and LVS `options.*` keys; `extract` `devices[]` gain
  `instance_path` (empty for flat leaf cells, naming the placed leaf instance
  for assembled rings/blocks); DRC `coverage` gains the
  `checked`/`inapplicable`/`skipped`/`unknown`/`nothing_checked` schema; LVS
  gains `power_connectivity` — `"unchecked"` on all 12, because
  `reference.form` is `plain-element` and the supplies take part in the
  ordinary compare — and `body_verification` (above).
- **DRC coverage**: `coverage.rules_skipped` gains exactly
  `metal4.space.1` and `metal4.width.1` on all 13. These rules do not exist
  in the old deck at all; no fixture draws Metal4, so the newer deck lists
  them as skipped with reason `"no_applicable_geometry"`. No rule the old
  run checked went unchecked.

Nothing came back *not* matching, so there was no finding to file
separately; the category split above is the measured change this
amendment records.

### Decision, as amended

1. `.github/workflows/pdk-nightly.yml` installs
   `"klayout-tools==0.6.0" "klayout==0.30.10"` (done in #281's PR, with a
   dated comment block in that file's convention).
2. `layout/reports/` is regenerated under that build with
   `python3 layout/verify.py --write` — including `environment.json`, whose
   `klt_origin` reads `commit: c622e8addb36…`, `tag: v0.6.0`,
   `is_release: true` (done in #281's PR). `layout/verify.py`'s 12 LVS
   expectations are re-baselined per fixture to the split above, and each
   now also pins its per-class `body_verification` counts and its
   `power_connectivity` status, so the next disclosure change fails by class
   and count.
3. `design/trng_top/trng_top.synth.json` is regenerated too: the nightly's
   `design/synth.py --check` runs under the same pinned build, and under
   0.6.0 `klt synthesize` adds a per-invocation `run_id`/`run_script_path`
   (upstream's own `RERUN_BOOKKEEPING_KEYS`, klayout-tools#2224) that
   `design/synth.py` now restates to `null`. The synthesized netlist
   `trng_top.synth.v` is byte-identical; only the report envelope moved.
4. `layout/floorplan/reports/` is still owed its confirmation under the new
   pin (item 4 of the original Decision, unchanged) — see "Follow-up
   status" below for what #281's PR did and did not establish. Its
   regeneration is #256's.
5. `provenance.deck.released: false` stays an accepted, disclosed
   consequence, as in the original item 5.

### Follow-up status

- Re-pin `pdk-nightly.yml`: **done** (#281).
- Regenerate `layout/reports/` and confirm `klt_origin.commit`: **done**
  (#281).
- Confirm `layout/floorplan/reports/` under the new pin: **run, not
  confirmed clean — still owed.** `python3 layout/floorplan/floorplan.py
  --require-tools` (check mode, no `--write`) was run under 0.6.0, twice,
  with identical output (about 5 minutes each, not the 25+ the original
  record feared), and once under the old `3fbb4478` pin as a control, all
  against the pinned `open_pdks` commit. Every composed verdict holds under
  0.6.0: the four ring-fit compositions are DRC clean with 0 violations
  introduced by the fit and LVS `match` with no unexpected category (the
  three analog regions at 3 mismatches instead of 2, the same PMOS
  disclosure as above); the composed row is DRC clean with 0 new
  violations; the inter-region LVS is `match`. Both runs still fail
  `floorplan.py`'s own checks, 11 each. Six are the committed artefacts
  that no longer match under *either* build (`area.json`, `compose.json`,
  `floorplan.drc.json`, `ring_fit.json`, `interregion.json`,
  `trng_floorplan.gds`), which is #256's regeneration. One is new
  information about the build: the inter-region extract's `pin_count` is
  114 under 0.6.0 and 109 under `3fbb4478`, against the 107 the script
  expects and the committed report recorded. The five extra pins under
  0.6.0 are exactly the five the script subtracts as unnameable, now
  extracted under label-joined names — filed as #309. The area rollup's
  ring `cell um²` column also moves (164.4 → 225.1 µm² per ring, because
  the generated starved-MOS footprint estimate moves from 2.386/3.580 to
  5.040/6.440 µm²); the guarded and total floorplan areas do not. None of
  this is papered over here: `layout/floorplan/` is untouched by #281's PR,
  and the nightly does not yet reach this step at all (its PDK provisioning
  omits `gf180mcu_fd_sc_mcu7t5v0`, #310).
- `signoff/block-manifest.json`'s `4.analog` citation gains its
  `content_hash` pin and `signoff/records/t1-tier-report.json` is
  regenerated (`citation.input_verified` `null` → `true` for that row; T1
  count unchanged at 5 of 22): **done** (#281).

### Revisit if (amended)

The next producer re-pin re-runs this same control-then-candidate comparison
(same host, same `open_pdks` commit, `_stable()` diff of all 13 fixtures)
rather than assuming this result holds. Pin the KLayout engine the
candidate release records (`klayout_version_expected`) alongside it, or
record why not.

## Context

### The drift, and how it was confirmed still current

`.github/workflows/pdk-nightly.yml` installs `klayout-tools` pinned to
`3fbb4478e3017c8d8580fba4feb08bc386b4c925` (#217). `layout/floorplan/reports/`
was most recently regenerated by #226 against a different upstream commit.
Re-confirmed today (2026-09-15) rather than trusted from #230's filing date:

```
$ gh api repos/2AMLogic/klayout-tools/compare/3fbb4478e3017c8d8580fba4feb08bc386b4c925...c903103cba9e -q '.ahead_by,.behind_by'
101
0
```

`c903103cba9ef3b87f18c0361fb847612df5c7d9` is 101 commits ahead of the
pinned ref, strictly forward (`behind_by: 0`), and its own commit metadata
(`gh api repos/2AMLogic/klayout-tools/commits/c903103cba9e...`) dates it
2026-09-11 — after #217 (2026-09-11) but before today.

### Measured evidence: what actually changes in `layout/reports/` under the newer build

The 101-commit count alone says nothing about *content* — a compare can be
101 commits of documentation and still not move a single verdict, or one
commit and move all of them. #230's acceptance criteria ask for the
committed `layout/reports/` fixtures to be run under both refs via
`layout/verify.py` and the JSON diffed, so that Alternative B's stated cost
("every other fixture must be re-verified") is quantified rather than
assumed. That was done here, on the same machine, following
`layout/README.md`'s "Pinning the tool" recipe:

```
$ uv tool install --force "klayout-tools @ git+https://github.com/2AMLogic/klayout-tools@3fbb4478e3017c8d8580fba4feb08bc386b4c925"
$ klt --version
klt 0.4.0+g3fbb4478e301.dirty
$ python3 layout/verify.py --require-tools
...
== reports ==
  ok   committed reports match this run
PASS: DRC/LVS flow is functional end to end.

$ uv tool install --force "klayout-tools @ git+https://github.com/2AMLogic/klayout-tools@c903103cba9ef3b87f18c0361fb847612df5c7d9"
$ klt --version
klt 0.4.0+gc903103cba9e.dirty
$ python3 layout/verify.py --require-tools
...
== reports ==
  FAIL layout/reports/trng_tc_inv.drc.json does not match this run -- re-run `python3 layout/verify.py --write`
  [... 38 report files total, one FAIL line per fixture/stage ...]
FAIL: 38 expectation(s) not met
```

Every one of `layout/verify.py`'s own hardcoded pass/fail expectations —
`drc.status`, `drc.rule_counts`, `extract.device_count`/`net_count`,
`lvs.status`, `lvs.category_counts`, `lvs.error_count` — printed identically
under both builds for all 13 fixtures (`trng_tc_inv`,
`trng_tc_inv_drcbad`, `trng_tc_inv_lvsbad`, `ro_stage`, `ro_stage_ring2`,
`ro_nand2`, `ro_nand2_ring2`, `ro_buf`, `xor2`, `sampler_dff`, `ro_ring11`,
`ro_ring11_ring2`, `combiner_sampler`). The 38 `FAIL` lines are
`verify.py`'s strict byte-for-byte `compare_reports` gate on the committed
JSON, which is stricter than the hardcoded expectations. Loading each
committed report and the live re-run through `verify.py`'s own `_stable()`
(the function that already strips the three machine-local fields — engine
version, PDK root, PDK source path — that legitimately move between hosts)
and diffing what is left shows the *entire* 38-file drift reduces to exactly
two kinds of change, present on every fixture and nothing else:

1. **`provenance.deck.content_hash` / `provenance.deck.released` move
   together, identically, on every report.** Committed (built under
   `3fbb4478`): `sha256:79e71a1e7d84be3cfc82e4c70afbdf7b743ac1f361fb8e981f57831014d2e8b0`,
   `released: true`. Live, under `c903103cba9e`:
   `sha256:36ed362443943bc488c41640b3e219c926bb251a7c1bd0e07bd6e96f5c158114`,
   `released: false`. This second hash is not a coincidence local to this
   run — it is **byte-identical** to the `provenance.deck.content_hash`
   already committed in `layout/floorplan/reports/floorplan.drc.json`
   (`"content_hash": "sha256:36ed362443943bc488c41640b3e219c926bb251a7c1bd0e07bd6e96f5c158114"`,
   `"released": false`). That is direct, measured confirmation — not an
   inference from the 101-commit count — that the floorplan reports already
   committed on `main` were built against a deck matching `c903103cba9e`
   (or a later commit with the same deck content), not the currently pinned
   `3fbb4478`.
2. **Every `extract` report's `devices[]` entries gain an additive
   `instance_path: []` field** (empty for every device in every one of
   these leaf-cell fixtures, none of which has instancing hierarchy below
   the extracted top cell). This moves each `extract.json`'s
   `netlist_sha256` — the extract stage's own record of "what changed" — but
   critically **does not** change the actual extracted netlist text: a
   direct `diff` of the committed `layout/reports/ro_stage.extracted.spice`
   against the live `c903103` re-run's `layout/.work/ro_stage.extracted.spice`,
   and of the committed `.lvs-request.json` against its live counterpart,
   is byte-identical in both cases. The new field is real (a schema
   addition upstream), but it carries no information for the flat,
   non-hierarchical fixtures this repository extracts today.

No device count, net count, DRC rule, LVS category, or match/mismatch
verdict moved for any fixture. `layout/reports/environment.json`'s
`klt_origin.commit` is the field that would need updating to reflect
whichever build is pinned, per `layout/README.md`'s own instruction to cite
it rather than `klt --version` (which reports `0.4.0` for both builds and
cannot distinguish them, confirmed above by `klt --version`'s tag suffix,
`+g3fbb4478e301` vs `+gc903103cba9e`, which is a local `uv`/setuptools_scm
convenience, not a `klt_origin`-quality provenance field a caller should
parse).

**Environment note on `git status --porcelain`**: both `verify.py` runs
above wrote only to the git-ignored `layout/.work/` scratch directory, per
that script's own docstring and `WORK_DIR` comment; `git status --porcelain`
was confirmed clean for `layout/reports/` and `layout/floorplan/reports/`
before this PR was opened, and no line of this record's evidence-gathering
touched a committed report or `.github/workflows/pdk-nightly.yml`'s pin.

### What was not measured, and why

#230's acceptance criteria scope the required evidence to `layout/reports/`
via `layout/verify.py` specifically — the harness that already exists for
exactly this comparison — not to re-running `layout/floorplan/reports/`'s
own generator (`layout/floorplan/floorplan.py`) under both builds. An
attempt was made anyway, to see whether the composed-floorplan check itself
moves: `python3 layout/floorplan/floorplan.py --require-tools` was started
under the currently-pinned `3fbb4478` build and had not completed after
more than 25 minutes of wall clock (on a host under unrelated concurrent
load at the time — `uptime`'s load average was in the 30s during the run),
consistent with DR-0025's own disclosed ~19.5-minute full-chip extraction
probe, and was terminated rather than waited out further; it was not re-run
under `c903103` for the same reason. This means: **this record's
"forward-pin is low-cost" conclusion is scoped to `layout/reports/`, which
is what #230 asked to be measured, and is not itself evidence that
`layout/floorplan/floorplan.py`'s own composed checks are unaffected by the
newer build** — though the fact that the two builds' shared deck rule set
produced identical DRC/LVS verdicts on every one of `layout/reports/`'s 13
fixtures is circumstantial evidence in the same direction. Whoever executes
the re-pin authorized below should re-run
`python3 layout/floorplan/floorplan.py --require-tools` (with a realistic
runtime budget, per the same disclosed cost DR-0025 already flagged for
`klt`'s composed/extract flows) as the actual confirmation, not assume it
from this record.

## Decision

**Re-pin `.github/workflows/pdk-nightly.yml`'s `klayout-tools` install to
`c903103cba9ef3b87f18c0361fb847612df5c7d9` (or a later commit, re-verified
forward the same way `#170`/`#171`/`#210`/`#217` were), and regenerate
whatever else moves under the new deck. Regenerating `layout/floorplan/reports/`
under the *older*, currently-pinned `3fbb4478e3017c8d8580fba4feb08bc386b4c925`
build is rejected.**

This is not the mechanical regeneration itself — that is explicit follow-up
work, tracked separately, once this record is accepted. What this decision
fixes is which direction that follow-up moves:

1. `.github/workflows/pdk-nightly.yml`'s `Install klayout-tools` step's pin
   moves from `3fbb4478e3017c8d8580fba4feb08bc386b4c925` to
   `c903103cba9ef3b87f18c0361fb847612df5c7d9` (or later), with the same kind
   of dated, motivated comment block the four prior pin moves in that file
   already carry (see Context above for the ancestry check this repeats).
2. `layout/reports/` — every one of the 38 files this record's evidence
   diffed — gets a plain `python3 layout/verify.py --write` and a commit.
   Per the measured evidence above, this is refreshing metadata
   (`provenance.deck.content_hash`/`released`, `netlist_sha256`) and an
   additive, empty-for-this-repository JSON field, not re-deriving any
   verdict — the diff is bounded and already known, not a re-verification
   in the sense Alternative B's "cost" framing implied.
3. `layout/reports/environment.json` gets the same `--write` refresh, so
   `klt_origin.commit` reads `c903103cba9e...` (or later), matching what
   is actually pinned.
4. `layout/floorplan/reports/` gets whatever `python3
   layout/floorplan/floorplan.py --write` produces under the new pin —
   expected to be a no-op or near-no-op on content, since those reports
   already carry `provenance.deck.content_hash: sha256:36ed3624...`, the
   same hash this record measured live under `c903103cba9e` — but this must
   be **run and confirmed**, not assumed, including the composed/ring-fit
   checks this record's own evidence-gathering did not finish measuring
   (see "What was not measured" above).
5. `provenance.deck.released` moving from `true` to `false` across every
   committed report is an accepted, disclosed consequence (see
   Consequences), not something this decision is obligated to make `true`
   again — `released` tracks the upstream tool's own release cadence, which
   this repository does not control.

## Alternatives considered

### A. Regenerate `layout/floorplan/reports/` under the currently-pinned `3fbb4478e3017c8d8580fba4feb08bc386b4c925`

- **What**: keep `pdk-nightly.yml`'s existing pin as the one normative
  build, and re-run #226's floorplan/routing regeneration under it instead,
  so every committed report in the repository (`layout/reports/` and
  `layout/floorplan/reports/` alike) is written against the same reference.
- **Why plausible**: it is the option that changes the fewest files today —
  no CI workflow edit, no re-verification of `layout/reports/` — and it
  keeps "one pin, one source of truth" as a standing invariant rather than
  something re-derived after the fact.
- **Why rejected**: the cost/benefit this alternative's own framing in #230
  relied on ("keeps a single pin as the one source of truth... avoids
  re-verifying the rest of `layout/reports/`") is exactly the claim this
  record's measured evidence weighs against. Re-verifying the rest of
  `layout/reports/` against the newer build turns out to be low-cost and
  low-risk — zero verdicts moved across all 13 fixtures, confirmed above —
  while regenerating `layout/floorplan/reports/` under the *older* build is
  the higher-risk, unmeasured direction: it means re-running #226's
  composed-region routing/DRC/LVS work under a build that is not the one it
  was verified against, with no evidence gathered here (or anywhere else on
  record) that the older build's composed-floorplan checks even produce the
  same result. Choosing this alternative would discard the already-reproduced
  #226 evidence in exchange for re-deriving it against a build 101 commits
  behind current upstream, for a "keep one pin fixed" property that #230's
  own evidence shows is not actually threatened by moving forward instead.

### B. Leave the decision open and file a CI gate only (do nothing about the drift itself)

- **What**: close #230 by pointing at #227's CI-gate work (closed, PR #235
  merged) and leave the pin/report mismatch itself unresolved, on the
  reasoning that the gate now makes the drift visible so it is no longer
  silent.
- **Why plausible**: #227's own scope note says the CI-gate addition is
  independent of which side of this decision is taken, and it is already
  done — the temptation is to treat "now detectable" as "handled."
- **Why rejected**: #227's gate cannot actually run yet. The four most
  recent `pdk-nightly.yml` runs (2026-09-10 through 2026-09-14, confirmed
  via `gh run list --workflow=pdk-nightly.yml`) all fail earlier, at an
  unrelated "Digital synthesis staleness guard" step, so the floorplan gate
  step itself shows as skipped in each — the drift this record exists to
  resolve has not yet turned the nightly job red even once. Leaving the
  decision unmade means the eventual first real gate failure (once the
  unrelated staleness-guard failure is fixed) lands on whoever is debugging
  CI that day, with no ratified answer for which side is normative. That is
  the out-of-band, undocumented judgment call #230 was filed specifically to
  avoid.

## Consequences

- **Positive**:
  - The nightly pin becomes true of the evidence that is already committed,
    rather than the reverse: `layout/floorplan/reports/` stops being the one
    report set built against an un-pinned, un-cited upstream commit.
  - The already-reproduced #226 floorplan/routing evidence is kept rather
    than discarded and re-derived under an older build with no measured
    reason to expect the same result.
  - The actual cost of moving the pin forward is now measured, not assumed:
    zero verdict changes across all of `layout/reports/`'s 13 fixtures,
    confirmed by running `layout/verify.py` under both builds and diffing
    the stable JSON.

- **Negative / accepted cost**:
  - `provenance.deck.released` flips from `true` to `false` on every
    committed `layout/reports/` file once regenerated under `c903103cba9e`
    — this repository's evidence base moves further from the upstream
    tool's last tagged release, a direction with no obvious ceiling until
    upstream cuts a new release past `v0.2.0`.
  - `layout/floorplan/floorplan.py`'s own composed/ring-fit checks were
    **not** re-confirmed under the new pin by this record (see "What was
    not measured" in Context) — the follow-up work owes that confirmation
    before treating the re-pin as fully verified, not just the mechanical
    file changes.
  - Every `extract.json` under `layout/reports/` gains a currently-inert
    `instance_path: []` field on every device entry. It carries no
    information today (this repository's extracted fixtures are all flat),
    but it is upstream schema surface this repository has not yet had a
    reason to use.

- **Follow-up required** (not performed by this record or its PR):
  - Move `.github/workflows/pdk-nightly.yml`'s `klayout-tools` pin to
    `c903103cba9ef3b87f18c0361fb847612df5c7d9` or later, with the dated
    comment block this file's existing pin history already establishes as
    convention.
  - Regenerate `layout/reports/` via `python3 layout/verify.py --write` and
    commit the (bounded, already-diffed) result.
  - Regenerate `layout/floorplan/reports/` via `python3
    layout/floorplan/floorplan.py --write`, budgeting real wall-clock time
    for it (this record's own attempt did not finish in ~25 minutes under
    concurrent host load; DR-0025 discloses ~19.5 minutes for a related,
    more expensive `--parasitics` run on a less loaded host) — and treat a
    clean pass as the actual confirmation this record's evidence stops
    short of providing.
  - Confirm `layout/reports/environment.json`'s `klt_origin.commit` reads
    the new pin after the `--write` runs above.

- **Revisit if**: upstream lands a klayout-tools commit between `c903103cba9e`
  and whatever the pin eventually moves to that changes a verdict this
  record found unchanged (a new DRC/LVS rule, a device-recognition change,
  or anything else this record's diff did not have to account for because
  it did not occur across these 101 commits) — the next re-pin should
  re-run this same `layout/verify.py`-under-both-builds comparison rather
  than assume the zero-verdict-change result found here still holds.
