---
record: 2026-07-31-inv-stage-noise-06
date: 2026-07-31T19:21:24Z
status: valid

testbench:
  path: sim/tb/inv-stage-noise/tb_inv_stage.sp
  sha: 2e89f1cafd31c265306f1ffda5be7181c34909fe
netlist:
  path: sim/tb/inv-stage-noise/tb_inv_stage.sp
  sha: 2e89f1cafd31c265306f1ffda5be7181c34909fe
repo_commit: 5988414021b3c1b1ea109dadc6097ae4e62000b3-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 27

analysis:
  type: noise
  tstop: n/a (small-signal: .ac and .noise, 1 kHz - 100 GHz)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-07-31-inv-stage-noise-06/
  files:
    - tt_27c_3.63v.spice  sha256:c7ca57c75c253f0f21dc6afdf28eec0fb02d1e6f4fbd833ce44770475847267a
    - tt_27c_3.63v.log  sha256:9c57104cea0c452a9ce8c4a6f7cae450c4e6b7704b06c65043bb088a9cab9ca4
wall_time: 1.6s
---

## Result

- `vtrip`: 1.69575
- `gain_1meg`: 17.0617
- `gain_100meg`: 16.7951
- `gain_1g`: 8.32611
- `inoise_dens_1meg`: 4.261335e-08
- `inoise_dens_10meg`: 1.567164e-08
- `inoise_dens_100meg`: 8.597658e-09
- `inoise_dens_1g`: 7.414218e-09
- `inoise_dens_10g`: 7.090275e-09
- `onoise_dens_1meg`: 7.270562e-07
- `onoise_dens_1g`: 6.173157e-08
- `onoise_rms_1k_100g`: 0.00450299
- `onoise_rms_100meg_100g`: 0.00360365

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners tt --temps 27 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.63 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
