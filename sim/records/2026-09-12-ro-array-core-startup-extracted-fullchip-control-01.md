---
record: 2026-09-12-ro-array-core-startup-extracted-fullchip-control-01
date: 2026-09-12T08:06:06Z
status: valid

testbench:
  path: sim/tb/ro-array-core-startup-extracted-fullchip-control/tb_ro_array_core_startup_extracted_fullchip_control.sp
  sha: de7105e97fa94e59881d031499b1b58cd50d5b8a
netlist:
  path: layout/pex/sampler_core.routed.extracted.spice
  sha: 4bf8c65adc37dad04d75c4641f81e4bfbb09ee4d
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
  path: sim/records/raw/2026-09-12-ro-array-core-startup-extracted-fullchip-control-01/
  files:
    - ss_125c_2.97v.spice  sha256:55e914860d4900a5694207ce05a48bde76a64e04166d0dc5f52b9144813eaf5f
    - ss_125c_2.97v.log  sha256:1a256c85bee83cd2782e267743b40ccab2518871a6856e04da26ef256426d8e1
wall_time: 8.3m
---

## Result

- `en_assert_s`: 5.000000e-09
- `t1r1_s`: 2.771570e-08
- `t2r1_s`: 5.021655e-08
- `t3r1_s`: 7.286739e-08
- `t4r1_s`: 9.552649e-08
- `t5r1_s`: 1.181625e-07
- `t6r1_s`: 1.408128e-07
- `t7r1_s`: 1.633683e-07
- `t8r1_s`: 1.861248e-07
- `t9r1_s`: 2.087615e-07
- `t10r1_s`: 2.314695e-07
- `t1r2_s`: 2.610305e-08
- `t2r2_s`: 4.715410e-08
- `t3r2_s`: 6.827142e-08
- `t4r2_s`: 8.941546e-08
- `t5r2_s`: 1.105803e-07
- `t6r2_s`: 1.317998e-07
- `t7r2_s`: 1.529976e-07
- `t8r2_s`: 1.741327e-07
- `t9r2_s`: 1.954714e-07
- `t10r2_s`: 2.167400e-07
- `t1xo_s`: 2.888879e-08
- `t2xo_s`: 3.836646e-08
- `t3xo_s`: 5.000402e-08
- `t4xo_s`: 5.933412e-08
- `ring_swing_early_v`: 2.85446
- `ring_swing_late_v`: 2.83882
- `xo_swing_early_v`: 2.51368
- `xo_swing_late_v`: 2.98335
- `v_ro1_off_v`: 2.97
- `v_xo_off_v`: 2.531748e-07

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-core-startup-extracted-fullchip-control --corners ss --temps 125 --supply 2.97 --supply-tol 0 --timeout 1800 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.routed.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- ZERO-DELTA CONTROL for sim/tb/ro-array-core-startup-extracted-fullchip/: this deck is byte-identical to that one except for its own header comment and the DUT subcircuit name (sampler_core_routed_extracted here, sampler_core_fullchip_extracted there), so the difference between this record and its -extracted-fullchip sibling at the same PVT point is EXACTLY what layout/pex/build.py's full-chip composition adds (DR-0025's ro1/ro2 inter-region trunk delta, plus the four disclosed driver-side-only output-load capacitors) and nothing else. It exists because the pre-existing -extracted-routed record of this family is composed from ro_array_core's topology, not sampler_core's, so it is NOT a valid subtraction baseline for the inter-region delta on its own -- see sim/characterization-post-layout-extracted.md section 8.
- Carries NO inter-region parasitic at all (that is the point of a control): the DUT is layout/pex/sampler_core.routed.extracted.spice, the same intra-region routing-level composition issue #217 recorded, per DR-0024.
- clk/rst_n are tied STATIC (clk=0, rst_n=vdd_val) -- this testbench measures the ring array's own start-up transient, not sampler activity.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for time-to-first-valid (ss/+125 C/2.97 V), the same point issues #17/#217's own records used -- not the full 27-point grid.
- Deterministic (noiseless) transient started from the operating point ngspice solves with en = 0, same as the leaf-level and routing-level families -- no .ic kick used or needed.
- v(xdut.rn1)/v(xdut.rn2) address the ring's own output AFTER the DR-0025 delta but BEFORE the buffer (this composition's own internal net names, unchanged from the routing-level family's identical convention); v(xdut.xcs.xo) moves one hierarchy hop deeper than the routing-level family's v(xo), because the buffer/XOR stage now lives inside the fully assembled combiner_sampler wrapper -- see this testbench's own .sp header.
- clk/rst_n arrival is still driven from an ideal, zero-impedance source at combiner_sampler's own pins (tied off entirely in this testbench) -- this record says nothing about clock-tree arrival at the sampler, per DR-0025.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
