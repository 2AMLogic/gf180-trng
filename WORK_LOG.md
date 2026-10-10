# Work Log

Merged PRs and closed issues recorded from recent 30-day query windows, through 2026-10-10.
Earlier history remains available in GitHub. Entries record repository activity,
not independent verification of the claims in issue or PR titles.

### 2026-10-10

- **PR #466**: Price the top-edge digital pin legs in the STA interface load and re-run the sweep (#456)
- **PR #465**: Skip superseded records in the remaining direct-glob record readers
- **Issue #456** (closed): Price the top-edge digital pin legs in the STA interface load and re-run the sweep against the regenerated trunks
- **Issue #427** (closed): Apply the superseded-record lifecycle filter to the remaining direct-glob record readers in sim/tools
- **PR #461**: Enforce activity capture-source freshness and full campaign coverage (#457)
- **PR #460**: Run tap-distance report regeneration in the mandatory nightly verification job
- **Issue #457** (closed): Enforce activity capture-source freshness and full campaign coverage
- **Issue #458** (closed): Run tap-distance report regeneration in the mandatory nightly verification job

### 2026-10-10

- **PR #455**: Characterize workload-dependent digital power with post-route per-net switching activity
- **PR #454**: Regenerate composed floorplan reports and GDS under klt 0.6.0 (depth-2 digital)
- **PR #452**: Record second batch attempt for combiner/sampler PEX grid (partial, #418)
- **PR #451**: layout: whole-block supply ERC over the composed floorplan stream (#447)
- **PR #450**: Measure digital well/substrate tap distances against GF180MCU DRM 14.3.1
- **PR #445**: Reject ambiguous and body-sourced PVT/lifecycle evidence metadata
- **Issue #453** (closed): Characterize workload-dependent digital power with post-route per-net switching activity
- **Issue #448** (closed): Measure digital well and substrate tap distances against applicable PDK rules
- **Issue #447** (closed): Verify supply isolation and connectivity on the composed routed floorplan
- **Issue #443** (closed): Reject ambiguous and body-sourced PVT/lifecycle evidence metadata
- **Issue #256** (closed): Regenerate the remaining floorplan reports and composed GDS from the depth-2 routed geometry

### 2026-10-10

- **PR #444**: Record batch capacity refusals for combiner/sampler PEX grid (partial #418)
- **PR #442**: Refresh Chipalooza current-evidence table and Row C corner coverage (#436)
- **PR #441**: Restate nested P&R DEF path and add host-path guard for tracked JSON
- **PR #440**: Reject partially unsupported characterization row selections
- **Issue #436** (closed): Refresh Chipalooza current-evidence table and reproduction corner coverage
- **Issue #437** (closed): Reject partially unsupported characterization row selections before running campaigns
- **Issue #404** (closed): Committed generated reports embed absolute host paths (home dir, worktree); add a guard

### 2026-10-09

- **PR #439**: Note supply-ripple batch retry; results still pending (#414)

### 2026-10-09

- **PR #435**: Keep current T1 summaries consistent with the graded verdict
- **PR #431**: Test verify_record_checksums.py's committed-to-git check and main() exit paths
- **PR #429**: Index characterization reports in sim/README.md and guard the index
- **PR #426**: Exclude superseded evidence from current analog rollups
- **PR #424**: Extend native ring pex comparison to ring2 (unrun fixture)
- **PR #422**: sim: opt-in supply-ripple susceptibility campaign for the buffered RO array (#414)
- **Issue #434** (closed): Keep current T1 summaries consistent with the graded verdict
- **Issue #430** (closed): Unit-test verify_record_checksums.py's committed-to-git check and main() exit paths
- **Issue #428** (closed): Index the characterization reports under sim/ and guard the index in corpus_counts --check
- **Issue #425** (closed): Exclude superseded evidence from current analog rollups
- **Issue #423** (closed): Extend native ring PEX comparison to the separately sized ring2

