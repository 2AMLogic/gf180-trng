# Start-up, time-to-first-valid, and the whole-block power budget

Status: characterization complete for issue #14. Supplies the first evidence
this repository has ever had behind two ratified README rows —
`Time-to-first-valid` and `Power` — both of which were ratified explicitly
unmeasured.

**This document is an ordinary summary, not evidence.** Every measured number
below cites the `sim/records/` stem family that produced it, and every number
that is an *estimate* rather than a measurement says so on the line it appears
on. Two commands regenerate everything here from committed records:

```sh
python3 sim/tools/time_to_first_valid.py
python3 sim/tools/power_rollup.py
```

**One ratified row is met and one is missed, and neither is edited by this
issue.** Per `CLAUDE.md`, a row the evidence contradicts is **reported, not
relaxed**: the miss is stated below with numbers and routed to
[`DR-0017`](../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md),
which proposes what to do about it and is `Proposed`, not ratified. Nothing
here decides anything.

---

## Headline

| Row | Ratified target | Measured / estimated | Binding corner | Verdict |
|---|---|---|---|---|
| Time-to-first-valid | ≥ ~1.28 ms at 1 Mbps (an arithmetic floor) | **1.281 ms** | `ss`/+125 °C/2.97 V, but see below — the corner barely matters | **Met**, and the floor is confirmed as a floor |
| Power — active | < 500 µW | **454.2 µW** (415.3 measured + 15.8 measured + 23.1 **estimated**) | `ff`/−40 °C/3.63 V | **Met**, 90.8 % of the row |
| Power — idle | < 1 µA | **4.46 µA** (32.8 nA measured + 4.43 µA **estimated**) | `ff`/+125 °C/3.63 V | **Missed, 4.5×** → [DR-0017] |

---

## What is and is not covered

**Covered, transistor-level, measured:**

- The shipped entropy array's start-up from its real clamped idle state, over
  the 27-point covered grid — `sim/records/2026-08-02-ro-array-core-startup-{01..27}.md`.
- Both `sampler_dff` instances' active energy per switching event, over the
  full 45-point grid — `sim/records/2026-08-02-sampler-dff-active-current-{01..45}.md`.
- The whole of `sampler_core` (two rings + XOR combiner + both flops) in the
  README's ratified idle state, over the full 45-point grid —
  `sim/records/2026-08-02-sampler-core-idle-leakage-{01..45}.md`.
- The array's active power and its `xo` transition rate, at each corner —
  pre-existing, `…-ro-array-core-pvt-q-{01..27}.md` and `…-ro-array-core-power-*.md`.

