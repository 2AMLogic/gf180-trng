---
record: 2026-11-09-digital-power-by-block-01
date: 2026-11-09T18:41:44Z
status: valid

level: gate (see spec/decision-records/DR-0021-gate-level-timing-and-power-records.md)

testbench:
  path: sim/tb/digital-power-by-block/run_by_block.py
  sha: e6cfa31e12649f4ed68431086bc29a0cc990aa36
netlist:
  path: layout/digital/trng_top.def
  sha: 87b3dedca82354ea1c6b17e7e2867c806f9625f5
  note: >-
    The committed routed DEF (same DUT as the digital-sta-power family).
    Instance names keep the RTL hierarchy prefix, which is how power is
    attributed to a sub-block.
repo_commit: cdaf2fee558545d50e36177b9b5528b8ca31a7d4-dirty

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
  path: sim/records/raw/2026-11-09-digital-power-by-block-01/
  files:
    - by-block.tcl  sha256:bdbba0143ab72491d38ac61ee97c23e10ca53af53f51536ae08eaa00b1b3de15
    - by-block.log  sha256:64f37118871ff6156360c084e9b8f85fe7ee84dae37f0c1391669299e88c7870
wall_time: 1.9s
---

## Result

- `p_total_1mhz_w`: 3.393501e-04
- `p_internal_1mhz_w`: 2.346892e-04
- `p_switching_1mhz_w`: 9.704430e-05
- `p_leakage_1mhz_w`: 7.616592e-06
- `p_instance_sum_1mhz_w`: 3.393501e-04
- `instance_sum_gap`: 4.386e-08
- `n_conditioner`: 249
- `p_conditioner_total_w`: 5.854427e-05
- `p_conditioner_internal_w`: 4.829276e-05
- `p_conditioner_switching_w`: 9.278376e-06
- `p_conditioner_leakage_w`: 9.731312e-07
- `n_health_test`: 250
- `p_health_test_total_w`: 4.343983e-05
- `p_health_test_internal_w`: 3.325387e-05
- `p_health_test_switching_w`: 9.403165e-06
- `p_health_test_leakage_w`: 7.827950e-07
- `n_interface`: 772
- `p_interface_total_w`: 1.397734e-04
- `p_interface_internal_w`: 1.076727e-04
- `p_interface_switching_w`: 2.914115e-05
- `p_interface_leakage_w`: 2.959515e-06
- `n_ring_liveness`: 100
- `p_ring_liveness_total_w`: 1.850661e-05
- `p_ring_liveness_internal_w`: 1.379530e-05
- `p_ring_liveness_switching_w`: 4.374313e-06
- `p_ring_liveness_leakage_w`: 3.370007e-07
- `n_clock_tree`: 47
- `p_clock_tree_total_w`: 7.350784e-05
- `p_clock_tree_internal_w`: 3.063954e-05
- `p_clock_tree_switching_w`: 4.260693e-05
- `p_clock_tree_leakage_w`: 2.613765e-07
- `n_top_level_other`: 3370
- `p_top_level_other_total_w`: 5.578122e-06
- `p_top_level_other_internal_w`: 1.035035e-06
- `p_top_level_other_switching_w`: 2.240280e-06
- `p_top_level_other_leakage_w`: 2.302807e-06

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