- **PR #420**: feat: combiner/sampler schematic-vs-extracted klt pex fixture (grid not yet run)
- **PR #417**: fix(floorplan): route digital's top-edge pins around the east flank (#315)
- **PR #419**: sim: min-entropy re-run at ss/+125C/3.63V (#406)
- **PR #416**: Run check:evidence-history in check:all; add check:ci/check:all parity test
- **PR #415**: fix(lvs): SPICE continuation past comments; LvsFlowError for unnamed bits (#387)
- **PR #409**: test(sim): unit-test build_dut port map refusal branches offline
- **Issue #315** (closed): Inter-region stubs miss digital's top-edge pins after the re-place-and-route (clk, rst_n, raw_bit, raw_valid, ring_bit unjoined)
- **Issue #406** (closed): Resolve the README's untracked 'still owed' min-entropy re-run at ss/+125C/3.63V
- **Issue #408** (closed): check:all omits the append-only evidence-history guard that check:ci runs
- **Issue #387** (closed): lvs.py: fix two latent gaps (SPICE continuation after comment; _bit_names net<id> fallback)
- **Issue #403** (closed): Unit-test build_dut.py's extraction_port_map refusal branches offline

### 2026-10-09

- **PR #407**: test(signoff): unit-test compare_record, _print_item_diff, resolve_artifact
- **PR #405**: ci: wire two missing --check self-checks into check:spec
- **PR #402**: test: unit-test corner_sanity_check's pass/fail logic without ngspice
- **PR #401**: ci: run the SDF regeneration guard in PDK nightly (#374)
- **PR #397**: test: unit-test combiner_sampler and ro_ring11 row/wiring geometry helpers
- **PR #399**: test: unit-test layout/pex/build.py's port-resolution and tap helpers
- **PR #398**: test: unit-test worst_corner_entropy.py's --check gate
- **PR #395**: test: unit-test floorplan.py's SPICE hierarchy-expansion helpers
- **PR #394**: test: unit-test the tap-phase launcher's stale-record cleanup
- **PR #389**: test: unit-test the digital LVS reference-netlist helpers
- **PR #386**: test: unit-test digital place-and-route DEF/GDS checks
- **Issue #391** (closed): Unit-test signoff/check.py's verdict-of-record comparison (compare_record, resolve_artifact)
- **Issue #400** (closed): Wire the DR-0012 estimator-calibration and statistical-battery self-checks into check:spec / CI
- **Issue #388** (closed): lvs.py: _bit_names documents a net<id> fallback it does not implement
- **Issue #377** (closed): Unit-test the corner-sanity guardrail's pass/fail logic without ngspice
- **Issue #374** (closed): Run the committed SDF regeneration guard in PDK nightly CI
- **Issue #392** (closed): Unit-test the combiner_sampler and ro_ring11 row/wiring geometry helpers
- **Issue #390** (closed): Unit-test layout/pex/build.py's port-resolution and tap-position helpers
- **Issue #396** (closed): Unit-test sim/tools/worst_corner_entropy.py's --check gate: it is only ever run against the real corpus
- **Issue #384** (closed): Unit-test floorplan.py's SPICE hierarchy-expansion helpers
- **Issue #393** (closed): Unit-test run_array_liveness_tap_phase.py's stale-record cleanup so it cannot delete complete evidence
- **Issue #382** (closed): Unit-test the digital LVS reference-netlist helpers in layout/digital/lvs.py
- **Issue #383** (closed): Unit-test the digital place-and-route DEF/GDS checks in layout/digital/build.py

### 2026-10-09

