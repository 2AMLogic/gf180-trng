---
record: 2026-11-13-digital-sta-activity-15
date: 2026-11-13T22:55:00Z
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
  temperature: -40
  liberty: gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60
  interconnect: max (OpenRCX rule deck)
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
  spef_sha256: 41a9a9724ecebfedc86c22aaee207e21c18b471825d556dde24a1a0f7b53d202
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
  path: sim/records/raw/2026-11-13-digital-sta-activity-15/
  files:
    - uniform.tcl  sha256:1f2597c15e6157b5b003dad23470e78efe88e0a300a66a2ebd76e1bb34ab06f4
    - uniform.log  sha256:ced8f7f656f78721c55822e0b4dc7b810c694baf32ff54d79d871354514b15de
    - observed.tcl  sha256:b678f093df32f7c3a72c2d349f441711b21fffeb575066c6e0ffd60adaf41aec
    - observed.log  sha256:88072af5d6c23426c66299622af872072bb42e4ecba6db8b11806570fe8fe684
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 8.7s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    211.73 |     97.62 |      0.25 |    309.60 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    141.06 |     46.78 |      0.24 |    188.08 | 0.607 | 5145 / 0 |
| alarm-gated | startup | 1040 |    156.82 |     57.29 |      0.25 |    214.36 | 0.692 | 5145 / 0 |
| alarm-gated | steady | 1024 |    152.79 |     54.28 |      0.25 |    207.31 | 0.670 | 5145 / 0 |
| backpressure | reset | 8 |    141.00 |     46.66 |      0.24 |    187.90 | 0.607 | 5145 / 0 |
| backpressure | startup | 1040 |    157.16 |     57.49 |      0.25 |    214.90 | 0.694 | 5145 / 0 |
| backpressure | steady | 1024 |    166.97 |     64.05 |      0.25 |    231.28 | 0.747 | 5145 / 0 |
| conditioned-streaming | reset | 8 |    141.05 |     46.75 |      0.24 |    188.04 | 0.607 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    157.57 |     57.80 |      0.25 |    215.62 | 0.696 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    167.16 |     64.26 |      0.25 |    231.68 | 0.748 | 5145 / 0 |
| disabled-clock-running | reset | 8 |    140.27 |     45.99 |      0.24 |    186.50 | 0.602 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |    143.91 |     47.99 |      0.24 |    192.14 | 0.621 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |    143.76 |     47.92 |      0.24 |    191.92 | 0.620 | 5145 / 0 |
| raw-streaming | reset | 8 |    140.92 |     46.93 |      0.24 |    188.09 | 0.608 | 5145 / 0 |
| raw-streaming | startup | 1040 |    157.66 |     58.34 |      0.25 |    216.25 | 0.698 | 5145 / 0 |
| raw-streaming | steady | 1024 |    167.51 |     64.94 |      0.25 |    232.70 | 0.752 | 5145 / 0 |

