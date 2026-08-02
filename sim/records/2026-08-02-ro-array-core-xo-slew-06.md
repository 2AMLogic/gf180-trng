---
record: 2026-08-02-ro-array-core-xo-slew-06
date: 2026-08-02T01:31:51Z
status: valid

testbench:
  path: sim/tb/ro-array-core-xo-slew/tb_ro_array_core_xo_slew.sp
  sha: 4b323ba0de77bff82a0df662f9f1abf1a8ae35f8
netlist:
  path: design/ro_array_core.spice
  sha: 7e3fd56790c30d8501c5b8164dfa0be03f2d1c7e
repo_commit: dc8570a59d334bdeec04c2e284ed2dbe14a6e0de-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 3.300 V (nominal 3.3 V)
  temperature: -40

analysis:
  type: tran
  tstop: 140n (observation window opens at 40n; the ring still starts from t = 0)
  tstep: 2p (print step; it also caps ngspice's own solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-02-ro-array-core-xo-slew-06/
  files:
    - ss_-40c_3.30v.spice  sha256:7451d555f95db38a15bf66d9c9504d6568976cd1912c3dc30f76314c118c03b5
    - ss_-40c_3.30v.log  sha256:1ec78bea2202eaecb0267b0b59c6329f98eb1d6ac12a8ce5ea046e59ed8095b9
wall_time: 11.1m
---

## Result

- `xo_slew_rise_v_per_s`: 3.336338e+10
- `xo_slew_fall_v_per_s`: -4.556479e+10
- `ro1_slew_rise_v_per_s`: 3.225228e+09
- `ro1_slew_fall_v_per_s`: -5.452510e+09
- `ro1_band_slew_a_v_per_s`: 1.459047e+09
- `ro1_band_slew_b_v_per_s`: 1.543932e+09
- `xo_swing_v`: 3.43236

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-xo-slew --corners ss --temps -40 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.30 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- fs/sf process corners are NOT covered, per DR-0006's ratified reduced process axis.
- `max(deriv(v(...)))` is the STEEPEST dV/dt anywhere in the window, not the dV/dt at any particular threshold. A sampler whose decision threshold sits away from the steepest point of the edge sees a slower crossing than this number, so using it to convert a voltage offset into a timing offset UNDERSTATES the timing offset. The 40-60% band figures on the ring node bracket it from the other side: they are an average across the middle fifth of the swing, and the ratio between the two on the same node is what says how much the choice matters.
- The band-crossing figures are measured on the ring node (xdut.ro1), not on xo: xo is the XOR of two independent rings, so its transitions are aperiodic and can include narrow runt pulses that a rise=N edge count would mis-pair across two different levels. That is exactly why the derivative method is used on xo. The ring node carries both methods so they can be compared on the SAME signal.
- Deterministic (mismatch-free, noiseless) transient: one nominal device draw per PVT point, and a slew rate is quoted from a single window rather than averaged over many edges (except the ring node's two band measurements, which are two separate edges).
- Says nothing about the sampler's own input loading: the DUT here drives the testbench's (essentially open) xo node, whereas in design/xschem/sampler_core.sch that node also drives sampler_dff's data transmission gate. A real load slows the edge, so the slew measured here is an upper bound on the loaded slew.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
