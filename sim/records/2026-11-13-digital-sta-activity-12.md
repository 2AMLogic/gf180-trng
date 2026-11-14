---
record: 2026-11-13-digital-sta-activity-12
date: 2026-11-13T22:54:34Z
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
  spef_sha256: 4a0445bda78087916cf9487697295175e7ee38e57843a80e389d1d84e323c78e
  spef_bytes: 1680256
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
  path: sim/records/raw/2026-11-13-digital-sta-activity-12/
  files:
    - uniform.tcl  sha256:7d64937069c0d472bd83f8bbf4b4f8eb917d9a507979c8bd0b216270207e5b36
    - uniform.log  sha256:3fdf02b231fab867aa37582f918333bb3328b22f8ba5f38bc3af2ab2b81d068f
    - observed.tcl  sha256:08aeac19ecf28abebac52fef1a32d4f3c7e1ca461ce3684f16bad37d1b189ffc
    - observed.log  sha256:75cd51f81285b313556f0217b5446cefeda8eb915c97e1b077bf9d3db428cfd2
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 8.7s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    232.49 |     98.04 |      7.58 |    338.12 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    153.04 |     47.02 |      7.00 |    207.06 | 0.612 | 5145 / 0 |
| alarm-gated | startup | 1040 |    170.87 |     57.57 |      7.65 |    236.10 | 0.698 | 5145 / 0 |
| alarm-gated | steady | 1024 |    166.29 |     54.54 |      7.64 |    228.46 | 0.676 | 5145 / 0 |
| backpressure | reset | 8 |    152.97 |     46.89 |      7.00 |    206.87 | 0.612 | 5145 / 0 |
| backpressure | startup | 1040 |    171.26 |     57.77 |      7.62 |    236.65 | 0.700 | 5145 / 0 |
| backpressure | steady | 1024 |    182.36 |     64.35 |      7.94 |    254.65 | 0.753 | 5145 / 0 |
| conditioned-streaming | reset | 8 |    153.02 |     46.99 |      7.00 |    207.02 | 0.612 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    171.71 |     58.08 |      7.63 |    237.43 | 0.702 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    182.57 |     64.57 |      7.85 |    254.99 | 0.754 | 5145 / 0 |
| disabled-clock-running | reset | 8 |    152.14 |     46.22 |      7.00 |    205.36 | 0.607 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |    156.35 |     48.24 |      7.34 |    211.92 | 0.627 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |    156.18 |     48.17 |      7.34 |    211.68 | 0.626 | 5145 / 0 |
| raw-streaming | reset | 8 |    152.89 |     47.17 |      7.00 |    207.06 | 0.612 | 5145 / 0 |
| raw-streaming | startup | 1040 |    171.82 |     58.62 |      7.58 |    238.02 | 0.704 | 5145 / 0 |
| raw-streaming | steady | 1024 |    182.96 |     65.25 |      7.86 |    256.06 | 0.757 | 5145 / 0 |

