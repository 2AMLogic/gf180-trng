---
record: 2026-10-30-digital-sta-activity-15
date: 2026-10-30T15:18:45Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-sta-power/activity_power.py
  sha: 4788da7e8a836f0f60a49125c3189c5391a137de
netlist:
  path: layout/digital/trng_top.def
  sha: d24d862fc3836f8f5514aa2fa32e319f1a96567c
  note: >-
    The committed routed DEF re-timed at this corner; the observed
    activity comes from simulating the matching as-built gate-level
    netlist layout/digital/trng_top.pnr.v (sha bb949d10cf059e01698f33f6531b74da1df90358).
repo_commit: 8939b542e96bfc19151bee88578dc394b5468fe2-dirty

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
  spef_sha256: d8e2b2cc2476097f38183773bb055fda96e4fd9afc8760d5a59b665ff9a03437
  spef_bytes: 1803172
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
      vcd_sha256: d73b73c2878833b11c530926e16d4581e020fd1f07ba48aec025168df2997b09
      vcd_bytes: 20199467
      stimulus_sha256: 8a293fe403af802995b4389bcb70b24d39896f62106bb0546573f661b33ad76f
      cycles: 2169
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1145, 2169]}
      instances_matched: 1490/1490
      xz_events: 4272
      same_timestamp_extra_changes: 0
    - workload: backpressure
      vcd_sha256: ce683a6499939dfdfbc7f0948d9cdf6e0fb7118b0eea81c99310ea9ff8a19a6d
      vcd_bytes: 21556003
      stimulus_sha256: 5ba36ddddb2b14957eb3d643f1eb68dae1749e72a1dab195b060d82b51234276
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4289
      same_timestamp_extra_changes: 0
    - workload: conditioned-streaming
      vcd_sha256: 1b70087f5ae79f73da990c9d9aa9738670f74a6b31e57f02cc3f2ba736fa55fc
      vcd_bytes: 21612163
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4168
      same_timestamp_extra_changes: 0
    - workload: disabled-clock-running
      vcd_sha256: a10758043594e820119885dbb73a054dc89bfbbf413e35c32c5bd544f30648a5
      vcd_bytes: 16158866
      stimulus_sha256: 75fcbcde1260c88b1d185a0f21a23c138292d86e1e94ed71855d367eba330f13
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 1798
      same_timestamp_extra_changes: 0
    - workload: raw-streaming
      vcd_sha256: a8544b5fe783833514bdbc26788df620d3f8969d23472620ed7021e0628acd65
      vcd_bytes: 21759020
      stimulus_sha256: d864523e1f3610d64b87a2cbaab8fd4eaf3a169b139b9ffc04c2da2aec1d94ab
      cycles: 2072
      windows_cycles: {"reset": [0, 8], "startup": [8, 1048], "steady": [1048, 2072]}
      instances_matched: 1490/1490
      xz_events: 4488
      same_timestamp_extra_changes: 0

raw:
  path: sim/records/raw/2026-10-30-digital-sta-activity-15/
  files:
    - uniform.tcl  sha256:47969b9ca0fe8779bb3f0e70c447b0302a6e7342af085137e17e801fdc39f9a4
    - uniform.log  sha256:58ad70d90318550ba52063013f416dd12f2ce07a655240dff45566d590f7e7a1
    - observed.tcl  sha256:1504b6b01c3aea7c35c8003063f13d6f40faaa7ed0aa51e728227f7a0e3890ba
    - observed.log  sha256:f1d5d8981b7f1c783e8011c7192e0ce1cbadb4ec35f1c690c4d8d0ac553a933d
    - activity-manifest.json  sha256:1e327145d7667bd16602328c74156fdb1a0755c542aa19e43d054aedb64852d1
