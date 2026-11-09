---
record: 2026-11-09-digital-power-by-block-activity-01
date: 2026-11-09T21:58:13Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-power-by-block/run_by_block.py
  sha: 521483dcd54464c447a1e76ffa5b14130f2af47c
netlist:
  path: layout/digital/trng_top.def
  sha: 87b3dedca82354ea1c6b17e7e2867c806f9625f5
  note: >-
    The committed routed DEF re-timed at this corner; the activity comes from
    simulating the matching as-built gate-level netlist
    layout/digital/trng_top.pnr.v (sha edd5900119f431c7d68f1f67eb3dcdf6b44ec32c).
repo_commit: 910461f4e20a99fe6369fa53beccde60370754b3-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /home/ubuntu/.ciel/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lib/gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60.lib (liberty corner ff_125C_3v60, sha256:b64f32b397097f2046e66ce7f9a4aaffc9a80c4c0bfd3c77385727268e81a016)
  - /home/ubuntu/.ciel/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/techlef/gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:80bf186e7fcc2c4b1bae9b8ee0e67100acf4f643e71a58daadc3f354f0836508)
  - /home/ubuntu/.ciel/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lef/gf180mcu_fd_sc_mcu9t5v0.lef (cell LEF, sha256:38afbef95529165e1d8999d5b5613c4aec9869df8c1ce6b5555e74586ba4c826)
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/librelane/rules.openrcx.gf180mcuD.max (OpenRCX interconnect corner max, sha256:0ee103cf2108f2fd945087551b6dd1eaf4ee55af60571de2983878c8a271515f)
  - <pdk>/libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/gf180mcu_fd_sc_mcu9t5v0.v (gate-simulation cell model, sha256:7dc2d6578c3580b0716c6a883a1b33c6cc7172f29c74ac1b148b0b20f981fe16)
  - <pdk>/libs.ref/gf180mcu_fd_sc_mcu9t5v0/verilog/primitives.v (gate-simulation cell model, sha256:fc47cb4d4e50feb06847eba4bb1d67bec09a648fe2ab7aeab30248cb75d3609c)

tool:
  ngspice: "n/a (gate-level record -- power comes from OpenSTA inside OpenROAD)"
  openroad: "26Q3-1510-g6cb3f2b704"
  simulator: "Icarus Verilog version 13.0 (stable) (v13_0) -g2012 -gno-specify (zero delay; specify blocks ignored)"

