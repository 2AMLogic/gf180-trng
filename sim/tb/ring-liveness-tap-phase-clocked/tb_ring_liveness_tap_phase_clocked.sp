* ring-liveness-tap-phase-clocked -- VARIANT 4 of issue #76's phase-cost
* experiment on the DR-0016 per-ring liveness digitizer: the digitizer's d
* input DIRECTLY on the ring node, with clk actually running.
*
* This is the arrangement design/sampler_core.spice shipped from #71 up to
* PR #82, and the one issue #76 was filed against. Since #82 the shipped
* netlist interposes a per-ring output buffer (xb1: rn1 -> ro1) and the
* digitizer taps the buffer output -- that topology is
* sim/tb/ring-liveness-tap-phase-buffered/. This deck is kept and measured
* because #82 adopted the buffer on COMBINER-path evidence (#75) and never
* measured the digitizer path, so without this row there is no "before" for
* the "after" to be a reduction of.
*
* The family, the question, the ring, the window geometry, the injected noise
* density and the corner are all documented once in
* sim/tb/ring-liveness-tap-phase-clk-high/tb_ring_liveness_tap_phase_clk_high.sp.
* This deck is that deck with clk driven by a pulse source instead of a DC
* rail, and nothing else changed.
*
* What THIS deck isolates
* -----------------------
* Everything the two static variants deliberately leave out: clk edges, and
* the alternation between the two static states they each hold. A
* positive-edge-triggered sampler_dff's master transmission gate conducts
* while clk is LOW and is open while clk is HIGH, so a running clk walks the
* ring's load back and forth between
*
*   sim/tb/ring-liveness-tap-phase-clk-low/   (master transparent, ro1 driving
*                                              the master latch inverter every
*                                              ring cycle)
* and
*   sim/tb/ring-liveness-tap-phase-clk-high/  (master open, ro1 seeing only
*                                              junction and overlap load)
*
* once per clk period, in lockstep with an external pin. That is the property
* issue #76 exists to put a number on: a disturbance locked to clk is coherent
* with the sampling instant by construction, where an incommensurate
* ring-to-ring beat is not.
*
* clk rate
* --------
* tclk_per (tb.json params) is 1.0007 us, i.e. ~1 MHz -- DR-0003's ratified
* raw-rate row is "> 1 Mbps sustained at the raw tap", and DR-0012 makes clk a
* fixed external pin with no divider, so ~1 MHz is the shipped operating
* point rather than a chosen stimulus. It is deliberately NOT a round number:
* see the breakpoint note below.
*
* Why the clk timings are all off the 10 ps grid
* ---------------------------------------------
* ngspice's trnoise() sources place a hard breakpoint every NT = vn_dt = 10 ps.
* With this deck's tap attached, a PULSE source breakpoint that lands exactly
* on one of those noise breakpoints makes the transient collapse --
* "Timestep too small; timestep = 1.25e-24" -- at that instant, every time,
* reproducibly, on ngspice-46. Moving the clk edges off the 10 ps grid
* (tclk_del = 5.003 ns, tclk_tr = 0.203 ns, so every edge time is a
* non-multiple of 10 ps) makes the same deck run to completion unchanged in
* every other respect. The offsets are ~0.3 % of an edge and ~0.0005 % of a clk
* period; nothing measured here resolves them.
*
* This is a solver limit, recorded so the next person does not rediscover it,
* and it is the reason tstop is 2.900301 us rather than a round 2.9 us.

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

* ---- DR-0012's fixed external sample clock, running --------------------
vclk clk 0 dc 0 pulse(0 'vdd_val' tclk_del tclk_tr tclk_tr 'tclk_per/2 - tclk_tr' tclk_per)
vrst rst_n 0 dc vdd_val

* ---- charge integrator: q1 is the ring's accumulated supply charge ----
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12

* ---- measurement probe ------------------------------------------------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val

.ic v(n11)=0
.ic v(q1)=0
