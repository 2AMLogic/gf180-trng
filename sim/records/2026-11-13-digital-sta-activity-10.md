---
record: 2026-11-13-digital-sta-activity-10
date: 2026-11-13T22:54:16Z
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
  - rules.openrcx.gf180mcuD.min (OpenRCX interconnect corner min, sha256:5cf275c985ffd49096407d22891910fea34aff5a915db8a5b9a7c1e04b737e00)
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
  interconnect: min (OpenRCX rule deck)
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
  spef_sha256: c4692dd9beac450bf44784099934e975d6f0c451f2e546f8126dd411e7548cc8
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
  path: sim/records/raw/2026-11-13-digital-sta-activity-10/
  files:
    - uniform.tcl  sha256:071000dff09a730c460d8521395371f113f7ab02c22a24a7f404a3200545dada
    - uniform.log  sha256:d86aecab7c2ad1014c833dacb33ec8a79d6f1fa0d3ece3be32dee6bf011cb119
    - observed.tcl  sha256:2b83007c6976a490d21a524ed3ae0e60f4c0622fb6531ed071c1f9c4dfdeabb5
    - observed.log  sha256:503de3cad086917f782d96fbd03cac7bc7f4435be07fda4afd73d5320a476374
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 8.6s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    230.42 |     90.96 |      7.58 |    328.96 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    151.37 |     43.84 |      7.00 |    202.21 | 0.615 | 5145 / 0 |
| alarm-gated | startup | 1040 |    169.16 |     53.78 |      7.65 |    230.60 | 0.701 | 5145 / 0 |
| alarm-gated | steady | 1024 |    164.60 |     50.89 |      7.64 |    223.12 | 0.678 | 5145 / 0 |
| backpressure | reset | 8 |    151.30 |     43.72 |      7.00 |    202.02 | 0.614 | 5145 / 0 |
| backpressure | startup | 1040 |    169.55 |     53.97 |      7.62 |    231.14 | 0.703 | 5145 / 0 |
| backpressure | steady | 1024 |    180.57 |     60.09 |      7.94 |    248.60 | 0.756 | 5145 / 0 |
| conditioned-streaming | reset | 8 |    151.35 |     43.81 |      7.00 |    202.17 | 0.615 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    170.01 |     54.25 |      7.63 |    231.89 | 0.705 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    180.79 |     60.29 |      7.85 |    248.93 | 0.757 | 5145 / 0 |
| disabled-clock-running | reset | 8 |    150.48 |     43.09 |      7.00 |    200.57 | 0.610 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |    154.68 |     45.04 |      7.34 |    207.05 | 0.629 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |    154.51 |     44.98 |      7.34 |    206.82 | 0.629 | 5145 / 0 |
| raw-streaming | reset | 8 |    151.22 |     43.98 |      7.00 |    202.20 | 0.615 | 5145 / 0 |
| raw-streaming | startup | 1040 |    170.11 |     54.74 |      7.58 |    232.42 | 0.707 | 5145 / 0 |
| raw-streaming | steady | 1024 |    181.17 |     60.91 |      7.86 |    249.93 | 0.760 | 5145 / 0 |

