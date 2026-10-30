---
record: 2026-10-30-digital-sta-activity-11
date: 2026-10-30T15:18:11Z
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
  spef_sha256: 72d3f2619167242d60a7538e9edbf0d28a3cc76520f052ec39307939bfcc662f
  spef_bytes: 1795569
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
  path: sim/records/raw/2026-10-30-digital-sta-activity-11/
  files:
    - uniform.tcl  sha256:19287d747f2f0e0a79506c1822971683ea341484a46f3ce9a1bfc0ed4a4839ea
    - uniform.log  sha256:2366989bd960f1cd66693b5b3b38d216edbf16b4756d30348d2456dc9e06ca77
    - observed.tcl  sha256:f01cb31cdff2661635766c5ca56310499942d33af9eb2f430524d5b9f162ea4e
    - observed.log  sha256:62da4ede10cbc318ef271b3b50de318e3c3c9cc1459b4d705fa6685a494c3b51
    - activity-manifest.json  sha256:1e327145d7667bd16602328c74156fdb1a0755c542aa19e43d054aedb64852d1
wall_time: 8.4s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    237.61 |     97.46 |      8.24 |    343.31 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    151.86 |     44.57 |      7.67 |    204.09 | 0.594 | 5371 / 0 |
| alarm-gated | startup | 1040 |    167.19 |     53.92 |      8.26 |    229.37 | 0.668 | 5371 / 0 |
| alarm-gated | steady | 1024 |    162.42 |     50.71 |      8.24 |    221.37 | 0.645 | 5371 / 0 |
| backpressure | reset | 8 |    151.79 |     44.45 |      7.67 |    203.91 | 0.594 | 5371 / 0 |
| backpressure | startup | 1040 |    167.46 |     54.08 |      8.25 |    229.80 | 0.669 | 5371 / 0 |
| backpressure | steady | 1024 |    178.43 |     60.19 |      8.58 |    247.20 | 0.720 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    151.84 |     44.54 |      7.67 |    204.05 | 0.594 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    167.76 |     54.35 |      8.26 |    230.37 | 0.671 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    178.57 |     60.36 |      8.50 |    247.42 | 0.721 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    151.35 |     43.91 |      7.67 |    202.93 | 0.591 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    155.35 |     45.37 |      8.05 |    208.77 | 0.608 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    155.17 |     45.30 |      8.05 |    208.52 | 0.607 | 5371 / 0 |
| raw-streaming | reset | 8 |    151.94 |     44.81 |      7.67 |    204.42 | 0.595 | 5371 / 0 |
| raw-streaming | startup | 1040 |    168.27 |     54.98 |      8.21 |    231.46 | 0.674 | 5371 / 0 |
| raw-streaming | steady | 1024 |    179.14 |     61.04 |      8.51 |    248.69 | 0.724 | 5371 / 0 |

