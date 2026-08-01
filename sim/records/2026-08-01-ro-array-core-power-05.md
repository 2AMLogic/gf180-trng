---
record: 2026-08-01-ro-array-core-power-05
date: 2026-08-01T12:30:35Z
status: valid

testbench:
  path: sim/tb/ro-array-core-power/tb_ro_array_core_power.sp
  sha: c542a00f2d0da65817f577351bef11876946a32a
netlist:
  path: design/ro_array_core.spice
  sha: 339e858e0010f1ca26412919af47621d40dedf93
repo_commit: c953bc4d235908b512d8c15b5a2e8b4a5bb6b5ec-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /home/ubuntu/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-42 : Circuit level simulation program"
  platform: Linux-7.0.0-1009-aws-x86_64-with-glibc2.39

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran
  tstop: 50n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-ro-array-core-power-05/
  files:
    - ss_-40c_3.63v.spice  sha256:70c494285733db323f248230e5d85f9cdc9ca087530a9a39802aaaeadb6e4c92
    - ss_-40c_3.63v.log  sha256:d7d51dab31490f7e9d5cc85947560c71ff1eb1536c54bbb91a65b71b8346140f
wall_time: 16.3m
---

## Result

- `period_r1`: 6.153700e-09
- `period_r2`: 5.796314e-09
- `f_r1`: 1.625039e+08
- `f_r2`: 1.725234e+08
- `i_r1_a`: -2.204149e-05
- `i_r2_a`: -2.354912e-05
- `i_tree_a`: -1.963719e-05
- `e_cycle_r1_j`: -4.923613e-13
- `c_eff_node_r1_f`: -3.396863e-15
- `ring_swing_v`: 3.72673
- `xo_swing_v`: 3.71436
- `i_total_a`: -6.522780e-05
- `p_rings_w`: -1.654939e-04
- `p_total_w`: -2.367769e-04
- `xo_trans_per_s`: 6.700545e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power --corners ss --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
