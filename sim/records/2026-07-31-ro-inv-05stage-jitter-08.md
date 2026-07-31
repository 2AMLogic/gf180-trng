---
record: 2026-07-31-ro-inv-05stage-jitter-08
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 125

analysis:
  type: tran-noise
  tstop: 170n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-08/
  files:
    - tt_125c_3.30v-run0.spice  sha256:de356b98126a996c21ae3888ace18bed369d0f63777c25f3c81722e4ff3f822a
    - tt_125c_3.30v-run0.log  sha256:77d53ae258556ca30b1359c5ec2f8b062071971e6a3d84e23b8e026fa61d319a
    - tt_125c_3.30v-run1.spice  sha256:9799c752da5dd02bb3582c59f8edf008bc72bdfba13a0ffff26fbe171308346b
    - tt_125c_3.30v-run1.log  sha256:102d73b62b644cd09efa14d38fba2ce17f2e07ef6f1add0b2f29f68e287385ea
    - tt_125c_3.30v-run2.spice  sha256:4eac2b56c9be1460c8a85ab25b5c308151413d33a776d8d438a6d5765a6076a2
    - tt_125c_3.30v-run2.log  sha256:8f3c48943a3ffe3604c51cf8baf713bf5e1c57ff17fe89be839abb0ea0fcd266
    - tt_125c_3.30v-run3.spice  sha256:843b329480858958c077516b787e89be47cf22e718facada906f3150dae3e8ca
    - tt_125c_3.30v-run3.log  sha256:e7170c5c6034992de48e9baf547d91795e65dac59f8460d688a1fffde80ce802
wall_time: 5.3m
---

## Result

- `period`: mean 7.262217e-10 over 4 seeds (sd 8.224083e-15, 0.0% of mean; min 7.262096e-10, max 7.262278e-10)
- `f_osc`: mean 1.376990e+09 over 4 seeds (sd 15593.9, 0.0% of mean; min 1.376978e+09, max 1.377013e+09)
- `slew_v_per_s`: mean 2.946925e+10 over 4 seeds (sd 3.616870e+07, 0.1% of mean; min 2.943669e+10, max 2.952096e+10)
- `sigma_1`: mean 9.320698e-14 over 4 seeds (sd 4.263440e-15, 4.6% of mean; min 8.870554e-14, max 9.851789e-14)
- `sigma_2`: mean 1.286327e-13 over 4 seeds (sd 6.440276e-15, 5.0% of mean; min 1.221783e-13, max 1.373699e-13)
- `sigma_4`: mean 1.781286e-13 over 4 seeds (sd 1.517957e-14, 8.5% of mean; min 1.594447e-13, max 1.940181e-13)
- `sigma_8`: mean 2.430667e-13 over 4 seeds (sd 4.227076e-14, 17.4% of mean; min 1.944529e-13, max 2.902134e-13)
- `sigma_16`: mean 3.197034e-13 over 4 seeds (sd 5.595437e-14, 17.5% of mean; min 2.671414e-13, max 3.986179e-13)
- `sigma_32`: mean 4.362765e-13 over 4 seeds (sd 1.844582e-13, 42.3% of mean; min 2.579244e-13, max 6.822209e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 125 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
