---
record: 2026-07-31-ro-inv-05stage-lownoise-02
date: 2026-07-31T19:26:38Z
status: valid

testbench:
  path: sim/tb/ro-inv-05stage-lownoise/tb_ro_inv_05stage_lownoise.sp
  sha: b4dbafe38b426aeb4a6dfbdce0e562ffa4502f75
netlist:
  path: sim/tb/ro-inv-05stage-lownoise/tb_ro_inv_05stage_lownoise.sp
  sha: b4dbafe38b426aeb4a6dfbdce0e562ffa4502f75
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
  tstop: 170n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-4 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-18 V^2/Hz (1e-09 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-lownoise-02/
  files:
    - ff_-40c_3.63v-run0.spice  sha256:b4e290ffaeafe3afa2b595e88a3a6b1353ba031f9f20ba04d33e521fc9ddfd3f
    - ff_-40c_3.63v-run0.log  sha256:2c83e82d43eb9ed92976cb34f6a9029adeba32cb015ef8f7273f663b5e92dab9
    - ff_-40c_3.63v-run1.spice  sha256:00ac9df8e5c5b29769174ebf4690af7131375b74513c1c0965e32e4648eafe94
    - ff_-40c_3.63v-run1.log  sha256:316f7a6c952ace86d11a629330db01adf7ebc2ddaf59d170767a7ecaf30ff31d
    - ff_-40c_3.63v-run2.spice  sha256:36be895898ed1f4aaee26481b8755d8c8a77934ce5077d045e75ab696f5d7423
    - ff_-40c_3.63v-run2.log  sha256:6dbb025ed1ab0872dbca6f68ed6c49e53118f33fa1e266fd44266921da04d7c1
    - ff_-40c_3.63v-run3.spice  sha256:ecb593f9e5dd856a1ef7ed9d285aee9869afd0a11244cefe0917796d44066680
    - ff_-40c_3.63v-run3.log  sha256:48d7ce1468039b798d1bd34fba9e77c669f808ce3657fd7ef201506360ee02b4
wall_time: 9.9m
---

## Result

- `period`: mean 4.342456e-10 over 4 seeds (sd 8.727500e-16, 0.0% of mean; min 4.342443e-10, max 4.342463e-10)
- `f_osc`: mean 2.302844e+09 over 4 seeds (sd 4628.29, 0.0% of mean; min 2.302840e+09, max 2.302851e+09)
- `slew_v_per_s`: mean 5.324435e+10 over 4 seeds (sd 9.762763e+06, 0.0% of mean; min 5.323361e+10, max 5.325704e+10)
- `sigma_1`: mean 7.265067e-15 over 4 seeds (sd 2.893026e-16, 4.0% of mean; min 6.986283e-15, max 7.566978e-15)
- `sigma_2`: mean 9.312544e-15 over 4 seeds (sd 7.198320e-16, 7.7% of mean; min 8.296285e-15, max 9.989465e-15)
- `sigma_4`: mean 1.273900e-14 over 4 seeds (sd 1.511968e-15, 11.9% of mean; min 1.076479e-14, max 1.435078e-14)
- `sigma_8`: mean 1.690984e-14 over 4 seeds (sd 3.916330e-15, 23.2% of mean; min 1.225057e-14, max 2.133336e-14)
- `sigma_16`: mean 2.309991e-14 over 4 seeds (sd 5.747951e-15, 24.9% of mean; min 1.699891e-14, max 2.916584e-14)
- `sigma_32`: mean 2.869284e-14 over 4 seeds (sd 5.235226e-15, 18.2% of mean; min 2.409080e-14, max 3.339381e-14)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-lownoise --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
