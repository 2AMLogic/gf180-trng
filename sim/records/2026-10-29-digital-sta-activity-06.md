---
record: 2026-10-29-digital-sta-activity-06
date: 2026-10-29T19:55:03Z
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
  spef_sha256: 34d1ffe50b2579680454a83798c966264feb9788b90779e2280ca95cf2024829
  spef_bytes: 1661196
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
  path: sim/records/raw/2026-10-29-digital-sta-activity-06/
  files:
    - uniform.tcl  sha256:ab733533c284cff36ad39410f0c4f0d24617a3cadccdc64a411ba59dc1ed42cd
    - uniform.log  sha256:0705b3c05f9882cd64465245bc314da61838319bcaec33502ccb0a57fde3c117
    - observed.tcl  sha256:39d66984291a1db1ac299bb0226168fc11f5fec3d8e11954763ca5de52357bf0
    - observed.log  sha256:57ad8d58b1f7899ca698e99dd4e9dcc26fdd0fd5c202091aaa24a01167054981
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 9.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    133.65 |     66.23 |      0.17 |    200.05 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     90.17 |     30.89 |      0.16 |    121.22 | 0.606 | 5143 / 0 |
| alarm-gated | startup | 1040 |     99.84 |     38.42 |      0.17 |    138.43 | 0.692 | 5143 / 0 |
| alarm-gated | steady | 1024 |     97.17 |     36.10 |      0.17 |    133.44 | 0.667 | 5143 / 0 |
| backpressure | reset | 8 |     90.13 |     30.80 |      0.16 |    121.09 | 0.605 | 5143 / 0 |
| backpressure | startup | 1040 |    100.04 |     38.55 |      0.17 |    138.76 | 0.694 | 5143 / 0 |
| backpressure | steady | 1024 |    105.79 |     42.80 |      0.17 |    148.76 | 0.744 | 5143 / 0 |
| conditioned-streaming | reset | 8 |     90.16 |     30.88 |      0.16 |    121.20 | 0.606 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    100.27 |     38.74 |      0.17 |    139.18 | 0.696 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    105.90 |     42.95 |      0.17 |    149.02 | 0.745 | 5143 / 0 |
| disabled-clock-running | reset | 8 |     89.70 |     30.33 |      0.16 |    120.20 | 0.601 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |     91.97 |     32.07 |      0.16 |    124.20 | 0.621 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |     91.88 |     32.01 |      0.16 |    124.06 | 0.620 | 5143 / 0 |
| raw-streaming | reset | 8 |     90.09 |     31.02 |      0.16 |    121.27 | 0.606 | 5143 / 0 |
| raw-streaming | startup | 1040 |    100.34 |     39.13 |      0.17 |    139.64 | 0.698 | 5143 / 0 |
| raw-streaming | steady | 1024 |    106.12 |     43.44 |      0.17 |    149.73 | 0.748 | 5143 / 0 |

