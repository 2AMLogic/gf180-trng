---
record: 2026-07-31-ro-inv-09stage-jitter-04
date: 2026-07-31T19:52:51Z
status: valid
supersedes: 2026-07-31-ro-inv-09stage-jitter-01

testbench:
  path: sim/tb/ro-inv-09stage-jitter/tb_ro_inv_09stage_jitter.sp
  sha: 1f809993aec2923642e9c288b788eb8d602a48ad
netlist:
  path: sim/tb/ro-inv-09stage-jitter/tb_ro_inv_09stage_jitter.sp
  sha: 1f809993aec2923642e9c288b788eb8d602a48ad
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
  tstop: 300n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-09stage-jitter-04/
  files:
    - tt_27c_3.30v-run0.spice  sha256:aeea5f8287252a119ade6fe6b63ce7a8afd4ab431a5e4ce4ae4253f46e1df019
    - tt_27c_3.30v-run0.log  sha256:187abe167825098aa3bb0d5fb37fc8e3cb8f8386a630efb3992ff86c0e9d2d6f
    - tt_27c_3.30v-run1.spice  sha256:afa963c253c2ae60c607db78d20e93a98d464fa68e5b6a84d60e88c41e07d780
    - tt_27c_3.30v-run1.log  sha256:ed6c232def12d6a31fc0a8ce641e21fd24947cb40d79c724ba1eafd2437f49a6
    - tt_27c_3.30v-run2.spice  sha256:36b128b6ade6954b1b1d2d9ae4bdcd8078d16e68ed4bf045b7a99c75ddee6c79
    - tt_27c_3.30v-run2.log  sha256:9133bb0dde4bd47b20ed12d475bce73cf0f01fae95db6120961b55ad7ab7d0a4
    - tt_27c_3.30v-run3.spice  sha256:d9dcd2869a881c999ce0e2cdee23e46dcea356450b9e667db2f71d27b62d6549
    - tt_27c_3.30v-run3.log  sha256:43d5bf1450b033275a8ee50ac0102ddba1e1c6b05a3bd42e8cd93fd23664f181
wall_time: 6.2m
---

## Result

- `period`: mean 1.119327e-09 over 4 seeds (sd 8.957001e-15, 0.0% of mean; min 1.119318e-09, max 1.119335e-09)
- `f_osc`: mean 8.933940e+08 over 4 seeds (sd 7149.04, 0.0% of mean; min 8.933873e+08, max 8.934009e+08)
- `slew_v_per_s`: mean 3.452070e+10 over 4 seeds (sd 5.631765e+07, 0.2% of mean; min 3.447735e+10, max 3.460026e+10)
- `sigma_1`: mean 1.185172e-13 over 4 seeds (sd 7.049316e-15, 5.9% of mean; min 1.120131e-13, max 1.265485e-13)
- `sigma_2`: mean 1.541064e-13 over 4 seeds (sd 9.446260e-15, 6.1% of mean; min 1.469710e-13, max 1.679854e-13)
- `sigma_4`: mean 2.091459e-13 over 4 seeds (sd 2.043828e-14, 9.8% of mean; min 1.906282e-13, max 2.337069e-13)
- `sigma_8`: mean 2.740428e-13 over 4 seeds (sd 3.294680e-14, 12.0% of mean; min 2.424217e-13, max 3.038270e-13)
- `sigma_16`: mean 3.281037e-13 over 4 seeds (sd 5.288654e-14, 16.1% of mean; min 2.627112e-13, max 3.912187e-13)
- `sigma_32`: mean 4.006583e-13 over 4 seeds (sd 8.395843e-14, 21.0% of mean; min 3.417207e-13, max 5.244172e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-09stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-09stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-09stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-09stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
