---
record: 2026-07-31-ro-inv-09stage-jitter-02
date: 2026-07-31T19:31:49Z
status: superseded
superseded_by: 2026-07-31-ro-inv-09stage-jitter-05

testbench:
  path: sim/tb/ro-inv-09stage-jitter/tb_ro_inv_09stage_jitter.sp
  sha: 1f809993aec2923642e9c288b788eb8d602a48ad
netlist:
  path: sim/tb/ro-inv-09stage-jitter/tb_ro_inv_09stage_jitter.sp
  sha: 1f809993aec2923642e9c288b788eb8d602a48ad
repo_commit: 5988414021b3c1b1ea109dadc6097ae4e62000b3-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
  voltage: 3.630 V (nominal 3.3 V, +10%)
  temperature: -40

analysis:
  type: tran-noise
  tstop: 300n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-09stage-jitter-02/
  files:
    - ff_-40c_3.63v-run0.spice  sha256:79560cde503da493bf7379519b72164ca72d062771f5b18eea3e03495d76d875
    - ff_-40c_3.63v-run0.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
    - ff_-40c_3.63v-run1.spice  sha256:a148a17c7881c0f7b9d7d7676109b633a6bb2dc749fdc0df13da884baf76af70
    - ff_-40c_3.63v-run1.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
    - ff_-40c_3.63v-run2.spice  sha256:5809ef908855b7898cb9d488fd67bcb96ddba0383e5700e3c261b651c8c29beb
    - ff_-40c_3.63v-run2.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
    - ff_-40c_3.63v-run3.spice  sha256:491cd6934932ad1df912e3d2cd7229cd064da170291eaa3f0afc42e1cea38cd6
    - ff_-40c_3.63v-run3.log  sha256:280f4349958f6b5a84ee5390a10361fc5079ed9957ea19ad5caebd47200f14fc
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
python3 sim/run_corners.py ro-inv-09stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-09stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-09stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-09stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