- **PR #381**: test: add unit tests for the shared layout engine _mos_row
- **Issue #378** (closed): Add unit tests for the shared hand-drawn layout engine layout/cells/_mos_row.py
- **PR #376**: Add unit tests for the hand-rolled GDSII writer
- **PR #375**: Unit-test gen_sdf SDF filter; raise SdfError on malformed input
- **PR #371**: pdk-nightly: provision gf180mcu_fd_sc_mcu7t5v0 for the floorplan step
- **PR #370**: Reject malformed raw provenance in the checksum gate
- **PR #368**: Add fail-path unit tests for the coupling and tap-phase --check gates
- **PR #364**: Fail closed when --changed record discovery cannot run git diff
- **Issue #373** (closed): Unit-test gen_sdf's SDF filter without openroad and raise SdfError on malformed input
- **Issue #372** (closed): Add unit tests for the hand-rolled GDSII writer in layout/testcells/gdsii.py
- **Issue #369** (closed): Reject malformed raw provenance instead of accepting a parsed checksum prefix
- **Issue #367** (closed): Guard telemetry: preserve fail-closed handling for computed path variables
- **Issue #365** (closed): Auditor Capability Request: Python 3 runtime for gf180-trng validation
- **Issue #362** (closed): Fail closed when checksum --changed cannot resolve its Git base
- **Issue #357** (closed): Add fail-path unit tests for the untested sim tool --check spec gates
- **Issue #310** (closed): pdk-nightly.yml does not provision gf180mcu_fd_sc_mcu7t5v0, so the floorplan step fails at the LEF lookup before checking anything
- **PR #361**: Guard the check:spec gate count and name list restated in prose
- **PR #358**: test(sim): fail-path tests for four spec-guarding --check gates
- **Issue #360** (closed): Guard the check:spec gate count and name list restated in README, ci.yml and package.json (11 / 11 / 13 vs 15 actual)
- **PR #356**: test(sim): add direct unit tests for the shared record parser
- **Issue #345** (closed): Unit-test the shared evidence-record parser (sim/tools/_record_parsing.py), which has no direct tests

### 2026-10-08

- **PR #354**: Pin RTL and verification sources in the item-7 digital freshness gate
- **PR #353**: Verify item-7 analog schematic DUT against its design source
- **Issue #351** (closed): Verify analog item-7 generated schematic DUT against its canonical source
- **Issue #350** (closed): Pin RTL and verification sources in the digital item-7 freshness gate
- **PR #349**: Guard every restated klt/klayout pin against signoff/check.py
- **PR #348**: Drop stale test counts from ci.yml self-check header
- **PR #347**: Require a complete current-DEF family for digital STA aggregates
- **PR #343**: Unit-test the signoff freshness gate against its failure branches
- **PR #342**: Consolidate duplicate klt_origin() into layout/_klt.py
- **PR #340**: Cite a native klt pex report over ring1 as T1 item 7 analog (#326)
- **Issue #344** (closed): Single-source the pinned klt/klayout build: guard the six restated pins against signoff/check.py KLT_PIN
- **Issue #341** (closed): Guard digital STA aggregates against mixed and stale routed-DUT revisions
- **Issue #337** (closed): Unit-test the signoff freshness gate (check_envelope_against_its_input) against its failure branches
- **Issue #336** (closed): ci.yml self-check inventory quotes test counts that are ~7x stale (71/43 vs 540/121)
- **Issue #335** (closed): Consolidate duplicate klt_origin(): verify.py fork vs layout/_klt.py
- **Issue #326** (closed): T1 item 7 (analog): emit the post-layout extraction as a native klt pex report and cite it
- **PR #334**: Enforce append-only simulation evidence against the PR base in CI
- **PR #333**: Consolidate duplicated Variant scaffold across sim/tools --check scripts
- **PR #332**: Cite 11.analog supply-ERC reports in the T1 manifest (#327)
- **PR #329**: Record why the digital STA sweep is not cited as a klt sta envelope (#322)
- **PR #324**: Cite 11.digital supply-ERC report in the T1 manifest (#321)
- **PR #323**: Guard the corpus totals quoted in README.md against the tree
- **PR #318**: Cite an aggregated analog characterization summary as T1 item 8 analog
- **PR #317**: feat(signoff): publish post-route functional run as T1 item 7 digital citation (#314)
- **PR #316**: floorplan: derive the composed interface for klt 0.6.0 and compare it by name (#309)
- **PR #311**: Ratify DR-0026 amended to klayout-tools 0.6.0; re-produce layout/reports/ and pin 4.analog
- **Issue #330** (closed): Consolidate duplicated Variant scaffold across sim/tools --check scripts
- **Issue #328** (closed): Enforce append-only simulation evidence against the PR base in CI
- **Issue #327** (closed): T1 item 11 (analog): write and run a klt erc supply spec for the analog regions and cite it
- **Issue #322** (closed): T1 item 5 (digital): emit the fifteen-corner STA sweep as a graded klt envelope and cite it
- **Issue #321** (closed): T1 item 11: cite the committed digital supply-ERC report in signoff/block-manifest.json so the grader sees it
- **Issue #320** (closed): Guard the corpus counts quoted in README.md (decision records, characterization summaries, evidence records) against the tree
- **Issue #314** (closed): Publish native post-route functional evidence for the T1 digital item-7 citation
- **Issue #313** (closed): Aggregate analog characterization into a pinned T1 item-8 evidence artifact
- **Issue #309** (closed): floorplan.py's inter-region pin-count expectation (107) is stale: klt 0.6.0 extracts 114, naming the five pins the formula subtracts as unnameable
- **Issue #308** (closed): Auditor Capability Request: Python 3 unavailable for local validation
- **Issue #281** (closed): Re-run the analog LVS under a settled producer pin, so item 4's analog citation carries a freshness pin and real power_connectivity/body_verification verdicts

