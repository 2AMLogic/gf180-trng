---
record: 2026-10-29-digital-sta-activity-11
date: 2026-10-29T19:55:50Z
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
repo_commit: 16fd09fb792db7bf363afd70ec8f8370e1c2d90b-dirty

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
  spef_sha256: 8264a6fedf52f11a0d3afe0c4bcdfe95d1deadaa327c5b39778028ce1830f2b4
  spef_bytes: 1654158
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
  path: sim/records/raw/2026-10-29-digital-sta-activity-11/
  files:
    - uniform.tcl  sha256:c99ecfb0a8f173b1dd9463f5e805dbee10097da63a032eec2118b2e72abe09d6
    - uniform.log  sha256:361682fdac8a55b3e4c703871fe22a7fcf5b0778b38b49bdf69c97aded0d454d
    - observed.tcl  sha256:b2ab1c012ed40a956702d06ca35f2f5b02e3b14b495ce598cb00e44557884d74
    - observed.log  sha256:f6a9d4c74bc7cbd7d2d6d7e3ae74e261f834bf02d3aaf2c31c603e9fe2d27ad0
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 9.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    233.57 |     93.25 |      7.62 |    334.43 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    152.53 |     43.75 |      7.05 |    203.33 | 0.608 | 5143 / 0 |
| alarm-gated | startup | 1040 |    170.44 |     54.43 |      7.70 |    232.57 | 0.695 | 5143 / 0 |
| alarm-gated | steady | 1024 |    165.29 |     51.15 |      7.67 |    224.11 | 0.670 | 5143 / 0 |
| backpressure | reset | 8 |    152.46 |     43.62 |      7.05 |    203.14 | 0.607 | 5143 / 0 |
| backpressure | startup | 1040 |    170.81 |     54.62 |      7.66 |    233.09 | 0.697 | 5143 / 0 |
| backpressure | steady | 1024 |    181.40 |     60.62 |      7.98 |    250.00 | 0.748 | 5143 / 0 |
| conditioned-streaming | reset | 8 |    152.51 |     43.74 |      7.05 |    203.30 | 0.608 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    171.23 |     54.89 |      7.68 |    233.80 | 0.699 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    181.61 |     60.84 |      7.89 |    250.33 | 0.749 | 5143 / 0 |
| disabled-clock-running | reset | 8 |    151.61 |     42.97 |      7.05 |    201.63 | 0.603 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |    156.05 |     45.43 |      7.37 |    208.85 | 0.624 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |    155.88 |     45.35 |      7.37 |    208.60 | 0.624 | 5143 / 0 |
| raw-streaming | reset | 8 |    152.39 |     43.92 |      7.05 |    203.37 | 0.608 | 5143 / 0 |
| raw-streaming | startup | 1040 |    171.41 |     55.43 |      7.62 |    234.46 | 0.701 | 5143 / 0 |
| raw-streaming | steady | 1024 |    182.04 |     61.51 |      7.90 |    251.45 | 0.752 | 5143 / 0 |

