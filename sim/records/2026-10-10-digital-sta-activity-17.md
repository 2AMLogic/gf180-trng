---
record: 2026-10-10-digital-sta-activity-17
date: 2026-10-10T07:11:39Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: 8f13adca1f40260c48314a800b021eda212876f4
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha b16950323f54a4dd4de1dc5f89abc8565ab11b72).
repo_commit: 37b0d1714e0aa26771c265216557e0ec45825dcb

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib (liberty corner ss_125C_3v00, sha256:c31d836785af6af4502aadaaf7cc0f604119d38fd66b8ee32733510eabdad6d2)
  - gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:332ae93d61ac55f793da97a6391703f78bc415653cb60e76dd8eb0092124485a)
  - gf180mcu_fd_sc_mcu9t5v0.lef (cell LEF, sha256:38afbef95529165e1d8999d5b5613c4aec9869df8c1ce6b5555e74586ba4c826)
  - rules.openrcx.gf180mcuD.nom (OpenRCX interconnect corner nom, sha256:d83a04ea28af9b74a097fb479bbab9ed52859a1e3428b33d3151cb5afae62ddf)
  - <pdk>/libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/gf180mcu_fd_sc_mcu9t5v0.v (gate-simulation cell model, sha256:7dc2d6578c3580b0716c6a883a1b33c6cc7172f29c74ac1b148b0b20f981fe16)
  - <pdk>/libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/primitives.v (gate-simulation cell model, sha256:fc47cb4d4e50feb06847eba4bb1d67bec09a648fe2ab7aeab30248cb75d3609c)

tool:
  ngspice: "n/a (gate-level record)"
  openroad: "26Q3-1510-g6cb3f2b704"
  simulator: "Icarus Verilog version 13.0 (stable) (v13_0) -g2012 -gno-specify (zero delay; specify blocks ignored)"

