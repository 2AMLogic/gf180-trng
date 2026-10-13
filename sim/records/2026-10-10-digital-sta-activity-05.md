---
record: 2026-10-10-digital-sta-activity-05
date: 2026-10-10T02:45:15Z
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
  spef_sha256: 8f242efe011f85b413056fa0a7864018bd63d88518a8648e7a99a19935ccff16
  spef_bytes: 1769620
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-05/
  files:
    - uniform.tcl  sha256:7ba382b69b1c2dbc48a28a228135b8b1a87dd5a6d88dc156a9207a14c8f309ff
    - uniform.log  sha256:3a2a340aedd0185f1d4b0dd19956f47bd29005f46f82e338268f6a68b7bbec21
    - observed.tcl  sha256:83701c32bb6c12557003e8117e87040b86f4cdb58bda444bd55421fffb0c784c
    - observed.log  sha256:efe1392c3ddf31ef3ef43774d97eeac9f92aa23538e2e4afcf879dec66cc0241
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 10.6s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    136.62 |     66.46 |      0.17 |    203.25 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     90.42 |     30.14 |      0.17 |    120.73 | 0.594 | 5371 / 0 |
| alarm-gated | startup | 1040 |     98.62 |     36.47 |      0.17 |    135.27 | 0.666 | 5371 / 0 |
| alarm-gated | steady | 1024 |     96.12 |     34.20 |      0.17 |    130.49 | 0.642 | 5371 / 0 |
| backpressure | reset | 8 |     90.38 |     30.06 |      0.17 |    120.61 | 0.593 | 5371 / 0 |
| backpressure | startup | 1040 |     98.77 |     36.59 |      0.17 |    135.53 | 0.667 | 5371 / 0 |
| backpressure | steady | 1024 |    104.69 |     40.83 |      0.17 |    145.69 | 0.717 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     90.41 |     30.12 |      0.17 |    120.70 | 0.594 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |     98.93 |     36.77 |      0.17 |    135.87 | 0.668 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    104.76 |     40.94 |      0.17 |    145.88 | 0.718 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     90.15 |     29.67 |      0.17 |    119.99 | 0.590 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     92.17 |     30.65 |      0.17 |    122.99 | 0.605 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     92.08 |     30.60 |      0.17 |    122.85 | 0.604 | 5371 / 0 |
| raw-streaming | reset | 8 |     90.46 |     30.31 |      0.17 |    120.94 | 0.595 | 5371 / 0 |
| raw-streaming | startup | 1040 |     99.18 |     37.20 |      0.17 |    136.55 | 0.672 | 5371 / 0 |
| raw-streaming | steady | 1024 |    105.05 |     41.41 |      0.17 |    146.64 | 0.721 | 5371 / 0 |

