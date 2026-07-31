---
record: 2026-07-31-ro-inv-05stage-jitter-11
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
  voltage: 3.300 V (nominal 3.3 V)
  temperature: -40

analysis:
  type: tran-noise
  tstop: 170n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-11/
  files:
    - ff_-40c_3.30v-run0.spice  sha256:6a89ec637068179fe1310e0b55c7746568aa42d15d24f87ab5da859a59c9b89d
    - ff_-40c_3.30v-run0.log  sha256:19a1d0a81aaa5a4e2f52df6f9dd2f57a4e5d5688ed80a106821e06726a8ededa
    - ff_-40c_3.30v-run1.spice  sha256:f7a956bc23782203c11d35deac5b04423a9582555e8d7feebaa366f5c14273c6
    - ff_-40c_3.30v-run1.log  sha256:196289ff287b38f8cfcb0c157680070584f62f61af81b58f393d100c910c144e
    - ff_-40c_3.30v-run2.spice  sha256:157c866bd15f4ed8a6ddbfe409a776044285069b985cef32b32af735b4acc98f
    - ff_-40c_3.30v-run2.log  sha256:f7ab9653580ad228958623fdfe4926ee32401ea9e291dd81d9f9fdf8f7bbe1ab
    - ff_-40c_3.30v-run3.spice  sha256:68d48769c8a292634ad1a314ab3e7d231324cb67bb77b66b90f6b50d09d4d85d
    - ff_-40c_3.30v-run3.log  sha256:ad1c0e1b84d6f3e56ebfaa387e6f93a9b58e252625a602688ff06e3e0759db75
wall_time: 3.3m
---

## Result

- `period`: mean 4.597360e-10 over 4 seeds (sd 3.486760e-15, 0.0% of mean; min 4.597326e-10, max 4.597409e-10)
- `f_osc`: mean 2.175161e+09 over 4 seeds (sd 16496.9, 0.0% of mean; min 2.175138e+09, max 2.175177e+09)
- `slew_v_per_s`: mean 4.584930e+10 over 4 seeds (sd 5.103186e+07, 0.1% of mean; min 4.579199e+10, max 4.590985e+10)
- `sigma_1`: mean 7.045681e-14 over 4 seeds (sd 5.141906e-15, 7.3% of mean; min 6.486428e-14, max 7.697240e-14)
- `sigma_2`: mean 9.621836e-14 over 4 seeds (sd 5.850771e-15, 6.1% of mean; min 8.879361e-14, max 1.013940e-13)
- `sigma_4`: mean 1.323410e-13 over 4 seeds (sd 8.948854e-15, 6.8% of mean; min 1.242124e-13, max 1.447002e-13)
- `sigma_8`: mean 1.793840e-13 over 4 seeds (sd 2.321423e-14, 12.9% of mean; min 1.604112e-13, max 2.129066e-13)
- `sigma_16`: mean 2.600316e-13 over 4 seeds (sd 1.996554e-14, 7.7% of mean; min 2.389687e-13, max 2.844022e-13)
- `sigma_32`: mean 3.389777e-13 over 4 seeds (sd 5.565049e-14, 16.4% of mean; min 2.775615e-13, max 4.068725e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps -40 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.30 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
