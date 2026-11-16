# Asymmetric fs/sf corners on the integrated ring-array, XOR and sampler path

Issue [#472](https://github.com/2AMLogic/gf180-trng/issues/472). Status: **the
campaign ran to completion on the batch fleet on 2026-11-15 (records
`2026-11-15-sampler-array-fs-sf-05` and `-06`): all 18 asymmetric PVT points and
the tt control measured; pooled verdicts 7 OK, 9 FLAGGED (informational
XOR-pulse flags), 2 INSUFFICIENT_COVERAGE, 0 FUNCTIONAL_MISS.** See "Run status".

This is a functional characterization of one named path, not a verdict on the
design. It changes no spec target, no decision record and no signoff verdict. It
makes **no entropy, jitter, randomness, silicon or post-layout claim**.

## The gap it addresses

[`DR-0006`](../spec/decision-records/DR-0006-ro-jitter-characterization-pvt-sampling-strategy.md)
dropped the asymmetric `fs`/`sf` MOS corners from the jitter campaign because no
downstream circuit was sensitive to N/P drive-strength asymmetry, and required a
follow-up if one appeared. The edge-triggered sampler is such a circuit: a
duty-cycle or pulse-shape error on the XOR node reaches its D input. Today:

| Existing evidence | Covers | Does not cover |
|---|---|---|
| `sim/tb/sampler-dff-setup-hold/` | the **isolated** `sampler_dff` at five MOS corners (incl. `fs`, `sf`), 1 Mbps clock, ideal 1 ps data edges: clk-to-Q, setup bracketing, zero-margin settling | the rings, the XOR, ring duty cycle, XOR pulse shape; it states that it excludes the entropy source |
| `sim/tb/sampler-array-digitize/` | source + sampler together, one noisy 100 MHz-clock demonstration, ten bits | `fs`/`sf` (no such record exists), the 1 Mbps clock, ring duty and XOR pulse widths; it states it is not a rate or entropy measurement |

This campaign puts the corner-skewed ring + XOR waveform on the sampler's input
at the 1 Mbps target clock and checks capture. It **adds to** the isolated-sampler
coverage and the stochastic records; it replaces neither, and their claim limits
stand.

## What the campaign tests

The shipped `sampler_core` (`design/sampler_core.spice`) instantiated whole,
deterministic (no noise, no mismatch), 1 us clock period, 1 ns edges. Declared
before any run (`sim/tb/sampler-array-fs-sf/README.md`,
`python3 sim/tools/fs_sf_capture.py plan`):

- corners: `fs` and `sf` x {-40, 27, 125} C x {2.97, 3.30, 3.63} V = 18 PVT
  points, plus a `tt`/27 C/3.30 V control through the same deck;
- phase sweep: four clock offsets (0, 1.5, 3.0, 4.5 ns) x three post-release edges
  = 12 sampling instants per PVT point; the edges also land at different ring
  phases because 1 us is not a multiple of either ring period;
- measured: ring high/low durations and duty cycle (`ro1`, `ro2`), XOR swing and
  high/low pulse widths, reset behaviour (including a clock edge that arrives
  during reset), `raw_valid` behaviour, and `raw_bit` at +8, +50 and +300 ns after
  each edge against the XOR level at the edge;
- thresholds: fixed in `fs_sf_capture.py` before any run (swing >= 0.90 x supply;
  rail tolerance 0.10 / 0.05 x supply; `raw_valid` above 0.90 x supply after
  release; a *decisive* sample must capture the XOR level; at least 6 decisive
  post-release samples per PVT point for coverage). A sample whose XOR node is
  crossing mid-supply inside the clock-edge aperture has no defined expected bit
  and is checked for resolution to a rail only;
- negative controls (tt/27 C/3.30 V): reset never released, and a 20 ps clock
  high time; the checker must return `FUNCTIONAL_MISS` for each;
- 78 simulation units in 2 `klt sim` requests; measured on the 2026-11-15 run:
  132-154 s per unit, about 2.8 CPU-hours for the grid, nothing run by CI or
  `sim/selftest.sh`.

Axis encoding: the deck's three time axes (`vph`, `vrel`, `vthw`) are DC sources
consumed only by its B-sources and are **encoded in nanoseconds** (1 V = 1 ns).
The seconds encoding is not usable on the fleet: klt derives each unit's
directory/id from axis values formatted to three decimals, so sub-milli values
collide and distinct units share one result set
([2AMLogic/klayout-tools#5870](https://github.com/2AMLogic/klayout-tools/issues/5870),
observed on the first 2026-11-15 submit, record `-05`). In ns every one of the
78 unit ids is distinct with stimulus identical to the seconds encoding.

## Run status

**Campaign complete (2026-11-15, records `-05` and `-06`): all 18 asymmetric PVT
points and the tt control measured on the batch fleet. Pooled verdicts: 7 OK,
9 FLAGGED, 2 INSUFFICIENT_COVERAGE, 0 FUNCTIONAL_MISS. Every decisive sample
captured the XOR level at its clock edge; reset and `raw_valid` behaved as the
contract requires everywhere; ring duty stayed within 0.524-0.534 across the
whole grid.**

First submit of the day (`-05`): the capacity-wait fix worked -- the fleet
accepted both requests, and the runner/client compatibility of `-01` (exit 87)
is confirmed gone (`runner_compatibility: match`, runner klt 0.9.0, client
0.9.3.dev16). But the control request's five sub-milli-valued units returned
byte-identical results (one simulation mis-attributed five ways) via the
upstream corner-id collision named above, and the 72-unit grid was deliberately
**not** submitted into that condition. Remedy: the ns axis encoding described
above; `-05` carries no measurement.

Second submit (`-06`): both requests ran cleanly -- 6 control units in 152 s,
72 grid units in 1304 s (unit runtimes 132-154 s, on spot c7i/m7i.4xlarge
workers, ngspice-47, runner klt 0.9.0), 72 and 6 distinct corner ids, no two
units sharing a measurement signature, and each phase unit's measured clock
edges at its declared offset. Corner-by-corner pooled verdicts (ranges across
the four phases of each point; full per-unit data in the record's
`grid.report.json`):

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

- The **FLAGGED** points carry only the pre-declared informational XOR
  minimum-pulse flag: sub-140 ps beat glitches on the XOR node, worst 14 ps at
  `sf` / +125 C / 3.63 V. This is exactly the pulse-shape mechanism DR-0006
  deferred the asymmetric corners over: the glitches are present at several
  corners, reach the sampler's D input, and still never produced a wrong or
  unsettled capture -- but the narrowest of them are far below a comfortable
  margin over the 10 ps solver resolution, so their widths are interpolated, not
  independently resolved.
- **INSUFFICIENT_COVERAGE** at `fs` and `sf` / -40 C / 3.63 V (5 of 12 sampling
  instants decisive, below the pre-declared floor of 6): the XOR node sits
  inside the clock-edge aperture more often at 3.63 V / -40 C. A coverage gap of
  the declared phase sweep, not a capture failure and not an unmeasured unit.
- **Negative controls: both caught** as `FUNCTIONAL_MISS` on the fleet (reset
  never released: `raw_valid` never high; 20 ps clock high time: no clock
  crossing), consistent with the `-03` local probes.
- No functional miss against the unchanged specification was observed at any of
  the 19 measured points.

Earlier attempts (`sim/records/2026-10-10-sampler-array-fs-sf-01.md` ..
`-04`): the campaign machinery was built (`-02`, `-03` local debug probes), but
every 2026-10-10 batch submit was refused (`batch_no_capacity`) or rejected by a
runner/client mismatch (exit 87, tracked upstream and closed 2026-11-14). Those
records stand unchanged; `-01`'s warning that the grid must not be run as a
local loop was honored throughout.

## Comparison with existing evidence

The tt control has now run (record `-06`), through the same deck and the same
measurement definitions as the `-03` local control probe: ring period/duty
(duty 0.528 / 0.528) and XOR swing (3.40 V) agree between the fleet run and the
2026-10-10 local probe at tt / 27 C / 3.30 V. That is the only cross-check with
matching clock, load and measurement definitions; the earlier
`ro-array-core-power` / `sampler-array-digitize` records still differ in deck,
clock and noise injection, and remain uncompared, as `-01` stated.

## Reproduce (cold start)

Declared before any run (`plan`, `emit --check`), then run on the batch fleet
(`KLT_SIM_BACKEND=batch`, one request at a time; never a local loop):

```sh
python3 sim/tools/fs_sf_capture.py plan
python3 sim/tools/fs_sf_capture.py emit --check
python3 sim/tools/fs_sf_capture.py run control-tt --outdir DIR --backend batch
python3 sim/tools/fs_sf_capture.py run grid --outdir DIR --backend batch
python3 sim/tools/fs_sf_capture.py analyze DIR1/grid.report.json DIR2/control-tt.report.json
```

Input hashes on this tree: testbench deck
`sim/tb/sampler-array-fs-sf/tb_sampler_array_fs_sf.sp` sha256
`63c8dea09184a99db93840a7af4e0896c325dbbd37a8fbc8fd03fb8d4fb881f9`;
`sim/tb/sampler-array-fs-sf/request-grid.json` sha256
`e0ddfa0d11a5d0e124eed4d66cefb19c13f197ee3bd38935d5bf735c97b90b1d`;
`sim/tb/sampler-array-fs-sf/request-control-tt.json` sha256
`92a36b4af96c5651a1eeef3855322d1ca3fd5107771f117a67d4b3d2c5938667`.
The `-06` runs used the deck as committed at `791ad51c` (sha256
`66904c21fde604ddd1fff55d5c064a5ec86d1d488d354dbaa11714958d3950e7`; one added
comment line since, no stimulus change) and byte-identical requests. The table
above re-derives from the committed fleet reports with `analyze` — its output is
record `-06`'s `analysis.txt` (`sim/records/2026-11-15-sampler-array-fs-sf-06.md`).

## Tested versus not tested

Tested offline (`sim/tests/test_fs_sf_capture.py`): the committed requests match the
declared grid (18 PVT points x phases, tt control, negative controls); duty and
pulse extraction on known edge trains; the checker on hand-built readouts (clean
capture; wrong captured bit; output parked mid-rail; slow drift; reset that does
not dominate a clock edge; reset never released; missing clock edge; low swing;
in-aperture sample; missing measurements -> `UNMEASURED`); and the pooling rule
that a missing unit prevents a coverage-complete verdict.

Not tested, and unbounded by the completed campaign:

- noise, jitter and mismatch (nothing here is randomness; no min-entropy figure);
- continuous clock-phase coverage (4 offsets, 3 edges), clock jitter, duty error or
  finite source impedance; the clock is ideal with 1 ns edges;
- the isolated sampler's setup/hold bracketing (already in
  `sim/tb/sampler-dff-setup-hold/`; not repeated);
- extracted parasitics, body-tie and well-tie effects (#339 / #411) and silicon;
- solver sensitivity beyond the stated 10 ps `tmax` with default tolerances (no
  finer-step re-run was made).
