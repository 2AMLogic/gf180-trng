---
record: 2026-11-09-digital-sta-activity-11
date: 2026-11-09T21:58:01Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: 87b3dedca82354ea1c6b17e7e2867c806f9625f5
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha edd5900119f431c7d68f1f67eb3dcdf6b44ec32c).
repo_commit: 910461f4e20a99fe6369fa53beccde60370754b3-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60.lib (liberty corner ff_125C_3v60, sha256:b64f32b397097f2046e66ce7f9a4aaffc9a80c4c0bfd3c77385727268e81a016)
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
  process: ff
  voltage: 3.60 V (nominal 3.3 V, +9.1%)
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60
  interconnect: nom (OpenRCX rule deck)
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
  spef_sha256: 86917579ff0c6b0171baeedd6a53fbd6a3e2b89de8ee1af984cc3ec2834ea13e
  spef_bytes: 1654157
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
      vcd_sha256: cb1d7aee2c0ba5e04161beca4aac3b24cc2dee586ed6cc7a1f5215d97863df01
      vcd_bytes: 17669097
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1423/1423
      xz_events: 4934
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: 9b061ae736049538e09ec41d92b1352fb3d84aa4e792f1c549283350dd05d96d
      vcd_bytes: 19101258
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1423/1423
      xz_events: 5236
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: 4f8de9215f6b9e43309280a614e7f84fa92be1c5d899956043c44e3c29bb0aaf
      vcd_bytes: 19148535
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1423/1423
      xz_events: 4971
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: 5a9bd1310e4c8d864b2d15546646caca70c24638ab57a921fd3910d43fe954b7
      vcd_bytes: 13464437
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1423/1423
      xz_events: 2224
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: 96e7b0cf056219fe0957d1c3af0f76b6c651a43eff1d95da3bf765e3c1e0ae14
      vcd_bytes: 19296058
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1423/1423
      xz_events: 5315
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-11-09-digital-sta-activity-11/
  files:
    - uniform.tcl  sha256:3aff5791a65422d93118c06bdd9036dca9b2d6577fb37e222266ffb92e092335
    - uniform.log  sha256:499c40b2386aed61ae661451abdd6a0c43c4f24ace249708141fba04ff4fdc6f
    - observed.tcl  sha256:791c38fc7cb09fb0656dc7fc8084d4626c4040ee7dd96d03b329ce1270ef3de4
    - observed.log  sha256:fc24925e2a1ae6bebf6031b36edece15e7e13ade4c7b13b800aec8ba7f9a7b59
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 9.2s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    233.57 |     93.25 |      7.62 |    334.44 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    152.53 |     43.75 |      7.05 |    203.34 | 0.608 | 5143 / 0 |
| alarm-gated | startup | 1040 |    170.45 |     54.43 |      7.70 |    232.57 | 0.695 | 5143 / 0 |
| alarm-gated | steady | 1024 |    165.29 |     51.15 |      7.67 |    224.11 | 0.670 | 5143 / 0 |
| backpressure | reset | 8 |    152.47 |     43.62 |      7.05 |    203.14 | 0.607 | 5143 / 0 |
| backpressure | startup | 1040 |    170.81 |     54.62 |      7.66 |    233.10 | 0.697 | 5143 / 0 |
| backpressure | steady | 1024 |    181.40 |     60.62 |      7.98 |    250.00 | 0.748 | 5143 / 0 |
| conditioned-streaming | reset | 8 |    152.52 |     43.74 |      7.05 |    203.30 | 0.608 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    171.23 |     54.89 |      7.68 |    233.80 | 0.699 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    181.61 |     60.84 |      7.89 |    250.33 | 0.749 | 5143 / 0 |
| disabled-clock-running | reset | 8 |    151.61 |     42.97 |      7.05 |    201.63 | 0.603 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |    156.06 |     45.43 |      7.37 |    208.86 | 0.624 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |    155.89 |     45.35 |      7.37 |    208.60 | 0.624 | 5143 / 0 |
| raw-streaming | reset | 8 |    152.39 |     43.92 |      7.05 |    203.37 | 0.608 | 5143 / 0 |
| raw-streaming | startup | 1040 |    171.42 |     55.43 |      7.62 |    234.47 | 0.701 | 5143 / 0 |
| raw-streaming | steady | 1024 |    182.05 |     61.51 |      7.90 |    251.46 | 0.752 | 5143 / 0 |

