---
record: 2026-07-31-corner-sanity-nfet-id-01
date: 2026-07-31T12:27:16Z
status: valid

testbench:
  path: sim/tb/corner-sanity-nfet-id/tb_id.sp
  sha: 513a36916bb9a42a88b31d4a7ed23ece9564b322
netlist:
  path: sim/tb/corner-sanity-nfet-id/tb_id.sp
  sha: 513a36916bb9a42a88b31d4a7ed23ece9564b322
repo_commit: 5119b522803b1811c1b63841a215cfd17754f168-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: op
  tstop: n/a (op-point analysis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-07-31-corner-sanity-nfet-id-01/
  files:
    - tt_27c_3.30v.spice  sha256:212a08539c8edfcace0ba0ae50eab0660abf3ba619cb8e61f709ae6ce88ac7ae
    - tt_27c_3.30v.log  sha256:30a5e620cc2f55f516457697409798fc522113056bfc3713fa917a8f4cacb269
wall_time: 1.1s
---

## Result

- `id`: 0.00274699

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py corner-sanity-nfet-id --corners tt --temps 27 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
