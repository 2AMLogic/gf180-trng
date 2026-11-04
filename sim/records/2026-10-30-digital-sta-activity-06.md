---
record: 2026-10-30-digital-sta-activity-06
date: 2026-10-30T15:17:29Z
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
  spef_sha256: ce026760c912df2d0e3a096f1b4144c986ac739bc0602c8da9c95787fca65b64
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
  path: sim/records/raw/2026-10-30-digital-sta-activity-06/
  files:
    - uniform.tcl  sha256:58e514bb6608c1a024a18ea6e69ed950402a5c711880856a6fa9e6b47bb8b01f
    - uniform.log  sha256:c9b08785d51b91c55226c805823350ea115458cf29152daf305b81b824ee917b
    - observed.tcl  sha256:b5460ede8e6dde9be2be0568fb9bae1771f7b95fece98455eef8f539047c451c
    - observed.log  sha256:d50f3fd847fe490c4ca18f0d5b8f8cce92f445f7f50c30ccae8a1ac4c650f5c0
    - activity-manifest.json  sha256:1e327145d7667bd16602328c74156fdb1a0755c542aa19e43d054aedb64852d1
wall_time: 8.8s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    136.82 |     69.41 |      0.19 |    206.41 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     90.60 |     31.61 |      0.18 |    122.39 | 0.593 | 5371 / 0 |
| alarm-gated | startup | 1040 |     98.82 |     38.21 |      0.19 |    137.21 | 0.665 | 5371 / 0 |
| alarm-gated | steady | 1024 |     96.31 |     35.95 |      0.18 |    132.44 | 0.642 | 5371 / 0 |
| backpressure | reset | 8 |     90.57 |     31.53 |      0.18 |    122.27 | 0.592 | 5371 / 0 |
| backpressure | startup | 1040 |     98.96 |     38.32 |      0.19 |    137.47 | 0.666 | 5371 / 0 |
| backpressure | steady | 1024 |    104.89 |     42.66 |      0.19 |    147.74 | 0.716 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     90.60 |     31.59 |      0.18 |    122.36 | 0.593 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |     99.12 |     38.52 |      0.18 |    137.82 | 0.668 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    104.96 |     42.79 |      0.19 |    147.94 | 0.717 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     90.34 |     31.14 |      0.18 |    121.66 | 0.589 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     92.37 |     32.14 |      0.18 |    124.69 | 0.604 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     92.28 |     32.08 |      0.18 |    124.54 | 0.603 | 5371 / 0 |
| raw-streaming | reset | 8 |     90.64 |     31.78 |      0.18 |    122.60 | 0.594 | 5371 / 0 |
| raw-streaming | startup | 1040 |     99.37 |     38.97 |      0.18 |    138.53 | 0.671 | 5371 / 0 |
| raw-streaming | steady | 1024 |    105.25 |     43.28 |      0.19 |    148.72 | 0.721 | 5371 / 0 |

