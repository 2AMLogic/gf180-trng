---
record: 2026-10-15-ro-array-supply-ripple-binding-beat-01
date: 2026-10-15T09:36:43Z
status: valid

testbench:
  path: sim/tb/ro-array-supply-ripple/tb_ro_array_supply_ripple.sp
  sha: cecaccd7c1dcb87d6563e081b3cc9c7d0342ad28
netlist:
  path: design/ro_array_core.spice
  sha: fd0aa75500320b36f980126377e3d07c71c0e6b1
repo_commit: 8467ccc79f77605271dd6186dfdcf96d44fa164d-dirty

pdk: gf180mcuD @ c6d73a35f524070e85faff4a6a9eef49553ebc2b
pdk.models:
  - libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  klt: 0.7.1.dev497+g7ea1e4bc8d31 (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V)
  temperature: 125

analysis:
  type: tran
  tstop: 700n
  tstep: 10p
  tmax: n/a
  noise_params: n/a (deterministic: no noise, no mismatch)
  runs: 7
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-10-15-ro-array-supply-ripple-binding-beat-01/
  files:
    - report.json  sha256:ed4d03cad9ad29670a705756ee7772266d38e5beb6c45409c2df881a85f14979
    - request.json  sha256:c9d35c994150512cfd270dff196f049a890f5506997c13dbb9c45134e7028db8
    - stderr.txt  sha256:3d3a93f996239dbfcd0bd960e2c0e560532feed97642b18163a89e5f5096ca0e
wall_time: 8.3m
---

## Result

Request `binding-beat` (7 units, one per control or perturbed case), executed on the batch fleet through `klt sim` (fleet jobs: klt-sim-fcc7ab6b9cb5). Ripple frequency 7.65 MHz; solver step 10 ps. Schematic-level deterministic susceptibility of `design/ro_array_core.spice` to an ideal series sinusoid on the ring supply pin(s). The zero-amplitude row is the control. Produced by `python3 sim/tools/supply_ripple.py analyze`.

| placement | amp (mV) | rails | ring1 x (ps) | ring2 x (ps) | beat-phase x (ps) | ring1 ffm (ppm/mV) | ring1 resid rms (ps) | ring1 tone/sigma | tone explains |
|---|---|---|---|---|---|---|---|---|---|
| control | 0 | - | 2.55 | 1.95 | 3.94 | n/a | 1.82 | 7.3 | 0.5154 |
| ring1 | 10 | OUT | 64.2 | 1.97 | 64.8 | 309 | 1.57 | 185.0 | 0.9989 |
| ring1 | 50 | OUT | 328 | 2.05 | 329 | 315 | 1.81 | 819.2 | 0.9999 |
| ring1 | 150 | OUT | 988 | 1.87 | 988 | 317 | 3.6 | 1242.1 | 1.0000 |
| both | 10 | OUT | 63.9 | 64.5 | 6.01 | 307 | 1.86 | 155.8 | 0.9984 |
| both | 50 | OUT | 328 | 325 | 16.8 | 315 | 1.89 | 786.2 | 0.9999 |
| both | 150 | OUT | 987 | 976 | 45.6 | 316 | 3.13 | 1427.7 | 1.0000 |

x = displacement amplitude at the injected frequency; ffm = fractional-frequency modulation; `OUT` in `rails` would mark a perturbed rail outside the 2.97-3.63 V envelope.

Limits of interpretation:

- Schematic-level DUT (design/ro_array_core.spice), deterministic (no noise, no mismatch), ideal series sinusoid: not an extracted supply network, not a physical aggressor.
- Only the ring supply pins (vddr1/vddr2) are perturbed; the output buffers and XOR combiner on `vdd`, the enable, ground and substrate are not.
- Reports susceptibility (timing response per volt). It is not a jitter, a min-entropy, a filter-sizing or an impedance-target result, and ripple-induced timing variation must not enter the sizing law as random jitter.
- A grid of 3 amplitudes x 2 placements x 2 frequency classes x 2 PVT corners: other corners, frequencies and phases between the two rails are untested.

## How to reproduce

```sh
python3 sim/tools/supply_ripple.py emit --check
python3 sim/tools/supply_ripple.py run binding-beat --outdir DIR
python3 sim/tools/supply_ripple.py analyze DIR/binding-beat.report.json
```

The simulation is deterministic (no noise, no mismatch), so a re-run reproduces the edge times up to solver and PDK-version differences.

## Caveats

- Not a supply network, substrate, aggressor or noise model; no min-entropy, filter-sizing or signoff claim is made.
- The PDK model content on the fleet is the one named in `pdk:` above; compare `pdk:` lines before pooling across records.

---

Written by `sim/tools/supply_ripple.py ingest`. Append-only: never edit or delete this file -- a re-run or correction mints a new record and points back here via `supersedes` (see `sim/README.md`).
