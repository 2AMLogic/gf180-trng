* ro-array-core-power-buffered -- issue #75: the buffer's own power cost,
* and whether each ring's own power drops from the load reduction, measured
* rather than estimated.
*
* This is sim/tb/ro-array-core-power/ (the shipped, un-mitigated
* design/ro_array_core.spice) with exactly one addition: one minimum-width
* inverter buffer per ring, spliced in between that ring's output node and
* xa1's input -- the same mitigation sim/tb/ro-array-coupling-xor-driven-buffered/
* tests for jitter, now measured for power at the corner
* layout/floorplan/README.md's ~24.4 uW estimate was made at: ff/-40 C/3.63 V,
* the power-binding corner (that estimate used
* sim/records/2026-08-01-ro-array-core-power-04.md's measured c_eff_node_r1
* and per-ring frequencies -- this deck supersedes the need to estimate at all
* by measuring the buffered array directly, at the same corner).
*
* Because design/ro_array_core.spice's own xdut instantiation (used by the
* unbuffered ro-array-core-power deck) has no splice point for the buffer,
* this deck hand-expands ro_array_core's two rings the same way
* sim/tb/ro-array-coupling-xor-driven/ already does for the jitter
* experiment, rather than editing the committed schematic-derived netlist --
* the buffer is not adopted into the schematic (issue #75's own scope: "no
* schematic adoption without a measured result first"). Every ring device is
* otherwise identical to design/ro_array_core.spice's expansion: an
* ro_nand2 enable stage plus ten ro_stage per ring (wstv = 0.220u / 0.240u,
* lstv = 2u, cld = 0.5f), the array's own xor2 combiner, no trnoise() sources
* (this is the deterministic power deck, not the jitter deck).
*
* Method notes -- identical to sim/tb/ro-array-core-power/ except for the
* buffer splice and its separate metering:
*   - Per-branch 0 V sense sources split one ideal vsup into five separately
*     integrable branches: each ring's own current (vr1/vr2), each ring's
*     buffer current (vb1/vb2, metered separately from its ring for the same
*     bookkeeping reason sim/tb/ro-array-coupling-xor-driven-buffered/ uses),
*     and the XOR tree's current (vtr).
*   - fqN/cqN/rqN is the same ideal charge integrator every power deck in
*     this repository uses.
*   - Start-up: enable held HIGH from t = 0, each ring kicked out of its
*     unstable DC solution by a .ic on its NAND output.
*   - bvth is a mid-supply reference so `meas ... when v(ring)=v(vth)` finds
*     crossings at any supply.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

* ---- separate ring, buffer and tree supply pins ------------------------
vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vb1 vsup vddb1 dc 0
vb2 vsup vddb2 dc 0
vtr vsup vdd dc 0

* ---- the buffer: one minimum-width inverter, same device sizing AND -----
* ---- the same diffusion geometry as xor2's own input stage --------------
* The ad/as/pd/ps/nrd/nrs expressions are copied verbatim from
* design/ro_array_core.spice's own devices, so the buffer's drain junction
* capacitance and source/drain resistance are modelled on the same footing as
* every other device in the deck. Omitting them would under-state the
* buffer's own switching cost, which is the number this deck exists to
* measure rather than estimate.
.subckt ro_buf a y vdd vss
XMp y a vdd vdd pfet_03v3 L=0.28u W=0.44u nf=1 ad='int((nf+1)/2) * W/nf * 0.18u' as='int((nf+2)/2) * W/nf * 0.18u'
+ pd='2*int((nf+1)/2) * (W/nf + 0.18u)' ps='2*int((nf+2)/2) * (W/nf + 0.18u)' nrd='0.18u / W' nrs='0.18u / W' sa=0 sb=0
+ sd=0 m=1
XMn y a vss vss nfet_03v3 L=0.28u W=0.22u nf=1 ad='int((nf+1)/2) * W/nf * 0.18u' as='int((nf+2)/2) * W/nf * 0.18u'
+ pd='2*int((nf+1)/2) * (W/nf + 0.18u)' ps='2*int((nf+2)/2) * (W/nf + 0.18u)' nrd='0.18u / W' nrs='0.18u / W' sa=0 sb=0
+ sd=0 m=1
.ends

* ---- ring 1 (wstv = 0.220u), 11-stage: ro_nand2 + 10 x ro_stage, one ---
* ---- nand instance whose `a` input closes the loop from the ring's own -
* ---- last stage (ro1) -- the same topology design/ro_array_core.spice's -
* ---- ro_ring11 expands to, just with un-dotted node names -------------
xg1 ro1 en n11 vddr1 0 ro_nand2 wstv=0.220u lstv=2u cld=0.5f
x11 n11 n12 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x12 n12 n13 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x13 n13 n14 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x14 n14 n15 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x15 n15 n16 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x16 n16 n17 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x17 n17 n18 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x18 n18 n19 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x19 n19 n1a vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x1a n1a ro1 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f

* ---- ring 2 (wstv = 0.240u), 11-stage, same topology -------------------
xg2 ro2 en n21 vddr2 0 ro_nand2 wstv=0.240u lstv=2u cld=0.5f
x21 n21 n22 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x22 n22 n23 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x23 n23 n24 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x24 n24 n25 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x25 n25 n26 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x26 n26 n27 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x27 n27 n28 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x28 n28 n29 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x29 n29 n2a vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x2a n2a ro2 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f

* ---- one buffer per ring, per-ring supply pin, never shared -----------
xb1 ro1 rb1 vddb1 0 ro_buf
xb2 ro2 rb2 vddb2 0 ro_buf

* ---- the array's combiner, now driven by the BUFFERED nodes -----------
xa1 rb1 rb2 xo vdd 0 xor2

fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fq2 q2 0 vr2 1
cq2 q2 0 1n
rq2 q2 0 1e12
fqb1 qb1 0 vb1 1
cqb1 qb1 0 1n
rqb1 qb1 0 1e12
fqb2 qb2 0 vb2 1
cqb2 qb2 0 1n
rqb2 qb2 0 1e12
fqt qt 0 vtr 1
cqt qt 0 1n
rqt qt 0 1e12

bvth vth 0 v = 0.5*vdd_val

.ic v(n11)=0
.ic v(n21)=0
.ic v(q1)=0
.ic v(q2)=0
.ic v(qb1)=0
.ic v(qb2)=0
.ic v(qt)=0
