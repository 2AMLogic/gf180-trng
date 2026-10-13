---
record: 2026-10-10-digital-sta-activity-12
date: 2026-10-10T02:46:23Z
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
repo_commit: d01212256aee65c9be3593221aded02dded2644f

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60.lib (liberty corner ff_125C_3v60, sha256:b64f32b397097f2046e66ce7f9a4aaffc9a80c4c0bfd3c77385727268e81a016)
  - gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:80bf186e7fcc2c4b1bae9b8ee0e67100acf4f643e71a58daadc3f354f0836508)
  - gf180mcu_fd_sc_mcu9t5v0.lef (cell LEF, sha256:38afbef95529165e1d8999d5b5613c4aec9869df8c1ce6b5555e74586ba4c826)
  - rules.openrcx.gf180mcuD.max (OpenRCX interconnect corner max, sha256:0ee103cf2108f2fd945087551b6dd1eaf4ee55af60571de2983878c8a271515f)
  - <pdk>/libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/gf180mcu_fd_sc_mcu9t5v0.v (gate-simulation cell model, sha256:7dc2d6578c3580b0716c6a883a1b33c6cc7172f29c74ac1b148b0b20f981fe16)
  - <pdk>/libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/primitives.v (gate-simulation cell model, sha256:fc47cb4d4e50feb06847eba4bb1d67bec09a648fe2ab7aeab30248cb75d3609c)

tool:
  ngspice: "n/a (gate-level record)"
  openroad: "26Q3-1510-g6cb3f2b704"
  simulator: "Icarus Verilog version 13.0 (stable) (v13_0) -g2012 -gno-specify (zero delay; specify blocks ignored)"