wall_time: 8.6s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    217.59 |    101.21 |      0.28 |    319.08 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    141.10 |     46.20 |      0.26 |    187.55 | 0.588 | 5371 / 0 |
| alarm-gated | startup | 1040 |    154.66 |     55.83 |      0.27 |    210.76 | 0.661 | 5371 / 0 |
| alarm-gated | steady | 1024 |    150.45 |     52.54 |      0.27 |    203.27 | 0.637 | 5371 / 0 |
| backpressure | reset | 8 |    141.04 |     46.08 |      0.26 |    187.37 | 0.587 | 5371 / 0 |
| backpressure | startup | 1040 |    154.90 |     56.00 |      0.27 |    211.17 | 0.662 | 5371 / 0 |
| backpressure | steady | 1024 |    164.62 |     62.33 |      0.28 |    227.23 | 0.712 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    141.08 |     46.16 |      0.26 |    187.51 | 0.588 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    155.16 |     56.29 |      0.27 |    211.72 | 0.664 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    164.74 |     62.51 |      0.28 |    227.53 | 0.713 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    140.64 |     45.52 |      0.26 |    186.42 | 0.584 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    144.11 |     46.99 |      0.27 |    191.36 | 0.600 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    143.96 |     46.91 |      0.27 |    191.13 | 0.599 | 5371 / 0 |
| raw-streaming | reset | 8 |    141.17 |     46.44 |      0.26 |    187.88 | 0.589 | 5371 / 0 |
| raw-streaming | startup | 1040 |    155.61 |     56.95 |      0.27 |    212.83 | 0.667 | 5371 / 0 |
| raw-streaming | steady | 1024 |    165.25 |     63.23 |      0.28 |    228.75 | 0.717 | 5371 / 0 |

