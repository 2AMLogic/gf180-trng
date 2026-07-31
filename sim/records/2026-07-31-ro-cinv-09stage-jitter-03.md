---
record: 2026-07-31-ro-cinv-09stage-jitter-03
date: 2026-07-31T19:41:51Z
status: superseded
superseded_by: 2026-07-31-ro-cinv-09stage-jitter-06

testbench:
  path: sim/tb/ro-cinv-09stage-jitter/tb_ro_cinv_09stage_jitter.sp
  sha: 14f2ebcbd6b97b99223bc5dbdb17b2ee56493df2
netlist:
  path: sim/tb/ro-cinv-09stage-jitter/tb_ro_cinv_09stage_jitter.sp
  sha: 14f2ebcbd6b97b99223bc5dbdb17b2ee56493df2
repo_commit: 5988414021b3c1b1ea109dadc6097ae4e62000b3-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: 125

analysis:
  type: tran-noise
  tstop: 580n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-cinv-09stage-jitter-03/
  files:
    - ss_125c_2.97v-run0.spice  sha256:491d7ef0a83347f421a69d54a9775774097c1a45f64cc1050e7ff6d29b96622f
    - ss_125c_2.97v-run0.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
    - ss_125c_2.97v-run1.spice  sha256:6c3992b4af8c1397a43f04b190d12cfbf96f83ed85d6f5e77c59dd323f61c9f0
    - ss_125c_2.97v-run1.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
    - ss_125c_2.97v-run2.spice  sha256:f25fa6ccabf15f4fff8cebd0cb8adcead943e07daa630451327539410b4b2b3b
    - ss_125c_2.97v-run2.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
    - ss_125c_2.97v-run3.spice  sha256:87b25630185f2f72f00744e1e8a144b5355359575ac13abc2155ee6742b6a2bf
    - ss_125c_2.97v-run3.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
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
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners ss --temps 125 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
