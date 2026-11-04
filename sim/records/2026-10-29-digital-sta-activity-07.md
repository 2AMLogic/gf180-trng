---
record: 2026-10-29-digital-sta-activity-07
date: 2026-10-29T19:55:13Z
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
  - gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30.lib (liberty corner tt_025C_3v30, sha256:1157d0aa147dba75a214708197d7a046f970175d723cdec108025f6f06727c12)
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
  process: tt
  voltage: 3.30 V (nominal 3.3 V)
  temperature: 25
  liberty: gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30
  interconnect: min (OpenRCX rule deck)
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
  spef_sha256: aacf3eed51e0f11f4f343586c5b3f570a9409ad4fb9eb7312aabf886066d992f
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
  path: sim/records/raw/2026-10-29-digital-sta-activity-07/
  files:
    - uniform.tcl  sha256:66ff19719a5ccbc9901f2ba53b38cc34b20f0f7f687d8038d206178f9056bbab
    - uniform.log  sha256:9be2072f70a7a85539edaf887a4e19bb63264b97e792011d0c39ce5be25ef158
    - observed.tcl  sha256:90c6e387ece20dde654447da65baea7c36a8c4ec28220a6f23f3b42a811c4980
    - observed.log  sha256:9b028376e24c9c2db2f31594d02bf5a74a1051e190a8bce8f07acf2a7ab48c1e
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 9.2s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    172.84 |     75.37 |      0.21 |    248.43 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    114.73 |     35.41 |      0.20 |    150.34 | 0.605 | 5143 / 0 |
| alarm-gated | startup | 1040 |    127.62 |     44.08 |      0.21 |    171.91 | 0.692 | 5143 / 0 |
| alarm-gated | steady | 1024 |    124.00 |     41.42 |      0.21 |    165.62 | 0.667 | 5143 / 0 |
| backpressure | reset | 8 |    114.68 |     35.30 |      0.20 |    150.18 | 0.605 | 5143 / 0 |
| backpressure | startup | 1040 |    127.88 |     44.23 |      0.21 |    172.33 | 0.694 | 5143 / 0 |
| backpressure | steady | 1024 |    135.49 |     49.11 |      0.22 |    184.82 | 0.744 | 5143 / 0 |
| conditioned-streaming | reset | 8 |    114.71 |     35.40 |      0.20 |    150.31 | 0.605 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    128.18 |     44.46 |      0.21 |    172.85 | 0.696 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    135.63 |     49.28 |      0.21 |    185.13 | 0.745 | 5143 / 0 |
| disabled-clock-running | reset | 8 |    114.08 |     34.78 |      0.20 |    149.06 | 0.600 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |    117.19 |     36.77 |      0.21 |    154.17 | 0.621 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |    117.07 |     36.71 |      0.21 |    153.99 | 0.620 | 5143 / 0 |
| raw-streaming | reset | 8 |    114.63 |     35.55 |      0.20 |    150.38 | 0.605 | 5143 / 0 |
| raw-streaming | startup | 1040 |    128.30 |     44.88 |      0.21 |    173.39 | 0.698 | 5143 / 0 |
| raw-streaming | steady | 1024 |    135.94 |     49.82 |      0.22 |    185.98 | 0.749 | 5143 / 0 |

