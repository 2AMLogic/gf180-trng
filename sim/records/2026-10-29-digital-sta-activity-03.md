---
record: 2026-10-29-digital-sta-activity-03
date: 2026-10-29T19:54:36Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00.lib (liberty corner ss_125C_3v00, sha256:d83917f827021eadb159f6011905bf20de632533b2953abba89266a88c2b24af)
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
  spef_sha256: 286f99f9cdf61cd2458bc5914e8ce69becfa1b98af7be2f1fb004ccb6faf6e32
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
  path: sim/records/raw/2026-10-29-digital-sta-activity-03/
  files:
    - uniform.tcl  sha256:7d2a1eeeb4250819b771b8e87dc64a723b4295f92d1be1c6e187e0027f0fc6c7
    - uniform.log  sha256:3ad9485531c69d14d0a2d6e2aa0294e82f93f7bc9168699d4aeb7c4c993bf6fd
    - observed.tcl  sha256:c04388fd668e9dfb48c21ee2ceb631cf9355b8c6d91ccdeb2937682974d6df73
    - observed.log  sha256:ed22e6010b66be70091d185bff74f4afa2a05080568c20971c150032ffbf1e28
    - activity-manifest.json  sha256:8983fe3617827472ef528e79e2d48d67cd5434898f0dc27ef0a5d711be0dce4d
wall_time: 9.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    144.18 |     67.76 |      2.14 |    214.08 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     96.08 |     31.60 |      2.13 |    129.80 | 0.606 | 5143 / 0 |
| alarm-gated | startup | 1040 |    106.78 |     39.33 |      2.14 |    148.25 | 0.692 | 5143 / 0 |
| alarm-gated | steady | 1024 |    103.80 |     36.95 |      2.14 |    142.89 | 0.667 | 5143 / 0 |
| backpressure | reset | 8 |     96.04 |     31.50 |      2.13 |    129.67 | 0.606 | 5143 / 0 |
| backpressure | startup | 1040 |    107.00 |     39.47 |      2.14 |    148.61 | 0.694 | 5143 / 0 |
| backpressure | steady | 1024 |    113.33 |     43.82 |      2.14 |    159.30 | 0.744 | 5143 / 0 |
| conditioned-streaming | reset | 8 |     96.07 |     31.59 |      2.13 |    129.78 | 0.606 | 5143 / 0 |
| conditioned-streaming | startup | 1040 |    107.25 |     39.66 |      2.14 |    149.05 | 0.696 | 5143 / 0 |
| conditioned-streaming | steady | 1024 |    113.45 |     43.98 |      2.14 |    159.57 | 0.745 | 5143 / 0 |
| disabled-clock-running | reset | 8 |     95.56 |     31.03 |      2.13 |    128.71 | 0.601 | 5143 / 0 |
| disabled-clock-running | startup | 1040 |     98.12 |     32.82 |      2.14 |    133.07 | 0.622 | 5143 / 0 |
| disabled-clock-running | steady | 1024 |     98.02 |     32.76 |      2.14 |    132.91 | 0.621 | 5143 / 0 |
| raw-streaming | reset | 8 |     96.00 |     31.73 |      2.13 |    129.85 | 0.607 | 5143 / 0 |
| raw-streaming | startup | 1040 |    107.34 |     40.06 |      2.14 |    149.54 | 0.699 | 5143 / 0 |
| raw-streaming | steady | 1024 |    113.70 |     44.47 |      2.14 |    160.32 | 0.749 | 5143 / 0 |

