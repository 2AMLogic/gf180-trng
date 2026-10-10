---
record: 2026-10-10-digital-sta-activity-23
date: 2026-10-10T07:12:29Z
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
  - gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30.lib (liberty corner tt_025C_3v30, sha256:154655e033bec8509acca1575cc2e48e4d7143dfe70a8c61e0695f24c3dcaf02)
  - gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:332ae93d61ac55f793da97a6391703f78bc415653cb60e76dd8eb0092124485a)
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
  spef_sha256: a3b2d183bc7e85d2d66ce98ba48336f27ad04ee79ad3f614b5af1b1a53b777e6
  spef_bytes: 1769620
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-23/
  files:
    - uniform.tcl  sha256:1706eb2207a75c2ecd1c8ddf07afbd0886a6d13df9cfceca7dd8938557a49df3
    - uniform.log  sha256:0555575821d5730965797daa3ed2d6e2b4bddfc81a3e4928027a9bad9f33b3d8
    - observed.tcl  sha256:98adff815e273ba0cc5d2dd840997685c15dc780fd5f37e8b1008496ad20cedb
    - observed.log  sha256:1a10bed26003a63d7a7c07d78f572c4c8faa9bc9539a9eea10a4a05c52fdf28b
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 8.3s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    176.71 |     81.46 |      0.22 |    258.39 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    114.89 |     37.01 |      0.21 |    152.10 | 0.589 | 5371 / 0 |
| alarm-gated | startup | 1040 |    125.88 |     44.79 |      0.22 |    170.88 | 0.661 | 5371 / 0 |
| alarm-gated | steady | 1024 |    122.50 |     42.01 |      0.22 |    164.72 | 0.637 | 5371 / 0 |
| backpressure | reset | 8 |    114.84 |     36.90 |      0.21 |    151.95 | 0.588 | 5371 / 0 |
| backpressure | startup | 1040 |    126.07 |     44.92 |      0.22 |    171.21 | 0.663 | 5371 / 0 |
| backpressure | steady | 1024 |    133.94 |     50.12 |      0.22 |    184.28 | 0.713 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    114.88 |     36.98 |      0.21 |    152.07 | 0.589 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    126.28 |     45.15 |      0.22 |    171.65 | 0.664 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    134.04 |     50.26 |      0.22 |    184.52 | 0.714 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    114.53 |     36.43 |      0.21 |    151.17 | 0.585 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    117.32 |     37.65 |      0.21 |    155.18 | 0.601 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    117.19 |     37.59 |      0.21 |    154.99 | 0.600 | 5371 / 0 |
| raw-streaming | reset | 8 |    114.95 |     37.22 |      0.21 |    152.38 | 0.590 | 5371 / 0 |
| raw-streaming | startup | 1040 |    126.63 |     45.68 |      0.22 |    172.52 | 0.668 | 5371 / 0 |
| raw-streaming | steady | 1024 |    134.44 |     50.83 |      0.22 |    185.49 | 0.718 | 5371 / 0 |

