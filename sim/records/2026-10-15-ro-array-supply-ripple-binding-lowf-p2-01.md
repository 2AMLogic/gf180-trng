---
record: 2026-10-15-ro-array-supply-ripple-binding-lowf-p2-01
date: 2026-10-15T13:02:20Z
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
  - libs.tech/ngspice/sm141064.ngspice (sections: ss bjt_ss diode_ss res_ss moscap_ss mimcap_ss)

tool:
  klt: 0.7.1.dev500+g247e3c89b14b (client; batch backend)
  ngspice: "ngspice-46 : Circuit level simulation program (batch fleet)"
  platform: "Linux-7.0.0-1014-aws-x86_64-with-glibc2.39 (submitting host)"

corner:
  process: ss
  voltage: 3.630 V (nominal 3.3 V)
  temperature: 125

analysis:
  type: tran
  tstop: 2700n
  tstep: 10p
  tmax: n/a
  noise_params: n/a (deterministic: no noise, no mismatch)
  runs: 3
seeds: n/a (deterministic analysis)

raw:
  path: sim/records/raw/2026-10-15-ro-array-supply-ripple-binding-lowf-p2-01/
  files:
    - report.json  sha256:63d45163099b97959a042d581d9dbde1ccd225fa4bfce5287b6d9d0c22b5b8fc
    - request.json  sha256:8d93f1ed7298b6749edb8f9fa4aba4e9db26d1bf81120266ee209b781ecef006
    - stderr.txt  sha256:e31cc613f074e9e054b50f6dfa30abc32459e3a8ab3fbe410b91a62794b51b99
wall_time: 35.3s
---

## Result

Request `binding-lowf-p2` (3 units, one per control or perturbed case), executed on the batch fleet through `klt sim` (fleet jobs: klt-sim-668edd045d0a). Ripple frequency 2 MHz; solver step 10 ps. Schematic-level deterministic susceptibility of `design/ro_array_core.spice` to an ideal series sinusoid on the ring supply pin(s). The zero-amplitude row is the control. Produced by `python3 sim/tools/supply_ripple.py analyze`.

| placement | amp (mV) | rails | ring1 x (ps) | ring2 x (ps) | beat-phase x (ps) | ring1 ffm (ppm/mV) | ring1 resid rms (ps) | ring1 tone/sigma | tone explains |
|---|---|---|---|---|---|---|---|---|---|
| control | 0 | - | 0.0968 | 0.108 | 0.142 | n/a | 2.54 | 0.4 | 0.0007 |
| ring1 | 150 | OUT | 3.78e+03 | 0.0619 | 3.78e+03 | 317 | 9.83 | 3931.3 | 1.0000 |
| both | 10 | OUT | 252 | 249 | 14.7 | 317 | 2.56 | 1006.9 | 0.9998 |

x = displacement amplitude at the injected frequency; ffm = fractional-frequency modulation; `OUT` in `rails` would mark a perturbed rail outside the 2.97-3.63 V envelope.

Limits of interpretation:

- Schematic-level DUT (design/ro_array_core.spice), deterministic (no noise, no mismatch), ideal series sinusoid: not an extracted supply network, not a physical aggressor.
- Only the ring supply pins (vddr1/vddr2) are perturbed; the output buffers and XOR combiner on `vdd`, the enable, ground and substrate are not.
- Reports susceptibility (timing response per volt). It is not a jitter, a min-entropy, a filter-sizing or an impedance-target result, and ripple-induced timing variation must not enter the sizing law as random jitter.
- A grid of 3 amplitudes x 2 placements x 2 frequency classes x 2 PVT corners: other corners, frequencies and phases between the two rails are untested.

## How to reproduce

```sh
python3 sim/tools/supply_ripple.py emit --check
python3 sim/tools/supply_ripple.py run binding-lowf-p2 --outdir DIR
python3 sim/tools/supply_ripple.py analyze DIR/binding-lowf-p2.report.json
```

The simulation is deterministic (no noise, no mismatch), so a re-run reproduces the edge times up to solver and PDK-version differences.

## Caveats

- Not a supply network, substrate, aggressor or noise model; no min-entropy, filter-sizing or signoff claim is made.
- The PDK model content on the fleet is the one named in `pdk:` above; compare `pdk:` lines before pooling across records.

---

Written by `sim/tools/supply_ripple.py ingest`. Append-only: never edit or delete this file -- a re-run or correction mints a new record and points back here via `supersedes` (see `sim/README.md`).
