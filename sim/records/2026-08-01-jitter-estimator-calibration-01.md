---
record: 2026-08-01-jitter-estimator-calibration-01
date: 2026-08-01T18:29:10Z
status: valid

testbench:
  path: sim/tb/jitter-estimator-calibration/tb_jitter_estimator_cal.sp
  sha: 013f0b463394b72e83a59a123dc4db90664efb84
netlist:
  path: sim/tb/jitter-estimator-calibration/tb_jitter_estimator_cal.sp
  sha: 013f0b463394b72e83a59a123dc4db90664efb84
repo_commit: 664c9039b5d4f82f7d42f0cbce2dc49076ba6b65-dirty

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
  tstop: 4u
  tstep: 10p
  tmax: n/a
  noise_params: trnoise(NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0); same S/H mapping validated in sim/tb/trnoise-calibration (S_w = 2*NA^2*NT). Each held sample v(nw) ~ N(0, NA^2); thresholding v(nw)+bias against 0 gives P(bit=1) = Phi(bias/NA) exactly.
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-01-jitter-estimator-calibration-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:2e6330d6240b7a84fedbac37dc238eae5234a3e40b02aed34bf0c9372dbaa64a
    - tt_27c_3.30v-run0.log  sha256:e217f6f752d062ef3162ea66e3c7410090eb111c4f35eadda77004dd55a0445c
    - tt_27c_3.30v-run1.spice  sha256:42dccae3e1602a33decbfb9aa2e2d0cf6b232903b2fdd2f1791d21316a86f74f
    - tt_27c_3.30v-run1.log  sha256:ca0e8d962277488e8c5e1f7f7ac9326cad2d3cc91148b3852009d25bb89e0156
    - tt_27c_3.30v-run2.spice  sha256:2c4f6e854c86b0b308666103f756afc6303c6de966269d8680620d4f8d25e4ad
    - tt_27c_3.30v-run2.log  sha256:85a994a67eb6844b0e3a6da3c8a7a7843559b66683344af5787b697df6f76a7c
    - tt_27c_3.30v-run3.spice  sha256:ae9fdb80a14aac42aecabab9d310730e4e31baabe638550c5314bcb7bd8e2c1c
    - tt_27c_3.30v-run3.log  sha256:c66d143ed1a8f6c97768591e300fdc2043ec68178d2939e3bc68228921ba03fe
wall_time: 12.4m
---

## Result

- `p1_h100`: mean 0.499922 over 4 seeds (sd 3.302545e-04, 0.1% of mean; min 0.499446, max 0.500189)
- `p1_h050`: mean 0.707165 over 4 seeds (sd 0.00101388, 0.1% of mean; min 0.70595, max 0.70831)
- `p1_h010`: mean 0.933673 over 4 seeds (sd 9.786644e-04, 0.1% of mean; min 0.932743, max 0.934816)
- `rms_check`: mean 0.00222883 over 4 seeds (sd 1.278832e-05, 0.6% of mean; min 0.00221188, max 0.00223895)
- `n_samples`: mean 4.000010e+05 over 4 seeds (sd 0, 0.0% of mean; min 4.000010e+05, max 4.000010e+05)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py jitter-estimator-calibration --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py jitter-estimator-calibration --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py jitter-estimator-calibration --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py jitter-estimator-calibration --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 2); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- Harness-bootstrap testbench: no design/ DUT schematic-derived netlist exists yet for this block, so testbench.path and netlist.path are the same self-contained demo fragment. Real DUT netlists will get their own netlist.path once design/ has content.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
