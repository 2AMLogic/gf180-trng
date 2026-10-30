---
record: 2026-10-30-digital-sta-activity-04
date: 2026-10-30T15:17:10Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: d24d862fc3836f8f5514aa2fa32e319f1a96567c
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha bb949d10cf059e01698f33f6531b74da1df90358).
repo_commit: 8939b542e96bfc19151bee88578dc394b5468fe2-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - gf180mcu_fd_sc_mcu9t5v0__ss_n40C_3v00.lib (liberty corner ss_n40C_3v00, sha256:03238cd7c39382b10bd1ff526c37c9ac3c73cc92c01cd2c249cb86978bda9de3)
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
  process: ss
  voltage: 3.00 V (nominal 3.3 V, -9.1%)
  temperature: -40
  liberty: gf180mcu_fd_sc_mcu9t5v0__ss_n40C_3v00
  interconnect: min (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature -40, nom_voltage 3 (read from the deck)

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
  spef_sha256: 3d8d38e81fff980a1157a4af5f1c00c48249c3c45c3935cf111dfb6c4a3abde7
  spef_bytes: 1789895
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
      vcd_sha256: d73b73c2878833b11c530926e16d4581e020fd1f07ba48aec025168df2997b09
      vcd_bytes: 20199467
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1490/1490
      xz_events: 4272
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: ce683a6499939dfdfbc7f0948d9cdf6e0fb7118b0eea81c99310ea9ff8a19a6d
      vcd_bytes: 21556003
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4289
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: 1b70087f5ae79f73da990c9d9aa9738670f74a6b31e57f02cc3f2ba736fa55fc
      vcd_bytes: 21612163
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4168
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: a10758043594e820119885dbb73a054dc89bfbbf413e35c32c5bd544f30648a5
      vcd_bytes: 16158866
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 1798
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: a8544b5fe783833514bdbc26788df620d3f8969d23472620ed7021e0628acd65
      vcd_bytes: 21759020
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4488
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-10-30-digital-sta-activity-04/
  files:
    - uniform.tcl  sha256:fca0446c20b8edca305adbf65832387be8795fe22e834dc7355b322aa95d0930
    - uniform.log  sha256:6e7a261bec3a58c5fd9a2062ef7857812adaec812c6aae2cd525a6b9b14837aa
    - observed.tcl  sha256:f819999783cde37f58675a70c11ee5ba0cd29ca7260103124fdfeb2e338a3a78
    - observed.log  sha256:eeffbcf0a9f799990f30600d8fb4f3ceddae128f2decee69a3f03ad8f7c9e2c5
    - activity-manifest.json  sha256:1e327145d7667bd16602328c74156fdb1a0755c542aa19e43d054aedb64852d1
wall_time: 8.4s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    136.69 |     64.15 |      0.19 |    201.03 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     90.52 |     29.28 |      0.18 |    119.98 | 0.597 | 5371 / 0 |
| alarm-gated | startup | 1040 |     98.73 |     35.47 |      0.19 |    134.38 | 0.668 | 5371 / 0 |
| alarm-gated | steady | 1024 |     96.23 |     33.33 |      0.18 |    129.74 | 0.645 | 5371 / 0 |
| backpressure | reset | 8 |     90.48 |     29.21 |      0.18 |    119.87 | 0.596 | 5371 / 0 |
| backpressure | startup | 1040 |     98.88 |     35.58 |      0.19 |    134.64 | 0.670 | 5371 / 0 |
| backpressure | steady | 1024 |    104.80 |     39.61 |      0.19 |    144.60 | 0.719 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     90.51 |     29.26 |      0.18 |    119.95 | 0.597 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |     99.03 |     35.76 |      0.18 |    134.97 | 0.671 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    104.87 |     39.73 |      0.19 |    144.78 | 0.720 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     90.26 |     28.85 |      0.18 |    119.29 | 0.593 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     92.29 |     29.82 |      0.18 |    122.28 | 0.608 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     92.19 |     29.77 |      0.18 |    122.14 | 0.608 | 5371 / 0 |
| raw-streaming | reset | 8 |     90.56 |     29.44 |      0.18 |    120.18 | 0.598 | 5371 / 0 |
| raw-streaming | startup | 1040 |     99.28 |     36.16 |      0.18 |    135.63 | 0.675 | 5371 / 0 |
| raw-streaming | steady | 1024 |    105.16 |     40.17 |      0.19 |    145.52 | 0.724 | 5371 / 0 |

- `uniform_total_w`: 2.010296e-04
- `uniform_internal_w`: 1.366939e-04
- `uniform_switching_w`: 6.414984e-05
- `uniform_leakage_w`: 1.858777e-07
- `uniform_clock_w`: 4.035761e-05
- `uniform_sequential_w`: 1.076982e-04
- `uniform_combinational_w`: 5.297356e-05
- `uniform_total_a`: 6.700987e-05
- `obs_alarm_gated_reset_total_w`: 1.199837e-04
- `obs_alarm_gated_reset_internal_w`: 9.052034e-05
- `obs_alarm_gated_reset_switching_w`: 2.928363e-05
- `obs_alarm_gated_reset_leakage_w`: 1.797297e-07
- `obs_alarm_gated_reset_clock_w`: 4.035761e-05
- `obs_alarm_gated_reset_sequential_w`: 7.633903e-05
- `obs_alarm_gated_reset_combinational_w`: 3.287184e-06
- `obs_alarm_gated_reset_total_a`: 3.999457e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.343828e-04
- `obs_alarm_gated_startup_internal_w`: 9.872986e-05
- `obs_alarm_gated_startup_switching_w`: 3.546780e-05
- `obs_alarm_gated_startup_leakage_w`: 1.851220e-07
- `obs_alarm_gated_startup_clock_w`: 4.035761e-05
- `obs_alarm_gated_startup_sequential_w`: 8.297811e-05
- `obs_alarm_gated_startup_combinational_w`: 1.104709e-05
- `obs_alarm_gated_startup_total_a`: 4.479427e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.297393e-04
- `obs_alarm_gated_steady_internal_w`: 9.622581e-05
- `obs_alarm_gated_steady_switching_w`: 3.332891e-05
- `obs_alarm_gated_steady_leakage_w`: 1.846309e-07
- `obs_alarm_gated_steady_clock_w`: 4.035761e-05
- `obs_alarm_gated_steady_sequential_w`: 8.123968e-05
- `obs_alarm_gated_steady_combinational_w`: 8.142063e-06
- `obs_alarm_gated_steady_total_a`: 4.324643e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.198680e-04
- `obs_backpressure_reset_internal_w`: 9.048187e-05
- `obs_backpressure_reset_switching_w`: 2.920641e-05
- `obs_backpressure_reset_leakage_w`: 1.797297e-07
- `obs_backpressure_reset_clock_w`: 4.035761e-05
- `obs_backpressure_reset_sequential_w`: 7.633217e-05
- `obs_backpressure_reset_combinational_w`: 3.178345e-06
- `obs_backpressure_reset_total_a`: 3.995600e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.346365e-04
- `obs_backpressure_startup_internal_w`: 9.887600e-05
- `obs_backpressure_startup_switching_w`: 3.557525e-05
- `obs_backpressure_startup_leakage_w`: 1.852611e-07
- `obs_backpressure_startup_clock_w`: 4.035761e-05
- `obs_backpressure_startup_sequential_w`: 8.300591e-05
- `obs_backpressure_startup_combinational_w`: 1.127298e-05
- `obs_backpressure_startup_total_a`: 4.487883e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.445973e-04
- `obs_backpressure_steady_internal_w`: 1.047969e-04
- `obs_backpressure_steady_switching_w`: 3.961301e-05
- `obs_backpressure_steady_leakage_w`: 1.874145e-07
- `obs_backpressure_steady_clock_w`: 4.035761e-05
- `obs_backpressure_steady_sequential_w`: 8.805610e-05
- `obs_backpressure_steady_combinational_w`: 1.618358e-05
- `obs_backpressure_steady_total_a`: 4.819910e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.199547e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.051188e-05
- `obs_conditioned_streaming_reset_switching_w`: 2.926308e-05
- `obs_conditioned_streaming_reset_leakage_w`: 1.797297e-07
- `obs_conditioned_streaming_reset_clock_w`: 4.035761e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.633903e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.258152e-06
- `obs_conditioned_streaming_reset_total_a`: 3.998490e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.349734e-04
- `obs_conditioned_streaming_startup_internal_w`: 9.903263e-05
- `obs_conditioned_streaming_startup_switching_w`: 3.575579e-05
- `obs_conditioned_streaming_startup_leakage_w`: 1.849570e-07
- `obs_conditioned_streaming_startup_clock_w`: 4.035761e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.315332e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.146244e-05
- `obs_conditioned_streaming_startup_total_a`: 4.499113e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.447817e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.048672e-04
- `obs_conditioned_streaming_steady_switching_w`: 3.972772e-05
- `obs_conditioned_streaming_steady_leakage_w`: 1.867787e-07
- `obs_conditioned_streaming_steady_clock_w`: 4.035761e-05
- `obs_conditioned_streaming_steady_sequential_w`: 8.803810e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.638604e-05
- `obs_conditioned_streaming_steady_total_a`: 4.826057e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.192863e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.025609e-05
- `obs_disabled_clock_running_reset_switching_w`: 2.885046e-05
- `obs_disabled_clock_running_reset_leakage_w`: 1.797297e-07
- `obs_disabled_clock_running_reset_clock_w`: 4.035761e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.630671e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.622055e-06
- `obs_disabled_clock_running_reset_total_a`: 3.976210e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.222836e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.228516e-05
- `obs_disabled_clock_running_startup_switching_w`: 2.981615e-05
- `obs_disabled_clock_running_startup_leakage_w`: 1.823146e-07
- `obs_disabled_clock_running_startup_clock_w`: 4.035761e-05
- `obs_disabled_clock_running_startup_sequential_w`: 7.749296e-05
- `obs_disabled_clock_running_startup_combinational_w`: 4.433120e-06
- `obs_disabled_clock_running_startup_total_a`: 4.076120e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.221406e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.219286e-05
- `obs_disabled_clock_running_steady_switching_w`: 2.976544e-05
- `obs_disabled_clock_running_steady_leakage_w`: 1.823140e-07
- `obs_disabled_clock_running_steady_clock_w`: 4.035761e-05
- `obs_disabled_clock_running_steady_sequential_w`: 7.753070e-05
- `obs_disabled_clock_running_steady_combinational_w`: 4.252372e-06
- `obs_disabled_clock_running_steady_total_a`: 4.071353e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.201822e-04
- `obs_raw_streaming_reset_internal_w`: 9.056065e-05
- `obs_raw_streaming_reset_switching_w`: 2.944178e-05
- `obs_raw_streaming_reset_leakage_w`: 1.797297e-07
- `obs_raw_streaming_reset_clock_w`: 4.035761e-05
- `obs_raw_streaming_reset_sequential_w`: 7.633901e-05
- `obs_raw_streaming_reset_combinational_w`: 3.485666e-06
- `obs_raw_streaming_reset_total_a`: 4.006073e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.356314e-04
- `obs_raw_streaming_startup_internal_w`: 9.928346e-05
- `obs_raw_streaming_startup_switching_w`: 3.616297e-05
- `obs_raw_streaming_startup_leakage_w`: 1.849621e-07
- `obs_raw_streaming_startup_clock_w`: 4.035761e-05
- `obs_raw_streaming_startup_sequential_w`: 8.315812e-05
- `obs_raw_streaming_startup_combinational_w`: 1.211574e-05
- `obs_raw_streaming_startup_total_a`: 4.521047e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.455185e-04
- `obs_raw_streaming_steady_internal_w`: 1.051602e-04
- `obs_raw_streaming_steady_switching_w`: 4.017106e-05
- `obs_raw_streaming_steady_leakage_w`: 1.872706e-07
- `obs_raw_streaming_steady_clock_w`: 4.035761e-05
- `obs_raw_streaming_steady_sequential_w`: 8.805910e-05
- `obs_raw_streaming_steady_combinational_w`: 1.710180e-05
- `obs_raw_streaming_steady_total_a`: 4.850617e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_n40C_3v00 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_n40C_3v00, interconnect `min`).
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
