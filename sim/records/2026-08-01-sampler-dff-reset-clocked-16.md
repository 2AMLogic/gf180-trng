---
record: 2026-08-01-sampler-dff-reset-clocked-16
date: 2026-08-01T23:31:56Z
status: valid

testbench:
  path: sim/tb/sampler-dff-reset-clocked/tb_sampler_dff_reset_clocked.sp
  sha: e03927876199ad9124d02640e57956a794f5828c
netlist:
  path: design/sampler_core.spice
  sha: 50bc082dc2798c8b98e4ced8ebb70432549aa2ec
repo_commit: dc8570a59d334bdeec04c2e284ed2dbe14a6e0de-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: tran
  tstop: 6u
  tstep: 100p (print step; ngspice's own LTE sets the actual solver step -- same choice as sim/tb/sampler-dff-setup-hold/, whose header argues it)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-sampler-dff-reset-clocked-16/
  files:
    - ff_125c_2.97v.spice  sha256:a165225a479d6148b58be747276c6a3fcd99fc10a3a7f63cf77395d94ed49b89
    - ff_125c_2.97v.log  sha256:99ef6fab4b2c039e0ea30ee4a6a7490073abbb5f5c1d26d869061ef74de58719
wall_time: 1.9m
---

## Result

- `q_rst_max_v`: 0.114722
- `q_rst_max_frac`: 0.0386269
- `s_rst_min_v`: 2.53263
- `s_rst_dev_frac`: 0.147261
- `mb_rst_min_v`: 2.84504
- `q_rel_v`: 2.493176e-06
- `q_cap_v`: 2.96999

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-reset-clocked --corners ff --temps 125 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Characterizes the SAMPLER CELL only, with an ideal 1 ps-edge clock and an ideal D. The entropy source is not present and nothing here is evidence about jitter, min-entropy or the raw bitstream.
- D is held at vdd for the whole window -- argued in the testbench header as the worst case for this mechanism (it forces the master to disagree with the reset state at every rising edge) and as xsv's literal condition in the shipped block. It is an argument from the topology plus a measurement at that point, not a sweep of D's phase against the clock.
- Three clock periods, one reset release, one release phase (between edges). Releasing rst_n coincident with a clk edge is a separate question this deck does not probe.
- q_cap_v checks that the cell still captures a 1 on the first rising edge after release; it is a functional sanity check on this deck's own stimulus, not a substitute for sim/tb/sampler-dff-setup-hold/'s setup/hold and metastability characterization.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
