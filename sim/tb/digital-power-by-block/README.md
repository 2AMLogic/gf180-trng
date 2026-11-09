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

## VCD-activity mode (`--activity`, #812)

Replaces the uniform activity with the toggle activity of a gate-level
simulation of the as-built netlist and tabulates VCD-derived against uniform
power per sub-block, at 1 MHz and at the 2 kHz raw rate. A 2 kHz trace needs
its own VCD at the 500 us period (OpenSTA reads toggles per trace-second), so
there are two captures, each reusing `sim/tb/digital-sta-power/activity.py`:

```sh
W=layout/.work/digital-power-by-block-activity
python3 sim/tb/digital-sta-power/activity.py capture --workload conditioned-streaming --out $W/1mhz
python3 sim/tb/digital-sta-power/activity.py capture --workload conditioned-streaming \
    --period-ns 500000 --out $W/2khz
python3 sim/tb/digital-power-by-block/run_by_block.py --activity --no-write   # print only
python3 sim/tb/digital-power-by-block/run_by_block.py --activity              # mint one record
```

Needs `iverilog` and `vvp` as well; ~25 s. Each rate runs a uniform session and
a VCD session over one SPEF. The same 0.1 % instance-sum check applies, and the
`activity.validate_annotation` rejection (under 99 % of pins bound to the VCD)
stays in force. The record slug is `digital-power-by-block-activity`, outside
`active_power_breakdown.BY_BLOCK_GLOB`, so the ratified breakdown and
`power_rollup.py` still read only the uniform records. One declared stimulus,
not a worst case; no entropy claim.

[DR-0021]: ../../../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
