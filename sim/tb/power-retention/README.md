# `power-retention` — retained state and measured idle (issue #790)

Deterministic transient testbench for the always-on set of
[`design/power-intent.md`](../../../design/power-intent.md), built from real cells
(`retention_cells.spice`, copied from the PDK: `dffrnq_1`, `icgtp_1`, `and2_1`) beside the #707
header (`design/power_switch.spice`). One `klt sim` request of 45 PVT points on the batch fleet;
`sim/tools/power_retention.py` declares the grid, runs it, writes the append-only records and summarises them.
`sim/characterization-power-switch.md` section 7 reads the result.

| file | role |
|---|---|
| `tb_power_retention.sp` | the deck: group F (power cycle, rail forced, with a free-running-clock control) and group I (switch off, idle current). The header comment says what each is. |
| `request-grid.json` | the declared request. Generated: `python3 sim/tools/power_retention.py emit --check` fails if it drifts. |

There is no `tb.json`: the measurements are `.meas` cards in the request, and `sim/run_corners.py` would run
the whole grid on this host, which the shared-worker rule forbids. The request sets `batch.capacity_wait_s`
so a burst waits for fleet capacity instead of failing the submit.

```sh
python3 sim/tools/power_retention.py emit --check
python3 sim/tools/power_retention.py run --outdir DIR --backend batch
python3 sim/tools/power_retention.py run --outdir DIR --backend local --only ff/125/3.63   # one probe point
python3 sim/tools/power_retention.py record DIR/grid.report.json
python3 sim/tools/power_retention.py summarize
```

The gated domain's logic is ideal behavioural sources, the rail in the function group is forced, and plain flops
stand in for the retention flops the library lacks (caveats in the records and in section 7). Wall time for the
whole grid on the fleet is under two minutes.
