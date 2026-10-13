---
record: 2026-10-10-digital-sta-activity-03
date: 2026-10-10T02:44:55Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: 8f13adca1f40260c48314a800b021eda212876f4
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha b16950323f54a4dd4de1dc5f89abc8565ab11b72).
repo_commit: d01212256aee65c9be3593221aded02dded2644f

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
  spef_sha256: 4965a986d7ae0c2e9ca201a84b8b78a82b9095d0064f9d8ae96fe18f7f599ec0
  spef_bytes: 1775752
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
      vcd_sha256: 4a33c9cf88e987f0ef819f9eb48a2a65ef24144150eaf5443a85cd973f6327d1
      vcd_bytes: 20199442
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1490/1490
      xz_events: 4272
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: f7f50e47e2354f5f0952f6bf411a0519d14ae1071847837f5a5d1ebf98fe7d22
      vcd_bytes: 21555986
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4289
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: a0e09fad484e70df0d364a6572e652af0e99e95f35051cc7d3e7b889cc77136f
      vcd_bytes: 21612178
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4168
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: d1259e79bcd8783392f642bc50703ff452608e0618f99694e80183970b262cc4
      vcd_bytes: 16158833
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 1798
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: f2e9b984f3a7f390094899a89512645de77cf3ce78e305fdfd35aa0818ae6227
      vcd_bytes: 21760619
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4488
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-10-10-digital-sta-activity-03/
  files:
    - uniform.tcl  sha256:e7b2901d6c2432534365fea6a4ea92ff6ca6113567da5a3b57622b574dff1ef0
    - uniform.log  sha256:bac4f9e4803c22761505e9511f91314c51d748370a88a71fc3d1ae2a99e06a39
    - observed.tcl  sha256:3308c480bd9825f5052f1a689deee61bb201ef7ff291b59ee0d194bd645411ae
    - observed.log  sha256:51a0dcb8af1f36c3b0904365151e7f20accaaded15862cc06da3ec0dec1e21f7
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 9.2s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    147.33 |     70.91 |      2.21 |    220.45 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |     96.20 |     32.06 |      2.20 |    130.46 | 0.592 | 5371 / 0 |
| alarm-gated | startup | 1040 |    105.31 |     38.80 |      2.21 |    146.32 | 0.664 | 5371 / 0 |
| alarm-gated | steady | 1024 |    102.52 |     36.39 |      2.21 |    141.12 | 0.640 | 5371 / 0 |
| backpressure | reset | 8 |     96.16 |     31.97 |      2.20 |    130.33 | 0.591 | 5371 / 0 |
| backpressure | startup | 1040 |    105.48 |     38.92 |      2.21 |    146.61 | 0.665 | 5371 / 0 |
| backpressure | steady | 1024 |    112.00 |     43.45 |      2.21 |    157.66 | 0.715 | 5371 / 0 |
| conditioned-streaming | reset | 8 |     96.19 |     32.04 |      2.20 |    130.43 | 0.592 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    105.65 |     39.12 |      2.21 |    146.98 | 0.667 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    112.08 |     43.57 |      2.21 |    157.86 | 0.716 | 5371 / 0 |
| disabled-clock-running | reset | 8 |     95.91 |     31.55 |      2.20 |    129.66 | 0.588 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |     98.19 |     32.60 |      2.20 |    133.00 | 0.603 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |     98.09 |     32.54 |      2.20 |    132.84 | 0.603 | 5371 / 0 |
| raw-streaming | reset | 8 |     96.25 |     32.24 |      2.20 |    130.69 | 0.593 | 5371 / 0 |
| raw-streaming | startup | 1040 |    105.93 |     39.58 |      2.21 |    147.73 | 0.670 | 5371 / 0 |
| raw-streaming | steady | 1024 |    112.41 |     44.08 |      2.21 |    158.70 | 0.720 | 5371 / 0 |

