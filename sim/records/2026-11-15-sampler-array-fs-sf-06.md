---
record: 2026-11-15-sampler-array-fs-sf-06
date: 2026-11-15T22:15:31Z
status: valid

testbench:
  path: sim/tb/sampler-array-fs-sf/tb_sampler_array_fs_sf.sp
  sha: 66904c21fde604ddd1fff55d5c064a5ec86d1d488d354dbaa11714958d3950e7
netlist:
  path: design/sampler_core.spice
  sha: 1e0dcf608ac2e45a7552f33af5958eab14b8f34a5bbceb7052eec580038c4c1f
repo_commit: 791ad51cf11efbcec254050dc779dff9d91a856f

pdk: gf180mcuD -- open_pdks f6eeac7dad085ffcc829ccfd721f7b4ce39edcf7 (fleet runner stamp sha256:4ca10280ae9f293aa1ff69f0060a52e0026929111bda881503717469b429ce67)
tool:
  ngspice: "ngspice-47" (fleet runner)
  klt: 0.9.3.dev16+gdcf18e2e0c03 (client) / 0.9.0 (runner); runner_compatibility: match
  platform: aws-batch-fleet (spot), jobs klt-sim-c748e8a1d478 (control, c7i.4xlarge, us-east-1d) and klt-sim-2071989d21b4 (grid, m7i.4xlarge, us-east-1c)

corner:
  process: fs, sf (grid) and tt (control)
  voltage: 2.97 / 3.30 / 3.63 V
  temperature: -40 / 27 / 125 C
  phases: 0 / 1.5 / 3 / 4.5 ns clock offsets (time axes encoded in ns; see below)

analysis:
  type: tran (deterministic)
  tstop: 3620n
  tstep: 10p (print step; also tmax)
  runs: 78 units (72 grid + 6 control), every corner id distinct; grid 72/72 pass, control 5/6 pass + 1 expected measurement error (the 20 ps control)
seeds: n/a (deterministic; no noise sources)

raw:
  path: sim/records/raw/2026-11-15-sampler-array-fs-sf-06/
  files:
    - analysis.txt  sha256:b367c17625f17bf073acc3ee0f724e39f5fa7d71ae04a22ecdd9e3f1712345ba
    - control-tt-batch-receipt.json  sha256:be17f4c3d22c9bff059b99e7ede457ab2b6da3d0d881966762c9306376295d79
    - control-tt.report.json  sha256:23b2937c702f3eec4d7457d6ef1b4544c0b4a0284e229e8b86a8f2e743ff44ac
    - control-tt.stderr.txt  sha256:c1c8a362f6dc84dac583dc395b82b5f2ac47b823110355655d798e0b52da9b8b
    - control-tt_vph0p000_vrel1000000000p000_vsupply3p300_vthw500p000V_27C-corner.cir  sha256:857791a893e2c3823be7cd146b4588250213662ac17ccb0a5d3aaa35795b818b
    - control-tt_vph0p000_vrel1000000000p000_vsupply3p300_vthw500p000V_27C-ngspice.log  sha256:3193296c183eafb4322cdafba5e931e6e9d2be35bdc5048cd6952faa0665edb9
    - control-tt_vph0p000_vrel500p000_vsupply3p300_vthw0p020V_27C-corner.cir  sha256:fc9dfd9f4663a303a80202d93e52f312ff4ced5d0621c8e1aa4847fb2283634f
    - control-tt_vph0p000_vrel500p000_vsupply3p300_vthw0p020V_27C-ngspice.log  sha256:879c735d3b6b2ebe4f99061d64b0fdb34e9715f334078557d9641b2bb479f813
    - control-tt_vph0p000_vrel500p000_vsupply3p300_vthw500p000V_27C-corner.cir  sha256:16fc725a6a5909e27bfb5e4c3bf4a80582a1e515ad2512c5d1b98aea3dccb0dc
    - control-tt_vph0p000_vrel500p000_vsupply3p300_vthw500p000V_27C-ngspice.log  sha256:d00263f7f4272da2fa14cc2a8b6e1f941106b9351d63d61bf864405b31a04012
    - control-tt_vph1p500_vrel500p000_vsupply3p300_vthw500p000V_27C-corner.cir  sha256:2353ffd9d9b139e7be33ee8e6c5cdbeabaaeedc0bde32f41a544a6638470fd68
    - control-tt_vph1p500_vrel500p000_vsupply3p300_vthw500p000V_27C-ngspice.log  sha256:0786211e985fd521b9b57595101c7d2468384ba94f891b9432fad6b780ebe21b
    - control-tt_vph3p000_vrel500p000_vsupply3p300_vthw500p000V_27C-corner.cir  sha256:cb3ec81650c309b822abdcb7b1dcac7241eb0bc1638eb6ac59167871e608bda0
    - control-tt_vph3p000_vrel500p000_vsupply3p300_vthw500p000V_27C-ngspice.log  sha256:90183226a62d0f9a6558a18500faae7ed2343868638b9fb6fed302cc9d0e3f52
    - control-tt_vph4p500_vrel500p000_vsupply3p300_vthw500p000V_27C-corner.cir  sha256:87e41e06d44dc4df8fe3255798ba60ba62ac5b7fb58d3c737146d2f81b4e9173
    - control-tt_vph4p500_vrel500p000_vsupply3p300_vthw500p000V_27C-ngspice.log  sha256:d4c976ac6e2f2650934da670b2b63495d1c775d26f21ac561b4d88ec27334293
    - grid-batch-receipt.json  sha256:1cf136d767af25e1853648b3eac709aa81e6bcab8f2401eae667e448efe6ebf4
    - grid.report.json  sha256:6a4b196aab5e380a015aea692c6d657832989b4fb791c691065672bbe47b48b8
    - grid.stderr.txt  sha256:809882827698bd15601c7a307d192ba38ee04130e65b5c2df149d1f10a628d2f
