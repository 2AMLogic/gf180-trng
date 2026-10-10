---
record: 2026-10-10-digital-sta-activity-25
date: 2026-10-10T07:12:46Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60.lib (liberty corner ff_125C_3v60, sha256:0354585714f92d093efa6cb0263b7305d8b8cee18ad802eb4e5a8d131241cb9c)
  - gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:332ae93d61ac55f793da97a6391703f78bc415653cb60e76dd8eb0092124485a)
  - gf180mcu_fd_sc_mcu9t5v0.lef (cell LEF, sha256:38afbef95529165e1d8999d5b5613c4aec9869df8c1ce6b5555e74586ba4c826)
  - rules.openrcx.gf180mcuD.min (OpenRCX interconnect corner min, sha256:5cf275c985ffd49096407d22891910fea34aff5a915db8a5b9a7c1e04b737e00)
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
  interconnect: min (OpenRCX rule deck)
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
  spef_sha256: cd86e63b8f966ec7f57b8ef0b49bcffb163e2838e238dea216b94b514af18b5c
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-25/
  files:
    - uniform.tcl  sha256:ee29d43f79533ac88bfdc4fb04eddbe7510ad193ff00c44812d0f5af68c78369
    - uniform.log  sha256:d3405cf388ddcfee67f1b41f347d3e56de1746b00a8af8a873f58c24704ab4d1
    - observed.tcl  sha256:a640ffe4855c5ea807ec8aa8aa052ca6c18b0ccd43f5d837370632e3eb35afb8
    - observed.log  sha256:6980b93763f20dbc8e589fa354b73d5fc57092e7f41cace611eba5090c0b1d40
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 8.2s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    236.69 |     94.07 |      7.84 |    338.60 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    150.91 |     42.90 |      7.27 |    201.09 | 0.594 | 5371 / 0 |
| alarm-gated | startup | 1040 |    166.21 |     51.93 |      7.86 |    226.00 | 0.667 | 5371 / 0 |
| alarm-gated | steady | 1024 |    161.46 |     48.70 |      7.84 |    218.00 | 0.644 | 5371 / 0 |
| backpressure | reset | 8 |    150.85 |     42.78 |      7.27 |    200.90 | 0.593 | 5371 / 0 |
| backpressure | startup | 1040 |    166.48 |     52.09 |      7.86 |    226.43 | 0.669 | 5371 / 0 |
| backpressure | steady | 1024 |    177.42 |     58.09 |      8.19 |    243.70 | 0.720 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    150.90 |     42.87 |      7.27 |    201.04 | 0.594 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    166.78 |     52.36 |      7.86 |    226.99 | 0.670 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    177.57 |     58.25 |      8.10 |    243.91 | 0.720 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    150.41 |     42.23 |      7.27 |    199.92 | 0.590 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    154.39 |     43.68 |      7.66 |    205.72 | 0.608 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    154.22 |     43.60 |      7.66 |    205.48 | 0.607 | 5371 / 0 |
| raw-streaming | reset | 8 |    151.00 |     43.14 |      7.27 |    201.42 | 0.595 | 5371 / 0 |
| raw-streaming | startup | 1040 |    167.28 |     52.95 |      7.81 |    228.04 | 0.673 | 5371 / 0 |
| raw-streaming | steady | 1024 |    178.13 |     58.90 |      8.12 |    245.15 | 0.724 | 5371 / 0 |

