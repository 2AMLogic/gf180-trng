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
   348.7 uW uniform.
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
| ss_125C_3v00/rc-min | 215.24 | 138.98 | 154.91 | 155.10 | 130.90 | 155.88 | 0.724 |
| ss_125C_3v00/rc-nom | 217.76 | 140.29 | 156.41 | 156.61 | 132.07 | 157.42 | 0.723 |
| ss_125C_3v00/rc-max | 220.87 | 141.89 | 158.27 | 158.47 | 133.51 | 159.31 | 0.721 |
| ss_n40C_3v00/rc-min | 201.03 | 129.74 | 144.60 | 144.78 | 122.14 | 145.52 | 0.724 |
| ss_n40C_3v00/rc-nom | 203.44 | 130.95 | 146.01 | 146.20 | 123.22 | 146.96 | 0.722 |
| ss_n40C_3v00/rc-max | 206.41 | 132.44 | 147.74 | 147.94 | 124.54 | 148.72 | 0.721 |
| tt_025C_3v30/rc-min | 255.35 | 163.58 | 182.72 | 182.95 | 153.91 | 183.89 | 0.720 |
| tt_025C_3v30/rc-nom | 258.54 | 165.27 | 184.66 | 184.89 | 155.43 | 185.87 | 0.719 |
| tt_025C_3v30/rc-max | 262.49 | 167.36 | 187.06 | 187.30 | 157.32 | 188.31 | 0.717 |
| ff_125C_3v60/rc-min | 338.98 | 218.92 | 244.42 | 244.64 | 206.29 | 245.87 | 0.725 |
| ff_125C_3v60/rc-nom | 343.31 | 221.37 | 247.20 | 247.42 | 208.52 | 248.69 | 0.724 |
| ff_125C_3v60/rc-max | 348.70 | 224.43 | 250.66 | 250.90 | 211.33 | 252.21 | 0.723 |
| ff_n40C_3v60/rc-min | 309.97 | 198.28 | 221.55 | 221.83 | 186.60 | 222.98 | 0.719 |
| ff_n40C_3v60/rc-nom | 314.03 | 200.50 | 224.08 | 224.37 | 188.62 | 225.56 | 0.718 |
| ff_n40C_3v60/rc-max | 319.08 | 203.27 | 227.23 | 227.53 | 191.13 | 228.75 | 0.717 |

### Workload-specific maxima over the 15 corners (uW) and where they bind

| workload | window | max total | at corner | internal | switching | leakage | vs uniform at that corner |
|---|---|---:|---|---:|---:|---:|---:|
| alarm-gated | reset | 206.90 | ff_125C_3v60/rc-max | 152.81 | 46.42 | 7.670 | 0.593 |
| alarm-gated | startup | 232.54 | ff_125C_3v60/rc-max | 168.19 | 56.10 | 8.258 | 0.667 |
| alarm-gated | steady | 224.43 | ff_125C_3v60/rc-max | 163.40 | 52.79 | 8.237 | 0.644 |
| backpressure | reset | 206.71 | ff_125C_3v60/rc-max | 152.74 | 46.30 | 7.670 | 0.593 |
| backpressure | startup | 232.98 | ff_125C_3v60/rc-max | 168.46 | 56.26 | 8.253 | 0.668 |
| backpressure | steady | 250.66 | ff_125C_3v60/rc-max | 179.47 | 62.61 | 8.580 | 0.719 |
| conditioned-streaming | reset | 206.85 | ff_125C_3v60/rc-max | 152.79 | 46.39 | 7.670 | 0.593 |
| conditioned-streaming | startup | 233.56 | ff_125C_3v60/rc-max | 168.76 | 56.55 | 8.255 | 0.670 |
| conditioned-streaming | steady | 250.90 | ff_125C_3v60/rc-max | 179.61 | 62.79 | 8.496 | 0.720 |
| disabled-clock-running | reset | 205.70 | ff_125C_3v60/rc-max | 152.30 | 45.74 | 7.670 | 0.590 |
| disabled-clock-running | startup | 211.58 | ff_125C_3v60/rc-max | 156.31 | 47.22 | 8.051 | 0.607 |
| disabled-clock-running | steady | 211.33 | ff_125C_3v60/rc-max | 156.13 | 47.14 | 8.051 | 0.606 |
| raw-streaming | reset | 207.23 | ff_125C_3v60/rc-max | 152.90 | 46.67 | 7.670 | 0.594 |
| raw-streaming | startup | 234.69 | ff_125C_3v60/rc-max | 169.27 | 57.22 | 8.209 | 0.673 |
| raw-streaming | steady | 252.21 | ff_125C_3v60/rc-max | 180.18 | 63.52 | 8.507 | 0.723 |

