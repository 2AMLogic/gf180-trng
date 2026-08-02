---
record: 2026-08-02-sampler-dff-setup-hold-30
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
  temperature: -40

analysis:
  type: tran
  tstop: 6.5u
  tstep: 100p (print step; ngspice's own LTE sets the actual solver step -- see the testbench header for why 100p, not this repo's usual 1p)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-02-sampler-dff-setup-hold-30/
  files:
    - fs_-40c_3.63v.spice  sha256:06280b35203e404aa49f26af1461a483cca99d5877370f3731ad0e388de83252
    - fs_-40c_3.63v.log  sha256:c5a37f15728aaea0dfb831a4e93ce65985f8400b0293033f7747e0fca511efd2
wall_time: 1.9m
---

## Result

- `tpd_clk_q_rise_s`: 8.660000e-11
- `tpd_clk_q_fall_s`: 8.600000e-11
- `q_rst_v`: 1.546432e-08
- `q_e1_v`: 3.63
- `q_e2_v`: 1.810233e-05
- `q_e4_v`: 2.413405e-06
- `q_e3_1ns_v`: 8.402205e-05
- `q_e3_10ns_v`: 2.808632e-06
- `q_e3_100ns_v`: 2.665809e-06
- `q_e3_drift_v`: -8.135624e-05
- `q_e3_rail_dev_v`: 2.665809e-06
- `q_e5_1ns_v`: 3.63043
- `q_e5_10ns_v`: 3.63
- `q_e5_100ns_v`: 3.63
- `q_e5_drift_v`: -4.300000e-04
- `q_e5_rail_dev_v`: 3.052669e-12
- `q_e6_v`: -3.266611e-06
- `q_e7_1ns_v`: 3.62918
- `q_e7_10ns_v`: 3.63
- `q_e7_100ns_v`: 3.63
- `q_e7_drift_v`: 8.220000e-04
- `q_e7_rail_dev_v`: 2.000003e-06

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-setup-hold --corners fs --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (fs / 3.63 V / -40 C). Says nothing about any other corner.
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
