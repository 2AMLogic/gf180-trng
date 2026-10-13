---
record: 2026-10-10-digital-sta-activity-10
date: 2026-10-10T02:46:03Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60.lib (liberty corner ff_125C_3v60, sha256:b64f32b397097f2046e66ce7f9a4aaffc9a80c4c0bfd3c77385727268e81a016)
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
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60
  interconnect: min (OpenRCX rule deck)
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
  spef_sha256: 75f65b9b53fcc17aa1fc9d1123074a3cede07f69a890d170fd005e7cea468ee5
  spef_bytes: 1766985
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-10/
  files:
    - uniform.tcl  sha256:0bc4f6bf6b25a62f77845980dfd026af64f150c1c499b17d74227b295dc25d12
    - uniform.log  sha256:985554edbd5aa57f4233143557c825853c54786e5433883c949c3b8f2e30dee9
    - observed.tcl  sha256:bd6751778e53c0244bd4953975ad0a71729b6ab3a346ee8433220334b1de244f
    - observed.log  sha256:30dc07ecf2d0356d1035903701dd708a731559d8999b4aa40a02eca679538a41
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 11.3s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    236.70 |     94.07 |      7.84 |    338.61 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    150.92 |     42.90 |      7.27 |    201.09 | 0.594 | 5371 / 0 |
| alarm-gated | startup | 1040 |    166.21 |     51.93 |      7.86 |    226.01 | 0.667 | 5371 / 0 |
| alarm-gated | steady | 1024 |    161.46 |     48.70 |      7.84 |    218.01 | 0.644 | 5371 / 0 |
| backpressure | reset | 8 |    150.85 |     42.78 |      7.27 |    200.91 | 0.593 | 5371 / 0 |
| backpressure | startup | 1040 |    166.49 |     52.09 |      7.86 |    226.44 | 0.669 | 5371 / 0 |
| backpressure | steady | 1024 |    177.43 |     58.09 |      8.19 |    243.71 | 0.720 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    150.90 |     42.87 |      7.27 |    201.05 | 0.594 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    166.78 |     52.36 |      7.86 |    227.00 | 0.670 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    177.57 |     58.25 |      8.10 |    243.92 | 0.720 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    150.41 |     42.23 |      7.27 |    199.92 | 0.590 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    154.39 |     43.68 |      7.66 |    205.73 | 0.608 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    154.22 |     43.60 |      7.66 |    205.48 | 0.607 | 5371 / 0 |
| raw-streaming | reset | 8 |    151.01 |     43.14 |      7.27 |    201.43 | 0.595 | 5371 / 0 |
| raw-streaming | startup | 1040 |    167.28 |     52.95 |      7.81 |    228.04 | 0.673 | 5371 / 0 |
| raw-streaming | steady | 1024 |    178.13 |     58.90 |      8.12 |    245.15 | 0.724 | 5371 / 0 |

