---
record: 2026-10-10-digital-sta-activity-15
date: 2026-10-10T02:46:50Z
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
  spef_sha256: 252c23956aecc851199a41b104b36d74f22a370462921d354119d339bf208538
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-15/
  files:
    - uniform.tcl  sha256:59884b440ad6c73493fcb62624a44fcce0ee71a38c92c73b0092b8dd7685fc19
    - uniform.log  sha256:100026187cc41c4dc2c5a9f9c4553a3b4280e2efa675b0b7264692abbd8d8310
    - observed.tcl  sha256:d9746432c409cb974c6c5e1a00fdbc54648f65f6fa6e2443ebdf163fbaf96bde
    - observed.log  sha256:d3d29bcf9aa8ff8c789bd305141cce78ec1f145eb4cf8463dccd29a7683768fe
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 8.5s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    217.55 |    101.09 |      0.26 |    318.90 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    140.86 |     45.84 |      0.25 |    186.95 | 0.586 | 5371 / 0 |
| alarm-gated | startup | 1040 |    154.41 |     55.42 |      0.25 |    210.09 | 0.659 | 5371 / 0 |
| alarm-gated | steady | 1024 |    150.21 |     52.00 |      0.25 |    202.47 | 0.635 | 5371 / 0 |
| backpressure | reset | 8 |    140.80 |     45.72 |      0.25 |    186.76 | 0.586 | 5371 / 0 |
| backpressure | startup | 1040 |    154.65 |     55.59 |      0.25 |    210.50 | 0.660 | 5371 / 0 |
| backpressure | steady | 1024 |    164.39 |     62.03 |      0.26 |    226.68 | 0.711 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    140.85 |     45.81 |      0.25 |    186.90 | 0.586 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    154.91 |     55.88 |      0.25 |    211.04 | 0.662 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    164.51 |     62.21 |      0.26 |    226.98 | 0.712 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    140.41 |     45.12 |      0.25 |    185.77 | 0.583 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    143.86 |     46.60 |      0.25 |    190.70 | 0.598 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    143.71 |     46.52 |      0.25 |    190.47 | 0.597 | 5371 / 0 |
| raw-streaming | reset | 8 |    140.94 |     46.11 |      0.25 |    187.29 | 0.587 | 5371 / 0 |
| raw-streaming | startup | 1040 |    155.36 |     56.54 |      0.25 |    212.15 | 0.665 | 5371 / 0 |
| raw-streaming | steady | 1024 |    165.02 |     62.93 |      0.26 |    228.20 | 0.716 | 5371 / 0 |