### 2026-10-07

- **PR #306**: fix(digital): rebuild place-and-route from the re-baselined netlist, guard the input hash (#293)
- **Issue #293** (closed): Digital P&R evidence records a superseded input netlist: place_and_route.json pins the pre-#292 trng_top.synth.v hash

### 2026-10-01

- **Issue #294** (closed): ci: pdk-nightly's layout DRC/LVS staleness check fails on ro_ring11.extract.json (new step reached after #291)
- **Issue #270** (closed): Main checkout stuck dirty since before 2026-09-20 — blocks resync-installed automation (202 aborted rebase cycles)

### 2026-09-27

- **PR #303**: chore(sim/harness): remove unused EXIT_SIM_ERROR exit code
- **PR #302**: refactor(sim/tb): deduplicate uniform_words/biased_bits into harness.bits
- **Issue #301** (closed): Remove unused EXIT_SIM_ERROR exit code from sim/harness/cli.py
- **PR #300**: docs(signoff): correct three stale T1 claims in README's claimant reading
- **PR #299**: chore(loom): mitigate #124 noop-cooldown re-dispatch storm with 6h cooldownSecs
- **Issue #298** (closed): Deduplicate uniform_words / biased_bits across sim/tb fault-injection source models
- **PR #297**: fix(layout): tolerate architecture-dependent net_id swap in freshness gate
- **Issue #296** (closed): Loom daemon repeatedly re-dispatches #124 despite noop-cooldown (61 sweeps over 36 days, some <2 min apart)
- **Issue #295** (closed): signoff/README.md's T1 reading is stale: item 5/6 evidence is unproducible upstream, and the grader pin's yardstick moved 9 commits
- **Issue #124** (closed): Track the gap to T1 sim-validated / bronze (klayout-tools design-evidence tiers)

### 2026-09-24

- **PR #267**: chore: resync installed Loom surfaces

### 2026-09-23