- `uniform_total_w`: 3.381151e-04
- `uniform_internal_w`: 2.324919e-04
- `uniform_switching_w`: 9.804400e-05
- `uniform_leakage_w`: 7.579158e-06
- `uniform_clock_w`: 7.672716e-05
- `uniform_sequential_w`: 1.718934e-04
- `uniform_combinational_w`: 8.949448e-05
- `uniform_total_a`: 9.392086e-05
- `obs_alarm_gated_reset_total_w`: 2.070581e-04
- `obs_alarm_gated_reset_internal_w`: 1.530387e-04
- `obs_alarm_gated_reset_switching_w`: 4.701726e-05
- `obs_alarm_gated_reset_leakage_w`: 7.002188e-06
- `obs_alarm_gated_reset_clock_w`: 7.672716e-05
- `obs_alarm_gated_reset_sequential_w`: 1.225571e-04
- `obs_alarm_gated_reset_combinational_w`: 7.773820e-06
- `obs_alarm_gated_reset_total_a`: 5.751614e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.360975e-04
- `obs_alarm_gated_startup_internal_w`: 1.708700e-04
- `obs_alarm_gated_startup_switching_w`: 5.757356e-05
- `obs_alarm_gated_startup_leakage_w`: 7.653976e-06
- `obs_alarm_gated_startup_clock_w`: 7.672716e-05
- `obs_alarm_gated_startup_sequential_w`: 1.352752e-04
- `obs_alarm_gated_startup_combinational_w`: 2.409519e-05
- `obs_alarm_gated_startup_total_a`: 6.558264e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.284649e-04
- `obs_alarm_gated_steady_internal_w`: 1.662892e-04
- `obs_alarm_gated_steady_switching_w`: 5.454027e-05
- `obs_alarm_gated_steady_leakage_w`: 7.635392e-06
- `obs_alarm_gated_steady_clock_w`: 7.672716e-05
- `obs_alarm_gated_steady_sequential_w`: 1.329022e-04
- `obs_alarm_gated_steady_combinational_w`: 1.883557e-05
- `obs_alarm_gated_steady_total_a`: 6.346247e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.068693e-04
- `obs_backpressure_reset_internal_w`: 1.529738e-04
- `obs_backpressure_reset_switching_w`: 4.689335e-05
- `obs_backpressure_reset_leakage_w`: 7.002188e-06
- `obs_backpressure_reset_clock_w`: 7.672716e-05
- `obs_backpressure_reset_sequential_w`: 1.225462e-04
- `obs_backpressure_reset_combinational_w`: 7.595988e-06
- `obs_backpressure_reset_total_a`: 5.746369e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.366509e-04
- `obs_backpressure_startup_internal_w`: 1.712566e-04
- `obs_backpressure_startup_switching_w`: 5.777176e-05
- `obs_backpressure_startup_leakage_w`: 7.622532e-06
- `obs_backpressure_startup_clock_w`: 7.672716e-05
- `obs_backpressure_startup_sequential_w`: 1.354238e-04
- `obs_backpressure_startup_combinational_w`: 2.450020e-05
- `obs_backpressure_startup_total_a`: 6.573636e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.546469e-04
- `obs_backpressure_steady_internal_w`: 1.823568e-04
- `obs_backpressure_steady_switching_w`: 6.435313e-05
- `obs_backpressure_steady_leakage_w`: 7.936968e-06
- `obs_backpressure_steady_clock_w`: 7.672716e-05
- `obs_backpressure_steady_sequential_w`: 1.445635e-04
- `obs_backpressure_steady_combinational_w`: 3.335629e-05
- `obs_backpressure_steady_total_a`: 7.073525e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.070165e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.530239e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.699046e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.002188e-06
- `obs_conditioned_streaming_reset_clock_w`: 7.672716e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.225571e-04
- `obs_conditioned_streaming_reset_combinational_w`: 7.732184e-06
- `obs_conditioned_streaming_reset_total_a`: 5.750458e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.374298e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.717148e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.808079e-05
- `obs_conditioned_streaming_startup_leakage_w`: 7.634230e-06
- `obs_conditioned_streaming_startup_clock_w`: 7.672716e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.357491e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.495371e-05
- `obs_conditioned_streaming_startup_total_a`: 6.595272e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.549920e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.825738e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.456538e-05
- `obs_conditioned_streaming_steady_leakage_w`: 7.852875e-06
- `obs_conditioned_streaming_steady_clock_w`: 7.672716e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.445935e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.367151e-05
- `obs_conditioned_streaming_steady_total_a`: 7.083111e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 2.053634e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.521425e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.621863e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.002188e-06
- `obs_disabled_clock_running_reset_clock_w`: 7.672716e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.224971e-04
- `obs_disabled_clock_running_reset_combinational_w`: 6.139059e-06
- `obs_disabled_clock_running_reset_total_a`: 5.704539e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.119201e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.563498e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.823503e-05
- `obs_disabled_clock_running_startup_leakage_w`: 7.335305e-06
- `obs_disabled_clock_running_startup_clock_w`: 7.672716e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.247506e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.044236e-05
- `obs_disabled_clock_running_startup_total_a`: 5.886669e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.116822e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.561793e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.816706e-05
- `obs_disabled_clock_running_steady_leakage_w`: 7.335824e-06
- `obs_disabled_clock_running_steady_clock_w`: 7.672716e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.248075e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.014767e-05
- `obs_disabled_clock_running_steady_total_a`: 5.880061e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.070577e-04
- `obs_raw_streaming_reset_internal_w`: 1.528855e-04
- `obs_raw_streaming_reset_switching_w`: 4.716995e-05
- `obs_raw_streaming_reset_leakage_w`: 7.002188e-06
- `obs_raw_streaming_reset_clock_w`: 7.672716e-05
- `obs_raw_streaming_reset_sequential_w`: 1.225526e-04
- `obs_raw_streaming_reset_combinational_w`: 7.777848e-06
- `obs_raw_streaming_reset_total_a`: 5.751603e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.380171e-04
- `obs_raw_streaming_startup_internal_w`: 1.718198e-04
- `obs_raw_streaming_startup_switching_w`: 5.862114e-05
- `obs_raw_streaming_startup_leakage_w`: 7.576150e-06
- `obs_raw_streaming_startup_clock_w`: 7.672716e-05
- `obs_raw_streaming_startup_sequential_w`: 1.354821e-04
- `obs_raw_streaming_startup_combinational_w`: 2.580785e-05
- `obs_raw_streaming_startup_total_a`: 6.611586e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.560629e-04
- `obs_raw_streaming_steady_internal_w`: 1.829588e-04
- `obs_raw_streaming_steady_switching_w`: 6.524905e-05
- `obs_raw_streaming_steady_leakage_w`: 7.855031e-06
- `obs_raw_streaming_steady_clock_w`: 7.672716e-05
- `obs_raw_streaming_steady_sequential_w`: 1.445441e-04
- `obs_raw_streaming_steady_combinational_w`: 3.479172e-05
- `obs_raw_streaming_steady_total_a`: 7.112858e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
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
