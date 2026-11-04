---
record: 2026-10-29-digital-sta-activity-05
date: 2026-10-29T19:54:54Z
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
  - rules.openrcx.gf180mcuD.nom (OpenRCX interconnect corner nom, sha256:d83a04ea28af9b74a097fb479bbab9ed52859a1e3428b33d3151cb5afae62ddf)
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
  interconnect: nom (OpenRCX rule deck)
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
  spef_sha256: 782ea115c1171cdbc4f262e4aac61481e59d389edeee78e5c030aab4f396569e
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
  path: sim/records/raw/2026-10-29-digital-sta-activity-05/
  files:
    - uniform.tcl  sha256:3145997af9f8332d13f377adf6de6f56f1c0d5941d7b9d0275a6c552d0a87e1a
    - uniform.log  sha256:a406739d98cb1efbbd1cf976c1f447fe93cd3430b75144d414471b87e035cdbf
    - observed.tcl  sha256:7dae51fc746062a4f25b84bc2ad2cb9b3bbebed40e940392d3cf5d1ece72febd
    - observed.log  sha256:d3cdc25b9fbacea6cebd2a76ed79f0b954a11e6443ed0fc92aa43a6d98317ef1
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 9.0s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    133.59 |     63.59 |      0.17 |    197.35 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     90.12 |     29.75 |      0.16 |    120.04 | 0.608 | 5143 / 0 |
| alarm-gated | startup | 1040 |     99.79 |     37.02 |      0.17 |    136.98 | 0.694 | 5143 / 0 |
| alarm-gated | steady | 1024 |     97.12 |     34.78 |      0.17 |    132.07 | 0.669 | 5143 / 0 |
| backpressure | reset | 8 |     90.09 |     29.66 |      0.16 |    119.91 | 0.608 | 5143 / 0 |
| backpressure | startup | 1040 |     99.99 |     37.15 |      0.17 |    137.31 | 0.696 | 5143 / 0 |
| backpressure | steady | 1024 |    105.74 |     41.24 |      0.17 |    147.16 | 0.746 | 5143 / 0 |
| conditioned-streaming | reset | 8 |     90.11 |     29.74 |      0.16 |    120.02 | 0.608 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    100.22 |     37.33 |      0.17 |    137.72 | 0.698 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    105.85 |     41.39 |      0.17 |    147.41 | 0.747 | 5143 / 0 |
| disabled-clock-running | reset | 8 |     89.66 |     29.22 |      0.16 |    119.04 | 0.603 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |     91.93 |     30.89 |      0.16 |    122.98 | 0.623 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |     91.84 |     30.83 |      0.16 |    122.83 | 0.622 | 5143 / 0 |
| raw-streaming | reset | 8 |     90.05 |     29.87 |      0.16 |    120.08 | 0.608 | 5143 / 0 |
| raw-streaming | startup | 1040 |    100.30 |     37.70 |      0.17 |    138.16 | 0.700 | 5143 / 0 |
| raw-streaming | steady | 1024 |    106.07 |     41.85 |      0.17 |    148.09 | 0.750 | 5143 / 0 |

