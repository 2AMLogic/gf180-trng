---
record: 2026-10-10-digital-sta-activity-04
date: 2026-10-10T02:45:04Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ss_n40C_3v00.lib (liberty corner ss_n40C_3v00, sha256:03238cd7c39382b10bd1ff526c37c9ac3c73cc92c01cd2c249cb86978bda9de3)
  - gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:80bf186e7fcc2c4b1bae9b8ee0e67100acf4f643e71a58daadc3f354f0836508)
  - gf180mcu_fd_sc_mcu9t5v0.lef (cell LEF, sha256:38afbef95529165e1d8999d5b5613c4aec9869df8c1ce6b5555e74586ba4c826)
  - rules.openrcx.gf180mcuD.min (OpenRCX interconnect corner min, sha256:5cf275c985ffd49096407d22891910fea34aff5a915db8a5b9a7c1e04b737e00)
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
  interconnect: min (OpenRCX rule deck)
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
  spef_sha256: 560eda88c54b837731c7bd03fe2cc10eb9658bfd83a986d206a35623c11b6643
  spef_bytes: 1766985
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-04/
  files:
    - uniform.tcl  sha256:4e863a1a53d8670d9cf3f980e061fedc7d156afd631c3437773c7dfe79bbbe8a
    - uniform.log  sha256:92e79f844eb19bbe63e2f1bc86db416533cf4bccfb4277f06ec0f9e0b434a829
    - observed.tcl  sha256:a90b6e4b98143bbd0c43fd640b2dcab25434fd785ab16cc09466ed0ebe2f82e5
    - observed.log  sha256:3c9ba676b5b5e78234f619b2f5fd0d7c10d8b2aaa38603bebab5a28d4439bb87
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 9.4s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    136.56 |     64.14 |      0.17 |    200.88 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     90.38 |     29.16 |      0.17 |    119.71 | 0.596 | 5371 / 0 |
| alarm-gated | startup | 1040 |     98.58 |     35.31 |      0.17 |    134.06 | 0.667 | 5371 / 0 |
| alarm-gated | steady | 1024 |     96.08 |     33.10 |      0.17 |    129.35 | 0.644 | 5371 / 0 |
| backpressure | reset | 8 |     90.34 |     29.07 |      0.17 |    119.59 | 0.595 | 5371 / 0 |
| backpressure | startup | 1040 |     98.73 |     35.41 |      0.17 |    134.32 | 0.669 | 5371 / 0 |
| backpressure | steady | 1024 |    104.65 |     39.51 |      0.17 |    144.33 | 0.719 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     90.37 |     29.13 |      0.17 |    119.68 | 0.596 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |     98.89 |     35.60 |      0.17 |    134.65 | 0.670 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    104.72 |     39.62 |      0.17 |    144.52 | 0.719 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     90.12 |     28.70 |      0.17 |    118.99 | 0.592 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     92.14 |     29.67 |      0.17 |    121.97 | 0.607 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     92.04 |     29.62 |      0.17 |    121.83 | 0.607 | 5371 / 0 |
| raw-streaming | reset | 8 |     90.42 |     29.32 |      0.17 |    119.91 | 0.597 | 5371 / 0 |
| raw-streaming | startup | 1040 |     99.14 |     36.00 |      0.17 |    135.31 | 0.674 | 5371 / 0 |
| raw-streaming | steady | 1024 |    105.01 |     40.07 |      0.17 |    145.26 | 0.723 | 5371 / 0 |

