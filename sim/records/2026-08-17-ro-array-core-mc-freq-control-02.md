---
record: 2026-08-17-ro-array-core-mc-freq-control-02
date: 2026-08-17T01:26:25Z
status: valid

testbench:
  path: sim/tb/ro-array-core-mc-freq-control/tb_ro_array_core_mc_freq_control.sp
  sha: f703db315527996480bfb45d64b215ebdd9b42e6
netlist:
  path: design/ro_array_core.spice
  sha: fd0aa75500320b36f980126377e3d07c71c0e6b1
repo_commit: 4da0bea1c43e66c3424fb5acd16a4cb30b538bba-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-47 : Circuit level simulation program"
  platform: macOS-26.6.1-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: 125

analysis:
  type: mc
  tstop: 100n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 3
seeds: [1, 2, 3]

raw:
  path: sim/records/raw/2026-08-17-ro-array-core-mc-freq-control-02/
  files:
    - ss_125c_3.63v-run0.spice  sha256:42003c29f321e69593e62ad539ce475588c90fa8ed4376e7aabaeb650e80702c
    - ss_125c_3.63v-run0.log  sha256:f877845f0bf526d63c8b45cb68b80693f86f3af0bb08624f55ff3bb67a4d2355
    - ss_125c_3.63v-run1.spice  sha256:eef8e5a0dcda4bae689aa55602411d8c39f73071ef2c14f12725079c64b885ff
    - ss_125c_3.63v-run1.log  sha256:2041d8ca6a7e1e0e05690164148c893bf0d590d3e53ee0d962cbbbe4e515b025
    - ss_125c_3.63v-run2.spice  sha256:ada5243cc2f649ecbfa782d840572c34a12fe45495a0c7dd28614e7a8d73354f
    - ss_125c_3.63v-run2.log  sha256:2843aa57ead77d5b9167c84e261eacdec7a31b052bfa08b1424e1efc37e3a323
wall_time: 3.3m
---

## Result

- `period_r1`: mean 9.581143e-09 over 3 seeds (sd 0, 0.0% of mean; min 9.581143e-09, max 9.581143e-09)
- `period_r2`: mean 8.926560e-09 over 3 seeds (sd 0, 0.0% of mean; min 8.926560e-09, max 8.926560e-09)
- `f_r1`: mean 1.043717e+08 over 3 seeds (sd 0, 0.0% of mean; min 1.043717e+08, max 1.043717e+08)
- `f_r2`: mean 1.120252e+08 over 3 seeds (sd 0, 0.0% of mean; min 1.120252e+08, max 1.120252e+08)
- `i_r1_a`: mean -1.507111e-05 over 3 seeds (sd 0, 0.0% of mean; min -1.507111e-05, max -1.507111e-05)
- `i_r2_a`: mean -1.612527e-05 over 3 seeds (sd 0, 0.0% of mean; min -1.612527e-05, max -1.612527e-05)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-mc-freq-control --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-control --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-control --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Same two PVT points as sim/tb/ro-array-core-mc-freq/ (tt/27C/3.30V paired, ss/125C/3.63V paired -- not a 2x2 grid), for direct comparison against that record's spread.
- sw_stat_mismatch=0 makes every device's local mismatch offset multiply to exactly zero regardless of the ngspice `.option seed` in force, so this run is deterministic: the same corner produces bit-identical measurements across every seed. 3 seeds are run (not 8, matching the mismatch-enabled record's count) purely to demonstrate that invariance empirically -- a single seed would already be sufficient given the mechanism, but seeing several distinct seeds collapse to the same number is more convincing evidence than asserting it from the mechanism alone.
- This is a mechanism check, not an independent measurement: it shares its DUT, corner points and measurement expressions with sim/tb/ro-array-core-mc-freq/ by construction, so it cannot show anything that testbench's own deterministic counterpart (sim/tb/ro-array-core-power/) does not already show about the mean device. Its only purpose is to demonstrate the MC record's spread is attributable to sw_stat_mismatch and not to some other source of run-to-run variation.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
