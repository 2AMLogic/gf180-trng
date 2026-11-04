---
record: 2026-10-29-digital-sta-activity-14
date: 2026-10-29T19:56:18Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60.lib (liberty corner ff_n40C_3v60, sha256:0b48b93d6800da325a2613ff6c0b998b230a1bbd28031f6da592e9ff30066602)
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
  temperature: -40
  liberty: gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60
  interconnect: nom (OpenRCX rule deck)
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
  spef_sha256: 54b05a07294bf55d20dcf13609e58f0ee94c662f3ac2ff09df7a6e763e20100f
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
  path: sim/records/raw/2026-10-29-digital-sta-activity-14/
  files:
    - uniform.tcl  sha256:0db5eadd0db3d4d76cd45efa3eeb6e5de5e50c0acd77eec1773b52da29ad807a
    - uniform.log  sha256:a5491e61ca3d3b8c29bea55eaa5d5f315ed5e55e3cacb66c8b44918ca3d492fe
    - observed.tcl  sha256:8685164bdd29d54b23575a80ec232c52503f87eafcc8397c4b3afdbb48915157
    - observed.log  sha256:f3a6869a21b24c9f809b062e0bf15993da4efcbd7c8cc8628563ba332043d22d
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 9.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    212.72 |     92.83 |      0.25 |    305.80 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    140.69 |     43.52 |      0.24 |    184.46 | 0.603 | 5143 / 0 |
| alarm-gated | startup | 1040 |    156.54 |     54.16 |      0.25 |    210.94 | 0.690 | 5143 / 0 |
| alarm-gated | steady | 1024 |    152.02 |     50.90 |      0.25 |    203.17 | 0.664 | 5143 / 0 |
| backpressure | reset | 8 |    140.64 |     43.39 |      0.24 |    184.27 | 0.603 | 5143 / 0 |
| backpressure | startup | 1040 |    156.86 |     54.35 |      0.25 |    211.46 | 0.691 | 5143 / 0 |
| backpressure | steady | 1024 |    166.24 |     60.33 |      0.25 |    226.82 | 0.742 | 5143 / 0 |
| conditioned-streaming | reset | 8 |    140.68 |     43.51 |      0.24 |    184.43 | 0.603 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    157.23 |     54.62 |      0.25 |    212.10 | 0.694 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    166.42 |     60.54 |      0.25 |    227.21 | 0.743 | 5143 / 0 |
| disabled-clock-running | reset | 8 |    139.89 |     42.74 |      0.24 |    182.87 | 0.598 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |    143.75 |     45.19 |      0.24 |    189.18 | 0.619 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |    143.60 |     45.11 |      0.24 |    188.95 | 0.618 | 5143 / 0 |
| raw-streaming | reset | 8 |    140.57 |     43.69 |      0.24 |    184.50 | 0.603 | 5143 / 0 |
| raw-streaming | startup | 1040 |    157.39 |     55.15 |      0.25 |    212.79 | 0.696 | 5143 / 0 |
| raw-streaming | steady | 1024 |    166.81 |     61.21 |      0.25 |    228.27 | 0.746 | 5143 / 0 |