- `uniform_total_w`: 2.064121e-04
- `uniform_internal_w`: 1.368158e-04
- `uniform_switching_w`: 6.941042e-05
- `uniform_leakage_w`: 1.858777e-07
- `uniform_clock_w`: 4.259878e-05
- `uniform_sequential_w`: 1.082707e-04
- `uniform_combinational_w`: 5.554263e-05
- `uniform_total_a`: 6.880403e-05
- `obs_alarm_gated_reset_total_w`: 1.223911e-04
- `obs_alarm_gated_reset_internal_w`: 9.060364e-05
- `obs_alarm_gated_reset_switching_w`: 3.160772e-05
- `obs_alarm_gated_reset_leakage_w`: 1.797297e-07
- `obs_alarm_gated_reset_clock_w`: 4.259878e-05
- `obs_alarm_gated_reset_sequential_w`: 7.633903e-05
- `obs_alarm_gated_reset_combinational_w`: 3.453434e-06
- `obs_alarm_gated_reset_total_a`: 4.079703e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.372101e-04
- `obs_alarm_gated_startup_internal_w`: 9.881757e-05
- `obs_alarm_gated_startup_switching_w`: 3.820745e-05
- `obs_alarm_gated_startup_leakage_w`: 1.851220e-07
- `obs_alarm_gated_startup_clock_w`: 4.259878e-05
- `obs_alarm_gated_startup_sequential_w`: 8.315484e-05
- `obs_alarm_gated_startup_combinational_w`: 1.145666e-05
- `obs_alarm_gated_startup_total_a`: 4.573670e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.324425e-04
- `obs_alarm_gated_steady_internal_w`: 9.631147e-05
- `obs_alarm_gated_steady_switching_w`: 3.594639e-05
- `obs_alarm_gated_steady_leakage_w`: 1.846309e-07
- `obs_alarm_gated_steady_clock_w`: 4.259878e-05
- `obs_alarm_gated_steady_sequential_w`: 8.137264e-05
- `obs_alarm_gated_steady_combinational_w`: 8.471122e-06
- `obs_alarm_gated_steady_total_a`: 4.414750e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.222700e-04
- `obs_backpressure_reset_internal_w`: 9.056518e-05
- `obs_backpressure_reset_switching_w`: 3.152505e-05
- `obs_backpressure_reset_leakage_w`: 1.797297e-07
- `obs_backpressure_reset_clock_w`: 4.259878e-05
- `obs_backpressure_reset_sequential_w`: 7.633217e-05
- `obs_backpressure_reset_combinational_w`: 3.339159e-06
- `obs_backpressure_reset_total_a`: 4.075667e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.374712e-04
- `obs_backpressure_startup_internal_w`: 9.896373e-05
- `obs_backpressure_startup_switching_w`: 3.832220e-05
- `obs_backpressure_startup_leakage_w`: 1.852611e-07
- `obs_backpressure_startup_clock_w`: 4.259878e-05
- `obs_backpressure_startup_sequential_w`: 8.318224e-05
- `obs_backpressure_startup_combinational_w`: 1.169026e-05
- `obs_backpressure_startup_total_a`: 4.582373e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.477403e-04
- `obs_backpressure_steady_internal_w`: 1.048896e-04
- `obs_backpressure_steady_switching_w`: 4.266323e-05
- `obs_backpressure_steady_leakage_w`: 1.874145e-07
- `obs_backpressure_steady_clock_w`: 4.259878e-05
- `obs_backpressure_steady_sequential_w`: 8.833004e-05
- `obs_backpressure_steady_combinational_w`: 1.681152e-05
- `obs_backpressure_steady_total_a`: 4.924677e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.223614e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.059517e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.158651e-05
- `obs_conditioned_streaming_reset_leakage_w`: 1.797297e-07
- `obs_conditioned_streaming_reset_clock_w`: 4.259878e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.633903e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.423750e-06
- `obs_conditioned_streaming_reset_total_a`: 4.078713e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.378225e-04
- `obs_conditioned_streaming_startup_internal_w`: 9.912057e-05
- `obs_conditioned_streaming_startup_switching_w`: 3.851702e-05
- `obs_conditioned_streaming_startup_leakage_w`: 1.849570e-07
- `obs_conditioned_streaming_startup_clock_w`: 4.259878e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.333383e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.189007e-05
- `obs_conditioned_streaming_startup_total_a`: 4.594083e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.479351e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.049601e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.278817e-05
- `obs_conditioned_streaming_steady_leakage_w`: 1.867787e-07
- `obs_conditioned_streaming_steady_clock_w`: 4.259878e-05
- `obs_conditioned_streaming_steady_sequential_w`: 8.831080e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.702551e-05
- `obs_conditioned_streaming_steady_total_a`: 4.931170e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.216610e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.033894e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.114232e-05
- `obs_disabled_clock_running_reset_leakage_w`: 1.797297e-07
- `obs_disabled_clock_running_reset_clock_w`: 4.259878e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.630672e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.755626e-06
- `obs_disabled_clock_running_reset_total_a`: 4.055367e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.246879e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.236763e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.213794e-05
- `obs_disabled_clock_running_startup_leakage_w`: 1.823146e-07
- `obs_disabled_clock_running_startup_clock_w`: 4.259878e-05
- `obs_disabled_clock_running_startup_sequential_w`: 7.752480e-05
- `obs_disabled_clock_running_startup_combinational_w`: 4.564394e-06
- `obs_disabled_clock_running_startup_total_a`: 4.156263e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.245399e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.227532e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.208229e-05
- `obs_disabled_clock_running_steady_leakage_w`: 1.823140e-07
- `obs_disabled_clock_running_steady_clock_w`: 4.259878e-05
- `obs_disabled_clock_running_steady_sequential_w`: 7.756437e-05
- `obs_disabled_clock_running_steady_combinational_w`: 4.376832e-06
- `obs_disabled_clock_running_steady_total_a`: 4.151330e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.226013e-04
- `obs_raw_streaming_reset_internal_w`: 9.064390e-05
- `obs_raw_streaming_reset_switching_w`: 3.177766e-05
- `obs_raw_streaming_reset_leakage_w`: 1.797297e-07
- `obs_raw_streaming_reset_clock_w`: 4.259878e-05
- `obs_raw_streaming_reset_sequential_w`: 7.633900e-05
- `obs_raw_streaming_reset_combinational_w`: 3.663667e-06
- `obs_raw_streaming_reset_total_a`: 4.086710e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.385322e-04
- `obs_raw_streaming_startup_internal_w`: 9.937271e-05
- `obs_raw_streaming_startup_switching_w`: 3.897458e-05
- `obs_raw_streaming_startup_leakage_w`: 1.849621e-07
- `obs_raw_streaming_startup_clock_w`: 4.259878e-05
- `obs_raw_streaming_startup_sequential_w`: 8.334044e-05
- `obs_raw_streaming_startup_combinational_w`: 1.259317e-05
- `obs_raw_streaming_startup_total_a`: 4.617740e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.487235e-04
- `obs_raw_streaming_steady_internal_w`: 1.052544e-04
- `obs_raw_streaming_steady_switching_w`: 4.328180e-05
- `obs_raw_streaming_steady_leakage_w`: 1.872706e-07
- `obs_raw_streaming_steady_clock_w`: 4.259878e-05
- `obs_raw_streaming_steady_sequential_w`: 8.833351e-05
- `obs_raw_streaming_steady_combinational_w`: 1.779120e-05
- `obs_raw_streaming_steady_total_a`: 4.957450e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
