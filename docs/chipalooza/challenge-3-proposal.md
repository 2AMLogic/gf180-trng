# Chipalooza Challenge #3 proposal — GF180 TRNG entropy source

**Program:** Open Circuit Design Chipalooza Challenge #3 (GF180MCU / Wafer.Space).
**Repository:** [`2AMLogic/gf180-trng`](https://github.com/2AMLogic/gf180-trng) — public, Apache-2.0.
**Status of this repository:** simulation-complete for most of the design; the
entropy source and sampler have a first DRC/LVS-clean layout, the digital
section has a separate placed-and-routed GDS (LVS not yet clean), and the two
have not been composed into one whole-block layout. Nothing has been
fabricated and nothing has been measured on silicon. That is the point of
this submission: this block is small, simulation-complete, and its central
claim — that its bits are actually random — is exactly the kind of claim a
shuttle seat and a bench exist to check.

This document is written to be ready to send verbatim as the Challenge #3
submission for this block. It contains no personal or institutional
identifiers; the designer/CV and test-equipment attachments the program asks
for separately are supplied outside this repository.

---

## 1. Type of IP block

A digital true-random-number-generator **entropy source** (not a DRBG): a
two-ring, XOR-combined, free-running ring-oscillator array feeding a
fixed-external-clock sampler, continuous on-die health tests structured to
SP 800-90B's pre-silicon obligations (RCT, APT, start-up test, per-ring
liveness), and a non-vetted CRC-32 conditioner — raw and conditioned output
both available, raw access never gated.

---

## 2. I/O list

The repository's full register-bus interface
([`design/interface/REGMAP.md`](../../design/interface/REGMAP.md)) has 22
ports (11 of which already leave the die at `trng_top`) built around three
32-bit buses (`reg_wdata`, `reg_rdata`, `str_data`). That interface is sized
for a SoC integration, not a shared multi-tenant test-chip slot, so this
proposal defines a **separate, reduced test-chip pinout** — a thin wrapper
around the existing `trng_top`/`trng_interface`, not a change to either.
Nothing below requires modifying `design/interface/trng_interface.v`'s
register map or its normative behaviour; it requires one small new piece of
wrapper RTL (a 1-bit serializer for the conditioned output, noted as an open
item in §2.7).

### 2.1 Budget summary

| Resource | Challenge #3 budget | Requested | Headroom |
|---|---|---|---|
| Digital control inputs | ≤ 24 | **12** | 12 spare |
| Digital test outputs | ≤ 12 | **12** | 0 spare — at the ceiling |
| Shared (multiplexed) analog lines | ≤ 4 | **1** | 3 declined |
| Bandgap-referenced current sources | ≤ 2 | **0** | 2 declined |
| Bandgap-referenced bias voltage | offered | **declined** | not needed |
| Dedicated pads | ≤ 4 | **4** | 0 spare — at the ceiling |

### 2.2 Digital control inputs (12 of 24)

| Pin | Width | Replaces / maps to | Purpose |
|---|---|---|---|
| `clk` | 1 | `trng_top.clk` | Sampler clock — fixed external per [DR-0012](../../spec/decision-records/DR-0012-sampler-fixed-external-clock.md); the whole block, including the register bus, is synchronous to it. |
| `rst_n` | 1 | `trng_top.rst_n` | Asynchronous power-on reset, active low. |
| `en` | 1 | `CTRL.EN` | Direct control pin. Reset default is logic-1 behaviour (the block starts acquiring at power-on with no write, per `REGMAP.md`), so this pin is expected held high in normal bench operation and pulsed low only to idle/flush the block on purpose. |
| `out_mode` | 1 | `CTRL.OUT_MODE` | 0 = conditioned, 1 = raw, on the streaming/serial test outputs (§2.3). Changing it flushes both paths, exactly as `CTRL.OUT_MODE` does today. |
| `soft_reset` | 1 (pulse) | `CTRL.SOFT_RESET` | Flush both paths and restart the start-up health test. Does not clear latched `HT_FAIL_*` alarms (same restriction as today). |
| `ht_clr_rct` | 1 (pulse) | `STATUS.HT_FAIL_RCT` (W1C) | Clears the RCT latch. |
| `ht_clr_apt` | 1 (pulse) | `STATUS.HT_FAIL_APT` (W1C) | Clears the APT latch. |
| `ht_clr_ring` | 1 (pulse) | `STATUS.HT_FAIL_RING` (W1C) | Clears the per-ring liveness latch ([DR-0016](../../spec/decision-records/DR-0016-per-ring-liveness-monitor.md)). |
| `str_ready` | 1 | `str_ready` (unchanged) | Streaming-port backpressure. Held low on purpose exercises the FIFO-overflow path (`OVF_DATA`/`OVF_RAW`, dropped as a direct test output in §2.7 but still exercisable this way). |
| `ring_sel` | 1 | new | Selects ring 1 or ring 2 onto the shared analog monitor line (§2.4). |
| `force_ring1_stop` | 1 | new | Bench fault-injection hook: forces ring 1's enable stage (`ro_nand2`'s `en` input) low, so the per-ring liveness monitor's response can be exercised on real silicon the same way [`sim/tb/ring-liveness-fault-injection/`](../../sim/tb/ring-liveness-fault-injection/) exercises it in simulation. |
| `force_ring2_stop` | 1 | new | Same, ring 2. |

