---
record: 2026-11-09-digital-sta-activity-12
date: 2026-11-09T21:58:10Z
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
  - rules.openrcx.gf180mcuD.max (OpenRCX interconnect corner max, sha256:0ee103cf2108f2fd945087551b6dd1eaf4ee55af60571de2983878c8a271515f)
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
  interconnect: max (OpenRCX rule deck)
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
  spef_sha256: b9d55d75e62037706a4ca8e9a5e05bfea5f3f1756ad64e71924a6d4954ef02be
  spef_bytes: 1661195
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
  path: sim/records/raw/2026-11-09-digital-sta-activity-12/
  files:
    - uniform.tcl  sha256:95a78931d39f674d1636f0cdac5096fba1d6d08549fcaec53be6b79aa90a2842
    - uniform.log  sha256:7c63340e5c8f26e46ab2c2ada6d531db3047c54690e57745e56dcef84bf2bd2b
    - observed.tcl  sha256:4c02f8f561bff5fecc92d52ef47b7e3066998e97af60c0ae1bf0765491e90750
    - observed.log  sha256:acf1b0bb0de85d5bf05cc0d3ccbcde1a2e9abe9e4f5239f3b32cc4016da4c2aa
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 8.9s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    234.69 |     97.04 |      7.62 |    339.35 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    153.41 |     45.39 |      7.05 |    205.85 | 0.607 | 5143 / 0 |
| alarm-gated | startup | 1040 |    171.36 |     56.45 |      7.70 |    235.51 | 0.694 | 5143 / 0 |
| alarm-gated | steady | 1024 |    166.19 |     53.06 |      7.67 |    226.92 | 0.669 | 5143 / 0 |
| backpressure | reset | 8 |    153.35 |     45.26 |      7.05 |    205.65 | 0.606 | 5143 / 0 |
| backpressure | startup | 1040 |    171.73 |     56.64 |      7.66 |    236.04 | 0.696 | 5143 / 0 |
| backpressure | steady | 1024 |    182.37 |     62.86 |      7.98 |    253.20 | 0.746 | 5143 / 0 |
| conditioned-streaming | reset | 8 |    153.40 |     45.38 |      7.05 |    205.82 | 0.607 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    172.15 |     56.93 |      7.68 |    236.75 | 0.698 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    182.58 |     63.09 |      7.89 |    253.55 | 0.747 | 5143 / 0 |
| disabled-clock-running | reset | 8 |    152.49 |     44.57 |      7.05 |    204.12 | 0.601 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |    156.96 |     47.13 |      7.37 |    211.45 | 0.623 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |    156.78 |     47.04 |      7.37 |    211.19 | 0.622 | 5143 / 0 |
| raw-streaming | reset | 8 |    153.27 |     45.57 |      7.05 |    205.90 | 0.607 | 5143 / 0 |
| raw-streaming | startup | 1040 |    172.34 |     57.49 |      7.62 |    237.46 | 0.700 | 5143 / 0 |
| raw-streaming | steady | 1024 |    183.02 |     63.79 |      7.90 |    254.71 | 0.751 | 5143 / 0 |

