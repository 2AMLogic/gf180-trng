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
| ss_125C_3v00/rc-min | 208.53 | 141.26 | 157.21 | 157.47 | 130.98 | 158.14 | 0.758 |
| ss_125C_3v00/rc-nom | 210.90 | 142.52 | 158.68 | 158.94 | 132.10 | 159.63 | 0.757 |
| ss_125C_3v00/rc-max | 213.81 | 144.08 | 160.48 | 160.75 | 133.48 | 161.46 | 0.755 |
| ss_n40C_3v00/rc-min | 194.91 | 132.00 | 146.89 | 147.13 | 122.36 | 147.76 | 0.758 |
| ss_n40C_3v00/rc-nom | 197.17 | 133.18 | 148.26 | 148.51 | 123.39 | 149.16 | 0.756 |
| ss_n40C_3v00/rc-max | 199.95 | 134.62 | 149.94 | 150.20 | 124.66 | 150.87 | 0.755 |
| tt_025C_3v30/rc-min | 247.79 | 166.82 | 185.98 | 186.29 | 154.49 | 187.09 | 0.755 |
| tt_025C_3v30/rc-nom | 250.79 | 168.46 | 187.87 | 188.18 | 155.96 | 189.00 | 0.754 |
| tt_025C_3v30/rc-max | 254.48 | 170.48 | 190.19 | 190.51 | 157.76 | 191.36 | 0.752 |
| ff_125C_3v60/rc-min | 328.96 | 223.12 | 248.60 | 248.93 | 206.82 | 249.93 | 0.760 |
| ff_125C_3v60/rc-nom | 333.06 | 225.51 | 251.31 | 251.64 | 208.99 | 252.68 | 0.759 |
| ff_125C_3v60/rc-max | 338.12 | 228.46 | 254.65 | 254.99 | 211.68 | 256.06 | 0.757 |
| ff_n40C_3v60/rc-min | 301.02 | 202.45 | 225.75 | 226.13 | 187.54 | 227.09 | 0.754 |
| ff_n40C_3v60/rc-nom | 304.87 | 204.63 | 228.23 | 228.61 | 189.50 | 229.60 | 0.753 |
| ff_n40C_3v60/rc-max | 309.60 | 207.31 | 231.28 | 231.68 | 191.92 | 232.70 | 0.752 |

### Workload-specific maxima over the 15 corners (uW) and where they bind

| workload | window | max total | at corner | internal | switching | leakage | vs uniform at that corner |
|---|---|---:|---|---:|---:|---:|---:|
| alarm-gated | reset | 207.06 | ff_125C_3v60/rc-max | 153.04 | 47.02 | 7.002 | 0.612 |
| alarm-gated | startup | 236.10 | ff_125C_3v60/rc-max | 170.87 | 57.57 | 7.654 | 0.698 |
| alarm-gated | steady | 228.46 | ff_125C_3v60/rc-max | 166.29 | 54.54 | 7.635 | 0.676 |
| backpressure | reset | 206.87 | ff_125C_3v60/rc-max | 152.97 | 46.89 | 7.002 | 0.612 |
| backpressure | startup | 236.65 | ff_125C_3v60/rc-max | 171.26 | 57.77 | 7.623 | 0.700 |
| backpressure | steady | 254.65 | ff_125C_3v60/rc-max | 182.36 | 64.35 | 7.937 | 0.753 |
| conditioned-streaming | reset | 207.02 | ff_125C_3v60/rc-max | 153.02 | 46.99 | 7.002 | 0.612 |
| conditioned-streaming | startup | 237.43 | ff_125C_3v60/rc-max | 171.71 | 58.08 | 7.634 | 0.702 |
| conditioned-streaming | steady | 254.99 | ff_125C_3v60/rc-max | 182.57 | 64.57 | 7.853 | 0.754 |
| disabled-clock-running | reset | 205.36 | ff_125C_3v60/rc-max | 152.14 | 46.22 | 7.002 | 0.607 |
| disabled-clock-running | startup | 211.92 | ff_125C_3v60/rc-max | 156.35 | 48.24 | 7.335 | 0.627 |
| disabled-clock-running | steady | 211.68 | ff_125C_3v60/rc-max | 156.18 | 48.17 | 7.336 | 0.626 |
| raw-streaming | reset | 207.06 | ff_125C_3v60/rc-max | 152.89 | 47.17 | 7.002 | 0.612 |
| raw-streaming | startup | 238.02 | ff_125C_3v60/rc-max | 171.82 | 58.62 | 7.576 | 0.704 |
| raw-streaming | steady | 256.06 | ff_125C_3v60/rc-max | 182.96 | 65.25 | 7.855 | 0.757 |

