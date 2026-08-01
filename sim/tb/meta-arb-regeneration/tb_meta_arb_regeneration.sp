* meta-arb-regeneration -- the metastable element's regeneration time constant.
*
* DUT: design/meta_arb.spice, exported from design/xschem/meta_arb.sch by
* design/netlist.py. Nothing about the DUT is redefined here; this fragment
* supplies rails, the two release edges, and measurement-only elements.
*
* WHAT THIS MEASURES, and why it is the measurement that exists
*
* The architecture survey (section B.2) makes one substantiability claim
* and one refusal about metastability in ngspice:
*
*   - refused: a resolution-time HISTOGRAM from many noise-seeded trials.
*     Not credibly reproducible at run lengths this project can afford.
*   - allowed: the element's REGENERATION TIME CONSTANT tau, "directly
*     ngspice-substantiable ... even though full resolution-time histograms
*     are not" (Recommendation 2), by the Kinniment/Chester method.
*
* This testbench takes the allowed one. Near the balance point a
* cross-coupled latch's differential grows as exp(t/tau), so a release-edge
* skew dt resolves after
*
*     t_res(dt) = t_0 + tau * ln(dt_ref / dt)
*
* i.e. t_res is LINEAR in ln(1/dt) with slope tau. Seven arbiter instances
* are released with dt spanning five decades (100 ps down to 1 fs, plus an
* exactly-balanced one); tau is then read off as the slope between adjacent
* decades. That is a deterministic transient -- no noise sources, no seeds
* -- so it is reproducible to the digit, which is precisely the property
* the histogram approach cannot offer.
*
* WHY DECADE PAIRS AND NOT A SINGLE FIT
*
* Reporting tau once per adjacent decade pair, rather than one regression
* over all of them, is the self-check. The physics says every pair must
* give the same tau. Where they stop agreeing is the numerical floor of
* the method on this solver, and that floor is a RESULT, not an
* embarrassment to hide inside a fit residual: it is the quantitative
* version of the survey's objection. A 1 fs skew is a ~165 uV differential
* at the arbiter inputs during a 20 ps ramp, and the point at which the
* decade-to-decade tau estimates diverge is the point at which the solver
* stops resolving that honestly.
*
* WHAT IT DOES NOT MEASURE
*
* Entropy. tau bounds how long resolution takes for a GIVEN dt; it says
* nothing about the distribution of dt in silicon, which is set by
* mismatch and noise. See DR-0011.
*
* METHOD NOTES
*
*   - The instances share one sn source so the reference edge is bit-identical
*     for every dt; only rn moves. Ideal voltage sources, so the instances do
*     not load each other.
*   - PULSE(V1=vdd V2=0 TD=1n TR=TF=20p PW) starts HIGH, asserts low at 1 ns
*     (both inputs low -> q = qn = 1, the latch driven off both stable states)
*     and releases at TD+TR+PW. sn releases at 5.000 ns for every instance;
*     rn releases at 5.000 ns + dt. The 20 ps ramp is a realistic edge for a
*     minimum-width gate in this process, not an idealised step: an idealised
*     step would put the entire skew into a single solver timepoint.
*   - dt > 0 means sn rises FIRST, so q is the output that falls. Every
*     instance therefore resolves the same way and one .meas form covers all.
*   - .ic pins q low at t = 0. With both inputs high the latch has two stable
*     DC solutions and one metastable one; without the .ic the operating
*     point could land anywhere, including on the metastable solution, and
*     the edge counting in the .meas statements would stop meaning anything.
*   - bvth is a measurement-only probe: a mid-supply reference so
*     `meas ... when v(q)=v(vth)` finds crossings at any supply without a
*     hard-coded trip voltage.
*   - Instance 0 has dt = 0 exactly. It is not measured with a `when`
*     crossing (it may not have one -- that is the point) but with a `find
*     ... at` late in the run, so the deck always yields a number.

vsup vddm 0 dc vdd_val
bvth vth 0 v = 0.5*vdd_val

* shared reference release edge (t_release = 5.000 ns, mid-crossing 5.010 ns)
vs sn 0 pulse({vdd_val} 0 1n 20p 20p 3.98n 100n)

* rn per instance: release skewed by dt = PW - 3.98n
vr0 rn0 0 pulse({vdd_val} 0 1n 20p 20p 3.98n 100n)
vr1 rn1 0 pulse({vdd_val} 0 1n 20p 20p 3.980001n 100n)
vr2 rn2 0 pulse({vdd_val} 0 1n 20p 20p 3.98001n 100n)
vr3 rn3 0 pulse({vdd_val} 0 1n 20p 20p 3.9801n 100n)
vr4 rn4 0 pulse({vdd_val} 0 1n 20p 20p 3.981n 100n)
vr5 rn5 0 pulse({vdd_val} 0 1n 20p 20p 3.99n 100n)
vr6 rn6 0 pulse({vdd_val} 0 1n 20p 20p 4.08n 100n)

xa0 sn rn0 q0 qn0 vddm 0 meta_arb cld=0.5f
xa1 sn rn1 q1 qn1 vddm 0 meta_arb cld=0.5f
xa2 sn rn2 q2 qn2 vddm 0 meta_arb cld=0.5f
xa3 sn rn3 q3 qn3 vddm 0 meta_arb cld=0.5f
xa4 sn rn4 q4 qn4 vddm 0 meta_arb cld=0.5f
xa5 sn rn5 q5 qn5 vddm 0 meta_arb cld=0.5f
xa6 sn rn6 q6 qn6 vddm 0 meta_arb cld=0.5f

.ic v(q0)=0
.ic v(q1)=0
.ic v(q2)=0
.ic v(q3)=0
.ic v(q4)=0
.ic v(q5)=0
.ic v(q6)=0
