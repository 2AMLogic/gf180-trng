---
record: 2026-07-31-ro-inv-05stage-jitter-13
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ff bjt_ff diode_ff res_ff moscap_ff mimcap_ff)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ff
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-13/
  files:
    - ff_27c_2.97v-run0.spice  sha256:c47c20ef47b323657f6de8817ce6bbc4bead6e521c9b82fe6315ce102f142e61
    - ff_27c_2.97v-run0.log  sha256:7bf22a4d19aff552022d7b48d8f767920ed9ab2997814908775c0a2b81015478
    - ff_27c_2.97v-run1.spice  sha256:5618a90be444255ceafe472b47032e1fa470914f9fc4a5563555249ea514dc4c
    - ff_27c_2.97v-run1.log  sha256:15ac92e8b01b90687615da7701d5985fe72430e77c6bb940daeee17cbc568291
    - ff_27c_2.97v-run2.spice  sha256:00bb68b4aa1deb09071ae210f7a473c90f4eedfab49bd7395c5bf2df0b03d2c4
    - ff_27c_2.97v-run2.log  sha256:6a2597dd235dbd6f5020e03a7fbfe4bef63541bf151ff60d9e15695d500b914b
    - ff_27c_2.97v-run3.spice  sha256:f4c406c5b007daa7fdfbe6d9001225dca73bad40601fd696edb540c6633f5474
    - ff_27c_2.97v-run3.log  sha256:63b4220054e87930bf8c28d394c797b63bfd0a494350fc65b972bb71ecb15f15
wall_time: 3.5m
---

## Result

- `period`: mean 5.614748e-10 over 4 seeds (sd 8.535907e-15, 0.0% of mean; min 5.614651e-10, max 5.614839e-10)
- `f_osc`: mean 1.781024e+09 over 4 seeds (sd 27076.3, 0.0% of mean; min 1.780995e+09, max 1.781055e+09)
- `slew_v_per_s`: mean 3.345069e+10 over 4 seeds (sd 3.965936e+07, 0.1% of mean; min 3.340832e+10, max 3.350065e+10)
- `sigma_1`: mean 9.022051e-14 over 4 seeds (sd 8.482795e-15, 9.4% of mean; min 8.029119e-14, max 9.883814e-14)
- `sigma_2`: mean 1.243976e-13 over 4 seeds (sd 9.789851e-15, 7.9% of mean; min 1.138087e-13, max 1.348334e-13)
- `sigma_4`: mean 1.814877e-13 over 4 seeds (sd 1.386442e-14, 7.6% of mean; min 1.690947e-13, max 1.999027e-13)
- `sigma_8`: mean 2.735809e-13 over 4 seeds (sd 2.976101e-14, 10.9% of mean; min 2.402108e-13, max 3.041243e-13)
- `sigma_16`: mean 4.129655e-13 over 4 seeds (sd 7.105907e-14, 17.2% of mean; min 3.491654e-13, max 4.935795e-13)
- `sigma_32`: mean 5.849507e-13 over 4 seeds (sd 1.549769e-13, 26.5% of mean; min 4.541058e-13, max 7.855892e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ff --temps 27 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ff / 2.97 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
