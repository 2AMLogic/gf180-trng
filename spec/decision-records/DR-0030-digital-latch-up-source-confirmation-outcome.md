---
dr: DR-0030-digital-latch-up-source-confirmation-outcome
title: The controlled GF180MCU DRM was not obtainable; the LU.3/LU.4 MV-column reading stays an unconfirmed working interpretation, and the failing evidence stays intact
status: Proposed
date: 2026-10-11
deciders: Builder of issue #486 (source-confirmation investigation only). Not an operator ratification and not a source confirmation. No ratified requirement is relaxed.
supersedes: n/a
superseded_by: n/a
related: "#486 (this investigation; criterion stays unresolved), #449 (original defect; stays open), #487 (placement remedy; not touched here), DR-0029 (amended by this record, not superseded); layout/digital/tap-distance-spec.json; layout/digital/README.md"
---

# DR-0030: Source-confirmation outcome for the digital LU.3/LU.4 device-class column

## Status

- 2026-10-11: Proposed. This record **amends** DR-0029 by recording the result
  of the source search DR-0029 listed as its follow-up (a). It does not
  supersede DR-0029: DR-0029's decision, its measurement provenance and its
  "Evidence gap" section remain in force and unedited. The source-confirmation
  criterion of #486 is **not met**.
- 2026-10-11 (second pass): re-verified the revisit triggers after the
  open-PDK repositories moved to the FOSSi Foundation. No revision-bearing
  source appeared anywhere in the moved ecosystem; the design-manual content
  is byte-identical to the checksums below. See "Re-check (2026-10-11, second
  pass)". The criterion is still **not met**.

## Context

DR-0029 applied the MV column (15 um) of DRM section 14.3.1 rules LU.3/LU.4 to
the 9t 5 V digital block, on the basis of library identity and DualGate
coverage, and recorded that no controlled DRM was consulted. #486 asks for a
revision-bearing source, the section/table, and how it assigns LV/MV to
dual-gate cells. This record documents what a search of official, publicly
retrievable sources found, on 2026-10-11, and what it does and does not
establish.

## Sources attempted

All retrieved 2026-10-11 from public endpoints, without credentials.

| Source | Result | Kind |
|---|---|---|
| `https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_3_1.html` (28,760 bytes, SHA-256 `171588c71102f5df4c4dc4fe65a454fa42684f0e651d8519c418abe81a730853`, identical to the 2026-10-10 retrieval) | HTTP 200. No revision identifier in the page. | **Unversioned rendered page** (the `latest` build) |
| `https://github.com/google/gf180mcu-pdk`, branch `main`, HEAD `de3240d7529a6970437ac3344820aaae7839f215` (committed 2023-05-31T20:09:57Z); snapshot `codeload.github.com/.../tar.gz/refs/heads/main`, 33,296,714 bytes, SHA-256 `d78a70b6fa2442b433949ea18c639fef1a6dd296942cdf0fae54fe556b085b3d` | Retrieved; source of the rendered docs (`docs/physical_verification/design_manual/`). | Open-PDK **transcription** of the DRM, pinned to a commit |
| GitHub releases of `google/gf180mcu-pdk` (`/releases`) | Empty list. The only tag is `v0.0.0` (`53e4356d8ab3a9eee9e68e157d797d79bb097106`); it carries no DRM revision. | none |
| Read the Docs PDF/HTML-zip downloads (`/_/downloads/en/latest/pdf/`, `.../htmlzip/`) | HTTP 404 | none |
| The controlled GlobalFoundries DRM (a numbered, dated document) | Not publicly retrievable; not obtained. | **Controlled**, unavailable |

Artifact checksums of the pinned `main` snapshot's relevant files:

| File (under `docs/physical_verification/design_manual/`) | SHA-256 |
|---|---|
| `drm_14_3_1.rst` | `ccd536ae6b58a175851c62e464e2030fb271f55c8df0e8c609a9cc9f7846e5e6` |
| `tables_clear/55_Latch-up_152.csv` (LU.1-LU.10 table) | `50f0f0274bafb7109504ed9f0c9febb3b956cce2fdc08eff8bcea291fb54d596` |
| `tables_clear/02_Process_Identification7.csv` (DRM 2.7) | `215a57055b83146f52e473615d34bae219125fd642d401addcb20be3d55d891c` |
| `tables_clear/01_Document_rev2_3_4.csv` (revision history) | `165851db9c1da4f4548170532bd8f515c30a25e1ee75006e68c18040af49c087` |
| `images/Latch-up1.png` / `images/Latch-up2.png` | `6a057038bf4be0bf7fdc09606d34b285dc2947c252e3ee925f152781a3506f45` / `60d3af6317d2506066d8b32d5026b83ddd2cc014754b0930fd425d9d8826ac6c` |

