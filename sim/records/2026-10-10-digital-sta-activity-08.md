---
record: 2026-10-10-digital-sta-activity-08
date: 2026-10-10T02:45:43Z
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
repo_commit: d01212256aee65c9be3593221aded02dded2644f

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
  spef_sha256: 411d0b34e7250b996768edb3578b26c1dfe660f8eee3e5f9fa30a714505e491e
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-08/
  files:
    - uniform.tcl  sha256:8e4ed6ce0fd433f643ae2bc3d5d6af3e58e71d1311906d44cc26712e8f42ffc0
    - uniform.log  sha256:0543ac5f0f535004dae84433b3aa588da8578743ccf52a15da60049f7a9d99d1
    - observed.tcl  sha256:da9fd7cf17bc57bada321c889d1dccabed0952caa6ee4142e6fd267d58702707
    - observed.log  sha256:3ec69069fd1193ae9b68bc5b68e6ef04a2344f7ff0a7b644d9961a14ada4a84a
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 9.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    176.72 |     81.46 |      0.22 |    258.40 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    114.90 |     37.01 |      0.21 |    152.11 | 0.589 | 5371 / 0 |
| alarm-gated | startup | 1040 |    125.88 |     44.79 |      0.22 |    170.89 | 0.661 | 5371 / 0 |
| alarm-gated | steady | 1024 |    122.50 |     42.01 |      0.22 |    164.72 | 0.637 | 5371 / 0 |
| backpressure | reset | 8 |    114.85 |     36.90 |      0.21 |    151.96 | 0.588 | 5371 / 0 |
| backpressure | startup | 1040 |    126.08 |     44.92 |      0.22 |    171.22 | 0.663 | 5371 / 0 |
| backpressure | steady | 1024 |    133.95 |     50.12 |      0.22 |    184.28 | 0.713 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    114.88 |     36.98 |      0.21 |    152.07 | 0.589 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    126.29 |     45.15 |      0.22 |    171.66 | 0.664 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    134.04 |     50.26 |      0.22 |    184.52 | 0.714 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    114.54 |     36.43 |      0.21 |    151.17 | 0.585 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    117.32 |     37.65 |      0.21 |    155.18 | 0.601 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    117.20 |     37.59 |      0.21 |    154.99 | 0.600 | 5371 / 0 |
| raw-streaming | reset | 8 |    114.96 |     37.22 |      0.21 |    152.38 | 0.590 | 5371 / 0 |
| raw-streaming | startup | 1040 |    126.64 |     45.68 |      0.22 |    172.53 | 0.668 | 5371 / 0 |
| raw-streaming | steady | 1024 |    134.44 |     50.83 |      0.22 |    185.50 | 0.718 | 5371 / 0 |

