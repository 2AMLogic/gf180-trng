---
record: 2026-11-13-digital-sta-activity-01
date: 2026-11-13T22:52:55Z
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
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ss_125C_3v00
  interconnect: min (OpenRCX rule deck)
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
  spef_sha256: 67795da8171e260b9adc5a792c6a55b888ce94303421b5bcb6e7a967a8a0ed87
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
  path: sim/records/raw/2026-11-13-digital-sta-activity-01/
  files:
    - uniform.tcl  sha256:69edbb876808ab94fcc965b5149d470c2129c36a53aab7df0416f26254cba168
    - uniform.log  sha256:9fb138fb8296c38936fd5ff245a41b979dd43f10001b64cd60238c7797579b8a
    - observed.tcl  sha256:16938d478964b632463df69b4c3b1a5cdde081a6de2aecebfd07f84d8a3603a4
    - observed.log  sha256:33c604845e66a18d53d9a5bcc5c3b57ab2adf14477f8b9db36188856bc3148d5
    - activity-manifest.json  sha256:a55ce345a1158b742cc6d76264e76890f193af270a8fed06ea51db6ee7de6c55
wall_time: 9.2s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    142.85 |     63.53 |      2.15 |    208.53 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     95.71 |     30.52 |      2.14 |    128.37 | 0.616 | 5145 / 0 |
| alarm-gated | startup | 1040 |    106.35 |     37.48 |      2.15 |    145.98 | 0.700 | 5145 / 0 |
| alarm-gated | steady | 1024 |    103.66 |     35.45 |      2.15 |    141.26 | 0.677 | 5145 / 0 |
| backpressure | reset | 8 |     95.67 |     30.44 |      2.14 |    128.25 | 0.615 | 5145 / 0 |
| backpressure | startup | 1040 |    106.58 |     37.61 |      2.15 |    146.34 | 0.702 | 5145 / 0 |
| backpressure | steady | 1024 |    113.16 |     41.91 |      2.15 |    157.21 | 0.754 | 5145 / 0 |
| conditioned-streaming | reset | 8 |     95.70 |     30.50 |      2.14 |    128.34 | 0.615 | 5145 / 0 |
| conditioned-streaming | startup | 1040 |    106.85 |     37.81 |      2.15 |    146.81 | 0.704 | 5145 / 0 |
| conditioned-streaming | steady | 1024 |    113.28 |     42.04 |      2.15 |    157.47 | 0.755 | 5145 / 0 |
| disabled-clock-running | reset | 8 |     95.20 |     30.00 |      2.14 |    127.35 | 0.611 | 5145 / 0 |
| disabled-clock-running | startup | 1040 |     97.61 |     31.37 |      2.14 |    131.13 | 0.629 | 5145 / 0 |
| disabled-clock-running | steady | 1024 |     97.51 |     31.33 |      2.14 |    130.98 | 0.628 | 5145 / 0 |
| raw-streaming | reset | 8 |     95.63 |     30.62 |      2.14 |    128.39 | 0.616 | 5145 / 0 |
| raw-streaming | startup | 1040 |    106.90 |     38.15 |      2.15 |    147.20 | 0.706 | 5145 / 0 |
| raw-streaming | steady | 1024 |    113.51 |     42.48 |      2.15 |    158.14 | 0.758 | 5145 / 0 |

