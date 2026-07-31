---
record: 2026-07-31-cinv-stage-noise-04
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 2.970 V (nominal 3.3 V, -10%)
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-04/
  files:
    - tt_27c_2.97v.spice  sha256:01b077027bf4ae1b318f2a198cf2cbc3d02e098bfc089bd65ca6300a439a3d78
    - tt_27c_2.97v.log  sha256:7ca76a17a57b583b20bf41201d047398bbc9b221c5dcba322422abaabd142e30
wall_time: 1.7s
---

## Result

- `vtrip`: 1.35017
- `vbias_n`: 1.60587
- `vbias_p`: 0.86236
- `gain_1meg`: 21.7354
- `gain_100meg`: 19.4904
- `gain_1g`: 4.34094
- `inoise_dens_1meg`: 3.781740e-08
- `inoise_dens_10meg`: 1.590665e-08
- `inoise_dens_100meg`: 1.108722e-08
- `inoise_dens_1g`: 1.030913e-08
- `inoise_dens_10g`: 9.515295e-09
- `onoise_dens_1meg`: 8.219778e-07
- `onoise_dens_1g`: 4.475132e-08
- `onoise_rms_1k_100g`: 0.00485633
- `onoise_rms_100meg_100g`: 0.00346403

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners tt --temps 27 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
