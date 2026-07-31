---
record: 2026-07-31-ro-inv-05stage-jitter-01
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-01/
  files:
    - tt_-40c_2.97v-run0.spice  sha256:9720adaf1a990a186a1f0fdd3850aee8318cdb3ec11c466561a9703156c5f884
    - tt_-40c_2.97v-run0.log  sha256:3a3fbdfa1ba6cdd6e9666e093ee2f1b598113d51738dcec82db7410ffbddfae8
    - tt_-40c_2.97v-run1.spice  sha256:ef69e6fa4e3862d302c74bd92f5eba058971c6f0fec446655ceb449487c012b9
    - tt_-40c_2.97v-run1.log  sha256:80a49f2ed06110b9d17855d7e2a1e6505023be049119b24cab06fb525f65964e
    - tt_-40c_2.97v-run2.spice  sha256:3ba0931d38f5d977722c871bccc1c8b34f051734864e3c1496184dba85aedced
    - tt_-40c_2.97v-run2.log  sha256:1cf01487a8b7fcbaa924e223fdb45a60542480d06f26b09d4c5284f6c7d43dd0
    - tt_-40c_2.97v-run3.spice  sha256:b511e3510f2f64cf66049d5b135ba27ff370cbc74a71afa63a3becfcb4556e12
    - tt_-40c_2.97v-run3.log  sha256:145ada2c60437c5b51db60b70b805fb9b8ad5853c1ab99211cfca404643b6c80
wall_time: 7.1m
---

## Result

- `period`: mean 5.951232e-10 over 4 seeds (sd 5.590174e-15, 0.0% of mean; min 5.951178e-10, max 5.951289e-10)
- `f_osc`: mean 1.680324e+09 over 4 seeds (sd 15783.8, 0.0% of mean; min 1.680308e+09, max 1.680340e+09)
- `slew_v_per_s`: mean 3.315803e+10 over 4 seeds (sd 5.547689e+07, 0.2% of mean; min 3.311775e+10, max 3.323635e+10)
- `sigma_1`: mean 9.491581e-14 over 4 seeds (sd 3.254616e-15, 3.4% of mean; min 9.036292e-14, max 9.800033e-14)
- `sigma_2`: mean 1.276410e-13 over 4 seeds (sd 7.021897e-15, 5.5% of mean; min 1.203192e-13, max 1.368640e-13)
- `sigma_4`: mean 1.793355e-13 over 4 seeds (sd 1.666745e-14, 9.3% of mean; min 1.559404e-13, max 1.917919e-13)
- `sigma_8`: mean 2.499413e-13 over 4 seeds (sd 2.593425e-14, 10.4% of mean; min 2.149853e-13, max 2.732932e-13)
- `sigma_16`: mean 3.551834e-13 over 4 seeds (sd 4.645562e-14, 13.1% of mean; min 2.899621e-13, max 3.992174e-13)
- `sigma_32`: mean 4.249158e-13 over 4 seeds (sd 7.078373e-14, 16.7% of mean; min 3.260670e-13, max 4.896140e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners tt --temps -40 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / -40 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
