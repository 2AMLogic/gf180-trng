---
record: 2026-11-09-digital-sta-activity-08
date: 2026-11-09T21:57:34Z
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
  spef_sha256: 97f429d60b3fdbc36a6827178c7a08f5784799ee2f2d87e028a2838a2444c469
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
  path: sim/records/raw/2026-11-09-digital-sta-activity-08/
  files:
    - uniform.tcl  sha256:b86d1474d719125856ae1c6189128a027ad7e00d00df7c6d9f1d89f1e9f4a321
    - uniform.log  sha256:eb3e20f0fce2c9de31436f6d0478cf67b5f0dbd2a90ae8571347eabf4b0ac34f
    - observed.tcl  sha256:587b2b7a6832dc7ad5c01a0670432d772d1f73987c648ed910794b2476b0d610
    - observed.log  sha256:668017a204ee2408ebe19de2ba07db85624c436c186eaaf7031ad7f560b8c035
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 8.8s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    173.17 |     77.96 |      0.21 |    251.35 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    114.98 |     36.53 |      0.20 |    151.71 | 0.604 | 5143 / 0 |
| alarm-gated | startup | 1040 |    127.88 |     45.46 |      0.21 |    173.55 | 0.690 | 5143 / 0 |
| alarm-gated | steady | 1024 |    124.26 |     42.71 |      0.21 |    167.18 | 0.665 | 5143 / 0 |
| backpressure | reset | 8 |    114.93 |     36.42 |      0.20 |    151.55 | 0.603 | 5143 / 0 |
| backpressure | startup | 1040 |    128.15 |     45.61 |      0.21 |    173.98 | 0.692 | 5143 / 0 |
| backpressure | steady | 1024 |    135.77 |     50.64 |      0.22 |    186.62 | 0.742 | 5143 / 0 |
| conditioned-streaming | reset | 8 |    114.97 |     36.51 |      0.20 |    151.69 | 0.603 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    128.45 |     45.84 |      0.21 |    174.50 | 0.694 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    135.91 |     50.82 |      0.21 |    186.94 | 0.744 | 5143 / 0 |
| disabled-clock-running | reset | 8 |    114.34 |     35.87 |      0.20 |    150.41 | 0.598 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |    117.45 |     37.93 |      0.21 |    155.59 | 0.619 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |    117.33 |     37.86 |      0.21 |    155.40 | 0.618 | 5143 / 0 |
| raw-streaming | reset | 8 |    114.88 |     36.67 |      0.20 |    151.76 | 0.604 | 5143 / 0 |
| raw-streaming | startup | 1040 |    128.57 |     46.29 |      0.21 |    175.07 | 0.697 | 5143 / 0 |
| raw-streaming | steady | 1024 |    136.22 |     51.38 |      0.22 |    187.81 | 0.747 | 5143 / 0 |

