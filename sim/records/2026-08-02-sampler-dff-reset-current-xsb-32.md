---
record: 2026-08-02-sampler-dff-reset-current-xsb-32
date: 2026-08-02T00:02:44Z
status: valid

testbench:
  path: sim/tb/sampler-dff-reset-current-xsb/tb_sampler_dff_reset_current_xsb.sp
  sha: fd1ef774d7cb74b982d3b379fb2609d3859d7a79
netlist:
  path: design/sampler_core.spice
  sha: 50bc082dc2798c8b98e4ced8ebb70432549aa2ec
repo_commit: dc8570a59d334bdeec04c2e284ed2dbe14a6e0de-dirty

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
  path: sim/records/raw/2026-08-02-sampler-dff-reset-current-xsb-32/
  files:
    - fs_27c_3.30v.spice  sha256:3823be346c8998162a4ceed3910f3a9a7981f511bcfdfb75cb6a10def7062b6d
    - fs_27c_3.30v.log  sha256:f0041171981839a7c1bcc2561618e212b607d07bc676e33c72b573364da43e01
wall_time: 13.3s
---

## Result

- `i_reset_xsb_a`: 1.911450e-08
- `p_reset_xsb_w`: 6.307785e-08
- `i_reset_xsb_first_a`: 2.899950e-08
- `i_reset_xsb_last_a`: 9.229500e-09
- `q_v`: -7.311239e-06

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-reset-current-xsb --corners fs --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (fs / 3.30 V / 27 C). Says nothing about any other corner.
- Run concurrently (-j 3); wall_time is the SUMMED per-run ngspice cost for this point, not elapsed time, and is inflated relative to a quiet machine by contention between concurrent runs.
- DUT is the schematic-derived netlist sampler_core.spice; netlist.sha above is that file's blob SHA, and `python3 design/netlist.py --check` is what ties it to the schematic it claims to come from.
- D is an ideal 500 ps (2 GHz) square wave, not the real ro_array_core -- deliberately, so this record does not conflate the reset-window conduction mechanism's PVT dependence with the ring's own frequency PVT dependence. See the testbench header for why the pre-#53 result should not depend on the chosen frequency.
- Models the WORST-CASE phase relationship (clk held at 0 for the whole window), not any specific power-on sequence -- how long reset is actually asserted, and at what clk phase, is a system-level timing question #26 owns, not measured here.
- What this current IS depends on which cell the record ran against, and the record's netlist.sha says which. Pre-#53 (a reset pulldown on node m): deliberate resistive contention between two simultaneously-ON pass devices, which must NOT be compared against sim/tb/device-leakage-03v3/ or sim/tb/ro-inv-05stage-stopped-leakage/ as if it were the same phenomenon. Post-#53 (reset gated into the latches' inverters, no device on a storage node): that path does not exist and what is left is nanoamp-scale.
- i_reset_xsb_first_a vs i_reset_xsb_last_a is a start-up/frequency-dependence check only while the measured total is large compared with the charge integrator's numerical residue. On the post-#53 cell it is not -- the two halves differ by a large fraction of a very small number, and that ratio carries no physical meaning.
- The 50% duty cycle assumed by driving D symmetrically is representative, not measured from xo -- xo's own duty cycle (rise/fall symmetry of the XOR node) is not characterized by this testbench or any other in this repository.
- D's driving current is idealized as a zero-impedance source powered from the same vdd rail (fq/fqd both integrate into the same charge node -- see the testbench header): a real xor2 output stage has finite ON resistance, which this record does not include.
- clk is held at 0 for the whole window, so this says nothing about what a clk EDGE does while reset is asserted. Post-#53 that is the case the cell's reset structure turns on (see design/xschem/sampler_dff.sch's header); it is not measured by this testbench.

---

Written by `sim/run_corners.py`. Append-only: never edit or delete this
file -- a re-run or correction mints a new record and points back here
via `supersedes` (see `sim/README.md`).
