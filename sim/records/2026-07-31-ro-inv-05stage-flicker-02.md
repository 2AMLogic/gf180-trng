---
record: 2026-07-31-ro-inv-05stage-flicker-02
date: 2026-07-31T19:26:40Z
status: valid

testbench:
  path: sim/tb/ro-inv-05stage-flicker/tb_ro_inv_05stage_flicker.sp
  sha: 12d732746920d22400f28b57b6f425b2622a0f96
netlist:
  path: sim/tb/ro-inv-05stage-flicker/tb_ro_inv_05stage_flicker.sp
  sha: 12d732746920d22400f28b57b6f425b2622a0f96
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
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=1 NAMP=5.4772e-5 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)) NALPHA=1 NAMP=5.4772e-5 (1/f corner intended at 3e+07 Hz)
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-flicker-02/
  files:
    - ff_-40c_3.63v-run0.spice  sha256:4f882fbfaf12f3ba4adb4a0f02288a1e7579160ddc29a9a103a3d2c8e9cc81c1
    - ff_-40c_3.63v-run0.log  sha256:7fdce4537645b31eec0bd9406e8e37a331378db712cc3b465f9436561be209a6
    - ff_-40c_3.63v-run1.spice  sha256:e05c2a38c6b636810da0ba1c7957eb43f5a284111e68fa2f5741f8b216086e72
    - ff_-40c_3.63v-run1.log  sha256:571f1abe0b81ff46a6ecf57cbb190c9413409b366a6af2797388602fff8f85fd
    - ff_-40c_3.63v-run2.spice  sha256:307d7f541e56c5af522809d7d78d5ac5a3f384614fa9ba22d62694ccc6024271
    - ff_-40c_3.63v-run2.log  sha256:76072a402a765b2176a4ea8255d62c2f0c44bb493b6f79b154250399906d03ba
    - ff_-40c_3.63v-run3.spice  sha256:9ab297bd39582809e5820a667284668a0e39d399603f6f52cb79d8fba1dd8b9c
    - ff_-40c_3.63v-run3.log  sha256:1630a39899d57e7c67bf40c0d1b5eeaef8179e6f5c0df0ad47107385ecaf632f
wall_time: 10.0m
---

## Result

- `period`: mean 4.342473e-10 over 4 seeds (sd 5.954330e-15, 0.0% of mean; min 4.342384e-10, max 4.342512e-10)
- `f_osc`: mean 2.302835e+09 over 4 seeds (sd 31576.5, 0.0% of mean; min 2.302814e+09, max 2.302882e+09)
- `slew_v_per_s`: mean 5.323179e+10 over 4 seeds (sd 9.613145e+07, 0.2% of mean; min 5.312843e+10, max 5.334705e+10)
- `sigma_1`: mean 6.321064e-14 over 4 seeds (sd 6.564323e-15, 10.4% of mean; min 5.677237e-14, max 7.029419e-14)
- `sigma_2`: mean 8.577288e-14 over 4 seeds (sd 8.333419e-15, 9.7% of mean; min 7.590789e-14, max 9.404583e-14)
- `sigma_4`: mean 1.175541e-13 over 4 seeds (sd 1.817186e-14, 15.5% of mean; min 9.214634e-14, max 1.353268e-13)
- `sigma_8`: mean 1.622548e-13 over 4 seeds (sd 2.693825e-14, 16.6% of mean; min 1.314688e-13, max 1.967005e-13)
- `sigma_16`: mean 2.318568e-13 over 4 seeds (sd 5.064916e-14, 21.8% of mean; min 1.700622e-13, max 2.923947e-13)
- `sigma_32`: mean 3.273448e-13 over 4 seeds (sd 7.931542e-14, 24.2% of mean; min 2.345217e-13, max 4.184843e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-flicker --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-flicker --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-flicker --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-flicker --corners ff --temps -40 --supply 3.63 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 3.63 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
