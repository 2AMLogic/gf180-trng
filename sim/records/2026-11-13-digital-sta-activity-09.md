---
record: 2026-11-13-digital-sta-activity-09
date: 2026-11-13T22:54:07Z
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
  - gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30.lib (liberty corner tt_025C_3v30, sha256:1157d0aa147dba75a214708197d7a046f970175d723cdec108025f6f06727c12)
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
  process: tt
  voltage: 3.30 V (nominal 3.3 V)
  temperature: 25
  liberty: gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30
  interconnect: max (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature 25, nom_voltage 3.3 (read from the deck)

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
  spef_sha256: ffd9a6b1e944747437ba77ef8095794c35eaef61f501bbccd849b263db78f495
  spef_bytes: 1680256
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
  path: sim/records/raw/2026-11-13-digital-sta-activity-09/
  files:
    - uniform.tcl  sha256:e2e587b51dd6cdfc0e0f5d97c364b0cb7e1ebc5132b8342eb4f4f58b62c09697
    - uniform.log  sha256:407e77cf3ab0581e374e4f9ee687a780bd7abb524b62dedad59e117fb8b18323
    - observed.tcl  sha256:f30f439255d1f42e326bdf790378e3fc8091a0adfa0c5a8927625ba25236ebed
    - observed.log  sha256:4f986e1039246dcc4e6222fb0785360bdba2c8534f239ae4514550a8fab2bc8f
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 8.7s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    172.29 |     81.98 |      0.21 |    254.48 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    115.14 |     39.26 |      0.20 |    154.60 | 0.608 | 5145 / 0 |
| alarm-gated | startup | 1040 |    127.98 |     48.09 |      0.21 |    176.28 | 0.693 | 5145 / 0 |
| alarm-gated | steady | 1024 |    124.71 |     45.55 |      0.21 |    170.48 | 0.670 | 5145 / 0 |
| backpressure | reset | 8 |    115.09 |     39.16 |      0.20 |    154.45 | 0.607 | 5145 / 0 |
| backpressure | startup | 1040 |    128.26 |     48.25 |      0.21 |    176.72 | 0.694 | 5145 / 0 |
| backpressure | steady | 1024 |    136.21 |     53.76 |      0.22 |    190.19 | 0.747 | 5145 / 0 |
| conditioned-streaming | reset | 8 |    115.13 |     39.24 |      0.20 |    154.57 | 0.607 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    128.58 |     48.51 |      0.21 |    177.31 | 0.697 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    136.36 |     53.94 |      0.21 |    190.51 | 0.749 | 5145 / 0 |
| disabled-clock-running | reset | 8 |    114.52 |     38.59 |      0.20 |    153.31 | 0.602 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |    117.45 |     40.28 |      0.21 |    157.94 | 0.621 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |    117.33 |     40.22 |      0.21 |    157.76 | 0.620 | 5145 / 0 |
| raw-streaming | reset | 8 |    115.04 |     39.39 |      0.20 |    154.63 | 0.608 | 5145 / 0 |
| raw-streaming | startup | 1040 |    128.65 |     48.96 |      0.21 |    177.83 | 0.699 | 5145 / 0 |
| raw-streaming | steady | 1024 |    136.63 |     54.51 |      0.22 |    191.36 | 0.752 | 5145 / 0 |

- `uniform_total_w`: 2.544791e-04
- `uniform_internal_w`: 1.722883e-04
- `uniform_switching_w`: 8.197631e-05
- `uniform_leakage_w`: 2.144338e-07
- `uniform_clock_w`: 5.660201e-05
- `uniform_sequential_w`: 1.317132e-04
- `uniform_combinational_w`: 6.616378e-05
- `uniform_total_a`: 7.711488e-05
- `obs_alarm_gated_reset_total_w`: 1.546043e-04
- `obs_alarm_gated_reset_internal_w`: 1.151409e-04
- `obs_alarm_gated_reset_switching_w`: 3.926024e-05
- `obs_alarm_gated_reset_leakage_w`: 2.031384e-07
- `obs_alarm_gated_reset_clock_w`: 5.660201e-05
- `obs_alarm_gated_reset_sequential_w`: 9.404813e-05
- `obs_alarm_gated_reset_combinational_w`: 3.954135e-06
- `obs_alarm_gated_reset_total_a`: 4.684979e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.762760e-04
- `obs_alarm_gated_startup_internal_w`: 1.279773e-04
- `obs_alarm_gated_startup_switching_w`: 4.808748e-05
- `obs_alarm_gated_startup_leakage_w`: 2.111742e-07
- `obs_alarm_gated_startup_clock_w`: 5.660201e-05
- `obs_alarm_gated_startup_sequential_w`: 1.036819e-04
- `obs_alarm_gated_startup_combinational_w`: 1.599201e-05
- `obs_alarm_gated_startup_total_a`: 5.341697e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.704773e-04
- `obs_alarm_gated_steady_internal_w`: 1.247149e-04
- `obs_alarm_gated_steady_switching_w`: 4.555162e-05
- `obs_alarm_gated_steady_leakage_w`: 2.108011e-07
- `obs_alarm_gated_steady_clock_w`: 5.660201e-05
- `obs_alarm_gated_steady_sequential_w`: 1.018517e-04
- `obs_alarm_gated_steady_combinational_w`: 1.202362e-05
- `obs_alarm_gated_steady_total_a`: 5.165979e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.544514e-04
- `obs_backpressure_reset_internal_w`: 1.150915e-04
- `obs_backpressure_reset_switching_w`: 3.915665e-05
- `obs_backpressure_reset_leakage_w`: 2.031384e-07
- `obs_backpressure_reset_clock_w`: 5.660201e-05
- `obs_backpressure_reset_sequential_w`: 9.403947e-05
- `obs_backpressure_reset_combinational_w`: 3.809842e-06
- `obs_backpressure_reset_total_a`: 4.680345e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.767222e-04
- `obs_backpressure_startup_internal_w`: 1.282575e-04
- `obs_backpressure_startup_switching_w`: 4.825316e-05
- `obs_backpressure_startup_leakage_w`: 2.114715e-07
- `obs_backpressure_startup_clock_w`: 5.660201e-05
- `obs_backpressure_startup_sequential_w`: 1.037925e-04
- `obs_backpressure_startup_combinational_w`: 1.632765e-05
- `obs_backpressure_startup_total_a`: 5.355218e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.901850e-04
- `obs_backpressure_steady_internal_w`: 1.362067e-04
- `obs_backpressure_steady_switching_w`: 5.376233e-05
- `obs_backpressure_steady_leakage_w`: 2.159677e-07
- `obs_backpressure_steady_clock_w`: 5.660201e-05
- `obs_backpressure_steady_sequential_w`: 1.106736e-04
- `obs_backpressure_steady_combinational_w`: 2.290919e-05
- `obs_backpressure_steady_total_a`: 5.763182e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.545706e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.151295e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.923793e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.031384e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.660201e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.404813e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.920395e-06
- `obs_conditioned_streaming_reset_total_a`: 4.683958e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.773070e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.285846e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.851168e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.108036e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.660201e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.040556e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.664930e-05
- `obs_conditioned_streaming_startup_total_a`: 5.372939e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.905108e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.363559e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.394016e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.147684e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.660201e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.107085e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.320025e-05
- `obs_conditioned_streaming_steady_total_a`: 5.773055e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.533121e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.145157e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.859328e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.031384e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.660201e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.400359e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.706502e-06
- `obs_disabled_clock_running_reset_total_a`: 4.645821e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.579371e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.174520e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.027862e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.065109e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.660201e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.553801e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.797060e-06
- `obs_disabled_clock_running_startup_total_a`: 4.785973e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.577586e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.173304e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.022173e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.065113e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.660201e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.558586e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.570711e-06
- `obs_disabled_clock_running_steady_total_a`: 4.780564e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.546273e-04
- `obs_raw_streaming_reset_internal_w`: 1.150351e-04
- `obs_raw_streaming_reset_switching_w`: 3.938897e-05
- `obs_raw_streaming_reset_leakage_w`: 2.031384e-07
- `obs_raw_streaming_reset_clock_w`: 5.660201e-05
- `obs_raw_streaming_reset_sequential_w`: 9.404527e-05
- `obs_raw_streaming_reset_combinational_w`: 3.979946e-06
- `obs_raw_streaming_reset_total_a`: 4.685676e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.778273e-04
- `obs_raw_streaming_startup_internal_w`: 1.286521e-04
- `obs_raw_streaming_startup_switching_w`: 4.896429e-05
- `obs_raw_streaming_startup_leakage_w`: 2.109694e-07
- `obs_raw_streaming_startup_clock_w`: 5.660201e-05
- `obs_raw_streaming_startup_sequential_w`: 1.038442e-04
- `obs_raw_streaming_startup_combinational_w`: 1.738120e-05
- `obs_raw_streaming_startup_total_a`: 5.388706e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.913615e-04
- `obs_raw_streaming_steady_internal_w`: 1.366329e-04
- `obs_raw_streaming_steady_switching_w`: 5.451276e-05
- `obs_raw_streaming_steady_leakage_w`: 2.157574e-07
- `obs_raw_streaming_steady_clock_w`: 5.660201e-05
- `obs_raw_streaming_steady_sequential_w`: 1.106616e-04
- `obs_raw_streaming_steady_combinational_w`: 2.409775e-05
- `obs_raw_streaming_steady_total_a`: 5.798833e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty tt_025C_3v30 --rc max --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (tt_025C_3v30, interconnect `max`).
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
