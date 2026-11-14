---
record: 2026-11-13-digital-sta-activity-05
date: 2026-11-13T22:53:32Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: 89e8f60a83222b44213d3c89a059db389405b475
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha 49a084e95789ff1acbd953235cf0612b7701ef36).
repo_commit: e783bb4f7336f4422aa26902c7003f638bccd0a7-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - gf180mcu_fd_sc_mcu9t5v0__ss_n40C_3v00.lib (liberty corner ss_n40C_3v00, sha256:03238cd7c39382b10bd1ff526c37c9ac3c73cc92c01cd2c249cb86978bda9de3)
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
  temperature: -40
  liberty: gf180mcu_fd_sc_mcu9t5v0__ss_n40C_3v00
  interconnect: nom (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature -40, nom_voltage 3 (read from the deck)

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
  spef_sha256: dba01d1a3ffaf2e1a57d9f07ab9fd2c3152821ec11516df8984fe66776a699ef
  spef_bytes: 1671005
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
      vcd_sha256: 0afb5fb92799a03d3444e0f27eb960c2ee5ea62fff79b5a3a5094558e2df1b4b
      vcd_bytes: 17698640
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1424/1424
      xz_events: 4931
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: a4094cb39c49b436bd01e672cded18bb2da8efe3791a0abfc0fe57e9ea40ebe6
      vcd_bytes: 19126901
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 5074
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: a0eb1a5723562558fb1acfcf8d8c0701c6e1cfe4e7270ce8aebbb72dd962965d
      vcd_bytes: 19173873
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 4809
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: ea20e05c09b17231d8eeee57c82747b30afe2abf409e7db8ff7f17a08e0cabfc
      vcd_bytes: 13485290
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 2222
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: 700215612e809607908e9865420a657acd559ed311b8ef2c862483deac89df1b
      vcd_bytes: 19322913
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 5153
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-11-13-digital-sta-activity-05/
  files:
    - uniform.tcl  sha256:89e7add9d544454c77ed5fbb6fb54661551eb4e1d92be9695a3753ff8ec202a0
    - uniform.log  sha256:0d2e6aeedb1601e0519fe0d211f1f0f2b36128ad14b2cc078ef351aef62da3da
    - observed.tcl  sha256:672221ba451e660eef688db96d8b9b4033874a5a12f91e997188f03fbfe5c5dc
    - observed.log  sha256:f10829782552652a29339dbd423bcb341d6d72bb92336254ce2939a17a3579c9
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 8.9s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    132.80 |     64.20 |      0.17 |    197.17 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     90.08 |     30.79 |      0.16 |    121.04 | 0.614 | 5145 / 0 |
| alarm-gated | startup | 1040 |     99.71 |     37.74 |      0.17 |    137.62 | 0.698 | 5145 / 0 |
| alarm-gated | steady | 1024 |     97.29 |     35.72 |      0.17 |    133.18 | 0.675 | 5145 / 0 |
| backpressure | reset | 8 |     90.05 |     30.71 |      0.16 |    120.92 | 0.613 | 5145 / 0 |
| backpressure | startup | 1040 |     99.92 |     37.87 |      0.17 |    137.96 | 0.700 | 5145 / 0 |
| backpressure | steady | 1024 |    105.90 |     42.19 |      0.17 |    148.26 | 0.752 | 5145 / 0 |
| conditioned-streaming | reset | 8 |     90.08 |     30.77 |      0.16 |    121.01 | 0.614 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    100.17 |     38.07 |      0.17 |    138.41 | 0.702 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    106.01 |     42.33 |      0.17 |    148.51 | 0.753 | 5145 / 0 |
| disabled-clock-running | reset | 8 |     89.63 |     30.27 |      0.16 |    120.06 | 0.609 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |     91.77 |     31.60 |      0.16 |    123.53 | 0.627 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |     91.67 |     31.56 |      0.16 |    123.39 | 0.626 | 5145 / 0 |
| raw-streaming | reset | 8 |     90.01 |     30.89 |      0.16 |    121.06 | 0.614 | 5145 / 0 |
| raw-streaming | startup | 1040 |    100.21 |     38.42 |      0.17 |    138.80 | 0.704 | 5145 / 0 |
| raw-streaming | steady | 1024 |    106.21 |     42.78 |      0.17 |    149.16 | 0.756 | 5145 / 0 |

- `uniform_total_w`: 1.971711e-04
- `uniform_internal_w`: 1.328024e-04
- `uniform_switching_w`: 6.420044e-05
- `uniform_leakage_w`: 1.682266e-07
- `uniform_clock_w`: 4.247424e-05
- `uniform_sequential_w`: 1.046108e-04
- `uniform_combinational_w`: 5.008577e-05
- `uniform_total_a`: 6.572370e-05
- `obs_alarm_gated_reset_total_w`: 1.210378e-04
- `obs_alarm_gated_reset_internal_w`: 9.008370e-05
- `obs_alarm_gated_reset_switching_w`: 3.079151e-05
- `obs_alarm_gated_reset_leakage_w`: 1.625760e-07
- `obs_alarm_gated_reset_clock_w`: 4.247424e-05
- `obs_alarm_gated_reset_sequential_w`: 7.548868e-05
- `obs_alarm_gated_reset_combinational_w`: 3.074806e-06
- `obs_alarm_gated_reset_total_a`: 4.034593e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.376176e-04
- `obs_alarm_gated_startup_internal_w`: 9.971071e-05
- `obs_alarm_gated_startup_switching_w`: 3.773973e-05
- `obs_alarm_gated_startup_leakage_w`: 1.671869e-07
- `obs_alarm_gated_startup_clock_w`: 4.247424e-05
- `obs_alarm_gated_startup_sequential_w`: 8.297918e-05
- `obs_alarm_gated_startup_combinational_w`: 1.216417e-05
- `obs_alarm_gated_startup_total_a`: 4.587253e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.331766e-04
- `obs_alarm_gated_steady_internal_w`: 9.728569e-05
- `obs_alarm_gated_steady_switching_w`: 3.572407e-05
- `obs_alarm_gated_steady_leakage_w`: 1.668848e-07
- `obs_alarm_gated_steady_clock_w`: 4.247424e-05
- `obs_alarm_gated_steady_sequential_w`: 8.155434e-05
- `obs_alarm_gated_steady_combinational_w`: 9.148081e-06
- `obs_alarm_gated_steady_total_a`: 4.439220e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.209169e-04
- `obs_backpressure_reset_internal_w`: 9.004547e-05
- `obs_backpressure_reset_switching_w`: 3.070885e-05
- `obs_backpressure_reset_leakage_w`: 1.625760e-07
- `obs_backpressure_reset_clock_w`: 4.247424e-05
- `obs_backpressure_reset_sequential_w`: 7.548177e-05
- `obs_backpressure_reset_combinational_w`: 2.960819e-06
- `obs_backpressure_reset_total_a`: 4.030563e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.379581e-04
- `obs_backpressure_startup_internal_w`: 9.992110e-05
- `obs_backpressure_startup_switching_w`: 3.786969e-05
- `obs_backpressure_startup_leakage_w`: 1.673350e-07
- `obs_backpressure_startup_clock_w`: 4.247424e-05
- `obs_backpressure_startup_sequential_w`: 8.306334e-05
- `obs_backpressure_startup_combinational_w`: 1.242045e-05
- `obs_backpressure_startup_total_a`: 4.598603e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.482581e-04
- `obs_backpressure_steady_internal_w`: 1.058952e-04
- `obs_backpressure_steady_switching_w`: 4.219339e-05
- `obs_backpressure_steady_leakage_w`: 1.694936e-07
- `obs_backpressure_steady_clock_w`: 4.247424e-05
- `obs_backpressure_steady_sequential_w`: 8.836600e-05
- `obs_backpressure_steady_combinational_w`: 1.741788e-05
- `obs_backpressure_steady_total_a`: 4.941937e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.210111e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.007518e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.077338e-05
- `obs_conditioned_streaming_reset_leakage_w`: 1.625760e-07
- `obs_conditioned_streaming_reset_clock_w`: 4.247424e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.548868e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.048152e-06
- `obs_conditioned_streaming_reset_total_a`: 4.033703e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.384099e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.001705e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.807238e-05
- `obs_conditioned_streaming_startup_leakage_w`: 1.670489e-07
- `obs_conditioned_streaming_startup_clock_w`: 4.247424e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.327131e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.266433e-05
- `obs_conditioned_streaming_startup_total_a`: 4.613663e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.485090e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.060086e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.233166e-05
- `obs_conditioned_streaming_steady_leakage_w`: 1.688380e-07
- `obs_conditioned_streaming_steady_clock_w`: 4.247424e-05
- `obs_conditioned_streaming_steady_sequential_w`: 8.839642e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.763841e-05
- `obs_conditioned_streaming_steady_total_a`: 4.950300e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.200588e-04
- `obs_disabled_clock_running_reset_internal_w`: 8.962888e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.026739e-05
- `obs_disabled_clock_running_reset_leakage_w`: 1.625760e-07
- `obs_disabled_clock_running_reset_clock_w`: 4.247424e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.545423e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.130320e-06
- `obs_disabled_clock_running_reset_total_a`: 4.001960e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.235300e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.176524e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.159996e-05
- `obs_disabled_clock_running_startup_leakage_w`: 1.647496e-07
- `obs_disabled_clock_running_startup_clock_w`: 4.247424e-05
- `obs_disabled_clock_running_startup_sequential_w`: 7.664818e-05
- `obs_disabled_clock_running_startup_combinational_w`: 4.407422e-06
- `obs_disabled_clock_running_startup_total_a`: 4.117667e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.233944e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.167408e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.155560e-05
- `obs_disabled_clock_running_steady_leakage_w`: 1.647490e-07
- `obs_disabled_clock_running_steady_clock_w`: 4.247424e-05
- `obs_disabled_clock_running_steady_sequential_w`: 7.668639e-05
- `obs_disabled_clock_running_steady_combinational_w`: 4.233720e-06
- `obs_disabled_clock_running_steady_total_a`: 4.113147e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.210605e-04
- `obs_raw_streaming_reset_internal_w`: 9.000730e-05
- `obs_raw_streaming_reset_switching_w`: 3.089065e-05
- `obs_raw_streaming_reset_leakage_w`: 1.625760e-07
- `obs_raw_streaming_reset_clock_w`: 4.247424e-05
- `obs_raw_streaming_reset_sequential_w`: 7.548669e-05
- `obs_raw_streaming_reset_combinational_w`: 3.099567e-06
- `obs_raw_streaming_reset_total_a`: 4.035350e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.388001e-04
- `obs_raw_streaming_startup_internal_w`: 1.002113e-04
- `obs_raw_streaming_startup_switching_w`: 3.842173e-05
- `obs_raw_streaming_startup_leakage_w`: 1.670639e-07
- `obs_raw_streaming_startup_clock_w`: 4.247424e-05
- `obs_raw_streaming_startup_sequential_w`: 8.310596e-05
- `obs_raw_streaming_startup_combinational_w`: 1.321991e-05
- `obs_raw_streaming_startup_total_a`: 4.626670e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.491585e-04
- `obs_raw_streaming_steady_internal_w`: 1.062118e-04
- `obs_raw_streaming_steady_switching_w`: 4.277722e-05
- `obs_raw_streaming_steady_leakage_w`: 1.693965e-07
- `obs_raw_streaming_steady_clock_w`: 4.247424e-05
- `obs_raw_streaming_steady_sequential_w`: 8.835879e-05
- `obs_raw_streaming_steady_combinational_w`: 1.832542e-05
- `obs_raw_streaming_steady_total_a`: 4.971950e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_n40C_3v00 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_n40C_3v00, interconnect `nom`).
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