- `uniform_total_w`: 3.386014e-04
- `uniform_internal_w`: 2.366943e-04
- `uniform_switching_w`: 9.406505e-05
- `uniform_leakage_w`: 7.842120e-06
- `uniform_clock_w`: 6.993315e-05
- `uniform_sequential_w`: 1.757394e-04
- `uniform_combinational_w`: 9.292897e-05
- `uniform_total_a`: 9.405594e-05
- `obs_alarm_gated_reset_total_w`: 2.010871e-04
- `obs_alarm_gated_reset_internal_w`: 1.509134e-04
- `obs_alarm_gated_reset_switching_w`: 4.290115e-05
- `obs_alarm_gated_reset_leakage_w`: 7.272558e-06
- `obs_alarm_gated_reset_clock_w`: 6.993315e-05
- `obs_alarm_gated_reset_sequential_w`: 1.229526e-04
- `obs_alarm_gated_reset_combinational_w`: 8.201270e-06
- `obs_alarm_gated_reset_total_a`: 5.585753e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.260044e-04
- `obs_alarm_gated_startup_internal_w`: 1.662092e-04
- `obs_alarm_gated_startup_switching_w`: 5.193230e-05
- `obs_alarm_gated_startup_leakage_w`: 7.862931e-06
- `obs_alarm_gated_startup_clock_w`: 6.993315e-05
- `obs_alarm_gated_startup_sequential_w`: 1.342086e-04
- `obs_alarm_gated_startup_combinational_w`: 2.186272e-05
- `obs_alarm_gated_startup_total_a`: 6.277900e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.180002e-04
- `obs_alarm_gated_steady_internal_w`: 1.614580e-04
- `obs_alarm_gated_steady_switching_w`: 4.870021e-05
- `obs_alarm_gated_steady_leakage_w`: 7.842063e-06
- `obs_alarm_gated_steady_clock_w`: 6.993315e-05
- `obs_alarm_gated_steady_sequential_w`: 1.313684e-04
- `obs_alarm_gated_steady_combinational_w`: 1.669860e-05
- `obs_alarm_gated_steady_total_a`: 6.055561e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.009034e-04
- `obs_backpressure_reset_internal_w`: 1.508487e-04
- `obs_backpressure_reset_switching_w`: 4.278214e-05
- `obs_backpressure_reset_leakage_w`: 7.272558e-06
- `obs_backpressure_reset_clock_w`: 6.993315e-05
- `obs_backpressure_reset_sequential_w`: 1.229416e-04
- `obs_backpressure_reset_combinational_w`: 8.028568e-06
- `obs_backpressure_reset_total_a`: 5.580650e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.264317e-04
- `obs_backpressure_startup_internal_w`: 1.664825e-04
- `obs_backpressure_startup_switching_w`: 5.209149e-05
- `obs_backpressure_startup_leakage_w`: 7.857784e-06
- `obs_backpressure_startup_clock_w`: 6.993315e-05
- `obs_backpressure_startup_sequential_w`: 1.342620e-04
- `obs_backpressure_startup_combinational_w`: 2.223669e-05
- `obs_backpressure_startup_total_a`: 6.289769e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.436993e-04
- `obs_backpressure_steady_internal_w`: 1.774204e-04
- `obs_backpressure_steady_switching_w`: 5.808740e-05
- `obs_backpressure_steady_leakage_w`: 8.191520e-06
- `obs_backpressure_steady_clock_w`: 6.993315e-05
- `obs_backpressure_steady_sequential_w`: 1.429611e-04
- `obs_backpressure_steady_combinational_w`: 3.080504e-05
- `obs_backpressure_steady_total_a`: 6.769425e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.010413e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.508987e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.287012e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.272558e-06
- `obs_conditioned_streaming_reset_clock_w`: 6.993315e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.229526e-04
- `obs_conditioned_streaming_reset_combinational_w`: 8.155539e-06
- `obs_conditioned_streaming_reset_total_a`: 5.584481e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.269917e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.667754e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.235608e-05
- `obs_conditioned_streaming_startup_leakage_w`: 7.860215e-06
- `obs_conditioned_streaming_startup_clock_w`: 6.993315e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.344900e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.256859e-05
- `obs_conditioned_streaming_startup_total_a`: 6.305325e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.439138e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.775653e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.825082e-05
- `obs_conditioned_streaming_steady_leakage_w`: 8.097756e-06
- `obs_conditioned_streaming_steady_clock_w`: 6.993315e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.429189e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.106167e-05
- `obs_conditioned_streaming_steady_total_a`: 6.775383e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.999160e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.504090e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.223443e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.272558e-06
- `obs_disabled_clock_running_reset_clock_w`: 6.993315e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.228976e-04
- `obs_disabled_clock_running_reset_combinational_w`: 7.085213e-06
- `obs_disabled_clock_running_reset_total_a`: 5.553222e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.057225e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.543888e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.367802e-05
- `obs_disabled_clock_running_startup_leakage_w`: 7.655682e-06
- `obs_disabled_clock_running_startup_clock_w`: 6.993315e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.251590e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.063041e-05
- `obs_disabled_clock_running_startup_total_a`: 5.714514e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.054780e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.542169e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.360485e-05
- `obs_disabled_clock_running_steady_leakage_w`: 7.656220e-06
- `obs_disabled_clock_running_steady_clock_w`: 6.993315e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.252134e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.033140e-05
- `obs_disabled_clock_running_steady_total_a`: 5.707722e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.014204e-04
- `obs_raw_streaming_reset_internal_w`: 1.510050e-04
- `obs_raw_streaming_reset_switching_w`: 4.314292e-05
- `obs_raw_streaming_reset_leakage_w`: 7.272558e-06
- `obs_raw_streaming_reset_clock_w`: 6.993315e-05
- `obs_raw_streaming_reset_sequential_w`: 1.229514e-04
- `obs_raw_streaming_reset_combinational_w`: 8.535799e-06
- `obs_raw_streaming_reset_total_a`: 5.595011e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.280390e-04
- `obs_raw_streaming_startup_internal_w`: 1.672777e-04
- `obs_raw_streaming_startup_switching_w`: 5.294916e-05
- `obs_raw_streaming_startup_leakage_w`: 7.812067e-06
- `obs_raw_streaming_startup_clock_w`: 6.993315e-05
- `obs_raw_streaming_startup_sequential_w`: 1.344912e-04
- `obs_raw_streaming_startup_combinational_w`: 2.361465e-05
- `obs_raw_streaming_startup_total_a`: 6.334417e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.451474e-04
- `obs_raw_streaming_steady_internal_w`: 1.781282e-04
- `obs_raw_streaming_steady_switching_w`: 5.890318e-05
- `obs_raw_streaming_steady_leakage_w`: 8.116017e-06
- `obs_raw_streaming_steady_clock_w`: 6.993315e-05
- `obs_raw_streaming_steady_sequential_w`: 1.429585e-04
- `obs_raw_streaming_steady_combinational_w`: 3.225573e-05
- `obs_raw_streaming_steady_total_a`: 6.809650e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_125C_3v60 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_125C_3v60, interconnect `min`).
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
