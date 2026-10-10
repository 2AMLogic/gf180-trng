---
record: 2026-10-10-digital-sta-activity-18
date: 2026-10-10T07:11:47Z
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
  - rules.openrcx.gf180mcuD.max (OpenRCX interconnect corner max, sha256:0ee103cf2108f2fd945087551b6dd1eaf4ee55af60571de2983878c8a271515f)
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
  interconnect: max (OpenRCX rule deck)
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
  spef_sha256: fca53086a8aaf3ac0ac2dc575e46255e6f08084c972ccea5555ebd3a43cc199a
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-18/
  files:
    - uniform.tcl  sha256:329dbcd1f1832e1b1be1180479b671d4ba0bcbbe729cf5c002d5e015f4a3ea18
    - uniform.log  sha256:4a55a7969b8baa17f4f33b8bc73758696c4cd7a854ee99d3ce2c6d9541b564b6
    - observed.tcl  sha256:fa2980e6f0c2f176d04e33680be38cfe70a8fd6ece749f121f6bd92f1df4230c
    - observed.log  sha256:0a1a410449f8d59eb12d4313694e9e264d8bfd642e51d735b1ed8709aa28405d
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 8.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    147.32 |     70.91 |      2.21 |    220.44 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     96.20 |     32.06 |      2.20 |    130.46 | 0.592 | 5371 / 0 |
| alarm-gated | startup | 1040 |    105.31 |     38.80 |      2.21 |    146.32 | 0.664 | 5371 / 0 |
| alarm-gated | steady | 1024 |    102.52 |     36.39 |      2.21 |    141.12 | 0.640 | 5371 / 0 |
| backpressure | reset | 8 |     96.16 |     31.97 |      2.20 |    130.33 | 0.591 | 5371 / 0 |
| backpressure | startup | 1040 |    105.47 |     38.92 |      2.21 |    146.60 | 0.665 | 5371 / 0 |
| backpressure | steady | 1024 |    112.00 |     43.45 |      2.21 |    157.66 | 0.715 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     96.19 |     32.04 |      2.20 |    130.43 | 0.592 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    105.64 |     39.12 |      2.21 |    146.97 | 0.667 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    112.08 |     43.57 |      2.21 |    157.86 | 0.716 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     95.91 |     31.55 |      2.20 |    129.66 | 0.588 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     98.19 |     32.60 |      2.20 |    132.99 | 0.603 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     98.09 |     32.54 |      2.20 |    132.83 | 0.603 | 5371 / 0 |
| raw-streaming | reset | 8 |     96.25 |     32.24 |      2.20 |    130.69 | 0.593 | 5371 / 0 |
| raw-streaming | startup | 1040 |    105.93 |     39.58 |      2.21 |    147.72 | 0.670 | 5371 / 0 |
| raw-streaming | steady | 1024 |    112.41 |     44.08 |      2.21 |    158.70 | 0.720 | 5371 / 0 |

