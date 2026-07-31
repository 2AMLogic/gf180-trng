---
record: 2026-07-31-ro-inv-05stage-jitter-26
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-26/
  files:
    - ss_125c_3.30v-run0.spice  sha256:1d54bc2705b61391d82ae638ecd10af298023ab7dcd79bcb2dde1ce27fc43ba9
    - ss_125c_3.30v-run0.log  sha256:c8be2535ef258e2c158739f74246a3aa857f0cadd1c3a1e2996b8ae37edd95cb
    - ss_125c_3.30v-run1.spice  sha256:55241f689d3e9bf360858f55ebaaee35b329d599f046cbb1aaad9b37b0ff7047
    - ss_125c_3.30v-run1.log  sha256:962f068d5c973ce146b05b2b2e151e678868e4fa7552065562cbfab8045a77a4
    - ss_125c_3.30v-run2.spice  sha256:49cd81c6726a402361fea961c826d42de39c54485e5a9f6e7eb87d5bf3471e80
    - ss_125c_3.30v-run2.log  sha256:f0cb0088efce436bcf74326313bc7849cd21a1612858b9a7074de090a7bd8812
    - ss_125c_3.30v-run3.spice  sha256:18993b3128b541a2bab3478508743f813e620ea76ec99c74449309e278727baa
    - ss_125c_3.30v-run3.log  sha256:00569a5c84c7f191856a401d1fd5a397487af8a05ac7c65cb42e50371e556d4a
wall_time: 1.5m
---

## Result

- `period`: mean 8.822452e-10 over 4 seeds (sd 8.859470e-15, 0.0% of mean; min 8.822348e-10, max 8.822544e-10)
- `f_osc`: mean 1.133472e+09 over 4 seeds (sd 11382.3, 0.0% of mean; min 1.133460e+09, max 1.133485e+09)
- `slew_v_per_s`: mean 2.513547e+10 over 4 seeds (sd 3.393850e+07, 0.1% of mean; min 2.509029e+10, max 2.517162e+10)
- `sigma_1`: mean 1.096661e-13 over 4 seeds (sd 8.097329e-15, 7.4% of mean; min 1.016738e-13, max 1.176794e-13)
- `sigma_2`: mean 1.438330e-13 over 4 seeds (sd 8.212985e-15, 5.7% of mean; min 1.342076e-13, max 1.521563e-13)
- `sigma_4`: mean 1.965823e-13 over 4 seeds (sd 1.324488e-14, 6.7% of mean; min 1.775945e-13, max 2.076080e-13)
- `sigma_8`: mean 2.755435e-13 over 4 seeds (sd 2.646646e-14, 9.6% of mean; min 2.490815e-13, max 3.074009e-13)
- `sigma_16`: mean 4.099760e-13 over 4 seeds (sd 7.690157e-14, 18.8% of mean; min 3.166910e-13, max 4.805260e-13)
- `sigma_32`: mean 6.125042e-13 over 4 seeds (sd 1.794015e-13, 29.3% of mean; min 4.111863e-13, max 7.802199e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 125 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 3.30 V / 125 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
