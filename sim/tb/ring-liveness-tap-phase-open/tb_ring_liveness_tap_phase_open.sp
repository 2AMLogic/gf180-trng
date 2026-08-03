* ring-liveness-tap-phase-open -- CONTROL B of issue #76's six-variant
* experiment: what does the DR-0016 per-ring liveness digitizer cost the ring
* it observes, in PHASE rather than in power?
*
* See sim/tb/ring-liveness-tap-phase-shut/'s deck header for the whole
* experiment (issue #76), the variant list, and why the digitizer's tap is
* structurally the arrangement sim/characterization-array-ring-coupling.md
* (issue #51) measured at 28.6x.
*
* What THIS deck isolates
* -----------------------
* The digitizer's static load with its input transmission gate TRANSPARENT.
* With clk = 0 the pfet pass device (gate = clk) and the nfet pass device
* (gate = clkb = vdd) are both on, so the ring node is connected straight
* through to the master latch node `m` and drives the master inverter's gates
* (0.44 um pfet + 0.44 um nfet) on top of the pass devices' own junction and
* overlap capacitance. This is the HEAVY of the digitizer's two static loads.
*
* Why both static points are measured, where issue #51 measured one
* ----------------------------------------------------------------
* Issue #51's variant 2 tied its XOR gate's second input to vss and recorded,
* as a stated limit, that the other fixed operating point was not measured.
* Here that limit cannot be accepted, because the difference between the two
* points IS the quantity the clocked variant modulates: a clk-driven pass gate
* does not sit at one of them, it alternates between them at the clock rate.
* So this deck and sim/tb/ring-liveness-tap-phase-shut/ measure both, and
* their difference is a prediction the clocked deck's sigma can be tested
* against rather than an unmeasured corner of the experiment.
*
* Everything else is deliberately identical to
* sim/tb/ring-liveness-tap-phase-shut/, device for device and parameter for
* parameter. The ONE difference is the dc value of vclk.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

* ---- separate ring and digitizer supply pins --------------------------
vr1 vsup vddr1 dc 0
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

* ---- the DR-0016 liveness digitizer, on the RAW ring node -------------
xsr1 ro1 clk rst_n ring_bit1 vddtap 0 sampler_dff

* ---- clk held LOW: the input transmission gate is TRANSPARENT ---------
vclk clk 0 dc 0
vrst rst_n 0 dc vdd_val

* ---- charge integrators: ring and digitizer, separately ---------------
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fqtap qtap 0 vtap 1
cqtap qtap 0 1n
rqtap qtap 0 1e12

* ---- measurement probe -- the RAW ring node ---------------------------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val

.ic v(n11)=0
.ic v(q1)=0
.ic v(qtap)=0