**Covered, estimated, never measured:** the conditioner (#8), the health tests
(#11) and the interface (#26). These are RTL/behavioural only — no schematic,
no netlist, no synthesis flow in this repository — so there is nothing to hand
ngspice. `design/digital_power_estimate.py` is the substitute: a gate-level
inventory of each block's RTL evaluated against the `gf180mcu_fd_sc_mcu7t5v0`
Liberty library that ships with the PDK. It is a [DR-0004] Tier 2 estimate and
is labelled as one everywhere it appears.

That script does **not** mint a `sim/records/` entry, deliberately. It runs no
simulation: `sim/records/` is simulation evidence, and a library lookup dressed
as a record would blur exactly the measured/estimated line this whole document
depends on. It follows the precedent `design/conditioner/area_estimate.py`
already set, whose area figures DR-0008 cites directly from the script.

**Not covered, and not projected:** post-layout parasitics (#15/#17), pads and
I/O, any clock source (the block contains none — [DR-0012]), and the two taps
that exist but are not instantiated by the shipped block (see
[Two taps that are not in the total](#two-taps-that-are-not-in-the-total)).

---

## Time-to-first-valid

### What the row claimed, and what was missing from it

> **≥ ~1.28 ms** at 1 Mbps — an arithmetic floor, not a measurement: 1024
> consecutive raw samples for the start-up health test (1.024 ms) plus 256
> samples of conditioner latency (0.256 ms), which do not overlap.

Two things were missing. The floor starts counting at the first raw sample, as
though the entropy source were already running — the oscillator's own start-up
was assumed away rather than bounded. And it converts sample *counts* into a
time using one rate, without saying that the rate row is itself unsettled.

### The oscillator starts in one period

`sim/tb/ro-array-core-startup/` holds `en` low from t = 0, lets ngspice solve
the clamped operating point, and toggles `en` at 5 ns. It uses **no `.ic`
kick** — the running decks need one because at `en = 1` a noiseless solver can
sit at the ring's unstable symmetric equilibrium, but at `en = 0` the NAND's
output is forced high independently of its ring input, the loop gain is zero,
and there is exactly one stable DC solution. The rising `en` edge, not an
initial condition the testbench invented, is what starts the oscillation.

Across all 27 corners, `sim/tools/time_to_first_valid.py` (1 % period-convergence
band, applied to nine successive period estimates per ring, first-and-thereafter):

| Quantity | Range over the 27-point grid |
|---|---|
| Oscillator start-up, `en` → stable period, both rings | **4.40 ns** (`ff`/−40 °C/3.63 V) … **13.38 ns** (`ss`/+125 °C/2.97 V) |
| …as a multiple of that corner's own steady period | 1.02 – 1.03 × `T₀` |
| First rising edge on the XOR node `xo` after `en` | 1.96 – 5.89 ns |
| Ring swing, early window ÷ late window | 0.967 – 1.069 |

The array reaches its steady period in **essentially one ring period**. That
is a property of the topology rather than a lucky result: this is a
NAND-clamped digital ring released from a defined static state, not a resonator
building up amplitude, so there is no envelope to grow. The swing-ratio column
is there to prove the same thing about amplitude independently — a period that
converged while the amplitude was still climbing would show up as a ratio well
below 1, and none does.

Two runner-up mechanisms are also bounded rather than assumed:

- **`xo` before the rings settle.** The XOR node's first edge arrives *earlier*
  than either ring's settled time, so the sampler is never waiting on the
  combiner.
- **Sampler reset release.** `sim/tb/sampler-dff-reset-clocked/` already shows
  `Q` at full rail (within ±3.4 ppm of supply) on the first rising edge after
  `rst_n` releases, at all 45 PVT points. The rollup charges exactly one sample
  period for it.

### The total, and what actually sets it

At DR-0003's ratified 1 Mbps:

| Term | Samples | Time | Share |
|---|---|---|---|
| Oscillator start-up (measured, worst corner) | — | 13.38 ns | 0.001 % |
| Sampler, reset release → first raw bit | 1 | 1 µs | 0.08 % |
| DR-0002 start-up health test | 1024 | 1.024 ms | 79.9 % |
| DR-0008 conditioner latency (K = 8) | 256 | 256 µs | 20.0 % |
| **Total** | **1281** | **1.281 ms** | |

**The row is met and the floor is confirmed as a floor** — the measured total
is 1.00079× the README's ~1.28 ms, the excess being the one sampler clock the
floor did not count. The oscillator contributes one part in 10⁵.

### Two things this changes about how the row should be read

1. **Its stated binding corner is very nearly vacuous.** The row says it "binds
   at `ss` / −10 % / +125 °C (slowest sampling)". [DR-0012] made the sample
   clock a *fixed external* clock, so the sample period does not move with PVT
   at all, and 99.999 % of this row is 1281 fixed sample periods. The corner
   spread across the whole grid is **9 ns on 1.281 ms**. The corner label is
   still formally correct — `ss`/+125 °C/2.97 V *is* the slowest — but a reader
   who takes it to mean the row is corner-sensitive is being misled by it.
2. **The row is a rate consequence, and the rate row is unsettled.** At
   [DR-0010]'s proposed 500 bps the same 1281 samples take **2.562 s** — 2000×
   worse, and a materially different product claim. DR-0010 §Consequences
   already names this row as one of the three things that must be re-derived on
   acceptance; this document supplies the arithmetic so that re-derivation is a
   lookup rather than a fresh analysis:

   ```sh
   python3 sim/tools/time_to_first_valid.py --rate 500
   ```

---

## Power

### Active: met, at 90.8 % of the row

At the binding corner `ff`/−40 °C/3.63 V, from
`python3 sim/tools/power_rollup.py`:

| Term | Power | Share of the < 500 µW row | Source |
|---|---|---|---|
| Entropy array (2 rings + XOR combiner) | 415.3 µW | 83.1 % | **measured**, `…-ro-array-core-power-04.md` / `…-pvt-q-*` |
| Sampler, data term | 15.7 µW | 3.1 % | **measured**, `…-sampler-dff-active-current-*` × that corner's `xo_trans_per_s` |
| Sampler, clock term | 60.3 nW | 0.01 % | **measured**, same family |
| Conditioner + health tests + interface | 23.1 µW | 4.6 % | **ESTIMATE**, `design/digital_power_estimate.py` |
| **Total** | **454.2 µW** | **90.8 %** | |

DR-0010 §Consequences stated the risk precisely: "the entropy source uses 83 %
of the active budget … leaving ~85 µW for the sampler, health tests,
conditioner and register file — none of which exist or are measured. That is a
tight allocation and it is stated here rather than discovered later." That
allocation now has numbers behind it: **everything downstream of the array
needs 38.9 µW of the 84.7 µW available, i.e. 45.9 % of the headroom.** The
allocation holds, with roughly a factor of two in hand.

#### The sampler burns power at the entropy node's rate, not the clock's

This is the non-obvious part of the sampler number and the reason
`sim/tb/sampler-dff-active-current/` measures energy per *event* instead of an
average current. `sampler_dff` is a transmission-gate master-slave flop: while
`clk` is low its master gate is transparent, so `xo`'s transitions propagate
into the master's internal nodes for **half of every clock period**. The flop
therefore dissipates at `xo`'s rate — 3.1×10⁸ to 9.6×10⁸ transitions/s across
the grid — and not at the 1 MHz sample rate. The measured decomposition, at
`ff`/−40 °C/3.63 V:

| Event | Charge | Rate applied | Contribution |
|---|---|---|---|
| One `D` transition, master **open** (`clk` low) | 9.02 fC | 4.80×10⁸ /s (½ × `xo_trans_per_s`) | 15.7 µW |
| One `D` transition, master **shut** (`clk` high) | ~0 (5×10⁻²⁰ C) | 4.80×10⁸ /s | negligible |
| One clock cycle, both instances | 8.3 fC each | 1×10⁶ /s | 60.3 nW |

The clock term is **260× smaller** than the data term. A deck that had simply
averaged current over one clock period would have reported the sum without
exposing which rate carried it — and would have been wrong by ~4× the moment
anyone quoted it against a different `xo` rate, which is exactly what
[DR-0010]'s rate change does. Only `xsb` (whose D is `xo`) pays the data term;
`xsv`'s D is tied to `vdd` and pays the clock term alone.

### Idle: missed by 4.5×, and the analog side is not the reason

At the binding corner `ff`/+125 °C/3.63 V:

| Term | Current | Share of the < 1 µA row | Source |
|---|---|---|---|
| Whole `sampler_core` — 2 rings + XOR + both flops, clamped, reset released, clock parked | **32.8 nA** | 3.3 % | **measured**, `…-sampler-core-idle-leakage-*` |
| Conditioner + health tests + interface, 658 flops / 1655 cells, no power gating | **4.43 µA** | 442.5 % | **ESTIMATE**, `design/digital_power_estimate.py` |
| **Total** | **4.46 µA** | **446 %** | |

Two separate findings, and they point in opposite directions:

- **The analog block is comfortable.** 32.8 nA at the leakiest corner is 3.3 %
  of the whole row, and the two clock-park states differ by only ~12 % (32.8 nA
  parked low, 29.2 nA parked high). The clamped ring array is a genuinely quiet
  idle state: every node sits at a rail with no crowbar path. This is the first
  measurement of the *shipped* block's idle current — the pre-existing
  `ro-inv-05stage-stopped-leakage` family measured the characterization-cell
  5-stage ring, not the shipped 11-stage starved array, and not the XOR tree or
  the flops.
- **The digital section blows the row on standard-cell leakage alone**, before
  any dynamic activity at all. Even the most favourable input-state assumption
  in the Liberty library gives 1.85 µA, still 1.8× over.

The README's own ratification note predicted this in words — "the < 1 µA idle
figure is order-of-magnitude questionable for an ungated few-kGE digital
section at `ff`/+125 °C without power gating" — and this is the measurement
that turns the prediction into a number. The response goes to
[`DR-0017`](../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md),
which sizes the four available levers (power gating, retention, shrinking the
FIFOs, moving the row) against this evidence. **No row is edited here.**

#### How much of that estimate could be wrong

The idle miss rests on an estimate, so its uncertainty matters more than the
active number's does. The estimate splits almost exactly in half, and the two
halves have very different standing:

| Contribution | Leakage | Share of the < 1 µA row | Standing |
|---|---|---|---|
| 658 flip-flops | 8.06 µW = **2.24 µA** | 224 % | **Enumerated.** Not an estimate. |
| 997 combinational cells | 7.87 µW = **2.19 µA** | 219 % | Structural estimate. |
| Total | 15.93 µW = **4.43 µA** | 442 % | |

- **The flop count is not an estimate.** 41 + 45 + 572 = 658 is read directly
  off the three modules' `reg` declarations at their shipped default
  parameters, and `sim/tests/test_power_rollups.py` fails if any parameter the
  count depends on (`FIFO_DEPTH`, `TRNG_LEVEL_BITS`, `C_RCT`, `W`, K) moves
  without the inventory being revisited. 512 of the 658 are the interface's
  two 8 × 32-bit output FIFOs.
- **Per-cell leakage is characterised library data**, not a model — read out of
  the PDK's own `ff_125C_3v60` Liberty file, which is exactly the row's binding
  corner. The library is characterised at 3.60 V against the envelope's
  3.63 V; that 0.8 % gap is far below the estimate's own uncertainty and is not
  corrected for.
- **The combinational half is soft, and it is not the load-bearing half.** Its
  largest single item is the FIFO read path: 576 `mux2_1` cells (two 32-bit 8:1
  read muxes, the 4:1 `reg_rdata` mux and the streaming mux) at 6.28 µW, which
  a synthesiser might implement more cheaply than a mux tree. **Delete every
  combinational cell in all three blocks and the flops alone still miss the row
  by 2.2×**; double every combinational count instead and the total goes to
  6.6 µA.

Getting from 4.46 µA to under 1 µA is therefore not a matter of tightening the
estimate — the part of it that is not an estimate already misses by 2.2×. It
needs a design change, which is what DR-0017 is for.

### Two taps that are not in the total

Both are measured, both exist in the tree, and neither is instantiated by the
shipped `sampler_core`/`trng_top`. They are excluded on the same basis
`design/README.md` already excludes the first, and `power_rollup.py --with-taps`
adds them so the cost of adopting one is a command rather than an argument:

| Tap | Measured cost | Effect on the active row if adopted |
|---|---|---|
| Metastability hybrid ([DR-0011], `ro_array_core_meta`) | ~187 µW | 454 → 641 µW, **1.28× over** |
| Per-ring liveness digitizer ([DR-0016], `sim/tb/ring-liveness-tap-power/`) | ~81 µW | 454 → 536 µW, **1.07× over** |

Adopting either one moves the active row from met to missed. That is a real
constraint on #65 (promoting the liveness tap into shipped RTL/schematic) and
on any future decision to ship the hybrid, and it is stated here so neither is
taken as free.

---

## Method notes worth knowing before re-running anything

Three method choices in this work were arrived at by rejecting a more obvious
one. Each is argued in full in its testbench header; they are listed here
because each was a *wrong answer that ran cleanly*, which is the dangerous kind.

1. **`op` on `sampler_core` reports 193 µA of "leakage".** `sampler_dff`'s two
   storage loops are bistable, so once `rst_n` releases they have an unstable
   mid-rail DC solution alongside the two real ones, and nothing in an
   operating-point analysis prefers a stable one. The solver lands at 1.543 V
   on a 3.63 V rail with every latch inverter at its trip point, and reports
   crowbar current — five orders of magnitude above the 32.8 nA the settled
   transient measures. `sim/tb/sampler-core-idle-leakage/` therefore drives the
   block into idle the way a real one gets there (reset, one clock edge, then
   park) and reads the current 600 ns later, cross-checked against a second
   window.
2. **Instantaneous branch-current reads are unusable in a quiescent
   transient.** With nothing switching, ngspice's timestep grows to a large
   fraction of the measurement window, and `meas ... find i(vsource) at=1u`
   returned a value disagreeing with the integrated one by three orders of
   magnitude — and in sign. Every current in the idle family is a
   charge-integrator average over a stated window, with a second window as the
   record's own self-check.
3. **Averaging the sampler's current over one real clock period cannot be
   run,** and would be the wrong instrument even if it could. At the real
   `xo` rate one 1 µs clock period is ~2000 data periods; a first attempt at
   exactly that deck timed out at every one of 45 PVT points after 300 s each.
   The per-event decomposition is both affordable and more informative, because
   the rate it must be multiplied by is corner-dependent, separately measured,
   and — under DR-0010 — potentially about to change.

## Reproducing everything above

```sh
# The two rollups, from committed records only (no ngspice, no PDK for the
# first; the second degrades to measured-silicon-only without a PDK):
python3 sim/tools/time_to_first_valid.py
python3 sim/tools/power_rollup.py

# Their self-checks, both wired into CI:
python3 sim/tools/time_to_first_valid.py --check
python3 sim/tools/power_rollup.py --check

# The digital estimate on its own, at every characterised corner:
python3 design/digital_power_estimate.py --all-corners

# The three testbenches (needs ngspice + the gf180mcu PDK):
python3 sim/run_corners.py ro-array-core-startup
python3 sim/run_corners.py sampler-dff-active-current
python3 sim/run_corners.py sampler-core-idle-leakage
```

[DR-0002]: ../spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md
[DR-0003]: ../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0004]: ../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0008]: ../spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md
[DR-0010]: ../spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0011]: ../spec/decision-records/DR-0011-metastability-hybrid-tap-claims-and-scope.md
[DR-0012]: ../spec/decision-records/DR-0012-sampler-fixed-external-clock.md
[DR-0016]: ../spec/decision-records/DR-0016-per-ring-liveness-monitor.md
[DR-0017]: ../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
