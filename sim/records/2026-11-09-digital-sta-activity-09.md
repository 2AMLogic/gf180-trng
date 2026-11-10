---
record: 2026-11-09-digital-sta-activity-09
date: 2026-11-09T21:57:43Z
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
  - gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30.lib (liberty corner tt_025C_3v30, sha256:1157d0aa147dba75a214708197d7a046f970175d723cdec108025f6f06727c12)
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
  process: tt
  voltage: 3.30 V (nominal 3.3 V)
  temperature: 25
  liberty: gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30
  interconnect: max (OpenRCX rule deck)
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
  spef_sha256: 4c3165a9db709592a1cb5e8d9b588c61a5b5af079b83b9f2ec4d0ae1290e292d
  spef_bytes: 1661195
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
  path: sim/records/raw/2026-11-09-digital-sta-activity-09/
  files:
    - uniform.tcl  sha256:e20740d65c1017298f72f96abd36e7464af636fb47d741991e67efb1054b5e73
    - uniform.log  sha256:d8910045abe914790b6ae754c7d44188cd3544a539fd89ca35ca49496bb2b48b
    - observed.tcl  sha256:351e14166e771f06552e8f7dc84c1b291ba414749b1c00093711988df95c0069
    - observed.log  sha256:90fc97c2b62ffe14d8f60d7f5ecc47f5aeec4e8700d1d3edb93ae9816d488bea
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 8.9s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    173.58 |     81.15 |      0.21 |    254.94 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    115.30 |     37.90 |      0.20 |    153.41 | 0.602 | 5143 / 0 |
| alarm-gated | startup | 1040 |    128.21 |     47.15 |      0.21 |    175.57 | 0.689 | 5143 / 0 |
| alarm-gated | steady | 1024 |    124.58 |     44.31 |      0.21 |    169.11 | 0.663 | 5143 / 0 |
| backpressure | reset | 8 |    115.25 |     37.79 |      0.20 |    153.24 | 0.601 | 5143 / 0 |
| backpressure | startup | 1040 |    128.48 |     47.31 |      0.21 |    176.00 | 0.690 | 5143 / 0 |
| backpressure | steady | 1024 |    136.11 |     52.52 |      0.22 |    188.84 | 0.741 | 5143 / 0 |
| conditioned-streaming | reset | 8 |    115.29 |     37.89 |      0.20 |    153.38 | 0.602 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    128.78 |     47.55 |      0.21 |    176.54 | 0.692 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    136.26 |     52.70 |      0.21 |    189.17 | 0.742 | 5143 / 0 |
| disabled-clock-running | reset | 8 |    114.66 |     37.22 |      0.20 |    152.08 | 0.597 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |    117.78 |     39.36 |      0.21 |    157.34 | 0.617 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |    117.65 |     39.29 |      0.21 |    157.15 | 0.616 | 5143 / 0 |
| raw-streaming | reset | 8 |    115.20 |     38.06 |      0.20 |    153.46 | 0.602 | 5143 / 0 |
| raw-streaming | startup | 1040 |    128.90 |     48.02 |      0.21 |    177.13 | 0.695 | 5143 / 0 |
| raw-streaming | steady | 1024 |    136.56 |     53.30 |      0.22 |    190.08 | 0.746 | 5143 / 0 |

