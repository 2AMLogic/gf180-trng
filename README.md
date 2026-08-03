# gf180-trng

A true random number generator on **gf180mcu**, GlobalFoundries' open PDK,
designed end to end by AI agents driving an entirely open-source analog flow:
xschem for schematics, ngspice for simulation, and
[klayout-tools](https://github.com/2AMLogic/klayout-tools) for layout.

**Status: early. Nothing here has been fabricated, and nothing here has been
measured on silicon.** As of this writing the repository contains an evidence-record
convention, ten decision records, an entropy-source architecture survey, and a
working PVT corner simulation harness with its first device-characterization
results. `design/` holds two blocks — the digital conditioner, as a behavioural
model plus synthesisable RTL, and the analog entropy source, as xschem
schematics with a deterministic SPICE netlist export — and there is still no
GDS in `layout/`. The specification table below was
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
| Raw min-entropy per bit | **placeholder — H₀ = 0.5 bit/sample is a design *target*, not a measurement.** Stated at the entropy-binding corner, which #13 measured over the full covered 27-point grid as **`ss` / +125 °C / 3.63 V** — the hot end of the `ss`/+10 % edge, *not* the cold end [DR-0012] predicted from three points ([DR-0015]; `fs`/`sf` remain uncovered per [DR-0006]). The measured `H` figure itself is still owed by #12 as a simulation-derived design estimate ([DR-0004] Tier 2, [DR-0007] §2–4) | — |
| Quality | designed-for-SP 800-90B (raw access + RCT/APT + entropy-source model), plus a **simulation-derived design-stage min-entropy estimate** within the #10 claim limits; 90B validation itself deferred to measured silicon ([DR-0004]) | AIS-31 PTG.2 — same three-tier treatment (structure now, conformance deferred) |
| Conditioning | **non-vetted** 32-bit CRC-32 LFSR compression (Galois, poly `0xEDB88320`), state cleared every block, **K = 8** — 256 raw bits in : one 32-bit word out. Creditable output entropy **0.85 bit per output bit** (SP 800-90B's non-vetted cap) for any raw stream at or above **H = 0.107 bit/sample**; a 4.70× margin under the H₀ = 0.5 target. ~0.005–0.008 mm² ([DR-0008]) | a 90B-*vetted* conditioning function — **rejected on area**: a compact serialised AES-128 is 88–124 % of the whole block budget ([DR-0008] §4). Live again only if the area budget grows |
| Delivered (post-conditioning) rate | **`R_cond = R_raw / K` > 125 kbps** at the raw-rate row's binding corner (`ss` / −10 % / +125 °C), K = 8; > 500 kbps at the stretch raw rate. **Derived from a target, not measured** — it inherits the raw-rate row's status exactly, and becomes a measured figure only when `R_raw` does ([DR-0003] §6, [DR-0008] §3) | — |
| Health tests | continuous RCT + APT on the **raw** stream, α = 2⁻⁴⁰, APT window W = 1024, cutoffs as formulas in min-entropy H (at H₀ = 0.5 → `C_RCT` = 81, `C_APT` = 824); failure latches a flag and gates the conditioned path until explicit clear + start-up test. The parameterization has a hard floor: **no valid APT cutoff exists at H ≤ 0.03** ([DR-0002]) | — |
| Time-to-first-valid | **≥ ~1.28 ms** at 1 Mbps — an arithmetic floor: 1024 consecutive raw samples for the start-up health test (1.024 ms) plus 256 samples of conditioner latency (0.256 ms), which do **not** overlap because the conditioner is held flushed while gated. Applies at power-on and after every alarm clear; binds at `ss` / −10 % / +125 °C (slowest sampling) ([DR-0002] §Failure behavior, [DR-0008] §7). **Now measured (#14): 1.281 ms**, the floor plus one sampler clock plus a 4.1–12.4 ns oscillator start-up (4.4–13.4 ns before #78's buffer adoption) — the row is met and the floor is confirmed as a floor ([`sim/characterization-startup-and-power-budget.md`](sim/characterization-startup-and-power-budget.md)) | — |
| Power | < 500 µW active, binding at `ff` / +10 % supply (fastest RO — max measured `f_osc` 2.30 GHz at −40 °C); < 1 µA idle, binding at `ff` / +10 % / +125 °C (max leakage). **Now evidenced (#14, re-measured after #78's buffer adoption): active 433 µW — met, at 86.6 % of the row. Idle 4.46 µA — missed by 4.5×**, and the cause is ungated standard-cell leakage in the digital section (4.43 µA, an estimate), not the analog block (32.8 nA, measured). The miss is reported, not absorbed: see [`sim/characterization-startup-and-power-budget.md`](sim/characterization-startup-and-power-budget.md) and [DR-0017] (`Proposed`), and the note below | — |
| Area | < 0.05 mm² | — |
| Operating envelope | −40 … +125 °C, 3.3 V ± 10 % (2.97–3.63 V). Every entropy, rate and health-test claim above holds **over this envelope and only over it**; the envelope is the security boundary, since an attacker chooses the operating point. Outside it, behavior is health-test-detected, not specified | — |
| Interface | streaming, mode-selectable raw / conditioned (`OUT_MODE`), + register read (`DATA` conditioned, `RAW_DATA` raw); raw access always available and never gated ([DR-0001]). Instantiated as four word-addressed registers — `CTRL`, `STATUS`, `DATA`, `RAW_DATA` — plus a 32-bit valid/ready streaming port, with a health-test gate that flushes the conditioned path and **never** the raw one ([DR-0013]) | — |

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
>   source is *sized* to hit it ([DR-0007]); the corner it has to hold at is
>   now measured over the whole covered grid and moved as a result
>   ([DR-0015], from #13), but `H` itself has not been measured (#12).
> - **Conditioning / delivered rate** were deferred to #8; [DR-0008] has since
>   filled both rows in. The delivered rate is still `R_raw / K` derived from a
>   *target* raw rate — filling in K does not turn the raw-rate row into a
>   measurement.
> - **Power** was ratified with no supply-current or leakage measurement
>   anywhere in `sim/`. "Idle" means: all ring oscillators stopped and no bits
>   being produced, with the block powered and register state retained — i.e.
>   leakage plus static bias only. #32 measured the delay cell, #7 the shipped
>   array, and **#14 has now closed both halves of the row** — with one met and
>   one missed:
>   - **Active: met.** 433 µW at `ff`/−40 °C/3.63 V — entropy source 393 µW
>     (measured), sampler 16.9 µW (measured), digital section 23 µW (a
>     library-based estimate; those three blocks have no netlist to simulate).
>     [DR-0010]'s stated worry, that the array leaves only ~85 µW for
>     everything downstream, holds with a little more room than it did:
>     everything downstream needs 40 µW of the 107 µW the array leaves.
>     #14 first measured this row at **454 µW** (entropy source 415 µW); #78
>     then adopted the per-ring output buffer ([DR-0018]), which *returns*
>     power rather than spending it, and the families that measure the array
>     were re-run against the buffered netlist — this is that re-run's number.
>   - **Idle: missed, by 4.5×.** 4.46 µA at `ff`/+125 °C/3.63 V. The
>     ratification note above guessed the cause exactly — the analog block
>     idles at 32.8 nA (3.3 % of the row, measured across 45 corners), and the
>     entire miss is ungated standard-cell leakage in the conditioner, health
>     tests and interface, whose 658 flip-flops alone exceed the row by 2.2×.
>     `gf180mcu_fd_sc_mcu7t5v0` ships no retention flop and no power-switch
>     cell, so the obvious fix is not a library instantiation.
>
>   Per `CLAUDE.md` no row is edited here: the miss goes to [DR-0017]
>   (`Proposed`), which sizes the four available responses against the
>   evidence. [DR-0007]'s separate conflict — that its first-cut array size
>   projected far more active power than this row allows — was resolved by
>   [DR-0010] shrinking the array to N = 2, which is the 415 µW measured above.
>
> Note also that rows bind at **different** corners, and none at nominal: rate
> at the slowest-RO corner, min-entropy per bit at the *least*-jitter
> (minimum-`Q`) corner, power at the fastest/leakiest corner, time-to-first-valid
> at the slowest-sampling corner. One caveat #14 added to that last one:
> [DR-0012] made the sample clock a *fixed external* clock, so the sample
> period does not move with PVT, and 99.999 % of the time-to-first-valid row is
> 1281 fixed sample periods. Its stated binding corner is formally correct and
> practically vacuous — the spread across the whole covered grid is 9 ns on
> 1.281 ms. What does move that row is the **rate**, and the rate row is
> unsettled: at [DR-0010]'s proposed 500 bps the same 1281 samples take
> **2.562 s**.

[DR-0001]: spec/decision-records/DR-0001-raw-and-conditioned-output-paths.md
[DR-0002]: spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md
[DR-0003]: spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0004]: spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0006]: spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md
[DR-0007]: spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md
[DR-0008]: spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md
[DR-0009]: spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0010]: spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0012]: spec/decision-records/DR-0012-sampler-fixed-external-clock.md
[DR-0013]: spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md
[DR-0015]: spec/decision-records/DR-0015-entropy-binding-corner-moves-to-the-hot-slow-corner.md
[DR-0017]: spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
[DR-0018]: spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md

Maturity ladder: simulation-complete → layout DRC/LVS-clean → shuttle
seat → measured silicon over temperature. **The block is on the first rung.**
The SP 800-90B validation claim attaches to the last rung, not the first
([DR-0004]) — a simulated min-entropy estimate is not an entropy assessment,
and this repository will not let one be read as the other.

## Layout

```
spec/          spec + decision records
design/        analog schematics / netlists (xschem) + digital blocks
sim/           testbenches + PVT corner results (ngspice)
layout/        GDS + DRC/LVS reports (klayout-tools driven)   — empty
measurements/  silicon characterization                       — empty until tape-out
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
harness unit tests on Python 3.10 and 3.13, the two spec-arithmetic checks that
are pure derivations over committed records (`sim/tools/jitter_energy_law.py
--check` and `sim/tools/array_sizing.py --check`), the register-map staleness
guard (`design/interface/regmap.py --check`), and `sim/selftest.sh` — whose
PDK-dependent stages detect the missing PDK and skip themselves on a hosted
runner. The same set is `npm run check:ci` locally.

The smoke run, the corner-sanity check and the schematic-vs-netlist staleness
guard (`python3 design/netlist.py --check`) are deliberately *not* on the PR
path: they need ngspice, xschem and a multi-gigabyte PDK, and a pull request
should not block on provisioning any of them. They run instead on a nightly
schedule — [`.github/workflows/pdk-nightly.yml`](.github/workflows/pdk-nightly.yml)
builds the pinned ngspice release, installs the gf180mcu PDK at a pinned
open_pdks commit, and runs both `design/netlist.py --check` and
`sim/selftest.sh --require-pdk`, the form that fails rather than skips. That job
writes no evidence records and fails if `sim/records/` changes.

The nightly run does not replace the local one: run `sim/selftest.sh
--require-pdk` (or `npm run check:all`) on a machine that has ngspice and the
PDK before committing an evidence record. `ci.yml` carries the full inventory
of which self-checks run where, and why.

Some testbenches under `sim/tb/` exercise the harness itself rather than the
TRNG design — they predate any `design/` content and are kept as the harness's
own regression set: `smoke-op` (trivial op-point smoke test),
`corner-sanity-nfet-id` (the automated guardrail behind
`sim/tools/corner_sanity_check.py`), and `nfet-mismatch-seed` (demonstrates
per-run seed control and exact reproducibility for stochastic analyses — see
`sim/README.md`'s "no seed, no evidence" rule). The rest exercise the design:
`rostage-noise`, `ro-array-core-power` and `ro-array-sanity-jitter` run against
the netlists exported from `design/xschem/`.

`sim/tb/conditioner-crc32/` is the first **behavioral-level** testbench: it
has no `tb.json`, is not discovered by `run_corners.py`, and is run directly
(`python3 sim/tb/conditioner-crc32/run_demo.py`). Its records carry
`level: behavioral` and no P/V/T corner, and may not be cited for anything
corner-dependent — see `sim/README.md` §Behavioral-level records and
[DR-0009]. `sim/tb/interface-regfile/` is the second, and runs both digital
blocks against each other with the conditioner's `en`/`flush` taken from the
interface's own outputs — the inter-block contract, not a stand-in for it.

## License

[Apache-2.0](LICENSE). `klayout-tools`, which this project drives, is
MIT-licensed and separately maintained.
