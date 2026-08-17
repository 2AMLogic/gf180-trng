# `digital-sta-power` — corner-swept STA and power over the routed digital section

Gate-level testbench ([DR-0021]): it re-opens the **committed** routed DEF
`layout/digital/trng_top.def` (#111) and re-times it, once per corner,
against the PDK's own liberty and extraction decks. No device models, no
ngspice, and no re-placement — one fixed piece of geometry, fifteen corners.

```sh
python3 sim/tb/digital-sta-power/run_sta.py --list      # the corner grid
python3 sim/tb/digital-sta-power/run_sta.py --no-write   # run it, mint nothing
python3 sim/tb/digital-sta-power/run_sta.py              # run it, mint 15 records
python3 sim/tb/digital-sta-power/run_sta.py --liberty ss_125C_3v00 --rc max --no-write
```

Needs `openroad` on `PATH` and a gf180mcu PDK install (`python3
sim/run_corners.py --check-env` resolves the PDK; `layout/digital/README.md`'s
"OpenROAD" section covers the OpenROAD side, including the pinned ORFS Docker
image for machines with no native build). ~9 s per corner, ~2 min for the
grid.

**No `tb.json`, on purpose.** `sim/harness/testbench.py`'s discovery only
picks up directories that have one, so `sim/run_corners.py` cannot sweep this
testbench across the analog PVT grid — which it must not, because a liberty
corner is a characterised *bundle* of process, voltage and temperature and
not a free P/V/T choice. This is the same construction DR-0009 rule 7 uses to
keep behavioral testbenches off the analog grid, for a different reason.

## The grid

Five liberty decks — every one `gf180mcu_fd_sc_mcu9t5v0` characterises in the
block's ratified 3.3 V supply family — crossed with all three OpenRCX
interconnect decks the PDK ships:

| | `min` | `nom` | `max` |
|---|---|---|---|
| `ss_125C_3v00` | ✓ | ✓ | ✓ |
| `ss_n40C_3v00` | ✓ | ✓ | ✓ |
| `tt_025C_3v30` | ✓ | ✓ | ✓ |
| `ff_125C_3v60` | ✓ | ✓ | ✓ |
| `ff_n40C_3v60` | ✓ | ✓ | ✓ |

The library also ships 1.8 V and 5.0 V families. They are excluded for the
same reason `layout/digital/build.py` excludes them: this block runs at 3.3 V
(`design/README.md`), and timing it against a deck for a supply it does not
have is not conservatism.

## What each run does

Per corner, two OpenROAD sessions:

1. **at the P&R run's own 50 ns (20 MHz) constraint** — read liberty + tech
   LEF + cell LEF + the committed DEF, `set_propagated_clock` (the CTS tree
   in the DEF is timed as a real tree, not an ideal clock), OpenRCX
   `extract_parasitics` → SPEF → `read_spef`, then worst setup/hold slack,
   TNS, clock skew, `report_power`, `report_design_area`, `check_setup`, and
   an **Fmax found by bisecting the clock period** rather than extrapolated
   from one slack number;
2. **at 1 MHz** ([DR-0003]'s ratified raw rate, one raw bit per `clk` edge) —
   the same session shape, for the power point that is directly comparable
   with `design/digital_power_estimate.py`'s library-based estimate.

Two sessions rather than one because OpenSTA caches a design's clock-derived
activity densities at the first power query: re-creating the clock at a new
period inside one session updates every slack correctly but leaves
`report_power`'s switching term at the old rate. `run_sta.py`'s `_tcl`
docstring records the live evidence for that.

Each record's raw output is the generated Tcl and the full OpenROAD log for
both sessions. The SPEF (3.3 MB per corner) is **not** committed; its sha256,
byte size and summed capacitance are, so a re-run is checkable against the
record.

## Reading the results

The fifteen records are `sim/records/<date>-digital-sta-power-<nn>.md`.
Read them through `sim/characterization-digital-sta-area-power.md`, which
aggregates them into the Fmax / area / power answer, and
`python3 sim/tools/digital_corner_characterization.py`, which re-derives
every figure in that document from the records themselves.

## What this is not

- Not signoff. Real extraction, but not a foundry-signed one; and the DEF it
  reads has no power delivery at all (#171, klayout-tools#1091), so nothing
  here sees IR drop.
- Not a supply-current measurement. Power carries a declared uniform
  switching activity (0.25 transitions/net/cycle, duty 0.5), chosen to match
  the estimate it is compared against. Leakage is the one column with no
  activity assumption in it.
- Not a re-run of the flow. The placement and routing are #111's, unchanged;
  re-placing per corner would make the corner sweep a sweep of fifteen
  different designs.
- Not an I/O timing result. The design carries no `set_input_delay` /
  `set_output_delay`, so port paths are unconstrained; every record states
  how many endpoints that leaves untimed.

[DR-0003]: ../../../spec/decision-records/DR-0003-throughput-defined-at-the-raw-tap.md
[DR-0021]: ../../../spec/decision-records/DR-0021-gate-level-timing-and-power-records.md
