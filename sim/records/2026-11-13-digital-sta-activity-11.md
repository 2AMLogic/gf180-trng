---
record: 2026-11-13-digital-sta-activity-11
date: 2026-11-13T22:54:25Z
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
  - gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60.lib (liberty corner ff_125C_3v60, sha256:b64f32b397097f2046e66ce7f9a4aaffc9a80c4c0bfd3c77385727268e81a016)
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
  process: ff
  voltage: 3.60 V (nominal 3.3 V, +9.1%)
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60
  interconnect: nom (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature 125, nom_voltage 3.6 (read from the deck)

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
  spef_sha256: 40544f567abcce4daf638b90951b1b00a99b4a641d8ddd7b6a6aaaf54377b069
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
  path: sim/records/raw/2026-11-13-digital-sta-activity-11/
  files:
    - uniform.tcl  sha256:d32dd05e50428c0ebeb7e52b13c7fd99a4c1377ac36611a9faed8884afa08910
    - uniform.log  sha256:addadc061a7af72561b26db5609c99a3a96ef75dcd89d5feda2119c625d726f2
    - observed.tcl  sha256:f8f29e8992c06c697be3ce37db43c294932acb0a7a11f02ff70726fd71861610
    - observed.log  sha256:17213fce95309e692115c68d3ac48d6d6d73c87b3a0473179bc32a24d38234d2
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 8.7s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    231.34 |     94.14 |      7.58 |    333.06 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    152.11 |     45.26 |      7.00 |    204.38 | 0.614 | 5145 / 0 |
| alarm-gated | startup | 1040 |    169.92 |     55.48 |      7.65 |    233.06 | 0.700 | 5145 / 0 |
| alarm-gated | steady | 1024 |    165.35 |     52.53 |      7.64 |    225.51 | 0.677 | 5145 / 0 |
| backpressure | reset | 8 |    152.05 |     45.14 |      7.00 |    204.19 | 0.613 | 5145 / 0 |
| backpressure | startup | 1040 |    170.31 |     55.68 |      7.62 |    233.61 | 0.701 | 5145 / 0 |
| backpressure | steady | 1024 |    181.36 |     62.00 |      7.94 |    251.31 | 0.755 | 5145 / 0 |
| conditioned-streaming | reset | 8 |    152.10 |     45.24 |      7.00 |    204.34 | 0.614 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    170.77 |     55.97 |      7.63 |    234.37 | 0.704 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    181.58 |     62.21 |      7.85 |    251.64 | 0.756 | 5145 / 0 |
| disabled-clock-running | reset | 8 |    151.22 |     44.50 |      7.00 |    202.72 | 0.609 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |    155.42 |     46.47 |      7.34 |    209.23 | 0.628 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |    155.25 |     46.41 |      7.34 |    208.99 | 0.627 | 5145 / 0 |
| raw-streaming | reset | 8 |    151.96 |     45.41 |      7.00 |    204.37 | 0.614 | 5145 / 0 |
| raw-streaming | startup | 1040 |    170.87 |     56.48 |      7.58 |    234.93 | 0.705 | 5145 / 0 |
| raw-streaming | steady | 1024 |    181.96 |     62.86 |      7.86 |    252.68 | 0.759 | 5145 / 0 |

- `uniform_total_w`: 3.330596e-04
- `uniform_internal_w`: 2.313403e-04
- `uniform_switching_w`: 9.414005e-05
- `uniform_leakage_w`: 7.579158e-06
- `uniform_clock_w`: 7.457520e-05
- `uniform_sequential_w`: 1.710205e-04
- `uniform_combinational_w`: 8.746398e-05
- `uniform_total_a`: 9.251656e-05
- `obs_alarm_gated_reset_total_w`: 2.043790e-04
- `obs_alarm_gated_reset_internal_w`: 1.521120e-04
- `obs_alarm_gated_reset_switching_w`: 4.526474e-05
- `obs_alarm_gated_reset_leakage_w`: 7.002188e-06
- `obs_alarm_gated_reset_clock_w`: 7.457520e-05
- `obs_alarm_gated_reset_sequential_w`: 1.221402e-04
- `obs_alarm_gated_reset_combinational_w`: 7.663577e-06
- `obs_alarm_gated_reset_total_a`: 5.677194e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.330597e-04
- `obs_alarm_gated_startup_internal_w`: 1.699214e-04
- `obs_alarm_gated_startup_switching_w`: 5.548427e-05
- `obs_alarm_gated_startup_leakage_w`: 7.653976e-06
- `obs_alarm_gated_startup_clock_w`: 7.457520e-05
- `obs_alarm_gated_startup_sequential_w`: 1.346966e-04
- `obs_alarm_gated_startup_combinational_w`: 2.378793e-05
- `obs_alarm_gated_startup_total_a`: 6.473881e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.255120e-04
- `obs_alarm_gated_steady_internal_w`: 1.653491e-04
- `obs_alarm_gated_steady_switching_w`: 5.252747e-05
- `obs_alarm_gated_steady_leakage_w`: 7.635392e-06
- `obs_alarm_gated_steady_clock_w`: 7.457520e-05
- `obs_alarm_gated_steady_sequential_w`: 1.323436e-04
- `obs_alarm_gated_steady_combinational_w`: 1.859314e-05
- `obs_alarm_gated_steady_total_a`: 6.264222e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.041928e-04
- `obs_backpressure_reset_internal_w`: 1.520471e-04
- `obs_backpressure_reset_switching_w`: 4.514352e-05
- `obs_backpressure_reset_leakage_w`: 7.002188e-06
- `obs_backpressure_reset_clock_w`: 7.457520e-05
- `obs_backpressure_reset_sequential_w`: 1.221292e-04
- `obs_backpressure_reset_combinational_w`: 7.488384e-06
- `obs_backpressure_reset_total_a`: 5.672022e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.336058e-04
- `obs_backpressure_startup_internal_w`: 1.703081e-04
- `obs_backpressure_startup_switching_w`: 5.567519e-05
- `obs_backpressure_startup_leakage_w`: 7.622532e-06
- `obs_backpressure_startup_clock_w`: 7.457520e-05
- `obs_backpressure_startup_sequential_w`: 1.348434e-04
- `obs_backpressure_startup_combinational_w`: 2.418719e-05
- `obs_backpressure_startup_total_a`: 6.489050e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.513055e-04
- `obs_backpressure_steady_internal_w`: 1.813639e-04
- `obs_backpressure_steady_switching_w`: 6.200466e-05
- `obs_backpressure_steady_leakage_w`: 7.936968e-06
- `obs_backpressure_steady_clock_w`: 7.457520e-05
- `obs_backpressure_steady_sequential_w`: 1.438829e-04
- `obs_backpressure_steady_combinational_w`: 3.284754e-05
- `obs_backpressure_steady_total_a`: 6.980708e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.043374e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.520972e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.523799e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.002188e-06
- `obs_conditioned_streaming_reset_clock_w`: 7.457520e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.221402e-04
- `obs_conditioned_streaming_reset_combinational_w`: 7.622019e-06
- `obs_conditioned_streaming_reset_total_a`: 5.676039e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.343722e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.707655e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.597247e-05
- `obs_conditioned_streaming_startup_leakage_w`: 7.634230e-06
- `obs_conditioned_streaming_startup_clock_w`: 7.457520e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.351628e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.463432e-05
- `obs_conditioned_streaming_startup_total_a`: 6.510339e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.516400e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.815804e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.220677e-05
- `obs_conditioned_streaming_steady_leakage_w`: 7.852875e-06
- `obs_conditioned_streaming_steady_clock_w`: 7.457520e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.439101e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.315460e-05
- `obs_conditioned_streaming_steady_total_a`: 6.990000e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 2.027177e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.512205e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.449506e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.002188e-06
- `obs_disabled_clock_running_reset_clock_w`: 7.457520e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.220802e-04
- `obs_disabled_clock_running_reset_combinational_w`: 6.062238e-06
- `obs_disabled_clock_running_reset_total_a`: 5.631047e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.092281e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.554191e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.647368e-05
- `obs_disabled_clock_running_startup_leakage_w`: 7.335305e-06
- `obs_disabled_clock_running_startup_clock_w`: 7.457520e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.243085e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.034446e-05
- `obs_disabled_clock_running_startup_total_a`: 5.811892e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.089935e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.552489e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.640870e-05
- `obs_disabled_clock_running_steady_leakage_w`: 7.335824e-06
- `obs_disabled_clock_running_steady_clock_w`: 7.457520e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.243641e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.005419e-05
- `obs_disabled_clock_running_steady_total_a`: 5.805375e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.043724e-04
- `obs_raw_streaming_reset_internal_w`: 1.519612e-04
- `obs_raw_streaming_reset_switching_w`: 4.540895e-05
- `obs_raw_streaming_reset_leakage_w`: 7.002188e-06
- `obs_raw_streaming_reset_clock_w`: 7.457520e-05
- `obs_raw_streaming_reset_sequential_w`: 1.221357e-04
- `obs_raw_streaming_reset_combinational_w`: 7.661427e-06
- `obs_raw_streaming_reset_total_a`: 5.677011e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.349256e-04
- `obs_raw_streaming_startup_internal_w`: 1.708677e-04
- `obs_raw_streaming_startup_switching_w`: 5.648177e-05
- `obs_raw_streaming_startup_leakage_w`: 7.576150e-06
- `obs_raw_streaming_startup_clock_w`: 7.457520e-05
- `obs_raw_streaming_startup_sequential_w`: 1.349010e-04
- `obs_raw_streaming_startup_combinational_w`: 2.544953e-05
- `obs_raw_streaming_startup_total_a`: 6.525711e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.526753e-04
- `obs_raw_streaming_steady_internal_w`: 1.819631e-04
- `obs_raw_streaming_steady_switching_w`: 6.285719e-05
- `obs_raw_streaming_steady_leakage_w`: 7.855031e-06
- `obs_raw_streaming_steady_clock_w`: 7.457520e-05
- `obs_raw_streaming_steady_sequential_w`: 1.438638e-04
- `obs_raw_streaming_steady_combinational_w`: 3.423627e-05
- `obs_raw_streaming_steady_total_a`: 7.018758e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_125C_3v60 --rc nom --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_125C_3v60, interconnect `nom`).
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
