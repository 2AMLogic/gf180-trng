---
record: 2026-10-10-digital-sta-activity-28
date: 2026-10-10T07:13:10Z
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
repo_commit: 37b0d1714e0aa26771c265216557e0ec45825dcb

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60.lib (liberty corner ff_n40C_3v60, sha256:ff10b2374d88c8614ccc9dc8c4b836a1e8eb54fe6cdfe6883ffd9b1be02487a4)
  - gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:332ae93d61ac55f793da97a6391703f78bc415653cb60e76dd8eb0092124485a)
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
  temperature: -40
  liberty: gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60
  interconnect: min (OpenRCX rule deck)
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
  spef_sha256: a59d128e7464fe5c8fc4aa0c490cee78616ddf1262019f265d89283e476ad721
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-28/
  files:
    - uniform.tcl  sha256:caa705bbb85ee1b1e62fe8286d89300ca596550bb4cc23c4b57880ad761e5afe
    - uniform.log  sha256:d80fd79c614165bbbd0c844c3368d257f0894eff53685a6a6eb99283c1262e1e
    - observed.tcl  sha256:275181bdadb5d3bf6349f2984e3154c5424c236d70ff41be088ab64bbc540718
    - observed.log  sha256:4be6793a1bea19465e17d31f378b4a866288c78f0c8091d4bada8529ac964a91
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 8.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    216.02 |     93.63 |      0.26 |    309.91 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    139.71 |     42.67 |      0.25 |    182.63 | 0.589 | 5371 / 0 |
| alarm-gated | startup | 1040 |    153.21 |     51.67 |      0.25 |    205.13 | 0.662 | 5371 / 0 |
| alarm-gated | steady | 1024 |    149.03 |     48.45 |      0.25 |    197.73 | 0.638 | 5371 / 0 |
| backpressure | reset | 8 |    139.65 |     42.56 |      0.25 |    182.45 | 0.589 | 5371 / 0 |
| backpressure | startup | 1040 |    153.45 |     51.82 |      0.25 |    205.53 | 0.663 | 5371 / 0 |
| backpressure | steady | 1024 |    163.13 |     57.80 |      0.26 |    221.19 | 0.714 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    139.70 |     42.64 |      0.25 |    182.58 | 0.589 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    153.71 |     52.09 |      0.25 |    206.05 | 0.665 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    163.26 |     57.96 |      0.26 |    221.48 | 0.715 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    139.26 |     42.01 |      0.25 |    181.52 | 0.586 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    142.70 |     43.44 |      0.25 |    186.39 | 0.601 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    142.55 |     43.37 |      0.25 |    186.17 | 0.601 | 5371 / 0 |
| raw-streaming | reset | 8 |    139.79 |     42.91 |      0.25 |    182.95 | 0.590 | 5371 / 0 |
| raw-streaming | startup | 1040 |    154.15 |     52.68 |      0.25 |    207.08 | 0.668 | 5371 / 0 |
| raw-streaming | steady | 1024 |    163.75 |     58.61 |      0.26 |    222.62 | 0.718 | 5371 / 0 |