- `uniform_total_w`: 3.386103e-04
- `uniform_internal_w`: 2.367032e-04
- `uniform_switching_w`: 9.406505e-05
- `uniform_leakage_w`: 7.842120e-06
- `uniform_clock_w`: 6.993619e-05
- `uniform_sequential_w`: 1.757418e-04
- `uniform_combinational_w`: 9.293233e-05
- `uniform_total_a`: 9.405842e-05
- `obs_alarm_gated_reset_total_w`: 2.010929e-04
- `obs_alarm_gated_reset_internal_w`: 1.509191e-04
- `obs_alarm_gated_reset_switching_w`: 4.290115e-05
- `obs_alarm_gated_reset_leakage_w`: 7.272558e-06
- `obs_alarm_gated_reset_clock_w`: 6.993619e-05
- `obs_alarm_gated_reset_sequential_w`: 1.229540e-04
- `obs_alarm_gated_reset_combinational_w`: 8.202582e-06
- `obs_alarm_gated_reset_total_a`: 5.585914e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.260101e-04
- `obs_alarm_gated_startup_internal_w`: 1.662149e-04
- `obs_alarm_gated_startup_switching_w`: 5.193230e-05
- `obs_alarm_gated_startup_leakage_w`: 7.862931e-06
- `obs_alarm_gated_startup_clock_w`: 6.993619e-05
- `obs_alarm_gated_startup_sequential_w`: 1.342089e-04
- `obs_alarm_gated_startup_combinational_w`: 2.186515e-05
- `obs_alarm_gated_startup_total_a`: 6.278058e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.180054e-04
- `obs_alarm_gated_steady_internal_w`: 1.614632e-04
- `obs_alarm_gated_steady_switching_w`: 4.870021e-05
- `obs_alarm_gated_steady_leakage_w`: 7.842063e-06
- `obs_alarm_gated_steady_clock_w`: 6.993619e-05
- `obs_alarm_gated_steady_sequential_w`: 1.313685e-04
- `obs_alarm_gated_steady_combinational_w`: 1.670065e-05
- `obs_alarm_gated_steady_total_a`: 6.055706e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.009091e-04
- `obs_backpressure_reset_internal_w`: 1.508544e-04
- `obs_backpressure_reset_switching_w`: 4.278214e-05
- `obs_backpressure_reset_leakage_w`: 7.272558e-06
- `obs_backpressure_reset_clock_w`: 6.993619e-05
- `obs_backpressure_reset_sequential_w`: 1.229430e-04
- `obs_backpressure_reset_combinational_w`: 8.029781e-06
- `obs_backpressure_reset_total_a`: 5.580808e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.264375e-04
- `obs_backpressure_startup_internal_w`: 1.664883e-04
- `obs_backpressure_startup_switching_w`: 5.209149e-05
- `obs_backpressure_startup_leakage_w`: 7.857784e-06
- `obs_backpressure_startup_clock_w`: 6.993619e-05
- `obs_backpressure_startup_sequential_w`: 1.342622e-04
- `obs_backpressure_startup_combinational_w`: 2.223921e-05
- `obs_backpressure_startup_total_a`: 6.289931e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.437051e-04
- `obs_backpressure_steady_internal_w`: 1.774262e-04
- `obs_backpressure_steady_switching_w`: 5.808740e-05
- `obs_backpressure_steady_leakage_w`: 8.191520e-06
- `obs_backpressure_steady_clock_w`: 6.993619e-05
- `obs_backpressure_steady_sequential_w`: 1.429613e-04
- `obs_backpressure_steady_combinational_w`: 3.080755e-05
- `obs_backpressure_steady_total_a`: 6.769586e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.010471e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.509044e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.287012e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.272558e-06
- `obs_conditioned_streaming_reset_clock_w`: 6.993619e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.229540e-04
- `obs_conditioned_streaming_reset_combinational_w`: 8.156823e-06
- `obs_conditioned_streaming_reset_total_a`: 5.584642e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.269977e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.667814e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.235608e-05
- `obs_conditioned_streaming_startup_leakage_w`: 7.860215e-06
- `obs_conditioned_streaming_startup_clock_w`: 6.993619e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.344902e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.257135e-05
- `obs_conditioned_streaming_startup_total_a`: 6.305492e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.439198e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.775712e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.825082e-05
- `obs_conditioned_streaming_steady_leakage_w`: 8.097756e-06
- `obs_conditioned_streaming_steady_clock_w`: 6.993619e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.429191e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.106436e-05
- `obs_conditioned_streaming_steady_total_a`: 6.775550e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.999211e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.504142e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.223443e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.272558e-06
- `obs_disabled_clock_running_reset_clock_w`: 6.993619e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.228990e-04
- `obs_disabled_clock_running_reset_combinational_w`: 7.085880e-06
- `obs_disabled_clock_running_reset_total_a`: 5.553364e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.057265e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.543928e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.367802e-05
- `obs_disabled_clock_running_startup_leakage_w`: 7.655682e-06
- `obs_disabled_clock_running_startup_clock_w`: 6.993619e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.251592e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.063111e-05
- `obs_disabled_clock_running_startup_total_a`: 5.714625e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.054819e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.542209e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.360485e-05
- `obs_disabled_clock_running_steady_leakage_w`: 7.656220e-06
- `obs_disabled_clock_running_steady_clock_w`: 6.993619e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.252136e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.033206e-05
- `obs_disabled_clock_running_steady_total_a`: 5.707831e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.014262e-04
- `obs_raw_streaming_reset_internal_w`: 1.510107e-04
- `obs_raw_streaming_reset_switching_w`: 4.314292e-05
- `obs_raw_streaming_reset_leakage_w`: 7.272558e-06
- `obs_raw_streaming_reset_clock_w`: 6.993619e-05
- `obs_raw_streaming_reset_sequential_w`: 1.229529e-04
- `obs_raw_streaming_reset_combinational_w`: 8.537041e-06
- `obs_raw_streaming_reset_total_a`: 5.595172e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.280447e-04
- `obs_raw_streaming_startup_internal_w`: 1.672835e-04
- `obs_raw_streaming_startup_switching_w`: 5.294916e-05
- `obs_raw_streaming_startup_leakage_w`: 7.812067e-06
- `obs_raw_streaming_startup_clock_w`: 6.993619e-05
- `obs_raw_streaming_startup_sequential_w`: 1.344914e-04
- `obs_raw_streaming_startup_combinational_w`: 2.361717e-05
- `obs_raw_streaming_startup_total_a`: 6.334575e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.451531e-04
- `obs_raw_streaming_steady_internal_w`: 1.781340e-04
- `obs_raw_streaming_steady_switching_w`: 5.890318e-05
- `obs_raw_streaming_steady_leakage_w`: 8.116017e-06
- `obs_raw_streaming_steady_clock_w`: 6.993619e-05
- `obs_raw_streaming_steady_sequential_w`: 1.429587e-04
- `obs_raw_streaming_steady_combinational_w`: 3.225825e-05
- `obs_raw_streaming_steady_total_a`: 6.809808e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_125C_3v60 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_125C_3v60, interconnect `min`).
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