wall_time: control 152 s (6 units); grid 1304 s (72 units; unit runtimes 132-154 s, ~2.8 CPU-hours)
---

## Result

**The declared fs/sf campaign ran to completion on the batch fleet: all 18
asymmetric PVT points and the tt control measured, with six distinct, correctly
attributed results per control unit. Pooled verdicts: 7 OK, 9 FLAGGED
(informational XOR-pulse flags), 2 INSUFFICIENT_COVERAGE, 0 FUNCTIONAL_MISS.
No entropy, jitter, randomness, silicon or post-layout claim is made, and no
specification target changed.**

This is the campaign `-05` could not run: the deck's three time axes are
encoded in nanoseconds (1 V = 1 ns; the B-sources multiply by 1e-9), so every
unit's corner id is distinct at klt's three-decimal formatting
([#5870](https://github.com/2AMLogic/klayout-tools/issues/5870)) with stimulus
identical to the seconds encoding. The as-run deck (`sha 66904c21…`, at
`791ad51c`) differs from the current tree's deck by one comment line only (the
upstream-issue reference added after the run).

Fleet evidence of correct attribution: 72 distinct corner ids in the grid
report, 6 in the control report, and no two units share a measurement
signature; each phase unit's measured clock edges sit at its declared offset
(te_0 = 300.5 / 302 / 303.5 / 305 ns for 0 / 1.5 / 3 / 4.5 ns).

Corner-by-corner pooled verdicts (ring duty per phase unit, ranges across the
four phases; full per-unit data in `grid.report.json`, printed summary in
`analysis.txt`):

| process | T (C) | VDD (V) | verdict | ring1 duty | ring2 duty | xo swing (V) | xo min pulse (ps) | decisive / in-aperture | ones |
|---|---|---|---|---|---|---|---|---|---|
| fs | -40 | 2.97 | FLAGGED | 0.526 | 0.526 | 3.09 | 78 | 7 / 5 | 7 |
| fs | -40 | 3.30 | FLAGGED | 0.526 | 0.526 | 3.41 | 77 | 7 / 5 | 5 |
| fs | -40 | 3.63 | INSUFFICIENT_COVERAGE | 0.527 | 0.527 | 3.73 | 56 | 5 / 7 | 2 |
| fs | 27 | 2.97 | OK | 0.525 | 0.525 | 3.07 | 190 | 9 / 3 | 4 |
| fs | 27 | 3.30 | OK | 0.525 | 0.525 | 3.39 | 180 | 8 / 4 | 3 |
| fs | 27 | 3.63 | FLAGGED | 0.525 | 0.525 | 3.72 | 56 | 6 / 6 | 2 |
| fs | 125 | 2.97 | FLAGGED | 0.526 | 0.525 | 3.05 | 109 | 9 / 3 | 4 |
| fs | 125 | 3.30 | OK | 0.525 | 0.525 | 3.37 | 221 | 7 / 5 | 3 |
| fs | 125 | 3.63 | OK | 0.524 | 0.524 | 3.70 | 198 | 8 / 4 | 7 |
| sf | -40 | 2.97 | FLAGGED | 0.530 | 0.531 | 3.09 | 82 | 9 / 3 | 4 |
| sf | -40 | 3.30 | FLAGGED | 0.532 | 0.533 | 3.42 | 133 | 6 / 6 | 4 |
| sf | -40 | 3.63 | INSUFFICIENT_COVERAGE | 0.533 | 0.534 | 3.74 | 162 | 5 / 7 | 4 |
| sf | 27 | 2.97 | OK | 0.530 | 0.531 | 3.07 | 181 | 9 / 3 | 1 |
| sf | 27 | 3.30 | FLAGGED | 0.531 | 0.532 | 3.41 | 32 | 10 / 2 | 6 |
| sf | 27 | 3.63 | OK | 0.531 | 0.532 | 3.72 | 152 | 10 / 2 | 2 |
| sf | 125 | 2.97 | OK | 0.531 | 0.531 | 3.05 | 304 | 8 / 4 | 4 |
| sf | 125 | 3.30 | FLAGGED | 0.531 | 0.532 | 3.38 | 104 | 9 / 3 | 3 |
| sf | 125 | 3.63 | FLAGGED | 0.531 | 0.532 | 3.71 | 14 | 9 / 3 | 3 |
| tt | 27 | 3.30 | FLAGGED | 0.528 | 0.528 | 3.40 | 60 | 7 / 5 | 4 |

Reading of the verdicts (thresholds were fixed in `fs_sf_capture.py` before any
run):

- **No functional miss anywhere.** Every decisive sample captured the XOR level
  at its clock edge, `raw_valid` rose after release and stayed high, `raw_bit`
  settled to a rail within the tolerances and did not drift, and reset dominated
  the edge that arrives during it -- at all 18 asymmetric points and the tt
  control. The duty-cycle and swing checks passed everywhere; duty stays in
  0.524-0.534 across the whole grid (band 0.30-0.70).
- **FLAGGED** points carry only the informational XOR minimum-pulse flag (band:
  report, do not fail): sub-140 ps beat glitches on the XOR node, worst 14 ps at
  `sf` / +125 C / 3.63 V and 32 ps at `sf` / 27 C / 3.30 V. These are the
  pulse-shape events DR-0006 worried about; capture still resolved at every
  flagged point (the sampler never produced a wrong bit from one), but the
  narrowest pulses are far below the 10 ps solver resolution's comfortable
  margin, so their *widths* are interpolated, not resolved (see limits below).
- **INSUFFICIENT_COVERAGE** at `fs` / -40 C / 3.63 V and `sf` / -40 C / 3.63 V:
  5 of 12 sampling instants decisive, below the pre-declared floor of 6 -- the
  XOR node sits inside the clock-edge aperture more often at 3.63 V / -40 C.
  This is a coverage gap of the declared phase sweep, not a capture failure and
  not an unmeasured unit.
- **Negative controls (both caught as designed)**: reset never released ->
  `FUNCTIONAL_MISS` (raw_valid never high); 20 ps clock high time ->
  `FUNCTIONAL_MISS` (no clock crossing, outputs never leave reset).
- **tt control vs existing evidence**: ring duty 0.528 / 0.528 and XOR swing
  3.40 V at tt / 27 C / 3.30 V, matching the `-03` local control probe (same
  deck, same measurement definitions) -- the comparison `-01` deferred is now
  made, clock and load definitions agreeing.

The 2026-10-10 runtime estimate ("about 2 minutes per unit, about 2.6
CPU-hours") was confirmed: 132-154 s per unit, 10131 s total on the grid.

## Numerical limitations

- Solver: 10 ps tmax, ngspice default tolerances; edge times and pulse widths
  are interpolated between steps by `.meas`, so sub-step quantities (in
  particular the narrowest XOR glitches above) are not independently resolved.
- Phase coverage is 4 declared clock offsets x 3 post-release edges = 12
  sampling instants per PVT point, not a continuous sweep.
- The fleet's whole-job ceiling warning (conservative serial bound vs
  `max_job_seconds` 3600 s) fired on both submits as designed-for; neither job
  approached it (152 s / 1304 s observed).
- A deterministic bit read here is the image of a deterministic waveform: no
  noise, no mismatch, no entropy claim. The isolated sampler's setup/hold
  bracketing (`sim/tb/sampler-dff-setup-hold/`) is not repeated here.

## How to reproduce

```sh
python3 sim/tools/fs_sf_capture.py run control-tt --outdir DIR --backend batch
python3 sim/tools/fs_sf_capture.py run grid --outdir DIR --backend batch
python3 sim/tools/fs_sf_capture.py analyze DIR1/grid.report.json DIR2/control-tt.report.json
```

Request hashes (as committed at `791ad51c`): `request-grid.json` sha256
`e0ddfa0d11a5d0e124eed4d66cefb19c13f197ee3bd38935d5bf735c97b90b1d`,
`request-control-tt.json` sha256
`92a36b4af96c5651a1eeef3855322d1ca3fd5107771f117a67d4b3d2c5938667`.
Environment: `KLT_SIM_BACKEND=batch`.