- `uniform_total_w`: 3.344346e-04
- `uniform_internal_w`: 2.335651e-04
- `uniform_switching_w`: 9.325296e-05
- `uniform_leakage_w`: 7.616592e-06
- `uniform_clock_w`: 7.373228e-05
- `uniform_sequential_w`: 1.709767e-04
- `uniform_combinational_w`: 8.972581e-05
- `uniform_total_a`: 9.289850e-05
- `obs_alarm_gated_reset_total_w`: 2.033318e-04
- `obs_alarm_gated_reset_internal_w`: 1.525279e-04
- `obs_alarm_gated_reset_switching_w`: 4.375281e-05
- `obs_alarm_gated_reset_leakage_w`: 7.051153e-06
- `obs_alarm_gated_reset_clock_w`: 7.373228e-05
- `obs_alarm_gated_reset_sequential_w`: 1.221910e-04
- `obs_alarm_gated_reset_combinational_w`: 7.408707e-06
- `obs_alarm_gated_reset_total_a`: 5.648106e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.325690e-04
- `obs_alarm_gated_startup_internal_w`: 1.704416e-04
- `obs_alarm_gated_startup_switching_w`: 5.443112e-05
- `obs_alarm_gated_startup_leakage_w`: 7.696259e-06
- `obs_alarm_gated_startup_clock_w`: 7.373228e-05
- `obs_alarm_gated_startup_sequential_w`: 1.347614e-04
- `obs_alarm_gated_startup_combinational_w`: 2.407539e-05
- `obs_alarm_gated_startup_total_a`: 6.460250e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.241098e-04
- `obs_alarm_gated_steady_internal_w`: 1.652898e-04
- `obs_alarm_gated_steady_switching_w`: 5.115203e-05
- `obs_alarm_gated_steady_leakage_w`: 7.668041e-06
- `obs_alarm_gated_steady_clock_w`: 7.373228e-05
- `obs_alarm_gated_steady_sequential_w`: 1.323494e-04
- `obs_alarm_gated_steady_combinational_w`: 1.802794e-05
- `obs_alarm_gated_steady_total_a`: 6.225272e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.031362e-04
- `obs_backpressure_reset_internal_w`: 1.524632e-04
- `obs_backpressure_reset_switching_w`: 4.362178e-05
- `obs_backpressure_reset_leakage_w`: 7.051153e-06
- `obs_backpressure_reset_clock_w`: 7.373228e-05
- `obs_backpressure_reset_sequential_w`: 1.221800e-04
- `obs_backpressure_reset_combinational_w`: 7.223941e-06
- `obs_backpressure_reset_total_a`: 5.642672e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.330949e-04
- `obs_backpressure_startup_internal_w`: 1.708099e-04
- `obs_backpressure_startup_switching_w`: 5.462023e-05
- `obs_backpressure_startup_leakage_w`: 7.664829e-06
- `obs_backpressure_startup_clock_w`: 7.373228e-05
- `obs_backpressure_startup_sequential_w`: 1.349061e-04
- `obs_backpressure_startup_combinational_w`: 2.445668e-05
- `obs_backpressure_startup_total_a`: 6.474858e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.499968e-04
- `obs_backpressure_steady_internal_w`: 1.813960e-04
- `obs_backpressure_steady_switching_w`: 6.062400e-05
- `obs_backpressure_steady_leakage_w`: 7.976833e-06
- `obs_backpressure_steady_clock_w`: 7.373228e-05
- `obs_backpressure_steady_sequential_w`: 1.438990e-04
- `obs_backpressure_steady_combinational_w`: 3.236548e-05
- `obs_backpressure_steady_total_a`: 6.944356e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.033014e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.525127e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.373753e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.051153e-06
- `obs_conditioned_streaming_reset_clock_w`: 7.373228e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.221910e-04
- `obs_conditioned_streaming_reset_combinational_w`: 7.378242e-06
- `obs_conditioned_streaming_reset_total_a`: 5.647261e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.337969e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.712272e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.489303e-05
- `obs_conditioned_streaming_startup_leakage_w`: 7.676662e-06
- `obs_conditioned_streaming_startup_clock_w`: 7.373228e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.352234e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.484121e-05
- `obs_conditioned_streaming_startup_total_a`: 6.494358e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.503305e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.816068e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.083725e-05
- `obs_conditioned_streaming_steady_leakage_w`: 7.886476e-06
- `obs_conditioned_streaming_steady_clock_w`: 7.373228e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.439255e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.267276e-05
- `obs_conditioned_streaming_steady_total_a`: 6.953625e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 2.016292e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.516101e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.296792e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.051153e-06
- `obs_disabled_clock_running_reset_clock_w`: 7.373228e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.221309e-04
- `obs_disabled_clock_running_reset_combinational_w`: 5.766085e-06
- `obs_disabled_clock_running_reset_total_a`: 5.600811e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.088530e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.560548e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.543126e-05
- `obs_disabled_clock_running_startup_leakage_w`: 7.366870e-06
- `obs_disabled_clock_running_startup_clock_w`: 7.373228e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.243723e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.074837e-05
- `obs_disabled_clock_running_startup_total_a`: 5.801472e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.086016e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.558826e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.535163e-05
- `obs_disabled_clock_running_steady_leakage_w`: 7.367390e-06
- `obs_disabled_clock_running_steady_clock_w`: 7.373228e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.244270e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.044234e-05
- `obs_disabled_clock_running_steady_total_a`: 5.794489e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.033659e-04
- `obs_raw_streaming_reset_internal_w`: 1.523908e-04
- `obs_raw_streaming_reset_switching_w`: 4.392394e-05
- `obs_raw_streaming_reset_leakage_w`: 7.051153e-06
- `obs_raw_streaming_reset_clock_w`: 7.373228e-05
- `obs_raw_streaming_reset_sequential_w`: 1.221866e-04
- `obs_raw_streaming_reset_combinational_w`: 7.447110e-06
- `obs_raw_streaming_reset_total_a`: 5.649053e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.344612e-04
- `obs_raw_streaming_startup_internal_w`: 1.714138e-04
- `obs_raw_streaming_startup_switching_w`: 5.542539e-05
- `obs_raw_streaming_startup_leakage_w`: 7.622009e-06
- `obs_raw_streaming_startup_clock_w`: 7.373228e-05
- `obs_raw_streaming_startup_sequential_w`: 1.349627e-04
- `obs_raw_streaming_startup_combinational_w`: 2.576621e-05
- `obs_raw_streaming_startup_total_a`: 6.512811e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.514522e-04
- `obs_raw_streaming_steady_internal_w`: 1.820448e-04
- `obs_raw_streaming_steady_switching_w`: 6.150892e-05
- `obs_raw_streaming_steady_leakage_w`: 7.898497e-06
- `obs_raw_streaming_steady_clock_w`: 7.373228e-05
- `obs_raw_streaming_steady_sequential_w`: 1.438835e-04
- `obs_raw_streaming_steady_combinational_w`: 3.383640e-05
- `obs_raw_streaming_steady_total_a`: 6.984783e-05
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
