---
record: 2026-10-10-digital-sta-activity-02
date: 2026-10-10T02:44:45Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib (liberty corner ss_125C_3v00, sha256:d83917f827021eadb159f6011905bf20de632533b2953abba89266a88c2b24af)
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
  spef_sha256: 435833a6cadbc7f65976ed9242d7f3b132cf0e9f7216a6577f5c8f83970b6d92
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-02/
  files:
    - uniform.tcl  sha256:f9d24b8d4c3a3b4d85067f64ff144acfd46714e41191174c365c58635725f2d9
    - uniform.log  sha256:1777f9b05482ad6dde8da1bf2c8a1d0233d3c62eab69f6d37ec06c8aedee966d
    - observed.tcl  sha256:2a59aa7114166690c5c7378a4edb56776a95c6f969d41ebaffc84ed9fe171350
    - observed.log  sha256:63d9757cfd3ce19cef8467f5df57919b0bad93b16ff61ff4b663c83af7f4340e
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 14.9s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    147.12 |     68.05 |      2.21 |    217.39 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     96.05 |     30.84 |      2.20 |    129.09 | 0.594 | 5371 / 0 |
| alarm-gated | startup | 1040 |    105.16 |     37.36 |      2.21 |    144.73 | 0.666 | 5371 / 0 |
| alarm-gated | steady | 1024 |    102.37 |     35.03 |      2.21 |    139.60 | 0.642 | 5371 / 0 |
| backpressure | reset | 8 |     96.01 |     30.76 |      2.20 |    128.96 | 0.593 | 5371 / 0 |
| backpressure | startup | 1040 |    105.32 |     37.48 |      2.21 |    145.01 | 0.667 | 5371 / 0 |
| backpressure | steady | 1024 |    111.84 |     41.82 |      2.21 |    155.88 | 0.717 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     96.04 |     30.82 |      2.20 |    129.06 | 0.594 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    105.49 |     37.67 |      2.21 |    145.37 | 0.669 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    111.92 |     41.94 |      2.21 |    156.07 | 0.718 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     95.76 |     30.36 |      2.20 |    128.32 | 0.590 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     98.04 |     31.39 |      2.20 |    131.63 | 0.606 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     97.94 |     31.33 |      2.20 |    131.48 | 0.605 | 5371 / 0 |
| raw-streaming | reset | 8 |     96.10 |     31.02 |      2.20 |    129.32 | 0.595 | 5371 / 0 |
| raw-streaming | startup | 1040 |    105.78 |     38.10 |      2.21 |    146.09 | 0.672 | 5371 / 0 |
| raw-streaming | steady | 1024 |    112.25 |     42.42 |      2.21 |    156.88 | 0.722 | 5371 / 0 |

