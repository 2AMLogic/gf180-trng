---
record: 2026-10-29-digital-sta-activity-15
date: 2026-10-29T19:56:27Z
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
repo_commit: 16fd09fb792db7bf363afd70ec8f8370e1c2d90b-dirty

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
  spef_sha256: 539fdbf5b9f78bd73fdef54392b393241aca71e5d0737b393fe219916ca90f94
  spef_bytes: 1661196
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
  path: sim/records/raw/2026-10-29-digital-sta-activity-15/
  files:
    - uniform.tcl  sha256:e9fdd14e5062d6073226d8b7df09831b505896e8dabd051bb8b0837a39b245e1
    - uniform.log  sha256:7d8fffe4dca892030dd68ccce3698b5f7989c996df48ee99c03fecceb5054f25
    - observed.tcl  sha256:b24611b37d950c1e821b4748d2739c7dd7cb934248447437cda3f2fc2fe8adb8
    - observed.log  sha256:a41717751eb5324f049b9d5ccade51ef92f772f937f64457f1e6ad1fdfdf9735
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 9.5s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    213.55 |     96.62 |      0.25 |    310.42 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    141.35 |     45.16 |      0.24 |    186.75 | 0.602 | 5143 / 0 |
| alarm-gated | startup | 1040 |    157.21 |     56.17 |      0.25 |    213.63 | 0.688 | 5143 / 0 |
| alarm-gated | steady | 1024 |    152.69 |     52.80 |      0.25 |    205.73 | 0.663 | 5143 / 0 |
| backpressure | reset | 8 |    141.29 |     45.03 |      0.24 |    186.55 | 0.601 | 5143 / 0 |
| backpressure | startup | 1040 |    157.54 |     56.37 |      0.25 |    214.16 | 0.690 | 5143 / 0 |
| backpressure | steady | 1024 |    166.95 |     62.56 |      0.25 |    229.76 | 0.740 | 5143 / 0 |
| conditioned-streaming | reset | 8 |    141.33 |     45.15 |      0.24 |    186.72 | 0.601 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    157.91 |     56.65 |      0.25 |    214.81 | 0.692 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    167.13 |     62.79 |      0.25 |    230.17 | 0.741 | 5143 / 0 |
| disabled-clock-running | reset | 8 |    140.53 |     44.35 |      0.24 |    185.12 | 0.596 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |    144.41 |     46.89 |      0.24 |    191.54 | 0.617 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |    144.26 |     46.80 |      0.24 |    191.30 | 0.616 | 5143 / 0 |
| raw-streaming | reset | 8 |    141.22 |     45.34 |      0.24 |    186.80 | 0.602 | 5143 / 0 |
| raw-streaming | startup | 1040 |    158.07 |     57.21 |      0.25 |    215.53 | 0.694 | 5143 / 0 |
| raw-streaming | steady | 1024 |    167.52 |     63.49 |      0.25 |    231.26 | 0.745 | 5143 / 0 |

