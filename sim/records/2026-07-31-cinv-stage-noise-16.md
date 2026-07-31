---
record: 2026-07-31-cinv-stage-noise-16
date: 2026-07-31T19:21:24Z
status: valid

testbench:
  path: sim/tb/cinv-stage-noise/tb_cinv_stage.sp
  sha: 35985181857b11df10f9a71f1306c2ed4a1eb34a
netlist:
  path: sim/tb/cinv-stage-noise/tb_cinv_stage.sp
  sha: 35985181857b11df10f9a71f1306c2ed4a1eb34a
repo_commit: 5988414021b3c1b1ea109dadc6097ae4e62000b3-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: noise
  tstop: n/a (small-signal: .ac and .noise, 1 kHz - 100 GHz)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-07-31-cinv-stage-noise-16/
  files:
    - ff_125c_2.97v.spice  sha256:10b72cbe41d5d81a4b03570a98e20440b8999fbceef7c3c8b079b162ee7b8c6d
    - ff_125c_2.97v.log  sha256:b029beeeafc40e8f4d95b0bb84dbcebcf3e267a10546b83ddbb26ec9a30d059f
wall_time: 1.2s
---

## Result

- `vtrip`: 1.36961
- `vbias_n`: 1.56006
- `vbias_p`: 0.933926
- `gain_1meg`: 16.6793
- `gain_100meg`: 15.3941
- `gain_1g`: 3.92198
- `inoise_dens_1meg`: 4.251557e-08
- `inoise_dens_10meg`: 1.846457e-08
- `inoise_dens_100meg`: 1.337824e-08
- `inoise_dens_1g`: 1.250845e-08
- `inoise_dens_10g`: 1.131142e-08
- `onoise_dens_1meg`: 7.091305e-07
- `onoise_dens_1g`: 4.905785e-08
- `onoise_rms_1k_100g`: 0.0047218
- `onoise_rms_100meg_100g`: 0.00360811

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners ff --temps 125 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
