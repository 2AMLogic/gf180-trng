---
record: 2026-07-31-cinv-stage-noise-05
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
  path: sim/records/raw/2026-07-31-cinv-stage-noise-05/
  files:
    - tt_27c_3.30v.spice  sha256:de91871c291945137d2bde28190e1df427b0ab325bbed94deb138c42176d13f6
    - tt_27c_3.30v.log  sha256:a99faf74a25e0ea77bb52c6241e9510705389bee5110425501c2b6908fac7396
wall_time: 1.7s
---

## Result

- `vtrip`: 1.50264
- `vbias_n`: 1.69667
- `vbias_p`: 1.06322
- `gain_1meg`: 20.2898
- `gain_100meg`: 18.6244
- `gain_1g`: 4.60127
- `inoise_dens_1meg`: 3.900462e-08
- `inoise_dens_10meg`: 1.618850e-08
- `inoise_dens_100meg`: 1.109634e-08
- `inoise_dens_1g`: 1.024662e-08
- `inoise_dens_10g`: 9.508021e-09
- `onoise_dens_1meg`: 7.913951e-07
- `onoise_dens_1g`: 4.714749e-08
- `onoise_rms_1k_100g`: 0.00479035
- `onoise_rms_100meg_100g`: 0.00351777

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py cinv-stage-noise --corners tt --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
