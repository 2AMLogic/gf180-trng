---
record: 2026-10-30-digital-sta-activity-07
date: 2026-10-30T15:17:38Z
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
  spef_sha256: 2203e9ecb345c10e60fd9e6786888bf5d46f01f534d3c898ed62f1bcb91e955c
  spef_bytes: 1789895
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
  path: sim/records/raw/2026-10-30-digital-sta-activity-07/
  files:
    - uniform.tcl  sha256:19e9e5320afb4fb3d65e8cfb7508a7f89304c36b768b83284c6d3907b57956dd
    - uniform.log  sha256:f180e8343cf3399789e62272059cef3174324db38bd9e351c10ab4bdab84669c
    - observed.tcl  sha256:b5d0904e16dd276d8dbe7b775f1e9acbb82948eea2afce7e0cef8f45aab5f6b3
    - observed.log  sha256:4ea55c9c262e25ea702e03decb7db706d9321c95852e371e7ad5fbd1b50200ef
    - activity-manifest.json  sha256:1e327145d7667bd16602328c74156fdb1a0755c542aa19e43d054aedb64852d1
wall_time: 8.4s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    176.46 |     78.65 |      0.23 |    255.35 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    114.80 |     35.96 |      0.22 |    150.99 | 0.591 | 5371 / 0 |
| alarm-gated | startup | 1040 |    125.79 |     43.56 |      0.23 |    169.58 | 0.664 | 5371 / 0 |
| alarm-gated | steady | 1024 |    122.41 |     40.94 |      0.23 |    163.58 | 0.641 | 5371 / 0 |
| backpressure | reset | 8 |    114.75 |     35.87 |      0.22 |    150.84 | 0.591 | 5371 / 0 |
| backpressure | startup | 1040 |    125.98 |     43.69 |      0.23 |    169.91 | 0.665 | 5371 / 0 |
| backpressure | steady | 1024 |    133.84 |     48.64 |      0.24 |    182.72 | 0.716 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    114.79 |     35.94 |      0.22 |    150.95 | 0.591 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    126.19 |     43.91 |      0.23 |    170.34 | 0.667 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    133.93 |     48.78 |      0.24 |    182.95 | 0.716 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    114.44 |     35.43 |      0.22 |    150.10 | 0.588 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    117.24 |     36.63 |      0.23 |    154.10 | 0.603 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    117.11 |     36.57 |      0.23 |    153.91 | 0.603 | 5371 / 0 |
| raw-streaming | reset | 8 |    114.86 |     36.15 |      0.22 |    151.24 | 0.592 | 5371 / 0 |
| raw-streaming | startup | 1040 |    126.54 |     44.41 |      0.23 |    171.18 | 0.670 | 5371 / 0 |
| raw-streaming | steady | 1024 |    134.33 |     49.32 |      0.24 |    183.89 | 0.720 | 5371 / 0 |

