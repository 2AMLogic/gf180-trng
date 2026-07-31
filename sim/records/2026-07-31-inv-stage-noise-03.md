---
record: 2026-07-31-inv-stage-noise-03
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
  temperature: -40

analysis:
  type: noise
  tstop: n/a (small-signal: .ac and .noise, 1 kHz - 100 GHz)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-07-31-inv-stage-noise-03/
  files:
    - tt_-40c_3.63v.spice  sha256:34891522b8a36140c83bf9e928abe7444393c567828a8a78a1cb9e2351af18f6
    - tt_-40c_3.63v.log  sha256:5ed28b9f0193cd372d5edaab053c31922ef033e7efb52f4a2bbdc5b66dad7ee6
wall_time: 1.7s
---

## Result

- `vtrip`: 1.69249
- `gain_1meg`: 18.1385
- `gain_100meg`: 17.8984
- `gain_1g`: 9.42994
- `inoise_dens_1meg`: 3.863369e-08
- `inoise_dens_10meg`: 1.406678e-08
- `inoise_dens_100meg`: 7.496263e-09
- `inoise_dens_1g`: 6.368146e-09
- `inoise_dens_10g`: 6.111184e-09
- `onoise_dens_1meg`: 7.007571e-07
- `onoise_dens_1g`: 6.005123e-08
- `onoise_rms_1k_100g`: 0.00430725
- `onoise_rms_100meg_100g`: 0.00345175

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners tt --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
