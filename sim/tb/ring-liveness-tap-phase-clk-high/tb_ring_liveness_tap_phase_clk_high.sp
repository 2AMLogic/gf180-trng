* ring-liveness-tap-phase-clk-high -- VARIANT 2 of the phase-cost experiment
* for issue #76: what the DR-0016 per-ring liveness digitizer costs its ring
* in PHASE, as opposed to in power (which sim/tb/ring-liveness-tap-power/
* already measured).
*
* The question (issue #76)
* -----------------------
* sim/characterization-array-ring-coupling.md (#51) indicted one arrangement:
* a ring node sharing an input stage with something else that is switching.
* At tt/27 C/3.30 V that arrangement put sigma_1 at 28.6x the standalone
* ring's, against 1.06x for the same gate load with the neighbour on a rail --
* so the load was innocent and the neighbour's SWITCHING was the mechanism.
*
* design/sampler_core.spice contains that shape a second time. xsr1/xsr2 (the
* DR-0016 digitizers, shipped by #71) put ro1/ro2 on a sampler_dff `d` input,
* which in that cell is the channel terminal of a transmission gate
*
*     XMtdp d clk  m vdd pfet_03v3 W=0.44u
*     XMtdn d clkb m vss nfet_03v3 W=0.22u
*
* whose GATES are driven by clk / clkb and whose far terminal `m` is the
* master latch node. clk is an external, attacker-rate pin (DR-0012).
*
* What PR #82 changed underneath the question
* -------------------------------------------
* While this family was being built, PR #82 (issue #75, DR-0018) adopted a
* per-ring output buffer, so design/sampler_core.spice now reads
*
*     xr1 en1 rn1 vddr1 vss ro_ring11 ...
*     xb1 rn1 ro1 vdd  vss ro_buf
*     xsr1 ro1 clk rst_n ring_bit1 vdd vss sampler_dff
*
* -- the ring's own node is rn1, and the digitizer taps ro1, the BUFFER's
* output. Variants 2-4 below are therefore the topology the block shipped from
* #71 up to #82 and the one issue #76 was filed against; variants 5-6 are the
* topology it ships now. Both are measured, because #82 adopted the buffer on
* the COMBINER-path evidence in sim/characterization-ring-buffer-mitigation.md
* and nothing measured what it did for the DIGITIZER path.
*
* The variant family (one change each, one corner, one window geometry)
* --------------------------------------------------------------------
*   1. sim/tb/ro-ring5-starved-jitter-long/       one ring, nothing attached
*                                                 (the CONTROL, #51's own).
*   2. THIS DECK                                  + the digitizer ON THE RING
*                                                 NODE, clk held HIGH: the
*                                                 master transmission gate is
*                                                 OFF, so the ring node sees
*                                                 only the tap's off-state
*                                                 junction and overlap
*                                                 capacitance. The LIGHTEST
*                                                 load the tap can present.
*   3. sim/tb/ring-liveness-tap-phase-clk-low/    + the same, clk held LOW: the
*                                                 master transmission gate is
*                                                 ON, so ro1 drives the master
*                                                 latch's input inverter
*                                                 continuously. The HEAVIEST
*                                                 load the tap can present.
*   4. sim/tb/ring-liveness-tap-phase-clocked/    + the same, clk running at
*                                                 DR-0003's raw-tap rate. The
*                                                 PRE-#82 shipped arrangement,
*                                                 which alternates between 2
*                                                 and 3 every half clk period.
*   5. sim/tb/ring-liveness-tap-phase-buffered/   variant 4 with the shipped
*                                                 ro_buf between the ring node
*                                                 and the tap. The POST-#82
*                                                 shipped arrangement.
*   6. sim/tb/ring-liveness-tap-phase-buffered-static/
*                                                 variant 5 with clk held HIGH:
*                                                 the buffered pair's own
*                                                 static reference.
*
* The clk question is asked INSIDE each topology, against that topology's own
* static reference (4 against 2, and 5 against 6), so exactly one thing
* differs between numerator and denominator -- whether clk toggles. Reading a
* buffered deck against an UNbuffered reference would span two changes at
* once, because a buffer both isolates the ring node and lightens it; that is
* the pairing argument sim/characterization-ring-buffer-mitigation.md makes
* for its own decks.
*
* What THIS deck isolates
* -----------------------
* One of the two static endpoints the clocked tap swings between. clk = vdd
* holds the master transmission gate off, which is the state the digitizer sits
* in for half of every clk period. Read against the control it says what the
* tap's *off-state* load alone does to the ring; read against variant 3 it says
* how much of the tap's cost is the transmission gate being open rather than
* shut. Neither endpoint is a "the tap is innocent" result on its own -- the
* part spends half its time in each, and variant 4 is what measures that.
*
* It is also the DENOMINATOR of the pre-#82 within-topology ratio: variant 4 is
* this deck with clk driven by a pulse source instead of a DC rail, and nothing
* else changed, so sigma_1(4)/sigma_1(2) isolates the toggling of clk from
* everything the tap's presence does statically.
*
* clk is a DC source here, not a pulse: this deck contains no edge anywhere
* after start-up, which is exactly what makes it the static reference.
*
* Ring 1 is device-for-device identical to sim/tb/ro-ring5-starved-jitter-long/
* (the control): a ro_nand2 enable stage plus four ro_stage at wstv = 0.220 um,
* lstv = 2 um, cld = 0.5 f, one trnoise() source in series with every stage
* input at the same fixed injected density
*
*     S_inj = 2 * vn_rms^2 * vn_dt = 1e-16 V^2/Hz  (1e-08 V/sqrt(Hz))
*
* the same charge integrator on the same separate ring supply pin, the same
* bx1 probe, the same .ic start-up, and the same measurement window: opened
* 256 periods after start-up, spanning 512 periods, with the 16-period
* start-up window reproduced inside the same run (sigma_startup16_*).
*
* Why a 5-stage ring when the shipped array's rings have 11 stages
* ---------------------------------------------------------------
* Comparability with #51, which is what issue #76 asks for: every number in
* sim/characterization-array-ring-coupling.md is on this exact 5-stage ring at
* this exact corner and window, so a tap variant built on the same ring drops
* straight into that ladder. The direction of the approximation is the safe
* one as well -- the tap loads exactly ONE ring node either way, and one node
* is a larger fraction of a 5-stage ring's total delay than of an 11-stage
* ring's, so a fractional period/phase effect measured here OVER-states what
* the shipped 11-stage ring would show, by roughly 11/5.
*
* The digitizer is design/sampler_core.spice's sampler_dff, instantiated
* unmodified and exactly as sampler_core.sch instantiates xsr1. It is supplied
* from vsup directly rather than through the ring's own sense source, so its
* switching current stays out of the ring's charge integrator; the tap's own
* power is not re-measured here because sim/tb/ring-liveness-tap-power/
* already measures it across three PVT points.
*
* rst_n is held at vdd for the whole run (no edge). The digitizer's reset
* behaviour is DR-0014's and is measured by sim/tb/sampler-dff-reset-clocked/;
* what this deck needs is a digitizer that is out of reset, and an rst_n edge
* would add a disturbance that is not the one under study.
*
* Start-up: the enable is held HIGH from t = 0 and the ring is kicked out of
* its unstable DC solution by a .ic, as in every transient-noise ring deck in
* this repository (an enable EDGE does not converge with trnoise() sources
* active in ngspice-42/46 -- a solver limit recorded in those testbenches).
*
* Only v(x1), v(q1) and v(vsup) are read by any measurement; tb.json saves
* that set and nothing else, because at 1 ps print step over microseconds the
* full node set is gigabytes of stored waveform per seeded run.

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

* ---- clk held HIGH: master transmission gate OFF ----------------------
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
