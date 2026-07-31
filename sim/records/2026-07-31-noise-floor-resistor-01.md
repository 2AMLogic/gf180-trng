---
record: 2026-07-31-noise-floor-resistor-01
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
  temperature: -40

analysis:
  type: noise
  tstop: n/a (small-signal .noise sweep 1 kHz - 1 MHz)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-07-31-noise-floor-resistor-01/
  files:
    - tt_-40c_3.30v.spice  sha256:2dcc6cd85f65096e0b859242a3d5803068184f0fd6cbfbfb2cdf919e93433dd1
    - tt_-40c_3.30v.log  sha256:789141e3d09b61c7dc0458cf5253a5f1f08a1ddc1e172ca5f8d9091e9735d6e8
wall_time: 1.3s
---

## Result

- `onoise_dens_1k`: 2.537314e-09
- `onoise_dens_1meg`: 2.537314e-09
- `inoise_dens_1k`: 5.074629e-09
- `onoise_total_1k_1meg`: 2.536045e-06
- `inoise_total_1k_1meg`: 5.072091e-06

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py noise-floor-resistor --corners tt --temps -40 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / -40 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
