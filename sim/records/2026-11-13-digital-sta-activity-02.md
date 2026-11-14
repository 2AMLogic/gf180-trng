---
record: 2026-11-13-digital-sta-activity-02
date: 2026-11-13T22:53:04Z
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
  spef_sha256: 5dbe2b18bfc8b67a566f02fcda4340158e3f59722331337f7a92e3335a07c607
  spef_bytes: 1671005
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
  path: sim/records/raw/2026-11-13-digital-sta-activity-02/
  files:
    - uniform.tcl  sha256:6fb0a3fd03bfa7fc18d5bdd74b1649255375e4ad456203c16b9971970a6bef08
    - uniform.log  sha256:a73dc8deb5783241dbf9626d19bb2b7279993a41f727d39865fadec9804156bd
    - observed.tcl  sha256:249d5976dfee42f3dea47d8dc84c693745b904303dc015c1cd1bc78e5f52c83a
    - observed.log  sha256:297423bfafac4f894a8a39234c315fa007e4ffb6f03086cc0640a6edc673a53d
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 9.3s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    143.02 |     65.73 |      2.15 |    210.90 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     95.84 |     31.51 |      2.14 |    129.49 | 0.614 | 5145 / 0 |
| alarm-gated | startup | 1040 |    106.48 |     38.67 |      2.15 |    147.29 | 0.698 | 5145 / 0 |
| alarm-gated | steady | 1024 |    103.79 |     36.59 |      2.15 |    142.52 | 0.676 | 5145 / 0 |
| backpressure | reset | 8 |     95.80 |     31.43 |      2.14 |    129.36 | 0.613 | 5145 / 0 |
| backpressure | startup | 1040 |    106.71 |     38.80 |      2.15 |    147.66 | 0.700 | 5145 / 0 |
| backpressure | steady | 1024 |    113.29 |     43.23 |      2.15 |    158.68 | 0.752 | 5145 / 0 |
| conditioned-streaming | reset | 8 |     95.83 |     31.50 |      2.14 |    129.46 | 0.614 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    106.98 |     39.01 |      2.15 |    148.14 | 0.702 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    113.42 |     43.38 |      2.15 |    158.94 | 0.754 | 5145 / 0 |
| disabled-clock-running | reset | 8 |     95.33 |     30.98 |      2.14 |    128.45 | 0.609 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |     97.74 |     32.37 |      2.14 |    132.25 | 0.627 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |     97.64 |     32.32 |      2.14 |    132.10 | 0.626 | 5145 / 0 |
| raw-streaming | reset | 8 |     95.75 |     31.62 |      2.14 |    129.51 | 0.614 | 5145 / 0 |
| raw-streaming | startup | 1040 |    107.04 |     39.36 |      2.15 |    148.54 | 0.704 | 5145 / 0 |
| raw-streaming | steady | 1024 |    113.64 |     43.83 |      2.15 |    159.63 | 0.757 | 5145 / 0 |

