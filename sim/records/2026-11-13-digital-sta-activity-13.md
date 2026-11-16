---
record: 2026-11-13-digital-sta-activity-13
date: 2026-11-13T22:54:42Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: 89e8f60a83222b44213d3c89a059db389405b475
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha 49a084e95789ff1acbd953235cf0612b7701ef36).
repo_commit: e783bb4f7336f4422aa26902c7003f638bccd0a7-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60.lib (liberty corner ff_n40C_3v60, sha256:0b48b93d6800da325a2613ff6c0b998b230a1bbd28031f6da592e9ff30066602)
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
  spef_sha256: df11c057bb9885b31175225a29cebe517e733326ed53b583cc094eee0695e582
  spef_bytes: 1665643
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
      vcd_sha256: 0afb5fb92799a03d3444e0f27eb960c2ee5ea62fff79b5a3a5094558e2df1b4b
      vcd_bytes: 17698640
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1424/1424
      xz_events: 4931
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: a4094cb39c49b436bd01e672cded18bb2da8efe3791a0abfc0fe57e9ea40ebe6
      vcd_bytes: 19126901
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 5074
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: a0eb1a5723562558fb1acfcf8d8c0701c6e1cfe4e7270ce8aebbb72dd962965d
      vcd_bytes: 19173873
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 4809
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: ea20e05c09b17231d8eeee57c82747b30afe2abf409e7db8ff7f17a08e0cabfc
      vcd_bytes: 13485290
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 2222
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: 700215612e809607908e9865420a657acd559ed311b8ef2c862483deac89df1b
      vcd_bytes: 19322913
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 5153
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-11-13-digital-sta-activity-13/
  files:
    - uniform.tcl  sha256:60897f4659d7de4c9ec0797cbf733ea0aa3b435066ee885be8717e83a2abc65a
    - uniform.log  sha256:8af271051ec55d9a3caa89b72d65a1dcde405c5147e5daf5ca5c87aa1decd312
    - observed.tcl  sha256:f120d282bb05e142f565e12189beeab7455130b9c7f5ac9ca2717f370688a7fc
    - observed.log  sha256:16d400263cac7a7aa5327ccd975a666f8c9fe33a4fb71096f96b235f751ac79b
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 8.7s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    210.24 |     90.53 |      0.25 |    301.02 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    139.87 |     43.60 |      0.24 |    183.71 | 0.610 | 5145 / 0 |
| alarm-gated | startup | 1040 |    155.61 |     53.50 |      0.25 |    209.35 | 0.695 | 5145 / 0 |
| alarm-gated | steady | 1024 |    151.58 |     50.62 |      0.25 |    202.45 | 0.673 | 5145 / 0 |
| backpressure | reset | 8 |    139.81 |     43.48 |      0.24 |    183.53 | 0.610 | 5145 / 0 |
| backpressure | startup | 1040 |    155.95 |     53.69 |      0.25 |    209.88 | 0.697 | 5145 / 0 |
| backpressure | steady | 1024 |    165.71 |     59.79 |      0.25 |    225.75 | 0.750 | 5145 / 0 |
| conditioned-streaming | reset | 8 |    139.86 |     43.57 |      0.24 |    183.67 | 0.610 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    156.35 |     53.97 |      0.25 |    210.57 | 0.700 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    165.90 |     59.98 |      0.25 |    226.13 | 0.751 | 5145 / 0 |
| disabled-clock-running | reset | 8 |    139.09 |     42.86 |      0.24 |    182.18 | 0.605 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |    142.71 |     44.79 |      0.24 |    187.75 | 0.624 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |    142.57 |     44.73 |      0.24 |    187.54 | 0.623 | 5145 / 0 |
| raw-streaming | reset | 8 |    139.73 |     43.74 |      0.24 |    183.71 | 0.610 | 5145 / 0 |
| raw-streaming | startup | 1040 |    156.44 |     54.46 |      0.25 |    211.14 | 0.701 | 5145 / 0 |
| raw-streaming | steady | 1024 |    166.23 |     60.60 |      0.25 |    227.09 | 0.754 | 5145 / 0 |