12 of 24 used, leaving 12 spare for whatever the Oct 5 schematic review adds
(a calibration trim, an extra fault-injection hook, or headroom the reviewers
request).

### 2.3 Digital test outputs (12 of 12 — at the ceiling)

| Pin | Width | Replaces / maps to | Purpose |
|---|---|---|---|
| `raw_bit_out` | 1 | `sampler_core.raw_bit` (the DR-0001 raw tap) | The entropy-evidence pin (§5.2): one raw, undecimated bit per sample-clock edge, straight off the raw tap. |
| `raw_valid_out` | 1 | `raw_valid` | Strobes `raw_bit_out`. |
| `cond_bit_out` | 1 | `DATA`/`str_data`, serialized | Conditioned output, one bit per cycle instead of one 32-bit word per FIFO pop. **Not yet implemented** — see §2.7. |
| `cond_valid_out` | 1 | `str_valid` (conditioned mode) | Strobes `cond_bit_out`. |
| `ht_alarm` | 1 | `ht_alarm` (unchanged) | Already an external `trng_top` pin today. |
| `ht_fail_rct` | 1 | `STATUS.HT_FAIL_RCT` | RCT latch, direct read instead of a register read. |
| `ht_fail_apt` | 1 | `STATUS.HT_FAIL_APT` | APT latch. |
| `ht_fail_ring` | 1 | `STATUS.HT_FAIL_RING` | Per-ring liveness latch. |
| `startup` | 1 | `STATUS.STARTUP` | Start-up health test in progress. |
| `cond_ready` | 1 | `STATUS.COND_READY` | Conditioned path ungated. |
| `data_avail` | 1 | `STATUS.DATA_AVAIL` | Conditioned FIFO non-empty. |
| `raw_avail` | 1 | `STATUS.RAW_AVAIL` | Raw FIFO non-empty. |

### 2.4 Shared analog lines (1 of 4 used)

| Pin | Purpose |
|---|---|
| `ro_mon` | Buffered analog monitor of whichever ring `ring_sel` (§2.2) selects — a direct bench measurement path for the ring frequencies in §4 Row A (81–249 MHz across the covered 3.3 V-family grid) and for jitter, without going through the digital sampler. **Needs a low-resistance, high-bandwidth pad, not an ordinary ESD-clamped digital I/O pad** — the signal of interest runs into the hundreds of MHz, well above what a standard digital pad's protection network is characterized to pass cleanly. |

The remaining 3 of 4 shared analog slots are declined — this block has no
other node worth spending shared-analog budget on.

### 2.5 Dedicated pads (4 of 4 — at the ceiling)

| Pad | Purpose |
|---|---|
| `VDDA` | Analog supply — entropy source (`ro_array_core`) + sampler (`sampler_core`). **Requested sourced from the Challenge's 3.3 V digital rail, not its 5.0 V analog rail — see the rail-routing note below.** |
| `VSSA` | Analog ground. |
| `VDDD` | Digital supply (3.3 V) — conditioner, health tests, interface. |
| `VSSD` | Digital ground. |

