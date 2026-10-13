# sampler-array-fs-sf — asymmetric MOS corners on the integrated capture path

Issue [#472](https://github.com/2AMLogic/gf180-trng/issues/472). An **opt-in**
campaign: it is not run by `sim/selftest.sh`, by CI, or by any other test. Only
the offline unit tests (`sim/tests/test_fs_sf_capture.py`) and
`fs_sf_capture.py emit --check` run in ordinary CI, and neither touches ngspice.

**What it is.** The shipped `sampler_core` (`design/sampler_core.spice`, whole:
two buffered 11-stage rings, the XOR, and the four `sampler_dff` cells) driven by
the fixed 1 Mbps external clock, deterministic (no noise, no mismatch), at the
`fs` and `sf` MOS corners over {-40, 27, 125} C x {2.97, 3.30, 3.63} V (18 PVT
points), plus a `tt`/27 C/3.30 V control through the same deck.

**What it adds.** DR-0006 dropped `fs`/`sf` from the jitter campaign until
duty-cycle-sensitive circuitry existed. `sim/tb/sampler-dff-setup-hold/` already
covers the isolated sampler at five MOS corners, but with ideal data edges: it
exercises neither the ring duty cycle, nor the XOR pulse shape, nor the two
together with the sampler. This deck puts the corner-skewed ring + XOR waveform on
the sampler's D input and checks reset, `raw_valid` and capture at several clock
phases. The isolated-sampler evidence is **not repeated or replaced**.

**What it is not.** No entropy, jitter, randomness, silicon or post-layout claim.
A bit pattern read here is the deterministic image of a deterministic waveform.
Post-layout and body-tie questions are #339 / #411 and are out of scope. No spec
target or decision record changes; a functional miss, if one is found, is
reported against the unchanged specification.

| File | Role |
|---|---|
| `tb_sampler_array_fs_sf.sp` | the circuit body: ideal supply, DC-source parameters `vsupply`/`vph`/`vrel`/`vthw`, a B-source clock with a per-unit phase, the reset ramp, the whole DUT, two `.ic` start-up kicks |
| `request-grid.json` | the 72-unit `klt sim` request: {fs, sf} x {-40, 27, 125} C x 3 supplies x 4 clock phases (generated; do not edit) |
| `request-control-tt.json` | the 6-unit request: tt/27 C/3.30 V x 4 phases, plus two negative controls (generated; do not edit) |

Everything else — the declared grid, thresholds, request generator, checker and
summary table — is `sim/tools/fs_sf_capture.py`.

## Declared grid and thresholds (fixed before any run)

| Item | Value |
|---|---|
| Corners | `fs`, `sf` (MOS skewed, passives typical, as `sim/harness/corners.py`); `tt` control |
| Temperature / supply | -40, 27, 125 C / 2.97, 3.30, 3.63 V (the ratified envelope) |
| Clock | 1 us period (1 Mbps, DR-0003), 1 ns edges, 50 % duty; DR-0012 fixed external clock |
| Phase sweep | clock offset 0, 1.5, 3.0, 4.5 ns (`vph`); in addition, each of the 3 post-release edges lands at a different ring phase because 1 us is not a multiple of either ring period. 12 sampling instants per PVT point |
| Timeline | edge 0 at 0.3 us under reset; reset releases at 0.5 us; edges 1-3 at 1.3, 2.3, 3.3 us; readouts at +8, +50, +300 ns after each nominal edge; `tstop` 3.62 us |
| Solver | `tmax` = print step = 10 ps, ngspice default tolerances, `measureprec=12` |
| Ring duty / XOR pulses | high and low durations of `ro1`, `ro2`, `xo` from mid-supply crossings 8-23 (rings) and 8-31 (xo), all before the first clock edge |

Thresholds are the named constants at the top of `fs_sf_capture.py`; `plan` prints
them. In words: ring and XOR swing >= 0.90 x supply; `raw_valid` and `raw_bit`
below 0.10 x supply through the edge that arrives during reset; `raw_valid` above
0.90 x supply after each post-release edge; `raw_bit` within 0.10 x supply of a
rail at +8 ns and 0.05 x supply at +50/+300 ns, moving no more than 0.05 x supply
between them; for a *decisive* sample (the XOR node on one side of mid-supply at
the 25 %, 50 % and 80 % levels of the clock edge and at least 0.20 x supply from
mid-supply at 50 %) the settled bit must equal that side. A sample whose XOR node
is crossing mid-supply inside the edge aperture is *in aperture*: counted, and
checked for resolution to a rail only. A PVT point is not coverage-complete with
fewer than 6 decisive post-release samples. Ring duty outside 0.30-0.70 and an XOR
pulse under 140 ps are informational flags and do not by themselves fail capture.

## Negative controls

Two intentionally invalid stimuli at tt/27 C/3.30 V, in the control request, that
the checker must catch (outcome `FUNCTIONAL_MISS`):

- `reset-never-released` — `vrel` = 1 s: `raw_valid` never rises, so the post-release
  checks fail;
- `clock-high-20ps` — `vthw` = 20 ps: the clock never swings far enough to operate
  the sampler's transmission gates; no mid-supply clock crossing exists and
  `raw_valid` never rises.

The checker's logic is also exercised on hand-built readouts in
`sim/tests/test_fs_sf_capture.py` (wrong captured bit, output parked mid-rail,
slow drift, reset that does not dominate, missing clock edge, low swing).

## Running it

```bash
python3 sim/tools/fs_sf_capture.py plan                     # grid, thresholds, units
python3 sim/tools/fs_sf_capture.py emit --check             # requests match the grid
# OPT-IN, one request at a time; the dispatch hosts send these to the batch fleet
python3 sim/tools/fs_sf_capture.py run grid --outdir DIR
python3 sim/tools/fs_sf_capture.py run control-tt --outdir DIR
python3 sim/tools/fs_sf_capture.py analyze DIR/grid.report.json DIR/control-tt.report.json
```

Runtime: one unit (3.62 us at 10 ps, ~360k steps) took about 2 minutes wall on a
dispatch worker in the local probes of `sim/records/2026-10-10-sampler-array-fs-sf-02.md`,
so the 78 units are about 2.6 CPU-hours; the fleet runs a request's units in
parallel. If a batch submit fails, report the error and record the point as
unmeasured; do not run the grid as a local loop. `klt sim` needs an **absolute**
`-o` directory on the local backend (a relative one makes every measurement read
"no value"; tracked upstream, e.g. klayout-tools#2966).