- `uniform_total_w`: 2.032546e-04
- `uniform_internal_w`: 1.366179e-04
- `uniform_switching_w`: 6.646370e-05
- `uniform_leakage_w`: 1.730075e-07
- `uniform_clock_w`: 4.099259e-05
- `uniform_sequential_w`: 1.080023e-04
- `uniform_combinational_w`: 5.425964e-05
- `uniform_total_a`: 6.775153e-05
- `obs_alarm_gated_reset_total_w`: 1.207280e-04
- `obs_alarm_gated_reset_internal_w`: 9.042022e-05
- `obs_alarm_gated_reset_switching_w`: 3.014096e-05
- `obs_alarm_gated_reset_leakage_w`: 1.668595e-07
- `obs_alarm_gated_reset_clock_w`: 4.099259e-05
- `obs_alarm_gated_reset_sequential_w`: 7.633941e-05
- `obs_alarm_gated_reset_combinational_w`: 3.395984e-06
- `obs_alarm_gated_reset_total_a`: 4.024267e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.352682e-04
- `obs_alarm_gated_startup_internal_w`: 9.862208e-05
- `obs_alarm_gated_startup_switching_w`: 3.647387e-05
- `obs_alarm_gated_startup_leakage_w`: 1.722517e-07
- `obs_alarm_gated_startup_clock_w`: 4.099259e-05
- `obs_alarm_gated_startup_sequential_w`: 8.306692e-05
- `obs_alarm_gated_startup_combinational_w`: 1.120856e-05
- `obs_alarm_gated_startup_total_a`: 4.508940e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.304909e-04
- `obs_alarm_gated_steady_internal_w`: 9.611561e-05
- `obs_alarm_gated_steady_switching_w`: 3.420356e-05
- `obs_alarm_gated_steady_leakage_w`: 1.717606e-07
- `obs_alarm_gated_steady_clock_w`: 4.099259e-05
- `obs_alarm_gated_steady_sequential_w`: 8.130342e-05
- `obs_alarm_gated_steady_combinational_w`: 8.194837e-06
- `obs_alarm_gated_steady_total_a`: 4.349697e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.206051e-04
- `obs_backpressure_reset_internal_w`: 9.038163e-05
- `obs_backpressure_reset_switching_w`: 3.005665e-05
- `obs_backpressure_reset_leakage_w`: 1.668595e-07
- `obs_backpressure_reset_clock_w`: 4.099259e-05
- `obs_backpressure_reset_sequential_w`: 7.633251e-05
- `obs_backpressure_reset_combinational_w`: 3.279992e-06
- `obs_backpressure_reset_total_a`: 4.020170e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.355269e-04
- `obs_backpressure_startup_internal_w`: 9.876823e-05
- `obs_backpressure_startup_switching_w`: 3.658630e-05
- `obs_backpressure_startup_leakage_w`: 1.723908e-07
- `obs_backpressure_startup_clock_w`: 4.099259e-05
- `obs_backpressure_startup_sequential_w`: 8.309230e-05
- `obs_backpressure_startup_combinational_w`: 1.144195e-05
- `obs_backpressure_startup_total_a`: 4.517563e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.456912e-04
- `obs_backpressure_steady_internal_w`: 1.046899e-04
- `obs_backpressure_steady_switching_w`: 4.082673e-05
- `obs_backpressure_steady_leakage_w`: 1.745426e-07
- `obs_backpressure_steady_clock_w`: 4.099259e-05
- `obs_backpressure_steady_sequential_w`: 8.823728e-05
- `obs_backpressure_steady_combinational_w`: 1.646126e-05
- `obs_backpressure_steady_total_a`: 4.856373e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.206981e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.041171e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.011950e-05
- `obs_conditioned_streaming_reset_leakage_w`: 1.668595e-07
- `obs_conditioned_streaming_reset_clock_w`: 4.099259e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.633941e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.366019e-06
- `obs_conditioned_streaming_reset_total_a`: 4.023270e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.358711e-04
- `obs_conditioned_streaming_startup_internal_w`: 9.892509e-05
- `obs_conditioned_streaming_startup_switching_w`: 3.677395e-05
- `obs_conditioned_streaming_startup_leakage_w`: 1.720867e-07
- `obs_conditioned_streaming_startup_clock_w`: 4.099259e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.324398e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.163442e-05
- `obs_conditioned_streaming_startup_total_a`: 4.529037e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.458792e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.047620e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.094328e-05
- `obs_conditioned_streaming_steady_leakage_w`: 1.739097e-07
- `obs_conditioned_streaming_steady_clock_w`: 4.099259e-05
- `obs_conditioned_streaming_steady_sequential_w`: 8.822409e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.666249e-05
- `obs_conditioned_streaming_steady_total_a`: 4.862640e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.199900e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.015487e-05
- `obs_disabled_clock_running_reset_switching_w`: 2.966831e-05
- `obs_disabled_clock_running_reset_leakage_w`: 1.668595e-07
- `obs_disabled_clock_running_reset_clock_w`: 4.099259e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.630706e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.690356e-06
- `obs_disabled_clock_running_reset_total_a`: 3.999667e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.229904e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.217356e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.064745e-05
- `obs_disabled_clock_running_startup_leakage_w`: 1.694443e-07
- `obs_disabled_clock_running_startup_clock_w`: 4.099259e-05
- `obs_disabled_clock_running_startup_sequential_w`: 7.749457e-05
- `obs_disabled_clock_running_startup_combinational_w`: 4.503222e-06
- `obs_disabled_clock_running_startup_total_a`: 4.099680e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.228459e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.208109e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.059538e-05
- `obs_disabled_clock_running_steady_leakage_w`: 1.694437e-07
- `obs_disabled_clock_running_steady_clock_w`: 4.099259e-05
- `obs_disabled_clock_running_steady_sequential_w`: 7.753267e-05
- `obs_disabled_clock_running_steady_combinational_w`: 4.320613e-06
- `obs_disabled_clock_running_steady_total_a`: 4.094863e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.209407e-04
- `obs_raw_streaming_reset_internal_w`: 9.046063e-05
- `obs_raw_streaming_reset_switching_w`: 3.031324e-05
- `obs_raw_streaming_reset_leakage_w`: 1.668595e-07
- `obs_raw_streaming_reset_clock_w`: 4.099259e-05
- `obs_raw_streaming_reset_sequential_w`: 7.633940e-05
- `obs_raw_streaming_reset_combinational_w`: 3.608709e-06
- `obs_raw_streaming_reset_total_a`: 4.031357e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.365496e-04
- `obs_raw_streaming_startup_internal_w`: 9.917600e-05
- `obs_raw_streaming_startup_switching_w`: 3.720149e-05
- `obs_raw_streaming_startup_leakage_w`: 1.720917e-07
- `obs_raw_streaming_startup_clock_w`: 4.099259e-05
- `obs_raw_streaming_startup_sequential_w`: 8.324307e-05
- `obs_raw_streaming_startup_combinational_w`: 1.231394e-05
- `obs_raw_streaming_startup_total_a`: 4.551653e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.466403e-04
- `obs_raw_streaming_steady_internal_w`: 1.050535e-04
- `obs_raw_streaming_steady_switching_w`: 4.141240e-05
- `obs_raw_streaming_steady_leakage_w`: 1.743987e-07
- `obs_raw_streaming_steady_clock_w`: 4.099259e-05
- `obs_raw_streaming_steady_sequential_w`: 8.824232e-05
- `obs_raw_streaming_steady_combinational_w`: 1.740536e-05
- `obs_raw_streaming_steady_total_a`: 4.888010e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