- `uniform_total_w`: 2.553505e-04
- `uniform_internal_w`: 1.764610e-04
- `uniform_switching_w`: 7.865448e-05
- `uniform_leakage_w`: 2.349355e-07
- `uniform_clock_w`: 5.207305e-05
- `uniform_sequential_w`: 1.349886e-04
- `uniform_combinational_w`: 6.828889e-05
- `uniform_total_a`: 7.737894e-05
- `obs_alarm_gated_reset_total_w`: 1.509852e-04
- `obs_alarm_gated_reset_internal_w`: 1.148013e-04
- `obs_alarm_gated_reset_switching_w`: 3.596075e-05
- `obs_alarm_gated_reset_leakage_w`: 2.230880e-07
- `obs_alarm_gated_reset_clock_w`: 5.207305e-05
- `obs_alarm_gated_reset_sequential_w`: 9.480501e-05
- `obs_alarm_gated_reset_combinational_w`: 4.107125e-06
- `obs_alarm_gated_reset_total_a`: 4.575309e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.695801e-04
- `obs_alarm_gated_startup_internal_w`: 1.257876e-04
- `obs_alarm_gated_startup_switching_w`: 4.356036e-05
- `obs_alarm_gated_startup_leakage_w`: 2.321263e-07
- `obs_alarm_gated_startup_clock_w`: 5.207305e-05
- `obs_alarm_gated_startup_sequential_w`: 1.032298e-04
- `obs_alarm_gated_startup_combinational_w`: 1.427725e-05
- `obs_alarm_gated_startup_total_a`: 5.138791e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.635806e-04
- `obs_alarm_gated_steady_internal_w`: 1.224096e-04
- `obs_alarm_gated_steady_switching_w`: 4.093947e-05
- `obs_alarm_gated_steady_leakage_w`: 2.314846e-07
- `obs_alarm_gated_steady_clock_w`: 5.207305e-05
- `obs_alarm_gated_steady_sequential_w`: 1.010270e-04
- `obs_alarm_gated_steady_combinational_w`: 1.048047e-05
- `obs_alarm_gated_steady_total_a`: 4.956988e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.508411e-04
- `obs_backpressure_reset_internal_w`: 1.147519e-04
- `obs_backpressure_reset_switching_w`: 3.586609e-05
- `obs_backpressure_reset_leakage_w`: 2.230880e-07
- `obs_backpressure_reset_clock_w`: 5.207305e-05
- `obs_backpressure_reset_sequential_w`: 9.479641e-05
- `obs_backpressure_reset_combinational_w`: 3.971648e-06
- `obs_backpressure_reset_total_a`: 4.570942e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.699086e-04
- `obs_backpressure_startup_internal_w`: 1.259843e-04
- `obs_backpressure_startup_switching_w`: 4.369186e-05
- `obs_backpressure_startup_leakage_w`: 2.324177e-07
- `obs_backpressure_startup_clock_w`: 5.207305e-05
- `obs_backpressure_startup_sequential_w`: 1.032677e-04
- `obs_backpressure_startup_combinational_w`: 1.456785e-05
- `obs_backpressure_startup_total_a`: 5.148745e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.827157e-04
- `obs_backpressure_steady_internal_w`: 1.338375e-04
- `obs_backpressure_steady_switching_w`: 4.864135e-05
- `obs_backpressure_steady_leakage_w`: 2.368907e-07
- `obs_backpressure_steady_clock_w`: 5.207305e-05
- `obs_backpressure_steady_sequential_w`: 1.097517e-04
- `obs_backpressure_steady_combinational_w`: 2.089093e-05
- `obs_backpressure_steady_total_a`: 5.536839e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.509486e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.147900e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.593555e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.230880e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.207305e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.480501e-05
- `obs_conditioned_streaming_reset_combinational_w`: 4.070563e-06
- `obs_conditioned_streaming_reset_total_a`: 4.574200e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.703351e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.261906e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.391282e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.317264e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.207305e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.034505e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.481160e-05
- `obs_conditioned_streaming_startup_total_a`: 5.161670e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.829475e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.339303e-04
- `obs_conditioned_streaming_steady_switching_w`: 4.878145e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.357359e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.207305e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.097238e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.115059e-05
- `obs_conditioned_streaming_steady_total_a`: 5.543864e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.500964e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.144440e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.542933e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.230880e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.207305e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.476352e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.259876e-06
- `obs_disabled_clock_running_reset_total_a`: 4.548376e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.540974e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.172356e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.663480e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.270612e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.207305e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.627046e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.753951e-06
- `obs_disabled_clock_running_startup_total_a`: 4.669618e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.539120e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.171123e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.657270e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.270616e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.207305e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.631672e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.522276e-06
- `obs_disabled_clock_running_steady_total_a`: 4.664000e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.512380e-04
- `obs_raw_streaming_reset_internal_w`: 1.148606e-04
- `obs_raw_streaming_reset_switching_w`: 3.615430e-05
- `obs_raw_streaming_reset_leakage_w`: 2.230880e-07
- `obs_raw_streaming_reset_clock_w`: 5.207305e-05
- `obs_raw_streaming_reset_sequential_w`: 9.480464e-05
- `obs_raw_streaming_reset_combinational_w`: 4.360371e-06
- `obs_raw_streaming_reset_total_a`: 4.582970e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.711833e-04
- `obs_raw_streaming_startup_internal_w`: 1.265403e-04
- `obs_raw_streaming_startup_switching_w`: 4.441112e-05
- `obs_raw_streaming_startup_leakage_w`: 2.318815e-07
- `obs_raw_streaming_startup_clock_w`: 5.207305e-05
- `obs_raw_streaming_startup_sequential_w`: 1.034572e-04
- `obs_raw_streaming_startup_combinational_w`: 1.565294e-05
- `obs_raw_streaming_startup_total_a`: 5.187373e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.838931e-04
- `obs_raw_streaming_steady_internal_w`: 1.343326e-04
- `obs_raw_streaming_steady_switching_w`: 4.932383e-05
- `obs_raw_streaming_steady_leakage_w`: 2.366255e-07
- `obs_raw_streaming_steady_clock_w`: 5.207305e-05
- `obs_raw_streaming_steady_sequential_w`: 1.097524e-04
- `obs_raw_streaming_steady_combinational_w`: 2.206762e-05
- `obs_raw_streaming_steady_total_a`: 5.572518e-05
- `obs_raw_streaming_steady_annotated_pins`: 5.371000e+03
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
