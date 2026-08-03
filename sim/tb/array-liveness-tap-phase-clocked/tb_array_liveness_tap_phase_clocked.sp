* array-liveness-tap-phase-clocked -- issue #87: what does the DR-0016
* liveness digitizer cost the SHIPPED array in phase, where each ro_buf
* output drives the XOR combiner as well as its own digitizer?
*
* The question this deck exists for
* --------------------------------
* Issue #76 (sim/characterization-liveness-tap-phase-cost.md, PR #85)
* measured the clk-locked phase disturbance on an ISOLATED ring: 541x on a
* raw ring node, 19.9x behind a DR-0018 ro_buf. It recorded that 19.9x as an
* UPPER BOUND rather than as the shipped number, and said why: its buffered
* deck's ro_buf output drives ONE consumer (the digitizer), where the
* shipped design/ro_array_core.spice has each ro_buf output driving the XOR
* combiner's input AS WELL --
*
*     xb1 rn1 ro1 vdd vss ro_buf
*     xa1 ro1 ro2 xo  vdd vss xor2      <- the second consumer
*     xsr1 ro1 clk rst_n ring_bit1 ...  <- the digitizer
*
* -- so the clk-modulated part of that node's capacitance is a smaller
* fraction of its total than it is in #76's deck, and the residual should be
* smaller. That argument is structural. It has not been measured. THIS deck
* measures it.
*
* What differs from #76's decks, and what does not
* ------------------------------------------------
* Same corner (tt/27 C/3.30 V), same injected noise density (1e-16 V^2/Hz,
* one trnoise() source in series with every stage input), same clk timing
* (tclk_per = 1.0007 us, DR-0003's ratified raw-rate floor with DR-0012's
* fixed external pin), same off-the-10-ps-grid clk edge placement, same
* sigma estimator, and the same "one change between numerator and
* denominator" discipline #51 and #76 both used: this deck's control is
* sim/tb/array-liveness-tap-phase-static/, which is THIS deck with clk
* parked on the HIGH rail and nothing else touched.
*
* What differs is the topology, deliberately, because that is the whole
* question: this is the SHIPPED design/sampler_core.spice arrangement --
* both 11-stage rings, both per-ring buffers, the XOR combiner, and all four
* sampler_dff instances (xsb on xo, xsv on vdd, xsr1/xsr2 on the two buffer
* outputs) -- rather than #76's one 5-stage ring with one consumer.
*
* Window geometry: matched to #76 in TIME, not in ring-period count
* -----------------------------------------------------------------
* #76's family opened its window 256 ring periods after start-up and spanned
* 512 ring periods on a 5-stage ring whose period is ~2.86 ns: 0.73 us of
* settling and a 1.46 us window, which is 1.46 clk periods.
*
* An 11-stage ring's period is ~7.1 ns, 2.5x longer. Reproducing 256/512
* ring periods would need ~5.5 us of transient noise on a circuit that costs
* ~21 CPU-minutes per simulated microsecond here. This family therefore
* opens its window 128 ring periods after start-up and spans 256 ring
* periods: 0.91 us of settling and a 1.82 us window, which is 1.82 clk
* periods. Both numbers are LONGER in absolute time -- and cover MORE clk
* periods -- than #76's, which is what the measurement actually depends on,
* because the disturbance is locked to clk rather than to the ring.
*
* The estimator is otherwise #76's, with the lag ladder truncated at 64
* (a quarter of the window) where #76's was truncated at 128 (a quarter of
* its window).
*
* Why the rings are restated here rather than instantiated
* --------------------------------------------------------
* The trnoise() sources go in series with every stage input, which cannot be
* done from outside a ro_ring11 instance. Both rings are therefore written
* out stage by stage -- but every stage is an instance of ro_nand2 /
* ro_stage out of design/sampler_core.spice, this tb.json's own design
* netlist, with ro_ring11's own wiring and its own wstv (0.220u for ring 1,
* 0.240u for ring 2). Everything downstream of the ring nodes -- both
* ro_buf, the xor2, and all four sampler_dff -- is instantiated from that
* netlist unmodified and wired exactly as ro_array_core / sampler_core wire
* it. This is the same compromise sim/tb/ro-array-coupling-xor-driven/ makes
* for the same reason.
*
* Supplies
* --------
* vr1 / vr2 meter each ring separately so ring 1's charge integrator sees
* ring 1's current alone, exactly as the control deck and #51's ladder do.
* Everything on the block side -- both buffers, the combiner and all four
* digitizers -- runs off ONE metered node vdd, which is how sampler_core
* wires them (they share the block supply pin; only the rings have their own
* vddr1/vddr2). All three branches are zero-impedance taps off one IDEAL
* vsup, so no supply-network coupling path exists in this deck at all; see
* the caveat in tb.json.

vsup vsup 0 dc vdd_val
ven1 en1 0 dc vdd_val
ven2 en2 0 dc vdd_val

* ---- per-ring supply pins (metered) and the block supply pin -----------
vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vd  vsup vdd   dc 0

