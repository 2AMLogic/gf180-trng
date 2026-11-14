---
record: 2026-11-13-digital-sta-activity-04
date: 2026-11-13T22:53:23Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: 89e8f60a83222b44213d3c89a059db389405b475
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha 49a084e95789ff1acbd953235cf0612b7701ef36).
repo_commit: e783bb4f7336f4422aa26902c7003f638bccd0a7-dirty

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
  spef_sha256: 43faf75274b6d7c53d63ef01fa7fcd35c4bbd28ed2bd7679603817a56bff2405
  spef_bytes: 1665643
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
      vcd_sha256: 0afb5fb92799a03d3444e0f27eb960c2ee5ea62fff79b5a3a5094558e2df1b4b
      vcd_bytes: 17698640
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1424/1424
      xz_events: 4931
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: a4094cb39c49b436bd01e672cded18bb2da8efe3791a0abfc0fe57e9ea40ebe6
      vcd_bytes: 19126901
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 5074
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: a0eb1a5723562558fb1acfcf8d8c0701c6e1cfe4e7270ce8aebbb72dd962965d
      vcd_bytes: 19173873
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 4809
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: ea20e05c09b17231d8eeee57c82747b30afe2abf409e7db8ff7f17a08e0cabfc
      vcd_bytes: 13485290
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 2222
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: 700215612e809607908e9865420a657acd559ed311b8ef2c862483deac89df1b
      vcd_bytes: 19322913
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1424/1424
      xz_events: 5153
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-11-13-digital-sta-activity-04/
  files:
    - uniform.tcl  sha256:d1fbb94ba7f4015ff412b55c6b7aa578f59b2755fed882533742f6f87f5aef1c
    - uniform.log  sha256:0d61110a445708a677e482833f9cf3721a9c0369b6db2a8b6912f76515da92ad
    - observed.tcl  sha256:5195ce96592a2e7c3eb9aab7c8aef5e52e98e0ea7d8bff73811f117b8359427d
    - observed.log  sha256:e57065259197a3a98e2e0b114768e2457ca0e7fbae38e358b083727a3924a00f
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 9.0s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    132.75 |     61.99 |      0.17 |    194.91 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     90.05 |     29.80 |      0.16 |    120.01 | 0.616 | 5145 / 0 |
| alarm-gated | startup | 1040 |     99.67 |     36.56 |      0.17 |    136.40 | 0.700 | 5145 / 0 |
| alarm-gated | steady | 1024 |     97.25 |     34.58 |      0.17 |    132.00 | 0.677 | 5145 / 0 |
| backpressure | reset | 8 |     90.01 |     29.72 |      0.16 |    119.89 | 0.615 | 5145 / 0 |
| backpressure | startup | 1040 |     99.88 |     36.68 |      0.17 |    136.73 | 0.702 | 5145 / 0 |
| backpressure | steady | 1024 |    105.85 |     40.87 |      0.17 |    146.89 | 0.754 | 5145 / 0 |
| conditioned-streaming | reset | 8 |     90.04 |     29.78 |      0.16 |    119.98 | 0.616 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    100.13 |     36.88 |      0.17 |    137.18 | 0.704 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    105.97 |     41.00 |      0.17 |    147.13 | 0.755 | 5145 / 0 |
| disabled-clock-running | reset | 8 |     89.59 |     29.29 |      0.16 |    119.05 | 0.611 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |     91.73 |     30.60 |      0.16 |    122.50 | 0.628 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |     91.64 |     30.56 |      0.16 |    122.36 | 0.628 | 5145 / 0 |
| raw-streaming | reset | 8 |     89.97 |     29.89 |      0.16 |    120.03 | 0.616 | 5145 / 0 |
| raw-streaming | startup | 1040 |    100.17 |     37.21 |      0.17 |    137.55 | 0.706 | 5145 / 0 |
| raw-streaming | steady | 1024 |    106.17 |     41.42 |      0.17 |    147.76 | 0.758 | 5145 / 0 |

