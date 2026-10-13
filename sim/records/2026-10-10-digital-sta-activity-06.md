---
record: 2026-10-10-digital-sta-activity-06
date: 2026-10-10T02:45:24Z
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
  - rules.openrcx.gf180mcuD.max (OpenRCX interconnect corner max, sha256:0ee103cf2108f2fd945087551b6dd1eaf4ee55af60571de2983878c8a271515f)
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
  interconnect: max (OpenRCX rule deck)
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
  spef_sha256: eaea3f492506ba4286dacb35d02980d53ee2af22d8149124281d2331ef364c2d
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-06/
  files:
    - uniform.tcl  sha256:47dab01c017d10195b10dcfb2575c4695aed0e1245d0af4c13180143c36b31e8
    - uniform.log  sha256:beb5f5288ce9dd956b3c00c112647488a51fa4b64e2a563c08a01270f6b22ec2
    - observed.tcl  sha256:2e176e134ff6aec4c208d461c1bd7528844c815804dcff60c3476c30af3d0a68
    - observed.log  sha256:3c289e7ef1daad428741a50c364f63b6ef94976bb2be80ced25a27e53642d5a7
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 9.6s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    136.69 |     69.32 |      0.17 |    206.18 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     90.46 |     31.36 |      0.17 |    121.99 | 0.592 | 5371 / 0 |
| alarm-gated | startup | 1040 |     98.67 |     37.91 |      0.17 |    136.76 | 0.663 | 5371 / 0 |
| alarm-gated | steady | 1024 |     96.16 |     35.57 |      0.17 |    131.90 | 0.640 | 5371 / 0 |
| backpressure | reset | 8 |     90.43 |     31.27 |      0.17 |    121.86 | 0.591 | 5371 / 0 |
| backpressure | startup | 1040 |     98.82 |     38.03 |      0.17 |    137.02 | 0.665 | 5371 / 0 |
| backpressure | steady | 1024 |    104.74 |     42.45 |      0.17 |    147.36 | 0.715 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     90.46 |     31.34 |      0.17 |    121.96 | 0.592 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |     98.97 |     38.23 |      0.17 |    137.37 | 0.666 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    104.81 |     42.57 |      0.17 |    147.56 | 0.716 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     90.20 |     30.86 |      0.17 |    121.23 | 0.588 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     92.22 |     31.86 |      0.17 |    124.25 | 0.603 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     92.13 |     31.80 |      0.17 |    124.10 | 0.602 | 5371 / 0 |
| raw-streaming | reset | 8 |     90.50 |     31.54 |      0.17 |    122.21 | 0.593 | 5371 / 0 |
| raw-streaming | startup | 1040 |     99.22 |     38.68 |      0.17 |    138.08 | 0.670 | 5371 / 0 |
| raw-streaming | steady | 1024 |    105.10 |     43.07 |      0.17 |    148.35 | 0.719 | 5371 / 0 |