corner:
  process: ss
  voltage: 3.00 V (nominal 3.3 V, -9.1%)
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00
  interconnect: nom (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature 125, nom_voltage 3 (read from the deck)

analysis:
  type: sta+power with per-pin switching activity annotated from a post-route gate-level simulation (OpenSTA read_vcd), against a like-for-like uniform baseline
  tstop: n/a (static power analysis over recorded activity)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 2 (uniform-baseline session + observed-activity session over 5 workloads x 3 capture windows)
  clock: clk, 1000 ns (1 MHz) -- DR-0003's ratified raw rate; traces simulated at the same period so no rate scaling is applied
  clock_model: propagated (CTS tree in the DEF); clock running in every window
  uniform_baseline: 0.25 transitions/net/cycle, duty 0.5 (set_power_activity -global), same session shape as the default flow's 1 MHz point
  activity_scope: tb/dut (read_vcd -scope)
seeds: base 453; per-workload alarm-gated 456, backpressure 455, conditioned-streaming 453, disabled-clock-running 457, raw-streaming 454

parasitics:
  spef_sha256: 96a073b7caddfcb8df0c81452e4f3842c6598e6b1c81e81e88e03f6e0f6f5fb9
  spef_bytes: 1769620
  note: >-
    Both sessions read this one SPEF; it is regenerated, not committed.

activity:
  note: >-
    Zero-delay gate simulation of the as-built post-route netlist
    (iverilog -gno-specify); synthetic stimulus with declared seeds -- the
    raw bits make no entropy claim. Not a silicon current measurement and
    not a worst case.
  simulator_x_z: x/z values are kept verbatim in the VCD and counted in `validation.xz_events`/`xz_vars` (FIFO memory flops without a reset port hold x until written); how OpenSTA's VCD reader treats a transition through x/z is that tool's behaviour and is not independently verified here
  clock_activity: clk is simulated at the stated period, 50 % duty, and its toggle count is checked against the window length; OpenSTA derives clock-network activity from the propagated clock
  testbench_sha: 3625a86ad31f107ce0bcf2795f1a1ea04e5aef7c
  workloads_module_sha: 8e72ab3c3fed2c91d225a21330821ef9fb2e43bb
  traces:
    - workload: alarm-gated
      vcd_sha256: 4a33c9cf88e987f0ef819f9eb48a2a65ef24144150eaf5443a85cd973f6327d1
      vcd_bytes: 20199442
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1490/1490
      xz_events: 4272
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: f7f50e47e2354f5f0952f6bf411a0519d14ae1071847837f5a5d1ebf98fe7d22
      vcd_bytes: 21555986
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4289
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: a0e09fad484e70df0d364a6572e652af0e99e95f35051cc7d3e7b889cc77136f
      vcd_bytes: 21612178
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4168
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: d1259e79bcd8783392f642bc50703ff452608e0618f99694e80183970b262cc4
      vcd_bytes: 16158833
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 1798
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: f2e9b984f3a7f390094899a89512645de77cf3ce78e305fdfd35aa0818ae6227
      vcd_bytes: 21760619
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4488
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-10-10-digital-sta-activity-17/
  files:
    - uniform.tcl  sha256:c5887f6d6daefeffd0a0ec7d005744d73a30a0ba2d0f659b93f3b0b121fdc5b8
    - uniform.log  sha256:7212001a2479594c885dded8f0966b0a9b39a202f067ae97c09bd94dc93f5b54
    - observed.tcl  sha256:ee9ca8a1f6d15106532431092742c8894de2c9b3de5570e2eb171d6aed844ee2
    - observed.log  sha256:1e43dcf601a30791de723a58b6d0f2521a6035aae5cd0ee6efde28ec56f38f7f
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 8.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    147.12 |     68.05 |      2.21 |    217.38 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     96.05 |     30.84 |      2.20 |    129.09 | 0.594 | 5371 / 0 |
| alarm-gated | startup | 1040 |    105.15 |     37.36 |      2.21 |    144.72 | 0.666 | 5371 / 0 |
| alarm-gated | steady | 1024 |    102.36 |     35.03 |      2.21 |    139.60 | 0.642 | 5371 / 0 |
| backpressure | reset | 8 |     96.01 |     30.76 |      2.20 |    128.96 | 0.593 | 5371 / 0 |
| backpressure | startup | 1040 |    105.32 |     37.48 |      2.21 |    145.00 | 0.667 | 5371 / 0 |
| backpressure | steady | 1024 |    111.84 |     41.82 |      2.21 |    155.87 | 0.717 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     96.04 |     30.82 |      2.20 |    129.06 | 0.594 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    105.49 |     37.67 |      2.21 |    145.36 | 0.669 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    111.91 |     41.94 |      2.21 |    156.07 | 0.718 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     95.76 |     30.36 |      2.20 |    128.32 | 0.590 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     98.04 |     31.39 |      2.20 |    131.63 | 0.606 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     97.94 |     31.33 |      2.20 |    131.47 | 0.605 | 5371 / 0 |
| raw-streaming | reset | 8 |     96.10 |     31.02 |      2.20 |    129.32 | 0.595 | 5371 / 0 |
| raw-streaming | startup | 1040 |    105.77 |     38.10 |      2.21 |    146.09 | 0.672 | 5371 / 0 |
| raw-streaming | steady | 1024 |    112.24 |     42.42 |      2.21 |    156.88 | 0.722 | 5371 / 0 |

- `uniform_total_w`: 2.173816e-04
- `uniform_internal_w`: 1.471206e-04
- `uniform_switching_w`: 6.805213e-05
- `uniform_leakage_w`: 2.208865e-06
- `uniform_clock_w`: 4.481110e-05
- `uniform_sequential_w`: 1.141018e-04
- `uniform_combinational_w`: 5.846859e-05
- `uniform_total_a`: 7.246053e-05
- `obs_alarm_gated_reset_total_w`: 1.290892e-04
- `obs_alarm_gated_reset_internal_w`: 9.604669e-05
- `obs_alarm_gated_reset_switching_w`: 3.084375e-05
- `obs_alarm_gated_reset_leakage_w`: 2.198723e-06
- `obs_alarm_gated_reset_clock_w`: 4.481110e-05
- `obs_alarm_gated_reset_sequential_w`: 8.028244e-05
- `obs_alarm_gated_reset_combinational_w`: 3.995672e-06
- `obs_alarm_gated_reset_total_a`: 4.302973e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.447229e-04
- `obs_alarm_gated_startup_internal_w`: 1.051539e-04
- `obs_alarm_gated_startup_switching_w`: 3.736059e-05
- `obs_alarm_gated_startup_leakage_w`: 2.208328e-06
- `obs_alarm_gated_startup_clock_w`: 4.481110e-05
- `obs_alarm_gated_startup_sequential_w`: 8.739559e-05
- `obs_alarm_gated_startup_combinational_w`: 1.251606e-05
- `obs_alarm_gated_startup_total_a`: 4.824097e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.396006e-04
- `obs_alarm_gated_steady_internal_w`: 1.023633e-04
- `obs_alarm_gated_steady_switching_w`: 3.502956e-05
- `obs_alarm_gated_steady_leakage_w`: 2.207755e-06
- `obs_alarm_gated_steady_clock_w`: 4.481110e-05
- `obs_alarm_gated_steady_sequential_w`: 8.553037e-05
- `obs_alarm_gated_steady_combinational_w`: 9.259119e-06
- `obs_alarm_gated_steady_total_a`: 4.653353e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.289620e-04
- `obs_backpressure_reset_internal_w`: 9.600622e-05
- `obs_backpressure_reset_switching_w`: 3.075709e-05
- `obs_backpressure_reset_leakage_w`: 2.198723e-06
- `obs_backpressure_reset_clock_w`: 4.481110e-05
- `obs_backpressure_reset_sequential_w`: 8.027512e-05
- `obs_backpressure_reset_combinational_w`: 3.875847e-06
- `obs_backpressure_reset_total_a`: 4.298733e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.450027e-04
- `obs_backpressure_startup_internal_w`: 1.053181e-04
- `obs_backpressure_startup_switching_w`: 3.747612e-05
- `obs_backpressure_startup_leakage_w`: 2.208553e-06
- `obs_backpressure_startup_clock_w`: 4.481110e-05
- `obs_backpressure_startup_sequential_w`: 8.742544e-05
- `obs_backpressure_startup_combinational_w`: 1.276612e-05
- `obs_backpressure_startup_total_a`: 4.833423e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.558732e-04
- `obs_backpressure_steady_internal_w`: 1.118364e-04
- `obs_backpressure_steady_switching_w`: 4.182474e-05
- `obs_backpressure_steady_leakage_w`: 2.212008e-06
- `obs_backpressure_steady_clock_w`: 4.481110e-05
- `obs_backpressure_steady_sequential_w`: 9.291904e-05
- `obs_backpressure_steady_combinational_w`: 1.814297e-05
- `obs_backpressure_steady_total_a`: 5.195773e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.290584e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.603801e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.082163e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.198723e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.481110e-05
- `obs_conditioned_streaming_reset_sequential_w`: 8.028244e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.964861e-06
- `obs_conditioned_streaming_reset_total_a`: 4.301947e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.453642e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.054879e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.766832e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.207989e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.481110e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.758109e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.297195e-05
- `obs_conditioned_streaming_startup_total_a`: 4.845473e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.560696e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.119147e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.194413e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.210763e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.481110e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.289967e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.835889e-05
- `obs_conditioned_streaming_steady_total_a`: 5.202320e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.283151e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.575706e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.035932e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.198723e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.481110e-05
- `obs_disabled_clock_running_reset_sequential_w`: 8.024770e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.256317e-06
- `obs_disabled_clock_running_reset_total_a`: 4.277170e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.316307e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.804045e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.138567e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.481110e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.149887e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.320755e-06
- `obs_disabled_clock_running_startup_total_a`: 4.387690e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.314739e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.793702e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.133226e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.481110e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.153791e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.124876e-06
- `obs_disabled_clock_running_steady_total_a`: 4.382463e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.293154e-04
- `obs_raw_streaming_reset_internal_w`: 9.609623e-05
- `obs_raw_streaming_reset_switching_w`: 3.102050e-05
- `obs_raw_streaming_reset_leakage_w`: 2.198723e-06
- `obs_raw_streaming_reset_clock_w`: 4.481110e-05
- `obs_raw_streaming_reset_sequential_w`: 8.028228e-05
- `obs_raw_streaming_reset_combinational_w`: 4.222100e-06
- `obs_raw_streaming_reset_total_a`: 4.310513e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.460854e-04
- `obs_raw_streaming_startup_internal_w`: 1.057735e-04
- `obs_raw_streaming_startup_switching_w`: 3.810396e-05
- `obs_raw_streaming_startup_leakage_w`: 2.207986e-06
- `obs_raw_streaming_startup_clock_w`: 4.481110e-05
- `obs_raw_streaming_startup_sequential_w`: 8.758205e-05
- `obs_raw_streaming_startup_combinational_w`: 1.369228e-05
- `obs_raw_streaming_startup_total_a`: 4.869513e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.568780e-04
- `obs_raw_streaming_steady_internal_w`: 1.122438e-04
- `obs_raw_streaming_steady_switching_w`: 4.242268e-05
- `obs_raw_streaming_steady_leakage_w`: 2.211509e-06
- `obs_raw_streaming_steady_clock_w`: 4.481110e-05
- `obs_raw_streaming_steady_sequential_w`: 9.292167e-05
- `obs_raw_streaming_steady_combinational_w`: 1.914529e-05
- `obs_raw_streaming_steady_total_a`: 5.229267e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_125C_3v00 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_125C_3v00, interconnect `nom`).
- **Observed activity is from a zero-delay simulation of five declared
  synthetic workloads.** Not a supply-current measurement, not silicon, and
  no workload here is claimed to be the worst case. Glitching beyond
  same-timestamp delta activity is not modelled.
- **Leakage is state-dependent in the library** (`when` conditions), so the
  leakage column moves a little between workloads. A *stopped* clock is not
  simulated: its idle power is leakage only, and this record's leakage
  column is the nearest evidence, not a measurement of that state. The
  `disabled-clock-running` workload is a disabled block with a **running**
  clock, which still pays the clock tree.
- **Clock-network activity** follows the propagated clock at the stated
  period (the VCD `clk` toggle count is validated against the window length).
- **Unannotated pins** (last column) run on OpenSTA's fallback activity and
  are never presented as measured; the trace is rejected outright below
  99% annotation.
- Uniform baseline: 0.25 transitions/net/cycle at duty
  0.5, the default flow's model assumption.
- No IR drop, no I/O timing, no foundry-signed extraction: see
  `sim/tb/digital-sta-power/README.md`.

---

Written by `sim/tb/digital-sta-power/activity_power.py`. Append-only: never edit
or delete this file -- a re-run or correction mints a new record and points
back here via `supersedes` (see `sim/README.md`).