- `uniform_total_w`: 1.949070e-04
- `uniform_internal_w`: 1.327479e-04
- `uniform_switching_w`: 6.199089e-05
- `uniform_leakage_w`: 1.682266e-07
- `uniform_clock_w`: 4.150324e-05
- `uniform_sequential_w`: 1.043638e-04
- `uniform_combinational_w`: 4.903978e-05
- `uniform_total_a`: 6.496900e-05
- `obs_alarm_gated_reset_total_w`: 1.200090e-04
- `obs_alarm_gated_reset_internal_w`: 9.004593e-05
- `obs_alarm_gated_reset_switching_w`: 2.980047e-05
- `obs_alarm_gated_reset_leakage_w`: 1.625760e-07
- `obs_alarm_gated_reset_clock_w`: 4.150324e-05
- `obs_alarm_gated_reset_sequential_w`: 7.548957e-05
- `obs_alarm_gated_reset_combinational_w`: 3.016169e-06
- `obs_alarm_gated_reset_total_a`: 4.000300e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.363961e-04
- `obs_alarm_gated_startup_internal_w`: 9.967161e-05
- `obs_alarm_gated_startup_switching_w`: 3.655732e-05
- `obs_alarm_gated_startup_leakage_w`: 1.671869e-07
- `obs_alarm_gated_startup_clock_w`: 4.150324e-05
- `obs_alarm_gated_startup_sequential_w`: 8.289015e-05
- `obs_alarm_gated_startup_combinational_w`: 1.200281e-05
- `obs_alarm_gated_startup_total_a`: 4.546537e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.319991e-04
- `obs_alarm_gated_steady_internal_w`: 9.724725e-05
- `obs_alarm_gated_steady_switching_w`: 3.458497e-05
- `obs_alarm_gated_steady_leakage_w`: 1.668848e-07
- `obs_alarm_gated_steady_clock_w`: 4.150324e-05
- `obs_alarm_gated_steady_sequential_w`: 8.147580e-05
- `obs_alarm_gated_steady_combinational_w`: 9.020144e-06
- `obs_alarm_gated_steady_total_a`: 4.399970e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.198895e-04
- `obs_backpressure_reset_internal_w`: 9.000768e-05
- `obs_backpressure_reset_switching_w`: 2.971928e-05
- `obs_backpressure_reset_leakage_w`: 1.625760e-07
- `obs_backpressure_reset_clock_w`: 4.150324e-05
- `obs_backpressure_reset_sequential_w`: 7.548266e-05
- `obs_backpressure_reset_combinational_w`: 2.903647e-06
- `obs_backpressure_reset_total_a`: 3.996317e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.367324e-04
- `obs_backpressure_startup_internal_w`: 9.988197e-05
- `obs_backpressure_startup_switching_w`: 3.668312e-05
- `obs_backpressure_startup_leakage_w`: 1.673350e-07
- `obs_backpressure_startup_clock_w`: 4.150324e-05
- `obs_backpressure_startup_sequential_w`: 8.297338e-05
- `obs_backpressure_startup_combinational_w`: 1.225584e-05
- `obs_backpressure_startup_total_a`: 4.557747e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.468885e-04
- `obs_backpressure_steady_internal_w`: 1.058537e-04
- `obs_backpressure_steady_switching_w`: 4.086524e-05
- `obs_backpressure_steady_leakage_w`: 1.694936e-07
- `obs_backpressure_steady_clock_w`: 4.150324e-05
- `obs_backpressure_steady_sequential_w`: 8.822472e-05
- `obs_backpressure_steady_combinational_w`: 1.716050e-05
- `obs_backpressure_steady_total_a`: 4.896283e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.199823e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.003741e-05
- `obs_conditioned_streaming_reset_switching_w`: 2.978234e-05
- `obs_conditioned_streaming_reset_leakage_w`: 1.625760e-07
- `obs_conditioned_streaming_reset_clock_w`: 4.150324e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.548957e-05
- `obs_conditioned_streaming_reset_combinational_w`: 2.989518e-06
- `obs_conditioned_streaming_reset_total_a`: 3.999410e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.371776e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.001313e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.687920e-05
- `obs_conditioned_streaming_startup_leakage_w`: 1.670489e-07
- `obs_conditioned_streaming_startup_clock_w`: 4.150324e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.317803e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.249633e-05
- `obs_conditioned_streaming_startup_total_a`: 4.572587e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.471334e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.059670e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.099761e-05
- `obs_conditioned_streaming_steady_leakage_w`: 1.688380e-07
- `obs_conditioned_streaming_steady_clock_w`: 4.150324e-05
- `obs_conditioned_streaming_steady_sequential_w`: 8.825355e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.737671e-05
- `obs_conditioned_streaming_steady_total_a`: 4.904447e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.190467e-04
- `obs_disabled_clock_running_reset_internal_w`: 8.959144e-05
- `obs_disabled_clock_running_reset_switching_w`: 2.929270e-05
- `obs_disabled_clock_running_reset_leakage_w`: 1.625760e-07
- `obs_disabled_clock_running_reset_clock_w`: 4.150324e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.545514e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.088339e-06
- `obs_disabled_clock_running_reset_total_a`: 3.968223e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.224960e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.172767e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.060358e-05
- `obs_disabled_clock_running_startup_leakage_w`: 1.647496e-07
- `obs_disabled_clock_running_startup_clock_w`: 4.150324e-05
- `obs_disabled_clock_running_startup_sequential_w`: 7.663609e-05
- `obs_disabled_clock_running_startup_combinational_w`: 4.356732e-06
- `obs_disabled_clock_running_startup_total_a`: 4.083200e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.223622e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.163655e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.056091e-05
- `obs_disabled_clock_running_steady_leakage_w`: 1.647490e-07
- `obs_disabled_clock_running_steady_clock_w`: 4.150324e-05
- `obs_disabled_clock_running_steady_sequential_w`: 7.667358e-05
- `obs_disabled_clock_running_steady_combinational_w`: 4.185471e-06
- `obs_disabled_clock_running_steady_total_a`: 4.078740e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.200271e-04
- `obs_raw_streaming_reset_internal_w`: 8.996970e-05
- `obs_raw_streaming_reset_switching_w`: 2.989485e-05
- `obs_raw_streaming_reset_leakage_w`: 1.625760e-07
- `obs_raw_streaming_reset_clock_w`: 4.150324e-05
- `obs_raw_streaming_reset_sequential_w`: 7.548758e-05
- `obs_raw_streaming_reset_combinational_w`: 3.036319e-06
- `obs_raw_streaming_reset_total_a`: 4.000903e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.375500e-04
- `obs_raw_streaming_startup_internal_w`: 1.001719e-04
- `obs_raw_streaming_startup_switching_w`: 3.721103e-05
- `obs_raw_streaming_startup_leakage_w`: 1.670639e-07
- `obs_raw_streaming_startup_clock_w`: 4.150324e-05
- `obs_raw_streaming_startup_sequential_w`: 8.301553e-05
- `obs_raw_streaming_startup_combinational_w`: 1.303126e-05
- `obs_raw_streaming_startup_total_a`: 4.585000e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.477638e-04
- `obs_raw_streaming_steady_internal_w`: 1.061700e-04
- `obs_raw_streaming_steady_switching_w`: 4.142445e-05
- `obs_raw_streaming_steady_leakage_w`: 1.693965e-07
- `obs_raw_streaming_steady_clock_w`: 4.150324e-05
- `obs_raw_streaming_steady_sequential_w`: 8.821760e-05
- `obs_raw_streaming_steady_combinational_w`: 1.804305e-05
- `obs_raw_streaming_steady_total_a`: 4.925460e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
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
