---
record: 2026-09-06-ro-array-core-startup-extracted-01
date: 2026-09-06T22:37:51Z
status: valid
level: extracted

testbench:
  path: sim/tb/ro-array-core-startup-extracted/tb_ro_array_core_startup_extracted.sp
  sha: c175911b4ee9320acd1b6d980dd5af59e133c9eb
netlist:
  path: layout/pex/ro_array_core.extracted.spice
  sha: 5a3aefd5e03c44c66f87213e6491332cd6650d60
repo_commit: 01b6c4d060ddff949cba90c49762d7d9059c431a-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: Linux-7.0.0-1010-aws-x86_64-with-glibc2.39

corner:
  process: ss
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: tran
  tstop: 180n
  tstep: 2p (print step; ngspice's own LTE sets the actual solver step). 2p resolves an edge crossing to well under a picosecond after `meas`'s linear interpolation, against period estimates of 4-13 ns -- i.e. below 1e-4 of the quantity being compared for convergence.
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-09-06-ro-array-core-startup-extracted-01/
  files:
    - ss_125c_2.97v.spice  sha256:ab427daa43926d03c6eb63286987b6a9433b85854438b5781ffeb0f7db600ff1
    - ss_125c_2.97v.log  sha256:ac638f248055b6da1e2b8cda214768f06974db3aa7d272bf38df90bcae862b02
wall_time: 37.4s
---

## Result

- `en_assert_s`: 5.000000e-09
- `t1r1_s`: 2.057390e-08
- `t2r1_s`: 3.645546e-08
- `t3r1_s`: 5.234646e-08
- `t4r1_s`: 6.825988e-08
- `t5r1_s`: 8.422208e-08
- `t6r1_s`: 1.002002e-07
- `t7r1_s`: 1.161546e-07
- `t8r1_s`: 1.321509e-07
- `t9r1_s`: 1.481063e-07
- `t10r1_s`: 1.641303e-07
- `t1r2_s`: 1.957901e-08
- `t2r2_s`: 3.435063e-08
- `t3r2_s`: 4.921552e-08
- `t4r2_s`: 6.411070e-08
- `t5r2_s`: 7.900213e-08
- `t6r2_s`: 9.390731e-08
- `t7r2_s`: 1.088771e-07
- `t8r2_s`: 1.237692e-07
- `t9r2_s`: 1.387205e-07
- `t10r2_s`: 1.536948e-07
- `t1xo_s`: 2.028509e-08
- `t2xo_s`: 2.756458e-08
- `t3xo_s`: 3.506128e-08
- `t4xo_s`: 4.233542e-08
- `ring_swing_early_v`: 3.07061
- `ring_swing_late_v`: 3.07988
- `xo_swing_early_v`: 3.04438
- `xo_swing_late_v`: 3.04898
- `v_ro1_off_v`: 2.97
- `v_xo_off_v`: 1.301915e-07

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-startup-extracted --corners ss --temps 125 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist ro_array_core.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, device-level-parasitic-annotated (layout/pex/build.py); NOT a full assembled-ring/inter-region routing extraction -- see layout/pex/build.py's own module docstring and sim/characterization-post-layout-extracted.md for exactly what this does and does not capture.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for time-to-first-valid (ss/+125 C/2.97 V), per issue #17's acceptance criteria ('spec table confirmed at the worst corner post-layout'), not the full 27-point grid.
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
