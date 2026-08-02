---
record: 2026-08-02-sampler-core-idle-leakage-44
date: 2026-08-02T10:09:51Z
status: valid

testbench:
  path: sim/tb/sampler-core-idle-leakage/tb_sampler_core_idle_leakage.sp
  sha: 143659fe7c96b77ba28a24e17d57647c27ed6e61
netlist:
  path: design/sampler_core.spice
  sha: 50bc082dc2798c8b98e4ced8ebb70432549aa2ec
repo_commit: 599badd86cb8bb05c22c7691fe9a318477143989-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: sf bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: sf
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 125

analysis:
  type: tran
  tstop: 1u
  tstep: 200p (print step; ngspice's own LTE sets the actual solver step, which is very coarse here because nothing switches after 300 ns)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-02-sampler-core-idle-leakage-44/
  files:
    - sf_125c_3.30v.spice  sha256:2c7b19e40476189e99973370945f94d8539e28d0899c3f4def100c0c9c6f7df2
    - sf_125c_3.30v.log  sha256:bac685ec46b900873422823aff332033efec77056f3b3e481adbff283ad6f6d1
wall_time: 1.3m
---

## Result

- `i_idle_clklo_a`: 1.908650e-09
- `i_idle_clkhi_a`: 1.735450e-09
- `p_idle_clklo_w`: 6.298545e-09
- `p_idle_clkhi_w`: 5.726985e-09
- `i_idle_clklo_prev_a`: 1.918650e-09
- `i_idle_clkhi_prev_a`: 1.735450e-09
- `i_idle_worst_a`: 1.908650e-09
- `p_idle_worst_w`: 6.298545e-09
- `v_ro1_v`: 3.3
- `v_ro2_v`: 3.3
- `v_xo_v`: 2.126453e-06
- `v_n1_v`: 3.3
- `v_n2_v`: 3.139039e-06
- `v_rawbit_clklo_v`: -6.811194e-06
- `v_rawvalid_clklo_v`: 3.3
- `v_rawbit_clkhi_v`: 4.289539e-07
- `v_rawvalid_clkhi_v`: 3.3
- `v_sup_v`: 3.3

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-core-idle-leakage --corners sf --temps 125 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (sf / 3.30 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- This is the ANALOG side of the DR-0009 boundary only: two rings, the XOR combiner, two sampler_dff instances. The conditioner, the health tests and the interface have no gate-level netlist in this repository (design/README.md), so their leakage cannot be SPICE-measured at all and is not in this number. sim/tools/power_rollup.py adds design/digital_power_estimate.py's library-based figure for those, clearly labelled an estimate (DR-0004 Tier 2) and not a measurement.
- Reports STATIC current in a settled state. It says nothing about the transient the block draws while entering idle (the rings' last decaying cycles after en falls, and the one clock edge this deck itself applies), and nothing about a supply ramp: vdd is a DC source, up from t = 0.
- 'Idle' here is the README's ratified definition -- rings stopped, reset RELEASED, state retained, block powered. It is deliberately not the reset-asserted state sim/tb/sampler-dff-reset-current-{xsv,xsb}/ measure, and the two must not be quoted interchangeably.
- The retained flop state is the one the block reaches by clamping the rings and then taking a clock edge: raw_valid = 1 (xsv's D is tied to vdd) and raw_bit = 0 (xo is low while both rings are clamped high). A block parked with raw_bit = 1 instead would bias the slave latch's devices differently; that state is not reachable in this deck without driving xo, and is not measured.
- No power gating of any kind is modelled. This is the ungated leakage floor: any gating scheme an integrator adds can only improve on it, and the README's own note already anticipates that the ungated figure may be the binding one.
- Both clock park states are reported because neither is normative. If a future decision record fixes the parked level, the corresponding column becomes the one to quote and the other stays as evidence that the choice mattered (or did not).
- Two independent windows of the same quantity are recorded per copy: the charge-integrator average over [800 ns, 1 us] (`i_idle_*_a`, the headline) and over the preceding [600 ns, 800 ns] (`i_idle_*_prev_a`). They agree only if the state really is static, so a disagreement between a pair is the record's own self-check failing, not a rounding difference to be averaged away. An INSTANTANEOUS branch-current read was tried first and rejected: with nothing switching, ngspice's timestep grows to a large fraction of the window and `meas ... find i(v...) at=1u` returns an interpolated value that disagreed with the integrated one by three orders of magnitude, and in sign. The integrator is insensitive to that because it reads a node voltage the solver actually carries, and it averages rather than samples.
- The node-voltage rows are witnesses, not results: they exist so a record where the solver landed somewhere other than the clamped state -- which would make the current figure meaningless, as an `op` analysis of this same block demonstrates -- is visible rather than silently plausible. With en = 0 the expected state is ro1 = ro2 = vdd, xo = 0, n1 = vdd, n2 = 0.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