- `uniform_total_w`: 2.549394e-04
- `uniform_internal_w`: 1.735781e-04
- `uniform_switching_w`: 8.114670e-05
- `uniform_leakage_w`: 2.145970e-07
- `uniform_clock_w`: 5.566904e-05
- `uniform_sequential_w`: 1.316120e-04
- `uniform_combinational_w`: 6.765849e-05
- `uniform_total_a`: 7.725436e-05
- `obs_alarm_gated_reset_total_w`: 1.534050e-04
- `obs_alarm_gated_reset_internal_w`: 1.152988e-04
- `obs_alarm_gated_reset_switching_w`: 3.790284e-05
- `obs_alarm_gated_reset_leakage_w`: 2.033711e-07
- `obs_alarm_gated_reset_clock_w`: 5.566904e-05
- `obs_alarm_gated_reset_sequential_w`: 9.406106e-05
- `obs_alarm_gated_reset_combinational_w`: 3.674875e-06
- `obs_alarm_gated_reset_total_a`: 4.648636e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.755720e-04
- `obs_alarm_gated_startup_internal_w`: 1.282115e-04
- `obs_alarm_gated_startup_switching_w`: 4.714918e-05
- `obs_alarm_gated_startup_leakage_w`: 2.113422e-07
- `obs_alarm_gated_startup_clock_w`: 5.566904e-05
- `obs_alarm_gated_startup_sequential_w`: 1.037151e-04
- `obs_alarm_gated_startup_combinational_w`: 1.618791e-05
- `obs_alarm_gated_startup_total_a`: 5.320364e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.691051e-04
- `obs_alarm_gated_steady_internal_w`: 1.245819e-04
- `obs_alarm_gated_steady_switching_w`: 4.431219e-05
- `obs_alarm_gated_steady_leakage_w`: 2.109673e-07
- `obs_alarm_gated_steady_clock_w`: 5.566904e-05
- `obs_alarm_gated_steady_sequential_w`: 1.018229e-04
- `obs_alarm_gated_steady_combinational_w`: 1.161322e-05
- `obs_alarm_gated_steady_total_a`: 5.124397e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.532426e-04
- `obs_backpressure_reset_internal_w`: 1.152496e-04
- `obs_backpressure_reset_switching_w`: 3.778964e-05
- `obs_backpressure_reset_leakage_w`: 2.033711e-07
- `obs_backpressure_reset_clock_w`: 5.566904e-05
- `obs_backpressure_reset_sequential_w`: 9.405243e-05
- `obs_backpressure_reset_combinational_w`: 3.521097e-06
- `obs_backpressure_reset_total_a`: 4.643715e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.760039e-04
- `obs_backpressure_startup_internal_w`: 1.284785e-04
- `obs_backpressure_startup_switching_w`: 4.731372e-05
- `obs_backpressure_startup_leakage_w`: 2.116402e-07
- `obs_backpressure_startup_clock_w`: 5.566904e-05
- `obs_backpressure_startup_sequential_w`: 1.038236e-04
- `obs_backpressure_startup_combinational_w`: 1.651117e-05
- `obs_backpressure_startup_total_a`: 5.333452e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.888419e-04
- `obs_backpressure_steady_internal_w`: 1.361103e-04
- `obs_backpressure_steady_switching_w`: 5.251542e-05
- `obs_backpressure_steady_leakage_w`: 2.161484e-07
- `obs_backpressure_steady_clock_w`: 5.566904e-05
- `obs_backpressure_steady_sequential_w`: 1.106534e-04
- `obs_backpressure_steady_combinational_w`: 2.251931e-05
- `obs_backpressure_steady_total_a`: 5.722482e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.533818e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.152874e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.789100e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.033711e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.566904e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.406108e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.651631e-06
- `obs_conditioned_streaming_reset_total_a`: 4.647933e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.765381e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.287771e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.755004e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.109732e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.566904e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.040848e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.678427e-05
- `obs_conditioned_streaming_startup_total_a`: 5.349639e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.891747e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.362556e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.270410e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.149503e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.566904e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.106872e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.281853e-05
- `obs_conditioned_streaming_steady_total_a`: 5.732567e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.520804e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.146559e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.722114e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.033711e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.566904e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.401645e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.394911e-06
- `obs_disabled_clock_running_reset_total_a`: 4.608497e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.573401e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.177760e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.935741e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.067526e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.566904e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.556681e-05
- `obs_disabled_clock_running_startup_combinational_w`: 6.104313e-06
- `obs_disabled_clock_running_startup_total_a`: 4.767882e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.571473e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.176540e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.928651e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.067530e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.566904e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.561364e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.864571e-06
- `obs_disabled_clock_running_steady_total_a`: 4.762039e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.534589e-04
- `obs_raw_streaming_reset_internal_w`: 1.151991e-04
- `obs_raw_streaming_reset_switching_w`: 3.805644e-05
- `obs_raw_streaming_reset_leakage_w`: 2.033711e-07
- `obs_raw_streaming_reset_clock_w`: 5.566904e-05
- `obs_raw_streaming_reset_sequential_w`: 9.405825e-05
- `obs_raw_streaming_reset_combinational_w`: 3.731593e-06
- `obs_raw_streaming_reset_total_a`: 4.650270e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.771310e-04
- `obs_raw_streaming_startup_internal_w`: 1.288967e-04
- `obs_raw_streaming_startup_switching_w`: 4.802315e-05
- `obs_raw_streaming_startup_leakage_w`: 2.111363e-07
- `obs_raw_streaming_startup_clock_w`: 5.566904e-05
- `obs_raw_streaming_startup_sequential_w`: 1.038743e-04
- `obs_raw_streaming_startup_combinational_w`: 1.758769e-05
- `obs_raw_streaming_startup_total_a`: 5.367606e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.900768e-04
- `obs_raw_streaming_steady_internal_w`: 1.365646e-04
- `obs_raw_streaming_steady_switching_w`: 5.329632e-05
- `obs_raw_streaming_steady_leakage_w`: 2.159377e-07
- `obs_raw_streaming_steady_clock_w`: 5.566904e-05
- `obs_raw_streaming_steady_sequential_w`: 1.106449e-04
- `obs_raw_streaming_steady_combinational_w`: 2.376289e-05
- `obs_raw_streaming_steady_total_a`: 5.759903e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty tt_025C_3v30 --rc max --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (tt_025C_3v30, interconnect `max`).
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
