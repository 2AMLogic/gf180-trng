---
record: 2026-10-10-digital-sta-activity-16
date: 2026-10-10T07:11:31Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib (liberty corner ss_125C_3v00, sha256:c31d836785af6af4502aadaaf7cc0f604119d38fd66b8ee32733510eabdad6d2)
  - gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:332ae93d61ac55f793da97a6391703f78bc415653cb60e76dd8eb0092124485a)
  - gf180mcu_fd_sc_mcu9t5v0.lef (cell LEF, sha256:38afbef95529165e1d8999d5b5613c4aec9869df8c1ce6b5555e74586ba4c826)
  - rules.openrcx.gf180mcuD.min (OpenRCX interconnect corner min, sha256:5cf275c985ffd49096407d22891910fea34aff5a915db8a5b9a7c1e04b737e00)
  - <pdk>/libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/gf180mcu_fd_sc_mcu9t5v0.v (gate-simulation cell model, sha256:7dc2d6578c3580b0716c6a883a1b33c6cc7172f29c74ac1b148b0b20f981fe16)
  - <pdk>/libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/primitives.v (gate-simulation cell model, sha256:fc47cb4d4e50feb06847eba4bb1d67bec09a648fe2ab7aeab30248cb75d3609c)

tool:
  ngspice: "n/a (gate-level record)"
  openroad: "26Q3-1510-g6cb3f2b704"
  simulator: "Icarus Verilog version 13.0 (stable) (v13_0) -g2012 -gno-specify (zero delay; specify blocks ignored)"

