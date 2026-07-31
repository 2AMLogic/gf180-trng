# gf180-trng

**PRIVATE — 2AM Logic proprietary IP. Canary block (wave 1).**

True random number generator on gf180mcu (open PDK), designed by agents driving
[klayout-tools](https://github.com/2AMLogic/klayout-tools) and the
open-source analog flow. Dual purpose, per the canary model: catalog
inventory (eventually silicon-measured) and tool forcing-function
(friction issues go to the public klayout-tools tracker).

Selection rationale: The one verified security-demand signal on this node (Tillitis-sponsored port); cheap to measure (matrix row 10).

## Target specification (DRAFT — engineering to ratify, see issue #1)

| Parameter | Target | Stretch |
|---|---|---|
| Entropy source | ring-oscillator jitter | metastability hybrid |
| Raw rate | > 1 Mbps sustained at the raw tap (sampler output), binding at the slowest-RO corner: `ss` / −10 % / +125 °C ([DR-0003]) | > 4 Mbps, same definition |
| Quality | designed-for-SP 800-90B (raw access + RCT/APT + entropy-source model), plus a **simulation-derived design-stage min-entropy estimate** within the #10 claim limits; 90B validation itself deferred to measured silicon ([DR-0004]) | AIS-31 PTG.2 — same three-tier treatment (structure now, conformance deferred) |
| Health tests | continuous RCT + APT on the **raw** stream, α = 2⁻⁴⁰, APT window W = 1024, cutoffs as formulas in min-entropy H (draft H₀ = 0.5 → `C_RCT` = 81, `C_APT` = 824); failure latches a flag and gates the conditioned path until explicit clear + start-up test ([DR-0002]) | — |
| Power | < 500 µW active, < 1 µA idle | — |
| Area | < 0.05 mm² | — |
| Interface | streaming, mode-selectable raw / conditioned (`OUT_MODE`), + register read (`DATA` conditioned, `RAW_DATA` raw); raw access always available and never gated ([DR-0001]) | — |

> **Rows carrying a DR reference are *proposed* clarifications.** All four
> decision records are status `Proposed` and are ratified together with this
> table in #1; the table stays DRAFT until then. Note the two rows bind at
> **opposite** corners — rate at the slowest-RO corner, min-entropy per bit at
> the fast/high-V/cold corner (see #13) — and neither at nominal.

[DR-0001]: spec/decision-records/DR-0001-raw-and-conditioned-output-paths.md
[DR-0002]: spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md
[DR-0003]: spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0004]: spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md

Maturity ladder: simulation-complete → layout DRC/LVS-clean → shuttle
seat → measured silicon over temperature. The SP 800-90B validation claim
attaches to the last rung, not the first ([DR-0004]).

## Layout

```
spec/          ratified spec + decision records
design/        schematics / netlists (xschem)
sim/           testbenches + PVT corner results (ngspice)
layout/        GDS + DRC/LVS reports (klayout-tools driven)
measurements/  silicon characterization (empty until tape-out)
```

Two conventions govern what lands in those directories:

- **[`sim/README.md`](sim/README.md)** — the append-only evidence record
  format. Every recorded simulation result carries its testbench/netlist
  identity, ngspice version, P/V/T corner, and seeds; re-runs are new
  records, never edits. A transient-noise result without its seeds is not
  evidence.
- **[`spec/decision-records/TEMPLATE.md`](spec/decision-records/TEMPLATE.md)**
  — the numbered decision-record template (`DR-0001-<slug>.md`). Spec
  changes go through a decision record.

### `sim/` harness bootstrap

The PVT corner runner is a stdlib-only Python CLI, bootstrapped from the
harness pattern in [`2AMLogic/gf180-bandgap`](https://github.com/2AMLogic/gf180-bandgap)
(gf180-bandgap#23) and adapted to emit into this repo's own ratified
`sim/README.md` record format — see
[`DR-0005`](spec/decision-records/DR-0005-sim-harness-record-granularity.md)
for how the two conventions reconcile.

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
```

Bootstrap testbenches under `sim/tb/` exercise the harness itself (not yet
the TRNG design, which has no `design/` content as of this bootstrap):
`smoke-op` (trivial op-point smoke test), `corner-sanity-nfet-id` (the
automated guardrail behind `sim/tools/corner_sanity_check.py`), and
`nfet-mismatch-seed` (demonstrates per-run seed control and exact
reproducibility for stochastic analyses — see `sim/README.md`'s "no seed,
no evidence" rule).