- `uniform_total_w`: 3.057960e-04
- `uniform_internal_w`: 2.127151e-04
- `uniform_switching_w`: 9.283037e-05
- `uniform_leakage_w`: 2.504850e-07
- `uniform_clock_w`: 6.706228e-05
- `uniform_sequential_w`: 1.581019e-04
- `uniform_combinational_w`: 8.063171e-05
- `uniform_total_a`: 8.494333e-05
- `obs_alarm_gated_reset_total_w`: 1.844579e-04
- `obs_alarm_gated_reset_internal_w`: 1.406947e-04
- `obs_alarm_gated_reset_switching_w`: 4.352353e-05
- `obs_alarm_gated_reset_leakage_w`: 2.396281e-07
- `obs_alarm_gated_reset_clock_w`: 6.706228e-05
- `obs_alarm_gated_reset_sequential_w`: 1.130408e-04
- `obs_alarm_gated_reset_combinational_w`: 4.354773e-06
- `obs_alarm_gated_reset_total_a`: 5.123831e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.109430e-04
- `obs_alarm_gated_startup_internal_w`: 1.565381e-04
- `obs_alarm_gated_startup_switching_w`: 5.415790e-05
- `obs_alarm_gated_startup_leakage_w`: 2.469438e-07
- `obs_alarm_gated_startup_clock_w`: 6.706228e-05
- `obs_alarm_gated_startup_sequential_w`: 1.245188e-04
- `obs_alarm_gated_startup_combinational_w`: 1.936215e-05
- `obs_alarm_gated_startup_total_a`: 5.859528e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.031670e-04
- `obs_alarm_gated_steady_internal_w`: 1.520243e-04
- `obs_alarm_gated_steady_switching_w`: 5.089612e-05
- `obs_alarm_gated_steady_leakage_w`: 2.465043e-07
- `obs_alarm_gated_steady_clock_w`: 6.706228e-05
- `obs_alarm_gated_steady_sequential_w`: 1.222627e-04
- `obs_alarm_gated_steady_combinational_w`: 1.384213e-05
- `obs_alarm_gated_steady_total_a`: 5.643528e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.842686e-04
- `obs_backpressure_reset_internal_w`: 1.406356e-04
- `obs_backpressure_reset_switching_w`: 4.339337e-05
- `obs_backpressure_reset_leakage_w`: 2.396281e-07
- `obs_backpressure_reset_clock_w`: 6.706228e-05
- `obs_backpressure_reset_sequential_w`: 1.130306e-04
- `obs_backpressure_reset_combinational_w`: 4.175690e-06
- `obs_backpressure_reset_total_a`: 5.118572e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.114569e-04
- `obs_backpressure_startup_internal_w`: 1.568631e-04
- `obs_backpressure_startup_switching_w`: 5.434651e-05
- `obs_backpressure_startup_leakage_w`: 2.472493e-07
- `obs_backpressure_startup_clock_w`: 6.706228e-05
- `obs_backpressure_startup_sequential_w`: 1.246476e-04
- `obs_backpressure_startup_combinational_w`: 1.974723e-05
- `obs_backpressure_startup_total_a`: 5.873803e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.268187e-04
- `obs_backpressure_steady_internal_w`: 1.662403e-04
- `obs_backpressure_steady_switching_w`: 6.032661e-05
- `obs_backpressure_steady_leakage_w`: 2.518242e-07
- `obs_backpressure_steady_clock_w`: 6.706228e-05
- `obs_backpressure_steady_sequential_w`: 1.328710e-04
- `obs_backpressure_steady_combinational_w`: 2.688541e-05
- `obs_backpressure_steady_total_a`: 6.300519e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.844290e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.406808e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.350856e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.396281e-07
- `obs_conditioned_streaming_reset_clock_w`: 6.706228e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.130408e-04
- `obs_conditioned_streaming_reset_combinational_w`: 4.325879e-06
- `obs_conditioned_streaming_reset_total_a`: 5.123028e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.120990e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.572336e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.461879e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.466174e-07
- `obs_conditioned_streaming_startup_clock_w`: 6.706228e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.249612e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.007570e-05
- `obs_conditioned_streaming_startup_total_a`: 5.891639e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.272144e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.664245e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.053931e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.505825e-07
- `obs_conditioned_streaming_steady_clock_w`: 6.706228e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.329133e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.723892e-05
- `obs_conditioned_streaming_steady_total_a`: 6.311511e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.828670e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.398855e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.274186e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.396281e-07
- `obs_disabled_clock_running_reset_clock_w`: 6.706228e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.129869e-04
- `obs_disabled_clock_running_reset_combinational_w`: 2.817759e-06
- `obs_disabled_clock_running_reset_total_a`: 5.079639e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.891793e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.437472e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.518982e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.422249e-07
- `obs_disabled_clock_running_startup_clock_w`: 6.706228e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.148218e-04
- `obs_disabled_clock_running_startup_combinational_w`: 7.295172e-06
- `obs_disabled_clock_running_startup_total_a`: 5.254981e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.889504e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.435979e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.511035e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.422247e-07
- `obs_disabled_clock_running_steady_clock_w`: 6.706228e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.148765e-04
- `obs_disabled_clock_running_steady_combinational_w`: 7.011676e-06
- `obs_disabled_clock_running_steady_total_a`: 5.248622e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.844993e-04
- `obs_raw_streaming_reset_internal_w`: 1.405661e-04
- `obs_raw_streaming_reset_switching_w`: 4.369357e-05
- `obs_raw_streaming_reset_leakage_w`: 2.396281e-07
- `obs_raw_streaming_reset_clock_w`: 6.706228e-05
- `obs_raw_streaming_reset_sequential_w`: 1.130372e-04
- `obs_raw_streaming_reset_combinational_w`: 4.399812e-06
- `obs_raw_streaming_reset_total_a`: 5.124981e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.127870e-04
- `obs_raw_streaming_startup_internal_w`: 1.573919e-04
- `obs_raw_streaming_startup_switching_w`: 5.514838e-05
- `obs_raw_streaming_startup_leakage_w`: 2.467104e-07
- `obs_raw_streaming_startup_clock_w`: 6.706228e-05
- `obs_raw_streaming_startup_sequential_w`: 1.247088e-04
- `obs_raw_streaming_startup_combinational_w`: 2.101590e-05
- `obs_raw_streaming_startup_total_a`: 5.910750e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.282689e-04
- `obs_raw_streaming_steady_internal_w`: 1.668094e-04
- `obs_raw_streaming_steady_switching_w`: 6.120792e-05
- `obs_raw_streaming_steady_leakage_w`: 2.516184e-07
- `obs_raw_streaming_steady_clock_w`: 6.706228e-05
- `obs_raw_streaming_steady_sequential_w`: 1.328614e-04
- `obs_raw_streaming_steady_combinational_w`: 2.834523e-05
- `obs_raw_streaming_steady_total_a`: 6.340803e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_n40C_3v60 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_n40C_3v60, interconnect `nom`).
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
