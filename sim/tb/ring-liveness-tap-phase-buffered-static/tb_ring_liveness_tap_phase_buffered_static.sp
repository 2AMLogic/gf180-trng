* ring-liveness-tap-phase-buffered-static -- VARIANT 6 of issue #76's
* phase-cost experiment: sim/tb/ring-liveness-tap-phase-buffered/ with clk held
* on the HIGH rail instead of running. The buffered pair's static reference.
*
* Why this deck exists
* --------------------
* sim/characterization-ring-buffer-mitigation.md (#75) makes the point this
* deck answers to: inserting a buffer changes TWO things about the ring at
* once -- it isolates the ring node, and it lightens the load on it. A ratio
* taken between a buffered variant and an UNbuffered control therefore spans
* two changes and attributes neither.
*
* So the clk-locked question is asked inside each topology, against that
* topology's own static reference, with exactly one change between numerator
* and denominator (clk toggles / clk does not):
*
*   unbuffered:  ring-liveness-tap-phase-clocked  / ring-liveness-tap-phase-clk-high
*   buffered:    ring-liveness-tap-phase-buffered / THIS DECK
*
* That is #51's variant-3-against-variant-2 discipline, applied twice.
*
* clk sits on the HIGH rail here, matching sim/tb/ring-liveness-tap-phase-
* clk-high/ so the two pairs use the same rail as their reference. The LOW
* rail was not run for the buffered topology; what the two rails do to the
* ring is measured in the unbuffered pair (clk-high against clk-low) and the
* buffered clocked deck's own per-block periods show its two levels directly.
*
* Everything else -- the ring, the injected noise density, the window
* geometry, the print step, the corner, the buffer, the digitizer -- is
* identical to sim/tb/ring-liveness-tap-phase-buffered/. clk and rst_n are DC
* sources, so this deck contains no edge anywhere after start-up.

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

* ---- the shipped per-ring output buffer (design/sampler_core.spice's
* ---- `ro_buf`, the cell PR #82 adopted), on its own supply ammeter -----
vb1 vsup vddb1 dc 0
xbuf ro1 ro1b vddb1 0 ro_buf

* ---- the shipped DR-0016 digitizer, unmodified, on the BUFFER output --
xsr1 ro1b clk rst_n ring_bit1 vsup 0 sampler_dff

* ---- clk parked on the HIGH rail: master transmission gate OFF ---------
vclk clk 0 dc vdd_val
vrst rst_n 0 dc vdd_val

* ---- charge integrator: q1 is the ring's accumulated supply charge ----
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12

* ---- measurement probe ------------------------------------------------
bx1 x1 0 v = v(ro1) - 0.5*vdd_val

.ic v(n11)=0
.ic v(q1)=0