- `uniform_total_w`: 2.204419e-04
- `uniform_internal_w`: 1.473216e-04
- `uniform_switching_w`: 7.091141e-05
- `uniform_leakage_w`: 2.208865e-06
- `uniform_clock_w`: 4.602308e-05
- `uniform_sequential_w`: 1.144810e-04
- `uniform_combinational_w`: 5.993783e-05
- `uniform_total_a`: 7.348063e-05
- `obs_alarm_gated_reset_total_w`: 1.304568e-04
- `obs_alarm_gated_reset_internal_w`: 9.619813e-05
- `obs_alarm_gated_reset_switching_w`: 3.205997e-05
- `obs_alarm_gated_reset_leakage_w`: 2.198723e-06
- `obs_alarm_gated_reset_clock_w`: 4.602308e-05
- `obs_alarm_gated_reset_sequential_w`: 8.034132e-05
- `obs_alarm_gated_reset_combinational_w`: 4.092430e-06
- `obs_alarm_gated_reset_total_a`: 4.348560e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.463204e-04
- `obs_alarm_gated_startup_internal_w`: 1.053105e-04
- `obs_alarm_gated_startup_switching_w`: 3.880161e-05
- `obs_alarm_gated_startup_leakage_w`: 2.208328e-06
- `obs_alarm_gated_startup_clock_w`: 4.602308e-05
- `obs_alarm_gated_startup_sequential_w`: 8.755525e-05
- `obs_alarm_gated_startup_combinational_w`: 1.274204e-05
- `obs_alarm_gated_startup_total_a`: 4.877347e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.411173e-04
- `obs_alarm_gated_steady_internal_w`: 1.025170e-04
- `obs_alarm_gated_steady_switching_w`: 3.639247e-05
- `obs_alarm_gated_steady_leakage_w`: 2.207755e-06
- `obs_alarm_gated_steady_clock_w`: 4.602308e-05
- `obs_alarm_gated_steady_sequential_w`: 8.566480e-05
- `obs_alarm_gated_steady_combinational_w`: 9.429327e-06
- `obs_alarm_gated_steady_total_a`: 4.703910e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.303259e-04
- `obs_backpressure_reset_internal_w`: 9.615768e-05
- `obs_backpressure_reset_switching_w`: 3.196951e-05
- `obs_backpressure_reset_leakage_w`: 2.198723e-06
- `obs_backpressure_reset_clock_w`: 4.602308e-05
- `obs_backpressure_reset_sequential_w`: 8.033399e-05
- `obs_backpressure_reset_combinational_w`: 3.968830e-06
- `obs_backpressure_reset_total_a`: 4.344197e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.466046e-04
- `obs_backpressure_startup_internal_w`: 1.054747e-04
- `obs_backpressure_startup_switching_w`: 3.892127e-05
- `obs_backpressure_startup_leakage_w`: 2.208553e-06
- `obs_backpressure_startup_clock_w`: 4.602308e-05
- `obs_backpressure_startup_sequential_w`: 8.758457e-05
- `obs_backpressure_startup_combinational_w`: 1.299689e-05
- `obs_backpressure_startup_total_a`: 4.886820e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.576598e-04
- `obs_backpressure_steady_internal_w`: 1.120003e-04
- `obs_backpressure_steady_switching_w`: 4.344751e-05
- `obs_backpressure_steady_leakage_w`: 2.212008e-06
- `obs_backpressure_steady_clock_w`: 4.602308e-05
- `obs_backpressure_steady_sequential_w`: 9.314093e-05
- `obs_backpressure_steady_combinational_w`: 1.849585e-05
- `obs_backpressure_steady_total_a`: 5.255327e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.304255e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.618945e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.203738e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.198723e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.602308e-05
- `obs_conditioned_streaming_reset_sequential_w`: 8.034131e-05
- `obs_conditioned_streaming_reset_combinational_w`: 4.061147e-06
- `obs_conditioned_streaming_reset_total_a`: 4.347517e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.469741e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.056447e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.912136e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.207989e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.602308e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.774286e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.320812e-05
- `obs_conditioned_streaming_startup_total_a`: 4.899137e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.578618e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.120788e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.357219e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.210763e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.602308e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.312172e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.871702e-05
- `obs_conditioned_streaming_steady_total_a`: 5.262060e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.296599e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.590777e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.155344e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.198723e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.602308e-05
- `obs_disabled_clock_running_reset_sequential_w`: 8.030657e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.330249e-06
- `obs_disabled_clock_running_reset_total_a`: 4.321997e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.329929e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.819189e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.259644e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.602308e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.157374e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.396119e-06
- `obs_disabled_clock_running_startup_total_a`: 4.433097e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.328334e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.808841e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.254041e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.602308e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.161368e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.196665e-06
- `obs_disabled_clock_running_steady_total_a`: 4.427780e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.306913e-04
- `obs_raw_streaming_reset_internal_w`: 9.624783e-05
- `obs_raw_streaming_reset_switching_w`: 3.224476e-05
- `obs_raw_streaming_reset_leakage_w`: 2.198723e-06
- `obs_raw_streaming_reset_clock_w`: 4.602308e-05
- `obs_raw_streaming_reset_sequential_w`: 8.034114e-05
- `obs_raw_streaming_reset_combinational_w`: 4.327076e-06
- `obs_raw_streaming_reset_total_a`: 4.356377e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.477243e-04
- `obs_raw_streaming_startup_internal_w`: 1.059316e-04
- `obs_raw_streaming_startup_switching_w`: 3.958471e-05
- `obs_raw_streaming_startup_leakage_w`: 2.207986e-06
- `obs_raw_streaming_startup_clock_w`: 4.602308e-05
- `obs_raw_streaming_startup_sequential_w`: 8.774388e-05
- `obs_raw_streaming_startup_combinational_w`: 1.395740e-05
- `obs_raw_streaming_startup_total_a`: 4.924143e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.586996e-04
- `obs_raw_streaming_steady_internal_w`: 1.124090e-04
- `obs_raw_streaming_steady_switching_w`: 4.407910e-05
- `obs_raw_streaming_steady_leakage_w`: 2.211509e-06
- `obs_raw_streaming_steady_clock_w`: 4.602308e-05
- `obs_raw_streaming_steady_sequential_w`: 9.314397e-05
- `obs_raw_streaming_steady_combinational_w`: 1.953253e-05
- `obs_raw_streaming_steady_total_a`: 5.289987e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_125C_3v00 --rc max --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_125C_3v00, interconnect `max`).
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