**Dropped:** `ro_array_core.spice`'s two independent per-ring supply pins
(`vddr1`/`vddr2` — used in simulation specifically so ring 1's and ring 2's
supply current could be measured separately, see
[`design/README.md`](../../design/README.md)) are tied together onto the
single `VDDA` pad above to fit the 4-pad budget. Bench measurement will only
see the combined analog supply current, not a per-ring split — which is
exactly what every power row in §4 already reports, so nothing in this
proposal's own spec table is weakened by that choice.

### 2.6 Bandgap-referenced bias voltage / current sources: declined

This design needs neither. The ring array's frequency-setting element is a
fixed-geometry series "starve" device (`Mph`/`Mnt` in
[`design/xschem/ro_stage.sch`](../../design/xschem/ro_stage.sch) and
[`ro_nand2.sch`](../../design/xschem/ro_nand2.sch), channel length `lstv` =
2 µm, sized once in the schematic) — not a voltage-controlled current mirror
referenced to an external bandgap. No net in `design/*.spice` or
`design/xschem/*.sch` is a bias or bandgap input. We ask that the shared
bandgap/current-source budget be allocated to another Challenge #3 entry.

### 2.7 Open items for the Oct 5 schematic review

- **`cond_bit_out`'s serializer does not exist yet.** `design/interface/`
  today only ever presents the conditioned stream as 32-bit words
  (`DATA`/`str_data`); a 1-bit-per-cycle serializer wrapper is new, small
  RTL that has to be written and verified against
  `sim/tb/interface-regfile/` before tape-out.
- **`OVF_DATA`/`OVF_RAW` are not direct test outputs** at the 12-pin ceiling;
  overflow behaviour is still exercisable via `str_ready` (§2.2) but only
  observed indirectly (a gap in `raw_avail`/`data_avail` behaviour), not read
  back as its own status bit.
- **The `VDDA` rail-routing question (§2.5) is unresolved** and gates several
  rows of §4 — see the rail-routing note there.

---

## 3. Functional description

The block is an **entropy source only** — it defines no DRBG, no seeding, and
no reseeding semantics; an integrator supplies its own DRBG downstream.

**Entropy source.** Two independent, free-running ring oscillators
(`ro_ring11`, 11 series-starved stages each, skewed starve-device widths so
the two rings run at different, uncorrelated frequencies), each isolated from
the rest of the circuit by its own minimum-width, unstarved output buffer
(`ro_buf`, adopted in [DR-0018](../../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md)),
then XOR-combined into a single node (`xo`). The entropy mechanism is
accumulated oscillator phase jitter from thermal/flicker device noise, not a
metastability tap — the metastability-hybrid alternative was evaluated in
[DR-0007](../../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md)
and rejected as a free-standing source (kept only as a possible future
secondary tap, not instantiated in the shipped array).

**Sampler.** A single flip-flop pair (`sampler_dff`) digitizes the combined
`xo` node on a **fixed external clock** — [DR-0012](../../spec/decision-records/DR-0012-sampler-fixed-external-clock.md)
deliberately decouples the raw sample rate from the ring's own free-running
frequency, so the sample rate is a system/bench choice, not a property of
the analog block.

**Health tests.** Continuous Repetition Count Test (RCT) and Adaptive
Proportion Test (APT) on the raw, undecimated tap, plus a start-up test built
from the same two tests, plus an independent per-ring liveness monitor
watching each ring's own digitized sample (so one dead ring out of the
shipped N = 2 is not invisible to the combined-tap RCT/APT, per
[DR-0016](../../spec/decision-records/DR-0016-per-ring-liveness-monitor.md)).
All three failure sources feed one latch-and-gate mechanism
([DR-0002](../../spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md)):
a failure latches a flag, asserts `ht_alarm`, and gates the *conditioned*
path only — the raw path is never gated, so raw access survives an alarm.

**Conditioner.** A non-vetted 32-bit Galois CRC-32 LFSR (polynomial
`0xEDB88320`), state cleared every 256 raw samples (K = 8), producing one
32-bit conditioned word per block
([DR-0008](../../spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md)).
A 90B-*vetted* conditioner (e.g. a serialized AES-128) was costed and
rejected on area — 88–124 % of the whole block's area budget by itself.

