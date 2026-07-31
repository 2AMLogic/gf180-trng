---
record: 2026-07-31-ro-inv-09stage-jitter-05
date: 2026-07-31T19:56:00Z
status: valid
supersedes: 2026-07-31-ro-inv-09stage-jitter-02

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
  path: sim/records/raw/2026-07-31-ro-inv-09stage-jitter-05/
  files:
    - ff_-40c_3.63v-run0.spice  sha256:79560cde503da493bf7379519b72164ca72d062771f5b18eea3e03495d76d875
    - ff_-40c_3.63v-run0.log  sha256:d786954b61cfac60945b33656c0f0bca35a4171d15be58839df34f8db4c74ab0
    - ff_-40c_3.63v-run1.spice  sha256:a148a17c7881c0f7b9d7d7676109b633a6bb2dc749fdc0df13da884baf76af70
    - ff_-40c_3.63v-run1.log  sha256:d1936c89662f9229358cc43f4e86fa6e516170234800a1c7d384ed337a28ec6d
    - ff_-40c_3.63v-run2.spice  sha256:5809ef908855b7898cb9d488fd67bcb96ddba0383e5700e3c261b651c8c29beb
    - ff_-40c_3.63v-run2.log  sha256:a0ac83f1a43d2329a866a7ae07c6d3b6034a17054560f197764581d06c8d4121
    - ff_-40c_3.63v-run3.spice  sha256:491cd6934932ad1df912e3d2cd7229cd064da170291eaa3f0afc42e1cea38cd6
    - ff_-40c_3.63v-run3.log  sha256:d8e482252ce753f2e4447748bf0d7f1d73ff78b6c3d00639535353c7dd63865d
wall_time: 5.5m
---

## Result

- `period`: mean 7.822697e-10 over 4 seeds (sd 6.583079e-15, 0.0% of mean; min 7.822642e-10, max 7.822792e-10)
- `f_osc`: mean 1.278331e+09 over 4 seeds (sd 10757.5, 0.0% of mean; min 1.278316e+09, max 1.278340e+09)
- `slew_v_per_s`: mean 5.322403e+10 over 4 seeds (sd 1.124837e+08, 0.2% of mean; min 5.306242e+10, max 5.332354e+10)
- `sigma_1`: mean 8.303727e-14 over 4 seeds (sd 5.807504e-15, 7.0% of mean; min 7.507627e-14, max 8.786139e-14)
- `sigma_2`: mean 1.146745e-13 over 4 seeds (sd 9.932897e-15, 8.7% of mean; min 1.005423e-13, max 1.235044e-13)
- `sigma_4`: mean 1.568320e-13 over 4 seeds (sd 1.372675e-14, 8.8% of mean; min 1.391395e-13, max 1.719495e-13)
- `sigma_8`: mean 2.150100e-13 over 4 seeds (sd 2.137427e-14, 9.9% of mean; min 1.848898e-13, max 2.342407e-13)
- `sigma_16`: mean 3.174209e-13 over 4 seeds (sd 5.857599e-14, 18.5% of mean; min 2.484419e-13, max 3.824503e-13)
- `sigma_32`: mean 4.435365e-13 over 4 seeds (sd 1.781365e-13, 40.2% of mean; min 2.850016e-13, max 6.505449e-13)

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