* ---- ring 1: ro_ring11 (wstv = 0.220u), one trnoise source per stage ---
xg1   a1_0  en1   n1_1  vddr1 0 ro_nand2 wstv=0.220u lstv=2u cld=0.5f
x1_1  a1_1  n1_2  vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x1_2  a1_2  n1_3  vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x1_3  a1_3  n1_4  vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x1_4  a1_4  n1_5  vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x1_5  a1_5  n1_6  vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x1_6  a1_6  n1_7  vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x1_7  a1_7  n1_8  vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x1_8  a1_8  n1_9  vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x1_9  a1_9  n1_10 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x1_10 a1_10 rn1   vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
vn1_0  rn1   a1_0  dc 0 trnoise( vn_rms vn_dt 0 0)
vn1_1  n1_1  a1_1  dc 0 trnoise( vn_rms vn_dt 0 0)
vn1_2  n1_2  a1_2  dc 0 trnoise( vn_rms vn_dt 0 0)
vn1_3  n1_3  a1_3  dc 0 trnoise( vn_rms vn_dt 0 0)
vn1_4  n1_4  a1_4  dc 0 trnoise( vn_rms vn_dt 0 0)
vn1_5  n1_5  a1_5  dc 0 trnoise( vn_rms vn_dt 0 0)
vn1_6  n1_6  a1_6  dc 0 trnoise( vn_rms vn_dt 0 0)
vn1_7  n1_7  a1_7  dc 0 trnoise( vn_rms vn_dt 0 0)
vn1_8  n1_8  a1_8  dc 0 trnoise( vn_rms vn_dt 0 0)
vn1_9  n1_9  a1_9  dc 0 trnoise( vn_rms vn_dt 0 0)
vn1_10 n1_10 a1_10 dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- ring 2: ro_ring11 (wstv = 0.240u), one trnoise source per stage ---
xg2   a2_0  en2   n2_1  vddr2 0 ro_nand2 wstv=0.240u lstv=2u cld=0.5f
x2_1  a2_1  n2_2  vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x2_2  a2_2  n2_3  vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x2_3  a2_3  n2_4  vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x2_4  a2_4  n2_5  vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x2_5  a2_5  n2_6  vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x2_6  a2_6  n2_7  vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x2_7  a2_7  n2_8  vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x2_8  a2_8  n2_9  vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x2_9  a2_9  n2_10 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x2_10 a2_10 rn2   vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
vn2_0  rn2   a2_0  dc 0 trnoise( vn_rms vn_dt 0 0)
vn2_1  n2_1  a2_1  dc 0 trnoise( vn_rms vn_dt 0 0)
vn2_2  n2_2  a2_2  dc 0 trnoise( vn_rms vn_dt 0 0)
vn2_3  n2_3  a2_3  dc 0 trnoise( vn_rms vn_dt 0 0)
vn2_4  n2_4  a2_4  dc 0 trnoise( vn_rms vn_dt 0 0)
vn2_5  n2_5  a2_5  dc 0 trnoise( vn_rms vn_dt 0 0)
vn2_6  n2_6  a2_6  dc 0 trnoise( vn_rms vn_dt 0 0)
vn2_7  n2_7  a2_7  dc 0 trnoise( vn_rms vn_dt 0 0)
vn2_8  n2_8  a2_8  dc 0 trnoise( vn_rms vn_dt 0 0)
vn2_9  n2_9  a2_9  dc 0 trnoise( vn_rms vn_dt 0 0)
vn2_10 n2_10 a2_10 dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- the shipped array's own buffers and combiner (ro_array_core) ------
xb1 rn1 ro1 vdd 0 ro_buf
xb2 rn2 ro2 vdd 0 ro_buf
xa1 ro1 ro2 xo  vdd 0 xor2

* ---- the shipped sampler's four digitizers, unmodified ----------------
* xsr1 / xsr2 are the DR-0016 per-ring liveness digitizers; xsb is the
* DR-0001 raw tap on the combiner output; xsv is the raw-valid flag, whose
* d input is tied to vdd exactly as sampler_core ties it.
xsb  xo  clk rst_n raw_bit   vdd 0 sampler_dff
xsv  vdd clk rst_n raw_valid vdd 0 sampler_dff
xsr1 ro1 clk rst_n ring_bit1 vdd 0 sampler_dff
xsr2 ro2 clk rst_n ring_bit2 vdd 0 sampler_dff

* ---- DR-0012's fixed external sample clock, RUNNING -------------------
vclk clk 0 dc 0 pulse(0 'vdd_val' tclk_del tclk_tr tclk_tr 'tclk_per/2 - tclk_tr' tclk_per)
vrst rst_n 0 dc vdd_val

* ---- charge integrators: q1 / q2 are each ring's accumulated charge ----
fq1 q1 0 vr1 1
cq1 q1 0 1n
rq1 q1 0 1e12
fq2 q2 0 vr2 1
cq2 q2 0 1n
rq2 q2 0 1e12

* ---- measurement probes -- the RING nodes, upstream of the buffers -----
bx1 x1 0 v = v(rn1) - 0.5*vdd_val
bx2 x2 0 v = v(rn2) - 0.5*vdd_val

.ic v(n1_1)=0
.ic v(n2_1)=0
.ic v(q1)=0
.ic v(q2)=0