- `uniform_total_w`: 3.099065e-04
- `uniform_internal_w`: 2.160227e-04
- `uniform_switching_w`: 9.362715e-05
- `uniform_leakage_w`: 2.566557e-07
- `uniform_clock_w`: 6.372773e-05
- `uniform_sequential_w`: 1.626741e-04
- `uniform_combinational_w`: 8.350468e-05
- `uniform_total_a`: 8.608514e-05
- `obs_alarm_gated_reset_total_w`: 1.826275e-04
- `obs_alarm_gated_reset_internal_w`: 1.397090e-04
- `obs_alarm_gated_reset_switching_w`: 4.267345e-05
- `obs_alarm_gated_reset_leakage_w`: 2.450344e-07
- `obs_alarm_gated_reset_clock_w`: 6.372773e-05
- `obs_alarm_gated_reset_sequential_w`: 1.139191e-04
- `obs_alarm_gated_reset_combinational_w`: 4.980609e-06
- `obs_alarm_gated_reset_total_a`: 5.072986e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.051326e-04
- `obs_alarm_gated_startup_internal_w`: 1.532135e-04
- `obs_alarm_gated_startup_switching_w`: 5.166564e-05
- `obs_alarm_gated_startup_leakage_w`: 2.534709e-07
- `obs_alarm_gated_startup_clock_w`: 6.372773e-05
- `obs_alarm_gated_startup_sequential_w`: 1.240975e-04
- `obs_alarm_gated_startup_combinational_w`: 1.730761e-05
- `obs_alarm_gated_startup_total_a`: 5.698128e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.977343e-04
- `obs_alarm_gated_steady_internal_w`: 1.490309e-04
- `obs_alarm_gated_steady_switching_w`: 4.845070e-05
- `obs_alarm_gated_steady_leakage_w`: 2.527087e-07
- `obs_alarm_gated_steady_clock_w`: 6.372773e-05
- `obs_alarm_gated_steady_sequential_w`: 1.214310e-04
- `obs_alarm_gated_steady_combinational_w`: 1.257563e-05
- `obs_alarm_gated_steady_total_a`: 5.492619e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.824501e-04
- `obs_backpressure_reset_internal_w`: 1.396499e-04
- `obs_backpressure_reset_switching_w`: 4.255518e-05
- `obs_backpressure_reset_leakage_w`: 2.450344e-07
- `obs_backpressure_reset_clock_w`: 6.372773e-05
- `obs_backpressure_reset_sequential_w`: 1.139090e-04
- `obs_backpressure_reset_combinational_w`: 4.813358e-06
- `obs_backpressure_reset_total_a`: 5.068058e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.055315e-04
- `obs_backpressure_startup_internal_w`: 1.534534e-04
- `obs_backpressure_startup_switching_w`: 5.182430e-05
- `obs_backpressure_startup_leakage_w`: 2.537612e-07
- `obs_backpressure_startup_clock_w`: 6.372773e-05
- `obs_backpressure_startup_sequential_w`: 1.241396e-04
- `obs_backpressure_startup_combinational_w`: 1.766433e-05
- `obs_backpressure_startup_total_a`: 5.709208e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.211901e-04
- `obs_backpressure_steady_internal_w`: 1.631341e-04
- `obs_backpressure_steady_switching_w`: 5.779771e-05
- `obs_backpressure_steady_leakage_w`: 2.582963e-07
- `obs_backpressure_steady_clock_w`: 6.372773e-05
- `obs_backpressure_steady_sequential_w`: 1.320941e-04
- `obs_backpressure_steady_combinational_w`: 2.536825e-05
- `obs_backpressure_steady_total_a`: 6.144169e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.825831e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.396953e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.264274e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.450344e-07
- `obs_conditioned_streaming_reset_clock_w`: 6.372773e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.139191e-04
- `obs_conditioned_streaming_reset_combinational_w`: 4.936252e-06
- `obs_conditioned_streaming_reset_total_a`: 5.071753e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.060533e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.537121e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.208813e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.531000e-07
- `obs_conditioned_streaming_startup_clock_w`: 6.372773e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.243676e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.795822e-05
- `obs_conditioned_streaming_startup_total_a`: 5.723703e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.214759e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.632581e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.796064e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.571063e-07
- `obs_conditioned_streaming_steady_clock_w`: 6.372773e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.320708e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.567733e-05
- `obs_conditioned_streaming_steady_total_a`: 6.152108e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.815161e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.392609e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.201014e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.450344e-07
- `obs_disabled_clock_running_reset_clock_w`: 6.372773e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.138693e-04
- `obs_disabled_clock_running_reset_combinational_w`: 3.919144e-06
- `obs_disabled_clock_running_reset_total_a`: 5.042114e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.863938e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.427041e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.344166e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.480637e-07
- `obs_disabled_clock_running_startup_clock_w`: 6.372773e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.156648e-04
- `obs_disabled_clock_running_startup_combinational_w`: 7.001272e-06
- `obs_disabled_clock_running_startup_total_a`: 5.177606e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.861708e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.425541e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.336868e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.480635e-07
- `obs_disabled_clock_running_steady_clock_w`: 6.372773e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.157193e-04
- `obs_disabled_clock_running_steady_combinational_w`: 6.723856e-06
- `obs_disabled_clock_running_steady_total_a`: 5.171411e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.829456e-04
- `obs_raw_streaming_reset_internal_w`: 1.397866e-04
- `obs_raw_streaming_reset_switching_w`: 4.291398e-05
- `obs_raw_streaming_reset_leakage_w`: 2.450344e-07
- `obs_raw_streaming_reset_clock_w`: 6.372773e-05
- `obs_raw_streaming_reset_sequential_w`: 1.139185e-04
- `obs_raw_streaming_reset_combinational_w`: 5.299405e-06
- `obs_raw_streaming_reset_total_a`: 5.081822e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.070838e-04
- `obs_raw_streaming_startup_internal_w`: 1.541519e-04
- `obs_raw_streaming_startup_switching_w`: 5.267866e-05
- `obs_raw_streaming_startup_leakage_w`: 2.531801e-07
- `obs_raw_streaming_startup_clock_w`: 6.372773e-05
- `obs_raw_streaming_startup_sequential_w`: 1.243636e-04
- `obs_raw_streaming_startup_combinational_w`: 1.899254e-05
- `obs_raw_streaming_startup_total_a`: 5.752328e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.226223e-04
- `obs_raw_streaming_steady_internal_w`: 1.637539e-04
- `obs_raw_streaming_steady_switching_w`: 5.861038e-05
- `obs_raw_streaming_steady_leakage_w`: 2.580173e-07
- `obs_raw_streaming_steady_clock_w`: 6.372773e-05
- `obs_raw_streaming_steady_sequential_w`: 1.320975e-04
- `obs_raw_streaming_steady_combinational_w`: 2.679708e-05
- `obs_raw_streaming_steady_total_a`: 6.183953e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_n40C_3v60 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_n40C_3v60, interconnect `min`).
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
