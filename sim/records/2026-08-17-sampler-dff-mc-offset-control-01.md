---
record: 2026-08-17-sampler-dff-mc-offset-control-01
date: 2026-08-17T01:17:52Z
status: valid

testbench:
  path: sim/tb/sampler-dff-mc-offset-control/tb_sampler_dff_mc_offset_control.sp
  sha: b35cac33d0f0b6d488777133d6e4d59566fdec15
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
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
  tstop: n/a (op-point analysis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 3
seeds: [1, 2, 3]

raw:
  path: sim/records/raw/2026-08-17-sampler-dff-mc-offset-control-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:6c8ee0abbe23a8792e60905a8e7f9cb6a8f7f431bdeea927db01fc7c334b5c60
    - tt_27c_3.30v-run0.log  sha256:fe3dda04a4d2e03f2555950f92d820c3e7f8dfa692395b36210e40c5b6088e4f
    - tt_27c_3.30v-run1.spice  sha256:d8e9618e148394769c7d64d076593067360b7a634476bfcfa2f23ff76928c1fc
    - tt_27c_3.30v-run1.log  sha256:a6472d368802ab323c6fe229943a3e57bdf2cc2780d0730f063fefdf09ca1610
    - tt_27c_3.30v-run2.spice  sha256:cec7c897505f91d2db8f2c28a14a5215721877ed61b2d0ca6d83481d66fb1ee5
    - tt_27c_3.30v-run2.log  sha256:1d249ec9fb4739602c10e831c6d8053d0dc082c12e2e80e973290cbcc37bf04a
wall_time: 1.5s
---

## Result

- `dtrip_v`: mean 1.38691 over 3 seeds (sd 0, 0.0% of mean; min 1.38691, max 1.38691)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-mc-offset-control --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset-control --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset-control --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Same two PVT points as sim/tb/sampler-dff-mc-offset/ (tt/27C/3.30V paired, ss/125C/3.63V paired -- not a 2x2 grid), for direct comparison against that record's spread.
- sw_stat_mismatch=0 makes every device's local mismatch offset multiply to exactly zero regardless of the ngspice `.option seed` in force, so this run is deterministic: the same corner produces bit-identical dtrip_v across every seed. 3 seeds are run (not 30, matching the mismatch-enabled record's count) purely to demonstrate that invariance empirically -- a single seed would already be sufficient given the mechanism, but seeing several distinct seeds collapse to the same number is more convincing evidence than asserting it from the mechanism alone.
- This is a mechanism check, not an independent measurement: it shares its DUT, corner points and measurement expressions with sim/tb/sampler-dff-mc-offset/ by construction, so it cannot show anything sim/tb/sampler-dff-setup-hold/ (this cell's deterministic characterization) does not already show about the mean device. Its only purpose is to demonstrate the MC record's spread is attributable to sw_stat_mismatch and not to some other source of run-to-run variation.
- Measures the MASTER LATCH's own decision threshold (node xdut.mb) with clk held at 0 throughout, not a full clocked capture -- see sim/tb/sampler-dff-mc-offset/'s tb.json for the same caveat restated in full.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
