* ring-liveness-tap-phase-buffered -- VARIANT 5 of issue #76's phase-cost
* experiment on the DR-0016 per-ring liveness digitizer: variant 4 with the
* SHIPPED per-ring output buffer between the ring node and the digitizer.
*
* The family, the question, the ring, the window geometry, the injected noise
* density, the corner and the clk timing (including why every clk edge is off
* the 10 ps trnoise breakpoint grid) are documented in
* sim/tb/ring-liveness-tap-phase-clk-high/tb_ring_liveness_tap_phase_clk_high.sp
* and sim/tb/ring-liveness-tap-phase-clocked/tb_ring_liveness_tap_phase_clocked.sp.
* This deck is the clocked deck plus exactly one element: xbuf.
*
* What THIS deck isolates
* -----------------------
* Whether the disturbance the clocked deck measures is removed by driving the
* digitizer from a per-ring buffer output instead of from the ring node --
* issue #76's last acceptance item.
*
* Since PR #82 that is not a hypothetical. design/sampler_core.spice now reads
*
*     xr1 en1 rn1 vddr1 vss ro_ring11 ...
*     xb1 rn1 ro1 vdd  vss ro_buf
*     xsr1 ro1 clk rst_n ring_bit1 vdd vss sampler_dff
*
* -- the ring's own node is rn1, and the DR-0016 digitizer taps ro1, which is
* the BUFFER's output. So variant 4 (this deck without xbuf) is the topology
* issue #76 was filed against and the block shipped up to #82, and THIS deck is
* the topology the block ships now. #82 adopted the buffer on the strength of
* the COMBINER-path measurement (#75, sim/characterization-ring-buffer-
* mitigation.md); nothing measured what it did for the digitizer path. That is
* what this variant closes.
*
* xbuf is the shipped cell itself -- `ro_buf` out of design/sampler_core.spice,
* the tb.json's own design netlist -- instantiated, not restated, so this deck
* cannot drift from the cell it claims to measure.
*
* Note that the buffer does not make the tap free: it moves the tap's load off
* the ring node and onto the buffer's output, and it puts its OWN input gate
* (0.66 um of gate width) on the ring node in place of the tap's transmission
* gate. What it removes is the *clk-dependence* of that load -- an inverter's
* input capacitance does not change when clk moves, because the inverter's
* input stage has no clk in it.
*
* The buffer is supplied through its own zero-volt ammeter source (vb1) off the
* same ideal vsup, exactly as sim/tb/ro-array-coupling-xor-driven-buffered/
* does, so the ring's charge integrator keeps seeing the RING's current alone
* and i_ring_a/p_active_w stay comparable expression for expression to the
* control's. In the shipped block the buffers likewise run off the block supply
* vdd, never off a ring's vddr.

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