- `uniform_total_w`: 3.096013e-04
- `uniform_internal_w`: 2.117341e-04
- `uniform_switching_w`: 9.761686e-05
- `uniform_leakage_w`: 2.502879e-07
- `uniform_clock_w`: 6.999944e-05
- `uniform_sequential_w`: 1.589186e-04
- `uniform_combinational_w`: 8.068316e-05
- `uniform_total_a`: 8.600036e-05
- `obs_alarm_gated_reset_total_w`: 1.880827e-04
- `obs_alarm_gated_reset_internal_w`: 1.410629e-04
- `obs_alarm_gated_reset_switching_w`: 4.678047e-05
- `obs_alarm_gated_reset_leakage_w`: 2.393473e-07
- `obs_alarm_gated_reset_clock_w`: 6.999944e-05
- `obs_alarm_gated_reset_sequential_w`: 1.132988e-04
- `obs_alarm_gated_reset_combinational_w`: 4.784436e-06
- `obs_alarm_gated_reset_total_a`: 5.224519e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.143643e-04
- `obs_alarm_gated_startup_internal_w`: 1.568233e-04
- `obs_alarm_gated_startup_switching_w`: 5.729425e-05
- `obs_alarm_gated_startup_leakage_w`: 2.467408e-07
- `obs_alarm_gated_startup_clock_w`: 6.999944e-05
- `obs_alarm_gated_startup_sequential_w`: 1.249190e-04
- `obs_alarm_gated_startup_combinational_w`: 1.944575e-05
- `obs_alarm_gated_startup_total_a`: 5.954564e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.073117e-04
- `obs_alarm_gated_steady_internal_w`: 1.527875e-04
- `obs_alarm_gated_steady_switching_w`: 5.427785e-05
- `obs_alarm_gated_steady_leakage_w`: 2.463008e-07
- `obs_alarm_gated_steady_clock_w`: 6.999944e-05
- `obs_alarm_gated_steady_sequential_w`: 1.227047e-04
- `obs_alarm_gated_steady_combinational_w`: 1.460761e-05
- `obs_alarm_gated_steady_total_a`: 5.758658e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.879004e-04
- `obs_backpressure_reset_internal_w`: 1.410036e-04
- `obs_backpressure_reset_switching_w`: 4.665743e-05
- `obs_backpressure_reset_leakage_w`: 2.393473e-07
- `obs_backpressure_reset_clock_w`: 6.999944e-05
- `obs_backpressure_reset_sequential_w`: 1.132887e-04
- `obs_backpressure_reset_combinational_w`: 4.612257e-06
- `obs_backpressure_reset_total_a`: 5.219456e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.149034e-04
- `obs_backpressure_startup_internal_w`: 1.571645e-04
- `obs_backpressure_startup_switching_w`: 5.749186e-05
- `obs_backpressure_startup_leakage_w`: 2.470454e-07
- `obs_backpressure_startup_clock_w`: 6.999944e-05
- `obs_backpressure_startup_sequential_w`: 1.250515e-04
- `obs_backpressure_startup_combinational_w`: 1.985258e-05
- `obs_backpressure_startup_total_a`: 5.969539e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.312757e-04
- `obs_backpressure_steady_internal_w`: 1.669749e-04
- `obs_backpressure_steady_switching_w`: 6.404919e-05
- `obs_backpressure_steady_leakage_w`: 2.516043e-07
- `obs_backpressure_steady_clock_w`: 6.999944e-05
- `obs_backpressure_steady_sequential_w`: 1.334207e-04
- `obs_backpressure_steady_combinational_w`: 2.785571e-05
- `obs_backpressure_steady_total_a`: 6.424325e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.880425e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.410492e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.675398e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.393473e-07
- `obs_conditioned_streaming_reset_clock_w`: 6.999944e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.132988e-04
- `obs_conditioned_streaming_reset_combinational_w`: 4.744192e-06
- `obs_conditioned_streaming_reset_total_a`: 5.223403e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.156174e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.575706e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.780036e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.464123e-07
- `obs_conditioned_streaming_startup_clock_w`: 6.999944e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.253729e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.024507e-05
- `obs_conditioned_streaming_startup_total_a`: 5.989372e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.316754e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.671639e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.426110e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.503599e-07
- `obs_conditioned_streaming_steady_clock_w`: 6.999944e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.334666e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.820948e-05
- `obs_conditioned_streaming_steady_total_a`: 6.435428e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.864955e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.402711e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.598504e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.393473e-07
- `obs_disabled_clock_running_reset_clock_w`: 6.999944e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.132450e-04
- `obs_disabled_clock_running_reset_combinational_w`: 3.251056e-06
- `obs_disabled_clock_running_reset_total_a`: 5.180431e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.921380e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.439092e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.798690e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.419290e-07
- `obs_disabled_clock_running_startup_clock_w`: 6.999944e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.150892e-04
- `obs_disabled_clock_running_startup_combinational_w`: 7.049441e-06
- `obs_disabled_clock_running_startup_total_a`: 5.337167e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.919222e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.437611e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.791909e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.419288e-07
- `obs_disabled_clock_running_steady_clock_w`: 6.999944e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.151461e-04
- `obs_disabled_clock_running_steady_combinational_w`: 6.776565e-06
- `obs_disabled_clock_running_steady_total_a`: 5.331172e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.880942e-04
- `obs_raw_streaming_reset_internal_w`: 1.409227e-04
- `obs_raw_streaming_reset_switching_w`: 4.693208e-05
- `obs_raw_streaming_reset_leakage_w`: 2.393473e-07
- `obs_raw_streaming_reset_clock_w`: 6.999944e-05
- `obs_raw_streaming_reset_sequential_w`: 1.132952e-04
- `obs_raw_streaming_reset_combinational_w`: 4.799549e-06
- `obs_raw_streaming_reset_total_a`: 5.224839e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.162458e-04
- `obs_raw_streaming_startup_internal_w`: 1.576612e-04
- `obs_raw_streaming_startup_switching_w`: 5.833806e-05
- `obs_raw_streaming_startup_leakage_w`: 2.465095e-07
- `obs_raw_streaming_startup_clock_w`: 6.999944e-05
- `obs_raw_streaming_startup_sequential_w`: 1.251145e-04
- `obs_raw_streaming_startup_combinational_w`: 2.113177e-05
- `obs_raw_streaming_startup_total_a`: 6.006828e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.326992e-04
- `obs_raw_streaming_steady_internal_w`: 1.675060e-04
- `obs_raw_streaming_steady_switching_w`: 6.494173e-05
- `obs_raw_streaming_steady_leakage_w`: 2.513999e-07
- `obs_raw_streaming_steady_clock_w`: 6.999944e-05
- `obs_raw_streaming_steady_sequential_w`: 1.334071e-04
- `obs_raw_streaming_steady_combinational_w`: 2.929249e-05
- `obs_raw_streaming_steady_total_a`: 6.463867e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_n40C_3v60 --rc max --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_n40C_3v60, interconnect `max`).
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
