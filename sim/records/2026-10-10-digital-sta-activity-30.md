---
record: 2026-10-10-digital-sta-activity-30
date: 2026-10-10T07:13:26Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ff_n40C_3v60.lib (liberty corner ff_n40C_3v60, sha256:ff10b2374d88c8614ccc9dc8c4b836a1e8eb54fe6cdfe6883ffd9b1be02487a4)
  - gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:332ae93d61ac55f793da97a6391703f78bc415653cb60e76dd8eb0092124485a)
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
  spef_sha256: 026a417396ffa86e819e7411abf010cf7884a6f9b5d78ebc67357b008e50550e
  spef_bytes: 1775752
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-30/
  files:
    - uniform.tcl  sha256:53658a021e1e3dc101e2b4806f717774a0c1ba63477d0545e05832d6dd51dcb1
    - uniform.log  sha256:8ca168e70c3a4e3422a7641a9ef3f6183f6bac9779c6ddcb316cffb51454999d
    - observed.tcl  sha256:6757b180bfcf22931e0f4c5cfedd24bf0446195f8664dfccc55fed50c83d542a
    - observed.log  sha256:e06c27595e4ef3ae03a339dd3e5c7f6bae934af6151183a720ceb4dd2398898d
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 7.9s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    217.54 |    101.09 |      0.26 |    318.89 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    140.86 |     45.84 |      0.25 |    186.94 | 0.586 | 5371 / 0 |
| alarm-gated | startup | 1040 |    154.41 |     55.42 |      0.25 |    210.08 | 0.659 | 5371 / 0 |
| alarm-gated | steady | 1024 |    150.21 |     52.00 |      0.25 |    202.46 | 0.635 | 5371 / 0 |
| backpressure | reset | 8 |    140.80 |     45.72 |      0.25 |    186.76 | 0.586 | 5371 / 0 |
| backpressure | startup | 1040 |    154.65 |     55.59 |      0.25 |    210.49 | 0.660 | 5371 / 0 |
| backpressure | steady | 1024 |    164.38 |     62.03 |      0.26 |    226.67 | 0.711 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    140.84 |     45.81 |      0.25 |    186.90 | 0.586 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    154.91 |     55.88 |      0.25 |    211.04 | 0.662 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    164.51 |     62.21 |      0.26 |    226.97 | 0.712 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    140.40 |     45.12 |      0.25 |    185.77 | 0.583 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    143.85 |     46.60 |      0.25 |    190.70 | 0.598 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    143.70 |     46.52 |      0.25 |    190.47 | 0.597 | 5371 / 0 |
| raw-streaming | reset | 8 |    140.93 |     46.11 |      0.25 |    187.28 | 0.587 | 5371 / 0 |
| raw-streaming | startup | 1040 |    155.35 |     56.54 |      0.25 |    212.15 | 0.665 | 5371 / 0 |
| raw-streaming | steady | 1024 |    165.01 |     62.93 |      0.26 |    228.20 | 0.716 | 5371 / 0 |

