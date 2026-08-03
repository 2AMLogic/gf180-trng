* sampler-bit-bias-clocked-generic -- issue #86, and the CANONICAL deck of
* this family. Every other deck in the family is this file with exactly one
* thing changed, and each says which; the experiment, the circuit, the window
* geometry and the method notes are documented here, once.
*
* The question (issue #86)
* -----------------------
* #76 / DR-0016 amendment A2 (sim/characterization-liveness-tap-phase-cost.md)
* measured that the DR-0016 per-ring liveness digitizer frequency-modulates
* the ring it observes, in lockstep with `clk`: 25.6 % apart on the raw ring
* node (541x the same deck's sigma_1 with clk parked), and, on the shipped
* DR-0018-buffered tap, a 19.9x clk-locked residual that is deterministic
* (0.12 % seed spread, L^0.96 accumulation).
*
* That is a measurement about PHASE. #76 declined to make a bit-level claim
* from it, which is the right call, and #86 is where that claim has to be
* earned: DR-0007 §1's independence argument rests on the rings being free-
* running with no phase relationship to anything, and what #76 measured is a
* ring whose instantaneous frequency is an exact function of the sampling
* clock's own waveform. Whether that moves the SAMPLED BIT's statistics is
* what this family measures.
*
* The mechanism the experiment has to be able to see
* --------------------------------------------------
* The modulation repeats exactly once per clk period, so to first order the
* deterministic phase advance between successive sampling instants is a
* constant -- exactly as it would be for a free-running ring, just a different
* constant. What is NOT constant is the phase at which each clk EDGE lands
* inside the ring's own cycle, and the phase kick that edge delivers depends
* on where it lands. That makes the sample-to-sample map a circle map rather
* than a pure rotation, and a circle map can lock: if the kick is large enough
* and the phase advance per sample is near an integer number of ring periods,
* the ring's phase at the sampling instant can stop advancing, and the sampled
* bit stops being a fresh draw.
*
* Two things follow, and they set this family's sweep:
*   - the dangerous clk rates are the ones where the per-clk-cycle phase
*     advance is NEAR AN INTEGER number of ring periods (the `-integer` deck),
*     and the informative background is a rate whose fractional part is well
*     away from any low-order rational (this deck, `-generic`);
*   - there are exactly TWO clk edges per clk period whatever the rate, so the
*     deterministic kick per sample is rate-independent while the jitter that
*     would smear it grows with the sample period. Measuring at a FAST clk is
*     therefore the conservative direction, and the DR-0003 floor
*     (`-clk-floor`) is the shipped operating point rather than the worst one.
*
* The DUT: design/sampler_core.spice, with 5-stage rings
* -----------------------------------------------------
* Everything below the noise sources is sampler_core's own wiring, cell for
* cell and connection for connection:
*
*     xr1/xr2  ->  rn1/rn2          the two skewed rings
*     xb1/xb2  ->  ro1/ro2          the DR-0018 per-ring output buffers
*     xa1      ->  xo               the DR-0007 §1 XOR combiner
*     xsb      ->  raw_bit          the DR-0001 RAW TAP -- the bit this
*                                   experiment is about
*     xsr1/xsr2                     the two DR-0016 per-ring liveness
*                                   digitizers, on the BUFFER OUTPUTS, which
*                                   is where PR #82 / DR-0018 put them
*
* Two deliberate departures, both stated rather than absorbed:
*
*   1. The rings are 5-stage, where the shipped ro_ring11 has 11. This is the
*      same choice #51's coupling ladder and #76's phase family made, for the
*      same reason -- the whole comparable body of evidence at this corner and
*      window is on this ring -- and it is the CONSERVATIVE direction here:
*      the digitizer loads exactly one node either way, and one node is a
*      larger share of a 5-stage ring's delay than of an 11-stage ring's, so
*      any modulation measured here over-states the shipped ring's by roughly
*      11/5. The array's top-level wiring is restated here rather than
*      instantiated whole because ngspice cannot insert a series noise source
*      inside a subcircuit, which is this repository's jitter method
*      (sim/tb/ro-array-sanity-jitter/, sim/tb/sampler-array-digitize/).
*      Every DEVICE still comes from design/sampler_core.spice.
*   2. sampler_core's `xsv` (the raw_valid register) is not instantiated. Its
*      only inputs are `clk` and `vdd`, both driven by ideal sources here, so
*      it can couple to nothing this deck measures; leaving it out buys
*      run-time and changes no measured quantity. raw_valid's own contract is
*      sim/tb/sampler-array-digitize/'s subject, not this family's.
*
* The one change that defines the variant
* ---------------------------------------
* `vclkm` -- the source driving the two LIVENESS digitizers' clock pin. In
* this deck it is an independent, identical copy of the raw tap's own clk
* waveform, i.e. the shipped arrangement. In sim/tb/sampler-bit-bias-static-*/
* it is a DC rail at vdd and NOTHING ELSE DIFFERS: same cells, same devices,
* same static load on ro1/ro2, same raw-tap clock, same noise sources in the
* same order (so a given seed draws the same noise realization in both decks
* and the comparison is paired). What changes between the two is exactly the
* thing issue #86 asks about -- whether the clk-locked modulation is present.
*
* Parking the liveness clock HIGH rather than LOW matches #76's own static
* reference for the buffered pair (sim/tb/ring-liveness-tap-phase-buffered-
* static/): clk high puts the digitizer's master transmission gate OFF, the
* lighter of the two endpoints its d input swings between.
*
* Reading the bit
* ---------------
* Each sample is read at a mid-supply crossing of clk's FALLING edge, i.e.
* half a clk period after the rising edge that captured it. sampler_dff is
* positive-edge-triggered (master transmission gate conducts while clk is
* low, slave while clk is high), so by then q has been settled for hundreds
* of ps -- far past this cell's clk-to-Q delay, which
* sim/tb/sampler-dff-setup-hold/ measures. Indexing the read off a CROSSING
* COUNT rather than an absolute time keeps the sample instants exact: the
* index is an integer, where a computed time would be re-formatted through
* ngspice's control-language substitution and lose digits.
*
* The raw VOLTAGE at each sample is what is recorded and thresholded, and the
* worst distance any sample sits from a rail is reported
* (`worst_rail_dev_v`). A reading that is not close to a rail is itself a
* finding -- a metastable capture -- and thresholding it away silently would
* hide exactly that.
*
* Method notes
* ------------
*   - Start-up: en held HIGH from t = 0, each ring kicked out of its unstable
*     DC solution by a .ic on its NAND output, because with trnoise sources
*     active ngspice fails to converge on an enable EDGE (the method
*     sim/tb/ro-array-sanity-jitter/ documents). clk starts at 300 ns, ~105
*     ring periods after the rings reach steady state, and the first four
*     clk periods are discarded before the first recorded sample.
*   - rst_n is held at vdd for the whole run, so every sampler is out of reset
*     throughout and no reset edge is in the window. DR-0014's gated-reset
*     behaviour is sim/tb/sampler-dff-reset-clocked/'s subject.
*   - Injected noise: the same white PSD every jitter deck in this repository
*     uses, S = 2*NA^2*NT = 1.0e-16 V^2/Hz, but with NT = 100 ps and NA
*     rescaled to match, where #51's coupling ladder and #76's phase family
*     used NT = 10 ps. A trnoise() source plants a solver breakpoint at every
*     NT, and 10 ps breakpoints cost ~4x the run time -- which is the
*     difference between this family being affordable on a two-ring array over
*     microsecond windows and not existing. The injected DENSITY is unchanged;
*     what changes is that the injection is band-limited to 5 GHz rather than
*     50 GHz, well above anything this circuit responds to (a ~350 MHz ring
*     with ~300 ps edges). Both arms of every comparison carry the identical
*     stimulus, so nothing differential can move with it -- and no per-period
*     jitter or sigma may be read off these records and compared against the
*     10 ps families'. This family reports no sigma, by construction.
*   - Print step 20 ps, a fifth of the noise sources' breakpoint spacing, which
*     floors the solver step anyway -- the reasoning
*     sim/tb/sampler-array-digitize/ records. A finer print step multiplies
*     output size and run time without changing what the solver does.
*   - `abstol=1e-10`, 100x looser than ngspice's 1e-12 default, for the reason
*     sim/tb/sampler-array-digitize/ bisected and documented at length: two
*     series-starved rings hold their devices at currents where a 1 pA
*     absolute tolerance is a meaningful fraction of the branch currents being
*     solved, and an abrupt external edge elsewhere in the same matrix then
*     drives the timestep control to zero. 100 pA is ~5e-6 of the per-ring
*     supply current, and everything measured here is a settled node voltage
*     or a zero-crossing time rather than a current.
*   - Every clk timing is deliberately off the 10 ps grid the trnoise()
*     sources place breakpoints on: tclk_del = 300.003 ns, tclk_tr =
*     0.203 ns, and tclk_per is a multiple of 20 ps so that every rising AND
*     falling edge inherits tclk_del's 3 ps offset. tstop carries the same
*     3 ns offset. A PULSE or tstop breakpoint landing exactly on a trnoise
*     breakpoint collapses ngspice-46's transient ("Timestep too small") at
*     that instant, reproducibly -- the solver limit #76's family recorded so
*     it would not be rediscovered.

vsup vsup 0 dc vdd_val
ven en 0 dc vdd_val

* ---- separate supply pins: per-ring (DR-0007 §1's own supply routing) ----
* ---- plus one for the buffers, combiner and samplers -------------------
vr1 vsup vddr1 dc 0
vr2 vsup vddr2 dc 0
vtr vsup vdd dc 0

* ---- ring 1 (wstv = 0.220u), per-stage series noise injection ----------
xg1 g10 en n11 vddr1 0 ro_nand2 wstv=0.220u lstv=2u cld=0.5f
x11 g11 n12 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x12 g12 n13 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x13 g13 n14 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
x14 g14 rn1 vddr1 0 ro_stage wstv=0.220u lstv=2u cld=0.5f
vn10 rn1 g10 dc 0 trnoise( vn_rms vn_dt 0 0)
vn11 n11 g11 dc 0 trnoise( vn_rms vn_dt 0 0)
vn12 n12 g12 dc 0 trnoise( vn_rms vn_dt 0 0)
vn13 n13 g13 dc 0 trnoise( vn_rms vn_dt 0 0)
vn14 n14 g14 dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- ring 2 (wstv = 0.240u), the skewed twin -------------------------
xg2 g20 en n21 vddr2 0 ro_nand2 wstv=0.240u lstv=2u cld=0.5f
x21 g21 n22 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x22 g22 n23 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x23 g23 n24 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
x24 g24 rn2 vddr2 0 ro_stage wstv=0.240u lstv=2u cld=0.5f
vn20 rn2 g20 dc 0 trnoise( vn_rms vn_dt 0 0)
vn21 n21 g21 dc 0 trnoise( vn_rms vn_dt 0 0)
vn22 n22 g22 dc 0 trnoise( vn_rms vn_dt 0 0)
vn23 n23 g23 dc 0 trnoise( vn_rms vn_dt 0 0)
vn24 n24 g24 dc 0 trnoise( vn_rms vn_dt 0 0)

* ---- DR-0018 per-ring output buffers (sampler_core's xb1/xb2) ---------
xb1 rn1 ro1 vdd 0 ro_buf
xb2 rn2 ro2 vdd 0 ro_buf

* ---- DR-0007 §1 combiner (sampler_core's xa1) -------------------------
xa1 ro1 ro2 xo vdd 0 xor2

* ---- the DR-0001 raw tap (sampler_core's xsb) -------------------------
xsb xo clk rst_n raw_bit vdd 0 sampler_dff

* ---- the DR-0016 per-ring liveness digitizers (sampler_core's xsr1/xsr2)
xsr1 ro1 clkm rst_n ring_bit1 vdd 0 sampler_dff
xsr2 ro2 clkm rst_n ring_bit2 vdd 0 sampler_dff

* ---- DR-0012's fixed external sample clock, driving the raw tap -------
vclk clk 0 dc 0 pulse(0 'vdd_val' tclk_del tclk_tr tclk_tr 'tclk_per/2 - tclk_tr' tclk_per)

* ---- THE ONE CHANGE: the liveness digitizers' clock, RUNNING ----------
* (sim/tb/sampler-bit-bias-static-*/ replaces this single line with a DC
*  rail at vdd and changes nothing else.)
vclkm clkm 0 dc 0 pulse(0 'vdd_val' tclk_del tclk_tr tclk_tr 'tclk_per/2 - tclk_tr' tclk_per)

vrst rst_n 0 dc vdd_val

* ---- measurement probes (measurement-only; no device is added) --------
* bx1/bx2 shift each RING node so a mid-supply crossing is a zero crossing;
* bxc does the same for clk, which is what indexes the samples; bvth is the
* decision threshold the recorded sample voltages are read against; btclk
* exposes the clk period to the control block, which cannot read a .param.
bx1 x1 0 v = v(rn1) - 0.5*vdd_val
bx2 x2 0 v = v(rn2) - 0.5*vdd_val
bxc xc 0 v = v(clk) - 0.5*vdd_val
bvth vth 0 v = 0.5*vdd_val
btclk tclkv 0 v = tclk_per

.ic v(n11)=0
.ic v(n21)=0
