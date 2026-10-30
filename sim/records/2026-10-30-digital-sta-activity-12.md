---
record: 2026-10-30-digital-sta-activity-12
date: 2026-10-30T15:18:20Z
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
  spef_sha256: 10c02d6f286cabe4d8feaca5c89983bf35f730040226813f4171409238e74f71
  spef_bytes: 1803172
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
  path: sim/records/raw/2026-10-30-digital-sta-activity-12/
  files:
    - uniform.tcl  sha256:02854f82c74e98820ad4c0032c069bc86a7ba91c5610fd526251a34ea8139920
    - uniform.log  sha256:e0d90f5fe1cf4533d3ec66828204dbcba3680b226fbda5141034891ddf1199d8
    - observed.tcl  sha256:ae46f7dd0dae1345d3aa1a04653ba72322ac98e43d84f2edfdfc61a48bd3df78
    - observed.log  sha256:c517b7a291ddd2cb9af08bb08e2505ebf35cef2503709ee2c5b0a02b63bff028
    - activity-manifest.json  sha256:1e327145d7667bd16602328c74156fdb1a0755c542aa19e43d054aedb64852d1
wall_time: 8.4s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    238.82 |    101.64 |      8.24 |    348.70 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    152.81 |     46.42 |      7.67 |    206.90 | 0.593 | 5371 / 0 |
| alarm-gated | startup | 1040 |    168.19 |     56.10 |      8.26 |    232.54 | 0.667 | 5371 / 0 |
| alarm-gated | steady | 1024 |    163.40 |     52.79 |      8.24 |    224.43 | 0.644 | 5371 / 0 |
| backpressure | reset | 8 |    152.74 |     46.30 |      7.67 |    206.71 | 0.593 | 5371 / 0 |
| backpressure | startup | 1040 |    168.46 |     56.26 |      8.25 |    232.98 | 0.668 | 5371 / 0 |
| backpressure | steady | 1024 |    179.47 |     62.61 |      8.58 |    250.66 | 0.719 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    152.79 |     46.39 |      7.67 |    206.85 | 0.593 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    168.76 |     56.55 |      8.26 |    233.56 | 0.670 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    179.61 |     62.79 |      8.50 |    250.90 | 0.720 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    152.30 |     45.74 |      7.67 |    205.70 | 0.590 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    156.31 |     47.22 |      8.05 |    211.58 | 0.607 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    156.13 |     47.14 |      8.05 |    211.33 | 0.606 | 5371 / 0 |
| raw-streaming | reset | 8 |    152.90 |     46.67 |      7.67 |    207.23 | 0.594 | 5371 / 0 |
| raw-streaming | startup | 1040 |    169.27 |     57.22 |      8.21 |    234.69 | 0.673 | 5371 / 0 |
| raw-streaming | steady | 1024 |    180.18 |     63.52 |      8.51 |    252.21 | 0.723 | 5371 / 0 |

