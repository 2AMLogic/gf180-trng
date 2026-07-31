---
record: 2026-07-31-ro-inv-05stage-jitter-15
date: 2026-07-31T19:37:01Z
status: valid

testbench:
  path: sim/tb/ro-inv-05stage-jitter/tb_ro_inv_05stage_jitter.sp
  sha: 3af228d176eeadc4a2f5ca5b471be9233df646f7
netlist:
  path: sim/tb/ro-inv-05stage-jitter/tb_ro_inv_05stage_jitter.sp
  sha: 3af228d176eeadc4a2f5ca5b471be9233df646f7
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
  temperature: 27

analysis:
  type: tran-noise
  tstop: 170n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-15/
  files:
    - ff_27c_3.63v-run0.spice  sha256:28855c6cccbb06e56fe4167bd4880052c29bf1792c50ad7d633dfce6c3bd4477
    - ff_27c_3.63v-run0.log  sha256:e4c2dd787c382d8639f29c1646e50eb287ac43b4b53c9faf4396f1987bdf183f
    - ff_27c_3.63v-run1.spice  sha256:0743ad302ef205ffb1459cdb1bbccab98744deade3efe0e2b5075a681b294a2a
    - ff_27c_3.63v-run1.log  sha256:40bb675da9ad2b24db8c96537483286d46fe2ebdf3cad96f564cbd5186db8d57
    - ff_27c_3.63v-run2.spice  sha256:407d3cc85f8ffd7d7d27fa98028ddb34de7554f934ab1c6c06dd37621037ec27
    - ff_27c_3.63v-run2.log  sha256:c0fbad55de0ab9729f63aba4f02f66eadd6b7c9c71d441574f025027c6de2062
    - ff_27c_3.63v-run3.spice  sha256:0a68dece6e45d438a04ea833da44d7fd21fb916db1cce371287f2e9031f8d184
    - ff_27c_3.63v-run3.log  sha256:69505e2ffdd54731dbd4098f7566ec0bc2764e1cdbe7b5a14dddd370f5650c98
wall_time: 1.9m
---

## Result

- `period`: mean 4.920082e-10 over 4 seeds (sd 3.948968e-15, 0.0% of mean; min 4.920058e-10, max 4.920141e-10)
- `f_osc`: mean 2.032486e+09 over 4 seeds (sd 16313.1, 0.0% of mean; min 2.032462e+09, max 2.032496e+09)
- `slew_v_per_s`: mean 4.633662e+10 over 4 seeds (sd 9.353112e+07, 0.2% of mean; min 4.619790e+10, max 4.639274e+10)
- `sigma_1`: mean 6.894137e-14 over 4 seeds (sd 4.553456e-15, 6.6% of mean; min 6.248152e-14, max 7.249732e-14)
- `sigma_2`: mean 9.612433e-14 over 4 seeds (sd 3.900274e-15, 4.1% of mean; min 9.054404e-14, max 9.937459e-14)
- `sigma_4`: mean 1.372337e-13 over 4 seeds (sd 6.406796e-15, 4.7% of mean; min 1.288062e-13, max 1.443853e-13)
- `sigma_8`: mean 1.988509e-13 over 4 seeds (sd 1.220585e-14, 6.1% of mean; min 1.816494e-13, max 2.104777e-13)
- `sigma_16`: mean 2.851289e-13 over 4 seeds (sd 5.239462e-14, 18.4% of mean; min 2.359275e-13, max 3.332875e-13)
- `sigma_32`: mean 3.457642e-13 over 4 seeds (sd 9.931884e-14, 28.7% of mean; min 2.544808e-13, max 4.591913e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
