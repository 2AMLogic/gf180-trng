---
record: 2026-10-10-digital-sta-activity-07
date: 2026-10-10T02:45:34Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: 8f13adca1f40260c48314a800b021eda212876f4
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha b16950323f54a4dd4de1dc5f89abc8565ab11b72).
repo_commit: d01212256aee65c9be3593221aded02dded2644f

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
  spef_sha256: e8df5b3c8914a031eecc113ca86cc8cd7e4b14e52e3dce617e0de6577f38c978
  spef_bytes: 1766985
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
      vcd_sha256: 4a33c9cf88e987f0ef819f9eb48a2a65ef24144150eaf5443a85cd973f6327d1
      vcd_bytes: 20199442
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1490/1490
      xz_events: 4272
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: f7f50e47e2354f5f0952f6bf411a0519d14ae1071847837f5a5d1ebf98fe7d22
      vcd_bytes: 21555986
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4289
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: a0e09fad484e70df0d364a6572e652af0e99e95f35051cc7d3e7b889cc77136f
      vcd_bytes: 21612178
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4168
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: d1259e79bcd8783392f642bc50703ff452608e0618f99694e80183970b262cc4
      vcd_bytes: 16158833
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 1798
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: f2e9b984f3a7f390094899a89512645de77cf3ce78e305fdfd35aa0818ae6227
      vcd_bytes: 21760619
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4488
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-10-10-digital-sta-activity-07/
  files:
    - uniform.tcl  sha256:3d2d3d8c0db5374a7b34ef52003d1979b5fdee58318e36ad8ecf3324d0aa1dcc
    - uniform.log  sha256:d85c6f74538dd2170e7d9e1e3c641f0b97df87c12f14fe0d865bb5bf3a8d3360
    - observed.tcl  sha256:054393cbc1fe067cb895c9b348bd64144654f11acba428d8221cdc6d4e0f861e
    - observed.log  sha256:0aa753103ae6258d7a8d4b9d244c7a130ac8aa00eab69eb1e067a2bc699b8427
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 9.3s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    176.38 |     78.65 |      0.22 |    255.25 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    114.64 |     35.81 |      0.21 |    150.66 | 0.590 | 5371 / 0 |
| alarm-gated | startup | 1040 |    125.62 |     43.37 |      0.22 |    169.21 | 0.663 | 5371 / 0 |
| alarm-gated | steady | 1024 |    122.24 |     40.67 |      0.22 |    163.12 | 0.639 | 5371 / 0 |
| backpressure | reset | 8 |    114.59 |     35.71 |      0.21 |    150.51 | 0.590 | 5371 / 0 |
| backpressure | startup | 1040 |    125.81 |     43.51 |      0.22 |    169.54 | 0.664 | 5371 / 0 |
| backpressure | steady | 1024 |    133.67 |     48.53 |      0.22 |    182.41 | 0.715 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    114.63 |     35.79 |      0.21 |    150.62 | 0.590 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    126.02 |     43.73 |      0.22 |    169.96 | 0.666 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    133.76 |     48.66 |      0.22 |    182.65 | 0.716 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    114.28 |     35.26 |      0.21 |    149.75 | 0.587 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    117.06 |     36.46 |      0.21 |    153.74 | 0.602 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    116.94 |     36.40 |      0.21 |    153.55 | 0.602 | 5371 / 0 |
| raw-streaming | reset | 8 |    114.70 |     36.02 |      0.21 |    150.92 | 0.591 | 5371 / 0 |
| raw-streaming | startup | 1040 |    126.37 |     44.22 |      0.22 |    170.81 | 0.669 | 5371 / 0 |
| raw-streaming | steady | 1024 |    134.16 |     49.21 |      0.22 |    183.59 | 0.719 | 5371 / 0 |

