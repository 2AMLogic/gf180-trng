---
record: 2026-10-10-sampler-core-liveness-active-01
date: 2026-10-10T11:18:26Z
status: valid

testbench:
  path: sim/tb/sampler-core-liveness-active/tb_sampler_core_liveness_active.sp
  sha: d266f12cc238e26730e2f12a4651854fd2d2a4e8
netlist:
  path: design/sampler_core.spice
  sha: 21c00afe568de2ae7e75cc4cf3c0b44d18478f6c
repo_commit: 870cb9ecd9e801f659fde2932233ec071cd9aae6-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - ~/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sha256:6edba54d23b38a2c60f8ffdbaa3eb75a7568c615e4820808969bd1121b77b1aa)

tool:
  klt: 0.7.0+gca3089cd4b9f
  ngspice: ngspice-42
  platform: Linux-7.0.0-1013-aws-x86_64-with-glibc2.39

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran (deterministic)
  tstop: 120n
  tstep: 5p (print step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-10-10-sampler-core-liveness-active-01/
  files:
    - corner.cir  sha256:21bba0637e5081c71c48b23c4630996e9f95aba282951b89622049ddb3ddd4e7
    - ngspice.log  sha256:c0928d85e66d0c7e79e7ddc766f7e43cc733ce9750df912f3b9ba52cc7b04667
    - report-unit.json  sha256:9065e8e87d8152a259341a1895fd2419ece9e030754c936b5e0a5976a10577d5
wall_time: 14.045s
---

## Result

Executed by local ngspice (single-point debug probe). Raw branch charges are read at the 2nd and 6th rising ring crossings (four ring periods); the derived terms below are `sim/tools/liveness_sampler_power.py`'s arithmetic on them.

- `i_data_a`: 5.815267e-06
- `dp_load_w`: 6.076759e-06
- `p_live_data_w`: 1.919038e-05
- `q_clk_run_c`: 7.921907e-15
- `q_xsr1_c`: 1.009060e-13
- `q_xsr2_c`: 8.975373e-14
- `q_xsv1_c`: 2.319616e-14
- `q_xsv2_c`: 1.773012e-14
- `q_data1_c`: 7.770985e-14
- `q_data2_c`: 7.202361e-14
- `q_per_transition1_c`: 9.713731e-15
- `q_per_transition2_c`: 9.002951e-15
- `f_r1_hz`: 1.503415e+08
- `f_r2_hz`: 1.607536e+08
- `f_r1_ctl_hz`: 1.497544e+08
- `f_r2_ctl_hz`: 1.602384e+08
- `i_arr_tapped_a`: 5.984026e-05
- `i_arr_ctl_a`: 5.799882e-05
- `w1_s`: 2.660610e-08
- `w2_s`: 2.488280e-08
- `cw1_s`: 2.671040e-08
- `cw2_s`: 2.496280e-08

At this corner the shipped liveness samplers cost 19.190 uW of ring-data power (flops only, before the 2*f_clk*q_clk clock term, which the ledger adds from `sampler-dff-active-current`) and change the array's own supply power by +6.077 uW (tapped array minus the in-run control).

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/tools/liveness_sampler_power.py run --outdir DIR --backend local --only tt/27/3.30
python3 sim/tools/liveness_sampler_power.py analyze DIR/probe-tt_27_3.30.report.json
```

## Caveats

- The clock is a LOCAL 10 ns clock, not the ratified 1 MHz; the term is per-event charge and the ledger applies the declared rate (see the testbench header).
- The clock charge is removed by in-run subtraction of `xsv` (D tied high); the output-node charge of `xsr` stays in the data term, which over-states a per-clock-cycle cost: a conservative direction.
- Pre-layout, schematic-level; one window of four ring periods; no mismatch or noise.
- The raw deck and log have this host's absolute paths replaced by `<repo>` and `~` before hashing.

---

Written by `sim/tools/liveness_sampler_power.py record`. Append-only: never edit or delete this file.