- `uniform_total_w`: 3.289587e-04
- `uniform_internal_w`: 2.304212e-04
- `uniform_switching_w`: 9.095835e-05
- `uniform_leakage_w`: 7.579158e-06
- `uniform_clock_w`: 7.281662e-05
- `uniform_sequential_w`: 1.703282e-04
- `uniform_combinational_w`: 8.581372e-05
- `uniform_total_a`: 9.137742e-05
- `obs_alarm_gated_reset_total_w`: 2.022085e-04
- `obs_alarm_gated_reset_internal_w`: 1.513686e-04
- `obs_alarm_gated_reset_switching_w`: 4.383768e-05
- `obs_alarm_gated_reset_leakage_w`: 7.002188e-06
- `obs_alarm_gated_reset_clock_w`: 7.281662e-05
- `obs_alarm_gated_reset_sequential_w`: 1.218182e-04
- `obs_alarm_gated_reset_combinational_w`: 7.573733e-06
- `obs_alarm_gated_reset_total_a`: 5.616903e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.305979e-04
- `obs_alarm_gated_startup_internal_w`: 1.691624e-04
- `obs_alarm_gated_startup_switching_w`: 5.378155e-05
- `obs_alarm_gated_startup_leakage_w`: 7.653976e-06
- `obs_alarm_gated_startup_clock_w`: 7.281662e-05
- `obs_alarm_gated_startup_sequential_w`: 1.342426e-04
- `obs_alarm_gated_startup_combinational_w`: 2.353876e-05
- `obs_alarm_gated_startup_total_a`: 6.405497e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.231194e-04
- `obs_alarm_gated_steady_internal_w`: 1.645968e-04
- `obs_alarm_gated_steady_switching_w`: 5.088719e-05
- `obs_alarm_gated_steady_leakage_w`: 7.635392e-06
- `obs_alarm_gated_steady_clock_w`: 7.281662e-05
- `obs_alarm_gated_steady_sequential_w`: 1.319059e-04
- `obs_alarm_gated_steady_combinational_w`: 1.839675e-05
- `obs_alarm_gated_steady_total_a`: 6.197761e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.020244e-04
- `obs_backpressure_reset_internal_w`: 1.513037e-04
- `obs_backpressure_reset_switching_w`: 4.371857e-05
- `obs_backpressure_reset_leakage_w`: 7.002188e-06
- `obs_backpressure_reset_clock_w`: 7.281662e-05
- `obs_backpressure_reset_sequential_w`: 1.218073e-04
- `obs_backpressure_reset_combinational_w`: 7.400623e-06
- `obs_backpressure_reset_total_a`: 5.611789e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.311381e-04
- `obs_backpressure_startup_internal_w`: 1.695490e-04
- `obs_backpressure_startup_switching_w`: 5.396661e-05
- `obs_backpressure_startup_leakage_w`: 7.622532e-06
- `obs_backpressure_startup_clock_w`: 7.281662e-05
- `obs_backpressure_startup_sequential_w`: 1.343882e-04
- `obs_backpressure_startup_combinational_w`: 2.393334e-05
- `obs_backpressure_startup_total_a`: 6.420503e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.486004e-04
- `obs_backpressure_steady_internal_w`: 1.805713e-04
- `obs_backpressure_steady_switching_w`: 6.009209e-05
- `obs_backpressure_steady_leakage_w`: 7.936968e-06
- `obs_backpressure_steady_clock_w`: 7.281662e-05
- `obs_backpressure_steady_sequential_w`: 1.433462e-04
- `obs_backpressure_steady_combinational_w`: 3.243738e-05
- `obs_backpressure_steady_total_a`: 6.905567e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.021670e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.513539e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.381093e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.002188e-06
- `obs_conditioned_streaming_reset_clock_w`: 7.281662e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.218182e-04
- `obs_conditioned_streaming_reset_combinational_w`: 7.532205e-06
- `obs_conditioned_streaming_reset_total_a`: 5.615750e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.318944e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.700059e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.425431e-05
- `obs_conditioned_streaming_startup_leakage_w`: 7.634230e-06
- `obs_conditioned_streaming_startup_clock_w`: 7.281662e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.347027e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.437520e-05
- `obs_conditioned_streaming_startup_total_a`: 6.441511e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.489259e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.807872e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.028577e-05
- `obs_conditioned_streaming_steady_leakage_w`: 7.852875e-06
- `obs_conditioned_streaming_steady_clock_w`: 7.281662e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.433713e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.273787e-05
- `obs_conditioned_streaming_steady_total_a`: 6.914608e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 2.005745e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.504808e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.309151e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.002188e-06
- `obs_disabled_clock_running_reset_clock_w`: 7.281662e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.217584e-04
- `obs_disabled_clock_running_reset_combinational_w`: 5.999540e-06
- `obs_disabled_clock_running_reset_total_a`: 5.571514e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.070493e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.546751e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.503889e-05
- `obs_disabled_clock_running_startup_leakage_w`: 7.335305e-06
- `obs_disabled_clock_running_startup_clock_w`: 7.281662e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.239660e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.026658e-05
- `obs_disabled_clock_running_startup_total_a`: 5.751369e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.068172e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.545050e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.497634e-05
- `obs_disabled_clock_running_steady_leakage_w`: 7.335824e-06
- `obs_disabled_clock_running_steady_clock_w`: 7.281662e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.240206e-04
- `obs_disabled_clock_running_steady_combinational_w`: 9.979782e-06
- `obs_disabled_clock_running_steady_total_a`: 5.744922e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.021970e-04
- `obs_raw_streaming_reset_internal_w`: 1.512198e-04
- `obs_raw_streaming_reset_switching_w`: 4.397503e-05
- `obs_raw_streaming_reset_leakage_w`: 7.002188e-06
- `obs_raw_streaming_reset_clock_w`: 7.281662e-05
- `obs_raw_streaming_reset_sequential_w`: 1.218138e-04
- `obs_raw_streaming_reset_combinational_w`: 7.566718e-06
- `obs_raw_streaming_reset_total_a`: 5.616583e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.324204e-04
- `obs_raw_streaming_startup_internal_w`: 1.701058e-04
- `obs_raw_streaming_startup_switching_w`: 5.473844e-05
- `obs_raw_streaming_startup_leakage_w`: 7.576150e-06
- `obs_raw_streaming_startup_clock_w`: 7.281662e-05
- `obs_raw_streaming_startup_sequential_w`: 1.344452e-04
- `obs_raw_streaming_startup_combinational_w`: 2.515873e-05
- `obs_raw_streaming_startup_total_a`: 6.456122e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.499323e-04
- `obs_raw_streaming_steady_internal_w`: 1.811680e-04
- `obs_raw_streaming_steady_switching_w`: 6.090919e-05
- `obs_raw_streaming_steady_leakage_w`: 7.855031e-06
- `obs_raw_streaming_steady_clock_w`: 7.281662e-05
- `obs_raw_streaming_steady_sequential_w`: 1.433273e-04
- `obs_raw_streaming_steady_combinational_w`: 3.378831e-05
- `obs_raw_streaming_steady_total_a`: 6.942564e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ff_125C_3v60 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ff_125C_3v60, interconnect `min`).
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
