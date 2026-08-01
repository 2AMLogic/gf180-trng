# gf180-trng

A true random number generator on **gf180mcu**, GlobalFoundries' open PDK,
designed end to end by AI agents driving an entirely open-source analog flow:
xschem for schematics, ngspice for simulation, and
[klayout-tools](https://github.com/2AMLogic/klayout-tools) for layout.

**Status: early. Nothing here has been fabricated, and nothing here has been
measured on silicon.** As of this writing the repository contains an evidence-record
convention, seven decision records, an entropy-source architecture survey, and a
working PVT corner simulation harness with its first device-characterization
results. There is no schematic in `design/` yet and no GDS in `layout/`. The
specification table below was
[ratified on 2026-07-31](spec/ratification-2026-07-31-target-spec.md) and is
binding on the design — but several of its rows are explicitly *unmeasured
placeholders*, and the table labels which.

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

| Parameter | Target | Stretch |
|---|---|---|
| Entropy source | **N-way array of independent free-running ring oscillators, XOR-combined ahead of a single sampler**, N fixed by the jitter-budget sizing law `Q_array ≥ 1.5 × 4.0×10⁻³` at the entropy-binding corner ([DR-0007]) | metastability hybrid, scoped as a *secondary tap on the RO core* — not a free-standing source |
| Raw rate | > 1 Mbps sustained at the raw tap (sampler output), binding at the slowest-RO corner: `ss` / −10 % / +125 °C ([DR-0003]) | > 4 Mbps, same definition |
| Raw min-entropy per bit | **placeholder — H₀ = 0.5 bit/sample is a design *target*, not a measurement.** Stated at the entropy-binding corner (measured minimum-`Q` corner; expected cold / +10 % supply, process letter TBD by #13). The measured number is owed by #12/#13 as a simulation-derived design estimate ([DR-0004] Tier 2, [DR-0007] §2–4) | — |
| Quality | designed-for-SP 800-90B (raw access + RCT/APT + entropy-source model), plus a **simulation-derived design-stage min-entropy estimate** within the #10 claim limits; 90B validation itself deferred to measured silicon ([DR-0004]) | AIS-31 PTG.2 — same three-tier treatment (structure now, conformance deferred) |
| Conditioning | **TBD per #8** ([DR-0003] §6, [DR-0004] §Constraint on #8). Default assumption: a lightweight **non-vetted** function; #8's own DR owes the function, its vetted/non-vetted status, the compression ratio K, an area estimate, and the non-vetted entropy accounting | a 90B-*vetted* conditioning function, if #8's area estimate shows one fits |
| Delivered (post-conditioning) rate | **TBD per #8** — `R_cond = R_raw / K` at the same binding corner as the raw-rate row; deliberately **not** inferred from that row until K exists ([DR-0003] §6) | — |
| Health tests | continuous RCT + APT on the **raw** stream, α = 2⁻⁴⁰, APT window W = 1024, cutoffs as formulas in min-entropy H (at H₀ = 0.5 → `C_RCT` = 81, `C_APT` = 824); failure latches a flag and gates the conditioned path until explicit clear + start-up test. The parameterization has a hard floor: **no valid APT cutoff exists at H ≤ 0.03** ([DR-0002]) | — |
| Time-to-first-valid | **≥ ~1.05 ms** at 1 Mbps — an arithmetic floor, not a measurement: 1024 consecutive raw samples for the start-up health test (1.024 ms) plus conditioner latency. Applies at power-on and after every alarm clear; binds at `ss` / −10 % / +125 °C (slowest sampling) ([DR-0002] §Failure behavior) | — |
| Power | < 500 µW active, binding at `ff` / +10 % supply (fastest RO — max measured `f_osc` 2.30 GHz at −40 °C); < 1 µA idle, binding at `ff` / +10 % / +125 °C (max leakage). **Neither figure has any evidence behind it yet** — see the note below | — |
| Area | < 0.05 mm² | — |
| Operating envelope | −40 … +125 °C, 3.3 V ± 10 % (2.97–3.63 V). Every entropy, rate and health-test claim above holds **over this envelope and only over it**; the envelope is the security boundary, since an attacker chooses the operating point. Outside it, behavior is health-test-detected, not specified | — |
| Interface | streaming, mode-selectable raw / conditioned (`OUT_MODE`), + register read (`DATA` conditioned, `RAW_DATA` raw); raw access always available and never gated ([DR-0001]) | — |

**Scope**: this block is an **entropy source only** — there is no DRBG in it,
and it defines no seeding or reseeding semantics. An integrator that needs a
DRBG supplies its own and treats this block as the seed source.

> **Ratified, with three rows explicitly unmeasured.** The table was ratified
> on 2026-07-31 by engineering (Robb) — see
> [`spec/ratification-2026-07-31-target-spec.md`](spec/ratification-2026-07-31-target-spec.md)
> and issue #1 — together with the amendment package in #29. Every row carrying
> a DR reference is now `Accepted`; a row that cannot be met is a **superseding
> decision record**, not an edit. What ratification does *not* do is turn
> placeholders into claims:
>
> - **Raw min-entropy per bit** is a design target (H₀ = 0.5). The entropy
>   source is *sized* to hit it ([DR-0007]); it has not been measured (#12/#13).
> - **Conditioning / delivered rate** are deferred to #8 with reasons on the
>   record — deferred, not omitted.
> - **Power** has no supply-current or leakage measurement anywhere in `sim/`;
>   the characterization task is #32. "Idle" means: all ring oscillators
>   stopped and no bits being produced, with the block powered and register
>   state retained — i.e. leakage plus static bias only. Both halves of the row
>   are unevidenced, and the < 1 µA idle
>   figure is order-of-magnitude questionable for an ungated few-kGE digital
>   section at `ff`/+125 °C without power gating. [DR-0007] additionally records
>   that its first-cut array size projects far more active power than this row
>   allows — a tracked, unresolved conflict, not a rounding error.
>
> Note also that rows bind at **different** corners, and none at nominal: rate
> at the slowest-RO corner, min-entropy per bit at the *least*-jitter
> (minimum-`Q`) corner, power at the fastest/leakiest corner, time-to-first-valid
> at the slowest-sampling corner.

[DR-0001]: spec/decision-records/DR-0001-raw-and-conditioned-output-paths.md
[DR-0002]: spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md
[DR-0003]: spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0004]: spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0007]: spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md

Maturity ladder: simulation-complete → layout DRC/LVS-clean → shuttle
seat → measured silicon over temperature. **The block is on the first rung.**
The SP 800-90B validation claim attaches to the last rung, not the first
([DR-0004]) — a simulated min-entropy estimate is not an entropy assessment,
and this repository will not let one be read as the other.

## Layout

```
spec/          spec + decision records
design/        schematics / netlists (xschem)                 — empty
sim/           testbenches + PVT corner results (ngspice)
layout/        GDS + DRC/LVS reports (klayout-tools driven)   — empty
measurements/  silicon characterization                       — empty until tape-out
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
pull request, the checks that need no PDK: a Python/shell syntax check, the
harness unit tests on Python 3.10 and 3.13, and `sim/selftest.sh` — whose
PDK-dependent stages detect the missing PDK and skip themselves on a hosted
runner. The same set is `npm run check:ci` locally.

The smoke run and the corner-sanity check are deliberately *not* on the PR
path: they need ngspice and a multi-gigabyte PDK, and a pull request should not
block on provisioning either. They run instead on a nightly schedule —
[`.github/workflows/pdk-nightly.yml`](.github/workflows/pdk-nightly.yml) builds
the pinned ngspice release, installs the gf180mcu PDK at a pinned open_pdks
commit, and runs `sim/selftest.sh --require-pdk`, the form that fails rather
than skips. That job writes no evidence records and fails if `sim/records/`
changes.

The nightly run does not replace the local one: run `sim/selftest.sh
--require-pdk` (or `npm run check:all`) on a machine that has ngspice and the
PDK before committing an evidence record. `ci.yml` carries the full inventory
of which self-checks run where, and why.

Bootstrap testbenches under `sim/tb/` exercise the harness itself (not yet
the TRNG design, which has no `design/` content as of this bootstrap):
`smoke-op` (trivial op-point smoke test), `corner-sanity-nfet-id` (the
automated guardrail behind `sim/tools/corner_sanity_check.py`), and
`nfet-mismatch-seed` (demonstrates per-run seed control and exact
reproducibility for stochastic analyses — see `sim/README.md`'s "no seed,
no evidence" rule).

## License

[Apache-2.0](LICENSE). `klayout-tools`, which this project drives, is
MIT-licensed and separately maintained.
