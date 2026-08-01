---
record: 2026-08-01-sampler-dff-reset-current-xsb-01
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: tt
  voltage: 2.970 V (nominal 3.3 V, -10%)
  temperature: -40

analysis:
  type: tran
  tstop: 4.6n
  tstep: 1p (print step; ngspice's own LTE sets the actual solver step)
  tmax: n/a
  noise_params: n/a
  runs: 1
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-08-01-sampler-dff-reset-current-xsb-01/
  files:
    - tt_-40c_2.97v.spice  sha256:f0fff789d68fdcaaa6ad2786bcd8c7f42e7733b8c4a8346e04fb7d8fcaac83ef
    - tt_-40c_2.97v.log  sha256:04d12719f8aadfe31a8c49bfde5b05e982f458d15f4f8d6ea1843bf1377f10c6
wall_time: 5.1s
---

## Result

- `i_reset_xsb_a`: 8.950049e-05
- `p_reset_xsb_w`: 2.658165e-04
- `i_reset_xsb_first_a`: 8.950048e-05
- `i_reset_xsb_last_a`: 8.950050e-05
- `q_v`: 1.441218e-08

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-reset-current-xsb --corners tt --temps -40 --supply 2.97 --supply-tol 0 --no-write
```

## Caveats

- Single corner (tt / 2.97 V / -40 C). Says nothing about any other corner.
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
