---
record: 2026-11-09-sampler-core-liveness-active-01
date: 2026-11-09T21:53:27Z
status: valid

testbench:
  path: sim/tb/sampler-core-liveness-active/tb_sampler_core_liveness_active.sp
  sha: d266f12cc238e26730e2f12a4651854fd2d2a4e8
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 910461f4e20a99fe6369fa53beccde60370754b3

pdk: gf180mcuD @ f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7
pdk.models:
  - ~/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sha256:f6f4a96e18fc5ad11270ad3451aaecc7ac37fc81eb61e15b0d7d94c7bc594a24)

tool:
  klt: 0.9.2.dev397+gd8fa2907890e
  ngspice: ngspice-46
  platform: Linux-7.0.0-1014-aws-x86_64-with-glibc2.39

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran (deterministic)
  tstop: 120n
  tstep: 5p (print step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-11-09-sampler-core-liveness-active-01/
  files:
    - corner.cir  sha256:71df00be80a661a79e1b003fd5bb4ed19e9c4606f7aca7968585eb1bfa521966
    - ngspice.log  sha256:c603d0c82887ea213158dc41a454d8a0fdc4cf81f7f9519c3edb1ffa2d2104b4
    - report-unit.json  sha256:22c08631bdeb209b0bd5a47bd59abfcda5760349109b7a1892ca16a420049c2b
wall_time: 23.187s
---

## Result

Executed by local ngspice (single-point debug probe). Raw branch charges are read at the 2nd and 6th rising ring crossings (four ring periods); the derived terms below are `sim/tools/liveness_sampler_power.py`'s arithmetic on them.

- `i_data_a`: 1.096619e-05
- `dp_load_w`: 2.177837e-05
- `p_live_data_w`: 3.980727e-05
- `q_clk_run_c`: 1.437319e-14
- `q_xsr1_c`: 1.096203e-13
- `q_xsr2_c`: 1.061537e-13
- `q_xsv1_c`: 2.239621e-14
- `q_xsv2_c`: 2.239616e-14
- `q_data1_c`: 8.722411e-14
- `q_data2_c`: 8.375754e-14
- `q_per_transition1_c`: 1.090301e-14
- `q_per_transition2_c`: 1.046969e-14
- `f_r1_hz`: 2.487566e+08
- `f_r2_hz`: 2.646590e+08
- `f_r1_ctl_hz`: 2.490229e+08
- `f_r2_ctl_hz`: 2.650242e+08
- `i_arr_tapped_a`: 1.189793e-04
- `i_arr_ctl_a`: 1.129797e-04
- `w1_s`: 1.607998e-08
- `w2_s`: 1.511379e-08
- `cw1_s`: 1.606278e-08
- `cw2_s`: 1.509296e-08

At this corner the shipped liveness samplers cost 39.807 uW of ring-data power (flops only, before the 2*f_clk*q_clk clock term, which the ledger adds from `sampler-dff-active-current`) and change the array's own supply power by +21.778 uW (tapped array minus the in-run control).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/liveness_sampler_power.py run --outdir DIR --backend local --only ff/-40/3.63
python3 sim/tools/liveness_sampler_power.py analyze DIR/probe-ff_-40_3.63.report.json
```

## Caveats

- The clock is a LOCAL 10 ns clock, not the ratified 1 MHz; the term is per-event charge and the ledger applies the declared rate (see the testbench header).
- The clock charge is removed by in-run subtraction of `xsv` (D tied high); the output-node charge of `xsr` stays in the data term, which over-states a per-clock-cycle cost: a conservative direction.
- Pre-layout, schematic-level; one window of four ring periods; no mismatch or noise.
- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.

---

Written by `sim/tools/liveness_sampler_power.py record`. Append-only: never edit or delete this file.
