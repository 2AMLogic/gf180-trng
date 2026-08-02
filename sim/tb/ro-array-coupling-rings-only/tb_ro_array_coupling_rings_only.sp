* ro-array-coupling-rings-only -- VARIANT 4 of the four-variant experiment
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
*   3. sim/tb/ro-array-coupling-xor-driven/     ring + xa1, xa1's second input
*                                               driven by a second ring.
*   4. THIS DECK                                two rings, electrically
*                                               UNCONNECTED.
*
* What THIS deck isolates -- and why it is the decisive one
* ---------------------------------------------------------
* Two hypotheses are on the table for the array deck's excess sigma, and both
* predict a seed-independent, faster-than-sqrt(t) result:
*
*   COUPLING -- ring 2's phase perturbs ring 1's threshold crossings through
*   the shared gate structure of the combiner's input stage;
*   NUMERICAL -- ngspice solves the whole deck on ONE shared adaptive
*   timestep, so a second ring at an incommensurate frequency changes where
*   ring 1's own timepoints land, and the crossing times ring 1's `meas`
*   interpolates from move with it.
*
* This deck contains everything the numerical explanation needs (two rings at
* incommensurate frequencies, ten trnoise() sources, one shared adaptive
* timestep) and nothing the coupling explanation needs (there is no node, no
* device and no supply pin shared between the two rings -- vr1 and vr2 are
* separate zero-volt sources off the same ideal vsup, which is a measurement
* arrangement, not an electrical path, because an ideal voltage source has no
* impedance for one ring's current to develop a voltage across for the other
* to see).
*
* So:
*   - if THIS deck reproduces the excess and variant 2 does not, the effect is
*     numerical and the honest outcome is a documented method limit;
*   - if variant 3 reproduces it and this deck does not, the effect is
*     coupling through the combiner input stage, which is a ring-independence
*     finding (issue #16, and DR-0007 section 2's independence assumption);
*   - if neither reproduces it, the array deck's excess is caused by something
*     else again -- most likely the two rings this deck omits, the rest of the
*     XOR tree, or the array deck's much shorter run -- and that is a stated
*     negative result, not a silence.
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
* (sigma_startup16_*). Ring 2 is the array's ring 2, at wstv = 0.240 um, with
* its own five trnoise() sources.
*
* Because nothing is attached to ro1, this deck's ring 1 should reproduce the
* CONTROL's period to within the seed spread. That equality is itself a check
* on the deck: if it does not hold, this variant differs from the control in
* more than the one intended thing and its comparison is void.
*
* Start-up: the enable is held HIGH from t = 0 and each ring is kicked out of
* its unstable DC solution by a .ic, as in every transient-noise ring deck in
* this repository (an enable EDGE does not converge with trnoise() sources
* active in ngspice-42/46 -- a solver limit recorded in those testbenches).
*
* Only v(x1), v(x2), v(q1) and v(vsup) are read by any measurement; tb.json
* saves that set and nothing else, because at 1 ps print step over 2.4 us the
* full node set is gigabytes of stored waveform per seeded run.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

* ---- separate ring supply pins ----------------------------------------
vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0

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

* ---- ring 2 (wstv = 0.240u), present but attached to nothing ----------
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

* ---- charge integrator: ring 1 -----------------------------------------
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12

* ---- measurement probes -----------------------------------------------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val
bx2 x2 0 v = v(ro2) - 0.5*vdd_val

.ic v(n11)=0
.ic v(n21)=0
.ic v(q1)=0
