---
record: 2026-10-10-digital-sta-activity-01
date: 2026-10-10T02:44:30Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib (liberty corner ss_125C_3v00, sha256:d83917f827021eadb159f6011905bf20de632533b2953abba89266a88c2b24af)
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
  process: ss
  voltage: 3.00 V (nominal 3.3 V, -9.1%)
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00
  interconnect: min (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature 125, nom_voltage 3 (read from the deck)

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
  spef_sha256: c1b15d77db00e517acd1c7d603fb94e4eb115b191c0d09e1c4ae0726a53433c3
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-01/
  files:
    - uniform.tcl  sha256:90ac829b9b0536275857ad8254207e0f2c5092c5b28ef9c1c7ae1afff798d13c
    - uniform.log  sha256:d2df34b79fefdfefd300e92b62ef9851d1065da3e299bdf5ddf5242fa2320305
    - observed.tcl  sha256:f59dd53ae29254b9f64943d425ba609ecc847dc4f67a9a3aa1d1e343ea61772e
    - observed.log  sha256:4ae3243d7ea8245ec26c11adff203c299f18af5eecf9830a7e2294146b8c7fc3
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 8.4s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    146.96 |     65.73 |      2.21 |    214.90 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     95.93 |     29.86 |      2.20 |    127.98 | 0.596 | 5371 / 0 |
| alarm-gated | startup | 1040 |    105.03 |     36.19 |      2.21 |    143.43 | 0.667 | 5371 / 0 |
| alarm-gated | steady | 1024 |    102.24 |     33.92 |      2.21 |    138.37 | 0.644 | 5371 / 0 |
| backpressure | reset | 8 |     95.89 |     29.77 |      2.20 |    127.86 | 0.595 | 5371 / 0 |
| backpressure | startup | 1040 |    105.19 |     36.30 |      2.21 |    143.71 | 0.669 | 5371 / 0 |
| backpressure | steady | 1024 |    111.71 |     40.51 |      2.21 |    154.43 | 0.719 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     95.92 |     29.84 |      2.20 |    127.95 | 0.595 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    105.36 |     36.49 |      2.21 |    144.06 | 0.670 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    111.78 |     40.62 |      2.21 |    154.62 | 0.719 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     95.64 |     29.39 |      2.20 |    127.23 | 0.592 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     97.92 |     30.41 |      2.20 |    130.53 | 0.607 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     97.82 |     30.35 |      2.20 |    130.38 | 0.607 | 5371 / 0 |
| raw-streaming | reset | 8 |     95.98 |     30.03 |      2.20 |    128.20 | 0.597 | 5371 / 0 |
| raw-streaming | startup | 1040 |    105.65 |     36.90 |      2.21 |    144.76 | 0.674 | 5371 / 0 |
| raw-streaming | steady | 1024 |    112.11 |     41.08 |      2.21 |    155.40 | 0.723 | 5371 / 0 |

- `uniform_total_w`: 2.148990e-04
- `uniform_internal_w`: 1.469615e-04
- `uniform_switching_w`: 6.572864e-05
- `uniform_leakage_w`: 2.208865e-06
- `uniform_clock_w`: 4.383170e-05
- `uniform_sequential_w`: 1.137949e-04
- `uniform_combinational_w`: 5.727239e-05
- `uniform_total_a`: 7.163300e-05
- `obs_alarm_gated_reset_total_w`: 1.279848e-04
- `obs_alarm_gated_reset_internal_w`: 9.592759e-05
- `obs_alarm_gated_reset_switching_w`: 2.985849e-05
- `obs_alarm_gated_reset_leakage_w`: 2.198723e-06
- `obs_alarm_gated_reset_clock_w`: 4.383170e-05
- `obs_alarm_gated_reset_sequential_w`: 8.023573e-05
- `obs_alarm_gated_reset_combinational_w`: 3.917395e-06
- `obs_alarm_gated_reset_total_a`: 4.266160e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.434305e-04
- `obs_alarm_gated_startup_internal_w`: 1.050296e-04
- `obs_alarm_gated_startup_switching_w`: 3.619264e-05
- `obs_alarm_gated_startup_leakage_w`: 2.208328e-06
- `obs_alarm_gated_startup_clock_w`: 4.383170e-05
- `obs_alarm_gated_startup_sequential_w`: 8.726680e-05
- `obs_alarm_gated_startup_combinational_w`: 1.233197e-05
- `obs_alarm_gated_startup_total_a`: 4.781017e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.383738e-04
- `obs_alarm_gated_steady_internal_w`: 1.022411e-04
- `obs_alarm_gated_steady_switching_w`: 3.392499e-05
- `obs_alarm_gated_steady_leakage_w`: 2.207755e-06
- `obs_alarm_gated_steady_clock_w`: 4.383170e-05
- `obs_alarm_gated_steady_sequential_w`: 8.542210e-05
- `obs_alarm_gated_steady_combinational_w`: 9.119980e-06
- `obs_alarm_gated_steady_total_a`: 4.612460e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.278607e-04
- `obs_backpressure_reset_internal_w`: 9.588702e-05
- `obs_backpressure_reset_switching_w`: 2.977493e-05
- `obs_backpressure_reset_leakage_w`: 2.198723e-06
- `obs_backpressure_reset_clock_w`: 4.383170e-05
- `obs_backpressure_reset_sequential_w`: 8.022837e-05
- `obs_backpressure_reset_combinational_w`: 3.800622e-06
- `obs_backpressure_reset_total_a`: 4.262023e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.437070e-04
- `obs_backpressure_startup_internal_w`: 1.051936e-04
- `obs_backpressure_startup_switching_w`: 3.630477e-05
- `obs_backpressure_startup_leakage_w`: 2.208553e-06
- `obs_backpressure_startup_clock_w`: 4.383170e-05
- `obs_backpressure_startup_sequential_w`: 8.729713e-05
- `obs_backpressure_startup_combinational_w`: 1.257810e-05
- `obs_backpressure_startup_total_a`: 4.790233e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.544267e-04
- `obs_backpressure_steady_internal_w`: 1.117064e-04
- `obs_backpressure_steady_switching_w`: 4.050830e-05
- `obs_backpressure_steady_leakage_w`: 2.212008e-06
- `obs_backpressure_steady_clock_w`: 4.383170e-05
- `obs_backpressure_steady_sequential_w`: 9.273984e-05
- `obs_backpressure_steady_combinational_w`: 1.785515e-05
- `obs_backpressure_steady_total_a`: 5.147557e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.279543e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.591888e-05
- `obs_conditioned_streaming_reset_switching_w`: 2.983673e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.198723e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.383170e-05
- `obs_conditioned_streaming_reset_sequential_w`: 8.023572e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.886933e-06
- `obs_conditioned_streaming_reset_total_a`: 4.265143e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.440619e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.053634e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.649054e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.207989e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.383170e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.745068e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.277951e-05
- `obs_conditioned_streaming_startup_total_a`: 4.802063e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.546187e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.117846e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.062328e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.210763e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.383170e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.272023e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.806686e-05
- `obs_conditioned_streaming_steady_total_a`: 5.153957e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.272293e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.563833e-05
- `obs_disabled_clock_running_reset_switching_w`: 2.939228e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.198723e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.383170e-05
- `obs_disabled_clock_running_reset_sequential_w`: 8.020095e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.196716e-06
- `obs_disabled_clock_running_reset_total_a`: 4.240977e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.305310e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.792073e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.040563e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.383170e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.143928e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.260008e-06
- `obs_disabled_clock_running_startup_total_a`: 4.351033e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.303762e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.781729e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.035432e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.383170e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.147752e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.067023e-06
- `obs_disabled_clock_running_steady_total_a`: 4.345873e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.282045e-04
- `obs_raw_streaming_reset_internal_w`: 9.597710e-05
- `obs_raw_streaming_reset_switching_w`: 3.002872e-05
- `obs_raw_streaming_reset_leakage_w`: 2.198723e-06
- `obs_raw_streaming_reset_clock_w`: 4.383170e-05
- `obs_raw_streaming_reset_sequential_w`: 8.023556e-05
- `obs_raw_streaming_reset_combinational_w`: 4.137295e-06
- `obs_raw_streaming_reset_total_a`: 4.273483e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.447598e-04
- `obs_raw_streaming_startup_internal_w`: 1.056481e-04
- `obs_raw_streaming_startup_switching_w`: 3.690373e-05
- `obs_raw_streaming_startup_leakage_w`: 2.207986e-06
- `obs_raw_streaming_startup_clock_w`: 4.383170e-05
- `obs_raw_streaming_startup_sequential_w`: 8.745156e-05
- `obs_raw_streaming_startup_combinational_w`: 1.347647e-05
- `obs_raw_streaming_startup_total_a`: 4.825327e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.554034e-04
- `obs_raw_streaming_steady_internal_w`: 1.121129e-04
- `obs_raw_streaming_steady_switching_w`: 4.107905e-05
- `obs_raw_streaming_steady_leakage_w`: 2.211509e-06
- `obs_raw_streaming_steady_clock_w`: 4.383170e-05
- `obs_raw_streaming_steady_sequential_w`: 9.274200e-05
- `obs_raw_streaming_steady_combinational_w`: 1.882969e-05
- `obs_raw_streaming_steady_total_a`: 5.180113e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_125C_3v00 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_125C_3v00, interconnect `min`).
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
