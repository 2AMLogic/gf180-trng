* ro-array-sanity-jitter -- array-level transient-noise sanity check.
*
* Four independent, separately-supplied 5-stage rings built from the
* design's own leaf cells (ro_nand2 / ro_stage of design/ro_array_sanity.spice,
* exported from design/xschem/ by design/netlist.py), XOR-combined by the
* design's own xor2 tree, with one injected trnoise() source in series with
* EVERY stage input -- the same stimulus, at the same fixed level, that
* sim/tb/ro-inv-05stage-jitter/ uses. Same stage count as that testbench
* too, so the per-ring sigma_1 measured here is comparable to
* sim/characterization-ro-delay-cell-jitter.md's flagship grid cell for
* cell, with the delay cell as the only variable.
*
* Why the array is wired here instead of instantiating ro_array_sanity
* whole: ngspice cannot insert a series source into the interior of a
* subcircuit, and per-stage series injection is the whole method. So this
* fragment instantiates the SAME leaf cells with the SAME parameters and
* reproduces the array's wiring around them. The leaf devices still come
* from the schematic; only the top-level wiring is restated. Compare with
* design/xschem/ro_array_sanity.sch when reviewing.
*
* Injected per-stage input-referred white PSD (harness params vn_rms /
* vn_dt, see tb.json):
*
*     S_inj = 2 * vn_rms^2 * vn_dt = 1e-16 V^2/Hz  (1e-08 V/sqrt(Hz))
*
* fixed across the PVT grid, so what varies corner to corner is the
* circuit's noise-to-jitter conversion, not the stimulus. Recovering the
* physical jitter needs the per-corner device-noise density of THIS cell,
* which sim/tb/rostage-noise/ measures.
*
* The four questions this run exists to answer are array questions, not
* cell questions:
*   1. do four rings simulated together on separate supplies stay at their
*      own frequencies, or do they pull into lock? (period_r1..4 against
*      the nominal wstv skew, and against each other)
*   2. does each ring's jitter in the array match a ring standing alone?
*      (sigma_r1_1 against sim/records/2026-07-31-ro-inv-05stage-jitter-*,
*      via the jitter-energy law of DR-0010 -- the cells differ, so the
*      comparison is at equal power, not equal sigma)
*   3. does jitter still accumulate as sqrt(t) inside the array?
*      (sigma_r1_1 .. sigma_r1_32)
*   4. is the XOR node alive, and what does it cost? (xo swing, tree
*      current, and the ring swing that feeds it)
*
* Per-ring charge integrators (fq/cq/rq, as in sim/tb/ro-inv-05stage-power/)
* run alongside, so the energy per ring cycle and the jitter come from the
* SAME run -- DR-0010's jitter-energy law relates exactly those two
* quantities, and relating them across two different runs would import a
* needless cross-run assumption.
*
* bx1..bx4 are measurement-only probes: they shift each ring output so a
* mid-supply crossing becomes a zero crossing that `meas ... when v(..)=0`
* finds at any supply. The measurement window opens at the second crossing,
* so start-up is not counted as jitter.
*
* Start-up: the enable is held HIGH from t = 0 and each ring is kicked out
* of its unstable DC solution by a .ic on one of its nodes -- exactly the
* method sim/tb/ro-inv-05stage-jitter/ uses. An enable EDGE would be more
* faithful to the block's real start-up path, and the deterministic
* sim/tb/ro-array-core-power/ testbench does use one, but here it is not
* simulable: with twenty trnoise() sources active, ngspice-42 fails to
* converge at the enable edge ("Timestep too small ... trouble with node
* <branch>") at every softening of the edge tried, whereas the .ic start
* runs cleanly. This is a solver limitation, not a circuit finding, and it
* is recorded in each record's Caveats rather than hidden.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vr3 vsup vddr3 dc 0
vr4 vsup vddr4 dc 0
vtr vsup vdd dc 0

* ---- ring 1 (wstv = 0.220u) -----------------------------------------
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

* ---- ring 2 (wstv = 0.240u) -----------------------------------------
xg2 g20 en n21 vddr2 0 ro_nand2 wstv=0.240u lstv=2u cld=0.5f
x21 g21 n22 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x22 g22 n23 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x23 g23 n24 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x24 g24 ro2 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
vn20 ro2 g20 dc 0 trnoise( vn_rms vn_dt 0 0)
vn21 n21 g21 dc 0 trnoise( vn_rms vn_dt 0 0)
vn22 n22 g22 dc 0 trnoise( vn_rms vn_dt 0 0)
vn23 n23 g23 dc 0 trnoise( vn_rms vn_dt 0 0)
vn24 n24 g24 dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- ring 3 (wstv = 0.260u) -----------------------------------------
xg3 g30 en n31 vddr3 0 ro_nand2 wstv=0.260u lstv=2u cld=0.5f
x31 g31 n32 vddr3 0 ro_stage wstv=0.260u lstv=2u cld=0.5f
x32 g32 n33 vddr3 0 ro_stage wstv=0.260u lstv=2u cld=0.5f
x33 g33 n34 vddr3 0 ro_stage wstv=0.260u lstv=2u cld=0.5f
x34 g34 ro3 vddr3 0 ro_stage wstv=0.260u lstv=2u cld=0.5f
vn30 ro3 g30 dc 0 trnoise( vn_rms vn_dt 0 0)
vn31 n31 g31 dc 0 trnoise( vn_rms vn_dt 0 0)
vn32 n32 g32 dc 0 trnoise( vn_rms vn_dt 0 0)
vn33 n33 g33 dc 0 trnoise( vn_rms vn_dt 0 0)
vn34 n34 g34 dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- ring 4 (wstv = 0.285u) -----------------------------------------
xg4 g40 en n41 vddr4 0 ro_nand2 wstv=0.285u lstv=2u cld=0.5f
x41 g41 n42 vddr4 0 ro_stage wstv=0.285u lstv=2u cld=0.5f
x42 g42 n43 vddr4 0 ro_stage wstv=0.285u lstv=2u cld=0.5f
x43 g43 n44 vddr4 0 ro_stage wstv=0.285u lstv=2u cld=0.5f
x44 g44 ro4 vddr4 0 ro_stage wstv=0.285u lstv=2u cld=0.5f
vn40 ro4 g40 dc 0 trnoise( vn_rms vn_dt 0 0)
vn41 n41 g41 dc 0 trnoise( vn_rms vn_dt 0 0)
vn42 n42 g42 dc 0 trnoise( vn_rms vn_dt 0 0)
vn43 n43 g43 dc 0 trnoise( vn_rms vn_dt 0 0)
vn44 n44 g44 dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- XOR combining tree ---------------------------------------------
xa1 ro1 ro2 t1 vdd 0 xor2
xa2 ro3 ro4 t2 vdd 0 xor2
xb1 t1 t2 xo vdd 0 xor2

* ---- charge integrators ---------------------------------------------
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fq4 q4 0 vr4 1
cq4 q4 0 1n
rq4 q4 0 1e12
fqt qt 0 vtr 1
cqt qt 0 1n
rqt qt 0 1e12

* ---- measurement probes ---------------------------------------------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val
bx2 x2 0 v = v(ro2) - 0.5*vdd_val
bx3 x3 0 v = v(ro3) - 0.5*vdd_val
bx4 x4 0 v = v(ro4) - 0.5*vdd_val

.ic v(n11)=0
.ic v(n21)=0
.ic v(n31)=0
.ic v(n41)=0
.ic v(q1)=0
.ic v(q4)=0
.ic v(qt)=0
