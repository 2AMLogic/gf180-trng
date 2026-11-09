---
record: 2026-10-29-digital-sta-activity-10
date: 2026-10-29T19:55:41Z
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
  spef_sha256: 1c24e1a13ddaae378730ae701a5cfba43eab5e80196e59d25b92df75530063ec
  spef_bytes: 1650518
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
  path: sim/records/raw/2026-10-29-digital-sta-activity-10/
  files:
    - uniform.tcl  sha256:9069678f5ca992a996b9aedacdd10d03423fe1a988ee5300310946fee56deca6
    - uniform.log  sha256:f29df21a160a2a7ca7f6f6bf9913cf5f28452278862ee290379cb56160c0b7f2
    - observed.tcl  sha256:625d2fa90b374c48126fa57cc2d6a38f1bffc2b8700f7c49c7aa75037f7b1b19
    - observed.log  sha256:21358f21919879b5ddf4580dbce94032e73f8f7293d5879efcde335c9daa629c
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 9.2s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    232.66 |     90.17 |      7.62 |    330.45 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    151.82 |     42.42 |      7.05 |    201.29 | 0.609 | 5143 / 0 |
| alarm-gated | startup | 1040 |    169.70 |     52.80 |      7.70 |    230.19 | 0.697 | 5143 / 0 |
| alarm-gated | steady | 1024 |    164.57 |     49.61 |      7.67 |    221.84 | 0.671 | 5143 / 0 |
| backpressure | reset | 8 |    151.75 |     42.30 |      7.05 |    201.10 | 0.609 | 5143 / 0 |
| backpressure | startup | 1040 |    170.07 |     52.98 |      7.66 |    230.71 | 0.698 | 5143 / 0 |
| backpressure | steady | 1024 |    180.62 |     58.81 |      7.98 |    247.40 | 0.749 | 5143 / 0 |
| conditioned-streaming | reset | 8 |    151.80 |     42.41 |      7.05 |    201.26 | 0.609 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    170.49 |     53.24 |      7.68 |    231.41 | 0.700 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    180.83 |     59.01 |      7.89 |    247.73 | 0.750 | 5143 / 0 |
| disabled-clock-running | reset | 8 |    150.90 |     41.66 |      7.05 |    199.62 | 0.604 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |    155.33 |     44.05 |      7.37 |    206.75 | 0.626 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |    155.16 |     43.98 |      7.37 |    206.51 | 0.625 | 5143 / 0 |
| raw-streaming | reset | 8 |    151.68 |     42.59 |      7.05 |    201.32 | 0.609 | 5143 / 0 |
| raw-streaming | startup | 1040 |    170.67 |     53.75 |      7.62 |    232.04 | 0.702 | 5143 / 0 |
| raw-streaming | steady | 1024 |    181.26 |     59.66 |      7.90 |    248.82 | 0.753 | 5143 / 0 |