**Interface.** A word-addressed register file (`CTRL`, `STATUS`, `DATA`,
`RAW_DATA`) plus a 32-bit valid/ready streaming port with mode selection
(raw vs. conditioned), described in full in
[`design/interface/REGMAP.md`](../../design/interface/REGMAP.md). §2 above
defines a reduced pin-level wrapper around this interface for the Challenge
#3 test-chip slot specifically; the full register interface is unchanged and
remains available to any other integration of this block.

---

## 4. Target specification

**Every row below is re-derived directly from this repository's `sim/`
results, at the widest supply corner this repository has ever simulated:
3.3 V nominal ± 10 % (2.97–3.63 V). No record anywhere under `sim/records/`
exercises any device above 3.63 V.** That is the load-bearing fact behind
most of the "unmet at challenge rails" verdicts below — see the rail-routing
note that follows the table.

| # | Parameter | Min | Typ | Max | Target / absolute limit | Binding corner | `sim/` citation | Verdict at 3.3 V | Verdict at 5.0 V (challenge analog rail) |
|---|---|---|---|---|---|---|---|---|---|
| A | Per-ring oscillation frequency, `f_osc` (ring 1 of the shipped, buffered 2-ring array) | 81.3 MHz | 149.7 MHz | 249.0 MHz | not separately targeted (feeds row B) | min: `ss`/+125 °C/2.97 V; typ: `tt`/27 °C/3.30 V; max: `ff`/−40 °C/3.63 V | `sim/records/2026-08-02-ro-array-core-pvt-q-{52,32,39}.md` (post-[DR-0018] buffered netlist); `sim/characterization-ro-delay-cell-jitter.md` | Measured, full grid | **Unmet/TBD — no record above 3.63 V** |
| B | Raw bit rate, sustained at the raw tap | — | — | — | Ratified: **> 1 Mbps** ([DR-0003](../../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md)). Array-sizing-law-derived (Proposed, unratified): **598.8 bps** ([DR-0015](../../spec/decision-records/DR-0015-entropy-binding-corner-moves-to-the-hot-slow-corner.md), generic constant) to **~2.05 kbps** ([DR-0011-rate](../../spec/decision-records/DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md), shipped-cell-specific constant) | `ss`/+125 °C/3.63 V (entropy-binding corner, [DR-0015]) | `sim/characterization-starved-cell-jitter-energy.md`; DR-0010, DR-0011-rate, DR-0015 | **Unmet** — the ratified 1 Mbps target is 490–1670× above what the array's own measured jitter-energy constant supports while also clearing the `H0 = 0.5` sizing margin | Same gap; unaffected by which rail (rate is set by the sizing law and the external sample clock, not by supply voltage directly) |
| C | Raw min-entropy per bit | — | — | — | Design target: `H0 = 0.5` bit/sample ([DR-0007]) | `tt`/27 °C/3.30 V and `ss`/−40 °C/3.63 V (only two corners a real bitstream exists for) | `sim/characterization-raw-min-entropy-and-battery.md`; `sim/records/2026-08-01-sampler-array-digitize-{01,02}.md` | **Unmet/TBD — not measurable pre-silicon.** MCV point estimates (`H_hat` = 0.74 and 0.51 bit at N = 10, SE ≈ 0.3–0.4 bit) exist but are explicitly not reportable as a design estimate; simulating enough raw bits at the entropy-supporting rate costs an estimated 4–8 years of ngspice time | Same — this row has no rate at which transistor-level simulation is affordable, independent of rail |
| D | Active supply current / power, whole block (2-ring array + XOR + sampler + digital section) | 794.7 µW | 905.0 µW | 1.122 mW | < 500 µW | min: `ss`/125 °C/2.97 V; typ: `tt`/27 °C/3.30 V; max: `ff`/−40 °C/3.63 V | `sim/tools/power_rollup.py` (regenerates from `sim/records/*-ro-array-core-pvt-q-*`, `*-sampler-dff-active-current-*`, and the gate-level digital sweep, [DR-0021](../../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)); `sim/characterization-startup-and-power-budget.md` | **Missed, 2.2×** at its own worst corner — 712.4 µW of the 1.122 mW is the synthesized digital section alone (measured at gate level, [DR-0023]) | **Unmet/TBD — no data above 3.63 V, and a fixed-topology switching term rises worse than linearly with supply, so 5.0 V would widen this miss, not narrow it** |
| E | Idle supply current, whole block | ≈ 0.11 µA | ≈ 0.16 µA | 3.979 µA | < 1 µA | min: `ss`/−40 °C/3.00 V (digital); typ: `tt`/25 °C/3.30 V; max: `ff`/+125 °C/3.63 V | `sim/characterization-digital-sta-area-power.md` §4.1 (digital leakage-current column) combined with the analog `sampler_core` idle term in `sim/characterization-startup-and-power-budget.md` / `sim/tools/power_rollup.py` | **Missed, ~4.0×** at its own worst corner — digital standard-cell leakage is 99+% of the miss ([DR-0017](../../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md)) | **Unmet/TBD — no data above 3.63 V** |
| F | Time-to-first-valid | — | — | 1.281 ms | ≥ ~1.28 ms (arithmetic floor: 1024 start-up samples + 256-sample conditioner latency) | `ss`/+125 °C/2.97 V, but the spread across the whole grid is 9 ns on 1.281 ms — dominated by the fixed sample count, not PVT | `sim/characterization-startup-and-power-budget.md` (issue #14); regenerable via `sim/tools/time_to_first_valid.py` | **Met** | **Unmet/TBD — no data above 3.63 V**, though this row is expected to be rail-insensitive since it is dominated by a fixed sample count and the external clock, not ring speed |
| G | Digital section max clean sample-clock frequency (`Fmax`) | 35.63 MHz | 70.69–75.54 MHz | 130.22 MHz | supplementary — no ratified row; informative headroom figure | min: `ss_125C_3v00`/`max` parasitics; typ: `tt_025C_3v30`; max: `ff_n40C_3v60`/`min` | `sim/characterization-digital-sta-area-power.md` §2 (issue #145) | **Met** — every candidate raw rate in row B is 3–5 orders of magnitude below this floor | **Unmet/TBD — the standard-cell library (`gf180mcu_fd_sc_mcu9t5v0`) is only characterized here at its own `3v00/3v30/3v60` corners** |
| H | Health-test cutoffs (RCT / APT), at assumed `H = 0.5`, α = 2⁻⁴⁰, `W` = 1024 | — | `C_RCT` = 81, `C_APT` = 824 | — | formula-derived, not independently measured | n/a (parameter, not a PVT-swept quantity) | [DR-0002](../../spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md); `design/health_test/rct_apt.py` | **Provisional** — only as good as the assumed `H`, which row C shows is unmeasured | Same caveat; rail-independent as a formula, but its real-world validity inherits row C's status |
| I | Area (whole block) | — | — | 0.1350 mm² (estimate, not a layout measurement) | < 0.05 mm² | n/a (not PVT-dependent) | `layout/floorplan/reports/area.json`; `layout/floorplan/README.md` | **Missed, 2.7×** as an inventory estimate — no full whole-block layout exists yet (composition gap, #106) | Rail-independent (a pad-frame choice for a 5.0 V rail could add second-order area not modeled here) |

### Independent verification of this table

Every row above cites a `sim/` record or a script that reads one — this
subsection is how a reviewer regenerates that evidence rather than taking the
citation on faith. The repository README's
[**"Independent verification (Chipalooza)"**](../../README.md#independent-verification-chipalooza)
section is the full answer: prerequisites (ngspice, the gf180mcu PDK — no
KLayout/OpenROAD needed for the rows below), three commands (`make check`,
`make smoke`, `make characterize`), where results land, and the row-by-row
regeneration mapping reproduced here for convenience:

| Row | Regenerated by |
|---|---|
| A | `make characterize` → `sim/records/<date>-ro-array-core-pvt-q-*.md` |
| B | `python3 sim/tools/jitter_energy_law.py --check` / `starved_cell_jitter_energy.py --check` (not a PVT sweep) |
| C | `make characterize` → `sim/records/<date>-sampler-array-digitize-*.md` (functional demonstration only, per this row's own caveats above) |
| D | `make characterize` (analog term) + `python3 sim/tb/digital-sta-power/run_sta.py` (digital term, needs OpenROAD) |
| E | `make characterize` (analog term) + the same `run_sta.py` (digital term) |
| F | `make characterize` → `sim/records/<date>-ro-array-core-startup-*.md` |
| G | `python3 sim/tb/digital-sta-power/run_sta.py` (needs OpenROAD; not covered by `make characterize`) |
| H | `python3 -c "from design.health_test.rct_apt import c_rct, c_apt, H0; print(c_rct(H0), c_apt(H0))"` (closed-form, no PVT dependency; `rct_apt.py` is a library, not a CLI) |
| I | `python3 layout/floorplan/floorplan.py` (needs `klt` + PDK; not covered by `make characterize`) |

### Rail-routing note (the single largest gap in this table)

**Every device in this design — the ring stages, the XOR combiner, the
sampler flip-flops, and the whole synthesized digital section — is
instantiated from gf180mcu's 3.3 V-rated families** (`nfet_03v3`/`pfet_03v3`
throughout `design/*.spice`; the digital standard-cell library
`gf180mcu_fd_sc_mcu9t5v0` is timed here only at its own `3v00`/`3v30`/`3v60`
corners, per `design/synth.py` and
`sim/characterization-digital-sta-area-power.md`). `sim/harness/corners.py`
generates supply points at ±10 % of a 3.3 V nominal and nothing wider. No
record under `sim/records/` — 859 of them — exercises any device above
3.63 V. Running this design continuously at a 5.0 V analog rail would put
every device above the supply range this repository has ever simulated it
at, and above the range its 3.3 V-rated family is designed for — a real
engineering risk, not a documentation gap, and one this repository is not
in a position to wave away with an assumption.

**Request:** route `VDDA` (§2.5) from the Challenge's 3.3 V digital rail
rather than its 5.0 V analog rail. If the program instead requires every
seat to sit on the 5.0 V analog rail, the two options are, before the Oct 5
schematic review: (a) migrate the entropy source to gf180mcu's 5.0 V-rated
device family and re-run the sizing analysis ([DR-0007]) and the
characterization suite above from scratch, or (b) add a compact series
regulation element ahead of `VDDA` to bring the block's own local supply to
3.3 V while still occupying only the 5.0 V analog dedicated pads. Neither
option has any evidence in `sim/` today, and this proposal does not pretend
otherwise.

---

## 5. Test-plan outline

### 5.1 Bench setup

The packaged part (QFN) is measured on a daughterboard mated to the
Chipalooza/Wafer.Space test board. Minimum bench instrumentation: a
programmable supply for `VDDA`/`VDDD` (independently, per the rail-routing
note above), a function generator or FPGA-sourced `clk` (the sample clock is
external by design, [DR-0012]), a logic analyzer or FPGA capture fabric wide
enough for the 12 digital test outputs plus the 12 digital control inputs
(§2.2–2.3), and an oscilloscope on `ro_mon` (§2.4) — through a probe/pad path
rated for the frequencies in Row A, per the low-resistance-pad note in §2.4.
A thermal chamber or hot/cold plate is needed to reach any temperature point
beyond bench-ambient, since every row in §4 that has been simulated at all
was simulated across −40…+125 °C.

### 5.2 Per-row bring-up and closure plan

1. **Power-on / reset smoke test.** Assert `rst_n`, release, confirm `en`
   defaults active and `startup` (§2.3) asserts, then clears within the
   Row F window once `clk` has run 1024+256 cycles. Confirms Row F
   (time-to-first-valid) directly, and is the first go/no-go gate before
   anything else is meaningful.
2. **Ring frequency / `ro_mon` sweep (Row A).** Step `ring_sel` between the
   two rings, sweep `VDDA` and temperature across whatever range the bench
   and rail decision (§4 rail-routing note) allow, and compare `ro_mon`'s
   measured frequency against the `sim/records/2026-08-02-ro-array-core-pvt-q-*`
   table. This is the first real silicon-vs-simulation comparison this
   repository will ever have.
3. **Raw bit rate / raw min-entropy (Rows B, C).** Drive `clk` at a
   candidate sample rate, capture `raw_bit_out`/`raw_valid_out` over a long
   consecutive run (target ≥ 10⁶ samples per [DR-0004] Tier 2's sequencing,
   now finally affordable because it is real time on real silicon instead of
   ngspice transient time), and run the SP 800-90B non-IID entropy-source
   estimator suite plus the restart test (≈1000 independent power-on
   restarts) against it. **This is the step that closes Row C** — it cannot
   be closed by any further pre-tapeout simulation (§4 explains why), and it
   is the primary reason this block is worth a shuttle seat.
4. **Statistical battery on the conditioned stream.** Capture `cond_bit_out`
   over a comparable run length and run the SP 800-22 battery this
   repository already implements behaviorally
   (`sim/tools/statistical_battery.py`, four tests: monobit, block
   frequency, runs, longest run of ones), extended with whatever the bench
   toolchain supports beyond that. The behavioral run
   (`sim/records/2026-08-08-conditioned-stream-battery-01.md`, 4096
   conditioned bits at a synthetic `H0 = 0.5` source) passed all four tests
   at α = 0.01 — a pipeline sanity check, not entropy evidence; the bench run
   is what turns it into evidence.
5. **Health-test fault injection (Rows H).** Use `force_ring1_stop` /
   `force_ring2_stop` to kill one ring at a time and confirm `ht_fail_ring`
   asserts and gates `cond_ready` while `raw_bit_out` keeps producing bits —
   the same behavior `sim/tb/ring-liveness-fault-injection/` and
   `sim/tb/health-test-fault-injection/` already exercise behaviorally.
   Confirms the RCT/APT cutoff table (Row H) trips where the formula
   predicts, at whatever `H` the Step 3 measurement finds — closing the
   "provisional" caveat on Row H with a real number for the first time.
6. **Power (Rows D, E).** Measure `VDDA`+`VDDD` current in the active state
   and in the idle state (`en` = 0, all rings clamped) across whatever
   voltage/temperature range the bench supports, and compare directly against
   the `sim/tools/power_rollup.py` table in §4.

### 5.3 Pre-Oct-5 action items (closing what can be closed before schematic review)

- **Resolve the `VDDA` rail-routing question (§4)** — this gates the 5.0 V
  verdict on Rows A, D, E, F and G.
- **If 5.0 V is required**, either extend `sim/harness/corners.py` with a
  5.0 V supply point and re-run the existing testbenches (cheap, if the
  3.3 V-rated devices are deemed to tolerate it — a PDK-rating question this
  repository cannot answer by itself), or migrate to 5.0 V-rated devices and
  re-run the sizing/characterization suite from scratch (expensive).
- **Ratify a raw-rate value (Row B)** — pick between the two competing
  Proposed decision records ([DR-0011-rate], [DR-0015]) or supersede both,
  since the sample-clock frequency the test board drives is a schematic-time
  decision.
- **Write and verify the `cond_bit_out` serializer** (§2.7) — new RTL,
  needed before the pinout in §2.3 is real.
- **Rows C and H's "provisional"/"unmet" status is not closeable by
  simulation before Oct 5** — they are exactly what the test plan in §5.2
  exists to close, on the packaged part, after tape-out. That is disclosed
  here as a plan, not hidden as a gap.

---

## Program compliance notes

- **License.** This repository is [Apache-2.0](../../LICENSE), one of the
  challenge's named acceptable licenses, with all modifiable sources —
  schematics, netlists, RTL, testbenches, evidence records, layout — public
  in this same repository. No separate licensing action is needed for this
  submission.
- **Open-source EDA flow.** Schematics and simulation: xschem + ngspice
  (ngspice ≥ 46) against the gf180mcu open PDK, installable via
  [ciel](https://github.com/fossi-foundation/ciel) (`PDK_ROOT`/`PDK` or an
  equivalent env var, resolved by `sim/harness/pdk.py`'s search chain).
  Digital synthesis: `klt synthesize` (klayout-tools, wrapping Yosys + ABC)
  against `gf180mcu_fd_sc_mcu9t5v0`. Layout DRC/LVS: klayout-tools (`klt`).
  Everything above is IIC-OSIC-TOOLS/ciel-compatible and runs from this
  repository's own committed scripts (`sim/run_corners.py`,
  `design/netlist.py`, `design/synth.py`, `layout/verify.py`) with no
  proprietary tool anywhere in the loop.
- **Disclosure.** This repository is public. Nothing in this document
  discloses anything beyond what is already committed to it; no
  wording about the organization that maintains this repository, its
  business, or its other work appears here or belongs here.