- `uniform_total_w`: 3.188911e-04
- `uniform_internal_w`: 2.175439e-04
- `uniform_switching_w`: 1.010905e-04
- `uniform_leakage_w`: 2.566557e-07
- `uniform_clock_w`: 6.724941e-05
- `uniform_sequential_w`: 1.640729e-04
- `uniform_combinational_w`: 8.756875e-05
- `uniform_total_a`: 8.858086e-05
- `obs_alarm_gated_reset_total_w`: 1.869441e-04
- `obs_alarm_gated_reset_internal_w`: 1.408555e-04
- `obs_alarm_gated_reset_switching_w`: 4.584357e-05
- `obs_alarm_gated_reset_leakage_w`: 2.450344e-07
- `obs_alarm_gated_reset_clock_w`: 6.724941e-05
- `obs_alarm_gated_reset_sequential_w`: 1.144530e-04
- `obs_alarm_gated_reset_combinational_w`: 5.241742e-06
- `obs_alarm_gated_reset_total_a`: 5.192892e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.100830e-04
- `obs_alarm_gated_startup_internal_w`: 1.544069e-04
- `obs_alarm_gated_startup_switching_w`: 5.542263e-05
- `obs_alarm_gated_startup_leakage_w`: 2.534709e-07
- `obs_alarm_gated_startup_clock_w`: 6.724941e-05
- `obs_alarm_gated_startup_sequential_w`: 1.248984e-04
- `obs_alarm_gated_startup_combinational_w`: 1.793537e-05
- `obs_alarm_gated_startup_total_a`: 5.835639e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.024624e-04
- `obs_alarm_gated_steady_internal_w`: 1.502057e-04
- `obs_alarm_gated_steady_switching_w`: 5.200391e-05
- `obs_alarm_gated_steady_leakage_w`: 2.527087e-07
- `obs_alarm_gated_steady_clock_w`: 6.724941e-05
- `obs_alarm_gated_steady_sequential_w`: 1.221646e-04
- `obs_alarm_gated_steady_combinational_w`: 1.304835e-05
- `obs_alarm_gated_steady_total_a`: 5.623956e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.867569e-04
- `obs_backpressure_reset_internal_w`: 1.407964e-04
- `obs_backpressure_reset_switching_w`: 4.571538e-05
- `obs_backpressure_reset_leakage_w`: 2.450344e-07
- `obs_backpressure_reset_clock_w`: 6.724941e-05
- `obs_backpressure_reset_sequential_w`: 1.144429e-04
- `obs_backpressure_reset_combinational_w`: 5.064654e-06
- `obs_backpressure_reset_total_a`: 5.187692e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.104936e-04
- `obs_backpressure_startup_internal_w`: 1.546477e-04
- `obs_backpressure_startup_switching_w`: 5.559208e-05
- `obs_backpressure_startup_leakage_w`: 2.537612e-07
- `obs_backpressure_startup_clock_w`: 6.724941e-05
- `obs_backpressure_startup_sequential_w`: 1.249390e-04
- `obs_backpressure_startup_combinational_w`: 1.830522e-05
- `obs_backpressure_startup_total_a`: 5.847044e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.266724e-04
- `obs_backpressure_steady_internal_w`: 1.643839e-04
- `obs_backpressure_steady_switching_w`: 6.203020e-05
- `obs_backpressure_steady_leakage_w`: 2.582963e-07
- `obs_backpressure_steady_clock_w`: 6.724941e-05
- `obs_backpressure_steady_sequential_w`: 1.330661e-04
- `obs_backpressure_steady_combinational_w`: 2.635691e-05
- `obs_backpressure_steady_total_a`: 6.296456e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.868986e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.408418e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.581167e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.450344e-07
- `obs_conditioned_streaming_reset_clock_w`: 6.724941e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.144530e-04
- `obs_conditioned_streaming_reset_combinational_w`: 5.196182e-06
- `obs_conditioned_streaming_reset_total_a`: 5.191628e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.110376e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.549080e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.587654e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.531000e-07
- `obs_conditioned_streaming_startup_clock_w`: 6.724941e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.251740e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.861452e-05
- `obs_conditioned_streaming_startup_total_a`: 5.862156e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.269730e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.645089e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.220702e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.571063e-07
- `obs_conditioned_streaming_steady_clock_w`: 6.724941e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.330433e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.668049e-05
- `obs_conditioned_streaming_steady_total_a`: 6.304806e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.857696e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.404023e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.512220e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.450344e-07
- `obs_disabled_clock_running_reset_clock_w`: 6.724941e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.144031e-04
- `obs_disabled_clock_running_reset_combinational_w`: 4.117177e-06
- `obs_disabled_clock_running_reset_total_a`: 5.160267e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.906979e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.438535e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.659637e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.480637e-07
- `obs_disabled_clock_running_startup_clock_w`: 6.724941e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.162422e-04
- `obs_disabled_clock_running_startup_combinational_w`: 7.206367e-06
- `obs_disabled_clock_running_startup_total_a`: 5.297164e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.904680e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.437033e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.651666e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.480635e-07
- `obs_disabled_clock_running_steady_clock_w`: 6.724941e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.162991e-04
- `obs_disabled_clock_running_steady_combinational_w`: 6.919497e-06
- `obs_disabled_clock_running_steady_total_a`: 5.290778e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.872847e-04
- `obs_raw_streaming_reset_internal_w`: 1.409346e-04
- `obs_raw_streaming_reset_switching_w`: 4.610507e-05
- `obs_raw_streaming_reset_leakage_w`: 2.450344e-07
- `obs_raw_streaming_reset_clock_w`: 6.724941e-05
- `obs_raw_streaming_reset_sequential_w`: 1.144524e-04
- `obs_raw_streaming_reset_combinational_w`: 5.582945e-06
- `obs_raw_streaming_reset_total_a`: 5.202353e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.121470e-04
- `obs_raw_streaming_startup_internal_w`: 1.553544e-04
- `obs_raw_streaming_startup_switching_w`: 5.653943e-05
- `obs_raw_streaming_startup_leakage_w`: 2.531801e-07
- `obs_raw_streaming_startup_clock_w`: 6.724941e-05
- `obs_raw_streaming_startup_sequential_w`: 1.251700e-04
- `obs_raw_streaming_startup_combinational_w`: 1.972761e-05
- `obs_raw_streaming_startup_total_a`: 5.892972e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.281992e-04
- `obs_raw_streaming_steady_internal_w`: 1.650107e-04
- `obs_raw_streaming_steady_switching_w`: 6.293054e-05
- `obs_raw_streaming_steady_leakage_w`: 2.580173e-07
- `obs_raw_streaming_steady_clock_w`: 6.724941e-05
- `obs_raw_streaming_steady_sequential_w`: 1.330707e-04
- `obs_raw_streaming_steady_combinational_w`: 2.787909e-05
- `obs_raw_streaming_steady_total_a`: 6.338867e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
