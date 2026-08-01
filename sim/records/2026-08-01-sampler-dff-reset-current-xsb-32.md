---
record: 2026-08-01-sampler-dff-reset-current-xsb-32
date: 2026-08-01T21:06:14Z
status: valid

testbench:
  path: sim/tb/sampler-dff-reset-current-xsb/tb_sampler_dff_reset_current_xsb.sp
  sha: 7c3523f3622425acfe9deb21a86a5f7a25ecd1ce
netlist:
  path: design/sampler_core.spice
  sha: 127c7959d1940ae2898bc90a268c1b2caa40311e
repo_commit: 443b434c664e2dfd3603837b70c929eef4c5c077-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: fs bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: fs
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran
  tstop: 4.6n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-sampler-dff-reset-current-xsb-32/
  files:
    - fs_27c_3.30v.spice  sha256:8044d39a94b94e48d36e3a3aac0ceadae69b13e85ed87cc576d320023e9c0434
    - fs_27c_3.30v.log  sha256:441d00fcab0e30ca234a3bdb9282dc4f3ab5211c6d5657e251c9dd8cd75cc4a7
wall_time: 4.1s
---

## Result

- `i_reset_xsb_a`: 1.012990e-04
- `p_reset_xsb_w`: 3.342868e-04
- `i_reset_xsb_first_a`: 1.012990e-04
- `i_reset_xsb_last_a`: 1.012990e-04
- `q_v`: -1.139642e-07

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-reset-current-xsb --corners fs --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (fs / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 4); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- D is an ideal 500 ps (2 GHz) square wave, not the real ro_array_core -- deliberately, so this record does not conflate the reset-window conduction mechanism's PVT dependence with the ring's own frequency PVT dependence. See the testbench header for why the result should not depend on the chosen frequency (checked via i_reset_xsb_first_a vs i_reset_xsb_last_a, not assumed).
- Models the WORST-CASE phase relationship (clk held at 0 for the whole window), not any specific power-on sequence -- how long reset is actually asserted, and at what clk phase, is a system-level timing question #26 owns, not measured here.
- This is deliberate resistive contention between two simultaneously-ON pass devices, not subthreshold/junction leakage -- do not compare this current directly against sim/tb/device-leakage-03v3/ or sim/tb/ro-inv-05stage-stopped-leakage/ figures as if they were the same phenomenon.
- The 50% duty cycle assumed by driving D symmetrically is representative, not measured from xo -- xo's own duty cycle (rise/fall symmetry of the XOR node) is not characterized by this testbench or any other in this repository.
- D's driving current is idealized as a zero-impedance source powered from the same vdd rail (fq/fqd both integrate into the same charge node -- see the testbench header): a real xor2 output stage has finite ON resistance, which this record does not include.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