- `uniform_total_w`: 1.973483e-04
- `uniform_internal_w`: 1.335869e-04
- `uniform_switching_w`: 6.359304e-05
- `uniform_leakage_w`: 1.683398e-07
- `uniform_clock_w`: 4.170556e-05
- `uniform_sequential_w`: 1.045174e-04
- `uniform_combinational_w`: 5.112523e-05
- `uniform_total_a`: 6.578277e-05
- `obs_alarm_gated_reset_total_w`: 1.200394e-04
- `obs_alarm_gated_reset_internal_w`: 9.012315e-05
- `obs_alarm_gated_reset_switching_w`: 2.975348e-05
- `obs_alarm_gated_reset_leakage_w`: 1.627358e-07
- `obs_alarm_gated_reset_clock_w`: 4.170556e-05
- `obs_alarm_gated_reset_sequential_w`: 7.548798e-05
- `obs_alarm_gated_reset_combinational_w`: 2.845824e-06
- `obs_alarm_gated_reset_total_a`: 4.001313e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.369797e-04
- `obs_alarm_gated_startup_internal_w`: 9.979369e-05
- `obs_alarm_gated_startup_switching_w`: 3.701869e-05
- `obs_alarm_gated_startup_leakage_w`: 1.673046e-07
- `obs_alarm_gated_startup_clock_w`: 4.170556e-05
- `obs_alarm_gated_startup_sequential_w`: 8.299311e-05
- `obs_alarm_gated_startup_combinational_w`: 1.228106e-05
- `obs_alarm_gated_startup_total_a`: 4.565990e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.320711e-04
- `obs_alarm_gated_steady_internal_w`: 9.712484e-05
- `obs_alarm_gated_steady_switching_w`: 3.477923e-05
- `obs_alarm_gated_steady_leakage_w`: 1.669966e-07
- `obs_alarm_gated_steady_clock_w`: 4.170556e-05
- `obs_alarm_gated_steady_sequential_w`: 8.152346e-05
- `obs_alarm_gated_steady_combinational_w`: 8.842113e-06
- `obs_alarm_gated_steady_total_a`: 4.402370e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.199118e-04
- `obs_backpressure_reset_internal_w`: 9.008506e-05
- `obs_backpressure_reset_switching_w`: 2.966401e-05
- `obs_backpressure_reset_leakage_w`: 1.627358e-07
- `obs_backpressure_reset_clock_w`: 4.170556e-05
- `obs_backpressure_reset_sequential_w`: 7.548111e-05
- `obs_backpressure_reset_combinational_w`: 2.725147e-06
- `obs_backpressure_reset_total_a`: 3.997060e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.373081e-04
- `obs_backpressure_startup_internal_w`: 9.999323e-05
- `obs_backpressure_startup_switching_w`: 3.714739e-05
- `obs_backpressure_startup_leakage_w`: 1.674532e-07
- `obs_backpressure_startup_clock_w`: 4.170556e-05
- `obs_backpressure_startup_sequential_w`: 8.307584e-05
- `obs_backpressure_startup_combinational_w`: 1.252667e-05
- `obs_backpressure_startup_total_a`: 4.576937e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.471556e-04
- `obs_backpressure_steady_internal_w`: 1.057411e-04
- `obs_backpressure_steady_switching_w`: 4.124486e-05
- `obs_backpressure_steady_leakage_w`: 1.696157e-07
- `obs_backpressure_steady_clock_w`: 4.170556e-05
- `obs_backpressure_steady_sequential_w`: 8.834071e-05
- `obs_backpressure_steady_combinational_w`: 1.710926e-05
- `obs_backpressure_steady_total_a`: 4.905187e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.200208e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.011478e-05
- `obs_conditioned_streaming_reset_switching_w`: 2.974331e-05
- `obs_conditioned_streaming_reset_leakage_w`: 1.627358e-07
- `obs_conditioned_streaming_reset_clock_w`: 4.170556e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.548799e-05
- `obs_conditioned_streaming_reset_combinational_w`: 2.827287e-06
- `obs_conditioned_streaming_reset_total_a`: 4.000693e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.377215e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.002212e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.733311e-05
- `obs_conditioned_streaming_startup_leakage_w`: 1.671678e-07
- `obs_conditioned_streaming_startup_clock_w`: 4.170556e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.328247e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.273357e-05
- `obs_conditioned_streaming_startup_total_a`: 4.590717e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.474110e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.058513e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.139082e-05
- `obs_conditioned_streaming_steady_leakage_w`: 1.689615e-07
- `obs_conditioned_streaming_steady_clock_w`: 4.170556e-05
- `obs_conditioned_streaming_steady_sequential_w`: 8.837025e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.733520e-05
- `obs_conditioned_streaming_steady_total_a`: 4.913700e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.190368e-04
- `obs_disabled_clock_running_reset_internal_w`: 8.965528e-05
- `obs_disabled_clock_running_reset_switching_w`: 2.921880e-05
- `obs_disabled_clock_running_reset_leakage_w`: 1.627358e-07
- `obs_disabled_clock_running_reset_clock_w`: 4.170556e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.545355e-05
- `obs_disabled_clock_running_reset_combinational_w`: 1.877732e-06
- `obs_disabled_clock_running_reset_total_a`: 3.967893e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.229792e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.192790e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.088633e-05
- `obs_disabled_clock_running_startup_leakage_w`: 1.649173e-07
- `obs_disabled_clock_running_startup_clock_w`: 4.170556e-05
- `obs_disabled_clock_running_startup_sequential_w`: 7.665894e-05
- `obs_disabled_clock_running_startup_combinational_w`: 4.614670e-06
- `obs_disabled_clock_running_startup_total_a`: 4.099307e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.228343e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.183764e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.083179e-05
- `obs_disabled_clock_running_steady_leakage_w`: 1.649168e-07
- `obs_disabled_clock_running_steady_clock_w`: 4.170556e-05
- `obs_disabled_clock_running_steady_sequential_w`: 7.669637e-05
- `obs_disabled_clock_running_steady_combinational_w`: 4.432417e-06
- `obs_disabled_clock_running_steady_total_a`: 4.094477e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.200821e-04
- `obs_raw_streaming_reset_internal_w`: 9.004805e-05
- `obs_raw_streaming_reset_switching_w`: 2.987131e-05
- `obs_raw_streaming_reset_leakage_w`: 1.627358e-07
- `obs_raw_streaming_reset_clock_w`: 4.170556e-05
- `obs_raw_streaming_reset_sequential_w`: 7.548599e-05
- `obs_raw_streaming_reset_combinational_w`: 2.890572e-06
- `obs_raw_streaming_reset_total_a`: 4.002737e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.381621e-04
- `obs_raw_streaming_startup_internal_w`: 1.002966e-04
- `obs_raw_streaming_startup_switching_w`: 3.769833e-05
- `obs_raw_streaming_startup_leakage_w`: 1.671805e-07
- `obs_raw_streaming_startup_clock_w`: 4.170556e-05
- `obs_raw_streaming_startup_sequential_w`: 8.311773e-05
- `obs_raw_streaming_startup_combinational_w`: 1.333880e-05
- `obs_raw_streaming_startup_total_a`: 4.605403e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.480945e-04
- `obs_raw_streaming_steady_internal_w`: 1.060739e-04
- `obs_raw_streaming_steady_switching_w`: 4.185107e-05
- `obs_raw_streaming_steady_leakage_w`: 1.695180e-07
- `obs_raw_streaming_steady_clock_w`: 4.170556e-05
- `obs_raw_streaming_steady_sequential_w`: 8.833599e-05
- `obs_raw_streaming_steady_combinational_w`: 1.805292e-05
- `obs_raw_streaming_steady_total_a`: 4.936483e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_n40C_3v00 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_n40C_3v00, interconnect `nom`).
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
