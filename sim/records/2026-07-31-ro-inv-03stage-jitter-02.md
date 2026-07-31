---
record: 2026-07-31-ro-inv-03stage-jitter-02
date: 2026-07-31T19:23:50Z
status: valid

testbench:
  path: sim/tb/ro-inv-03stage-jitter/tb_ro_inv_03stage_jitter.sp
  sha: 8b4771cbd7ba0fabbb3c58f9067b5bf73d17caf8
netlist:
  path: sim/tb/ro-inv-03stage-jitter/tb_ro_inv_03stage_jitter.sp
  sha: 8b4771cbd7ba0fabbb3c58f9067b5bf73d17caf8
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
  tstop: 110n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-03stage-jitter-02/
  files:
    - ff_-40c_3.63v-run0.spice  sha256:5c94bc4a297b04f33b5746088b16c7e0bdee0bc2329d0aefec895350ffec9c5b
    - ff_-40c_3.63v-run0.log  sha256:9f514d7d75333de7b8ec207640dd21612a1724b59d9b18d9c3ea4e00daf33302
    - ff_-40c_3.63v-run1.spice  sha256:4f07b91ea64744f0905964bd72541b502c34f0221c21ca2145bdce56ddd8ec40
    - ff_-40c_3.63v-run1.log  sha256:6aa585639f20b5e25512c6340712b108756d9043ebff264f6f219e846155de24
    - ff_-40c_3.63v-run2.spice  sha256:de0fccc2e8122aa0c052b3b71395c4b55db9deeaad8736e71f8d0691807cf78b
    - ff_-40c_3.63v-run2.log  sha256:8309e7c0f010a465658fff0d5192bc1baf259504b80a9db5da6698e125c6af99
    - ff_-40c_3.63v-run3.spice  sha256:e72b39634f746292d4ecbb555ce89d195909239f3385187b48223d1106821f1e
    - ff_-40c_3.63v-run3.log  sha256:f0c4bc1dd724d2457aa171f451aaa3795d43b69d699f17ddf7ad17c0edc3a4ba
wall_time: 4.1m
---

## Result

- `period`: mean 2.531465e-10 over 4 seeds (sd 3.408270e-15, 0.0% of mean; min 2.531414e-10, max 2.531488e-10)
- `f_osc`: mean 3.950282e+09 over 4 seeds (sd 53185.8, 0.0% of mean; min 3.950245e+09, max 3.950361e+09)
- `slew_v_per_s`: mean 5.339322e+10 over 4 seeds (sd 7.270735e+07, 0.1% of mean; min 5.330788e+10, max 5.347278e+10)
- `sigma_1`: mean 5.276538e-14 over 4 seeds (sd 1.142393e-15, 2.2% of mean; min 5.158269e-14, max 5.430422e-14)
- `sigma_2`: mean 7.275411e-14 over 4 seeds (sd 9.999165e-16, 1.4% of mean; min 7.190628e-14, max 7.416860e-14)
- `sigma_4`: mean 1.001113e-13 over 4 seeds (sd 7.915601e-15, 7.9% of mean; min 8.948370e-14, max 1.085418e-13)
- `sigma_8`: mean 1.346932e-13 over 4 seeds (sd 1.841853e-14, 13.7% of mean; min 1.122474e-13, max 1.573294e-13)
- `sigma_16`: mean 1.778265e-13 over 4 seeds (sd 2.672287e-14, 15.0% of mean; min 1.510674e-13, max 2.118426e-13)
- `sigma_32`: mean 2.271024e-13 over 4 seeds (sd 4.860763e-14, 21.4% of mean; min 1.835912e-13, max 2.765958e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-03stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-03stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-03stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-03stage-jitter --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
