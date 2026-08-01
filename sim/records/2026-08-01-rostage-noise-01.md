---
record: 2026-08-01-rostage-noise-01
date: 2026-08-01T11:06:10Z
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
  - /home/ubuntu/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-42 : Circuit level simulation program"
  platform: Linux-7.0.0-1009-aws-x86_64-with-glibc2.39

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-08-01-rostage-noise-01/
  files:
    - tt_27c_3.30v.spice  sha256:46339dbf12a82948792d2def301cd4a51f9acd640c138377585d20e4f6e54d2d
    - tt_27c_3.30v.log  sha256:651209fdfe3466fe94382806e5510497eab80b5e8f128a33ecd166e24178d740
wall_time: 1.4s
---

## Result

- `vtrip`: 1.14079
- `v_starve_p_node`: 2.47673
- `v_starve_n_node`: 0.212274
- `gain_1meg`: 21.112
- `gain_100meg`: 15.4851
- `gain_1g`: 2.59142
- `inoise_dens_1meg`: 1.084304e-07
- `inoise_dens_10meg`: 4.901250e-08
- `inoise_dens_100meg`: 3.677782e-08
- `inoise_dens_1g`: 3.186365e-08
- `inoise_dens_10g`: 1.992890e-08
- `onoise_dens_1meg`: 2.289185e-06
- `onoise_dens_1g`: 8.257198e-08
- `onoise_rms_1k_100g`: 0.0121534
- `onoise_rms_100meg_100g`: 0.00733153

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py rostage-noise --corners tt --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