- `uniform_total_w`: 2.008763e-04
- `uniform_internal_w`: 1.365632e-04
- `uniform_switching_w`: 6.414013e-05
- `uniform_leakage_w`: 1.730075e-07
- `uniform_clock_w`: 4.004922e-05
- `uniform_sequential_w`: 1.077431e-04
- `uniform_combinational_w`: 5.308419e-05
- `uniform_total_a`: 6.695877e-05
- `obs_alarm_gated_reset_total_w`: 1.197060e-04
- `obs_alarm_gated_reset_internal_w`: 9.038342e-05
- `obs_alarm_gated_reset_switching_w`: 2.915570e-05
- `obs_alarm_gated_reset_leakage_w`: 1.668595e-07
- `obs_alarm_gated_reset_clock_w`: 4.004922e-05
- `obs_alarm_gated_reset_sequential_w`: 7.633927e-05
- `obs_alarm_gated_reset_combinational_w`: 3.317649e-06
- `obs_alarm_gated_reset_total_a`: 3.990200e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.340613e-04
- `obs_alarm_gated_startup_internal_w`: 9.858321e-05
- `obs_alarm_gated_startup_switching_w`: 3.530583e-05
- `obs_alarm_gated_startup_leakage_w`: 1.722517e-07
- `obs_alarm_gated_startup_clock_w`: 4.004922e-05
- `obs_alarm_gated_startup_sequential_w`: 8.298500e-05
- `obs_alarm_gated_startup_combinational_w`: 1.102717e-05
- `obs_alarm_gated_startup_total_a`: 4.468710e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.293484e-04
- `obs_alarm_gated_steady_internal_w`: 9.607766e-05
- `obs_alarm_gated_steady_switching_w`: 3.309895e-05
- `obs_alarm_gated_steady_leakage_w`: 1.717606e-07
- `obs_alarm_gated_steady_clock_w`: 4.004922e-05
- `obs_alarm_gated_steady_sequential_w`: 8.124194e-05
- `obs_alarm_gated_steady_combinational_w`: 8.057366e-06
- `obs_alarm_gated_steady_total_a`: 4.311613e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.195862e-04
- `obs_backpressure_reset_internal_w`: 9.034482e-05
- `obs_backpressure_reset_switching_w`: 2.907449e-05
- `obs_backpressure_reset_leakage_w`: 1.668595e-07
- `obs_backpressure_reset_clock_w`: 4.004922e-05
- `obs_backpressure_reset_sequential_w`: 7.633236e-05
- `obs_backpressure_reset_combinational_w`: 3.204750e-06
- `obs_backpressure_reset_total_a`: 3.986207e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.343167e-04
- `obs_backpressure_startup_internal_w`: 9.872938e-05
- `obs_backpressure_startup_switching_w`: 3.541489e-05
- `obs_backpressure_startup_leakage_w`: 1.723908e-07
- `obs_backpressure_startup_clock_w`: 4.004922e-05
- `obs_backpressure_startup_sequential_w`: 8.301086e-05
- `obs_backpressure_startup_combinational_w`: 1.125666e-05
- `obs_backpressure_startup_total_a`: 4.477223e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.443336e-04
- `obs_backpressure_steady_internal_w`: 1.046488e-04
- `obs_backpressure_steady_switching_w`: 3.951031e-05
- `obs_backpressure_steady_leakage_w`: 1.745426e-07
- `obs_backpressure_steady_clock_w`: 4.004922e-05
- `obs_backpressure_steady_sequential_w`: 8.810576e-05
- `obs_backpressure_steady_combinational_w`: 1.617862e-05
- `obs_backpressure_steady_total_a`: 4.811120e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.196764e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.037491e-05
- `obs_conditioned_streaming_reset_switching_w`: 2.913460e-05
- `obs_conditioned_streaming_reset_leakage_w`: 1.668595e-07
- `obs_conditioned_streaming_reset_clock_w`: 4.004922e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.633927e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.288038e-06
- `obs_conditioned_streaming_reset_total_a`: 3.989213e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.346543e-04
- `obs_conditioned_streaming_startup_internal_w`: 9.888608e-05
- `obs_conditioned_streaming_startup_switching_w`: 3.559609e-05
- `obs_conditioned_streaming_startup_leakage_w`: 1.720867e-07
- `obs_conditioned_streaming_startup_clock_w`: 4.004922e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.316043e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.144471e-05
- `obs_conditioned_streaming_startup_total_a`: 4.488477e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.445173e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.047208e-04
- `obs_conditioned_streaming_steady_switching_w`: 3.962258e-05
- `obs_conditioned_streaming_steady_leakage_w`: 1.739097e-07
- `obs_conditioned_streaming_steady_clock_w`: 4.004922e-05
- `obs_conditioned_streaming_steady_sequential_w`: 8.809245e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.637563e-05
- `obs_conditioned_streaming_steady_total_a`: 4.817243e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.189865e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.011834e-05
- `obs_disabled_clock_running_reset_switching_w`: 2.870129e-05
- `obs_disabled_clock_running_reset_leakage_w`: 1.668595e-07
- `obs_disabled_clock_running_reset_clock_w`: 4.004922e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.630690e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.630510e-06
- `obs_disabled_clock_running_reset_total_a`: 3.966217e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.219740e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.213718e-05
- `obs_disabled_clock_running_startup_switching_w`: 2.966741e-05
- `obs_disabled_clock_running_startup_leakage_w`: 1.694443e-07
- `obs_disabled_clock_running_startup_clock_w`: 4.004922e-05
- `obs_disabled_clock_running_startup_sequential_w`: 7.748168e-05
- `obs_disabled_clock_running_startup_combinational_w`: 4.443284e-06
- `obs_disabled_clock_running_startup_total_a`: 4.065800e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.218316e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.204475e-05
- `obs_disabled_clock_running_steady_switching_w`: 2.961745e-05
- `obs_disabled_clock_running_steady_leakage_w`: 1.694437e-07
- `obs_disabled_clock_running_steady_clock_w`: 4.004922e-05
- `obs_disabled_clock_running_steady_sequential_w`: 7.751903e-05
- `obs_disabled_clock_running_steady_combinational_w`: 4.263561e-06
- `obs_disabled_clock_running_steady_total_a`: 4.061053e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.199122e-04
- `obs_raw_streaming_reset_internal_w`: 9.042382e-05
- `obs_raw_streaming_reset_switching_w`: 2.932148e-05
- `obs_raw_streaming_reset_leakage_w`: 1.668595e-07
- `obs_raw_streaming_reset_clock_w`: 4.004922e-05
- `obs_raw_streaming_reset_sequential_w`: 7.633925e-05
- `obs_raw_streaming_reset_combinational_w`: 3.523848e-06
- `obs_raw_streaming_reset_total_a`: 3.997073e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.353100e-04
- `obs_raw_streaming_startup_internal_w`: 9.913670e-05
- `obs_raw_streaming_startup_switching_w`: 3.600123e-05
- `obs_raw_streaming_startup_leakage_w`: 1.720917e-07
- `obs_raw_streaming_startup_clock_w`: 4.004922e-05
- `obs_raw_streaming_startup_sequential_w`: 8.315943e-05
- `obs_raw_streaming_startup_combinational_w`: 1.210137e-05
- `obs_raw_streaming_startup_total_a`: 4.510333e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.452551e-04
- `obs_raw_streaming_steady_internal_w`: 1.050120e-04
- `obs_raw_streaming_steady_switching_w`: 4.006877e-05
- `obs_raw_streaming_steady_leakage_w`: 1.743987e-07
- `obs_raw_streaming_steady_clock_w`: 4.004922e-05
- `obs_raw_streaming_steady_sequential_w`: 8.811049e-05
- `obs_raw_streaming_steady_combinational_w`: 1.709539e-05
- `obs_raw_streaming_steady_total_a`: 4.841837e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_n40C_3v00 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_n40C_3v00, interconnect `min`).
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
