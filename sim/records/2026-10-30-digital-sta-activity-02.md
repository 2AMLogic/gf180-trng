---
record: 2026-10-30-digital-sta-activity-02
date: 2026-10-30T15:16:53Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: d24d862fc3836f8f5514aa2fa32e319f1a96567c
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha bb949d10cf059e01698f33f6531b74da1df90358).
repo_commit: 8939b542e96bfc19151bee88578dc394b5468fe2-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib (liberty corner ss_125C_3v00, sha256:d83917f827021eadb159f6011905bf20de632533b2953abba89266a88c2b24af)
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
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00
  interconnect: nom (OpenRCX rule deck)
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
  spef_sha256: fc6dd7350388e51206fd900b8a662eaf7341338c7a3c5ab699b899bd3d198d82
  spef_bytes: 1795569
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
      vcd_sha256: d73b73c2878833b11c530926e16d4581e020fd1f07ba48aec025168df2997b09
      vcd_bytes: 20199467
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1490/1490
      xz_events: 4272
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: ce683a6499939dfdfbc7f0948d9cdf6e0fb7118b0eea81c99310ea9ff8a19a6d
      vcd_bytes: 21556003
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4289
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: 1b70087f5ae79f73da990c9d9aa9738670f74a6b31e57f02cc3f2ba736fa55fc
      vcd_bytes: 21612163
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4168
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: a10758043594e820119885dbb73a054dc89bfbbf413e35c32c5bd544f30648a5
      vcd_bytes: 16158866
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 1798
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: a8544b5fe783833514bdbc26788df620d3f8969d23472620ed7021e0628acd65
      vcd_bytes: 21759020
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4488
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-10-30-digital-sta-activity-02/
  files:
    - uniform.tcl  sha256:0158bb67077ed0e487fd9a6b56e5f46c39072616ed3de1c13d37bf85b853c984
    - uniform.log  sha256:b60dd77869ff9ddb83af68616a3adbde0daf90516d00c5f5d386079d0353dc8e
    - observed.tcl  sha256:9e66eeb2da2a65fe1b01a95dcb130477dfdf455b85df58c21fa536189bd2bea9
    - observed.log  sha256:f9fceaee35fe18793973c72590f445190f02c006a32d78211e8a9a24da6dea64
    - activity-manifest.json  sha256:1e327145d7667bd16602328c74156fdb1a0755c542aa19e43d054aedb64852d1
wall_time: 8.2s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    147.22 |     68.08 |      2.46 |    217.76 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     96.19 |     31.02 |      2.45 |    129.65 | 0.595 | 5371 / 0 |
| alarm-gated | startup | 1040 |    105.31 |     37.57 |      2.46 |    145.33 | 0.667 | 5371 / 0 |
| alarm-gated | steady | 1024 |    102.51 |     35.32 |      2.46 |    140.29 | 0.644 | 5371 / 0 |
| backpressure | reset | 8 |     96.15 |     30.93 |      2.45 |    129.53 | 0.595 | 5371 / 0 |
| backpressure | startup | 1040 |    105.47 |     37.68 |      2.46 |    145.61 | 0.669 | 5371 / 0 |
| backpressure | steady | 1024 |    111.99 |     41.97 |      2.46 |    156.41 | 0.718 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     96.18 |     30.99 |      2.45 |    129.62 | 0.595 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    105.64 |     37.88 |      2.46 |    145.97 | 0.670 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    112.06 |     42.09 |      2.46 |    156.61 | 0.719 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     95.90 |     30.56 |      2.45 |    128.90 | 0.592 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     98.19 |     31.58 |      2.45 |    132.23 | 0.607 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     98.09 |     31.53 |      2.45 |    132.07 | 0.606 | 5371 / 0 |
| raw-streaming | reset | 8 |     96.24 |     31.18 |      2.45 |    129.87 | 0.596 | 5371 / 0 |
| raw-streaming | startup | 1040 |    105.93 |     38.31 |      2.46 |    146.69 | 0.674 | 5371 / 0 |
| raw-streaming | steady | 1024 |    112.40 |     42.56 |      2.46 |    157.42 | 0.723 | 5371 / 0 |

