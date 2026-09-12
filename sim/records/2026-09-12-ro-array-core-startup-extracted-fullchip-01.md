---
record: 2026-09-12-ro-array-core-startup-extracted-fullchip-01
date: 2026-09-12T08:14:25Z
status: valid

testbench:
  path: sim/tb/ro-array-core-startup-extracted-fullchip/tb_ro_array_core_startup_extracted_fullchip.sp
  sha: 7ad9155c1029a188a15cd11e94c1e4ccb9c06452
netlist:
  path: layout/pex/sampler_core.fullchip.extracted.spice
  sha: 9c992f581fb2fb86afa46685aded83ca58413428
repo_commit: f03b78efa77b0bf73b7ae3c144fd936b00d78c68-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /Users/rwalters/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6.2-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: tran
  tstop: 280n
  tstep: 2p (print step; ngspice's own LTE sets the actual solver step; same window as the routing-level family -- see that family's own tb.json for the 180n->280n widening derivation this family inherits unchanged).
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-09-12-ro-array-core-startup-extracted-fullchip-01/
  files:
    - ss_125c_2.97v.spice  sha256:3c461773a26abd8fb05e9089a3f40709785b05097aab4845d7130143995371d9
    - ss_125c_2.97v.log  sha256:2641efafc9b23f6a6c2e47f42c9de65844f37c61debc2193a9139125959b5725
wall_time: 8.4m
---

## Result

- `en_assert_s`: 5.000000e-09
- `t1r1_s`: 3.144245e-08
- `t2r1_s`: 5.695269e-08
- `t3r1_s`: 8.233750e-08
- `t4r1_s`: 1.079765e-07
- `t5r1_s`: 1.334958e-07
- `t6r1_s`: 1.589556e-07
- `t7r1_s`: 1.847032e-07
- `t8r1_s`: 2.103667e-07
- `t9r1_s`: 2.362138e-07
- `t10r1_s`: 2.618325e-07
- `t1r2_s`: 2.741570e-08
- `t2r2_s`: 4.956738e-08
- `t3r2_s`: 7.182220e-08
- `t4r2_s`: 9.409193e-08
- `t5r2_s`: 1.164549e-07
- `t6r2_s`: 1.387573e-07
- `t7r2_s`: 1.612709e-07
- `t8r2_s`: 1.838479e-07
- `t9r2_s`: 2.063152e-07
- `t10r2_s`: 2.287989e-07
- `t1xo_s`: 3.035845e-08
- `t2xo_s`: 3.981999e-08
- `t3xo_s`: 5.251397e-08
- `t4xo_s`: 6.181391e-08
- `ring_swing_early_v`: 2.55297
- `ring_swing_late_v`: 2.55333
- `xo_swing_early_v`: 2.96801
- `xo_swing_late_v`: 2.97839
- `v_ro1_off_v`: 2.97
- `v_xo_off_v`: 2.828994e-07

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-startup-extracted-fullchip --corners ss --temps 125 --supply 2.97 --supply-tol 0 --timeout 1800 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.fullchip.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, FULL-CHIP-DELTA-annotated for the ro1/ro2 inter-region trunks ONLY (layout/pex/build.py); every other inter-region trunk is unpriced by this composition -- see DR-0025 and layout/pex/build.py's own module docstring for the full accounting.
- CELL-INSTANCE GRANULARITY, NOT TRANSISTOR LEVEL (DR-0025): the inter-region parasitics this DUT carries were measured by a full-chip `klt extract --parasitics` run over layout/floorplan/trng_floorplan.gds in which every one of digital's ~2500 gf180mcu_fd_sc_mcu9t5v0__* standard-cell instances was abstracted as an opaque black box -- the same granularity the composed LVS already uses. No number in this record is evidence about any standard cell's own devices, and digital is not instantiated in this deck at all.
- clk/rst_n are tied STATIC (clk=0, rst_n=vdd_val) -- this testbench measures the ring array's own start-up transient, not sampler activity.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for time-to-first-valid (ss/+125 C/2.97 V), the same point issues #17/#217's own records used -- not the full 27-point grid.
- Deterministic (noiseless) transient started from the operating point ngspice solves with en = 0, same as the leaf-level and routing-level families -- no .ic kick used or needed.
- v(xdut.rn1)/v(xdut.rn2) address the ring's own output AFTER the DR-0025 delta but BEFORE the buffer (this composition's own internal net names, unchanged from the routing-level family's identical convention); v(xdut.xcs.xo) moves one hierarchy hop deeper than the routing-level family's v(xo), because the buffer/XOR stage now lives inside the fully assembled combiner_sampler wrapper -- see this testbench's own .sp header.
- clk/rst_n arrival is still driven from an ideal, zero-impedance source at combiner_sampler's own pins (tied off entirely in this testbench) -- this record says nothing about clock-tree arrival at the sampler, per DR-0025.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
