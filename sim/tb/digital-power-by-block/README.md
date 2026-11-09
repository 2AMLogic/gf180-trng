# `digital-power-by-block` — per-sub-block power of the routed digital section

Gate-level ([DR-0021]) companion to `sim/tb/digital-sta-power/`: the same
committed routed DEF, OpenRCX extraction, declared uniform activity and 1 MHz
clock, but with OpenSTA's `report_power -instances` summed by the hierarchy
prefix the as-built netlist keeps in its instance names (`u_conditioner/`,
`u_health_test/`, `u_interface/`, `u_ring_liveness/`), with the CTS clock tree
(`clkbuf_*`, `clkload*`) and the remaining top-level instances as their own
groups.

```sh
python3 sim/tb/digital-power-by-block/run_by_block.py --no-write   # print only
python3 sim/tb/digital-power-by-block/run_by_block.py              # mint one record
python3 sim/tb/digital-power-by-block/run_by_block.py --liberty ff_n40C_3v60 --rc max
```

Needs `openroad` on `PATH` and a gf180mcu PDK install; ~10 s. Default corner is
`ff_125C_3v60` / `max`, where `sim/tools/power_rollup.py` finds the digital
active term binding. A run is refused if the per-instance sum differs from
`report_power`'s own total by more than 0.1 %.

Like the `digital-sta-power` family this is a liberty-power model at a declared
activity, not a measured supply current (DR-0021 section 3). It has no
`tb.json` on purpose: a liberty corner is a characterised bundle, not a free
PVT choice, so `sim/run_corners.py` must not sweep it across the analog grid.
`sim/tools/active_power_breakdown.py` assembles these records with the array
and sampler records into the whole-block breakdown.

[DR-0021]: ../../../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
