---
record: 2026-08-02-sampler-dff-setup-hold-17
date: 2026-08-02T00:59:42Z
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-08-02-sampler-dff-setup-hold-17/
  files:
    - ff_125c_3.30v.spice  sha256:b4b7bee1c290447e55e90b706b4880aab0f9cde05cdfaa6372346443d1875bdc
    - ff_125c_3.30v.log  sha256:dc8c98874a7d42b6e2bbe1a59e69491cdf4e5e0f044472c0e7635487983f92b4
wall_time: 2.3m
---

## Result

- `tpd_clk_q_rise_s`: 1.061000e-10
- `tpd_clk_q_fall_s`: 1.100000e-10
- `q_rst_v`: 6.368210e-07
- `q_e1_v`: 3.29999
- `q_e2_v`: -1.453798e-05
- `q_e4_v`: 3.391468e-06
- `q_e3_1ns_v`: 3.534028e-05
- `q_e3_10ns_v`: -1.724948e-06
- `q_e3_100ns_v`: -1.606296e-06
- `q_e3_drift_v`: -3.694658e-05
- `q_e3_rail_dev_v`: -1.606296e-06
- `q_e5_1ns_v`: -3.436087e-05
- `q_e5_10ns_v`: 4.882042e-06
- `q_e5_100ns_v`: 4.692018e-06
- `q_e5_drift_v`: 3.905289e-05
- `q_e5_rail_dev_v`: 4.692018e-06
- `q_e6_v`: 3.391557e-06
- `q_e7_1ns_v`: 3.30178
- `q_e7_10ns_v`: 3.29999
- `q_e7_100ns_v`: 3.29999
- `q_e7_drift_v`: -0.001785
- `q_e7_rail_dev_v`: 7.999997e-06

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-setup-hold --corners ff --temps 125 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.30 V / 125 C). Says nothing about any other corner.
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
