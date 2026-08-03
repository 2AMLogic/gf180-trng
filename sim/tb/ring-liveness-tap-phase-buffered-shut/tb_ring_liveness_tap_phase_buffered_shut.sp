* ring-liveness-tap-phase-buffered-shut -- CONTROL D of issue #76's
* six-variant experiment: the DR-0016 liveness digitizer driven from a
* DR-0018 ro_buf output, with clk held HIGH so the digitizer's input
* transmission gate is opaque.
*
* See sim/tb/ring-liveness-tap-phase-shut/'s deck header for the whole
* experiment (issue #76) and the variant list.
*
* Why this control exists
* -----------------------
* Inserting the buffer changes two things about the ring at once: it isolates
* the ring node from whatever the digitizer does, and it changes the ring's
* load from the digitizer's pass devices to the buffer's 0.66 um input gate --
* a different operating point, so a different period. Reading the buffered
* clocked deck against the UNBUFFERED static controls would therefore span two
* changes and attribute neither. This deck and
* sim/tb/ring-liveness-tap-phase-buffered-open/ hold the buffered operating
* point fixed at each of the clock's two static values, so
*
*     sigma_1(buffered, clk running) / sigma_1(buffered, clk quiet)
*
* differs in exactly one thing -- does the clock switch -- and is the direct
* counterpart of the same ratio taken on the unbuffered pair. Issue #75 /
* sim/characterization-ring-buffer-mitigation.md learned this the same way and
* for the same reason, and this deck is that lesson applied to this family.
*
* This deck is the clk = vdd half of that pair. The buffer's OUTPUT node rb1
* sees only the digitizer's pass-device junction and overlap capacitance here,
* against the master latch's full input gate in the -open half. The difference
* between the two decks' PERIODS is the residual load modulation the buffer
* passes back to the ring node through its own gate-drain capacitance, and it
* is what the buffered clocked deck's sigma_1 is predicted from -- exactly as
* the unbuffered -shut/-open pair predicts the unbuffered clocked deck's.
*
* Everything else is deliberately identical to
* sim/tb/ring-liveness-tap-phase-buffered-clocked/, device for device and
* parameter for parameter. The ONE difference is that vclk is a dc source
* instead of a pulse source.

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

* ---- clk held HIGH: the input transmission gate is OPAQUE -------------
vclk clk 0 dc vdd_val
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

* ---- measurement probe -- the RAW ring node, upstream of the buffer ---
bx1 x1 0 v = v(ro1) - 0.5*vdd_val

.ic v(n11)=0
.ic v(q1)=0
.ic v(qbf)=0
.ic v(qtap)=0
