* ro-array-coupling-xor-driven-buffered -- issue #75: does one per-ring
* buffer, ahead of the combiner, remove the 28.6x coupling issue #51 / PR #67
* measured?
*
* This deck is sim/tb/ro-array-coupling-xor-driven/ (issue #51's variant 3,
* the 28.6x case) plus exactly one change, per that issue's own
* one-change-per-variant discipline: a minimum-width inverter buffer is
* spliced in between each ring's output node and xa1's input, exactly as
* layout/floorplan/README.md's "Proposed mitigation" section describes it --
* one buffer per ring, never shared. xa1 now sees rb1/rb2 (the buffer
* outputs), not ro1/ro2 (the ring nodes) directly.
*
* Nothing else differs from sim/tb/ro-array-coupling-xor-driven/: same two
* rings (wstv = 0.220u / 0.240u), same injected noise density and sources,
* same corner (tt/27 C/3.30 V), same window geometry (opened 256 periods
* after start-up, spans 512 periods, with the 16-period start-up window
* reproduced alongside), same tstop, same seed count (4). See that deck's
* header comment for the full experiment context (issue #51) this variant
* extends.
*
* The buffer
* ----------
* One minimum-width inverter, the same device sizing xor2's own input stage
* and ro_stage's core inverter already use in this design: pfet_03v3
* w=0.44u, nfet_03v3 w=0.22u, both l=0.28u (the standard gate length used
* throughout -- lstv=2u is reserved for the RING's own series starve
* devices, which the buffer does not have; it is a plain static inverter).
* layout/floorplan/README.md states the structural point this replaces: the
* buffer's input presents 0.66 um of total gate width to the ring node,
* against xa1's 1.98 um -- a 3x load reduction on top of whatever isolation
* the buffer's low-impedance output offers.
*
* Both rings get their own buffer instance (xb1/xb2), not one buffer shared
* between them -- the "per-ring, never shared" requirement the README and
* the issue both state, because a shared buffer stage recreates exactly the
* shared node this mitigation exists to remove.
*
* Measurement points
* -------------------
* bx1/bx2 still probe v(ro1)/v(ro2) -- the RAW ring nodes, upstream of the
* buffer -- not the buffered nodes rb1/rb2. The question this deck answers
* is whether the buffer keeps the disturbance from reaching the ring's own
* oscillating node, so the ring node is where sigma must be measured; probing
* the buffer output would answer a different, less interesting question
* (whether the buffered signal is quiet, which it trivially is by
* construction of a low-impedance driven node).
*
* Each buffer is given its OWN metered supply pin (vddb1/vddb2), separate
* from its ring's own supply pin (vddr1/vddr2), purely for power bookkeeping
* -- exactly the same reason vtr is metered separately from vr1/vr2 in the
* unbuffered variant. This lets "the ring's own current, now under a lighter
* load" and "the buffer's own current" be read as two independent numbers
* instead of one combined figure, which is what issue #75's acceptance
* criteria asks for (the buffer's cost measured, and separately, whether the
* ring's own power drops from the load reduction). In an adopted layout the
* buffer would most naturally sit on the ring's own per-ring supply domain
* (vddr1/vddr2 per layout/floorplan/README.md's region table) rather than on
* a fifth rail; this testbench meters it separately without changing that
* electrical connection's *intent* -- both branches are still zero-impedance
* taps off the same ideal vsup, so no coupling path is added or removed by
* the metering split itself.

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
* design/ro_array_sanity.spice's own devices, so the buffer's drain junction
* capacitance and source/drain resistance are modelled on the same footing as
* every other device in the deck. Omitting them would under-state the
* buffer's own switching cost, which is the number issue #75 exists to
* measure rather than estimate.
.subckt ro_buf a y vdd vss
XMp y a vdd vdd pfet_03v3 L=0.28u W=0.44u nf=1 ad='int((nf+1)/2) * W/nf * 0.18u' as='int((nf+2)/2) * W/nf * 0.18u'
+ pd='2*int((nf+1)/2) * (W/nf + 0.18u)' ps='2*int((nf+2)/2) * (W/nf + 0.18u)' nrd='0.18u / W' nrs='0.18u / W' sa=0 sb=0
+ sd=0 m=1
XMn y a vss vss nfet_03v3 L=0.28u W=0.22u nf=1 ad='int((nf+1)/2) * W/nf * 0.18u' as='int((nf+2)/2) * W/nf * 0.18u'
+ pd='2*int((nf+1)/2) * (W/nf + 0.18u)' ps='2*int((nf+2)/2) * (W/nf + 0.18u)' nrd='0.18u / W' nrs='0.18u / W' sa=0 sb=0
+ sd=0 m=1
.ends

* ---- ring 1 (wstv = 0.220u), identical to the control/xor-driven decks -
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

* ---- one buffer per ring, per-ring supply pin, never shared -----------
xb1 ro1 rb1 vddb1 0 ro_buf
xb2 ro2 rb2 vddb2 0 ro_buf

* ---- the array's first combiner gate, now driven by the BUFFERED nodes -
xa1 rb1 rb2 t1 vdd 0 xor2

* ---- charge integrators: ring 1, ring 2's buffer, buffer 1, tree -------
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fqb1 qb1 0 vb1 1
cqb1 qb1 0 1n
rqb1 qb1 0 1e12
fqb2 qb2 0 vb2 1
cqb2 qb2 0 1n
rqb2 qb2 0 1e12
fqt qt 0 vtr 1
cqt qt 0 1n
rqt qt 0 1e12

* ---- measurement probes -- RAW ring nodes, upstream of the buffer ------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val
bx2 x2 0 v = v(ro2) - 0.5*vdd_val

.ic v(n11)=0
.ic v(n21)=0
.ic v(q1)=0
.ic v(qb1)=0
.ic v(qb2)=0
.ic v(qt)=0