corner:
  process: ff
  voltage: 3.60 V
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60
  interconnect: max (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature 125, nom_voltage 3.6

analysis:
  type: power (OpenSTA report_power -instances over the committed routed DEF, OpenRCX parasitics as SPEF, switching activity read from a gate-level VCD), against a uniform-activity session at the same clock
  clock: 1mhz 1000 ns, propagated; 2khz 500000 ns, propagated
  uniform_baseline: 0.25 transitions/net/cycle, duty 0.5 (set_power_activity -global; as digital-power-by-block)
  activity_scope: tb/dut (read_vcd -scope)
  activity_window: steady
seeds: base 453; workload conditioned-streaming 453

activity:
  note: >-
    Zero-delay gate simulation of the as-built post-route netlist; one declared
    synthetic workload, not a worst case. The raw bits make no entropy claim.
    Not a silicon current measurement.
  workload: conditioned-streaming
  window: steady (cycles [1048, 2072])
  testbench_sha: 3625a86ad31f107ce0bcf2795f1a1ea04e5aef7c
  workloads_module_sha: 8e72ab3c3fed2c91d225a21330821ef9fb2e43bb
  traces:
    - rate: 1mhz
      clock_period_ns: 1000
      vcd_sha256: 4f8de9215f6b9e43309280a614e7f84fa92be1c5d899956043c44e3c29bb0aaf
      vcd_bytes: 19148535
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      instances_matched: 1423/1423
      xz_events: 4971
    - rate: 2khz
      clock_period_ns: 500000
      vcd_sha256: 6b72df367295d6b52dc89b79fa0ef1917f245c26c43036e67f5e0971b07258c0
      vcd_bytes: 19158745
      stimulus_sha256: 3f94423435f333ad70adb1de7018f8cf88c455e242804222ef2df6acf29cc13e
      cycles: 2072
      instances_matched: 1423/1423
      xz_events: 4971

raw:
  path: sim/records/raw/2026-11-09-digital-power-by-block-activity-01/
  files:
    - 1mhz-uniform.tcl  sha256:0f88672df0f84b0ad164a0ccc4c48638b6c3364cac7d9b69ba843d723bebc072
    - 1mhz-uniform.log  sha256:adb39dc6a023d00af16c5150659e14f1353c384b8501206467bdacd05f324ee2
    - 1mhz-activity.tcl  sha256:09db0871e05cf7ac4cb95ed4e943f8462954642604cf1d82afada1e73f1e72ac
    - 1mhz-activity.log  sha256:e6725727ac60dadfbe2b3efa00926e858cd6bccaffdcb6b6869d372e28b4310a
    - 1mhz-manifest.json  sha256:f824b645c280db82069d1da6238976435b82427418318b6aae79a5c825e99a10
    - 2khz-uniform.tcl  sha256:4447d3f051d3b2cf3148faf82917f5ede2a0d859c3e90e68dc63f28ddf6eb966
    - 2khz-uniform.log  sha256:13180b5e53b24c330c9d2544e58cab4aaeb22c00616f976a2e8a0a2133b4742a
    - 2khz-activity.tcl  sha256:52ca38903df03a104f2b1b29789b728661dbde027a741807f467560c9b7719b4
    - 2khz-activity.log  sha256:ce91410a2c7f92bd3dac7d3835d5c41d465bb68d56984ef1b6d9f661034b1e52
    - 2khz-manifest.json  sha256:0660baf4a29328cc34dcc4bce6800b751a4f3a3fbc5bd22fbf491b3c7f2d98c9
wall_time: 7.6s
---

## Result

Per-sub-block power of the routed digital section, OpenSTA `report_power
-instances` summed by `group_of` (the grouping of `digital-power-by-block-01`),
with switching activity read from a gate-level VCD (conditioned-streaming,
`steady` window) and, for the baseline column, the declared uniform
activity at the same clock. Every instance is in exactly one group; each group
set sums to `report_power`'s own total (gap in the bullets, limit
0.1%).

### 1mhz (clock period 1000 ns)

| sub-block | uniform uW | VCD-derived uW | VCD - uniform uW | VCD / uniform |
|---|---:|---:|---:|---:|
| u_conditioner | 58.544 | 51.832 | -6.712 | 0.885 |
| u_health_test | 43.440 | 27.490 | -15.949 | 0.633 |
| u_interface | 139.774 | 80.590 | -59.184 | 0.577 |
| u_ring_liveness | 18.507 | 17.804 | -0.703 | 0.962 |
| clock_tree | 73.510 | 73.510 | 0.000 | 1.000 |
| top_level_other | 5.577 | 2.325 | -3.253 | 0.417 |
| **whole section** | 339.352 | 253.551 | -85.801 | 0.747 |

### 2khz (clock period 500000 ns)

| sub-block | uniform uW | VCD-derived uW | VCD - uniform uW | VCD / uniform |
|---|---:|---:|---:|---:|
| u_conditioner | 1.088 | 1.184 | 0.095 | 1.088 |
| u_health_test | 0.868 | 0.917 | 0.049 | 1.056 |
| u_interface | 3.233 | 3.138 | -0.095 | 0.971 |
| u_ring_liveness | 0.373 | 0.407 | 0.033 | 1.089 |
| clock_tree | 0.408 | 0.408 | 0.000 | 1.000 |
| top_level_other | 2.309 | 2.325 | 0.015 | 1.007 |
| **whole section** | 8.280 | 8.378 | 0.098 | 1.012 |

