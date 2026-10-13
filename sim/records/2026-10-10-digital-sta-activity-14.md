---
record: 2026-10-10-digital-sta-activity-14
date: 2026-10-10T02:46:41Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60.lib (liberty corner ff_n40C_3v60, sha256:0b48b93d6800da325a2613ff6c0b998b230a1bbd28031f6da592e9ff30066602)
  - gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:80bf186e7fcc2c4b1bae9b8ee0e67100acf4f643e71a58daadc3f354f0836508)
  - gf180mcu_fd_sc_mcu9t5v0.lef (cell LEF, sha256:38afbef95529165e1d8999d5b5613c4aec9869df8c1ce6b5555e74586ba4c826)
  - rules.openrcx.gf180mcuD.nom (OpenRCX interconnect corner nom, sha256:d83a04ea28af9b74a097fb479bbab9ed52859a1e3428b33d3151cb5afae62ddf)
  - <pdk>/libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/gf180mcu_fd_sc_mcu9t5v0.v (gate-simulation cell model, sha256:7dc2d6578c3580b0716c6a883a1b33c6cc7172f29c74ac1b148b0b20f981fe16)
  - <pdk>/libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/primitives.v (gate-simulation cell model, sha256:fc47cb4d4e50feb06847eba4bb1d67bec09a648fe2ab7aeab30248cb75d3609c)

tool:
  ngspice: "n/a (gate-level record)"
  openroad: "26Q3-1510-g6cb3f2b704"
  simulator: "Icarus Verilog version 13.0 (stable) (v13_0) -g2012 -gno-specify (zero delay; specify blocks ignored)"

