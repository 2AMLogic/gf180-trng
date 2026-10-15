---
record: 2026-10-15-ro-array-supply-ripple-nominal-lowf-p1-01
date: 2026-10-15T13:02:19Z
status: valid

testbench:
  path: sim/tb/ro-array-supply-ripple/tb_ro_array_supply_ripple.sp
  sha: cecaccd7c1dcb87d6563e081b3cc9c7d0342ad28
netlist:
  path: design/ro_array_core.spice
  sha: fd0aa75500320b36f980126377e3d07c71c0e6b1
repo_commit: 82cb08bd08fc4e1ffe415e14d803ec1c865de9cf-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - libs.tech/ngspice/sm141064.ngspice (sections: typical bjt_typical diode_typical res_typical moscap_typical mimcap_typical)

tool:
  klt: 0.7.1.dev500+g247e3c89b14b (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: tt
  voltage: 3.300 V (nominal 3.3 V)
  temperature: 27

analysis:
  type: tran
  tstop: 2700n
  tstep: 10p
  tmax: n/a
  noise_params: n/a (deterministic: no noise, no mismatch)
  runs: 3
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-10-15-ro-array-supply-ripple-nominal-lowf-p1-01/
  files:
    - report.json  sha256:16a0574eac1dccbbb3b2c9a3f31df7d58b9d26b8b1db05e87a04423b3edbfd08
    - request.json  sha256:f509f4959d35489cedfced7b396a3a73f05f07a89334a8a9a994de51149b756d
    - stderr.txt  sha256:e31cc613f074e9e054b50f6dfa30abc32459e3a8ab3fbe410b91a62794b51b99
wall_time: 39.9s
---

## Result

Request `nominal-lowf-p1` (3 units, one per control or perturbed case), executed on the batch fleet through `klt sim` (fleet jobs: klt-sim-be91bc34af67). Ripple frequency 2 MHz; solver step 10 ps. Schematic-level deterministic susceptibility of `design/ro_array_core.spice` to an ideal series sinusoid on the ring supply pin(s). The zero-amplitude row is the control. Produced by `python3 sim/tools/supply_ripple.py analyze`.

| placement | amp (mV) | rails | ring1 x (ps) | ring2 x (ps) | beat-phase x (ps) | ring1 ffm (ppm/mV) | ring1 resid rms (ps) | ring1 tone/sigma | tone explains |
|---|---|---|---|---|---|---|---|---|---|
| control | 0 | - | 0.145 | 0.0821 | 0.214 | n/a | 2.23 | 0.8 | 0.0021 |
| ring1 | 10 | in | 265 | 0.029 | 265 | 333 | 2.23 | 1454.3 | 0.9999 |
| ring1 | 50 | in | 1.32e+03 | 0.136 | 1.32e+03 | 333 | 2.81 | 5761.1 | 1.0000 |

x = displacement amplitude at the injected frequency; ffm = fractional-frequency modulation; `OUT` in `rails` would mark a perturbed rail outside the 2.97-3.63 V envelope.

Limits of interpretation:

- Schematic-level DUT (design/ro_array_core.spice), deterministic (no noise, no mismatch), ideal series sinusoid: not an extracted supply network, not a physical aggressor.
- Only the ring supply pins (vddr1/vddr2) are perturbed; the output buffers and XOR combiner on `vdd`, the enable, ground and substrate are not.
- Reports susceptibility (timing response per volt). It is not a jitter, a min-entropy, a filter-sizing or an impedance-target result, and ripple-induced timing variation must not enter the sizing law as random jitter.
- A grid of 3 amplitudes x 2 placements x 2 frequency classes x 2 PVT corners: other corners, frequencies and phases between the two rails are untested.

## How to reproduce

```sh
python3 sim/tools/supply_ripple.py emit --check
python3 sim/tools/supply_ripple.py run nominal-lowf-p1 --outdir DIR
python3 sim/tools/supply_ripple.py analyze DIR/nominal-lowf-p1.report.json
```

The simulation is deterministic (no noise, no mismatch), so a re-run reproduces the edge times up to solver and PDK-version differences.

## Caveats

- Not a supply network, substrate, aggressor or noise model; no min-entropy, filter-sizing or signoff claim is made.
- The PDK model content on the fleet is the one named in `pdk:` above; compare `pdk:` lines before pooling across records.

---

Written by `sim/tools/supply_ripple.py ingest`. Append-only: never edit or delete this file -- a re-run or correction mints a new record and points back here via `supersedes` (see `sim/README.md`).