## What the sources show

1. **A numbered revision history exists, but only inside the repository.**
   `tables_clear/01_Document_rev2_3_4.csv` lists "Document Revision" entries 1
   to 13 with changed sections; it is not included in any rendered page. It has
   no dates, no document number, and no revision stamp tied to a particular
   page. The last numbered entry (13) includes "Section 14.3.1: Modify LU.3 and
   LU.4 to define N/P tap by NWELL by adding in LU.1 & LU.2". This shows that
   the 14.3.1 text descends from a numbered DRM revision (most likely 13 or
   later; the file does not say which revision the transcription reproduces),
   and that LU.3/LU.4 were revised relative to earlier ones. It is **not** a
   controlled revision citation: no identifier, no date, no controlled-document
   number, and the transcription's fidelity to any revision is unstated.
2. **Device-class vocabulary.** DRM section 2.7 (the process-identification
   table) states "LV=3.3V, HV=5V or 6V" for the 0.18um 3.3V/(5V)6V processes.
   The latch-up table headers are `LV` and `MV`. No page in the pinned
   snapshot defines `MV`: a word search of the design-manual sources finds
   "MV" only as the latch-up table headers and the phrase "LV and MV" in rule
   headings (and "LV or MV area" in the Schottky diode section 10.14).
3. **DualGate semantics.** DRM rules DF.15a/DF.15b and DV.4 tie the Dualgate
   layer to 5V/6V operation ("NCOMP inside DNWELL and Dualgate ... can only be
   connected to 5V/6V VDD"; "Circuits covered by Dualgate layer will have 6V
   gate oxide"). So the DRM supports "DualGate marks 5V/6V devices".
4. **The LU.3/LU.4 table** (reproduced from the CSV above): both rules are
   headed "FOR LV and MV outside DNWELL". Distance: max Nwell tap space to
   every point on the boundary of PCOMP inside Nwell (LU.4), and max LVPWELL
   (Psub) tap outside DNWELL space to every point on the boundary of NCOMP
   outside NWELL/DNWELL (LU.3). Each applies "within 50um from" the subject
   diffusion, where y is the minimum NWELL to (NCOMP outside Nwell) space.
   Limits: y >= 2.0um gives LV 50 / MV 15; 1.0 <= y < 2.0um gives 30 / 15;
   y < 1.0um gives 15 / 15. MV is 15 um in every sub-case, so no clearance
   measurement is needed to apply the MV column. The LV column needs y.

## What is and is not established

Established by the sources above (all from the open-PDK transcription):

- The table text, columns, distance definition and limits recorded in DR-0029
  and in item 4 above.
- DualGate is the 5V/6V gate-oxide marker (item 3), and the process names the
  5V/6V class "HV" (item 2).

**Not established by any source obtained.** The inference is unchanged:

- That the table's `MV` column is the class that applies to 5 V/6 V DualGate
  devices. The table's header word `MV` is never defined; the DRM's own name
  for the 5V/6V class is `HV`. Reading `MV` as 5V/6V is plausible and is
  consistent with the table and with the 15 um strictness, but the text does
  not say it.
- How a layout decides the column for a device (by DualGate coverage of its
  gate, of its COMP, or of the tap).
- Whether a mixed-class neighbourhood (a tap and its subject in different
  classes) changes the limit; no applicability exclusions are stated.
- Whether the 9t 5 V library's cells are "MV" in the DRM's sense beyond their
  DualGate coverage, which the tool does verify.

The transcription is also undated against the controlled document, so it
cannot be shown to be the current revision.

## Decision

1. **The source-confirmation criterion of #486 stays unresolved.** A publicly
   retrievable, unversioned rendered page and a commit-pinned transcription are
   recorded; neither is a numbered controlled revision. This record does not
   present the MV reading as source-confirmed, and DR-0029's characterisation
   of it as an inference stands.
2. **No spec, measurement, test or report change.**
   `layout/digital/tap-distance-spec.json`, `layout/digital/tap_distance.py`,
   its tests and `layout/digital/reports/tap-distance.json` are unchanged. The
   MV column remains the working limit, the physical verdict remains `fail`
   (LU.4 49.727 um, LU.3 49.691 um against 15 um), and #449 stays open. Adopting
   the LV column would be a relaxation without source; the retrieved text gives
   no rule for doing so.
3. **Exact remaining access requirement.** One of: (a) the controlled
   GlobalFoundries GF180MCU Design Rule Manual, with its document number,
   revision and date, from a GlobalFoundries customer/foundry channel (access
   needs an account or contact that automation does not have); the needed
   passages are section 2.7 (process identification), the definition or legend
   for `LV`/`MV`, section 14.3.1 table LU.1-LU.4 and its figures, and the
   revision history; or (b) written confirmation from GlobalFoundries that the
   `MV` column of LU.3/LU.4 is the 5V/6V (DualGate) class and how mixed
   classes are treated. This is an operator/foundry-contact step, to be routed
   separately from the placement work in #487.
4. **Re-placement (#487) is unaffected** and may proceed under the stricter MV
   reading, which a controlled source could only confirm or loosen later.

## Alternatives considered

- **Treat the repository revision table as the controlled revision.** Rejected:
  it has no identifier tying it to a document, no dates, and is not rendered.
- **Infer the column from the HV/5V naming or from the DRC deck.** Rejected,
  as DR-0029 and the #486 clarification require: naming, supply voltage and a
  deck that has no LU.* rule are not source.
- **Switch to LV sub-case a).** Rejected: needs unmeasured clearance y and a
  source rule that does not exist in what was retrieved.

## Consequences

- The evidence gap in DR-0029 is narrowed (the section 2.7 HV wording and the
  DualGate semantics are now recorded) but not closed.
- No `sim/` records or derived reports are touched; `check:spec` corpus counts
  are unaffected.
- **Revisit if**: the controlled DRM or a foundry confirmation is supplied,
  whichever column it assigns; or the open-PDK documentation adds a revision
  stamp or a definition of `MV` (the watch point is now the FOSSi Foundation
  continuation, `fossi-foundation/gf180mcu-pdk` and its
  `globalfoundries-pdk-libs-*` repositories, supplanting the archived
  `google/gf180mcu-pdk`).

## Re-check (2026-10-11, second pass)

A second dispatch on #486 re-verified the revisit triggers above after
discovering that the open-PDK ecosystem had moved. All retrievals on
2026-10-11, from public endpoints, without credentials.

| Check | Result |
|---|---|
| `google/gf180mcu-pdk` (the repository pinned above) | **Archived** (GitHub `archived: true`). `main` HEAD is still `de3240d7529a6970437ac3344820aaae7839f215` (2023-05-31): the transcription recorded above is still its last content state. |
| `fossi-foundation/gf180mcu-pdk` | Fork of the archived repository, HEAD `25ed9c64b64b8e1b93cc4d2d5cade4cd82383a9a` (pushed 2026-05-23): three commits on top of `de3240d`, all Read the Docs build configuration — one repoints the docs at the fork, and one **disables PDF output** to fit the build-time limit (which is why the PDF download above returns 404). No tags, no releases. **No `docs/` content change.** |
| Byte-identity at the fork HEAD | `drm_14_3_1.rst` `ccd536ae6b58…`, `55_Latch-up_152.csv` `50f0f0274baf…`, `01_Document_rev2_3_4.csv` `165851db9c1d…`, `02_Process_Identification7.csv` `215a57055b83…` — identical to the checksums recorded above. The rendered `latest` page re-retrieved: 28,760 bytes, SHA-256 `171588c71102…`, identical again. |
| Read the Docs versioned builds | `en/v0.0.0/…/drm_14_3_1.html` returns 404; `latest` remains the only build, still without a revision identifier. |
| `fossi-foundation/globalfoundries-pdk-libs-gf180mcu_fd_pv` (the active DRC/LVS deck repository, pushed 2026-10-06) | Still no `LU.*` rule: there is no latch-up rule deck; `rule_decks/guard_ring.rb` codes GR.* only; `rule_decks/dualgate.rb` codes DV.* including DV.9 ("3.3V and 5V/6V PMOS cannot be sitting inside same NWELL"), which corroborates the DualGate = 5V/6V semantics but adds nothing about the LU column. Per the #486 clarification an executable deck is not source for the column in any case. |
| `fossi-foundation/globalfoundries-pdk-libs-gf180mcu_fd_sc_mcu9t5v0` (the 9t 5 V library repository, active) | README and tree carry no latch-up or device-class documentation; per-cell datasheets only. |
| Other canonical locations | No `gf180mcu-pdk` GitHub organization exists (404). The `foss-eda-tools.googlesource.com/gf180mcu-pdk` Gitiles mirror exposes only `main` and `v0.0.0`, both matching GitHub. GlobalFoundries' former product-page URL no longer resolves (404 after redirect to `gf.com`). |

Outcome: the revisit triggers have not fired anywhere in the moved ecosystem —
no revision stamp, no definition of `MV`, no numbered release, and no new
executable latch-up rule. The source-confirmation criterion of #486 stays
unresolved, and the access requirement in Decision item 3 is unchanged (a
controlled, numbered DRM revision or written foundry confirmation; an
operator/foundry-contact step). No spec, measurement, test or report change
follows from this re-check.
