---
record: 2026-10-30-digital-sta-activity-08
date: 2026-10-30T15:17:46Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: d24d862fc3836f8f5514aa2fa32e319f1a96567c
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha bb949d10cf059e01698f33f6531b74da1df90358).
repo_commit: 8939b542e96bfc19151bee88578dc394b5468fe2-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30.lib (liberty corner tt_025C_3v30, sha256:1157d0aa147dba75a214708197d7a046f970175d723cdec108025f6f06727c12)
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
  process: tt
  voltage: 3.30 V (nominal 3.3 V)
  temperature: 25
  liberty: gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30
  interconnect: nom (OpenRCX rule deck)
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
  spef_sha256: cf0ebf708b7f62b959207d6763a0b2fcac0ea8f5cd7078dee9abd027bb9504e6
  spef_bytes: 1795569
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
      vcd_sha256: d73b73c2878833b11c530926e16d4581e020fd1f07ba48aec025168df2997b09
      vcd_bytes: 20199467
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1490/1490
      xz_events: 4272
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: ce683a6499939dfdfbc7f0948d9cdf6e0fb7118b0eea81c99310ea9ff8a19a6d
      vcd_bytes: 21556003
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4289
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: 1b70087f5ae79f73da990c9d9aa9738670f74a6b31e57f02cc3f2ba736fa55fc
      vcd_bytes: 21612163
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4168
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: a10758043594e820119885dbb73a054dc89bfbbf413e35c32c5bd544f30648a5
      vcd_bytes: 16158866
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 1798
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: a8544b5fe783833514bdbc26788df620d3f8969d23472620ed7021e0628acd65
      vcd_bytes: 21759020
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4488
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-10-30-digital-sta-activity-08/
  files:
    - uniform.tcl  sha256:0b4de286b6f6c680254a11e836070f14f1c3223ba21f401f80947d1466e0ff80
    - uniform.log  sha256:e2ebf76b5ea19a3fea7ca5163eea0a573b88f9f2e3b1b7b8aa3e1dfa1372abcc
    - observed.tcl  sha256:2db8eba1c92cb89ba8c1fcc9827bff2226150f28790e0a5284cd71436b086dd4
    - observed.log  sha256:482638409e1298b6ee74da7b8c68aeb4ef2a111cad60b15bb50c31d7bdb1ebf6
    - activity-manifest.json  sha256:1e327145d7667bd16602328c74156fdb1a0755c542aa19e43d054aedb64852d1
wall_time: 8.7s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    176.80 |     81.51 |      0.23 |    258.54 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    115.07 |     37.22 |      0.22 |    152.51 | 0.590 | 5371 / 0 |
| alarm-gated | startup | 1040 |    126.06 |     45.05 |      0.23 |    171.34 | 0.663 | 5371 / 0 |
| alarm-gated | steady | 1024 |    122.68 |     42.36 |      0.23 |    165.27 | 0.639 | 5371 / 0 |
| backpressure | reset | 8 |    115.02 |     37.12 |      0.22 |    152.36 | 0.589 | 5371 / 0 |
| backpressure | startup | 1040 |    126.26 |     45.18 |      0.23 |    171.67 | 0.664 | 5371 / 0 |
| backpressure | steady | 1024 |    134.12 |     50.30 |      0.24 |    184.66 | 0.714 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    115.06 |     37.19 |      0.22 |    152.47 | 0.590 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    126.47 |     45.41 |      0.23 |    172.11 | 0.666 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    134.22 |     50.44 |      0.24 |    184.89 | 0.715 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    114.71 |     36.67 |      0.22 |    151.60 | 0.586 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    117.50 |     37.89 |      0.23 |    155.62 | 0.602 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    117.38 |     37.83 |      0.23 |    155.43 | 0.601 | 5371 / 0 |
| raw-streaming | reset | 8 |    115.13 |     37.42 |      0.22 |    152.77 | 0.591 | 5371 / 0 |
| raw-streaming | startup | 1040 |    126.82 |     45.94 |      0.23 |    172.99 | 0.669 | 5371 / 0 |
| raw-streaming | steady | 1024 |    134.62 |     51.01 |      0.24 |    185.87 | 0.719 | 5371 / 0 |

