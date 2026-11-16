# Audit: content lost in conflict-resolution merges `a395d6e1`, `742bb2af` and `d870871b` (2026-11-15)

Three hand-resolved merges on `main`'s history are known to have discarded
finished work without anything failing: the tapcell placement (#717) and the
`6.analog` manifest citation (#885). This note is a read-only audit of exactly
those three merges — `a395d6e1`, `742bb2af` and `d870871b` — that lists every
candidate path, classifies each as `lost` or `intended`, and records why no
existing check caught the losses. **It restores nothing and changes no code,
spec row, or evidence record.**

**Provenance.** Produced against `origin/main` at
`dd30f2dfb8d4505646ed72c3acff17a3d35a7484` on 2026-11-15 with git 2.43.0.
The three merges are immutable history, so the per-merge scan output (the
candidate sets and blob ids) will not drift. The "absent from `origin/main`
today" and "restored" figures *do* drift as restoring work lands: between the
curation scan of issue #887 (`cce9a1aa`, 2026-11-14) and this audit, #885
restored the `6.analog` citation (PR #911, merged 2026-11-15T02:08:25Z).
Re-run the recipe in § Reproduction before relying on any status figure.

## The two known losses

- **`layout/digital/build.py` under `a395d6e1`.** `a395d6e1` ("Merge
  origin/main into feature/issue-734") kept the `origin/main` side. Its first
  parent `510b899e` carried `8939b542`, which added `TAPCELL_DISTANCE_UM` and
  re-placed the digital block at a 30 um tapcell pitch (#717). As of
  `origin/main` @ `dd30f2df`, `layout/digital/build.py` contains no
  `TAPCELL_DISTANCE_UM` and
  [`layout/digital/reports/tap-distance.json`](../layout/digital/reports/tap-distance.json)
  still reads `"verdict": "fail"`.
- **`signoff/block-manifest.json` under `742bb2af`.** `742bb2af` ("Merge
  origin/main into feature/issue-656") lists this file among its conflicts and
  produced a manifest without the `evidence.6.analog.file` citation that its
  own first parent `c3ed2b9f` had added (commit `c3ed2b9f`, "feat(signoff):
  ratify mismatch MC limits and cite a klt yield report as item 6 analog",
  2026-11-09 18:33). The issue #887 body originally attributed this loss to
  `d870871b`; that was wrong — see § `d870871b` below.

Both were found by accident, and each merge touched many other files. Nothing
established that these were the only losses; the scans below make the full
candidate set explicit.

## Detection: two tests, and why both are needed

- **Test (a) — blob identity.** The merge result equals one parent's blob at
  a path while the other parent changed that path relative to the merge base
  (and the two parents' blobs differ). This catches take-one-side-wholesale
  resolutions. It finds all 236 discarded paths of `a395d6e1` — and *zero*
  for the other two merges.
- **Test (b) — committed result vs git's own auto-merge.** Compare the
  committed merge result at each path with `git merge-tree --write-tree`'s
  auto-merge of the same two parents. Every hand-decided path differs from
  the auto-merge (conflicted paths get conflict-marker blobs; cleanly
  auto-merged paths that were nonetheless hand-edited differ too), so the
  differing set is exactly the set of paths a human decided. It finds the
  10 and 11 hand-resolved paths of `742bb2af` and `d870871b`, including the
  `6.analog` loss — which test (a) provably cannot see: the blend result blob
  `28b989a8` equals neither parent (`aa112235`, `4b33e17e`) nor the base
  (`4cd8bb1b`).

Neither test alone finds both known losses, so both are required. For
`a395d6e1` the two tests return the *same* 236 paths (verified set-identical
on 2026-11-15).

### Exact commands

```sh
git fetch origin

# Test (a): blob-identity scan — result equals one parent, other side changed.
scan() {
  M="$1"
  P1=$(git rev-parse "$M^1"); P2=$(git rev-parse "$M^2")
  B=$(git merge-base "$P1" "$P2")
  blob() { git rev-parse --quiet --verify "$1:$2" 2>/dev/null || echo MISSING; }
  { git diff --name-only "$B" "$P1"; git diff --name-only "$B" "$P2"; } \
    | sort -u | while read -r p; do
      bm=$(blob "$M" "$p"); b1=$(blob "$P1" "$p")
      b2=$(blob "$P2" "$p"); bb=$(blob "$B" "$p")
      if   [ "$bm" = "$b1" ] && [ "$b2" != "$bb" ] && [ "$b1" != "$b2" ]; then
        printf 'DISCARDED-P2\t%s\n' "$p"
      elif [ "$bm" = "$b2" ] && [ "$b1" != "$bb" ] && [ "$b1" != "$b2" ]; then
        printf 'DISCARDED-P1\t%s\n' "$p"
      fi
    done
}
for m in a395d6e1 742bb2af d870871b; do echo "== $m"; scan "$m"; done

# Test (b): committed result vs git's own auto-merge of the same parents.
for m in a395d6e1 742bb2af d870871b; do
  t=$(git merge-tree --write-tree "$m^1" "$m^2" | head -1)
  echo "== $m"; git diff --name-only "$t" "$m"
done

# Attribute each discarded path to the commit that made the change
# (last commit touching the path on the discarded side).
git log -1 --format=%h "$B".."$P1" -- "<path>"

# Single merge base? (all three merges here: yes, exactly one)
git merge-base --all "$m^1" "$m^2"

# Evidence-key count of signoff/block-manifest.json at each of the five
# revisions in the seeded-case table (expected: 19 20 19 19 20).
for r in 0acf3c5a c3ed2b9f d225f324 742bb2af dd30f2df; do
  git show "$r:signoff/block-manifest.json" |
    python3 -I -c 'import json,sys; print(len(json.load(sys.stdin)["evidence"]))'
done

# Is a candidate path present on origin/main today?
git rev-parse --quiet --verify "origin/main:<path>"

# Was the discarded change net-new on the branch (absent at the merge base)?
git rev-parse --quiet --verify "<base>:<path>"
```

**Soundness notes.** A path that one parent deleted and the other changed,
and a path absent at the merge base, both classify without crashing the scan:
the `MISSING` sentinel makes the comparisons simply fail their branches. A
merge with more than one merge base would need `--all` handling; all three
merges here have exactly one — `d1ce0dd8` (`a395d6e1`), `0acf3c5a`
(`742bb2af`), `884437d8` (`d870871b`) — so the single-base form is sound for
this note and must not be generalised without change. `git merge-tree
--write-tree` requires git >= 2.38.

## Findings

### `a395d6e1` — 236 candidate paths (test (a): 236, test (b): 236, identical sets)

All 236 are `DISCARDED-P1`: the merge result took the `origin/main` side and
discarded the feature-branch side. The branch side's 236 paths come from four
commits (attribution = last commit touching the path in
`d1ce0dd8..a395d6e1^1`):

| Originating commit | Paths | Subject | Classification |
|---|---:|---|---|
| `8939b542` | 17 | feat(digital): pass a tapcell pitch to place-and-route and re-place at 30 um | **lost** |
| `cf37931d` | 191 | evidence: re-run digital STA, activity and post-route records on the 30 um tapcell geometry | **lost** |
| `3c449eae` | 16 | evidence: re-mint the digital-sta-power records after the floorplan recompose | **lost** |
| `0ff3a33e` | 12 | Merge origin/main into feature/issue-718 (Doctor: update before push) | **intended** |

**The seeded case.** `layout/digital/build.py` sits in the `8939b542` group
(`DISCARDED-P1`): main's copy has no `TAPCELL_DISTANCE_UM` today and
[`layout/digital/build.py`](../layout/digital/build.py) still drives
place-and-route at the pre-tapcell pitch. **Lost. Restored by #717 (open PR
`feature/issue-717` → `main`, PR #720).**

**The lost groups (224 paths, named in Appendix A).** 177 of them are absent
from `origin/main` @ `dd30f2df` today — 31 evidence records under
`sim/records/` and 146 raw-output files under `sim/records/raw/`; the other
177-`absent`-complement (47 paths in these groups) exist on main only as
later, regenerated versions without the discarded content. The discarded
records document the 30 um tapcell geometry — work main never adopted. Two
things make the restoration path concrete rather than hypothetical:

- **All 236 discarded paths exist, blob-identical to the discarded versions,
  on `origin/feature/issue-717`** (verified 2026-11-15). The open PR #720
  therefore carries the complete discarded content, including the
  `cf37931d`/`3c449eae` evidence. Note for its reviewers: the branch also
  carries stale copies of the 59 candidate paths main has since regenerated
  (e.g. `build.py`, `README.md`, the `signoff/` evidence family), so its
  merge will have to take main's side again for exactly those — the same
  failure mode this note documents.
- **#734** ("Refresh extracted/routed ro-array startup records on the 30 um
  tapcell geometry", closed 2026-11-04) was the deliverable issue for the
  `cf37931d`/`3c449eae` records; being closed, it restores nothing. **No open
  issue is dedicated to the records themselves** — the open restorers of this
  content are #717 (PR #720, geometry + records) and #718 (open, "Refresh
  sim/signoff evidence after digital tapcell re-placement", the post-landing
  evidence refresh). If PR #720 were abandoned, no open issue would restore
  the 177 absent paths.

**The intended group (`0ff3a33e`, 12 paths: `README.md`,
`signoff/block-manifest.json`, the eight `signoff/evidence/{inventory,t1-item}-{9,10}-{analog,digital}.json`,
`signoff/records/t1-tier-report.json`, `sim/tools/verify_report_host_paths.py`).**
These were the branch's own hand-blended Doctor-sync reconciliation of an
older `main`, discarded four days later when `a395d6e1` took main's newer
side. The blend's values are tree-specific, not portable content, and main
has since regenerated all twelve paths itself: the README record count
(branch 1122, main-side 1092 at the time; main today 1301), the README power
row (branch 758.7 µW / 2.32 µA from the branch's recomposed floorplan; main
today 748.2 µW / 2.138 µA from its own), the
`verify_report_host_paths.py` exemption hash (`a4917849…` matched the
branch's `gate_klt_response.json`; main's `af63e519…` matches main's), and
the evidence `files`/`content_hash`/`items` values. Nothing unique was
identified in the discarded blobs, and neither side of `0ff3a33e` carried the
`6.analog` key (verified 0 matches on `0ff3a33e^1`, `0ff3a33e`, `0ff3a33e^2`,
`510b899e`, `a395d6e1`, `a395d6e1^2`). **Intended.**

### `742bb2af` — 10 candidate paths (test (a): 0, test (b): 10)

All ten are hand-blended: the committed result equals neither parent. P1 =
`c3ed2b9f` (issue-656 side), P2 = `d225f324` (main side), base = `0acf3c5a`.
The P1-side changes were made by `c3ed2b9f`; the P2-side changes by
`ebfca9de` ("Merge origin/main into feature/issue-790 (Judge: regenerate
signoff inventories, README count 1179)") except `t1-tier-report.json`
(`233b1617`).

| Path | Discarded change made by | Classification |
|---|---|---|
| `signoff/block-manifest.json` | `c3ed2b9f` (P1 side) | **lost** — restored by #885 |
| `signoff/evidence/inventory-10-analog.json` | both sides | intended |
| `signoff/evidence/inventory-10-digital.json` | both sides | intended |
| `signoff/evidence/inventory-9-analog.json` | both sides | intended |
| `signoff/evidence/inventory-9-digital.json` | both sides | intended |
| `signoff/evidence/t1-item-10-analog.json` | both sides | intended |
| `signoff/evidence/t1-item-10-digital.json` | both sides | intended |
| `signoff/evidence/t1-item-9-analog.json` | both sides | intended |
| `signoff/evidence/t1-item-9-digital.json` | both sides | intended |
| `signoff/records/t1-tier-report.json` | both sides | intended |

**The seeded case — `signoff/block-manifest.json`.** Key-level comparison of
the five revisions. `Evidence keys` is the number of top-level keys of the
manifest's `evidence` object (`len(manifest["evidence"])`), re-derived by the
`evidence_keys` loop in § Exact commands:

| Revision | Role | Blob | `evidence.6.analog.file` present | Evidence keys |
|---|---|---|---|---|
| `0acf3c5a` | merge base | `4cd8bb1b` | no | 19 |
| `c3ed2b9f` | parent 1 | `aa112235` | **yes** | 20 |
| `d225f324` | parent 2 | `4b33e17e` | no | 19 |
| `742bb2af` | merge result | `28b989a8` | **no** | 19 |
| `origin/main` @ `dd30f2df` | today | `056df580` | yes (restored) | 20 |

The blend dropped the one *structural* addition P1 carried — the
`evidence.6.analog.file` citation — while taking P2's regenerated shape for
the rest. **Lost; restored by #885** (closed; fix landed 2026-11-15 as
`a5331fcc` via PR #911, "fix(signoff): cite the committed klt yield response
as 6.analog again").

**The intended nine.** For each, the blend re-derived tree-specific values
(the `files` lists, `cold_start_docs`, `provenance.input.content_hash`,
`items`) rather than taking either parent's: both sides had regenerated
evidence for their own trees, and the committed values describe the merged
tree. No key present in a parent is absent from the blend (key counts equal
the base's on all nine), so nothing structural was dropped, and main has
since regenerated every one of the ten paths again (none of the blend blobs
is main's blob today). **Intended.**

### `d870871b` — 11 candidate paths (test (a): 0, test (b): 11)

Same-day Doctor merge over the same conflict family ("Merge origin/main into
feature/issue-808"). P1 = `ac1e5825`, P2 = `d4438946`, base = `884437d8`. The
P1-side changes were made by `ac1e5825`; P2-side by `d5236e8d`, except
`README.md` (P1-side `2e63db7d`, P2-side `d5236e8d`).

| Path | Discarded change made by | Classification |
|---|---|---|
| `README.md` | `2e63db7d` (P1) / `d5236e8d` (P2) | intended — hand count reconciliation, verified correct |
| `signoff/block-manifest.json` | `ac1e5825` (P1) / `d5236e8d` (P2) | intended — carrier of the 742bb2af loss, not its cause |
| `signoff/evidence/inventory-10-analog.json` | both sides | intended |
| `signoff/evidence/inventory-10-digital.json` | both sides | intended |
| `signoff/evidence/inventory-9-analog.json` | both sides | intended |
| `signoff/evidence/inventory-9-digital.json` | both sides | intended |
| `signoff/evidence/t1-item-10-analog.json` | both sides | intended |
| `signoff/evidence/t1-item-10-digital.json` | both sides | intended |
| `signoff/evidence/t1-item-9-analog.json` | both sides | intended |
| `signoff/evidence/t1-item-9-digital.json` | both sides | intended |
| `signoff/records/t1-tier-report.json` | both sides | intended |

- **`signoff/block-manifest.json` did **not** lose content here.** Both of its
  parents already lack the `6.analog` key (verified: 0 matches at
  `ac1e5825` and `d4438946`; `d870871b`'s result also 0). The merge carried
  the `742bb2af` loss forward but did not cause it — this corrects issue
  #887's original attribution, first reported by the Curator of #885
  (comment of 2026-11-14T04:02:51Z) and re-verified independently here.
- **`README.md`'s hand edit was a correct reconciliation.** The blend bumped
  the record count from P1's 1259 to 1260; the merged tree at `d870871b`
  really contains 1260 record files under `sim/records/` (P1 had 1259, P2 had
  1226 — P2's stale 1226 prose was what the hand edit corrected).
- The nine shared signoff paths classify as under `742bb2af`: tree-specific
  regeneration blends, nothing structural dropped, all superseded again by
  main's own later regeneration.

## Why no existing check caught these

- **`sim/tools/verify_evidence_history.py` (the `check:evidence-history`
  gate) compares HEAD against the merge-base of the base and HEAD** — the two
  endpoint trees, not the intermediate history. A record added on a branch
  (`cf37931d`, `3c449eae`) and then dropped by a conflict-resolution merge on
  that *same branch* (`a395d6e1`) is a net no-op across those endpoints, so
  the 177 absent evidence paths never appeared in any diff the gate saw. The
  append-only guarantee covers evidence already on `main`; it does not cover
  evidence that never arrives.
- **The `742bb2af`/`d870871b` family is not under `sim/records/` at all.**
  `signoff/block-manifest.json` and `signoff/evidence/` are outside
  `verify_evidence_history.py`'s prefixes (`sim/records/`,
  `manifests/artifacts/*.manifest.json`), so no history check applies to them
  whatsoever.
- **The current-tree checks validate consistency, not completeness.**
  `verify_record_checksums.py` and `signoff/check.py` check that the
  committed tree is internally consistent — a thinner-but-consistent manifest
  (19 evidence keys, all hashes matching) passes, and did. Nothing fails on a
  *missing* citation; #885 exists precisely because a human noticed.
- **`corpus_counts.py`** holds README's prose totals (decision records,
  characterization summaries, evidence-record counts) to the tree — it
  catches count drift like the `README.md` case at `d870871b`, not content
  loss, and it reads only the current tree.
- No other gate in `check:ci` inspects merge topology or parent-vs-result
  content.

Fixing any of these blind spots is out of scope for this note (issue #887,
§ Out of Scope); file separately if warranted.

## Reproduction

Run the § Exact commands block against any checkout with full history. As of
this note (2026-11-15, `origin/main` @ `dd30f2df`) the expected output is:

| Merge | Test (a) paths | Test (b) paths | Sets identical? |
|---|---:|---:|---|
| `a395d6e1` | 236 | 236 | yes (all `DISCARDED-P1`) |
| `742bb2af` | 0 | 10 | n/a |
| `d870871b` | 0 | 11 | n/a |

Additional verified figures: 177 of `a395d6e1`'s 236 are absent from
`origin/main` @ `dd30f2df` (146 under `sim/records/raw/`, 31 evidence records
under `sim/records/`); all 177 were net-new on the branch (absent at merge
base `d1ce0dd8`); all 236 exist blob-identical on `origin/feature/issue-717`.
Each merge has exactly one merge base. The per-merge candidate sets and blob
ids are immutable; the presence/restoration figures drift as restoring work
lands — re-run before relying on them.

## Appendix A: the 236 candidate paths of `a395d6e1`, by originating commit

Attribution = last commit touching the path in `d1ce0dd8..a395d6e1^1`.
"On `origin/main` 2026-11-15" is presence at `dd30f2df`. The `0ff3a33e`
group is classified **intended** (§ Findings); the other three groups are
**lost**, restored in blob-identical form on `origin/feature/issue-717`
(PR #720).

#### Commit `8939b542` — 17 paths

| Path | Discarding commit | On `origin/main` 2026-11-15 |
|---|---|---|
| `layout/digital/README.md` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/build.py` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/lvs.py` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/reports/drc.json` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/reports/erc-supply.json` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/reports/lvs.json` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/reports/place_and_route.json` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/reports/sdf_export.json` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/reports/tap-distance.json` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/trng_top.def` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/trng_top.extracted.spice` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/trng_top.gds` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/trng_top.lvs_reference.spice` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/trng_top.pnr.v` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/digital/trng_top.sdf` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/tests/test_digital_build_checks.py` | `8939b542` | present, regenerated on main without the discarded content |
| `layout/tests/test_digital_lvs_reference.py` | `8939b542` | present, regenerated on main without the discarded content |

#### Commit `cf37931d` — 191 paths

| Path | Discarding commit | On `origin/main` 2026-11-15 |
|---|---|---|
| `docs/chipalooza/challenge-3-proposal.md` | `cf37931d` | present, regenerated on main without the discarded content |
| `docs/higher-rate-source-options-study.md` | `cf37931d` | present, regenerated on main without the discarded content |
| `docs/spec-row-status.md` | `cf37931d` | present, regenerated on main without the discarded content |
| `layout/floorplan/reports/compose.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `layout/floorplan/reports/erc-supply.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `layout/floorplan/reports/floorplan.drc.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `layout/floorplan/reports/interregion.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `layout/floorplan/reports/ring_fit.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `layout/floorplan/trng_floorplan.gds` | `cf37931d` | present, regenerated on main without the discarded content |
| `signoff/README.md` | `cf37931d` | present, regenerated on main without the discarded content |
| `signoff/evidence/characterization-analog.generic.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `signoff/evidence/characterization-digital.generic.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `signoff/evidence/digital-sta/comparison.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `signoff/evidence/digital-sta/klt_sta_response.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `signoff/evidence/inventory-2-analog.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `signoff/evidence/inventory-2-digital.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `signoff/evidence/post-route/gate_klt_response.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `signoff/evidence/post-route/publication.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `signoff/evidence/t1-item-2-analog.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `signoff/evidence/t1-item-2-digital.json` | `cf37931d` | present, regenerated on main without the discarded content |
| `sim/characterization-analog-summary.md` | `cf37931d` | present, regenerated on main without the discarded content |
| `sim/characterization-digital-activity-power.md` | `cf37931d` | present, regenerated on main without the discarded content |
| `sim/characterization-digital-sta-area-power.md` | `cf37931d` | present, regenerated on main without the discarded content |
| `sim/characterization-liveness-sampler-active-power.md` | `cf37931d` | present, regenerated on main without the discarded content |
| `sim/records/2026-10-30-digital-sta-activity-01.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-02.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-03.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-04.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-05.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-06.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-07.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-08.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-09.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-10.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-11.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-12.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-13.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-14.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-digital-sta-activity-15.md` | `cf37931d` | absent |
| `sim/records/2026-10-30-trng-top-post-route-01.md` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-01/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-01/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-01/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-01/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-01/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-02/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-02/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-02/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-02/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-02/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-03/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-03/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-03/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-03/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-03/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-04/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-04/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-04/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-04/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-04/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-05/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-05/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-05/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-05/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-05/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-06/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-06/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-06/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-06/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-06/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-07/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-07/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-07/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-07/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-07/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-08/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-08/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-08/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-08/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-08/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-09/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-09/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-09/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-09/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-09/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-10/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-10/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-10/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-10/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-10/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-11/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-11/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-11/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-11/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-11/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-12/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-12/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-12/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-12/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-12/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-13/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-13/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-13/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-13/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-13/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-14/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-14/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-14/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-14/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-14/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-15/activity-manifest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-15/observed.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-15/observed.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-15/uniform.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-activity-15/uniform.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-01/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-01/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-01/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-01/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-02/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-02/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-02/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-02/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-03/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-03/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-03/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-03/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-04/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-04/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-04/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-04/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-05/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-05/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-05/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-05/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-06/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-06/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-06/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-06/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-07/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-07/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-07/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-07/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-08/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-08/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-08/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-08/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-09/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-09/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-09/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-09/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-10/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-10/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-10/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-10/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-11/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-11/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-11/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-11/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-12/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-12/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-12/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-12/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-13/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-13/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-13/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-13/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-14/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-14/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-14/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-14/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-15/constraint.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-15/constraint.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-15/ratified-rate.log` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-digital-sta-power-15/ratified-rate.tcl` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-trng-top-post-route-01/environment.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-trng-top-post-route-01/gate_comparison.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-trng-top-post-route-01/gate_klt_response.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-trng-top-post-route-01/gate_request.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-trng-top-post-route-01/gate_transcript_digest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-trng-top-post-route-01/rtl_comparison.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-trng-top-post-route-01/rtl_klt_response.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-trng-top-post-route-01/rtl_request.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-trng-top-post-route-01/rtl_transcript_digest.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-trng-top-post-route-01/sources.json` | `cf37931d` | absent |
| `sim/records/raw/2026-10-30-trng-top-post-route-01/verdict.json` | `cf37931d` | absent |
| `sim/tb/digital-sta-power/max_transition_probe.py` | `cf37931d` | present, regenerated on main without the discarded content |
| `sim/tests/test_analog_characterization_summary.py` | `cf37931d` | present, regenerated on main without the discarded content |
| `sim/tests/test_chipalooza_table_consistency.py` | `cf37931d` | present, regenerated on main without the discarded content |
| `sim/tests/test_report_host_paths.py` | `cf37931d` | present, regenerated on main without the discarded content |
| `sim/tools/digital_corner_characterization.py` | `cf37931d` | present, regenerated on main without the discarded content |

#### Commit `3c449eae` — 16 paths

| Path | Discarding commit | On `origin/main` 2026-11-15 |
|---|---|---|
| `sim/characterization-digital-supply-ir-drop.md` | `3c449eae` | present, regenerated on main without the discarded content |
| `sim/records/2026-10-30-digital-sta-power-01.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-02.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-03.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-04.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-05.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-06.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-07.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-08.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-09.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-10.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-11.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-12.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-13.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-14.md` | `3c449eae` | absent |
| `sim/records/2026-10-30-digital-sta-power-15.md` | `3c449eae` | absent |

#### Commit `0ff3a33e` — 12 paths

| Path | Discarding commit | On `origin/main` 2026-11-15 |
|---|---|---|
| `README.md` | `0ff3a33e` | present, regenerated on main without the discarded content |
| `signoff/block-manifest.json` | `0ff3a33e` | present, regenerated on main without the discarded content |
| `signoff/evidence/inventory-10-analog.json` | `0ff3a33e` | present, regenerated on main without the discarded content |
| `signoff/evidence/inventory-10-digital.json` | `0ff3a33e` | present, regenerated on main without the discarded content |
| `signoff/evidence/inventory-9-analog.json` | `0ff3a33e` | present, regenerated on main without the discarded content |
| `signoff/evidence/inventory-9-digital.json` | `0ff3a33e` | present, regenerated on main without the discarded content |
| `signoff/evidence/t1-item-10-analog.json` | `0ff3a33e` | present, regenerated on main without the discarded content |
| `signoff/evidence/t1-item-10-digital.json` | `0ff3a33e` | present, regenerated on main without the discarded content |
| `signoff/evidence/t1-item-9-analog.json` | `0ff3a33e` | present, regenerated on main without the discarded content |
| `signoff/evidence/t1-item-9-digital.json` | `0ff3a33e` | present, regenerated on main without the discarded content |
| `signoff/records/t1-tier-report.json` | `0ff3a33e` | present, regenerated on main without the discarded content |
| `sim/tools/verify_report_host_paths.py` | `0ff3a33e` | present, regenerated on main without the discarded content |

## Appendix B: the candidate paths of `742bb2af` and `d870871b`

Both sets were flagged by test (b) only (test (a) returns 0 for both merges:
every path is a hand blend, equal to neither parent). Dispositions per
§ Findings. The `742bb2af` set is an exact subset of the `d870871b` set plus
`README.md` (10 shared paths).

| Path | In `742bb2af` set | In `d870871b` set | Classification |
|---|---|---|---|
| `README.md` | — | yes | intended (count reconciliation) |
| `signoff/block-manifest.json` | yes — **lost**, restored by #885 | yes — intended (carrier) | see § Findings |
| `signoff/evidence/inventory-10-analog.json` | yes | yes | intended |
| `signoff/evidence/inventory-10-digital.json` | yes | yes | intended |
| `signoff/evidence/inventory-9-analog.json` | yes | yes | intended |
| `signoff/evidence/inventory-9-digital.json` | yes | yes | intended |
| `signoff/evidence/t1-item-10-analog.json` | yes | yes | intended |
| `signoff/evidence/t1-item-10-digital.json` | yes | yes | intended |
| `signoff/evidence/t1-item-9-analog.json` | yes | yes | intended |
| `signoff/evidence/t1-item-9-digital.json` | yes | yes | intended |
| `signoff/records/t1-tier-report.json` | yes | yes | intended |
