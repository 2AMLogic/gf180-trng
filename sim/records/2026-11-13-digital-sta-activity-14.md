---
record: 2026-11-13-digital-sta-activity-14
date: 2026-11-13T22:54:51Z
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
  - rules.openrcx.gf180mcuD.nom (OpenRCX interconnect corner nom, sha256:d83a04ea28af9b74a097fb479bbab9ed52859a1e3428b33d3151cb5afae62ddf)
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
  interconnect: nom (OpenRCX rule deck)
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
  spef_sha256: 0d03ea3a5c9fa1bb406b764845cbb0e50b06d4fa4d15ed523a490409704e9ff1
  spef_bytes: 1671005
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
  path: sim/records/raw/2026-11-13-digital-sta-activity-14/
  files:
    - uniform.tcl  sha256:998f05908bc6aac6cd701606eb87a760317f1cfdab83c9b930a69c703dba0ff5
    - uniform.log  sha256:b4b302dc583e12fe646ff02da5bf9015daa29b06fca72283db3b9538acf12c3d
    - observed.tcl  sha256:5dd071d982cc369ef13c00398dafc2335c5b4d147b7925adf3f8c460f97f7ba3
    - observed.log  sha256:6cdbfd99ed9ed604e9f2a640301e0d226a6530df5b7d93509637bac22af2fd0b
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 9.0s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    210.90 |     93.71 |      0.25 |    304.87 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    140.40 |     45.03 |      0.24 |    185.67 | 0.609 | 5145 / 0 |
| alarm-gated | startup | 1040 |    156.15 |     55.20 |      0.25 |    211.60 | 0.694 | 5145 / 0 |
| alarm-gated | steady | 1024 |    152.12 |     52.27 |      0.25 |    204.63 | 0.671 | 5145 / 0 |
| backpressure | reset | 8 |    140.34 |     44.91 |      0.24 |    185.49 | 0.608 | 5145 / 0 |
| backpressure | startup | 1040 |    156.49 |     55.40 |      0.25 |    212.13 | 0.696 | 5145 / 0 |
| backpressure | steady | 1024 |    166.27 |     61.70 |      0.25 |    228.23 | 0.749 | 5145 / 0 |
| conditioned-streaming | reset | 8 |    140.39 |     45.00 |      0.24 |    185.63 | 0.609 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    156.90 |     55.69 |      0.25 |    212.83 | 0.698 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    166.46 |     61.90 |      0.25 |    228.61 | 0.750 | 5145 / 0 |
| disabled-clock-running | reset | 8 |    139.62 |     44.26 |      0.24 |    184.12 | 0.604 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |    143.25 |     46.23 |      0.24 |    189.72 | 0.622 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |    143.10 |     46.16 |      0.24 |    189.50 | 0.622 | 5145 / 0 |
| raw-streaming | reset | 8 |    140.27 |     45.17 |      0.24 |    185.68 | 0.609 | 5145 / 0 |
| raw-streaming | startup | 1040 |    156.98 |     56.20 |      0.25 |    213.43 | 0.700 | 5145 / 0 |
| raw-streaming | steady | 1024 |    166.80 |     62.55 |      0.25 |    229.60 | 0.753 | 5145 / 0 |