- `uniform_total_w`: 3.104238e-04
- `uniform_internal_w`: 2.135516e-04
- `uniform_switching_w`: 9.662168e-05
- `uniform_leakage_w`: 2.504850e-07
- `uniform_clock_w`: 6.895854e-05
- `uniform_sequential_w`: 1.588232e-04
- `uniform_combinational_w`: 8.264212e-05
- `uniform_total_a`: 8.622883e-05
- `obs_alarm_gated_reset_total_w`: 1.867477e-04
- `obs_alarm_gated_reset_internal_w`: 1.413463e-04
- `obs_alarm_gated_reset_switching_w`: 4.516176e-05
- `obs_alarm_gated_reset_leakage_w`: 2.396281e-07
- `obs_alarm_gated_reset_clock_w`: 6.895854e-05
- `obs_alarm_gated_reset_sequential_w`: 1.133305e-04
- `obs_alarm_gated_reset_combinational_w`: 4.458579e-06
- `obs_alarm_gated_reset_total_a`: 5.187436e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.136345e-04
- `obs_alarm_gated_startup_internal_w`: 1.572141e-04
- `obs_alarm_gated_startup_switching_w`: 5.617349e-05
- `obs_alarm_gated_startup_leakage_w`: 2.469438e-07
- `obs_alarm_gated_startup_clock_w`: 6.895854e-05
- `obs_alarm_gated_startup_sequential_w`: 1.249726e-04
- `obs_alarm_gated_startup_combinational_w`: 1.970352e-05
- `obs_alarm_gated_startup_total_a`: 5.934292e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.057330e-04
- `obs_alarm_gated_steady_internal_w`: 1.526865e-04
- `obs_alarm_gated_steady_switching_w`: 5.279997e-05
- `obs_alarm_gated_steady_leakage_w`: 2.465043e-07
- `obs_alarm_gated_steady_clock_w`: 6.895854e-05
- `obs_alarm_gated_steady_sequential_w`: 1.226863e-04
- `obs_alarm_gated_steady_combinational_w`: 1.408823e-05
- `obs_alarm_gated_steady_total_a`: 5.714806e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.865542e-04
- `obs_backpressure_reset_internal_w`: 1.412873e-04
- `obs_backpressure_reset_switching_w`: 4.502728e-05
- `obs_backpressure_reset_leakage_w`: 2.396281e-07
- `obs_backpressure_reset_clock_w`: 6.895854e-05
- `obs_backpressure_reset_sequential_w`: 1.133204e-04
- `obs_backpressure_reset_combinational_w`: 4.275219e-06
- `obs_backpressure_reset_total_a`: 5.182061e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.141568e-04
- `obs_backpressure_startup_internal_w`: 1.575396e-04
- `obs_backpressure_startup_switching_w`: 5.636985e-05
- `obs_backpressure_startup_leakage_w`: 2.472493e-07
- `obs_backpressure_startup_clock_w`: 6.895854e-05
- `obs_backpressure_startup_sequential_w`: 1.251025e-04
- `obs_backpressure_startup_combinational_w`: 2.009586e-05
- `obs_backpressure_startup_total_a`: 5.948800e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.297613e-04
- `obs_backpressure_steady_internal_w`: 1.669471e-04
- `obs_backpressure_steady_switching_w`: 6.256237e-05
- `obs_backpressure_steady_leakage_w`: 2.518242e-07
- `obs_backpressure_steady_clock_w`: 6.895854e-05
- `obs_backpressure_steady_sequential_w`: 1.334135e-04
- `obs_backpressure_steady_combinational_w`: 2.738916e-05
- `obs_backpressure_steady_total_a`: 6.382258e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.867198e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.413324e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.514774e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.396281e-07
- `obs_conditioned_streaming_reset_clock_w`: 6.895854e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.133305e-04
- `obs_conditioned_streaming_reset_combinational_w`: 4.430644e-06
- `obs_conditioned_streaming_reset_total_a`: 5.186661e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.148090e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.579106e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.665184e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.466174e-07
- `obs_conditioned_streaming_startup_clock_w`: 6.895854e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.254217e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.042904e-05
- `obs_conditioned_streaming_startup_total_a`: 5.966917e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.301697e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.671320e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.278716e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.505825e-07
- `obs_conditioned_streaming_steady_clock_w`: 6.895854e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.334582e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.775296e-05
- `obs_conditioned_streaming_steady_total_a`: 6.393603e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.851226e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.405342e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.434886e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.396281e-07
- `obs_disabled_clock_running_reset_clock_w`: 6.895854e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.132765e-04
- `obs_disabled_clock_running_reset_combinational_w`: 2.887555e-06
- `obs_disabled_clock_running_reset_total_a`: 5.142294e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.915370e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.444068e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.688801e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.422249e-07
- `obs_disabled_clock_running_startup_clock_w`: 6.895854e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.151386e-04
- `obs_disabled_clock_running_startup_combinational_w`: 7.439873e-06
- `obs_disabled_clock_running_startup_total_a`: 5.320472e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.913025e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.442568e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.680350e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.422247e-07
- `obs_disabled_clock_running_steady_clock_w`: 6.895854e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.151944e-04
- `obs_disabled_clock_running_steady_combinational_w`: 7.149549e-06
- `obs_disabled_clock_running_steady_total_a`: 5.313958e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.867994e-04
- `obs_raw_streaming_reset_internal_w`: 1.412168e-04
- `obs_raw_streaming_reset_switching_w`: 4.534295e-05
- `obs_raw_streaming_reset_leakage_w`: 2.396281e-07
- `obs_raw_streaming_reset_clock_w`: 6.895854e-05
- `obs_raw_streaming_reset_sequential_w`: 1.133269e-04
- `obs_raw_streaming_reset_combinational_w`: 4.513951e-06
- `obs_raw_streaming_reset_total_a`: 5.188872e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.155321e-04
- `obs_raw_streaming_startup_internal_w`: 1.580715e-04
- `obs_raw_streaming_startup_switching_w`: 5.721387e-05
- `obs_raw_streaming_startup_leakage_w`: 2.467104e-07
- `obs_raw_streaming_startup_clock_w`: 6.895854e-05
- `obs_raw_streaming_startup_sequential_w`: 1.251644e-04
- `obs_raw_streaming_startup_combinational_w`: 2.140926e-05
- `obs_raw_streaming_startup_total_a`: 5.987003e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.312619e-04
- `obs_raw_streaming_steady_internal_w`: 1.675192e-04
- `obs_raw_streaming_steady_switching_w`: 6.349113e-05
- `obs_raw_streaming_steady_leakage_w`: 2.516184e-07
- `obs_raw_streaming_steady_clock_w`: 6.895854e-05
- `obs_raw_streaming_steady_sequential_w`: 1.334042e-04
- `obs_raw_streaming_steady_combinational_w`: 2.889918e-05
- `obs_raw_streaming_steady_total_a`: 6.423942e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
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
