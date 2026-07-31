---
record: 2026-07-31-ro-cinv-09stage-jitter-04
date: 2026-07-31T20:05:18Z
status: valid
supersedes: 2026-07-31-ro-cinv-09stage-jitter-01

testbench:
  path: sim/tb/ro-cinv-09stage-jitter/tb_ro_cinv_09stage_jitter.sp
  sha: 14f2ebcbd6b97b99223bc5dbdb17b2ee56493df2
netlist:
  path: sim/tb/ro-cinv-09stage-jitter/tb_ro_cinv_09stage_jitter.sp
  sha: 14f2ebcbd6b97b99223bc5dbdb17b2ee56493df2
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
  tstop: 580n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz))
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-cinv-09stage-jitter-04/
  files:
    - tt_27c_3.30v-run0.spice  sha256:49e471e8f7cc1d7dd4e5c458158808717c565d316269d3338476783678553924
    - tt_27c_3.30v-run0.log  sha256:f4455e4b6c3f9b8117b1a3c54fa1cb7735add509f02544fc67250de5470ca218
    - tt_27c_3.30v-run1.spice  sha256:e82221e19e59df659dd03f36eae651b736a81c217ca11bac6da66e4b8cf11d40
    - tt_27c_3.30v-run1.log  sha256:8404b37e71615ad6ff4fb41cde671a7caebf25a25317afa09be0c572cb739d6a
    - tt_27c_3.30v-run2.spice  sha256:2915e25003db0dd8543dea69005e4b5864926634683f35ff1a16d92ca8b70bd8
    - tt_27c_3.30v-run2.log  sha256:ab7584a0ba86ce3ab9ff09192233dd75370ad635b48ec748cb491b666da45c71
    - tt_27c_3.30v-run3.spice  sha256:d481150d41a96029283ad24e5977cd535b5795f24321330ab35c49b02de470ba
    - tt_27c_3.30v-run3.log  sha256:97b3d5edc6bd4856937da5575d16c8d3a2eaef03d6c91034dd8fc116ef8b0715
wall_time: 18.1m
---

## Result

- `period`: mean 2.268543e-09 over 4 seeds (sd 2.676114e-14, 0.0% of mean; min 2.268510e-09, max 2.268571e-09)
- `f_osc`: mean 4.408115e+08 over 4 seeds (sd 5200.1, 0.0% of mean; min 4.408061e+08, max 4.408179e+08)
- `slew_v_per_s`: mean 1.471477e+10 over 4 seeds (sd 2.518815e+07, 0.2% of mean; min 1.469082e+10, max 1.475025e+10)
- `sigma_1`: mean 2.079661e-13 over 4 seeds (sd 5.647212e-15, 2.7% of mean; min 2.006908e-13, max 2.144716e-13)
- `sigma_2`: mean 2.580241e-13 over 4 seeds (sd 1.213892e-14, 4.7% of mean; min 2.429162e-13, max 2.709706e-13)
- `sigma_4`: mean 3.389394e-13 over 4 seeds (sd 1.222640e-14, 3.6% of mean; min 3.254147e-13, max 3.546133e-13)
- `sigma_8`: mean 4.608005e-13 over 4 seeds (sd 2.718763e-14, 5.9% of mean; min 4.201773e-13, max 4.774945e-13)
- `sigma_16`: mean 6.384059e-13 over 4 seeds (sd 1.303534e-13, 20.4% of mean; min 4.437105e-13, max 7.173564e-13)
- `sigma_32`: mean 9.386130e-13 over 4 seeds (sd 2.278482e-13, 24.3% of mean; min 6.312581e-13, max 1.180935e-12)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-cinv-09stage-jitter --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