- `uniform_total_w`: 3.010166e-04
- `uniform_internal_w`: 2.102351e-04
- `uniform_switching_w`: 9.053129e-05
- `uniform_leakage_w`: 2.502879e-07
- `uniform_clock_w`: 6.634847e-05
- `uniform_sequential_w`: 1.575786e-04
- `uniform_combinational_w`: 7.708964e-05
- `uniform_total_a`: 8.361572e-05
- `obs_alarm_gated_reset_total_w`: 1.837105e-04
- `obs_alarm_gated_reset_internal_w`: 1.398703e-04
- `obs_alarm_gated_reset_switching_w`: 4.360088e-05
- `obs_alarm_gated_reset_leakage_w`: 2.393473e-07
- `obs_alarm_gated_reset_clock_w`: 6.634847e-05
- `obs_alarm_gated_reset_sequential_w`: 1.127743e-04
- `obs_alarm_gated_reset_combinational_w`: 4.587634e-06
- `obs_alarm_gated_reset_total_a`: 5.103069e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.093546e-04
- `obs_alarm_gated_startup_internal_w`: 1.556056e-04
- `obs_alarm_gated_startup_switching_w`: 5.350220e-05
- `obs_alarm_gated_startup_leakage_w`: 2.467408e-07
- `obs_alarm_gated_startup_clock_w`: 6.634847e-05
- `obs_alarm_gated_startup_sequential_w`: 1.241043e-04
- `obs_alarm_gated_startup_combinational_w`: 1.890189e-05
- `obs_alarm_gated_startup_total_a`: 5.815406e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.024511e-04
- `obs_alarm_gated_steady_internal_w`: 1.515801e-04
- `obs_alarm_gated_steady_switching_w`: 5.062476e-05
- `obs_alarm_gated_steady_leakage_w`: 2.463008e-07
- `obs_alarm_gated_steady_clock_w`: 6.634847e-05
- `obs_alarm_gated_steady_sequential_w`: 1.219251e-04
- `obs_alarm_gated_steady_combinational_w`: 1.417753e-05
- `obs_alarm_gated_steady_total_a`: 5.623642e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.835329e-04
- `obs_backpressure_reset_internal_w`: 1.398109e-04
- `obs_backpressure_reset_switching_w`: 4.348264e-05
- `obs_backpressure_reset_leakage_w`: 2.393473e-07
- `obs_backpressure_reset_clock_w`: 6.634847e-05
- `obs_backpressure_reset_sequential_w`: 1.127642e-04
- `obs_backpressure_reset_combinational_w`: 4.420195e-06
- `obs_backpressure_reset_total_a`: 5.098136e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.098805e-04
- `obs_backpressure_startup_internal_w`: 1.559468e-04
- `obs_backpressure_startup_switching_w`: 5.368662e-05
- `obs_backpressure_startup_leakage_w`: 2.470454e-07
- `obs_backpressure_startup_clock_w`: 6.634847e-05
- `obs_backpressure_startup_sequential_w`: 1.242339e-04
- `obs_backpressure_startup_combinational_w`: 1.929829e-05
- `obs_backpressure_startup_total_a`: 5.830014e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.257476e-04
- `obs_backpressure_steady_internal_w`: 1.657078e-04
- `obs_backpressure_steady_switching_w`: 5.978816e-05
- `obs_backpressure_steady_leakage_w`: 2.516043e-07
- `obs_backpressure_steady_clock_w`: 6.634847e-05
- `obs_backpressure_steady_sequential_w`: 1.324293e-04
- `obs_backpressure_steady_combinational_w`: 2.696953e-05
- `obs_backpressure_steady_total_a`: 6.270767e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.836703e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.398565e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.357444e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.393473e-07
- `obs_conditioned_streaming_reset_clock_w`: 6.634847e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.127743e-04
- `obs_conditioned_streaming_reset_combinational_w`: 4.547454e-06
- `obs_conditioned_streaming_reset_total_a`: 5.101953e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.105727e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.563525e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.397378e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.464123e-07
- `obs_conditioned_streaming_startup_clock_w`: 6.634847e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.245448e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.967960e-05
- `obs_conditioned_streaming_startup_total_a`: 5.849242e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.261276e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.658958e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.998140e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.503599e-07
- `obs_conditioned_streaming_steady_clock_w`: 6.634847e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.324703e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.730870e-05
- `obs_conditioned_streaming_steady_total_a`: 6.281322e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.821828e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.390855e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.285792e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.393473e-07
- `obs_disabled_clock_running_reset_clock_w`: 6.634847e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.127206e-04
- `obs_disabled_clock_running_reset_combinational_w`: 3.113693e-06
- `obs_disabled_clock_running_reset_total_a`: 5.060633e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.877470e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.427143e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.479075e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.419290e-07
- `obs_disabled_clock_running_startup_clock_w`: 6.634847e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.145214e-04
- `obs_disabled_clock_running_startup_combinational_w`: 6.877139e-06
- `obs_disabled_clock_running_startup_total_a`: 5.215194e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.875366e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.425663e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.472836e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.419288e-07
- `obs_disabled_clock_running_steady_clock_w`: 6.634847e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.145760e-04
- `obs_disabled_clock_running_steady_combinational_w`: 6.612154e-06
- `obs_disabled_clock_running_steady_total_a`: 5.209350e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.837106e-04
- `obs_raw_streaming_reset_internal_w`: 1.397341e-04
- `obs_raw_streaming_reset_switching_w`: 4.373714e-05
- `obs_raw_streaming_reset_leakage_w`: 2.393473e-07
- `obs_raw_streaming_reset_clock_w`: 6.634847e-05
- `obs_raw_streaming_reset_sequential_w`: 1.127707e-04
- `obs_raw_streaming_reset_combinational_w`: 4.591357e-06
- `obs_raw_streaming_reset_total_a`: 5.103072e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.111405e-04
- `obs_raw_streaming_startup_internal_w`: 1.564387e-04
- `obs_raw_streaming_startup_switching_w`: 5.445527e-05
- `obs_raw_streaming_startup_leakage_w`: 2.465095e-07
- `obs_raw_streaming_startup_clock_w`: 6.634847e-05
- `obs_raw_streaming_startup_sequential_w`: 1.242955e-04
- `obs_raw_streaming_startup_combinational_w`: 2.049657e-05
- `obs_raw_streaming_startup_total_a`: 5.865014e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.270875e-04
- `obs_raw_streaming_steady_internal_w`: 1.662343e-04
- `obs_raw_streaming_steady_switching_w`: 6.060182e-05
- `obs_raw_streaming_steady_leakage_w`: 2.513999e-07
- `obs_raw_streaming_steady_clock_w`: 6.634847e-05
- `obs_raw_streaming_steady_sequential_w`: 1.324163e-04
- `obs_raw_streaming_steady_combinational_w`: 2.832256e-05
- `obs_raw_streaming_steady_total_a`: 6.307986e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
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
