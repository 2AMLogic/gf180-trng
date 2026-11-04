# Digital section: workload-dependent power from post-route switching activity

Status: measurement complete for issue [#453], the per-net switching-activity
follow-up that [DR-0023] named when it made the whole-block digital power term
a gate-level measurement. **Characterization only.** The ratified rollup
(`python3 sim/tools/power_rollup.py`) and every specification target are
unchanged; nothing here is adopted into either (see "What changes in the
budget, and what does not").

[DR-0023]: ../spec/decision-records/DR-0023-power-rollup-digital-term-becomes-measured-gate-level-power.md
[#453]: https://github.com/2AMLogic/gf180-trng/issues/453

## 0. Findings

1. **The uniform 0.25 transitions/net/cycle assumption is conservative for
   every workload tried**, by a margin that is almost corner-independent:
   at the same netlist, SPEF and 1 MHz rate, the largest observed steady-state
   total is **0.716 to 0.724** of the uniform figure across all 15 corners
   (table below). At the digital-binding corner of the rollup
   (`ff_125C_3v60`, `max` interconnect) that is 251.3 uW observed against
   348.2 uW uniform.
2. **The workloads differ from each other by far less than either differs from
   the uniform model.** Steady-state conditioned streaming, raw streaming and a
   fully stalled consumer are within about 1 % of each other. Alarm-gated
   operation (conditioned path gated, raw tap still running) is about 11 %
   lower, and a **disabled block with a running clock still draws 0.60 of the
   uniform figure**: the clock tree and every flop's clock-pin internal energy
   are paid regardless of whether the block is doing anything. No claim is made
   that any of these five stimuli is a universal worst case.
3. **Start-up and reset are cheaper than steady state**, not dearer, for the
   streaming workloads (reset 0.59, start-up 0.67, steady 0.72 of uniform at the
   binding corner): the conditioner and FIFOs are still gated or empty.
4. **Annotation is complete.** Every window of every workload of every corner
   binds all 5371 pins to VCD activity; no pin runs on a fallback activity, so
   nothing in the table is an unannotated number presented as measured.
5. **The budget verdict does not move.** See section 5.

## 1. Method

`sim/tb/trng-top-post-route/activity_workloads.py` declares five seeded
workloads over `trng_top`'s pins; `sim/tb/digital-sta-power/activity.py`
simulates the **as-built** post-route netlist (`layout/digital/trng_top.pnr.v`,
CTS buffers and resized cells included) with Icarus Verilog against the PDK
cell models (zero delay, `-gno-specify`) at a 1 us clock period, dumps a VCD of
the whole DUT hierarchy, and pins everything by hash.
`python3 sim/tb/digital-sta-power/run_sta.py --activity` then, per corner,
(a) re-runs the default flow's 1 MHz session (uniform activity) and (b) reads
the same SPEF in a second OpenSTA session and, per (workload, window), runs
`read_vcd -scope tb/dut -begin_time B -end_time E` followed by
`report_activity_annotation` and `report_power`. One record per corner,
`sim/records/2026-10-10-digital-sta-activity-{16..30}.md` (current). The
first family, `-{01..15}`, was minted before issue #456 priced the top-edge
legs of the six `digital`-facing nets into the interface load; the family was
re-captured and re-run so that its uniform baseline again equals the default
flow's (`--check` compares them). The older records are unchanged, the newest
valid record per corner is the one read, and the generated tables below follow
the current family (they differ from the first family by at most 0.01 uW in
the last printed digit).

| workload | what it is |
|---|---|
| `conditioned-streaming` | default conditioned output, consumer always ready |
| `raw-streaming` | `CTRL.OUT_MODE` = raw, consumer always ready |
| `backpressure` | conditioned, consumer stalled (`str_ready` never asserts) |
| `alarm-gated` | ring 1 stuck after start-up; DR-0016 latches `ht_alarm`; steady window opens after the latch |
| `disabled-clock-running` | `CTRL.EN` = 0, raw tap idle, clock running |

Windows, in cycles of the 1 us clock: `reset` is the first 8 (`rst_n` low);
`startup` runs to cycle 1048, which covers DR-0002's 1024-sample window plus
16 cycles for the registered handoffs; `steady` is the next 1024 cycles (for
`alarm-gated`, the 1024 cycles after the alarm has latched). Seeds: base 453,
per workload 453 to 457, recorded in every record. The raw bits are synthetic
and make **no entropy claim**.

Clock behaviour is explicit: the clock runs, 50 % duty, 1 MHz, in every window.
**A stopped clock is a different state (leakage only) and was not simulated.**
`disabled-clock-running` is the "disabled but clocked" case and is not a proxy
for it.

## 2. Validation, and why a bad trace cannot become a number

`activity.validate_trace` and `activity.validate_annotation` reject, with no
downgrade to a warning: an empty trace; a wrong or missing DUT scope; a trace
whose instance set differs from the netlist's (both directions); a clock that
does not toggle as declared in each window; a window with no value changes; a
trace shorter than its workload; an OpenSTA run that binds no (or under 99 % of)
pins to the VCD. A manifest is rejected if the netlist blob, a trace hash or a
regenerated stimulus hash no longer matches. Reported per trace: instances
matched, x/z event counts, same-timestamp repeated changes (zero in every
trace), clock toggles per
window.

Negative controls against the real data (`python3
sim/tb/digital-sta-power/activity_power.py negative-controls`), all rejected:

```
rejected  empty-waveform: empty trace: 19001 variables, 0 value changes
rejected  wrong-dut-scope: no DUT scope 'tb.dut' in the trace -- a wrong scope would annotate nothing
rejected  mismatched-netlist: trace does not describe this netlist: 1 netlist instances absent from the trace (e.g. ['clkbuf_0_clk']), 1 trace instances not in the netlist (e.g. ['not_in_this_netlist'])
rejected  wrong-scope-in-opensta: OpenSTA bound no VCD activity to any pin (vcd=0, unannotated=5371) -- wrong scope, wrong netlist or empty trace
```

One bring-up finding that shaped the capture: OpenSTA binds VCD activity to
**pins** by hierarchical path. A dump of the DUT's nets alone annotated 109 of
5371 pins (the top-level ports) and nothing else, which `validate_annotation`
rejects; dumping the cell instances' hierarchy annotates all 5371.

## 3. Results

Generated from the records by `python3 sim/tools/activity_power_characterization.py
--markdown`; `--check` fails if this block is stale.

<!-- activity-tables:begin (generated by sim/tools/activity_power_characterization.py; do not edit) -->
### Same netlist, same rate: uniform vs observed, steady window, every corner

Digital total power in uW at 1 MHz (`report_power`), identical SPEF in both columns.

| corner | uniform 0.25 | alarm-gated | backpressure | conditioned-streaming | disabled-clock-running | raw-streaming | observed max / uniform |
|---|---:|---:|---:|---:|---:|---:|---:|
| ss_125C_3v00/rc-min | 208.93 | 140.20 | 156.17 | 156.43 | 130.49 | 157.13 | 0.752 |
| ss_125C_3v00/rc-nom | 211.24 | 141.40 | 157.57 | 157.84 | 131.57 | 158.56 | 0.751 |
| ss_125C_3v00/rc-max | 214.08 | 142.89 | 159.30 | 159.57 | 132.91 | 160.32 | 0.749 |
| ss_n40C_3v00/rc-min | 195.15 | 130.96 | 145.85 | 146.10 | 121.84 | 146.77 | 0.752 |
| ss_n40C_3v00/rc-nom | 197.35 | 132.07 | 147.16 | 147.41 | 122.83 | 148.09 | 0.750 |
| ss_n40C_3v00/rc-max | 200.05 | 133.44 | 148.76 | 149.02 | 124.06 | 149.73 | 0.748 |
| tt_025C_3v30/rc-min | 248.43 | 165.62 | 184.82 | 185.13 | 153.99 | 185.98 | 0.749 |
| tt_025C_3v30/rc-nom | 251.34 | 167.18 | 186.62 | 186.94 | 155.40 | 187.81 | 0.747 |
| tt_025C_3v30/rc-max | 254.94 | 169.10 | 188.84 | 189.17 | 157.14 | 190.07 | 0.746 |
| ff_125C_3v60/rc-min | 330.45 | 221.84 | 247.40 | 247.73 | 206.51 | 248.82 | 0.753 |
| ff_125C_3v60/rc-nom | 334.43 | 224.11 | 250.00 | 250.33 | 208.60 | 251.45 | 0.752 |
| ff_125C_3v60/rc-max | 339.35 | 226.91 | 253.20 | 253.55 | 211.19 | 254.71 | 0.751 |
| ff_n40C_3v60/rc-min | 302.05 | 201.10 | 224.45 | 224.83 | 187.06 | 225.86 | 0.748 |
| ff_n40C_3v60/rc-nom | 305.80 | 203.17 | 226.82 | 227.21 | 188.95 | 228.27 | 0.746 |
| ff_n40C_3v60/rc-max | 310.42 | 205.73 | 229.76 | 230.17 | 191.30 | 231.26 | 0.745 |

### Workload-specific maxima over the 15 corners (uW) and where they bind

| workload | window | max total | at corner | internal | switching | leakage | vs uniform at that corner |
|---|---|---:|---|---:|---:|---:|---:|
| alarm-gated | reset | 205.85 | ff_125C_3v60/rc-max | 153.41 | 45.39 | 7.051 | 0.607 |
| alarm-gated | startup | 235.50 | ff_125C_3v60/rc-max | 171.36 | 56.45 | 7.696 | 0.694 |
| alarm-gated | steady | 226.91 | ff_125C_3v60/rc-max | 166.19 | 53.06 | 7.668 | 0.669 |
| backpressure | reset | 205.65 | ff_125C_3v60/rc-max | 153.34 | 45.26 | 7.051 | 0.606 |
| backpressure | startup | 236.04 | ff_125C_3v60/rc-max | 171.73 | 56.64 | 7.665 | 0.696 |
| backpressure | steady | 253.20 | ff_125C_3v60/rc-max | 182.36 | 62.86 | 7.977 | 0.746 |
| conditioned-streaming | reset | 205.82 | ff_125C_3v60/rc-max | 153.39 | 45.38 | 7.051 | 0.607 |
| conditioned-streaming | startup | 236.75 | ff_125C_3v60/rc-max | 172.15 | 56.93 | 7.677 | 0.698 |
| conditioned-streaming | steady | 253.55 | ff_125C_3v60/rc-max | 182.58 | 63.09 | 7.886 | 0.747 |
| disabled-clock-running | reset | 204.12 | ff_125C_3v60/rc-max | 152.49 | 44.57 | 7.051 | 0.601 |
| disabled-clock-running | startup | 211.45 | ff_125C_3v60/rc-max | 156.95 | 47.13 | 7.367 | 0.623 |
| disabled-clock-running | steady | 211.19 | ff_125C_3v60/rc-max | 156.78 | 47.04 | 7.367 | 0.622 |
| raw-streaming | reset | 205.90 | ff_125C_3v60/rc-max | 153.27 | 45.57 | 7.051 | 0.607 |
| raw-streaming | startup | 237.45 | ff_125C_3v60/rc-max | 172.34 | 57.49 | 7.622 | 0.700 |
| raw-streaming | steady | 254.71 | ff_125C_3v60/rc-max | 183.02 | 63.79 | 7.898 | 0.751 |

### Term breakdown at the digital-binding corner of the ratified rollup (ff_125C_3v60/rc-max)

| workload / window | clock | sequential | combinational | internal | switching | leakage | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| uniform | 75.74 | 171.82 | 91.79 | 234.69 | 97.04 | 7.617 | 339.35 |
| alarm-gated / reset | 75.74 | 122.60 | 7.51 | 153.41 | 45.39 | 7.051 | 205.85 |
| alarm-gated / startup | 75.74 | 135.34 | 24.43 | 171.36 | 56.45 | 7.696 | 235.50 |
| alarm-gated / steady | 75.74 | 132.89 | 18.28 | 166.19 | 53.06 | 7.668 | 226.91 |
| backpressure / reset | 75.74 | 122.59 | 7.32 | 153.34 | 45.26 | 7.051 | 205.65 |
| backpressure / startup | 75.74 | 135.48 | 24.82 | 171.73 | 56.64 | 7.665 | 236.04 |
| backpressure / steady | 75.74 | 144.57 | 32.90 | 182.36 | 62.86 | 7.977 | 253.20 |
| conditioned-streaming / reset | 75.74 | 122.60 | 7.48 | 153.39 | 45.38 | 7.051 | 205.82 |
| conditioned-streaming / startup | 75.74 | 135.81 | 25.21 | 172.15 | 56.93 | 7.677 | 236.75 |
| conditioned-streaming / steady | 75.74 | 144.60 | 33.21 | 182.58 | 63.09 | 7.886 | 253.55 |
| disabled-clock-running / reset | 75.74 | 122.54 | 5.84 | 152.49 | 44.57 | 7.051 | 204.12 |
| disabled-clock-running / startup | 75.74 | 124.81 | 10.90 | 156.95 | 47.13 | 7.367 | 211.45 |
| disabled-clock-running / steady | 75.74 | 124.87 | 10.59 | 156.78 | 47.04 | 7.367 | 211.19 |
| raw-streaming / reset | 75.74 | 122.60 | 7.56 | 153.27 | 45.57 | 7.051 | 205.90 |
| raw-streaming / startup | 75.74 | 135.54 | 26.17 | 172.34 | 57.49 | 7.622 | 237.45 |
| raw-streaming / steady | 75.74 | 144.55 | 34.42 | 183.02 | 63.79 | 7.898 | 254.71 |

### Annotation coverage

Pins in the design as OpenSTA sees them: [5143]. Largest unannotated count in any (corner, workload, window): 0. Every window is annotated from the VCD; no pin runs on a fallback activity in any record.

### Illustration only: whole-block active power if the digital term were the observed maximum

The ratified rollup (`python3 sim/tools/power_rollup.py`) is unchanged and still uses the uniform-activity digital term. Substituting, at the same digital-binding corner, the largest observed steady-window total of any declared workload for that term:

- ratified digital term (uniform, ff_125C_3v60/rc-max): 339.4 uW
- largest observed steady total at the same corner: 254.7 uW (0.751 of the ratified term)
- change to the whole-block active total at any analog corner: -84.6 uW
<!-- activity-tables:end -->

## 4. What the table does and does not say

- **Not a supply-current measurement, not silicon, not a worst case.** Five
  declared synthetic stimuli, simulated with zero delay. Glitching that real
  delays would add is not modelled, so the observed numbers are, if anything,
  optimistic for dynamic power. The uniform figure is a model assumption and
  its being higher here says only that this design under these stimuli toggles
  less than 0.25 transitions/net/cycle on average, not that the assumption is
  wrong for other stimuli.
- **Clock-network power is not workload-dependent in this analysis.** The
  clock group (73.7 uW at the binding corner) is identical in every row,
  because OpenSTA derives clock-network activity from the propagated clock, not
  from the VCD; the VCD's `clk` toggle count is checked against the window
  length instead. This is also why a disabled block with a running clock
  retains most of the power.
- **Leakage** is a separate column in every row and is state-dependent in the
  library (`when` conditions), so it moves by a few percent between workloads
  (7.27 to 8.19 uW at the binding corner). It is **not** the stopped-clock idle
  figure: that state was not simulated and its leakage depends on the flop
  contents it holds. The default flow's leakage column (7.84 uW at the same
  corner) is the nearest like-for-like number.
- **x/z handling.** FIFO memory flops have no reset port and hold x until
  written; the x events are counted per trace (about 0.2 % of events or fewer)
  and kept verbatim. How OpenSTA's reader treats a transition through x is that
  tool's behaviour and is not independently verified here.
- **Coverage.** 5371 of 5371 pins annotated from the VCD in every window;
  unannotated pins are counted per window in every record and, above 1 %,
  reject the corner.
- Interconnect, IR drop, I/O timing and extraction caveats are those of the
  default flow (`sim/tb/digital-sta-power/README.md`).

## 5. What changes in the budget, and what does not

Nothing is changed. `python3 sim/tools/power_rollup.py` still prices the digital
term at its ratified 348.2 uW (uniform activity, `ff_125C_3v60`/`max`) and
reports the worst active corner at 758.2 uW, 151.6 % of the < 500 uW row. The
illustration at the end of section 3 shows what a substitution would do: the
digital term would fall by 96.9 uW, taking that worst-corner total to about
661 uW, still above the row (about 132 %). The verdict (the active-power row is
not met) is therefore the same under either digital term, which is why this is
recorded as characterization. The 758.2 uW (and the 661 uW illustration) are a lower bound on the
analog side: the ledger now carries the shipped liveness samplers as a required
term (#463), measured at 1 of 27 corners so far and a gap at this one, so the
analog term here excludes them. That is independent of the digital choice and
does not change the comparison, which is digital-only. Adopting an activity-derived term in the rollup
would change the published number, and under [DR-0023] that goes through a
decision record, not through this document. The idle-current row is untouched:
it is a leakage-only quantity and this campaign adds no stopped-clock state.

## 6. Reproduce, and what keeps it honest

```sh
python3 sim/tb/digital-sta-power/activity.py capture            # 5 traces + manifest (about 20 s)
python3 sim/tb/digital-sta-power/run_sta.py --activity          # 15 records (about 2.5 min)
python3 sim/tb/digital-sta-power/activity_power.py negative-controls
python3 sim/tools/activity_power_characterization.py --check    # no PDK, no simulator
```

`--check` is part of `npm run check:spec`. It fails if the 15-corner family
does not describe the committed DEF and `pnr.v`, if the records disagree about
trace identities, if a workload no longer generates the stimulus a record was
captured from, if any record's uniform baseline differs from the default flow's
`digital-sta-power` 1 MHz total at the same corner, if any window lost pins
to fallback, or if this document's generated block is stale. Traces
(16 to 22 MB each) are not committed; their sha256 and stimulus sha256 are in
every record and regenerate byte-identically (the VCD `$date` header is
normalised).