- `uniform_total_w`: 3.433092e-04
- `uniform_internal_w`: 2.376093e-04
- `uniform_switching_w`: 9.746134e-05
- `uniform_leakage_w`: 8.238576e-06
- `uniform_clock_w`: 7.249122e-05
- `uniform_sequential_w`: 1.764243e-04
- `uniform_combinational_w`: 9.439379e-05
- `uniform_total_a`: 9.536367e-05
- `obs_alarm_gated_reset_total_w`: 2.040946e-04
- `obs_alarm_gated_reset_internal_w`: 1.518554e-04
- `obs_alarm_gated_reset_switching_w`: 4.456957e-05
- `obs_alarm_gated_reset_leakage_w`: 7.669590e-06
- `obs_alarm_gated_reset_clock_w`: 7.249122e-05
- `obs_alarm_gated_reset_sequential_w`: 1.233124e-04
- `obs_alarm_gated_reset_combinational_w`: 8.290774e-06
- `obs_alarm_gated_reset_total_a`: 5.669294e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 2.293665e-04
- `obs_alarm_gated_startup_internal_w`: 1.671900e-04
- `obs_alarm_gated_startup_switching_w`: 5.391862e-05
- `obs_alarm_gated_startup_leakage_w`: 8.257824e-06
- `obs_alarm_gated_startup_clock_w`: 7.249122e-05
- `obs_alarm_gated_startup_sequential_w`: 1.346787e-04
- `obs_alarm_gated_startup_combinational_w`: 2.219668e-05
- `obs_alarm_gated_startup_total_a`: 6.371292e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 2.213652e-04
- `obs_alarm_gated_steady_internal_w`: 1.624227e-04
- `obs_alarm_gated_steady_switching_w`: 5.070545e-05
- `obs_alarm_gated_steady_leakage_w`: 8.236960e-06
- `obs_alarm_gated_steady_clock_w`: 7.249122e-05
- `obs_alarm_gated_steady_sequential_w`: 1.318169e-04
- `obs_alarm_gated_steady_combinational_w`: 1.705710e-05
- `obs_alarm_gated_steady_total_a`: 6.149033e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 2.039131e-04
- `obs_backpressure_reset_internal_w`: 1.517907e-04
- `obs_backpressure_reset_switching_w`: 4.445278e-05
- `obs_backpressure_reset_leakage_w`: 7.669590e-06
- `obs_backpressure_reset_clock_w`: 7.249122e-05
- `obs_backpressure_reset_sequential_w`: 1.233015e-04
- `obs_backpressure_reset_combinational_w`: 8.120232e-06
- `obs_backpressure_reset_total_a`: 5.664253e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 2.297972e-04
- `obs_backpressure_startup_internal_w`: 1.674643e-04
- `obs_backpressure_startup_switching_w`: 5.408025e-05
- `obs_backpressure_startup_leakage_w`: 8.252681e-06
- `obs_backpressure_startup_clock_w`: 7.249122e-05
- `obs_backpressure_startup_sequential_w`: 1.347345e-04
- `obs_backpressure_startup_combinational_w`: 2.257158e-05
- `obs_backpressure_startup_total_a`: 6.383256e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 2.471953e-04
- `obs_backpressure_steady_internal_w`: 1.784257e-04
- `obs_backpressure_steady_switching_w`: 6.018951e-05
- `obs_backpressure_steady_leakage_w`: 8.580112e-06
- `obs_backpressure_steady_clock_w`: 7.249122e-05
- `obs_backpressure_steady_sequential_w`: 1.434373e-04
- `obs_backpressure_steady_combinational_w`: 3.126695e-05
- `obs_backpressure_steady_total_a`: 6.866536e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 2.040492e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.518407e-04
- `obs_conditioned_streaming_reset_switching_w`: 4.453891e-05
- `obs_conditioned_streaming_reset_leakage_w`: 7.669590e-06
- `obs_conditioned_streaming_reset_clock_w`: 7.249122e-05
- `obs_conditioned_streaming_reset_sequential_w`: 1.233124e-04
- `obs_conditioned_streaming_reset_combinational_w`: 8.245380e-06
- `obs_conditioned_streaming_reset_total_a`: 5.668033e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 2.303676e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.677594e-04
- `obs_conditioned_streaming_startup_switching_w`: 5.435311e-05
- `obs_conditioned_streaming_startup_leakage_w`: 8.255111e-06
- `obs_conditioned_streaming_startup_clock_w`: 7.249122e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.349624e-04
- `obs_conditioned_streaming_startup_combinational_w`: 2.291399e-05
- `obs_conditioned_streaming_startup_total_a`: 6.399100e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 2.474241e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.785653e-04
- `obs_conditioned_streaming_steady_switching_w`: 6.036306e-05
- `obs_conditioned_streaming_steady_leakage_w`: 8.495754e-06
- `obs_conditioned_streaming_steady_clock_w`: 7.249122e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.433880e-04
- `obs_conditioned_streaming_steady_combinational_w`: 3.154501e-05
- `obs_conditioned_streaming_steady_total_a`: 6.872892e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 2.029316e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.513494e-04
- `obs_disabled_clock_running_reset_switching_w`: 4.391251e-05
- `obs_disabled_clock_running_reset_leakage_w`: 7.669590e-06
- `obs_disabled_clock_running_reset_clock_w`: 7.249122e-05
- `obs_disabled_clock_running_reset_sequential_w`: 1.232571e-04
- `obs_disabled_clock_running_reset_combinational_w`: 7.183166e-06
- `obs_disabled_clock_running_reset_total_a`: 5.636989e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 2.087714e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.553461e-04
- `obs_disabled_clock_running_startup_switching_w`: 4.537474e-05
- `obs_disabled_clock_running_startup_leakage_w`: 8.050591e-06
- `obs_disabled_clock_running_startup_clock_w`: 7.249122e-05
- `obs_disabled_clock_running_startup_sequential_w`: 1.255552e-04
- `obs_disabled_clock_running_startup_combinational_w`: 1.072505e-05
- `obs_disabled_clock_running_startup_total_a`: 5.799206e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 2.085217e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.551733e-04
- `obs_disabled_clock_running_steady_switching_w`: 4.529731e-05
- `obs_disabled_clock_running_steady_leakage_w`: 8.051127e-06
- `obs_disabled_clock_running_steady_clock_w`: 7.249122e-05
- `obs_disabled_clock_running_steady_sequential_w`: 1.256114e-04
- `obs_disabled_clock_running_steady_combinational_w`: 1.041907e-05
- `obs_disabled_clock_running_steady_total_a`: 5.792269e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 2.044224e-04
- `obs_raw_streaming_reset_internal_w`: 1.519449e-04
- `obs_raw_streaming_reset_switching_w`: 4.480789e-05
- `obs_raw_streaming_reset_leakage_w`: 7.669590e-06
- `obs_raw_streaming_reset_clock_w`: 7.249122e-05
- `obs_raw_streaming_reset_sequential_w`: 1.233112e-04
- `obs_raw_streaming_reset_combinational_w`: 8.620029e-06
- `obs_raw_streaming_reset_total_a`: 5.678400e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 2.314571e-04
- `obs_raw_streaming_startup_internal_w`: 1.682663e-04
- `obs_raw_streaming_startup_switching_w`: 5.498162e-05
- `obs_raw_streaming_startup_leakage_w`: 8.209090e-06
- `obs_raw_streaming_startup_clock_w`: 7.249122e-05
- `obs_raw_streaming_startup_sequential_w`: 1.349725e-04
- `obs_raw_streaming_startup_combinational_w`: 2.399333e-05
- `obs_raw_streaming_startup_total_a`: 6.429364e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 2.486898e-04
- `obs_raw_streaming_steady_internal_w`: 1.791393e-04
- `obs_raw_streaming_steady_switching_w`: 6.104373e-05
- `obs_raw_streaming_steady_leakage_w`: 8.506731e-06
- `obs_raw_streaming_steady_clock_w`: 7.249122e-05
- `obs_raw_streaming_steady_sequential_w`: 1.434325e-04
- `obs_raw_streaming_steady_combinational_w`: 3.276619e-05
- `obs_raw_streaming_steady_total_a`: 6.908050e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
