---
record: 2026-11-09-digital-sta-activity-02
date: 2026-11-09T21:56:41Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: 87b3dedca82354ea1c6b17e7e2867c806f9625f5
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha edd5900119f431c7d68f1f67eb3dcdf6b44ec32c).
repo_commit: 910461f4e20a99fe6369fa53beccde60370754b3-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib (liberty corner ss_125C_3v00, sha256:d83917f827021eadb159f6011905bf20de632533b2953abba89266a88c2b24af)
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
  process: ss
  voltage: 3.00 V (nominal 3.3 V, -9.1%)
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00
  interconnect: nom (OpenRCX rule deck)
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
  spef_sha256: 7af00669f760fb7e14a93ef1c3f5bb38ee62e77a2e331824c01011e8bef9079d
  spef_bytes: 1654157
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
      vcd_sha256: cb1d7aee2c0ba5e04161beca4aac3b24cc2dee586ed6cc7a1f5215d97863df01
      vcd_bytes: 17669097
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1423/1423
      xz_events: 4934
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: 9b061ae736049538e09ec41d92b1352fb3d84aa4e792f1c549283350dd05d96d
      vcd_bytes: 19101258
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1423/1423
      xz_events: 5236
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: 4f8de9215f6b9e43309280a614e7f84fa92be1c5d899956043c44e3c29bb0aaf
      vcd_bytes: 19148535
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1423/1423
      xz_events: 4971
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: 5a9bd1310e4c8d864b2d15546646caca70c24638ab57a921fd3910d43fe954b7
      vcd_bytes: 13464437
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1423/1423
      xz_events: 2224
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: 96e7b0cf056219fe0957d1c3af0f76b6c651a43eff1d95da3bf765e3c1e0ae14
      vcd_bytes: 19296058
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1423/1423
      xz_events: 5315
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-11-09-digital-sta-activity-02/
  files:
    - uniform.tcl  sha256:427ce58421dc2718a22324bde83fcd81c8b2fd814d135c8e5425226f21844a71
    - uniform.log  sha256:c101f09a34233db865e8b2366d0ab2d40f45fd2be4a8103e70fe1278cca45876
    - observed.tcl  sha256:52926528783a6a00984942041bab907061daba790ad3e8c709392a7fe679f010
    - observed.log  sha256:f6205d7c2c58f01c90da13b4e93f0731c77fa4c60d1dfe9ba5779c7d51600a32
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 8.8s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    143.98 |     65.13 |      2.14 |    211.24 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     95.92 |     30.46 |      2.13 |    128.50 | 0.608 | 5143 / 0 |
| alarm-gated | startup | 1040 |    106.61 |     37.93 |      2.14 |    146.68 | 0.694 | 5143 / 0 |
| alarm-gated | steady | 1024 |    103.63 |     35.63 |      2.14 |    141.40 | 0.669 | 5143 / 0 |
| backpressure | reset | 8 |     95.88 |     30.37 |      2.13 |    128.37 | 0.608 | 5143 / 0 |
| backpressure | startup | 1040 |    106.84 |     38.06 |      2.14 |    147.04 | 0.696 | 5143 / 0 |
| backpressure | steady | 1024 |    113.16 |     42.27 |      2.14 |    157.57 | 0.746 | 5143 / 0 |
| conditioned-streaming | reset | 8 |     95.91 |     30.45 |      2.13 |    128.49 | 0.608 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    107.08 |     38.25 |      2.14 |    147.47 | 0.698 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    113.28 |     42.42 |      2.14 |    157.84 | 0.747 | 5143 / 0 |
| disabled-clock-running | reset | 8 |     95.40 |     29.91 |      2.13 |    127.44 | 0.603 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |     97.96 |     31.64 |      2.14 |    131.73 | 0.624 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |     97.85 |     31.58 |      2.14 |    131.57 | 0.623 | 5143 / 0 |
| raw-streaming | reset | 8 |     95.84 |     30.58 |      2.13 |    128.55 | 0.609 | 5143 / 0 |
| raw-streaming | startup | 1040 |    107.17 |     38.63 |      2.14 |    147.94 | 0.700 | 5143 / 0 |
| raw-streaming | steady | 1024 |    113.53 |     42.89 |      2.14 |    158.56 | 0.751 | 5143 / 0 |

