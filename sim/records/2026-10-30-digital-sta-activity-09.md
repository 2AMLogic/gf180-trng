---
record: 2026-10-30-digital-sta-activity-09
date: 2026-10-30T15:17:55Z
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
  spef_sha256: 3004f6ebb906635be156b28f2f6feb4979d879cee4f11af141c25d7191fe042a
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
  path: sim/records/raw/2026-10-30-digital-sta-activity-09/
  files:
    - uniform.tcl  sha256:5d77a11d62c48ca8e28dc7b407fc861ff5810d68db96598c9a10d81b2fa4e2b6
    - uniform.log  sha256:5c037493478b84d03251ee247c16b67859ebf5252e1de59fadd21a63ca629abc
    - observed.tcl  sha256:55b9290845b1426f8411ffd9a57ae591cb5cdbd3333327c82dd9e905ab56e913
    - observed.log  sha256:ba40ea32d18c38f222d683a010aa5658ba648475da01787ffe008f131fbbf536
    - activity-manifest.json  sha256:1e327145d7667bd16602328c74156fdb1a0755c542aa19e43d054aedb64852d1
wall_time: 8.5s
---

## Result

Power in the table is OpenSTA's `report_power` total for the named capture
window, at the 1 MHz clock, over this corner's SPEF. Internal, switching and
leakage are kept as separate columns; the same terms are the bullets below.

| workload | window | cycles | internal uW | switching uW | leakage uW | total uW | vs uniform | annotated / unannotated pins |
|---|---|---:|---:|---:|---:|---:|---:|---|
| uniform (0.25 tr/net/cycle) | -- | -- |    177.23 |     85.02 |      0.23 |    262.49 | 1.000 | n/a (global) |
| alarm-gated | reset | 8 |    115.40 |     38.77 |      0.22 |    154.40 | 0.588 | 5371 / 0 |
| alarm-gated | startup | 1040 |    126.41 |     46.88 |      0.23 |    173.52 | 0.661 | 5371 / 0 |
| alarm-gated | steady | 1024 |    123.03 |     44.11 |      0.23 |    167.36 | 0.638 | 5371 / 0 |
| backpressure | reset | 8 |    115.35 |     38.67 |      0.22 |    154.25 | 0.588 | 5371 / 0 |
| backpressure | startup | 1040 |    126.61 |     47.02 |      0.23 |    173.86 | 0.662 | 5371 / 0 |
| backpressure | steady | 1024 |    134.49 |     52.33 |      0.24 |    187.06 | 0.713 | 5371 / 0 |
| conditioned-streaming | reset | 8 |    115.39 |     38.75 |      0.22 |    154.36 | 0.588 | 5371 / 0 |
| conditioned-streaming | startup | 1040 |    126.82 |     47.25 |      0.23 |    174.30 | 0.664 | 5371 / 0 |
| conditioned-streaming | steady | 1024 |    134.58 |     52.48 |      0.24 |    187.30 | 0.714 | 5371 / 0 |
| disabled-clock-running | reset | 8 |    115.04 |     38.20 |      0.22 |    153.47 | 0.585 | 5371 / 0 |
| disabled-clock-running | startup | 1040 |    117.84 |     39.44 |      0.23 |    157.51 | 0.600 | 5371 / 0 |
| disabled-clock-running | steady | 1024 |    117.72 |     39.38 |      0.23 |    157.32 | 0.599 | 5371 / 0 |
| raw-streaming | reset | 8 |    115.46 |     38.98 |      0.22 |    154.67 | 0.589 | 5371 / 0 |
| raw-streaming | startup | 1040 |    127.17 |     47.81 |      0.23 |    175.22 | 0.668 | 5371 / 0 |
| raw-streaming | steady | 1024 |    134.99 |     53.09 |      0.24 |    188.31 | 0.717 | 5371 / 0 |

