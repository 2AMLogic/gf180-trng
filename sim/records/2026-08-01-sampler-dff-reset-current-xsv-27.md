---
record: 2026-08-01-sampler-dff-reset-current-xsv-27
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
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
  path: sim/records/raw/2026-08-01-sampler-dff-reset-current-xsv-27/
  files:
    - ss_125c_3.63v.spice  sha256:bd852186d023e7a8239ef18b5f37a248958040b23a98263a31bb208e9ff966c5
    - ss_125c_3.63v.log  sha256:1a7397e2816dbbb8907af0b3175b737fde47727a4e38064c8a5fb53a117dcdbd
wall_time: 1.4s
---

## Result

- `i_reset_xsv_a`: 1.640992e-04
- `p_reset_xsv_w`: 5.956802e-04
- `v_q`: 3.429433e-08
- `v_m`: 1.06444
- `v_rst`: 3.63

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-reset-current-xsv --corners ss --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Models the WORST-CASE phase relationship (clk held at 0 for the whole reset assertion), not any specific power-on sequence -- how long reset is actually asserted, and at what clk phase, is a system-level timing question #26 owns, not measured here.
- This is deliberate resistive contention between two simultaneously-ON pass devices, not subthreshold/junction leakage -- do not compare this current directly against sim/tb/device-leakage-03v3/ or sim/tb/ro-inv-05stage-stopped-leakage/ figures as if they were the same phenomenon.
- xsv's D is wired directly to vdd in design/sampler_core.spice, so this DC bias is exactly xsv's real condition during a clk-low, reset-asserted interval -- not an approximation of it.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