- `uniform_total_w`: 2.177633e-04
- `uniform_internal_w`: 1.472224e-04
- `uniform_switching_w`: 6.808455e-05
- `uniform_leakage_w`: 2.456396e-06
- `uniform_clock_w`: 4.539897e-05
- `uniform_sequential_w`: 1.140583e-04
- `uniform_combinational_w`: 5.830601e-05
- `uniform_total_a`: 7.258777e-05
- `obs_alarm_gated_reset_total_w`: 1.296495e-04
- `obs_alarm_gated_reset_internal_w`: 9.618823e-05
- `obs_alarm_gated_reset_switching_w`: 3.101506e-05
- `obs_alarm_gated_reset_leakage_w`: 2.446252e-06
- `obs_alarm_gated_reset_clock_w`: 4.539897e-05
- `obs_alarm_gated_reset_sequential_w`: 8.028554e-05
- `obs_alarm_gated_reset_combinational_w`: 3.964964e-06
- `obs_alarm_gated_reset_total_a`: 4.321650e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.453313e-04
- `obs_alarm_gated_startup_internal_w`: 1.053053e-04
- `obs_alarm_gated_startup_switching_w`: 3.757021e-05
- `obs_alarm_gated_startup_leakage_w`: 2.455845e-06
- `obs_alarm_gated_startup_clock_w`: 4.539897e-05
- `obs_alarm_gated_startup_sequential_w`: 8.738943e-05
- `obs_alarm_gated_startup_combinational_w`: 1.254291e-05
- `obs_alarm_gated_startup_total_a`: 4.844377e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.402856e-04
- `obs_alarm_gated_steady_internal_w`: 1.025146e-04
- `obs_alarm_gated_steady_switching_w`: 3.531575e-05
- `obs_alarm_gated_steady_leakage_w`: 2.455274e-06
- `obs_alarm_gated_steady_clock_w`: 4.539897e-05
- `obs_alarm_gated_steady_sequential_w`: 8.552991e-05
- `obs_alarm_gated_steady_combinational_w`: 9.356644e-06
- `obs_alarm_gated_steady_total_a`: 4.676187e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.295270e-04
- `obs_backpressure_reset_internal_w`: 9.614773e-05
- `obs_backpressure_reset_switching_w`: 3.093304e-05
- `obs_backpressure_reset_leakage_w`: 2.446252e-06
- `obs_backpressure_reset_clock_w`: 4.539897e-05
- `obs_backpressure_reset_sequential_w`: 8.027821e-05
- `obs_backpressure_reset_combinational_w`: 3.849774e-06
- `obs_backpressure_reset_total_a`: 4.317567e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.456097e-04
- `obs_backpressure_startup_internal_w`: 1.054696e-04
- `obs_backpressure_startup_switching_w`: 3.768404e-05
- `obs_backpressure_startup_leakage_w`: 2.456071e-06
- `obs_backpressure_startup_clock_w`: 4.539897e-05
- `obs_backpressure_startup_sequential_w`: 8.742153e-05
- `obs_backpressure_startup_combinational_w`: 1.278911e-05
- `obs_backpressure_startup_total_a`: 4.853657e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.564139e-04
- `obs_backpressure_steady_internal_w`: 1.119880e-04
- `obs_backpressure_steady_switching_w`: 4.196639e-05
- `obs_backpressure_steady_leakage_w`: 2.459506e-06
- `obs_backpressure_steady_clock_w`: 4.539897e-05
- `obs_backpressure_steady_sequential_w`: 9.286365e-05
- `obs_backpressure_steady_combinational_w`: 1.815122e-05
- `obs_backpressure_steady_total_a`: 5.213797e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.296194e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.617955e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.099355e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.446252e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.539897e-05
- `obs_conditioned_streaming_reset_sequential_w`: 8.028554e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.934772e-06
- `obs_conditioned_streaming_reset_total_a`: 4.320647e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.459706e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.056395e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.787558e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.455506e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.539897e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.757482e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.299674e-05
- `obs_conditioned_streaming_startup_total_a`: 4.865687e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.566110e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.120643e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.208841e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.458290e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.539897e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.283899e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.837303e-05
- `obs_conditioned_streaming_steady_total_a`: 5.220367e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.289010e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.589920e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.055557e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.446252e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.539897e-05
- `obs_disabled_clock_running_reset_sequential_w`: 8.025079e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.251155e-06
- `obs_disabled_clock_running_reset_total_a`: 4.296700e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.322270e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.819275e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.158216e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.452133e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.539897e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.151460e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.313338e-06
- `obs_disabled_clock_running_startup_total_a`: 4.407567e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.320693e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.808924e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.152790e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.452133e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.539897e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.155409e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.116071e-06
- `obs_disabled_clock_running_steady_total_a`: 4.402310e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.298664e-04
- `obs_raw_streaming_reset_internal_w`: 9.623721e-05
- `obs_raw_streaming_reset_switching_w`: 3.118291e-05
- `obs_raw_streaming_reset_leakage_w`: 2.446252e-06
- `obs_raw_streaming_reset_clock_w`: 4.539897e-05
- `obs_raw_streaming_reset_sequential_w`: 8.028534e-05
- `obs_raw_streaming_reset_combinational_w`: 4.181967e-06
- `obs_raw_streaming_reset_total_a`: 4.328880e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.466945e-04
- `obs_raw_streaming_startup_internal_w`: 1.059256e-04
- `obs_raw_streaming_startup_switching_w`: 3.831333e-05
- `obs_raw_streaming_startup_leakage_w`: 2.455513e-06
- `obs_raw_streaming_startup_clock_w`: 4.539897e-05
- `obs_raw_streaming_startup_sequential_w`: 8.758223e-05
- `obs_raw_streaming_startup_combinational_w`: 1.371320e-05
- `obs_raw_streaming_startup_total_a`: 4.889817e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.574186e-04
- `obs_raw_streaming_steady_internal_w`: 1.123958e-04
- `obs_raw_streaming_steady_switching_w`: 4.256377e-05
- `obs_raw_streaming_steady_leakage_w`: 2.459014e-06
- `obs_raw_streaming_steady_clock_w`: 4.539897e-05
- `obs_raw_streaming_steady_sequential_w`: 9.286434e-05
- `obs_raw_streaming_steady_combinational_w`: 1.915538e-05
- `obs_raw_streaming_steady_total_a`: 5.247287e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_125C_3v00 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_125C_3v00, interconnect `nom`).
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