- `uniform_total_w`: 3.344389e-04
- `uniform_internal_w`: 2.335693e-04
- `uniform_switching_w`: 9.325296e-05
- `uniform_leakage_w`: 7.616592e-06
- `uniform_clock_w`: 7.373444e-05
- `uniform_sequential_w`: 1.709781e-04
- `uniform_combinational_w`: 8.972641e-05
- `uniform_total_a`: 9.289969e-05
- `obs_alarm_gated_reset_total_w`: 2.033351e-04
- `obs_alarm_gated_reset_internal_w`: 1.525311e-04
- `obs_alarm_gated_reset_switching_w`: 4.375281e-05
- `obs_alarm_gated_reset_leakage_w`: 7.051153e-06
- `obs_alarm_gated_reset_clock_w`: 7.373444e-05
- `obs_alarm_gated_reset_sequential_w`: 1.221919e-04
- `obs_alarm_gated_reset_combinational_w`: 7.408763e-06
- `obs_alarm_gated_reset_total_a`: 5.648197e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.325727e-04
- `obs_alarm_gated_startup_internal_w`: 1.704453e-04
- `obs_alarm_gated_startup_switching_w`: 5.443112e-05
- `obs_alarm_gated_startup_leakage_w`: 7.696259e-06
- `obs_alarm_gated_startup_clock_w`: 7.373444e-05
- `obs_alarm_gated_startup_sequential_w`: 1.347615e-04
- `obs_alarm_gated_startup_combinational_w`: 2.407681e-05
- `obs_alarm_gated_startup_total_a`: 6.460353e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.241133e-04
- `obs_alarm_gated_steady_internal_w`: 1.652932e-04
- `obs_alarm_gated_steady_switching_w`: 5.115203e-05
- `obs_alarm_gated_steady_leakage_w`: 7.668041e-06
- `obs_alarm_gated_steady_clock_w`: 7.373444e-05
- `obs_alarm_gated_steady_sequential_w`: 1.323495e-04
- `obs_alarm_gated_steady_combinational_w`: 1.802919e-05
- `obs_alarm_gated_steady_total_a`: 6.225369e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.031393e-04
- `obs_backpressure_reset_internal_w`: 1.524664e-04
- `obs_backpressure_reset_switching_w`: 4.362178e-05
- `obs_backpressure_reset_leakage_w`: 7.051153e-06
- `obs_backpressure_reset_clock_w`: 7.373444e-05
- `obs_backpressure_reset_sequential_w`: 1.221809e-04
- `obs_backpressure_reset_combinational_w`: 7.223937e-06
- `obs_backpressure_reset_total_a`: 5.642758e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.330987e-04
- `obs_backpressure_startup_internal_w`: 1.708136e-04
- `obs_backpressure_startup_switching_w`: 5.462023e-05
- `obs_backpressure_startup_leakage_w`: 7.664829e-06
- `obs_backpressure_startup_clock_w`: 7.373444e-05
- `obs_backpressure_startup_sequential_w`: 1.349062e-04
- `obs_backpressure_startup_combinational_w`: 2.445816e-05
- `obs_backpressure_startup_total_a`: 6.474964e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.500006e-04
- `obs_backpressure_steady_internal_w`: 1.813998e-04
- `obs_backpressure_steady_switching_w`: 6.062400e-05
- `obs_backpressure_steady_leakage_w`: 7.976833e-06
- `obs_backpressure_steady_clock_w`: 7.373444e-05
- `obs_backpressure_steady_sequential_w`: 1.438991e-04
- `obs_backpressure_steady_combinational_w`: 3.236695e-05
- `obs_backpressure_steady_total_a`: 6.944461e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.033046e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.525159e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.373753e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.051153e-06
- `obs_conditioned_streaming_reset_clock_w`: 7.373444e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.221919e-04
- `obs_conditioned_streaming_reset_combinational_w`: 7.378283e-06
- `obs_conditioned_streaming_reset_total_a`: 5.647350e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.338008e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.712311e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.489303e-05
- `obs_conditioned_streaming_startup_leakage_w`: 7.676662e-06
- `obs_conditioned_streaming_startup_clock_w`: 7.373444e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.352236e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.484282e-05
- `obs_conditioned_streaming_startup_total_a`: 6.494467e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.503344e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.816107e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.083725e-05
- `obs_conditioned_streaming_steady_leakage_w`: 7.886476e-06
- `obs_conditioned_streaming_steady_clock_w`: 7.373444e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.439256e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.267434e-05
- `obs_conditioned_streaming_steady_total_a`: 6.953733e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 2.016322e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.516131e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.296792e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.051153e-06
- `obs_disabled_clock_running_reset_clock_w`: 7.373444e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.221318e-04
- `obs_disabled_clock_running_reset_combinational_w`: 5.765962e-06
- `obs_disabled_clock_running_reset_total_a`: 5.600894e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.088557e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.560576e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.543126e-05
- `obs_disabled_clock_running_startup_leakage_w`: 7.366870e-06
- `obs_disabled_clock_running_startup_clock_w`: 7.373444e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.243725e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.074878e-05
- `obs_disabled_clock_running_startup_total_a`: 5.801547e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.086043e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.558853e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.535163e-05
- `obs_disabled_clock_running_steady_leakage_w`: 7.367390e-06
- `obs_disabled_clock_running_steady_clock_w`: 7.373444e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.244272e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.044272e-05
- `obs_disabled_clock_running_steady_total_a`: 5.794564e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.033691e-04
- `obs_raw_streaming_reset_internal_w`: 1.523940e-04
- `obs_raw_streaming_reset_switching_w`: 4.392394e-05
- `obs_raw_streaming_reset_leakage_w`: 7.051153e-06
- `obs_raw_streaming_reset_clock_w`: 7.373444e-05
- `obs_raw_streaming_reset_sequential_w`: 1.221875e-04
- `obs_raw_streaming_reset_combinational_w`: 7.447133e-06
- `obs_raw_streaming_reset_total_a`: 5.649142e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.344650e-04
- `obs_raw_streaming_startup_internal_w`: 1.714176e-04
- `obs_raw_streaming_startup_switching_w`: 5.542539e-05
- `obs_raw_streaming_startup_leakage_w`: 7.622009e-06
- `obs_raw_streaming_startup_clock_w`: 7.373444e-05
- `obs_raw_streaming_startup_sequential_w`: 1.349628e-04
- `obs_raw_streaming_startup_combinational_w`: 2.576769e-05
- `obs_raw_streaming_startup_total_a`: 6.512917e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.514560e-04
- `obs_raw_streaming_steady_internal_w`: 1.820486e-04
- `obs_raw_streaming_steady_switching_w`: 6.150892e-05
- `obs_raw_streaming_steady_leakage_w`: 7.898497e-06
- `obs_raw_streaming_steady_clock_w`: 7.373444e-05
- `obs_raw_streaming_steady_sequential_w`: 1.438836e-04
- `obs_raw_streaming_steady_combinational_w`: 3.383788e-05
- `obs_raw_streaming_steady_total_a`: 6.984889e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_125C_3v60 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_125C_3v60, interconnect `nom`).
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
