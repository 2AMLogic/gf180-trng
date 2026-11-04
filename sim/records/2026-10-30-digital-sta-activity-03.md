---
record: 2026-10-30-digital-sta-activity-03
date: 2026-10-30T15:17:02Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib (liberty corner ss_125C_3v00, sha256:d83917f827021eadb159f6011905bf20de632533b2953abba89266a88c2b24af)
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
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00
  interconnect: max (OpenRCX rule deck)
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
  spef_sha256: 501e2aa432474c024f5a81d5ee2a31de8a41ae89a329f8e61272a9ae797cc962
  spef_bytes: 1803172
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
  path: sim/records/raw/2026-10-30-digital-sta-activity-03/
  files:
    - uniform.tcl  sha256:266b28b399dde00c919addda83a66d57314c7213e6bbd487b7faf7b114f85fcb
    - uniform.log  sha256:605de9548c5b4e4209655d102ca200c97f682f938821d1c16df4b3056cd39526
    - observed.tcl  sha256:bfc83d04a3993a45ee4d49b722fef768a507dd36b8a1e83e489a2c7ec7a43d7b
    - observed.log  sha256:05ebb8aaf8b5c16ca009dc3a6b7d890a96088319c9c540f58b3a6f935e591531
    - activity-manifest.json  sha256:1e327145d7667bd16602328c74156fdb1a0755c542aa19e43d054aedb64852d1
wall_time: 8.5s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    147.43 |     70.99 |      2.46 |    220.87 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     96.35 |     32.30 |      2.45 |    131.09 | 0.594 | 5371 / 0 |
| alarm-gated | startup | 1040 |    105.47 |     39.08 |      2.46 |    147.01 | 0.666 | 5371 / 0 |
| alarm-gated | steady | 1024 |    102.68 |     36.76 |      2.46 |    141.89 | 0.642 | 5371 / 0 |
| backpressure | reset | 8 |     96.31 |     32.21 |      2.45 |    130.97 | 0.593 | 5371 / 0 |
| backpressure | startup | 1040 |    105.63 |     39.20 |      2.46 |    147.29 | 0.667 | 5371 / 0 |
| backpressure | steady | 1024 |    112.16 |     43.65 |      2.46 |    158.27 | 0.717 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     96.34 |     32.28 |      2.45 |    131.06 | 0.593 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    105.80 |     39.40 |      2.46 |    147.66 | 0.669 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    112.24 |     43.78 |      2.46 |    158.47 | 0.717 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     96.06 |     31.82 |      2.45 |    130.33 | 0.590 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     98.35 |     32.86 |      2.45 |    133.67 | 0.605 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     98.25 |     32.81 |      2.45 |    133.51 | 0.604 | 5371 / 0 |
| raw-streaming | reset | 8 |     96.40 |     32.47 |      2.45 |    131.32 | 0.595 | 5371 / 0 |
| raw-streaming | startup | 1040 |    106.09 |     39.87 |      2.46 |    148.41 | 0.672 | 5371 / 0 |
| raw-streaming | steady | 1024 |    112.57 |     44.28 |      2.46 |    159.31 | 0.721 | 5371 / 0 |

