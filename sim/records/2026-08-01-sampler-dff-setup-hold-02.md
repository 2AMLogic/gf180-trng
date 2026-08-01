---
record: 2026-08-01-sampler-dff-setup-hold-02
date: 2026-08-01T17:20:37Z
status: valid

testbench:
  path: sim/tb/sampler-dff-setup-hold/tb_sampler_dff_setup_hold.sp
  sha: 1b0599b370c3b1655ec065655d17c880e4f53c9b
netlist:
  path: design/sampler_core.spice
  sha: b884211ac1a7fbaf020472ffc9354d86cb1df74c
repo_commit: c9b72997210073c432e5ff79cccef2b8e717ce89-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
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
  path: sim/records/raw/2026-08-01-sampler-dff-setup-hold-02/
  files:
    - tt_-40c_3.30v.spice  sha256:4741d983369334b8fbb81f40075b5700048c933658d92d46670e435db282a8a3
    - tt_-40c_3.30v.log  sha256:eff4fb17c3f84d6a0dadfdb55fc61a92c46c5d499c665547c41f994291273e9c
wall_time: 2.9m
---

## Result

- `tpd_clk_q_rise_s`: 1.037000e-10
- `tpd_clk_q_fall_s`: 1.100000e-10
- `q_rst_v`: 1.534254e-08
- `q_e1_v`: 3.3
- `q_e2_v`: 3.774955e-06
- `q_e4_v`: 3.530806e-06
- `q_e3_1ns_v`: -2.212843e-06
- `q_e3_10ns_v`: 9.160736e-07
- `q_e3_100ns_v`: 8.701418e-07
- `q_e3_drift_v`: 3.082985e-06
- `q_e3_rail_dev_v`: 8.701418e-07
- `q_e5_1ns_v`: 3.30324
- `q_e5_10ns_v`: 3.3
- `q_e5_100ns_v`: 3.3
- `q_e5_drift_v`: -0.00324
- `q_e5_rail_dev_v`: 9.999967e-07
- `q_e6_v`: -9.284354e-06
- `q_e7_1ns_v`: 3.29994
- `q_e7_10ns_v`: 3.30001
- `q_e7_100ns_v`: 3.3
- `q_e7_drift_v`: 6.000000e-05
- `q_e7_rail_dev_v`: -4.000003e-06

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-setup-hold --corners tt --temps -40 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Characterizes the SAMPLER CELL only. The entropy source is not present: D is an ideal 1 ps digital transition, not the analog xo swing the cell sees in sampler_core. Nothing here is evidence about jitter, min-entropy, or the raw bitstream -- see sim/tb/sampler-array-digitize/ for the cell driven by the real source.
- The setup time is BRACKETED, not measured: this run reports whether the cell captured data arriving 59 ps and 500 ps before the clock edge, which places the setup time inside an interval. It does not sweep the data-to-clock offset, so the interval is as tight as those two points allow and no tighter.
- The metastability stress is one aligned edge per run, deterministically placed. That characterizes how this cell RESOLVES when struck at zero margin; it does not estimate a mean-time-between-failures, which needs a statistical treatment of the resolution time constant this deck does not perform.
- The clock is ideal: no jitter, no duty-cycle error, no finite source impedance. DR-0012 accepts the external clock's own quality as a system-level dependency this repository does not characterize; this record inherits that limit.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
