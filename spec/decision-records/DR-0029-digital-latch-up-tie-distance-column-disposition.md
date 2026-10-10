---
dr: DR-0029-digital-latch-up-tie-distance-column-disposition
title: Keep the MV column of LU.3/LU.4 as the binding digital tie-distance limit until a controlled DRM says otherwise, keep the failing verdict, and stage the placement remedy as separate work
status: Proposed
date: 2026-10-10
deciders: Builder of issue #449 (investigation unit only). Not an operator ratification, and it is not a source confirmation: no controlled DRM was available. No ratified requirement is relaxed.
supersedes: n/a
superseded_by: n/a
related: "#449 (this investigation; stays open), #448 (the measurement), #411 (analog ring well ties; separate defect, not a dependency), #456 (digital-facing interface-load geometry; consider when planning the reroute); layout/digital/tap-distance-spec.json; layout/digital/tap_distance.py; layout/digital/reports/tap-distance.json; klayout-tools#3051 (tapcell pitch override gap)"
---

# DR-0029: Digital latch-up tie-distance column disposition

## Status

- 2026-10-10: Proposed. The source-confirmation criterion of #449 is **not
  met** (see "Evidence gap"). The original defect remains open.

## Context

`layout/digital/tap_distance.py` (#448) measures the committed
`layout/digital/trng_top.gds` against GF180MCU DRM section 14.3.1 (Core
Latch-up Rules and Guidelines) rules LU.3 and LU.4. Its input spec applies the
MV (5 V / 6 V) column, 15 um, and the committed report's overall verdict is
`fail`: maximum boundary-to-tap distance 49.727 um (LU.4) and 49.691 um (LU.3);
35 of the 36 LU.4 Nwell groups are over the limit. The report inventories 38
Nwell islands, 265 ntap and 265 ptap polygons, 18,402 gate polygons and zero
gates outside DualGate. The question #449 asks first is whether the MV column
really is the one that applies to this library, because the as-built distances
sit just inside the LV column's 50 um sub-case a).

### Sources

| Source | Kind | What it supports |
|---|---|---|
| `https://gf180mcu-pdk.readthedocs.io/en/latest/physical_verification/design_manual/drm_14_3_1.html`, retrieved 2026-10-10, 28,760 bytes, SHA-256 `171588c71102f5df4c4dc4fe65a454fa42684f0e651d8519c418abe81a730853` | **Published** open-PDK documentation page ("14.3.1 Core Latch-up Rules and Guidelines", copyright line "2022, GlobalFoundries PDK Authors", built with Sphinx). The page carries no DRM revision identifier. | The table text reproduced below. |
| The controlled GlobalFoundries GF180MCU Design Rule Manual (a numbered, dated revision) | **Controlled** | Nothing: it was not available to this builder and was not consulted. |
| Installed open-PDK KLayout decks (variant gf180mcuD) and klt's curated gf180mcu deck | Executable decks | Nothing: neither codes any LU.* rule (`klt deck rules --deck gf180mcu` lists no tie-distance rule), so there is no executable cross-check. |

What the published page says (re-read in this unit): the rule table has columns
`RULE NO.`, `DESCRIPTION`, `LV`, `MV`, `Comment`. LU.3 and LU.4 are headed
"FOR LV and MV outside DNWELL". Each has three sub-cases keyed on a well
clearance (y for LU.3 and LU.4; x for LU.1 and LU.2): y >= 2.0 um gives 50 (LV)
and 15 (MV); 1.0 <= y < 2.0 um gives 30 and 15; y < 1.0 um gives 15 and 15.
The distance is "Max Nwell tap space to every point on the boundary of PCOMP
inside Nwell" (LU.4) and "Max LVPWELL (Psub) tap outside DNWELL space to every
point on the boundary of NCOMP outside NWELL/DNWELL" (LU.3). The page does
**not** define "LV" and "MV" in the table, and it does not say how a layout
decides which column a given diffusion falls in.

### What the repository can and cannot say about the device class

- The cell library is `gf180mcu_fd_sc_mcu9t5v0`, a 5 V library (site
  `GF018hv5v_green_sc9`). By library identity it is the 5 V device family.
- `tap_distance.py` verifies geometrically that every gate (Poly2 and Comp) lies
  inside DualGate (55/0): 18,402 gate polygons, 0 outside. DualGate is the
  thick-oxide marker for the 5 V / 6 V devices, so this is evidence the gates
  are of the dual-gate (MV) class, and it is the evidence that gates the tool's
  choice of the MV column. If any gate were outside DualGate, the tool reports
  the rule `unsupported`, because the LV limit depends on the clearance y,
  which is not measured.
- The digital supply voltage alone does not establish the column, and neither
  does a clean curated DRC verdict (that deck has no LU.* rule). Neither is
  used here as evidence.
- Tap electrical identity: all 265 ntap polygons are on the VDD side and all 265
  ptap polygons on the VSS side (`tap_identity`: none on the other rail, on
  neither, or shorted). The geometry-only worst distances equal the
  identity-filtered ones, so the failure is not an artifact of the identity
  exclusion.
- DNWELL, NAT and Latchup_MK are absent from the stream, so LU.1, LU.2, LU.5
  are `not_applicable` and the I/O rules are not triggered by marker geometry
  (the I/O rule family itself remains `unsupported`).

### Reproduction of the committed-stream measurement

Run in a worktree of checkout `870cb9ecd9e801f659fde2932233ec071cd9aae6`
(main after PR #482), 2026-10-10.

| Item | Value |
|---|---|
| GDS | `layout/digital/trng_top.gds`, SHA-256 `b164476c4e630f4d9f78777b6a248e8be6917a8107029667295076a5165f35b7` (matches `input.gds_sha256` in the report) |
| Spec | `layout/digital/tap-distance-spec.json`, SHA-256 `f54e4d3ff0b6323c30cc8804702d10032582e878fafeddfaa004b548467f68c4` (matches `input.spec_sha256`) |
| Committed report | `layout/digital/reports/tap-distance.json`, SHA-256 `d3ecf7c7b10dea8c3af71fac8e7704b2820d02248909854c3c1327e2875e46e9` |
| Tools | `klt 0.7.0+gca3089cd4b9f`; KLayout Python module 0.30.12 (the klt tool environment's interpreter; the report's `provenance.klayout_version` records 0.30.10, and the freshness comparison passed regardless) |
| Command | `<klt-tool-python> layout/digital/tap_distance.py --check --require-tools` |
| Exit status | 0 |
| Freshness result | "reports/tap-distance.json matches a fresh run" |
| Physical verdict | `fail`: LU.4 49.727 um and LU.3 49.691 um against 15 um; LU.1/LU.2/LU.5 not_applicable; LU.7-LU.10 and DRM 14.3.2 unsupported |

`--check` exits 0 when the committed report is current. That is a statement
about report freshness, not about physical compliance; the physical verdict is
the `fail` in the report. The system `python3` has no `klayout` module, so under
it the same command exits 2 ("the `klayout` Python module is not installed");
the unit tests then self-skip the four geometry cases (8 run, 4 skipped, OK),
and with the klt tool interpreter all 8 run and pass. The 8 tests include the
compliant, over-limit and wrong-rail fixtures, so a wrong-rail tap or an
over-limit spacing is not turned into a pass.

### Evidence gap

The column assignment (MV for the 9t 5 V library) has **not** been confirmed
against a controlled DRM revision. This record therefore cites no controlled
revision or table number, and it does not claim confirmation. What is
established is narrower: (1) the published open-PDK page transcribes an LV and
an MV column; (2) this library's gates are all inside DualGate; (3) the
repository's tool applied the MV column on that basis and the stream fails it.
Whether the published page's "MV" column is the correct one for DualGate 5 V
cells inside a 5 V library is an inference from device naming, not a stated
rule of the page.

## Decision

1. **Keep the MV column, 15 um, as the working binding limit.** It is the
   stricter reading and the one the committed tool applies; adopting the
   weaker LV column to obtain a pass would be a relaxation without evidence.
   `layout/digital/tap-distance-spec.json` is not modified: its hash is part
   of the committed report's identity, and nothing in this unit substantiates
   a different interpretation.
2. **Preserve the `fail` verdict and keep #449 open.** This record and its PR do
   not close the defect. Closing it needs either the controlled-source
   confirmation plus a passing remeasurement of a corrected placement, or a
   controlled-source finding that another interpretation applies.
3. **No measurement defect was found.** The reconciliation of library
   identity, DualGate coverage and tap identity above agrees with what
   `tap-distance-spec.json` assumes; `tap_distance.py` and its tests are
   unchanged. Rule applicability (which column) is separated from measurement
   correctness (the 49.7 um figures are what the stream's geometry gives).
4. **Stage the remedy as separate, separately approved work** (below). This unit
   regenerates no placement and edits no `sim/` record.

### Recommended placement remedy (not performed here)

- The OpenROAD `tapcell -distance` value is a placement input, not a
  boundary-to-tap distance. The klt pin used here fixes it at 100 um for this
  library as a per-library constant (`_TAPCELL_CELLS` in
  `klayout_tools/place_and_route.py`), and the `request.power` schema has no
  field that overrides it. That gap is reported generically as
  klayout-tools#3051. The measured worst distance (about 49.7 um) is roughly
  half the 100 um pitch, which indicates the right order of magnitude for a
  first candidate (a pitch near 30 um or below) but proves nothing; the candidate
  must be accepted only on a remeasurement with `tap_distance.py`.
- The remedy should be configurable in `layout/digital/build.py` (a named
  constant carried into the request once the klt override exists), with the
  default chosen by the measurement, not by the pitch.
- Alternatives to evaluate in the same follow-up: an additional tap-insertion
  pass after placement, or a post-route tap fill into free site gaps. Any such
  change must keep the tap cells on the VDD and VSS nets (`tap_identity`) and
  must not break the Metal1 followpin rails.

### Artifacts that must be refreshed after any re-placement

Re-placement changes the routed geometry, so every artifact derived from it is
stale and must be regenerated, each in an append-only fashion where it is a
`sim/` record (new dated record stems; existing records are never edited):

- `layout/digital/`: `trng_top.def`, `trng_top.gds`, `trng_top.pnr.v`,
  `trng_top.sdf`, `trng_top.extracted.spice`, `trng_top.lvs_reference.spice`,
  `trng_top.lvs-request.json`, and `reports/` (`place_and_route.json`,
  `drc.json`, `lvs.json`, `erc-supply.json`, `sdf_export.json`,
  `tap-distance.json` via `tap_distance.py --write`), plus the numbers quoted in
  `layout/digital/README.md`.
- `sim/records/` families that depend on the routed digital geometry:
  `*-digital-sta-power`, `*-trng-top-post-route`, the extracted/routed
  ro-array startup family, and the power roll-up and activity/corner
  characterization tools' inputs (`sim/tools/power_rollup.py`,
  `digital_corner_characterization.py`, `activity_power_characterization.py`).
  The new records must restate the PVT coverage already used.
- DR-0027 / DR-0028 trunk and top-edge-leg estimates (the interface-load
  geometry; coordinate with #456) and `layout/floorplan/` digital-partition
  reports; `signoff/records/t1-tier-report.json` and its evidence.
- The rerouted block must be verified for actual tap distances (this tool),
  DRC, LVS, power-domain isolation, timing and functional behavior on the new
  geometry, at the stated PVT coverage, before any claim is made.

## Alternatives considered

### Adopt the LV column because the as-built distances sit just inside 50 um

- **What**: re-key `tap-distance-spec.json` to LV, sub-case a), and record a pass.
- **Why plausible**: the distances (49.73 / 49.69 um) fall under 50 um, and
  the platform's `tapcell -distance 100` was chosen for 3.3 V cells.
- **Why rejected**: it needs a clearance (y >= 2.0 um) that the tool does not
  measure, the page gives no rule that 5 V DualGate gates take the LV column,
  and it would relax the committed result to obtain a pass without a
  controlled source. Proximity to a threshold is not provenance.

### Regenerate the placement now with a smaller tapcell pitch

- **What**: edit `build.py`, rerun place-and-route and the downstream evidence.
- **Why plausible**: it is the obvious physical remedy if MV is right.
- **Why rejected**: the column is unconfirmed, klt cannot express the override
  today (klayout-tools#3051), and the downstream refresh is large; the curator
  scoping for #449 asks that source confirmation and the refresh not be
  combined in one PR.

### Do nothing and close #449 as "not applicable"

- **What**: record that the rule does not apply.
- **Why rejected**: no source supports that.

## Consequences

- **Positive**: the failure, its provenance and the exact evidence gap are
  recorded and reproducible; the refresh inventory is written down before a
  reroute is attempted; the klt gap is reported.
- **Negative / accepted cost**: the digital partition continues to fail the
  tie-distance rule as measured; the digital physical evidence is not clean
  until the follow-ups land. This is not hidden by this record.
- **Follow-up required**: (a) obtain the controlled DRM revision and the
  section/table covering LU.3/LU.4, and record the revision and column
  definition (supersede or amend this record); (b) once klayout-tools#3051 or an
  equivalent exists, make the tapcell pitch configurable in `build.py` and
  re-place; (c) regenerate the artifacts listed above. (a) and (b)/(c) are
  filed as `loom:triage` issues linked from #449.
- **Revisit if**: a controlled DRM revision is supplied, whichever column it
  assigns; or klt grows a tapcell override.