### Term breakdown at the digital-binding corner of the ratified rollup (ff_125C_3v60/rc-max)

| workload / window | clock | sequential | combinational | internal | switching | leakage | total |
|---|---:|---:|---:|---:|---:|---:|---:|
| uniform | 74.69 | 177.37 | 96.64 | 238.82 | 101.64 | 8.239 | 348.70 |
| alarm-gated / reset | 74.69 | 123.77 | 8.43 | 152.81 | 46.42 | 7.670 | 206.90 |
| alarm-gated / startup | 74.69 | 135.28 | 22.56 | 168.19 | 56.10 | 8.258 | 232.54 |
| alarm-gated / steady | 74.69 | 132.39 | 17.35 | 163.40 | 52.79 | 8.237 | 224.43 |
| backpressure / reset | 74.69 | 123.76 | 8.26 | 152.74 | 46.30 | 7.670 | 206.71 |
| backpressure / startup | 74.69 | 135.34 | 22.94 | 168.46 | 56.26 | 8.253 | 232.98 |
| backpressure / steady | 74.69 | 144.13 | 31.83 | 179.47 | 62.61 | 8.580 | 250.66 |
| conditioned-streaming / reset | 74.69 | 123.77 | 8.38 | 152.79 | 46.39 | 7.670 | 206.85 |
| conditioned-streaming / startup | 74.69 | 135.57 | 23.30 | 168.76 | 56.55 | 8.255 | 233.56 |
| conditioned-streaming / steady | 74.69 | 144.08 | 32.12 | 179.61 | 62.79 | 8.496 | 250.90 |
| disabled-clock-running / reset | 74.69 | 123.72 | 7.29 | 152.30 | 45.74 | 7.670 | 205.70 |
| disabled-clock-running / startup | 74.69 | 126.04 | 10.84 | 156.31 | 47.22 | 8.051 | 211.58 |
| disabled-clock-running / steady | 74.69 | 126.10 | 10.53 | 156.13 | 47.14 | 8.051 | 211.33 |
| raw-streaming / reset | 74.69 | 123.77 | 8.77 | 152.90 | 46.67 | 7.670 | 207.23 |
| raw-streaming / startup | 74.69 | 135.58 | 24.42 | 169.27 | 57.22 | 8.209 | 234.69 |
| raw-streaming / steady | 74.69 | 144.12 | 33.39 | 180.18 | 63.52 | 8.507 | 252.21 |

### Annotation coverage

Pins in the design as OpenSTA sees them: [5371]. Largest unannotated count in any (corner, workload, window): 0. Every window is annotated from the VCD; no pin runs on a fallback activity in any record.

### Illustration only: whole-block active power if the digital term were the observed maximum

The ratified rollup (`python3 sim/tools/power_rollup.py`) is unchanged and still uses the uniform-activity digital term. Substituting, at the same digital-binding corner, the largest observed steady-window total of any declared workload for that term:

- ratified digital term (uniform, ff_125C_3v60/rc-max): 348.7 uW
- largest observed steady total at the same corner: 252.2 uW (0.723 of the ratified term)
- change to the whole-block active total at any analog corner: -96.5 uW
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
term at its ratified 348.7 uW (uniform activity, `ff_125C_3v60`/`max`) and
reports the worst active corner at 758.7 uW, 151.7 % of the < 500 uW row. The
illustration at the end of section 3 shows what a substitution would do: the
digital term would fall by 96.9 uW, taking that worst-corner total to about
661 uW, still above the row (about 132 %). The verdict (the active-power row is
not met) is therefore the same under either digital term, which is why this is
recorded as characterization. The 758.7 uW (and the 661 uW illustration) are a lower bound on the
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