- `uniform_total_w`: 3.486963e-04
- `uniform_internal_w`: 2.388167e-04
- `uniform_switching_w`: 1.016410e-04
- `uniform_leakage_w`: 8.238576e-06
- `uniform_clock_w`: 7.469414e-05
- `uniform_sequential_w`: 1.773656e-04
- `uniform_combinational_w`: 9.663653e-05
- `uniform_total_a`: 9.686008e-05
- `obs_alarm_gated_reset_total_w`: 2.068964e-04
- `obs_alarm_gated_reset_internal_w`: 1.528092e-04
- `obs_alarm_gated_reset_switching_w`: 4.641763e-05
- `obs_alarm_gated_reset_leakage_w`: 7.669590e-06
- `obs_alarm_gated_reset_clock_w`: 7.469414e-05
- `obs_alarm_gated_reset_sequential_w`: 1.237721e-04
- `obs_alarm_gated_reset_combinational_w`: 8.430186e-06
- `obs_alarm_gated_reset_total_a`: 5.747122e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.325398e-04
- `obs_alarm_gated_startup_internal_w`: 1.681861e-04
- `obs_alarm_gated_startup_switching_w`: 5.609587e-05
- `obs_alarm_gated_startup_leakage_w`: 8.257824e-06
- `obs_alarm_gated_startup_clock_w`: 7.469414e-05
- `obs_alarm_gated_startup_sequential_w`: 1.352836e-04
- `obs_alarm_gated_startup_combinational_w`: 2.256213e-05
- `obs_alarm_gated_startup_total_a`: 6.459439e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.244262e-04
- `obs_alarm_gated_steady_internal_w`: 1.634035e-04
- `obs_alarm_gated_steady_switching_w`: 5.278577e-05
- `obs_alarm_gated_steady_leakage_w`: 8.236960e-06
- `obs_alarm_gated_steady_clock_w`: 7.469414e-05
- `obs_alarm_gated_steady_sequential_w`: 1.323859e-04
- `obs_alarm_gated_steady_combinational_w`: 1.734615e-05
- `obs_alarm_gated_steady_total_a`: 6.234061e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.067107e-04
- `obs_backpressure_reset_internal_w`: 1.527446e-04
- `obs_backpressure_reset_switching_w`: 4.629651e-05
- `obs_backpressure_reset_leakage_w`: 7.669590e-06
- `obs_backpressure_reset_clock_w`: 7.469414e-05
- `obs_backpressure_reset_sequential_w`: 1.237612e-04
- `obs_backpressure_reset_combinational_w`: 8.255382e-06
- `obs_backpressure_reset_total_a`: 5.741964e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.329771e-04
- `obs_backpressure_startup_internal_w`: 1.684611e-04
- `obs_backpressure_startup_switching_w`: 5.626323e-05
- `obs_backpressure_startup_leakage_w`: 8.252681e-06
- `obs_backpressure_startup_clock_w`: 7.469414e-05
- `obs_backpressure_startup_sequential_w`: 1.353391e-04
- `obs_backpressure_startup_combinational_w`: 2.294387e-05
- `obs_backpressure_startup_total_a`: 6.471586e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.506580e-04
- `obs_backpressure_steady_internal_w`: 1.794650e-04
- `obs_backpressure_steady_switching_w`: 6.261285e-05
- `obs_backpressure_steady_leakage_w`: 8.580112e-06
- `obs_backpressure_steady_clock_w`: 7.469414e-05
- `obs_backpressure_steady_sequential_w`: 1.441293e-04
- `obs_backpressure_steady_combinational_w`: 3.183455e-05
- `obs_backpressure_steady_total_a`: 6.962722e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.068505e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.527944e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.638645e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.669590e-06
- `obs_conditioned_streaming_reset_clock_w`: 7.469414e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.237721e-04
- `obs_conditioned_streaming_reset_combinational_w`: 8.384239e-06
- `obs_conditioned_streaming_reset_total_a`: 5.745847e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.335604e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.687578e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.654749e-05
- `obs_conditioned_streaming_startup_leakage_w`: 8.255111e-06
- `obs_conditioned_streaming_startup_clock_w`: 7.469414e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.355705e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.329566e-05
- `obs_conditioned_streaming_startup_total_a`: 6.487789e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.508957e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.796054e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.279455e-05
- `obs_conditioned_streaming_steady_leakage_w`: 8.495754e-06
- `obs_conditioned_streaming_steady_clock_w`: 7.469414e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.440791e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.212239e-05
- `obs_conditioned_streaming_steady_total_a`: 6.969325e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 2.057048e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.523002e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.573506e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.669590e-06
- `obs_disabled_clock_running_reset_clock_w`: 7.469414e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.237167e-04
- `obs_disabled_clock_running_reset_combinational_w`: 7.293980e-06
- `obs_disabled_clock_running_reset_total_a`: 5.714022e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.115792e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.563078e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.722079e-05
- `obs_disabled_clock_running_startup_leakage_w`: 8.050591e-06
- `obs_disabled_clock_running_startup_clock_w`: 7.469414e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.260423e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.084274e-05
- `obs_disabled_clock_running_startup_total_a`: 5.877200e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.113251e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.561345e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.713944e-05
- `obs_disabled_clock_running_steady_leakage_w`: 8.051127e-06
- `obs_disabled_clock_running_steady_clock_w`: 7.469414e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.260999e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.053101e-05
- `obs_disabled_clock_running_steady_total_a`: 5.870142e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.072347e-04
- `obs_raw_streaming_reset_internal_w`: 1.528997e-04
- `obs_raw_streaming_reset_switching_w`: 4.666537e-05
- `obs_raw_streaming_reset_leakage_w`: 7.669590e-06
- `obs_raw_streaming_reset_clock_w`: 7.469414e-05
- `obs_raw_streaming_reset_sequential_w`: 1.237708e-04
- `obs_raw_streaming_reset_combinational_w`: 8.769713e-06
- `obs_raw_streaming_reset_total_a`: 5.756519e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.346944e-04
- `obs_raw_streaming_startup_internal_w`: 1.692691e-04
- `obs_raw_streaming_startup_switching_w`: 5.721613e-05
- `obs_raw_streaming_startup_leakage_w`: 8.209090e-06
- `obs_raw_streaming_startup_clock_w`: 7.469414e-05
- `obs_raw_streaming_startup_sequential_w`: 1.355819e-04
- `obs_raw_streaming_startup_combinational_w`: 2.441824e-05
- `obs_raw_streaming_startup_total_a`: 6.519289e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.522054e-04
- `obs_raw_streaming_steady_internal_w`: 1.801834e-04
- `obs_raw_streaming_steady_switching_w`: 6.351529e-05
- `obs_raw_streaming_steady_leakage_w`: 8.506731e-06
- `obs_raw_streaming_steady_clock_w`: 7.469414e-05
- `obs_raw_streaming_steady_sequential_w`: 1.441247e-04
- `obs_raw_streaming_steady_combinational_w`: 3.338665e-05
- `obs_raw_streaming_steady_total_a`: 7.005706e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
