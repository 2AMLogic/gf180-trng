---
record: 2026-11-13-digital-power-by-block-01
date: 2026-11-13T23:18:43Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-power-by-block/run_by_block.py
  sha: 521483dcd54464c447a1e76ffa5b14130f2af47c
netlist:
  path: layout/digital/trng_top.def
  sha: 89e8f60a83222b44213d3c89a059db389405b475
  note: >-
    The committed routed DEF (same DUT as the digital-sta-power family).
    Instance names keep the RTL hierarchy prefix, which is how power is
    attributed to a sub-block.
repo_commit: e783bb4f7336f4422aa26902c7003f638bccd0a7-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /home/ubuntu/.ciel/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lib/gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60.lib (liberty corner ff_125C_3v60, sha256:b64f32b397097f2046e66ce7f9a4aaffc9a80c4c0bfd3c77385727268e81a016)
  - /home/ubuntu/.ciel/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/techlef/gf180mcu_fd_sc_mcu9t5v0__nom.tlef (tech LEF, nom deck, sha256:80bf186e7fcc2c4b1bae9b8ee0e67100acf4f643e71a58daadc3f354f0836508)
  - /home/ubuntu/.ciel/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu9t5v0/lef/gf180mcu_fd_sc_mcu9t5v0.lef (cell LEF, sha256:38afbef95529165e1d8999d5b5613c4aec9869df8c1ce6b5555e74586ba4c826)
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/librelane/rules.openrcx.gf180mcuD.max (OpenRCX interconnect corner max, sha256:0ee103cf2108f2fd945087551b6dd1eaf4ee55af60571de2983878c8a271515f)

tool:
  ngspice: "n/a (gate-level record -- power comes from OpenSTA inside OpenROAD)"
  openroad: "26Q3-1510-g6cb3f2b704"

corner:
  process: ff
  voltage: 3.60 V
  temperature: 125
  liberty: gf180mcu_fd_sc_mcu9t5v0__ff_125C_3v60
  interconnect: max (OpenRCX rule deck)
  liberty_operating_conditions: nom_process 1, nom_temperature 125, nom_voltage 3.6

analysis:
  type: power (OpenSTA report_power -instances over the committed routed DEF, OpenRCX-extracted parasitics back-annotated as SPEF)
  clock: clk, 1000 ns (1 MHz), propagated (the CTS-built tree in the DEF)
  power_activity: 0.25 transitions/net/cycle, duty 0.5 (set_power_activity -global; the same declared activity as digital-sta-power)
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-11-13-digital-power-by-block-01/
  files:
    - by-block.tcl  sha256:18cf5f7ea16583e6f18864e62cbdf924fdce5c180c50a1d97a475c80e68b800b
    - by-block.log  sha256:7575f73e416cd3af43a32067f7112080ec27c607844740936a5d9cb128abe4fc
wall_time: 4.2s
---

## Result

- `p_total_1mhz_w`: 3.381151e-04
- `p_internal_1mhz_w`: 2.324919e-04
- `p_switching_1mhz_w`: 9.804400e-05
- `p_leakage_1mhz_w`: 7.579158e-06
- `p_instance_sum_1mhz_w`: 3.381151e-04
- `instance_sum_gap`: 1.085e-07
- `n_conditioner`: 249
- `p_conditioner_total_w`: 5.849943e-05
- `p_conditioner_internal_w`: 4.828844e-05
- `p_conditioner_switching_w`: 9.239208e-06
- `p_conditioner_leakage_w`: 9.717854e-07
- `n_health_test`: 250
- `p_health_test_total_w`: 4.173924e-05
- `p_health_test_internal_w`: 3.223141e-05
- `p_health_test_switching_w`: 8.766718e-06
- `p_health_test_leakage_w`: 7.411070e-07
- `n_interface`: 770
- `p_interface_total_w`: 1.386241e-04
- `p_interface_internal_w`: 1.068649e-04
- `p_interface_switching_w`: 2.883280e-05
- `p_interface_leakage_w`: 2.926316e-06
- `n_ring_liveness`: 99
- `p_ring_liveness_total_w`: 1.811197e-05
- `p_ring_liveness_internal_w`: 1.347912e-05
- `p_ring_liveness_switching_w`: 4.309967e-06
- `p_ring_liveness_leakage_w`: 3.228812e-07
- `n_clock_tree`: 49
- `p_clock_tree_total_w`: 7.448251e-05
- `p_clock_tree_internal_w`: 3.014771e-05
- `p_clock_tree_switching_w`: 4.406791e-05
- `p_clock_tree_leakage_w`: 2.668861e-07
- `n_top_level_other`: 3399
- `p_top_level_other_total_w`: 6.657859e-06
- `p_top_level_other_internal_w`: 1.480255e-06
- `p_top_level_other_switching_w`: 2.827382e-06
- `p_top_level_other_leakage_w`: 2.350223e-06

Numbers only. These are liberty-power figures at a declared uniform activity
(DR-0021 section 3), not measured supply currents. Each instance is counted in
exactly one group and the group totals sum to `report_power`'s own total (gap
above). The clock-tree group is `clkbuf_*`/`clkload*` cells; `top_level_other`
is every remaining instance without a hierarchy prefix (placement/repair
buffers, tap, endcap and filler cells).

## How to reproduce

```sh
python3 sim/tb/digital-power-by-block/run_by_block.py --liberty ff_125C_3v60 --rc max
```

## Caveats

- Single corner (ff_125C_3v60 / OpenRCX max); says nothing about any other corner.
- Uniform declared activity, not this design's data-dependent activity.
- Hierarchy attribution is by instance-name prefix in the flattened as-built
  netlist; a cell the flow added outside a prefix lands in `top_level_other` or
  `clock_tree`.

---

Written by `sim/tb/digital-power-by-block/run_by_block.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
