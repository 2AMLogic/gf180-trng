---
record: 2026-11-13-digital-sta-activity-08
date: 2026-11-13T22:53:59Z
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
  - gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30.lib (liberty corner tt_025C_3v30, sha256:1157d0aa147dba75a214708197d7a046f970175d723cdec108025f6f06727c12)
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
  process: tt
  voltage: 3.30 V (nominal 3.3 V)
  temperature: 25
  liberty: gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30
  interconnect: nom (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature 25, nom_voltage 3.3 (read from the deck)

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
  spef_sha256: e9028975a92bb4c7734b26defe303c654f4580aad4f012b0683df392be7365fd
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
  path: sim/records/raw/2026-11-13-digital-sta-activity-08/
  files:
    - uniform.tcl  sha256:c1f90be17cbbf8eea942737e080ad93fcbfca18b22580d12b7492560e15177ec
    - uniform.log  sha256:586a6a9e346ef63ce322a435cea31b95acafb65a74d6809cf80d103f0c671b23
    - observed.tcl  sha256:34fbbe5abd9e2d2db8d32188f13020b7d9d51ba19879847cb7d97544a474888d
    - observed.log  sha256:16fbbce16fb388c9a56232f7ab292395db4c378e1cf6bdefcd090d40cf9fbedb
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 9.0s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    171.88 |     78.70 |      0.21 |    250.79 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    114.82 |     37.79 |      0.20 |    152.81 | 0.609 | 5145 / 0 |
| alarm-gated | startup | 1040 |    127.65 |     46.33 |      0.21 |    174.19 | 0.695 | 5145 / 0 |
| alarm-gated | steady | 1024 |    124.39 |     43.86 |      0.21 |    168.46 | 0.672 | 5145 / 0 |
| backpressure | reset | 8 |    114.77 |     37.69 |      0.20 |    152.66 | 0.609 | 5145 / 0 |
| backpressure | startup | 1040 |    127.93 |     46.49 |      0.21 |    174.63 | 0.696 | 5145 / 0 |
| backpressure | steady | 1024 |    135.86 |     51.79 |      0.22 |    187.87 | 0.749 | 5145 / 0 |
| conditioned-streaming | reset | 8 |    114.81 |     37.77 |      0.20 |    152.77 | 0.609 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    128.25 |     46.74 |      0.21 |    175.20 | 0.699 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    136.01 |     51.96 |      0.21 |    188.18 | 0.750 | 5145 / 0 |
| disabled-clock-running | reset | 8 |    114.19 |     37.15 |      0.20 |    151.54 | 0.604 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |    117.13 |     38.80 |      0.21 |    156.13 | 0.623 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |    117.01 |     38.74 |      0.21 |    155.96 | 0.622 | 5145 / 0 |
| raw-streaming | reset | 8 |    114.71 |     37.91 |      0.20 |    152.82 | 0.609 | 5145 / 0 |
| raw-streaming | startup | 1040 |    128.32 |     47.17 |      0.21 |    175.70 | 0.701 | 5145 / 0 |
| raw-streaming | steady | 1024 |    136.29 |     52.50 |      0.22 |    189.00 | 0.754 | 5145 / 0 |

- `uniform_total_w`: 2.507918e-04
- `uniform_internal_w`: 1.718816e-04
- `uniform_switching_w`: 7.869578e-05
- `uniform_leakage_w`: 2.144338e-07
- `uniform_clock_w`: 5.502301e-05
- `uniform_sequential_w`: 1.312118e-04
- `uniform_combinational_w`: 6.455702e-05
- `uniform_total_a`: 7.599752e-05
- `obs_alarm_gated_reset_total_w`: 1.528080e-04
- `obs_alarm_gated_reset_internal_w`: 1.148172e-04
- `obs_alarm_gated_reset_switching_w`: 3.778766e-05
- `obs_alarm_gated_reset_leakage_w`: 2.031384e-07
- `obs_alarm_gated_reset_clock_w`: 5.502301e-05
- `obs_alarm_gated_reset_sequential_w`: 9.391943e-05
- `obs_alarm_gated_reset_combinational_w`: 3.865488e-06
- `obs_alarm_gated_reset_total_a`: 4.630545e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.741894e-04
- `obs_alarm_gated_startup_internal_w`: 1.276464e-04
- `obs_alarm_gated_startup_switching_w`: 4.633178e-05
- `obs_alarm_gated_startup_leakage_w`: 2.111742e-07
- `obs_alarm_gated_startup_clock_w`: 5.502301e-05
- `obs_alarm_gated_startup_sequential_w`: 1.034189e-04
- `obs_alarm_gated_startup_combinational_w`: 1.574733e-05
- `obs_alarm_gated_startup_total_a`: 5.278467e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.684581e-04
- `obs_alarm_gated_steady_internal_w`: 1.243869e-04
- `obs_alarm_gated_steady_switching_w`: 4.386034e-05
- `obs_alarm_gated_steady_leakage_w`: 2.108011e-07
- `obs_alarm_gated_steady_clock_w`: 5.502301e-05
- `obs_alarm_gated_steady_sequential_w`: 1.016048e-04
- `obs_alarm_gated_steady_combinational_w`: 1.183025e-05
- `obs_alarm_gated_steady_total_a`: 5.104791e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.526572e-04
- `obs_backpressure_reset_internal_w`: 1.147678e-04
- `obs_backpressure_reset_switching_w`: 3.768632e-05
- `obs_backpressure_reset_leakage_w`: 2.031384e-07
- `obs_backpressure_reset_clock_w`: 5.502301e-05
- `obs_backpressure_reset_sequential_w`: 9.391076e-05
- `obs_backpressure_reset_combinational_w`: 3.723432e-06
- `obs_backpressure_reset_total_a`: 4.625976e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.746294e-04
- `obs_backpressure_startup_internal_w`: 1.279266e-04
- `obs_backpressure_startup_switching_w`: 4.649137e-05
- `obs_backpressure_startup_leakage_w`: 2.114715e-07
- `obs_backpressure_startup_clock_w`: 5.502301e-05
- `obs_backpressure_startup_sequential_w`: 1.035282e-04
- `obs_backpressure_startup_combinational_w`: 1.607818e-05
- `obs_backpressure_startup_total_a`: 5.291800e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.878662e-04
- `obs_backpressure_steady_internal_w`: 1.358612e-04
- `obs_backpressure_steady_switching_w`: 5.178901e-05
- `obs_backpressure_steady_leakage_w`: 2.159677e-07
- `obs_backpressure_steady_clock_w`: 5.502301e-05
- `obs_backpressure_steady_sequential_w`: 1.103306e-04
- `obs_backpressure_steady_combinational_w`: 2.251235e-05
- `obs_backpressure_steady_total_a`: 5.692915e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.527742e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.148057e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.776539e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.031384e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.502301e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.391942e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.831795e-06
- `obs_conditioned_streaming_reset_total_a`: 4.629521e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.752042e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.282534e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.673999e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.108036e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.502301e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.037864e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.639465e-05
- `obs_conditioned_streaming_startup_total_a`: 5.309218e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.881832e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.360102e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.195821e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.147684e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.502301e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.103633e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.279692e-05
- `obs_conditioned_streaming_steady_total_a`: 5.702521e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.515414e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.141932e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.714502e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.031384e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.502301e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.387491e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.643469e-06
- `obs_disabled_clock_running_reset_total_a`: 4.592164e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.561325e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.171274e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.879857e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.065109e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.502301e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.538929e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.720212e-06
- `obs_disabled_clock_running_startup_total_a`: 4.731288e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.559566e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.170059e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.874421e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.065113e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.502301e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.543608e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.497447e-06
- `obs_disabled_clock_running_steady_total_a`: 4.725958e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.528247e-04
- `obs_raw_streaming_reset_internal_w`: 1.147123e-04
- `obs_raw_streaming_reset_switching_w`: 3.790926e-05
- `obs_raw_streaming_reset_leakage_w`: 2.031384e-07
- `obs_raw_streaming_reset_clock_w`: 5.502301e-05
- `obs_raw_streaming_reset_sequential_w`: 9.391657e-05
- `obs_raw_streaming_reset_combinational_w`: 3.885129e-06
- `obs_raw_streaming_reset_total_a`: 4.631052e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.756972e-04
- `obs_raw_streaming_startup_internal_w`: 1.283197e-04
- `obs_raw_streaming_startup_switching_w`: 4.716659e-05
- `obs_raw_streaming_startup_leakage_w`: 2.109694e-07
- `obs_raw_streaming_startup_clock_w`: 5.502301e-05
- `obs_raw_streaming_startup_sequential_w`: 1.035792e-04
- `obs_raw_streaming_startup_combinational_w`: 1.709502e-05
- `obs_raw_streaming_startup_total_a`: 5.324158e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.890047e-04
- `obs_raw_streaming_steady_internal_w`: 1.362861e-04
- `obs_raw_streaming_steady_switching_w`: 5.250286e-05
- `obs_raw_streaming_steady_leakage_w`: 2.157574e-07
- `obs_raw_streaming_steady_clock_w`: 5.502301e-05
- `obs_raw_streaming_steady_sequential_w`: 1.103188e-04
- `obs_raw_streaming_steady_combinational_w`: 2.366300e-05
- `obs_raw_streaming_steady_total_a`: 5.727415e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty tt_025C_3v30 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (tt_025C_3v30, interconnect `nom`).
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