- `uniform_total_w`: 3.048657e-04
- `uniform_internal_w`: 2.109025e-04
- `uniform_switching_w`: 9.371290e-05
- `uniform_leakage_w`: 2.502879e-07
- `uniform_clock_w`: 6.798398e-05
- `uniform_sequential_w`: 1.581809e-04
- `uniform_combinational_w`: 7.870098e-05
- `uniform_total_a`: 8.468492e-05
- `obs_alarm_gated_reset_total_w`: 1.856703e-04
- `obs_alarm_gated_reset_internal_w`: 1.404030e-04
- `obs_alarm_gated_reset_switching_w`: 4.502797e-05
- `obs_alarm_gated_reset_leakage_w`: 2.393473e-07
- `obs_alarm_gated_reset_clock_w`: 6.798398e-05
- `obs_alarm_gated_reset_sequential_w`: 1.130107e-04
- `obs_alarm_gated_reset_combinational_w`: 4.675717e-06
- `obs_alarm_gated_reset_total_a`: 5.157508e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.116008e-04
- `obs_alarm_gated_startup_internal_w`: 1.561492e-04
- `obs_alarm_gated_startup_switching_w`: 5.520485e-05
- `obs_alarm_gated_startup_leakage_w`: 2.467408e-07
- `obs_alarm_gated_startup_clock_w`: 6.798398e-05
- `obs_alarm_gated_startup_sequential_w`: 1.244710e-04
- `obs_alarm_gated_startup_combinational_w`: 1.914587e-05
- `obs_alarm_gated_startup_total_a`: 5.877800e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.046305e-04
- `obs_alarm_gated_steady_internal_w`: 1.521192e-04
- `obs_alarm_gated_steady_switching_w`: 5.226507e-05
- `obs_alarm_gated_steady_leakage_w`: 2.463008e-07
- `obs_alarm_gated_steady_clock_w`: 6.798398e-05
- `obs_alarm_gated_steady_sequential_w`: 1.222760e-04
- `obs_alarm_gated_steady_combinational_w`: 1.437050e-05
- `obs_alarm_gated_steady_total_a`: 5.684181e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.854907e-04
- `obs_backpressure_reset_internal_w`: 1.403437e-04
- `obs_backpressure_reset_switching_w`: 4.490762e-05
- `obs_backpressure_reset_leakage_w`: 2.393473e-07
- `obs_backpressure_reset_clock_w`: 6.798398e-05
- `obs_backpressure_reset_sequential_w`: 1.130005e-04
- `obs_backpressure_reset_combinational_w`: 4.506188e-06
- `obs_backpressure_reset_total_a`: 5.152519e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.121327e-04
- `obs_backpressure_startup_internal_w`: 1.564904e-04
- `obs_backpressure_startup_switching_w`: 5.539519e-05
- `obs_backpressure_startup_leakage_w`: 2.470454e-07
- `obs_backpressure_startup_clock_w`: 6.798398e-05
- `obs_backpressure_startup_sequential_w`: 1.246019e-04
- `obs_backpressure_startup_combinational_w`: 1.954694e-05
- `obs_backpressure_startup_total_a`: 5.892575e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.282257e-04
- `obs_backpressure_steady_internal_w`: 1.662734e-04
- `obs_backpressure_steady_switching_w`: 6.170074e-05
- `obs_backpressure_steady_leakage_w`: 2.516043e-07
- `obs_backpressure_steady_clock_w`: 6.798398e-05
- `obs_backpressure_steady_sequential_w`: 1.328752e-04
- `obs_backpressure_steady_combinational_w`: 2.736649e-05
- `obs_backpressure_steady_total_a`: 6.339603e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.856302e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.403893e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.500153e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.393473e-07
- `obs_conditioned_streaming_reset_clock_w`: 6.798398e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.130107e-04
- `obs_conditioned_streaming_reset_combinational_w`: 4.635528e-06
- `obs_conditioned_streaming_reset_total_a`: 5.156394e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.128346e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.568962e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.569195e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.464123e-07
- `obs_conditioned_streaming_startup_clock_w`: 6.798398e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.249175e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.993325e-05
- `obs_conditioned_streaming_startup_total_a`: 5.912072e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.286147e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.664620e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.190235e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.503599e-07
- `obs_conditioned_streaming_steady_clock_w`: 6.798398e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.329184e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.771219e-05
- `obs_conditioned_streaming_steady_total_a`: 6.350408e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.841162e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.396154e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.426146e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.393473e-07
- `obs_disabled_clock_running_reset_clock_w`: 6.798398e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.129569e-04
- `obs_disabled_clock_running_reset_combinational_w`: 3.175389e-06
- `obs_disabled_clock_running_reset_total_a`: 5.114339e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.897154e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.432479e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.622554e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.419290e-07
- `obs_disabled_clock_running_startup_clock_w`: 6.798398e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.147772e-04
- `obs_disabled_clock_running_startup_combinational_w`: 6.954214e-06
- `obs_disabled_clock_running_startup_total_a`: 5.269872e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.895025e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.430999e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.616073e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.419288e-07
- `obs_disabled_clock_running_steady_clock_w`: 6.798398e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.148329e-04
- `obs_disabled_clock_running_steady_combinational_w`: 6.685701e-06
- `obs_disabled_clock_running_steady_total_a`: 5.263958e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.856756e-04
- `obs_raw_streaming_reset_internal_w`: 1.402652e-04
- `obs_raw_streaming_reset_switching_w`: 4.517108e-05
- `obs_raw_streaming_reset_leakage_w`: 2.393473e-07
- `obs_raw_streaming_reset_clock_w`: 6.798398e-05
- `obs_raw_streaming_reset_sequential_w`: 1.130070e-04
- `obs_raw_streaming_reset_combinational_w`: 4.684603e-06
- `obs_raw_streaming_reset_total_a`: 5.157656e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.134295e-04
- `obs_raw_streaming_startup_internal_w`: 1.569844e-04
- `obs_raw_streaming_startup_switching_w`: 5.619865e-05
- `obs_raw_streaming_startup_leakage_w`: 2.465095e-07
- `obs_raw_streaming_startup_clock_w`: 6.798398e-05
- `obs_raw_streaming_startup_sequential_w`: 1.246642e-04
- `obs_raw_streaming_startup_combinational_w`: 2.078146e-05
- `obs_raw_streaming_startup_total_a`: 5.928597e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.296030e-04
- `obs_raw_streaming_steady_internal_w`: 1.668019e-04
- `obs_raw_streaming_steady_switching_w`: 6.254976e-05
- `obs_raw_streaming_steady_leakage_w`: 2.513999e-07
- `obs_raw_streaming_steady_clock_w`: 6.798398e-05
- `obs_raw_streaming_steady_sequential_w`: 1.328619e-04
- `obs_raw_streaming_steady_combinational_w`: 2.875702e-05
- `obs_raw_streaming_steady_total_a`: 6.377861e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_n40C_3v60 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_n40C_3v60, interconnect `nom`).
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
