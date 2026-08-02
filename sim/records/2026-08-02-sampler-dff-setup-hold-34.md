---
record: 2026-08-02-sampler-dff-setup-hold-34
date: 2026-08-02T01:04:32Z
status: valid

testbench:
  path: sim/tb/sampler-dff-setup-hold/tb_sampler_dff_setup_hold.sp
  sha: 37dafbdf68660fdb043b35bf74e07ef0699f25dc
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
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: tran
  tstop: 6.5u
  tstep: 100p (print step; ngspice's own LTE sets the actual solver step -- see the testbench header for why 100p, not this repo's usual 1p)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-02-sampler-dff-setup-hold-34/
  files:
    - fs_125c_2.97v.spice  sha256:780e601b14fbef124940b35879635640c326ac5d07483830d0d4ef15e86bf6c4
    - fs_125c_2.97v.log  sha256:3abb6a895be4721ca744444031440d2f7ce1982c7507aa3e1a30a2742e9c6ae2
wall_time: 2.0m
---

## Result

- `tpd_clk_q_rise_s`: 1.400000e-10
- `tpd_clk_q_fall_s`: 1.290000e-10
- `q_rst_v`: 2.956771e-08
- `q_e1_v`: 2.96999
- `q_e2_v`: -9.535511e-07
- `q_e4_v`: 9.148475e-07
- `q_e3_1ns_v`: 7.939754e-05
- `q_e3_10ns_v`: -3.583063e-06
- `q_e3_100ns_v`: -3.397208e-06
- `q_e3_drift_v`: -8.279475e-05
- `q_e3_rail_dev_v`: -3.397208e-06
- `q_e5_1ns_v`: 8.745402e-05
- `q_e5_10ns_v`: 1.965954e-06
- `q_e5_100ns_v`: 1.858923e-06
- `q_e5_drift_v`: -8.559510e-05
- `q_e5_rail_dev_v`: 1.858923e-06
- `q_e6_v`: 9.148171e-07
- `q_e7_1ns_v`: 2.9697
- `q_e7_10ns_v`: 2.96999
- `q_e7_100ns_v`: 2.96999
- `q_e7_drift_v`: 2.950000e-04
- `q_e7_rail_dev_v`: 7.000001e-06

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-setup-hold --corners fs --temps 125 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (fs / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 9); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Characterizes the SAMPLER CELL only. The entropy source is not present: D is an ideal 1 ps digital transition, not the analog xo swing the cell sees in sampler_core. Nothing here is evidence about jitter, min-entropy, or the raw bitstream -- see sim/tb/sampler-array-digitize/ for the cell driven by the real source.
- The setup time is BRACKETED, not measured: this run reports whether the cell captured data arriving 59 ps and 500 ps before the clock edge, which places the setup time inside an interval. It does not sweep the data-to-clock offset, so the interval is as tight as those two points allow and no tighter.
- The metastability stress is one aligned edge per run, deterministically placed. That characterizes how this cell RESOLVES when struck at zero margin; it does not estimate a mean-time-between-failures, which needs a statistical treatment of the resolution time constant this deck does not perform.
- The clock is ideal: no jitter, no duty-cycle error, no finite source impedance. DR-0012 accepts the external clock's own quality as a system-level dependency this repository does not characterize; this record inherits that limit.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