corner:
  process: ff
  voltage: 3.60 V (nominal 3.3 V, +9.1%)
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60
  interconnect: max (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature 125, nom_voltage 3.6 (read from the deck)

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
  spef_sha256: f1c13c8ef501708939bd991f53de1a973dfb4abd5ca915bbcb5c24e8586d43e8
  spef_bytes: 1775752
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-12/
  files:
    - uniform.tcl  sha256:06de7ab8e11e00d4ab6c663effdf79cb12d7bba50c404b5f22114a56d51bdec5
    - uniform.log  sha256:6463923b5067bc12a7e403faae7d6097fe6c4450721589898bbf10d477dc02b6
    - observed.tcl  sha256:3d4230c07aa2d8feed208c0ad96c3c11636d70dcc63a72ab4d5da00293d3caab
    - observed.log  sha256:f0bbbf5dfae1c418a8fccec1529553c270f2886df7d36dcb3c8aada2e86438f2
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 9.6s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    238.82 |    101.53 |      7.84 |    348.19 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    152.55 |     46.07 |      7.27 |    205.90 | 0.591 | 5371 / 0 |
| alarm-gated | startup | 1040 |    167.92 |     55.69 |      7.86 |    231.47 | 0.665 | 5371 / 0 |
| alarm-gated | steady | 1024 |    163.14 |     52.25 |      7.84 |    223.24 | 0.641 | 5371 / 0 |
| backpressure | reset | 8 |    152.49 |     45.94 |      7.27 |    205.70 | 0.591 | 5371 / 0 |
| backpressure | startup | 1040 |    168.19 |     55.86 |      7.86 |    231.91 | 0.666 | 5371 / 0 |
| backpressure | steady | 1024 |    179.22 |     62.32 |      8.19 |    249.73 | 0.717 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    152.54 |     46.04 |      7.27 |    205.85 | 0.591 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    168.49 |     56.14 |      7.86 |    232.49 | 0.668 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    179.37 |     62.50 |      8.10 |    249.96 | 0.718 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    152.04 |     45.35 |      7.27 |    204.66 | 0.588 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    156.04 |     46.83 |      7.66 |    210.52 | 0.605 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    155.86 |     46.75 |      7.66 |    210.27 | 0.604 | 5371 / 0 |
| raw-streaming | reset | 8 |    152.65 |     46.33 |      7.27 |    206.25 | 0.592 | 5371 / 0 |
| raw-streaming | startup | 1040 |    169.00 |     56.81 |      7.81 |    233.62 | 0.671 | 5371 / 0 |
| raw-streaming | steady | 1024 |    179.94 |     63.22 |      8.12 |    251.27 | 0.722 | 5371 / 0 |

- `uniform_total_w`: 3.481905e-04
- `uniform_internal_w`: 2.388199e-04
- `uniform_switching_w`: 1.015284e-04
- `uniform_leakage_w`: 7.842120e-06
- `uniform_clock_w`: 7.371024e-05
- `uniform_sequential_w`: 1.773889e-04
- `uniform_combinational_w`: 9.709135e-05
- `uniform_total_a`: 9.671958e-05
- `obs_alarm_gated_reset_total_w`: 2.058956e-04
- `obs_alarm_gated_reset_internal_w`: 1.525518e-04
- `obs_alarm_gated_reset_switching_w`: 4.607128e-05
- `obs_alarm_gated_reset_leakage_w`: 7.272558e-06
- `obs_alarm_gated_reset_clock_w`: 7.371024e-05
- `obs_alarm_gated_reset_sequential_w`: 1.237202e-04
- `obs_alarm_gated_reset_combinational_w`: 8.465311e-06
- `obs_alarm_gated_reset_total_a`: 5.719322e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.314712e-04
- `obs_alarm_gated_startup_internal_w`: 1.679190e-04
- `obs_alarm_gated_startup_switching_w`: 5.568926e-05
- `obs_alarm_gated_startup_leakage_w`: 7.862931e-06
- `obs_alarm_gated_startup_clock_w`: 7.371024e-05
- `obs_alarm_gated_startup_sequential_w`: 1.352467e-04
- `obs_alarm_gated_startup_combinational_w`: 2.251424e-05
- `obs_alarm_gated_startup_total_a`: 6.429756e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.232368e-04
- `obs_alarm_gated_steady_internal_w`: 1.631413e-04
- `obs_alarm_gated_steady_switching_w`: 5.225340e-05
- `obs_alarm_gated_steady_leakage_w`: 7.842063e-06
- `obs_alarm_gated_steady_clock_w`: 7.371024e-05
- `obs_alarm_gated_steady_sequential_w`: 1.323379e-04
- `obs_alarm_gated_steady_combinational_w`: 1.718863e-05
- `obs_alarm_gated_steady_total_a`: 6.201022e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.057021e-04
- `obs_backpressure_reset_internal_w`: 1.524872e-04
- `obs_backpressure_reset_switching_w`: 4.594235e-05
- `obs_backpressure_reset_leakage_w`: 7.272558e-06
- `obs_backpressure_reset_clock_w`: 7.371024e-05
- `obs_backpressure_reset_sequential_w`: 1.237093e-04
- `obs_backpressure_reset_combinational_w`: 8.282745e-06
- `obs_backpressure_reset_total_a`: 5.713947e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.319105e-04
- `obs_backpressure_startup_internal_w`: 1.681935e-04
- `obs_backpressure_startup_switching_w`: 5.585923e-05
- `obs_backpressure_startup_leakage_w`: 7.857784e-06
- `obs_backpressure_startup_clock_w`: 7.371024e-05
- `obs_backpressure_startup_sequential_w`: 1.352987e-04
- `obs_backpressure_startup_combinational_w`: 2.290174e-05
- `obs_backpressure_startup_total_a`: 6.441958e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.497311e-04
- `obs_backpressure_steady_internal_w`: 1.792197e-04
- `obs_backpressure_steady_switching_w`: 6.231988e-05
- `obs_backpressure_steady_leakage_w`: 8.191520e-06
- `obs_backpressure_steady_clock_w`: 7.371024e-05
- `obs_backpressure_steady_sequential_w`: 1.441795e-04
- `obs_backpressure_steady_combinational_w`: 3.184126e-05
- `obs_backpressure_steady_total_a`: 6.936975e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.058487e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.525370e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.603907e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.272558e-06
- `obs_conditioned_streaming_reset_clock_w`: 7.371024e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.237202e-04
- `obs_conditioned_streaming_reset_combinational_w`: 8.418347e-06
- `obs_conditioned_streaming_reset_total_a`: 5.718019e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.324937e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.684890e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.614449e-05
- `obs_conditioned_streaming_startup_leakage_w`: 7.860215e-06
- `obs_conditioned_streaming_startup_clock_w`: 7.371024e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.355338e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.324975e-05
- `obs_conditioned_streaming_startup_total_a`: 6.458158e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.499607e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.793657e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.249721e-05
- `obs_conditioned_streaming_steady_leakage_w`: 8.097756e-06
- `obs_conditioned_streaming_steady_clock_w`: 7.371024e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.441376e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.211285e-05
- `obs_conditioned_streaming_steady_total_a`: 6.943353e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 2.046605e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.520415e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.534649e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.272558e-06
- `obs_disabled_clock_running_reset_clock_w`: 7.371024e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.236651e-04
- `obs_disabled_clock_running_reset_combinational_w`: 7.285195e-06
- `obs_disabled_clock_running_reset_total_a`: 5.685014e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.105236e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.560352e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.683277e-05
- `obs_disabled_clock_running_startup_leakage_w`: 7.655682e-06
- `obs_disabled_clock_running_startup_clock_w`: 7.371024e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.259717e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.084149e-05
- `obs_disabled_clock_running_startup_total_a`: 5.847878e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.102716e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.558626e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.675283e-05
- `obs_disabled_clock_running_steady_leakage_w`: 7.656220e-06
- `obs_disabled_clock_running_steady_clock_w`: 7.371024e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.260284e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.053286e-05
- `obs_disabled_clock_running_steady_total_a`: 5.840878e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.062527e-04
- `obs_raw_streaming_reset_internal_w`: 1.526462e-04
- `obs_raw_streaming_reset_switching_w`: 4.633401e-05
- `obs_raw_streaming_reset_leakage_w`: 7.272558e-06
- `obs_raw_streaming_reset_clock_w`: 7.371024e-05
- `obs_raw_streaming_reset_sequential_w`: 1.237190e-04
- `obs_raw_streaming_reset_combinational_w`: 8.823480e-06
- `obs_raw_streaming_reset_total_a`: 5.729242e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.336211e-04
- `obs_raw_streaming_startup_internal_w`: 1.689991e-04
- `obs_raw_streaming_startup_switching_w`: 5.680990e-05
- `obs_raw_streaming_startup_leakage_w`: 7.812067e-06
- `obs_raw_streaming_startup_clock_w`: 7.371024e-05
- `obs_raw_streaming_startup_sequential_w`: 1.355349e-04
- `obs_raw_streaming_startup_combinational_w`: 2.437588e-05
- `obs_raw_streaming_startup_total_a`: 6.489475e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.512749e-04
- `obs_raw_streaming_steady_internal_w`: 1.799356e-04
- `obs_raw_streaming_steady_switching_w`: 6.322328e-05
- `obs_raw_streaming_steady_leakage_w`: 8.116017e-06
- `obs_raw_streaming_steady_clock_w`: 7.371024e-05
- `obs_raw_streaming_steady_sequential_w`: 1.441779e-04
- `obs_raw_streaming_steady_combinational_w`: 3.338677e-05
- `obs_raw_streaming_steady_total_a`: 6.979858e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_125C_3v60 --rc max --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_125C_3v60, interconnect `max`).
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