- `1mhz_period_ns`: 1.000000e+03
- `1mhz_uniform_total_w`: 3.393520e-04
- `1mhz_vcd_total_w`: 2.535505e-04
- `1mhz_vcd_over_uniform`: 7.471608e-01
- `1mhz_uniform_internal_w`: 2.346911e-04
- `1mhz_vcd_internal_w`: 1.825790e-04
- `1mhz_uniform_switching_w`: 9.704430e-05
- `1mhz_vcd_switching_w`: 6.308504e-05
- `1mhz_uniform_leakage_w`: 7.616592e-06
- `1mhz_vcd_leakage_w`: 7.886476e-06
- `1mhz_vcd_instance_sum_gap`: 2.837900e-07
- `1mhz_uniform_instance_sum_gap`: 5.108560e-08
- `1mhz_annotated_pins`: 5.143000e+03
- `1mhz_unannotated_pins`: 0.000000e+00
- `1mhz_annotated_fraction`: 1.000000e+00
- `1mhz_conditioner_uniform_w`: 5.854418e-05
- `1mhz_conditioner_vcd_w`: 5.183175e-05
- `1mhz_conditioner_ratio`: 8.853442e-01
- `1mhz_conditioner_vcd_leakage_w`: 1.082144e-06
- `1mhz_health_test_uniform_w`: 4.343974e-05
- `1mhz_health_test_vcd_w`: 2.749032e-05
- `1mhz_health_test_ratio`: 6.328381e-01
- `1mhz_health_test_vcd_leakage_w`: 8.634601e-07
- `1mhz_interface_uniform_w`: 1.397738e-04
- `1mhz_interface_vcd_w`: 8.058991e-05
- `1mhz_interface_ratio`: 5.765736e-01
- `1mhz_interface_vcd_leakage_w`: 2.983178e-06
- `1mhz_ring_liveness_uniform_w`: 1.850694e-05
- `1mhz_ring_liveness_vcd_w`: 1.780407e-05
- `1mhz_ring_liveness_ratio`: 9.620214e-01
- `1mhz_ring_liveness_vcd_leakage_w`: 3.717442e-07
- `1mhz_clock_tree_uniform_w`: 7.350998e-05
- `1mhz_clock_tree_vcd_w`: 7.350998e-05
- `1mhz_clock_tree_ratio`: 1.000000e+00
- `1mhz_clock_tree_vcd_leakage_w`: 2.613765e-07
- `1mhz_top_level_other_uniform_w`: 5.577336e-06
- `1mhz_top_level_other_vcd_w`: 2.324539e-06
- `1mhz_top_level_other_ratio`: 4.167830e-01
- `1mhz_top_level_other_vcd_leakage_w`: 2.324539e-06
- `2khz_period_ns`: 5.000000e+05
- `2khz_uniform_total_w`: 8.280063e-06
- `2khz_vcd_total_w`: 8.377804e-06
- `2khz_vcd_over_uniform`: 1.011804e+00
- `2khz_uniform_internal_w`: 4.693820e-07
- `2khz_vcd_internal_w`: 3.651582e-07
- `2khz_uniform_switching_w`: 1.940885e-07
- `2khz_vcd_switching_w`: 1.261701e-07
- `2khz_uniform_leakage_w`: 7.616592e-06
- `2khz_vcd_leakage_w`: 7.886476e-06
- `2khz_vcd_instance_sum_gap`: 4.023883e-06
- `2khz_uniform_instance_sum_gap`: 4.127384e-06
- `2khz_annotated_pins`: 5.143000e+03
- `2khz_unannotated_pins`: 0.000000e+00
- `2khz_annotated_fraction`: 1.000000e+00
- `2khz_conditioner_uniform_w`: 1.088273e-06
- `2khz_conditioner_vcd_w`: 1.183643e-06
- `2khz_conditioner_ratio`: 1.087634e+00
- `2khz_conditioner_vcd_leakage_w`: 1.082144e-06
- `2khz_health_test_uniform_w`: 8.681090e-07
- `2khz_health_test_vcd_w`: 9.167138e-07
- `2khz_health_test_ratio`: 1.055989e+00
- `2khz_health_test_vcd_leakage_w`: 8.634601e-07
- `2khz_interface_uniform_w`: 3.233144e-06
- `2khz_interface_vcd_w`: 3.138392e-06
- `2khz_interface_ratio`: 9.706935e-01
- `2khz_interface_vcd_leakage_w`: 2.983178e-06
- `2khz_ring_liveness_uniform_w`: 3.733406e-07
- `2khz_ring_liveness_vcd_w`: 4.066088e-07
- `2khz_ring_liveness_ratio`: 1.089110e+00
- `2khz_ring_liveness_vcd_leakage_w`: 3.717442e-07
- `2khz_clock_tree_uniform_w`: 4.078738e-07
- `2khz_clock_tree_vcd_w`: 4.078738e-07
- `2khz_clock_tree_ratio`: 1.000000e+00
- `2khz_clock_tree_vcd_leakage_w`: 2.613765e-07
- `2khz_top_level_other_uniform_w`: 2.309357e-06
- `2khz_top_level_other_vcd_w`: 2.324539e-06
- `2khz_top_level_other_ratio`: 1.006574e+00
- `2khz_top_level_other_vcd_leakage_w`: 2.324539e-06

