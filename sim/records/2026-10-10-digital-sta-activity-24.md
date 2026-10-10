---
record: 2026-10-10-digital-sta-activity-24
date: 2026-10-10T07:12:37Z
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
repo_commit: 37b0d1714e0aa26771c265216557e0ec45825dcb

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - gf180mcu_fd_sc_mcu9t5v0__tt_025C_3v30.lib (liberty corner tt_025C_3v30, sha256:154655e033bec8509acca1575cc2e48e4d7143dfe70a8c61e0695f24c3dcaf02)
  - gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:332ae93d61ac55f793da97a6391703f78bc415653cb60e76dd8eb0092124485a)
  - gf180mcu_fd_sc_mcu9t5v0.lef (cell LEF, sha256:38afbef95529165e1d8999d5b5613c4aec9869df8c1ce6b5555e74586ba4c826)
  - rules.openrcx.gf180mcuD.max (OpenRCX interconnect corner max, sha256:0ee103cf2108f2fd945087551b6dd1eaf4ee55af60571de2983878c8a271515f)
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
  interconnect: max (OpenRCX rule deck)
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
  spef_sha256: 3b26223ed462edc0c5c5b2f0e2584a8ebcc838c0f531aaee14668e5e7df32020
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
  path: sim/records/raw/2026-10-10-digital-sta-activity-24/
  files:
    - uniform.tcl  sha256:145aff3188f410a87ea33a6d9f42937180b4e61b32461d5748465bda0d4f47f4
    - uniform.log  sha256:447c8c84985a06e8cc27dc6c12d3422865476d898d352a8fcb6e01b1c14b5ef4
    - observed.tcl  sha256:82d39330141eb6c7b2cebe310b63a17b2e8dcfa8bed462f6bef2c811abb84803
    - observed.log  sha256:f6a1e0e14da7118c62be317e91d566c52d8702d23e6be1d5f289ea4666cf2c50
    - activity-manifest.json  sha256:bbcad3ee73d024bbfa9d98d64d1ff3f580d1871f755d8cd82385ec3db9089df7
wall_time: 8.2s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    177.13 |     84.92 |      0.22 |    262.27 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    115.21 |     38.48 |      0.21 |    153.89 | 0.587 | 5371 / 0 |
| alarm-gated | startup | 1040 |    126.21 |     46.53 |      0.22 |    172.95 | 0.659 | 5371 / 0 |
| alarm-gated | steady | 1024 |    122.82 |     43.66 |      0.22 |    166.69 | 0.636 | 5371 / 0 |
| backpressure | reset | 8 |    115.16 |     38.37 |      0.21 |    153.73 | 0.586 | 5371 / 0 |
| backpressure | startup | 1040 |    126.40 |     46.67 |      0.22 |    173.29 | 0.661 | 5371 / 0 |
| backpressure | steady | 1024 |    134.29 |     52.08 |      0.22 |    186.59 | 0.711 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    115.19 |     38.45 |      0.21 |    153.85 | 0.587 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    126.61 |     46.91 |      0.22 |    173.74 | 0.662 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    134.38 |     52.23 |      0.22 |    186.83 | 0.712 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    114.85 |     37.87 |      0.21 |    152.92 | 0.583 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    117.63 |     39.11 |      0.21 |    156.96 | 0.598 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    117.51 |     39.05 |      0.21 |    156.77 | 0.598 | 5371 / 0 |
| raw-streaming | reset | 8 |    115.27 |     38.70 |      0.21 |    154.17 | 0.588 | 5371 / 0 |
| raw-streaming | startup | 1040 |    126.96 |     47.47 |      0.22 |    174.65 | 0.666 | 5371 / 0 |
| raw-streaming | steady | 1024 |    134.78 |     52.84 |      0.22 |    187.84 | 0.716 | 5371 / 0 |

