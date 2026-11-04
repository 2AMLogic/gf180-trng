---
record: 2026-10-30-digital-sta-activity-13
date: 2026-10-30T15:18:28Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60.lib (liberty corner ff_n40C_3v60, sha256:0b48b93d6800da325a2613ff6c0b998b230a1bbd28031f6da592e9ff30066602)
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
  process: ff
  voltage: 3.60 V (nominal 3.3 V, +9.1%)
  temperature: -40
  liberty: gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60
  interconnect: min (OpenRCX rule deck)
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
  spef_sha256: a705b66453becb4a7941509a02232b83a82ea3cbaacb71f474e70cf6c90d34a8
  spef_bytes: 1789895
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
  path: sim/records/raw/2026-10-30-digital-sta-activity-13/
  files:
    - uniform.tcl  sha256:495eb7136b39f6abc303e9f0fc80a5d2a72108468e62baff29894cd80daf49b2
    - uniform.log  sha256:48d41883beb932b7c7dbfc7bc08fac30886ef23720d0acdf64dfb271b1d3b3ca
    - observed.tcl  sha256:c57d252ee6311c3c412b56c20520ce2008332c70e035c1cb019695f5f911743d
    - observed.log  sha256:d760af7f8f9bb09e34a9bfce2fa96d7e6c4de17989667ddbcace0fde4b2ee0f0
    - activity-manifest.json  sha256:1e327145d7667bd16602328c74156fdb1a0755c542aa19e43d054aedb64852d1
wall_time: 8.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    216.06 |     93.63 |      0.28 |    309.97 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    139.91 |     42.85 |      0.26 |    183.02 | 0.590 | 5371 / 0 |
| alarm-gated | startup | 1040 |    153.42 |     51.89 |      0.27 |    205.58 | 0.663 | 5371 / 0 |
| alarm-gated | steady | 1024 |    149.23 |     48.77 |      0.27 |    198.28 | 0.640 | 5371 / 0 |
| backpressure | reset | 8 |    139.85 |     42.74 |      0.26 |    182.85 | 0.590 | 5371 / 0 |
| backpressure | startup | 1040 |    153.66 |     52.05 |      0.27 |    205.98 | 0.665 | 5371 / 0 |
| backpressure | steady | 1024 |    163.33 |     57.94 |      0.28 |    221.55 | 0.715 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    139.89 |     42.82 |      0.26 |    182.98 | 0.590 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    153.92 |     52.31 |      0.27 |    206.50 | 0.666 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    163.45 |     58.10 |      0.28 |    221.83 | 0.716 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    139.46 |     42.22 |      0.26 |    181.94 | 0.587 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    142.91 |     43.65 |      0.27 |    186.82 | 0.603 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    142.76 |     43.57 |      0.27 |    186.60 | 0.602 | 5371 / 0 |
| raw-streaming | reset | 8 |    139.98 |     43.08 |      0.26 |    183.32 | 0.591 | 5371 / 0 |
| raw-streaming | startup | 1040 |    154.36 |     52.90 |      0.27 |    207.53 | 0.670 | 5371 / 0 |
| raw-streaming | steady | 1024 |    163.95 |     58.75 |      0.28 |    222.98 | 0.719 | 5371 / 0 |