- `uniform_total_w`: 3.188974e-04
- `uniform_internal_w`: 2.175502e-04
- `uniform_switching_w`: 1.010905e-04
- `uniform_leakage_w`: 2.566557e-07
- `uniform_clock_w`: 6.725305e-05
- `uniform_sequential_w`: 1.640748e-04
- `uniform_combinational_w`: 8.756951e-05
- `uniform_total_a`: 8.858261e-05
- `obs_alarm_gated_reset_total_w`: 1.869488e-04
- `obs_alarm_gated_reset_internal_w`: 1.408602e-04
- `obs_alarm_gated_reset_switching_w`: 4.584357e-05
- `obs_alarm_gated_reset_leakage_w`: 2.450344e-07
- `obs_alarm_gated_reset_clock_w`: 6.725305e-05
- `obs_alarm_gated_reset_sequential_w`: 1.144540e-04
- `obs_alarm_gated_reset_combinational_w`: 5.241922e-06
- `obs_alarm_gated_reset_total_a`: 5.193022e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.100880e-04
- `obs_alarm_gated_startup_internal_w`: 1.544119e-04
- `obs_alarm_gated_startup_switching_w`: 5.542263e-05
- `obs_alarm_gated_startup_leakage_w`: 2.534709e-07
- `obs_alarm_gated_startup_clock_w`: 6.725305e-05
- `obs_alarm_gated_startup_sequential_w`: 1.248985e-04
- `obs_alarm_gated_startup_combinational_w`: 1.793656e-05
- `obs_alarm_gated_startup_total_a`: 5.835778e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.024669e-04
- `obs_alarm_gated_steady_internal_w`: 1.502102e-04
- `obs_alarm_gated_steady_switching_w`: 5.200391e-05
- `obs_alarm_gated_steady_leakage_w`: 2.527087e-07
- `obs_alarm_gated_steady_clock_w`: 6.725305e-05
- `obs_alarm_gated_steady_sequential_w`: 1.221647e-04
- `obs_alarm_gated_steady_combinational_w`: 1.304914e-05
- `obs_alarm_gated_steady_total_a`: 5.624081e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.867614e-04
- `obs_backpressure_reset_internal_w`: 1.408010e-04
- `obs_backpressure_reset_switching_w`: 4.571538e-05
- `obs_backpressure_reset_leakage_w`: 2.450344e-07
- `obs_backpressure_reset_clock_w`: 6.725305e-05
- `obs_backpressure_reset_sequential_w`: 1.144438e-04
- `obs_backpressure_reset_combinational_w`: 5.064679e-06
- `obs_backpressure_reset_total_a`: 5.187817e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.104986e-04
- `obs_backpressure_startup_internal_w`: 1.546527e-04
- `obs_backpressure_startup_switching_w`: 5.559208e-05
- `obs_backpressure_startup_leakage_w`: 2.537612e-07
- `obs_backpressure_startup_clock_w`: 6.725305e-05
- `obs_backpressure_startup_sequential_w`: 1.249392e-04
- `obs_backpressure_startup_combinational_w`: 1.830645e-05
- `obs_backpressure_startup_total_a`: 5.847183e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.266774e-04
- `obs_backpressure_steady_internal_w`: 1.643889e-04
- `obs_backpressure_steady_switching_w`: 6.203020e-05
- `obs_backpressure_steady_leakage_w`: 2.582963e-07
- `obs_backpressure_steady_clock_w`: 6.725305e-05
- `obs_backpressure_steady_sequential_w`: 1.330663e-04
- `obs_backpressure_steady_combinational_w`: 2.635810e-05
- `obs_backpressure_steady_total_a`: 6.296594e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.869032e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.408465e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.581167e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.450344e-07
- `obs_conditioned_streaming_reset_clock_w`: 6.725305e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.144540e-04
- `obs_conditioned_streaming_reset_combinational_w`: 5.196312e-06
- `obs_conditioned_streaming_reset_total_a`: 5.191756e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.110426e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.549130e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.587654e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.531000e-07
- `obs_conditioned_streaming_startup_clock_w`: 6.725305e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.251742e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.861572e-05
- `obs_conditioned_streaming_startup_total_a`: 5.862294e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.269780e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.645139e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.220702e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.571063e-07
- `obs_conditioned_streaming_steady_clock_w`: 6.725305e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.330434e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.668166e-05
- `obs_conditioned_streaming_steady_total_a`: 6.304944e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.857745e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.404072e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.512220e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.450344e-07
- `obs_disabled_clock_running_reset_clock_w`: 6.725305e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.144041e-04
- `obs_disabled_clock_running_reset_combinational_w`: 4.117539e-06
- `obs_disabled_clock_running_reset_total_a`: 5.160403e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.907026e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.438582e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.659637e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.480637e-07
- `obs_disabled_clock_running_startup_clock_w`: 6.725305e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.162424e-04
- `obs_disabled_clock_running_startup_combinational_w`: 7.207273e-06
- `obs_disabled_clock_running_startup_total_a`: 5.297294e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.904727e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.437079e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.651666e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.480635e-07
- `obs_disabled_clock_running_steady_clock_w`: 6.725305e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.162993e-04
- `obs_disabled_clock_running_steady_combinational_w`: 6.920351e-06
- `obs_disabled_clock_running_steady_total_a`: 5.290908e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.872894e-04
- `obs_raw_streaming_reset_internal_w`: 1.409393e-04
- `obs_raw_streaming_reset_switching_w`: 4.610507e-05
- `obs_raw_streaming_reset_leakage_w`: 2.450344e-07
- `obs_raw_streaming_reset_clock_w`: 6.725305e-05
- `obs_raw_streaming_reset_sequential_w`: 1.144534e-04
- `obs_raw_streaming_reset_combinational_w`: 5.583086e-06
- `obs_raw_streaming_reset_total_a`: 5.202483e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.121519e-04
- `obs_raw_streaming_startup_internal_w`: 1.553593e-04
- `obs_raw_streaming_startup_switching_w`: 5.653943e-05
- `obs_raw_streaming_startup_leakage_w`: 2.531801e-07
- `obs_raw_streaming_startup_clock_w`: 6.725305e-05
- `obs_raw_streaming_startup_sequential_w`: 1.251702e-04
- `obs_raw_streaming_startup_combinational_w`: 1.972878e-05
- `obs_raw_streaming_startup_total_a`: 5.893108e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.282042e-04
- `obs_raw_streaming_steady_internal_w`: 1.650156e-04
- `obs_raw_streaming_steady_switching_w`: 6.293054e-05
- `obs_raw_streaming_steady_leakage_w`: 2.580173e-07
- `obs_raw_streaming_steady_clock_w`: 6.725305e-05
- `obs_raw_streaming_steady_sequential_w`: 1.330709e-04
- `obs_raw_streaming_steady_combinational_w`: 2.788027e-05
- `obs_raw_streaming_steady_total_a`: 6.339006e-05
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
