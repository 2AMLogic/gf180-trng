---
record: 2026-07-31-ro-cinv-05stage-jitter-01
date: 2026-07-31T19:21:43Z
status: superseded
superseded_by: 2026-07-31-ro-cinv-05stage-jitter-04

testbench:
  path: sim/tb/ro-cinv-05stage-jitter/tb_ro_cinv_05stage_jitter.sp
  sha: 7105b542b3496eee5482fbb24dee2f644b6f71c7
netlist:
  path: sim/tb/ro-cinv-05stage-jitter/tb_ro_cinv_05stage_jitter.sp
  sha: 7105b542b3496eee5482fbb24dee2f644b6f71c7
repo_commit: 5988414021b3c1b1ea109dadc6097ae4e62000b3-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran-noise
  tstop: 330n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-cinv-05stage-jitter-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:b5b85e61473ce88d81eac11083a0187307e2ea6f7908ec5ca3571fc34f5eb23d
    - tt_27c_3.30v-run0.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
    - tt_27c_3.30v-run1.spice  sha256:d09db8a70c097213368a8cb95ee37426345d7387664b5801678790973288e00a
    - tt_27c_3.30v-run1.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
    - tt_27c_3.30v-run2.spice  sha256:3b9973cdabb8cea576ace7f952135257f6eb3f50d9e706be9d54e987ef660e96
    - tt_27c_3.30v-run2.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
    - tt_27c_3.30v-run3.spice  sha256:81b73391b11ced4948feb52496bb8d650466dc0e021b2ff06596f73769de9c59
    - tt_27c_3.30v-run3.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
wall_time: 20.0m
---

## Result

- `period`: no data (all runs failed to converge)
- `f_osc`: no data (all runs failed to converge)
- `slew_v_per_s`: no data (all runs failed to converge)
- `sigma_1`: no data (all runs failed to converge)
- `sigma_2`: no data (all runs failed to converge)
- `sigma_4`: no data (all runs failed to converge)
- `sigma_8`: no data (all runs failed to converge)
- `sigma_16`: no data (all runs failed to converge)
- `sigma_32`: no data (all runs failed to converge)

Run failures:
- seed 1: error -- ngspice timed out after 300s
- seed 2: error -- ngspice timed out after 300s
- seed 3: error -- ngspice timed out after 300s
- seed 4: error -- ngspice timed out after 300s

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