- `uniform_total_w`: 2.484252e-04
- `uniform_internal_w`: 1.728408e-04
- `uniform_switching_w`: 7.536977e-05
- `uniform_leakage_w`: 2.145970e-07
- `uniform_clock_w`: 5.298397e-05
- `uniform_sequential_w`: 1.307349e-04
- `uniform_combinational_w`: 6.470631e-05
- `uniform_total_a`: 7.528036e-05
- `obs_alarm_gated_reset_total_w`: 1.503385e-04
- `obs_alarm_gated_reset_internal_w`: 1.147254e-04
- `obs_alarm_gated_reset_switching_w`: 3.540974e-05
- `obs_alarm_gated_reset_leakage_w`: 2.033711e-07
- `obs_alarm_gated_reset_clock_w`: 5.298397e-05
- `obs_alarm_gated_reset_sequential_w`: 9.383248e-05
- `obs_alarm_gated_reset_combinational_w`: 3.522045e-06
- `obs_alarm_gated_reset_total_a`: 4.555712e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.719082e-04
- `obs_alarm_gated_startup_internal_w`: 1.276159e-04
- `obs_alarm_gated_startup_switching_w`: 4.408100e-05
- `obs_alarm_gated_startup_leakage_w`: 2.113422e-07
- `obs_alarm_gated_startup_clock_w`: 5.298397e-05
- `obs_alarm_gated_startup_sequential_w`: 1.032361e-04
- `obs_alarm_gated_startup_combinational_w`: 1.568798e-05
- `obs_alarm_gated_startup_total_a`: 5.209339e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.656247e-04
- `obs_alarm_gated_steady_internal_w`: 1.239987e-04
- `obs_alarm_gated_steady_switching_w`: 4.141506e-05
- `obs_alarm_gated_steady_leakage_w`: 2.109673e-07
- `obs_alarm_gated_steady_clock_w`: 5.298397e-05
- `obs_alarm_gated_steady_sequential_w`: 1.013900e-04
- `obs_alarm_gated_steady_combinational_w`: 1.125072e-05
- `obs_alarm_gated_steady_total_a`: 5.018930e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.501827e-04
- `obs_backpressure_reset_internal_w`: 1.146762e-04
- `obs_backpressure_reset_switching_w`: 3.530310e-05
- `obs_backpressure_reset_leakage_w`: 2.033711e-07
- `obs_backpressure_reset_clock_w`: 5.298397e-05
- `obs_backpressure_reset_sequential_w`: 9.382387e-05
- `obs_backpressure_reset_combinational_w`: 3.374834e-06
- `obs_backpressure_reset_total_a`: 4.550991e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.723275e-04
- `obs_backpressure_startup_internal_w`: 1.278822e-04
- `obs_backpressure_startup_switching_w`: 4.423366e-05
- `obs_backpressure_startup_leakage_w`: 2.116402e-07
- `obs_backpressure_startup_clock_w`: 5.298397e-05
- `obs_backpressure_startup_sequential_w`: 1.033428e-04
- `obs_backpressure_startup_combinational_w`: 1.600059e-05
- `obs_backpressure_startup_total_a`: 5.222045e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.848161e-04
- `obs_backpressure_steady_internal_w`: 1.354881e-04
- `obs_backpressure_steady_switching_w`: 4.911191e-05
- `obs_backpressure_steady_leakage_w`: 2.161484e-07
- `obs_backpressure_steady_clock_w`: 5.298397e-05
- `obs_backpressure_steady_sequential_w`: 1.100437e-04
- `obs_backpressure_steady_combinational_w`: 2.178838e-05
- `obs_backpressure_steady_total_a`: 5.600488e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.503138e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.147140e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.539647e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.033711e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.298397e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.383249e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.497360e-06
- `obs_conditioned_streaming_reset_total_a`: 4.554964e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.728466e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.281804e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.445517e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.109732e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.298397e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.035956e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.626684e-05
- `obs_conditioned_streaming_startup_total_a`: 5.237776e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.851299e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.356328e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.928217e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.149503e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.298397e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.100737e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.207234e-05
- `obs_conditioned_streaming_steady_total_a`: 5.609997e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.490640e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.140848e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.477581e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.033711e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.298397e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.378796e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.292037e-06
- `obs_disabled_clock_running_reset_total_a`: 4.517091e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.541744e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.171947e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.677296e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.067526e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.298397e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.529647e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.893901e-06
- `obs_disabled_clock_running_startup_total_a`: 4.671952e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.539898e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.170733e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.670973e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.067530e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.298397e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.534162e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.664156e-06
- `obs_disabled_clock_running_steady_total_a`: 4.666358e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.503759e-04
- `obs_raw_streaming_reset_internal_w`: 1.146261e-04
- `obs_raw_streaming_reset_switching_w`: 3.554641e-05
- `obs_raw_streaming_reset_leakage_w`: 2.033711e-07
- `obs_raw_streaming_reset_clock_w`: 5.298397e-05
- `obs_raw_streaming_reset_sequential_w`: 9.382967e-05
- `obs_raw_streaming_reset_combinational_w`: 3.562266e-06
- `obs_raw_streaming_reset_total_a`: 4.556845e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.733871e-04
- `obs_raw_streaming_startup_internal_w`: 1.282973e-04
- `obs_raw_streaming_startup_switching_w`: 4.487873e-05
- `obs_raw_streaming_startup_leakage_w`: 2.111363e-07
- `obs_raw_streaming_startup_clock_w`: 5.298397e-05
- `obs_raw_streaming_startup_sequential_w`: 1.033926e-04
- `obs_raw_streaming_startup_combinational_w`: 1.701060e-05
- `obs_raw_streaming_startup_total_a`: 5.254155e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.859757e-04
- `obs_raw_streaming_steady_internal_w`: 1.359393e-04
- `obs_raw_streaming_steady_switching_w`: 4.982052e-05
- `obs_raw_streaming_steady_leakage_w`: 2.159377e-07
- `obs_raw_streaming_steady_clock_w`: 5.298397e-05
- `obs_raw_streaming_steady_sequential_w`: 1.100347e-04
- `obs_raw_streaming_steady_combinational_w`: 2.295721e-05
- `obs_raw_streaming_steady_total_a`: 5.635627e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty tt_025C_3v30 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (tt_025C_3v30, interconnect `min`).
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