- `uniform_total_w`: 3.190756e-04
- `uniform_internal_w`: 2.175920e-04
- `uniform_switching_w`: 1.012084e-04
- `uniform_leakage_w`: 2.751911e-07
- `uniform_clock_w`: 6.786104e-05
- `uniform_sequential_w`: 1.640383e-04
- `uniform_combinational_w`: 8.717615e-05
- `uniform_total_a`: 8.863211e-05
- `obs_alarm_gated_reset_total_w`: 1.875542e-04
- `obs_alarm_gated_reset_internal_w`: 1.410952e-04
- `obs_alarm_gated_reset_switching_w`: 4.619544e-05
- `obs_alarm_gated_reset_leakage_w`: 2.635719e-07
- `obs_alarm_gated_reset_clock_w`: 6.786104e-05
- `obs_alarm_gated_reset_sequential_w`: 1.144910e-04
- `obs_alarm_gated_reset_combinational_w`: 5.202372e-06
- `obs_alarm_gated_reset_total_a`: 5.209839e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.107641e-04
- `obs_alarm_gated_startup_internal_w`: 1.546573e-04
- `obs_alarm_gated_startup_switching_w`: 5.583485e-05
- `obs_alarm_gated_startup_leakage_w`: 2.720082e-07
- `obs_alarm_gated_startup_clock_w`: 6.786104e-05
- `obs_alarm_gated_startup_sequential_w`: 1.249188e-04
- `obs_alarm_gated_startup_combinational_w`: 1.798448e-05
- `obs_alarm_gated_startup_total_a`: 5.854558e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.032660e-04
- `obs_alarm_gated_steady_internal_w`: 1.504529e-04
- `obs_alarm_gated_steady_switching_w`: 5.254181e-05
- `obs_alarm_gated_steady_leakage_w`: 2.712460e-07
- `obs_alarm_gated_steady_clock_w`: 6.786104e-05
- `obs_alarm_gated_steady_sequential_w`: 1.221955e-04
- `obs_alarm_gated_steady_combinational_w`: 1.320950e-05
- `obs_alarm_gated_steady_total_a`: 5.646278e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.873747e-04
- `obs_backpressure_reset_internal_w`: 1.410360e-04
- `obs_backpressure_reset_switching_w`: 4.607507e-05
- `obs_backpressure_reset_leakage_w`: 2.635719e-07
- `obs_backpressure_reset_clock_w`: 6.786104e-05
- `obs_backpressure_reset_sequential_w`: 1.144809e-04
- `obs_backpressure_reset_combinational_w`: 5.033033e-06
- `obs_backpressure_reset_total_a`: 5.204853e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.111723e-04
- `obs_backpressure_startup_internal_w`: 1.548983e-04
- `obs_backpressure_startup_switching_w`: 5.600165e-05
- `obs_backpressure_startup_leakage_w`: 2.722985e-07
- `obs_backpressure_startup_clock_w`: 6.786104e-05
- `obs_backpressure_startup_sequential_w`: 1.249631e-04
- `obs_backpressure_startup_combinational_w`: 1.834835e-05
- `obs_backpressure_startup_total_a`: 5.865897e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.272276e-04
- `obs_backpressure_steady_internal_w`: 1.646220e-04
- `obs_backpressure_steady_switching_w`: 6.232879e-05
- `obs_backpressure_steady_leakage_w`: 2.768367e-07
- `obs_backpressure_steady_clock_w`: 6.786104e-05
- `obs_backpressure_steady_sequential_w`: 1.330010e-04
- `obs_backpressure_steady_combinational_w`: 2.636563e-05
- `obs_backpressure_steady_total_a`: 6.311878e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.875096e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.410815e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.616457e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.635719e-07
- `obs_conditioned_streaming_reset_clock_w`: 6.786104e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.144910e-04
- `obs_conditioned_streaming_reset_combinational_w`: 5.157834e-06
- `obs_conditioned_streaming_reset_total_a`: 5.208600e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.117164e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.551596e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.628515e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.716374e-07
- `obs_conditioned_streaming_startup_clock_w`: 6.786104e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.251942e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.866126e-05
- `obs_conditioned_streaming_startup_total_a`: 5.881011e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.275281e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.647425e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.250993e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.756414e-07
- `obs_conditioned_streaming_steady_clock_w`: 6.786104e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.329695e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.669747e-05
- `obs_conditioned_streaming_steady_total_a`: 6.320225e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.864234e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.406435e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.551631e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.635719e-07
- `obs_disabled_clock_running_reset_clock_w`: 6.786104e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.144410e-04
- `obs_disabled_clock_running_reset_combinational_w`: 4.121478e-06
- `obs_disabled_clock_running_reset_total_a`: 5.178428e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.913627e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.441061e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.698999e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.666009e-07
- `obs_disabled_clock_running_startup_clock_w`: 6.786104e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.162986e-04
- `obs_disabled_clock_running_startup_combinational_w`: 7.203128e-06
- `obs_disabled_clock_running_startup_total_a`: 5.315631e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.911308e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.439553e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.690883e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.666007e-07
- `obs_disabled_clock_running_steady_clock_w`: 6.786104e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.163563e-04
- `obs_disabled_clock_running_steady_combinational_w`: 6.913480e-06
- `obs_disabled_clock_running_steady_total_a`: 5.309189e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.878773e-04
- `obs_raw_streaming_reset_internal_w`: 1.411717e-04
- `obs_raw_streaming_reset_switching_w`: 4.644196e-05
- `obs_raw_streaming_reset_leakage_w`: 2.635719e-07
- `obs_raw_streaming_reset_clock_w`: 6.786104e-05
- `obs_raw_streaming_reset_sequential_w`: 1.144903e-04
- `obs_raw_streaming_reset_combinational_w`: 5.526075e-06
- `obs_raw_streaming_reset_total_a`: 5.218814e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.128295e-04
- `obs_raw_streaming_startup_internal_w`: 1.556066e-04
- `obs_raw_streaming_startup_switching_w`: 5.695119e-05
- `obs_raw_streaming_startup_leakage_w`: 2.717171e-07
- `obs_raw_streaming_startup_clock_w`: 6.786104e-05
- `obs_raw_streaming_startup_sequential_w`: 1.252007e-04
- `obs_raw_streaming_startup_combinational_w`: 1.976787e-05
- `obs_raw_streaming_startup_total_a`: 5.911931e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.287547e-04
- `obs_raw_streaming_steady_internal_w`: 1.652500e-04
- `obs_raw_streaming_steady_switching_w`: 6.322808e-05
- `obs_raw_streaming_steady_leakage_w`: 2.765572e-07
- `obs_raw_streaming_steady_clock_w`: 6.786104e-05
- `obs_raw_streaming_steady_sequential_w`: 1.330024e-04
- `obs_raw_streaming_steady_combinational_w`: 2.789126e-05
- `obs_raw_streaming_steady_total_a`: 6.354297e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
