---
record: 2026-11-13-digital-sta-activity-07
date: 2026-11-13T22:53:50Z
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
  - gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30.lib (liberty corner tt_025C_3v30, sha256:1157d0aa147dba75a214708197d7a046f970175d723cdec108025f6f06727c12)
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
  process: tt
  voltage: 3.30 V (nominal 3.3 V)
  temperature: 25
  liberty: gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30
  interconnect: min (OpenRCX rule deck)
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
  spef_sha256: 97613148e8a4dfcaa617ad12dba867170d289a561fcab58de7ef27c25a84e1ce
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
  path: sim/records/raw/2026-11-13-digital-sta-activity-07/
  files:
    - uniform.tcl  sha256:8ac712db10aadb480a02d7470227b3a0cb08a86ba05d2e980c42a8f78e813e20
    - uniform.log  sha256:3327e1f6cf547d3c0b7c0ab4ae5c23f9247784ab519a650d5750020010888638
    - observed.tcl  sha256:aaa1ede15d4c1b5f6c00bc1ae9e4a7e81ff0485214a9f91dc8c7f0b19e6648bb
    - observed.log  sha256:dfda2a50775d67049b439770eb7d04a8e374c4251e70968b5a5b82231fc84e42
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 9.1s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    171.55 |     76.02 |      0.21 |    247.79 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    114.55 |     36.59 |      0.20 |    151.35 | 0.611 | 5145 / 0 |
| alarm-gated | startup | 1040 |    127.38 |     44.90 |      0.21 |    172.49 | 0.696 | 5145 / 0 |
| alarm-gated | steady | 1024 |    124.12 |     42.48 |      0.21 |    166.82 | 0.673 | 5145 / 0 |
| backpressure | reset | 8 |    114.50 |     36.49 |      0.20 |    151.20 | 0.610 | 5145 / 0 |
| backpressure | startup | 1040 |    127.66 |     45.06 |      0.21 |    172.93 | 0.698 | 5145 / 0 |
| backpressure | steady | 1024 |    135.58 |     50.18 |      0.22 |    185.98 | 0.751 | 5145 / 0 |
| conditioned-streaming | reset | 8 |    114.54 |     36.57 |      0.20 |    151.31 | 0.611 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    127.99 |     45.30 |      0.21 |    173.49 | 0.700 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    135.73 |     50.34 |      0.21 |    186.29 | 0.752 | 5145 / 0 |
| disabled-clock-running | reset | 8 |    113.93 |     35.97 |      0.20 |    150.10 | 0.606 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |    116.86 |     37.59 |      0.21 |    154.66 | 0.624 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |    116.74 |     37.54 |      0.21 |    154.49 | 0.623 | 5145 / 0 |
| raw-streaming | reset | 8 |    114.45 |     36.70 |      0.20 |    151.36 | 0.611 | 5145 / 0 |
| raw-streaming | startup | 1040 |    128.05 |     45.70 |      0.21 |    173.96 | 0.702 | 5145 / 0 |
| raw-streaming | steady | 1024 |    136.01 |     50.87 |      0.22 |    187.09 | 0.755 | 5145 / 0 |