- `uniform_total_w`: 2.585442e-04
- `uniform_internal_w`: 1.768012e-04
- `uniform_switching_w`: 8.150809e-05
- `uniform_leakage_w`: 2.349355e-07
- `uniform_clock_w`: 5.339356e-05
- `uniform_sequential_w`: 1.354175e-04
- `uniform_combinational_w`: 6.973302e-05
- `uniform_total_a`: 7.834673e-05
- `obs_alarm_gated_reset_total_w`: 1.525102e-04
- `obs_alarm_gated_reset_internal_w`: 1.150670e-04
- `obs_alarm_gated_reset_switching_w`: 3.722004e-05
- `obs_alarm_gated_reset_leakage_w`: 2.230880e-07
- `obs_alarm_gated_reset_clock_w`: 5.339356e-05
- `obs_alarm_gated_reset_sequential_w`: 9.491749e-05
- `obs_alarm_gated_reset_combinational_w`: 4.199147e-06
- `obs_alarm_gated_reset_total_a`: 4.621521e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.713417e-04
- `obs_alarm_gated_startup_internal_w`: 1.260637e-04
- `obs_alarm_gated_startup_switching_w`: 4.504593e-05
- `obs_alarm_gated_startup_leakage_w`: 2.321263e-07
- `obs_alarm_gated_startup_clock_w`: 5.339356e-05
- `obs_alarm_gated_startup_sequential_w`: 1.034395e-04
- `obs_alarm_gated_startup_combinational_w`: 1.450866e-05
- `obs_alarm_gated_startup_total_a`: 5.192173e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.652712e-04
- `obs_alarm_gated_steady_internal_w`: 1.226811e-04
- `obs_alarm_gated_steady_switching_w`: 4.235859e-05
- `obs_alarm_gated_steady_leakage_w`: 2.314846e-07
- `obs_alarm_gated_steady_clock_w`: 5.339356e-05
- `obs_alarm_gated_steady_sequential_w`: 1.012127e-04
- `obs_alarm_gated_steady_combinational_w`: 1.066492e-05
- `obs_alarm_gated_steady_total_a`: 5.008218e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.523632e-04
- `obs_backpressure_reset_internal_w`: 1.150177e-04
- `obs_backpressure_reset_switching_w`: 3.712242e-05
- `obs_backpressure_reset_leakage_w`: 2.230880e-07
- `obs_backpressure_reset_clock_w`: 5.339356e-05
- `obs_backpressure_reset_sequential_w`: 9.490889e-05
- `obs_backpressure_reset_combinational_w`: 4.060730e-06
- `obs_backpressure_reset_total_a`: 4.617067e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.716744e-04
- `obs_backpressure_startup_internal_w`: 1.262606e-04
- `obs_backpressure_startup_switching_w`: 4.518135e-05
- `obs_backpressure_startup_leakage_w`: 2.324177e-07
- `obs_backpressure_startup_clock_w`: 5.339356e-05
- `obs_backpressure_startup_sequential_w`: 1.034772e-04
- `obs_backpressure_startup_combinational_w`: 1.480359e-05
- `obs_backpressure_startup_total_a`: 5.202255e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.846563e-04
- `obs_backpressure_steady_internal_w`: 1.341237e-04
- `obs_backpressure_steady_switching_w`: 5.029573e-05
- `obs_backpressure_steady_leakage_w`: 2.368907e-07
- `obs_backpressure_steady_clock_w`: 5.339356e-05
- `obs_backpressure_steady_sequential_w`: 1.100160e-04
- `obs_backpressure_steady_combinational_w`: 2.124667e-05
- `obs_backpressure_steady_total_a`: 5.595645e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.524732e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.150557e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.719449e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.230880e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.339356e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.491749e-05
- `obs_conditioned_streaming_reset_combinational_w`: 4.162223e-06
- `obs_conditioned_streaming_reset_total_a`: 4.620400e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.721090e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.264671e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.541012e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.317264e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.339356e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.036622e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.505323e-05
- `obs_conditioned_streaming_startup_total_a`: 5.215424e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.848938e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.342167e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.044143e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.357359e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.339356e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.099876e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.151272e-05
- `obs_conditioned_streaming_steady_total_a`: 5.602842e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.516029e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.147088e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.667104e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.230880e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.339356e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.487598e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.333326e-06
- `obs_disabled_clock_running_reset_total_a`: 4.594027e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.556227e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.175027e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.789295e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.270612e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.339356e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.640097e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.828246e-06
- `obs_disabled_clock_running_startup_total_a`: 4.715839e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.554346e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.173793e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.782819e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.270616e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.339356e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.644822e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.592813e-06
- `obs_disabled_clock_running_steady_total_a`: 4.710139e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.527696e-04
- `obs_raw_streaming_reset_internal_w`: 1.151266e-04
- `obs_raw_streaming_reset_switching_w`: 3.741993e-05
- `obs_raw_streaming_reset_leakage_w`: 2.230880e-07
- `obs_raw_streaming_reset_clock_w`: 5.339356e-05
- `obs_raw_streaming_reset_sequential_w`: 9.491711e-05
- `obs_raw_streaming_reset_combinational_w`: 4.458925e-06
- `obs_raw_streaming_reset_total_a`: 4.629382e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.729860e-04
- `obs_raw_streaming_startup_internal_w`: 1.268185e-04
- `obs_raw_streaming_startup_switching_w`: 4.593564e-05
- `obs_raw_streaming_startup_leakage_w`: 2.318815e-07
- `obs_raw_streaming_startup_clock_w`: 5.339356e-05
- `obs_raw_streaming_startup_sequential_w`: 1.036699e-04
- `obs_raw_streaming_startup_combinational_w`: 1.592252e-05
- `obs_raw_streaming_startup_total_a`: 5.242000e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.858681e-04
- `obs_raw_streaming_steady_internal_w`: 1.346205e-04
- `obs_raw_streaming_steady_switching_w`: 5.101102e-05
- `obs_raw_streaming_steady_leakage_w`: 2.366255e-07
- `obs_raw_streaming_steady_clock_w`: 5.339356e-05
- `obs_raw_streaming_steady_sequential_w`: 1.100169e-04
- `obs_raw_streaming_steady_combinational_w`: 2.245761e-05
- `obs_raw_streaming_steady_total_a`: 5.632367e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty tt_025C_3v30 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (tt_025C_3v30, interconnect `nom`).
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
