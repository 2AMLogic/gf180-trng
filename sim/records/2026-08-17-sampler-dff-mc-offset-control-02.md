---
record: 2026-08-17-sampler-dff-mc-offset-control-02
date: 2026-08-17T01:17:57Z
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
  tstop: n/a (op-point analysis)
  tstep: n/a
  tmax: n/a
  noise_params: n/a
  runs: 3
seeds: [1, 2, 3]

raw:
  path: sim/records/raw/2026-08-17-sampler-dff-mc-offset-control-02/
  files:
    - ss_125c_3.63v-run0.spice  sha256:97bad37c898086f85e94e5abc7bf1a9b7b9b8520b1a4319d05055f491d3f328e
    - ss_125c_3.63v-run0.log  sha256:372bd19ab054d527564454d3b80673d32eb84368c08c9e32f8f928c95a1da435
    - ss_125c_3.63v-run1.spice  sha256:2ea2ac725d0199c114560a834c1bd221d461c8ed6bef9391da9a0db1f94a5465
    - ss_125c_3.63v-run1.log  sha256:32a5ad81438ed2f3b527ffec667de73d1c5d9f389af0280b73e73549cc952125
    - ss_125c_3.63v-run2.spice  sha256:878647f81a1f419fd7964aff5fd3e3fdb65e6c3400eddab5e9a6d3b167056e20
    - ss_125c_3.63v-run2.log  sha256:cc1041aa4aaf67e2a8ce6227b8e0dc2b0599be9f8411a58976f3b10ee5b2396f
wall_time: 1.1s
---

## Result

- `dtrip_v`: mean 1.54233 over 3 seeds (sd 0, 0.0% of mean; min 1.54233, max 1.54233)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-mc-offset-control --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset-control --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py sampler-dff-mc-offset-control --corners ss --temps 125 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
```

## Caveats

- Single corner (ss / 3.63 V / 125 C). Says nothing about any other corner.
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
