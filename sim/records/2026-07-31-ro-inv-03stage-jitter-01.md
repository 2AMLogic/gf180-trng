---
record: 2026-07-31-ro-inv-03stage-jitter-01
date: 2026-07-31T19:21:43Z
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
  tstop: 110n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-03stage-jitter-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:55b68aba1df187dd48771c9604f14c452e4f06bb0fec5d6468a59033e24449df
    - tt_27c_3.30v-run0.log  sha256:510a3da7b4daa187bde45e9fe1259a40bdc5f55cdee2dd083d06d2734c025561
    - tt_27c_3.30v-run1.spice  sha256:02ed7e3422ccca1d5ec2ff57f8e74812018e7d37661d7be7878ed0117de6c9a2
    - tt_27c_3.30v-run1.log  sha256:4d52d6f2349415726827993383f6159f34c8fab1c79dc15ef4927e3b77903f54
    - tt_27c_3.30v-run2.spice  sha256:1ac3a46b9cd369fec1a8bb41e5900bbd5e41f6e4b819db421f21f561bc3d1b69
    - tt_27c_3.30v-run2.log  sha256:358df6bf1081e47a801fa789693d6230a5981ba38605c847b1951fac6c4b5ddb
    - tt_27c_3.30v-run3.spice  sha256:274041bd8f4e6849d5954d38d478e3be7420ea6a9acf0313604bc685bf2ba2eb
    - tt_27c_3.30v-run3.log  sha256:ba94cc67b69539a5894bcf445d19c55e1965c8f9910e0cf8ff211286867810f1
wall_time: 4.1m
---

## Result

- `period`: mean 3.619532e-10 over 4 seeds (sd 5.580558e-15, 0.0% of mean; min 3.619490e-10, max 3.619610e-10)
- `f_osc`: mean 2.762788e+09 over 4 seeds (sd 42596, 0.0% of mean; min 2.762729e+09, max 2.762820e+09)
- `slew_v_per_s`: mean 3.461485e+10 over 4 seeds (sd 5.747146e+07, 0.2% of mean; min 3.456221e+10, max 3.469120e+10)
- `sigma_1`: mean 7.183680e-14 over 4 seeds (sd 5.056818e-15, 7.0% of mean; min 6.436051e-14, max 7.545969e-14)
- `sigma_2`: mean 9.597316e-14 over 4 seeds (sd 6.320459e-15, 6.6% of mean; min 8.711210e-14, max 1.018086e-13)
- `sigma_4`: mean 1.326169e-13 over 4 seeds (sd 6.476750e-15, 4.9% of mean; min 1.252836e-13, max 1.410442e-13)
- `sigma_8`: mean 1.809440e-13 over 4 seeds (sd 7.518703e-15, 4.2% of mean; min 1.726904e-13, max 1.889347e-13)
- `sigma_16`: mean 2.855828e-13 over 4 seeds (sd 4.142148e-14, 14.5% of mean; min 2.429466e-13, max 3.353418e-13)
- `sigma_32`: mean 4.347481e-13 over 4 seeds (sd 1.242872e-13, 28.6% of mean; min 3.288626e-13, max 6.123223e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-03stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-03stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-03stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-03stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