- `uniform_total_w`: 2.112415e-04
- `uniform_internal_w`: 1.439754e-04
- `uniform_switching_w`: 6.512593e-05
- `uniform_leakage_w`: 2.140195e-06
- `uniform_clock_w`: 4.567318e-05
- `uniform_sequential_w`: 1.104168e-04
- `uniform_combinational_w`: 5.515137e-05
- `uniform_total_a`: 7.041383e-05
- `obs_alarm_gated_reset_total_w`: 1.285048e-04
- `obs_alarm_gated_reset_internal_w`: 9.591630e-05
- `obs_alarm_gated_reset_switching_w`: 3.045816e-05
- `obs_alarm_gated_reset_leakage_w`: 2.130306e-06
- `obs_alarm_gated_reset_clock_w`: 4.567318e-05
- `obs_alarm_gated_reset_sequential_w`: 7.940856e-05
- `obs_alarm_gated_reset_combinational_w`: 3.423043e-06
- `obs_alarm_gated_reset_total_a`: 4.283493e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.466825e-04
- `obs_alarm_gated_startup_internal_w`: 1.066130e-04
- `obs_alarm_gated_startup_switching_w`: 3.793029e-05
- `obs_alarm_gated_startup_leakage_w`: 2.139170e-06
- `obs_alarm_gated_startup_clock_w`: 4.567318e-05
- `obs_alarm_gated_startup_sequential_w`: 8.734046e-05
- `obs_alarm_gated_startup_combinational_w`: 1.366885e-05
- `obs_alarm_gated_startup_total_a`: 4.889417e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.414036e-04
- `obs_alarm_gated_steady_internal_w`: 1.036347e-04
- `obs_alarm_gated_steady_switching_w`: 3.563010e-05
- `obs_alarm_gated_steady_leakage_w`: 2.138797e-06
- `obs_alarm_gated_steady_clock_w`: 4.567318e-05
- `obs_alarm_gated_steady_sequential_w`: 8.578223e-05
- `obs_alarm_gated_steady_combinational_w`: 9.948149e-06
- `obs_alarm_gated_steady_total_a`: 4.713453e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.283729e-04
- `obs_backpressure_reset_internal_w`: 9.587668e-05
- `obs_backpressure_reset_switching_w`: 3.036591e-05
- `obs_backpressure_reset_leakage_w`: 2.130306e-06
- `obs_backpressure_reset_clock_w`: 4.567318e-05
- `obs_backpressure_reset_sequential_w`: 7.940121e-05
- `obs_backpressure_reset_combinational_w`: 3.298537e-06
- `obs_backpressure_reset_total_a`: 4.279097e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.470368e-04
- `obs_backpressure_startup_internal_w`: 1.068351e-04
- `obs_backpressure_startup_switching_w`: 3.806235e-05
- `obs_backpressure_startup_leakage_w`: 2.139317e-06
- `obs_backpressure_startup_clock_w`: 4.567318e-05
- `obs_backpressure_startup_sequential_w`: 8.743040e-05
- `obs_backpressure_startup_combinational_w`: 1.393319e-05
- `obs_backpressure_startup_total_a`: 4.901227e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.575712e-04
- `obs_backpressure_steady_internal_w`: 1.131592e-04
- `obs_backpressure_steady_switching_w`: 4.226925e-05
- `obs_backpressure_steady_leakage_w`: 2.142745e-06
- `obs_backpressure_steady_clock_w`: 4.567318e-05
- `obs_backpressure_steady_sequential_w`: 9.305409e-05
- `obs_backpressure_steady_combinational_w`: 1.884400e-05
- `obs_backpressure_steady_total_a`: 5.252373e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.284852e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.590760e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.044732e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.130306e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.567318e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.940856e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.403520e-06
- `obs_conditioned_streaming_reset_total_a`: 4.282840e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.474732e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.070816e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.825286e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.138804e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.567318e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.764320e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.415685e-05
- `obs_conditioned_streaming_startup_total_a`: 4.915773e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.578383e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.132786e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.241828e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.141460e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.567318e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.307922e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.908587e-05
- `obs_conditioned_streaming_steady_total_a`: 5.261277e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.274387e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.539734e-05
- `obs_disabled_clock_running_reset_switching_w`: 2.991106e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.130306e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.567318e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.937133e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.394202e-06
- `obs_disabled_clock_running_reset_total_a`: 4.247957e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.317278e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.795624e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.163633e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.135238e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.567318e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.063878e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.415847e-06
- `obs_disabled_clock_running_startup_total_a`: 4.390927e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.315704e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.785459e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.158055e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.135238e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.567318e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.067713e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.220071e-06
- `obs_disabled_clock_running_steady_total_a`: 4.385680e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.285470e-04
- `obs_raw_streaming_reset_internal_w`: 9.583645e-05
- `obs_raw_streaming_reset_switching_w`: 3.058026e-05
- `obs_raw_streaming_reset_leakage_w`: 2.130306e-06
- `obs_raw_streaming_reset_clock_w`: 4.567318e-05
- `obs_raw_streaming_reset_sequential_w`: 7.940627e-05
- `obs_raw_streaming_reset_combinational_w`: 3.467585e-06
- `obs_raw_streaming_reset_total_a`: 4.284900e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.479390e-04
- `obs_raw_streaming_startup_internal_w`: 1.071749e-04
- `obs_raw_streaming_startup_switching_w`: 3.862529e-05
- `obs_raw_streaming_startup_leakage_w`: 2.138783e-06
- `obs_raw_streaming_startup_clock_w`: 4.567318e-05
- `obs_raw_streaming_startup_sequential_w`: 8.747222e-05
- `obs_raw_streaming_startup_combinational_w`: 1.479365e-05
- `obs_raw_streaming_startup_total_a`: 4.931300e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.585625e-04
- `obs_raw_streaming_steady_internal_w`: 1.135316e-04
- `obs_raw_streaming_steady_switching_w`: 4.288870e-05
- `obs_raw_streaming_steady_leakage_w`: 2.142267e-06
- `obs_raw_streaming_steady_clock_w`: 4.567318e-05
- `obs_raw_streaming_steady_sequential_w`: 9.304654e-05
- `obs_raw_streaming_steady_combinational_w`: 1.984286e-05
- `obs_raw_streaming_steady_total_a`: 5.285417e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_125C_3v00 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_125C_3v00, interconnect `nom`).
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
