* ring-liveness-tap-phase-buffered-clocked -- the MITIGATION variant of issue
* #76: the DR-0016 per-ring liveness digitizer driven from an ro_buf output
* instead of from the raw ring node, with clk running.
*
* See sim/tb/ring-liveness-tap-phase-shut/'s deck header for the whole
* experiment (issue #76) and the variant list. This deck is
* sim/tb/ring-liveness-tap-phase-clocked/ with exactly one change: where the
* digitizer taps.
*
* This is not a hypothetical mitigation
* -------------------------------------
* It is the arrangement the shipped design has carried since #82 / DR-0018.
* design/xschem/ro_array_core.sch instantiates one ro_buf per ring (xb1/xb2,
* never shared) between the ring's own last stage (rn1/rn2) and everything
* that consumes it, and re-drives the exported ro1/ro2 pins from the buffer
* outputs -- so sampler_core.sch's xsr1/xsr2 digitize the BUFFERED node, not
* the ring node. DR-0018 adopted that buffer for a different reason (the
* array-to-array coupling issue #75 measured through the XOR combiner);
* issue #76 asks whether it also removes the digitizer's phase disturbance,
* which is a question about a different consumer of the same buffer.
*
* The buffer here is the shipped `ro_buf` subcircuit out of
* design/sampler_core.spice, unmodified -- the same cell ro_array_core
* instantiates, not a hand-copied inverter.
*
* Where sigma is measured
* -----------------------
* bx1 probes v(ro1) -- the RAW ring node, UPSTREAM of the buffer -- exactly as
* sim/tb/ro-array-coupling-xor-driven-buffered/ does for the same reason. The
* question is whether the buffer keeps the disturbance off the ring's own
* oscillating node; probing the buffer output would answer a different and
* trivial question.
*
* Fidelity limit worth stating up front: in the shipped array the buffer's
* output drives the XOR combiner AND both digitizers, where here it drives one
* digitizer only. That makes this deck's buffer LIGHTLY loaded relative to the
* shipped one. That has two consequences, in opposite directions, and both are
* stated rather than assumed:
*   - i_buf_a is a FLOOR on the shipped buffer's own current, not the shipped
*     buffer's number;
*   - the residual disturbance measured here is an UPPER BOUND on the shipped
*     arrangement's. What the clock modulates is the capacitance hung on the
*     buffer's OUTPUT node; the fraction of that node's total capacitance the
*     modulation represents is what determines how much of it feeds back
*     through the buffer's gate-drain capacitance to the ring. The shipped
*     buffer carries xa1's fixed input capacitance on the same node in
*     addition, which can only make that fraction smaller.
* Neither statement is a measurement of the shipped arrangement, which this
* family does not contain.
*
* Everything else is deliberately identical to
* sim/tb/ring-liveness-tap-phase-clocked/, device for device and parameter for
* parameter.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

* ---- separate ring, buffer and digitizer supply pins ------------------
vr1 vsup vddr1 dc 0
vb1 vsup vddb1 dc 0
vtap vsup vddtap dc 0

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

* ---- DR-0018's per-ring output buffer, shipped cell, on its own pin ---
xb1 ro1 rb1 vddb1 0 ro_buf

* ---- the DR-0016 liveness digitizer, on the BUFFERED node -------------
xsr1 rb1 clk rst_n ring_bit1 vddtap 0 sampler_dff

* ---- clk RUNNING at DR-0003's ratified 1 Mbps raw rate ----------------
vclk clk 0 dc 0 pulse(0 'vdd_val' 'tclk0' 'tclk_tr' 'tclk_tr' 'tclk/2-tclk_tr' 'tclk')
vrst rst_n 0 dc vdd_val

* ---- charge integrators: ring, buffer and digitizer, separately -------
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fqbf qbf 0 vb1 1
cqbf qbf 0 1n
rqbf qbf 0 1e12
fqtap qtap 0 vtap 1
cqtap qtap 0 1n
rqtap qtap 0 1e12

* ---- measurement probes -- the RAW ring node, upstream of the buffer --
bx1 x1 0 v = v(ro1) - 0.5*vdd_val
bclkp clkp 0 v = tclk

.ic v(n11)=0
.ic v(q1)=0
.ic v(qbf)=0
.ic v(qtap)=0