- `uniform_total_w`: 2.140769e-04
- `uniform_internal_w`: 1.441780e-04
- `uniform_switching_w`: 6.775873e-05
- `uniform_leakage_w`: 2.140195e-06
- `uniform_clock_w`: 4.684623e-05
- `uniform_sequential_w`: 1.107646e-04
- `uniform_combinational_w`: 5.646614e-05
- `uniform_total_a`: 7.135897e-05
- `obs_alarm_gated_reset_total_w`: 1.298016e-04
- `obs_alarm_gated_reset_internal_w`: 9.607546e-05
- `obs_alarm_gated_reset_switching_w`: 3.159582e-05
- `obs_alarm_gated_reset_leakage_w`: 2.130306e-06
- `obs_alarm_gated_reset_clock_w`: 4.684623e-05
- `obs_alarm_gated_reset_sequential_w`: 7.946457e-05
- `obs_alarm_gated_reset_combinational_w`: 3.490804e-06
- `obs_alarm_gated_reset_total_a`: 4.326720e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.482470e-04
- `obs_alarm_gated_startup_internal_w`: 1.067777e-04
- `obs_alarm_gated_startup_switching_w`: 3.933006e-05
- `obs_alarm_gated_startup_leakage_w`: 2.139170e-06
- `obs_alarm_gated_startup_clock_w`: 4.684623e-05
- `obs_alarm_gated_startup_sequential_w`: 8.751026e-05
- `obs_alarm_gated_startup_combinational_w`: 1.389036e-05
- `obs_alarm_gated_startup_total_a`: 4.941567e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.428871e-04
- `obs_alarm_gated_steady_internal_w`: 1.037962e-04
- `obs_alarm_gated_steady_switching_w`: 3.695214e-05
- `obs_alarm_gated_steady_leakage_w`: 2.138797e-06
- `obs_alarm_gated_steady_clock_w`: 4.684623e-05
- `obs_alarm_gated_steady_sequential_w`: 8.593145e-05
- `obs_alarm_gated_steady_combinational_w`: 1.010960e-05
- `obs_alarm_gated_steady_total_a`: 4.762903e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.143000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.296668e-04
- `obs_backpressure_reset_internal_w`: 9.603590e-05
- `obs_backpressure_reset_switching_w`: 3.150058e-05
- `obs_backpressure_reset_leakage_w`: 2.130306e-06
- `obs_backpressure_reset_clock_w`: 4.684623e-05
- `obs_backpressure_reset_sequential_w`: 7.945725e-05
- `obs_backpressure_reset_combinational_w`: 3.363331e-06
- `obs_backpressure_reset_total_a`: 4.322227e-05
- `obs_backpressure_reset_annotated_pins`: 5.143000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.486068e-04
- `obs_backpressure_startup_internal_w`: 1.070000e-04
- `obs_backpressure_startup_switching_w`: 3.946746e-05
- `obs_backpressure_startup_leakage_w`: 2.139317e-06
- `obs_backpressure_startup_clock_w`: 4.684623e-05
- `obs_backpressure_startup_sequential_w`: 8.760105e-05
- `obs_backpressure_startup_combinational_w`: 1.415946e-05
- `obs_backpressure_startup_total_a`: 4.953560e-05
- `obs_backpressure_startup_annotated_pins`: 5.143000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.592961e-04
- `obs_backpressure_steady_internal_w`: 1.133315e-04
- `obs_backpressure_steady_switching_w`: 4.382186e-05
- `obs_backpressure_steady_leakage_w`: 2.142745e-06
- `obs_backpressure_steady_clock_w`: 4.684623e-05
- `obs_backpressure_steady_sequential_w`: 9.328250e-05
- `obs_backpressure_steady_combinational_w`: 1.916753e-05
- `obs_backpressure_steady_total_a`: 5.309870e-05
- `obs_backpressure_steady_annotated_pins`: 5.143000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.297827e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.606679e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.158565e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.130306e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.684623e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.946458e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.471954e-06
- `obs_conditioned_streaming_reset_total_a`: 4.326090e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.490500e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.072465e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.966472e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.138804e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.684623e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.781766e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.438608e-05
- `obs_conditioned_streaming_startup_total_a`: 4.968333e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.595718e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.134511e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.397926e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.141460e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.684623e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.330943e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.941616e-05
- `obs_conditioned_streaming_steady_total_a`: 5.319060e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.143000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.287138e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.555647e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.102703e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.130306e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.684623e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.942734e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.440255e-06
- `obs_disabled_clock_running_reset_total_a`: 4.290460e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.330689e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.811809e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.281559e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.135238e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.684623e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.071360e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.509183e-06
- `obs_disabled_clock_running_startup_total_a`: 4.435630e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.329079e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.801629e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.275634e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.135238e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.684623e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.075276e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.308956e-06
- `obs_disabled_clock_running_steady_total_a`: 4.430263e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.143000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.298516e-04
- `obs_raw_streaming_reset_internal_w`: 9.599565e-05
- `obs_raw_streaming_reset_switching_w`: 3.172567e-05
- `obs_raw_streaming_reset_leakage_w`: 2.130306e-06
- `obs_raw_streaming_reset_clock_w`: 4.684623e-05
- `obs_raw_streaming_reset_sequential_w`: 7.946230e-05
- `obs_raw_streaming_reset_combinational_w`: 3.543101e-06
- `obs_raw_streaming_reset_total_a`: 4.328387e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.495392e-04
- `obs_raw_streaming_startup_internal_w`: 1.073408e-04
- `obs_raw_streaming_startup_switching_w`: 4.005965e-05
- `obs_raw_streaming_startup_leakage_w`: 2.138783e-06
- `obs_raw_streaming_startup_clock_w`: 4.684623e-05
- `obs_raw_streaming_startup_sequential_w`: 8.764334e-05
- `obs_raw_streaming_startup_combinational_w`: 1.504964e-05
- `obs_raw_streaming_startup_total_a`: 4.984640e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.143000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.603213e-04
- `obs_raw_streaming_steady_internal_w`: 1.137048e-04
- `obs_raw_streaming_steady_switching_w`: 4.447427e-05
- `obs_raw_streaming_steady_leakage_w`: 2.142267e-06
- `obs_raw_streaming_steady_clock_w`: 4.684623e-05
- `obs_raw_streaming_steady_sequential_w`: 9.327514e-05
- `obs_raw_streaming_steady_combinational_w`: 2.019993e-05
- `obs_raw_streaming_steady_total_a`: 5.344043e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.143000e+03
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
