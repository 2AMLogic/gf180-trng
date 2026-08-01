---
record: 2026-08-01-rostage-noise-04
date: 2026-08-01T11:06:15Z
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
  path: sim/records/raw/2026-08-01-rostage-noise-04/
  files:
    - ss_125c_2.97v.spice  sha256:48f682911fd4321b5d38f14a812cb93862979461faabeb2b69413722ee0012a3
    - ss_125c_2.97v.log  sha256:f156f6acae01d30a546ae4bce09783d09fd793b75781c36f6f24c04fa5cd124b
wall_time: 0.2s
---

## Result

- `vtrip`: 1.06279
- `v_starve_p_node`: 2.3047
- `v_starve_n_node`: 0.176824
- `gain_1meg`: 23.8183
- `gain_100meg`: 11.1414
- `gain_1g`: 1.68437
- `inoise_dens_1meg`: 1.187427e-07
- `inoise_dens_10meg`: 6.383761e-08
- `inoise_dens_100meg`: 5.415281e-08
- `inoise_dens_1g`: 4.305884e-08
- `inoise_dens_10g`: 2.543287e-08
- `onoise_dens_1meg`: 2.828245e-06
- `onoise_dens_1g`: 7.252716e-08
- `onoise_rms_1k_100g`: 0.014177
- `onoise_rms_100meg_100g`: 0.00672036

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py rostage-noise --corners ss --temps 125 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
