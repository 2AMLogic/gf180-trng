---
record: 2026-10-10-digital-sta-activity-27
date: 2026-10-10T07:13:02Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60.lib (liberty corner ff_125C_3v60, sha256:0354585714f92d093efa6cb0263b7305d8b8cee18ad802eb4e5a8d131241cb9c)
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
  spef_sha256: 8062220519699767853d79c95b1cf9bb8931deeece74595ac7415e014a9561d3
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-27/
  files:
    - uniform.tcl  sha256:8572dee87a517847a4ea2b26b834db7f7eb98e911b22b33888df3e11c57c3f74
    - uniform.log  sha256:78069b21cc27a778c9c626190d34c04e1701f8e8e9f4c20293a7e7cafd452dfe
    - observed.tcl  sha256:03240ca4332c37553ee0dee07bbe5e9029197d1c7b54fc36e609c9001a28d0fb
    - observed.log  sha256:3586c21e7aacaa8126457b1efb89fec1961d7f852f24328377dbe244f69812fb
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 8.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    238.81 |    101.53 |      7.84 |    348.18 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    152.55 |     46.07 |      7.27 |    205.89 | 0.591 | 5371 / 0 |
| alarm-gated | startup | 1040 |    167.91 |     55.69 |      7.86 |    231.47 | 0.665 | 5371 / 0 |
| alarm-gated | steady | 1024 |    163.14 |     52.25 |      7.84 |    223.23 | 0.641 | 5371 / 0 |
| backpressure | reset | 8 |    152.48 |     45.94 |      7.27 |    205.70 | 0.591 | 5371 / 0 |
| backpressure | startup | 1040 |    168.19 |     55.86 |      7.86 |    231.91 | 0.666 | 5371 / 0 |
| backpressure | steady | 1024 |    179.22 |     62.32 |      8.19 |    249.73 | 0.717 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    152.53 |     46.04 |      7.27 |    205.84 | 0.591 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    168.48 |     56.14 |      7.86 |    232.49 | 0.668 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    179.36 |     62.50 |      8.10 |    249.96 | 0.718 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    152.04 |     45.35 |      7.27 |    204.66 | 0.588 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    156.03 |     46.83 |      7.66 |    210.52 | 0.605 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    155.86 |     46.75 |      7.66 |    210.27 | 0.604 | 5371 / 0 |
| raw-streaming | reset | 8 |    152.64 |     46.33 |      7.27 |    206.25 | 0.592 | 5371 / 0 |
| raw-streaming | startup | 1040 |    168.99 |     56.81 |      7.81 |    233.62 | 0.671 | 5371 / 0 |
| raw-streaming | steady | 1024 |    179.93 |     63.22 |      8.12 |    251.27 | 0.722 | 5371 / 0 |

