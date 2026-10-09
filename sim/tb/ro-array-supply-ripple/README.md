# ro-array-supply-ripple — deterministic supply-ripple susceptibility

Issue [#414](https://github.com/2AMLogic/gf180-trng/issues/414). An **opt-in**
experiment: it is not run by `sim/selftest.sh`, by CI, or by any other test.
Only the offline unit tests (`sim/tests/test_supply_ripple.py`) and
`supply_ripple.py emit --check` run in ordinary CI, and neither touches
ngspice.

**What it is.** The shipped buffered two-ring array
(`design/ro_array_core.spice`) with a declared sinusoid in series with one ring
supply pin (`vddr1`), or both ring pins at once (same phase), against an
otherwise ideal supply. The response is the ring edge-time displacement at the
injected frequency, per volt of injected ripple. It is **schematic-level,
deterministic and synthetic**.

**What it is not.** It is not an extracted supply network, a substrate model, a
physical aggressor, or a noise measurement. It reports no jitter and no
min-entropy, sizes no filter or decoupling, states no impedance target, and does
not feed the DR-0007 sizing law (ripple-induced timing variation is deterministic
and must not be added there as random jitter). No spec target or signoff verdict
changes.

| File | Role |
|---|---|
| `tb_ro_array_supply_ripple.sp` | the circuit body: ideal supply, DC-source parameters `vamp`/`vfrq`/`vm1`/`vm2`, series B-source ripple on `vddr1`/`vddr2`, the DUT, one `.ic` kick |
| `request-<corner>-<freq>.json` | the `klt sim` requests (generated; do not edit) |
| `request-conv-*.json` | solver-step convergence re-runs (5 ps, 2.5 ps) of the control and one perturbed unit |

Everything else — the declared grid, the request generator, the edge-time tone
extraction and the sensitivity table — is `sim/tools/supply_ripple.py`.

## Declared grid (fixed before any run)

| Axis | Values |
|---|---|
| PVT corner | `tt`/27 C/3.30 V (nominal); `ss`/125 C/3.63 V (the entropy-binding corner, `sim/characterization-worst-corner-and-mc-mismatch.md` section 2) |
| Ripple placement | ring 1 only; both rings, same phase |
| Peak amplitude | 0 (control), 10 mV, 50 mV, 150 mV |
| Ripple frequency | 2 MHz (low-frequency point, well below the ring frequencies); the corner's observed ring-frequency difference, rounded: 10.50 MHz nominal, 7.65 MHz binding |
| Solver | `tmax` = print step = 10 ps (convergence re-runs at 5 ps and 2.5 ps on the binding-corner beat point); `measureprec=12` |
| Window | edges before 100 ns are not fitted; fits use a whole number of ripple cycles; `tstop` 2.7 us (2 MHz) or 0.7 us (beat) |

Each request holds one corner and one ripple frequency; its `corners.supply_v`
carries the supply and the four ripple parameters moving together by index, so
the 7 units of a request are control + 2 placements x 3 amplitudes. The
zero-amplitude unit of every request is the control: same netlist, corner,
window and solver settings. The DUT blob hash and the klt/ngspice/PDK versions
are printed by `supply_ripple.py analyze`.

The binding corner sits at the top of the 2.97-3.63 V envelope, so any positive
excursion leaves it. That is by construction of the request, not hidden: the
analysis labels each perturbed rail `in` or `OUT` of the envelope from the
measured rail minimum and maximum, and the table repeats the label.

## Running it

```bash
python3 sim/tools/supply_ripple.py plan                     # grid, units, runtime estimate
python3 sim/tools/supply_ripple.py emit --check             # requests match the grid
# OPT-IN, one request at a time; the dispatch hosts send these to the batch fleet
python3 sim/tools/supply_ripple.py run binding-beat --outdir DIR
python3 sim/tools/supply_ripple.py analyze DIR/*.report.json
```

Runtime estimate: about 1.1 CPU-hours across the 32 units, from a single local
probe (30k solver steps in ~21 s). The fleet runs a request's units in parallel,
so elapsed time is set by the longest unit (the 2 MHz requests, ~270k steps each)
plus capacity acquisition. If a batch submit fails, report the error; do not run
the grid as a local loop.

## How the tone is read

Edge times of `ro1`/`ro2` (the buffered ring outputs) are `.meas` rows. For
each ring, edge time is fitted to a quadratic in edge index (absorbing the ring
period, slow drift and any start-up remnant) plus `a cos(wt) + b sin(wt)` at the
injected frequency; the tone amplitude is the edge-time displacement in seconds,
and `2 pi f` times it is the fractional-frequency modulation. The relative phase
of the two rings is read the same way (`beat-phase x`), which is what an
XOR-then-sample structure sees. White-residual standard errors
(`sigma = rms*sqrt(2/n)`) are reported, but a deterministic start-up remnant is
not white, so the zero-amplitude control's own tone amplitude is the floor the
perturbed units are compared against.

Offline tests (`sim/tests/test_supply_ripple.py`) exercise the extraction with
synthetic signals: amplitude/phase recovery under drift, a zero-amplitude
control, and a deterministic tone told apart from a seeded stochastic residual.

## Limits

See `LIMITS` in `sim/tools/supply_ripple.py`; they are printed with every table.
The results and what they leave unbounded are summarised in
`sim/characterization-array-supply-ripple.md`.