- **PR #292**: design: re-baseline trng_top.synth.{v,json} on pdk-nightly's pinned toolchain
- **PR #291**: fix(design): accept both klt netlist_path schemas in synth.py
- **Issue #290** (closed): Digital synthesis artefacts are stale: trng_top.synth.{v,json} do not match a fresh run
- **PR #289**: Remove dead --record CLI flag from six testbench entry points
- **Issue #288** (closed): ci: pdk-nightly's synthesis staleness guard aborts — design/synth.py rejects the pinned klt's string netlist_path (#283 regression)
- **Issue #287** (closed): Remove dead --record CLI flag from 6 run_demo.py/run_battery.py scripts
- **PR #286**: docs: carry #277's re-tuned depth-2 digital power figures into README
- **PR #285**: feat(digital): declare ties[] in the ERC supply spec (T1 item 11)
- **Issue #284** (closed): merge-pr.sh: _check_champion_hold_state_staleness aborts every normal merge (set -e + pipefail + grep no-match)
- **PR #283**: fix(design): read klt synthesize's netlist_path {path, scope} envelope
- **PR #282**: feat(signoff): re-emit the digital DRC/LVS as gradeable klt envelopes (3/22 -> 5/22)
- **PR #280**: feat(digital): add klt erc supply spec and report for T1 item 11
- **Issue #279** (closed): Propagate #277's re-tuned depth-2 digital power figures into README's Power row
- **Issue #278** (closed): design/synth.py --check crashes: klt synthesize's netlist_path is now an object, not a path string
- **PR #277**: fix(digital): re-tune max_transition_ns for the FIFO_DEPTH = 2 topology
- **Issue #276** (closed): T1 item 11: declare ties[] in the digital supply spec so erc.missing_tie is computed (klayout-tools#2169 is fixed in 0.6.0)
- **Issue #275** (closed): README: embed the fleet burndown chart (one line)
- **Issue #273** (closed): Re-emit the digital partition's DRC/LVS and the analog LVS as gradeable klt envelopes, so T1 items 3 and 4 grade on both partitions
- **Issue #268** (closed): T1 item 11 (power delivery, structural): no klt erc supply spec or report in this repo
- **Issue #264** (closed): Re-tune digital place-and-route's max_transition/max_capacitance constraints for FIFO_DEPTH = 2

### 2026-09-22

- **PR #274**: feat(signoff): commit a klt signoff block manifest so T1 state is graded, not hand-read
- **PR #272**: docs: propagate #255/#266's depth-2 digital power figures into the Power row
- **Issue #269** (closed): Commit a klt signoff block manifest so this block's T1 state is graded, not hand-read
- **Issue #265** (closed): Propagate the depth-2 gate-level digital power figures into README's Power row

### 2026-09-19

- **PR #266**: feat(digital): re-synthesize and re-place-and-route at DR-0020's FIFO_DEPTH = 2
- **PR #263**: docs(sim): correct the FIFO-read-path mux2_1 leakage figure to 5.60 µW
- **Issue #262** (closed): The 6.28 uW FIFO-read-path mux figure in characterization-startup-and-power-budget.md does not reproduce from the Liberty library
- **PR #261**: docs(sim): label every digital-estimate figure with its FIFO_DEPTH and add the depth-2 figures
- **Issue #257** (closed): Propagate the FIFO_DEPTH = 2 digital estimate figures into sim/characterization-startup-and-power-budget.md
- **Issue #255** (closed): Re-synthesize and place-and-route the digital block at FIFO_DEPTH = 2

### 2026-09-18

- **PR #260**: chore: remove unused `import re` from test_pex_fullchip.py
- **Issue #259** (closed): Remove unused import: re in layout/tests/test_pex_fullchip.py
- **PR #258**: feat: set FIFO_DEPTH to DR-0020's ratified 2 and re-derive area/power
- **Issue #254** (closed): Implement DR-0020's ratified FIFO_DEPTH=2 in RTL/regmap and refresh the digital power/area estimates

### 2026-09-16

- **PR #253**: docs: propagate idle-current figures after #240's digital rebuild
- **Issue #252** (closed): Refresh README.md's Power row idle-leakage figure after #240's digital rebuild

### 2026-09-15

- **PR #251**: docs(digital): refresh README's P&R figures after #240's rebuild
- **Issue #250** (closed): Refresh layout/digital/README.md's P&R figures after #240's max_transition/max_capacitance rebuild
- **PR #249**: fix(digital): constrain max_transition/max_capacitance at P&R and rebuild
- **PR #248**: docs(spec): propose DR-0026, re-pin klayout-tools forward to match floorplan reports
- **Issue #240** (closed): Constrain max_transition at place-and-route time once klt can express it (follow-up to #237)
- **Issue #230** (closed): Decide which klayout-tools build is normative for layout/floorplan/reports/