Numbers only. Liberty-power figures at the stated activity (DR-0021 section 3),
not measured supply currents.

## Reconciliation with the uniform records

The 1 MHz uniform column is this tool's own uniform session and equals the
whole-section figure of `digital-power-by-block-01` (339.4 uW) because both use
the same DEF, SPEF extraction, activity and clock. It differs from the 348.2 uW
quoted in `sim/characterization-digital-activity-power.md` because that figure
comes from the 2026-10-10 `digital-sta-activity` records, taken on an earlier
routed DEF (blob `8f13adca...`); the 2026-10-29 records on the current DEF
(blob `87b3dedc...`) give 339.35 uW at this corner, and the whole-section
VCD figure for this workload there (253.55 uW, `conditioned_streaming` steady
window) agrees with the 1 MHz VCD column above to about 0.002 % (the residual
is not traced).

## Leakage versus switching at each rate

OpenSTA reads toggles per second of *trace* time, so each rate has its own VCD
(simulated at that rate's clock period) rather than a rescale of the other.
Leakage does not depend on the clock: it is the same state-weighted liberty
leakage at either rate (it varies a little with the logic states the trace
visits, see `*_vcd_leakage_w` against `*_uniform_leakage_w`). Internal and
switching power fall with the toggle rate, so at 2 kHz the section is
leakage-dominated; the VCD/uniform ratio there is therefore close to 1 and says
little about activity.

## How to reproduce

```sh
python3 sim/tb/digital-sta-power/activity.py capture --workload conditioned-streaming \
    --out layout/.work/digital-power-by-block-activity/1mhz
python3 sim/tb/digital-sta-power/activity.py capture --workload conditioned-streaming \
    --period-ns 500000 --out layout/.work/digital-power-by-block-activity/2khz
python3 sim/tb/digital-power-by-block/run_by_block.py --liberty ff_125C_3v60 --rc max --activity
```

## Caveats

- Single corner (ff_125C_3v60 / OpenRCX max); says nothing about any other corner.
- One declared stimulus (conditioned-streaming); not a worst case and no entropy claim.
  The `steady` window is the post-start-up cycles of the workload
  (`windows_cycles` in the manifest); reset and start-up are not in the figures.
- Zero-delay simulation: glitching beyond same-timestamp delta activity is not
  modelled; x/z events are counted in the front matter.
- Unannotated pins run on OpenSTA's fallback activity and are counted above; a
  trace binding under 99% of pins is rejected.
- Hierarchy attribution is by instance-name prefix, as in `digital-power-by-block`.

---

Written by `sim/tb/digital-power-by-block/run_by_block.py --activity`. Append-only: never edit or
delete this file -- a re-run or correction mints a new record and points back here
