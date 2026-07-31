---
record: 2026-07-31-inv-stage-noise-19
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 2.970 V (nominal 3.3 V, -10%)
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
  path: sim/records/raw/2026-07-31-inv-stage-noise-19/
  files:
    - ss_-40c_2.97v.spice  sha256:8d45a9afce3e6896dfeccf6c75587e744896e3113351364f4b49f7aea8c22684
    - ss_-40c_2.97v.log  sha256:32fe527e1acbf7bd75497077b3ea943f8b2f7d52d785f7f6e91b048201ad5c9e
wall_time: 1.2s
---

## Result

- `vtrip`: 1.36101
- `gain_1meg`: 24.8634
- `gain_100meg`: 23.7512
- `gain_1g`: 7.64462
- `inoise_dens_1meg`: 3.315011e-08
- `inoise_dens_10meg`: 1.258313e-08
- `inoise_dens_100meg`: 7.403869e-09
- `inoise_dens_1g`: 6.581972e-09
- `inoise_dens_10g`: 6.248904e-09
- `onoise_dens_1meg`: 8.242236e-07
- `onoise_dens_1g`: 5.031669e-08
- `onoise_rms_1k_100g`: 0.00462457
- `onoise_rms_100meg_100g`: 0.00340421

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py inv-stage-noise --corners ss --temps -40 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
