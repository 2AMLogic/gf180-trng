* ro-array-coupling-xor-driven -- VARIANT 3 of the four-variant experiment
* that asks why sim/records/2026-08-01-ro-array-sanity-jitter-01.md measures
* ~40x more per-ring jitter, on the same delay cell at the same injected
* noise level, than sim/tb/ro-ring5-starved-jitter-long/ does.
*
* The experiment (issue #51)
* --------------------------
* Four decks, one corner (tt/27 C/3.30 V), one window geometry, differing in
* exactly one thing each:
*
*   1. sim/tb/ro-ring5-starved-jitter-long/     one ring, nothing attached
*                                               (the CONTROL).
*   2. sim/tb/ro-array-coupling-xor-static/     ring + xa1, xa1's second input
*                                               tied to a rail (static load).
*   3. THIS DECK                                ring + xa1, xa1's second input
*                                               driven by a second ring at a
*                                               different frequency.
*   4. sim/tb/ro-array-coupling-rings-only/     two rings, electrically
*                                               unconnected.
*
* What THIS deck isolates
* -----------------------
* The hypothesis under test. In sim/tb/ro-array-sanity-jitter/, ring 1's
* output node ro1 drives the `a` input of xa1 (`xa1 ro1 ro2 t1 vdd 0 xor2`),
* and the internal nodes of that same input stage are driven by ring 2 at a
* different frequency. Gate-drain / gate-source coupling in that stage is a
* path by which ring 2's phase can perturb ring 1's threshold crossings. A
* perturbation of that kind would be deterministic (hence seed-independent),
* and a beat between two incommensurate frequencies rather than a random walk
* (hence an accumulation exponent above 0.5) -- both of which the array-sanity
* record shows.
*
* This deck is variant 2 plus exactly one change: xa1's `b` input is driven by
* a second, independently supplied 5-stage ring at wstv = 0.240 um -- the same
* ring 2 the array carries -- instead of being tied to vss. Ring 2 also gets
* its own five trnoise() sources at the same fixed density, as it does in the
* array. Nothing else connects the two rings: separate supply pins from the
* same vsup, no shared node except through xa1's input stage. Compared with
* variant 4 (the same two rings with xa1 removed), the ONLY difference is the
* electrical attachment.
*
* Ring 1 is the ring under measurement, exactly as in the array-sanity deck.
* Ring 2's period is measured too (period_r2), because the beat frequency the
* hypothesis predicts is set by the two periods and a record that does not
* state both cannot be checked against it.
*
* Ring 1 is device-for-device identical to the control deck: a ro_nand2 enable
* stage plus four ro_stage at wstv = 0.220 um, lstv = 2 um, cld = 0.5 f, one
* trnoise() source in series with every stage input at the same fixed injected
* density
*
*     S_inj = 2 * vn_rms^2 * vn_dt = 1e-16 V^2/Hz  (1e-08 V/sqrt(Hz))
*
* the same charge integrator on the same separate ring supply pin, the same
* bx1 probe, the same .ic start-up, and the same measurement window: opened
* 256 periods after start-up, spanning 512 periods, with the 16-period
* start-up window the array deck used reproduced inside the same run
* (sigma_startup16_*).
*
* Start-up: the enable is held HIGH from t = 0 and each ring is kicked out of
* its unstable DC solution by a .ic, as in every transient-noise ring deck in
* this repository (an enable EDGE does not converge with trnoise() sources
* active in ngspice-42/46 -- a solver limit recorded in those testbenches).
*
* Only v(x1), v(x2), v(q1), v(qt) and v(vsup) are read by any measurement;
* tb.json saves that set and nothing else, because at 1 ps print step over
* 3.2 us the full node set is gigabytes of stored waveform per seeded run.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

* ---- separate ring and tree supply pins -------------------------------
vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
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

* ---- ring 2 (wstv = 0.240u), as in sim/tb/ro-array-sanity-jitter/ -----
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

* ---- the array's first combiner gate, both inputs live ----------------
xa1 ro1 ro2 t1 vdd 0 xor2

* ---- charge integrators: ring 1 and tree, separately ------------------
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fqt qt 0 vtr 1
cqt qt 0 1n
rqt qt 0 1e12

* ---- measurement probes -----------------------------------------------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val
bx2 x2 0 v = v(ro2) - 0.5*vdd_val

.ic v(n11)=0
.ic v(n21)=0
.ic v(q1)=0
.ic v(qt)=0
