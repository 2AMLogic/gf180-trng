* ro-array-coupling-xor-static -- VARIANT 2 of the four-variant experiment
* that asks why sim/records/2026-08-01-ro-array-sanity-jitter-01.md measures
* ~40x more per-ring jitter, on the same delay cell at the same injected
* noise level, than sim/tb/ro-ring5-starved-jitter-long/ does.
*
* The experiment (issue #51)
* --------------------------
* Four decks, one corner (tt/27 C/3.30 V), one window geometry, differing in
* exactly one thing each:
*
*   1. sim/tb/ro-ring5-starved-jitter-long/  -- one ring, nothing attached.
*      The CONTROL. Already measured: sigma_1 = 0.587 ps (raw, at the fixed
*      injected level), records 2026-08-01-ro-ring5-starved-jitter-long-02.
*   2. THIS DECK -- the same ring, plus the array's own xa1 XOR gate, with
*      xa1's second input tied to a RAIL. Ring 1 therefore carries the array's
*      static gate load but sees no switching neighbour.
*   3. sim/tb/ro-array-coupling-xor-driven/  -- the same ring plus xa1, with
*      xa1's second input driven by a second ring at a different frequency.
*      The array's combiner input stage, in isolation from the rest of the
*      tree.
*   4. sim/tb/ro-array-coupling-rings-only/  -- two rings present in the deck
*      and electrically UNCONNECTED. Separates "another ring is being solved
*      on the same adaptive timestep" (a numerical explanation) from "another
*      ring is electrically attached" (a coupling explanation).
*
* What THIS deck isolates
* -----------------------
* The static load from the dynamic coupling. In the array, ro1 drives the `a`
* input of xa1 -- four transistor gates (2x 0.44 um pfet, 1x 0.88 um pfet,
* 1x 0.44 um nfet, see design/xschem/xor2.sch). That load slows the ring and
* changes its output slew, and a slower slew converts a given input-referred
* noise voltage into more timing jitter. So a load alone is not a priori
* innocent, and this deck measures how much of the array deck's excess sigma
* it accounts for. If sigma comes back at the control's value, the load is
* innocent and whatever the array deck saw is dynamic.
*
* xa1's `b` input is tied to vss (0) rather than left floating or driven:
* floating would leave an undriven gate node and is not a defined experiment,
* and driving it is variant 3. With b = 0 the gate computes y = a, so the
* internal nodes of the input stage sit at one fixed operating point instead
* of the two ring 2 walks it through. Tying b to vdd instead would put them at
* the other fixed point; that asymmetry is a limit of this variant and is
* stated in the records it produces.
*
* Everything else is deliberately identical to
* sim/tb/ro-ring5-starved-jitter-long/, device for device and parameter for
* parameter: a ro_nand2 enable stage plus four ro_stage at wstv = 0.220 um,
* lstv = 2 um, cld = 0.5 f, one trnoise() source in series with every stage
* input at the same fixed injected density
*
*     S_inj = 2 * vn_rms^2 * vn_dt = 1e-16 V^2/Hz  (1e-08 V/sqrt(Hz))
*
* the same charge integrator on the same separate ring supply pin, the same
* bx1 measurement probe, the same .ic start-up, and the same measurement
* window: opened 256 periods after start-up, spanning 512 periods, with the
* 16-period start-up window the array deck used reproduced inside the same run
* (sigma_startup16_*) for a like-for-like comparison.
*
* The XOR gate is supplied from its own pin (vtr) so the tree's current can be
* separated from the ring's, exactly as sim/tb/ro-array-sanity-jitter/ does.
*
* Start-up: the enable is held HIGH from t = 0 and the ring is kicked out of
* its unstable DC solution by a .ic, as in every transient-noise ring deck in
* this repository (an enable EDGE does not converge with trnoise() sources
* active in ngspice-42/46 -- a solver limit recorded in those testbenches).
*
* Only v(x1), v(q1), v(qt) and v(vsup) are read by any measurement; tb.json
* saves that set and nothing else, because at 1 ps print step over 3.2 us the
* full node set is gigabytes of stored waveform per seeded run.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

* ---- separate ring and tree supply pins -------------------------------
vr1 vsup vddr1 dc 0
vtr vsup vdd dc 0

* ---- ring 1 (wstv = 0.220u), identical to the control deck ------------
xg1 g10 en n11 vddr1 0 ro_nand2 wstv=0.220u lstv=2u cld=0.5f
x11 g11 n12 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x12 g12 n13 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x13 g13 n14 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x14 g14 ro1 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
vn10 ro1 g10 dc 0 trnoise( vn_rms vn_dt 0 0)
vn11 n11 g11 dc 0 trnoise( vn_rms vn_dt 0 0)
vn12 n12 g12 dc 0 trnoise( vn_rms vn_dt 0 0)
vn13 n13 g13 dc 0 trnoise( vn_rms vn_dt 0 0)
vn14 n14 g14 dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- the array's first combiner gate, second input tied to a rail -----
xa1 ro1 0 t1 vdd 0 xor2

* ---- charge integrators: ring and tree, separately --------------------
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fqt qt 0 vtr 1
cqt qt 0 1n
rqt qt 0 1e12

* ---- measurement probe ------------------------------------------------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val

.ic v(n11)=0
.ic v(q1)=0
.ic v(qt)=0
