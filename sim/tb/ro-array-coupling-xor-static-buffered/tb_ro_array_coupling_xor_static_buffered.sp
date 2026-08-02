* ro-array-coupling-xor-static-buffered -- issue #75's MATCHED CONTROL for
* sim/tb/ro-array-coupling-xor-driven-buffered/.
*
* Why this deck exists
* --------------------
* Issue #51 measured 28.6x by comparing two decks that differ in exactly one
* thing: sim/tb/ro-array-coupling-xor-driven/ (neighbour switching) against
* sim/tb/ro-array-coupling-xor-static/ (same gate load, neighbour on a rail).
* That variant-2 deck's own tb.json states why the pairing is the one that
* attributes anything: "a slower ring is a different operating point, so a
* sigma difference between this variant and the control is not by itself
* evidence of anything dynamic".
*
* Inserting a buffer changes the ring's load (from xa1's 1.98 um of gate to
* the buffer's 0.66 um), so the buffered ring is a different operating point
* again -- faster, and closer to the unloaded control's. Reading the buffered
* DRIVEN deck against issue #51's UNBUFFERED controls therefore mixes two
* changes: the buffer's isolation and the buffer's lighter load. This deck is
* the missing quiet-neighbour control at the buffered operating point, so that
*
*   ro-array-coupling-xor-driven-buffered   (neighbour switching, buffered)
*   ro-array-coupling-xor-static-buffered   (neighbour on a rail, buffered)  <- THIS DECK
*
* differ in exactly one thing -- whether the neighbour switches -- exactly as
* issue #51's variant 3 / variant 2 pair does. Their sigma_1 ratio is the
* residual coupling factor at the buffered operating point, directly against
* the 28.6x that same ratio gives unbuffered.
*
* What it is
* ----------
* sim/tb/ro-array-coupling-xor-static/ (issue #51's variant 2) plus exactly
* one change: a minimum-width inverter buffer between the ring node and xa1's
* input, so xa1 sees rb1 rather than ro1. xa1's second input is tied to vss,
* the same rail and the same fixed operating point variant 2 uses -- and the
* same caveat applies, that the other rail was not measured.
*
* Everything else is device-for-device variant 2: one starved 5-stage ring
* (ro_nand2 enable stage + four ro_stage, wstv = 0.220 um, lstv = 2 um,
* cld = 0.5 f), five trnoise() sources at the same fixed injected density
*
*     S_inj = 2 * vn_rms^2 * vn_dt = 1e-16 V^2/Hz  (1e-08 V/sqrt(Hz))
*
* the same charge integrators on the same separate supply pins, the same bx1
* probe, the same .ic start-up, the same corner, the same tstop, the same seed
* count and the same window: opened 256 periods after start-up, spanning 512
* periods, with the 16-period start-up window reproduced inside the same run.
*
* sigma is measured at the RAW ring node v(ro1), upstream of the buffer, for
* the same reason the driven-buffered deck does it: the question is whether
* the ring's own oscillating node stays quiet, not whether a low-impedance
* driven node is quiet (which it is by construction).
*
* The buffer gets its own metered supply pin (vddb1) purely for bookkeeping,
* as in the driven-buffered deck. All branches are zero-volt ammeter sources
* off the same IDEAL vsup, so the metering split adds no electrical path.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

* ---- separate ring, buffer and tree supply pins ------------------------
vr1 vsup vddr1 dc 0
vb1 vsup vddb1 dc 0
vtr vsup vdd dc 0

* ---- the buffer: one minimum-width inverter, same device sizing AND -----
* ---- the same diffusion geometry as xor2's own input stage --------------
* Identical to the ro_buf in sim/tb/ro-array-coupling-xor-driven-buffered/;
* the ad/as/pd/ps/nrd/nrs expressions come from design/ro_array_sanity.spice's
* own devices, so the buffer's drain junction capacitance is modelled on the
* same footing as the circuit it is spliced into.
.subckt ro_buf a y vdd vss
XMp y a vdd vdd pfet_03v3 L=0.28u W=0.44u nf=1 ad='int((nf+1)/2) * W/nf * 0.18u' as='int((nf+2)/2) * W/nf * 0.18u'
+ pd='2*int((nf+1)/2) * (W/nf + 0.18u)' ps='2*int((nf+2)/2) * (W/nf + 0.18u)' nrd='0.18u / W' nrs='0.18u / W' sa=0 sb=0
+ sd=0 m=1
XMn y a vss vss nfet_03v3 L=0.28u W=0.22u nf=1 ad='int((nf+1)/2) * W/nf * 0.18u' as='int((nf+2)/2) * W/nf * 0.18u'
+ pd='2*int((nf+1)/2) * (W/nf + 0.18u)' ps='2*int((nf+2)/2) * (W/nf + 0.18u)' nrd='0.18u / W' nrs='0.18u / W' sa=0 sb=0
+ sd=0 m=1
.ends

* ---- ring 1 (wstv = 0.220u), identical to variant 2 and the control ----
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

* ---- the ring's own buffer, then the combiner with its 2nd input on a rail
xb1 ro1 rb1 vddb1 0 ro_buf
xa1 rb1 0 t1 vdd 0 xor2

* ---- charge integrators: ring, buffer and tree, separately -------------
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fqb1 qb1 0 vb1 1
cqb1 qb1 0 1n
rqb1 qb1 0 1e12
fqt qt 0 vtr 1
cqt qt 0 1n
rqt qt 0 1e12

* ---- measurement probe -- RAW ring node, upstream of the buffer --------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val

.ic v(n11)=0
.ic v(q1)=0
.ic v(qb1)=0
.ic v(qt)=0