### Term breakdown at the digital-binding corner of the ratified rollup (ff_125C_3v60/rc-max)

| workload / window | clock | sequential | combinational | internal | switching | leakage | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| uniform | 76.73 | 171.89 | 89.49 | 232.49 | 98.04 | 7.579 | 338.12 |
| alarm-gated / reset | 76.73 | 122.56 | 7.77 | 153.04 | 47.02 | 7.002 | 207.06 |
| alarm-gated / startup | 76.73 | 135.28 | 24.10 | 170.87 | 57.57 | 7.654 | 236.10 |
| alarm-gated / steady | 76.73 | 132.90 | 18.84 | 166.29 | 54.54 | 7.635 | 228.46 |
| backpressure / reset | 76.73 | 122.55 | 7.60 | 152.97 | 46.89 | 7.002 | 206.87 |
| backpressure / startup | 76.73 | 135.42 | 24.50 | 171.26 | 57.77 | 7.623 | 236.65 |
| backpressure / steady | 76.73 | 144.56 | 33.36 | 182.36 | 64.35 | 7.937 | 254.65 |
| conditioned-streaming / reset | 76.73 | 122.56 | 7.73 | 153.02 | 46.99 | 7.002 | 207.02 |
| conditioned-streaming / startup | 76.73 | 135.75 | 24.95 | 171.71 | 58.08 | 7.634 | 237.43 |
| conditioned-streaming / steady | 76.73 | 144.59 | 33.67 | 182.57 | 64.57 | 7.853 | 254.99 |
| disabled-clock-running / reset | 76.73 | 122.50 | 6.14 | 152.14 | 46.22 | 7.002 | 205.36 |
| disabled-clock-running / startup | 76.73 | 124.75 | 10.44 | 156.35 | 48.24 | 7.335 | 211.92 |
| disabled-clock-running / steady | 76.73 | 124.81 | 10.15 | 156.18 | 48.17 | 7.336 | 211.68 |
| raw-streaming / reset | 76.73 | 122.55 | 7.78 | 152.89 | 47.17 | 7.002 | 207.06 |
| raw-streaming / startup | 76.73 | 135.48 | 25.81 | 171.82 | 58.62 | 7.576 | 238.02 |
| raw-streaming / steady | 76.73 | 144.54 | 34.79 | 182.96 | 65.25 | 7.855 | 256.06 |

### Annotation coverage

Pins in the design as OpenSTA sees them: [5145]. Largest unannotated count in any (corner, workload, window): 0. Every window is annotated from the VCD; no pin runs on a fallback activity in any record.

### Illustration only: whole-block active power if the digital term were the observed maximum

The ratified rollup (`python3 sim/tools/power_rollup.py`) is unchanged and still uses the uniform-activity digital term. Substituting, at the same digital-binding corner, the largest observed steady-window total of any declared workload for that term:

- ratified digital term (uniform, ff_125C_3v60/rc-max): 338.1 uW
- largest observed steady total at the same corner: 256.1 uW (0.757 of the ratified term)
- change to the whole-block active total at any analog corner: -82.1 uW
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