- `uniform_total_w`: 2.583913e-04
- `uniform_internal_w`: 1.767101e-04
- `uniform_switching_w`: 8.146177e-05
- `uniform_leakage_w`: 2.193580e-07
- `uniform_clock_w`: 5.296115e-05
- `uniform_sequential_w`: 1.354667e-04
- `uniform_combinational_w`: 6.996332e-05
- `uniform_total_a`: 7.830039e-05
- `obs_alarm_gated_reset_total_w`: 1.521039e-04
- `obs_alarm_gated_reset_internal_w`: 1.148903e-04
- `obs_alarm_gated_reset_switching_w`: 3.700610e-05
- `obs_alarm_gated_reset_leakage_w`: 2.075095e-07
- `obs_alarm_gated_reset_clock_w`: 5.296115e-05
- `obs_alarm_gated_reset_sequential_w`: 9.491050e-05
- `obs_alarm_gated_reset_combinational_w`: 4.232218e-06
- `obs_alarm_gated_reset_total_a`: 4.609209e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.708800e-04
- `obs_alarm_gated_startup_internal_w`: 1.258776e-04
- `obs_alarm_gated_startup_switching_w`: 4.478579e-05
- `obs_alarm_gated_startup_leakage_w`: 2.165480e-07
- `obs_alarm_gated_startup_clock_w`: 5.296115e-05
- `obs_alarm_gated_startup_sequential_w`: 1.034425e-04
- `obs_alarm_gated_startup_combinational_w`: 1.447636e-05
- `obs_alarm_gated_startup_total_a`: 5.178182e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.647176e-04
- `obs_alarm_gated_steady_internal_w`: 1.224957e-04
- `obs_alarm_gated_steady_switching_w`: 4.200592e-05
- `obs_alarm_gated_steady_leakage_w`: 2.159064e-07
- `obs_alarm_gated_steady_clock_w`: 5.296115e-05
- `obs_alarm_gated_steady_sequential_w`: 1.012089e-04
- `obs_alarm_gated_steady_combinational_w`: 1.054757e-05
- `obs_alarm_gated_steady_total_a`: 4.991442e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.519513e-04
- `obs_backpressure_reset_internal_w`: 1.148410e-04
- `obs_backpressure_reset_switching_w`: 3.690286e-05
- `obs_backpressure_reset_leakage_w`: 2.075095e-07
- `obs_backpressure_reset_clock_w`: 5.296115e-05
- `obs_backpressure_reset_sequential_w`: 9.490189e-05
- `obs_backpressure_reset_combinational_w`: 4.088211e-06
- `obs_backpressure_reset_total_a`: 4.604585e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.712147e-04
- `obs_backpressure_startup_internal_w`: 1.260745e-04
- `obs_backpressure_startup_switching_w`: 4.492336e-05
- `obs_backpressure_startup_leakage_w`: 2.168396e-07
- `obs_backpressure_startup_clock_w`: 5.296115e-05
- `obs_backpressure_startup_sequential_w`: 1.034777e-04
- `obs_backpressure_startup_combinational_w`: 1.477594e-05
- `obs_backpressure_startup_total_a`: 5.188324e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.842789e-04
- `obs_backpressure_steady_internal_w`: 1.339396e-04
- `obs_backpressure_steady_switching_w`: 5.011802e-05
- `obs_backpressure_steady_leakage_w`: 2.213108e-07
- `obs_backpressure_steady_clock_w`: 5.296115e-05
- `obs_backpressure_steady_sequential_w`: 1.100793e-04
- `obs_backpressure_steady_combinational_w`: 2.123854e-05
- `obs_backpressure_steady_total_a`: 5.584209e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.520663e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.148789e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.697981e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.075095e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.296115e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.491049e-05
- `obs_conditioned_streaming_reset_combinational_w`: 4.194548e-06
- `obs_conditioned_streaming_reset_total_a`: 4.608070e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.716499e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.262809e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.515290e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.161481e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.296115e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.036655e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.502323e-05
- `obs_conditioned_streaming_startup_total_a`: 5.201512e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.845163e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.340358e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.026041e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.201589e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.296115e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.100572e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.149812e-05
- `obs_conditioned_streaming_steady_total_a`: 5.591403e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.511657e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.145313e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.642693e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.075095e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.296115e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.486907e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.335389e-06
- `obs_disabled_clock_running_reset_total_a`: 4.580779e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.551754e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.173151e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.764881e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.114828e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.296115e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.637889e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.835313e-06
- `obs_disabled_clock_running_startup_total_a`: 4.702285e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.549884e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.171918e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.758506e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.114832e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.296115e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.642557e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.601630e-06
- `obs_disabled_clock_running_steady_total_a`: 4.696618e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.523752e-04
- `obs_raw_streaming_reset_internal_w`: 1.149510e-04
- `obs_raw_streaming_reset_switching_w`: 3.721676e-05
- `obs_raw_streaming_reset_leakage_w`: 2.075095e-07
- `obs_raw_streaming_reset_clock_w`: 5.296115e-05
- `obs_raw_streaming_reset_sequential_w`: 9.491016e-05
- `obs_raw_streaming_reset_combinational_w`: 4.503830e-06
- `obs_raw_streaming_reset_total_a`: 4.617430e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.725237e-04
- `obs_raw_streaming_startup_internal_w`: 1.266315e-04
- `obs_raw_streaming_startup_switching_w`: 4.567590e-05
- `obs_raw_streaming_startup_leakage_w`: 2.163030e-07
- `obs_raw_streaming_startup_clock_w`: 5.296115e-05
- `obs_raw_streaming_startup_sequential_w`: 1.036655e-04
- `obs_raw_streaming_startup_combinational_w`: 1.589703e-05
- `obs_raw_streaming_startup_total_a`: 5.227991e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.854906e-04
- `obs_raw_streaming_steady_internal_w`: 1.344357e-04
- `obs_raw_streaming_steady_switching_w`: 5.083391e-05
- `obs_raw_streaming_steady_leakage_w`: 2.210452e-07
- `obs_raw_streaming_steady_clock_w`: 5.296115e-05
- `obs_raw_streaming_steady_sequential_w`: 1.100825e-04
- `obs_raw_streaming_steady_combinational_w`: 2.244711e-05
- `obs_raw_streaming_steady_total_a`: 5.620927e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
