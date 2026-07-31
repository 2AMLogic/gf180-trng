---
record: 2026-07-31-ro-cinv-05stage-jitter-05
date: 2026-07-31T20:01:21Z
status: valid
supersedes: 2026-07-31-ro-cinv-05stage-jitter-02

testbench:
  path: sim/tb/ro-cinv-05stage-jitter/tb_ro_cinv_05stage_jitter.sp
  sha: 7105b542b3496eee5482fbb24dee2f644b6f71c7
netlist:
  path: sim/tb/ro-cinv-05stage-jitter/tb_ro_cinv_05stage_jitter.sp
  sha: 7105b542b3496eee5482fbb24dee2f644b6f71c7
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
  tstop: 330n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-cinv-05stage-jitter-05/
  files:
    - ff_-40c_3.63v-run0.spice  sha256:9cc4342e031930ac2ac1996879c2ae675b771a85fa2bc44a337c440f8a5cc1f1
    - ff_-40c_3.63v-run0.log  sha256:a0dcab413fdce9a2fbc56c9c9efe447865420fed3929a85d547d3d29ea8ca169
    - ff_-40c_3.63v-run1.spice  sha256:17b317fd330e1a9e54e72a733d9feb456fbeff46fe4f88100410e40d59e5c800
    - ff_-40c_3.63v-run1.log  sha256:034254ca48a1fffe06135131f13b0e554efde0577e75b0bf11ba60de44b80677
    - ff_-40c_3.63v-run2.spice  sha256:becd2528b2917003d30a11e27a4ce2b22413fbfe0f2898273d7d524e3ab607ef
    - ff_-40c_3.63v-run2.log  sha256:fccdba33db4cc4ecc44c22532644b4b420e2466f3467dcde56798712eb39a7c9
    - ff_-40c_3.63v-run3.spice  sha256:6e14e18ad6ac71920883fd1ba90e17326caa88867acdf644fcbaf06143fba532
    - ff_-40c_3.63v-run3.log  sha256:a8ff672487d7ba19fefa77acd8f19230d3199f1d1421674dcc3e8464e2eb004d
wall_time: 7.9m
---

## Result

- `period`: mean 9.354463e-10 over 4 seeds (sd 8.190700e-15, 0.0% of mean; min 9.354360e-10, max 9.354542e-10)
- `f_osc`: mean 1.069008e+09 over 4 seeds (sd 9360.21, 0.0% of mean; min 1.068999e+09, max 1.069020e+09)
- `slew_v_per_s`: mean 2.132849e+10 over 4 seeds (sd 2.248870e+07, 0.1% of mean; min 2.130782e+10, max 2.135922e+10)
- `sigma_1`: mean 2.262884e-13 over 4 seeds (sd 8.951533e-15, 4.0% of mean; min 2.138555e-13, max 2.351064e-13)
- `sigma_2`: mean 3.259300e-13 over 4 seeds (sd 7.386002e-15, 2.3% of mean; min 3.192315e-13, max 3.361940e-13)
- `sigma_4`: mean 4.004386e-13 over 4 seeds (sd 1.764114e-14, 4.4% of mean; min 3.800094e-13, max 4.228980e-13)
- `sigma_8`: mean 4.880693e-13 over 4 seeds (sd 4.333156e-14, 8.9% of mean; min 4.469105e-13, max 5.490680e-13)
- `sigma_16`: mean 6.762382e-13 over 4 seeds (sd 1.513420e-14, 2.2% of mean; min 6.546506e-13, max 6.895682e-13)
- `sigma_32`: mean 1.144556e-12 over 4 seeds (sd 1.499612e-13, 13.1% of mean; min 9.766802e-13, max 1.298454e-12)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-cinv-05stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
