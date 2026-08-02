---
record: 2026-08-02-sampler-dff-reset-current-xsb-23
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
  - /Users/rwalters/.volare/gf180mcuD/libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  ngspice: "ngspice-46 : Circuit level simulation program"
  platform: macOS-26.6-arm64-arm-64bit-Mach-O

corner:
  process: ss
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
  path: sim/records/raw/2026-08-02-sampler-dff-reset-current-xsb-23/
  files:
    - ss_27c_3.30v.spice  sha256:807109f6f9e113ac810473b134ef56696a25c6fa0c5327a79e96f690832c9cde
    - ss_27c_3.30v.log  sha256:4989c5b927e7740f74af370d920a21765372ca370cdbd78cec5ce9054cbf20a4
wall_time: 12.7s
---

## Result

- `i_reset_xsb_a`: 2.212350e-08
- `p_reset_xsb_w`: 7.300755e-08
- `i_reset_xsb_first_a`: 3.359450e-08
- `i_reset_xsb_last_a`: 1.065250e-08
- `q_v`: -1.404415e-05

Numbers only. No entropy-rate or spec-compliance claim is made by this record.

## How to reproduce

```sh
python3 sim/run_corners.py sampler-dff-reset-current-xsb --corners ss --temps 27 --supply 3.3 --supply-tol 0 --no-write
```

## Caveats

- Single corner (ss / 3.30 V / 27 C). Says nothing about any other corner.
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
