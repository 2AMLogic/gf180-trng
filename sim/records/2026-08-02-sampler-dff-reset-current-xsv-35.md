---
record: 2026-08-02-sampler-dff-reset-current-xsv-35
date: 2026-08-02T00:01:50Z
status: valid

testbench:
  path: sim/tb/sampler-dff-reset-current-xsv/tb_sampler_dff_reset_current_xsv.sp
  sha: cac6272146084909a3ff6ac2a8afdc957425ef13
netlist:
  path: design/sampler_core.spice
  sha: 50bc082dc2798c8b98e4ced8ebb70432549aa2ec
repo_commit: dc8570a59d334bdeec04c2e284ed2dbe14a6e0de-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: fs bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: fs
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-08-02-sampler-dff-reset-current-xsv-35/
  files:
    - fs_125c_3.30v.spice  sha256:cf78d709c7fd313f058161e76cbaad6315198feb4f3b621444a84d39d8b5f6d7
    - fs_125c_3.30v.log  sha256:37ca064f2239acf3b2f6e450ac41567e04bfc4e7d9d93fdbdeb676eef4ea7ec2
wall_time: 3.2s
---

## Result

- `i_reset_xsv_a`: 2.095100e-09
- `p_reset_xsv_w`: 6.913832e-09
- `v_q`: 3.059726e-08
- `v_m`: 3.29999
- `v_mb`: 3.29999
- `v_qb`: 3.3

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-reset-current-xsv --corners fs --temps 125 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (fs / 3.30 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Models the WORST-CASE phase relationship (clk held at 0 for the whole reset assertion), not any specific power-on sequence -- how long reset is actually asserted, and at what clk phase, is a system-level timing question #26 owns, not measured here.
- What this current IS depends on which cell the record ran against, and the record's netlist.sha says which. Pre-#53 (a reset pulldown on node m): deliberate resistive contention between two simultaneously-ON pass devices, which must NOT be compared against sim/tb/device-leakage-03v3/ or sim/tb/ro-inv-05stage-stopped-leakage/ as if it were the same phenomenon. Post-#53 (reset gated into the latches' inverters, no device on a storage node): that path does not exist and what is left is ordinary off-device leakage at this bias.
- xsv's D is wired directly to vdd in design/sampler_core.spice, so this DC bias is exactly xsv's real condition during a clk-low, reset-asserted interval -- not an approximation of it.
- A DC operating point says nothing about what happens at a clk EDGE while reset is asserted. Post-#53 that is the case the cell's reset structure turns on (see design/xschem/sampler_dff.sch's header); it is not measured by this testbench.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