- `uniform_total_w`: 3.304504e-04
- `uniform_internal_w`: 2.326648e-04
- `uniform_switching_w`: 9.016903e-05
- `uniform_leakage_w`: 7.616592e-06
- `uniform_clock_w`: 7.209987e-05
- `uniform_sequential_w`: 1.702998e-04
- `uniform_combinational_w`: 8.805077e-05
- `uniform_total_a`: 9.179178e-05
- `obs_alarm_gated_reset_total_w`: 2.012926e-04
- `obs_alarm_gated_reset_internal_w`: 1.518174e-04
- `obs_alarm_gated_reset_switching_w`: 4.242406e-05
- `obs_alarm_gated_reset_leakage_w`: 7.051153e-06
- `obs_alarm_gated_reset_clock_w`: 7.209987e-05
- `obs_alarm_gated_reset_sequential_w`: 1.218699e-04
- `obs_alarm_gated_reset_combinational_w`: 7.322943e-06
- `obs_alarm_gated_reset_total_a`: 5.591461e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.301929e-04
- `obs_alarm_gated_startup_internal_w`: 1.697014e-04
- `obs_alarm_gated_startup_switching_w`: 5.279524e-05
- `obs_alarm_gated_startup_leakage_w`: 7.696259e-06
- `obs_alarm_gated_startup_clock_w`: 7.209987e-05
- `obs_alarm_gated_startup_sequential_w`: 1.343059e-04
- `obs_alarm_gated_startup_combinational_w`: 2.378733e-05
- `obs_alarm_gated_startup_total_a`: 6.394247e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.218412e-04
- `obs_alarm_gated_steady_internal_w`: 1.645652e-04
- `obs_alarm_gated_steady_switching_w`: 4.960801e-05
- `obs_alarm_gated_steady_leakage_w`: 7.668041e-06
- `obs_alarm_gated_steady_clock_w`: 7.209987e-05
- `obs_alarm_gated_steady_sequential_w`: 1.319192e-04
- `obs_alarm_gated_steady_combinational_w`: 1.782209e-05
- `obs_alarm_gated_steady_total_a`: 6.162256e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.011003e-04
- `obs_backpressure_reset_internal_w`: 1.517527e-04
- `obs_backpressure_reset_switching_w`: 4.229652e-05
- `obs_backpressure_reset_leakage_w`: 7.051153e-06
- `obs_backpressure_reset_clock_w`: 7.209987e-05
- `obs_backpressure_reset_sequential_w`: 1.218589e-04
- `obs_backpressure_reset_combinational_w`: 7.141616e-06
- `obs_backpressure_reset_total_a`: 5.586119e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.307118e-04
- `obs_backpressure_startup_internal_w`: 1.700690e-04
- `obs_backpressure_startup_switching_w`: 5.297802e-05
- `obs_backpressure_startup_leakage_w`: 7.664829e-06
- `obs_backpressure_startup_clock_w`: 7.209987e-05
- `obs_backpressure_startup_sequential_w`: 1.344497e-04
- `obs_backpressure_startup_combinational_w`: 2.416252e-05
- `obs_backpressure_startup_total_a`: 6.408661e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.474040e-04
- `obs_backpressure_steady_internal_w`: 1.806178e-04
- `obs_backpressure_steady_switching_w`: 5.880927e-05
- `obs_backpressure_steady_leakage_w`: 7.976833e-06
- `obs_backpressure_steady_clock_w`: 7.209987e-05
- `obs_backpressure_steady_sequential_w`: 1.433684e-04
- `obs_backpressure_steady_combinational_w`: 3.193557e-05
- `obs_backpressure_steady_total_a`: 6.872333e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.012614e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.518022e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.240802e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.051153e-06
- `obs_conditioned_streaming_reset_clock_w`: 7.209987e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.218699e-04
- `obs_conditioned_streaming_reset_combinational_w`: 7.291721e-06
- `obs_conditioned_streaming_reset_total_a`: 5.590594e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.314052e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.704856e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.324295e-05
- `obs_conditioned_streaming_startup_leakage_w`: 7.676662e-06
- `obs_conditioned_streaming_startup_clock_w`: 7.209987e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.347626e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.454301e-05
- `obs_conditioned_streaming_startup_total_a`: 6.427922e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.477268e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.808277e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.901266e-05
- `obs_conditioned_streaming_steady_leakage_w`: 7.886476e-06
- `obs_conditioned_streaming_steady_clock_w`: 7.209987e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.433929e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.223426e-05
- `obs_conditioned_streaming_steady_total_a`: 6.881300e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.996180e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.509020e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.166479e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.051153e-06
- `obs_disabled_clock_running_reset_clock_w`: 7.209987e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.218099e-04
- `obs_disabled_clock_running_reset_combinational_w`: 5.708263e-06
- `obs_disabled_clock_running_reset_total_a`: 5.544944e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.067536e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.553330e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.405372e-05
- `obs_disabled_clock_running_startup_leakage_w`: 7.366870e-06
- `obs_disabled_clock_running_startup_clock_w`: 7.209987e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.240282e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.062562e-05
- `obs_disabled_clock_running_startup_total_a`: 5.743156e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.065072e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.551616e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.397819e-05
- `obs_disabled_clock_running_steady_leakage_w`: 7.367390e-06
- `obs_disabled_clock_running_steady_clock_w`: 7.209987e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.240820e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.032536e-05
- `obs_disabled_clock_running_steady_total_a`: 5.736311e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.013181e-04
- `obs_raw_streaming_reset_internal_w`: 1.516807e-04
- `obs_raw_streaming_reset_switching_w`: 4.258620e-05
- `obs_raw_streaming_reset_leakage_w`: 7.051153e-06
- `obs_raw_streaming_reset_clock_w`: 7.209987e-05
- `obs_raw_streaming_reset_sequential_w`: 1.218656e-04
- `obs_raw_streaming_reset_combinational_w`: 7.352778e-06
- `obs_raw_streaming_reset_total_a`: 5.592169e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.320404e-04
- `obs_raw_streaming_startup_internal_w`: 1.706696e-04
- `obs_raw_streaming_startup_switching_w`: 5.374875e-05
- `obs_raw_streaming_startup_leakage_w`: 7.622009e-06
- `obs_raw_streaming_startup_clock_w`: 7.209987e-05
- `obs_raw_streaming_startup_sequential_w`: 1.345058e-04
- `obs_raw_streaming_startup_combinational_w`: 2.543490e-05
- `obs_raw_streaming_startup_total_a`: 6.445567e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.488180e-04
- `obs_raw_streaming_steady_internal_w`: 1.812639e-04
- `obs_raw_streaming_steady_switching_w`: 5.965562e-05
- `obs_raw_streaming_steady_leakage_w`: 7.898497e-06
- `obs_raw_streaming_steady_clock_w`: 7.209987e-05
- `obs_raw_streaming_steady_sequential_w`: 1.433527e-04
- `obs_raw_streaming_steady_combinational_w`: 3.336512e-05
- `obs_raw_streaming_steady_total_a`: 6.911611e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
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