- `uniform_total_w`: 2.584001e-04
- `uniform_internal_w`: 1.767190e-04
- `uniform_switching_w`: 8.146177e-05
- `uniform_leakage_w`: 2.193580e-07
- `uniform_clock_w`: 5.296433e-05
- `uniform_sequential_w`: 1.354686e-04
- `uniform_combinational_w`: 6.996717e-05
- `uniform_total_a`: 7.830306e-05
- `obs_alarm_gated_reset_total_w`: 1.521097e-04
- `obs_alarm_gated_reset_internal_w`: 1.148960e-04
- `obs_alarm_gated_reset_switching_w`: 3.700610e-05
- `obs_alarm_gated_reset_leakage_w`: 2.075095e-07
- `obs_alarm_gated_reset_clock_w`: 5.296433e-05
- `obs_alarm_gated_reset_sequential_w`: 9.491140e-05
- `obs_alarm_gated_reset_combinational_w`: 4.233843e-06
- `obs_alarm_gated_reset_total_a`: 4.609385e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.708857e-04
- `obs_alarm_gated_startup_internal_w`: 1.258834e-04
- `obs_alarm_gated_startup_switching_w`: 4.478579e-05
- `obs_alarm_gated_startup_leakage_w`: 2.165480e-07
- `obs_alarm_gated_startup_clock_w`: 5.296433e-05
- `obs_alarm_gated_startup_sequential_w`: 1.034430e-04
- `obs_alarm_gated_startup_combinational_w`: 1.447854e-05
- `obs_alarm_gated_startup_total_a`: 5.178355e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.647229e-04
- `obs_alarm_gated_steady_internal_w`: 1.225011e-04
- `obs_alarm_gated_steady_switching_w`: 4.200592e-05
- `obs_alarm_gated_steady_leakage_w`: 2.159064e-07
- `obs_alarm_gated_steady_clock_w`: 5.296433e-05
- `obs_alarm_gated_steady_sequential_w`: 1.012091e-04
- `obs_alarm_gated_steady_combinational_w`: 1.054950e-05
- `obs_alarm_gated_steady_total_a`: 4.991603e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.519569e-04
- `obs_backpressure_reset_internal_w`: 1.148465e-04
- `obs_backpressure_reset_switching_w`: 3.690286e-05
- `obs_backpressure_reset_leakage_w`: 2.075095e-07
- `obs_backpressure_reset_clock_w`: 5.296433e-05
- `obs_backpressure_reset_sequential_w`: 9.490274e-05
- `obs_backpressure_reset_combinational_w`: 4.089744e-06
- `obs_backpressure_reset_total_a`: 4.604755e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.712206e-04
- `obs_backpressure_startup_internal_w`: 1.260804e-04
- `obs_backpressure_startup_switching_w`: 4.492336e-05
- `obs_backpressure_startup_leakage_w`: 2.168396e-07
- `obs_backpressure_startup_clock_w`: 5.296433e-05
- `obs_backpressure_startup_sequential_w`: 1.034781e-04
- `obs_backpressure_startup_combinational_w`: 1.477820e-05
- `obs_backpressure_startup_total_a`: 5.188503e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.842847e-04
- `obs_backpressure_steady_internal_w`: 1.339454e-04
- `obs_backpressure_steady_switching_w`: 5.011802e-05
- `obs_backpressure_steady_leakage_w`: 2.213108e-07
- `obs_backpressure_steady_clock_w`: 5.296433e-05
- `obs_backpressure_steady_sequential_w`: 1.100797e-04
- `obs_backpressure_steady_combinational_w`: 2.124078e-05
- `obs_backpressure_steady_total_a`: 5.584385e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.520720e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.148846e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.697981e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.075095e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.296433e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.491139e-05
- `obs_conditioned_streaming_reset_combinational_w`: 4.196150e-06
- `obs_conditioned_streaming_reset_total_a`: 4.608242e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.716559e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.262869e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.515290e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.161481e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.296433e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.036660e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.502562e-05
- `obs_conditioned_streaming_startup_total_a`: 5.201694e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.845223e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.340417e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.026041e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.201589e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.296433e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.100576e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.150043e-05
- `obs_conditioned_streaming_steady_total_a`: 5.591585e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.511707e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.145363e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.642693e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.075095e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.296433e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.486991e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.336373e-06
- `obs_disabled_clock_running_reset_total_a`: 4.580930e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.551796e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.173193e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.764881e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.114828e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.296433e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.637935e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.835945e-06
- `obs_disabled_clock_running_startup_total_a`: 4.702412e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.549926e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.171960e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.758506e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.114832e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.296433e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.642599e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.602221e-06
- `obs_disabled_clock_running_steady_total_a`: 4.696745e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.523809e-04
- `obs_raw_streaming_reset_internal_w`: 1.149566e-04
- `obs_raw_streaming_reset_switching_w`: 3.721676e-05
- `obs_raw_streaming_reset_leakage_w`: 2.075095e-07
- `obs_raw_streaming_reset_clock_w`: 5.296433e-05
- `obs_raw_streaming_reset_sequential_w`: 9.491106e-05
- `obs_raw_streaming_reset_combinational_w`: 4.505388e-06
- `obs_raw_streaming_reset_total_a`: 4.617603e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.725295e-04
- `obs_raw_streaming_startup_internal_w`: 1.266373e-04
- `obs_raw_streaming_startup_switching_w`: 4.567590e-05
- `obs_raw_streaming_startup_leakage_w`: 2.163030e-07
- `obs_raw_streaming_startup_clock_w`: 5.296433e-05
- `obs_raw_streaming_startup_sequential_w`: 1.036660e-04
- `obs_raw_streaming_startup_combinational_w`: 1.589924e-05
- `obs_raw_streaming_startup_total_a`: 5.228167e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.854964e-04
- `obs_raw_streaming_steady_internal_w`: 1.344415e-04
- `obs_raw_streaming_steady_switching_w`: 5.083391e-05
- `obs_raw_streaming_steady_leakage_w`: 2.210452e-07
- `obs_raw_streaming_steady_clock_w`: 5.296433e-05
- `obs_raw_streaming_steady_sequential_w`: 1.100829e-04
- `obs_raw_streaming_steady_combinational_w`: 2.244931e-05
- `obs_raw_streaming_steady_total_a`: 5.621103e-05
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