- `uniform_total_w`: 3.099656e-04
- `uniform_internal_w`: 2.160574e-04
- `uniform_switching_w`: 9.363300e-05
- `uniform_leakage_w`: 2.751911e-07
- `uniform_clock_w`: 6.415258e-05
- `uniform_sequential_w`: 1.626047e-04
- `uniform_combinational_w`: 8.320853e-05
- `uniform_total_a`: 8.610156e-05
- `obs_alarm_gated_reset_total_w`: 1.830190e-04
- `obs_alarm_gated_reset_internal_w`: 1.399066e-04
- `obs_alarm_gated_reset_switching_w`: 4.284875e-05
- `obs_alarm_gated_reset_leakage_w`: 2.635719e-07
- `obs_alarm_gated_reset_clock_w`: 6.415258e-05
- `obs_alarm_gated_reset_sequential_w`: 1.139137e-04
- `obs_alarm_gated_reset_combinational_w`: 4.952479e-06
- `obs_alarm_gated_reset_total_a`: 5.083861e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.055803e-04
- `obs_alarm_gated_startup_internal_w`: 1.534187e-04
- `obs_alarm_gated_startup_switching_w`: 5.188962e-05
- `obs_alarm_gated_startup_leakage_w`: 2.720082e-07
- `obs_alarm_gated_startup_clock_w`: 6.415258e-05
- `obs_alarm_gated_startup_sequential_w`: 1.240829e-04
- `obs_alarm_gated_startup_combinational_w`: 1.734494e-05
- `obs_alarm_gated_startup_total_a`: 5.710564e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.982776e-04
- `obs_alarm_gated_steady_internal_w`: 1.492337e-04
- `obs_alarm_gated_steady_switching_w`: 4.877264e-05
- `obs_alarm_gated_steady_leakage_w`: 2.712460e-07
- `obs_alarm_gated_steady_clock_w`: 6.415258e-05
- `obs_alarm_gated_steady_sequential_w`: 1.214237e-04
- `obs_alarm_gated_steady_combinational_w`: 1.270151e-05
- `obs_alarm_gated_steady_total_a`: 5.507711e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.828473e-04
- `obs_backpressure_reset_internal_w`: 1.398475e-04
- `obs_backpressure_reset_switching_w`: 4.273623e-05
- `obs_backpressure_reset_leakage_w`: 2.635719e-07
- `obs_backpressure_reset_clock_w`: 6.415258e-05
- `obs_backpressure_reset_sequential_w`: 1.139036e-04
- `obs_backpressure_reset_combinational_w`: 4.790928e-06
- `obs_backpressure_reset_total_a`: 5.079092e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.059770e-04
- `obs_backpressure_startup_internal_w`: 1.536587e-04
- `obs_backpressure_startup_switching_w`: 5.204598e-05
- `obs_backpressure_startup_leakage_w`: 2.722985e-07
- `obs_backpressure_startup_clock_w`: 6.415258e-05
- `obs_backpressure_startup_sequential_w`: 1.241277e-04
- `obs_backpressure_startup_combinational_w`: 1.769688e-05
- `obs_backpressure_startup_total_a`: 5.721583e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.215461e-04
- `obs_backpressure_steady_internal_w`: 1.633327e-04
- `obs_backpressure_steady_switching_w`: 5.793650e-05
- `obs_backpressure_steady_leakage_w`: 2.768367e-07
- `obs_backpressure_steady_clock_w`: 6.415258e-05
- `obs_backpressure_steady_sequential_w`: 1.320152e-04
- `obs_backpressure_steady_combinational_w`: 2.537819e-05
- `obs_backpressure_steady_total_a`: 6.154058e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.829754e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.398930e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.281882e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.635719e-07
- `obs_conditioned_streaming_reset_clock_w`: 6.415258e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.139137e-04
- `obs_conditioned_streaming_reset_combinational_w`: 4.908908e-06
- `obs_conditioned_streaming_reset_total_a`: 5.082650e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.064984e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.539180e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.230882e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.716374e-07
- `obs_conditioned_streaming_startup_clock_w`: 6.415258e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.243527e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.799336e-05
- `obs_conditioned_streaming_startup_total_a`: 5.736067e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.218307e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.634521e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.810290e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.756414e-07
- `obs_conditioned_streaming_steady_clock_w`: 6.415258e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.319854e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.569274e-05
- `obs_conditioned_streaming_steady_total_a`: 6.161964e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.819388e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.394592e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.221603e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.635719e-07
- `obs_disabled_clock_running_reset_clock_w`: 6.415258e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.138637e-04
- `obs_disabled_clock_running_reset_combinational_w`: 3.922385e-06
- `obs_disabled_clock_running_reset_total_a`: 5.053856e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.868248e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.429116e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.364661e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.666009e-07
- `obs_disabled_clock_running_startup_clock_w`: 6.415258e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.156744e-04
- `obs_disabled_clock_running_startup_combinational_w`: 6.997906e-06
- `obs_disabled_clock_running_startup_total_a`: 5.189578e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.866003e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.427612e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.357257e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.666007e-07
- `obs_disabled_clock_running_steady_clock_w`: 6.415258e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.157294e-04
- `obs_disabled_clock_running_steady_combinational_w`: 6.718413e-06
- `obs_disabled_clock_running_steady_total_a`: 5.183342e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.833241e-04
- `obs_raw_streaming_reset_internal_w`: 1.399822e-04
- `obs_raw_streaming_reset_switching_w`: 4.307830e-05
- `obs_raw_streaming_reset_leakage_w`: 2.635719e-07
- `obs_raw_streaming_reset_clock_w`: 6.415258e-05
- `obs_raw_streaming_reset_sequential_w`: 1.139130e-04
- `obs_raw_streaming_reset_combinational_w`: 5.258317e-06
- `obs_raw_streaming_reset_total_a`: 5.092336e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.075325e-04
- `obs_raw_streaming_startup_internal_w`: 1.543585e-04
- `obs_raw_streaming_startup_switching_w`: 5.290231e-05
- `obs_raw_streaming_startup_leakage_w`: 2.717171e-07
- `obs_raw_streaming_startup_clock_w`: 6.415258e-05
- `obs_raw_streaming_startup_sequential_w`: 1.243567e-04
- `obs_raw_streaming_startup_combinational_w`: 1.902329e-05
- `obs_raw_streaming_startup_total_a`: 5.764792e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.229789e-04
- `obs_raw_streaming_steady_internal_w`: 1.639538e-04
- `obs_raw_streaming_steady_switching_w`: 5.874860e-05
- `obs_raw_streaming_steady_leakage_w`: 2.765572e-07
- `obs_raw_streaming_steady_clock_w`: 6.415258e-05
- `obs_raw_streaming_steady_sequential_w`: 1.320162e-04
- `obs_raw_streaming_steady_combinational_w`: 2.680998e-05
- `obs_raw_streaming_steady_total_a`: 6.193858e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_n40C_3v60 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_n40C_3v60, interconnect `min`).
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
