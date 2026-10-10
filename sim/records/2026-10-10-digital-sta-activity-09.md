---
record: 2026-10-10-digital-sta-activity-09
date: 2026-10-10T02:45:52Z
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
  spef_sha256: 74e255c9e919ebb1467ccef54f7860b209ec77784729455d9dd0386db1f992a3
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-09/
  files:
    - uniform.tcl  sha256:03bd7c9b031ceabfb5f2fb38c838b6e0f92c8a38dc8eed1777cfee3c4d2e9c3c
    - uniform.log  sha256:b906c18ee02bc24c53ce328bf5a90211554999cc3723c9808df353a15c202e25
    - observed.tcl  sha256:3a050861cb1fc12ddc028e8b2cef0aab58e8eba5589ddc3c332af83e0ff3ebdf
    - observed.log  sha256:0be3a19eb96f3b6ff4e02e62abbdb8d780b119c46d8fe3267c1e73de0553e299
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 9.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    177.13 |     84.92 |      0.22 |    262.28 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    115.21 |     38.48 |      0.21 |    153.90 | 0.587 | 5371 / 0 |
| alarm-gated | startup | 1040 |    126.21 |     46.53 |      0.22 |    172.96 | 0.659 | 5371 / 0 |
| alarm-gated | steady | 1024 |    122.82 |     43.66 |      0.22 |    166.70 | 0.636 | 5371 / 0 |
| backpressure | reset | 8 |    115.16 |     38.37 |      0.21 |    153.74 | 0.586 | 5371 / 0 |
| backpressure | startup | 1040 |    126.41 |     46.67 |      0.22 |    173.30 | 0.661 | 5371 / 0 |
| backpressure | steady | 1024 |    134.29 |     52.08 |      0.22 |    186.59 | 0.711 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    115.20 |     38.45 |      0.21 |    153.86 | 0.587 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    126.62 |     46.91 |      0.22 |    173.74 | 0.662 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    134.39 |     52.23 |      0.22 |    186.84 | 0.712 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    114.85 |     37.87 |      0.21 |    152.93 | 0.583 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    117.64 |     39.11 |      0.21 |    156.96 | 0.598 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    117.51 |     39.05 |      0.21 |    156.77 | 0.598 | 5371 / 0 |
| raw-streaming | reset | 8 |    115.27 |     38.70 |      0.21 |    154.18 | 0.588 | 5371 / 0 |
| raw-streaming | startup | 1040 |    126.97 |     47.47 |      0.22 |    174.65 | 0.666 | 5371 / 0 |
| raw-streaming | steady | 1024 |    134.79 |     52.84 |      0.22 |    187.85 | 0.716 | 5371 / 0 |