- `uniform_total_w`: 2.204461e-04
- `uniform_internal_w`: 1.473259e-04
- `uniform_switching_w`: 7.091141e-05
- `uniform_leakage_w`: 2.208865e-06
- `uniform_clock_w`: 4.602489e-05
- `uniform_sequential_w`: 1.144818e-04
- `uniform_combinational_w`: 5.993948e-05
- `uniform_total_a`: 7.348203e-05
- `obs_alarm_gated_reset_total_w`: 1.304598e-04
- `obs_alarm_gated_reset_internal_w`: 9.620111e-05
- `obs_alarm_gated_reset_switching_w`: 3.205997e-05
- `obs_alarm_gated_reset_leakage_w`: 2.198723e-06
- `obs_alarm_gated_reset_clock_w`: 4.602489e-05
- `obs_alarm_gated_reset_sequential_w`: 8.034173e-05
- `obs_alarm_gated_reset_combinational_w`: 4.093179e-06
- `obs_alarm_gated_reset_total_a`: 4.348660e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.463234e-04
- `obs_alarm_gated_startup_internal_w`: 1.053134e-04
- `obs_alarm_gated_startup_switching_w`: 3.880161e-05
- `obs_alarm_gated_startup_leakage_w`: 2.208328e-06
- `obs_alarm_gated_startup_clock_w`: 4.602489e-05
- `obs_alarm_gated_startup_sequential_w`: 8.755551e-05
- `obs_alarm_gated_startup_combinational_w`: 1.274293e-05
- `obs_alarm_gated_startup_total_a`: 4.877447e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.411199e-04
- `obs_alarm_gated_steady_internal_w`: 1.025197e-04
- `obs_alarm_gated_steady_switching_w`: 3.639247e-05
- `obs_alarm_gated_steady_leakage_w`: 2.207755e-06
- `obs_alarm_gated_steady_clock_w`: 4.602489e-05
- `obs_alarm_gated_steady_sequential_w`: 8.566494e-05
- `obs_alarm_gated_steady_combinational_w`: 9.430059e-06
- `obs_alarm_gated_steady_total_a`: 4.703997e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.303288e-04
- `obs_backpressure_reset_internal_w`: 9.616059e-05
- `obs_backpressure_reset_switching_w`: 3.196951e-05
- `obs_backpressure_reset_leakage_w`: 2.198723e-06
- `obs_backpressure_reset_clock_w`: 4.602489e-05
- `obs_backpressure_reset_sequential_w`: 8.033437e-05
- `obs_backpressure_reset_combinational_w`: 3.969547e-06
- `obs_backpressure_reset_total_a`: 4.344293e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.466076e-04
- `obs_backpressure_startup_internal_w`: 1.054777e-04
- `obs_backpressure_startup_switching_w`: 3.892127e-05
- `obs_backpressure_startup_leakage_w`: 2.208553e-06
- `obs_backpressure_startup_clock_w`: 4.602489e-05
- `obs_backpressure_startup_sequential_w`: 8.758484e-05
- `obs_backpressure_startup_combinational_w`: 1.299781e-05
- `obs_backpressure_startup_total_a`: 4.886920e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.576628e-04
- `obs_backpressure_steady_internal_w`: 1.120033e-04
- `obs_backpressure_steady_switching_w`: 4.344751e-05
- `obs_backpressure_steady_leakage_w`: 2.212008e-06
- `obs_backpressure_steady_clock_w`: 4.602489e-05
- `obs_backpressure_steady_sequential_w`: 9.314119e-05
- `obs_backpressure_steady_combinational_w`: 1.849677e-05
- `obs_backpressure_steady_total_a`: 5.255427e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.304285e-04
- `obs_conditioned_streaming_reset_internal_w`: 9.619241e-05
- `obs_conditioned_streaming_reset_switching_w`: 3.203738e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.198723e-06
- `obs_conditioned_streaming_reset_clock_w`: 4.602489e-05
- `obs_conditioned_streaming_reset_sequential_w`: 8.034172e-05
- `obs_conditioned_streaming_reset_combinational_w`: 4.061889e-06
- `obs_conditioned_streaming_reset_total_a`: 4.347617e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.469772e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.056478e-04
- `obs_conditioned_streaming_startup_switching_w`: 3.912136e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.207989e-06
- `obs_conditioned_streaming_startup_clock_w`: 4.602489e-05
- `obs_conditioned_streaming_startup_sequential_w`: 8.774313e-05
- `obs_conditioned_streaming_startup_combinational_w`: 1.320916e-05
- `obs_conditioned_streaming_startup_total_a`: 4.899240e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.578649e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.120819e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.357219e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.210763e-06
- `obs_conditioned_streaming_steady_clock_w`: 4.602489e-05
- `obs_conditioned_streaming_steady_sequential_w`: 9.312198e-05
- `obs_conditioned_streaming_steady_combinational_w`: 1.871803e-05
- `obs_conditioned_streaming_steady_total_a`: 5.262163e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.296626e-04
- `obs_disabled_clock_running_reset_internal_w`: 9.591039e-05
- `obs_disabled_clock_running_reset_switching_w`: 3.155344e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.198723e-06
- `obs_disabled_clock_running_reset_clock_w`: 4.602489e-05
- `obs_disabled_clock_running_reset_sequential_w`: 8.030696e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.330676e-06
- `obs_disabled_clock_running_reset_total_a`: 4.322087e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.329953e-04
- `obs_disabled_clock_running_startup_internal_w`: 9.819421e-05
- `obs_disabled_clock_running_startup_switching_w`: 3.259644e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_startup_clock_w`: 4.602489e-05
- `obs_disabled_clock_running_startup_sequential_w`: 8.157402e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.396366e-06
- `obs_disabled_clock_running_startup_total_a`: 4.433177e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.328357e-04
- `obs_disabled_clock_running_steady_internal_w`: 9.809072e-05
- `obs_disabled_clock_running_steady_switching_w`: 3.254041e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.204614e-06
- `obs_disabled_clock_running_steady_clock_w`: 4.602489e-05
- `obs_disabled_clock_running_steady_sequential_w`: 8.161394e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.196895e-06
- `obs_disabled_clock_running_steady_total_a`: 4.427857e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.306943e-04
- `obs_raw_streaming_reset_internal_w`: 9.625077e-05
- `obs_raw_streaming_reset_switching_w`: 3.224476e-05
- `obs_raw_streaming_reset_leakage_w`: 2.198723e-06
- `obs_raw_streaming_reset_clock_w`: 4.602489e-05
- `obs_raw_streaming_reset_sequential_w`: 8.034155e-05
- `obs_raw_streaming_reset_combinational_w`: 4.327796e-06
- `obs_raw_streaming_reset_total_a`: 4.356477e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.477273e-04
- `obs_raw_streaming_startup_internal_w`: 1.059346e-04
- `obs_raw_streaming_startup_switching_w`: 3.958471e-05
- `obs_raw_streaming_startup_leakage_w`: 2.207986e-06
- `obs_raw_streaming_startup_clock_w`: 4.602489e-05
- `obs_raw_streaming_startup_sequential_w`: 8.774414e-05
- `obs_raw_streaming_startup_combinational_w`: 1.395833e-05
- `obs_raw_streaming_startup_total_a`: 4.924243e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.587026e-04
- `obs_raw_streaming_steady_internal_w`: 1.124120e-04
- `obs_raw_streaming_steady_switching_w`: 4.407910e-05
- `obs_raw_streaming_steady_leakage_w`: 2.211509e-06
- `obs_raw_streaming_steady_clock_w`: 4.602489e-05
- `obs_raw_streaming_steady_sequential_w`: 9.314423e-05
- `obs_raw_streaming_steady_combinational_w`: 1.953346e-05
- `obs_raw_streaming_steady_total_a`: 5.290087e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
