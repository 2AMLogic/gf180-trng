---
record: 2026-08-17-ro-array-core-mc-freq-control-01
date: 2026-08-17T01:25:14Z
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-47 : Circuit level simulation program"
  platform: macOS-26.6.1-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: mc
  tstop: 100n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 3
seeds: [1, 2, 3]

raw:
  path: sim/records/raw/2026-08-17-ro-array-core-mc-freq-control-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:4f462acf850e979a12e4f968ea243fefdac52a7fc5c15bfba79adf97b658be13
    - tt_27c_3.30v-run0.log  sha256:b87548d30172c724f2a9feb2340de1bdfc5fdc2ccbbd978ebe2187f4730f9111
    - tt_27c_3.30v-run1.spice  sha256:07c80073510d0ffbda05b9f440197feec96715b7b6f93ada8dba518a950eb3a5
    - tt_27c_3.30v-run1.log  sha256:8cebb728f863488b554ced295c73a2cdb4b9b2eded75100f9c82f5b4dab3bbc9
    - tt_27c_3.30v-run2.spice  sha256:1751780ed266be1d873e1beb9109f8045fd05d4aa7c81e8f1c230071fa2bc770
    - tt_27c_3.30v-run2.log  sha256:39a0b85ace5af7687624af04921b4816e217aeb44d6d1b28a9583e6009466495
wall_time: 3.1m
---

## Result

- `period_r1`: mean 6.677432e-09 over 3 seeds (sd 0, 0.0% of mean; min 6.677432e-09, max 6.677432e-09)
- `period_r2`: mean 6.240492e-09 over 3 seeds (sd 0, 0.0% of mean; min 6.240492e-09, max 6.240492e-09)
- `f_r1`: mean 1.497582e+08 over 3 seeds (sd 0, 0.0% of mean; min 1.497582e+08, max 1.497582e+08)
- `f_r2`: mean 1.602438e+08 over 3 seeds (sd 0, 0.0% of mean; min 1.602438e+08, max 1.602438e+08)
- `i_r1_a`: mean -1.896104e-05 over 3 seeds (sd 0, 0.0% of mean; min -1.896104e-05, max -1.896104e-05)
- `i_r2_a`: mean -2.022904e-05 over 3 seeds (sd 0, 0.0% of mean; min -2.022904e-05, max -2.022904e-05)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-mc-freq-control --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-control --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-core-mc-freq-control --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Same two PVT points as sim/tb/ro-array-core-mc-freq/ (tt/27C/3.30V paired, ss/125C/3.63V paired -- not a 2x2 grid), for direct comparison against that record's spread.
- sw_stat_mismatch=0 makes every device's local mismatch offset multiply to exactly zero regardless of the ngspice `.option seed` in force, so this run is deterministic: the same corner produces bit-identical measurements across every seed. 3 seeds are run (not 8, matching the mismatch-enabled record's count) purely to demonstrate that invariance empirically -- a single seed would already be sufficient given the mechanism, but seeing several distinct seeds collapse to the same number is more convincing evidence than asserting it from the mechanism alone.
- This is a mechanism check, not an independent measurement: it shares its DUT, corner points and measurement expressions with sim/tb/ro-array-core-mc-freq/ by construction, so it cannot show anything that testbench's own deterministic counterpart (sim/tb/ro-array-core-power/) does not already show about the mean device. Its only purpose is to demonstrate the MC record's spread is attributable to sw_stat_mismatch and not to some other source of run-to-run variation.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
