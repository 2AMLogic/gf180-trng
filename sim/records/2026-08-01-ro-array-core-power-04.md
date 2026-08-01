---
record: 2026-08-01-ro-array-core-power-04
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
  - /home/ubuntu/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-42 : Circuit level simulation program"
  platform: Linux-7.0.0-1009-aws-x86_64-with-glibc2.39

corner:
  process: ff
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
  path: sim/records/raw/2026-08-01-ro-array-core-power-04/
  files:
    - ff_-40c_3.63v.spice  sha256:c7f7d6e19d857574ab6067978d8146ad4e44316554364870afe49cc95af9b22e
    - ff_-40c_3.63v.log  sha256:c2ab3538ecf85eccd020d7968e119638c5663306cb28f6bdc81e60cced1c87ac
wall_time: 14.6m
---

## Result

- `period_r1`: 4.285939e-09
- `period_r2`: 4.056380e-09
- `f_r1`: 2.333211e+08
- `f_r2`: 2.465252e+08
- `i_r1_a`: -3.600596e-05
- `i_r2_a`: -3.824208e-05
- `i_tree_a`: -4.015056e-05
- `e_cycle_r1_j`: -5.601791e-13
- `c_eff_node_r1_f`: -3.864746e-15
- `ring_swing_v`: 3.65348
- `xo_swing_v`: 3.70257
- `i_total_a`: -1.143986e-04
- `p_rings_w`: -2.695204e-04
- `p_total_w`: -4.152669e-04
- `xo_trans_per_s`: 9.596926e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-power --corners ff --temps -40 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