- `uniform_total_w`: 2.624880e-04
- `uniform_internal_w`: 1.772332e-04
- `uniform_switching_w`: 8.501988e-05
- `uniform_leakage_w`: 2.349355e-07
- `uniform_clock_w`: 5.502261e-05
- `uniform_sequential_w`: 1.359543e-04
- `uniform_combinational_w`: 7.151115e-05
- `uniform_total_a`: 7.954182e-05
- `obs_alarm_gated_reset_total_w`: 1.544000e-04
- `obs_alarm_gated_reset_internal_w`: 1.154040e-04
- `obs_alarm_gated_reset_switching_w`: 3.877293e-05
- `obs_alarm_gated_reset_leakage_w`: 2.230880e-07
- `obs_alarm_gated_reset_clock_w`: 5.502261e-05
- `obs_alarm_gated_reset_sequential_w`: 9.506514e-05
- `obs_alarm_gated_reset_combinational_w`: 4.312223e-06
- `obs_alarm_gated_reset_total_a`: 4.678788e-05
- `obs_alarm_gated_reset_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_reset_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_startup_total_w`: 1.735219e-04
- `obs_alarm_gated_startup_internal_w`: 1.264143e-04
- `obs_alarm_gated_startup_switching_w`: 4.687545e-05
- `obs_alarm_gated_startup_leakage_w`: 2.321263e-07
- `obs_alarm_gated_startup_clock_w`: 5.502261e-05
- `obs_alarm_gated_startup_sequential_w`: 1.037065e-04
- `obs_alarm_gated_startup_combinational_w`: 1.479275e-05
- `obs_alarm_gated_startup_total_a`: 5.258239e-05
- `obs_alarm_gated_startup_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_startup_unannotated_pins`: 0.000000e+00
- `obs_alarm_gated_steady_total_w`: 1.673643e-04
- `obs_alarm_gated_steady_internal_w`: 1.230262e-04
- `obs_alarm_gated_steady_switching_w`: 4.410660e-05
- `obs_alarm_gated_steady_leakage_w`: 2.314846e-07
- `obs_alarm_gated_steady_clock_w`: 5.502261e-05
- `obs_alarm_gated_steady_sequential_w`: 1.014502e-04
- `obs_alarm_gated_steady_combinational_w`: 1.089152e-05
- `obs_alarm_gated_steady_total_a`: 5.071645e-05
- `obs_alarm_gated_steady_annotated_pins`: 5.371000e+03
- `obs_alarm_gated_steady_unannotated_pins`: 0.000000e+00
- `obs_backpressure_reset_total_w`: 1.542494e-04
- `obs_backpressure_reset_internal_w`: 1.153546e-04
- `obs_backpressure_reset_switching_w`: 3.867166e-05
- `obs_backpressure_reset_leakage_w`: 2.230880e-07
- `obs_backpressure_reset_clock_w`: 5.502261e-05
- `obs_backpressure_reset_sequential_w`: 9.505654e-05
- `obs_backpressure_reset_combinational_w`: 4.170196e-06
- `obs_backpressure_reset_total_a`: 4.674224e-05
- `obs_backpressure_reset_annotated_pins`: 5.371000e+03
- `obs_backpressure_reset_unannotated_pins`: 0.000000e+00
- `obs_backpressure_startup_total_w`: 1.738597e-04
- `obs_backpressure_startup_internal_w`: 1.266115e-04
- `obs_backpressure_startup_switching_w`: 4.701574e-05
- `obs_backpressure_startup_leakage_w`: 2.324177e-07
- `obs_backpressure_startup_clock_w`: 5.502261e-05
- `obs_backpressure_startup_sequential_w`: 1.037440e-04
- `obs_backpressure_startup_combinational_w`: 1.509300e-05
- `obs_backpressure_startup_total_a`: 5.268476e-05
- `obs_backpressure_startup_annotated_pins`: 5.371000e+03
- `obs_backpressure_startup_unannotated_pins`: 0.000000e+00
- `obs_backpressure_steady_total_w`: 1.870577e-04
- `obs_backpressure_steady_internal_w`: 1.344888e-04
- `obs_backpressure_steady_switching_w`: 5.233200e-05
- `obs_backpressure_steady_leakage_w`: 2.368907e-07
- `obs_backpressure_steady_clock_w`: 5.502261e-05
- `obs_backpressure_steady_sequential_w`: 1.103506e-04
- `obs_backpressure_steady_combinational_w`: 2.168439e-05
- `obs_backpressure_steady_total_a`: 5.668415e-05
- `obs_backpressure_steady_annotated_pins`: 5.371000e+03
- `obs_backpressure_steady_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_reset_total_w`: 1.543626e-04
- `obs_conditioned_streaming_reset_internal_w`: 1.153926e-04
- `obs_conditioned_streaming_reset_switching_w`: 3.874693e-05
- `obs_conditioned_streaming_reset_leakage_w`: 2.230880e-07
- `obs_conditioned_streaming_reset_clock_w`: 5.502261e-05
- `obs_conditioned_streaming_reset_sequential_w`: 9.506513e-05
- `obs_conditioned_streaming_reset_combinational_w`: 4.274852e-06
- `obs_conditioned_streaming_reset_total_a`: 4.677655e-05
- `obs_conditioned_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_startup_total_w`: 1.743043e-04
- `obs_conditioned_streaming_startup_internal_w`: 1.268185e-04
- `obs_conditioned_streaming_startup_switching_w`: 4.725402e-05
- `obs_conditioned_streaming_startup_leakage_w`: 2.317264e-07
- `obs_conditioned_streaming_startup_clock_w`: 5.502261e-05
- `obs_conditioned_streaming_startup_sequential_w`: 1.039318e-04
- `obs_conditioned_streaming_startup_combinational_w`: 1.534988e-05
- `obs_conditioned_streaming_startup_total_a`: 5.281948e-05
- `obs_conditioned_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_conditioned_streaming_steady_total_w`: 1.873022e-04
- `obs_conditioned_streaming_steady_internal_w`: 1.345819e-04
- `obs_conditioned_streaming_steady_switching_w`: 5.248455e-05
- `obs_conditioned_streaming_steady_leakage_w`: 2.357359e-07
- `obs_conditioned_streaming_steady_clock_w`: 5.502261e-05
- `obs_conditioned_streaming_steady_sequential_w`: 1.103214e-04
- `obs_conditioned_streaming_steady_combinational_w`: 2.195829e-05
- `obs_conditioned_streaming_steady_total_a`: 5.675824e-05
- `obs_conditioned_streaming_steady_annotated_pins`: 5.371000e+03
- `obs_conditioned_streaming_steady_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_reset_total_w`: 1.534700e-04
- `obs_disabled_clock_running_reset_internal_w`: 1.150444e-04
- `obs_disabled_clock_running_reset_switching_w`: 3.820250e-05
- `obs_disabled_clock_running_reset_leakage_w`: 2.230880e-07
- `obs_disabled_clock_running_reset_clock_w`: 5.502261e-05
- `obs_disabled_clock_running_reset_sequential_w`: 9.502358e-05
- `obs_disabled_clock_running_reset_combinational_w`: 3.423702e-06
- `obs_disabled_clock_running_reset_total_a`: 4.650606e-05
- `obs_disabled_clock_running_reset_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_reset_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_startup_total_w`: 1.575123e-04
- `obs_disabled_clock_running_startup_internal_w`: 1.178411e-04
- `obs_disabled_clock_running_startup_switching_w`: 3.944416e-05
- `obs_disabled_clock_running_startup_leakage_w`: 2.270612e-07
- `obs_disabled_clock_running_startup_clock_w`: 5.502261e-05
- `obs_disabled_clock_running_startup_sequential_w`: 9.657032e-05
- `obs_disabled_clock_running_startup_combinational_w`: 5.919420e-06
- `obs_disabled_clock_running_startup_total_a`: 4.773100e-05
- `obs_disabled_clock_running_startup_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_startup_unannotated_pins`: 0.000000e+00
- `obs_disabled_clock_running_steady_total_w`: 1.573207e-04
- `obs_disabled_clock_running_steady_internal_w`: 1.177176e-04
- `obs_disabled_clock_running_steady_switching_w`: 3.937609e-05
- `obs_disabled_clock_running_steady_leakage_w`: 2.270616e-07
- `obs_disabled_clock_running_steady_clock_w`: 5.502261e-05
- `obs_disabled_clock_running_steady_sequential_w`: 9.661877e-05
- `obs_disabled_clock_running_steady_combinational_w`: 5.679380e-06
- `obs_disabled_clock_running_steady_total_a`: 4.767294e-05
- `obs_disabled_clock_running_steady_annotated_pins`: 5.371000e+03
- `obs_disabled_clock_running_steady_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_reset_total_w`: 1.546675e-04
- `obs_raw_streaming_reset_internal_w`: 1.154637e-04
- `obs_raw_streaming_reset_switching_w`: 3.898072e-05
- `obs_raw_streaming_reset_leakage_w`: 2.230880e-07
- `obs_raw_streaming_reset_clock_w`: 5.502261e-05
- `obs_raw_streaming_reset_sequential_w`: 9.506472e-05
- `obs_raw_streaming_reset_combinational_w`: 4.580116e-06
- `obs_raw_streaming_reset_total_a`: 4.686894e-05
- `obs_raw_streaming_reset_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_reset_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_startup_total_w`: 1.752170e-04
- `obs_raw_streaming_startup_internal_w`: 1.271719e-04
- `obs_raw_streaming_startup_switching_w`: 4.781328e-05
- `obs_raw_streaming_startup_leakage_w`: 2.318815e-07
- `obs_raw_streaming_startup_clock_w`: 5.502261e-05
- `obs_raw_streaming_startup_sequential_w`: 1.039407e-04
- `obs_raw_streaming_startup_combinational_w`: 1.625375e-05
- `obs_raw_streaming_startup_total_a`: 5.309606e-05
- `obs_raw_streaming_startup_annotated_pins`: 5.371000e+03
- `obs_raw_streaming_startup_unannotated_pins`: 0.000000e+00
- `obs_raw_streaming_steady_total_w`: 1.883121e-04
- `obs_raw_streaming_steady_internal_w`: 1.349877e-04
- `obs_raw_streaming_steady_switching_w`: 5.308776e-05
- `obs_raw_streaming_steady_leakage_w`: 2.366255e-07
- `obs_raw_streaming_steady_clock_w`: 5.502261e-05
- `obs_raw_streaming_steady_sequential_w`: 1.103518e-04
- `obs_raw_streaming_steady_combinational_w`: 2.293775e-05
- `obs_raw_streaming_steady_total_a`: 5.706427e-05
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
