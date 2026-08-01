---
record: 2026-08-01-rostage-noise-03
date: 2026-08-01T11:06:13Z
status: valid

testbench:
  path: sim/tb/rostage-noise/tb_rostage.sp
  sha: 6cb9857afd7816599a1e2937d381885bc84310be
netlist:
  path: design/ro_array_core.spice
  sha: faa556c8ef00db6f2bc7d15b29431ebe0bf24d78
repo_commit: c953bc4d235908b512d8c15b5a2e8b4a5bb6b5ec-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /home/ubuntu/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-42 : Circuit level simulation program"
  platform: Linux-7.0.0-1009-aws-x86_64-with-glibc2.39

corner:
  process: ss
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
  path: sim/records/raw/2026-08-01-rostage-noise-03/
  files:
    - ss_-40c_3.63v.spice  sha256:45fa4d4ea68044b1966e300fe6b96d31e94b89a3ea364d920f1196bffe69c47a
    - ss_-40c_3.63v.log  sha256:94435dc8384364089ceb24419f85e89b0de9184851776fbe984cd7ba7fecf692
wall_time: 0.8s
---

## Result

- `vtrip`: 1.29595
- `v_starve_p_node`: 2.8537
- `v_starve_n_node`: 0.198457
- `gain_1meg`: 24.309
- `gain_100meg`: 18.5027
- `gain_1g`: 3.08051
- `inoise_dens_1meg`: 1.019247e-07
- `inoise_dens_10meg`: 4.324117e-08
- `inoise_dens_100meg`: 3.026261e-08
- `inoise_dens_1g`: 2.681684e-08
- `inoise_dens_10g`: 1.779444e-08
- `onoise_dens_1meg`: 2.477691e-06
- `onoise_dens_1g`: 8.260953e-08
- `onoise_rms_1k_100g`: 0.0123692
- `onoise_rms_100meg_100g`: 0.0073046

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py rostage-noise --corners ss --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
