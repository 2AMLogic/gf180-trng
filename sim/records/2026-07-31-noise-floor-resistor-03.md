---
record: 2026-07-31-noise-floor-resistor-03
date: 2026-07-31T19:21:23Z
status: valid

testbench:
  path: sim/tb/noise-floor-resistor/tb_rdiv.sp
  sha: 61ad9f051a064727efcf009a0734c74d49827d92
netlist:
  path: sim/tb/noise-floor-resistor/tb_rdiv.sp
  sha: 61ad9f051a064727efcf009a0734c74d49827d92
repo_commit: 5988414021b3c1b1ea109dadc6097ae4e62000b3-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 125

analysis:
  type: noise
  tstop: n/a (small-signal .noise sweep 1 kHz - 1 MHz)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-07-31-noise-floor-resistor-03/
  files:
    - tt_125c_3.30v.spice  sha256:1ab5a1837cc3ad622ac04ec9cf1b7318bfcf8fb08e4024a9aa02e1c522534411
    - tt_125c_3.30v.log  sha256:668a3faa954e504efea7e1c706a1a020b57d5f0a3432c7990bef4973175138a7
wall_time: 1.4s
---

## Result

- `onoise_dens_1k`: 3.315736e-09
- `onoise_dens_1meg`: 3.315736e-09
- `inoise_dens_1k`: 6.631472e-09
- `onoise_total_1k_1meg`: 3.314078e-06
- `inoise_total_1k_1meg`: 6.628155e-06

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py noise-floor-resistor --corners tt --temps 125 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 125 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