- `uniform_total_w`: 2.000480e-04
- `uniform_internal_w`: 1.336538e-04
- `uniform_switching_w`: 6.622585e-05
- `uniform_leakage_w`: 1.683398e-07
- `uniform_clock_w`: 4.282159e-05
- `uniform_sequential_w`: 1.048079e-04
- `uniform_combinational_w`: 5.241850e-05
- `uniform_total_a`: 6.668267e-05
- `obs_alarm_gated_reset_total_w`: 1.212219e-04
- `obs_alarm_gated_reset_internal_w`: 9.016806e-05
- `obs_alarm_gated_reset_switching_w`: 3.089114e-05
- `obs_alarm_gated_reset_leakage_w`: 1.627358e-07
- `obs_alarm_gated_reset_clock_w`: 4.282159e-05
- `obs_alarm_gated_reset_sequential_w`: 7.548707e-05
- `obs_alarm_gated_reset_combinational_w`: 2.913232e-06
- `obs_alarm_gated_reset_total_a`: 4.040730e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.384267e-04
- `obs_alarm_gated_startup_internal_w`: 9.984099e-05
- `obs_alarm_gated_startup_switching_w`: 3.841841e-05
- `obs_alarm_gated_startup_leakage_w`: 1.673046e-07
- `obs_alarm_gated_startup_clock_w`: 4.282159e-05
- `obs_alarm_gated_startup_sequential_w`: 8.310608e-05
- `obs_alarm_gated_startup_combinational_w`: 1.249900e-05
- `obs_alarm_gated_startup_total_a`: 4.614223e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.334389e-04
- `obs_alarm_gated_steady_internal_w`: 9.717057e-05
- `obs_alarm_gated_steady_switching_w`: 3.610132e-05
- `obs_alarm_gated_steady_leakage_w`: 1.669966e-07
- `obs_alarm_gated_steady_clock_w`: 4.282159e-05
- `obs_alarm_gated_steady_sequential_w`: 8.161587e-05
- `obs_alarm_gated_steady_combinational_w`: 9.001496e-06
- `obs_alarm_gated_steady_total_a`: 4.447963e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.210914e-04
- `obs_backpressure_reset_internal_w`: 9.013001e-05
- `obs_backpressure_reset_switching_w`: 3.079867e-05
- `obs_backpressure_reset_leakage_w`: 1.627358e-07
- `obs_backpressure_reset_clock_w`: 4.282159e-05
- `obs_backpressure_reset_sequential_w`: 7.548021e-05
- `obs_backpressure_reset_combinational_w`: 2.789566e-06
- `obs_backpressure_reset_total_a`: 4.036380e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.387605e-04
- `obs_backpressure_startup_internal_w`: 1.000406e-04
- `obs_backpressure_startup_switching_w`: 3.855247e-05
- `obs_backpressure_startup_leakage_w`: 1.674532e-07
- `obs_backpressure_startup_clock_w`: 4.282159e-05
- `obs_backpressure_startup_sequential_w`: 8.318964e-05
- `obs_backpressure_startup_combinational_w`: 1.274926e-05
- `obs_backpressure_startup_total_a`: 4.625350e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.487583e-04
- `obs_backpressure_steady_internal_w`: 1.057912e-04
- `obs_backpressure_steady_switching_w`: 4.279750e-05
- `obs_backpressure_steady_leakage_w`: 1.696157e-07
- `obs_backpressure_steady_clock_w`: 4.282159e-05
- `obs_backpressure_steady_sequential_w`: 8.851135e-05
- `obs_backpressure_steady_combinational_w`: 1.742535e-05
- `obs_backpressure_steady_total_a`: 4.958610e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.212041e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.015973e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.088163e-05
- `obs_conditioned_streaming_reset_leakage_w`: 1.627358e-07
- `obs_conditioned_streaming_reset_clock_w`: 4.282159e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.548709e-05
- `obs_conditioned_streaming_reset_combinational_w`: 2.895370e-06
- `obs_conditioned_streaming_reset_total_a`: 4.040137e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.391808e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.002687e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.874497e-05
- `obs_conditioned_streaming_startup_leakage_w`: 1.671678e-07
- `obs_conditioned_streaming_startup_clock_w`: 4.282159e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.340010e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.295909e-05
- `obs_conditioned_streaming_startup_total_a`: 4.639360e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.490222e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.059015e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.295176e-05
- `obs_conditioned_streaming_steady_leakage_w`: 1.689615e-07
- `obs_conditioned_streaming_steady_clock_w`: 4.282159e-05
- `obs_conditioned_streaming_steady_sequential_w`: 8.854261e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.765801e-05
- `obs_conditioned_streaming_steady_total_a`: 4.967407e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.201974e-04
- `obs_disabled_clock_running_reset_internal_w`: 8.969985e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.033478e-05
- `obs_disabled_clock_running_reset_leakage_w`: 1.627358e-07
- `obs_disabled_clock_running_reset_clock_w`: 4.282159e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.545264e-05
- `obs_disabled_clock_running_reset_combinational_w`: 1.923111e-06
- `obs_disabled_clock_running_reset_total_a`: 4.006580e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.242038e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.197328e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.206560e-05
- `obs_disabled_clock_running_startup_leakage_w`: 1.649173e-07
- `obs_disabled_clock_running_startup_clock_w`: 4.282159e-05
- `obs_disabled_clock_running_startup_sequential_w`: 7.667664e-05
- `obs_disabled_clock_running_startup_combinational_w`: 4.705622e-06
- `obs_disabled_clock_running_startup_total_a`: 4.140127e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.240555e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.188301e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.200758e-05
- `obs_disabled_clock_running_steady_leakage_w`: 1.649168e-07
- `obs_disabled_clock_running_steady_clock_w`: 4.282159e-05
- `obs_disabled_clock_running_steady_sequential_w`: 7.671490e-05
- `obs_disabled_clock_running_steady_combinational_w`: 4.519020e-06
- `obs_disabled_clock_running_steady_total_a`: 4.135183e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.212723e-04
- `obs_raw_streaming_reset_internal_w`: 9.009288e-05
- `obs_raw_streaming_reset_switching_w`: 3.101672e-05
- `obs_raw_streaming_reset_leakage_w`: 1.627358e-07
- `obs_raw_streaming_reset_clock_w`: 4.282159e-05
- `obs_raw_streaming_reset_sequential_w`: 7.548508e-05
- `obs_raw_streaming_reset_combinational_w`: 2.965631e-06
- `obs_raw_streaming_reset_total_a`: 4.042410e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.396443e-04
- `obs_raw_streaming_startup_internal_w`: 1.003444e-04
- `obs_raw_streaming_startup_switching_w`: 3.913268e-05
- `obs_raw_streaming_startup_leakage_w`: 1.671805e-07
- `obs_raw_streaming_startup_clock_w`: 4.282159e-05
- `obs_raw_streaming_startup_sequential_w`: 8.323199e-05
- `obs_raw_streaming_startup_combinational_w`: 1.359073e-05
- `obs_raw_streaming_startup_total_a`: 4.654810e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.497306e-04
- `obs_raw_streaming_steady_internal_w`: 1.061244e-04
- `obs_raw_streaming_steady_switching_w`: 4.343663e-05
- `obs_raw_streaming_steady_leakage_w`: 1.695180e-07
- `obs_raw_streaming_steady_clock_w`: 4.282159e-05
- `obs_raw_streaming_steady_sequential_w`: 8.850684e-05
- `obs_raw_streaming_steady_combinational_w`: 1.840219e-05
- `obs_raw_streaming_steady_total_a`: 4.991020e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
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