- `uniform_total_w`: 2.477886e-04
- `uniform_internal_w`: 1.715519e-04
- `uniform_switching_w`: 7.602225e-05
- `uniform_leakage_w`: 2.144338e-07
- `uniform_clock_w`: 5.373323e-05
- `uniform_sequential_w`: 1.308084e-04
- `uniform_combinational_w`: 6.324696e-05
- `uniform_total_a`: 7.508745e-05
- `obs_alarm_gated_reset_total_w`: 1.513458e-04
- `obs_alarm_gated_reset_internal_w`: 1.145541e-04
- `obs_alarm_gated_reset_switching_w`: 3.658852e-05
- `obs_alarm_gated_reset_leakage_w`: 2.031384e-07
- `obs_alarm_gated_reset_clock_w`: 5.373323e-05
- `obs_alarm_gated_reset_sequential_w`: 9.381947e-05
- `obs_alarm_gated_reset_combinational_w`: 3.793050e-06
- `obs_alarm_gated_reset_total_a`: 4.586236e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.724921e-04
- `obs_alarm_gated_startup_internal_w`: 1.273798e-04
- `obs_alarm_gated_startup_switching_w`: 4.490115e-05
- `obs_alarm_gated_startup_leakage_w`: 2.111742e-07
- `obs_alarm_gated_startup_clock_w`: 5.373323e-05
- `obs_alarm_gated_startup_sequential_w`: 1.032096e-04
- `obs_alarm_gated_startup_combinational_w`: 1.554925e-05
- `obs_alarm_gated_startup_total_a`: 5.227033e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.668157e-04
- `obs_alarm_gated_steady_internal_w`: 1.241228e-04
- `obs_alarm_gated_steady_switching_w`: 4.248202e-05
- `obs_alarm_gated_steady_leakage_w`: 2.108011e-07
- `obs_alarm_gated_steady_clock_w`: 5.373323e-05
- `obs_alarm_gated_steady_sequential_w`: 1.014083e-04
- `obs_alarm_gated_steady_combinational_w`: 1.167410e-05
- `obs_alarm_gated_steady_total_a`: 5.055021e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.511968e-04
- `obs_backpressure_reset_internal_w`: 1.145047e-04
- `obs_backpressure_reset_switching_w`: 3.648896e-05
- `obs_backpressure_reset_leakage_w`: 2.031384e-07
- `obs_backpressure_reset_clock_w`: 5.373323e-05
- `obs_backpressure_reset_sequential_w`: 9.381081e-05
- `obs_backpressure_reset_combinational_w`: 3.652758e-06
- `obs_backpressure_reset_total_a`: 4.581721e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.729272e-04
- `obs_backpressure_startup_internal_w`: 1.276600e-04
- `obs_backpressure_startup_switching_w`: 4.505572e-05
- `obs_backpressure_startup_leakage_w`: 2.114715e-07
- `obs_backpressure_startup_clock_w`: 5.373323e-05
- `obs_backpressure_startup_sequential_w`: 1.033177e-04
- `obs_backpressure_startup_combinational_w`: 1.587626e-05
- `obs_backpressure_startup_total_a`: 5.240218e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.859813e-04
- `obs_backpressure_steady_internal_w`: 1.355835e-04
- `obs_backpressure_steady_switching_w`: 5.018185e-05
- `obs_backpressure_steady_leakage_w`: 2.159677e-07
- `obs_backpressure_steady_clock_w`: 5.373323e-05
- `obs_backpressure_steady_sequential_w`: 1.100560e-04
- `obs_backpressure_steady_combinational_w`: 2.219203e-05
- `obs_backpressure_steady_total_a`: 5.635797e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.513121e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.145427e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.656625e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.031384e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.373323e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.381947e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.759367e-06
- `obs_conditioned_streaming_reset_total_a`: 4.585215e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.734940e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.279869e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.529629e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.108036e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.373323e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.035720e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.618871e-05
- `obs_conditioned_streaming_startup_total_a`: 5.257394e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.862912e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.357324e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.034404e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.147684e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.373323e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.100868e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.247127e-05
- `obs_conditioned_streaming_steady_total_a`: 5.645188e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.501002e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.139314e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.596565e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.031384e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.373323e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.377496e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.592037e-06
- `obs_disabled_clock_running_reset_total_a`: 4.548491e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.546632e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.168638e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.759296e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.065109e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.373323e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.527300e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.656970e-06
- `obs_disabled_clock_running_startup_total_a`: 4.686764e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.544893e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.167421e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.754063e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.065113e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.373323e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.531888e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.437164e-06
- `obs_disabled_clock_running_steady_total_a`: 4.681494e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.513575e-04
- `obs_raw_streaming_reset_internal_w`: 1.144500e-04
- `obs_raw_streaming_reset_switching_w`: 3.670436e-05
- `obs_raw_streaming_reset_leakage_w`: 2.031384e-07
- `obs_raw_streaming_reset_clock_w`: 5.373323e-05
- `obs_raw_streaming_reset_sequential_w`: 9.381662e-05
- `obs_raw_streaming_reset_combinational_w`: 3.807636e-06
- `obs_raw_streaming_reset_total_a`: 4.586591e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.739647e-04
- `obs_raw_streaming_startup_internal_w`: 1.280520e-04
- `obs_raw_streaming_startup_switching_w`: 4.570174e-05
- `obs_raw_streaming_startup_leakage_w`: 2.109694e-07
- `obs_raw_streaming_startup_clock_w`: 5.373323e-05
- `obs_raw_streaming_startup_sequential_w`: 1.033682e-04
- `obs_raw_streaming_startup_combinational_w`: 1.686321e-05
- `obs_raw_streaming_startup_total_a`: 5.271658e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.870892e-04
- `obs_raw_streaming_steady_internal_w`: 1.360075e-04
- `obs_raw_streaming_steady_switching_w`: 5.086597e-05
- `obs_raw_streaming_steady_leakage_w`: 2.157574e-07
- `obs_raw_streaming_steady_clock_w`: 5.373323e-05
- `obs_raw_streaming_steady_sequential_w`: 1.100443e-04
- `obs_raw_streaming_steady_combinational_w`: 2.331169e-05
- `obs_raw_streaming_steady_total_a`: 5.669370e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty tt_025C_3v30 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (tt_025C_3v30, interconnect `min`).
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
