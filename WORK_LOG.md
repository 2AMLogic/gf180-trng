# Work Log

Merged PRs and closed issues from the 30-day window ending 2026-10-07.
Earlier history remains available in GitHub. Entries record repository activity,
not independent verification of the claims in issue or PR titles.

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