corner:
  process: ff
  voltage: 3.60 V (nominal 3.3 V, +9.1%)
  temperature: -40
  liberty: gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60
  interconnect: nom (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature -40, nom_voltage 3.6 (read from the deck)

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
  spef_sha256: 9939a0b184561f88808ef158e5d170ba9f2a88309f4641a2a83eb92e2b7d9bbb
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-14/
  files:
    - uniform.tcl  sha256:e49ee655209e8bc091e1d97b71310dc1eed38810c87d0b3f6feddb321fc939f6
    - uniform.log  sha256:fff25178c2e6af1314b457235bb882e45931d926083a53e943e5bf4b05f858ac
    - observed.tcl  sha256:e6737bef950a1c33984f2bdbe40ae3728aac998f7a57670cdce7436e7af6aaba
    - observed.log  sha256:9e5b0c1f7675e280af92c1ba3fbd28dfc1998dbe3cd31604f7ea449f85373d75
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 8.7s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    216.70 |     96.97 |      0.26 |    313.93 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    140.22 |     44.09 |      0.25 |    184.56 | 0.588 | 5371 / 0 |
| alarm-gated | startup | 1040 |    153.75 |     53.35 |      0.25 |    207.35 | 0.660 | 5371 / 0 |
| alarm-gated | steady | 1024 |    149.55 |     50.04 |      0.25 |    199.85 | 0.637 | 5371 / 0 |
| backpressure | reset | 8 |    140.16 |     43.97 |      0.25 |    184.38 | 0.587 | 5371 / 0 |
| backpressure | startup | 1040 |    153.99 |     53.51 |      0.25 |    207.75 | 0.662 | 5371 / 0 |
| backpressure | steady | 1024 |    163.69 |     59.69 |      0.26 |    223.64 | 0.712 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    140.21 |     44.06 |      0.25 |    184.51 | 0.588 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    154.25 |     53.78 |      0.25 |    208.28 | 0.663 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    163.82 |     59.86 |      0.26 |    223.94 | 0.713 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    139.77 |     43.40 |      0.25 |    183.42 | 0.584 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    143.22 |     44.85 |      0.25 |    188.32 | 0.600 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    143.07 |     44.78 |      0.25 |    188.09 | 0.599 | 5371 / 0 |
| raw-streaming | reset | 8 |    140.30 |     44.34 |      0.25 |    184.89 | 0.589 | 5371 / 0 |
| raw-streaming | startup | 1040 |    154.69 |     54.41 |      0.25 |    209.35 | 0.667 | 5371 / 0 |
| raw-streaming | steady | 1024 |    164.31 |     60.55 |      0.26 |    225.12 | 0.717 | 5371 / 0 |

- `uniform_total_w`: 3.139316e-04
- `uniform_internal_w`: 2.167019e-04
- `uniform_switching_w`: 9.697297e-05
- `uniform_leakage_w`: 2.566557e-07
- `uniform_clock_w`: 6.529987e-05
- `uniform_sequential_w`: 1.633021e-04
- `uniform_combinational_w`: 8.532974e-05
- `uniform_total_a`: 8.720322e-05
- `obs_alarm_gated_reset_total_w`: 1.845573e-04
- `obs_alarm_gated_reset_internal_w`: 1.402201e-04
- `obs_alarm_gated_reset_switching_w`: 4.409222e-05
- `obs_alarm_gated_reset_leakage_w`: 2.450344e-07
- `obs_alarm_gated_reset_clock_w`: 6.529987e-05
- `obs_alarm_gated_reset_sequential_w`: 1.141585e-04
- `obs_alarm_gated_reset_combinational_w`: 5.099027e-06
- `obs_alarm_gated_reset_total_a`: 5.126592e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.073469e-04
- `obs_alarm_gated_startup_internal_w`: 1.537459e-04
- `obs_alarm_gated_startup_switching_w`: 5.334756e-05
- `obs_alarm_gated_startup_leakage_w`: 2.534709e-07
- `obs_alarm_gated_startup_clock_w`: 6.529987e-05
- `obs_alarm_gated_startup_sequential_w`: 1.244558e-04
- `obs_alarm_gated_startup_combinational_w`: 1.759148e-05
- `obs_alarm_gated_startup_total_a`: 5.759636e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.998485e-04
- `obs_alarm_gated_steady_internal_w`: 1.495544e-04
- `obs_alarm_gated_steady_switching_w`: 5.004139e-05
- `obs_alarm_gated_steady_leakage_w`: 2.527087e-07
- `obs_alarm_gated_steady_clock_w`: 6.529987e-05
- `obs_alarm_gated_steady_sequential_w`: 1.217590e-04
- `obs_alarm_gated_steady_combinational_w`: 1.278969e-05
- `obs_alarm_gated_steady_total_a`: 5.551347e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.843753e-04
- `obs_backpressure_reset_internal_w`: 1.401608e-04
- `obs_backpressure_reset_switching_w`: 4.396950e-05
- `obs_backpressure_reset_leakage_w`: 2.450344e-07
- `obs_backpressure_reset_clock_w`: 6.529987e-05
- `obs_backpressure_reset_sequential_w`: 1.141483e-04
- `obs_backpressure_reset_combinational_w`: 4.927194e-06
- `obs_backpressure_reset_total_a`: 5.121536e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.077512e-04
- `obs_backpressure_startup_internal_w`: 1.539863e-04
- `obs_backpressure_startup_switching_w`: 5.351109e-05
- `obs_backpressure_startup_leakage_w`: 2.537612e-07
- `obs_backpressure_startup_clock_w`: 6.529987e-05
- `obs_backpressure_startup_sequential_w`: 1.244973e-04
- `obs_backpressure_startup_combinational_w`: 1.795419e-05
- `obs_backpressure_startup_total_a`: 5.770867e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.236431e-04
- `obs_backpressure_steady_internal_w`: 1.636914e-04
- `obs_backpressure_steady_switching_w`: 5.969348e-05
- `obs_backpressure_steady_leakage_w`: 2.582963e-07
- `obs_backpressure_steady_clock_w`: 6.529987e-05
- `obs_backpressure_steady_sequential_w`: 1.325289e-04
- `obs_backpressure_steady_combinational_w`: 2.581416e-05
- `obs_backpressure_steady_total_a`: 6.212308e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.845124e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.402063e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.406100e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.450344e-07
- `obs_conditioned_streaming_reset_clock_w`: 6.529987e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.141585e-04
- `obs_conditioned_streaming_reset_combinational_w`: 5.054100e-06
- `obs_conditioned_streaming_reset_total_a`: 5.125344e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.082831e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.542458e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.378421e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.531000e-07
- `obs_conditioned_streaming_startup_clock_w`: 6.529987e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.247284e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.825508e-05
- `obs_conditioned_streaming_startup_total_a`: 5.785642e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.239356e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.638159e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.986260e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.571063e-07
- `obs_conditioned_streaming_steady_clock_w`: 6.529987e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.325058e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.612978e-05
- `obs_conditioned_streaming_steady_total_a`: 6.220433e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.834170e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.397693e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.340267e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.450344e-07
- `obs_disabled_clock_running_reset_clock_w`: 6.529987e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.141086e-04
- `obs_disabled_clock_running_reset_combinational_w`: 4.008722e-06
- `obs_disabled_clock_running_reset_total_a`: 5.094917e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.883166e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.432156e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.485292e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.480637e-07
- `obs_disabled_clock_running_startup_clock_w`: 6.529987e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.159226e-04
- `obs_disabled_clock_running_startup_combinational_w`: 7.094050e-06
- `obs_disabled_clock_running_startup_total_a`: 5.231017e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.880903e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.430653e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.477692e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.480635e-07
- `obs_disabled_clock_running_steady_clock_w`: 6.529987e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.159782e-04
- `obs_disabled_clock_running_steady_combinational_w`: 6.812337e-06
- `obs_disabled_clock_running_steady_total_a`: 5.224731e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.848853e-04
- `obs_raw_streaming_reset_internal_w`: 1.402982e-04
- `obs_raw_streaming_reset_switching_w`: 4.434213e-05
- `obs_raw_streaming_reset_leakage_w`: 2.450344e-07
- `obs_raw_streaming_reset_clock_w`: 6.529987e-05
- `obs_raw_streaming_reset_sequential_w`: 1.141579e-04
- `obs_raw_streaming_reset_combinational_w`: 5.427784e-06
- `obs_raw_streaming_reset_total_a`: 5.135703e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.093487e-04
- `obs_raw_streaming_startup_internal_w`: 1.546883e-04
- `obs_raw_streaming_startup_switching_w`: 5.440714e-05
- `obs_raw_streaming_startup_leakage_w`: 2.531801e-07
- `obs_raw_streaming_startup_clock_w`: 6.529987e-05
- `obs_raw_streaming_startup_sequential_w`: 1.247244e-04
- `obs_raw_streaming_startup_combinational_w`: 1.932443e-05
- `obs_raw_streaming_startup_total_a`: 5.815242e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.251175e-04
- `obs_raw_streaming_steady_internal_w`: 1.643141e-04
- `obs_raw_streaming_steady_switching_w`: 6.054535e-05
- `obs_raw_streaming_steady_leakage_w`: 2.580173e-07
- `obs_raw_streaming_steady_clock_w`: 6.529987e-05
- `obs_raw_streaming_steady_sequential_w`: 1.325328e-04
- `obs_raw_streaming_steady_combinational_w`: 2.728466e-05
- `obs_raw_streaming_steady_total_a`: 6.253264e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_n40C_3v60 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_n40C_3v60, interconnect `nom`).
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