- `uniform_total_w`: 2.061815e-04
- `uniform_internal_w`: 1.366854e-04
- `uniform_switching_w`: 6.932307e-05
- `uniform_leakage_w`: 1.730075e-07
- `uniform_clock_w`: 4.215705e-05
- `uniform_sequential_w`: 1.083214e-04
- `uniform_combinational_w`: 5.570312e-05
- `uniform_total_a`: 6.872717e-05
- `obs_alarm_gated_reset_total_w`: 1.219885e-04
- `obs_alarm_gated_reset_internal_w`: 9.046446e-05
- `obs_alarm_gated_reset_switching_w`: 3.135718e-05
- `obs_alarm_gated_reset_leakage_w`: 1.668595e-07
- `obs_alarm_gated_reset_clock_w`: 4.215705e-05
- `obs_alarm_gated_reset_sequential_w`: 7.633967e-05
- `obs_alarm_gated_reset_combinational_w`: 3.491857e-06
- `obs_alarm_gated_reset_total_a`: 4.066283e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.367558e-04
- `obs_alarm_gated_startup_internal_w`: 9.866875e-05
- `obs_alarm_gated_startup_switching_w`: 3.791484e-05
- `obs_alarm_gated_startup_leakage_w`: 1.722517e-07
- `obs_alarm_gated_startup_clock_w`: 4.215705e-05
- `obs_alarm_gated_startup_sequential_w`: 8.316770e-05
- `obs_alarm_gated_startup_combinational_w`: 1.143109e-05
- `obs_alarm_gated_startup_total_a`: 4.558527e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.318993e-04
- `obs_alarm_gated_steady_internal_w`: 9.616114e-05
- `obs_alarm_gated_steady_switching_w`: 3.556643e-05
- `obs_alarm_gated_steady_leakage_w`: 1.717606e-07
- `obs_alarm_gated_steady_clock_w`: 4.215705e-05
- `obs_alarm_gated_steady_sequential_w`: 8.137913e-05
- `obs_alarm_gated_steady_combinational_w`: 8.363171e-06
- `obs_alarm_gated_steady_total_a`: 4.396643e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.218618e-04
- `obs_backpressure_reset_internal_w`: 9.042588e-05
- `obs_backpressure_reset_switching_w`: 3.126908e-05
- `obs_backpressure_reset_leakage_w`: 1.668595e-07
- `obs_backpressure_reset_clock_w`: 4.215705e-05
- `obs_backpressure_reset_sequential_w`: 7.633277e-05
- `obs_backpressure_reset_combinational_w`: 3.372081e-06
- `obs_backpressure_reset_total_a`: 4.062060e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.370189e-04
- `obs_backpressure_startup_internal_w`: 9.881501e-05
- `obs_backpressure_startup_switching_w`: 3.803146e-05
- `obs_backpressure_startup_leakage_w`: 1.723908e-07
- `obs_backpressure_startup_clock_w`: 4.215705e-05
- `obs_backpressure_startup_sequential_w`: 8.319253e-05
- `obs_backpressure_startup_combinational_w`: 1.166921e-05
- `obs_backpressure_startup_total_a`: 4.567297e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.473638e-04
- `obs_backpressure_steady_internal_w`: 1.047397e-04
- `obs_backpressure_steady_switching_w`: 4.244953e-05
- `obs_backpressure_steady_leakage_w`: 1.745426e-07
- `obs_backpressure_steady_clock_w`: 4.215705e-05
- `obs_backpressure_steady_sequential_w`: 8.839939e-05
- `obs_backpressure_steady_combinational_w`: 1.680732e-05
- `obs_backpressure_steady_total_a`: 4.912127e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.219581e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.045596e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.133525e-05
- `obs_conditioned_streaming_reset_leakage_w`: 1.668595e-07
- `obs_conditioned_streaming_reset_clock_w`: 4.215705e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.633967e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.461424e-06
- `obs_conditioned_streaming_reset_total_a`: 4.065270e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.373709e-04
- `obs_conditioned_streaming_startup_internal_w`: 9.897188e-05
- `obs_conditioned_streaming_startup_switching_w`: 3.822695e-05
- `obs_conditioned_streaming_startup_leakage_w`: 1.720867e-07
- `obs_conditioned_streaming_startup_clock_w`: 4.215705e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.334679e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.186704e-05
- `obs_conditioned_streaming_startup_total_a`: 4.579030e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.475571e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.048118e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.257140e-05
- `obs_conditioned_streaming_steady_leakage_w`: 1.739097e-07
- `obs_conditioned_streaming_steady_clock_w`: 4.215705e-05
- `obs_conditioned_streaming_steady_sequential_w`: 8.838638e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.701373e-05
- `obs_conditioned_streaming_steady_total_a`: 4.918570e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.212281e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.019880e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.086243e-05
- `obs_disabled_clock_running_reset_leakage_w`: 1.668595e-07
- `obs_disabled_clock_running_reset_clock_w`: 4.215705e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.630731e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.763823e-06
- `obs_disabled_clock_running_reset_total_a`: 4.040937e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.242452e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.221759e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.185819e-05
- `obs_disabled_clock_running_startup_leakage_w`: 1.694443e-07
- `obs_disabled_clock_running_startup_clock_w`: 4.215705e-05
- `obs_disabled_clock_running_startup_sequential_w`: 7.751089e-05
- `obs_disabled_clock_running_startup_combinational_w`: 4.577279e-06
- `obs_disabled_clock_running_startup_total_a`: 4.141507e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.240981e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.212513e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.180353e-05
- `obs_disabled_clock_running_steady_leakage_w`: 1.694437e-07
- `obs_disabled_clock_running_steady_clock_w`: 4.215705e-05
- `obs_disabled_clock_running_steady_sequential_w`: 7.754996e-05
- `obs_disabled_clock_running_steady_combinational_w`: 4.391123e-06
- `obs_disabled_clock_running_steady_total_a`: 4.136603e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.222093e-04
- `obs_raw_streaming_reset_internal_w`: 9.050489e-05
- `obs_raw_streaming_reset_switching_w`: 3.153751e-05
- `obs_raw_streaming_reset_leakage_w`: 1.668595e-07
- `obs_raw_streaming_reset_clock_w`: 4.215705e-05
- `obs_raw_streaming_reset_sequential_w`: 7.633965e-05
- `obs_raw_streaming_reset_combinational_w`: 3.712647e-06
- `obs_raw_streaming_reset_total_a`: 4.073643e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.380781e-04
- `obs_raw_streaming_startup_internal_w`: 9.922359e-05
- `obs_raw_streaming_startup_switching_w`: 3.868237e-05
- `obs_raw_streaming_startup_leakage_w`: 1.720917e-07
- `obs_raw_streaming_startup_clock_w`: 4.215705e-05
- `obs_raw_streaming_startup_sequential_w`: 8.334607e-05
- `obs_raw_streaming_startup_combinational_w`: 1.257491e-05
- `obs_raw_streaming_startup_total_a`: 4.602603e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.483473e-04
- `obs_raw_streaming_steady_internal_w`: 1.051041e-04
- `obs_raw_streaming_steady_switching_w`: 4.306879e-05
- `obs_raw_streaming_steady_leakage_w`: 1.743987e-07
- `obs_raw_streaming_steady_clock_w`: 4.215705e-05
- `obs_raw_streaming_steady_sequential_w`: 8.840502e-05
- `obs_raw_streaming_steady_combinational_w`: 1.778520e-05
- `obs_raw_streaming_steady_total_a`: 4.944910e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_n40C_3v00 --rc max --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_n40C_3v00, interconnect `max`).
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