corner:
  process: ss
  voltage: 3.00 V (nominal 3.3 V, -9.1%)
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00
  interconnect: min (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature 125, nom_voltage 3 (read from the deck)

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
  spef_sha256: b31e0cf9bd8fca7776f16822d83cd190a9f6907f32eb355155a09b2af0a18699
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-16/
  files:
    - uniform.tcl  sha256:d4c060c0565d30a9fef572f5e731fad5b6ea92ca2f16fbb8b3251547f351bdeb
    - uniform.log  sha256:c62f43a2963500f51d441c7845d40d92f7a7e01ec817a236809bfbabd18b105e
    - observed.tcl  sha256:e522b06bb0b9845d149b358f87003e6bbcd89c7e8b050a2ffcea072c89ebb0ad
    - observed.log  sha256:74a1657a73713bcf8efca818d09952143763c174cab3d39f12602f2a6c70eda1
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 7.9s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    146.96 |     65.73 |      2.21 |    214.89 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     95.92 |     29.86 |      2.20 |    127.98 | 0.596 | 5371 / 0 |
| alarm-gated | startup | 1040 |    105.03 |     36.19 |      2.21 |    143.43 | 0.667 | 5371 / 0 |
| alarm-gated | steady | 1024 |    102.24 |     33.92 |      2.21 |    138.37 | 0.644 | 5371 / 0 |
| backpressure | reset | 8 |     95.88 |     29.77 |      2.20 |    127.86 | 0.595 | 5371 / 0 |
| backpressure | startup | 1040 |    105.19 |     36.30 |      2.21 |    143.70 | 0.669 | 5371 / 0 |
| backpressure | steady | 1024 |    111.70 |     40.51 |      2.21 |    154.42 | 0.719 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     95.92 |     29.84 |      2.20 |    127.95 | 0.595 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    105.36 |     36.49 |      2.21 |    144.06 | 0.670 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    111.78 |     40.62 |      2.21 |    154.62 | 0.719 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     95.64 |     29.39 |      2.20 |    127.23 | 0.592 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     97.92 |     30.41 |      2.20 |    130.53 | 0.607 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     97.82 |     30.35 |      2.20 |    130.37 | 0.607 | 5371 / 0 |
| raw-streaming | reset | 8 |     95.97 |     30.03 |      2.20 |    128.20 | 0.597 | 5371 / 0 |
| raw-streaming | startup | 1040 |    105.65 |     36.90 |      2.21 |    144.76 | 0.674 | 5371 / 0 |
| raw-streaming | steady | 1024 |    112.11 |     41.08 |      2.21 |    155.40 | 0.723 | 5371 / 0 |

- `uniform_total_w`: 2.148947e-04
- `uniform_internal_w`: 1.469572e-04
- `uniform_switching_w`: 6.572864e-05
- `uniform_leakage_w`: 2.208865e-06
- `uniform_clock_w`: 4.382992e-05
- `uniform_sequential_w`: 1.137941e-04
- `uniform_combinational_w`: 5.727071e-05
- `uniform_total_a`: 7.163157e-05
- `obs_alarm_gated_reset_total_w`: 1.279819e-04
- `obs_alarm_gated_reset_internal_w`: 9.592465e-05
- `obs_alarm_gated_reset_switching_w`: 2.985849e-05
- `obs_alarm_gated_reset_leakage_w`: 2.198723e-06
- `obs_alarm_gated_reset_clock_w`: 4.382992e-05
- `obs_alarm_gated_reset_sequential_w`: 8.023532e-05
- `obs_alarm_gated_reset_combinational_w`: 3.916632e-06
- `obs_alarm_gated_reset_total_a`: 4.266063e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.434276e-04
- `obs_alarm_gated_startup_internal_w`: 1.050266e-04
- `obs_alarm_gated_startup_switching_w`: 3.619264e-05
- `obs_alarm_gated_startup_leakage_w`: 2.208328e-06
- `obs_alarm_gated_startup_clock_w`: 4.382992e-05
- `obs_alarm_gated_startup_sequential_w`: 8.726655e-05
- `obs_alarm_gated_startup_combinational_w`: 1.233106e-05
- `obs_alarm_gated_startup_total_a`: 4.780920e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.383711e-04
- `obs_alarm_gated_steady_internal_w`: 1.022384e-04
- `obs_alarm_gated_steady_switching_w`: 3.392499e-05
- `obs_alarm_gated_steady_leakage_w`: 2.207755e-06
- `obs_alarm_gated_steady_clock_w`: 4.382992e-05
- `obs_alarm_gated_steady_sequential_w`: 8.542196e-05
- `obs_alarm_gated_steady_combinational_w`: 9.119231e-06
- `obs_alarm_gated_steady_total_a`: 4.612370e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.278578e-04
- `obs_backpressure_reset_internal_w`: 9.588415e-05
- `obs_backpressure_reset_switching_w`: 2.977493e-05
- `obs_backpressure_reset_leakage_w`: 2.198723e-06
- `obs_backpressure_reset_clock_w`: 4.382992e-05
- `obs_backpressure_reset_sequential_w`: 8.022800e-05
- `obs_backpressure_reset_combinational_w`: 3.799892e-06
- `obs_backpressure_reset_total_a`: 4.261927e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.437040e-04
- `obs_backpressure_startup_internal_w`: 1.051907e-04
- `obs_backpressure_startup_switching_w`: 3.630477e-05
- `obs_backpressure_startup_leakage_w`: 2.208553e-06
- `obs_backpressure_startup_clock_w`: 4.382992e-05
- `obs_backpressure_startup_sequential_w`: 8.729686e-05
- `obs_backpressure_startup_combinational_w`: 1.257716e-05
- `obs_backpressure_startup_total_a`: 4.790133e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.544237e-04
- `obs_backpressure_steady_internal_w`: 1.117034e-04
- `obs_backpressure_steady_switching_w`: 4.050830e-05
- `obs_backpressure_steady_leakage_w`: 2.212008e-06
- `obs_backpressure_steady_clock_w`: 4.382992e-05
- `obs_backpressure_steady_sequential_w`: 9.273958e-05
- `obs_backpressure_steady_combinational_w`: 1.785422e-05
- `obs_backpressure_steady_total_a`: 5.147457e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.279514e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.591595e-05
- `obs_conditioned_streaming_reset_switching_w`: 2.983673e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.198723e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.382992e-05
- `obs_conditioned_streaming_reset_sequential_w`: 8.023532e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.886177e-06
- `obs_conditioned_streaming_reset_total_a`: 4.265047e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.440588e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.053603e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.649054e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.207989e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.382992e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.745041e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.277845e-05
- `obs_conditioned_streaming_startup_total_a`: 4.801960e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.546156e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.117816e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.062328e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.210763e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.382992e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.271997e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.806584e-05
- `obs_conditioned_streaming_steady_total_a`: 5.153853e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.272268e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.563575e-05
- `obs_disabled_clock_running_reset_switching_w`: 2.939228e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.198723e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.382992e-05
- `obs_disabled_clock_running_reset_sequential_w`: 8.020058e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.196285e-06
- `obs_disabled_clock_running_reset_total_a`: 4.240893e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.305287e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.791844e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.040563e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.382992e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.143902e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.259761e-06
- `obs_disabled_clock_running_startup_total_a`: 4.350957e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.303740e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.781503e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.035432e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.382992e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.147727e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.066792e-06
- `obs_disabled_clock_running_steady_total_a`: 4.345800e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.282016e-04
- `obs_raw_streaming_reset_internal_w`: 9.597418e-05
- `obs_raw_streaming_reset_switching_w`: 3.002872e-05
- `obs_raw_streaming_reset_leakage_w`: 2.198723e-06
- `obs_raw_streaming_reset_clock_w`: 4.382992e-05
- `obs_raw_streaming_reset_sequential_w`: 8.023516e-05
- `obs_raw_streaming_reset_combinational_w`: 4.136561e-06
- `obs_raw_streaming_reset_total_a`: 4.273387e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.447568e-04
- `obs_raw_streaming_startup_internal_w`: 1.056451e-04
- `obs_raw_streaming_startup_switching_w`: 3.690373e-05
- `obs_raw_streaming_startup_leakage_w`: 2.207986e-06
- `obs_raw_streaming_startup_clock_w`: 4.382992e-05
- `obs_raw_streaming_startup_sequential_w`: 8.745129e-05
- `obs_raw_streaming_startup_combinational_w`: 1.347552e-05
- `obs_raw_streaming_startup_total_a`: 4.825227e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.554004e-04
- `obs_raw_streaming_steady_internal_w`: 1.121099e-04
- `obs_raw_streaming_steady_switching_w`: 4.107905e-05
- `obs_raw_streaming_steady_leakage_w`: 2.211509e-06
- `obs_raw_streaming_steady_clock_w`: 4.382992e-05
- `obs_raw_streaming_steady_sequential_w`: 9.274173e-05
- `obs_raw_streaming_steady_combinational_w`: 1.882874e-05
- `obs_raw_streaming_steady_total_a`: 5.180013e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_125C_3v00 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_125C_3v00, interconnect `min`).
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
