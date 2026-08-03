---
record: 2026-08-03-ro-array-core-startup-04
date: 2026-08-03T00:25:13Z
status: valid

testbench:
  path: sim/tb/ro-array-core-startup/tb_ro_array_core_startup.sp
  sha: 0d2e5bc07b1bee20d18d79e79de86b2bb4493417
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
  temperature: 27

analysis:
  type: tran
  tstop: 180n
  tstep: 2p (print step; ngspice's own LTE sets the actual solver step). 2p resolves an edge crossing to well under a picosecond after `meas`'s linear interpolation, against period estimates of 4-13 ns -- i.e. below 1e-4 of the quantity being compared for convergence.
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-03-ro-array-core-startup-04/
  files:
    - tt_27c_2.97v.spice  sha256:eb979f43f15e34443e01cd5dd68401a90338200b5b483e0b0ee09e05b41543d8
    - tt_27c_2.97v.log  sha256:9f91406d96daf4133321ff8c15340611c4801c5548833b2ce10ddb1a7f646e4b
wall_time: 1.9m
---

## Result

- `en_assert_s`: 5.000000e-09
- `t1r1_s`: 1.262407e-08
- `t2r1_s`: 2.017169e-08
- `t3r1_s`: 2.771919e-08
- `t4r1_s`: 3.526659e-08
- `t5r1_s`: 4.281400e-08
- `t6r1_s`: 5.036141e-08
- `t7r1_s`: 5.791193e-08
- `t8r1_s`: 6.545600e-08
- `t9r1_s`: 7.300208e-08
- `t10r1_s`: 8.054816e-08
- `t1r2_s`: 1.211205e-08
- `t2r2_s`: 1.915534e-08
- `t3r2_s`: 2.619861e-08
- `t4r2_s`: 3.324188e-08
- `t5r2_s`: 4.028512e-08
- `t6r2_s`: 4.732801e-08
- `t7r2_s`: 5.437160e-08
- `t8r2_s`: 6.141455e-08
- `t9r2_s`: 6.845775e-08
- `t10r2_s`: 7.550099e-08
- `t1xo_s`: 8.646393e-09
- `t2xo_s`: 1.233691e-08
- `t3xo_s`: 1.569145e-08
- `t4xo_s`: 1.937927e-08
- `ring_swing_early_v`: 3.06434
- `ring_swing_late_v`: 3.06398
- `xo_swing_early_v`: 3.0825
- `xo_swing_late_v`: 3.12423
- `v_ro1_off_v`: 2.97
- `v_xo_off_v`: 4.291307e-08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-startup --corners tt --temps 27 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Deterministic (noiseless) transient started from the operating point ngspice solves with en = 0. That state is unique and stable -- ro_nand2's output is forced high independently of its ring input, so the loop gain is zero -- which is why this deck needs no .ic kick and why its start-up time is not an artefact of one. What it does assume is that the real block's idle state is that same clamped state: it says nothing about a supply ramp (vdd is a step-free DC source here, up from t = 0), about power-gated restart, or about start-up out of a partially-collapsed rail.
- A real ring on real silicon leaves its clamped state through a deterministic NAND transition, exactly as modelled here, so unlike a symmetric-equilibrium start this measurement does not depend on noise to get going. It does, however, ignore noise entirely: run-to-run variation in start-up time caused by device noise is not measured, and no seed applies.
- 27-point grid: {tt, ff, ss} x {-40, 27, 125} C x {2.97, 3.30, 3.63} V -- identical to sim/tb/ro-array-core-pvt-q/, so a start-up time can be compared to the steady period at the same PVT point. fs/sf are not covered (DR-0006).
- Reports EDGE TIMES and SWINGS, not a start-up verdict. sim/tools/time_to_first_valid.py applies the period-convergence tolerance and derives the elapsed start-up time from these raw numbers, so the tolerance is visible and re-derivable rather than frozen into the record.
- Ten rising edges (nine period estimates) per ring is a fixed budget. At the slowest grid point (ss/125 C/2.97 V, steady period 13.2 ns per sim/tb/ro-array-core-pvt-q/) ten edges land near 137 ns, inside the 180 ns tstop; if any corner had not converged by its tenth edge the tool reports that explicitly rather than extrapolating.
- The early swing window (20-50 ns after t = 0, i.e. 15-45 ns after en) is a FIXED window in absolute time, not a fixed number of periods, so it spans about 7 periods at the fastest corner and about 2.3 at the slowest. It is a settling check, not a per-period amplitude characterisation; sim/tb/ro-array-core-pvt-q/ remains the steady-state swing evidence.
- The sampler is not present in this deck. It measures when the ARRAY is running and when xo is a clean digitiser input, not when a raw bit is valid -- the sampler's own reset-release-to-first-capture behaviour is sim/tb/sampler-dff-reset-clocked/'s, and the digital blocks' warm-up is behavioural (DR-0009). sim/tools/time_to_first_valid.py is where the three are combined.
- The per-ring measurements (t1r1_s..t10r2_s, ring_swing_early_v, ring_swing_late_v, v_ro1_off_v) address v(xdut.rn1)/v(xdut.rn2) since #78 -- each RING'S OWN output node, the same physical node the pre-#65 records of this family measured as v(xdut.ro1). ro_array_core's ro1/ro2 ports now carry the per-ring output BUFFERS' outputs (DR-0018), which are the complement of the ring node and one buffer delay later; those ports are connected but unmeasured here. The record keys keep their historical names so this family's start-up times remain directly comparable across #65's pin promotion and #78's buffer adoption. What the sampler sees is the combined node xo, which is measured and is driven through the buffers.
- vddr1, vddr2 and the XOR tree's vdd are tied to one supply node here. This deck measures no current, so the per-branch split sim/tb/ro-array-core-power/ needs is not reproduced; a start-up ENERGY figure is therefore not available from this record.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