- `uniform_total_w`: 2.622755e-04
- `uniform_internal_w`: 1.771346e-04
- `uniform_switching_w`: 8.492156e-05
- `uniform_leakage_w`: 2.193580e-07
- `uniform_clock_w`: 5.449667e-05
- `uniform_sequential_w`: 1.359984e-04
- `uniform_combinational_w`: 7.178068e-05
- `uniform_total_a`: 7.947742e-05
- `obs_alarm_gated_reset_total_w`: 1.538965e-04
- `obs_alarm_gated_reset_internal_w`: 1.152113e-04
- `obs_alarm_gated_reset_switching_w`: 3.847774e-05
- `obs_alarm_gated_reset_leakage_w`: 2.075095e-07
- `obs_alarm_gated_reset_clock_w`: 5.449667e-05
- `obs_alarm_gated_reset_sequential_w`: 9.504814e-05
- `obs_alarm_gated_reset_combinational_w`: 4.351721e-06
- `obs_alarm_gated_reset_total_a`: 4.663530e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.729583e-04
- `obs_alarm_gated_startup_internal_w`: 1.262123e-04
- `obs_alarm_gated_startup_switching_w`: 4.652945e-05
- `obs_alarm_gated_startup_leakage_w`: 2.165480e-07
- `obs_alarm_gated_startup_clock_w`: 5.449667e-05
- `obs_alarm_gated_startup_sequential_w`: 1.037028e-04
- `obs_alarm_gated_startup_combinational_w`: 1.475881e-05
- `obs_alarm_gated_startup_total_a`: 5.241161e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.666958e-04
- `obs_alarm_gated_steady_internal_w`: 1.228249e-04
- `obs_alarm_gated_steady_switching_w`: 4.365501e-05
- `obs_alarm_gated_steady_leakage_w`: 2.159064e-07
- `obs_alarm_gated_steady_clock_w`: 5.449667e-05
- `obs_alarm_gated_steady_sequential_w`: 1.014381e-04
- `obs_alarm_gated_steady_combinational_w`: 1.076092e-05
- `obs_alarm_gated_steady_total_a`: 5.051388e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.537392e-04
- `obs_backpressure_reset_internal_w`: 1.151618e-04
- `obs_backpressure_reset_switching_w`: 3.836991e-05
- `obs_backpressure_reset_leakage_w`: 2.075095e-07
- `obs_backpressure_reset_clock_w`: 5.449667e-05
- `obs_backpressure_reset_sequential_w`: 9.503948e-05
- `obs_backpressure_reset_combinational_w`: 4.203064e-06
- `obs_backpressure_reset_total_a`: 4.658764e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.732984e-04
- `obs_backpressure_startup_internal_w`: 1.264095e-04
- `obs_backpressure_startup_switching_w`: 4.667203e-05
- `obs_backpressure_startup_leakage_w`: 2.168396e-07
- `obs_backpressure_startup_clock_w`: 5.449667e-05
- `obs_backpressure_startup_sequential_w`: 1.037373e-04
- `obs_backpressure_startup_combinational_w`: 1.506437e-05
- `obs_backpressure_startup_total_a`: 5.251467e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.865939e-04
- `obs_backpressure_steady_internal_w`: 1.342909e-04
- `obs_backpressure_steady_switching_w`: 5.208163e-05
- `obs_backpressure_steady_leakage_w`: 2.213108e-07
- `obs_backpressure_steady_clock_w`: 5.449667e-05
- `obs_backpressure_steady_sequential_w`: 1.104168e-04
- `obs_backpressure_steady_combinational_w`: 2.168041e-05
- `obs_backpressure_steady_total_a`: 5.654361e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.538582e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.151999e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.845089e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.075095e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.449667e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.504813e-05
- `obs_conditioned_streaming_reset_combinational_w`: 4.313458e-06
- `obs_conditioned_streaming_reset_total_a`: 4.662370e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.737436e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.266163e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.691108e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.161481e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.449667e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.039283e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.531856e-05
- `obs_conditioned_streaming_startup_total_a`: 5.264958e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.868380e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.343873e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.223045e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.201589e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.449667e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.103948e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.194651e-05
- `obs_conditioned_streaming_steady_total_a`: 5.661758e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.529297e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.148504e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.787181e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.075095e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.449667e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.500667e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.426414e-06
- `obs_disabled_clock_running_reset_total_a`: 4.634233e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.569611e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.176358e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.911382e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.114828e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.449667e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.653629e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.928124e-06
- `obs_disabled_clock_running_startup_total_a`: 4.756397e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.567707e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.175123e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.904694e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.114832e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.449667e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.658404e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.690072e-06
- `obs_disabled_clock_running_steady_total_a`: 4.750627e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.541779e-04
- `obs_raw_streaming_reset_internal_w`: 1.152723e-04
- `obs_raw_streaming_reset_switching_w`: 3.869813e-05
- `obs_raw_streaming_reset_leakage_w`: 2.075095e-07
- `obs_raw_streaming_reset_clock_w`: 5.449667e-05
- `obs_raw_streaming_reset_sequential_w`: 9.504780e-05
- `obs_raw_streaming_reset_combinational_w`: 4.633490e-06
- `obs_raw_streaming_reset_total_a`: 4.672058e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.746528e-04
- `obs_raw_streaming_startup_internal_w`: 1.269688e-04
- `obs_raw_streaming_startup_switching_w`: 4.746770e-05
- `obs_raw_streaming_startup_leakage_w`: 2.163030e-07
- `obs_raw_streaming_startup_clock_w`: 5.449667e-05
- `obs_raw_streaming_startup_sequential_w`: 1.039283e-04
- `obs_raw_streaming_startup_combinational_w`: 1.622767e-05
- `obs_raw_streaming_startup_total_a`: 5.292509e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.878482e-04
- `obs_raw_streaming_steady_internal_w`: 1.347890e-04
- `obs_raw_streaming_steady_switching_w`: 5.283820e-05
- `obs_raw_streaming_steady_leakage_w`: 2.210452e-07
- `obs_raw_streaming_steady_clock_w`: 5.449667e-05
- `obs_raw_streaming_steady_sequential_w`: 1.104205e-04
- `obs_raw_streaming_steady_combinational_w`: 2.293107e-05
- `obs_raw_streaming_steady_total_a`: 5.692370e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
