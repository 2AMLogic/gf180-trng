---
record: 2026-09-06-sampler-core-idle-leakage-extracted-01
date: 2026-09-06T23:27:06Z
status: valid
level: extracted

testbench:
  path: sim/tb/sampler-core-idle-leakage-extracted/tb_sampler_core_idle_leakage_extracted.sp
  sha: 58249f4965c7c30f53aa1d7cd02e5d55bfbf5750
netlist:
  path: layout/pex/sampler_core.extracted.spice
  sha: 1ac5fc2ec119729e3a5f3f7cc485fe8ddc145167
repo_commit: 01b6c4d060ddff949cba90c49762d7d9059c431a-dirty

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - /home/ubuntu/.ciel/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: Linux-7.0.0-1010-aws-x86_64-with-glibc2.39

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
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
  path: sim/records/raw/2026-09-06-sampler-core-idle-leakage-extracted-01/
  files:
    - ff_125c_3.63v.spice  sha256:42f144c7c9dcd5a9cd0e4273fe43a62926e8e08e4e8ce75818221112763d0b96
    - ff_125c_3.63v.log  sha256:b921a7f99edc0e162a1ca7670a65e6017f8d96e0edbe261588d34d4a4e7c561e
wall_time: 10.0s
---

## Result

- `i_idle_clklo_a`: 9.336800e-08
- `i_idle_clkhi_a`: 8.279600e-08
- `p_idle_clklo_w`: 3.389258e-07
- `p_idle_clkhi_w`: 3.005495e-07
- `i_idle_clklo_prev_a`: 9.338550e-08
- `i_idle_clkhi_prev_a`: 8.320600e-08
- `i_idle_worst_a`: 9.336800e-08
- `p_idle_worst_w`: 3.389258e-07
- `v_xo_v`: 1.040265e-05
- `v_n1_v`: 3.6298
- `v_n2_v`: 4.165438e-05
- `v_rawbit_clklo_v`: 1.998568e-05
- `v_rawvalid_clklo_v`: 3.62999
- `v_rawbit_clkhi_v`: 2.430968e-05
- `v_rawvalid_clkhi_v`: 3.62999
- `v_sup_v`: 3.63

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-core-idle-leakage-extracted --corners ff --temps 125 --supply 3.63 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / 125 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.extracted.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Post-layout, device-level-parasitic-annotated (layout/pex/build.py); NOT a full assembled-ring/inter-region routing extraction -- see layout/pex/build.py's own module docstring and sim/characterization-post-layout-extracted.md for exactly what this does and does not capture.
- v_ro1_v/v_ro2_v (the pre-layout deck's ro_buf-output witnesses) are DROPPED from this extracted deck's measurement set. Both v(xduta.xdut.ro1) and the one-level-deeper v(xduta.xdut.xb1.y) report 'no such vector' from ngspice against this specific composed subcircuit, even though xo, n1 and n2 at the same or greater hierarchy depth resolve fine in the same run -- a node-resolution quirk of this particular flattening (ro1 is a zero-impedance pass-through named identically at three nested levels: ro_buf's own 'y' port, ro_array_core_extracted's 'ro1' port, and sampler_core_extracted's own 'ro1' net) rather than a broken netlist or a missing electrical connection. xo, n1 and n2 remain as witnesses that the block reached the expected clamped idle state (en = 0 implies n1 = vdd, n2 = 0, xo = 0); ro1/ro2 themselves are not load-bearing to the current/power result, which is unaffected.
- Scoped to the single corner sim/characterization-startup-and-power-budget.md identified as binding for idle power (ff/+125 C/3.63 V), per issue #17's acceptance criteria ('spec table confirmed at the worst corner post-layout'), not the full 45-point grid.
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