- `uniform_total_w`: 2.085268e-04
- `uniform_internal_w`: 1.428536e-04
- `uniform_switching_w`: 6.352529e-05
- `uniform_leakage_w`: 2.147984e-06
- `uniform_clock_w`: 4.541671e-05
- `uniform_sequential_w`: 1.102024e-04
- `uniform_combinational_w`: 5.290777e-05
- `uniform_total_a`: 6.950893e-05
- `obs_alarm_gated_reset_total_w`: 1.283691e-04
- `obs_alarm_gated_reset_internal_w`: 9.570802e-05
- `obs_alarm_gated_reset_switching_w`: 3.052306e-05
- `obs_alarm_gated_reset_leakage_w`: 2.137999e-06
- `obs_alarm_gated_reset_clock_w`: 4.541671e-05
- `obs_alarm_gated_reset_sequential_w`: 7.935700e-05
- `obs_alarm_gated_reset_combinational_w`: 3.595434e-06
- `obs_alarm_gated_reset_total_a`: 4.278970e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.459790e-04
- `obs_alarm_gated_startup_internal_w`: 1.063492e-04
- `obs_alarm_gated_startup_switching_w`: 3.748280e-05
- `obs_alarm_gated_startup_leakage_w`: 2.146937e-06
- `obs_alarm_gated_startup_clock_w`: 4.541671e-05
- `obs_alarm_gated_startup_sequential_w`: 8.718529e-05
- `obs_alarm_gated_startup_combinational_w`: 1.337689e-05
- `obs_alarm_gated_startup_total_a`: 4.865967e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.412571e-04
- `obs_alarm_gated_steady_internal_w`: 1.036581e-04
- `obs_alarm_gated_steady_switching_w`: 3.545241e-05
- `obs_alarm_gated_steady_leakage_w`: 2.146606e-06
- `obs_alarm_gated_steady_clock_w`: 4.541671e-05
- `obs_alarm_gated_steady_sequential_w`: 8.568190e-05
- `obs_alarm_gated_steady_combinational_w`: 1.015861e-05
- `obs_alarm_gated_steady_total_a`: 4.708570e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.145000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.282454e-04
- `obs_backpressure_reset_internal_w`: 9.566833e-05
- `obs_backpressure_reset_switching_w`: 3.043909e-05
- `obs_backpressure_reset_leakage_w`: 2.137999e-06
- `obs_backpressure_reset_clock_w`: 4.541671e-05
- `obs_backpressure_reset_sequential_w`: 7.934964e-05
- `obs_backpressure_reset_combinational_w`: 3.479137e-06
- `obs_backpressure_reset_total_a`: 4.274847e-05
- `obs_backpressure_reset_annotated_pins`: 5.145000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.463421e-04
- `obs_backpressure_startup_internal_w`: 1.065830e-04
- `obs_backpressure_startup_switching_w`: 3.761207e-05
- `obs_backpressure_startup_leakage_w`: 2.147085e-06
- `obs_backpressure_startup_clock_w`: 4.541671e-05
- `obs_backpressure_startup_sequential_w`: 8.727577e-05
- `obs_backpressure_startup_combinational_w`: 1.364956e-05
- `obs_backpressure_startup_total_a`: 4.878070e-05
- `obs_backpressure_startup_annotated_pins`: 5.145000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.572148e-04
- `obs_backpressure_steady_internal_w`: 1.131583e-04
- `obs_backpressure_steady_switching_w`: 4.190602e-05
- `obs_backpressure_steady_leakage_w`: 2.150514e-06
- `obs_backpressure_steady_clock_w`: 4.541671e-05
- `obs_backpressure_steady_sequential_w`: 9.288474e-05
- `obs_backpressure_steady_combinational_w`: 1.891342e-05
- `obs_backpressure_steady_total_a`: 5.240493e-05
- `obs_backpressure_steady_annotated_pins`: 5.145000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.283416e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.569930e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.050426e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.137999e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.541671e-05
- `obs_conditioned_streaming_reset_sequential_w`: 7.935699e-05
- `obs_conditioned_streaming_reset_combinational_w`: 3.567936e-06
- `obs_conditioned_streaming_reset_total_a`: 4.278053e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.468125e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.068528e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.781313e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.146571e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.541671e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.748661e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.390910e-05
- `obs_conditioned_streaming_startup_total_a`: 4.893750e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.574717e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.132809e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.204153e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.149249e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.541671e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.290915e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.914592e-05
- `obs_conditioned_streaming_steady_total_a`: 5.249057e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.273458e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.520483e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.000300e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.137999e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.541671e-05
- `obs_disabled_clock_running_reset_sequential_w`: 7.931983e-05
- `obs_disabled_clock_running_reset_combinational_w`: 2.609344e-06
- `obs_disabled_clock_running_reset_total_a`: 4.244860e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.311271e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.761436e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.136976e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.142986e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.541671e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.056382e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.146644e-06
- `obs_disabled_clock_running_startup_total_a`: 4.370903e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.309812e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.751238e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.132585e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.142986e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.541671e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.060219e-05
- `obs_disabled_clock_running_steady_combinational_w`: 4.962353e-06
- `obs_disabled_clock_running_steady_total_a`: 4.366040e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.145000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.283854e-04
- `obs_raw_streaming_reset_internal_w`: 9.562574e-05
- `obs_raw_streaming_reset_switching_w`: 3.062170e-05
- `obs_raw_streaming_reset_leakage_w`: 2.137999e-06
- `obs_raw_streaming_reset_clock_w`: 4.541671e-05
- `obs_raw_streaming_reset_sequential_w`: 7.935473e-05
- `obs_raw_streaming_reset_combinational_w`: 3.614086e-06
- `obs_raw_streaming_reset_total_a`: 4.279513e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.472034e-04
- `obs_raw_streaming_startup_internal_w`: 1.069049e-04
- `obs_raw_streaming_startup_switching_w`: 3.815191e-05
- `obs_raw_streaming_startup_leakage_w`: 2.146540e-06
- `obs_raw_streaming_startup_clock_w`: 4.541671e-05
- `obs_raw_streaming_startup_sequential_w`: 8.731787e-05
- `obs_raw_streaming_startup_combinational_w`: 1.446878e-05
- `obs_raw_streaming_startup_total_a`: 4.906780e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.581378e-04
- `obs_raw_streaming_steady_internal_w`: 1.135094e-04
- `obs_raw_streaming_steady_switching_w`: 4.247835e-05
- `obs_raw_streaming_steady_leakage_w`: 2.150023e-06
- `obs_raw_streaming_steady_clock_w`: 4.541671e-05
- `obs_raw_streaming_steady_sequential_w`: 9.287478e-05
- `obs_raw_streaming_steady_combinational_w`: 1.984629e-05
- `obs_raw_streaming_steady_total_a`: 5.271260e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.145000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty ss_125C_3v00 --rc min --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (ss_125C_3v00, interconnect `min`).
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