- `uniform_total_w`: 2.513480e-04
- `uniform_internal_w`: 1.731724e-04
- `uniform_switching_w`: 7.796100e-05
- `uniform_leakage_w`: 2.145970e-07
- `uniform_clock_w`: 5.418801e-05
- `uniform_sequential_w`: 1.311269e-04
- `uniform_combinational_w`: 6.603320e-05
- `uniform_total_a`: 7.616606e-05
- `obs_alarm_gated_reset_total_w`: 1.517121e-04
- `obs_alarm_gated_reset_internal_w`: 1.149825e-04
- `obs_alarm_gated_reset_switching_w`: 3.652626e-05
- `obs_alarm_gated_reset_leakage_w`: 2.033711e-07
- `obs_alarm_gated_reset_clock_w`: 5.418801e-05
- `obs_alarm_gated_reset_sequential_w`: 9.393296e-05
- `obs_alarm_gated_reset_combinational_w`: 3.591178e-06
- `obs_alarm_gated_reset_total_a`: 4.597336e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.735503e-04
- `obs_alarm_gated_startup_internal_w`: 1.278835e-04
- `obs_alarm_gated_startup_switching_w`: 4.545553e-05
- `obs_alarm_gated_startup_leakage_w`: 2.113422e-07
- `obs_alarm_gated_startup_clock_w`: 5.418801e-05
- `obs_alarm_gated_startup_sequential_w`: 1.034485e-04
- `obs_alarm_gated_startup_combinational_w`: 1.591385e-05
- `obs_alarm_gated_startup_total_a`: 5.259100e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.671841e-04
- `obs_alarm_gated_steady_internal_w`: 1.242606e-04
- `obs_alarm_gated_steady_switching_w`: 4.271248e-05
- `obs_alarm_gated_steady_leakage_w`: 2.109673e-07
- `obs_alarm_gated_steady_clock_w`: 5.418801e-05
- `obs_alarm_gated_steady_sequential_w`: 1.015814e-04
- `obs_alarm_gated_steady_combinational_w`: 1.141473e-05
- `obs_alarm_gated_steady_total_a`: 5.066185e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.515533e-04
- `obs_backpressure_reset_internal_w`: 1.149333e-04
- `obs_backpressure_reset_switching_w`: 3.641668e-05
- `obs_backpressure_reset_leakage_w`: 2.033711e-07
- `obs_backpressure_reset_clock_w`: 5.418801e-05
- `obs_backpressure_reset_sequential_w`: 9.392433e-05
- `obs_backpressure_reset_combinational_w`: 3.441000e-06
- `obs_backpressure_reset_total_a`: 4.592524e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.739753e-04
- `obs_backpressure_startup_internal_w`: 1.281501e-04
- `obs_backpressure_startup_switching_w`: 4.561356e-05
- `obs_backpressure_startup_leakage_w`: 2.116402e-07
- `obs_backpressure_startup_clock_w`: 5.418801e-05
- `obs_backpressure_startup_sequential_w`: 1.035560e-04
- `obs_backpressure_startup_combinational_w`: 1.623129e-05
- `obs_backpressure_startup_total_a`: 5.271979e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.866210e-04
- `obs_backpressure_steady_internal_w`: 1.357681e-04
- `obs_backpressure_steady_switching_w`: 5.063669e-05
- `obs_backpressure_steady_leakage_w`: 2.161484e-07
- `obs_backpressure_steady_clock_w`: 5.418801e-05
- `obs_backpressure_steady_sequential_w`: 1.103144e-04
- `obs_backpressure_steady_combinational_w`: 2.211859e-05
- `obs_backpressure_steady_total_a`: 5.655182e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.516881e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.149711e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.651363e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.033711e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.418801e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.393297e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.567125e-06
- `obs_conditioned_streaming_reset_total_a`: 4.596609e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.745013e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.284486e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.584163e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.109732e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.418801e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.038125e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.650073e-05
- `obs_conditioned_streaming_startup_total_a`: 5.287918e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.869436e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.359133e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.081530e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.149503e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.418801e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.103462e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.240942e-05
- `obs_conditioned_streaming_steady_total_a`: 5.664958e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.504148e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.143406e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.587081e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.033711e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.418801e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.388837e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.338436e-06
- `obs_disabled_clock_running_reset_total_a`: 4.558024e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.555921e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.174548e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.793049e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.067526e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.418801e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.541545e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.988615e-06
- `obs_disabled_clock_running_startup_total_a`: 4.714912e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.554037e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.173331e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.786382e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.067530e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.418801e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.546133e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.754375e-06
- `obs_disabled_clock_running_steady_total_a`: 4.709203e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.517569e-04
- `obs_raw_streaming_reset_internal_w`: 1.148831e-04
- `obs_raw_streaming_reset_switching_w`: 3.667048e-05
- `obs_raw_streaming_reset_leakage_w`: 2.033711e-07
- `obs_raw_streaming_reset_clock_w`: 5.418801e-05
- `obs_raw_streaming_reset_sequential_w`: 9.393015e-05
- `obs_raw_streaming_reset_combinational_w`: 3.638794e-06
- `obs_raw_streaming_reset_total_a`: 4.598694e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.750653e-04
- `obs_raw_streaming_startup_internal_w`: 1.285666e-04
- `obs_raw_streaming_startup_switching_w`: 4.628751e-05
- `obs_raw_streaming_startup_leakage_w`: 2.111363e-07
- `obs_raw_streaming_startup_clock_w`: 5.418801e-05
- `obs_raw_streaming_startup_sequential_w`: 1.036062e-04
- `obs_raw_streaming_startup_combinational_w`: 1.727111e-05
- `obs_raw_streaming_startup_total_a`: 5.305009e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.878145e-04
- `obs_raw_streaming_steady_internal_w`: 1.362208e-04
- `obs_raw_streaming_steady_switching_w`: 5.137777e-05
- `obs_raw_streaming_steady_leakage_w`: 2.159377e-07
- `obs_raw_streaming_steady_clock_w`: 5.418801e-05
- `obs_raw_streaming_steady_sequential_w`: 1.103057e-04
- `obs_raw_streaming_steady_combinational_w`: 2.332091e-05
- `obs_raw_streaming_steady_total_a`: 5.691348e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
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