- `uniform_total_w`: 2.208702e-04
- `uniform_internal_w`: 1.474269e-04
- `uniform_switching_w`: 7.098692e-05
- `uniform_leakage_w`: 2.456396e-06
- `uniform_clock_w`: 4.668667e-05
- `uniform_sequential_w`: 1.144378e-04
- `uniform_combinational_w`: 5.974559e-05
- `uniform_total_a`: 7.362340e-05
- `obs_alarm_gated_reset_total_w`: 1.310918e-04
- `obs_alarm_gated_reset_internal_w`: 9.634715e-05
- `obs_alarm_gated_reset_switching_w`: 3.229843e-05
- `obs_alarm_gated_reset_leakage_w`: 2.446252e-06
- `obs_alarm_gated_reset_clock_w`: 4.668667e-05
- `obs_alarm_gated_reset_sequential_w`: 8.034809e-05
- `obs_alarm_gated_reset_combinational_w`: 4.057077e-06
- `obs_alarm_gated_reset_total_a`: 4.369727e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.470080e-04
- `obs_alarm_gated_startup_internal_w`: 1.054699e-04
- `obs_alarm_gated_startup_switching_w`: 3.908226e-05
- `obs_alarm_gated_startup_leakage_w`: 2.455845e-06
- `obs_alarm_gated_startup_clock_w`: 4.668667e-05
- `obs_alarm_gated_startup_sequential_w`: 8.754982e-05
- `obs_alarm_gated_startup_combinational_w`: 1.277147e-05
- `obs_alarm_gated_startup_total_a`: 4.900267e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.418918e-04
- `obs_alarm_gated_steady_internal_w`: 1.026761e-04
- `obs_alarm_gated_steady_switching_w`: 3.676040e-05
- `obs_alarm_gated_steady_leakage_w`: 2.455274e-06
- `obs_alarm_gated_steady_clock_w`: 4.668667e-05
- `obs_alarm_gated_steady_sequential_w`: 8.566602e-05
- `obs_alarm_gated_steady_combinational_w`: 9.539097e-06
- `obs_alarm_gated_steady_total_a`: 4.729727e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.309663e-04
- `obs_backpressure_reset_internal_w`: 9.630668e-05
- `obs_backpressure_reset_switching_w`: 3.221341e-05
- `obs_backpressure_reset_leakage_w`: 2.446252e-06
- `obs_backpressure_reset_clock_w`: 4.668667e-05
- `obs_backpressure_reset_sequential_w`: 8.034077e-05
- `obs_backpressure_reset_combinational_w`: 3.938896e-06
- `obs_backpressure_reset_total_a`: 4.365543e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.472904e-04
- `obs_backpressure_startup_internal_w`: 1.056342e-04
- `obs_backpressure_startup_switching_w`: 3.920008e-05
- `obs_backpressure_startup_leakage_w`: 2.456071e-06
- `obs_backpressure_startup_clock_w`: 4.668667e-05
- `obs_backpressure_startup_sequential_w`: 8.758166e-05
- `obs_backpressure_startup_combinational_w`: 1.302195e-05
- `obs_backpressure_startup_total_a`: 4.909680e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.582681e-04
- `obs_backpressure_steady_internal_w`: 1.121593e-04
- `obs_backpressure_steady_switching_w`: 4.364927e-05
- `obs_backpressure_steady_leakage_w`: 2.459506e-06
- `obs_backpressure_steady_clock_w`: 4.668667e-05
- `obs_backpressure_steady_sequential_w`: 9.307851e-05
- `obs_backpressure_steady_combinational_w`: 1.850283e-05
- `obs_backpressure_steady_total_a`: 5.275603e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.310613e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.633847e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.227656e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.446252e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.668667e-05
- `obs_conditioned_streaming_reset_sequential_w`: 8.034809e-05
- `obs_conditioned_streaming_reset_combinational_w`: 4.026519e-06
- `obs_conditioned_streaming_reset_total_a`: 4.368710e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.476594e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.058044e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.939947e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.455506e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.668667e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.773727e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.323536e-05
- `obs_conditioned_streaming_startup_total_a`: 4.921980e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.584708e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.122356e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.377696e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.458290e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.668667e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.305319e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.873097e-05
- `obs_conditioned_streaming_steady_total_a`: 5.282360e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.303252e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.605772e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.182123e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.446252e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.668667e-05
- `obs_disabled_clock_running_reset_sequential_w`: 8.031334e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.325182e-06
- `obs_disabled_clock_running_reset_total_a`: 4.344173e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.336682e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.835196e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.286415e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.452133e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.668667e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.159455e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.387051e-06
- `obs_disabled_clock_running_startup_total_a`: 4.455607e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.335077e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.824839e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.280715e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.452133e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.668667e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.163503e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.186022e-06
- `obs_disabled_clock_running_steady_total_a`: 4.450257e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.313153e-04
- `obs_raw_streaming_reset_internal_w`: 9.639619e-05
- `obs_raw_streaming_reset_switching_w`: 3.247283e-05
- `obs_raw_streaming_reset_leakage_w`: 2.446252e-06
- `obs_raw_streaming_reset_clock_w`: 4.668667e-05
- `obs_raw_streaming_reset_sequential_w`: 8.034788e-05
- `obs_raw_streaming_reset_combinational_w`: 4.280715e-06
- `obs_raw_streaming_reset_total_a`: 4.377177e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.484123e-04
- `obs_raw_streaming_startup_internal_w`: 1.060917e-04
- `obs_raw_streaming_startup_switching_w`: 3.986510e-05
- `obs_raw_streaming_startup_leakage_w`: 2.455513e-06
- `obs_raw_streaming_startup_clock_w`: 4.668667e-05
- `obs_raw_streaming_startup_sequential_w`: 8.774563e-05
- `obs_raw_streaming_startup_combinational_w`: 1.398004e-05
- `obs_raw_streaming_startup_total_a`: 4.947077e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.593077e-04
- `obs_raw_streaming_steady_internal_w`: 1.125685e-04
- `obs_raw_streaming_steady_switching_w`: 4.428014e-05
- `obs_raw_streaming_steady_leakage_w`: 2.459014e-06
- `obs_raw_streaming_steady_clock_w`: 4.668667e-05
- `obs_raw_streaming_steady_sequential_w`: 9.307939e-05
- `obs_raw_streaming_steady_combinational_w`: 1.954153e-05
- `obs_raw_streaming_steady_total_a`: 5.310257e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_125C_3v00 --rc max --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_125C_3v00, interconnect `max`).
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
