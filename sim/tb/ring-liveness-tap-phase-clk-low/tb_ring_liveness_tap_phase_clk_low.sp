* ring-liveness-tap-phase-clk-low -- VARIANT 3 of issue #76's phase-cost
* experiment on the DR-0016 per-ring liveness digitizer.
*
* The family, the question, the ring, the window geometry, the injected noise
* density and the corner are all documented once in
* sim/tb/ring-liveness-tap-phase-clk-high/tb_ring_liveness_tap_phase_clk_high.sp;
* this deck differs from that one in exactly one character of one line:
*
*     clk-high:  vclk clk 0 dc vdd_val
*     THIS DECK: vclk clk 0 dc 0
*
* What THIS deck isolates
* -----------------------
* The other static endpoint the clocked tap swings between. In
* sampler_dff the master transmission gate
*
*     XMtdp d clk  m vdd pfet_03v3 W=0.44u
*     XMtdn d clkb m vss nfet_03v3 W=0.22u
*
* conducts when clk is LOW, so with clk on the low rail the ring node ro1 is
* connected straight through to the master latch node `m`, and therefore
* drives the master latch's input inverter (XMimpa 0.44 um pfet + XMimna
* 0.44 um nfet) -- and drives it *through a full transition every ring cycle*,
* because a transparent latch follows its input. That is the HEAVIEST load the
* tap can present to the ring, and it is the state the digitizer sits
* in for half of every clk period (a positive-edge-triggered flip-flop's master
* is transparent while clk is low).
*
* Read against sim/tb/ring-liveness-tap-phase-clk-high/ this deck says how far
* apart the tap's two static endpoints are. If they are far apart, then a clk
* that alternates between them is not a small perturbation on a ring -- it is a
* frequency modulation locked to clk -- and sim/tb/ring-liveness-tap-phase-clocked/
* is what measures that directly.
*
* Like the clk-high deck, this one contains no edge anywhere after start-up:
* clk and rst_n are DC sources. That is what makes it a static reference.
*
* tstop is longer than the clk-high deck's because this deck's ring is slower
* (the master latch is a real load and the ring pays for it every cycle), and
* the measurement window is still 770 rises. Nothing else about the window
* changed: it still opens 256 periods after start-up and spans 512 periods.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

* ---- separate ring supply pin, so the charge integrator sees the ring
*      current alone (identical arrangement to the control deck) ---------
vr1 vsup vddr1 dc 0

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

* ---- the shipped DR-0016 per-ring liveness digitizer, unmodified ------
* ---- (design/sampler_core.spice: `xsr1 ro1 clk rst_n ring_bit1 vdd vss`)
xsr1 ro1 clk rst_n ring_bit1 vsup 0 sampler_dff

* ---- clk held LOW: master transmission gate ON ------------------------
vclk clk 0 dc 0
vrst rst_n 0 dc vdd_val

* ---- charge integrator: q1 is the ring's accumulated supply charge ----
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12

* ---- measurement probe ------------------------------------------------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val

.ic v(n11)=0
.ic v(q1)=0
