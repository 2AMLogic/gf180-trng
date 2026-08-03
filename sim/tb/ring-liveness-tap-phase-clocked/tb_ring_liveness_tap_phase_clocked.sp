* ring-liveness-tap-phase-clocked -- THE MEASUREMENT of issue #76: the
* DR-0016 per-ring liveness digitizer attached to the RAW ring node with clk
* RUNNING, against the same digitizer with clk held on a rail.
*
* See sim/tb/ring-liveness-tap-phase-shut/'s deck header for the whole
* experiment (issue #76) and the variant list. In one line: this deck is
* sim/tb/ring-liveness-tap-phase-shut/ and sim/tb/ring-liveness-tap-phase-open/
* with exactly one thing changed -- the clock switches instead of sitting at
* one of its two rails -- which is the same one-change-per-variant discipline
* issue #51 used to attribute its 28.6x to the neighbour's switching rather
* than to the neighbour's load.
*
* What THIS deck isolates, and why the mechanism is not the same one #51 found
* --------------------------------------------------------------------------
* Issue #51's mechanism was charge injected backwards into the ring node
* through the gate-drain/gate-source capacitance of a gate whose inputs a
* neighbouring ring was walking. The digitizer's mechanism is different in
* kind, and this deck is built to expose it rather than to assume it:
*
*   - `d` on a sampler_dff is NOT a gate. It is one source/drain terminal of
*     the input transmission gate (XMtdp/XMtdn in design/sampler_core.spice),
*     whose other terminal is the master latch node `m` and whose gates are
*     clk and clkb.
*   - When clk is LOW that gate is transparent, and the ring node drives the
*     master inverter's 0.88 um of gate directly.
*   - When clk is HIGH it is opaque, and the ring node sees only junction and
*     overlap capacitance.
*
* So a running clk does not inject a rare impulse into the ring: it MODULATES
* the ring's own load between two values, at the clock rate, with a 50 % duty
* cycle. The two static variants measure the ring's period at each of those
* two loads; this deck measures what happens when the load alternates between
* them.
*
* The clock rate
* --------------
* tclk = 1 us (1 MHz). DR-0012 makes the sample clock a fixed EXTERNAL input,
* and DR-0003's ratified raw-rate row is "> 1 Mbps sustained at the raw tap",
* so 1 MHz is the slowest clock the shipped block is specified to run at --
* i.e. the rate at which a clk-correlated disturbance arrives LEAST often, and
* therefore the most favourable rate to the digitizer that the specification
* permits. Deliberately chosen for that reason. Note the sign of the argument:
* the mechanism's amplitude (how far the ring's period moves between the two
* loads) does not depend on the clock rate at all, so a faster clock does not
* make the disturbance bigger -- it makes it more frequent. What 1 MHz buys is
* that the effect measured here cannot be dismissed as an artefact of an
* unrealistically fast clock, the way sim/tb/ring-liveness-tap-power/'s own
* 100 MHz measurement clock honestly could be.
*
* The 512-period measurement window spans ~1.6 clk cycles at this rate, so
* roughly half the sampled periods fall in each clock phase. The exact split
* is reported: period_b00..period_b15 bin the run into sixteen 48-period bins,
* each ~1/6 of a clock half-period, so the clk-locked modulation is directly
* visible in the record as a square wave across the bin series rather than
* only as an aggregate sigma.
*
* Everything else is deliberately identical to
* sim/tb/ring-liveness-tap-phase-shut/, device for device and parameter for
* parameter. The ONE difference is that vclk is a pulse source instead of a dc
* source.

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

* ---- clk RUNNING at DR-0003's ratified 1 Mbps raw rate ----------------
vclk clk 0 dc 0 pulse(0 'vdd_val' 'tclk0' 'tclk_tr' 'tclk_tr' 'tclk/2-tclk_tr' 'tclk')
vrst rst_n 0 dc vdd_val

* ---- charge integrators: ring and digitizer, separately ---------------
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fqtap qtap 0 vtap 1
cqtap qtap 0 1n
rqtap qtap 0 1e12

* ---- measurement probes -----------------------------------------------
* bx1: the RAW ring node, exactly as every deck in this family probes it.
* bclkp: a measurement-only probe carrying the clock period as a voltage, so
* the record states the rate that produced it rather than leaving it in the
* manifest only (the ngspice control language cannot read a .param directly).
bx1 x1 0 v = v(ro1) - 0.5*vdd_val
bclkp clkp 0 v = tclk

.ic v(n11)=0
.ic v(q1)=0
.ic v(qtap)=0
