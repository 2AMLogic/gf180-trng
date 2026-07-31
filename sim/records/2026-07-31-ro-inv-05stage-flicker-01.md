---
record: 2026-07-31-ro-inv-05stage-flicker-01
date: 2026-07-31T19:21:43Z
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
  tstop: 170n
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=1 NAMP=5.4772e-5 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)) NALPHA=1 NAMP=5.4772e-5 (1/f corner intended at 3e+07 Hz)
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-07-31-ro-inv-05stage-flicker-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:bba7033b5a7d78325afef0baef56069bc098c3f776a4eb9b7eb237e5e6caf108
    - tt_27c_3.30v-run0.log  sha256:f4d0008a735ebc82be6074e9fef76c024105188f842033ebceb94b83dd4c5b70
    - tt_27c_3.30v-run1.spice  sha256:e8d0c74f4bdd805d351097ee080a4ede8595de45e0a9af2765307fc107c92189
    - tt_27c_3.30v-run1.log  sha256:58caca83b444a970706cca0395d5d95e42b5e5eaba7882907eeb00a990e09b16
    - tt_27c_3.30v-run2.spice  sha256:5d659fa8748e230570f0f9560de35382a1cd394a6d0f2a856d5ec3ef97617778
    - tt_27c_3.30v-run2.log  sha256:462bf0d3420dda085dae3c41a4ce8c0f91ff219852c8cb9f1b904c16c1c9fccf
    - tt_27c_3.30v-run3.spice  sha256:e46d327094e2c4e8f97ae96b8d4e2f9714919d401d985c2a45a9a921e68692db
    - tt_27c_3.30v-run3.log  sha256:0275ac9bd7cc060f1dea5e70025f5e6de4b4c8d222b628b7f3df56b6ea3c59eb
wall_time: 9.7m
---

## Result

- `period`: mean 6.213376e-10 over 4 seeds (sd 3.023069e-15, 0.0% of mean; min 6.213347e-10, max 6.213410e-10)
- `f_osc`: mean 1.609431e+09 over 4 seeds (sd 7830.56, 0.0% of mean; min 1.609422e+09, max 1.609439e+09)
- `slew_v_per_s`: mean 3.456003e+10 over 4 seeds (sd 6.108475e+07, 0.2% of mean; min 3.450078e+10, max 3.464567e+10)
- `sigma_1`: mean 8.128163e-14 over 4 seeds (sd 5.650585e-15, 7.0% of mean; min 7.397635e-14, max 8.723728e-14)
- `sigma_2`: mean 1.126622e-13 over 4 seeds (sd 7.692320e-15, 6.8% of mean; min 1.035194e-13, max 1.211801e-13)
- `sigma_4`: mean 1.585262e-13 over 4 seeds (sd 1.712827e-14, 10.8% of mean; min 1.419740e-13, max 1.746088e-13)
- `sigma_8`: mean 2.161259e-13 over 4 seeds (sd 3.684116e-14, 17.0% of mean; min 1.830236e-13, max 2.591759e-13)
- `sigma_16`: mean 2.714202e-13 over 4 seeds (sd 7.944696e-14, 29.3% of mean; min 1.993880e-13, max 3.834974e-13)
- `sigma_32`: mean 3.739334e-13 over 4 seeds (sd 1.509435e-13, 40.4% of mean; min 2.146798e-13, max 5.652642e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-flicker --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-flicker --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-flicker --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-flicker --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