- `uniform_total_w`: 2.108981e-04
- `uniform_internal_w`: 1.430153e-04
- `uniform_switching_w`: 6.573489e-05
- `uniform_leakage_w`: 2.147984e-06
- `uniform_clock_w`: 4.643010e-05
- `uniform_sequential_w`: 1.104971e-04
- `uniform_combinational_w`: 5.397082e-05
- `uniform_total_a`: 7.029937e-05
- `obs_alarm_gated_reset_total_w`: 1.294880e-04
- `obs_alarm_gated_reset_internal_w`: 9.583596e-05
- `obs_alarm_gated_reset_switching_w`: 3.151410e-05
- `obs_alarm_gated_reset_leakage_w`: 2.137999e-06
- `obs_alarm_gated_reset_clock_w`: 4.643010e-05
- `obs_alarm_gated_reset_sequential_w`: 7.940314e-05
- `obs_alarm_gated_reset_combinational_w`: 3.654731e-06
- `obs_alarm_gated_reset_total_a`: 4.316267e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.472909e-04
- `obs_alarm_gated_startup_internal_w`: 1.064788e-04
- `obs_alarm_gated_startup_switching_w`: 3.866520e-05
- `obs_alarm_gated_startup_leakage_w`: 2.146937e-06
- `obs_alarm_gated_startup_clock_w`: 4.643010e-05
- `obs_alarm_gated_startup_sequential_w`: 8.732140e-05
- `obs_alarm_gated_startup_combinational_w`: 1.353941e-05
- `obs_alarm_gated_startup_total_a`: 4.909697e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.425247e-04
- `obs_alarm_gated_steady_internal_w`: 1.037866e-04
- `obs_alarm_gated_steady_switching_w`: 3.659154e-05
- `obs_alarm_gated_steady_leakage_w`: 2.146606e-06
- `obs_alarm_gated_steady_clock_w`: 4.643010e-05
- `obs_alarm_gated_steady_sequential_w`: 8.580741e-05
- `obs_alarm_gated_steady_combinational_w`: 1.028721e-05
- `obs_alarm_gated_steady_total_a`: 4.750823e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.293629e-04
- `obs_backpressure_reset_internal_w`: 9.579628e-05
- `obs_backpressure_reset_switching_w`: 3.142866e-05
- `obs_backpressure_reset_leakage_w`: 2.137999e-06
- `obs_backpressure_reset_clock_w`: 4.643010e-05
- `obs_backpressure_reset_sequential_w`: 7.939578e-05
- `obs_backpressure_reset_combinational_w`: 3.536973e-06
- `obs_backpressure_reset_total_a`: 4.312097e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.476583e-04
- `obs_backpressure_startup_internal_w`: 1.067125e-04
- `obs_backpressure_startup_switching_w`: 3.879863e-05
- `obs_backpressure_startup_leakage_w`: 2.147085e-06
- `obs_backpressure_startup_clock_w`: 4.643010e-05
- `obs_backpressure_startup_sequential_w`: 8.741280e-05
- `obs_backpressure_startup_combinational_w`: 1.381530e-05
- `obs_backpressure_startup_total_a`: 4.921943e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.586780e-04
- `obs_backpressure_steady_internal_w`: 1.132932e-04
- `obs_backpressure_steady_switching_w`: 4.323430e-05
- `obs_backpressure_steady_leakage_w`: 2.150514e-06
- `obs_backpressure_steady_clock_w`: 4.643010e-05
- `obs_backpressure_steady_sequential_w`: 9.307389e-05
- `obs_backpressure_steady_combinational_w`: 1.917401e-05
- `obs_backpressure_steady_total_a`: 5.289267e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.294605e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.582725e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.149530e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.137999e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.643010e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.940314e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.627229e-06
- `obs_conditioned_streaming_reset_total_a`: 4.315350e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.481353e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.069824e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.900630e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.146571e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.643010e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.762696e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.407820e-05
- `obs_conditioned_streaming_startup_total_a`: 4.937843e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.589409e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.134160e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.337558e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.149249e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.643010e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.309981e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.941086e-05
- `obs_conditioned_streaming_steady_total_a`: 5.298030e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.284475e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.533182e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.097769e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.137999e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.643010e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.936595e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.651404e-06
- `obs_disabled_clock_running_reset_total_a`: 4.281583e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.322512e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.774206e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.236614e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.142986e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.643010e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.062302e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.197961e-06
- `obs_disabled_clock_running_startup_total_a`: 4.408373e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.321036e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.764000e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.232056e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.142986e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.643010e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.066212e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.011226e-06
- `obs_disabled_clock_running_steady_total_a`: 4.403453e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.295085e-04
- `obs_raw_streaming_reset_internal_w`: 9.575300e-05
- `obs_raw_streaming_reset_switching_w`: 3.161750e-05
- `obs_raw_streaming_reset_leakage_w`: 2.137999e-06
- `obs_raw_streaming_reset_clock_w`: 4.643010e-05
- `obs_raw_streaming_reset_sequential_w`: 7.940087e-05
- `obs_raw_streaming_reset_combinational_w`: 3.677488e-06
- `obs_raw_streaming_reset_total_a`: 4.316950e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.485443e-04
- `obs_raw_streaming_startup_internal_w`: 1.070352e-04
- `obs_raw_streaming_startup_switching_w`: 3.936255e-05
- `obs_raw_streaming_startup_leakage_w`: 2.146540e-06
- `obs_raw_streaming_startup_clock_w`: 4.643010e-05
- `obs_raw_streaming_startup_sequential_w`: 8.745530e-05
- `obs_raw_streaming_startup_combinational_w`: 1.465887e-05
- `obs_raw_streaming_startup_total_a`: 4.951477e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.596259e-04
- `obs_raw_streaming_steady_internal_w`: 1.136448e-04
- `obs_raw_streaming_steady_switching_w`: 4.383116e-05
- `obs_raw_streaming_steady_leakage_w`: 2.150023e-06
- `obs_raw_streaming_steady_clock_w`: 4.643010e-05
- `obs_raw_streaming_steady_sequential_w`: 9.306375e-05
- `obs_raw_streaming_steady_combinational_w`: 2.013217e-05
- `obs_raw_streaming_steady_total_a`: 5.320863e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
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