- `uniform_total_w`: 2.552535e-04
- `uniform_internal_w`: 1.763838e-04
- `uniform_switching_w`: 7.865039e-05
- `uniform_leakage_w`: 2.193580e-07
- `uniform_clock_w`: 5.171791e-05
- `uniform_sequential_w`: 1.350443e-04
- `uniform_combinational_w`: 6.849129e-05
- `uniform_total_a`: 7.734955e-05
- `obs_alarm_gated_reset_total_w`: 1.506617e-04
- `obs_alarm_gated_reset_internal_w`: 1.146403e-04
- `obs_alarm_gated_reset_switching_w`: 3.581394e-05
- `obs_alarm_gated_reset_leakage_w`: 2.075095e-07
- `obs_alarm_gated_reset_clock_w`: 5.171791e-05
- `obs_alarm_gated_reset_sequential_w`: 9.480627e-05
- `obs_alarm_gated_reset_combinational_w`: 4.137504e-06
- `obs_alarm_gated_reset_total_a`: 4.565506e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.692069e-04
- `obs_alarm_gated_startup_internal_w`: 1.256178e-04
- `obs_alarm_gated_startup_switching_w`: 4.337255e-05
- `obs_alarm_gated_startup_leakage_w`: 2.165480e-07
- `obs_alarm_gated_startup_clock_w`: 5.171791e-05
- `obs_alarm_gated_startup_sequential_w`: 1.032378e-04
- `obs_alarm_gated_startup_combinational_w`: 1.425119e-05
- `obs_alarm_gated_startup_total_a`: 5.127482e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.631248e-04
- `obs_alarm_gated_steady_internal_w`: 1.222396e-04
- `obs_alarm_gated_steady_switching_w`: 4.066933e-05
- `obs_alarm_gated_steady_leakage_w`: 2.159064e-07
- `obs_alarm_gated_steady_clock_w`: 5.171791e-05
- `obs_alarm_gated_steady_sequential_w`: 1.010289e-04
- `obs_alarm_gated_steady_combinational_w`: 1.037810e-05
- `obs_alarm_gated_steady_total_a`: 4.943176e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.505127e-04
- `obs_backpressure_reset_internal_w`: 1.145907e-04
- `obs_backpressure_reset_switching_w`: 3.571445e-05
- `obs_backpressure_reset_leakage_w`: 2.075095e-07
- `obs_backpressure_reset_clock_w`: 5.171791e-05
- `obs_backpressure_reset_sequential_w`: 9.479761e-05
- `obs_backpressure_reset_combinational_w`: 3.997129e-06
- `obs_backpressure_reset_total_a`: 4.560991e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.695373e-04
- `obs_backpressure_startup_internal_w`: 1.258145e-04
- `obs_backpressure_startup_switching_w`: 4.350600e-05
- `obs_backpressure_startup_leakage_w`: 2.168396e-07
- `obs_backpressure_startup_clock_w`: 5.171791e-05
- `obs_backpressure_startup_sequential_w`: 1.032735e-04
- `obs_backpressure_startup_combinational_w`: 1.454602e-05
- `obs_backpressure_startup_total_a`: 5.137494e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.824146e-04
- `obs_backpressure_steady_internal_w`: 1.336683e-04
- `obs_backpressure_steady_switching_w`: 4.852508e-05
- `obs_backpressure_steady_leakage_w`: 2.213108e-07
- `obs_backpressure_steady_clock_w`: 5.171791e-05
- `obs_backpressure_steady_sequential_w`: 1.098121e-04
- `obs_backpressure_steady_combinational_w`: 2.088472e-05
- `obs_backpressure_steady_total_a`: 5.527715e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.506244e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.146288e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.578808e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.075095e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.171791e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.480627e-05
- `obs_conditioned_streaming_reset_combinational_w`: 4.100246e-06
- `obs_conditioned_streaming_reset_total_a`: 4.564376e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.699646e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.260207e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.372776e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.161481e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.171791e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.034588e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.478792e-05
- `obs_conditioned_streaming_startup_total_a`: 5.150442e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.826468e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.337643e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.866228e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.201589e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.171791e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.097898e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.113907e-05
- `obs_conditioned_streaming_steady_total_a`: 5.534752e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.497458e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.142815e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.525682e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.075095e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.171791e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.476479e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.263073e-06
- `obs_disabled_clock_running_reset_total_a`: 4.537752e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.537371e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.170627e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.646294e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.114828e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.171791e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.625791e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.761358e-06
- `obs_disabled_clock_running_startup_total_a`: 4.658700e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.535527e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.169394e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.640176e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.114832e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.171791e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.630367e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.531146e-06
- `obs_disabled_clock_running_steady_total_a`: 4.653112e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.509247e-04
- `obs_raw_streaming_reset_internal_w`: 1.147005e-04
- `obs_raw_streaming_reset_switching_w`: 3.601672e-05
- `obs_raw_streaming_reset_leakage_w`: 2.075095e-07
- `obs_raw_streaming_reset_clock_w`: 5.171791e-05
- `obs_raw_streaming_reset_sequential_w`: 9.480595e-05
- `obs_raw_streaming_reset_combinational_w`: 4.400802e-06
- `obs_raw_streaming_reset_total_a`: 4.573476e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.708092e-04
- `obs_raw_streaming_startup_internal_w`: 1.263694e-04
- `obs_raw_streaming_startup_switching_w`: 4.422353e-05
- `obs_raw_streaming_startup_leakage_w`: 2.163030e-07
- `obs_raw_streaming_startup_clock_w`: 5.171791e-05
- `obs_raw_streaming_startup_sequential_w`: 1.034586e-04
- `obs_raw_streaming_startup_combinational_w`: 1.563282e-05
- `obs_raw_streaming_startup_total_a`: 5.176036e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.835919e-04
- `obs_raw_streaming_steady_internal_w`: 1.341627e-04
- `obs_raw_streaming_steady_switching_w`: 4.920810e-05
- `obs_raw_streaming_steady_leakage_w`: 2.210452e-07
- `obs_raw_streaming_steady_clock_w`: 5.171791e-05
- `obs_raw_streaming_steady_sequential_w`: 1.098149e-04
- `obs_raw_streaming_steady_combinational_w`: 2.205917e-05
- `obs_raw_streaming_steady_total_a`: 5.563391e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
