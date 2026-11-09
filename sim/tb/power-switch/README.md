# `power-switch` — PMOS header for the digital section (issue #707)

Deterministic transient testbench for `design/power_switch.spice` (schematic
`design/xschem/power_switch.sch`), run on the batch fleet as one `klt sim`
request of 45 PVT points. `sim/tools/power_switch.py` declares the grid, runs it, writes the
append-only records and summarises them; `sim/characterization-power-switch.md` reads the result.

| file | role |
|---|---|
| `tb_power_switch.sp` | the deck: four groups of switch instances (on-resistance, off leakage, gated idle, wake), loads and sleep drive. The header comment says what each load is. |
| `request-grid.json` | the declared `klt sim` request. Generated: `python3 sim/tools/power_switch.py emit --check` fails if it drifts. |

There is no `tb.json`: like the other fleet-run benches here, the measurements are `.meas` cards in the
request, not a `tb.json` for the local harness (`sim/run_corners.py` would run the whole grid on this host,
which the shared-worker rule forbids).

## Header, not footer

The digital section already has its own supply pin, `vddd` (`layout/floorplan/README.md`: four disjoint
supplies `vddr1`, `vddr2`, `vdd`, `vddd`), while `vss` is the one deliberately shared return
(`sim/characterization-vss-trunk-ir-drop.md`). A footer would sit in that shared return, so its on-resistance
would lift the reference the analog taps see. A header sits between the `vddd` pin and the digital power
grid and touches nothing the analog block shares. This is checked against those two documents, not against
the Liberty file or a layout trace. The issue's other argument for a header, that a footer would need an
isolated well because the digital `vss` is tied to the substrate straps, was not examined here: it is
unnecessary once the shared-return argument holds.

## Device choice

`pfet_03v3` at the minimum length 0.28 um, drawn as 40 parallel 10 um fingers, the same fingers the layout
draws. The 3.3 V device is enough: the supply is 3.3 V +10 %, and the gate drive is a plain
logic level from the always-on domain (`sleep` high = off, low = on), so no level shifter and no thick-oxide
device is needed. `sim/pdk.json` and `sim/harness/pdk_models.py` were not consulted for the choice; the
device is the same `pfet_03v3` every other cell in `design/` uses, and the records pin the models that
actually ran.

## Running it

```sh
python3 sim/tools/power_switch.py emit --check
python3 sim/tools/power_switch.py run --outdir DIR --backend batch     # the whole grid: fleet only
python3 sim/tools/power_switch.py run --outdir DIR --backend local --only ff/125/3.63   # one probe point
python3 sim/tools/power_switch.py record DIR/grid.report.json
python3 sim/tools/power_switch.py summarize
```

The request pins `set num_threads=1`. Without it the fleet's ngspice-46 did not finish this small circuit in
120 s and every unit hit its timeout; see the attempt record `sim/records/2026-10-28-power-switch-attempt-01.md`.
