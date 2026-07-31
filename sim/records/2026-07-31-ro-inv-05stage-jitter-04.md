---
record: 2026-07-31-ro-inv-05stage-jitter-04
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
  voltage: 2.970 V (nominal 3.3 V, -10%)
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-04/
  files:
    - tt_27c_2.97v-run0.spice  sha256:b849b028e700b4b523bd323eda716e8a08199971ace73c189d79d467a3156cdf
    - tt_27c_2.97v-run0.log  sha256:1b9bbc93b1caad80668318198a8daa13b2a74036e0b099c06ce5de1f04729497
    - tt_27c_2.97v-run1.spice  sha256:501b40d4bdad6e3c3108065e90a5fc4a488a2c08903d51ff785ace29cd29d90c
    - tt_27c_2.97v-run1.log  sha256:6e518d42b4309ce4a0fe71b0039c48e238635e0ad503f077ef411429ea17ba4f
    - tt_27c_2.97v-run2.spice  sha256:2c6d36bd7f35d2aa86636cff883a4b74ffea18b0655546dc037b68f076d355e4
    - tt_27c_2.97v-run2.log  sha256:e1bbce9d21918f9763510ccb8e0adb9f24865296a2f1bd550334355171636d3e
    - tt_27c_2.97v-run3.spice  sha256:93acba3e7a1eb0bac0d77ae0edd1134b104d592a34ac9d26ec83529e08bcced5
    - tt_27c_2.97v-run3.log  sha256:ef1c2ddb8dcfd8345bcb2501e68f58f1bc91d3a44433e9650ca267e5aeb31052
wall_time: 8.5m
---

## Result

- `period`: mean 6.775387e-10 over 4 seeds (sd 1.000639e-14, 0.0% of mean; min 6.775284e-10, max 6.775496e-10)
- `f_osc`: mean 1.475930e+09 over 4 seeds (sd 21797.6, 0.0% of mean; min 1.475907e+09, max 1.475953e+09)
- `slew_v_per_s`: mean 2.870192e+10 over 4 seeds (sd 3.275409e+07, 0.1% of mean; min 2.866657e+10, max 2.874008e+10)
- `sigma_1`: mean 1.037328e-13 over 4 seeds (sd 7.046653e-15, 6.8% of mean; min 9.653169e-14, max 1.127357e-13)
- `sigma_2`: mean 1.409911e-13 over 4 seeds (sd 6.264113e-15, 4.4% of mean; min 1.347226e-13, max 1.476624e-13)
- `sigma_4`: mean 1.967821e-13 over 4 seeds (sd 2.371642e-14, 12.1% of mean; min 1.785582e-13, max 2.309243e-13)
- `sigma_8`: mean 2.712222e-13 over 4 seeds (sd 7.641799e-14, 28.2% of mean; min 2.032685e-13, max 3.800222e-13)
- `sigma_16`: mean 3.710889e-13 over 4 seeds (sd 1.317246e-13, 35.5% of mean; min 2.529784e-13, max 5.591279e-13)
- `sigma_32`: mean 4.227530e-13 over 4 seeds (sd 1.619330e-13, 38.3% of mean; min 2.815451e-13, max 6.231300e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps 27 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
