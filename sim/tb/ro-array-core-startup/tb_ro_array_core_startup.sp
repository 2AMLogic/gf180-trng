* ro-array-core-startup -- how long the shipped entropy-source array takes to
* reach its steady oscillation period and its steady swing after `en` actually
* asserts, i.e. the "oscillator start from power-down and idle states" half of
* issue #14's time-to-first-valid deliverable.
*
* DUT: design/ro_array_core.spice, exported from design/xschem/ro_array_core.sch
* by design/netlist.py -- unmodified, the same DUT sim/tb/ro-array-core-power/
* and sim/tb/ro-array-core-pvt-q/ use.
*
* Why this deck exists, and what it changes relative to the two decks above.
* sim/tb/ro-array-core-power/'s own header states plainly: "Start-up time
* itself is worth measuring; it is not what THIS testbench measures." Both
* running-state decks hold `en` HIGH from t = 0 and kick each ring off its
* unstable symmetric DC equilibrium with a `.ic` on the NAND output, because a
* noiseless solver started at `en = 1` can otherwise converge to that
* equilibrium and never oscillate. That kick buys them measurement window at
* the cost of the one quantity this deck is about.
*
* THIS DECK USES NO `.ic`, DELIBERATELY, AND DOES NOT NEED ONE. With `en` low
* the ring is not at an unstable equilibrium at all: `ro_nand2`'s output is
* forced HIGH independently of its ring input, the loop gain around the ring is
* zero, and the eleven stages have exactly one stable DC solution
* (n1 = 1, n2 = 0, ... n10 = 0, ro = 1). ngspice's operating-point solve at
* t = 0 finds that state, which is precisely design/README.md's "off, clamped"
* idle state, and the rising `en` edge -- not an initial condition invented by
* the testbench -- is what starts the oscillation. Adding the running decks'
* `.ic` here would be actively wrong: it forces `n1 = 0` against an `en = 0`
* state that wants `n1 = 1`, so the ring would still be relaxing out of an
* inconsistent condition at the moment `en` asserts, and the measured start-up
* would be contaminated by the testbench's own artefact.
*
* `en` asserts at t = 5 ns rather than t = 0 so there is a clean, visibly
* settled interval of "actually off" ahead of the edge; every reported time is
* referenced to that edge (`en_assert_s`) and not to t = 0.
*
* What is measured, per PVT point:
*   - the first ten successive rising-edge crossings of a mid-supply reference
*     on EACH ring's own output node, probed hierarchically (no per-ring signal
*     is brought out of the core -- DR-0001/DR-0007: observability in the
*     testbench must not become an exposed tap in the design). Nine successive
*     period estimates per ring; sim/tools/time_to_first_valid.py finds the
*     first that agrees with the last to a stated tolerance and reports the
*     elapsed time from `en` to that edge as this run's oscillator start-up
*     time. The tolerance therefore lives in a tool a reader can re-run with a
*     different value, not baked irreversibly into the record.
*   - the first four rising crossings of the XOR-combined node `xo`, which is
*     what the sampler actually sees. A ring can be running before `xo` is a
*     usable digitiser input, and the two are not the same instant.
*   - ring and `xo` swing over an EARLY window and a LATE window. A converged
*     period does not by itself prove a converged amplitude, and a starved ring
*     that reaches its final frequency while still climbing to the rails would
*     hand the sampler an analog level. Measuring both closes that gap here
*     instead of leaving it as a caveat.
*
* Corner coverage is the SAME 27-point grid sim/tb/ro-array-core-pvt-q/ uses
* ({tt,ff,ss} x {-40,27,125} C x {2.97,3.30,3.63} V), so a start-up time and
* the steady period it converges to can be compared at the identical PVT point
* without interpolating between two different grids. `fs`/`sf` remain
* uncovered, per DR-0006.
*
* bvth is a measurement-only probe: a mid-supply reference so
* `meas ... when v(node)=v(vth)` finds crossings at any supply without a
* hard-coded trip voltage. It is the same construction
* sim/tb/ro-array-core-power/ uses.

vsup vsup 0 dc vdd_val
ven en 0 dc 0 pulse(0 vdd_val 5n 1p 1p 10u 20u)

xdut en en vsup vsup vsup 0 xo ro_array_core

bvth vth 0 v = 0.5*vdd_val
