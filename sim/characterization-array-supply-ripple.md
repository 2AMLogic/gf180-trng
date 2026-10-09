# Deterministic supply-ripple susceptibility of the buffered RO array

Issue [#414](https://github.com/2AMLogic/gf180-trng/issues/414). Status: **the
campaign is defined, committed and unit-tested; the simulations have not been
run, so this document reports no sensitivity numbers.** See "Run status".

This is characterization of one named coupling path, not a verdict. It changes
no spec target, no decision record and no signoff verdict, and it makes no
claim about min-entropy, supply-filter sizing or a supply-network impedance
target.

## The gap it addresses

[`characterization-array-ring-coupling.md`](characterization-array-ring-coupling.md)
(Caveats, "Ideal supply") states that every coupling deck connects both ring
supplies through zero-volt ammeters to one *ideal* source, which has no
impedance for one ring's current to develop a voltage across; supply-network
coupling is a second path those decks cannot see. The array deck
`sim/tb/ro-array-core-pvt-q/` has the same structure, and
`layout/floorplan/README.md` records that supply filtering is unsized because no
supply-network impedance target exists. So the isolation argument has no
quantified answer to a *deterministic* supply disturbance at the ring pins.

## What the campaign tests

An ideal series sinusoid on a ring supply pin of the shipped buffered array
(`design/ro_array_core.spice`, blob `fd0aa75500320b36f980126377e3d07c71c0e6b1`),
read out as the edge-time displacement of each ring and of the rings' relative
phase at the injected frequency. Declared before any run (`sim/tb/ro-array-supply-ripple/README.md`,
`python3 sim/tools/supply_ripple.py plan`):

- corners: `tt`/27 C/3.30 V and the entropy-binding `ss`/125 C/3.63 V;
- placement: ring 1 only, and both rings in phase;
- amplitude: 0 (control), 10, 50, 150 mV peak;
- frequency: 2 MHz, and the corner's observed ring-frequency difference
  (10.50 MHz nominal, 7.65 MHz binding);
- numerical checks: the binding-corner beat point re-run at 5 ps and 2.5 ps
  against the 10 ps main grid, and a one-cycle-shorter fit window on every unit;
- 32 simulation units in 6 `klt sim` requests, about 1.1 CPU-hours (a planning
  estimate from one local probe), nothing run by CI or `sim/selftest.sh`.

Because the binding corner already sits at the top of the 2.97-3.63 V envelope,
any positive excursion there leaves it; each perturbed rail is labelled `in` or
`OUT` of the envelope from its measured minimum and maximum rather than assumed.

## Run status

The two `klt sim --backend batch` submits made from this issue's worktree did
not run:

1. the first stopped with `batch_no_capacity` (no Spot capacity in any pool);
2. a retry obtained a fleet job, which the runner rejected with
   `batch_runner_version_mismatch`: the fleet runner image carries klt 0.5.0
   and the submitting client is 0.7.0. The older client that matches the runner
   (`uvx --from klayout-tools==0.5.0`) has no `batch` backend, so no compatible
   client/runner pair exists today.

This is the fleet-image problem already tracked in
[2AMLogic/klayout-tools#2948](https://github.com/2AMLogic/klayout-tools/issues/2948)
and [#2851](https://github.com/2AMLogic/klayout-tools/issues/2851); no new
tool issue is warranted. The grid was **not** run as a local loop. Once the
runner image accepts the client, run the six requests with
`supply_ripple.py run` and mint records with the repository's append-only
conventions.

The only simulation performed was an unrecorded two-unit local pipeline smoke
check (a control and one 150 mV unit at `tt`/27 C/3.30 V, 10.5 MHz, one corner)
to confirm that the deck's `alter` parameters take effect, that the `.meas` edge
rows come back, and that `supply_ripple.py analyze` reads a real `klt` report.
It is not evidence and is not recorded; no value from it appears here.

## Tested versus not tested

Tested offline (`sim/tests/test_supply_ripple.py`): tone extraction recovers a
known amplitude and phase under drift; a zero-amplitude control yields a
negligible tone; a deterministic tone is distinguished from a seeded stochastic
residual (the tone is detected and the residual rms equals the noise sigma, while
pure noise is not detected); ring edge-time displacement and relative-phase
extraction recover known displacements, including common-mode cancellation; the
committed requests match the declared grid; the cited PVT records' ring
frequencies still match the grid's provenance.

Not tested, and unbounded by this work even once the campaign runs:

- the actual supply network: source impedance, shared-trunk IR drop, return
  paths, decoupling, and any aggressor that would produce the ripple;
- ripple on the buffer/combiner rail (`vdd`) or on ground/substrate, and ripple
  with unequal phase or amplitude between the two rings;
- extracted parasitics (this is the schematic DUT; the extracted-PMOS
  body-bias and well-tie questions, #339/#411, are separate);
- stochastic behaviour: no noise or mismatch is simulated, so the experiment
  separates nothing from jitter and adds no seeds;
- other PVT corners, other frequencies and amplitudes, and large-signal
  (harmonic) ripple.

## How to read a result when it exists

A sensitivity is a number of picoseconds of edge-time displacement (or ppm of
fractional frequency) per millivolt of injected ripple, for a synthetic ideal
aggressor. It is deterministic, so it must not be added to the sizing law as
random jitter, and it says nothing about a built chip's supply noise until a
supply-network model exists to supply the ripple.