- `uniform_total_w`: 3.481841e-04
- `uniform_internal_w`: 2.388136e-04
- `uniform_switching_w`: 1.015284e-04
- `uniform_leakage_w`: 7.842120e-06
- `uniform_clock_w`: 7.370720e-05
- `uniform_sequential_w`: 1.773865e-04
- `uniform_combinational_w`: 9.709038e-05
- `uniform_total_a`: 9.671781e-05
- `obs_alarm_gated_reset_total_w`: 2.058910e-04
- `obs_alarm_gated_reset_internal_w`: 1.525471e-04
- `obs_alarm_gated_reset_switching_w`: 4.607128e-05
- `obs_alarm_gated_reset_leakage_w`: 7.272558e-06
- `obs_alarm_gated_reset_clock_w`: 7.370720e-05
- `obs_alarm_gated_reset_sequential_w`: 1.237188e-04
- `obs_alarm_gated_reset_combinational_w`: 8.465046e-06
- `obs_alarm_gated_reset_total_a`: 5.719194e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.314670e-04
- `obs_alarm_gated_startup_internal_w`: 1.679148e-04
- `obs_alarm_gated_startup_switching_w`: 5.568926e-05
- `obs_alarm_gated_startup_leakage_w`: 7.862931e-06
- `obs_alarm_gated_startup_clock_w`: 7.370720e-05
- `obs_alarm_gated_startup_sequential_w`: 1.352465e-04
- `obs_alarm_gated_startup_combinational_w`: 2.251322e-05
- `obs_alarm_gated_startup_total_a`: 6.429639e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.232330e-04
- `obs_alarm_gated_steady_internal_w`: 1.631375e-04
- `obs_alarm_gated_steady_switching_w`: 5.225340e-05
- `obs_alarm_gated_steady_leakage_w`: 7.842063e-06
- `obs_alarm_gated_steady_clock_w`: 7.370720e-05
- `obs_alarm_gated_steady_sequential_w`: 1.323378e-04
- `obs_alarm_gated_steady_combinational_w`: 1.718798e-05
- `obs_alarm_gated_steady_total_a`: 6.200917e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.056975e-04
- `obs_backpressure_reset_internal_w`: 1.524827e-04
- `obs_backpressure_reset_switching_w`: 4.594235e-05
- `obs_backpressure_reset_leakage_w`: 7.272558e-06
- `obs_backpressure_reset_clock_w`: 7.370720e-05
- `obs_backpressure_reset_sequential_w`: 1.237079e-04
- `obs_backpressure_reset_combinational_w`: 8.282582e-06
- `obs_backpressure_reset_total_a`: 5.713819e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.319062e-04
- `obs_backpressure_startup_internal_w`: 1.681892e-04
- `obs_backpressure_startup_switching_w`: 5.585923e-05
- `obs_backpressure_startup_leakage_w`: 7.857784e-06
- `obs_backpressure_startup_clock_w`: 7.370720e-05
- `obs_backpressure_startup_sequential_w`: 1.352985e-04
- `obs_backpressure_startup_combinational_w`: 2.290068e-05
- `obs_backpressure_startup_total_a`: 6.441839e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.497268e-04
- `obs_backpressure_steady_internal_w`: 1.792154e-04
- `obs_backpressure_steady_switching_w`: 6.231988e-05
- `obs_backpressure_steady_leakage_w`: 8.191520e-06
- `obs_backpressure_steady_clock_w`: 7.370720e-05
- `obs_backpressure_steady_sequential_w`: 1.441793e-04
- `obs_backpressure_steady_combinational_w`: 3.184023e-05
- `obs_backpressure_steady_total_a`: 6.936856e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.058440e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.525324e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.603907e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.272558e-06
- `obs_conditioned_streaming_reset_clock_w`: 7.370720e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.237188e-04
- `obs_conditioned_streaming_reset_combinational_w`: 8.418112e-06
- `obs_conditioned_streaming_reset_total_a`: 5.717889e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.324893e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.684846e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.614449e-05
- `obs_conditioned_streaming_startup_leakage_w`: 7.860215e-06
- `obs_conditioned_streaming_startup_clock_w`: 7.370720e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.355336e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.324856e-05
- `obs_conditioned_streaming_startup_total_a`: 6.458036e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.499563e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.793614e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.249721e-05
- `obs_conditioned_streaming_steady_leakage_w`: 8.097756e-06
- `obs_conditioned_streaming_steady_clock_w`: 7.370720e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.441374e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.211169e-05
- `obs_conditioned_streaming_steady_total_a`: 6.943231e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 2.046558e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.520368e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.534649e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.272558e-06
- `obs_disabled_clock_running_reset_clock_w`: 7.370720e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.236637e-04
- `obs_disabled_clock_running_reset_combinational_w`: 7.284852e-06
- `obs_disabled_clock_running_reset_total_a`: 5.684883e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.105197e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.560312e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.683277e-05
- `obs_disabled_clock_running_startup_leakage_w`: 7.655682e-06
- `obs_disabled_clock_running_startup_clock_w`: 7.370720e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.259715e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.084078e-05
- `obs_disabled_clock_running_startup_total_a`: 5.847769e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.102677e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.558587e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.675283e-05
- `obs_disabled_clock_running_steady_leakage_w`: 7.656220e-06
- `obs_disabled_clock_running_steady_clock_w`: 7.370720e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.260282e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.053219e-05
- `obs_disabled_clock_running_steady_total_a`: 5.840769e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.062481e-04
- `obs_raw_streaming_reset_internal_w`: 1.526415e-04
- `obs_raw_streaming_reset_switching_w`: 4.633401e-05
- `obs_raw_streaming_reset_leakage_w`: 7.272558e-06
- `obs_raw_streaming_reset_clock_w`: 7.370720e-05
- `obs_raw_streaming_reset_sequential_w`: 1.237176e-04
- `obs_raw_streaming_reset_combinational_w`: 8.823239e-06
- `obs_raw_streaming_reset_total_a`: 5.729114e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.336167e-04
- `obs_raw_streaming_startup_internal_w`: 1.689948e-04
- `obs_raw_streaming_startup_switching_w`: 5.680990e-05
- `obs_raw_streaming_startup_leakage_w`: 7.812067e-06
- `obs_raw_streaming_startup_clock_w`: 7.370720e-05
- `obs_raw_streaming_startup_sequential_w`: 1.355347e-04
- `obs_raw_streaming_startup_combinational_w`: 2.437479e-05
- `obs_raw_streaming_startup_total_a`: 6.489353e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.512706e-04
- `obs_raw_streaming_steady_internal_w`: 1.799313e-04
- `obs_raw_streaming_steady_switching_w`: 6.322328e-05
- `obs_raw_streaming_steady_leakage_w`: 8.116017e-06
- `obs_raw_streaming_steady_clock_w`: 7.370720e-05
- `obs_raw_streaming_steady_sequential_w`: 1.441777e-04
- `obs_raw_streaming_steady_combinational_w`: 3.338569e-05
- `obs_raw_streaming_steady_total_a`: 6.979739e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
