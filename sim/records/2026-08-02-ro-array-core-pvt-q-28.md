---
record: 2026-08-02-ro-array-core-pvt-q-28
date: 2026-08-02T23:58:41Z
status: valid

testbench:
  path: sim/tb/ro-array-core-pvt-q/tb_ro_array_core_pvt_q.sp
  sha: 0964440e1e8a06efa3a8eb800d75dcf9c1ace733
netlist:
  path: design/ro_array_core.spice
  sha: fd0aa75500320b36f980126377e3d07c71c0e6b1
repo_commit: fdbc373e5ede42fcecd66f63ba5e9b7bb911ba59-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: -40

analysis:
  type: tran
  tstop: 300n
  tstep: 5p (print step; it also caps ngspice's own solver step, which is the reason it is stated rather than left at the default)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-02-ro-array-core-pvt-q-28/
  files:
    - tt_-40c_2.97v.spice  sha256:d962b5dceb5f25caca2090f6574ef66110e66baf6927461208210820e4e65abd
    - tt_-40c_2.97v.log  sha256:902d9c850f60b8c951cd06a34e829dfd93c5ea77b185df94a95b618fb4d0657d
wall_time: 2.8m
---

## Result

- `period_r1`: 5.945855e-09
- `period_r2`: 5.558338e-09
- `f_r1`: 1.681844e+08
- `f_r2`: 1.799099e+08
- `i_r1_a`: -1.743586e-05
- `i_r2_a`: -1.859686e-05
- `i_tree_a`: -1.413062e-05
- `e_cycle_r1_j`: -3.079031e-13
- `c_eff_node_r1_f`: -3.173281e-15
- `ring_swing_v`: 3.14029
- `xo_swing_v`: 3.14045
- `i_total_a`: -5.016333e-05
- `p_rings_w`: -1.070172e-04
- `p_total_w`: -1.489851e-04
- `xo_trans_per_s`: 6.961886e+08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-pvt-q --corners tt --temps -40 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 10); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- fs/sf process corners are NOT covered, per DR-0006's ratified reduced process axis. Every minimum/maximum this record family supports is a minimum/maximum over {tt, ff, ss} only, and does not extend to fs/sf.
- The 5 ps print step also caps ngspice's own solver step (SPICE3 defaults tmax to min(tstep, (tstop-tstart)/50)), which is 5x looser than the 1 ps of sim/tb/ro-array-core-power/. It is the reason a 6x longer window costs the same per point. The two families overlap at three PVT points (tt/27/3.30, ff/-40/3.63, ss/-40/3.63) and sim/tools/worst_corner_entropy.py reports the resulting per-quantity agreement; that comparison, not an assertion, is what justifies reading records from both families as the same measurement.
- Deterministic (mismatch-free, noiseless) transient: one nominal device draw per PVT point. Device mismatch is sim/tb/ro-array-core-mc-freq/'s subject and jitter is sim/tb/ro-ring5-starved-jitter-long/'s; nothing here measures either.
- The swing window (200-295 ns) and the 2nd-to-6th rising-edge measurement window are fixed in simulated time, not in ring periods, so they cover a different NUMBER of periods at fast and slow corners. That is deliberate -- period and integrated charge are both read between like edges an exact integer number of periods apart, so neither depends on how many periods the window happens to span -- but the swing figures are max/min over a fixed 95 ns window and therefore over more periods at fast corners than slow ones.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
