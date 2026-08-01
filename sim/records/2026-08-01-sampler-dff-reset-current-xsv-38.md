---
record: 2026-08-01-sampler-dff-reset-current-xsv-38
date: 2026-08-01T21:05:52Z
status: valid

testbench:
  path: sim/tb/sampler-dff-reset-current-xsv/tb_sampler_dff_reset_current_xsv.sp
  sha: 673d61fc58404b4e5cd8fbe6ed09e381c8c77db8
netlist:
  path: design/sampler_core.spice
  sha: 127c7959d1940ae2898bc90a268c1b2caa40311e
repo_commit: 443b434c664e2dfd3603837b70c929eef4c5c077-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: sf bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: sf
  voltage: 3.300 V (nominal 3.3 V)
  temperature: -40

analysis:
  type: dc
  tstop: n/a (operating-point analysis: no time axis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-sampler-dff-reset-current-xsv-38/
  files:
    - sf_-40c_3.30v.spice  sha256:e289f2b1c5c87f666a60de763d6d561a1c1f8f9f0311e65e1f0da8f8b19f0e5e
    - sf_-40c_3.30v.log  sha256:fca53c1dd0a4f4190a10986c2e95e286b160ab95016abbee34649d54d266b22c
wall_time: 1.2s
---

## Result

- `i_reset_xsv_a`: 2.119887e-04
- `p_reset_xsv_w`: 6.995628e-04
- `v_q`: 1.635362e-08
- `v_m`: 1.02766
- `v_rst`: 3.3

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-reset-current-xsv --corners sf --temps -40 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (sf / 3.30 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Models the WORST-CASE phase relationship (clk held at 0 for the whole reset assertion), not any specific power-on sequence -- how long reset is actually asserted, and at what clk phase, is a system-level timing question #26 owns, not measured here.
- This is deliberate resistive contention between two simultaneously-ON pass devices, not subthreshold/junction leakage -- do not compare this current directly against sim/tb/device-leakage-03v3/ or sim/tb/ro-inv-05stage-stopped-leakage/ figures as if they were the same phenomenon.
- xsv's D is wired directly to vdd in design/sampler_core.spice, so this DC bias is exactly xsv's real condition during a clk-low, reset-asserted interval -- not an approximation of it.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
