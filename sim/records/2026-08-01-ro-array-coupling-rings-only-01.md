---
record: 2026-08-01-ro-array-coupling-rings-only-01
date: 2026-08-01T23:20:58Z
status: valid

testbench:
  path: sim/tb/ro-array-coupling-rings-only/tb_ro_array_coupling_rings_only.sp
  sha: 7426eef663d599c47bf6dd6b7dbb4263066689fd
netlist:
  path: design/ro_array_sanity.spice
  sha: 969b5873c37a527f15c86e6f5619304c9b7a9d33
repo_commit: ef0edb9c3ac4b9496477e459e576fac74603816d-dirty

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
  tstop: 2.4u
  tstep: 1p (print step; ngspice's own LTE and the trnoise breakpoints at vn_dt set the actual solver step)
  tmax: n/a
  noise_params: per-stage trnoise( NA=2.2361e-3 NT=1e-11 NALPHA=0 NAMP=0 ) -> injected white PSD 1e-16 V^2/Hz (1e-08 V/sqrt(Hz)), 5 sources per ring, 10 in total
  runs: 4
seeds: [1, 2, 3, 4]

raw:
  path: sim/records/raw/2026-08-01-ro-array-coupling-rings-only-01/
  files:
    - tt_27c_3.30v-run0.spice  sha256:084f4f0774657da1fed2df0b9b8a00785300c41e8e2ce7fd33b2b140ea0175b1
    - tt_27c_3.30v-run0.log  sha256:c7c70b0aba79ad33525f99fb5be6feef72a16c7fe4b9a1ab7c0ab525ffa8a50e
    - tt_27c_3.30v-run1.spice  sha256:4ddbaae08a0d409d51bd5d349136a7e53f72ad2c0c7a3483451aba9edc6b7dbb
    - tt_27c_3.30v-run1.log  sha256:ee014cd6c3834cbe10f9fe9a62370a7776750bbf206b4225f8da29307f8e7e67
    - tt_27c_3.30v-run2.spice  sha256:ad7e9d9dba918a7b2b384cd0a29450ddfb4d43cf591de1e39c627b45a52ce03d
    - tt_27c_3.30v-run2.log  sha256:c0d3ab21916122336847b98ac98fcd8b1d52f1d5f9026d7ff70a09dfe088241a
    - tt_27c_3.30v-run3.spice  sha256:0db6cbf79855f14a0a1171ad26776348fccf9d1da1990a4e468732e1a7956ffa
    - tt_27c_3.30v-run3.log  sha256:04e7eb58848f49dde570b2be1dfbe20cde9b8b1f4be3106c75810d4e3333e54b
wall_time: 853.1m
---

## Result

- `period`: mean 2.563519e-09 over 4 seeds (sd 7.751224e-15, 0.0% of mean; min 2.563510e-09, max 2.563527e-09)
- `f_osc`: mean 3.900888e+08 over 4 seeds (sd 1179.5, 0.0% of mean; min 3.900876e+08, max 3.900902e+08)
- `period_r2`: mean 2.369131e-09 over 4 seeds (sd 2.037851e-14, 0.0% of mean; min 2.369119e-09, max 2.369162e-09)
- `period_startup16`: mean 2.563549e-09 over 4 seeds (sd 6.152940e-14, 0.0% of mean; min 2.563488e-09, max 2.563618e-09)
- `period_b00`: mean 2.563516e-09 over 4 seeds (sd 4.819840e-14, 0.0% of mean; min 2.563445e-09, max 2.563547e-09)
- `period_b01`: mean 2.563484e-09 over 4 seeds (sd 4.854660e-14, 0.0% of mean; min 2.563431e-09, max 2.563542e-09)
- `period_b02`: mean 2.563601e-09 over 4 seeds (sd 5.839531e-14, 0.0% of mean; min 2.563542e-09, max 2.563669e-09)
- `period_b03`: mean 2.563525e-09 over 4 seeds (sd 5.740832e-14, 0.0% of mean; min 2.563448e-09, max 2.563583e-09)
- `period_b04`: mean 2.563482e-09 over 4 seeds (sd 5.110187e-14, 0.0% of mean; min 2.563406e-09, max 2.563517e-09)
- `period_b05`: mean 2.563516e-09 over 4 seeds (sd 1.069676e-13, 0.0% of mean; min 2.563358e-09, max 2.563596e-09)
- `period_b06`: mean 2.563506e-09 over 4 seeds (sd 9.502985e-14, 0.0% of mean; min 2.563433e-09, max 2.563644e-09)
- `period_b07`: mean 2.563471e-09 over 4 seeds (sd 7.678246e-15, 0.0% of mean; min 2.563463e-09, max 2.563481e-09)
- `period_b08`: mean 2.563518e-09 over 4 seeds (sd 1.007693e-13, 0.0% of mean; min 2.563446e-09, max 2.563663e-09)
- `period_b09`: mean 2.563552e-09 over 4 seeds (sd 7.887374e-14, 0.0% of mean; min 2.563438e-09, max 2.563604e-09)
- `period_b10`: mean 2.563495e-09 over 4 seeds (sd 5.737053e-14, 0.0% of mean; min 2.563438e-09, max 2.563563e-09)
- `period_b11`: mean 2.563552e-09 over 4 seeds (sd 3.989283e-14, 0.0% of mean; min 2.563521e-09, max 2.563604e-09)
- `period_b12`: mean 2.563547e-09 over 4 seeds (sd 7.090476e-14, 0.0% of mean; min 2.563479e-09, max 2.563646e-09)
- `period_b13`: mean 2.563563e-09 over 4 seeds (sd 3.803630e-14, 0.0% of mean; min 2.563521e-09, max 2.563604e-09)
- `period_b14`: mean 2.563521e-09 over 4 seeds (sd 4.500512e-14, 0.0% of mean; min 2.563479e-09, max 2.563583e-09)
- `period_b15`: mean 2.563469e-09 over 4 seeds (sd 4.959327e-14, 0.0% of mean; min 2.563396e-09, max 2.563500e-09)
- `sigma_1`: mean 6.416907e-13 over 4 seeds (sd 3.863669e-14, 6.0% of mean; min 6.003892e-13, max 6.823096e-13)
- `sigma_2`: mean 7.599511e-13 over 4 seeds (sd 2.632358e-14, 3.5% of mean; min 7.358975e-13, max 7.864888e-13)
- `sigma_4`: mean 9.474334e-13 over 4 seeds (sd 1.745572e-14, 1.8% of mean; min 9.239054e-13, max 9.658220e-13)
- `sigma_8`: mean 1.268683e-12 over 4 seeds (sd 3.435511e-14, 2.7% of mean; min 1.240370e-12, max 1.318380e-12)
- `sigma_16`: mean 1.711938e-12 over 4 seeds (sd 4.146169e-14, 2.4% of mean; min 1.659275e-12, max 1.757461e-12)
- `sigma_32`: mean 2.446947e-12 over 4 seeds (sd 1.687367e-13, 6.9% of mean; min 2.200680e-12, max 2.569822e-12)
- `sigma_64`: mean 3.576729e-12 over 4 seeds (sd 6.220921e-13, 17.4% of mean; min 2.672793e-12, max 4.088822e-12)
- `sigma_128`: mean 5.102904e-12 over 4 seeds (sd 7.741793e-13, 15.2% of mean; min 4.049435e-12, max 5.879382e-12)
- `sigma_startup16_1`: mean 4.599153e-13 over 4 seeds (sd 7.213459e-14, 15.7% of mean; min 3.805564e-13, max 5.377207e-13)
- `sigma_startup16_2`: mean 5.411547e-13 over 4 seeds (sd 4.019977e-14, 7.4% of mean; min 5.075410e-13, max 5.983195e-13)
- `sigma_startup16_4`: mean 6.799670e-13 over 4 seeds (sd 1.582973e-13, 23.3% of mean; min 5.406937e-13, max 9.075415e-13)
- `sigma_startup16_8`: mean 6.881859e-13 over 4 seeds (sd 1.966157e-13, 28.6% of mean; min 4.080196e-13, max 8.392304e-13)
- `i_ring_a`: mean 1.925250e-05 over 4 seeds (sd 2.041969e-11, 0.0% of mean; min 1.925248e-05, max 1.925253e-05)
- `p_active_w`: mean 6.353324e-05 over 4 seeds (sd 6.738476e-11, 0.0% of mean; min 6.353318e-05, max 6.353334e-05)
- `e_per_cycle_j`: mean 1.628687e-13 over 4 seeds (sd 3.607856e-19, 0.0% of mean; min 1.628683e-13, max 1.628691e-13)
- `c_eff_node_f`: mean 2.991160e-15 over 4 seeds (sd 6.625955e-21, 0.0% of mean; min 2.991154e-15, max 2.991168e-15)
- `vsup_v`: mean 3.3 over 4 seeds (sd 0, 0.0% of mean; min 3.3, max 3.3)

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ro-array-coupling-rings-only --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 1 --no-write
python3 sim/run_corners.py ro-array-coupling-rings-only --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 2 --no-write
python3 sim/run_corners.py ro-array-coupling-rings-only --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 3 --no-write
python3 sim/run_corners.py ro-array-coupling-rings-only --corners tt --temps 27 --supply 3.3 --supply-tol 0 --seeds 4 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist ro_array_sanity.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- Variant 4 of issue #51's four-variant experiment. It is comparable to sim/tb/ro-ring5-starved-jitter-long/ (the control) ONLY because the delay cell, the injected noise density, the window geometry, the print step and the corner are identical; the one intended difference is the presence of a second, unconnected ring in the same deck. period (ring 1) reproducing the control's 2.5635 ns is the record's own check that no second difference crept in.
- The two rings share no node, no device and no supply pin: vr1 and vr2 are separate zero-volt ammeter sources off the same IDEAL vsup, which has no impedance for one ring's current to develop a voltage across. This deck therefore says nothing about supply-network coupling in a real array, where the supply is not ideal. That is a separate question and needs a deck with a modelled supply impedance.
- sigma_startup16_* reproduce, inside this same run, the 16-period window opened at the second rise that sim/records/2026-08-01-ro-array-sanity-jitter-01.md used. They are a like-for-like comparison with that record and are deliberately imprecise (a 16-period estimate carries ~15 % seed-to-seed spread); the sigma_* series over the 512-period window is the precise measurement.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