- `uniform_total_w`: 2.173859e-04
- `uniform_internal_w`: 1.471249e-04
- `uniform_switching_w`: 6.805213e-05
- `uniform_leakage_w`: 2.208865e-06
- `uniform_clock_w`: 4.481290e-05
- `uniform_sequential_w`: 1.141026e-04
- `uniform_combinational_w`: 5.847025e-05
- `uniform_total_a`: 7.246197e-05
- `obs_alarm_gated_reset_total_w`: 1.290921e-04
- `obs_alarm_gated_reset_internal_w`: 9.604965e-05
- `obs_alarm_gated_reset_switching_w`: 3.084375e-05
- `obs_alarm_gated_reset_leakage_w`: 2.198723e-06
- `obs_alarm_gated_reset_clock_w`: 4.481290e-05
- `obs_alarm_gated_reset_sequential_w`: 8.028284e-05
- `obs_alarm_gated_reset_combinational_w`: 3.996428e-06
- `obs_alarm_gated_reset_total_a`: 4.303070e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.447258e-04
- `obs_alarm_gated_startup_internal_w`: 1.051569e-04
- `obs_alarm_gated_startup_switching_w`: 3.736059e-05
- `obs_alarm_gated_startup_leakage_w`: 2.208328e-06
- `obs_alarm_gated_startup_clock_w`: 4.481290e-05
- `obs_alarm_gated_startup_sequential_w`: 8.739586e-05
- `obs_alarm_gated_startup_combinational_w`: 1.251696e-05
- `obs_alarm_gated_startup_total_a`: 4.824193e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.396033e-04
- `obs_alarm_gated_steady_internal_w`: 1.023659e-04
- `obs_alarm_gated_steady_switching_w`: 3.502956e-05
- `obs_alarm_gated_steady_leakage_w`: 2.207755e-06
- `obs_alarm_gated_steady_clock_w`: 4.481290e-05
- `obs_alarm_gated_steady_sequential_w`: 8.553051e-05
- `obs_alarm_gated_steady_combinational_w`: 9.259859e-06
- `obs_alarm_gated_steady_total_a`: 4.653443e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.289649e-04
- `obs_backpressure_reset_internal_w`: 9.600911e-05
- `obs_backpressure_reset_switching_w`: 3.075709e-05
- `obs_backpressure_reset_leakage_w`: 2.198723e-06
- `obs_backpressure_reset_clock_w`: 4.481290e-05
- `obs_backpressure_reset_sequential_w`: 8.027549e-05
- `obs_backpressure_reset_combinational_w`: 3.876571e-06
- `obs_backpressure_reset_total_a`: 4.298830e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.450057e-04
- `obs_backpressure_startup_internal_w`: 1.053210e-04
- `obs_backpressure_startup_switching_w`: 3.747612e-05
- `obs_backpressure_startup_leakage_w`: 2.208553e-06
- `obs_backpressure_startup_clock_w`: 4.481290e-05
- `obs_backpressure_startup_sequential_w`: 8.742572e-05
- `obs_backpressure_startup_combinational_w`: 1.276706e-05
- `obs_backpressure_startup_total_a`: 4.833523e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.558762e-04
- `obs_backpressure_steady_internal_w`: 1.118394e-04
- `obs_backpressure_steady_switching_w`: 4.182474e-05
- `obs_backpressure_steady_leakage_w`: 2.212008e-06
- `obs_backpressure_steady_clock_w`: 4.481290e-05
- `obs_backpressure_steady_sequential_w`: 9.291930e-05
- `obs_backpressure_steady_combinational_w`: 1.814389e-05
- `obs_backpressure_steady_total_a`: 5.195873e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.290613e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.604096e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.082163e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.198723e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.481290e-05
- `obs_conditioned_streaming_reset_sequential_w`: 8.028284e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.965611e-06
- `obs_conditioned_streaming_reset_total_a`: 4.302043e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.453673e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.054910e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.766832e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.207989e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.481290e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.758136e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.297299e-05
- `obs_conditioned_streaming_startup_total_a`: 4.845577e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.560727e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.119178e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.194413e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.210763e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.481290e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.289994e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.835991e-05
- `obs_conditioned_streaming_steady_total_a`: 5.202423e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.283177e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.575966e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.035932e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.198723e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.481290e-05
- `obs_disabled_clock_running_reset_sequential_w`: 8.024807e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.256746e-06
- `obs_disabled_clock_running_reset_total_a`: 4.277257e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.316330e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.804276e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.138567e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.481290e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.149915e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.321003e-06
- `obs_disabled_clock_running_startup_total_a`: 4.387767e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.314762e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.793929e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.133226e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.481290e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.153816e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.125107e-06
- `obs_disabled_clock_running_steady_total_a`: 4.382540e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.293184e-04
- `obs_raw_streaming_reset_internal_w`: 9.609915e-05
- `obs_raw_streaming_reset_switching_w`: 3.102050e-05
- `obs_raw_streaming_reset_leakage_w`: 2.198723e-06
- `obs_raw_streaming_reset_clock_w`: 4.481290e-05
- `obs_raw_streaming_reset_sequential_w`: 8.028268e-05
- `obs_raw_streaming_reset_combinational_w`: 4.222828e-06
- `obs_raw_streaming_reset_total_a`: 4.310613e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.460884e-04
- `obs_raw_streaming_startup_internal_w`: 1.057765e-04
- `obs_raw_streaming_startup_switching_w`: 3.810396e-05
- `obs_raw_streaming_startup_leakage_w`: 2.207986e-06
- `obs_raw_streaming_startup_clock_w`: 4.481290e-05
- `obs_raw_streaming_startup_sequential_w`: 8.758232e-05
- `obs_raw_streaming_startup_combinational_w`: 1.369323e-05
- `obs_raw_streaming_startup_total_a`: 4.869613e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.568810e-04
- `obs_raw_streaming_steady_internal_w`: 1.122468e-04
- `obs_raw_streaming_steady_switching_w`: 4.242268e-05
- `obs_raw_streaming_steady_leakage_w`: 2.211509e-06
- `obs_raw_streaming_steady_clock_w`: 4.481290e-05
- `obs_raw_streaming_steady_sequential_w`: 9.292194e-05
- `obs_raw_streaming_steady_combinational_w`: 1.914622e-05
- `obs_raw_streaming_steady_total_a`: 5.229367e-05
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