### 2026-09-14

- **Issue #247** (closed): Point digital_corner_characterization.py at the shared record-parsing helper (#104 follow-up)

### 2026-09-12

- **PR #246**: refactor: deduplicate load_variants() across sim/tools variant scripts
- **Issue #245** (closed): Deduplicate load_variants() across sim/tools variant-comparison scripts
- **PR #244**: docs: disclose the post-route STA interface load as a floor, not the measured value
- **PR #243**: analysis: decide the post-route max-transition question and gate the accepted residual
- **Issue #242** (closed): post-route STA inter-region interface load is a floor: trunk-only arithmetic undercounts C ~14 % and R ~48 %
- **PR #241**: pex: build the scoped full-chip inter-region delta path (#232, DR-0025)
- **PR #239**: layout: promote digital's vddd/vss to real LVS pins and draw the composed PDN tie (#224)
- **PR #238**: sim: carry the six digital-facing inter-region trunks into the post-route STA (#233)
- **Issue #237** (closed): Post-route max-transition violations inside u_interface at 9 of 15 corners (pre-existing, found by #233)
- **PR #236**: analysis: bound the shared vss return trunk's IR drop per region (#234)
- **PR #235**: ci: gate floorplan provenance on the pdk-nightly job (#227)
- **Issue #234** (closed): IR drop on the shared 430 um vss return trunk: no region's local ground reference has ever been checked
- **Issue #233** (closed): Load the six digital-facing inter-region trunks into the post-route STA as an interface capacitance
- **Issue #232** (closed): Build the scoped full-chip PEX path: price the ro1/ro2 inter-region trunks and re-run the entropy-binding corner
- **PR #231**: spec: scope the full-chip PEX path before building it (DR-0025)
- **PR #229**: fix: remove unused sys import from floorplan_netlist.py
- **Issue #228** (closed): Remove unused import: sys in design/floorplan_netlist.py
- **Issue #227** (closed): Floorplan reports record an unreleased deck, and the build they were written against is not the pinned nightly ref
- **PR #226**: feat: route the inter-region nets across the isolation channels (#222)
- **Issue #225** (closed): Follow-up: a full-chip PEX path is now possible (the composed floorplan is wired) -- decide what it would measure
- **Issue #224** (closed): Phase 3: reconcile digital's vddd/vss PDN tie with the composed LVS reference (the one inter-region connection #222 could not draw)
- **Issue #222** (closed): [Parent #219] Phase 2: physically route the inter-region nets in compose() and verify DRC/LVS/pin-count
- **Issue #219** (closed): Floorplan: the four guarded regions are not electrically joined, so inter-region (full-chip) extraction is still impossible

### 2026-09-11

- **PR #223**: Declare the trng_floorplan inter-region net list and its LVS reference netlist
- **Issue #221** (closed): [Parent #219] Phase 1: declare the trng_floorplan inter-region net list and its LVS reference netlist
- **PR #220**: Routing-level re-run of the sixth testbench family: noise-tapped ring variant, closing #217's §7.5 residual
- **PR #218**: layout(pex): routing-level post-layout extraction of assembled rings and combiner/sampler block
- **Issue #217** (closed): Routing-level post-layout extraction of the assembled rings and combiner/sampler block (closes #17's device-level caveat, now that klayout-tools#1540 is fixed)

### 2026-09-07

- **PR #216**: layout: consolidate duplicated _rect/_pad/_narrow geometry helpers
- **Issue #215** (closed): Consolidate duplicated _rect/_pad/_narrow geometry helpers across layout build.py scripts
- **PR #214**: spec: ratify DR-0019, DR-0020, and DR-0023 via the two-key mechanism
- **Issue #213** (closed): File the ratification PR for DR-0019, DR-0020, and DR-0023 via the two-key mechanism
- **PR #212**: sim(post-layout): re-run entropy/worst-corner/startup-power against the extracted netlist
- **Issue #17** (closed): Post-layout extracted re-run of the verification suite
