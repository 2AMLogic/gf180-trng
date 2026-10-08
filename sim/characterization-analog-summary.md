# Analog partition: characterization summary, per ratified spec row

Status: aggregation for issue [#313]. This is the analog partition's one
aggregated characterization artifact for T1 item 8 of the klayout-tools
design-evidence ladder. It is the analog counterpart of
[`characterization-digital-sta-area-power.md`](characterization-digital-sta-area-power.md).
It is organized by the rows of the ratified target specification
([`README.md`](../README.md) §Target specification, ratified 2026-07-31), not
by the fourteen per-topic documents it draws on.

**This document is an ordinary summary, not evidence.** It runs no new
simulation and mints no record. Every number below names the `sim/records/`
record (or record family) it rests on and the `sim/tools/` derivation that
reads it. Where a tool exists, the number is that tool's printed output
rather than a fresh calculation. Three commands reproduce every row-level
figure here from committed records, with no PDK and no ngspice:

```sh
python3 sim/tools/power_rollup.py              # Power rows (whole block)
python3 sim/tools/power_rollup.py --no-digital # Power rows (analog terms only)
python3 sim/tools/time_to_first_valid.py       # Time-to-first-valid row
python3 sim/tools/worst_corner_entropy.py      # Entropy-source row, MC mismatch
```

`sim/tests/test_analog_characterization_summary.py` (part of `npm run test`)
re-runs those tools and fails if a figure quoted in §1 is no longer what the
tool prints. A row edited here without that check passing is a defect.

**Label (mandatory, [DR-0004]):** every number in this document comes from
simulation or from arithmetic on simulation. None of it is silicon
measurement, and none of it is an SP 800-90B entropy assessment.

**No spec row is edited, relaxed or evaluated anew here.** A miss below is a
miss already recorded elsewhere. Its decision record is cited, and nothing in
this document absorbs it.

## 0. Scope

### 0.1 Partition boundary

The analog partition is the one `signoff/block-manifest.json` declares in
`partition_boundary.analog`: regions `ring1` (cell `ro_ring11`), `ring2`
(`ro_ring11_ring2`) and `combiner_sampler` (which contains both [DR-0018]
`ro_buf` instances). Its supplies are `vddr1`, `vddr2` and `vdd`, which are
analog-side star branches, and `vsubs`. It shares one net, `vss`, with the
digital region. Its boundary pins are `clk`, `rst_n`, `raw_bit`,
`raw_valid`, `ring_bit1` and `ring_bit2`.

[DR-0009] places the transistor/behavioural boundary at the raw tap. The
conditioner, health tests, interface, FIFOs and the power-delivery cells are
in the **digital** partition. Their characterization is
[`characterization-digital-sta-area-power.md`](characterization-digital-sta-area-power.md).
Where a ratified row is a whole-block row (Power, Area), this document gives
the analog terms and quotes the whole-block total, so the analog share is
never presented as the row's verdict.

### 0.2 Corner coverage

| Evidence family | Points | Grid |
|---|---|---|
| RO array steady state (`ro-array-core-pvt-q`, `-power`), start-up (`ro-array-core-startup`) | 27 | {`tt`, `ff`, `ss`} × {−40, 27, 125} °C × {2.97, 3.30, 3.63} V. `fs`/`sf` are **not covered** for the array ([DR-0006]). |
| Sampler active current (`sampler-dff-active-current`), whole-block idle leakage (`sampler-core-idle-leakage`) | 45 | All five process corners × the same 3 × 3 temperature/supply grid |
| Monte Carlo mismatch (`ro-array-core-mc-freq`, `sampler-dff-mc-offset`) | 2 PVT points | `tt`/27 °C/3.30 V and `ss`/125 °C/3.63 V. 8 seeds per array record, 30 per sampler-offset record. |
| Post-layout extracted (`level: extracted`, [DR-0024]) | Binding corners only | Device-level (#17), routing-level (#217), full-chip inter-region delta (#232). See §2.1. |
| Coupling, liveness-tap and bit-bias studies (#51, #75, #76, #86, #87) | 1–2 points | Mostly `tt`/27 °C/3.30 V. See §2. |

The ratified operating envelope is −40 … +125 °C and 2.97–3.63 V. Every
array-derived claim below holds over the covered `tt`/`ff`/`ss` grid and
only over that grid.

### 0.3 Evidence classes used in §1

- **MEASURED**: transistor-level ngspice simulation of the schematic-derived
  netlist (`level: transistor`).
- **MEASURED-extracted**: the same, run on a `klt extract`-derived netlist
  (`level: extracted`, [DR-0024]).
- **DERIVED**: arithmetic on MEASURED records by a named `sim/tools/`
  script.
- **TARGET ARITHMETIC**: arithmetic on a ratified *target*. It is not a
  measurement and cannot become one until its inputs are measured.
- **ESTIMATE**: an inventory estimate with a stated method.
- **UNMEASURED**: no supportable figure exists, and the reason is given.

## 1. Per-row summary

| Ratified row (target) | Analog-partition result | Corner / scope | Evidence (records; tool) | Class | Reading and claim limit |
|---|---|---|---|---|---|
| **Entropy source**: `Q_array ≥ 1.5 × 4.0×10⁻³ = 6.0×10⁻³` at the entropy-binding corner ([DR-0007] §2) | Minimum-`Q` corner is **`ss`/125 °C/3.63 V** at every jitter-energy constant checked ([DR-0015]). The sizing law holds up to `R_max` = **678.1 bps** (`a` = 1.79, plain cell), **4458 bps** (`a` = 11.768, starved cell, asymptotic) or **9412 bps** (`a` = 24.843, starved cell, lag-1). | 27-point covered grid, pre-layout | `2026-08-02-ro-array-core-pvt-q-54` (binding corner) and the `ro-array-core-pvt-q` family; `worst_corner_entropy.py` | DERIVED | **Not met at the ratified 1 Mbps.** `Q ∝ T_s`, so at 1 Mbps the inequality falls short by `10⁶ / R_max`: about 1475×, 224× and 106× at the three constants. The law holds only at rates near [DR-0010]'s and [DR-0011-rate]'s `Proposed`, unratified 500 bps and 2 kbps. Post-layout extraction shrinks the margin further (§2.1). |
| **Raw rate**: > 1 Mbps sustained at the raw tap, binding at `ss`/−10 %/+125 °C ([DR-0003]) | The sample clock is a fixed external clock ([DR-0012]), so one raw bit per 1 µs period is a property of the clock. At the binding corner `ss`/125 °C/2.97 V, ring 1's period is **12.3 ns** pre-layout and **25.619 ns** with the full-chip inter-region delta. | Rate-binding corner; pre-layout and full-chip extracted | `time_to_first_valid.py` (T0 column); `2026-09-12-ro-array-core-startup-extracted-fullchip-01` | MEASURED / MEASURED-extracted | The ring is not what limits throughput: its period is far inside the sample period. **That does not make the row met.** The array supports the [DR-0007] sizing law only at rates 106× to 1475× below 1 Mbps, depending on the jitter-energy constant (row above), and no transistor-level bitstream at 1 Mbps exists. `signoff/README.md` counts this row as missed under item 5. A sustained-rate measurement as [DR-0003] §2 defines it (`N_bits / t_sim` over a full run) has not been made at transistor level. |
| **Raw min-entropy per bit**: placeholder, H₀ = 0.5 design target | **UNMEASURED.** The only transistor-level raw bits are 10 per corner at `T_s` = 10 ns, and they are bit-identical across all seeds. At those records' 10 ns sample interval, `Q_array` is four to five orders of magnitude below the sizing requirement, and at the ratified 1 µs period it is still short (Entropy-source row above). | `tt`/27 °C/3.30 V and `ss`/−40 °C/3.63 V (the corners [DR-0012] predicted before [DR-0015] moved the binding corner) | `2026-08-01-sampler-array-digitize-01`, `-02`; `raw_min_entropy_estimate.py`; [`characterization-raw-min-entropy-and-battery.md`](characterization-raw-min-entropy-and-battery.md) §1 | UNMEASURED | The MCV estimator's output on those ten bits (0.74 and 0.51 bit) is **not** a design estimate, and that document says so. Re-running at [DR-0015]'s `ss`/125 °C/3.63 V is still owed and is expected to hit the same ceiling. A supportable figure needs measured silicon ([DR-0004] Tier 3). |
| **Quality**: designed-for-SP 800-90B, plus a simulation-derived min-entropy estimate ([DR-0004]) | Tier 1 (structural: raw access, RCT/APT, source model) is a design property. **Tier 2 is not delivered**, for the reason in the row above. | n/a | [`characterization-raw-min-entropy-and-battery.md`](characterization-raw-min-entropy-and-battery.md) §3 | UNMEASURED | No 90B or AIS-31 conformance is claimed pre-silicon. The SP 800-22-style battery (`2026-08-08-conditioned-stream-battery-01`, 4 of 4 pass) uses a **declared-synthetic** source and is evidence about the conditioner, never about the analog source ([DR-0009] rule 4). |
| **Conditioning**: CRC-32, K = 8 ([DR-0008]) | Not an analog row. | n/a | Digital partition | n/a | This document makes no claim. |
| **Delivered rate**: `R_cond = R_raw / K` > 125 kbps ([DR-0003] §6, [DR-0008] §3) | 1 Mbps / 8 = 125 kbps | n/a | README row text | TARGET ARITHMETIC | Inherits the raw-rate row's status exactly. It is not a measurement. |
| **Health tests**: RCT/APT at α = 2⁻⁴⁰, cutoffs from H ([DR-0002]) | The logic is digital. The analog input to it is raw-bit **bias**. Under a stated bounding model, the worst modelled mismatch bias (systematic + 3 sd at `ss`/−40 °C/3.63 V, `p_major` = 0.5078) leaves the RCT false-alarm probability at 2.842e-24 and the APT at 1.395e-86, both below α. | MC at `tt`/27 °C/3.30 V and `ss`/125 °C/3.63 V. The `ss`/−40 °C/3.63 V row is an **extrapolation** of the nominal offset. | `2026-08-17-sampler-dff-mc-offset-02`, `-03`; `worst_corner_entropy.py` §"Does the measured mismatch bias fit" | DERIVED | This is a bias-only ceiling, not a min-entropy figure. The cutoffs are frozen at the *assumed* H₀ = 0.5, and the APT degeneracy floor (no valid cutoff at H ≤ 0.03) is [DR-0002]'s and is unchanged. |
| **Time-to-first-valid**: ≥ ~1.28 ms floor at 1 Mbps ([DR-0002], [DR-0008] §7) | **1.281 ms**, binding at `ss`/125 °C/2.97 V. The analog term (oscillator start-up) is **12.41 ns**, 0.001 % of the total, and all 27 corners converged. | 27-point grid, pre-layout. Full-chip start-up at the binding corner is +13.4 % on the first edge. | `2026-08-03-ro-array-core-startup-25` and the `ro-array-core-startup` family; `2026-09-12-ro-array-core-startup-extracted-fullchip-01`; `time_to_first_valid.py` | MEASURED + behavioural sample counts | **Met**, and the floor is confirmed as a floor. 1281 of the samples are fixed behavioural counts from the RTL parameters, so the row's real sensitivity is the sample **rate**: at the `Proposed` 500 bps or 2 kbps the same count takes 2.562 s or 641 ms. The row says nothing about whether the early bits are good. |
| **Power, active**: < 500 µW at `ff`/+10 % (whole block) | Analog terms at `ff`/−40 °C/3.63 V: entropy source **393.2 µW** and sampler **16.88 µW**, giving **410 µW = 82.0 %** of the row. The whole block is **758.2 µW = 151.6 %**, because the digital term is 348.2 µW, MEASURED-at-gate-level at `ff_125C_3v60`/`rc-max`. | 27 array × 45 sampler corners, pre-layout. Full-chip extraction adds +1.45 % to the rings' own term. | `2026-08-02-ro-array-core-pvt-q-39`, `2026-08-02-sampler-dff-active-current-12`; `2026-09-12-ro-array-core-power-extracted-fullchip-01` (and `-control-01`); `power_rollup.py` (`--no-digital` for the analog-only total) | MEASURED (analog); MEASURED-at-gate-level (digital, [DR-0021]) | **Whole-block row missed by 1.5×** ([DR-0023]). The analog share alone fits inside the row but leaves only 106.8 µW headroom for everything else. That 82 % is not a pass of a whole-block row. |
| **Power, idle**: < 1 µA at `ff`/+10 %/+125 °C (whole block) | Analog `sampler_core` is **32.77 nA** pre-layout and **127.04 nA** with full-chip extraction (the most complete settled figure). The whole block is **2.211 µA = 221 %** of the row, with digital leakage at 2.178 µA. | 45 corners, pre-layout; extracted at `ff`/125 °C/3.63 V only | `2026-08-02-sampler-core-idle-leakage-18`; `2026-09-12-sampler-core-idle-leakage-extracted-fullchip-01`; `power_rollup.py` | MEASURED / MEASURED-extracted | **Whole-block row missed by ~2.2×** ([DR-0017], `Proposed`). `power_rollup.py` sums the pre-layout analog term. Substituting the extracted 127.04 nA would give about 2.305 µA (DERIVED, this line). That widens the miss and does not change the verdict. |
| **Area**: < 0.05 mm² (whole block) | Analog regions plus their isolation channels come to **7 026.4 µm² = 14.05 %** of the row (`ring1` 546.14, `ring2` 546.14 and `combiner_sampler` 5 434.12 µm² guarded, plus 500 µm² of channels). | n/a | `layout/floorplan/reports/area.json` `rollup.subtotals.analog` (each region sized from its committed assembled GDS bounding box) | ESTIMATE (floorplan method over drawn geometry) | **Whole-block row missed** on the digital section's area ([DR-0019]). The analog share is not a pass of the row. |
| **Operating envelope**: −40 … +125 °C, 2.97–3.63 V | Covered at the 27 `tt`/`ff`/`ss` points for the array and at 45 points for the sampler and idle leakage | §0.2 | Families above | Coverage statement | `fs`/`sf` are uncovered for the array ([DR-0006]). Monte Carlo covers 2 points, and post-layout covers binding corners only. |
| **Interface**: raw always observable ([DR-0001], [DR-0013]) | The analog side exposes `raw_bit`/`raw_valid`/`ring_bit1`/`ring_bit2` at the boundary | n/a | `design/floorplan_netlist.py` `INTER_REGION_NETS`, `npm run check:floorplan-netlist` | Structural | This is not a performance row. Layout correctness is items 3 and 4. |

## 2. Cross-cutting characterization that limits the rows above

### 2.1 Post-layout extraction: scope, and what it moved

Source: [`characterization-post-layout-extracted.md`](characterization-post-layout-extracted.md).

- **Scope.** The extraction has three increments: device-level leaf cells
  (#17), routing-level (#217), and the full-chip delta on the `ro1`/`ro2`
  entropy trunks plus `raw_bit` load (#232, [DR-0025]). Twelve of the
  fourteen drawn inter-region nets are still not simulated. The
  digital-facing taps carry driver-side load only. Net-to-net coupling is
  reported but not composed. Every degradation is therefore a **floor**, not
  a ceiling (§0.1 and §8.7 of that document).
- **Sizing margin** at [DR-0010]'s `Proposed` 500 bps (`a` = 1.79):
  1.356× (pre-layout), 0.865× (leaf), 0.442× (routed), **0.374×** (full
  chip). At `a` = 11.77 it is **2.462×** full chip. No ratified row's
  verdict changes, because the ratified 1 Mbps already misses this target.
- **The extracted family is not in the rollups.** `power_rollup.py`,
  `time_to_first_valid.py` and `worst_corner_entropy.py` read the
  schematic-derived families. The extracted figures are quoted beside them
  in §1, not summed into them.
- **No analog `klt pex` envelope exists.** T1 item 7 analog therefore stays
  uncited. See `signoff/README.md`.

### 2.2 Monte Carlo device mismatch

Source: `worst_corner_entropy.py` and
[`characterization-worst-corner-and-mc-mismatch.md`](characterization-worst-corner-and-mc-mismatch.md).

- Ring frequency ratio `f_r2/f_r1`: mean 1.0691 (sd 0.0018) at the nominal
  corner and 1.0726 (sd 0.0013) at `ss`/125 °C/3.63 V
  (`2026-08-17-ro-array-core-mc-freq-01`, `-02`, 8 seeds each). The ratio
  sits 39–54 sd from an integer, so injection locking ([DR-0007] §1) is not
  approached.
- Sampler decision threshold (30 seeds each): a systematic offset of
  −265.2 mV (nominal) and −274.8 mV (`ss`/125 °C/3.63 V), present at every
  seed, plus a mismatch spread of 14.78 mV and 15.02 mV sd.
- The full-chip increment did not re-run Monte Carlo. Its argument for
  skipping it is stated in §8.2 of the post-layout document and is not a
  measurement.
- No `klt yield` report exists. T1 item 6 stays unmet; see
  `signoff/README.md`.

### 2.3 Coupling and clock-locked disturbance (single-corner studies)

| Study | Finding | Corner | Source |
|---|---|---|---|
| Ring-to-ring coupling through the XOR input (#51) | σ₁ is 28.6× higher with a switching neighbour; the mechanism is the combiner's input stage | `tt`/27 °C/3.30 V | [`characterization-array-ring-coupling.md`](characterization-array-ring-coupling.md) |
| Per-ring output buffer (#75, adopted by #78/[DR-0018]) | Removes 92.8 % of that coupling and returns 19.1 µW | Two corners | [`characterization-ring-buffer-mitigation.md`](characterization-ring-buffer-mitigation.md) |
| Liveness digitizer phase cost (#76) | 19.9× `clk`-locked residual on an isolated buffered ring, recorded as an upper bound | `tt`/27 °C/3.30 V | [`characterization-liveness-tap-phase-cost.md`](characterization-liveness-tap-phase-cost.md) |
| Shipped-array residual (#87) | 3.46× on ring 1 and 5.80× on ring 2. The residual is **not** removed. The `xsb`-on-`xo` path is below resolution. | `tt`/27 °C/3.30 V | [`characterization-shipped-array-tap-phase.md`](characterization-shipped-array-tap-phase.md) |
| Sampled-bit bias from that modulation (#86) | No bias or lag correlation outside measurement resolution, plus a +0.225 % static frequency shift | `tt`/27 °C/3.30 V | [`characterization-sampler-bit-bias.md`](characterization-sampler-bit-bias.md) |
| Shared `vss` trunk IR drop (#234) | 16.07 mV worst (`ring1`, active corner) and a 21.93 mV conservative bound, against a 33 mV materiality yardstick | Active and idle binding corners | `vss_trunk_ir_drop.py`; [`characterization-vss-trunk-ir-drop.md`](characterization-vss-trunk-ir-drop.md) |

The single-corner studies are characterization, not PVT claims. None of
them is extended to other corners here.

### 2.4 Device-level groundwork

[`characterization-ro-delay-cell-jitter.md`](characterization-ro-delay-cell-jitter.md)
(#4), [`characterization-starved-cell-jitter-energy.md`](characterization-starved-cell-jitter-energy.md)
(#46: the `a` constants used in §1) and
[`characterization-supply-current-and-leakage.md`](characterization-supply-current-and-leakage.md)
(#32) characterize the delay cell and the device leakage that the array
sizing rests on. They feed §1 through `jitter_energy_law.py`,
`starved_cell_jitter_energy.py` and `array_sizing.py`, all held by
`npm run check:spec`. [`characterization-startup-and-power-budget.md`](characterization-startup-and-power-budget.md)
(#14) is the narrative behind the time-to-first-valid and power rows.

## 3. What this document does and does not claim

- **Does:** gather, in one current place, every applicable ratified row's
  analog-partition evidence. Each entry names its corner or scope, its
  record, its method, its evidence class and its limit.
- **Does not:** claim any performance row passes. Of the rows above, one is
  met (time-to-first-valid). Raw rate, raw min-entropy, power and area are
  missed or unmeasured at the whole-block level, as `signoff/README.md`
  item 5 already records.
- **Does not:** stand in for silicon. Every figure is simulation, and the
  raw min-entropy row cannot be filled by simulation at all at the rates
  under consideration.
- **Does not:** make T1 items 5, 6 or 7 gradeable for the analog partition.
  Those items need `klt sim`, `klt yield` and `klt pex` envelopes
  respectively, and none exists (klayout-tools#2533, #2531).
- `sim/` records are append-only. This document cites them and does not
  restate or correct any of them. Superseded figures (for example the
  pre-#78 unbuffered array, or the 136.80 nA routed idle reading) stay in
  their own documents as history.

[#313]: https://github.com/2AMLogic/gf180-trng/issues/313
[DR-0001]: ../spec/decision-records/DR-0001-raw-and-conditioned-output-paths.md
[DR-0002]: ../spec/decision-records/DR-0002-health-test-parameters-and-failure-behavior.md
[DR-0003]: ../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0004]: ../spec/decision-records/DR-0004-sp-800-90b-path-pre-silicon.md
[DR-0006]: ../spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md
[DR-0007]: ../spec/decision-records/DR-0007-multi-ro-xor-combined-entropy-source.md
[DR-0008]: ../spec/decision-records/DR-0008-crc32-lfsr-non-vetted-conditioner.md
[DR-0009]: ../spec/decision-records/DR-0009-behavioral-vs-transistor-verification-split.md
[DR-0010]: ../spec/decision-records/DR-0010-raw-rate-moves-to-the-measured-jitter-energy-limit.md
[DR-0011-rate]: ../spec/decision-records/DR-0011-raw-rate-at-the-measured-starved-cell-jitter-energy.md
[DR-0012]: ../spec/decision-records/DR-0012-sampler-fixed-external-clock.md
[DR-0013]: ../spec/decision-records/DR-0013-interface-register-map-and-streaming-semantics.md
[DR-0015]: ../spec/decision-records/DR-0015-entropy-binding-corner-moves-to-the-hot-slow-corner.md
[DR-0017]: ../spec/decision-records/DR-0017-idle-current-row-versus-ungated-standard-cell-leakage.md
[DR-0018]: ../spec/decision-records/DR-0018-adopt-per-ring-output-buffer.md
[DR-0019]: ../spec/decision-records/DR-0019-area-row-versus-output-fifo-dominated-digital-section.md
[DR-0021]: ../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
[DR-0023]: ../spec/decision-records/DR-0023-power-rollup-digital-term-becomes-measured-gate-level-power.md
[DR-0024]: ../spec/decision-records/DR-0024-extracted-netlist-record-level.md
[DR-0025]: ../spec/decision-records/DR-0025-full-chip-pex-scope.md
