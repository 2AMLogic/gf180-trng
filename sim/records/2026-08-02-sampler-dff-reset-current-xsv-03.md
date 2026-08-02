---
record: 2026-08-02-sampler-dff-reset-current-xsv-03
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.630 V (nominal 3.3 V, +10%)
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
  path: sim/records/raw/2026-08-02-sampler-dff-reset-current-xsv-03/
  files:
    - tt_-40c_3.63v.spice  sha256:b7f815adf76dacfc39c1913a3f357fd999a06e71555dccb46cd9338b213926a0
    - tt_-40c_3.63v.log  sha256:4548fd29a451175498ca6e03bda83158c2743f9cf6ccd27be583a8a3c7f53c7d
wall_time: 3.2s
---

## Result

- `i_reset_xsv_a`: 5.335297e-11
- `p_reset_xsv_w`: 1.936713e-10
- `v_q`: 1.642808e-08
- `v_m`: 3.63
- `v_mb`: 3.63
- `v_qb`: 3.63

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-reset-current-xsv --corners tt --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.63 V / -40 C). Says nothing about any other corner.
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
