# Work Log Archive — 2026-09

Sections moved byte-for-byte from [WORK_LOG.md](../WORK_LOG.md) by `loom-daemon work-docs archive`.

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
