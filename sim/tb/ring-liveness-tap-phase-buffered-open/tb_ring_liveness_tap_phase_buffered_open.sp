* ring-liveness-tap-phase-buffered-open -- CONTROL E of issue #76's
* six-variant experiment: the DR-0016 liveness digitizer driven from a
* DR-0018 ro_buf output, with clk held LOW so the digitizer's input
* transmission gate is transparent.
*
* See sim/tb/ring-liveness-tap-phase-shut/'s deck header for the whole
* experiment (issue #76) and the variant list, and
* sim/tb/ring-liveness-tap-phase-buffered-shut/'s for why the buffered pair
* needs its own two static controls rather than borrowing the unbuffered ones.
*
* What THIS deck isolates
* -----------------------
* The buffered arrangement at the clock's OTHER static value. With clk = 0 the
* digitizer's pass devices are both on, so the buffer's OUTPUT node rb1 drives
* the master latch node and the master inverter's 0.66 um of gate; with clk =
* vdd (sim/tb/ring-liveness-tap-phase-buffered-shut/) it drives only the pass
* devices' junction and overlap capacitance.
*
* The ring node itself is behind the buffer in both cases, so a period
* difference between this deck and the -buffered-shut one is not a load change
* seen by the ring: it is the part of the buffer's OUTPUT load change that
* reaches the ring node backwards through the buffer's own gate-drain
* capacitance. That residual is exactly the quantity the mitigation is being
* judged on, and measuring it as a period difference between two static decks
* makes it a prediction the buffered clocked deck's sigma_1 can be tested
* against rather than an assumption.
*
* Everything else is deliberately identical to
* sim/tb/ring-liveness-tap-phase-buffered-shut/, device for device and
* parameter for parameter. The ONE difference is the dc value of vclk.

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

* ---- clk held LOW: the input transmission gate is TRANSPARENT ---------
vclk clk 0 dc 0
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
