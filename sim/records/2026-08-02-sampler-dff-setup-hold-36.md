---
record: 2026-08-02-sampler-dff-setup-hold-36
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
  voltage: 3.630 V (nominal 3.3 V, +10%)
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
  path: sim/records/raw/2026-08-02-sampler-dff-setup-hold-36/
  files:
    - fs_125c_3.63v.spice  sha256:b9a06aecef45ed01c02b7f59bd8ba2e5f63758deed4d3193c366216a70fd99e7
    - fs_125c_3.63v.log  sha256:2d6357053f1a534cdb53a4b767fed43aa311521ddba7a5e188cfa7de6db0fc17
wall_time: 2.0m
---

## Result

- `tpd_clk_q_rise_s`: 1.159000e-10
- `tpd_clk_q_fall_s`: 1.160000e-10
- `q_rst_v`: 3.194480e-08
- `q_e1_v`: 3.62999
- `q_e2_v`: -9.650263e-06
- `q_e4_v`: 3.951400e-06
- `q_e3_1ns_v`: 3.847693e-05
- `q_e3_10ns_v`: -1.842794e-06
- `q_e3_100ns_v`: -1.755908e-06
- `q_e3_drift_v`: -4.023284e-05
- `q_e3_rail_dev_v`: -1.755908e-06
- `q_e5_1ns_v`: 5.211105e-04
- `q_e5_10ns_v`: 4.468608e-06
- `q_e5_100ns_v`: 4.321638e-06
- `q_e5_drift_v`: -5.167889e-04
- `q_e5_rail_dev_v`: 4.321638e-06
- `q_e6_v`: 3.951248e-06
- `q_e7_1ns_v`: 3.63067
- `q_e7_10ns_v`: 3.62999
- `q_e7_100ns_v`: 3.62999
- `q_e7_drift_v`: -6.800000e-04
- `q_e7_rail_dev_v`: 6.000003e-06

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-setup-hold --corners fs --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (fs / 3.63 V / 125 C). Says nothing about any other corner.
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
