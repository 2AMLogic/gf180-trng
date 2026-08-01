---
record: 2026-08-01-sampler-dff-reset-current-xsv-36
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: fs bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: fs
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: dc
  tstop: n/a (operating-point analysis: no time axis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-sampler-dff-reset-current-xsv-36/
  files:
    - fs_125c_3.63v.spice  sha256:9715595d50f384dc3effa408f793c200d8db90098fd368dae6d5168c0c1c44fb
    - fs_125c_3.63v.log  sha256:6b55b5a5a990043e05c3bb90638d4001295689b7e53704c1be53a7f5a11520d4
wall_time: 1.1s
---

## Result

- `i_reset_xsv_a`: 2.100899e-04
- `p_reset_xsv_w`: 7.626264e-04
- `v_q`: 3.194494e-08
- `v_m`: 1.03363
- `v_rst`: 3.62999

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-reset-current-xsv --corners fs --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (fs / 3.63 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Models the WORST-CASE phase relationship (clk held at 0 for the whole reset assertion), not any specific power-on sequence -- how long reset is actually asserted, and at what clk phase, is a system-level timing question #26 owns, not measured here.
- This is deliberate resistive contention between two simultaneously-ON pass devices, not subthreshold/junction leakage -- do not compare this current directly against sim/tb/device-leakage-03v3/ or sim/tb/ro-inv-05stage-stopped-leakage/ figures as if they were the same phenomenon.
- xsv's D is wired directly to vdd in design/sampler_core.spice, so this DC bias is exactly xsv's real condition during a clk-low, reset-asserted interval -- not an approximation of it.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
