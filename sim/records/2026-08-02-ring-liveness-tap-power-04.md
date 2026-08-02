---
record: 2026-08-02-ring-liveness-tap-power-04
date: 2026-08-02T04:57:58Z
status: valid

testbench:
  path: sim/tb/ring-liveness-tap-power/tb_ring_liveness_tap_power.sp
  sha: a8e2d44807e34ce2cef7e39a8e2a206cba4a6704
netlist:
  path: design/sampler_core.spice
  sha: 50bc082dc2798c8b98e4ced8ebb70432549aa2ec
repo_commit: 0f9618ad42cdc4ada5aec54d31b13b7ec1061b2e-dirty

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
  type: tran
  tstop: 50n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-02-ring-liveness-tap-power-04/
  files:
    - tt_27c_3.30v.spice  sha256:75f8e96038806c1b552485c57bc6e70b9fc17ba00c45408b9603570bf1173cef
    - tt_27c_3.30v.log  sha256:85c840b25509ae791c5cf1632ce298dc2e287fe75a104c17f8a1a1c38dfe71af
wall_time: 9.5m
---

## Result

- `period_r1`: 7.526883e-09
- `period_r2`: 7.094625e-09
- `f_r1`: 1.328571e+08
- `f_r2`: 1.409518e+08
- `i_r1_a`: -1.854625e-05
- `i_r2_a`: -2.008637e-05
- `i_tree_a`: -2.296550e-05
- `ring_swing_v`: 3.31662
- `xo_swing_v`: 3.36309
- `p_rings_w`: -1.274877e-04
- `p_total_w`: -2.032738e-04
- `i_tap_avg_a`: -1.414789e-05
- `p_tap_avg_w`: -4.668805e-05
- `ro1_bit_end_v`: 3.3
- `ro2_bit_end_v`: 1.849018e-08
- `ro1_bit_rail_dev_v`: -7.771561e-13
- `ro2_bit_rail_dev_v`: 1.849018e-08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py ring-liveness-tap-power --corners tt --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 3.30 V / 27 C). Says nothing about any other corner.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- The tap clock (mclk, 10 ns period from t=5n) is deliberately fast and bears no resemblance to DR-0012's real fixed external sample clock rate. It exists only to exercise the two sampler_dff taps' loading and switching behaviour within the same 50 ns transient window sim/tb/ro-array-core-power/ already uses for the un-tapped baseline, so the two records are directly comparable point for point. DR-0016's stated detection latency is a sampler-clock CYCLE count (C_LIVE, default 81), independent of the clock's absolute rate, so nothing about the monitor's own timing claim depends on this deck's clock frequency.
- period_r1/r2, i_r1_a/i_r2_a, i_tree_a, ring_swing_v, xo_swing_v, p_rings_w and p_total_w use measurement expressions copied unchanged from sim/tb/ro-array-core-power/tb.json, against the same DUT (xdut = a bare ro_array_core instance, not the sampler_core wrapper) and the same 50 ns window -- this is what makes this record directly comparable, point for point, to sim/records/2026-08-01-ro-array-core-power-{04,05,06}.md (the shipped N=2 array's baseline).
- i_tap_avg_a/p_tap_avg_w average the two taps' combined switching current over a 48 ns window (charge at t=48n divided by the window -- 48n rather than the full 50 ns tstop because ngspice's adaptive transient step does not always land exactly on the requested stop time, and 48n matches the ring_swing_v/xo_swing_v/ro*_bit_end_v measurement window already used above), not per-cycle -- an average bound, not a precise energy-per-toggle figure, because the taps' own D inputs (ro1/ro2) are not synchronous to mclk and a per-cycle energy split would need a phase-locked reference this deck does not have.
- ro1_bit_end_v/ro2_bit_end_v/*_rail_dev_v confirm the taps resolve to a rail rather than lingering half-way, the same check sim/tb/sampler-array-digitize/ makes for raw_bit -- at a single sample instant (t=48n) rather than across every bit, since this deck's purpose is the loading/power bound, not a digitize demonstration.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
