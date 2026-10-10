# Asymmetric fs/sf corners on the integrated ring-array, XOR and sampler path

Issue [#472](https://github.com/2AMLogic/gf180-trng/issues/472). Status: **the
campaign is defined, committed and unit-tested; the 18-point asymmetric grid and
the tt control were not run (the batch fleet refused or rejected every submit), so
this document reports a two-unit local pilot and no coverage-complete verdict.**
See "Run status".

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
- 78 simulation units in 2 `klt sim` requests; about 2 minutes per unit on one
  worker, about 2.6 CPU-hours, nothing run by CI or `sim/selftest.sh`.

## Run status

**The coverage-complete verdict is not available: 16 of 18 asymmetric PVT points,
the tt capture control, and 3 of 4 phases at the other two are unmeasured.**

Batch (`sim/records/2026-10-10-sampler-array-fs-sf-01.md`, raw error envelopes and
the one fleet report): five submits. Three stopped with `batch_no_capacity`; one
obtained a fleet job (`klt-sim-d40243c0c1ee`) that the runner rejected with exit 87
(`runner_compatibility: mismatch`: runner klt 0.5.0, client 0.7.0), all six units
`batch_job_failed`; the matching older client has no `batch` backend. This is the
fleet-image problem tracked upstream in
[2AMLogic/klayout-tools#2948](https://github.com/2AMLogic/klayout-tools/issues/2948),
[#2851](https://github.com/2AMLogic/klayout-tools/issues/2851) and
[#3015](https://github.com/2AMLogic/klayout-tools/issues/3015), plus the capacity
refusals also logged for #418; no new tool issue is warranted. The grid was **not**
run as a local loop. Once the runner image accepts the client, run the two requests
with `fs_sf_capture.py run`, `analyze` them, and mint records with the repository's
append-only conventions.

Local single-unit probes (debug probes, not the campaign):

- `-02`: `fs` and `sf`, -40 C, 2.97 V, phase 0: both rings start without noise and
  oscillate (periods 5.97 / 5.57 ns at both), ring duty 0.526 / 0.526 (fs) and
  0.530 / 0.531 (sf); XOR swing 3.09 V; reset and `raw_valid` as the contract
  requires; all 6 post-release samples resolved to a rail and all 3 decisive ones
  captured the XOR level; 3 were in the edge aperture. Informational flag: the XOR
  carries ~80 ps beat glitches. This is **2 of 18 PVT points at 1 of 4 phases**;
  coverage is below the 6-decisive floor, so these are not coverage-complete.
- `-03`: the two negative controls at tt/27 C/3.30 V, both caught as
  `FUNCTIONAL_MISS`; the unchanged rings give tt/27 C/3.30 V duty 0.528 / 0.528 and
  XOR swing 3.40 V. That is a ring/XOR waveform measurement only; the tt capture
  control is unmeasured.

No functional miss against the unchanged specification was observed in the
measured units; because only 2 of 18 points at one phase were measured, the absence
of a miss elsewhere is **not** established.

## Comparison with existing evidence

The tt ring figures (period 6.67 / 6.23 ns, duty 0.528 at 27 C, 3.30 V) were not
compared with the earlier `ro-array-core-power` / `sampler-array-digitize` records,
whose decks differ (the older digitize deck restates an un-buffered wiring and
runs a 10 ns clock under injected noise); a comparison needs matching clock, load
and measurement definitions and is left for when the tt control has run.

## Tested versus not tested

Tested offline (`sim/tests/test_fs_sf_capture.py`): the committed requests match the
declared grid (18 PVT points x phases, tt control, negative controls); duty and
pulse extraction on known edge trains; the checker on hand-built readouts (clean
capture; wrong captured bit; output parked mid-rail; slow drift; reset that does
not dominate a clock edge; reset never released; missing clock edge; low swing;
in-aperture sample; missing measurements -> `UNMEASURED`); and the pooling rule
that a missing unit prevents a coverage-complete verdict.

Not tested, and unbounded by this work even once the campaign runs:

- noise, jitter and mismatch (nothing here is randomness; no min-entropy figure);
- continuous clock-phase coverage (4 offsets, 3 edges), clock jitter, duty error or
  finite source impedance; the clock is ideal with 1 ns edges;
- the isolated sampler's setup/hold bracketing (already in
  `sim/tb/sampler-dff-setup-hold/`; not repeated);
- extracted parasitics, body-tie and well-tie effects (#339 / #411) and silicon;
- solver sensitivity beyond the stated 10 ps `tmax` with default tolerances (no
  finer-step re-run was made).