- `uniform_total_w`: 3.393520e-04
- `uniform_internal_w`: 2.346911e-04
- `uniform_switching_w`: 9.704430e-05
- `uniform_leakage_w`: 7.616592e-06
- `uniform_clock_w`: 7.573952e-05
- `uniform_sequential_w`: 1.718254e-04
- `uniform_combinational_w`: 9.178715e-05
- `uniform_total_a`: 9.426444e-05
- `obs_alarm_gated_reset_total_w`: 2.058532e-04
- `obs_alarm_gated_reset_internal_w`: 1.534110e-04
- `obs_alarm_gated_reset_switching_w`: 4.539105e-05
- `obs_alarm_gated_reset_leakage_w`: 7.051153e-06
- `obs_alarm_gated_reset_clock_w`: 7.573952e-05
- `obs_alarm_gated_reset_sequential_w`: 1.226016e-04
- `obs_alarm_gated_reset_combinational_w`: 7.512216e-06
- `obs_alarm_gated_reset_total_a`: 5.718144e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.355077e-04
- `obs_alarm_gated_startup_internal_w`: 1.713648e-04
- `obs_alarm_gated_startup_switching_w`: 5.644666e-05
- `obs_alarm_gated_startup_leakage_w`: 7.696259e-06
- `obs_alarm_gated_startup_clock_w`: 7.573952e-05
- `obs_alarm_gated_startup_sequential_w`: 1.353372e-04
- `obs_alarm_gated_startup_combinational_w`: 2.443113e-05
- `obs_alarm_gated_startup_total_a`: 6.541881e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.269164e-04
- `obs_alarm_gated_steady_internal_w`: 1.661925e-04
- `obs_alarm_gated_steady_switching_w`: 5.305584e-05
- `obs_alarm_gated_steady_leakage_w`: 7.668041e-06
- `obs_alarm_gated_steady_clock_w`: 7.573952e-05
- `obs_alarm_gated_steady_sequential_w`: 1.328948e-04
- `obs_alarm_gated_steady_combinational_w`: 1.828204e-05
- `obs_alarm_gated_steady_total_a`: 6.303233e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.056532e-04
- `obs_backpressure_reset_internal_w`: 1.533464e-04
- `obs_backpressure_reset_switching_w`: 4.525569e-05
- `obs_backpressure_reset_leakage_w`: 7.051153e-06
- `obs_backpressure_reset_clock_w`: 7.573952e-05
- `obs_backpressure_reset_sequential_w`: 1.225907e-04
- `obs_backpressure_reset_combinational_w`: 7.323140e-06
- `obs_backpressure_reset_total_a`: 5.712589e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.360425e-04
- `obs_backpressure_startup_internal_w`: 1.717341e-04
- `obs_backpressure_startup_switching_w`: 5.664354e-05
- `obs_backpressure_startup_leakage_w`: 7.664829e-06
- `obs_backpressure_startup_clock_w`: 7.573952e-05
- `obs_backpressure_startup_sequential_w`: 1.354831e-04
- `obs_backpressure_startup_combinational_w`: 2.481999e-05
- `obs_backpressure_startup_total_a`: 6.556736e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.532036e-04
- `obs_backpressure_steady_internal_w`: 1.823670e-04
- `obs_backpressure_steady_switching_w`: 6.285977e-05
- `obs_backpressure_steady_leakage_w`: 7.976833e-06
- `obs_backpressure_steady_clock_w`: 7.573952e-05
- `obs_backpressure_steady_sequential_w`: 1.445679e-04
- `obs_backpressure_steady_combinational_w`: 3.289628e-05
- `obs_backpressure_steady_total_a`: 7.033433e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.058237e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.533959e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.537671e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.051153e-06
- `obs_conditioned_streaming_reset_clock_w`: 7.573952e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.226016e-04
- `obs_conditioned_streaming_reset_combinational_w`: 7.482685e-06
- `obs_conditioned_streaming_reset_total_a`: 5.717325e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.367550e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.721523e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.692609e-05
- `obs_conditioned_streaming_startup_leakage_w`: 7.676662e-06
- `obs_conditioned_streaming_startup_clock_w`: 7.573952e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.358060e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.520957e-05
- `obs_conditioned_streaming_startup_total_a`: 6.576528e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.535505e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.825790e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.308504e-05
- `obs_conditioned_streaming_steady_leakage_w`: 7.886476e-06
- `obs_conditioned_streaming_steady_clock_w`: 7.573952e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.445969e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.321422e-05
- `obs_conditioned_streaming_steady_total_a`: 7.043069e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 2.041179e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.524918e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.457493e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.051153e-06
- `obs_disabled_clock_running_reset_clock_w`: 7.573952e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.225414e-04
- `obs_disabled_clock_running_reset_combinational_w`: 5.836931e-06
- `obs_disabled_clock_running_reset_total_a`: 5.669942e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.114513e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.569551e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.712943e-05
- `obs_disabled_clock_running_startup_leakage_w`: 7.366870e-06
- `obs_disabled_clock_running_startup_clock_w`: 7.573952e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.248111e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.090081e-05
- `obs_disabled_clock_running_startup_total_a`: 5.873647e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.111938e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.567816e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.704477e-05
- `obs_disabled_clock_running_steady_leakage_w`: 7.367390e-06
- `obs_disabled_clock_running_steady_clock_w`: 7.573952e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.248668e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.058758e-05
- `obs_disabled_clock_running_steady_total_a`: 5.866494e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.058982e-04
- `obs_raw_streaming_reset_internal_w`: 1.532737e-04
- `obs_raw_streaming_reset_switching_w`: 4.557332e-05
- `obs_raw_streaming_reset_leakage_w`: 7.051153e-06
- `obs_raw_streaming_reset_clock_w`: 7.573952e-05
- `obs_raw_streaming_reset_sequential_w`: 1.225973e-04
- `obs_raw_streaming_reset_combinational_w`: 7.561467e-06
- `obs_raw_streaming_reset_total_a`: 5.719394e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.374551e-04
- `obs_raw_streaming_startup_internal_w`: 1.723422e-04
- `obs_raw_streaming_startup_switching_w`: 5.749088e-05
- `obs_raw_streaming_startup_leakage_w`: 7.622009e-06
- `obs_raw_streaming_startup_clock_w`: 7.573952e-05
- `obs_raw_streaming_startup_sequential_w`: 1.355403e-04
- `obs_raw_streaming_startup_combinational_w`: 2.617528e-05
- `obs_raw_streaming_startup_total_a`: 6.595975e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.547104e-04
- `obs_raw_streaming_steady_internal_w`: 1.830198e-04
- `obs_raw_streaming_steady_switching_w`: 6.379209e-05
- `obs_raw_streaming_steady_leakage_w`: 7.898497e-06
- `obs_raw_streaming_steady_clock_w`: 7.573952e-05
- `obs_raw_streaming_steady_sequential_w`: 1.445526e-04
- `obs_raw_streaming_steady_combinational_w`: 3.441825e-05
- `obs_raw_streaming_steady_total_a`: 7.075289e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_125C_3v60 --rc max --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_125C_3v60, interconnect `max`).
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