- `uniform_total_w`: 2.622675e-04
- `uniform_internal_w`: 1.771266e-04
- `uniform_switching_w`: 8.492156e-05
- `uniform_leakage_w`: 2.193580e-07
- `uniform_clock_w`: 5.449347e-05
- `uniform_sequential_w`: 1.359966e-04
- `uniform_combinational_w`: 7.177763e-05
- `uniform_total_a`: 7.947500e-05
- `obs_alarm_gated_reset_total_w`: 1.538911e-04
- `obs_alarm_gated_reset_internal_w`: 1.152059e-04
- `obs_alarm_gated_reset_switching_w`: 3.847774e-05
- `obs_alarm_gated_reset_leakage_w`: 2.075095e-07
- `obs_alarm_gated_reset_clock_w`: 5.449347e-05
- `obs_alarm_gated_reset_sequential_w`: 9.504725e-05
- `obs_alarm_gated_reset_combinational_w`: 4.350419e-06
- `obs_alarm_gated_reset_total_a`: 4.663367e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.729529e-04
- `obs_alarm_gated_startup_internal_w`: 1.262069e-04
- `obs_alarm_gated_startup_switching_w`: 4.652945e-05
- `obs_alarm_gated_startup_leakage_w`: 2.165480e-07
- `obs_alarm_gated_startup_clock_w`: 5.449347e-05
- `obs_alarm_gated_startup_sequential_w`: 1.037024e-04
- `obs_alarm_gated_startup_combinational_w`: 1.475708e-05
- `obs_alarm_gated_startup_total_a`: 5.240997e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.666909e-04
- `obs_alarm_gated_steady_internal_w`: 1.228200e-04
- `obs_alarm_gated_steady_switching_w`: 4.365501e-05
- `obs_alarm_gated_steady_leakage_w`: 2.159064e-07
- `obs_alarm_gated_steady_clock_w`: 5.449347e-05
- `obs_alarm_gated_steady_sequential_w`: 1.014379e-04
- `obs_alarm_gated_steady_combinational_w`: 1.075945e-05
- `obs_alarm_gated_steady_total_a`: 5.051239e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.537339e-04
- `obs_backpressure_reset_internal_w`: 1.151565e-04
- `obs_backpressure_reset_switching_w`: 3.836991e-05
- `obs_backpressure_reset_leakage_w`: 2.075095e-07
- `obs_backpressure_reset_clock_w`: 5.449347e-05
- `obs_backpressure_reset_sequential_w`: 9.503865e-05
- `obs_backpressure_reset_combinational_w`: 4.201854e-06
- `obs_backpressure_reset_total_a`: 4.658603e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.732930e-04
- `obs_backpressure_startup_internal_w`: 1.264041e-04
- `obs_backpressure_startup_switching_w`: 4.667203e-05
- `obs_backpressure_startup_leakage_w`: 2.168396e-07
- `obs_backpressure_startup_clock_w`: 5.449347e-05
- `obs_backpressure_startup_sequential_w`: 1.037368e-04
- `obs_backpressure_startup_combinational_w`: 1.506257e-05
- `obs_backpressure_startup_total_a`: 5.251303e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.865884e-04
- `obs_backpressure_steady_internal_w`: 1.342855e-04
- `obs_backpressure_steady_switching_w`: 5.208163e-05
- `obs_backpressure_steady_leakage_w`: 2.213108e-07
- `obs_backpressure_steady_clock_w`: 5.449347e-05
- `obs_backpressure_steady_sequential_w`: 1.104164e-04
- `obs_backpressure_steady_combinational_w`: 2.167864e-05
- `obs_backpressure_steady_total_a`: 5.654194e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.538529e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.151945e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.845089e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.075095e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.449347e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.504724e-05
- `obs_conditioned_streaming_reset_combinational_w`: 4.312179e-06
- `obs_conditioned_streaming_reset_total_a`: 4.662209e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.737381e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.266108e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.691108e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.161481e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.449347e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.039278e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.531667e-05
- `obs_conditioned_streaming_startup_total_a`: 5.264791e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.868325e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.343819e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.223045e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.201589e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.449347e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.103944e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.194468e-05
- `obs_conditioned_streaming_steady_total_a`: 5.661591e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.529247e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.148454e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.787181e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.075095e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.449347e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.500584e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.425484e-06
- `obs_disabled_clock_running_reset_total_a`: 4.634082e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.569567e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.176314e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.911382e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.114828e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.449347e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.653583e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.927473e-06
- `obs_disabled_clock_running_startup_total_a`: 4.756264e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.567665e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.175081e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.904694e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.114832e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.449347e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.658362e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.689464e-06
- `obs_disabled_clock_running_steady_total_a`: 4.750500e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.541726e-04
- `obs_raw_streaming_reset_internal_w`: 1.152669e-04
- `obs_raw_streaming_reset_switching_w`: 3.869813e-05
- `obs_raw_streaming_reset_leakage_w`: 2.075095e-07
- `obs_raw_streaming_reset_clock_w`: 5.449347e-05
- `obs_raw_streaming_reset_sequential_w`: 9.504691e-05
- `obs_raw_streaming_reset_combinational_w`: 4.632243e-06
- `obs_raw_streaming_reset_total_a`: 4.671897e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.746474e-04
- `obs_raw_streaming_startup_internal_w`: 1.269634e-04
- `obs_raw_streaming_startup_switching_w`: 4.746770e-05
- `obs_raw_streaming_startup_leakage_w`: 2.163030e-07
- `obs_raw_streaming_startup_clock_w`: 5.449347e-05
- `obs_raw_streaming_startup_sequential_w`: 1.039279e-04
- `obs_raw_streaming_startup_combinational_w`: 1.622592e-05
- `obs_raw_streaming_startup_total_a`: 5.292345e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.878428e-04
- `obs_raw_streaming_steady_internal_w`: 1.347836e-04
- `obs_raw_streaming_steady_switching_w`: 5.283820e-05
- `obs_raw_streaming_steady_leakage_w`: 2.210452e-07
- `obs_raw_streaming_steady_clock_w`: 5.449347e-05
- `obs_raw_streaming_steady_sequential_w`: 1.104201e-04
- `obs_raw_streaming_steady_combinational_w`: 2.292933e-05
- `obs_raw_streaming_steady_total_a`: 5.692206e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_steady_unannotated_pins`: 0.000000e+00

Numbers only. No spec-compliance claim is made by this record; see
`sim/characterization-digital-activity-power.md` for what the family reads
as, and what it does not establish.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture
python3 sim/tb/digital-sta-power/run_sta.py --activity --liberty tt_025C_3v30 --rc max --no-write
```

Records are append-only: a re-run mints a new stem. Needs `iverilog` 13.0+,
`openroad` on `PATH` and the gf180mcu PDK.

## Caveats

- **One corner** (tt_025C_3v30, interconnect `max`).
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
