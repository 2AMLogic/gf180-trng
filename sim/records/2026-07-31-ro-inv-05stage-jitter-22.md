---
record: 2026-07-31-ro-inv-05stage-jitter-22
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
  path: sim/records/raw/2026-07-31-ro-inv-05stage-jitter-22/
  files:
    - ss_27c_2.97v-run0.spice  sha256:b972a72095d0813b69b94c057642f18548d51a9f77194df7732928ccfaeca5aa
    - ss_27c_2.97v-run0.log  sha256:e30c7b7804bd89f9b42cf7d5c19116955fb3322fe4f9ab677cbb0a21986c7721
    - ss_27c_2.97v-run1.spice  sha256:fc39c704a1af7bb9ef13a9a0e8e1dbff0502450da6648f80c4b6e330319eed38
    - ss_27c_2.97v-run1.log  sha256:f8e8bdfc49286bb8637d273f68dfd1afe1381405ada9c8d4a87bb28c80baf600
    - ss_27c_2.97v-run2.spice  sha256:d1d15c4a980985471f55b5c83e9a3bdeb216f12f238e1e48c1fa965720618bcd
    - ss_27c_2.97v-run2.log  sha256:1ffed578504fe54871872e46cbfbabcce0e07871ec67bf541f7c16e6ff237ac6
    - ss_27c_2.97v-run3.spice  sha256:747f1d835ac4e16e4f38ebc12ccbe4d35a3227c1e5b3f8215e701eae3011ac67
    - ss_27c_2.97v-run3.log  sha256:0c46322443560774b27de3a887d10d5469afb6687bc6439c32a2852a333715ac
wall_time: 2.6m
---

## Result

- `period`: mean 8.338200e-10 over 4 seeds (sd 1.321059e-14, 0.0% of mean; min 8.338089e-10, max 8.338371e-10)
- `f_osc`: mean 1.199300e+09 over 4 seeds (sd 19000.9, 0.0% of mean; min 1.199275e+09, max 1.199316e+09)
- `slew_v_per_s`: mean 2.417372e+10 over 4 seeds (sd 5.820181e+07, 0.2% of mean; min 2.414143e+10, max 2.426074e+10)
- `sigma_1`: mean 1.204441e-13 over 4 seeds (sd 3.969018e-15, 3.3% of mean; min 1.150904e-13, max 1.242935e-13)
- `sigma_2`: mean 1.690163e-13 over 4 seeds (sd 1.515473e-14, 9.0% of mean; min 1.490024e-13, max 1.847604e-13)
- `sigma_4`: mean 2.346941e-13 over 4 seeds (sd 1.121066e-14, 4.8% of mean; min 2.224160e-13, max 2.450552e-13)
- `sigma_8`: mean 3.277884e-13 over 4 seeds (sd 3.257651e-14, 9.9% of mean; min 2.789349e-13, max 3.446444e-13)
- `sigma_16`: mean 4.811221e-13 over 4 seeds (sd 6.861359e-14, 14.3% of mean; min 3.900722e-13, max 5.566399e-13)
- `sigma_32`: mean 6.898970e-13 over 4 seeds (sd 1.478103e-13, 21.4% of mean; min 5.402230e-13, max 8.739318e-13)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 2.97 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 2.97 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 2.97 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-inv-05stage-jitter --corners ss --temps 27 --supply 2.97 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (ss / 2.97 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
