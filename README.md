# gf180-trng

A true random number generator on **gf180mcu**, GlobalFoundries' open PDK,
designed end to end by AI agents driving an entirely open-source analog flow:
xschem for schematics, ngspice for simulation, and
[klayout-tools](https://github.com/2AMLogic/klayout-tools) for layout.

**Evidence:** start with the
[index of characterization reports](sim/README.md#characterization-reports),
which says what each report answers and whether it is complete.

**Status: early. Nothing here has been fabricated, and nothing here has been
measured on silicon.** What exists today is an evidence-record convention,
[twenty-nine decision records](spec/decision-records/), an entropy-source
architecture survey, a PVT corner simulation harness and a gate-level
static-timing and power flow, together producing twenty characterization
summaries (`sim/characterization-*.md`) resting on 1030 append-only evidence
records under [`sim/records/`](sim/records/). `design/` holds the analog
entropy source and sampler as xschem schematics plus four digital blocks, each
a behavioural model with RTL checked against it. `layout/` holds a DRC/LVS
flow, hand-drawn cells and rings, a placed-and-routed digital section, and a
composed floorplan; what is placed, and what is still deferred, is stated in
[`layout/README.md`](layout/README.md) and
[`layout/digital/README.md`](layout/digital/README.md). Simulation evidence is
indexed in [`sim/README.md`](sim/README.md), and per-row status of the
specification in [`docs/spec-row-status.md`](docs/spec-row-status.md). The
specification table below was
[ratified on 2026-07-31](spec/ratification-2026-07-31-target-spec.md) and is
binding on the design, but several of its rows are explicitly *unmeasured
placeholders*; the table labels which.

## Why this repo exists

Two reasons, and the second is why it is public.

**It is a real design.** A TRNG is a good first block for an open-PDK flow: it
is small, it is analog where it matters, and its central claim — that the bits
are actually random — cannot be hand-waved. It has to be simulated across
process, voltage and temperature, and eventually measured.

**It is a forcing function for the tools.** Every time the open-source flow is
awkward, missing a capability, or wrong for the job, that friction gets filed
as an issue against [klayout-tools](https://github.com/2AMLogic/klayout-tools)
rather than worked around silently. A block that is actually being built finds
tool gaps that a test case never will. Those issues are public, and they are
part of the point.

## Built by agents

This repository is developed autonomously. Issues are triaged, specified,
implemented, reviewed and merged by AI agents orchestrated with
[Loom](https://github.com/rjwalters/loom); the commit history, the decision
records, and the simulation evidence are all agent-authored. That is not a
disclaimer — it is the thesis being tested. The interesting question is not
whether an agent can write a netlist, it is whether an agent-run project can
hold itself to an engineering standard of evidence over hundreds of commits.

So the standard is enforced by structure rather than by supervision:

- **No claim without a testbench.** Every recorded number comes from a
  simulation that can be re-run.
- **Every result carries its corner.** Process, voltage and temperature on
  every record — no nominal-only results.
- **Evidence is append-only.** A re-run is a new record, never an edit to an
  old one. A stochastic result without its seeds is not evidence.
- **Spec changes go through a decision record**, so that "the spec moved" is
  always visible as a deliberate act rather than a quiet convenience.

If the structure works, it should be legible from the outside. If it does not,
that should be legible too.

## Target specification (ratified 2026-07-31)

The table below is the contract: the ratified target and stretch for each row,
and a one-line **Status** tag — `met`, `missed`, `unmeasured` (a placeholder,
not a claim), `derived from target`, or `specified` (a design or interface
decision with no measured quantity to meet or miss). Every measured figure
behind a tag, and how each one moved from issue to issue, is in
[`docs/spec-row-status.md`](docs/spec-row-status.md), one section per row. A
tag summarises that record; it never overrides it.

| Parameter | Target | Stretch | Status |
|---|---|---|---|
| Entropy source | **N-way array of independent free-running ring oscillators, XOR-combined ahead of a single sampler**, N fixed by the jitter-budget sizing law `Q_array ≥ 1.5 × 4.0×10⁻³` at the entropy-binding corner ([DR-0007]) | metastability hybrid, scoped as a *secondary tap on the RO core* — not a free-standing source | specified ([DR-0007]) — [evidence](docs/spec-row-status.md#entropy-source) |
| Raw rate | > 1 Mbps sustained at the raw tap (sampler output), binding at the slowest-RO corner: `ss` / −10 % / +125 °C ([DR-0003]) | > 4 Mbps, same definition | **unmeasured** — a target, and unsettled: see [binding corners](docs/spec-row-status.md#binding-corners-and-the-rate-row) — [evidence](docs/spec-row-status.md#raw-rate) |
| Raw min-entropy per bit | **placeholder — H₀ = 0.5 bit/sample is a design *target*, not a measurement.** Stated at the entropy-binding corner, **`ss` / +125 °C / 3.63 V** ([DR-0015]; `fs`/`sf` remain uncovered per [DR-0006]). Still owed: measured silicon ([DR-0004] Tier 3) | — | **unmeasured placeholder** — no `H` figure is supportable by transistor-level simulation (#12, #406); owed to measured silicon — [evidence](docs/spec-row-status.md#raw-min-entropy-per-bit) |
| Quality | designed-for-SP 800-90B (raw access + RCT/APT + entropy-source model), plus a **simulation-derived design-stage min-entropy estimate** within the #10 claim limits; 90B validation itself deferred to measured silicon ([DR-0004]) | AIS-31 PTG.2 — same three-tier treatment (structure now, conformance deferred) | specified; 90B validation deferred to measured silicon ([DR-0004]) — [evidence](docs/spec-row-status.md#quality) |
| Conditioning | **non-vetted** 32-bit CRC-32 LFSR compression (Galois, poly `0xEDB88320`), state cleared every block, **K = 8** — 256 raw bits in : one 32-bit word out. Creditable output entropy **0.85 bit per output bit** (SP 800-90B's non-vetted cap) for any raw stream at or above **H = 0.107 bit/sample**; a 4.70× margin under the H₀ = 0.5 target. ~0.005–0.008 mm² ([DR-0008]) | a 90B-*vetted* conditioning function — **rejected on area**: a compact serialised AES-128 is 88–124 % of the whole block budget ([DR-0008] §4). Live again only if the area budget grows | specified ([DR-0008]) — [evidence](docs/spec-row-status.md#conditioning) |
| Delivered (post-conditioning) rate | **`R_cond = R_raw / K` > 125 kbps** at the raw-rate row's binding corner (`ss` / −10 % / +125 °C), K = 8; > 500 kbps at the stretch raw rate ([DR-0003] §6, [DR-0008] §3) | — | **derived from target** — not measured; inherits the raw-rate row's status — [evidence](docs/spec-row-status.md#delivered-post-conditioning-rate) |
| Health tests | continuous RCT + APT on the **raw** stream, α = 2⁻⁴⁰, APT window W = 1024, cutoffs as formulas in min-entropy H (at H₀ = 0.5 → `C_RCT` = 81, `C_APT` = 824); failure latches a flag and gates the conditioned path until explicit clear + start-up test. The parameterization has a hard floor: **no valid APT cutoff exists at H ≤ 0.03** ([DR-0002]) | — | specified ([DR-0002]) — [evidence](docs/spec-row-status.md#health-tests) |
| Time-to-first-valid | **≥ ~1.28 ms** at 1 Mbps — an arithmetic floor: 1024 consecutive raw samples for the start-up health test (1.024 ms) plus 256 samples of conditioner latency (0.256 ms), which do **not** overlap because the conditioner is held flushed while gated. Applies at power-on and after every alarm clear; binds at `ss` / −10 % / +125 °C (slowest sampling) ([DR-0002] §Failure behavior, [DR-0008] §7). | — | **met** — measured 1.281 ms (#14) — [evidence](docs/spec-row-status.md#time-to-first-valid) |
| Power | < 500 µW active, binding at `ff` / +10 % supply (fastest RO — max measured `f_osc` 2.30 GHz at −40 °C); < 1 µA idle, binding at `ff` / +10 % / +125 °C (max leakage) | — | **missed** — active 758.2 µW, missed by 1.5×; idle 2.21 µA, missed by ~2.2× ([DR-0023], [DR-0017]) — [evidence](docs/spec-row-status.md#power) |
| Area | < 0.05 mm² | — | **missed** — the regenerated floorplan misses by 3.5×: 175 789.9 µm² including isolation channels, 351.6 % of the row ([DR-0019]) — [evidence](docs/spec-row-status.md#area) |
| Operating envelope | −40 … +125 °C, 3.3 V ± 10 % (2.97–3.63 V). Every entropy, rate and health-test claim above holds **over this envelope and only over it**; the envelope is the security boundary, since an attacker chooses the operating point. Outside it, behavior is health-test-detected, not specified | — | specified — [evidence](docs/spec-row-status.md#operating-envelope) |
| Interface | streaming, mode-selectable raw / conditioned (`OUT_MODE`), + register read (`DATA` conditioned, `RAW_DATA` raw); raw access always available and never gated ([DR-0001]). Instantiated as four word-addressed registers — `CTRL`, `STATUS`, `DATA`, `RAW_DATA` — plus a 32-bit valid/ready streaming port, with a health-test gate that flushes the conditioned path and **never** the raw one ([DR-0013]) | — | specified ([DR-0001], [DR-0013]) — [evidence](docs/spec-row-status.md#interface) |

**Scope**: this block is an **entropy source only** — there is no DRBG in it,
and it defines no seeding or reseeding semantics. An integrator that needs a
DRBG supplies its own and treats this block as the seed source.

> **Ratified, with four rows explicitly unmeasured.** The table was ratified
> on 2026-07-31 by engineering (Robb) — see
> [`spec/ratification-2026-07-31-target-spec.md`](spec/ratification-2026-07-31-target-spec.md)
> and issue #1 — together with the amendment package in #29. Every decision
> record the rows above cite is `Accepted` except [DR-0017], which is
> `Proposed` (its idle-current options are unchosen; see the
> [Power note](docs/spec-row-status.md#power));
> [DR-0015] was `Accepted` 2026-10-10 via the two-key ratification mechanism,
> #480; a row that cannot be met is a **superseding decision record**,
> not an edit. What ratification does *not* do is turn placeholders into
> claims: **Raw min-entropy per bit**, **Conditioning / delivered rate**,
> **Power** and **Area** were ratified unmeasured. Where each stands now is
> its Status tag above; the full ratification note, row by row, is in
> [`docs/spec-row-status.md`](docs/spec-row-status.md#ratification-four-rows-explicitly-unmeasured).
>
> Note also that rows bind at **different** corners, and none at nominal: rate
> at the slowest-RO corner, min-entropy per bit at the *least*-jitter
> (minimum-`Q`) corner, power at the fastest/leakiest corner, time-to-first-valid
> at the slowest-sampling corner. What that means for the time-to-first-valid
> and raw-rate rows is in
> [`docs/spec-row-status.md`](docs/spec-row-status.md#binding-corners-and-the-rate-row).

[DR-0001]: spec/decision-records/DR-0001-raw-and-conditioned-output-paths.md
[DR-0002]: spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md
[DR-0003]: spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0004]: spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0006]: spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md
[DR-0007]: spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md
[DR-0008]: spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md
[DR-0009]: spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0010]: spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0011-rate]: spec/decision-records/DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md
[DR-0012]: spec/decision-records/DR-0012-sampler-fixed-external-clock.md
[DR-0013]: spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md
[DR-0015]: spec/decision-records/DR-0015-entropy-binding-corner-moves-to-the-hot-slow-corner.md
[DR-0017]: spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
[DR-0018]: spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md
[DR-0019]: spec/decision-records/DR-0019-area-row-versus-output-fifo-dominated-digital-section.md
[DR-0020]: spec/decision-records/DR-0020-fifo-depth-set-to-two-against-power-area-and-streaming.md
[DR-0021]: spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
[DR-0023]: spec/decision-records/DR-0023-power-rollup-digital-term-becomes-measured-gate-level-power.md

Maturity ladder: simulation-complete → layout DRC/LVS-clean → shuttle
seat → measured silicon over temperature. **The block is on the first rung.**
Layout work has started on both halves — the entropy source and sampler are
placed, DRC-clean and LVS-matching, and the digital section has a
standalone placed-and-routed, DRC-clean GDS (#170), and, since #187, a
clean LVS (`status: match`, zero mismatches after #306). Since
#209/#210 the two are composed into one whole-block layout too
(`layout/floorplan/trng_floorplan.gds`, DRC-clean and LVS-matching for all
four regions) — see
[`layout/floorplan/README.md`](layout/floorplan/README.md#tool-friction)
for exactly what that composed check does and does not establish before
reading it as more than the first rung.
The SP 800-90B validation claim attaches to the last rung, not the first
([DR-0004]) — a simulated min-entropy estimate is not an entropy assessment,
and this repository will not let one be read as the other.

Where this block stands against the klayout-tools design-evidence ladder is
**graded, not asserted**: [`signoff/records/t1-tier-report.json`](signoff/records/t1-tier-report.json)
is the verdict of record, produced by `klt signoff --manifest` from
[`signoff/block-manifest.json`](signoff/block-manifest.json) and re-run by CI
on every push. <!-- current-t1-status:begin -->Today it reads `tier: null`, **T1 8 of 22 items met**<!-- current-t1-status:end --> (a
`mixed-signal` block is graded once per partition, so the eleven-item T1
checklist renders 22 rows). That is a stricter reading than "which work has
been done", because it counts only evidence a third party can re-grade from a
committed `klt` JSON envelope — most of this repo's verification evidence is
in its own Markdown record format and is invisible to the grader.
[`signoff/README.md`](signoff/README.md) reads every row, states the
disclosures the grader structurally cannot check, and lists what would move
the needle.

## Layout

```
spec/          spec + decision records
design/        analog schematics / netlists (xschem) + digital blocks
sim/           testbenches + PVT corner results (ngspice)
layout/        DRC/LVS flow + drawn cells + digital P&R          — composed (#209/#210)
signoff/       T1 evidence manifest + graded tier report         — `klt signoff --manifest`
measurements/  silicon characterization                          — empty until tape-out
```

`design/` holds the two halves of the block, one on each side of the raw tap.
[`conditioner/`](design/conditioner/) is the digital post-processing stage,
[`health_test/`](design/health_test/) is the on-die RCT/APT health tests, and
[`interface/`](design/interface/) is the register file, output FIFOs and
gate/flush machine — each a normative behavioural model plus synthesisable RTL
checked against it. [`trng_top/`](design/trng_top/) is the top-level
integration (#27): the analog entropy source and sampler, plus these three
digital blocks, wired together per their pinouts, with one nominal-corner
smoke record proving bits flow end to end.
[`xschem/`](design/xschem/) is the analog entropy source — the starved delay
cell, the ring built from it, and the XOR-combined multi-ring array — together
with the SPICE netlists exported from those schematics by
[`design/netlist.py`](design/netlist.py), which also provides the
schematic-vs-netlist staleness guard that makes a netlist SHA quoted in an
evidence record provable rather than asserted. See
[`design/README.md`](design/README.md) for the cell-by-cell inventory.

Which parts of the block are simulated at transistor level and which are
modelled behaviourally is fixed by [DR-0009]: the boundary is the raw tap, and
every evidence record says which side of it produced the number.

`layout/` holds the verification flow before the layout it will check — the
same order `sim/` was stood up in, and for the same reason: a flow whose first
run is on the thing you care about is a flow you cannot distinguish from one
that always says "clean". [`layout/verify.py`](layout/verify.py) drives `klt`
DRC, extraction and LVS over three deliberately-chosen fixtures (a known-good
inverter, a DRC-bad copy, an LVS-bad copy) and compares every report against a
declared expectation, so the flow is itself a test.
[`layout/floorplan/`](layout/floorplan/) is the entropy source's isolation
rationale (#16) and the floorplan abstract that carries it — four guarded
regions, DRC'd as one stream, priced against the area row. Three of those
regions — `ring1`, `ring2`, `combiner_sampler`, and, since #209/#210,
`digital` — are no longer an abstract: they all carry real, placed,
guard-ringed geometry assembled from the drawn cells above (or, for
`digital`, from its own standalone placed-and-routed GDS,
[`layout/digital/`](layout/digital/), #170/#187), DRC-clean and
LVS-matching per `layout/floorplan/reports/ring_fit.json`
(#110, #135, #209/#210). Since #222 they are also **wired to each other**:
real routing geometry crosses the isolation channels for every net
`design/floorplan_netlist.py` declares (#221), and the composed, routed
stream is DRC-clean and LVS-matches that declaration's own composed
reference — `layout/floorplan/reports/interregion.json`. That is a composed
whole-block *floorplan*, not a tapeout sign-off — see
[`layout/floorplan/README.md`](layout/floorplan/README.md#tool-friction)
for exactly what its DRC/LVS checks do and do not establish. Nothing under
`layout/reports/` should be read as a statement about the whole design.
[`layout/README.md`](layout/README.md) says exactly what a clean report from
this flow does and does not mean, and why it is not tapeout sign-off.

Two conventions govern what lands in those directories:

- **[`sim/README.md`](sim/README.md)** — the append-only evidence record
  format. Every recorded simulation result carries its testbench/netlist
  identity, ngspice version, P/V/T corner, and seeds; re-runs are new
  records, never edits. A transient-noise result without its seeds is not
  evidence.
- **[`spec/decision-records/TEMPLATE.md`](spec/decision-records/TEMPLATE.md)**
  — the numbered decision-record template (`DR-0001-<slug>.md`). Spec
  changes go through a decision record.

### `sim/` harness

The PVT corner runner is a stdlib-only Python CLI. It emits into this repo's
`sim/README.md` evidence-record format — one record per PVT point — as
reconciled in
[`DR-0005`](spec/decision-records/DR-0005-sim-harness-record-granularity.md).

You will need the gf180mcu PDK and ngspice 46 or newer. Nothing else — the
harness is stdlib-only Python 3.

The simplest way to get the PDK is
[ciel](https://github.com/fossi-foundation/ciel), which installs prebuilt
[open_pdks](https://github.com/RTimothyEdwards/open_pdks) releases into
`~/.ciel/<variant>` — one of the harness's built-in search roots, so nothing
needs wiring up afterwards:

```sh
pip install ciel
ciel enable --pdk-family gf180mcu -l gf180mcu_fd_pr \
  f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
```

That open_pdks commit is the one
[`.github/workflows/pdk-nightly.yml`](.github/workflows/pdk-nightly.yml) pins,
so a local run and the nightly agree on a PDK version by default;
`-l gf180mcu_fd_pr` fetches only the primitive device library the testbenches
here need instead of the full ~5 GB set. A PDK from
[IIC-OSIC-TOOLS](https://github.com/iic-jku/IIC-OSIC-TOOLS), a source
`open_pdks` build, or ciel's predecessor
[volare](https://github.com/efabless/volare) works too — but volare's gf180mcu
release feed stopped publishing in Aug 2025, so it can no longer install a
current PDK.

```sh
# One-time PDK check (no hardcoded paths -- see sim/harness/pdk.py for the
# GF180_PDK_PATH / PDK_ROOT+PDK / sim/pdk.local.json / sim/pdk.json /
# built-in-search-root resolution chain).
python3 sim/run_corners.py --check-env

# List testbenches (sim/tb/<slug>/tb.json) and available corners/corner-sets.
python3 sim/run_corners.py --list

# Run a testbench across a PVT grid -- one evidence record per grid point,
# written under sim/records/, per sim/README.md. No manual netlist edits.
python3 sim/run_corners.py <testbench-slug> --corner-set mos

# Harness acceptance test: unit tests + env check + smoke run + the
# corner-sanity guardrail (does switching process corner actually move
# device behavior, or is a corner file being silently ignored?).
sim/selftest.sh                # no evidence written
sim/selftest.sh --record       # also mints real records under sim/records/
sim/selftest.sh --require-pdk  # fail (instead of skip) if ngspice/PDK are absent
```

### Checks

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs, on every push and
pull request, every check that needs no PDK, on Python 3.10 and 3.13, by
calling `npm run <script>` once per group — `package.json` is the one
inventory of what each check is, and the workflow is a runner over it rather
than a second list that can say something different (#97):

- **`npm run lint`** — a Python/shell syntax check and the schematic
  text-block brace guard (`design/netlist.py --lint`, #61);
- **`npm run test`** — the harness unit tests;
- **`npm run check:spec`**, **nineteen spec-arithmetic self-checks** — pure
  derivations over records already committed under `sim/records/`, so a newly
  appended record cannot silently move a conclusion a summary document still
  asserts: `jitter_energy_law.py`, `starved_cell_jitter_energy.py`,
  `array_sizing.py`, `worst_corner_entropy.py`, `array_coupling_variants.py`,
  `array_coupling_buffer_variant.py`, `liveness_tap_phase_variants.py`,
  `array_liveness_tap_phase_variants.py`, `sampler_bit_bias_variants.py`,
  `time_to_first_valid.py`, `power_rollup.py`,
  `digital_corner_characterization.py`, `activity_power_characterization.py`,
  `vss_trunk_ir_drop.py`, `digital_supply_ir_drop.py`,
  `corpus_counts.py`, `klt_pin_sites.py`,
  `jitter_estimator_calibration_check.py` and `statistical_battery.py`, each
  `--check`;
- `sim/tools/verify_record_checksums.py`, which re-hashes every file each
  record's `raw.files` cites against `sim/records/raw/` (#60) — run as its own
  workflow step (the stricter, git-commit-state-checking form) rather than via
  `npm run`, since `check:ci` only reaches this script indirectly, through the
  `sim/selftest.sh` call at the end of its chain;
- **`npm run check:regmap`** — the register-map staleness guard
  (`design/interface/regmap.py --check`);
- **`npm run check:fixtures`** — the layout test-cell staleness guard
  (`layout/testcells/build.py --check`);
- **`npm run check:digital-input`** — the digital implementation's input
  guard (`layout/digital/build.py --check-input`, #293): the netlist hash
  `layout/digital/reports/place_and_route.json` records as its input must
  equal the committed `design/trng_top/trng_top.synth.v`;
- **`npm run check:layout`** and **`npm run check:floorplan`** —
  `layout/verify.py` and `layout/floorplan/floorplan.py`, both of which
  self-skip when `klt`/the PDK are absent;
- **`npm run check:digital-tap-distance`** — tap-distance report freshness
  (`layout/digital/tap_distance.py --check`, #458); it prints that the
  `klayout` module is missing and skips when it is absent;
- **`sim/selftest.sh`** — whose PDK-dependent stages detect the missing PDK
  and skip themselves on a hosted runner.

`npm run check:ci` runs the same steps, in the same order, as the local
entry point for the same intent — a contributor who runs it before pushing
exercises exactly what the PR-blocking workflow above will run.

The smoke run, the corner-sanity check and the schematic-vs-netlist staleness
guard (`python3 design/netlist.py --check`) are deliberately *not* on the PR
path: they need ngspice, xschem and a multi-gigabyte PDK, and a pull request
should not block on provisioning any of them. They run instead on a nightly
schedule — [`.github/workflows/pdk-nightly.yml`](.github/workflows/pdk-nightly.yml)
builds the pinned ngspice release, installs the gf180mcu PDK at a pinned
open_pdks commit, installs `klt`, and runs `design/netlist.py --check`,
`sim/selftest.sh --require-pdk` and `layout/verify.py --require-tools` — the
forms that fail rather than skip. It also runs the committed post-route SDF
regeneration guard, `npm run check:digital-sdf` (`layout/digital/gen_sdf.py
--check`), which re-runs OpenSTA over `layout/digital/trng_top.pnr.v` and the
provisioned liberty deck and compares the result with the committed
`trng_top.sdf` and `reports/sdf_export.json` (wall-clock `DATE` normalised,
everything else exact). Its prerequisites are the provisioned gf180mcu
`gf180mcu_fd_sc_mcu9t5v0` library and OpenROAD: a native `openroad` if one is
on `PATH`, otherwise Docker with the digest-pinned image behind
`layout/openroad_docker.sh`. A reachability probe step first checks that the
PDK's liberty and LEF files are visible inside the container; a missing
OpenROAD, container or PDK file fails the job rather than skipping. The guard
is read-only. The same job runs the strict tap-distance freshness check,
`python3 layout/digital/tap_distance.py --check --require-tools` (#458), which
re-measures `layout/digital/trng_top.gds` and compares the result with
`layout/digital/reports/tap-distance.json`; it runs under `if: always()` so it
reports independently of earlier validation failures, and a missing `klayout`
module fails it. It checks that the report follows from the current measuring
program, not that the layout is physically compliant, and writes nothing. That
job writes no evidence records and fails if `sim/records/` changes.

The nightly run does not replace the local one: run `sim/selftest.sh
--require-pdk` (or `npm run check:all`) on a machine that has ngspice and the
PDK before committing an evidence record.

`sim/tb/` holds 64 testbenches. Three of them exercise the harness itself
rather than the TRNG design — they predate any `design/` content and are kept
as the harness's own regression set: `smoke-op` (trivial op-point smoke test),
`corner-sanity-nfet-id` (the automated guardrail behind
`sim/tools/corner_sanity_check.py`), and `nfet-mismatch-seed` (demonstrates
per-run seed control and exact reproducibility for stochastic analyses — see
`sim/README.md`'s "no seed, no evidence" rule). A second group characterizes
the PDK devices and the noise methodology rather than any cell of this design
(`device-leakage-03v3`, `noise-floor-resistor`, `inv-stage-noise`,
`cinv-stage-noise`, `trnoise-calibration`, `jitter-estimator-calibration`). The
rest exercise the design, running against the netlists exported from
`design/xschem/`: the ring and its delay cell (`rostage-noise`, `ro-*-jitter`),
the array and its combiner (`ro-array-core-*`, `ro-array-coupling-*`), the
sampler (`sampler-dff-*`, `sampler-bit-bias-*`, `sampler-array-digitize`), the
metastability tap (`meta-arb-regeneration`, `ro-meta-tap-skew`) and the
DR-0016 liveness tap (`ring-liveness-*`, `array-liveness-*`).

Five of the 64 are **behavioral-level**: `conditioner-crc32` (the first),
`interface-regfile`, `health-test-fault-injection`,
`ring-liveness-fault-injection` and `smoke-trng-top`. They have no `tb.json`,
are not discovered by `run_corners.py`, and are run directly (e.g. `python3
sim/tb/conditioner-crc32/run_demo.py`). Their records carry `level: behavioral`
and no P/V/T corner, and may not be cited for anything corner-dependent — see
`sim/README.md` §Behavioral-level records and [DR-0009]. `interface-regfile`
runs two digital blocks against each other with the conditioner's `en`/`flush`
taken from the interface's own outputs — the inter-block contract, not a
stand-in for it.

## Chipalooza

[`docs/chipalooza/challenge-3-proposal.md`](docs/chipalooza/challenge-3-proposal.md)
is this block's proposal for Open Circuit Design's Chipalooza Challenge #3
(GF180MCU / Wafer.Space) — a five-section, email-ready submission whose
target-specification table cites this repository's actual `sim/` results at
the challenge's rails, marks the rows that miss or are unmeasured there, and
proposes a reduced test-chip pinout mapped onto the challenge's slot budget.
The next section is this repository's answer to that program's own review
bar: how an outside reviewer independently re-runs the simulations that
table's numbers come from.

## Independent verification (Chipalooza)

This section is written for someone who has never seen this repository
before — specifically, for a Chipalooza Challenge #3 schematic reviewer
checking the bar stated in [#202](https://github.com/2AMLogic/gf180-trng/issues/202):
*"It must be possible for me to independently run simulations to verify the
performance of the circuit,"* from a single command, with README instructions
sufficient to understand how. If you only read one paragraph of this
document, read the next one.

**In three commands**, from a clean clone, with the prerequisites below
installed: `make check` (are the tools present?), `make smoke` (does the
harness work at all, in seconds), `make characterize` (regenerate the
transistor-level evidence behind [the proposal's spec table](docs/chipalooza/challenge-3-proposal.md#4-target-specification)).
Every result lands under [`sim/records/`](sim/records/) in the append-only
format [`sim/README.md`](sim/README.md) fixes — nothing is overwritten, so
re-running this after a clone changes nothing about the records already
committed here, it only adds new, independently-produced ones alongside them.

### Prerequisites

| Tool | Version | Needed for |
|---|---|---|
| Python 3 | 3.10+ (stdlib only — no `pip install`) | all three `make` targets |
| [ngspice](http://ngspice.sourceforge.net/) | ≥ 46 | `make smoke`, `make characterize` |
| gf180mcu PDK | the `open_pdks` commit `.github/workflows/pdk-nightly.yml` pins (`f6eeac7d…`, or any current one) | `make smoke`, `make characterize` |
| `PDK_ROOT` / `PDK` (or `GF180_PDK_PATH`) | — | only if the PDK is not under `~/.ciel`, `~/.volare`, or another of `sim/harness/pdk.py`'s built-in search roots |

The simplest way to get ngspice + the PDK together is
[IIC-OSIC-TOOLS](https://github.com/iic-jku/IIC-OSIC-TOOLS) (a maintained
Docker image with the whole open-source analog IC stack preinstalled) or,
PDK-only, [ciel](https://github.com/fossi-foundation/ciel):

```sh
pip install ciel
ciel enable --pdk-family gf180mcu -l gf180mcu_fd_pr \
  f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
```

ciel installs into `~/.ciel/<variant>`, one of the harness's built-in search
roots, so nothing needs wiring up afterwards — `make check`'s environment
report (below) confirms it found the PDK before you run anything longer.
ciel's predecessor [volare](https://github.com/efabless/volare) also works,
except its gf180mcu release feed stopped publishing in Aug 2025 and so can no
longer install a *current* PDK. See the [`sim/` harness](#sim-harness) section
above for the full PDK-resolution chain if you need to point at a PDK
installed somewhere else (`GF180_PDK_PATH`, `PDK_ROOT`+`PDK`, or
`sim/pdk.local.json`).

**KLayout, Magic and Netgen are not needed for any of the three targets
below.** This design's layout verification runs through
[klayout-tools](https://github.com/2AMLogic/klayout-tools) (`klt`, which
brings its own KLayout Python module rather than driving a standalone
`magic`/`netgen` install) and the digital section's static timing needs
OpenROAD — both are **separate flows** from the three `make` targets this
section covers, invoked by `npm run check:layout` / `check:floorplan` and by
`sim/tb/digital-sta-power/run_sta.py` respectively. The row-mapping table
below names the exact command for the two spec-table rows that need them
(Rows G and, partly, D/E), so a reviewer who only wants the analog entropy
source's evidence never needs to install either.

### The three make targets

```sh
make check              # unit tests + environment report -- run this first
make smoke              # harness acceptance test, one typical corner -- seconds
make characterize       # full PVT/corner campaign -- tens of minutes, multi-core
make characterize-dry-run   # print the plan for `make characterize` without running it
make help                   # all of the above, from the repo itself
```

| Target | What it does | Wall-clock (this repository's own 8-core host) | Exits non-zero on |
|---|---|---|---|
| `make check` | `sim/tests/` + `layout/tests/` unit tests (stdlib `unittest`, no PDK needed), then `python3 sim/run_corners.py --check-env` (ngspice version, OS watchdog, PDK resolution — see [Prerequisites](#prerequisites)) | ~10 s, fresh clone | any unit-test failure, or ngspice/PDK not found |
| `make smoke` | `sim/selftest.sh`: the same unit tests, `sim/tools/verify_record_checksums.py` over every already-committed record, an end-to-end run of `sim/tb/smoke-op` at one corner (`--no-write`, mints no evidence), and `sim/tools/corner_sanity_check.py` (does switching the process corner actually move device behavior — the guardrail against a silently-ignored corner selection contaminating every downstream record) | ~11 s, fresh clone | any stage failing; the PDK-dependent stages **skip** (exit 0) instead of failing when ngspice/the PDK are absent, so this is also safe to run before installing either |
| `make characterize` | `sim/characterize.py`: `sim/run_corners.py` invocations across seven campaign steps (five testbenches, one run three times at three corners), at the same corner grids the proposal's spec-table citations use — 27 + 27 + 45 + 45 + 3 + 3 + 3 = 153 ngspice points total — writing real evidence records under `sim/records/` per `sim/README.md` | **per-point cost, uncontended**: ~85 s/point (measured: one 3-point sub-grid, 4m15s serial). The default is a bounded 2 concurrent ngspice runs, not every core; at `JOBS=8` on a dedicated 8-core host, expect roughly 25–35 minutes for the full campaign; PR #203's own fresh-clone dry run ran on a heavily shared, multi-tenant host (load average measured >100 from concurrent unrelated builds) and is not a clean baseline — see the PR body for that run's actual, honestly-reported numbers | any `run_corners.py` invocation failing, or ngspice/the PDK not found |

`JOBS=<n>` overrides the default concurrency (a bounded 2) on any of the
three, e.g. `make characterize JOBS=8` to use every core of a dedicated
machine. `make clean` removes `sim/`'s scratch working directory
(`sim/.work/`) — never `sim/records/`, which this repository never deletes.

### Where results land, and how to read them

Every `make characterize` run writes new records at
`sim/records/<YYYY-MM-DD>-<testbench-slug>-<NN>.md` (frontmatter: corner,
seeds, ngspice version, testbench/netlist SHAs — see
[`sim/README.md`](sim/README.md) for the full format) with raw ngspice output
under `sim/records/raw/<same-stem>/`. Two roll-up tools read *every* matching
record (old and newly-added) and print the current per-corner table:

```sh
python3 sim/tools/power_rollup.py           # Rows D/E's active/idle power
python3 sim/tools/time_to_first_valid.py    # Row F's time-to-first-valid
```

### Proposal spec-table row → regeneration command

Each row of [the proposal's target-specification
table](docs/chipalooza/challenge-3-proposal.md#4-target-specification) maps
to one of these commands. `make characterize` covers the ngspice-based
(transistor-level) rows; the rest are separate, clearly out-of-scope flows
with their own prerequisites, named here rather than silently skipped.

| Row | Parameter | Regenerated by | Output |
|---|---|---|---|
| A | Per-ring oscillation frequency | `make characterize` (`ro-array-core-pvt-q`, 27-point grid) | `sim/records/<date>-ro-array-core-pvt-q-*.md` |
| B | Raw bit rate | *not* a PVT sweep — `python3 sim/tools/jitter_energy_law.py --check` and `starved_cell_jitter_energy.py --check`, derived from the existing `rostage-noise` / `ro-ring5-starved-jitter-long` records (`npm run check:spec`) | stdout only; no new record |
| C | Raw min-entropy | `make characterize` (`sampler-array-digitize`, the three corners a real bitstream exists for: `tt`/27 °C/3.30 V, `ss`/−40 °C/3.63 V and the measured entropy-binding corner `ss`/+125 °C/3.63 V, seeds 1001..1003 at each) | `sim/records/<date>-sampler-array-digitize-*.md` (functional demonstration only — see the record's own caveats and the proposal's Row C notes; **not** an entropy measurement) |
| D | Active power (whole block) | four required terms, rolled up by `power_rollup.py`: **array** and **raw sampler**: `make characterize` (`ro-array-core-pvt-q` + `sampler-dff-active-current`); **liveness** (`xsr1`/`xsr2`): a separate opt-in `klt sim` campaign, *not* run by `make characterize` or CI (see below); **digital**: `python3 sim/tb/digital-sta-power/run_sta.py` (needs OpenROAD) | `sim/records/<date>-{ro-array-core-pvt-q,sampler-dff-active-current,sampler-core-liveness-active}-*.md`; digital: `sim/records/<date>-digital-sta-power-*.md` |
| E | Idle current (whole block) | analog term: `make characterize` (`sampler-core-idle-leakage`), rolled up by `power_rollup.py`; digital leakage term: same `run_sta.py` flow as Row D | `sim/records/<date>-sampler-core-idle-leakage-*.md`; digital: `sim/records/<date>-digital-sta-power-*.md` |
| F | Time-to-first-valid | `make characterize` (`ro-array-core-startup`), rolled up by `time_to_first_valid.py` | `sim/records/<date>-ro-array-core-startup-*.md` |
| G | Digital section max clean sample-clock frequency (`Fmax`) | gate-level, not ngspice: `python3 sim/tb/digital-sta-power/run_sta.py` (needs OpenROAD; not covered by `make characterize`) | `sim/records/<date>-digital-sta-power-*.md` |
| H | Health-test cutoffs (RCT/APT) | closed-form, no PVT dependency — `design/health_test/rct_apt.py` is a library, not a CLI: `python3 -c "from design.health_test.rct_apt import c_rct, c_apt, H0; print(c_rct(H0), c_apt(H0))"` | stdout only; no new record |
| I | Area (whole block) | layout, no PVT dependency: `python3 layout/floorplan/floorplan.py` (needs `klt` + PDK) | `layout/floorplan/reports/area.json` |

#### Row D liveness term (separate, opt-in, batch backend)

`power_rollup.py` requires a liveness term (the shipped per-ring samplers
`xsr1`/`xsr2`), measured by `sim/tb/sampler-core-liveness-active/`. That
testbench has no `tb.json` on purpose, so `make characterize` does not run it
and a Row D reproduction that stops at `make characterize` leaves the term
either unregenerated (committed records reused) or an explicit gap in the
rollup. The full 27-unit grid goes to the batch backend through `klt sim`;
it is never swept locally. Commands, all from
`sim/tools/liveness_sampler_power.py`:

```sh
python3 sim/tools/liveness_sampler_power.py plan                # offline: grid, method, runtime note
python3 sim/tools/liveness_sampler_power.py emit --check        # offline: committed request-grid.json matches the grid
python3 sim/tools/liveness_sampler_power.py emit                # offline: regenerate request-grid.json
python3 sim/tools/liveness_sampler_power.py run --outdir DIR    # OPT-IN: klt sim --backend batch (needs klt + batch access)
python3 sim/tools/liveness_sampler_power.py analyze DIR/grid.report.json   # offline: derived ledger terms
python3 sim/tools/liveness_sampler_power.py record DIR/grid.report.json    # mint NEW append-only records
```

`run` refuses a whole-grid local run (`--backend local` is accepted only with
`--only PROCESS/TEMP/VDD`, a single debug point). If the batch submit fails or
no batch access exists, say so and keep the committed records; do not
substitute a local loop. Freshly regenerated evidence is exactly the new
`sim/records/<date>-sampler-core-liveness-active-NN.md` files `record` writes
(existing records are never edited); `python3 sim/tools/power_rollup.py` then
prints the per-corner total and flags any corner still lacking a liveness
record as a gap.

`sim/characterize.py --dry-run` prints this same mapping (Row D's four
evidence terms and the liveness commands via `ROW_D_EVIDENCE`, and
`ROWS_NOT_COVERED` for the rows it does not produce) alongside the exact
`run_corners.py` command for each row it does — read it, or the script's own
module docstring, if this table and the code ever disagree.

## License

[Apache-2.0](LICENSE). `klayout-tools`, which this project drives, is
MIT-licensed and separately maintained.
