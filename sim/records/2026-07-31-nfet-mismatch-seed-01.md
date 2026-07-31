---
record: 2026-07-31-nfet-mismatch-seed-01
date: 2026-07-31T12:27:20Z
status: valid

testbench:
  path: sim/tb/nfet-mismatch-seed/tb_mismatch.sp
  sha: eea037431e9f7b6004ad5ebfec37e0cfb9e641d5
netlist:
  path: sim/tb/nfet-mismatch-seed/tb_mismatch.sp
  sha: eea037431e9f7b6004ad5ebfec37e0cfb9e641d5
repo_commit: 5119b522803b1811c1b63841a215cfd17754f168-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: statistical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: mc
  tstop: n/a (op-point analysis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 3
seeds: [1, 1, 42]

raw:
  path: sim/records/raw/2026-07-31-nfet-mismatch-seed-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:8406f7f39ad18415d7c9001deba6bd21cc91195582caae98a26a461f3950dfae
    - tt_27c_3.30v-run0.log  sha256:b5fa76cbf92bab319fd8f6d7faec6ba23d27ab4f8c4f0f14aa6d409acc6621d3
    - tt_27c_3.30v-run1.spice  sha256:8406f7f39ad18415d7c9001deba6bd21cc91195582caae98a26a461f3950dfae
    - tt_27c_3.30v-run1.log  sha256:b5fa76cbf92bab319fd8f6d7faec6ba23d27ab4f8c4f0f14aa6d409acc6621d3
    - tt_27c_3.30v-run2.spice  sha256:ac5bd2412e4d2c1bf73d46ac0732e760a19dc73077685d40ea649216f7ebacc1
    - tt_27c_3.30v-run2.log  sha256:5ee97dd21ffb64c40eff668ae62b5757d00697985306039515f207a22987556f
wall_time: 3.3s
---

## Result

- `id`: mean 2.749631e-04 over 3 seeds (min 2.748425e-04, max 2.752043e-04)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py nfet-mismatch-seed --corners tt --temps 27 --seeds 1 --no-write
python3 sim/run_corners.py nfet-mismatch-seed --corners tt --temps 27 --seeds 1 --no-write
python3 sim/run_corners.py nfet-mismatch-seed --corners tt --temps 27 --seeds 42 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.
- corner.process (tt) is bookkeeping only for this testbench -- the actually-loaded model section is statistical (see pdk.models), which replaces the plain per-family corner sections.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
