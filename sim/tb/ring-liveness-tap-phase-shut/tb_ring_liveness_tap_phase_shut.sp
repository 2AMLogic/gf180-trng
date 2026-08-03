* ring-liveness-tap-phase-shut -- CONTROL A of issue #76's six-variant
* experiment: what does the DR-0016 per-ring liveness digitizer cost the ring
* it observes, in PHASE rather than in power?
*
* The question (issue #76)
* -----------------------
* sim/characterization-array-ring-coupling.md (issue #51 / PR #67) measured
* that a ring node driving the input of a cell whose internal nodes something
* else is driving shows sigma_1 28.6x higher than the same ring with that
* neighbour held on a rail. The load was innocent (1.06x); the neighbour's
* SWITCHING was the mechanism.
*
* DR-0016's per-ring liveness digitizers (xsr1/xsr2 in sampler_core.sch,
* shipped by #65) are structurally the same arrangement a second time: each
* ring's observation node drives a sampler_dff `d` input, which is one
* terminal of a transmission gate whose OTHER terminal is the master latch
* node and whose gate is driven by clk. sim/tb/ring-liveness-tap-power/
* measured what those digitizers cost the rings in POWER. Nothing measured
* what they cost them in phase. This family does.
*
* Also note what the fix path already is. Since #82 / DR-0018 the shipped
* ro_array_core re-drives its exported ro1/ro2 pins from a per-ring ro_buf, so
* what sampler_core.sch's xsr1/xsr2 digitize TODAY is a buffer output, not a
* ring node. The unbuffered arrangement issue #76 indicts is the one the block
* shipped between #65 and #82, and it is still the arrangement any consumer
* that taps a ring node directly would recreate. This family measures both, so
* the buffer's effect on this path is a number rather than an inference.
*
* The six variants, all at tt/27 C/3.30 V, all one change apart
* ------------------------------------------------------------
*   0. sim/tb/ro-ring5-starved-jitter-long/ -- the same ring, NOTHING
*      attached. Issue #51's own control, already on file
*      (sim/records/2026-08-01-ro-ring5-starved-jitter-long-02.md,
*      T0 = 2.5635 ns, sigma_1 = 0.641 ps). This is the "digitizers absent"
*      row issue #76's first acceptance bullet asks for; it is cited, not
*      re-run.
*   1. THIS DECK (-shut) -- digitizer attached to the RAW ring node, clk held
*      HIGH so the input transmission gate is OPAQUE. The digitizer's static
*      load at one of its two fixed operating points, with nothing switching.
*   2. sim/tb/ring-liveness-tap-phase-open/ -- same, clk held LOW so the gate
*      is TRANSPARENT. The digitizer's static load at the OTHER fixed
*      operating point. Issue #51 measured only one of its gate's two static
*      points and said so; this family measures both, because the difference
*      between them is precisely the quantity the clocked variant modulates.
*   3. sim/tb/ring-liveness-tap-phase-clocked/ -- same, clk RUNNING at
*      DR-0003's ratified 1 Mbps raw rate. One change from variants 1 and 2:
*      the clock switches.
*   4. sim/tb/ring-liveness-tap-phase-buffered-clocked/ -- the digitizer driven
*      from an ro_buf output instead of the raw ring node (the DR-0018
*      arrangement the shipped design has carried since #82), clk running. One
*      change from variant 3: where the digitizer taps.
*   5. sim/tb/ring-liveness-tap-phase-buffered-shut/ -- variant 4's matched
*      quiet control, clk held HIGH.
*   6. sim/tb/ring-liveness-tap-phase-buffered-open/ -- variant 4's matched
*      quiet control at the clock's OTHER static value, clk held LOW. Variants
*      5 and 6 stand to variant 4 exactly as variants 1 and 2 stand to variant
*      3, so the buffered and unbuffered arrangements are judged by the same
*      one-change ratio and by the same static-pair prediction.
*
* What THIS deck isolates
* -----------------------
* The digitizer's static load with its input transmission gate shut. With
* clk = vdd the pfet pass device (gate = clk) is off and the nfet pass device
* (gate = clkb = 0) is off, so the ring node sees only the pass devices'
* junction and gate-overlap capacitance -- not the master latch behind them.
* This is the LIGHT of the digitizer's two static loads, and it is the
* matched quiet control the clocked variant's sigma is read against.
*
* Everything else is deliberately identical to
* sim/tb/ro-ring5-starved-jitter-long/ and to issue #51's variant decks,
* device for device and parameter for parameter: a ro_nand2 enable stage plus
* four ro_stage at wstv = 0.220 um, lstv = 2 um, cld = 0.5 f, one trnoise()
* source in series with every stage input at the same fixed injected density
*
*     S_inj = 2 * vn_rms^2 * vn_dt = 1e-16 V^2/Hz  (1e-08 V/sqrt(Hz))
*
* the same charge integrator on the same separate ring supply pin, the same
* bx1 measurement probe, the same .ic start-up, and the same measurement
* window: opened 256 periods after start-up, spanning 512 periods, with the
* 16-period start-up window reproduced inside the same run
* (sigma_startup16_*).
*
* The digitizer is the SHIPPED cell, unmodified: `sampler_dff` out of
* design/sampler_core.spice, the same subcircuit sampler_core.sch
* instantiates as xsr1/xsr2. It is supplied from its own metered pin
* (vddtap), never from the ring's vddr1, exactly as DR-0016's own power
* accounting separates them -- so the ring's supply pin stays a pure per-ring
* current signature and the digitizer's own cost is a second, independent
* number.
*
* rst_n is held HIGH from t = 0 (dc, no edge). DR-0014's reset is an
* initialisation input, not an operating-mode one, and a reset EDGE inside a
* transient-noise run is an extra switching event this experiment has no use
* for. The latch resolves out of the operating point; nothing downstream of
* the digitizer is measured here.
*
* Start-up: the enable is held HIGH from t = 0 and the ring is kicked out of
* its unstable DC solution by a .ic, as in every transient-noise ring deck in
* this repository (an enable EDGE does not converge with trnoise() sources
* active in ngspice-42/46 -- a solver limit recorded in those testbenches).
*
* Only v(x1), v(q1), v(qtap) and v(vsup) are read by any measurement; tb.json
* saves that set and nothing else, because at 1 ps print step over 3 us the
* full node set is gigabytes of stored waveform per seeded run.

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

* ---- clk held HIGH: the input transmission gate is OPAQUE -------------
vclk clk 0 dc vdd_val
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
